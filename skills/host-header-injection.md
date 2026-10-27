---
name: host-header-injection
description: Test whether the app trusts the Host / X-Forwarded-* headers in security-sensitive ways (password reset, cache, routing, SSRF).
category: infra
triggers: ["host header", "host injection", "x-forwarded-host", "password reset host"]
status: active
---

# Host Header Injection

When the server builds links, routes, or decisions from the incoming `Host` /
`X-Forwarded-Host` header, an attacker can poison them. The classic high-impact
case: **password-reset link poisoning** → account takeover.

## Attack model
- **Asset:** reset/verification links, cache keys, routing/trust decisions derived from the host.
- **Authority decision:** should the server trust a client-supplied host header to build security-sensitive output?
- **Attacker input:** `Host`, `X-Forwarded-Host`, `X-Forwarded-Server`, `X-Host`, `Forwarded`, duplicate Host headers, absolute-URI request line.
- **Smallest proof:** the server emits/acts on your injected host in a security-sensitive context (a reset email pointing to your domain, a cache entry, an SSRF).

## Technique
- **Password-reset poisoning (highest value):** trigger a reset for your **owned** account with a poisoned `Host`/`X-Forwarded-Host: attacker.com`. If the reset email link points to `attacker.com` carrying the token → a victim clicking leaks their token to you → ATO. Test on your own account only; demonstrate the poisoned link, don't harvest others' tokens.
- **Header variants:** real `Host` changed, `X-Forwarded-Host` added, duplicate `Host`, absolute URL in request line, `Host: target.com:@attacker.com`, port injection.
- **Routing/vhost confusion:** does a changed Host reach a different internal app/admin vhost?
- **Cache poisoning via host:** host reflected in a cacheable response → see `cache-poisoning`.
- **Host-based SSRF:** does the backend fetch based on the header? → `ssrf`.

## Bypass ladder
Host → X-Forwarded-Host → Forwarded → duplicate/ambiguous Host → absolute-URI → port/userinfo
tricks. One at a time; check reset emails, redirects, cache headers, and any reflected host.

## Chain targets
Reset poisoning → **ATO**. Host reflection + caching → cache poisoning → stored impact.
Host-based routing → internal admin vhost. Host → SSRF.

## FP traps
- Host reflected in a non-security context (a harmless page title) → informational.
- Reset email that uses a **hardcoded** domain (ignores your header) = secure.
- Redirect to your host that carries **no** secret/token → low impact.
- A changed Host that just 400s / is rejected by the front proxy.

## Promotion / proof
- CONFIRMED: security-sensitive use of the injected host — a reset link to your domain carrying the token (own account), a poisoned cache entry, or an SSRF — reproduced 2x, with the raw request + the resulting email/response saved.
- Severity: reset-poisoning ATO = P1; cache/SSRF per their impact; bare reflection = P4.

## References
`cache-poisoning`, `ssrf`, `forgot-password`, `auth-bypass`,
`request-response-analyzer`; memory first.
