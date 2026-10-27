#!/usr/bin/env python3
"""Generate the canonical runtime/registry.json for the bug-bounty agent.

Single source of truth. Each skill has:
  - category (attack surface group)
  - triggers (keywords that activate it when a surface is described)
  - path (where the skill file lives; skills/<name>.md by default)
  - load_order (lower loads first; foundations = 0)
  - modes (which run modes it applies to; empty = all)

Also defines the 5 collection sub-agents and the skills registered to each role.
"""
import json

# ---- Foundation (always loaded first, every session) ----
FOUNDATION = [
    ("master-bugbounty-rules", ["*always*"], 0),
    ("learning-engine-integration", ["*always*"], 1, ".agents/skills/learning-engine-integration/SKILL.md"),
]

# ---- (name, category, [triggers]) ----
SKILLS = [
    # Recon / Discovery
    ("recon-workflow",        "recon", ["recon", "subdomain", "enumerate", "discovery", "asset", "dns", "host"]),
    ("tech-fingerprint",      "recon", ["fingerprint", "tech stack", "technology", "framework", "server header", "waf", "cdn"]),
    ("endpoint-triage",       "recon", ["endpoint", "url", "route", "path discovery", "sitemap"]),
    ("fuzzing",               "recon", ["fuzz", "wordlist", "bruteforce path", "hidden endpoint", "directory", "ffuf"]),
    ("dorking-and-osint-discovery", "recon", ["dork", "osint", "google", "github search", "shodan", "leak search"]),
    ("offensive-osint",       "recon", ["osint", "exposed secret", "public source", "crt.sh", "wayback", "urlscan"]),
    ("subdomain-takeover",    "recon", ["subdomain takeover", "dangling dns", "cname", "unclaimed"]),
    ("js-deep-analysis",      "recon", ["js", "javascript", "bundle", "source map", "sourcemap", "client route", "webpack"]),
    ("js-secret-and-api-review","recon", ["js secret", "api key in js", "hardcoded", "token in bundle", "client id"]),

    # API & GraphQL
    ("api-security",          "api", ["api", "rest", "json body", "endpoint method", "swagger", "openapi"]),
    ("graphql-security",      "api", ["graphql", "introspection", "mutation", "query resolver", "gql"]),
    ("request-response-analyzer","api", ["request", "response", "status diff", "body diff", "header analysis"]),
    ("parameter-pollution",   "api", ["parameter", "param pollution", "duplicate key", "hpp", "coercion", "type confusion"]),

    # Authentication & Identity
    ("auth-bypass",           "auth", ["login", "auth", "authentication", "signin", "sign in", "register", "signup", "bypass"]),
    ("session-management",    "auth", ["session", "cookie", "session fixation", "logout", "session token"]),
    ("oauth-oidc-security",   "auth", ["oauth", "oidc", "redirect_uri", "state param", "openid", "sso token"]),
    ("saml-security",         "auth", ["saml", "samlrequest", "samlresponse", "acs", "assertion"]),
    ("jwt-security",          "auth", ["jwt", "json web token", "alg none", "kid", "bearer token"]),
    ("rate-limiting",         "auth", ["rate limit", "otp", "2fa", "mfa", "totp", "brute", "resend code"]),
    ("forgot-password",       "auth", ["forgot password", "reset password", "password reset", "reset", "magic link", "recovery", "reset token"]),
    ("owned-account",         "auth", ["owned account", "login.md", "email verification", "invite", "inbox"]),

    # Authorization & Access Control
    ("idor",                  "authz", ["idor", "object id", "user_id", "uid", "numeric id", "uuid", "bola", "ownership"]),
    ("access-control-testing","authz", ["authz", "access control", "acl", "bfla", "function level", "permission"]),
    ("privilege-escalation",  "authz", ["privilege escalation", "privesc", "admin", "role", "rbac", "support action", "vertical", "horizontal"]),
    ("business-context-analysis","authz", ["tenant", "org_id", "multi-tenant", "cross-tenant", "account_id", "isolation"]),

    # Client-Side
    ("xss",                   "client", ["xss", "reflected", "stored xss", "script injection", "html injection", "innerhtml"]),
    ("dom-xss",               "client", ["dom xss", "dom-based", "sink", "postmessage", "location.hash", "document.write"]),
    ("content-security",      "client", ["csp", "content security policy", "markdown", "rich text", "sanitizer bypass"]),
    ("client-side-security",  "client", ["prototype pollution", "clickjacking", "client-side", "frontend"]),

    # Injection & Parsing
    ("sql-injection",         "injection", ["sqli", "sql injection", "union", "blind sql", "error-based", "stacked query"]),
    ("ssti",                  "injection", ["ssti", "template injection", "jinja", "twig", "freemarker", "velocity"]),
    ("ssrf",                  "injection", ["ssrf", "url fetch", "webhook", "redirect", "callback", "import url", "fetcher", "metadata"]),
    ("xxe",                   "injection", ["xxe", "xml external entity", "xml parser", "doctype", "svg upload"]),
    ("command-injection",     "injection", ["command injection", "rce", "os command", "shell", "exec", "code execution"]),
    ("path-traversal",        "injection", ["path traversal", "lfi", "directory traversal", "../", "file read", "arbitrary read"]),
    ("file-upload",           "injection", ["upload", "file upload", "multipart", "content-type", "polyglot file", "svg"]),
    ("database-security",     "injection", ["nosql", "ldap", "xpath", "injection", "query language"]),

    # Infrastructure & Perimeter
    ("cors-misconfiguration", "infra", ["cors", "access-control-allow-origin", "cross-origin", "wildcard origin"]),
    ("cache-poisoning",       "infra", ["cache", "cache poisoning", "web cache", "x-forwarded", "cache key"]),
    ("host-header-injection", "infra", ["host header", "host injection", "x-forwarded-host", "password reset host"]),
    ("http-smuggling",        "infra", ["http smuggling", "request smuggling", "transfer-encoding", "content-length", "chunked"]),
    ("waf-bypass",            "infra", ["waf", "filter bypass", "encoding bypass", "blocked", "403 waf"]),
    ("infrastructure-security","infra", ["infrastructure", "vpn", "vcenter", "sharepoint", "appliance", "ntlm", "port"]),

    # Stateful & Realtime
    ("websocket-security",    "realtime", ["websocket", "ws", "wss", "socket.io", "realtime channel"]),
    ("race-conditions",       "realtime", ["race condition", "race", " toctou", "concurrent", "double spend", "parallel request"]),
    ("business-logic",        "realtime", ["business logic", "workflow", "coupon", "discount", "approval", "quota", "trial", "credit"]),
    ("payments-security",     "realtime", ["payment", "checkout", "price", "invoice", "billing", "subscription", "refund"]),

    # Cloud / Mobile / AI / Web3
    ("cloud-security",        "cloud", ["cloud", "s3", "bucket", "iam", "gcs", "azure blob", "signed url", "presigned"]),
    ("mobile-security",       "cloud", ["mobile", "apk", "android", "ios", "mobile api"]),
    ("ai-security",           "cloud", ["llm", "ai", "prompt injection", "model", "chatbot", "rag"]),
    ("prompt-injection",      "cloud", ["prompt injection", "jailbreak", "system prompt", "llm abuse"]),
    ("web3-security",         "cloud", ["web3", "smart contract", "solidity", "blockchain", "wallet"]),

    # Blind / OOB
    ("blind-vuln",            "oob", ["blind", "oob", "out of band", "collaborator", "dns callback", "delayed"]),

    # Workflow & Chain
    ("exploit-chain-analysis","chain", ["chain", "exploit chain", "pivot", "escalate", "combine"]),

    # Validation & Reporting
    ("response-diff-analysis","validation", ["response diff", "baseline diff", "signal score", "diff"]),
    ("false-positive-filter", "validation", ["false positive", "fp", "validate finding", "fp filter"]),
    ("evidence-validation-and-severity-calibration","validation", ["severity", "calibration", "evidence validation", "cvss"]),
    ("evidence-hygiene",      "validation", ["evidence", "redact", "hygiene", "poc hygiene"]),
    ("structured-summary-reporting","reporting", ["summary", "structured summary", "session report"]),
    ("report-writer",         "reporting", ["report", "write report", "writeup", "finding report"]),
    ("bugcrowd-reporting",    "reporting", ["bugcrowd", "bugcrowd report", "submission"]),
    ("redteam-report-template","reporting", ["redteam", "red team", "client deliverable", "pentest report"]),
]

# Sub-agent role -> registered skills (loaded before the agent works)
AGENTS = {
    "recon-agent": {
        "role": "Passive+active recon: subdomains, URLs, tech fingerprint, DNS, ports, HTTP probes, WAF/CDN detection",
        "skills": ["recon-workflow", "tech-fingerprint", "endpoint-triage", "subdomain-takeover"],
        "tools": ["read", "glob", "grep", "web_search", "bash"],
        "max_spawns": 2, "timeout_min": 10,
    },
    "dorking-agent": {
        "role": "Passive OSINT across public sources (no target contact)",
        "skills": ["dorking-and-osint-discovery", "offensive-osint"],
        "tools": ["read", "glob", "grep", "web_search", "bash"],
        "max_spawns": 2, "timeout_min": 5,
    },
    "js-agent": {
        "role": "JS bundle + source map analysis, auth-aware",
        "skills": ["js-deep-analysis", "js-secret-and-api-review"],
        "tools": ["read", "glob", "grep", "web_search", "bash", "chrome"],
        "max_spawns": 4, "timeout_min": 5,
    },
    "fuzzing-agent": {
        "role": "Tech-aware endpoint/param fuzzing, WAF-gated by recon-agent",
        "skills": ["fuzzing", "endpoint-triage", "waf-bypass"],
        "tools": ["read", "write", "glob", "bash"],
        "max_spawns": 6, "timeout_min": 5,
    },
    "understand-agent": {
        "role": "Auth-first browse + app mapping, delivers live session, NO testing",
        "skills": ["business-context-analysis", "recon-workflow"],
        "tools": ["read", "glob", "grep", "web_search", "bash", "chrome"],
        "max_spawns": 2, "timeout_min": 10,
    },
}


def build():
    skills = {}
    # foundation
    for item in FOUNDATION:
        name, triggers, order = item[0], item[1], item[2]
        path = item[3] if len(item) > 3 else f"skills/{name}.md"
        skills[name] = {
            "category": "foundation",
            "triggers": triggers,
            "path": path,
            "load_order": order,
            "foundation": True,
            "modes": [],
        }
    # regular skills, load_order 10+
    for name, category, triggers in SKILLS:
        skills[name] = {
            "category": category,
            "triggers": triggers,
            "path": f"skills/{name}.md",
            "load_order": 10,
            "foundation": False,
            "modes": [],
        }
    return {
        "version": "1.0",
        "updated": "2026-10-27",
        "description": "Canonical skill + agent registry. Source of truth for scripts/skill_registry.py.",
        "foundation_order": ["master-bugbounty-rules", "learning-engine-integration"],
        "skills": skills,
        "agents": AGENTS,
    }


if __name__ == "__main__":
    import sys
    reg = build()
    out = sys.argv[1] if len(sys.argv) > 1 else "registry.json"
    with open(out, "w") as f:
        json.dump(reg, f, indent=2)
    print(f"wrote {out}: {len(reg['skills'])} skills, {len(reg['agents'])} agents")
