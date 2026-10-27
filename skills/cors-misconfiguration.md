---
name: cors-misconfiguration
description: Test CORS policy for origin-reflection/trust flaws that let a malicious site read authenticated cross-origin responses.
category: infra
triggers: ["cors", "access-control-allow-origin", "cross-origin", "wildcard origin"]
status: active
---

# CORS Misconfiguration

CORS is only a vuln when a malicious origin can **read a sensitive authenticated
response** cross-origin. A permissive header alone is not a finding — you must
prove data exposure with credentials. This is a frequently over-rated class; be
strict.

## Attack model
- **Asset:** sensitive data in an authenticated cross-origin response (tokens, PII, account data).
- **Authority decision:** should *this* origin be allowed to read responses that carry the user's credentials?
- **Attacker input:** the `Origin` header.
- **Smallest proof:** a browser PoC from an attacker origin reads a victim's authenticated response (requires `Access-Control-Allow-Credentials: true` + a reflected/overly-broad origin on a sensitive endpoint).

## Technique
1. Send requests to sensitive, credentialed endpoints with varying `Origin`:
   - `Origin: https://attacker.com` → reflected in `Access-Control-Allow-Origin`?
   - `Origin: null` → allowed? (sandboxed iframe can send `null`).
   - Subdomain / suffix tricks: `https://victim.com.attacker.com`, `https://attacker-victim.com`, trailing-dot, pre/suffix matches.
2. Check `Access-Control-Allow-Credentials: true` — **required** for a credentialed read to matter. Wildcard `*` + credentials is spec-invalid (browsers block) → usually NOT exploitable.
3. If origin is reflected AND credentials true AND endpoint returns sensitive data → build a browser PoC that reads the response from the attacker origin.

## The exploitability gate (critical)
- `ACAO: *` **without** credentials → public data → NOT a vuln.
- Reflected origin **without** `ACAC: true` → attacker can't send cookies → usually NOT exploitable.
- Permissive CORS on a **non-sensitive/unauthenticated** endpoint → informational.
- Only reflected-origin + credentials + sensitive authenticated data = real.

## Chain targets
CORS read of an API that returns tokens/CSRF → session theft → ATO. CORS + sensitive
export endpoint → data exposure.

## FP traps
- Wildcard `*` alone (no creds) — the most common false "CORS bug." Not exploitable.
- Reflected origin on a public/static endpoint.
- `ACAC: true` with `*` — browsers reject; not exploitable as-is.
- Preflight allowed but the actual response has no sensitive data.

## Promotion / proof
- CONFIRMED: a working browser PoC (saved HTML) reading a victim's authenticated sensitive response from the attacker origin, reproduced 2x, with the request/response headers + PoC saved.
- Severity: credentialed sensitive-data read = P2; otherwise Informational/P4 — do not inflate.

## References
`request-response-analyzer`, `host-header-injection`, `cache-poisoning`,
`exploit-chain-analysis`; memory first. Per `prioritization.md`, CORS is P4 until a browser PoC reads sensitive cross-origin data.
