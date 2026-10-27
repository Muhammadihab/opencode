---
name: request-response-analyzer
description: Systematically compare baseline vs modified requests/responses to extract real signal from noise before claiming anything.
category: api
triggers: ["request", "response", "status diff", "body diff", "header analysis"]
status: active
---

# Request / Response Analyzer

The discipline that turns "looks interesting" into evidence. Every claimed signal
must come from a **baseline vs attack diff** — not a single response in isolation.
This is the validation substrate for all other skills.

## Core method
1. **Baseline:** capture the clean request + full response (status, headers, body, timing, resulting state). Save under `requests/` `responses/`.
2. **One variable:** change exactly one thing (the attack variant).
3. **Diff:** compare status, meaningful body, headers, timing, and server-side state — not status code alone.
4. **Score the diff (0–4):** ignore noise (CSRF rotation, timestamps, nonces, cache artifacts, request IDs); escalate only when 2+ meaningful signals move together (see `response-diff-analysis`).

## What to read (not just status)
- **Status:** 200/403/401/302/500 — but a 200 can be a denied body, a 403 can leak.
- **Body:** length delta, new/removed fields, different object, error vs data. Mask volatile tokens before comparing (the FP hash does this — `fp_check.py`).
- **Headers:** `Set-Cookie`, `Location`, `Content-Type`, CORS headers, cache headers, custom app headers, framework/version leaks.
- **Timing:** only with multiple samples + a clean baseline (for blind/time-based — `sql-injection`, `command-injection`).
- **State:** did a write actually change something? Re-fetch to confirm.

## Techniques this enables
- **Auth/authz diffs:** same request with/without token, other-user token, other role → access-control signal.
- **Injection diffs:** boolean `1=1` vs `1=2`, payload vs benign → injection signal.
- **Enumeration diffs:** valid vs invalid username/ID response/timing.
- **Method/content-type diffs:** GET vs POST, JSON vs form — parser behaviour.
- **Header reflection:** does `Host`/`X-Forwarded-*`/`Origin`/`Referer` change the response? → host-header/CORS/cache leads.

## FP traps (this skill IS the FP defense)
- Dynamic content (ads, timestamps, CSRF, A/B flags) masquerading as a signal — normalize first.
- A WAF/error page that differs but means nothing — run `fp_check.py`.
- Single-sample timing — never trust without repetition.
- Reflected input mistaken for stored/server-side effect.

## Output
- For any lead: baseline pair + modified pair + the specific diff that is the signal + which noise you ruled out. This is what every finding's evidence section is built from.

## References
`response-diff-analysis`, `false-positive-filter`, `evidence-hygiene`;
used by every injection/authz/auth skill. Run before claiming ANY signal.
