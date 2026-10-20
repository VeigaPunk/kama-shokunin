# ScribeSourcesRows — round 16 advice (sources-rows)

Owned output: `.ufo/waves/round-16/build/drafts/sources-rows.md` (rows S035–S038, search-log supplement). This report adds nothing to `corpus/` and changes no other file. Access date for every item: 2026-10-20.

## Behaviour and findings

1. **Loading body is served by middleware on every non-frontend path, not only `/health`.** `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76/tools/server/server-http.cpp:307-328` (lambda `middleware_server_state`): `if (!is_ready.load())` → only frontend paths pass (309–311); otherwise `res.status = 503` with `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` (314–321). Quote (312): "no endpoints are allowed to be accessed when the server is not ready". Called from the pre-routing handler at lines 331 and 354. Implication for C1: a stub 503 on `/v1/models` with exactly that object is the loading body; `code` is an integer in source, matching the C1 match rule.
2. **Documented shape.** `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76/tools/server/README.md:479-490`: `/health` 503 body `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}`, "Explanation: the model is still being loaded." (line 487); 200 `{"status": "ok" }` when ready (488–490). `README.md:1258`: `/v1/models` "`meta` field can be `null` (for example, while the model is still loading)."
3. **Release identity.** `https://github.com/ggml-org/llama.cpp/releases/tag/b11755`: "released this 20 Oct 11:18", commit `704366d` (704366d76f8748cf9ad3df62a464bfcc8d1ae6ad), page label "Pre-release". Digest via `https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11755`: `llama-b11755-bin-ubuntu-x64.tar.gz` `sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`, size 22240468, published_at 2026-10-20T11:18:44Z.
4. **Model identity — the lane's path is slightly wrong.** The pinned file is `tinyllamas/stories260K.gguf` inside `ggml-org/models` (page: `https://huggingface.co/ggml-org/models/blob/main/tinyllamas/stories260K.gguf`, title "tinyllamas/stories260K.gguf · ggml-org/models-moved at main", SHA256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; tree API `https://huggingface.co/api/models/ggml-org/models/tree/main/tinyllamas`: size 1185376, lfs oid 270cba1b…). A root-path `ggml-org/models/resolve/main/stories260K.gguf` returns HTTP 404. A recursive tree sweep (`https://huggingface.co/api/models/ggml-org/models/tree/main?recursive=true`, 36 entries) lists stories260K only under `tinyllamas/`. `ggml-org/tiny-llamas/stories260K.gguf` has the same size but lfs oid `047bf46455a544931cff6fef14d7910154c56afbc23ab1c5e56a72e69912c04b`, so it is not the lane's bytes.
5. **Local bytes match the official asset (own check, read-only).** I downloaded `llama-b11755-bin-ubuntu-x64.tar.gz` once to a scratch directory and compared digests: tarball sha256 `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226` (equals the API digest and the lane's pin). Extracted `llama-b11755/llama-server` sha256 `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` equals `~/.local/opt/llama-b11755/llama-server` and `~/.local/bin/llama-server` (same bytes via link). `libllama.so.0.7.0` sha256 `983e1a2a037c6e6a393848e3be9f5e6e00d7ee3022aca4c2f17ed093de819fb6` matches both the tarball and the installed copy. The local model file sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` matches the models-repo lfs oid. I did not execute `llama-server` (no `--version`), so no runtime claim is made.

## Draft rows and integration notes (for L1)

- Rows S035–S038 are drafted in `drafts/sources-rows.md`, all `queued`, `used-by` `—`: `corpus/knowledge/llamacpp-loading-lifecycle.md` and `corpus/lessons/round-16.md` do not exist yet (checked 2026-10-20). Flip to `mined` and fill used-by only when those files exist; otherwise the census "mined rows whose used-by paths do not exist" check fails.
- `kind` for S038 is `dataset` as the nearest frozen value for a GGUF artifact; no `model` kind exists. L1 decides whether to accept that.
- S037's teaches records that the release page is marked Pre-release; a stability claim would need a separate source.
- S001 (commit c0fd786) remains; S035 is a later pin, not a supersession.

## Limitations and unknowns

- The `is_ready` setter (`is_ready.store(true)` or equivalent) is not in `server-http.cpp` (only the load at line 308 appears); its file and line were not located because it is outside the four named sources. Unknown: exactly when `is_ready` flips.
- The release web asset list did not render in the reader; digests come from the REST API.
- Access was by raw GitHub files, the REST API and Hugging Face API/page, all 2026-10-20. No web search engine was used; the search-log supplement records the fetch sweep only.
- The `ggml-org/models` repo id resolves to `ggml-org/models-moved`; the commit at fetch time was 499bc8821c6b12b4e53c5bffcb21ec206f212d81 (lastModified 2025-10-28T10:43:38Z). Whether the repo was renamed, and when, is unknown.

## Tooling

- Installs or updates: none. Used existing `curl`, `sha256sum`, `tar`, `python3`.
- Scratch files were created under `/tmp/r16src` (outside the lane) and removed after use.
- No lane gate, harness or test was run; no lane file other than the draft and this report was written.
