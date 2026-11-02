# GoreeCloud Drive — dependency remediation candidate (review-only)

**Status: experimental; not production-approved, not merged, not deployed.**

This branch changes only dependency manifests and their matching vendored Go source, plus this review record. It is based on the GoreeCloud Drive production-track fork of official OpenCloud v7.2.4. It must not be used to replace the pinned VPS 01 image until the full release gates pass.

## Reproducible evidence — November 1, 2026

- The original v7.2.4 candidate had **35 module-level vulnerability advisories** across 13 dependency modules under official `govulncheck v1.9.0` using the then-current Go vulnerability database.
- The patched worktree returned **one module-level advisory**, [GO-2026-5932](https://pkg.go.dev/vuln/GO-2026-5932), covering the unmaintained `golang.org/x/crypto/openpgp` package with no fixed module version. It requires further call-path inspection; it was not declared safe.
- Direct module updates were applied in groups, with targeted Go tests passing after each group: `x/net`, `x/crypto`, `x/text`, gRPC, `x/image`, go-git, compress, chi, OpenTelemetry SDK/exporters, etcd and lego/ACME.
- Selected module versions include `x/net v0.62.0`, `x/crypto v0.58.0`, `x/text v0.43.0`, `grpc v1.83.2`, `x/image v0.45.0`, `go-git v5.19.2`, `compress v1.18.7`, `chi v5.3.0`, `etcd client/pkg v3.6.14`, OpenTelemetry `v1.45.0`, and lego `v4.34.0`. See `go.mod` for exact resolved versions and replacements.
- Go `1.27.3` was used on an authorized Linux laptop. The module's `go` directive advanced to `1.26.0`.
- `go mod vendor` succeeded and regenerated `vendor/`. Using default **vendor-mode** resolution, the targeted package tests passed: `./pkg/config/...`, `./services/proxy/pkg/config/...`, `./services/sharing/pkg/config/...`, and `./opencloud/pkg/init/...`. The same scoped `go vet -p 2` passed; `go mod verify` reported all modules verified.
- `git diff --check -- go.mod go.sum` passed. A whole-tree `git diff --check` did flag trailing whitespace in copied upstream `vendor/github.com/klauspost/compress/README.md`; that upstream third-party document was not modified to suppress the warning.
- A previously built **production candidate binary** was inspected in isolation on VPS 01, and all 13 original flagged module versions were confirmed embedded. The original binary is **not** patched by this branch.

## Mandatory gates before promotion

1. Review every dependency and vendored code diff for compatibility, licensing, security and unexpected transitive changes. Treat upstream modules and tools as untrusted until verified.
2. Rework the **builder image**: the original production Dockerfile uses `quay.io/opencloudeu/golang-ci:1.25`, which is incompatible with the updated `go 1.26.0` directive. Select and pin a vetted Go 1.26+ build environment supporting the real `ENABLE_VIPS=true` / CGO / libvips pipeline.
3. Build the full branded application and Web assets, run its complete Go test suite plus applicable UI/integration tests, compare source labels and embedded dependency metadata, and verify a new image digest. Targeted package tests alone do not satisfy this gate.
4. Run `govulncheck` on the **actual generated binary**, with the production build flags, plus frontend and container/OS package vulnerability scans; investigate `openpgp` reachability and document any accepted risk.
5. Exercise real private authentication, authorization, link sharing, OIDC/HTTPS origins, file uploads/downloads, restarts and rollback under test conditions.
6. Establish encrypted off-host backups with isolated restore proof and enforced storage-capacity limits/alerts before exposing user data.
7. Keep the existing VPS 01 image, containers and live Caddy configuration unchanged until a separately authorized, reversible release satisfies the gates.

**Do not merge or deploy solely because this review branch's branding CI succeeds.** GitHub Dependabot alerts/updates were previously verified disabled, so external dependency monitoring remains an open requirement.
