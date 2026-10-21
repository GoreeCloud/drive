# GoreeCloud Drive — maintained OpenCloud web-client source and build

**State: Development.** This document describes a genuine Files web client built
from a pinned upstream snapshot and embedded into the GoreeCloud Drive Go server.
It does **not** establish a completed GoreeCloud UI redesign, secure deployment,
authentication acceptance, or Stable release.

## Source and licensing

| Source component | Upstream | Revision | License |
| --- | --- | --- | --- |
| Go storage and service backend | [opencloud-eu/opencloud](https://github.com/opencloud-eu/opencloud) | `61ae13a1fea0bb8a36bf4b96c1d222fc84aeaa9c` | Apache-2.0 |
| Browser frontend under `web-client/` | [opencloud-eu/web](https://github.com/opencloud-eu/web) | `954dbee3ac5b428d1f42c6eeaf9184484d1cda43` (`main`, 2026-10-21) | **AGPL-3.0** |

The complete tracked upstream web source tree, its `web-client/LICENSE`,
workspace packages, configurations, tests, legal attributions and
`pnpm-lock.yaml` are retained. The parent repository's server
`LICENSE` remains Apache-2.0; **it does not relicence the browser frontend**.
The compiled client under `services/web/assets/core` is generated from the
AGPL-covered source and must be distributed and deployed in compliance with
its network-source and third-party notice obligations. Before any production
release, provide a prominent corresponding-source link to end users and
review third-party source/license and distribution obligations. This document
is not a legal compliance certification.

A dedicated [read-only upstream web-client watch](WEB-CLIENT-WATCH.json) detects
browser-source, latest-release, and public advisory changes independently of
the Go-server watch. It does not authorize automatic upgrades or assert that
browser dependencies are vulnerability-free.

The frontend source is imported as a pinned independent source snapshot,
not a GitHub-native linked fork or a submodule. Its upstream Git ancestry is
not included; reconcile upstream updates by explicit source comparisons and
reviewed patches. Keep server and web-client revisions independently pinned.

## Real included functionality

The upstream web client includes the functioning Files application and its
existing search, spaces, sharing, versioning, upload/download, previews,
file operations, authentication flow, and supporting applications. Those
features **depend on properly configured GoreeCloud Drive backend services**;
a built client alone is not verification of live operation or authorization.
Maintaining these capabilities is a core GoreeCloud Fork requirement.

The generated `index.html`, `oidc-callback.html`, application module
bundles, CSS/fonts/icons, and PWA manifest are staged into the server's
embedded `services/web/assets/core` directory. The Go web service serves
the client with existing HTTP routes. Real identity, OIDC and backend
configuration are generated and served by the server; **no secrets or
production configuration are embedded in this imported source**.

## Build a functional development binary

Use Node.js 22+ and the pinned PNPM version declared in
`web-client/package.json`; install only reviewed dependencies.

```bash
corepack enable
bash scripts/build_drive_web_client.sh
go test -mod=vendor ./services/web/...
go build -p=2 -mod=vendor -tags disable_crypt -o /tmp/goreecloud-drive ./opencloud/cmd/opencloud
```

The build script uses `pnpm install --frozen-lockfile`, runs the frontend
build with the browser title **GoreeCloud Drive**, validates the Files
entrypoint, then replaces only generated web-core assets while retaining
the existing `.keep` marker. The `services/web/assets/core` directory is
reserved for generated web-core assets. The committed browser output is
used by the Go embed fallback without requiring PNPM during normal Go builds.

**Do not serve development credentials, sample accounts or unreviewed
defaults to public networks.** Full local deployment requires supported OIDC,
storage, message bus and API configuration, and an actual authenticated E2E
test. A successful build is not deployment acceptance.

## GoreeCloud UI adoption boundary

Browser title and PWA identity are labeled GoreeCloud Drive. Existing
upstream icons, some copy and UI implementations remain and have **not**
been approved as final GoreeCloud product branding. The opt-in
[GoreeCloud UI Foundations preview](GC-UI-FOUNDATIONS-THEME.md) maps
the official semantic light/dark palette but does not automatically replace
the separate frontend's component system.

Next UI acceptance work: original Drive product artwork, actual functional
GC UI components and navigation, responsive keyboard and assistive-technology
verification, file operations in an isolated authenticated runtime, and
planned platform-system integrations. No migration to a forced native rewrite.

## Rollback

For code, revert the import/branding commit on a development branch. For
the browser experience, rebuild the previous pinned frontend snapshot into
the generated core assets; preserve the original artifacts and source
revision. For theme changes, revert
`WEB_UI_THEME_PATH` to `/themes/opencloud/theme.json`. No user data or
storage schema is migrated by these build steps.
