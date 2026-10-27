# MASTER CONFIG: Complete Agent System Overview

## 1. System Architecture

### Configuration Files (Load Order)
| Order | File | Purpose | When |
| --- | --- | --- | --- |
| 1 | `agent-briefing.md` | Session briefing, priorities, current state | **Always first** |
| 2 | `AGENTS.md` | Constitution, boot sequence, scope, multi-agent rules | Always |
| 3 | `prioritization.md` | Signal engine, ranking, impact classes | Always |
| 4 | `runtime/AGENT_SKILL_ACTIVATION.md` | Skill activation guidance | On demand |
| 5 | `runtime/AGENT_INIT_TEMPLATE.md` | Initialization template | On demand |
| 6 | `references/VERIFICATION_CHECKLIST.md` | Readiness audit | On demand/debug |

### Skill Sources
| Source | Notes |
| --- | --- |
| `skills/` | Primary skill files (mirrors) |
| `.agents/skills/` | Active skill implementations |
| `runtime/registry.json` | **Authoritative** skill/agent registry |
| `scripts/skill_registry.py` | Resolver (use before testing) |
| `learning_engine/` | **Mandatory every hunt** (5 hooks) |
| `runtime/opencode/` | Orchestration/runtime (loader, manifest, ORCHESTRATION, agents) |

### Working Directory Tree
```
testing/
└── <root-domain>/
    ├── <subdomain>/
    │   ├── notes/        # notes, ledgers, mindmap, auth_session, understanding
    │   ├── requests/     # raw HTTP requests
    │   ├── responses/    # raw HTTP responses
    │   ├── screenshots/  # evidence screenshots
    │   ├── scripts/      # helper scripts
    │   ├── scans/        # scan outputs
    │   ├── wordlists/    # scoped wordlists
    │   ├── urls/         # discovered URLs
    │   ├── subdomains/   # subdomain lists
    │   ├── evidence/     # consolidated evidence
    │   └── reports/      # reports (only when requested)
    └── reports/          # cross-subdomain reports if needed
```
**Rule:** Never create target artifacts in project root. Create target folder first.

## 2. Execution Flow

### Phase 1: BOOT (< 5 min)
1. [ ] Read `agent-briefing.md` first
2. [ ] Load foundations: `master-bugbounty-rules` + `learning-engine-integration`
3. [ ] Load `AGENTS.md`, `prioritization.md`, `runtime/opencode/loader.md`, `runtime/opencode/manifest.md`, `runtime/registry.json`
4. [ ] Lock scope (exact host). Quick tech fingerprint (1-2 requests)
5. [ ] Check prior data in `testing/` and `memory/CONTEXT_LEDGER.md`
6. [ ] Bootstrap notes, create/update `MINDMAP.md`
7. [ ] Run `scripts/runtime_preflight.py --target "<exact target>" --scenario "<surface>" --mode <hunt|recon|scan|update> --workspace "testing/<root>/<subdomain>" --ensure-session`
8. [ ] **READY TO HUNT**

### Phase 2: DISCOVERY ↔ EXPLOIT (Interleaved)
- [ ] Exploit-first: when usable surface exists, test immediately (never wait for full inventory)
- [ ] Parallel bounded collection (see ORCHESTRATION.md)
- [ ] JS deep analysis feeds direct testing
- [ ] Tech-aware discovery with strict scope boundaries

### Phase 3: DEEP EXPLOIT
- [ ] Skill trigger sweep before every test
- [ ] Build attack model (asset/authority/attacker-controls/expected impact)
- [ ] Bypass ladder (change one variable at a time)
- [ ] Response-diff every test vs baseline
- [ ] FP DB check → replay 2x → response-diff → FP GATE on signal
- [ ] Maintain tested-variant ledger + chain board
- [ ] Exhaust high-value surfaces (30-60+ min when warranted)

### Phase 4: REPORT (Gated)
- [ ] Only CONFIRMED/REPORTABLE per gates
- [ ] Complete FP gate from `AGENTS.md`
- [ ] Apply false-positive-filter + evidence-validation-and-severity-calibration
- [ ] Rank by exploitability
- [ ] **No PoCs/reports until user asks**

## 3. Debugging Architecture
This file is the system overview. Load only when debugging architecture/configuration. For execution details see:
- [ ] `AGENTS.md` (constitution/flow)
- [ ] `runtime/opencode/ORCHESTRATION.md` (multi-agent)
- [ ] `runtime/opencode/loader.md` (runtime loading)
- [ ] `runtime/registry.json` (registry)
- [ ] `references/skill-router.md` (routing)
