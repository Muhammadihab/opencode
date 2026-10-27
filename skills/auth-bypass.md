---
name: auth-bypass
description: Test authentication flows (login, registration, session) for bypasses, logic flaws, and takeover preconditions.
category: auth
triggers: ["login", "auth", "authentication", "signin", "sign in", "register", "signup", "bypass"]
status: active
---

# Authentication Bypass & Logic

Auth bugs live in the **edges**: recovery, fallback, alternate flows, state
transitions — not the happy path. Use ONLY the owned account from `login.md`;
read OTPs/links from its inbox. Never brute-force, never touch third-party accounts.

## Attack model
- **Asset:** the identity boundary — becoming someone else, or authenticated without valid credentials.
- **Authority decision:** did this request prove possession of valid credentials / a valid session for *this* identity?
- **Attacker input:** credentials, tokens, session artifacts, the flow's step order.
- **Smallest proof:** reaching an authenticated response/action without completing legitimate auth, shown by a raw request + the authenticated body.

## Surfaces & techniques

### Login logic
- **Response/flow confusion:** does a failed login still set a session cookie or return a token? Compare success vs failure response-diff.
- **Forced browsing:** request a post-login page/endpoint directly with no/partial session — is it served?
- **SQLi (low-impact only on login):** `' OR '1'='1' -- ` style as a *logic* probe, single careful attempts, documented — not a credential list. See `sql-injection`.
- **Account enumeration:** different response/timing for valid vs invalid username (feeds other attacks; P3 alone).
- **Password/username case & unicode:** `Admin` vs `admin`, trailing space, unicode normalization collisions.

### Session & tokens (see `session-management`, `jwt-security`)
- Session fixation: does the pre-login session ID survive login? Reuse after logout?
- Token in predictable/forgeable form; missing expiry; reuse across accounts.
- Cookie flags (HttpOnly/Secure/SameSite) — note but don't over-rate without impact.

### Registration
- Register an existing email (collision → takeover precondition).
- Skip email verification: is the account usable before verifying? Can you change email post-verify without re-verifying?
- Mass-assign role/privilege fields at signup (`"role":"admin"`, `"isVerified":true`). See `access-control-testing`.

### Multi-step / MFA / recovery (see `forgot-password`, `rate-limiting`)
- Skip or reorder steps (go straight to step 3's endpoint).
- Replay a one-time token; use a token issued for A on B's flow.
- MFA: is the post-password-pre-MFA state already authenticated for any endpoint?

## Bypass ladder
Identity/state (fresh vs stale session, second owned account) → method/path (force-browse,
HTTP method swap) → parser (duplicate params, token in header vs body) → workflow
(skip/reorder/replay steps) → platform variants (mobile API, legacy `/v1/` login, SSO vs
password path).

## FP traps
- A set-cookie on failure that is **not** a valid session (test if it actually authorizes anything).
- "Bypass" that only works with credentials you legitimately hold (self — not a bug).
- Enumeration from a generic timing difference under noise — need stable, repeated signal.
- Reaching a page that then redirects to login = not bypassed.

## Promotion / proof
- CONFIRMED: an authenticated action/data obtained without valid auth for that identity, raw request saved, reproduced 2x. Registration/collision bugs: show the takeover precondition concretely.
- Severity: full auth bypass / ATO = P1; enumeration or weak cookie flags alone = P3/P4.

## References
`session-management`, `jwt-security`, `forgot-password`, `rate-limiting`,
`oauth-oidc-security`, `access-control-testing`; `owned-account` discipline; memory first.
