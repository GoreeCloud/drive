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
its network-source and third-party notice obligations. The browser client now
includes an unconditional **Source code (AGPL-3.0)** link in the account-menu
footer (including guest contexts) pointing to the publicly readable
[GoreeCloud Drive web-client source](https://github.com/GoreeCloud/drive/tree/main/web-client).
It opens in a new tab with `rel="noopener noreferrer"`, and the Go embedded
asset tests verify that the compiled frontend actually contains the source URL.
Continue to review network availability, complete corresponding-source
coverage, third-party notices, license details and release-specific distribution
obligations before deployment. **A link by itself is not a legal compliance
certification.**

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

### Project-space access-denied navigation backport

The GoreeCloud Fork selectively includes the frontend fix from upstream web
commit `a57e87e47065ef618ab81fe890b77f53b5d61cd2`. When a logged-in
user opens a stale or inaccessible `project/...` space route that no longer
resolves, the Files app shows its existing accessible **Resource not found**
message with a link to the spaces overview; it does not silently redirect
the user into their personal files. Guest contexts retain their share-list
fallback and personal-drive aliases still resolve to the appropriate space.
The route handler also transitions correctly when navigating away from an
unknown project space.

The companion upstream component regression tests are carried in the
AGPL-3.0 source tree and run in GoreeCloud's independent web-client CI.

### Search route registration cleanup

A separate selective fix from upstream web commit
`8297034c331dc1014a1b795100f0d7b9464b9b63` drops the retired
standalone `/search/list` route registration from the Search application.
The Search app identity, dynamic extensions and provider extension points
remain registered. The legacy `App.vue` source remains dormant for now but
is **not imported or routed** by the application registration. A new
focused Vitest registration test verifies that the app remains present while
no standalone route is published; full frontend/Go/browser regression checks
run on the rebuilt embedded client. This is a scoped navigation repair,
not an API search-service redesign or full upstream version bump.

### Dynamic locale updates for search and route titles

Selectively backport upstream OpenCloud web commit
`73a26af3d6a281023a5d9e5550a14fb36263c449` (AGPL-3.0) into the
Search location filter and runtime App, with the corresponding upstream
Vitest regression cases. The selected search scope retains its stable ID
while its visible label updates from the reactive translated options when
the language changes. Route-generated document titles likewise update to
the new language **without falsely announcing a page navigation** to
assistive technologies. Explicitly view-owned titles, such as a file
preview title, remain untouched by the language-change watcher.

Tests cover both the German-to-English label/title transition and
preservation of view-owned titles. The test's mocked theme name uses
**GoreeCloud Drive** for project-specific branding; the runtime still
uses the configured theme name. The built JS is regenerated from the
frozen upstream lockfile, and the independent frontend CI gates the
targeted Vue tests, compiled asset reproducibility, Go embedding and
desktop/mobile Chromium static delivery. These are component/browser
build checks, **not** evidence of end-to-end localization in an
authenticated deployed environment.

The pinned upstream source and advisory baselines do not change as
part of this targeted correction. Roll back by reverting the scoped
Vue/tests/generated-assets commit and rebuilding the previous revision.
This is a focused UX/access-state correction, **not** an API authorization
policy change, claim of a fully authenticated deployment, or blanket upgrade
of the pinned upstream web revision. The upstream watch retains the original
baseline until a separate full-source review; revert the scoped source/asset
commit and rebuild to roll back.

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
