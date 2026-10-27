---
description: "Normal bug bounty scan triage"
agent: build
---
# SCAN: Normal bug bounty scan triage

## MANDATES
- [ ] **Use all relevant skills** from the registry. Start with `master-bugbounty-rules` + `learning-engine`.
- [ ] **Exploit-first**: Scan output is a lead generator, not the deliverable. After scope lock and first usable endpoint, **test immediately**.
- [ ] **Conservative**: No brute force, credential attacks, destructive payloads, third-party data access, aggressive volume.
- [ ] **Prefer project wordlists**: Use `wordlist/` over SecLists.
- [ ] **Artifacts**: Never write to project root. All artifacts under `testing/<root-domain>/<subdomain>/`.
- [ ] **Scope lock**: Exact-host boundary. Sub-subdomain permutations only inside supplied hostname. No root wildcard without approval.

## REQUIRED STARTUP
1. [ ] **Learn first**: Read relevant `memory/` files (`report-lessons.md`, `patterns.md`, `methodology.md`).
2. [ ] **Prior history**: Check `testing/` for prior history ("we had checked this target before").
3. [ ] **Registry**: Verify `python scripts/skill_registry.py check`.
4. [ ] **Preflight**: Run `python scripts/runtime_preflight.py --target "<exact target>" --scenario "<scan source>" --mode scan --workspace "testing/<root>/<subdomain>" --ensure-session`. Stop if blocked.
5. [ ] **Resolver**: Resolve with `--mode scan` and load **every** returned skill from `skills/<skill>.md` or `.agents/skills/<skill>/SKILL.md`.
6. [ ] **Engine**: Call `learning_engine.before_recon(target, technologies)` after fingerprinting.

## WORKFLOW
1. [ ] **Scope lock**: Lock exact host + boundaries.
2. [ ] **Triage provided results first**: If scan/fuzz results are provided, triage them before fresh discovery.
3. [ ] **Fingerprint**: Quick tech fingerprint (stack/auth/CDN/WAF).
4. [ ] **Prioritize leads**: Pick highest-value usable endpoint from scan output (object/workflow/role boundary).
5. [ ] **Test immediately**: Run skill trigger sweep, load skills, test first safe variant with baseline diff.
6. [ ] **Bounded expansion**: Only use bounded discovery/fuzzing to validate leads. Follow systematic order (tech-aware -> app-type -> wordlists LAST).

## ARTIFACT PATH RULE
`testing/<root-domain>/<subdomain>/` with: `notes/`, `requests/`, `responses/`, `screenshots/`, `scripts/`, `scans/`, `wordlists/`, `urls/`, `subdomains/`, `evidence/`, `reports/`. Never project root.

## OUTPUT STRUCTURE (RETURN THIS)
- [ ] **Target + scope** (exact host, boundaries, prior history found)
- [ ] **Recon + fingerprint** (stack/auth/CDN/WAF)
- [ ] **Scan/fuzzing plan** (with wordlists from `wordlist/`, conservative volume)
- [ ] **Prioritized findings** (leads ranked by exploitability, not count)
- [ ] **FP filtering notes** (hash checks against `memory/FALSE_POSITIVE_DB.md` if applicable)
- [ ] **Safe validation steps** (first variant for top lead)
- [ ] **Evidence needed** (raw pairs, contexts)
- [ ] **Recommended next commands** (scope-safe)
