---
name: sql-injection
description: Test inputs reaching SQL for injection — error-based, UNION, boolean/time-blind, stacked, second-order.
category: injection
triggers: ["sqli", "sql injection", "union", "blind sql", "error-based", "stacked query"]
status: active
---

# SQL Injection

Impact is **reading/altering the database or auth state**, proven by a server-side
effect — not an error message alone. On production bug-bounty targets, prove it
**safely**: read a harmless value, never dump tables, never `DROP`, never run
destructive or high-volume payloads.

## Attack model
- **Asset:** the database — other users' data, credentials, auth decisions.
- **Authority decision:** should this input alter the query's structure? Never.
- **Attacker input:** any param/field/header reaching a query — numeric, string, ORDER BY, LIMIT, column name, JSON.
- **Smallest safe proof:** a conditional response difference or a controlled delay tied to a boolean you set — e.g. `AND 1=1` vs `AND 1=2` diverge, or a time payload adds exactly your delay.

## Detection ladder (safe → confirmed)
1. **Probe:** append `'`, `"`, `)`, `--` and watch for errors/500/behaviour change. Also test numeric context (no quotes).
2. **Boolean-blind:** `... AND 1=1` vs `... AND 1=2` — stable response-diff = injectable. Prefer this over noisy payloads.
3. **Error-based:** if errors leak, extract a single harmless value (DB version) to confirm — one value, not a dump.
4. **Time-blind (last resort, low delay):** `... AND SLEEP(3)` / `pg_sleep(3)` / `WAITFOR DELAY '0:0:3'` — confirm with 2-3 samples vs baseline (timing needs a clean baseline; see master rules). Keep delays small.
5. **UNION:** only to confirm column count/read one safe value; find column count with `ORDER BY n` then `UNION SELECT NULL,...`.
6. **Second-order:** input stored now, executed later in a different query (registration → profile view). Mark + revisit.

## Context / DBMS variants
- Numeric vs quoted-string vs identifier (ORDER BY/column) — each needs a different break-out.
- Per-DBMS comment & function syntax (MySQL `-- `/`#`, Postgres, MSSQL, Oracle, SQLite).
- JSON/ORM layers: injection through a filter param that builds raw SQL.

## WAF/filter bypass (see `waf-bypass`)
Inline comments (`/**/`), case toggles, encoding (URL/double/hex/unicode), whitespace
alternatives (`%09`, `%0a`, `/**/`), keyword splitting, `OR`→`||`, logic equivalents.
One family at a time, logged.

## Chain targets
Auth-context SQLi → **login bypass / ATO**. Read creds/tokens → lateral. Stacked (if
allowed) → write. SQLi in admin tooling → mass data. Highest severity class — but prove it.

## FP traps
- **Error message ≠ injection** — a 500 or SQL error on `'` may be input validation, not an executable injection. Need a boolean/time/UNION confirmation.
- **Timing noise** — network jitter mimics time-blind; require multiple samples + baseline.
- **WAF block page** looks like a "different response" — run `fp_check.py`, response-diff.
- **Reflected SQL error text** without control over the query = info leak (P3), not SQLi.

## Promotion / proof
- CONFIRMED: a controlled boolean/time/UNION effect reproduced 2x, raw requests saved, with a single safe extracted value or clean conditional diff. Never dump data to "prove more."
- Severity: data access / auth bypass = P1 (Critical class) — but only on real server-side proof. Error leak alone = P3.

## References
`waf-bypass`, `database-security` (NoSQL/LDAP/XPath), `request-response-analyzer`,
`auth-bypass` (login-context), `exploit-chain-analysis`; memory first.
