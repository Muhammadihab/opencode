---
name: ssrf
description: Test server-side request functions for SSRF — making the server fetch attacker-chosen internal/metadata/arbitrary destinations.
category: injection
triggers: ["ssrf", "url fetch", "webhook", "redirect", "callback", "import url", "fetcher", "metadata"]
status: active
---

# SSRF (Server-Side Request Forgery)

Any feature where the **server** fetches a URL you influence: webhooks, URL
imports, PDF/screenshot/preview generators, avatar-from-URL, link unfurlers,
file-from-URL, SSO metadata, integrations. Goal: redirect that fetch to internal
services, cloud metadata, or arbitrary hosts.

## Attack model
- **Asset at stake:** internal network, cloud metadata creds, internal admin APIs, the trust the backend places in "its own" requests.
- **Authority decision:** should the server fetch *this* destination on the user's behalf? It should allow-list; SSRF is when it doesn't.
- **Attacker input:** the URL/host/IP the server will request.
- **Smallest safe proof:** a callback to your **user-provided Burp Collaborator** domain tied to a unique marker, OR a raw response showing internal-only content (e.g. metadata JSON). Submission alone is **never** proof — see OOB discipline.

## OOB discipline (mandatory)
- Use ONLY the user-provided Collaborator domain recorded in the session bootstrap. None provided → **pause and ask**.
- **Never** curl/open the Collaborator yourself (false callback).
- Unique marker per target/endpoint/param/method/account/time.
- See `blind-vuln` for the full OOB workflow.

## Payload / bypass ladder (one variable at a time)
Start with a harmless canary to your Collaborator, then escalate scope only if it fires.
- **Baseline canary:** `http://<marker>.<collab>/` — confirms the server fetches at all.
- **Internal targets (only after canary fires):** `http://127.0.0.1/`, `http://localhost/`, `http://[::1]/`, internal ranges `http://169.254.169.254/` (AWS IMDSv1 metadata), `http://metadata.google.internal/` (GCP, needs `Metadata-Flavor: Google`), `http://100.100.100.200/` (Alibaba).
- **IP format bypasses** (for allow-list/deny-list evasion): decimal `http://2130706433/`, octal `http://0177.0.0.1/`, hex `http://0x7f000001/`, mixed, IPv6-mapped `http://[::ffff:127.0.0.1]/`, zero `http://0/`.
- **Scheme bypasses:** `file://`, `gopher://` (raw TCP — can hit redis/smtp), `dict://`, `ftp://` — test which the fetcher accepts.
- **Redirect chain:** point the URL at *your* server that 302-redirects to the internal target (bypasses front-door host checks that only validate the first URL).
- **DNS rebinding:** host that resolves public on first lookup, internal on second (TOCTOU between validation and fetch).
- **Parser confusion:** `http://allowed.com@127.0.0.1/`, `http://127.0.0.1#@allowed.com/`, `http://allowed.com.attacker.com/`, embedded CR/LF, `http://127.0.0.1:80\\@allowed.com`.
- **Placement variants:** if the body URL is filtered, try it in a header, a redirect target, file metadata (SVG/XML `SYSTEM`), or an imported document.

## Chain targets
Metadata endpoint → **cloud credentials** → account/infra compromise (P1). Internal
admin API reachable → privileged actions. Gopher → internal redis/db. Blind SSRF →
port-scan internal network via timing/status.

## FP traps
- **Collaborator hit from your own machine / scanner / the validation itself** — never counts. Only the *target's* egress IP counts.
- **The app fetches a preview client-side** (browser), not server-side → not SSRF.
- **DNS lookup only, no HTTP** — a DNS callback proves name resolution, not a full fetch; state exactly which you proved.
- **Open redirect ≠ SSRF** unless the server itself follows it server-side.
- Error "could not fetch" with no callback → no proof; record as LEAD, try alternate placement.

## Promotion / proof
- LEAD: canary fires from the target's egress once.
- CONFIRMED: reproducible callback with your unique marker from the target's IP, OR raw internal-only response body saved. For metadata/cred exposure, capture the response (redact the secret value, keep the key names + proof) under `evidence/`.
- Severity: internal/metadata/cred SSRF = P1; blind SSRF with only DNS = P3 until escalated.

## References
`blind-vuln`, `host-header-injection`, `file-upload` (SVG/XXE vectors),
`exploit-chain-analysis`, `cloud-security`; memory: `memory/targets/ssrf.md` (read first).
