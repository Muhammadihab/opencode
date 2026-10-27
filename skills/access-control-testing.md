---
name: access-control-testing
description: Test function-level and resource-level authorization — can an identity reach actions/endpoints it shouldn't (BFLA, forced browsing, method/role gaps).
category: authz
triggers: ["authz", "access control", "acl", "bfla", "function level", "permission"]
status: active
---

# Access Control Testing (Function-Level Authz / BFLA)

IDOR is about *objects*; this is about *functions* — can a low-priv or
unauthenticated identity invoke an action/endpoint gated to admins/other roles.
Needs accounts at **different privilege levels** (from `login.md`) to prove.

## Attack model
- **Asset:** privileged actions/endpoints (admin, support, moderation, billing, config).
- **Authority decision:** does this identity's *role* permit this *function*? Often enforced only in the UI, not server-side.
- **Attacker input:** the endpoint path, HTTP method, role/scope params, the request itself.
- **Smallest proof:** a low-priv/unauth identity successfully invokes a higher-priv action, shown by the action's effect + a response-diff vs the denied baseline.

## Technique
- **Forced browsing:** take admin endpoints (from JS, docs, `js-deep-analysis`, guesses like `/admin`, `/api/admin/*`, `/internal/*`) and hit them as a low-priv user. Served? → vertical escalation.
- **Method gap:** endpoint authorizes `GET` but not `POST/PUT/DELETE` (or an override header `X-HTTP-Method-Override`). Try every method.
- **UI-only gating:** the button is hidden for your role but the API call still works — replay the admin API call with a low-priv token.
- **Role/scope params:** `?admin=true`, `role=admin`, `isAdmin=1`, scope in JWT/body — flip and resend (see `privilege-escalation`, `jwt-security`).
- **Missing auth entirely:** endpoint needs a token but doesn't check it (send none/expired/other-user's).
- **Referer/step trust:** action authorized only because you "came from" an admin page — forge/skip it.

## Bypass ladder
Identity (unauth / low-priv / other-role tokens) → method (GET/POST/PUT/PATCH/DELETE +
override headers) → path (trailing slash, case, encoded segments, `/v1` vs `/v2`, `.json`) →
params (role/scope flags) → workflow (skip the gate step). One at a time.

## Chain targets
Function-level bypass → admin action → full compromise. Hidden admin API (from JS) →
unauth invocation → data/state change. Combine with IDOR for object+function coverage.

## FP traps
- Endpoint returns `200` but a **permission-denied body** — read the body, not just status.
- Action "works" but only on *your own* resources at your own level → not escalation.
- A public endpoint intended to be unauth → not a finding.
- Soft 403 / redirect to login that renders 200 → denied, not bypassed.

## Promotion / proof
- CONFIRMED: a privileged action's *effect* achieved by an under-privileged identity, reproduced 2x, with the denied baseline + bypass request + resulting state saved, and both role contexts noted.
- Severity: admin/support break or privileged state change = P1; lower-sensitivity function gap = P2.

## References
`idor`, `privilege-escalation`, `business-context-analysis`, `jwt-security`,
`parameter-pollution`, `js-deep-analysis`; memory first.
