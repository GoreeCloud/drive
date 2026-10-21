# GoreeCloud Drive — isolated authenticated WebDAV acceptance

**Status:** Development test gate. Neither this script nor its GitHub CI job
is evidence that a real GoreeCloud Drive backend has passed authenticated
file-operation acceptance. CI runs **only a simulated local DAV fixture**.

## Purpose

The existing OpenCloud-derived Behat acceptance suite covers extensive
WebDAV, TUS, spaces, sharing and versioning scenarios but requires a
configured environment. This additional small, standard-library-only probe
provides an auditable **real-service smoke path** before proceeding to
full authenticated test execution.

`scripts/drive_webdav_acceptance.py` validates a single, explicitly
provided WebDAV collection. By default it makes **no mutations**:

1. Rejects anonymous `PROPFIND Depth: 0` directory enumeration.
2. Authenticates as an isolated test principal using test-only Basic
   credentials or a bearer token; expects a valid WebDAV `207 multistatus`
   for the root collection.

When the disposable mutation gate is explicitly enabled, the probe also
performs a unique dot-prefixed test-file create, authenticated download with
exact bytes, anonymous access denial, overwrite, exact bytes again, delete,
and missing-after-delete check. The initial upload sets
`If-None-Match: *`, requiring the WebDAV server to atomically reject a
concurrently created filename with HTTP 412. If another client wins the
create race, the probe **does not delete** the competing client's file.
A successful initial create must return HTTP 201; otherwise the probe fails.
This atomicity guarantee depends on the actual server honoring the
precondition, which offline fixtures cannot establish.

The probe tries cleanup after ambiguous uploads, including a server that
persists bytes but reports an error. It refuses to replace a pre-existing
file with the generated fixture name. If cleanup fails, inspect the
isolated test volume for the generated filename before disposal.

## Mandatory isolation controls

- The URL **must be literal 127.0.0.1 or ::1**, HTTP(S), have an explicit
  port, and point to an **existing DAV collection path**. The tool rejects
  remote hosts, usernames in URLs, query strings, fragments and traversal.
- **Do not forward a production endpoint to loopback.** The script cannot
  distinguish a local test service from a tunnel to real user storage.
- Test credentials come from environment variables only; they are never
  logged, incorporated into URLs or saved to GitHub. No proxy or HTTP
  redirect is followed.
- Test responses are bounded to 256 KiB; requests have a ten-second timeout.
- Mutation requires **both**
  `GOREECLOUD_E2E_MUTATE=YES` and
  `GOREECLOUD_E2E_DISPOSABLE=YES`. Only set these after verifying the
  connected service, test account and storage volume are disposable and
  contain no production user data. The marker is owner/operator
  attestation, not an automatic proof of isolation.
- Cleanup failure is a **test failure** and prints only the generated
  disposable filename. Inspect and remove the fixture in the test volume
  before destroying it.

## Running against an explicitly configured local test backend

Point the URL at the *existing isolated test user's WebDAV collection*. An
illustrative legacy WebDAV path is shown; actual backend identity and
routing configuration may use a different endpoint or bearer credentials.

```bash
export GOREECLOUD_E2E_DAV_URL='http://127.0.0.1:9200/remote.php/dav/files/test-user/'
export GOREECLOUD_E2E_USERNAME='test-user'
export GOREECLOUD_E2E_PASSWORD='<test-account-password-from-your-local-secret-store>'
python3 scripts/drive_webdav_acceptance.py
```

The password placeholder is not a usable secret; supply only an isolated
ephemeral account password. Instead of username/password, set
`GOREECLOUD_E2E_BEARER_TOKEN` for a valid, disposable identity token and
unset the Basic variables.

**Only after the isolated instance is validated**, additionally run:

```bash
GOREECLOUD_E2E_DISPOSABLE=YES GOREECLOUD_E2E_MUTATE=YES \
  python3 scripts/drive_webdav_acceptance.py
```

Run the fuller existing Behat/Web E2E suites separately for TUS, sharing,
auth grants and revocations, WebDAV spaces, versions, files larger than
the test response limit, quota, retry/concurrency, recovery, interrupted
upload and administrative denial. This simple smoke path cannot certify
those functions or a production deployment.

## Offline CI and rollback

```bash
python3 -m unittest discover -s scripts/tests \
  -p 'test_drive_webdav_acceptance.py' -v
```

GitHub workflow `authenticated-dav-acceptance.yml` runs that offline
fixture only, including cleanup-on-error, unauthorized access, no-follow
redirect and no-remote-host cases. **It never receives real credentials,
starts a full Drive instance, or writes to an external service.**

The code is additive and changes no service route, deployed configuration,
database or user data. To roll it back, revert its script/tests/docs/CI
commit. Do not classify the product as Stable from offline fixture tests.
