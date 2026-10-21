# OpenCloud upstream/security watch — GoreeCloud Drive

**Status:** Active source-level maintenance mechanism after the associated
pull request is merged. It does not attest to Stable or production security.

As a maintained **GoreeCloud Fork**, Drive must detect and explicitly review
upstream changes. The canonical source is
[opencloud-eu/opencloud](https://github.com/opencloud-eu/opencloud).
The imported source revision and license are recorded in [UPSTREAM.md](UPSTREAM.md).

## Read-only daily check

The [upstream-watch GitHub Actions workflow](../.github/workflows/upstream-watch.yml)
runs once daily on the default branch and can also be launched manually.
It independently checks **both** the Apache-2.0 OpenCloud Go server and the
separately licensed AGPL-3.0 OpenCloud web frontend. A problem in either
check makes the combined workflow fail; neither repository is auto-upgraded.
It uses a read-only GitHub token and standard Python libraries. It neither
edits source nor creates PRs or upgrades dependencies automatically.

It reads the publicly available upstream:
- `main` commit SHA
- latest published release tag
- public security advisory IDs, severity and last-update timestamps

It compares all three to the versioned, dated
[UPSTREAM-WATCH.json](UPSTREAM-WATCH.json). Any new/different commit,
release or advisory record produces a nonzero workflow result with public
identifiers requiring manual review. Network failures also fail closed as
**unverified**; they are not treated as a clean upstream result.

The watcher does not evaluate all transitive vulnerabilities, private
advisories, deployment settings, proprietary dependencies, exposure,
or remediation efficacy. An unchanged upstream SHA or known advisory list
is **not** evidence that GoreeCloud Drive is secure.

## Reviewed server baseline (October 21, 2026 UTC)

- Imported OpenCloud upstream SHA:
  `61ae13a1fea0bb8a36bf4b96c1d222fc84aeaa9c`
- Latest published upstream server release: `v8.1.0`
- Observed public advisories:
  - `GHSA-gf4p-7p27-26w7` — medium severity; internal metadata access
  - `GHSA-vf5j-r2hw-2hrw` — high severity; public link issue

These published advisories list affected *historical* release ranges
(older than the current 8.1 line), but **inclusion in the baseline is
not remediation proof**. The actual fork, its dependencies and runtime
require independent security validation. This watch detects *new or changed*
public upstream advisory records, not active exploitation.

## Browser-source baseline

The complete upstream browser client is tracked separately at
[WEB-CLIENT-WATCH.json](WEB-CLIENT-WATCH.json). Its imported source revision
is `954dbee3ac5b428d1f42c6eeaf9184484d1cda43`, published release
`v8.1.0`, and the public GitHub security-advisory list was empty at the time
of verification. **An empty public advisory list is not a security audit.**
The watch detects changes in this independent frontend source/release/advisory
set without conflating the Apache-licensed server with AGPL browser code.

## Local validation and maintenance

Run offline comparator tests from the repository root:

```sh
python3 -m unittest discover -s scripts/tests -p 'test_check_*upstream.py' -v
```

Run a live check with an authorized GoreeCloud GitHub token:

```sh
GH_TOKEN="$(gh auth token)" python3 scripts/check_opencloud_upstream.py
GH_TOKEN="$(gh auth token)" python3 scripts/check_opencloud_web_upstream.py
```

After an alert, inspect the **actual upstream commits, release notes and
security advisory impact**, determine whether changes apply, integrate
selected patches through a reviewed feature branch, validate functional
regressions and data compatibility, and preserve rollback. Advance the
reviewed JSON baseline only with an accurate review record; updating the
baseline to silence an alert is not sufficient. Do not claim a fork is
synchronized until the source revision and fixes are actually integrated.

Scheduled workflows may be delayed or disabled by GitHub and do not provide
a guaranteed notification delivery channel. Check GitHub Actions status
when verifying maintenance coverage.
