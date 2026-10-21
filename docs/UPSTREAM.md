# Upstream provenance — GoreeCloud Drive

- **Product classification:** GoreeCloud Fork (owner-designated).
- **Upstream source:** https://github.com/opencloud-eu/opencloud
- **Imported branch:** `main`
- **Imported commit:** `61ae13a1fea0bb8a36bf4b96c1d222fc84aeaa9c`
- **Import date:** October 20, 2026
- **Import method:** pinned upstream source snapshot imported into the existing GoreeCloud/drive Git history. The original GoreeCloud/drive initial commit is retained; upstream Git commit ancestry is not embedded in the destination. This is a **source-code fork**, **not** a GitHub-hosted upstream-linked fork relationship (`isFork: false` at verification).
- **Imported server license:** Apache-2.0, retained in `LICENSE`.
- **Separate upstream web client:** https://github.com/opencloud-eu/web (AGPL-3.0). This import does not include or fork that separate repository.
- **Canonical product repository:** https://github.com/GoreeCloud/drive
- **Upstream Git URL:** https://github.com/opencloud-eu/opencloud.git

This file records attribution and a reproducible source baseline. **GoreeCloud Fork** means GoreeCloud independently maintains a derivative of OpenCloud, reviewing and incorporating applicable upstream security and feature updates while adding GoreeCloud improvements. This project has no requirement to replace its entire inherited backend with a new native implementation.

Upstream changes are reviewed, tested and selectively integrated rather than blindly synchronized. Record both upstream SHA and GoreeCloud revisions, preserve appropriate copyright and third-party notices, and reassess distribution duties when updating or removing bundled components. Do not delete/recreate the repository merely to change its GitHub-native fork status.

The initial repository's `README.md` is the GoreeCloud landing page; the unchanged upstream README from the pinned import is retained in `docs/UPSTREAM-README.md` for technical guidance. The fork maintenance policy and acceptance plan are in `docs/GOREECLOUD-FORK.md`.

A [read-only OpenCloud source/release/security advisory watch](UPSTREAM-WATCH.md) records a dated public baseline, provides offline regression tests and reports upstream changes for review. It does not automatically incorporate fixes, certify security or replace deployment-specific vulnerability assessments.

**Release boundary:** The source import does not prove deployed, secured, web-client-integrated, GoreeCloud UI-compliant, or production-ready functionality.
