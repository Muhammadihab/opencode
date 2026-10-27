---
name: ssti
description: Test for server-side template injection — input evaluated by a template engine, leading to data disclosure or RCE.
category: injection
triggers: ["ssti", "template injection", "jinja", "twig", "freemarker", "velocity"]
status: active
---

# SSTI (Server-Side Template Injection)

Input rendered *through* a template engine (not just reflected) — the engine
evaluates your expression. Impact ranges from data disclosure to full RCE
depending on the engine. Prove **safely**: evaluate arithmetic, then stop short
of destructive RCE on a live target.

## Attack model
- **Asset:** template context data, and often the server (RCE) via engine internals.
- **Authority decision:** should user input be *evaluated* as template code? Never.
- **Attacker input:** any field reflected into a server-rendered template — names, subjects, profile fields, email templates, error messages, export templates.
- **Smallest safe proof:** a math expression evaluates server-side (`{{7*7}}` → `49`) — proves evaluation without running commands.

## Detection
1. **Polyglot probe:** `${7*7}`, `{{7*7}}`, `<%= 7*7 %>`, `#{7*7}`, `{7*7}` — look for `49` in the response (evaluation), not the literal string.
2. **Distinguish from XSS:** `{{7*7}}` rendering `49` server-side = SSTI; `<script>` reflecting = XSS. SSTI evaluates; XSS just echoes.
3. **Identify the engine:** the syntax that works narrows it (Jinja2/Twig `{{}}`, Freemarker `${}`, Velocity `#{}`, ERB `<%= %>`). Engine-specific error messages help.

## Exploitation (engine-specific, safe-first)
- Confirm with arithmetic and simple object access first (e.g. config/env *names*, not secrets).
- Escalate toward RCE **only** per program scope and with a safe proof — prefer a controlled delay or OOB callback (see `command-injection`, `blind-vuln`) over running arbitrary commands.
- Each engine has a known gadget chain to reach the runtime; use the minimal step that proves impact, then stop.

## Bypass ladder
Syntax variants per engine → context break-out (inside a string/attribute in the template) →
filter bypass (attribute access via `[]`, concatenation, encoding) → minimal escalation to
prove impact. One at a time.

## Chain targets
SSTI → read secrets/config → deeper access. SSTI → RCE (terminal). SSTI in email/export
templates often runs with elevated server context.

## FP traps
- `{{7*7}}` appearing **literally** as `{{7*7}}` = not evaluated → not SSTI (maybe XSS/HTML injection).
- Client-side template (Angular/Vue) evaluating in the browser = client-side, not server-side — different class.
- A math result that's actually your reflected input coincidentally.
- Engine error ≠ evaluation; need the computed result or side-effect.

## Promotion / proof
- CONFIRMED: server-side evaluation proven (`49` from `7*7`), reproduced 2x, raw request + response saved; for RCE, a safe delay/OOB callback with marker. Don't dump secrets or run destructive commands to "prove more."
- Severity: SSTI→RCE = P1; evaluation/data disclosure only = P2.

## References
`command-injection`, `xss` (to distinguish), `blind-vuln`, `waf-bypass`,
`exploit-chain-analysis`; memory first.
