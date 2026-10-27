---
name: js-deep-analysis
description: Deep-analyze JS bundles and source maps for endpoints, hidden routes, secrets, and client logic that reveals attack surface.
category: recon
triggers: ["js", "javascript", "bundle", "source map", "sourcemap", "client route", "webpack"]
status: active
---

# JavaScript Deep Analysis

JS bundles are the app's map — endpoints, hidden routes, feature flags, roles,
GraphQL operations, and sometimes secrets, all shipped to the client. Analyze
every JS file touching the active flow **immediately**; auth/API bundles first.
This feeds every other skill with surface.

## What to extract
- **Endpoints & API paths:** full/relative URLs, `fetch`/`axios`/`XHR` calls, path templates, API base URLs, `/api/...`, versioned paths.
- **Hidden/role-gated routes:** client router config (React Router, Vue Router), admin/internal routes not linked in the UI → forced-browse them (`access-control-testing`).
- **GraphQL:** operation names, queries, mutations, fragments — recover the schema even when introspection is off (`graphql-security`).
- **Secrets:** API keys, tokens, OAuth client IDs, cloud keys, signing secrets, hardcoded creds (`js-secret-and-api-review`). Note type + prefix; never paste full secret in shared output.
- **Feature flags / roles / entitlements:** client-side gates that the server may not enforce (`business-logic`, `access-control-testing`).
- **Internal URLs / hosts:** staging, internal APIs, third-party integrations, webhooks.
- **Client-side sinks:** `innerHTML`, `eval`, `document.write`, `postMessage` handlers → DOM XSS (`dom-xss`).

## Technique
- Inventory every JS file (unauthenticated first, then post-login — auth-gated bundles often hold the richest surface).
- **Source maps:** try `.map` for each bundle (append `.map`, check `//# sourceMappingURL`, common paths); a map reconstructs original source → huge surface win.
- Beautify/deobfuscate minified bundles; grep for the extraction targets above.
- Diff bundles across versions/deploys for newly added endpoints.
- For each endpoint/route found → hand to the resolver and **test it directly** (collection is never completion).

## Chain targets
Hidden route → unauth/priv-esc access. Leaked endpoint → IDOR/BOLA. Source-map leak →
full logic → auth bypass. Client secret → direct API/cloud access.

## FP traps
- A route in the client ≠ a reachable/authorized server endpoint — verify server-side.
- A "secret" that's a public/publishable key (e.g. Stripe `pk_`, public API keys) = not sensitive alone.
- Dead code / commented endpoints that 404.
- Client-side feature flag ≠ server enforcement gap until proven.

## Promotion / proof
- This is **recon** — outputs are leads, not findings. Promotion happens when a discovered surface is tested and proven by its own skill. Record every endpoint/route/secret-type in notes + mindmap with a next-action.

## References
`js-secret-and-api-review`, `graphql-security`, `dom-xss`, `access-control-testing`,
`idor`, `endpoint-triage`; feeds the whole hunt. Auto-trigger on every in-scope JS file.
