# GoreeCloud Drive

**GoreeCloud Drive** is GoreeCloud's self-hosted file storage, synchronization, sharing, and collaboration platform. This project is an owner-designated **GoreeCloud Fork** of the Apache-2.0-licensed [OpenCloud server](https://github.com/opencloud-eu/opencloud).

> **Development status — foundation import.** The OpenCloud-derived backend has been imported and compiled in development, but this is not a Stable release, deployed service, completed GoreeCloud UI experience, or verified production configuration. Review security settings before using real data.

## Source and architecture

- **Product:** GoreeCloud Drive.
- **Canonical repository:** [GoreeCloud/drive](https://github.com/GoreeCloud/drive).
- **Development approach:** Independently maintained **GoreeCloud Fork**. Continue improving the OpenCloud foundation, reviewing upstream fixes and releases, and developing GoreeCloud-specific features. **There is no mandatory native rewrite.**
- **Upstream source:** [opencloud-eu/opencloud](https://github.com/opencloud-eu/opencloud); the precise imported revision and licensing are recorded in [docs/UPSTREAM.md](docs/UPSTREAM.md).
- **Repository relationship:** Source was imported into an existing GoreeCloud repository. GitHub currently does **not** mark this repository as an upstream-linked GitHub fork; do not confuse source-code derivation with GitHub's `isFork` metadata.
- **Current architecture:** Go server and services derived from OpenCloud; upstream module names and protocol behavior remain intact for compatibility.
- **Web frontend:** The separate upstream [OpenCloud web client](https://github.com/opencloud-eu/web) is AGPL-3.0, and **has not been imported** into this server repository. Evaluate web-client licensing, architecture, and build independently.
- **Maintenance and quality:** [docs/GOREECLOUD-FORK.md](docs/GOREECLOUD-FORK.md), [docs/UPSTREAM.md](docs/UPSTREAM.md), and the [preserved upstream README](docs/UPSTREAM-README.md).
- **GoreeCloud UI developer preview:** An [opt-in GC UI Foundations theme](docs/GC-UI-FOUNDATIONS-THEME.md) supplies tested light/dark semantic colors through the existing web theme handler; the official Drive visual identity and full web-client UI adoption are not yet complete.

## Build the imported server

The initial import preserves upstream build mechanics. With the Go toolchain and generation dependencies installed:

```bash
make generate
make -C opencloud build
```

The upstream development binary is `opencloud/bin/opencloud`; its inherited CLI naming is intentional until renaming is separately implemented and compatibility-tested. For **local isolated development only**, follow the [upstream development instructions](docs/UPSTREAM-README.md). Do not publicly expose default development configurations or use live credentials or data before security and deployment validation.

## GoreeCloud fork development

Preserve and improve OpenCloud's existing capabilities; apply the approved GoreeCloud visual identity and GoreeCloud UI where implemented; strengthen security, reliability, privacy, and accessibility; integrate approved GoreeCloud platform capabilities; and maintain a reviewable path for upstream security updates and fixes. Upstream code is a foundation to maintain, not a temporary architecture that must be rewritten.

All changes must preserve upstream attribution, relevant third-party licenses, user data, sharing behavior, API/client compatibility, and rollback paths. **Do not claim features, integrations, tests, or deployments without evidence.**

## Licensing and acknowledgement

The imported server is based on OpenCloud and retains its upstream [Apache License 2.0](LICENSE), original copyright notices, and licenses for bundled third-party dependencies. GoreeCloud Drive is an independent derivative project, not an official OpenCloud release and not endorsed by OpenCloud.
