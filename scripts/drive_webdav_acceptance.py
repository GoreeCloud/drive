#!/usr/bin/env python3
"""Opt-in, loopback-only authenticated WebDAV acceptance probe.

No production hosts, stored user data, identity provisioning, or permanent
files. The default probe performs no writes. Explicitly gated mutation tests
create unique temporary files and always attempt cleanup.
"""
from __future__ import annotations

import base64
import os
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass

DAV_PROPFIND = b'<?xml version="1.0"?><d:propfind xmlns:d="DAV:"><d:prop><d:resourcetype/></d:prop></d:propfind>'
DENIAL_STATUSES = frozenset((301, 302, 303, 307, 308, 401, 403, 404))
MAX_BODY_BYTES = 256 * 1024


class AcceptanceError(Exception):
    """Safe, non-credential-bearing acceptance failure."""


@dataclass(frozen=True)
class Config:
    dav_url: str
    authorization: str
    mutate: bool = False

    @classmethod
    def from_environment(cls, env: dict[str, str] | None = None) -> Config:
        env = os.environ if env is None else env
        url = env.get("GOREECLOUD_E2E_DAV_URL", "")
        validate_dav_url(url)
        bearer = env.get("GOREECLOUD_E2E_BEARER_TOKEN", "")
        username = env.get("GOREECLOUD_E2E_USERNAME", "")
        password = env.get("GOREECLOUD_E2E_PASSWORD", "")
        if bearer and (username or password):
            raise AcceptanceError("Choose a bearer token OR username/password")
        if bearer:
            auth = "Bearer " + bearer
        elif username and password:
            auth = "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode("ascii")
        else:
            raise AcceptanceError("Provide test credentials using dedicated environment variables")
        requested_mode = env.get("GOREECLOUD_E2E_MUTATE", "NO")
        if requested_mode not in ("", "NO", "YES"):
            raise AcceptanceError("GOREECLOUD_E2E_MUTATE must be YES or NO")
        mutate = requested_mode == "YES"
        if mutate and env.get("GOREECLOUD_E2E_DISPOSABLE") != "YES":
            raise AcceptanceError("Mutation requires GOREECLOUD_E2E_DISPOSABLE=YES")
        return cls(dav_url=url.rstrip("/") + "/", authorization=auth, mutate=mutate)


def validate_dav_url(value: str) -> None:
    try:
        parsed = urllib.parse.urlsplit(value)
        port = parsed.port
    except (ValueError, TypeError):
        raise AcceptanceError("Invalid WebDAV URL") from None
    if (
        parsed.scheme not in ("http", "https")
        or parsed.hostname not in ("127.0.0.1", "::1")
        or not port
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query or parsed.fragment
        or not parsed.path.startswith("/")
        or "//" in parsed.path
        or "/../" in parsed.path
        or "/./" in parsed.path
    ):
        raise AcceptanceError("Use a loopback-only http(s) DAV URL with an explicit port and no credentials/query")
    if parsed.path == "/":
        raise AcceptanceError("Provide an explicit disposable WebDAV collection path, not the HTTP root")
    decoded = urllib.parse.unquote(parsed.path)
    if any(s in (".", "..") for s in decoded.split("/")) or "\\" in decoded:
        raise AcceptanceError("DAV URL path must not contain navigation segments")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


@dataclass(frozen=True)
class Response:
    status: int
    data: bytes


class DavClient:
    def __init__(self, config: Config):
        validate_dav_url(config.dav_url)
        self.config = config
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), NoRedirect()
        )

    def request(self, method: str, url: str, *, auth: bool = True,
                body: bytes | None = None) -> Response:
        if url != self.config.dav_url and not url.startswith(self.config.dav_url):
            raise AcceptanceError("Request escaped configured DAV collection")
        validate_dav_url(url)
        headers = {"Accept": "application/xml"}
        if auth:
            headers["Authorization"] = self.config.authorization
        if method == "PROPFIND":
            headers["Depth"] = "0"
            headers["Content-Type"] = "application/xml"
            body = DAV_PROPFIND
        elif method == "PUT":
            headers["Content-Type"] = "text/plain; charset=utf-8"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            response = self.opener.open(req, timeout=10)
        except urllib.error.HTTPError as error:
            response = error
        except (OSError, urllib.error.URLError):
            raise AcceptanceError(f"Network failure during {method} to loopback DAV fixture") from None
        try:
            content = response.read(MAX_BODY_BYTES + 1)
            if len(content) > MAX_BODY_BYTES:
                raise AcceptanceError("DAV response exceeds bounded acceptance-test size")
            return Response(status=response.status, data=content)
        finally:
            response.close()


def _require_status(response: Response, statuses: set[int] | frozenset[int], label: str) -> None:
    if response.status not in statuses:
        raise AcceptanceError(f"{label}: unexpected HTTP {response.status}")


def read_only_contract(client: DavClient) -> list[str]:
    url = client.config.dav_url
    response = client.request("PROPFIND", url, auth=False)
    _require_status(response, DENIAL_STATUSES, "Anonymous collection enumeration")
    authenticated = client.request("PROPFIND", url)
    _require_status(authenticated, {207}, "Authenticated collection enumeration")
    try:
        xml = ET.fromstring(authenticated.data)
    except ET.ParseError:
        raise AcceptanceError("Authenticated PROPFIND returned invalid XML") from None
    if xml.tag != "{DAV:}multistatus":
        raise AcceptanceError("Authenticated PROPFIND did not return DAV multistatus")
    return ["anonymous enumeration denied", "authenticated DAV collection enumerated"]


def mutation_contract(client: DavClient, *, name: str | None = None) -> list[str]:
    if not client.config.mutate:
        raise AcceptanceError("Mutation is disabled by default")
    filename = name or (".goreecloud-acceptance-" + secrets.token_hex(12) + ".txt")
    if not filename.startswith(".goreecloud-acceptance-") or "/" in filename or "\\" in filename:
        raise AcceptanceError("Unsafe disposable fixture name")
    url = client.config.dav_url + urllib.parse.quote(filename, safe="")
    original = ("GoreeCloud Drive acceptance " + secrets.token_hex(16)).encode()
    replacement = ("GoreeCloud Drive update " + secrets.token_hex(16)).encode()
    created = False
    attempted_put = False
    error = None
    # Fail closed if this supposedly disposable name already exists.
    # Never overwrite unrelated data even if a name collision occurs.
    _require_status(client.request("GET", url), {404, 410}, "Disposable name preflight")
    try:
        attempted_put = True
        response = client.request("PUT", url, body=original)
        _require_status(response, {200, 201, 204}, "Creating disposable file")
        created = True
        downloaded = client.request("GET", url)
        _require_status(downloaded, {200}, "Reading created file")
        if downloaded.data != original:
            raise AcceptanceError("Round-trip file content mismatch")
        _require_status(client.request("GET", url, auth=False), DENIAL_STATUSES, "Anonymous file access")
        _require_status(client.request("PUT", url, body=replacement), {200, 201, 204}, "Replacing disposable file")
        current = client.request("GET", url)
        _require_status(current, {200}, "Reading replacement")
        if current.data != replacement:
            raise AcceptanceError("Replacement bytes differ")
    except AcceptanceError as exc:
        error = exc
    finally:
        if attempted_put:
            # A server can persist a PUT and still return an error or time out.
            # The preflight established that this unique name was absent.
            removed = client.request("DELETE", url)
            successful_cleanup = removed.status in (200, 202, 204)
            safely_absent = not created and removed.status in (404, 410)
            if not (successful_cleanup or safely_absent):
                raise AcceptanceError(f"Cleanup failed for disposable file {filename}: HTTP {removed.status}")
    if error:
        raise error
    _require_status(client.request("GET", url), {404, 410}, "Confirming disposable file deletion")
    return ["disposable file created", "authenticated bytes round-tripped",
            "anonymous file access denied", "overwrite verified", "disposable file removed"]


def main() -> int:
    try:
        config = Config.from_environment()
        client = DavClient(config)
        checks = read_only_contract(client)
        if config.mutate:
            checks.extend(mutation_contract(client))
        for check in checks:
            print("PASS:", check)
        if not config.mutate:
            print("READ-ONLY: no file was created; set MUTATE=YES and DISPOSABLE=YES only for isolated test storage")
        return 0
    except AcceptanceError as exc:
        print("FAIL:", str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
