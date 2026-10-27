---
name: business-logic
description: Test workflow and business-rule enforcement — abusing intended functionality (pricing, limits, state, approvals) for unintended gain.
category: realtime
triggers: ["business logic", "workflow", "coupon", "discount", "approval", "quota", "trial", "credit"]
status: active
---

# Business Logic Abuse

No payload — you abuse *intended* features by breaking the assumptions behind
them: negative quantities, skipped steps, replayed approvals, client-trusted
prices. The scanner can't find these; you need to understand what the app is
*for* (see `business-context-analysis`).

## Attack model
- **Asset:** money, credits, quota, trust decisions, workflow integrity.
- **Authority decision:** does the server enforce the business rule, or trust the client/sequence?
- **Attacker input:** values, quantities, step order, state transitions, repeated actions.
- **Smallest proof:** you obtain value or a state the rules shouldn't allow, shown by before/after.

## Patterns to test
- **Price/amount tampering:** change price, total, currency, or quantity in the request — is it recomputed server-side? Negative quantity → refund/credit. Negative/zero price.
- **Coupon/discount abuse:** stack coupons, reuse single-use (also a race — `race-conditions`), apply after total, expired code still honored, coupon on already-discounted.
- **Quota/limit bypass:** exceed plan limits, seats, API quota, trial length; reset trial by re-signup/param.
- **Workflow skipping:** jump to a later step (payment → fulfillment without paying), skip approval, reach "completed" state directly.
- **Approval/replay:** replay a one-time approval token; approve your own request; self-approve where two parties required.
- **Refund/cancellation logic:** refund more than paid, cancel-after-use, keep goods + refund.
- **Currency/rounding:** rounding in your favor at scale, currency mismatch.
- **Integer/parameter edge:** very large/negative/zero/overflow values in quantities, dates, IDs.

## Technique
- Map the money/identity/workflow paths first (`business-context-analysis`).
- For each, ask "what does the server *assume* here?" then break that one assumption.
- Always prove **server-side state change**, not a UI display change.
- One assumption at a time; capture before/after.

## FP traps
- A price change in the request that the server **recomputes** (ignores your value) = secure.
- UI shows a discount but the charged amount is correct → display-only, not a bug.
- "Free" access to something actually free/public.
- A limit you exceeded that resets legitimately.

## Promotion / proof
- CONFIRMED: value obtained / rule broken with server-side effect, reproduced 2x, before/after state + requests saved. Quantify ("paid $0 for a $50 item", "trial extended indefinitely via param").
- Severity: payment/credit/quota abuse with real impact = P1/P2; minor logic quirk = P3.

## References
`business-context-analysis`, `race-conditions`, `payments-security`,
`access-control-testing`, `parameter-pollution`; memory first.
