# ScoutBaseOverlap — scoped findings (C1 clause-b pre-screen + freshness)

Date 2026-10-23. Seat: KamaR26.ScoutBaseOverlap. No server started, no ports used.
Full evidence with commands and outputs: `.ufo/waves/round-26/w1-build/out/ScoutBaseOverlap/overlap.md`.

## Verdict

Clause (b) blocks **4** candidate signature strings the executor families target
(`Context size has been exceeded.`, `Stream owner model is loading, retry later`,
`no slot available`, `Invalid API Key`), plus `exceed_context_size_error`. Every
other family candidate verified in the pinned source is free. The Historical error
signatures section is fresh: all llama.cpp-attributed rows still match the pinned
704366d source. No overlap risk for the remaining wave-1 rows.

## Held-at-base signatures (blocked, must not be registered)

1. `Context size has been exceeded.` — server-context.cpp:4301 — base hits: SKILL.md:689, corpus/SOURCES.md:121. `ExecPromptTooLong` must use the surrounding format strings instead:
   - `request (%d tokens) exceeds the available context size (%d tokens), try increasing it` (server-context.cpp:3678)
   - `input (%d tokens) is larger than the max context size (%d tokens). skipping` (server-context.cpp:3669)
   - `context shift is disabled` (3378), `context shift cannot be used for shared prompt` (3390)
   Also held: `exceed_context_size_error` (server-common.cpp:124; corpus/knowledge/context-capacity.md:164) — do not use the type string as a signature.
2. `Stream owner model is loading, retry later` — server-models.cpp:2585 — base hits: SKILL.md:519, corpus/knowledge/endpoint-identity.md:207. `ExecRouterModels` blocked on that exact string; free: `model name is missing from the request` (server-models.cpp:2165), `model '<name>' not found` (2170), `model is not found` (2317/2461), `model name=<name> is not found` (854/1330/1672/1731/1850), `Stream not found or expired` (2587), `model limit reached, try again later` (1396).
3. `no slot available` — server-context.cpp:5396 — held in six corpus files + SKILL.md:519. `ExecSlotsOff` must use `This server does not support slots endpoint. Start it with \`--slots\`` (server-context.cpp:5366).
4. `Invalid API Key` — server-http.cpp:302 — held at SKILL.md:181 (spec already told ExecApiKey to avoid it). The composed 401 JSON envelope `{"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}` is the only api-key candidate; it is not held as a whole, but spacing must be byte-exact (`safe_json_to_str` emits no spaces) and the body contains the held `Invalid API Key` substring (clause (b) blocks the signature string itself; the substring is not a blocker unless it is the signature).

## Freshness of `## Historical error signatures` (SKILL.md 167-196)

Byte-identical at base and tip. All llama.cpp-attributed rows re-verified in the pinned source:
- `Server: llama.cpp` — server-http.cpp:180 (`set_default_headers`).
- `{"status":"ok"}` — server-context.cpp:5297 (`res->ok({{"status", "ok"}})`).
- `default_generation_settings` — server-context.cpp:5243.
- 404 `{"error":{"message":"File Not Found","type":"not_found_error","code":404}}` — server-http.cpp:201-207.
- `Invalid API Key` 401 — server-http.cpp:290-303.
- `Loading model` 503 envelope — server-http.cpp:314-322.

No staleness. (The Jetty-html 404 and curl rows are foreign-service/curl observations, not llama.cpp claims.)

## Overlap candidates for other seats

The full 24-source-literal and 38-base-quote lists are in overlap.md. Notable for the scribes: `--kv-unified-per-slot`, `LLAMA_ARG_KV_UNIFIED(_PER_SLOT)`, `n_busy_slots_per_decode`, `tokens_predicted_total`, `text/plain; version=0.0.4`, `application/json; charset=utf-8`, `Access-Control-Allow-Origin`, `https://huggingface.co/` are held — none are error signatures, so this does not constrain C1 rows unless an executor picks a help-text phrase.

## Method note

Equivalent to clauses (b)+(f) pre-screen: extracted all C string literals >= 20 bytes from the 13 pinned sources (1812), checked raw and unescaped forms per-line against `git show 1560e4d8:<file>` for the 60 tracked files (SKILL.md + corpus/), plus `41 shaped signatures with realistic values (missing model path, 1025-token prompt vs 2048 context, port 47560). Direction B extracted 3381 base quoted strings >= 20 B and found 38 occurring in pinned sources. No server run, no tools installed.
