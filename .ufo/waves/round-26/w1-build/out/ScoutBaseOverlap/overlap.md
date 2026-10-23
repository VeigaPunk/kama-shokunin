# ScoutBaseOverlap — C1 clause (b) pre-screen: held signatures at base 1560e4d8

Scout seat, wave 1. Date 2026-10-23. Frozen tip a23c0e0; base 1560e4d8.
Method mirrors the frozen counter `count-c1.py` clause (b): `git grep -F -q -e <sig> BASE -- SKILL.md corpus`.
No server started, no ports touched (seat has no port block).

## 1. Direction A — source literals (>= 20 raw bytes) held at base

Extracted every C string literal of >= 20 bytes from the 13 pinned source files under
`.ufo/waves/round-26/sources/llama.cpp-704366d/` (arg.cpp, common.cpp, gguf.cpp, llama-context.cpp,
llama-model-loader.cpp, llama.cpp, server-common.cpp, server-context.cpp, server-http.cpp,
server-models.cpp, server-queue.cpp, server-task.cpp, server.cpp): 1812 raw literals.
Checked each raw AND unescaped-emitted form with the per-line containment rule of `git grep -F`
against every tracked file of `SKILL.md` + `corpus/` at base 1560e4d8 (60 files, 12814 lines).

**24 held literals** (these cannot be counted as signatures under clause (b)):

| Literal (raw C form) | Source loc | Held at base (path:line) |
|---|---|---|
| `--chat-template-file` | arg.cpp:3803 | corpus/lessons/round-1-safety.md:11 |
| `--kv-unified-per-slot` | arg.cpp:1653 | SKILL.md:688, corpus/SOURCES.md:124 |
| `--sleep-idle-seconds` | arg.cpp:3851 | corpus/knowledge/served-identity-crosswalk.md:155 |
| `/v1/chat/completions` | server-http.cpp:774,828 | SKILL.md:160,175 |
| `Access-Control-Allow-Origin` | server-http.cpp:334,339 | corpus/knowledge/consumer-registry.md:265 |
| `Context size has been exceeded.` | server-context.cpp:4301 | SKILL.md:689, corpus/SOURCES.md:121 |
| `LLAMA_ARG_KV_UNIFIED` | arg.cpp:1734 | corpus/knowledge/context-capacity.md:195 |
| `LLAMA_ARG_KV_UNIFIED_PER_SLOT` | arg.cpp:1659 | corpus/knowledge/context-capacity.md:195 |
| `LLAMA_ARG_N_PARALLEL` | arg.cpp:2556,2564 | corpus/knowledge/context-capacity.md:194 |
| `Stream owner model is loading, retry later` | server-models.cpp:2585 | SKILL.md:519, corpus/knowledge/endpoint-identity.md:207 |
| `application/json; charset=utf-8` | server-http.cpp:209,299 | corpus/knowledge/consumer-registry.md:264, corpus/knowledge/llamacpp-loading-lifecycle.md:118 |
| `default_generation_settings` | server-context.cpp:5243, server-models.cpp:2248 | SKILL.md:174,687 |
| `exceed_context_size_error` | server-common.cpp:124 | corpus/knowledge/context-capacity.md:164 |
| `https://huggingface.co/` | common.cpp:1548 | corpus/SOURCES.md:51, corpus/lessons/round-16.md:194 |
| `n_busy_slots_per_decode` | server-task.cpp:1589 | corpus/lessons/round-1-safety.md:20 |
| `predicted_tokens_seconds` | server-task.cpp:1577 | corpus/knowledge/serving-metrics-crosswalk.md:21 |
| `prompt_seconds_total` | server-task.cpp:1537 | corpus/knowledge/serving-metrics-crosswalk.md:20 |
| `prompt_tokens_seconds` | server-task.cpp:1573 | corpus/knowledge/serving-metrics-crosswalk.md:21 |
| `set model name aliases, comma-separated (to be used by API)` | arg.cpp:3026 | corpus/knowledge/served-identity-crosswalk.md:43 |
| `set model tags, comma-separated (informational, not used for routing)` | arg.cpp:3038 | corpus/knowledge/served-identity-crosswalk.md:43 |
| `text/plain; version=0.0.4` | server-context.cpp:5314,5355 | corpus/lessons/round-1-safety.md:17 |
| `tokens_predicted_seconds_total` | server-task.cpp:1545 | corpus/knowledge/serving-metrics-crosswalk.md:20 |
| `tokens_predicted_total` | server-task.cpp:1541 | corpus/knowledge/served-model-identity.md:27,34 |
| `when set without -c/--ctx-size, the shared KV pool is sized to n_parallel*N` | arg.cpp:1655 | corpus/lessons/round-25.md:28 |

`git grep -F -q -e '<sig>' 1560e4d8 -- SKILL.md corpus; echo $?` -> 0 for every row above (verified via the same per-line containment on `git show 1560e4d8:<file>`).

**Clause-(b) relevant held candidates (error-like):**
- `Context size has been exceeded.` — server-context.cpp:4301 — **already held** (SKILL.md:689, corpus/SOURCES.md:121). C1's `round-16` lesson corpus already holds the round-16 exact variant `Context size has been exceeded` and the exact round-26 variant too. `ExecPromptTooLong` cannot use this exact trailing-period string; the surrounding `request (%d tokens) exceeds the available context size (%d tokens), try increasing it` and `input (%d tokens) is larger than the max context size (%d tokens). skipping` (server-context.cpp:3669/3678) are NOT held and are free.
- `Stream owner model is loading, retry later` — server-models.cpp:2585 — **already held** (SKILL.md:519, corpus/knowledge/endpoint-identity.md:207). `ExecRouterModels` cannot use it.
- `exceed_context_size_error` — server-common.cpp:124 — **already held** (corpus/knowledge/context-capacity.md:164). A row containing this type string verbatim cannot count.
- `no slot available` — server-context.cpp:5396 (source literal `"no slot available"`) — **already held** (SKILL.md:519, corpus/SOURCES.md:208, corpus/knowledge/endpoint-identity.md:206, corpus/knowledge/llamacpp-loading-lifecycle.md:66, corpus/lessons/round-16-verifier-spotcheck.md:132, corpus/lessons/round-16.md:48). `ExecSlotsOff` cannot use it.
- `Invalid API Key` — server-http.cpp:302 (log literal `"unauthorized: Invalid API Key\n"`) and the JSON message `"Invalid API Key"` — **already held** (SKILL.md:181). The spec already tells `ExecApiKey`: find any >= 20-byte string other than `Invalid API Key`. The 401 JSON envelope `{"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}` is a composed JSON object; the individual literals are held except `authentication_error` (only 18 bytes alone) — the composed envelope is a candidate but check `authentication_error` occurrence (not held at base per Direction A; the emitted body would contain held `Invalid API Key` as a component, so the *body* contains a held string; clause (b) checks the signature string itself, not its substring components — but a signature of the whole envelope would contain the held `Invalid API Key` substring. Clause (g) only blocks earlier-counted-row strings, not base-held substrings, so a full-envelope signature is technically passable for (b) since `git grep -F` looks for the full envelope, which is not held. NOTE: emitted JSON spacing must be byte-exact: `{"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}`.)

## 2. Direction B — base quoted strings (>= 20 bytes) that occur in pinned sources

Extracted every quoted string of >= 20 bytes from base `SKILL.md` + `corpus/` (3381 unique) and checked
occurrence in the concatenated pinned sources. **38 of them occur in sources.** These are strings the lane ALREADY holds and that exist in the pinned tree — any exact-signature reuse is blocked. Notable:

- `Context size has been exceeded` / `Context size has been exceeded.`
- `Stream owner model is loading, retry later`
- `no slot available` (via corpus quotes)
- `default_generation_settings`
- `exceed_context_size_error`
- `/v1/chat/completions`
- `--kv-unified-per-slot`, `LLAMA_ARG_KV_UNIFIED` etc.
- `error and loading states are handled by middleware`, `no endpoints are allowed to be accessed when the server is not ready` (comment strings; not error signatures but present)
- `set model name aliases, comma-separated (to be used by API)`, `set model tags, ...`
- `DEPRECATED: argument ` (prefix)
- `Received second interrupt, terminating immediately.` (server.cpp:33)
- `only last value will be used`, ` specified multiple times, use comma-separated values instead (only last value will be used)`
- `n_ctx is not divisible by n_seq_max - rounding down to %u`
- `disable context reduction in llama_params_fit ...`, `when set without -c/--ctx-size, ...`
- `params.api_keys.push_back(key);`, `params.kv_unified = true;`, etc. (code stubs in corpus lessons)

Also held at base: `Server: llama.cpp` (server-http.cpp:180; corpus/knowledge/*), `{"status":"ok"}` (server-context.cpp:5297; SKILL.md:172), `{"error":{"message":"File Not Found","type":"not_found_error","code":404}}` composed (server-http.cpp:201-207) — the individual fragments `File Not Found`, `not_found_error` are held (SKILL.md:177; corpus); the composed envelope with exact spacing is not held but check the JSON output formatting (`safe_json_to_str`) byte-for-byte.

## 3. Historical error signatures freshness (SKILL.md lines 167-196)

The `## Historical error signatures — September runtime sample` section is byte-identical between base 1560e4d8 and the working tree and still describes b11755:

- `Server: llama.cpp` — still emitted: server-http.cpp:180 `srv->set_default_headers({{"Server", "llama.cpp"}})`. OK.
- `{"status":"ok"}` — still emitted: server-context.cpp:5297 `res->ok({{"status", "ok"}})`. OK.
- `default_generation_settings` — still in props: server-context.cpp:5243. OK.
- 404 `{"error":{"message":"File Not Found","type":"not_found_error","code":404}}` — still emitted: server-http.cpp:201-207 (content type `application/json; charset=utf-8`). OK. (The Jetty-html 404 row is a foreign service, not llama.cpp.)
- `Unauthorized`/`Invalid API Key`/`--api-key KEY` — `Invalid API Key` still emitted at server-http.cpp:302 (401 middleware); `--api-key` still a valid flag. OK.
- The `Loading model` 503 envelope (`{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`) at SKILL.md:518-523 — still emitted: server-http.cpp:314-322 (`middleware_server_state`). OK. 

All row claims attributed to llama.cpp remain true of the pinned 704366d source for the fixture model. No staleness found.

## 4. Family-level verdicts (which likely signatures are already held)

| Executor family | Held candidates (blocked) | Free candidates verified in source (unblocked) |
|---|---|---|
| ExecMetricsOff | none | `This server does not support metrics endpoint. Start it with \`--metrics\`` (server-context.cpp:5304) |
| ExecSlotsOff | `no slot available` (server-context.cpp:5396) — HELD | `This server does not support slots endpoint. Start it with \`--slots\`` (server-context.cpp:5366) |
| ExecSlotActionNoPath | `Invalid slot ID` (server-context.cpp:5403) and `Invalid action` (5413) and `Invalid filename` (6052/6119) and `Unable to save slot` (3025) / `Unable to restore slot` (3102) are NOT held | `This server does not support slots action. Start it with \`--slot-save-path\`` (server-context.cpp:5408) |
| ExecPropsOff | none | `This server does not support changing global properties. Start it with \`--props\`` (server-context.cpp:5453) |
| ExecEmbeddingsOff | none | `This server does not support embeddings. Start it with \`--embeddings\`` (server-context.cpp:6132) |
| ExecEmbeddingsInput | none | `"input" or "content" must be provided` (server-context.cpp:6159); `Pooling type 'none' is not OAI compatible. Please use a different pooling type` (server-context.cpp:6144) |
| ExecRerankOff | none | `This server does not support reranking. Start it with \`--reranking\`` (server-context.cpp:5803); `"query" must be a string` (5814); `"query" must be provided` (5818); `"documents" must be a non-empty string array` (5826) |
| ExecInfill | none | `Infill is not supported by this model: prefix token is missing. suffix token is missing. middle token is missing.` (emitted, server-context.cpp:5476 + 5462-5470 fragments) |
| ExecMissingModel | none | `error: failed to open file '<path>'` (arg.cpp:70,1833,1845,2298,3125,3549); `error: --model is required` (arg.cpp:919); `failed to load model from <path>` (llama-model-loader.cpp:574) |
| ExecJunkModel | none | `invalid magic characters: '<c0><c1><c2><c3>', expected 'GGUF'` (gguf.cpp:482); `GGUFv1 is no longer supported, please use a more up-to-date version` (gguf.cpp:512); `this GGUF file is version %d but this software only supports up to version %d` (gguf.cpp:516); `failed to read magic` (gguf.cpp:471); `failed to open GGUF file '<path>' (<errno>)` (gguf.cpp:1021) |
| ExecBadArgs | none | `error: invalid argument: <arg>` (arg.cpp:830,1223); `error: unknown value for --color: '<value>'` (arg.cpp:1515); `error: invalid value for n_parallel` (arg.cpp:2552); `error: argument with 2 values is not yet supported` (arg.cpp:1246) |
| ExecPortInUse | none | `couldn't bind HTTP server socket, hostname: <host>, port: <port>` (server-http.cpp:517); `listener on <addr> stopped unexpectedly` (server-http.cpp:533); wait `SS`-verified (the httplib bind error message itself comes from `SRV_ERR("couldn't bind HTTP server socket, ...")` — no `Address already in use` literal in the pinned source) |
| ExecPromptTooLong | `Context size has been exceeded.` (server-context.cpp:4301) — HELD; `exceed_context_size_error` (server-common.cpp:124) — HELD | `request (%d tokens) exceeds the available context size (%d tokens), try increasing it` (server-context.cpp:3678); `input (%d tokens) is larger than the max context size (%d tokens). skipping` (server-context.cpp:3669); `context shift is disabled` (server-context.cpp:3378); `context shift cannot be used for shared prompt` (server-context.cpp:3390) |
| ExecChatFormat | none | `'messages' is required` (server-common.cpp:1386); `Expected 'messages' to be an array` (1390); `All non-assistant messages must contain 'content'` (1395); `Assistant message must contain either 'content' or 'tool_calls'!` (1399); `Expected 'content' to be a string or an array` (1411); `Cannot have 2 or more assistant messages at the end of the list.` (1434); `Cannot set both add_generation_prompt and continue_final_message to true.` (1440); `Cannot continue an assistant message that contains tool calls.` (1446); `Cannot use custom grammar constraints with tools.` (1455); `invalid type for "enable_thinking" (expected boolean, got string)` (1473); `logprobs is not supported with tools + stream` (1517); `top_logprobs requires logprobs to be set to true` (1521); `response_format type must be one of "text" or "json_object", but got: <t>` (1375); `tools param requires --jinja flag` (1343) |
| ExecLoraAudio | none | `Request body must be an array` (server-context.cpp:5999); `Cannot run multiple aLoRAs in a single request` (server-context.cpp:1877); `Multimodal data provided, but model does not support multimodal requests.` (server-common.cpp:1100); `image input is not supported - hint: if this is unexpected, you may need to provide the mmproj` (1259); `audio input is not supported - hint: ...` (1272); `video input is not supported - hint: ...` (1287); `The current model does not support audio input.` (server-context.cpp:5655) |
| ExecRequestParams | none | `"prompt" elements must be a string, a list of tokens, ...` (server-common.cpp:1114); `"prompt" must not be empty` (1129); `"prompt" is required` (1143); `Unsupported param: <param>` (1162); `request body must be a JSON object` (server-http.cpp:857); `Invalid input batch.` (server-context.cpp:4303); `Compute error.` (server-context.cpp:4308) |
| ExecApiKey | `Invalid API Key` — HELD (SKILL.md:181) | composed 401 envelope `{"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}` (spacing-critical; component held) |
| ExecRouterModels | `Stream owner model is loading, retry later` — HELD (SKILL.md:519) | `model name is missing from the request` (server-models.cpp:2165); `model '<name>' not found` (server-models.cpp:2170); `model is not found` (server-models.cpp:2317,2461); `Stream not found or expired` (server-models.cpp:2587); `model name=<name> is not found` (server-models.cpp:854,1330,1672,1731,1850); `model limit reached, try again later` (server-models.cpp:1396) |

## 5. Method notes

- Extraction: C string literals via regex `"(?:\\.|[^"\\\n])*"`, min length 20 raw bytes, unescaped (`\n`, `\t`, `\"`, `\\`, `\0`) for the emitted form; both forms checked.
- Base text: 60 tracked files (`SKILL.md` + `corpus/**`), read via `git show 1560e4d8:<path>`, per-line containment (`s in line`) mirroring `git grep -F -q -e` (fixed-string, substring per line).
- Shape-checked formatted signatures (`%s`/`%d` substituted with realistic values: `</nonexistent/kama-r26/missing.gguf`, 1025 tokens vs 2048 context, port 47560): none held.
- The counter's `present_at_base` greps exactly `git grep -F -q -e <sig> 1560e4d8 -- SKILL.md corpus` — this writeup's containment check is equivalent for non-newline signatures (all C string literals are single-line).

## 6. Warnings

1. Spacing: emitted JSON bodies (`safe_json_to_str` output) must be byte-exact. `{"error":{"message":...}}` has NO spaces after `:`/`,`; the corpus quotes in SKILL.md:177 use exactly `{"error":{"message":"File Not Found","type":"not_found_error","code":404}}`.
2. Clause (b) blocks a signature that occurs at base anywhere — including inside a longer held string. E.g. `Context size has been exceeded` (no period) is ALSO held (round-16 corpus), so only the period-suffixed variant is additionally held; both directions checked.
3. Clause (f) additionally blocks help/version text — unaffected by this scan.
4. `--parallel <n>` help/usage text like `n_parallel` words are held in corpus (LLAMA_ARG_N_PARALLEL etc.) but are not error signatures; they only matter if an executor tries to use a help-text phrase as a signature (already blocked by (f)).
