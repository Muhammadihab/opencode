---
name: graphql-security
description: Test GraphQL endpoints for introspection, authorization gaps on resolvers, injection, and batching abuse.
category: api
triggers: ["graphql", "introspection", "mutation", "query resolver", "gql"]
status: active
---

# GraphQL Security

GraphQL authenticates the request but frequently fails to authorize the
**resolver** — object-level and field-level authz are per-resolver and easy to
miss. The schema is the map; mutations are the state-changers.

## Attack model
- **Asset:** every object/field/mutation behind the endpoint.
- **Authority decision:** does this identity own/have-role-for *this node/field/mutation*? Often checked at the query level but not per-resolver.
- **Attacker input:** query/mutation text, variables, operation name, aliases, batch array.
- **Smallest proof:** a resolver returns/mutates data the identity shouldn't reach.

## Map the surface first
- **Endpoint:** `/graphql`, `/api/graphql`, `/v1/graphql`, `/query`; also GET with `?query=`.
- **Introspection:** send the introspection query (`__schema{types{name fields{name}}}`). If enabled → full map of types, queries, mutations. If disabled, recover operations from JS bundles (`js-deep-analysis`) and field-stuffing/suggestions.
- **Suggestions:** many servers reply "did you mean `userById`?" on a typo — leaks field names even with introspection off.

## Core tests
- **Resolver authz (the big one):** enumerate every query/mutation; for each, try it as a low-priv / other-tenant / unauthenticated identity. `node(id:)`, `userById(id:)`, `*ById`, `*ByEmail` are prime IDOR/BOLA (see `idor`, `business-context-analysis`).
- **Mutations:** the state-changers — role grants, email change, invites, payments. Test each for missing authz and mass-assignment of extra input fields.
- **Field-level leakage:** a node you *can* read exposing a field you shouldn't (`email`, `passwordHash`, `token`, internal flags).
- **Injection through resolvers:** variables flowing into SQL/NoSQL/OS → see `sql-injection`, `database-security`, `command-injection`. GraphQL just transports it.
- **Batching / aliasing abuse:** many aliased copies of a sensitive mutation in one request to bypass rate limits / brute OTP (see `rate-limiting`): `a:login(...) b:login(...) c:login(...)`.
- **Query depth/complexity DoS:** note only — do NOT run destructive deep queries (out of scope behaviour).

## Bypass ladder
Identity (unauth/low-priv/other-tenant tokens) → operation (query vs mutation vs
subscription) → transport (POST JSON, GET, form-encoded) → field selection (request the
sensitive field directly) → batching/aliases → introspection-off recovery via JS + suggestions.

## Chain targets
Introspection → hidden mutation → IDOR/priv-esc. `userByEmail` → account enumeration →
reset-flow abuse. Mutation mass-assignment → role escalation → admin.

## FP traps
- Introspection enabled is **informational** alone (P4) until it leads to an actual authz/data bug.
- A field returning `null`/permission-error = authz working, not a finding.
- Data you're entitled to via your own role ≠ a bug.
- Errors that merely echo your input ≠ injection — need a server-side effect.

## Promotion / proof
- CONFIRMED: a resolver returns/mutates unauthorized data cross-identity, reproduced 2x, raw query + response + account context saved. Batching-OTP-bypass: show multiple attempts in one request succeeding past the limit.
- Severity: unauth/cross-tenant data or privileged mutation = P1; sensitive IDOR via resolver = P2; introspection only = P4.

## References
`idor`, `access-control-testing`, `business-context-analysis`, `api-security`,
`parameter-pollution`, `rate-limiting`, `js-deep-analysis`; memory first.
