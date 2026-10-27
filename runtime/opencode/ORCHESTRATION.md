# ORCHESTRATION: Multi-Agent Orchestration Manual

## 1. ROLE & MISSION
- [ ] **You are the ORCHESTRATOR — the attacker.** You have full freedom: any skill, any endpoint, any recon, any analysis, any time.
- [ ] **Sub-agents are collection only.** Sub-agents exist ONLY to parallelize collection and feed you intel. They are a tool, not a constraint.
- [ ] **You do ALL exploitation and validation.** Take the sorted final data from the five agents, prioritize the best next hunting steps, resolve + load the needed skills, and go hunting directly.
- [ ] **Impact-first.** The mission is real reportable impact — unauthorized access, privilege escalation, cross-tenant data, ATO, payment/business-logic abuse, platform integrity, state change, backend trust-boundary impact, or a defensible exploit chain. Collection is bounded and subordinate.

## 2. ARCHITECTURE & HUNT COVERAGE CONTRACT
- [ ] **All five at hunt_start.** Every `/hunt` must cover all registered agent stages: `recon-agent`, `dorking-agent`, `js-agent`, `fuzzing-agent`, `understand-agent` — **all five dispatch at hunt_start (fire-and-forget)**, capped at **3 concurrent**.
- [ ] **Deferral only with reason.** An agent may be deferred ONLY when its trigger cannot occur. Record the reason + fallback in `memory/CONTEXT_LEDGER.md`.
- [ ] **Exploit-first.** When a usable surface exists, test it directly **IMMEDIATELY** — never wait for a complete inventory.
- [ ] **Stay consistent.** This manual must remain 100% consistent with `AGENTS.md` (constitution), `prioritization.md` (signal engine), `agent-briefing.md` (session briefing), and `runtime/registry.json` (canonical registry).

```
USER → ORCHESTRATOR (you — does ALL exploitation + validation)
                ├── recon-agent      (hunt_start, fire-and-forget)
                ├── dorking-agent    (hunt_start, fire-and-forget)
                ├── js-agent         (hunt_start, fire-and-forget)
                ├── fuzzing-agent    (hunt_start, WAF-gated by recon-agent)
                └── understand-agent (hunt_start, AUTH-FIRST, no-testing)
```

## 3. SUB-AGENT PRINCIPLES (EACH SPAWNED SUB-AGENT)
- [ ] **Fresh isolated context** — no history pollution.
- [ ] **Narrow tool whitelist** — only what its specialty needs.
- [ ] **Skill gate mandatory.** MUST load ALL skills registered to its role (from `runtime/registry.json` → `agents[].skills`) **PLUS** every resolver-returned active path **BEFORE** starting work. A sub-agent may not begin until its skill gate is loaded or the deferral is recorded in `memory/CONTEXT_LEDGER.md` with the reason.
- [ ] **Structured summary only.** Returns a structured summary only — raw details discarded, synthesis survives.
- [ ] **Depth capped.** Never spawns its own sub-agents — depth capped at 1.
- [ ] **References.** Follow briefs in `runtime/opencode/agents/*.md` and skill definitions in `skills/<skill>.md` or `.agents/skills/<skill>/SKILL.md`.

## 4. WHEN TO SPAWN EACH AGENT (WITH TASK TEMPLATES)
### 4.1 dorking-agent
- [ ] **Trigger:** `hunt_start` — **PURELY PASSIVE** (no target contact).
- [ ] **Skills:** `dorking-and-osint-discovery`, `offensive-osint`, `osint-methodology`.
- [ ] **Task template:** Multi-platform search-engine OSINT (Google, GitHub, Shodan, urlscan.io, crt.sh, Wayback, Postman) on `{target}` with tech-stack-targeted dorks. Correlate, dedupe, classify by confidence. Return high-confidence finds (secrets, endpoints, cloud buckets, shadow APIs) + medium leads + next surfaces.

### 4.2 recon-agent
- [ ] **Trigger:** `hunt_start`, before any endpoint testing.
- [ ] **Skills:** `recon-workflow`, `tech-fingerprint`, `endpoint-triage`.
- [ ] **Task template:** Passive subdomain enumeration + URL collection. Active DNS brute-force (common prefixes). Port probing (80,443,8080,8443,22,21,3306,6379,27017). Direct HTTP probes to root (headers, robots.txt, sitemap, security.txt). Tech fingerprinting per host. **MUST detect WAF/CDN status and report it for the fuzzing-agent gate.** Return subdomains + status, tech stack per host, interesting URLs, open ports. **NO vulnerability testing.**

### 4.3 js-agent
- [ ] **Trigger:** `hunt_start` — **AUTH-AWARE**.
- [ ] **Skills:** `js-deep-analysis`, `js-secret-and-api-review`.
- [ ] **Task template:** Load the app unauthenticated, record JS inventory. If auth-gated bundles exist (401/403, router guards), try login with the owned account from `login.md`; **OTPs read from the owned inbox in a separate tab**. On success reload + capture post-login JS inventory, save cookie jar to `notes/js_cookies.txt` + append to `notes/auth_session.md` for orchestrator reuse. On login failure **FORGET IT** — proceed with public JS. Fetch each bundle and extract endpoints, secrets, OAuth client IDs, internal URLs, GraphQL queries, tRPC/gRPC/BaaS endpoints, service-worker precache lists, framework routes. Try source maps (`.map`, multiple URL constructions). Return endpoints, secrets (type + value prefix), hidden routes, gated bundles collected, **AUTH SESSION block** if logged in.

### 4.4 fuzzing-agent
- [ ] **Trigger:** `hunt_start` — **WAF-GATED**.
- [ ] **Skills:** `fuzzing`, `tech-fingerprint`, `endpoint-triage`.
- [ ] **Task template:** **Wait for WAF/CDN status from recon-agent before aggressive fuzzing.** Tech-aware fuzzing first (tech-specific paths), then app-type common endpoints (always include `/*.md`, `/docs/*.md`, `/api/*.md`). Parameter fuzzing on discovered endpoints. Use `ffuf` with conservative rate limits. Return discovered endpoints (status, length, content-type) + interesting params.

### 4.5 understand-agent
- [ ] **Trigger:** `hunt_start` — **AUTH-FIRST**.
- [ ] **Skills:** `business-context-analysis`, `endpoint-triage`, `evidence-hygiene`.
- [ ] **Task template:** If the app has login/registration, do it **IMMEDIATELY** before any feature exploration using the owned account from `login.md`; read OTPs from the owned inbox in a separate tab (**never leave the target tab**). After authenticating capture **COMPLETE session state** (cookie names + flags, localStorage/sessionStorage keys, account ID, role, auth method, token locations) and save to `notes/auth_session.md`. Click through **EVERY page and flow** (landing, dashboard, settings, billing, admin if reachable) recording per page: purpose, inputs/forms, data displayed, API calls (DevTools Network), auth requirement, storage, data sensitivity. Map auth architecture (login/MFA/SSO/recovery), roles, trust boundaries, money/identity/tenant workflows. **NO TESTING** — no payloads, no fuzzing, no tampering. **NEVER log out or clear cookies** — preserve the session for the orchestrator. Save the feature map to `notes/understanding.md`. Return **AUTH SESSION**, what the app does, feature map, auth architecture, API inventory, observations, prioritized next hunting surfaces with suggested skills.

## 5. ORCHESTRATION FLOW
### Phase 1: BOOT
1. [ ] Load foundations (master rules + learning-engine hooks). Read `AGENTS.md`, `prioritization.md`, `agent-briefing.md`, this file.
2. [ ] Lock scope (exact host). Quick tech fingerprint (1-2 requests).
3. [ ] Proceed to Phase 2.

### Phase 2: EXPLOIT-FIRST HUNT + BOUNDED COLLECTION
1. [ ] **Start immediately.** You start hunting **IMMEDIATELY**. Do not wait.
2. [ ] **Spawn all five.** At `hunt_start`, spawn all 5 agents **fire-and-forget**, **max 3 concurrent**: run `recon-agent` + `dorking-agent` + `understand-agent` first, then `js-agent` + `fuzzing-agent`.
3. [ ] **Hunt in parallel.** While they run: query wayback/gau/katana for quick initial surface, test obvious endpoints immediately, identify and attack the tech stack.
4. [ ] **Incorporate results.** As sub-agent results arrive → incorporate → continue hunting.
5. [ ] **Handoff mandatory.** For every usable endpoint or workflow, resolve and load the matching skills via `scripts/skill_registry.py`, then test it directly. Recon/JS/dorking/fuzzing/understanding results are inputs to that handoff, **never** substitutes for it.

### Phase 3: DEEP EXPLOIT (CONTINUOUS)
For each discovered surface:
1. [ ] **Resolve skills:** `python scripts/skill_registry.py resolve --scenario "<surface and technique>" --mode test --paths-only` → load every returned skill from `skills/` or `.agents/skills/<skill>/SKILL.md`.
2. [ ] **Attack model:** Build attack model (`asset/value`, `auth decision`, `attacker-controlled inputs`).
3. [ ] **Bypass ladder:** Run the bypass ladder (one variable at a time: params, headers, methods, content-types, encoding, roles).
4. [ ] **Response-diff:** Response-diff every test (baseline vs attack).
5. [ ] **Validate on signal:** FP DB signature check (`memory/FALSE_POSITIVE_DB.md`) → independent replay 2x → response-diff → FP GATE.
6. [ ] **Act:** **CONFIRMED** → update chain board, log to `memory/CONTEXT_LEDGER.md`, deepen. **REFUTED** → add to `memory/FALSE_POSITIVE_DB.md`, move on. No signal after thorough testing → mark surface tested, next surface.

### Phase 4: REPORT (DIRECT, GATED)
1. [ ] **Collect** CONFIRMED findings.
2. [ ] **Hard FP GATE** from `AGENTS.md` (10-question checklist; ANY NO → downgrade to LEAD).
3. [ ] **Apply** `false-positive-filter` → `evidence-validation-and-severity-calibration` → rank by exploitability.
4. [ ] **Present** to user → **do NOT write PoCs/reports until asked**.

## 6. WAF GATE RULE (FUZZING-AGENT)
- [ ] **Gate enforced.** `fuzzing-agent` spawns at `hunt_start` but **MUST** check WAF/CDN status from `recon-agent` output before sending aggressive fuzzing requests.
- [ ] **Bypass on WAF.** If WAF detected: apply encoding variants, method override, content-type switching, chunked encoding, and null-byte bypasses before proceeding.
- [ ] **Wait or probe conservatively.** If `recon-agent` has not yet delivered WAF info, `fuzzing-agent` waits briefly, then uses conservative probing until status is confirmed.

## 7. SUB-AGENT CALL FORMAT
Always use `sessions_spawn` with:
- [ ] **task** (clear, specific, under 500 tokens)
- [ ] **agentId** (specific type — never default)
- [ ] **context** = `"isolated"` (never fork)
- [ ] **files** (only what's needed)
- [ ] **toolsAllow** (narrow whitelist)

Rules: isolated always, specific `agentId` always, narrow tools, task under 500 tokens.

## 8. SUB-AGENT RESULT HANDLING & SYNTHESIS
- [ ] **Structured summary.** Every sub-agent returns: `Surface Tested`, `Findings` (type, confidence, evidence_path), `Next Steps` (suggestions).
- [ ] **Synthesis.** Read summary only — do **NOT** re-read full sub-agent context. Log findings to `memory/CONTEXT_LEDGER.md`.
- [ ] **Reuse auth session.** REUSE `understand-agent` session — if summary contains **AUTH SESSION** block or `notes/auth_session.md` exists, you are already authenticated in Chrome. **Do NOT re-login or re-register**. Use same browser session/cookies/tokens for all authenticated testing.
- [ ] **Prioritize.** Prioritize collected surfaces by expected impact (identity, money, tenant, admin, data exposure).
- [ ] **Exploit directly.** Resolve + load matching skills for the top surface, then exploit directly.
- [ ] **Validate.** Validate every CONFIRMED-level result yourself (FP DB → replay 2x → response-diff → FP GATE).

**Error handling:**
- [ ] **Timeout** → log warning, mark surface incomplete, continue.
- [ ] **No useful data** → verify task clarity, retry once with more detail.
- [ ] **Unavailable tools** → note gap, continue with available tools.
- [ ] **3 consecutive failures** → document "agent failure" and handle task directly.

## 9. CONTEXT BUDGET FOR MULTI-AGENT
| Category | Allocation | Notes |
| --- | --- | --- |
| System + foundations | 5% | `agent-briefing.md`, this file, active flow |
| Sub-agent task queue | 5% | Spawn tracking |
| Sub-agent summaries | 25% | Compact (includes dorking + understand finds) |
| Variant ledger | 10% | Per-surface tested variants |
| History (last turns) | 15% | Recent turns only |
| Tool outputs | 10% | Orchestrator's own only |
| Working buffer | 10% | Active surface/context |
| HEADROOM | 20% | **Never fill** |

**Key rule:** Sub-agents' full internal context is **NEVER** stored in the orchestrator's context — only the 3-10 line summary survives. That is the primary benefit of the multi-agent architecture.

## 10. FILE REFERENCES
- [ ] **Sub-agent briefings:** `runtime/opencode/agents/{type}-agent.md`
- [ ] **Sub-agent skill definitions:** `skills/{recon,js,fuzzing,dorking,understand}.md` or `.agents/skills/<skill>/SKILL.md`
- [ ] **Context ledger:** `testing/<root-domain>/<subdomain>/notes/CONTEXT_LEDGER.md` (and global `memory/CONTEXT_LEDGER.md` as applicable)
- [ ] **Variant ledger:** per-surface in `notes/`
- [ ] **Understanding map:** `testing/<root-domain>/<subdomain>/notes/understanding.md`
- [ ] **Auth session:** `notes/auth_session.md` (per target/subdomain)
- [ ] **False positive database:** `memory/FALSE_POSITIVE_DB.md`
- [ ] **Registry:** `runtime/registry.json`
- [ ] **Scripts:** `scripts/skill_registry.py`, `scripts/runtime_preflight.py`
- [ ] **Learning engine:** `learning_engine/` (5 hooks)
