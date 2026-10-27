---
description: "Full intelligence update - fetch, process, index, and learn from write-ups"
agent: build
---
# UPDATE: Full intelligence pipeline

## MANDATES
- [ ] **Foundations**: Read `agent-briefing.md`. Load `master-bugbounty-rules` + `learning-engine`.
- [ ] **Registry**: Verify `python scripts/skill_registry.py check`.
- [ ] **Preflight**: Run `python scripts/runtime_preflight.py --mode update`. Stop if blocked.
- [ ] **Resolver**: Resolve `python scripts/skill_registry.py resolve --scenario "write-up intelligence update" --mode update --paths-only`. Load matching skills.
- [ ] **Preserve briefing**: `agent-briefing.md` static sections are **PRESERVED**. Never overwrite them. Only update timestamp + knowledge count.

## PIPELINE STEPS (RUN AUTONOMOUSLY)
Run `scripts/update.sh` or equivalent in order:

1. [ ] **Fetch**: Fetch new write-ups from configured public sources into `writeups/raw/` organized by source: `github/`, `hackerone/`, `medium/`, `yeswehack/`, `bugboard/`, `projectzero/`, `vickieli/`, `nahamsec/`, `cobalt/`, `cloudflare/`, etc. Save as `writeups/raw/[source]/[topic]_[timestamp].md`.
2. [ ] **Process**: Process raw -> structured under `writeups/processed/` with **triple-layer dedup**: exact URL, normalized title, content hash SHA256 of first 300 chars.
3. [ ] **Index**: Rebuild `writeups/index.md` as a **TABLE** (Title, Vuln Type, Target, Source).
4. [ ] **Lessons**: Extract lessons into `memory/report-lessons.md`.
5. [ ] **Update memory**: Update `memory/methodology.md` and `memory/patterns.md`.
6. [ ] **Target checklists**: Generate/refresh `memory/targets/<vuln>.md` checklists **only** for types appearing **3+ times**.
7. [ ] **Briefing**: Update timestamp + knowledge count in `agent-briefing.md`. **Static sections PRESERVED**.
8. [ ] **Audit**: Run learning-engine audit in report-only mode if present: `learning_engine/scripts/audit_learning_engine.py --report-only`. Re-read `agent-briefing.md`. Record update summary in session notes.

## AFTER PIPELINE
- [ ] **Hunts note**: New write-ups found during hunts go to `writeups/raw/` first.

## OUTPUT STRUCTURE (RETURN THIS)
- [ ] **Fetch status** + sources queried
- [ ] **Per-source new write-ups** (count/skipped)
- [ ] **Processing status** (new/skipped/errors)
- [ ] **Index total** (row count in table)
- [ ] **Memory files updated** (`report-lessons.md`, `methodology.md`, `patterns.md`, `targets/*` if created)
- [ ] **Top categories** (by vuln type/count)
- [ ] **Briefing timestamp confirmation** (updated count/time)
