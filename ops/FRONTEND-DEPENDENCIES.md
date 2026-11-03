# GoreeCloud Drive — identity-provider frontend dependency gate

**2026-11-01 evidence. Experimental security branch only; not deployed or cleared.**

## Source inventory and reproducibility

The built-in OpenCloud identity provider uses the React-based [identifier interface](../services/idp/README.md) with its manifest at `services/idp/package.json` and lock at `services/idp/pnpm-lock.yaml`. It is part of the application's authentication surface, so treat dependencies as security-relevant.

Read-only parsing on the verified `security/goreecloud-7.2.4-vuln-trial` source identified:

| Metric | Locked snapshot |
| --- | --- |
| Package manager declared in manifest | `pnpm@11.1.3` |
| Lock format | `9.0` |
| Direct runtime dependencies | 20 |
| Direct development dependencies | 30 |
| Locked package records | 1,134 |
| Dependency snapshot records | 1,134 |
| Overrides | 5 |

The manifest lists `react@^17.0.2`, `react-dom@^17.0.2`, `@material-ui/core@^4.12.4` and `react-router-dom@5.2.1`. **These are versions and framework lifecycle considerations, not independently confirmed vulnerabilities.** The existing lock includes overrides affecting `fast-uri`, `postcss`, `serialize-javascript`, a Babel SystemJS transform, and `@xmldom/xmldom`; overrides are not evidence that every known advisory is fixed.

## Automated check

Run the new **read-only** contract check from a checkout containing the IDP manifest and lock:

```sh
python3 ops/tests/test_idp_lock_contract.py
```

Requires `PyYAML`. On the connected laptop, the test **passed** on November 1, 2026. The separate `python3 ops/tests/test_idp_lock_selftest.py` also **passed**: it copies the actual manifest/lock into a disposable directory, confirms the valid case passes, deliberately changes the `axios` version requirement, and confirms that the contract rejects that mismatch. These checks touch no live IDP files. It checks that every direct runtime/development dependency, range and resolved importer entry matches `package.json`, that the lock includes package/snapshot records, and that package-manager/lock format are as expected. It neither installs dependencies nor executes package scripts. A passing result proves **manifest/lock consistency, not vulnerability safety**.

**November 2 CI addition (review-only):** Draft PR #3 now runs both read-only tests on pull requests through `.github/workflows/goreecloud-brand-check.yml`, using an ephemeral Python virtual environment and pinned binary-only `PyYAML==6.0.3`. [GitHub Actions run 41441712751](https://github.com/GoreeCloud/drive/actions/runs/41441712751) passed: 20 runtime and 30 development direct dependencies, 1,134 package/snapshot records, and the synthetic `axios` drift rejection. This is repeatable lock consistency coverage only; it is **not** a pnpm vulnerability audit, binary/container scan, or release approval.

The optional stacked IDP hardening also validates all **1,134** current package-resolution records for syntactically valid SHA-512 digests and rejects unexpected `tarball`/custom resolution metadata. The synthetic self-test intentionally corrupts a digest and adds an HTTP tarball URL and expects both to fail. These static integrity pins are **not evidence the downloaded tarballs were retrieved or independently verified**. A trusted pnpm 11.1.3 toolchain, real frozen offline/reproducible build, package audit, runtime/browser acceptance and OS/image scanning remain open.

The production-track IDP Makefile historically invoked `pnpm install` without an explicit `--frozen-lockfile`. Draft, stacked hardening now proposes `pnpm install --frozen-lockfile` and extends the existing CI contract to reject both manifest/lock dependency drift and deliberate removal of the frozen-install flag. This is a **fail-closed source invariant**; it does **not** establish that the current upstream Node image has the required pnpm 11.1.3 or that assets rebuild successfully. A mismatched or missing package-manager version must block acceptance instead of silently resolving a different graph. Confirm the actual builder's package manager and reproduce verified asset hashes and licensing output before promotion. Do not silently update framework major versions or override transitive dependencies without acceptance testing.

## Security scan status and blockers

A network-disabled inspection of the official OpenCloud `nodejs-ci:24` image showed Node `v24.22.0` and bundled pnpm `10.26.1`. The manifest requests pnpm `11.1.3` and pnpm attempted to switch versions when auditing the source. The first locked-down audit **did not execute** because the temporary location prohibited executing the new CLI. A subsequent audit invocation was explicitly blocked by remote-management safety controls. **No pnpm vulnerability-audit result has been obtained; do not claim a clean or failed vulnerability scan from those attempts.** No live IDP files were touched.

Other surfaces needing independent analysis: the bundled Web frontend assets and dependencies, generated JavaScript source maps, Go-embedded auth/OIDC logic, image-base Alpine libraries, and the server's native `libvips` dependencies. The successful `ENABLE_VIPS=true` build and existing Go `govulncheck` scan **do not** cover these frontend/runtime surfaces.

## Hold points before public release

1. Perform an approved, reproducible pnpm 11 audit or equivalent trusted dependency scan against the exact lockfile; record advisory IDs, severity, patched versions and whether runtime/build only.
2. Review any replacement of React 17, Material UI 4 or React Router 5 as a tested UI/security migration; retain GoreeCloud branding, responsive layouts and accessible authentication flows.
3. Verify a frozen, integrity-checked build from the pinned source/lock, record Web asset digests, and run authentication/redirect/CSP and browser-accessibility acceptance tests.
4. Assess Alpine and `libvips` binary/runtime packages in the exact image independently of Go module scans.
5. Preserve the security trial as **draft/unmerged**, and require off-host encrypted recovery, storage protection and private functional testing before any deployment or public Caddy route.

**Current disposition:** identity-provider manifest/lock consistency verified. Frontend dependency vulnerability posture **unverified**; release remains blocked.
