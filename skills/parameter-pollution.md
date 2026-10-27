---
name: parameter-pollution
description: Test parameter handling for HPP, duplicate keys, type coercion, and mass assignment — making the server read a value you shouldn't control.
category: api
triggers: ["parameter", "param pollution", "duplicate key", "hpp", "coercion", "type confusion"]
status: active
---

# Parameter Pollution & Coercion

Front-end and back-end often parse parameters differently. Duplicate keys, type
changes, and extra fields let you smuggle values past validation or into
sensitive fields. A cheap, high-yield check on every write endpoint.

## Attack model
- **Asset:** whichever value the server trusts — an ID, a role, a price, an authz flag.
- **Authority decision:** which value does the server bind when the input is ambiguous or over-supplied?
- **Attacker input:** duplicate params, arrays vs scalars, type mismatches, extra JSON fields.
- **Smallest proof:** the server acts on a value you injected via the ambiguity, with a response/state diff vs the clean request.

## Techniques
- **HTTP Parameter Pollution:** `?id=victim&id=me` (and the reverse). Front-end may authz the first, back-end serve the last (or concatenate). Try in query, body, and both at once.
- **Array vs scalar:** `id=1` → `id[]=1&id[]=2`, `role=user` → `role[]=user&role[]=admin`. Some parsers take the last/first/array.
- **Type coercion:** string vs int vs bool vs null (`"true"`, `1`, `[]`, `{}`), wrapping a scalar in an object/array to confuse validators or ORM casts.
- **Mass assignment:** add fields the client never sends — `"role":"admin"`, `"isVerified":true`, `"ownerId":<other>`, `"price":0`, `"credits":9999` — to a write/update endpoint. Harvest field names from JS/GraphQL/responses (`js-deep-analysis`).
- **JSON/form/multipart confusion:** send the same endpoint as JSON vs form vs multipart; duplicate keys across content types (see `request-response-analyzer`).
- **Casing / whitespace / prefix:** `Role` vs `role`, trailing chars validators miss.

## Bypass ladder
Duplicate (query/body/both) → array vs scalar → type mismatch → extra/mass-assign fields →
content-type switch → casing. One at a time; response-diff each against the clean baseline.

## Chain targets
Mass-assign `role` → privilege escalation. Mass-assign `ownerId` → IDOR-by-assignment.
HPP on an authz param → access-control bypass (`access-control-testing`). Price field → business-logic.

## FP traps
- The server picks a value but it's **your own/legitimate** one → no impact.
- An extra field accepted but **ignored** (not bound) → not mass assignment; prove it changed state.
- A 400/validation error on the polluted request = validation working.
- Different value echoed in the response but server state unchanged → display only.

## Promotion / proof
- CONFIRMED: the server bound an attacker-controlled value with real effect (role changed, other-owner object written, price altered), reproduced 2x, clean vs polluted requests + state saved.
- Severity: inherits the impact it unlocks (priv-esc/IDOR/payment = P1/P2).

## References
`access-control-testing`, `idor`, `business-logic`, `request-response-analyzer`,
`js-deep-analysis`, `api-security`; memory first.
