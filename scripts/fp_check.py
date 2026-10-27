#!/usr/bin/env python3
"""False-positive signature gate — real code, not a mental step.

Implements the hash contract from AGENTS.md / FALSE_POSITIVE_DB.md:
    signature = SHA256(f"{status}:{body_length}:{body_substring}")[:8]

Where body_substring is a stable identifying fragment of the response body
(by default the first 120 chars with volatile bits — csrf tokens, timestamps,
uuids, nonces — masked out so the same page hashes the same across requests).

Commands:
  fp_check.py hash   --status 200 --body-file resp.txt
  fp_check.py check  --status 200 --body-file resp.txt      # exit 0 = MATCH (known FP), 10 = miss
  fp_check.py add    --status 200 --body-file resp.txt --pattern "waf block page" --notes "..."

The DB lives at memory/FALSE_POSITIVE_DB.md and is a markdown table:
  | hash | pattern | count | last_seen | notes |
check increments the count + last_seen on a match. add appends a new row on a miss.
Exit codes let the agent branch in a hook/script without "imagining" the result.
"""
import argparse
import hashlib
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "memory", "FALSE_POSITIVE_DB.md")

# volatile fragments masked before hashing so dynamic tokens don't change the sig
_VOLATILE = [
    (re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I), "<uuid>"),
    # token/nonce/state assignments BEFORE the generic hex rule (keep the label)
    (re.compile(r'\b(csrf|token|nonce|state|sid|session)\b(["\'=:\s]+)[A-Za-z0-9._-]+', re.I), r"\1\2<tok>"),
    (re.compile(r"\b[0-9a-f]{16,64}\b", re.I), "<hex>"),
    (re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\S*"), "<ts>"),
    (re.compile(r"\bID[:=]\s*\S+", re.I), "ID=<id>"),
    (re.compile(r"\d{6,}"), "<num>"),
]


def normalize(body, length=160):
    b = body or ""
    for pat, repl in _VOLATILE:
        b = pat.sub(repl, b)
    b = re.sub(r"\s+", " ", b).strip()
    return b[:length]


def signature(status, body):
    # Hash the NORMALIZED fragment only. Raw body length is deliberately excluded:
    # volatile tokens change length, which would break the signature for the same page.
    frag = normalize(body)
    raw = f"{status}:{len(frag)}:{frag}"
    return hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()[:8]


# ---------- DB handling ----------
_ROW = re.compile(r"^\|\s*([0-9a-f]{8}|hash|example|-+)\s*\|")


def _read_db():
    if not os.path.exists(DB):
        return []
    rows = []
    for line in open(DB, encoding="utf-8"):
        if line.strip().startswith("|") and not re.match(r"^\|\s*-+", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 5 and cells[0] not in ("hash",):
                rows.append(cells)
    return rows


def _write_rows(rows):
    header = "# FALSE_POSITIVE_DB\n\n| hash | pattern | count | last_seen | notes |\n|---|---|---|---|---|\n"
    body = ""
    for r in rows:
        body += "| " + " | ".join(r[:5]) + " |\n"
    # preserve the explanatory sections below the table if they exist
    tail = ""
    if os.path.exists(DB):
        txt = open(DB, encoding="utf-8").read()
        m = re.search(r"\n(## .*)", txt, re.S)
        if m:
            tail = "\n" + m.group(1)
    with open(DB, "w", encoding="utf-8") as f:
        f.write(header + body + tail)


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_check(sig):
    rows = _read_db()
    for r in rows:
        if r[0] == sig:
            # increment count + last_seen
            try:
                r[2] = str(int(r[2]) + 1)
            except ValueError:
                r[2] = "1"
            r[3] = _now()
            _write_rows(rows)
            return True
    return False


def cmd_add(sig, pattern, notes):
    rows = [r for r in _read_db() if r[0] not in ("example",)]
    for r in rows:
        if r[0] == sig:
            return False  # already present
    rows.append([sig, pattern or "unlabeled", "1", _now(), notes or ""])
    _write_rows(rows)
    return True


def _load_body(args):
    if args.body_file:
        return open(args.body_file, encoding="utf-8", errors="replace").read()
    if args.body is not None:
        return args.body
    return sys.stdin.read()


def main():
    p = argparse.ArgumentParser(description="FP signature gate")
    sub = p.add_subparsers(dest="cmd", required=True)
    for c in ("hash", "check", "add"):
        sp = sub.add_parser(c)
        sp.add_argument("--status", required=True)
        sp.add_argument("--body")
        sp.add_argument("--body-file")
        if c == "add":
            sp.add_argument("--pattern")
            sp.add_argument("--notes")
    args = p.parse_args()

    body = _load_body(args)
    sig = signature(args.status, body)

    if args.cmd == "hash":
        print(sig)
        sys.exit(0)
    if args.cmd == "check":
        if cmd_check(sig):
            print(f"MATCH {sig} — known false positive, DOWNGRADE to INFORMATIONAL")
            sys.exit(0)
        print(f"MISS {sig} — not a known FP, continue validation")
        sys.exit(10)
    if args.cmd == "add":
        if cmd_add(sig, args.pattern, args.notes):
            print(f"ADDED {sig}")
            sys.exit(0)
        print(f"EXISTS {sig} — already in DB")
        sys.exit(11)


if __name__ == "__main__":
    main()
