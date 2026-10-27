---
name: learning-engine-integration
description: load and use the persistent learning engine for adaptive hunting, signal scoring, memory retrieval, and triage feedback ingestion across hunts
---

# PURPOSE

This skill is loaded automatically before every hunt and provides pre-hunt intelligence, real-time signal scoring, finding persistence, post-triage learning, report-lesson retrieval, and exploitability ranking.

# PREREQUISITES

- The engine lives at `learning_engine/` — pure Python, no external dependencies.
- Include the import snippet:

```python
from learning_engine import LearningEngine
engine = LearningEngine()
```

# INTEGRATION POINTS

1. **Before Recon — Load Intelligence**
   - **Call:** `engine.before_recon(target, technologies)`
   - **When:** After scope parse, before any recon tool runs
   - **Why:** Retrieves target profile, similar targets, historically successful signals
   - **Use:** Read the plan and prioritize high-value surfaces first. **ALSO:** Read `memory/report-lessons.md` before opening processed write-ups — the index is for retrieval only, the lesson file is the hunter's distilled memory.

2. **During Testing — Score Signals**
   - **Call:** `engine.during_testing(signals)`
   - **When:** Every time a new signal is discovered (endpoint, JS leak, header, etc.)
   - **Why:** Scores each signal by historical outcomes
   - **Use:** High scores → deep test, low → note and move on.

3. **After Finding — Persist Memory**
   - **Call:** `engine.after_finding(target=..., subdomain=..., vulnerability_class=..., signals=..., validation_state=..., source_provenance=...)`
   - **When:** After documenting a finding in notes/
   - **Why:** Saves to learning memory and updates the target profile
   - **Use:** ALWAYS call after every finding, even low-confidence observations.

3.5. **On Strong Lead — Expand Similar Cases**
   - **Call:** Search local write-up + memory sources for highly similar patterns when a lead looks credible enough for confirmation or impact expansion
   - **When:** On strong leads
   - **Why:** Maximize defensible impact and avoid known FP traps
   - **Use:** Start from `memory/report-lessons.md`, then search `writeups/index.md` by vuln class, mechanism, affected feature, and trust boundary; read matching processed write-ups only after the lesson pass, before deciding reportability or final severity.

3.75. **During /update — Learn From Reports**
   - **Call:** Convert collected reports into `memory/report-lessons.md` plus methodology, patterns, and target checklists
   - **When:** During /update pipeline
   - **Why:** Learn reusable hunting judgment, not merely accumulate searchable documents
   - **Use:** Extract entry point, trust boundary, precondition, bypass, proof method, false-positive trap, chain opportunity, matching skills, and how the lesson changes future priority.

4. **After Triage — Learn from Feedback**
   - **Call:** `engine.after_triage(finding_id, feedback_type, notes, provenance)`
   - **When:** When the program responds (accepted, duplicate, informative, false_positive)
   - **Why:** Atomically moves the finding, records feedback provenance, recalibrates outcomes
   - **Use:** Reinforce successful patterns, penalize noisy ones. Never use session-level outcomes as feedback.

5. **Before Summary — Rank by Exploitability**
   - **Call:** `engine.before_summary(findings)`
   - **When:** Before structured-summary-reporting
   - **Why:** Ranks by historical exploitability, accept rate, chain value
   - **Use:** Present highest-value findings first.

# SIGNAL REGISTRY

The engine tracks these signal types by default; weights configurable in `learning_engine/scoring/signals.json`:

## High value (7-9)
- `graphql_introspection`, `internal_admin_route`, `api_key_exposed`, `sourcemap_exposed`, `admin_panel_exposed`, `pii_in_response`, `cross_tenant_access`, `hidden_api_endpoint`, `unauthenticated_graphql`, `s3_bucket_listed`, `payment_bypass_candidate`, `debug_endpoint`, `default_credential_candidate`, `template_injection_hint`.

## Medium value (4-6)
- `jwt_token_found`, `oauth_flow_detected`, `idor_parameter`, `mass_assignment_candidate`, `hidden_graphql_field`, `ssrf_url_parameter`, `prototype_pollution_gadget`, `race_condition_candidate`, `unauthenticated_endpoint`, `host_header_injection`, `staging_system`, `legacy_endpoint`, `blind_ssrf_candidate`, `xml_external_entity`.

## Low value (1-3)
- `reflected_param_only`, `stack_trace_exposed`, `cacheable_sensitive`, `open_redirect_param`, `version_disclosure`, `rate_limit_missing`, `cors_wildcard`, `cookie_without_flags`.

# SCORING AUTO-ESCALATION

The engine automatically boosts scores: cross_tenant +30%, admin_bypass +30%, state_changing +20%, sensitive_data +20%, auth_bypass +30%, chainable +20%, payment_impact +30%.

# MEMORY BUCKETS

| Bucket | Purpose | Learning effect |
|---|---|---|
| `heuristics/` | Validated signal patterns only — outcome-calibrated tracking | Trains scoring |
| `pending/` | Initial storage for observations — traceability only | Never trains heuristics |
| `accepted/` | Signal reinforced from triage evidence | Reinforced |
| `duplicates/` | Signal penalized, pattern refined | Penalized |
| `informative/` | Signal weight may reduce | Reduced weight |
| `false_positive/` | Signal penalized, pattern downgraded | Downgraded |
| `chains/` | Chain frequency tracked | Chain value tracked |
| `target_profiles/` | Technology/surface/bug class accumulation | Target intelligence |

# ANALYTICS

Available after hunts: `engine.get_statistics()`, `engine.get_tuning()`, `engine.get_heatmap()`, `engine.get_chains()`, `rebuild_graph()`, `engine.analytics.highest_signal_surfaces(limit=10)`, `engine.analytics.duplicate_heavy_patterns()`, `engine.analytics.target_summary(target)`

# QUICK REFERENCE

```python
from learning_engine import LearningEngine
engine = LearningEngine()

# Initialize once at agent start
plan = engine.before_recon(target, techs)
score = engine.during_testing(signals)
f = engine.after_finding(target=target, subdomain=subdomain, vulnerability_class=vc, signals=signals, validation_state="LEAD", source_provenance="hunt")
engine.after_triage(f["id"], "accepted", notes="ok", provenance={"source": "program_triage", "actor": "tester"})
ranked = engine.before_summary(all_findings)
```

# FILE LOCATIONS

- **Engine code:** `learning_engine/`
- **Skill file:** `.agents/skills/learning-engine-integration/SKILL.md`
- **Signal config:** `learning_engine/scoring/signals.json`
- **Memory source of truth:** `learning_engine/memory/learning.db`
- **Legacy:** `learning_engine/memory/learning.json` and `.bak` folders = migration/recovery artifacts only
- **Audit:** `python learning_engine/scripts/audit_learning_engine.py --report-only`
- **Schemas:** `learning_engine/schemas/*.json`
- **Docs:** `learning_engine/docs/*.md`

# TESTING REQUIREMENT

After writing this skill, verify the engine contract: run `python learning_engine/scripts/audit_learning_engine.py --report-only` and the learning-engine test suite; confirm all 5 hooks accept and return the documented shapes and that signal scoring is bounded. Report pass/fail.
