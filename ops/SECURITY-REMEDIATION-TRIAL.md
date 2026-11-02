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
- **New non-production image build on VPS 01 (November 1, 2026):** A clean `security/goreecloud-7.2.4-vuln-trial` checkout at source SHA `6a34b6f88030ebb57bec5a3df6c3e71755fcfbd8` was built with branded Web assets, `ENABLE_VIPS=true`, and the official OpenCloud Go 1.26 builder pinned to amd64 manifest `sha256:620c7a90212b46c4aa90e64ce6ed5cbb8934ccabc056d6bfd6bb2683f3f1d1e4`. Full Docker build **exit 0**. The resulting image `goreecloud-drive:7.2.4-gc1-security-trial` has digest `sha256:838992c8de2b9bda1839d6aa03f5a47172cfbb9af440c707cbcd0b9336b0d3e0`, correct source OCI revision, and `goreecloud.release.approved=false`. Restricted network-disabled non-root `--help` CLI smoke test **passed**, with the known custom-build 'dev' edition warning. **No application container or public route was started.** The original `goreecloud-drive:7.2.4-gc1` digest remained unchanged. This closes **build feasibility only**, not runtime or security acceptance.
- **Binary-scan constraint:** A remote action to export the patched binary from the image was blocked by platform safety controls; it was not bypassed. Production-tag source-level `govulncheck` using the pinned Go 1.26/native-libvips build environment is a separate permitted check, but cannot replace an actual binary-level verdict.

## Mandatory gates before promotion

1. Review every dependency and vendored code diff for compatibility, licensing, security and unexpected transitive changes. Treat upstream modules and tools as untrusted until verified.
2. **Builder feasibility passed in isolation** using pinned official Go 1.26 image and native Vips. Before promotion, evaluate builder trust/reproducibility and attach the reviewed Dockerfile and verified build instructions to the approved release path; the original production Dockerfile still uses Go 1.25.
3. **Full branded image build and OCI source-label check passed** in a separate security-trial tag. Still required: complete Go/Web tests, integration/runtime health and auth/file acceptance, correct release edition metadata and full binary/module provenance. Targeted package tests and a CLI help command alone do not satisfy this gate.
4. Run `govulncheck` on the **actual generated binary**, with the production build flags, plus frontend and container/OS package vulnerability scans; investigate `openpgp` reachability and document any accepted risk.
5. Exercise real private authentication, authorization, link sharing, OIDC/HTTPS origins, file uploads/downloads, restarts and rollback under test conditions.
6. Establish encrypted off-host backups with isolated restore proof and enforced storage-capacity limits/alerts before exposing user data.
7. Keep the existing VPS 01 image, containers and live Caddy configuration unchanged until a separately authorized, reversible release satisfies the gates.

**Do not merge or deploy solely because this review branch's branding CI succeeds.** GitHub Dependabot alerts/updates were previously verified disabled, so external dependency monitoring remains an open requirement.
