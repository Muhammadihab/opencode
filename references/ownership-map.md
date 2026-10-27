# OWNERSHIP MAP: File Governance & Responsibility

## Core Principle
Shared files are **immutable**. Runtime files are **orchestration-only**. No duplication.

## Table 1 — Shared Knowledge (Immutable, Root Level)
| File | Owner | Purpose | Modification Policy |
| --- | --- | --- | --- |
| `agent-briefing.md` | System / Update Pipeline | Session briefing/state | **Updated via `/update` only**. Preserve static sections. Update timestamp + knowledge count. |
| `AGENTS.md` | Constitution | Core rules/workflow/boot | **DO NOT MODIFY** |
| `prioritization.md` | Constitution | Signal engine/ranking | **DO NOT MODIFY** |
| `skills/master-bugbounty-rules.md` | Foundation | Operating system | **DO NOT MODIFY** |
| `skills/learning-engine-integration.md` | Foundation | Learning hooks | **DO NOT MODIFY** |
| `runtime/AGENT_SKILL_ACTIVATION.md` | Reference | Skill activation guidance | Reference only (coordinated change if necessary) |
| `runtime/AGENT_INIT_TEMPLATE.md` | Reference | Init template | Reference only (coordinated change if necessary) |

## Table 2 — Shared Knowledge Subdirectories (Append-Only)
| Path | Owner | Purpose | Modification Policy |
| --- | --- | --- | --- |
| `skills/` | Skill Registry | Skill definitions | Add/update via registry/skill work. Follow resolver paths. |
| `.agents/skills/` | Skill Registry | Active skill implementations | Add/update via registry. |
| `memory/report-lessons.md` | Learning Engine | Lessons learned | **Append-only** via `/update` pipeline. |
| `memory/patterns.md` | Learning Engine | Patterns | **Append-only/regenerate** via `/update`. |
| `memory/methodology.md` | Learning Engine | Methodology | **Append-only/regenerate** via `/update`. |
| `memory/targets/<vuln>.md` | Learning Engine | Vuln checklists | Generate/refresh **only** for types appearing **>= 3 times** via `/update`. |
| `memory/FALSE_POSITIVE_DB.md` | Orchestrator | FP DB | Append on confirmed FP; signature-hash checked. |
| `memory/CONTEXT_LEDGER.md` | Orchestrator | Action log | Append-only per target/global as needed. |
| `writeups/raw/` | Update Pipeline | Raw write-ups | Add new files (naming: `[source]/[topic]_[timestamp].md`). |
| `writeups/processed/` | Update Pipeline | Structured write-ups | Regenerate from raw with triple-layer dedup. |
| `writeups/index.md` | Update Pipeline | Index table | **Rebuild as TABLE** (Title, Vuln Type, Target, Source) via `/update`. Retrieval only. |
| `learning_engine/` | Learning Engine | Hooks/scripts | Mandatory every hunt; update via pipeline/coordinated changes. |

## Table 3 — Runtime Configuration (Lightweight Orchestration)
| Path | Owner | Purpose | Modification Policy |
| --- | --- | --- | --- |
| `runtime/opencode/loader.md` | Orchestrator Runtime | BOOT loader | Orchestration-only. Execute verbatim. Coordinated changes only. |
| `runtime/opencode/manifest.md` | Orchestrator Runtime | Manifest | Orchestration-only. Coordinated changes only. |
| `runtime/opencode/ORCHESTRATION.md` | Orchestrator Runtime | Multi-agent manual | Orchestration-only. Coordinated changes only. |
| `runtime/opencode/agents/*.md` | Orchestrator Runtime | Agent briefings | Orchestration-only. Coordinated changes only. |
| `runtime/registry.json` | Registry | **Authoritative** registry | Authoritative; changes via registry management/coordinated. |
| `.opencode/commands/*.md` | Commands | Custom commands | Orchestration-only. Coordinated changes only. |
| `scripts/skill_registry.py` | Registry | Resolver/checker | Functional tool; coordinated changes only. |
| `scripts/runtime_preflight.py` | Runtime | Preflight/bootstrap | Functional tool; coordinated changes only. |
| `scripts/update.sh` | Update Pipeline | Update pipeline | Functional tool; coordinated changes only. |

## Table 4 — Target Workspace
| Path | Owner | Purpose | Modification Policy |
| --- | --- | --- | --- |
| `testing/<root-domain>/` | Hunting Agent | Target workspace | Per-target artifacts. Owned by hunting agent. No governance review needed. |
| `testing/<root-domain>/<subdomain>/` | Hunting Agent | Subdomain workspace | Standard folders: `notes/`, `requests/`, `responses/`, `screenshots/`, `scripts/`, `scans/`, `wordlists/`, `urls/`, `subdomains/`, `evidence/`, `reports/`. Owned by hunting agent. |
| `logs/` | Runtime | Logs | Operational; cleanup as needed. |
| `wordlist/` | Project | Project wordlists | Prefer over SecLists; add scoped lists as needed. |

**Note:** All files referenced by `AGENTS.md`, `prioritization.md`, `ORCHESTRATION.md`, `agent-briefing.md`, commands, and registry should follow this governance.
