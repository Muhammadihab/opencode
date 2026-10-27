#!/usr/bin/env python3
"""Generate skill stub files for every skill in registry.json that lacks one.

A stub is NOT a full skill, but it is a real, structured file the resolver can
load: YAML frontmatter (name, description, category, triggers) + a checklist
skeleton the orchestrator fills with real technique. Marked TODO so you can
flesh each out. Never overwrites an existing file.

Usage: python3 -I gen_skill_stubs.py /path/to/repo
"""
import json
import os
import sys

TEMPLATE = """---
name: {name}
description: {desc}
category: {category}
triggers: [{triggers}]
status: stub
---

# {title}

> **STUB** — structured placeholder so the resolver loads a real file for this
> surface. Replace the TODO sections with concrete technique. Keep the
> frontmatter `triggers` in sync with `runtime/registry.json`.

## When this triggers
{trigger_line}

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
"""


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    reg = json.load(open(os.path.join(repo, "runtime", "registry.json")))
    created, skipped = [], []
    for name, meta in reg["skills"].items():
        path = meta.get("path", f"skills/{name}.md")
        full = os.path.join(repo, path)
        if os.path.exists(full):
            skipped.append(path)
            continue
        os.makedirs(os.path.dirname(full), exist_ok=True)
        triggers = meta.get("triggers", [])
        trig_str = ", ".join(f'"{t}"' for t in triggers)
        title = name.replace("-", " ").title()
        desc = f"{meta.get('category','').title()} skill for: {title}."
        trigger_line = "Surfaces matching: " + ", ".join(f"`{t}`" for t in triggers if t != "*always*")
        content = TEMPLATE.format(
            name=name, desc=desc, category=meta.get("category", ""),
            triggers=trig_str, title=title, trigger_line=trigger_line or "Always (foundation)."
        )
        with open(full, "w") as f:
            f.write(content)
        created.append(path)
    print(f"created {len(created)} stub(s), skipped {len(skipped)} existing")
    for c in created:
        print("  +", c)


if __name__ == "__main__":
    main()
