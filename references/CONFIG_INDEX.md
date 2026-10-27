# CONFIG INDEX: Lightweight Runtime Map

## Runtime Load Order
1. `agent-briefing.md` — first
2. `AGENTS.md` — constitution
3. `prioritization.md` — signal engine
4. `runtime/opencode/loader.md` → execute BOOT steps verbatim
5. `runtime/opencode/manifest.md`
6. `runtime/registry.json`
7. Foundations: `skills/master-bugbounty-rules.md`, `skills/learning-engine-integration.md` (and/or `.agents/skills/`)

## Active Skill Sources
- `skills/` (mirrors)
- `.agents/skills/` (active)
- Resolved via `scripts/skill_registry.py` (authoritative routing)

## Knowledge Sources (Priority)
1. `memory/targets/<vuln>.md` — vuln-class memory first
2. `memory/report-lessons.md`
3. `memory/patterns.md`
4. `memory/methodology.md`
5. `writeups/processed/`
6. Base training

**Note:** `writeups/index.md` = retrieval only. New write-ups go to `writeups/raw/` first.

## Command / Agent Entry Points
- Commands: `.opencode/commands/{hunt,recon,scan,update,report}.md`
- Agents: `runtime/opencode/agents/*.md`
- Orchestration: `runtime/opencode/ORCHESTRATION.md`
- Browser: `.opencode.json` / config as applicable

## Guardrails (Quick)
- **Scope:** Exact-host only. Sub-subdomain permutations inside supplied hostname only. No `*.<root>` without approval.
- **Target stickiness:** Exhaust primary scope before pivot (with documented criteria).
- **Skill gate:** Before any test → resolver + load all returned skills. Maintain tested-variant ledger.
- **Browser:** MCP `chrome-devtools-mcp` + Chrome DevTools together when browser needed.
- **Owned account:** Use `login.md` only; read OTPs from owned inbox in separate tab.
- **Artifacts:** Under `testing/<root-domain>/<subdomain>/` only. Never project root.
- **FP gate:** Hard pre-report gate from `AGENTS.md`.

## Target Workspace Rule
All target work goes under `testing/<root-domain>/<subdomain>/` with: `notes/`, `requests/`, `responses/`, `screenshots/`, `scripts/`, `scans/`, `wordlists/`, `urls/`, `subdomains/`, `evidence/`, `reports/`.

## Current Status
**Ready for supervised autonomous hunting** — foundations, routing, orchestration, and guardrails in place.
