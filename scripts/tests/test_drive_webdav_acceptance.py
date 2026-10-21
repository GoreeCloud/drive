"""Offline, loopback-only regression tests for the authenticated DAV acceptance gate."""
import base64
import os
import subprocess
import sys
import threading
import unittest
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from scripts.drive_webdav_acceptance import (
    AcceptanceError, Config, DavClient, DENIAL_STATUSES,
    mutation_contract, read_only_contract, validate_dav_url,
)

AUTH = "Basic " + base64.b64encode(b"test-user:isolated-secret").decode()
MULTISTATUS = b'<?xml version="1.0"?><d:multistatus xmlns:d="DAV:"><d:response/></d:multistatus>'


class DavFixture(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, status, body=b"", *, location=None):
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        if location:
            self.send_header("Location", location)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def allowed(self):
        return self.headers.get("Authorization") == AUTH

    def do_PROPFIND(self):
        if self.server.redirect:
            return self.respond(302, location="http://example.invalid/never-follow")
        if not self.allowed():
            return self.respond(401)
        if self.path == "/dav/":
            return self.respond(207, MULTISTATUS)
        return self.respond(404)

    def do_GET(self):
        if not self.allowed():
            return self.respond(403)
        if self.path in self.server.files:
            payload = self.server.files[self.path]
            if self.server.corrupt:
                payload = b"corrupted"
            return self.respond(200, payload)
        return self.respond(404)

    def do_PUT(self):
        if not self.allowed():
            return self.respond(403)
        if not self.path.startswith("/dav/.goreecloud-acceptance-"):
            return self.respond(403)
        data = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        existed = self.path in self.server.files
        if self.server.inject_race and not existed:
            self.server.files[self.path] = b"another test principal"
            existed = True
        if self.headers.get("If-None-Match") == "*" and existed:
            return self.respond(412)
        self.server.files[self.path] = data
        if self.server.fail_after_put:
            return self.respond(503)
        return self.respond(204 if existed else 201)

    def do_DELETE(self):
        if not self.allowed():
            return self.respond(403)
        if self.path in self.server.files:
            del self.server.files[self.path]
            self.server.delete_count += 1
            return self.respond(204)
        return self.respond(404)


class AcceptanceGateTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), DavFixture)
        self.server.files = {}
        self.server.redirect = False
        self.server.corrupt = False
        self.server.fail_after_put = False
        self.server.inject_race = False
        self.server.delete_count = 0
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/dav/"
        self.config = Config(self.url, AUTH)

    def tearDown(self):
        self.server.shutdown()
        self.worker.join(timeout=5)
        self.server.server_close()

    def test_read_only_access_contract(self):
        result = read_only_contract(DavClient(self.config))
        self.assertEqual(len(result), 2)
        self.assertEqual(self.server.files, {})

    def test_disposable_create_read_replace_unauthorized_and_delete(self):
        config = Config(self.url, AUTH, mutate=True)
        checks = mutation_contract(DavClient(config))
        self.assertEqual(len(checks), 5)
        self.assertEqual(self.server.files, {})
        self.assertEqual(self.server.delete_count, 1)

    def test_error_path_cleans_created_file(self):
        self.server.corrupt = True
        with self.assertRaisesRegex(AcceptanceError, "mismatch"):
            mutation_contract(DavClient(Config(self.url, AUTH, mutate=True)))
        self.assertEqual(self.server.delete_count, 1)
        self.assertEqual(self.server.files, {})

    def test_server_error_after_write_still_cleans_test_file(self):
        self.server.fail_after_put = True
        with self.assertRaisesRegex(AcceptanceError, "HTTP 503"):
            mutation_contract(DavClient(Config(self.url, AUTH, mutate=True)))
        self.assertEqual(self.server.files, {})
        self.assertEqual(self.server.delete_count, 1)

    def test_existing_disposable_name_is_never_overwritten_or_deleted(self):
        name = ".goreecloud-acceptance-existing.txt"
        original = b"preserve unrelated data"
        self.server.files["/dav/" + name] = original
        with self.assertRaisesRegex(AcceptanceError, "preflight"):
            mutation_contract(DavClient(Config(self.url, AUTH, mutate=True)), name=name)
        self.assertEqual(self.server.files["/dav/" + name], original)
        self.assertEqual(self.server.delete_count, 0)

    def test_competing_create_is_rejected_and_other_file_is_preserved(self):
        self.server.inject_race = True
        name = ".goreecloud-acceptance-race.txt"
        with self.assertRaisesRegex(AcceptanceError, "Conditional creation"):
            mutation_contract(DavClient(Config(self.url, AUTH, mutate=True)), name=name)
        self.assertEqual(self.server.files["/dav/" + name], b"another test principal")
        self.assertEqual(self.server.delete_count, 0)

    def test_conditional_creation_cannot_be_used_with_get(self):
        with self.assertRaisesRegex(AcceptanceError, "only to PUT"):
            DavClient(self.config).request("GET", self.url, create_only=True)

    def test_mutation_disabled_by_default(self):
        with self.assertRaisesRegex(AcceptanceError, "disabled"):
            mutation_contract(DavClient(self.config))
        self.assertEqual(self.server.files, {})

    def test_wrong_credentials_never_pass_authenticated_collection_probe(self):
        with self.assertRaisesRegex(AcceptanceError, "HTTP 401"):
            read_only_contract(DavClient(Config(self.url, "Basic invalid")))
        self.assertEqual(self.server.files, {})

    def test_redirect_is_not_followed_as_authenticated_success(self):
        self.server.redirect = True
        with self.assertRaisesRegex(AcceptanceError, "HTTP 302"):
            read_only_contract(DavClient(self.config))

    def test_cli_read_only_against_disposable_fixture(self):
        env = dict(os.environ,
            GOREECLOUD_E2E_DAV_URL=self.url,
            GOREECLOUD_E2E_USERNAME="test-user",
            GOREECLOUD_E2E_PASSWORD="isolated-secret",
            GOREECLOUD_E2E_MUTATE="NO",
            GOREECLOUD_E2E_DISPOSABLE="NO",
        )
        env.pop("GOREECLOUD_E2E_BEARER_TOKEN", None)
        script = Path(__file__).resolve().parents[1] / "drive_webdav_acceptance.py"
        completed = subprocess.run([sys.executable, str(script)], env=env,
                                   capture_output=True, text=True, timeout=15, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("READ-ONLY", completed.stdout)
        self.assertNotIn("isolated-secret", completed.stdout + completed.stderr)
        self.assertEqual(self.server.files, {})

    def test_cli_mutation_against_disposable_fixture(self):
        env = dict(os.environ,
            GOREECLOUD_E2E_DAV_URL=self.url,
            GOREECLOUD_E2E_USERNAME="test-user",
            GOREECLOUD_E2E_PASSWORD="isolated-secret",
            GOREECLOUD_E2E_MUTATE="YES",
            GOREECLOUD_E2E_DISPOSABLE="YES",
        )
        env.pop("GOREECLOUD_E2E_BEARER_TOKEN", None)
        script = Path(__file__).resolve().parents[1] / "drive_webdav_acceptance.py"
        completed = subprocess.run([sys.executable, str(script)], env=env,
                                   capture_output=True, text=True, timeout=15, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("disposable file removed", completed.stdout)
        self.assertNotIn("isolated-secret", completed.stdout + completed.stderr)
        self.assertEqual(self.server.files, {})
        self.assertEqual(self.server.delete_count, 1)

    def test_full_url_credentials_rejected(self):
        with self.assertRaises(AcceptanceError):
            validate_dav_url("http://user:secret@127.0.0.1:9181/dav/")

    def test_malformed_and_remote_urls_rejected(self):
        for url in (
            "https://drive.example.com/dav/",
            "http://localhost:8443/dav/",
            "http://127.0.0.2:8080/dav/",
            "http://127.0.0.1/dav/",
            "http://127.0.0.1:8000/",
            "http://127.0.0.1:8000/dav/../",
            "http://127.0.0.1:8000/dav/%2e%2e/",
            "http://127.0.0.1:8000/dav/?token=secret",
            "file:///tmp/drive/",
        ):
            with self.subTest(url=url), self.assertRaises(AcceptanceError):
                validate_dav_url(url)

    def test_environment_is_read_only_by_default(self):
        config = Config.from_environment({
            "GOREECLOUD_E2E_DAV_URL": self.url,
            "GOREECLOUD_E2E_USERNAME": "test-user",
            "GOREECLOUD_E2E_PASSWORD": "isolated-secret",
        })
        self.assertEqual(config.authorization, AUTH)
        self.assertFalse(config.mutate)

    def test_environment_requires_strong_disposable_mutation_optin(self):
        env = {
            "GOREECLOUD_E2E_DAV_URL": self.url,
            "GOREECLOUD_E2E_BEARER_TOKEN": "fixture-token",
            "GOREECLOUD_E2E_MUTATE": "YES",
        }
        with self.assertRaisesRegex(AcceptanceError, "DISPOSABLE"):
            Config.from_environment(env)
        env["GOREECLOUD_E2E_DISPOSABLE"] = "YES"
        self.assertTrue(Config.from_environment(env).mutate)

    def test_ambiguous_mutation_setting_fails_closed(self):
        with self.assertRaisesRegex(AcceptanceError, "must be YES or NO"):
            Config.from_environment({
                "GOREECLOUD_E2E_DAV_URL": self.url,
                "GOREECLOUD_E2E_BEARER_TOKEN": "fixture-token",
                "GOREECLOUD_E2E_MUTATE": "1",
            })

    def test_auth_token_and_basic_credentials_cannot_be_mixed(self):
        with self.assertRaisesRegex(AcceptanceError, "Choose"):
            Config.from_environment({
                "GOREECLOUD_E2E_DAV_URL": self.url,
                "GOREECLOUD_E2E_BEARER_TOKEN": "token",
                "GOREECLOUD_E2E_USERNAME": "user",
                "GOREECLOUD_E2E_PASSWORD": "password",
            })

    def test_reject_escaped_collection_request(self):
        with self.assertRaises(AcceptanceError):
            DavClient(self.config).request("GET", self.url + "../outside")

    def test_disposable_filename_restricted(self):
        with self.assertRaisesRegex(AcceptanceError, "Unsafe"):
            mutation_contract(DavClient(Config(self.url, AUTH, mutate=True)), name="../escape.txt")
        self.assertEqual(self.server.files, {})


if __name__ == "__main__":
    unittest.main()
