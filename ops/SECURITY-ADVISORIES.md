# GoreeCloud Drive — upstream security advisories and release evidence

Evidence date: 2026-11-01. **This is a targeted advisory review, not a complete SCA, SAST, vulnerability, runtime or penetration test.** The release remains blocked from public operation until its security and recovery gates are met.

## Exact source and dependency provenance

- GitHub fork: `GoreeCloud/drive`, branch `release/goreecloud-7.2.4`, derived from official OpenCloud `v7.2.4` upstream commit `1770793f2657e153836c32d32dd6d256b8531d3d`.
- Official [v7.2.4 release notes](https://github.com/opencloud-eu/opencloud/releases/tag/v7.2.4) classify this as a **production release**, dated August 21, 2026.
- Official [v9.0.0 release notes](https://github.com/opencloud-eu/opencloud/releases/tag/v9.0.0), October 27, 2026, classify that as **rolling**, not a superseding stable production release.
- Source `go.mod` at `v7.2.4` specifies `github.com/opencloud-eu/reva/v2 v2.46.8`. This check concerns declared source modules. A compiled binary's exact bill of materials has not been independently verified.

## Targeted upstream advisories

| Advisory | Severity | Fix threshold in upstream advisory | Assessment for v7.2.4 |
| --- | --- | --- | --- |
| [GHSA-vf5j-r2hw-2hrw](https://github.com/opencloud-eu/opencloud/security/advisories/GHSA-vf5j-r2hw-2hrw) — Public Link Exploit | High (CVSS 8.2) | Stable 4.0.3 or rolling 5.0.2; underlying Reva [GHSA-9j2f-3rj3-wgpg](https://github.com/opencloud-eu/reva/security/advisories/GHSA-9j2f-3rj3-wgpg) fixed at 2.40.3 / 2.42.3 | **Above the published fixed versions**; declared Reva version is 2.46.8. No exploit reproduction or binary-level validation was performed. |
| [GHSA-gf4p-7p27-26w7](https://github.com/opencloud-eu/opencloud/security/advisories/GHSA-gf4p-7p27-26w7) — Access to internal metadata | Moderate (CVSS 6.3) | Stable 4.0.8 or 7.2.0 | **Above the published fixed version**; no runtime or exploit validation was performed. |

These two advisories are the **published upstream repository advisories found during this bounded review**. Their fix thresholds do not establish that newer dependencies are vulnerability-free or that no other advisories exist for transitive packages, operating-system libraries, container base images, Web client dependencies, or the fork's implementation.

## Repository and build coverage gaps

- GoreeCloud's GitHub repository secret scanning and push protection were enabled when last checked; GitHub Dependabot **security updates were disabled**, and the Dependabot alerts API reported that alerts were disabled. Recheck current settings before claiming continuous vulnerability monitoring.
- The production-track custom image is `goreecloud-drive:7.2.4-gc1`, built locally and branded, but reports a self-compiled `dev` edition metadata channel. It is not a vendor-certified release image.
- On 2026-11-01, official Go-team `govulncheck` v1.9.0 **module-level** scanning completed and reported **35 advisories affecting 13 dependency modules** (details below). This is a positive security finding, not a clean scan. Neither compiled-image scanning nor a production-tag symbol-level scan has passed. Trivy/Grype/OS packages and frontend dependencies remain unscanned.
- GitHub's current brand integrity CI and targeted Go tests are useful but are **not** substitutes for a source/dependency/container scanner, functional security tests or a verified backup restore.
- Public-link password-required configuration is staged and verified against release source annotations. Requiring passwords does **not** disable public-link creation or prove the security of the sharing mechanism.

## Verified Go dependency vulnerability scan (2026-11-01)

**Result: release-blocking findings; no production deployment.** A local source checkout of the production-track branch was inspected with the Go team's official `golang.org/x/vuln/cmd/govulncheck@v1.9.0` (Go source tag `e672cbe8fbc8c76e28fcb6db0efd9ce354e0dac5`, license BSD-3-Clause), with `GOTELEMETRY=off`. The project source and scanner manifest were reviewed before running.

```sh
GOTELEMETRY=off govulncheck -scan=module -C /path/to/fork/opencloud/cmd/opencloud
```

The scanner returned **35 module-level advisories across 13 modules** (nonzero exit, "Your code may be affected"). The affected versions include:

| Module | Observed version | Selected fixed thresholds from scan |
| --- | --- | --- |
| `golang.org/x/net` | v0.55.0 | v0.62.0 for GO-2026-6866/6860; HTTP/2 findings fixed by v0.60.0 |
| `golang.org/x/text` | v0.37.0 | v0.41.0 for GO-2026-6629 |
| `golang.org/x/crypto` | v0.52.0 | v0.56.0 for SSH DoS findings; GO-2026-5932 (`openpgp`) has **no fixed version** — audit usage |
| `google.golang.org/grpc` | v1.81.1 | v1.83.1 for multiple xDS/HTTP2 issues |
| `golang.org/x/image` | v0.40.0 | v0.45.0 for GO-2026-6222 |
| `github.com/go-git/go-git/v5` | v5.19.1 | v5.19.2 for reference/symlink issues |
| `github.com/klauspost/compress` | v1.18.5 | v1.18.7 |
| `github.com/go-chi/chi/v5` | v5.2.5 | v5.3.0 for forwarded-IP spoofing |
| `go.etcd.io/etcd/client/pkg/v3` | v3.6.11 | v3.6.14 |
| `go.opentelemetry.io/otel/exporters/otlp/otlptrace`, `otlptracegrpc`, `sdk` | v1.44.0 | v1.45.0 |
| `github.com/go-acme/lego/v4` | v4.4.0 | v4.34.0 for a webroot path issue |

**Precision:** Module-level findings do not prove that vulnerable functions are reachable, that all affected packages ship in the built image, or that each item is exploitable. The first **symbol-level** scan with the production build tags `disable_crypt,enable_vips` failed on the laptop because it lacks native `libvips`/pkg-config files. Thus **no valid production-tag symbol-level or built-image scan verdict** has been obtained. The release image was built from fork code commit `e721728a163417961a0b3b28c3c26ec85fef273e` and has not been replaced or redeployed.

**Triage order:** (1) network-exposed gRPC and HTTP/2 memory, parser and authorization defects; (2) file/image parsing and archive handling; (3) cryptography, SSH and Git-related consumers; (4) telemetry/logging and ancillary integrations; (5) unchanged Alpine/Node/frontend dependencies. First verify reachability and binary/module versions. Do not bulk-upgrade the stable fork's vendor packages or replace it with the rolling upstream release without compatibility tests, a new build, regression testing and a rollback plan.

**Verified patch compatibility constraint:** The current staged production Dockerfile builds with `quay.io/opencloudeu/golang-ci:1.25`. Downloaded official module manifests for selected fixed versions report `golang.org/x/net@v0.62.0` **requires Go 1.26.0**, and `golang.org/x/crypto@v0.56.0` **requires Go 1.26.0**. In contrast `golang.org/x/text@v0.41.0` and `google.golang.org/grpc@v1.83.1` declare **Go 1.25.0**. These are module `go` directives, not evidence the patched application builds or works. Any comprehensive remediation must evaluate a reviewed Go toolchain/base-image upgrade plus vendor/release compatibility rather than blindly updating module versions while retaining the 1.25 build image. The official Go module checksum verification (`go mod verify`) passed on the clean checkout; that checks module integrity, **not absence of vulnerabilities**.

**Tracking:** GitHub Issues are disabled for `GoreeCloud/drive` (GitHub returned HTTP 410), so these results must also be tracked in the existing authorized Todoist deployment task. No issue was created.

## Isolated dependency remediation trial — not built or deployed (November 1, 2026)

A **separate experimental Git worktree**, based on release revision `e9d65b017da9d13a7a61037b73892de51ab57195`, has now been preserved as a [review-only security branch](https://github.com/GoreeCloud/drive/tree/security/goreecloud-7.2.4-vuln-trial) at commit `6a34b6f88030ebb57bec5a3df6c3e71755fcfbd8`. The branch includes `go.mod`, `go.sum`, regenerated `vendor/`, and an explicit non-production review note. No production image, VPS runtime, `main`, or release-branch dependency source was changed. GitHub's private-email push restriction was respected using the authenticated account's no-reply commit identity; privacy settings were not weakened.

Official `govulncheck v1.9.0` module scans reported a reproducible reduction as patch groups were introduced with `GOFLAGS=-mod=mod`:

| Trial stage | Module-level advisory count | Targeted Go configuration / initialization tests |
| --- | ---: | --- |
| Unmodified 7.2.4 candidate | 35 | Previously passed |
| Upgrade `x/net`, `x/crypto`, `x/text`, gRPC | 19 | Passed |
| Upgrade `x/image`, go-git, compress, chi | 6 | Passed |
| Upgrade OpenTelemetry exporters/SDK, etcd, gRPC patch | 3 | Passed |
| Upgrade lego ACME library from v4.4.0 to v4.34.0 | **1** | Passed |

The remaining finding is [GO-2026-5932](https://pkg.go.dev/vuln/GO-2026-5932) for the unmaintained `golang.org/x/crypto/openpgp` package; there is **no fixed module version**. Direct application-source import searches did not identify a reference to `openpgp`, and the original binary did not contain that exact package path as a printable string. **Neither observation proves absence of reachable vulnerable code; an authoritative production-tag symbol/binary scan is still required.**

A separate **network-disabled inspection** of the original `goreecloud-drive:7.2.4-gc1` Docker image's executable confirmed that all 13 modules reported by the original module scan are embedded at the reported affected versions. Its binary source revision remains `e721728a163417961a0b3b28c3c26ec85fef273e`. The experiment has **not** replaced that image.

**Constraints and acceptance:** The trial's `go.mod` directive advances to Go 1.26, while the VPS image's verified builder is `quay.io/opencloudeu/golang-ci:1.25`. Regeneration of `vendor/` with `go mod vendor` **succeeded**, and the targeted tests **passed again in default vendor mode**, alongside scoped `go vet`, `go mod verify` and `git diff --check` for the module manifests on a laptop running Go 1.27.3. A full-tree whitespace check flagged whitespace in updated third-party vendor README text; its upstream wording was not changed to suppress the warning. A complete Go/web build with real native `libvips` and a vetted Go 1.26+ builder, production-tag symbol/binary vulnerability scan, functional integration tests, image SBOM, backup restore and deployment acceptance have **not** passed. The review branch remains **unreviewed and not suitable for production**. Do not merge its dependency changes without proving release-toolchain compatibility and reviewing transitive changes.

## Exit criteria

1. Evaluate and remediate applicable *current* OpenCloud and Reva upstream security advisories, Go module vulnerabilities, Node/web frontend dependencies and the built Alpine container filesystem.
2. Check the actual production image digest and bill of materials rather than assuming it matches an upstream artifact.
3. Run appropriate source and dependency/container scans using trusted, reviewed scanners, recording versions, findings, accepted risks and remediations.
4. Validate authentication/authorization and link-sharing behavior privately before allowing the public hostname. Preserve upstream licensing and attribution.
5. Record a new review when the upstream production release changes; avoid silently replacing the validated source with a rolling release.

**Current disposition:** The two specific upstream repository advisories have patch thresholds predating v7.2.4, **but the Go module scan detects 35 known advisories and this is a release blocker**. Applicability, binary composition, frontend/system-library vulnerabilities and remediation remain unverified. **Not ready for public release.**
