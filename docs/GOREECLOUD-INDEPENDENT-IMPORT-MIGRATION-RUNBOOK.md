# GoreeCloud Drive — Independent-Import Migration Safety Runbook

> **Status: NO-GO for detachment or replacement.** This is a repository-specific, review-stage engineering procedure. It is **not** approval to leave a GitHub fork network, delete or recreate this repository, force-push refs, merge PRs, or deploy Drive. No backup or migration is asserted by this document.

## Scope and source of authority

GoreeCloud's founder prefers independently maintained GitHub **source imports**, rather than GitHub fork-network relationships, for control of repository lifecycle and upstream continuity. The canonical policies remain the existing [technology provenance directive](https://drive.google.com/file/d/1K8S2M7a9PeufY0qNmM51Y0v2KC7fF5Cj/view) and [repository maintenance directive](https://drive.google.com/file/d/1H32dxodw-ehoNhRjKleY_8eZKJgO6AgZ/view) in the authorized GoreeCloud Google Drive. This document is a subordinate technical migration plan, **not** a duplicate governing policy.

An independent repository is still an attributed derivative of [OpenCloud](https://github.com/opencloud-eu/opencloud), not code independently written from scratch. Copyright, Apache-2.0 obligations, notices, third-party dependencies, security reviews, and upstream provenance survive any GitHub topology change. Independence also does **not** replace off-host backups, permissions hygiene, or disaster recovery. A public GitHub fork is already a separate repository; do not falsely claim it vanishes whenever its public upstream is deleted.

## Verified baseline — November 7, 2026 (read-only GitHub API)

- Repository: `GoreeCloud/drive`; public GitHub **fork** with parent/source `opencloud-eu/opencloud` (`fork: true`), default branch `main`.
- Approximate repository metadata size: 328,621 KiB (about 321 MiB); 0 child forks reported; 1 star. These observations are not proof the self-service detach option is available.
- Six branches and the corresponding commit IDs at inspection time:

| Branch | Observed tip SHA |
| --- | --- |
| `main` | `50f4a4458a50ab5627271fd8789be6c8b19eb89e` |
| `release/goreecloud-7.2.4` | `f2f3e0c917ed41e369a6c7f6e76fd53d1b0e5044` |
| `dev/drive-dev-private` | `29a5d8947f010faa1812c92660cf73dbb1f42616` |
| `security/goreecloud-7.2.4-vuln-trial` | `30f8fbf0640a1381d01de6f6f3cb161aff923413` |
| `security/idp-frozen-pnpm-install-20261103` | `89b282043b220dea3cae7672a6b4e175008c40a8` |
| `test/drive-storage-headroom-fail-closed-20261102` | `6eb08ef8587ac526c434df7a9b67c25387f4eaa6` |

- 77 Git tag refs observed; no published GitHub releases observed. The tag count and ref set must be re-read immediately before any migration.
- Four open **draft** PRs at inspection: [#3 — Go dependency vulnerability remediation](https://github.com/GoreeCloud/drive/pull/3); [#4 — private development hostname](https://github.com/GoreeCloud/drive/pull/4); [#5 — storage threshold and filesystem preflight](https://github.com/GoreeCloud/drive/pull/5); [#6 — fail-closed IDP package lockfile validation](https://github.com/GoreeCloud/drive/pull/6). Do not close or merge these solely to enable detachment.
- GitHub's branch-protection endpoint returned `403 Resource not accessible by integration`; protection settings remain **unverified**.
- Repository Issues are disabled. GitHub Actions/history, PR reviews, branch rules, credentials, releases, and deployment links require their own complete audit; the above is **not** a full metadata inventory.

## Confirm the provider's destructive behavior

GitHub's [Detaching a fork](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/detaching-a-fork) documents that leaving a fork network is permanent and retains Git commit metadata **but not** associated pull requests, issues, wiki, stars, watchers, comments, child forks, or other metadata. The manual delete/recreate path likewise deletes existing PRs and configurations. This loss is relevant **even if every Git commit is correctly backed up**. Treat both paths as material-risk operations.

**Default decision: remain a fork for now.** First preserve and resolve legitimate development work through its own normal review process. If GitHub Support offers a different documented, metadata-preserving procedure, independently verify its scope and limitations; do not assume one exists.

## Gate A — authenticated, read-only preflight

1. Confirm the authorized GitHub identity is `GoreeCloud` associated with `admin@goreecloud.com`, admin permissions, the exact repository ID/name, default branch, visibility, and fork parent. Check repository size and whether there are child forks.
2. Freeze the migration *plan*, not ongoing unrelated development: capture a new dated repository snapshot before every migration attempt. Inventory **all** heads, annotated/lightweight tags, Git object integrity, PR source/base refs, protected branch/ruleset configuration, releases/assets, Actions workflows and artifacts, collaborator roles, integration identities, notifications, webhooks, GitHub Apps, deployment dependencies, package publication, and all repository URL backlinks.
3. Record PR comments, reviews, statuses/check runs, labels, approvals, discussions, and links separately using authorized API access. Ensure personal details are handled under GoreeShield privacy rules and secrets/credentials under Wardveil controls. Do **not** export secret values or publish webhook payloads/tokens.
4. Verify the pinned OpenCloud source revision and license/NOTICE text, modifications, dependencies, vendored assets, and any obligations that remain when disconnected from the upstream network. No new relicensing of upstream code is implied.

## Gate B — independent, verifiable Git backup

Use a **private, access-controlled, disposable workspace with sufficient storage**. After reviewing the commands and choosing an actual approved backup destination, a read-only source capture can follow this outline:

```sh
umask 077
mkdir -p /approved/private/workspace
cd /approved/private/workspace
git ls-remote https://github.com/GoreeCloud/drive.git 'refs/heads/*' 'refs/tags/*' > source-refs.txt
git clone --mirror https://github.com/GoreeCloud/drive.git GoreeCloud-drive.git
git -C GoreeCloud-drive.git fsck --full
git -C GoreeCloud-drive.git show-ref > mirrored-refs.txt
git -C GoreeCloud-drive.git bundle create ../GoreeCloud-drive.bundle --all
git -C GoreeCloud-drive.git bundle verify ../GoreeCloud-drive.bundle
sha256sum GoreeCloud-drive.bundle > GoreeCloud-drive.bundle.sha256
```

These commands are **examples, not evidence they ran**. Check disk capacity, access permissions, actual refs, exit codes, and hashes. `--mirror` does not, by itself, guarantee recovery of GitHub PR conversations, workflow artifacts, Git LFS objects, packages, release files, protections, secrets, or all provider-specific refs. Inventory those assets separately. Keep backup archives encrypted/off-host under authorized retention, and test an **isolated** restoration; do not overwrite any production or existing repository. Do not run inherited upstream build scripts or hooks as part of a metadata-only backup.

## Gate C — compare migration options without changing production

| Option | Safety posture | Required decision |
| --- | --- | --- |
| Retain GitHub fork while preserving existing PRs | Default, no topology change | Continue regular reviewed development and independent backup coverage |
| GitHub 'Leave fork network' | Irreversible; repository metadata including PRs lost under provider's published behavior | Explicit founder acceptance of documented consequences after metadata preservation and recovery validation |
| Delete/recreate and mirror push | High risk of metadata, configuration, URLs, collaboration, and integrations being lost | **Not a default fallback**; separate explicit approval, verified alternatives analysis, recovery tests |
| Support-assisted alternative | Unknown availability or guarantees | Obtain specific written provider conditions before relying on it |

## Gate D — migration acceptance criteria

- [ ] Authorized approver explicitly accepts the **specific** procedure, timing, residual data/metadata loss, and rollback limitations.
- [ ] Off-host Git backup is complete, integrity verified, and restored in isolation; branch, tag, commit, Git LFS, and needed PR refs are accounted for.
- [ ] Every open PR (#3–#6 and any subsequent PR) is properly resolved or its complete source, review history, and owner decisions are captured and reconciled; no silent metadata loss.
- [ ] Repository integrations, Actions, rules/protections, GitHub Apps, deployment credentials **by reference only**, release assets, and source links have a documented restoration/reconfiguration plan.
- [ ] License, NOTICE, provenance, copyright, dependency and Wardveil/GoreeShield controls are accepted; the existing technical OpenCloud origin is transparently attributed.
- [ ] Changes are executed in an approved maintenance window with a stop/go decision; release branches, CI, test results, and app operation are independently validated after any change.
- [ ] The final live GitHub API reports the intended standalone topology (`fork: false`) **if migration was approved and actually completed**, with all required refs, permissions, integrations and CI verified; documented exceptions are signed off.
- [ ] Existing canonical Drive Markdown policies/inventory are edited **in place**, verified by Drive readback, and Todoist migration status updated only to match actual evidence.

## Stop conditions and non-goals

Stop before mutation if any backup/restore check fails, protection details are unavailable, active PRs cannot be preserved or appropriately resolved, an upstream/license obligation is unclear, or a required founder approval is missing. Git history restoration **cannot** resurrect lost GitHub issue/PR/stars/review metadata automatically. There is no safe 'undo' assumption for GitHub fork-network exit.

This runbook does not detach the fork, deploy the service, certify recovery or security, change the canonical Drive policies, or authorize publishing sensitive records. It creates a traceable, reviewable engineering gate only.
