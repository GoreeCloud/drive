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

Requires `PyYAML`. On the connected laptop, the test **passed** on November 1, 2026. It checks that every direct runtime/development dependency, range and resolved importer entry matches `package.json`, that the lock includes package/snapshot records, and that package-manager/lock format are as expected. It neither installs dependencies nor executes package scripts. A passing result proves **manifest/lock consistency, not vulnerability safety**.

The source IDP Makefile currently invokes `pnpm install` without an explicit `--frozen-lockfile`. Before promoting a dependency refresh, evaluate using frozen installs in a reviewed follow-up and verify that the actual builder/package-manager combination reproduces asset hashes and licensing output. Do not silently update framework major versions or override transitive dependencies without acceptance testing.

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
