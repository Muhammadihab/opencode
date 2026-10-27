---
name: cache-poisoning
description: Test web caches for poisoning via unkeyed inputs — storing an attacker-controlled response served to other users.
category: infra
triggers: ["cache", "cache poisoning", "web cache", "x-forwarded", "cache key"]
status: active
---

# Web Cache Poisoning

A cache keys responses on some request parts (path, maybe query) but not others
(certain headers). If an **unkeyed** input influences the response, you poison
the cached copy that *other users* then receive. Test carefully — you're affecting
shared cache; avoid poisoning production pages broadly.

## Attack model
- **Asset:** the response other users receive from the cache.
- **Authority decision:** which request inputs are part of the cache key? Unkeyed inputs that change the response = the bug.
- **Attacker input:** unkeyed headers (`X-Forwarded-Host`, `X-Forwarded-Scheme`, `X-Host`, custom), sometimes query params/order.
- **Smallest proof:** a response you influenced via an unkeyed input is cached and served back on a clean request (cache HIT) — demonstrated safely on a non-critical, self-chosen cache buster.

## Technique
1. **Find the cache:** `Age`, `X-Cache: HIT/MISS`, `CF-Cache-Status`, `Cache-Control`, CDN headers.
2. **Identify unkeyed inputs:** add a cache-buster (`?cb=random`) to avoid poisoning real users; inject candidate headers (`X-Forwarded-Host: attacker.com`) and see if they reflect in the response.
3. **Confirm keying:** does the injected value persist on a second clean request to the same buster URL (HIT)? If yes → the input is unkeyed and poisoned.
4. **Assess impact:** reflected host → redirect/XSS/resource swap; reflected into script src → stored XSS (`xss`); reset/link poisoning (`host-header-injection`).
5. **Cache deception** (sibling): trick the cache into storing an authenticated page (`/account/profile.css` style path confusion) → another user reads cached private data.

## Safety discipline
- Always use a unique cache-buster so you poison **your** URL, not shared production paths.
- Don't poison high-traffic/critical endpoints. Prove the mechanism on a benign path.
- Clean up / note TTL so entries expire.

## Chain targets
Unkeyed host → reflected XSS served to all cache users (stored-like impact). Cache deception
→ private data exposure. Reflected script src → mass XSS.

## FP traps
- A header that reflects but is **keyed** (varies the cache) → not poisoning, each gets their own.
- Reflection with no exploitable sink (harmless text) → informational.
- `X-Cache: MISS` every time → not actually cached.
- Your own buster showing your value ≠ other users affected — prove the unkeyed persistence.

## Promotion / proof
- CONFIRMED: an attacker-influenced response served from cache on a clean request (HIT) with a real sink (XSS/redirect/data), reproduced 2x, with the poisoning request + the cached clean response saved. Demonstrate on a safe buster, not production at large.
- Severity: cache-poisoned XSS/redirect affecting users = P2; deception exposing private data = P1/P2; reflection-only = P3/P4.

## References
`host-header-injection`, `xss`, `request-response-analyzer`,
`exploit-chain-analysis`; memory first.
