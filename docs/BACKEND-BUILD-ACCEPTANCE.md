# Full backend build and offline CLI acceptance

**Status:** Active CI compilation safeguard; **not** deployed-backend acceptance.

The imported OpenCloud backend includes many independently compiled Go
services. Component tests for the browser assets or the authenticated DAV
fixture cannot prove that the **complete GoreeCloud Drive executable** links
successfully. The
[full-backend workflow](../.github/workflows/backend-build.yml)
closes that gap.

For changes to server packages, vendored dependencies, embedded web assets,
configuration or command wiring, GitHub Actions builds the actual
`./opencloud/cmd/opencloud` executable from **checked-in vendored
dependencies**, with `GOPROXY=off` and `GOSUMDB=off`. The workflow checks
that the executable is nonempty, exercises CLI `--help`, `server --help`
and `init --help` without starting any services, and verifies the Go build
provenance contains the retained upstream module path.

On the authorized development laptop, the same full backend build passed
at main `6ec81dec366dec419a08c79e62198b01ae52893b` on October 21,
2026. The resulting executable's help entry points also ran in a Podman
container without networking. This does not validate the account system
or the behavior of any running service.

## Reproduce without accessing user data

```sh
GOMAXPROCS=2 GOPROXY=off GOSUMDB=off \
  go build -p=2 -mod=vendor -trimpath \
  -o /tmp/goreecloud-drive-backend ./opencloud/cmd/opencloud

/tmp/goreecloud-drive-backend --help
/tmp/goreecloud-drive-backend server --help
/tmp/goreecloud-drive-backend init --help
go version -m /tmp/goreecloud-drive-backend
```

These are **read-only CLI checks**, not a server initialization command.
Do not run the upstream bare-metal installer against real users, and do not
infer production readiness from a successful build or module metadata.

Real authenticated WebDAV operations must follow
[the isolated acceptance runbook](AUTHENTICATED-WEBDAV-ACCEPTANCE.md):
a genuinely disposable service and test account, loopback-only access,
explicit mutation gating, and strong cleanup verification. The existing
Behat TUS, sharing, versions, quota, interruption and recovery scenarios
remain separate mandatory stages for broader acceptance. Server Reva
upstream compatibility and upgrade/rollback also remain separate tasks.

## Risk and rollback

This workflow changes no server behavior, data or schema. It uses
read-only GitHub Actions permissions, does not receive credentials,
does not initialize a server, and does not deploy. Revert the CI and
documentation commit to remove the gate if necessary; do not silently
ignore a build failure or downgrade standards to obtain a green check.
