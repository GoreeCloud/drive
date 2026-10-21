# GoreeCloud Drive — Fork-to-Native architecture and acceptance plan

**Status:** Development plan; no native-conversion milestone is claimed complete by this document.

## Scope and ownership

Preserve the OpenCloud server's working file, share, access, identity, collaboration, search, versioning, administration, API and recovery behavior, where present, while selectively isolating and replacing strategically important inherited components. The source import is the functional reference, not a Stable GoreeCloud release.

## Controlled milestones

| Stage | Outcome | Verification gate |
| --- | --- | --- |
| F0 — Baseline | Import attributed OpenCloud server and preserve existing GoreeCloud repository history | Source SHA, license, tree, reproducible readback |
| F1 — Reliability | Establish a reproducible Go build, smoke testing, backup/restore and secure reference deployment | CI plus isolated runtime/security evidence |
| F2 — Experience | Apply approved GoreeCloud brand assets, Glaze themes, onboarding, accessibility and coherent login/navigation | Screenshot-led audit, light/dark and keyboard/mobile regression tests |
| F3 — Boundaries | Own contracts for identity, policy, observability, backup and storage interoperability | Compatibility tests, data migration plan and reversible feature flags |
| F4 — Native replacement | Incrementally replace product-defining upstream components only where justified | Side-by-side verification, no feature/data loss, tested rollback |
| F5 — Stable | Meet all platform, security, privacy, performance, accessibility, recovery and deployment requirements | Exact-release acceptance evidence; no inferred production status |

## Nine GoreeCloud Integral Platform Systems

All nine require applicability and current-contract checks before integration:

1. GoreeCloud Manager — administration.
2. Privacy Shield — user controls and data minimization.
3. Wardveil Security — threat protection and security policies.
4. Everkeep — backup, recovery, resilience and preservation.
5. Glaze — approved design and experience system.
6. GoreeCloud Mesh — authenticated device/service connectivity.
7. GoreeCloud Identity — governed authentication and account lifecycle.
8. GoreeCloud Policy — policy evaluation and compliance.
9. GoreeCloud Observability — private, minimal operational telemetry.

**All entries above are pending assessment, not marked integrated.** Cross-product contracts must be sourced from their current canonical implementations rather than invented.

## Safety and migration invariants

- Keep upstream module names, binary identity, storage schemas and protocol behavior until replacements are tested; cosmetic relabeling is not native conversion.
- Do not claim restored data, offline sync, deployment, Glaze parity or native identity without concrete evidence.
- Preserve user data, metadata, share permissions and revision histories during migration. Require before/after counts, backups and restore/rollback trials.
- Handle external OIDC, WebDAV/Graph, shared links, access revocation, upload interruption, conflicts and quota enforcement as first-class test paths.
- Follow upstream vulnerability advisories during the transition; never disable TLS/authentication, introduce hardcoded secrets or expose sample credentials.
- Consider desktop/mobile client compatibility separately: those applications live in other upstream repositories and are not imported by this server fork.
