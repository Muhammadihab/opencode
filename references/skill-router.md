# SKILL ROUTER: Trigger Mapping & Discovery

**Version:** 1.0  
**Last Updated:** 2026-10-27  
**Purpose:** Route hunters to the correct skills based on the discovered attack surface.

> [!IMPORTANT]
> `runtime/registry.json` + `scripts/skill_registry.py` are **AUTHORITATIVE**. This table is a human-readable compatibility cross-check. **Use the resolver before testing** so all matching skills load automatically.

## How to Use
1. [ ] Find the surface in the left column.
2. [ ] Check the "Trigger Surface" description.
3. [ ] Load **ALL** skills in "Skills to Load".
4. [ ] Skip skills in "When NOT to Load" if conditions apply.
5. [ ] Reference the links for exact file paths (`skills/<skill>.md` or `.agents/skills/<skill>/SKILL.md`).

## Master Registry Table

### FOUNDATION (Always First)
| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
| --- | --- | --- | --- | --- |
| **Foundation** | Every hunt/scan/triage/report | `master-bugbounty-rules`, `learning-engine-integration` | Never. Load first. | Scope, impact-first, evidence, FP discipline. |
| **Orchestration** | Multi-agent hunt (`/hunt`) | `runtime/opencode/ORCHESTRATION.md` (reference) | Single-surface quick test | 5 agents, WAF gate, handoff, validation. |

### Authentication & Identity
| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
| --- | --- | --- | --- | --- |
| **Login form** | `POST /login`, username/password fields | `auth-bypass`, `session-management`, `evidence-hygiene` | Already authenticated + no auth testing needed | Brute-force discipline, SQLi low-impact, MFA flows, owned account only. |
| **Magic link/passwordless** | Email/token links, "login with email" | `auth-bypass`, `request-response-analyzer` | If only observing public content | Token reuse, timing, open redirect in callback. |
| **Registration** | `POST /register/signup` | `auth-bypass`, `business-context-analysis` | Read-only exploration | Account takeover preconditions, email verification abuse (in-scope only). |
| **OAuth/OIDC** | `/oauth/*`, `redirect_uri`, `state` | `oauth-oidc-security`, `auth-bypass` | If external IdP out of scope | `redirect_uri` manipulation, `state` missing/replay, token leakage. |
| **SAML** | SAMLRequest/Response, ACS endpoints | `auth-bypass`, `evidence-hygiene` | If SSO vendor out of scope | Assertion tampering (in-scope only), signature validation. |
| **2FA/TOTP/SMS/Email OTP** | MFA prompts, `/mfa/*`, resend | `auth-bypass`, `rate-limiting` | If purely informational | Bypass logic, code reuse, rate limits (conservative). |
| **Backup codes/WebAuthn/FIDO2** | Recovery flows | `auth-bypass` | If not in scope | Recovery abuse, downgrade attacks (in-scope only). |
| **Reset link/code** | Forgot password flows | `auth-bypass`, `owned-account` discipline via `login.md` | Never use third-party accounts | Use owned account inbox only, read codes from inbox. |
| **Security questions/verification** | KBA flows | `auth-bypass` | If impossible without PII | Avoid guessing sensitive data. |

### Authorization & Access Control
| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
| --- | --- | --- | --- | --- |
| **User/object IDs** | `user_id`, `id`, `uid`, numeric/UUID | `idor`, `access-control-testing`, `evidence-hygiene` | Public objects intentionally shared | IDOR across accounts/roles/tenants, horizontal/vertical. |
| **Tenant/org ID** | `org_id`, `tenant_id`, `account_id` | `idor`, `business-context-analysis` | Single-tenant app | Cross-tenant access, org isolation. |
| **Resource paths** | `/users/123/*`, nested resources | `idor`, `access-control-testing` | Static public resources | Path-based authz, function-level authz. |
| **Filter/query params** | `?role=`, `?scope=`, ACL params | `access-control-testing`, `parameter-pollution` | Read-only filters with no side effects | Privilege escalation via params. |
| **RBAC roles/admin/support** | Admin panels, `/admin/*`, role-gated | `privilege-escalation`, `access-control-testing` | If admin fully out of scope | Vertical/horizontal escalation, function-level gaps. |
| **Feature gates** | Plan/entitlement checks | `business-logic`, `access-control-testing` | Cosmetic gates only | Bypass entitlement checks server-side. |

### API & GraphQL
| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
| --- | --- | --- | --- | --- |
| **REST endpoints** | JSON APIs, `/api/*` | `api-security`, `endpoint-triage`, `request-response-analyzer` | Public read-only with no authz | Mass assignment, BOLA/IDOR, authn/authz. |
| **GraphQL** | `/graphql`, introspection enabled | `graphql-security`, `api-security` | Introspection disabled + no queries found | Introspection, query batching, field-level authz, aliases, fragments. |
| **Hidden methods** | OPTIONS/PUT/PATCH/DELETE | `api-security` | Methods properly forbidden with no behavior change | Method override, verb tampering. |
| **Webhooks** | Webhook callbacks/config | `api-security`, `business-logic` | If third-party webhooks out of scope | Replay, signature bypass (in-scope only). |

### Client-Side & JS
| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
| --- | --- | --- | --- | --- |
| **JS bundles** | `.js`, chunked bundles | `js-deep-analysis`, `js-secret-and-api-review` | No bundles or already fully analyzed | Endpoints, secrets (prefix only), routes, client logic. |
| **Source maps** | `.js.map` | `js-deep-analysis` | Maps blocked/unavailable | Recover routes/types/logic. |
| **Client routes** | SPA routes/guards | `js-deep-analysis` | Server-rendered only | Hidden routes, gated features. |
| **Forms/reflected content** | User input rendered | `xss`, `dom-xss` | Static content only | Reflected/stored/DOM XSS (safe proof). |
| **Markdown/rich text** | WYSIWYG/renderers | `xss`, `content-security` | Sanitized/escaped with no sinks | Sanitizer bypass (careful). |
| **postMessage** | `postMessage` listeners | `dom-xss`, `client-side-security` | No listeners found | Origin validation gaps. |

### Injection & Parsing
| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
| --- | --- | --- | --- | --- |
| **SQL** | DB-driven params/filters | `sql-injection`, `database-security` | No SQL indicators + out of scope | Error/UNION/blind/time-based; low-impact on login pages. |
| **XSS** | HTML/JS injection sinks | `xss`, `dom-xss` | Self-XSS only / CSP blocks all with no bypass | Reflected/stored/DOM; safe proof, no social engineering. |
| **SSTI** | Template expressions | `ssti` | No template engine suspected | Engine-specific, bounded testing. |
| **SSRF/URL fetchers** | `url=`, `fetch=`, webhooks | `ssrf`, `network-security` | Internal network fully out of scope OR no user input | Scheme/IP/redirect bypasses; use user-provided OOB only if needed. |
| **XXE/XML** | XML uploads/parsers | `xxe` | JSON-only APIs | Classic/blind/upload vectors (in-scope only). |
| **File uploads** | Upload forms/endpoints | `file-upload`, `path-traversal` | No uploads or read-only | Extension/content-type/path traversal, parser abuse (safe). |
| **Path traversal** | `file=`, `path=`, `download=` | `path-traversal`, `file-handling` | No file access | LFI/RFI considerations, scope-limited. |
| **Command injection** | OS command params | `command-injection` | No command execution indicators | Bounded, read-only proof only if safe. |

### Infrastructure & Perimeter
| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
| --- | --- | --- | --- | --- |
| **CORS** | `Access-Control-*` | `cors-misconfiguration`, `api-security` | CORS not present | Origin reflection, wildcard+credentials. |
| **Cache** | CDN/cache headers, vary | `cache-poisoning`, `web-cache` | No cache/CDN indicators | Poisoning only if safe and in-scope. |
| **Host headers** | Host header manipulation | `host-header-injection` | No virtual host routing | SSRF/password reset poisoning (in-scope). |
| **CDN/WAF** | Detected by recon | `waf-bypass`, `fuzzing` | No WAF detected | Encoding/method-override/content-type/chunked/null-byte. |
| **Subdomains** | Related subdomains | `subdomain-takeover`, `recon-workflow` | Fully unrelated & out of scope | Takeover only if claims can be verified safely. |
| **Appliances (VPN/Vcenter/SharePoint)** | Known appliances | `infrastructure-security` | Out of scope per program | Follow program scope strictly. |
| **NTLM** | Auth headers/flows | `authentication-ntlm` | No NTLM indicators | Auth coercion only in authorized scope. |

### Stateful & Realtime
| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
| --- | --- | --- | --- | --- |
| **WebSockets** | `ws://`, `wss://`, Socket.IO | `websocket-security` | No WS endpoints | Authz on upgrade/messages, origin validation. |
| **Race conditions** | One-time actions/coupons/claims | `race-conditions`, `business-logic` | Idempotent actions with no value | Parallel requests, safe proof of double-spend/duplicate. |
| **One-time actions** | OTP/coupon/verification/redeem | `business-logic`, `race-conditions` | Already consumed & locked | Replay vs race (conservative). |
| **Payments** | Checkout, billing, wallets | `business-logic`, `payments-security` | Payment provider sandbox/out of scope | Price tampering, promo abuse (safe proof only). |

### Cloud/Mobile/AI/Web3
| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
| --- | --- | --- | --- | --- |
| **Buckets** | S3/Blob/GCS URLs | `cloud-security`, `offensive-osint` | Bucket public in error but no data access confirmed | Enumeration limited, no exfiltration of third-party data. |
| **IAM** | Roles/policies found via JS/leaks | `cloud-security` | Out of target cloud account scope | Assume least privilege, no privilege escalation in external accounts. |
| **LLM/AI** | Chatbots, prompt injection points | `ai-security`, `prompt-injection` | Pure static FAQ with no input processing | Prompt injection, system prompt leakage (safe). |
| **APK/Mobile** | Mobile apps/files | `mobile-security` | If only web targets requested | Deep link/webview, auth flows, insecure storage. |
| **Smart contracts/Web3** | Blockchain apps | `web3-security` | Out of scope for most programs | Reentrancy logic only if explicitly in scope. |

### Workflow & Chain
| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
| --- | --- | --- | --- | --- |
| **Business logic** | Multi-step workflows/orders/approvals | `business-logic`, `exploit-chain-analysis`, `business-context-analysis` | Single-step trivial action | Workflow bypass, parameter manipulation across steps. |
| **Exploit chains** | Multiple weaknesses together | `exploit-chain-analysis` | Single minor issue | Combine authz + logic to reach real impact. |

### Validation & Reporting
| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
| --- | --- | ---Tag: 
| **Response-diff** | Every test against baseline | `request-response-analyzer` | If already validated and clear state change proven | Status/body/headers/timing/state comparison. |
| **False-positive-filter** | Before promoting to LEAD/CONFIRMED | `false-positive-filter` | Already in FP DB with confirmed match | 10-question FP gate, signature hash. |
| **Evidence validation** | Before severity/reportability | `evidence-validation-and-severity-calibration`, `evidence-hygiene` | Already reportable and user requested report | Strength verification, proof quality. |
| **Structured summary** | Sub-agent results / session output | `structured-summary-reporting` | Fluff/banter only | Compact summaries, ledgers. |
| **Report-writer** (on request only) | User asks for report or `report.md` command | `report-writer`, `bugcrowd-reporting`, `redteam-report-template` | No confirmed reportable evidence OR user not asked for report / no evidence ready: output "Not ready to report" if weak. | Bugcrowd-ready, raw requests, evidence paths, limitations, avoid speculative claims. |

> **Note:** Skill names match exactly as referenced in `runtime/registry.json`. Always run the resolver: `python scripts/skill_registry.py resolve --scenario "<surface>" --mode test --paths-only` to load **all** matching skills automatically.

## References
- [ ] `runtime/registry.json` (Authoritative)
- [ ] `scripts/skill_registry.py` (Resolver)
- [ ] `skills/<skill>.md` / `.agents/skills/<skill>/SKILL.md`
- [ ] `AGENTS.md`, `prioritization.md`, `agent-briefing.md`
- [ ] `.opencode/commands/*.md`
- [ ] `runtime/opencode/ORCHESTRATION.md`, `runtime/opencode/loader.md` />
