# VERIFICATION CHECKLIST: Audit & Readiness

## 1. Skill Coverage
- [ ] `skills/` mirrors exist and contain required foundation skills.
- [ ] `.agents/skills/` has active skill folders where applicable.
- [ ] `master-bugbounty-rules.md` is **loaded FIRST** (before `learning-engine-integration`).
- [ ] `learning-engine-integration.md` is available and hooks are present under `learning_engine/` (5 hooks).
- [ ] `scripts/skill_registry.py` is present and `python scripts/skill_registry.py check` passes.
- [ ] All skills referenced by `runtime/registry.json` resolve to existing paths or are marked deferred with reason.

## 2. Startup & Hunting Rules
- [ ] `agent-briefing.md` read first on every session.
- [ ] `AGENTS.md` defines workflow and is followed (constitution).
- [ ] `prioritization.md` used for ranking/signals.
- [ ] 4-phase interleaved flow enforced (BOOT → DISCOVERY↔EXPLOIT → DEEP EXPLOIT → REPORT gated).
- [ ] Exact-host scope lock enforced. Target stickiness applied. Prior-data checked in `testing/`.
- [ ] Session bootstrap via `scripts/runtime_preflight.py` used every hunt.
- [ ] `MINDMAP.md` created/updated per target.
- [ ] JS deep analysis performed when bundles found (`js-agent` / skills).
- [ ] Skill gates enforced before any test (resolver + load all returned skills).
- [ ] Owned-account login discipline enforced via `login.md` + inbox separation.
- [ ] Chrome MCP + Chrome DevTools used together when browser needed.

## 3. Learning & Update Pipeline
- [ ] `memory/report-lessons.md` read before processed reports.
- [ ] `memory/patterns.md`, `memory/methodology.md`, `memory/targets/<vuln>.md` guide hunting.
- [ ] `writeups/index.md` used for retrieval only (not blindly applied).
- [ ] Raw write-ups go to `writeups/raw/` first during hunts.
- [ ] `/update` pipeline runs: fetch → process (triple-layer dedup) → rebuild `writeups/index.md` (table) → extract lessons → update `patterns.md`/`methodology.md` → generate `memory/targets/<vuln>.md` only if >=3x → update `agent-briefing.md` (preserve static sections).
- [ ] Learning engine audit available (`learning_engine/scripts/audit_learning_engine.py --report-only`).

## 4. Validation & Reporting
- [ ] Scanner output treated as leads only, not deliverables.
- [ ] FP filter + evidence validation + evidence hygiene applied before severity.
- [ ] 10-question FP gate + Findings Strength Verification before REPORTABLE.
- [ ] Structured summaries used (sub-agents/orchestrator).
- [ ] Report skills loaded only when requested (`report.md` command) and only for REPORTABLE findings.
- [ ] Evidence stored under `testing/<root-domain>/<subdomain>/` (requests/responses/screenshots/evidence/reports).
- [ ] No artifacts in project root.

## Current Status: Ready for supervised autonomous hunting
- [ ] All above items reviewed and confirmed for this workspace.
