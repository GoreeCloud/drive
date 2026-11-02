# GoreeCloud Drive private-development ingress acceptance (review only)

**Status:** BLOCKED / design-and-evidence checklist only. This document does not approve a listener, change NetBird/AdGuard/Caddy, create DNS, start Drive, or authorize release. Applies solely to `drive-dev.goreecloud.com` in draft PR #4; production `drive.goreecloud.com` is separate.

## Source authority and evidence boundary

- Canonical GoreeCloud instructions: `GoreeCloud/GoreeCloud-Instructions.md` in the authorized GoreeCloud Google Drive.
- Application/service routing requirement: private `*-dev.goreecloud.com` addresses use Caddy or GoreeCloud Gateway, authenticated NetBird/GoreeCloud VPN access, and private AdGuard Home/GoreeCloud DNS rewrites. A hostname pattern does **not** authorize public DNS or public backend ingress.
- Live checks on **2026-11-02**, from authorized VPS01 and laptop, are dynamic snapshots, not continuing guarantees. The VPS01 NetBird client reported management/signaling connected, `100.71.27.119/16` on `wt0`, and a P2P connection to the laptop `100.71.238.171`. The laptop reported the exact VPS01 peer connected and a NetBird nameserver `100.71.27.119:53` available; `resolvectl` resolved `drive-dev.goreecloud.com` to `100.71.27.119` via `wt0`.
- The VPS01 socket inventory still had wildcard IPv4/IPv6 listeners on `:443`, plus a pre-existing private-address listener on `100.71.27.119:3000`. Neither proves a Drive-specific ingress boundary or service identity. The laptop's normal, certificate-verifying HTTPS request failed with a TLS internal-error alert and HTTP 000. **Trusted HTTPS is NOT READY.**
- VPS01 reported **two connected NetBird peers**, including the laptop and a phone. A connected peer is **not** automatically an authorized Drive-dev client. There is no demonstrated per-peer Drive ingress policy or negative unauthorized-peer test.
- Earlier combined firewall/AdGuard inspection was rejected by remote-provider safety controls. Do not retry that blocked action or infer an ACL or DNS-rewrite verdict from the absence of evidence.

## Required design decisions and independently verifiable acceptance

| Gate | Evidence required before any active route | Current result |
| --- | --- | --- |
| Identity | Record the exact intended client peer identity and VPS01 gateway peer identity from authorized, fresh NetBird control-plane **and** endpoint state; distinguish connectivity from policy authorization. | Endpoint connectivity observed; management policy authorization **unverified**. |
| Peer-specific network policy | Through a provider-supported, authorized **read-only** policy view, independently verify a narrowly scoped NetBird management ACL (source peer/group, destination gateway and service port, protocol) and effective server/gateway enforcement. Require explicit denial for all other VPN peers and public-origin traffic; do not treat `remote_ip`, a CGNAT CIDR, or a connected container as authorization. | **BLOCKED / unverified**. |
| Listener design | Select a dedicated private-interface HTTPS ingress design that cannot be reached from the public interface. The existing shared wildcard `:443` listener conflicts with assuming an independent `100.71.27.119:443` binding; no new listener or public Caddy change is authorized. Validate proposed port/IP with `ops/tests/probe_drive_dev_listener.py` and independent socket/service-ownership evidence. | **Not designed/approved**. |
| DNS provenance | In an authorized AdGuard Home/GoreeCloud DNS **read-only** view, confirm the exact rewrite, active private resolver, and NetBird distribution to the intended client; independently confirm private answer via `wt0` and absence of a public `drive-dev` record. A working answer alone is insufficient provenance. | Resolver path observed; authoritative rewrite **unverified**. |
| Trusted TLS | From the authorized laptop, require successful default-CA/trust-store validation for `drive-dev.goreecloud.com`, correct SNI/hostname, certificate chain, and HTTPS protocol. No `-k`, `--insecure`, trust bypass, or automatic live certificate issuance. | **FAIL**: TLS alert/internal error. |
| Negative authorization | From separately authorized, safe test vantage points, verify intended peer succeeds **only after** gates, unauthorized VPN peer is denied, and public-origin traffic cannot reach the dev backend. Do not use broad scans or start an application to manufacture a pass. | **Not tested**. |
| Isolation and recovery | Independently verify non-production credentials, separate data/metadata/storage, no production tokens, encrypted off-host backup, isolated restore, and owner/security acceptance. | **Unverified**. |
| Release/security | Resolve PR #3 binary/symbol reachability, IDP/frontend and container/OS scans, integration, authentication, rollback and restore gates before any deployment. | **OPEN**. |

## Safe next evidence collection

Use only individually permitted, bounded read-only NetBird management-policy and gateway-ingress evidence sources; a provider refusal is a hard stop for that action. Independently review the AdGuard/GoreeCloud DNS rewrite through an authorized read-only source, and propose a private-interface listener design **on paper** that does not conflict with the shared wildcard Caddy listener. Re-run the existing read-only peer/DNS/listener probes from authorized devices as conditions change; CI synthetic self-tests are not live ACL or TLS acceptance.

**Hold:** keep PR #3 and PR #4 draft/unmerged. No public DNS, active reverse proxy, backend exposure, Drive initialization, app start, deployment, live Caddy/DNS/NetBird/firewall change, credential exposure, or production alteration.
