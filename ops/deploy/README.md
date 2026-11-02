# GoreeCloud Drive — staged production-track deployment

**Not an operational deployment.** This folder contains a non-secret deployment template for the GoreeCloud Drive fork's `release/goreecloud-7.2.4` branch (base OpenCloud v7.2.4). Neither a build nor a Compose configuration proves public readiness.

## Included files

- `compose.yaml` — a non-root, read-only, resource-bounded service using relative persistent config/data directories and an externally managed `proxy` network. It publishes **no** host port and does not provision Caddy or TLS.
- `env.runtime.example` — non-secret environment defaults verified against the source configuration annotations. The sample uses `drive.goreecloud.com`; customize this to the approved origin before any use. Copy privately to `.env.runtime`; do not commit that runtime file.
- `../BACKUP-RESTORE.md` — backup, metadata and restore acceptance protocol.
- `../monitor_storage.py` — read-only, machine-readable disk/inode headroom check, not a scheduler or quota.
- `../SECURITY-ADVISORIES.md` — targeted upstream advisory review and outstanding dependency/container scanning coverage.
- `../tests/test_archive_metadata.py` — **synthetic only** metadata round-trip test.
- `../tests/test_env_contract.py` — source-level validation of these example variable names and security flags.

## Repository security-monitoring snapshot (November 1, 2026)

Authenticated repository settings showed GitHub secret scanning and push protection **enabled**, while Dependabot security updates **disabled**. The Dependabot alerts API reported that alerts are disabled for this repository; no dependency-vulnerability triage could be verified through that facility. These settings may change later. A source or container build is not a substitute for vulnerability assessment, and the production release checklist must account for this gap. Do not claim dependency alerts or security updates are active until confirmed in the repository's current settings.

## Read-only storage headroom check

On a compatible Linux host with the *actual* persistent Drive data directory present, run:

```sh
python3 ops/monitor_storage.py --path /path/to/goreecloud-drive/data
```

Defaults are a minimum **20 GiB free**, **20% free filesystem space**, and **10% free inodes**. It prints one JSON object, returns exit code `0` for PASS, `2` for CRITICAL, and `3` for a filesystem error. It warns if the data directory shares the OS filesystem. A deliberate high threshold should produce `CRITICAL` when exercising negative-path tests.

**This is an on-demand check only.** Do not claim alerts are actively sent or quotas are enforced until a secured, authorized monitoring scheduler/receiver and capacity controls are configured and tested. Disk usage can change immediately after a check. The absolute/free-percent thresholds are temporary safeguards, not a substitute for capacity planning.

## Operator prerequisites and hold points

1. Verify the source checkout revision, image build exit code, image OCI labels and applicable vulnerability analysis. Build from the branded production branch rather than silently using an upstream image.
2. Establish dedicated capacity protections, appropriate filesystem xattr/ACL support, ownership matching the container UID/GID (currently 1001 in this example), and restrictive directory permissions. Never mount the Docker socket or expose its permissions to the application.
3. Generate a unique administrator credential in a **separate, permission-0600 init-only env**, initialize `/etc/opencloud` with certificate validation enabled, and verify `opencloud.yaml` exists in the persistent config volume. Keep the initial credential out of the runtime environment and out of source control.
4. Verify `docker compose -f compose.yaml config --quiet` **with a privately prepared `.env.runtime`** and confirm effective settings. Check that the application can write to its persistent data/config paths and required temporary paths. Startup, health check, user login and file operations have **not** been verified by these static instructions.
5. Establish encrypted **off-host** backup and perform a successful **isolated restore** of configuration, identity, metadata and file data as described in `../BACKUP-RESTORE.md`. Do not take a live `tar` of a changing data tree and call it a consistent backup.
6. Only after a successful private functional and recovery acceptance, attach to the existing reverse proxy through an authorized change process, validate Caddy, verify certificate issuance and test the public login, upload/download and sharing flows.

The built-in health probe observes HTTP reachability only; it does not prove authentication, authorization, storage durability or recovery.

**Important:** `OC_SHARING_PUBLIC_SHARE_MUST_HAVE_PASSWORD=true` and `OC_SHARING_PUBLIC_WRITEABLE_SHARE_MUST_HAVE_PASSWORD=true` require passwords on public share links. They do **not** disable link creation. Do not claim guest links have been disabled: `OC_ENABLE_GUEST_LINKS` is not a verified setting in the OpenCloud v7.2.4 source.

**Blocked release gates:** VPS first-run initialization and live Caddy mutation were previously rejected by the remote management safety controls. Do not use these templates to bypass such restrictions. The separate VPS staging environment and high-priority Todoist task record the live status.
