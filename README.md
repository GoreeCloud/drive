# GoreeCloud Drive

**GoreeCloud Drive** is GoreeCloud's self-hosted file storage, synchronization, sharing, and collaboration platform. This repository follows the **Fork-to-Native** development path, initially importing the Apache-2.0-licensed [OpenCloud server](https://github.com/opencloud-eu/opencloud) while progressively establishing GoreeCloud-owned product and architecture boundaries.

> **Development status — foundation import.** This source import is not a Stable release, deployment, completed Glaze integration, or completed native conversion. Review security settings before using any real data.

## Source and architecture

- **Product:** GoreeCloud Drive.
- **Canonical repository:** [GoreeCloud/drive](https://github.com/GoreeCloud/drive).
- **Upstream foundation:** [opencloud-eu/opencloud](https://github.com/opencloud-eu/opencloud).
- **Current architecture:** inherited Go backend and services; upstream module paths are intentionally retained during initial import for compatibility.
- **Web frontend:** the OpenCloud Vue/TypeScript web project is maintained [separately](https://github.com/opencloud-eu/web) and is under AGPL-3.0; the server's own LICENSE is Apache-2.0. Review component-specific licensing before modifying or distributing bundled components.
- **Provenance and development gates:** [docs/UPSTREAM.md](docs/UPSTREAM.md), [docs/FORK-TO-NATIVE.md](docs/FORK-TO-NATIVE.md), and [docs/UPSTREAM-README.md](docs/UPSTREAM-README.md).

## Build the inherited server

The initial import preserves upstream build mechanics. From the repository root, with the Go toolchain and generation dependencies installed:

```bash
make generate
make -C opencloud build
```

The expected development binary is `opencloud/bin/opencloud`. For a **local, isolated test installation only**, follow the [upstream development instructions](docs/UPSTREAM-README.md) to initialize and run the service. The initial upstream configuration may not meet production security requirements; do not expose it to the public internet or use live credentials/data before hardening and verification.

## GoreeCloud direction

The program's next milestones are (1) reproducible backend builds and security baseline, (2) preservation inventory and test coverage, (3) approved GoreeCloud identity and Glaze interface without feature regression, (4) GoreeCloud-owned integrations and API boundaries, and (5) incremental, tested replacement of strategic inherited components. These are planned milestones, **not shipped claims**.

Source changes must preserve upstream attribution, important user capabilities, data continuity, accessibility, and rollback paths. Avoid rewriting Go module paths or storage formats as a branding shortcut.

## License and upstream acknowledgements

The imported server is based on OpenCloud and retains the upstream [Apache License 2.0](LICENSE), original source copyright notices, and licenses for included third-party dependencies. GoreeCloud Drive is an independent derivative development project, not an official OpenCloud release or an assertion of upstream endorsement.
