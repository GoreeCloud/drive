# GoreeCloud Drive — GoreeCloud Fork maintenance and acceptance plan

**Owner product designation:** **GoreeCloud Fork** of OpenCloud.

**Current state:** OpenCloud server source foundation imported into `GoreeCloud/drive`; build and baseline CI were verified during import. This document does **not** claim finished branding, a deployed instance, completed integrations, or Stable status.

## Fork operating model

Maintain OpenCloud as a substantial, independently controlled GoreeCloud product. Preserve and extend existing features, security fixes, interoperable protocols, and data models where useful. Maintain a distinct GoreeCloud visual identity and product direction. **A mandatory rewrite, or eventual full native conversion, is not a requirement for this owner-designated GoreeCloud Fork.**

This is currently a pinned source **snapshot** in an independent repository, not a GitHub-native linked fork; see [UPSTREAM.md](UPSTREAM.md). Do not delete/recreate the repository to alter GitHub fork metadata without a separately approved continuity and history-preservation plan.

## Active workstreams

| Phase | Outcome | Acceptance evidence |
| --- | --- | --- |
| F0 — Source baseline | Preserve OpenCloud server and GoreeCloud repository history | Pinned revision, notices, source/license inspection |
| F1 — Upstream maintenance | Track relevant security advisories and upstream fixes, integrate reviewed patches | Diff review, compatibility and regression tests, audit log |
| F2 — Reliability | Keep core files, shares, permissions, versioning, search, WebDAV/Graph, administration, and recovery working | Reproducible builds, isolated runtime tests, restore trials |
| F3 — GoreeCloud experience | Implement GoreeCloud identity and GoreeCloud UI where appropriate, responsive accessibility, functional navigation | Screenshot-led audit, keyboard/mobile/light/dark and E2E tests |
| F4 — Ecosystem interoperability | Integrate supported GoreeCloud platform capabilities without breaking upstream interfaces | Authoritative contract checks, integration tests and safe fallbacks |
| F5 — Release | Produce a secure, observable, recoverable self-hosted service | Full security/privacy, recovery, performance and release validation |

## Upstream synchronization

1. Record the current pinned upstream SHA and monitor upstream release notes, security advisories and commits.
2. Compare source revisions and identify relevant security/compatibility fixes; the initial import lacks inherited upstream Git ancestry, so do not treat `git merge upstream/main` as safe without establishing compatible ancestry.
3. Port selected changes on a scoped branch with upstream attribution and a changelog of GoreeCloud-specific deviations.
4. Run regression, authentication, access control, sync, backup/restore, migration, and API tests. Require exact-head CI/review before merging.
5. Document upstream update decisions, including intentionally deferred fixes and associated risk. Do not enable automatic uncontrolled upstream merges.

## GoreeCloud platform systems

Assess each system against its current canonical contract: GoreeCloud Manager, Privacy Shield, Wardveil Security, Everkeep, GoreeCloud UI, GoreeCloud Mesh, GoreeCloud Identity, GoreeCloud Policy, and GoreeCloud Observability.

**No system is presumed integrated merely because it appears above.** Feature implementations must be exercised in real workflows before being marked complete.

## Engineering safeguards

- Retain Apache-2.0 notices and audit all bundled third-party licenses. The distinct upstream web frontend is AGPL-3.0 and is not included in this source import.
- Preserve accounts, file contents, metadata, version history, permissions and share links throughout migrations, and validate restoration and reversible changes.
- Do not rename Go module paths, change storage formats or rewrite runtime architecture merely for cosmetic branding.
- Test OIDC, WebDAV/Graph endpoints, sharing, revocation, quotas, upload interruptions, large-file handling, concurrent edits and conflict resolution.
- Keep example passwords, certificates and insecure development configurations out of deployed environments; never assume upstream defaults are hardened.
- Ensure the GoreeCloud experience is substantively designed and functional rather than a logo-only reskin. Run screenshot-led UI audits when evaluating user interfaces.

## Current owner-approved development and interface authority

The owner-approved [Policy — Native and GoreeCloud Fork Development and GoreeCloud UI](https://docs.google.com/document/d/1vQVPdwUZdiq95anbMXlg7mmVVAirXoITyc35GiYrD8E/edit) (effective October 20, 2026) explicitly recognizes **Native** and **GoreeCloud Fork** as the only two development models. It recognizes this OpenCloud-derived product as **GoreeCloud Fork**. The former conversion requirement is historical and does not govern this project.

**GoreeCloud UI (GC UI)**, with its canonical implementation in [GoreeCloud/gc-ui](https://github.com/GoreeCloud/gc-ui), is the sole active interface/experience authority. Prior design-system names are retired; they do not authorize new UI. The current [Foundations 1.0.1](https://github.com/GoreeCloud/gc-ui/releases/tag/foundations-v1.0.1) supports a scoped semantic-token/color/theme-controller foundation, **not** an accepted full Drive interface. Do not use the predecessor as a design-source shortcut.

A [selectable, embedded GC UI Foundations theme preview](GC-UI-FOUNDATIONS-THEME.md) maps the officially released semantic light/dark colors into OpenCloud's existing web theme contract. It preserves inherited icons for compatibility, is not the default, and has backend contract tests; it is **not** final GoreeCloud product branding.

A properly branded and functioning Drive experience requires its own approved Drive iconography and design, plus actual web-client integration with the GC UI contract. The imported OpenCloud web theme is a preserved compatibility baseline, not evidence of completed GoreeCloud UI adoption. A source-only rename, new color value, or isolated theme file cannot satisfy the interface acceptance gates.

Governance document migrations remain in progress. Current owner approval does **not** by itself prove older canonical instructions, legacy consumer references, and all repository artifacts have been reconciled; verify affected records before relying on them.

**Stable release is not assumed** from a successful upstream import, documentation changes, or a passing development build.
