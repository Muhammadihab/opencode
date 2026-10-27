---
name: xss
description: Test for reflected and stored XSS — attacker JavaScript executing in another user's authenticated browser context.
category: client
triggers: ["xss", "reflected", "stored xss", "script injection", "html injection", "innerhtml"]
status: active
---

# XSS (Cross-Site Scripting)

Impact is **script execution in a victim's authenticated context**, not reflection.
A payload that echoes but doesn't execute is HTML injection at most. Stored >
reflected; admin/support-viewed stored XSS is the prize.

## Attack model
- **Asset:** the victim's session/DOM — their cookies, tokens, actions, in *their* browser.
- **Authority decision:** should attacker-supplied content become executable markup in another user's page? Never.
- **Attacker input:** any field that ends up rendered — forms, params, headers (Referer/UA reflected), filenames, markdown, JSON shown in a template.
- **Smallest proof:** controlled JS executes (`alert`/`console`/a DOM change/a beacon) in a context you don't control — ideally demonstrated as victim, not self.

## Find the sink first (don't spray payloads)
- **Reflected:** inject a unique marker (`zqx123`) in each param/header; find where it lands in the response. Note the **context**: HTML body, attribute, `<script>`, URL, CSS, JSON.
- **Stored:** submit the marker; find every place it's later rendered (profile shown to admins, comments, logs, exports, support dashboards). Stored XSS into an admin view is high-value.
- **DOM:** see `dom-xss` — source (`location.hash`, `postMessage`) → sink (`innerHTML`, `eval`, `document.write`). Read JS with `js-deep-analysis`.

## Context-driven payloads (match the sink)
- **HTML body:** `<svg onload=alert(1)>`, `<img src=x onerror=alert(1)>`.
- **Attribute:** break out — `" onmouseover=alert(1) x="`, `'><svg onload=alert(1)>`.
- **Inside `<script>`:** `';alert(1);//` or `</script><svg onload=alert(1)>`.
- **URL/href:** `javascript:alert(1)` (test if scheme survives).
- **Markdown/rich text:** `[x](javascript:alert(1))`, raw HTML if allowed, `onerror` in embedded img.
- **Polyglot** (when context unknown): `jaVasСript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//` style — then narrow once you see which context breaks.

## WAF / filter bypass ladder (see `waf-bypass`)
Case toggling (`<ScRiPt>`), encoding (HTML entity, URL, double-URL, unicode), event-handler
swaps (`onload`→`onpointerover`), tag swaps, no-space tricks (`/` as separator),
null bytes, split across attributes, alternative tags (`<details open ontoggle=>`).
Change one encoding family at a time; log every variant.

## Chain targets
Stored XSS in admin/support view → **session/token theft → admin takeover** (P2→P1).
XSS → CSRF-token exfil → state change. XSS + weak CSP → full page control.
Self-XSS alone is **not** a finding (kill condition) unless chained to a delivery vector.

## FP traps
- **Reflection without execution** — marker appears but is HTML-encoded. Verify it actually runs.
- **Self-XSS** — only you can trigger it, no delivery to a victim → not reportable alone.
- **Executes only in a broken/old browser** or requires unrealistic interaction → downgrade.
- **CSP blocks execution** — if a strict CSP stops the payload, note it; the injection may still be HTML injection, not XSS.
- `alert(document.domain)` on `about:blank`/sandbox ≠ on the real origin — prove the origin.

## Promotion / proof
- CONFIRMED: JS executes in the target origin, reproduced 2x, with the raw injected request/stored value and a screenshot (support only) + the executing context noted. For stored, state *who* renders it (self vs other users vs admins).
- Severity: stored/admin-context = P2; reflected-with-execution = P3 unless chained; self/HTML-only = P4.

## References
`dom-xss`, `content-security` (CSP), `waf-bypass`, `js-deep-analysis`,
`session-management`, `exploit-chain-analysis`; memory first.
