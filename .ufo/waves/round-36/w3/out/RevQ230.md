# RevQ230 — S230 quarantine row: /get_model_info deprecation sentence

**Target:** https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py
**Verdict: PRESENT.**

## Measured (single fetch, 2026-10-25)

- One HTTP GET, no retries: **HTTP 200**, `content-length: 110718` bytes, `content-type: text/plain; charset=utf-8`, served from GitHub raw via Fastly (`x-cache: HIT`, `x-github-request-id: 8720:E0071:15C9EE:1EDC0C:6ADD4FF7`, `date: Sun, 25 Oct 2026 01:48:14 GMT`, `etag: "cf80aa59…"`).
- Local bytes: 2961 lines; sha256 `a89d20bb2fa8a86c511ab4d9d054f74d707423ab220f733ff25e62fcc0e49979`.
- Search: local grep of the fetched file for `get_model_info` and `deprecat` (literal text match against downloaded bytes; not a semantic/AST claim).

## Findings

Deprecation material for `/get_model_info` is present at:

- **Line 788** (docstring): deprecation note pointing to `/model_info`.
- **Lines 790–791** (runtime `logger.warning` string, spans two source lines): the explicit deprecation sentence.

Quote (16 words, from lines 790–791):

> "Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead."

Context: route handler `@app.get("/get_model_info")` at line 786; it warns then delegates to `/model_info` (line 793). No row appended; no other lane files touched. Fetched copy retained at `.ufo/waves/round-36/w3/out/RevQ230/http_server.py` (scratch) with headers in `headers.txt`.

## Residual risk / gaps

- Raw.githubusercontent content is branch/tag-served and cacheable (`max-age=300`); a later retag of `v0.5.22` would silently change bytes. Etag + sha256 above pin what this verdict covers.
- Verdict is byte-level presence in the fetched revision; endpoint runtime behavior was not executed.
