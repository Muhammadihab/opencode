---
name: xxe
description: Test XML parsers for external entity injection — file read, SSRF, and blind OOB exfiltration.
category: injection
triggers: ["xxe", "xml external entity", "xml parser", "doctype", "svg upload"]
status: active
---

# XXE (XML External Entity)

Anywhere the server parses XML with external entities enabled: XML APIs, SOAP,
SVG/`.docx`/`.xlsx` uploads, SAML, RSS/sitemap imports, config imports. Impact:
**local file read**, **SSRF**, or **blind OOB** exfiltration.

## Attack model
- **Asset:** server files (`/etc/passwd`, app config, keys), internal network (SSRF), the XML parser's trust.
- **Authority decision:** should the parser resolve external entities / DTDs from attacker input? Should be disabled; XXE is when it isn't.
- **Attacker input:** XML body, or XML inside an uploaded container (SVG/OOXML/SAML).
- **Smallest proof:** file content reflected back, OR an OOB callback to your Collaborator with a unique marker. Submission alone ≠ proof.

## Technique ladder
1. **Detect:** send a benign DOCTYPE with an internal entity; does it expand in the response? Error differences on malformed DTD hint the parser resolves DTDs.
2. **Classic in-band (file read):** define `<!ENTITY xxe SYSTEM "file:///etc/hostname">` and reference it where output echoes — read a harmless file first (`/etc/hostname`), not secrets, to prove.
3. **SSRF via XXE:** `SYSTEM "http://169.254.169.254/..."` or `http://<marker>.<collab>/` — turns the parser into a fetcher (see `ssrf`).
4. **Blind / OOB (no echo):** external-DTD exfiltration — host a parameter-entity DTD on your Collaborator; the parser fetches it and calls back with file content in the subdomain/query. Use ONLY the user-provided Collaborator (see `blind-vuln`).
5. **Via upload:** embed the DOCTYPE in an `.svg`/`.xml`, or in `[Content_Types].xml` of a `.docx`/`.xlsx` (see `file-upload`).

## Parser/placement variants
XML body vs uploaded container vs SAML assertion; `SYSTEM` vs `PUBLIC`; general vs
parameter entities (`%`); UTF-16/UTF-7 encoding tricks if UTF-8 is filtered; nested/
recursive only if safe (avoid billion-laughs DoS — out of scope behaviour, don't run).

## Chain targets
File read → app config → DB creds/keys → deeper access. XXE-SSRF → metadata creds.
XXE in SAML → auth bypass.

## FP traps
- A DTD **error** ≠ XXE — the parser rejecting it is the secure case. Need actual resolution.
- Your Collaborator hit from your own box/scanner ≠ proof — must be the target's egress.
- In-band echo that's just your input reflected ≠ file content.
- Many modern parsers disable this by default — don't claim without the read/callback.

## Promotion / proof
- CONFIRMED: file content returned (harmless file) OR OOB callback with your marker carrying data, reproduced 2x, raw request + response/callback saved. Redact any secret value if one appears; keep proof of access.
- Severity: file read / SSRF-to-metadata = P1; blind DNS-only = P3 until escalated.

## References
`ssrf`, `file-upload`, `blind-vuln`, `saml-security`, `exploit-chain-analysis`; memory first.
