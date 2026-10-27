---
name: structured-summary-reporting
description: Reporting skill for: Structured Summary Reporting.
category: reporting
triggers: ["summary", "structured summary", "session report"]
status: stub
---

# Structured Summary Reporting

> **STUB** — structured placeholder so the resolver loads a real file for this
> surface. Replace the TODO sections with concrete technique. Keep the
> frontmatter `triggers` in sync with `runtime/registry.json`.

## When this triggers
Surfaces matching: `summary`, `structured summary`, `session report`

## Attack model (fill before testing)
- **Asset / value at stake:** TODO
- **Authority decision the server must enforce:** TODO
- **Attacker-controlled inputs:** TODO
- **Expected proof (smallest safe request/callback):** TODO

## Core test checklist
- [ ] Establish baseline (raw request + response) and save under `requests/` `responses/`.
- [ ] Apply the primary technique for this class (TODO: list the concrete payload families).
- [ ] Run the bypass ladder — change ONE variable at a time (identity/state, method/path,
      parser/content-type, headers, encoding, workflow order).
- [ ] Response-diff baseline vs attack before claiming any signal.
- [ ] Record every variant in the tested-variant ledger (surface, variant, result, reason, next).

## FP traps for this class
- TODO: the common ways this class produces false positives (generic errors, redirects,
  client-side-only reflections, WAF pages). Check `memory/FALSE_POSITIVE_DB.md`.

## Promotion criteria
- OBSERVATION → LEAD: reproducible 2x.
- LEAD → CONFIRMED: server-side effect proven, impact defined.
- See `AGENTS.md` EXPLOITABILITY GATES for the full state machine.

## References
- Foundation: `skills/master-bugbounty-rules.md`
- Signal engine: `prioritization.md`
- Vuln-class memory: `memory/targets/<vuln>.md` (read first if present)
