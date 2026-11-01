# GoreeCloud Drive — production-track 7.2.4

**A self-hosted file, sharing, and collaboration platform for the GoreeCloud ecosystem.**

> **Branch provenance:** This maintenance branch starts at the official [OpenCloud v7.2.4 production release](https://github.com/opencloud-eu/opencloud/releases/tag/v7.2.4) (upstream commit `1770793f2657e153836c32d32dd6d256b8531d3d`) and applies GoreeCloud branding and security documentation. The `main` branch tracks a newer rolling/development line. Neither branch is proven production-ready without end-to-end deployment acceptance.


GoreeCloud Drive is the GoreeCloud-maintained **fork of [OpenCloud](https://github.com/opencloud-eu/opencloud)**. It retains OpenCloud's Go backend, services, protocols, dependencies, and Apache-2.0 licensing, with a scoped GoreeCloud UI branding layer. This is **not** a ground-up rewrite or an official upstream OpenCloud distribution.

> **Status — integration in progress.** This repository is public source code, **not evidence of a deployed or production-hardened service**. The intended address is [drive.goreecloud.com](https://drive.goreecloud.com); DNS, HTTPS, persistent storage, backups, first-run setup, and live service acceptance must be verified independently. Do not use it for irreplaceable data before recovery testing.

## What it does

The inherited OpenCloud platform provides browser file management, user identity, uploads and downloads, WebDAV-compatible access, file sharing, and other services supported by the particular upstream version. Specific features, clients, and production integrations should be tested against this fork rather than assumed from the upstream roadmap.

GoreeCloud-specific work in this repository:

- **GC UI-based brand theme:** GoreeCloud Drive name, slogan, light/dark semantic colors, responsive wordmark, and favicon. Design tokens are derived from [GoreeCloud UI](https://github.com/GoreeCloud/gc-ui/blob/main/tokens/gc.v1.tokens.json); visual and accessibility acceptance remains pending.
- **Secure maintenance baseline:** documented operational guardrails, a source-level branding check, and honest release-readiness guidance.
- **Upstream traceability:** the fork relationship, OpenCloud technical package names, original licensing, and third-party notices are preserved.

GoreeCloud-specific brand assets live in `services/web/assets/themes/goreecloud/assets/`. The embedded default theme is configured by `services/web/assets/themes/opencloud/theme.json`. Do not rename OpenCloud's Go module or internal service identifiers just to change the product name.

## Getting started — development

You need a supported Go/Node build toolchain and the tools referenced by the upstream Makefiles. Consult the [upstream development docs](https://docs.opencloud.eu/) for version-specific prerequisites.

```sh
make generate
make -C opencloud build
opencloud/bin/opencloud init
opencloud/bin/opencloud server
```

`init` creates local server configuration (typically under `~/.opencloud`). **Review generated credentials and configuration before any external exposure.** This developer flow alone is **not** a recommended public deployment configuration.

You can alternatively build from the included upstream `Dockerfile` (build-time tooling and resources required):

```sh
docker build --pull -t goreecloud-drive:local .
```

Pin the source commit and resulting image digest for any release. The Dockerfile retains upstream build tooling and image metadata for provenance; an image build is not proof of runtime readiness.

## Deploying safely

For production, use [OpenCloud's maintained deployment guidance](https://docs.opencloud.eu/docs/admin/getting-started/container/docker-compose/) and adapt it **outside the application source tree** to the approved GoreeCloud host and reverse proxy. Never commit `.env` files, OIDC client secrets, tokens, passwords, TLS private keys, or backup credentials.

Before exposing `drive.goreecloud.com`:

1. Confirm intended VPS, DNS authority, TLS certificates, firewall, reverse-proxy and origin configuration. Make administrative interfaces private.
2. Initialize a unique admin account and persistent config/data volumes with least-privilege permissions. Disable test/demo settings and insecure authentication shortcuts.
3. Review OpenID Connect issuer, redirect URI and cookie/session security for the final HTTPS origin.
4. Establish encrypted, access-controlled backups **and demonstrate restore** of files, identities, configuration, and encryption keys as applicable.
5. Validate upload/download, WebDAV, sharing permissions, authorization boundaries, account recovery, restarts, storage exhaustion, logs, health checks, and rollback.
6. Complete desktop/mobile accessibility and GC UI visual acceptance before calling the service stable.

The planned public URL must not be interpreted as a live-service health claim.

## Security

Read [SECURITY.md](SECURITY.md) for reporting and the GoreeCloud operational hardening checklist. The new source-level checks do not replace dependency scanning, SAST, container/image scanning, authentication tests, penetration testing, or a verified disaster-recovery rehearsal.

If you discover a vulnerability in **the underlying OpenCloud project**, also follow the [upstream responsible disclosure guidance](https://github.com/opencloud-eu/opencloud/security). Avoid publishing an exploit or secrets in a public issue.

## Development and upstream updates

- **Primary branch:** `main`. Make reviewable changes on short-lived branches and check tests before merging.
- **Upstream:** [opencloud-eu/opencloud](https://github.com/opencloud-eu/opencloud); review upstream releases, migrations, advisories, and conflicts before synchronizing.
- **Brand authority:** [GoreeCloud UI](https://github.com/GoreeCloud/gc-ui) — shared design requirements, tokens, and acceptance evidence.
- **Operational scope:** configuration and deployment may live in private infrastructure. This public source repository intentionally contains no production secrets.

See upstream [CONTRIBUTING.md](CONTRIBUTING.md) for general code conventions; GoreeCloud-specific policy must be followed for changes in this fork.

## Credits and license

GoreeCloud Drive is **derived from OpenCloud, developed by the OpenCloud community**. OpenCloud and its contributors retain credit for their work. This fork is independently maintained by GoreeCloud and is not endorsed by OpenCloud GmbH. Existing copyright notices and licensing are preserved; source is distributed under the applicable [Apache License 2.0](LICENSE) and third-party licenses.

Original upstream project: https://github.com/opencloud-eu/opencloud
