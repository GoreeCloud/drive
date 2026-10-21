# GoreeCloud Drive — opt-in GoreeCloud UI Foundations theme

**State:** Developer preview; **not** the final GoreeCloud Drive identity, complete GoreeCloud UI migration, or a production-ready web experience.

## What works

The embedded theme at `services/web/assets/themes/goreecloud/theme.json` translates
the supported light/dark semantic color tokens from the published, verified
**GoreeCloud UI Foundations v1.0.1** archive into the existing OpenCloud web
client's 42 design-token color roles. It preserves OpenCloud's share-role IDs,
descriptions, icon mappings and compatibility fields, so the inherited sharing
interface can continue to work. It is served through the **existing real theme
handler**—not a mock or a disconnected design artifact.

Select it for an **isolated development instance** with:

```sh
WEB_UI_THEME_PATH=/themes/goreecloud/theme.json
```

Restart the web service to apply its configured environment. Revert by
unsetting `WEB_UI_THEME_PATH` or restoring the inherited default:
`/themes/opencloud/theme.json`. This is a theme-path selection, not a data
migration or backend module rename. External theme paths remain supported.

The official server default **remains the upstream OpenCloud theme** during
the preview, avoiding an unreviewed cosmetic cutover for existing deployments.

### Known incomplete work

- **Identity:** The preview displays a distinct development label but
  temporarily references the inherited upstream SVG logo and favicon files.
  They remain valid compatibility placeholders; **they are not GoreeCloud
  Drive's approved first-party product identity**. Do not publish the preview
  as a fully rebranded production product.
- **Client:** A separate, pinned source snapshot of the AGPL-3.0 OpenCloud
  Vue/TypeScript frontend now exists under `web-client/`; its real Files
  application is embedded by a deterministic build. The Foundations preview
  still does not replace the frontend's component system. Actual supported
  GC UI component/controller integration, licensing, behavior, identity and
  accessibility require further review and acceptance.
- **Platform and accessibility:** Semantic pairing and >=4.5:1 text-token
  contrast tests do not prove rendered layouts, keyboard/AT navigation,
  mobile experience, high-contrast OS mode, responsive behavior, or deployment.
- **Personalization:** The preview maps the Foundations **Iris** light/dark
  palette, not every GC UI accent or generated color mode. It does not set a
  portfolio-wide preferred hue; future Drive-specific user choices must honor
  GC UI's color-controller contract and first-party identity direction.

## Exact legal and technical provenance

- GC UI source: <https://github.com/GoreeCloud/gc-ui>
- Stable scoped token release: <https://github.com/GoreeCloud/gc-ui/releases/tag/foundations-v1.0.1>
- GC UI release tag commit: `7e0b61ee70af2edb87aa736cca483425f0aacaf4`
- Verified archive: `goreecloud-gc-ui-1.0.1.tgz`
- SHA-256: `275d7e6dc9503b2e74b3190bcecf176d73d2345860e8a20fa5faa3b326cd2298`
- GC UI source license: **Apache-2.0**. The mapped color values and their
  role names originate in that first-party GC UI release. The original theme
  compatibility fields and source are from the Apache-2.0 OpenCloud server.
  Copyright/license notices for both sources remain applicable.
- This is a **generated derivative semantic mapping**, not an import of the
  experimental GC UI component catalog, native hosts or a separate client.

## Deterministic regeneration

For an update, download a specific supported Foundations release and its
checksum from GoreeCloud's official GitHub release. Verify before extraction
and pin the intended tag and checksum; do not pull an unverified latest build.

```sh
gh release download foundations-v1.0.1 --repo GoreeCloud/gc-ui --pattern '*.tgz' --pattern SHA256SUMS
sha256sum -c SHA256SUMS
tar xzf goreecloud-gc-ui-1.0.1.tgz
python3 scripts/generate_gc_ui_theme.py \
  --tokens package/tokens/gc.v1.tokens.json \
  --upstream-theme services/web/assets/themes/opencloud/theme.json \
  --output services/web/assets/themes/goreecloud/theme.json
go test -mod=vendor ./services/web/pkg/theme ./services/web/pkg/assets
```

Review the generated diff, color contrast, branding references, licensing,
theming format and real browser behavior before promoting a later version.
The source snapshot remains deliberately committed for repeatable offline
Go builds and is verified by tests without downloading packages during CI.

The existing OpenCloud theme is retained unchanged as a known functional
fallback. Successful Go tests only establish this server-side preview
contract; a real instance/user-experience acceptance remains outstanding.
