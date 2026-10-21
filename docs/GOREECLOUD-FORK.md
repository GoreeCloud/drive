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
| F3 — GoreeCloud experience | Implement GoreeCloud identity and Glaze where appropriate, responsive accessibility, functional navigation | Screenshot-led audit, keyboard/mobile/light/dark and E2E tests |
| F4 — Ecosystem interoperability | Integrate supported GoreeCloud platform capabilities without breaking upstream interfaces | Authoritative contract checks, integration tests and safe fallbacks |
| F5 — Release | Produce a secure, observable, recoverable self-hosted service | Full security/privacy, recovery, performance and release validation |

## Upstream synchronization

1. Record the current pinned upstream SHA and monitor upstream release notes, security advisories and commits.
2. Compare source revisions and identify relevant security/compatibility fixes; the initial import lacks inherited upstream Git ancestry, so do not treat `git merge upstream/main` as safe without establishing compatible ancestry.
3. Port selected changes on a scoped branch with upstream attribution and a changelog of GoreeCloud-specific deviations.
4. Run regression, authentication, access control, sync, backup/restore, migration, and API tests. Require exact-head CI/review before merging.
5. Document upstream update decisions, including intentionally deferred fixes and associated risk. Do not enable automatic uncontrolled upstream merges.

## GoreeCloud platform systems

Assess each system against its current canonical contract: GoreeCloud Manager, Privacy Shield, Wardveil Security, Everkeep, Glaze, GoreeCloud Mesh, GoreeCloud Identity, GoreeCloud Policy, and GoreeCloud Observability.

**No system is presumed integrated merely because it appears above.** Feature implementations must be exercised in real workflows before being marked complete.

## Engineering safeguards

- Retain Apache-2.0 notices and audit all bundled third-party licenses. The distinct upstream web frontend is AGPL-3.0 and is not included in this source import.
- Preserve accounts, file contents, metadata, version history, permissions and share links throughout migrations, and validate restoration and reversible changes.
- Do not rename Go module paths, change storage formats or rewrite runtime architecture merely for cosmetic branding.
- Test OIDC, WebDAV/Graph endpoints, sharing, revocation, quotas, upload interruptions, large-file handling, concurrent edits and conflict resolution.
- Keep example passwords, certificates and insecure development configurations out of deployed environments; never assume upstream defaults are hardened.
- Ensure the GoreeCloud experience is substantively designed and functional rather than a logo-only reskin. Run screenshot-led UI audits when evaluating user interfaces.

## Governance discrepancy to resolve

The owner's explicit designation for GoreeCloud Drive is **GoreeCloud Fork**. The current cross-product `Policy — Native Application and Platform System Conformance` v3.2 describes only **Native** and **Fork-to-Native** as approved permanent development pathways. The current product direction and that policy conflict. This document records the owner's direction, **not** a claim that global policy has already been revised. Reconcile through the authorized governance process before making contradictory portfolio-wide claims.

**Stable release is not assumed** from a successful upstream import or from documentation changes.
