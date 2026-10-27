# OpenCode Runtime Manifest

- **Title:** OpenCode Runtime Manifest
- **Version:** 1.0
- **Runtime:** OpenCode — Practical 4-Phase Interleaved Flow
- **Last Updated:** 2026-10-27
- **Purpose:** Define what OpenCode provides, requires, and governs; canonical source is `../registry.json`; generated snapshots are reference views only.

# RUNTIME PROFILE

| Attribute | Value |
|---|---|
| Architecture | Multi-Agent (Orchestrator + 5 collection sub-agents; orchestrator does ALL exploitation + validation). |
| Workflow | Exploit-first orchestrator: BOOT → resolve skills → immediate exploit loop with bounded dorking/recon/JS/fuzzing/understanding → validate → REPORT. |
| Context strategy | Orchestrator loads foundations + ORCHESTRATION.md; sub-agents get fresh isolated context per spawn. |
| Skill activation | Every agent resolves the scenario via `scripts/skill_registry.py` and loads every returned active skill path. |
| Sub-agent types | `dorking-agent`, `recon-agent`, `js-agent`, `fuzzing-agent`, `understand-agent`. |
| Phase coverage | BOOT (<5 min) → DISPATCH (parallel sub-agents) → SYNTHESIS → EXPLOIT (orchestrator direct) → REPORT (gated). |
| Parameter testing | Orchestrator, comprehensive all vectors. |
| Memory model | Orchestrator maintains `CONTEXT_LEDGER`, sub-agent summaries, variant ledger; sub-agents stateless. |
| Scope model | Locked at start; scope-enforcer gate loaded before any expansion; sub-agents inherit scope constraints. |
| Learning | Orchestrator calls learning engine; sub-agents do not persist learning. |
| Reporting | Gated — no auto-reports. |
| Parallelism | Max 3 concurrent sub-agents (recon → dorking → understand → js → fuzzing waves). |

# WHAT OPENCODE PROVIDES (shared knowledge — read-only reference)

- **Canonical skill registry:** `runtime/registry.json` (all skills indexed by attack surface, load order, autonomous directives — all agents use it as truth).
- **Signal prioritization:** `prioritization.md` (P1-P4, chain analysis, when to stop; reference only — flow is defined in `ORCHESTRATION.md` + `AGENTS.md`).
- **Foundation rules:** `skills/master-bugbounty-rules.md` (load first).
- **Learning engine skill:** `.agents/skills/learning-engine-integration/SKILL.md` (load second).
- **Session briefing:** `agent-briefing.md` (read first, every session).
- **Memory base:** `memory/` (methodology.md, patterns.md, report-lessons.md, targets/).
- **Evidence repository:** `writeups/` (index.md, processed/, raw/ via /update).
- **Skill library:** `skills/` + `.agents/skills/` (one file per skill, loaded on demand, never duplicated locally).
- **Learning engine:** `learning_engine/` (Python module, 5 hooks).
- **Multi-agent config:** `ORCHESTRATION.md` + `agents/` directory (5 briefing files).
- **Runtime config:** `loader.md` + `manifest.md` (this file).

# WHAT OPENCODE REQUIRES AT STARTUP

## Required files

| File | Purpose | Location |
|---|---|---|
| `agent-briefing.md` | Session start briefing | project root |
| `runtime/registry.json` | Authoritative skill registry | `runtime/` |
| `prioritization.md` | Signal engine | project root |
| `master-bugbounty-rules` skill | Foundation rules | `skills/` or `.agents/skills/` |
| `learning-engine-integration` skill | Learning hooks | `.agents/skills/` |
| `skills/` folder | Skill library | project root |
| `memory/` folder | Memory base | project root |
| `learning_engine/` | Learning module | project root |
| `writeups/` folder | Evidence repository | project root |
| `testing/` folder | Target workspace | project root |

## Workspace requirements

- **Target structure:** `testing/<root-domain>/` with standard subfolders (notes, requests, responses, screenshots, scripts, scans, wordlists, urls, subdomains, evidence, reports).
- **Browser:** Chrome for app exploration.
- **Tools:** Terminal for local tools (ffuf, httpx, katana, nuclei, subfinder, amass — verify availability).
- **OOB:** Optional user-provided Burp Collaborator domain (never curl/access directly — embed in payloads only).

# AGENT DEFINITIONS

## Orchestrator (main agent)

- **Full tool access, full freedom.** Performs ALL exploitation and validation directly.
- **Responsibilities:** Consume sorted final data from the five agents, prioritize next steps, resolve + load skills, hunt, validate against the FP gate. Decompose collection into the 5 parallel sub-agents, exploit everything yourself.
- **Tools:** Full (read, write, glob, grep, web_search, bash, sessions_spawn, chrome browser + devtools MCP).
- **Loaded at boot:** `agent-briefing.md`, `AGENTS.md`, `ORCHESTRATION.md`, `master-bugbounty-rules`, `learning-engine-integration`.

## Sub-agent registry

| Agent ID | Role | Tool whitelist | Max spawns/session | Context |
|---|---|---|---|---|
| `dorking-agent` | Passive OSINT | read, glob, grep, web_search, bash (public sources only) | 2 | Isolated |
| `recon-agent` | Passive+active recon incl. subdomains, URLs, tech fingerprint, DNS brute-force, port probes, HTTP probes, WAF/CDN detection | read, glob, grep, web_search, bash (subfinder, amass, httpx, katana, waybackurls, gau, curl, Test-NetConnection) | 2 | Isolated |
| `js-agent` | JS bundle + source map analysis, AUTH-AWARE | read, glob, grep, web_search, bash(curl, python), chrome MCP | 4 | Isolated |
| `fuzzing-agent` | Tech-aware endpoint/param fuzzing, WAF-gated | read, write, glob, bash(ffuf, curl, httpx) | 6 | Isolated |
| `understand-agent` | AUTH-FIRST browse + click, maps app, delivers session to `notes/auth_session.md`, NO testing | read, glob, grep, web_search, bash(safe GET only), chrome MCP | 2 | Isolated |

## Spawning rules

- **Call pattern:** `sessions_spawn(task, agentId, context="isolated", toolsAllow=[...])`
- **Strictness:** Never `context="fork"`; never omit agentId; toolsAllow must match the whitelist exactly.
- **Limits:** Max 3 concurrent; 3 consecutive failures → document + handle directly; timeout 5 min default, 10 for recon-agent and understand-agent.
- **Briefings:** `agents/{type}-agent.md` loaded on spawn — define identity, tool whitelist, procedure, output format, quality rules.

# WORKFLOW EXECUTION MODEL

Every hunt follows this orchestrated dispatch sequence:

1. **BOOT (<5 min):** Read `agent-briefing.md` → read `ORCHESTRATION.md` → load foundations → lock scope, quick fingerprint, check workspace history → session bootstrap → READY TO DISPATCH.
2. **DISPATCH ALL COLLECTION AGENTS at hunt_start (max 3 concurrent: recon + dorking + understand first, then js + fuzzing):** `recon-agent` (passive+active recon + WAF/CDN detection), `dorking-agent` (passive OSINT), `understand-agent` (AUTH-FIRST, delivers live session — no re-login), `js-agent` (AUTH-AWARE), `fuzzing-agent` (WAF-GATED). Do NOT wait — start exploiting immediately; as results arrive update `CONTEXT_LEDGER.md` and incorporate.
3. **EXPLOIT ORCHESTRATOR DIRECT (continuous):** Per surface resolve + load skills (`scripts/skill_registry.py resolve --mode test --paths-only`) → attack model → baseline → bypass ladder (params, headers, methods, content-type, encoding, roles) → response-diff every test → update `CONTEXT_LEDGER.md`; prioritize with the understand-agent feature map (money, identity, tenant, admin, data first).
4. **VALIDATE ORCHESTRATOR DIRECT:** For each HIGH-CONFIDENCE+ finding: FP DB signature check → independent replay 2x → response-diff → HARD FP GATE from `AGENTS.md`; CONFIRMED → chain board + evidence path; REFUTED → add to `FALSE_POSITIVE_DB.md`.
5. **REPORT (gated):** Collect CONFIRMED → FP filter + evidence validation → rank by exploitability → structured summary in notes → no PoCs/reports until asked.

## Key discipline requirements

| Requirement | Rule |
|---|---|
| Multi-agent | Orchestrator full freedom; every hunt covers all 5 stages; direct work never replaces handoff records. |
| Exploitation | Only by orchestrator. |
| Validation | Only by orchestrator. |
| Startup | Foundations + ORCHESTRATION.md < 5 min, rest on demand. |
| Sub-agent context | Always isolated. |
| Tool whitelists | Narrow per role. |
| Scope | Locked, expansion only for chains/shared vulns. |
| Context budget | 25% headroom, never store sub-agent contexts. |
| Finding pipeline | OBSERVATION → LEAD → HIGH-CONF → CONFIRMED → VALIDATED → REPORTABLE. |
| No-progress | 5 same-pattern results → change surface. |
| Circuit breaker | 5× 403/429 → 60s backoff → stop surface. |
| Sub-agent failures | 3 → document, handle directly once, then skip. |
| Parallelism | Max 3, never two on one endpoint. |
| Memory | Orchestrator keeps ledger + summaries + variant ledger. |
| Bypass strategy | 3-5 families on promising leads. |
| Evidence | Raw HTTP from own evidence files. |
| Reporting | Gated; no auto-reports. |
| Browser | Reuse window, new tab default. |

# SKILL ACTIVATION MANIFEST

OpenCode automatically activates all applicable skills per discovered surface.

- **Mandatory load order:** 1) `master-bugbounty-rules`, 2) `learning-engine-integration`, 3) all other skills per category as triggered.
- **Canonical source:** `runtime/registry.json` — always run `scripts/skill_registry.py resolve --scenario "<surface>" --mode <mode> --paths-only`.

| Category | Triggered skills (compatibility map) |
|---|---|
| Recon/Discovery | `subdomain-enum`, `tech-fingerprint`, `wayback-analysis`, `js-deep-analysis` |
| APIs | `api-security-testing`, `graphql-testing`, `request-response-analyzer`, `request-response-manipulation` |
| Parameters | `parameter-analysis-and-guessing`, `idor-testing`, `authz-access-control-tester` |
| Auth | `login-security-testing`, `forgot-password-testing`, `two-factor-bypass-testing`, `captcha-bypass-testing`, `oauth-oidc-testing`, `saml-testing`, `jwt-testing` |
| Authz | `privilege-escalation-testing`, `idor-testing`, `authz-access-control-tester` |
| Client | `xss-client-side-testing`, `dom-xss-testing`, `postmessage-testing`, `csp-bypass` |
| Blind/OOB | `blind-vuln`, `ssrf-redirect-url-testing`, `xxe-testing` |
| Realtime | `websocket-testing` |
| Infrastructure | `host-header-injection`, `cors-misconfiguration`, `cache-poisoning-testing`, `http-smuggling-testing` |
| Injection/Parsing | `sqli-testing`, `command-injection`, `ssti-testing`, `xxe-testing`, `file-upload-testing`, `path-traversal` |
| Cloud/Mobile/AI | `cloud-storage-review`, `cloud-iam-deep`, `mobile-api-testing`, `llm-ai-security-testing` |
| Web3 | `web3-smart-contract` (if applicable) |
| Workflow/Chain | `business-logic-testing`, `business-context-analysis`, `race-condition-testing` |
| Foundation | `master-bugbounty-rules`, `learning-engine-integration` |
| Reporting | `reporting-standards` (as needed) |

# MEMORY & LEARNING MODEL

- **Continuous context:** Must maintain every URL/endpoint/param tested, all payloads/variants/bypass families, success indicators, FPs, dead ends, findings with proof level + chains, active/deferred hypotheses.
- **Learning engine hooks:** `before_recon(target, techs)`, `during_testing(signals)`, `after_finding(target, endpoint, vulnerability_class, signals, validation_state, source_provenance)`, `before_summary(findings)`, `after_triage(finding_id, feedback_type, notes, provenance)` — never session-level outcomes.
- **Knowledge priority order:** `memory/targets/<vuln>.md` → `memory/report-lessons.md` → `memory/patterns.md` → `memory/methodology.md` → `writeups/processed/` (5-7 best matches) → base training.

# REPORTING & EVIDENCE STANDARDS

## Minimum Reportability Bar
Reproducible raw HTTP proving server-side impact; no physical access/social engineering/self-XSS; real-world impact demonstrated; tested across representative contexts.

## Evidence checklist
- [ ] Scope confirmation
- [ ] Exact URL/endpoint/method/timestamp
- [ ] Raw baseline + modified request/response
- [ ] Account/role/tenant/ownership context
- [ ] Before/after state for writes
- [ ] Screenshots support only
- [ ] Impact statement + limitations + safe reproduction
- [ ] FP reasoning when weak

# WHEN HUNT ENDS

- **If finding:** Update learning engine, preserve evidence, wait for user instruction on PoC/report.
- **If no finding:** Leave structured summary, tested-surfaces list, tested-variant ledger with full parameter coverage, open leads, deferred follow-ups, all discovered URLs with attack models in notes.
- **Always:** Update target notes, call learning engine to ingest session outcome.

# DIFFERENCES FROM ANTIGRAVITY CLI RUNTIME

| Aspect | OpenCode | Antigravity CLI Runtime |
|---|---|---|
| Architecture | Multi-Agent (Orchestrator + 5 collection sub-agents) | Single-agent |
| Phases | Exploit-first dispatch: BOOT → DISPATCH → SYNTHESIS → EXPLOIT → REPORT | 4 interleaved phases |
| Preload | Foundations + ORCHESTRATION.md | Foundations only |
| Skill activation | Orchestrator any skill anytime via resolver | Triggered as needed |
| Memory model | Comprehensive ledger + summaries + variant ledger | Lightweight P1/P2 |
| Parameter testing | Systematic all vectors | High-signal only |
| Finding validation | FP DB + replay 2x + response-diff + FP GATE | Self-validated |
| Time per surface | Priority budget (prioritization.md): P1 60-120, P2 30-60, P3 10-15, P4 <=10 min | 10-15 max, skip P4 |
| Primary guide | ORCHESTRATION.md + AGENTS.md | prioritization.md |

# NEXT STEPS

1. **Startup:** Execute `loader.md` → load foundations + `ORCHESTRATION.md` → spawn all 5 collection agents.
2. **Hunting:** Exploit immediately, bounded feeds, max 3 concurrent.
3. **Spawning:** `sessions_spawn` with `context="isolated"`, never fork.
4. **Synthesis:** Summaries only, prioritize, update `CONTEXT_LEDGER.md`.
5. **Validation:** Every HIGH-CONFIDENCE+ finding → FP DB → replay 2x → response-diff → FP GATE.
6. **Reporting:** Collect CONFIRMED, FP filter, rank, present — no auto-reports.

**OpenCode runtime is now initialized.**
