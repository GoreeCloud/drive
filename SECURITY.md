# GoreeCloud Drive — Security Policy

## Scope and maturity

This is a GoreeCloud-maintained fork of [OpenCloud](https://github.com/opencloud-eu/opencloud). Its current source and CI checks **do not constitute certification of production security**. Use an up-to-date reviewed upstream commit and apply platform-specific mitigations.

## Reporting a vulnerability

Report vulnerabilities affecting this fork privately using GitHub's **Report a vulnerability** feature, **if enabled**, or by contacting **admin@goreecloud.com**. Do not put tokens, personal files, exploitable details, or credentials in public issues or pull requests. For vulnerabilities shared with the upstream codebase, coordinate responsibly with [OpenCloud's upstream security process](https://github.com/opencloud-eu/opencloud/security).

No response time, bounty, or coordinated disclosure window is promised without an explicit published policy.

## Minimum operational baseline

### Deployment and networking

- Use a dedicated unprivileged service identity, isolation boundaries, and persistent data volumes. Avoid privileged containers and host-level mounts beyond demonstrated need.
- Restrict admin panels and diagnostics behind private VPN/access controls. Expose only intended application ingress over authenticated HTTPS; validate redirects, forwarded headers and public URL.
- Configure TLS, secure session cookies, trusted identity-provider issuers, narrow redirect origins, and appropriate request size/rate limits in the actual ingress stack.
- Turn off debug modes, sample users, developer login shortcuts, and permissive CORS outside trusted development.
- Keep secrets out of Git, CI logs, container image layers and sample configuration. Rotate any compromised credential.

### Data protection

- Define storage ownership and quotas. Encrypt off-host backups where appropriate, restrict access and retention, and rehearse recovery in an isolated environment.
- Verify authorization across tenants, user roles, public links and sharing revocation. Test WebDAV, uploads, downloads and archive extraction against path traversal and oversized payloads.
- Capture audit events without logging file content, credentials, bearer tokens or unnecessary personal information.

### Supply chain

- Pin production release source revisions and image digests. Track OpenCloud and third-party security advisories; run dependency, code, container and secret scans at every release boundary.
- Keep the upstream Apache-2.0 license, notices, module paths and attribution intact. Reconcile upstream changes deliberately, not by blind auto-merge.
- Require source review, branch isolation, test evidence, restore evidence and rollback readiness before changing production.

## Release acceptance

A release is **not** production-approved until required builds, security scans, HTTPS/authentication acceptance, backup/restore, accessibility checks, deployment rollback and operational monitoring have been verified on the intended environment and the evidence recorded. A successful static CI job is only a limited check.
