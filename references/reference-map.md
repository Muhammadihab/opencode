# REFERENCE MAP: Cross-file Dependencies & Routing

## Reference Conventions
- `../FILE.md` = project root
- `FILE.md` = same directory
- `../` = up one level

## File Cross-Reference Matrix

| Major File | Purpose | Referenced BY | References TO |
| --- | --- | --- | --- |
| `agent-briefing.md` | Session briefing/state | `AGENTS.md`, all `.opencode/commands/*`, `ORCHESTRATION.md`, boot sequence | `AGENTS.md`, `prioritization.md`, `runtime/*`, `skills/`, `memory/`, `writeups/`, `testing/` |
| `AGENTS.md` | Constitution | All commands, `ORCHESTRATION.md`, skills, runtime | `agent-briefing.md`, `prioritization.md`, `runtime/opencode/{loader,manifest,ORCHESTRATION}.md`, `runtime/registry.json`, `scripts/*`, `memory/*`, `testing/` |
| `prioritization.md` | Signal engine | `AGENTS.md`, commands, skills | `memory/`, `testing/`, impact classes, ranking rules |
| `runtime/opencode/ORCHESTRATION.md` | Multi-agent manual | `AGENTS.md`, `/hunt`, `references/*` | `AGENTS.md`, `prioritization.md`, `agent-briefing.md`, `runtime/registry.json`, `scripts/skill_registry.py`, `runtime/preflight`, `learning_engine/`, `memory/*`, `notes/*`, `skills/`, `.agents/skills/` |
| `runtime/opencode/loader.md` | Runtime loader/BOOT | Commands, `AGENTS.md` | `runtime/opencode/{manifest,ORCHESTRATION}.md`, `runtime/registry.json`, `agent-briefing.md`, foundations |
| `runtime/opencode/manifest.md` | Manifest | Loader/commands | Runtime components, agents, skills |
| `runtime/opencode/agents/*.md` | Agent briefings | `ORCHESTRATION.md`, spawns | Skills registered in `runtime/registry.json`, tools, scope rules |
| `runtime/registry.json` | **Authoritative** registry | All commands, ORCHESTRATION, loader, skill-router | Skills, agents, paths |
| `scripts/skill_registry.py` | Resolver/checker | All commands, ORCHESTRATION, skill-router | `runtime/registry.json`, `skills/`, `.agents/skills/` |
| `scripts/runtime_preflight.py` | Preflight/bootstrap | All commands, boot | `agent-briefing.md`, target workspace, session |
| `scripts/update.sh` | Update pipeline | `/update` command | `writeups/raw/`, `writeups/processed/`, `writeups/index.md`, `memory/`, `agent-briefing.md` |
| `skills/master-bugbounty-rules.md` | Foundation (first) | All sessions/commands | `AGENTS.md`, `prioritization.md`, `agent-briefing.md`, `login.md`, `scripts/skill_registry.py`, `testing/` |
| `skills/learning-engine-integration.md` | Foundation (second) | All sessions | `learning_engine/`, `memory/`, `writeups/` |
| `memory/report-lessons.md` | Lessons | Commands, skills, update | Feeds triage/reporting |
| `memory/patterns.md` | Patterns | Skills, update | Feeds hunting logic |
| `memory/methodology.md` | Methodology | Skills, update | Feeds approach |
| `memory/targets/<vuln>.md` | Vuln checklists | Skill gate, hunt | Generated via `/update` (>=3x) |
| `memory/FALSE_POSITIVE_DB.md` | FP DB | FP gate, ORCHESTRATION | Signature hashes |
| `memory/CONTEXT_LEDGER.md` | Action log | ORCHESTRATION, agents | Appended per action/spawn/result |
| `writeups/raw/` | Raw intel | `/update` | Processed by pipeline |
| `writeups/processed/` | Structured intel | `/update`, skills | Feeds lessons/memory |
| `writeups/index.md` | Index (table) | Retrieval | Built by `/update` (retrieval only) |
| `.opencode/commands/hunt.md` | Hunt command | User | All above, browser, agents, FP gate |
| `.opencode/commands/recon.md` | Recon command | User | Foundations, resolver, engine |
| `.opencode/commands/scan.md` | Scan command | User | Triage, resolver, engine |
| `.opencode/commands/update.md` | Update command | User | Pipeline scripts, memory, briefing |
| `.opencode/commands/report.md` | Report command | User | FP gate, report skills, evidence paths |
| `references/skill-router.md` | Routing cross-check | Commands/skills/runtime | `runtime/registry.json`, `scripts/skill_registry.py`, skills |
| `references/VERIFICATION_CHECKLIST.md` | Audit | Runtime/debug | All major components |
| `references/MASTER_CONFIG.md` | Overview | Debug/architecture | Load order, flow, paths |
| `references/CONFIG_INDEX.md` | Lightweight map | Runtime/debug | Load order, guardrails |
| `references/ownership-map.md` | Governance | Runtime/debug | Ownership/policies |
| `references/reference-map.md` | Dependencies | Runtime/debug | This matrix |

## Dependency Note
- **Hub:** `runtime/registry.json` + `scripts/skill_registry.py` are the routing hub.
- **Constitution:** `AGENTS.md` + `prioritization.md` are immutable.
- **Orchestration:** `runtime/opencode/ORCHESTRATION.md` must stay consistent with constitution and registry.
- **Every reference must resolve to an existing path** — run a link check and report any broken references found.
