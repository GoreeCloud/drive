# Identity-provider keyboard focus backport

**Scope:** A small upstream accessibility fix in the existing OpenCloud-derived
identity provider. This is a **GoreeCloud Fork** maintenance change, not a new
sign-in experience, redesign or a complete WCAG certification.

## Source

Upstream OpenCloud server commit
[`8acaef28e2795e569fdf4687bd563c97f70d2eee`](https://github.com/opencloud-eu/opencloud/commit/8acaef28e2795e569fdf4687bd563c97f70d2eee)
(`fix(idp): show keyboard focus on every control`, October 21, 2026) modifies
`services/idp/src/app.css`. The GoreeCloud patch selectively ports the
focus style change without silently advancing the imported server revision
or pulling the unrelated Reva dependency bump.

## User-facing behavior

The identity provider suppresses Material UI ripple and button box-shadow.
The previous style only made the text input's focus treatment visible; other
keyboard-focused controls could lack a clear indicator.

- `body :focus-visible` adds a visible 2px outline with 2px offset for
  keyboard-focused controls.
- The logo link receives a contrasting white outline and a darker 6px
  surrounding ring, covering light/dark backgrounds.
- Existing input focus remains styled and is explicitly offset 0.

## Verification and limitations

- Four offline CSS contract tests cover universal keyboard focus, logo focus,
  existing input focus, and retained ripple suppression.
- On the development laptop a **Chromium DOM/CSS smoke test** verified
  keyboard Tab navigation, computed outline width, and logo box-shadow at
  desktop 1280×800 and mobile 375×812 viewports (isolated representative
  controls, not the entire live authentication flow).
- Not yet verified: actual deployed IdP login, assistive-technology screen
  readers, full WCAG audit, authentication security, and the unrelated
  upstream Reva/storage updates.

Rollback is a revert of this source patch and regeneration of IdP assets.
Preserve the original Apache-2.0 licensing and upstream attribution.
