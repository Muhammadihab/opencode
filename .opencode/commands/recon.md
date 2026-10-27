---
description: "Exploit-first scope-safe bug bounty discovery and attack-surface prioritization"
agent: build
---
# RECON: Exploit-first scope-safe discovery

## MANDATES
- [ ] **Exploit-first**: Minimum-viable recon to find an authorized high-value surface, then enter the exploit loop immediately. Never build an inventory without testing.
- [ ] **Scope-safe**: No brute force, DoS, credential abuse, destructive actions, third-party data access.
- [ ] **Foundations**: Follow `AGENTS.md` and `prioritization.md`.
- [ ] **Artifacts**: Never write to project root. All artifacts under `testing/<root-domain>/<subdomain>/`.
- [ ] **Scope lock**: Exact-host scope. No `*.<root>` fuzzing without approval. Stay on supplied target.

## REQUIRED CONTEXT
1. [ ] **Briefing**: Read `agent-briefing.md`.
2. [ ] **Memory**: Read `memory/report-lessons.md`, `memory/patterns.md`, `memory/methodology.md`.
3. [ ] **Registry**: Verify `python scripts/skill_registry.py check`.
4. [ ] **Preflight**: Run `python scripts/runtime_preflight.py --target "<exact target>" --scenario "<initial surface>" --mode recon --workspace "testing/<root>/<subdomain>" --ensure-session`. Stop if blocked.
5. [ ] **Resolver**: Resolve with `--mode recon` and load **every** returned skill from `skills/<skill>.md` or `.agents/skills/<skill>/SKILL.md`.
6. [ ] **Engine**: Call `learning_engine.before_recon(target, technologies)` after fingerprinting and record the plan in `notes/`.

## RECON SKILL STACK (LOAD AS NEEDED/TRIGGERED)
Load these when relevant (resolver will return matching ones; load all returned):
- `master-bugbounty-rules`, `learning-engine-integration`
- `recon-workflow`, `tech-fingerprint`, `endpoint-triage`, `fuzzing`
- `dorking-and-osint-discovery`, `offensive-osint`, `osint-methodology`
- `js-deep-analysis`, `js-secret-and-api-review`
- `business-context-analysis`, `exploit-chain-analysis`
- `evidence-hygiene`, `structured-summary-reporting`

## WORKFLOW
1. [ ] **Passive recon**: Wayback, CT logs, subdomains (scope-safe, passive where possible).
2. [ ] **Tech fingerprint**: Identify stack/framework/auth/CDN/WAF. Record in `notes/`.
3. [ ] **Prioritize**: Pick the **highest-value surface** (object/workflow/role boundary/token/upload/URL fetcher) — not longest list.
4. [ ] **Test immediately**: Stop collecting and test the chosen surface. Run skill trigger sweep + load matching skills.
5. [ ] **Expand**: If bug class hits, resolver -> load skills -> test before collecting more. Use JS analysis + tech-aware fuzzing.
6. [ ] **Boundaries**: Exact-host first. Sub-subdomain permutations only inside supplied hostname. No root wildcard without approval.

## ARTIFACT PATH RULE
`testing/<root-domain>/<subdomain>/` with: `notes/`, `requests/`, `responses/`, `screenshots/`, `scripts/`, `scans/`, `wordlists/`, `urls/`, `subdomains/`, `evidence/`, `reports/`. Never project root.

## OUTPUT STRUCTURE (RETURN THIS)
- [ ] **Target + scope assumptions** (exact host, boundaries)
- [ ] **Fingerprint** (stack/framework/auth/CDN/WAF)
- [ ] **Prioritized surfaces** (top 1-3 with rationale + attack angle)
- [ ] **Safe validation steps** (for top surface, first safe variant)
- [ ] **Evidence needed** (requests/responses/diffs)
- [ ] **Recommended next commands** (concrete, scope-safe)
