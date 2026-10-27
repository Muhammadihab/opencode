---
name: jwt-security
description: Test JWT handling for signature bypass, algorithm confusion, weak secrets, and claim tampering.
category: auth
triggers: ["jwt", "json web token", "alg none", "kid", "bearer token"]
status: active
---

# JWT Security

A JWT is only as good as its signature verification. Bugs: the server accepts
unsigned/weakly-signed tokens, confuses algorithms, or trusts tampered claims.
Impact: forge any identity → auth bypass / privilege escalation.

## Attack model
- **Asset:** the identity/claims the token asserts (user id, role, tenant, scope).
- **Authority decision:** is this token's signature valid for a key the server trusts, and are its claims authoritative?
- **Attacker input:** the token — header, payload, signature.
- **Smallest proof:** a token you crafted (not legitimately issued for that identity) is accepted and authorizes a different/higher identity.

## Technique ladder
1. **Decode & inspect** (don't guess): header `alg`/`kid`, payload claims (`sub`, `role`, `tenant`, `exp`, `iss`, `aud`). Base64url-decode — no key needed to read.
2. **`alg:none`:** set header `{"alg":"none"}`, strip the signature — does the server accept it? (Classic, still found.)
3. **Algorithm confusion (RS256→HS256):** if the server uses RS256 (public key), re-sign the token with HS256 using the *public key as the HMAC secret* — if it verifies, you can forge anything.
4. **Weak HMAC secret:** if HS256, test a short list of common/weak secrets **offline** (never online brute on the target); if cracked, forge claims.
5. **`kid` injection:** `kid` header feeding a path/SQL/command — path traversal to a known file used as key, or injection (see `sql-injection`, `path-traversal`).
6. **Claim tampering:** without breaking the sig — does the server actually re-verify, or trust the payload? Flip `role`/`tenant`/`sub` and resend (catches servers that decode-without-verify).
7. **Expiry/replay:** is `exp` enforced? Does an old/revoked token still work? Cross-account token reuse.
8. **`jku`/`x5u`:** header pointing to a key URL → can you host your own key (SSRF-adjacent)? See `ssrf`.

## Bypass ladder
alg none → alg confusion → weak secret (offline) → kid injection → claim-trust test →
jku/x5u key injection → expiry/replay. One at a time; keep every crafted token.

## Chain targets
Forge `role:admin` → admin takeover. Forge `sub` → full ATO. `jku` → SSRF. Weak secret →
mint tokens for any user.

## FP traps
- Decoding a token proves nothing — anyone can read it. The bug is **acceptance** of a crafted one.
- The server rejecting `alg:none` / tampered claims = secure.
- Cracking a secret offline that's actually strong = you didn't crack it; verify the forged token is accepted.
- An expired token still "working" on a cached/static endpoint ≠ auth bypass.

## Promotion / proof
- CONFIRMED: a token you forged (different/elevated identity) is accepted for an authenticated action, reproduced 2x, with the crafted token + the authorized response saved. Never use real secrets you shouldn't have.
- Severity: forge-any-identity / role = P1; replay/expiry gaps = P2/P3 per impact.

## References
`auth-bypass`, `session-management`, `oauth-oidc-security`, `ssrf` (jku),
`path-traversal` (kid), `access-control-testing`; memory first.
