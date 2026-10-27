---
name: race-conditions
description: Test one-time / limit-bound actions for race conditions (TOCTOU) — concurrent requests bypassing a check.
category: realtime
triggers: ["race condition", "race", "toctou", "concurrent", "double spend", "parallel request"]
status: active
---

# Race Conditions (TOCTOU)

When a check and the action it guards aren't atomic, firing many requests in
parallel can slip multiple through before the state updates — "use once" becomes
"use N times". Test only where it's **safe** (no destructive/irreversible effect
on real data) and the program allows it.

## Attack model
- **Asset:** a limit or uniqueness the server enforces — one coupon use, one vote, balance ≥ amount, single invite, unique signup.
- **Authority decision:** is this action still permitted *at the moment it commits*? Races break the gap between check and commit.
- **Attacker input:** timing — N identical requests sent simultaneously.
- **Smallest proof:** the limited action succeeds more times than allowed (e.g. coupon applied twice, balance goes negative), shown by before/after state.

## Where to look
- Coupons/discounts/gift cards (apply once → apply many).
- Balance/credits/withdrawal (spend beyond balance → double-spend).
- Invites/seats/quota (exceed the cap).
- Vote/like/follow (inflate past one).
- Signup/username uniqueness (two accounts, same unique field).
- OTP/token verification (extra attempts in the window — see `rate-limiting`).
- Any "mark as used" / state transition.

## Technique
- Capture the single legitimate request (baseline + resulting state).
- Fire **many copies in parallel** — single-packet / last-byte-sync where possible, or a tight concurrent burst (controlled count, e.g. 20–50; not a flood — avoid DoS).
- Compare final state to the limit: more successes than allowed = race.
- Vary concurrency and the exact action; some races need a specific window.
- GraphQL batching/aliases can send many in one request (see `graphql-security`).

## FP traps
- The server **does** serialize (only one succeeds) = secure; your "extra" successes may be retries that failed server-side — verify the *state*, not just 200s.
- Idempotent action (same result regardless of count) → no race impact.
- "Double" caused by your own double-click, not concurrency.
- Volume that looks like a race but is just you exceeding rate limits (different bug — see `rate-limiting`).

## Promotion / proof
- CONFIRMED: the guarded limit is exceeded via concurrency, reproduced 2x, with before/after state (balance/count/uses) and the burst saved. State the business effect ("coupon worth $X applied N times").
- Severity: payment/balance/quota race with business impact = P1/P2 per value; cosmetic (extra like) = P4.

## References
`business-logic`, `payments-security`, `rate-limiting`, `graphql-security`,
`request-response-analyzer`; memory first. Confirm program allows concurrency testing.
