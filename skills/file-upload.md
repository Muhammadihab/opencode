---
name: file-upload
description: Test file upload/import features for unrestricted upload, stored XSS, SSRF/XXE via parsers, and path traversal.
category: injection
triggers: ["upload", "file upload", "multipart", "content-type", "polyglot file", "svg"]
status: active
---

# File Upload & Import

Upload bugs are rarely "upload a webshell" on modern stacks — the wins are
**stored XSS (SVG/HTML)**, **SSRF/XXE via parsers**, **path traversal in the
filename**, and **content-type confusion**. Map what the server *does* with the
file (store, render, parse, convert, fetch).

## Attack model
- **Asset:** code execution context, other users' browsers (served files), internal network (parsers), the filesystem.
- **Authority decision:** should this file type/content/path/location be accepted and served/parsed as-is?
- **Attacker input:** file content, filename, extension, MIME/`Content-Type`, magic bytes, and any URL the importer fetches.
- **Smallest proof:** the server stores/serves/parses the file in a way that executes attacker intent (XSS fires, parser calls out, file lands outside its dir).

## Test matrix
- **Extension / type bypass:** double ext (`shell.php.jpg`), case (`.PhP`), trailing dot/space/null (`x.php%00.jpg`), uncommon exts the handler maps, `Content-Type` mismatch (declare `image/png`, send HTML), magic-byte prefix + real payload.
- **Stored XSS via SVG/HTML:** upload an `.svg` containing `<script>`/`onload`; if served inline (not `Content-Disposition: attachment`) on the app origin → stored XSS (see `xss`, `content-security`). Also HTML files, `.xml`, polyglots.
- **XXE via parsed formats:** `.svg`, `.docx`/`.xlsx` (zip of XML), `.xml` imports — external entity to your Collaborator (see `xxe`, `blind-vuln`).
- **SSRF via importers:** "import from URL", avatar-from-URL, remote-document — point at internal/metadata (see `ssrf`).
- **Path traversal in filename:** `../../../x`, encoded, to write/read outside the upload dir. Confirm where the file lands.
- **Image/doc conversion:** ImageMagick/ffmpeg/ghostscript/LibreOffice backends have known RCE/SSRF classes — probe safely, don't run destructive payloads.
- **Serving origin:** is the file served from the app origin (XSS-relevant) or a sandboxed/CDN origin (reduces XSS)? Check.

## Bypass ladder
Extension → MIME → magic bytes → parser type → filename path → serving origin →
import-URL destination. One variable at a time; log each in the variant ledger.

## Chain targets
SVG stored XSS in admin view → admin takeover. XXE → SSRF/file read. Import-URL →
internal SSRF → metadata creds. Traversal write → overwrite config.

## FP traps
- File **accepted** but served as `attachment`/`text/plain` from a sandbox origin → no XSS; note it, don't claim.
- Upload "succeeds" but server re-encodes the image (strips payload) → payload gone.
- A parser error ≠ XXE/SSRF — need the callback/side-effect.
- Being able to upload a benign file is not a finding.

## Promotion / proof
- CONFIRMED: the executed effect, reproduced 2x — XSS firing on the app origin (screenshot + stored value), parser callback with your marker, or the file read/written where it shouldn't be. Save the raw upload request + the serve/render response.
- Severity: stored XSS/parser-SSRF/traversal with impact = P2–P1 per effect; benign accept = P4.

## References
`xss`, `xxe`, `ssrf`, `content-security`, `path-traversal`, `blind-vuln`; memory first.
