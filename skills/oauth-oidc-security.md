---
name: oauth-oidc-security
description: Test OAuth2/OIDC flows for redirect_uri abuse, state/CSRF gaps, code/token leakage, and account takeover.
category: auth
triggers: ["oauth", "oidc", "redirect_uri", "state param", "openid", "sso token"]
status: active
---

# OAuth2 / OIDC Security

OAuth bugs are **flow logic** bugs — the pieces (redirect_uri, state, code,
token) are each a trust assumption that, if broken, leaks the code/token or
lets you link/take over accounts. Stay in scope: don't attack the external IdP
itself unless it's in scope.

## Attack model
- **Asset:** the authorization code / access token / id_token — possession = the victim's session.
- **Authority decision:** is this callback going to a registered client/redirect, bound to the user who started it (state), and exchanged by the legitimate client?
- **Attacker input:** `redirect_uri`, `state`, `scope`, `response_type`, `code`, the callback request.
- **Smallest proof:** the code/token reaches a destination you control, or you authenticate as/link to another account.

## Technique
- **`redirect_uri` manipulation:** the #1 bug. Try: other path on same host, open-redirect on the allowed host (chain — see `ssrf`/open redirect), subdomain, `//attacker`, `\@`, `?`/`#` tricks, suffix (`allowed.com.attacker.com`), missing exact-match. If the code is sent to your URL → ATO.
- **`state` missing/static/not-validated:** no state = login CSRF / forced account linking. Reuse/replay state.
- **Code/token in referer or history:** does the callback leak `code` to third-party scripts/referrer?
- **Account linking:** can you link your social login to a *victim's* existing account (email collision, no verification)? → ATO. See `auth-bypass`.
- **`response_type`/mode confusion:** request token in fragment vs query; implicit flow where code flow expected.
- **Code reuse / expiry:** is an auth code single-use and short-lived? Replay it.
- **Scope escalation:** request broader scopes; does the server honor them silently?
- **PKCE:** downgrade/skip PKCE on a public client; missing `code_challenge` verification.
- **id_token (OIDC):** validate signature/`iss`/`aud`/`nonce` — overlaps `jwt-security`.

## Bypass ladder
redirect_uri variants → state handling → response_type/mode → account-linking → code
reuse/expiry → scope → PKCE → id_token claims. One at a time; capture each callback.

## Chain targets
redirect_uri leak → code theft → **ATO**. Forced linking → **ATO**. Open redirect on
allowed host → code exfil. id_token forgery → auth bypass.

## FP traps
- A redirect_uri that only accepts exact registered values = secure; your "bypass" must actually deliver the code elsewhere.
- Attacking the IdP (Google/Okta) itself when out of scope — don't.
- `state` present but you didn't test it's *validated* — presence ≠ enforcement.
- Code that leaks but is already expired/single-used before you can use it.

## Promotion / proof
- CONFIRMED: code/token delivered to your controlled endpoint, OR authenticating as/linking another account, reproduced 2x, with the manipulated authorize request + callback saved.
- Severity: ATO via redirect/linking = P1; CSRF-linking without full ATO = P2.

## References
`auth-bypass`, `jwt-security`, `session-management`, `ssrf` (open-redirect chain),
`access-control-testing`; `owned-account` discipline; memory first.
