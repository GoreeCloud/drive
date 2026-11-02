# GoreeCloud Drive — backup, restore and storage gates

**Status:** Operator procedure, **not** evidence of a production backup. This document applies to the GoreeCloud production-track fork based on upstream OpenCloud v7.2.4.

## Why this is a hard release gate

OpenCloud may keep metadata in POSIX extended attributes (`user.*`) or adjacent metadata files. A plain file copy that drops extended attributes is not a reliable restore. OpenCloud's backup guidance requires a consistent point in time: stop the OpenCloud application or use an application-consistent storage snapshot, then back up **configuration and all relevant data**. The search index may be rebuilt after a recovery if omitted, but identity material, file metadata, and blobs must not be omitted.

Sources: [OpenCloud backup guidance](https://docs.opencloud.eu/docs/next/admin/maintenance/backup/), [PosixFS metadata](https://docs.opencloud.eu/docs/next/admin/configuration/storage/storage-posix/), and [production considerations](https://docs.opencloud.eu/docs/next/admin/getting-started/container/docker-compose/docker-compose-production-considerations/).

## Gate A — inventory and ownership

1. Identify the *actual* container/stack, config bind mount, data bind mount, user-data filesystem, and every external storage backend. Do not assume paths from this document describe an already-running deployment.
2. Confirm both persistent volumes are readable by the dedicated runtime user, are not publicly shared, and have enough free capacity for the expected uploads and version history. Establish disk and inode alerts **before** general availability, especially if the application shares the OS disk with unrelated services.
3. Confirm the backup destination is **off-host**, encrypted, under least-privilege credentials, supports retention/immutability as appropriate, and is independently recoverable if the VPS is lost. Store the key/recovery instructions separately from the server.

## Gate B — encrypted backup

1. Schedule a maintenance window or obtain a verified application-consistent snapshot. For a non-snapshot backup, **stop only the Drive application** through its approved Compose project; do not interrupt unrelated GoreeCloud services.
2. Use a verified backup program that preserves relevant POSIX metadata including xattrs, ACLs, ownership, modes, files, directory structure, and symbolic links. For a pure POSIX setup, cover the complete configuration and data trees, not just user-upload blobs. Include a source commit and container image digest in the protected backup manifest.
3. Transfer the encrypted archive/snapshot to the off-host destination; verify the copy is complete and decryptable without relying on credentials stored only on the VPS.
4. After backup integrity validation, restore the application to its prior operational state using the approved runbook, and inspect logs/health for regressions.

**Do not** back up a changing OpenCloud filesystem merely by running `tar` on live bind mounts. Do not put unencrypted archives or secrets into GitHub, public object storage, email, or shared folders.

## Gate C — actual restore acceptance

1. Use an **isolated** restore target; never overwrite live configuration, encryption keys, identity records, or user data to test recovery.
2. Restore full config and data at a compatible pinned image revision. Verify ACLs/xattrs and ownership, as well as file counts/hashes for a sample of real data under authorized access.
3. Confirm authentication, identities, permissions, user files, version metadata, sharing and uploads/downloads. Run OpenCloud's built-in storage consistency checker where applicable.
4. Record date, operator, source image digest, backup snapshot ID, destination, elapsed restore duration, acceptance evidence, and residual risks. Only then can the backup/restore gate be marked **passed**.

## What is automated now

`python3 ops/tests/test_archive_metadata.py` creates *synthetic, disposable* data and confirms that a GNU tar archive preserves a file's bytes, `user.*` extended attribute, file mode, and config fixture after extraction. The test does **not** back up any GoreeCloud files and does not validate off-site encryption, scheduling, a running application or real-world restoration.

## Preconditions that remain open

No off-host backup repository, recovery key custody, retention schedule, successful full restore, or production storage quota has been verified for GoreeCloud Drive. Do not represent the synthetic test as satisfying those requirements.
