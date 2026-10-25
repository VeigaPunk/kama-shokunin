# RevQ224 — quarantine row S224 byte check

- Seat: wave 3 leaf, round 36, lane kama-shokunin. Date: 2026-10-24.
- Target: https://docs.vllm.ai/en/v0.17.0/api/vllm/entrypoints/serve/instrumentator/health/
- Method: single fetch (curl, UA Mozilla/5.0 Chrome/120, --max-redirs 5), body + headers saved to seat scratch (`body.html`, `headers.txt`); every string check below ran against the saved bytes. No re-fetch, no second source.

## Measured (fetch)

- HTTP 200, `size_download` 386,143 bytes, `content_type text/html; charset=utf-8`, 0 redirects, final URL identical to requested URL (wall ~0.14 s).
- Page identity confirmed in-body: `<title>health - vLLM</title>`; canonical link = requested URL; generator `mkdocs-1.6.1, mkdocs-material-9.7.4`; ReadTheDocs meta `readthedocs-resolver-filename: /api/vllm/entrypoints/serve/instrumentator/health/` and `readthedocs-http-status: 200`; prev/next nav to `../basic/` and `../metrics/`. This is the genuine server-rendered API page, not a JS shell or 404 fallback — absence verdicts on these bytes are meaningful.

## Verdicts

| String | Verdict | Measured |
|---|---|---|
| `check_health` | **present** | 1 occurrence in body (line 23), inside the code-highlighted example: `await engine_client(raw_request).check_health()` (`<span class=n>check_health</span>`). Case-sensitive and -i counts both 1. |
| `render-only` | **absent** | 0 hits for `render.only` (-i; covers hyphen/space/en-dash single-char separators) and 0 for `render.{0,40}only` (-i). The bare word "render" occurs 16× but only in site chrome (RTD addons JS, asset/URI strings), never adjacent to "only". |
| `always return 200` | **absent** | 0 hits for exact phrase (-i) and 0 for windows `always.{0,10}return`, `always.{0,60}200`, `return.{0,20}200` (-i). Decisive: the word `always` occurs **0 times** in the entire 386,143-byte body, so no markup/entity-split variant of the phrase can exist. |

No `quote-not-located` verdict issued: the page was located (200, identity confirmed) and content is in the served HTML, so present/absent was directly measurable for all three strings.

## Measured vs inference

- Measured: every number above (HTTP status, byte size, content type, redirect count, occurrence counts, the single `check_health` evidence line, zero-count variant greps).
- Inference: none beyond grep semantics. I did not render the page in a browser; the absence verdicts hold for the served HTML bytes, which for this mkdocs-material page contain the body content server-side (the `check_health` example is in the static HTML, corroborating that prose would be too).

## Residual risk / verification gaps

- Single fetch at 2026-10-24 against live docs.vllm.ai/ReadTheDocs; bytes could differ at another time or CDN edge. Per task bounds I did not fetch again or cross-check an archive.
- Raw-HTML grep includes mkdocs/RTD chrome; a phrase present only inside client-side JS could be missed. Mitigated: the page is server-rendered and its content (code example) is present in the static HTML.
- `corpus/SOURCES.md` contains no literal `S224` row (grep: no matches); the "quarantine row" phrasing was not verifiable in that file. Out of my scope — I appended no row anywhere and did not chase the tracker.

## Scope compliance

- Writes: this report + scratch (`RevQ224/headers.txt`, `RevQ224/body.html`) only. No lane file, SOURCES row, jj/Git state, or fleet path touched. No subagents dispatched. Read-only git: none needed.
