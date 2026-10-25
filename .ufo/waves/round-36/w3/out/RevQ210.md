# RevQ210 — Quarantine row S210 (unsloth.ai JP SGLang guide)

Target: https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide
Fetched: 2026-10-24, single curl -sS -L fetch (browser UA), body saved to `body.html` beside this report. One fetch, one URL; no re-fetch.

## Measured
- HTTP status: **200** (final_url identical to requested URL; num_redirects=0)
- Downloaded size: **1,112,304 bytes** (full page body, not an error shell)
- Literal `Page Not Found` in served bytes: **0 occurrences** (also 0 for case-variant `Page Not Found`/`page not found` pattern `Page [Nn]ot [Ff]ound`)
- Literal `sglang.launch_server` in served bytes: **12 occurrences**
- Served `<title>`: `SGLangデプロイメント＆推論ガイド | Unsloth Documentation`

## Verdict
**present** — page resolves with HTTP 200, does not contain `Page Not Found`, and does contain `sglang.launch_server`.

## Inference (not measured)
- Title text and the `/docs/jp/ji-chu/...` path indicate this is the Japanese-localized SGLang deployment guide; content appears live rather than quarantined/dead. Whether S210 *should* remain in quarantine is a policy call outside this check — I only measured liveness and the two literal strings. No row appended to SOURCES.md or any corpus file.

Residual risk: check ran on served HTML bytes (SSR payload), not on browser-rendered DOM; a client-side-only "Page Not Found" overlay would not be visible here. No such marker exists in the 1.1 MB payload.
