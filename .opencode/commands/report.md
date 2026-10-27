---
description: "Write a Bugcrowd-ready report from confirmed bug evidence"
agent: build
---
# REPORT: Bugcrowd-ready report from confirmed evidence

## MANDATES
- [ ] **Skills**: Use `master-bugbounty-rules`, `false-positive-filter`, `evidence-validation-and-severity-calibration`, `evidence-hygiene`, `request-response-analyzer`, `report-writer`. Use `bugcrowd-reporting` or `redteam-report-template` when applicable.
- [ ] **Resolver**: Resolve `python scripts/skill_registry.py resolve --scenario "validated report <finding class>" --mode report --paths-only`, load **every** returned skill.
- [ ] **FP gate**: Run the **COMPLETE FP gate** from `AGENTS.md` before writing. Only **REPORTABLE-state** findings with raw evidence may be rendered.
- [ ] **Severity**: Read `memory/report-lessons.md` and closest `memory/targets/<vuln>.md` before final severity wording. Never claim data breach/ATO/RCE/admin/cross-tenant unless evidence proves it.
- [ ] **Artifacts**: Never write to project root. Reports under `testing/<root-domain>/reports/` or `testing/<root-domain>/<subdomain>/reports/`. Supporting files in `evidence/`, `requests/`, `responses/`, `screenshots/`.

## BEFORE WRITING
1. [ ] **Evidence check**: Confirm enough evidence exists (raw reproducible HTTP proof + real impact + representative contexts).
2. [ ] **State check**: Finding must be in **REPORTABLE** state (>=95%, all gates). If not, output "Not ready to report".
3. [ ] **FP check**: Complete 10-question FP gate verbatim + Findings Strength Verification. Any "NO" -> NOT ready.
4. [ ] **Memory**: Read `memory/report-lessons.md` and closest target checklist.
5. [ ] **Skill load**: Load all resolver skills.

## RULES
- [ ] **Not ready**: If weak, output a **"Not ready to report"** section listing missing proof + safest next validation step.
- [ ] **Proof required**: Include raw reproduction steps with exact HTTP requests (redacted). Evidence paths for requests/responses/screenshots/evidence.
- [ ] **Impact justified**: Concrete impact statement based on evidence, not speculation.
- [ /] **Contexts**: Include representative contexts (accounts/roles/tenants) used in validation.
- [ ] **Limitations**: Include limitations and false-positive reasoning.

## OUTPUT STRUCTURE (BUGCROWD-READY)
- [ ] **Title** (clear, specific, impact-focused)
- [ ] **Affected asset** (exact URL/host/endpoint/object)
- [ ] **Severity** (with justification per `prioritization.md`)
- [ ] **Impact statement** (concrete, evidence-based)
- [ ] **Reproduction steps** (raw requests, method, path, headers (redacted), body, account/role/context)
- [ ] **Evidence paths** (requests/, responses/, screenshots/, evidence/)
- [ ] **Remediation** (brief, actionable)
- [ ] **Limitations** (scope limits, assumptions)
- [ ] **Triager notes** (explain why impact is real, avoid speculation)
- [ ] **Not ready to report** (if applicable: missing proof + safest next validation step)
