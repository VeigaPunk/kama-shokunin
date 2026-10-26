# U1Server prediction: llama-server b11906 vs b11889 receipts (from source, no live run)

Verdict: all seven items are predicted EQUAL to the b11889 receipts, except `/props.build_info`, which is predicted to change by construction to `b11906-4d71b42fd`. That is a build-identity change, not a behaviour change.

Commits: A = b11889 = d854d98bae598388ecea1ed84396587e5edc326d; B = b11906 = 4d71b42fd87db24b8b7c808c151b713aa4459cfd. Bare clone: /fast/scratch/hyaku/kama-r46/L1/llama.git. Receipt: .ufo/waves/round-45/c1/live/receipt-1.json (llama-server -m stories260K.gguf --alias kama-r45-live --no-webui, single-model mode, text-only, no mmproj).

## What changed in tools/server/ (A..B)
`git diff A B -- tools/server/` is 81 lines in 3 files:
- server-context.cpp (+9/-6): new `mtmd_helper_cap mtmd_cap` member (B:1015). `has_cap_tts()` is `mtmd_cap.audio_gen` (B:1020-1022). `has_cap_chat()` is `mtmd_cap.chat` (B:1024-1026). `mtmd_cap = mtmd_helper_get_capabilities(model_tgt, mctx)` runs once in load_model (B:1401), before the first use (B:1518). `chat_params.allow_image/audio/video` read `mtmd_cap.vision/audio/video` (B:1711-1713). `has_audio_stream` reads `mtmd_cap.audio_stream` (B:5133).
- server-models.cpp: one comment (`mtmd_helper_model_can_chat` renamed to `mtmd_helper_get_capabilities`), no code.
- tests/utils.py: `DEFAULT_HTTP_TIMEOUT` 60 to 600 (test harness only).

Files with no diff A..B (checked with `git diff --stat A B -- <paths>`, empty output): server-http.cpp, server.cpp, server-common.cpp, server-queue.cpp, common/, cmake/, CMakeLists.txt, scripts/build-info.sh.

The refactor is semantically equivalent for a text-only server. Outside tools/server/, commit c6fb3b5be (tools/mtmd/mtmd-helper.cpp, "mtmd: add mtmd_helper_get_capabilities") defines the helper. With `mctx == nullptr` it returns `chat=true, text_gen=true` and every other field false, so there is no mmproj/TTS branch to differ. This matches A:
- A `has_cap_chat()` was `mctx == nullptr || mtmd_helper_model_can_chat(...)`, which is true with no mctx.
- A `has_cap_tts()` was `mctx != nullptr && ...`, which is false with no mctx.
- A allow_image/audio/video were `mctx ? ... : false`, which is false.
- A `has_audio_stream` was `mctx != nullptr && ...`, which is false.

Wider A..B changes (65 files) are ggml-cpu concat, vulkan/sycl/metal, deepseek, llama-model-saver, ui, CI, and common model resolution (74b104c9b, test-model-resolution.cpp). None touches the HTTP/readiness/signal paths below. The model-resolution commit affects `-hf`/preset resolution; the receipt used a local `-m` path.

## Per-item prediction (A line | B line)

| # | Item | Receipt (b11889) | Predicted b11906 | Equal? | Source |
|---|------|------------------|------------------|--------|--------|
| 1 | Loading-state 503 envelope | `/v1/models` 503 `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`; `loading_envelope_exact:true`, 24 repeats, one distinct body, sha256 baa09177... | Identical bytes and status. Ordering: `ctx_http.start()` runs before `load_model()` and `is_ready.store(true)` follows `load_model()`, so there is a loading window. Pre-routing middleware 503s every non-frontend path, including `/health`, while `!is_ready`. | YES | server-http.cpp:308-327 (A and B identical, `"Loading model"` at :319, `unavailable_error` at :320, 503 at :321); server.cpp:620 (ctx_http.start), :633 (load_model), :641 (is_ready.store(true)) unchanged; the envelope is hard-coded in middleware, not via `format_error_response` |
| 2 | `GET /health` body | 200 `{"status":"ok"}`, Content-Length 15 | Identical | YES | A:5606-5618 / B:5609-5621: `res->ok({{"status","ok"}})`; handler body unchanged; routes server.cpp:171-172 |
| 3 | `/v1/models` `owned_by` and `data[].id` / aliases | `owned_by:"llamacpp"`, `data[0].id == "kama-r45-live"`, `aliases:["kama-r45-live"]` | Identical | YES | `get_res_model_info` A:5486 / B:5489; `id` = `meta.model_name` A:5490 / B:5493; `aliases` A:5491 / B:5494; `owned_by` "llamacpp" A:5500 / B:5503. `model_name` = first `--alias` (A:1600 / B:1603), `model_aliases = params_base.model_alias` (B:1612). The router variant (server-models.cpp:2311-2315, :2385) is also unchanged and unused with `-m`. The Ollama-style `"capabilities":["completion"]` (A:5528 / B:5531) depends on `has_mtmd`, not on the new `mtmd_cap`, and stays `["completion"]`. |
| 4 | `/metrics` when not enabled | 501 | 501 with message "This server does not support metrics endpoint. Start it with `--metrics`" | YES | `get_metrics` A:5619 / B:5622 guard `!params.endpoint_metrics` then `ERROR_TYPE_NOT_SUPPORTED`; server-common.cpp:117-120 maps it to 501 "not_supported_error" (identical at both commits); route server.cpp:173 |
| 5 | `/props` `build_info` | `b11889-d854d98ba`; `model_alias`, `total_slots`, `is_sleeping`, `n_ctx` as in the receipt | `build_info` = `"b" + LLAMA_BUILD_NUMBER + "-" + LLAMA_COMMIT` (common/build-info.cpp.in:27-29, identical at A and B). Predicted value `b11906-4d71b42fd` (9 hex chars, matching the 9-char `d854d98ba` shape of the b11889 receipt; this depends on the release pipeline's abbreviated-hash length). Other fields equal: `model_alias` A:5563 / B:5566, `total_slots` = `params.n_parallel`, `is_sleeping`. | NO on build_info (expected, by construction); YES on the others | props assembly A:5556-5595 / B:5559-5598 unchanged; `build_info` fed from `llama_build_info()` A:5118 / B:5121 |
| 6 | SIGTERM shutdown | `sigterm_sent:true`, `sigkill_sent:false`, `returncode:0`, `term_wait_ms:15`, port closed | Identical path: `sigaction(SIGTERM)` calls `signal_handler`, which calls `shutdown_handler`, which calls `ctx_server.terminate()` and unblocks `start_loop()`. Then `clean_up()`, `ctx_http.join()`, return 0. Process exit 0. The new `mtmd_cap` member is a POD struct, so there is no new teardown. A second SIGTERM would `exit(1)` (unchanged). | YES | server.cpp:26-38 (handler, `is_terminating`), :320-325 (sigaction, SIGINT+SIGTERM), :645-649 (shutdown_handler), :671 (start_loop), then clean_up, :684 (return 0). Whole file has no diff A..B. The 3-15 ms timing is a measurement, not a contract. |
| 7 | Probe/consumer-level grades | `probe_model_ok` MODEL_OK/matched exit 0; `probe_mismatch` MODEL_MISMATCH exit 2 | Same, since they derive from items 2-3. | YES | derived |

## Receipt checks mapped (S041/S046/S055 statements)
- S041, S046, S055 assert: loading 503 exact envelope; `/health` 200 `{"status":"ok"}`; `/v1/models` id == alias and `owned_by` `llamacpp`; `/metrics` 501; SIGTERM returncode 0 with no SIGKILL; (S046/S055) `/props` model_alias == alias. All predicted to hold at b11906 (rows S041/S046/S055 stay `holds`, as S485's b11889 receipts did).
- The only observable difference in the receipt is `/props.build_info` and the server binary sha256, which is a different release artifact. A b11906 receipt must not pin `b11889-d854d98ba`.

## Residual risks / unverified (predictions, not observations)
1. The `build_info` hash abbreviation length of the b11906 release binary is inferred from b11889 (9 chars) [INFERENCE].
2. The b11906 release asset's linked sonames (libmtmd etc.) may differ from b11889's `install_links`. The receipt's `install_links` are a harness pin, not a server behaviour [INFERENCE]; check at install time.
3. `mtmd_cap` is assigned unconditionally in load_model (B:1401), after the mmproj block (which ends at B:1398). It is not re-assigned anywhere else. If `load_model` were skipped, the `{}` default would give `chat=false`, so `/v1/chat/completions` would return "does not support chat/completions" (B:5208). The server cannot reach ready without load_model (server.cpp:633-641), so this is not reachable for the readiness path. Out of scope for the receipts (completion/health only).
4. Port-bind/ready timing (loading 503 observed count: 25 responses at b11889) is a runtime measurement. The window exists by construction at both commits, but its length (and the repeat count) is not predictable from source.

## Falsifiers
- A live b11906 run showing `/health` body other than `{"status":"ok"}`, a different loading envelope, `/metrics` != 501, `owned_by` != `llamacpp`, `data[0].id` != `--alias`, or SIGTERM returncode != 0 would falsify this prediction.
- `build_info` != `b11906-<hash>` would falsify item 5's rule.

Commands run (all read-only): `git -C /fast/scratch/hyaku/kama-r46/L1/llama.git diff [--stat] A B -- tools/server/ | tools/mtmd | common cmake ...`; `git show A|B:tools/server/{server-context,server-http,server,server-common,server-models}.cpp`; `git show A|B:common/build-info.cpp.in`; `git log --oneline A..B`; `git tag --points-at` (b11889 and b11906 verified). Scratch copies in /fast/scratch/hyaku/kama-r46/U1Server removed at end.
