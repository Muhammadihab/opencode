---
name: idor
description: Test object references for broken access control (IDOR/BOLA) — accessing or mutating another user/role/tenant's objects.
category: authz
triggers: ["idor", "object id", "user_id", "uid", "numeric id", "uuid", "bola", "ownership"]
status: active
---

# IDOR / BOLA (Broken Object-Level Authorization)

The server must prove *this identity owns this object* on every request. IDOR is
when it doesn't — it trusts the ID in the request instead of the session. Needs
**two owned accounts** (A and B, from `login.md`) to prove cross-user access.

## Attack model
- **Asset at stake:** another user's / tenant's object (record, file, message, invoice, setting).
- **Authority decision the server must enforce:** does the *authenticated identity* own or have a role granting access to the *referenced object*?
- **Attacker-controlled input:** the object reference — path segment, query param, JSON field, header, or array element.
- **Smallest proof:** account A's session returns account B's object (or mutates it), shown by a response-diff of A-owned vs B-owned requests.

## Where the ID lives (check all)
- Path: `/api/users/1024/profile`, `/orders/5f3c.../items`
- Query: `?id=`, `?user_id=`, `?account=`, `?file=`, `?doc=`, `?ref=`
- Body: JSON fields (`"ownerId":`, `"accountId":`), form fields, GraphQL variables
- Headers: `X-Account-Id`, `X-Tenant`, custom app headers
- Nested / batch: arrays of IDs, GraphQL aliases, bulk endpoints (`ids=[...]`)

## Test procedure (two accounts)
1. As **B**, create/open an object; record its ID and the exact GET/response (baseline B).
2. As **A** (different session), replay B's request with B's ID. Compare:
   - A sees B's data → **horizontal IDOR (read)**.
   - A can `PUT/PATCH/POST/DELETE` B's object → **IDOR (write)** — higher impact.
3. Repeat for **vertical**: low-priv user hitting an admin object/action.
4. Repeat for **cross-tenant**: swap `org_id`/`tenant_id` to B's org (see `business-context-analysis`).

## ID-manipulation bypass ladder (one variable at a time)
- **Sequential:** `1024 → 1023, 1025, 1, 0, -1, 999999`.
- **UUID/opaque:** harvest real IDs from other responses, JS bundles (`js-deep-analysis`), emails, exports, referers — don't guess; **find** them.
- **Encoding:** try the raw ID, URL-encoded, base64-decoded-then-reencoded if it looks encoded.
- **Format/type:** string vs int (`"1024"` vs `1024`), array vs scalar (`id=1024` → `id[]=1024&id[]=1025`), wrapped object.
- **Parameter pollution:** `?id=A&id=B` (yours + target's — some stacks authz the first, serve the last). See `parameter-pollution`.
- **Method swap:** if `GET` is authorized but `POST/PUT` isn't checked (or vice versa). See `access-control-testing`.
- **Sibling/nested:** `/users/<me>/orders/<B's order>` — parent authz'd, child not.
- **Wrapper endpoints:** export, print, PDF, share-link, "email me this", webhook — often skip the authz check the main endpoint has.

## Chain targets
Harvested ID → IDOR read → **sensitive data** (PII, invoices, tokens). IDOR write →
**account takeover** (change B's email/password/role), **privilege escalation**,
**cross-tenant** breach. Signed-URL/export IDOR → bulk data exposure.

## FP traps (check before claiming)
- **Same data to everyone by design** (public object) → not IDOR.
- **Reflected input, not stored** — the "other user's" data is just your echoed input.
- **A guessed ID that happens to be yours** — confirm the object is genuinely B's (different account, different session cookie).
- **403/404 that looks like success** because the body is a generic error — run `fp_check.py` and response-diff.
- **"Access" that's really a redirect to login** — check status + final body, not just 200.

## Promotion / proof
- LEAD: A's session returns B-shaped data, reproducible 2x.
- CONFIRMED: response-diff proves A received B's *specific* object (unique field only B has), with both raw requests saved under `requests/` and the two account contexts noted.
- Severity per `prioritization.md`: sensitive-object IDOR = P2; cross-tenant / ATO-enabling = P1. Never assign from the param name alone.

## References
`access-control-testing`, `business-context-analysis`, `parameter-pollution`,
`privilege-escalation`, `js-deep-analysis`; memory: `memory/targets/idor.md` (read first).
