# CriticC2ToyModel — evidentiary weight of the C2 live receipt (advice, not a verdict)

Seat: critic, read-only. Axes attacked: **calibration** (does the receipt support only what it claims?) and **operability** (does the capability carry over to real llama.cpp deployments?).
State at review time: `tools/kama-llamacpp-live.py` and `tests/llamacpp-live/check-receipt.py` do not exist yet (`ls tools/` → kama-ollama-evidence.py, kama-probe.sh, test-snapshot.sh). I attacked the **design** in `build/spec.json` items LiveHarness / LiveReceiptGate and the context's C2 bullet.
Upstream sources were read at the pinned commit (raw.githubusercontent.com/ggml-org/llama.cpp/704366d76/…); links below use that commit. I ran no server, harness, gate or test. I installed nothing.

## What the model is (measured by reading the file's GGUF header, read-only)

`~/.cache/kama-shokunin/models/stories260K.gguf`: 1,185,376 bytes, GGUF v3, 48 tensors, **all type 0 (F32)**, `general.name = llama`, `llama.block_count = 5`, `embedding_length = 64`, `context_length = 2048`, 512-token vocab, **no `tokenizer.chat_template` key**. Summing tensor dims gives n_params = 292,800 and 1,171,200 tensor bytes.
The installed release has only CPU backends: `~/.local/opt/llama-b11755/libggml-cpu-{x64,sse42,haswell,zen4,…}.so` plus `libggml-rpc.so`. It has no CUDA, Vulkan, HIP or Metal backend.

## What a passing receipt DOES establish (keep it to this list)

1. **Real llama.cpp b11755 HTTP surface shapes**, on one CPU-only single-model build with default flags. `/health` → 200 `{"status":"ok"}`. `/v1/models` has both a `data[]` (OpenAI) array and a `models[]` (Ollama) array. `owned_by` is `llamacpp`. The `Server: llama.cpp` header is present. `/metrics` is refused without `--metrics`.
   Source: server-context.cpp L5182 `{"owned_by", "llamacpp"},`; server-http.cpp L180 `srv->set_default_headers({{"Server", "llama.cpp"}});`.
2. **kama-probe parses a genuine llama.cpp `/v1/models` body.** `served_ids` uses `data[].id` before `models[].name` (`tools/kama-probe.sh:325` "data[].id -> models[].id -> models[].name"). It returns MODEL_OK/matched on equality and MODEL_MISMATCH/served-id-mismatch on inequality, against a real server rather than a stub.
3. **The lane can acquire, launch and tear down an ephemeral llama-server.** It binds loopback only, avoids every registered port, and leaves no listener behind. This is the operability capability C2 claims, and the receipt is legitimate evidence for it.
4. **Only if `loading_observed` is true:** the live 503 loading envelope matches the C1 stub fixture **as parsed JSON**. C1's MODEL_LOADING rule is otherwise backed by source and README alone.

## What it must NEVER be used to claim

| # | Forbidden claim | Counterexample / evidence | Axis |
|---|---|---|---|
| N1 | **Served-model identity** ("the pinned model is what is being served") | `/v1/models` `id` is the caller's `--alias` echoed back. Source: server-context.cpp L5172 `{"id", meta.model_name},`; README L1284 "You can set a custom value for model `id` field via `--alias`". Any GGUF launched with `--alias kama-live-probe` passes `models_alias_id`, `props_alias` and `probe_model_ok` identically. The pre-launch sha256 gate binds only the *file path* handed to argv. llama.cpp itself reports no digest: L5206 `{"digest", ""}, // dummy value, llama.cpp does not support managing model file's hash`. | calibration |
| N2 | **Build identity from the recorded server sha256** | `~/.local/bin/llama-server` resolves to a 17,864-byte launcher (sha256 b6a31a8e…d804). `readelf -d` shows `NEEDED [libllama-server-impl.so]` and `RUNPATH [$ORIGIN]`. The serving code is in `libllama-server-impl.so` (7.3 MB, sha256 e404b91a…59ed), `libllama.so`, `libggml*.so`, and whichever `libggml-cpu-<variant>.so` is picked at runtime. The launcher hash pins none of that code. | calibration |
| N3 | **Health of registered consumers** | `registry/endpoint-consumers.tsv:35-37` lists only `:8080` (omp default) and `:34113` (Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS). The harness *refuses* exactly those ports, so the two sets overlap in zero ports by construction. The probe runs in `--port` override mode, which emits `"file_match":"cli-override"` (`tools/kama-probe.sh:847`) and is not a registry row. `registry/history/latest.tsv` still has all three rows `DEAD connection-refused`, and the receipt must not change that. Mirrors `SHONEN.md:8` "current `DEAD` is not model readiness". | calibration, operability |
| N4 | **Model readiness of real deployments, including what MODEL_OK means there** | MODEL_OK is computed from `/v1/models` alone (`tools/kama-probe.sh:476` "MODEL_OK requires a model array"). In b11755 `/v1/models` is answered *from cache while sleeping*: server-context.cpp L5727-5730 "this endpoint must be accessible during sleep … res->ok(cached_models)". README L2337 says "the model and its associated memory … are unloaded from RAM". README L2342-2344 list `/health`, `/props` and `/models` as exempt from reload. A `--sleep-idle-seconds` deployment therefore grades MODEL_OK and `/health` 200 with no model resident. In router mode, `GET /models` carries `status.value` `loading` / `unloaded`+`failed` / `sleeping` (README L2067-2094). The receipt runs neither mode: sleep is disabled by default (README L247 "default: -1; -1 = disabled"). | calibration |
| N5 | **Performance**: load time, latency, throughput, timeout sizing | The model is 1.17 MB F32 on CPU with `-t 1 -c 256`. Its loading window and transition timestamps (monotonic ms) are toy-scale. A 30B IQ2_XXS GGUF is several GB and is usually GPU-offloaded [INFERENCE: size class from quant name, not measured]. Transition timings must not set `--ready-timeout`, probe `--timeout`/`--connect-timeout`, or any expectation of how long a real MODEL_LOADING lasts. | operability, calibration |
| N6 | **Inference quality, generation, tokenization, chat templates** | The harness never calls `/completion`, `/v1/chat/completions` or `/tokenize`. The GGUF has no chat template and a 512-token vocab. stories260K is a TinyStories toy. Neither "the server generates" nor anything about quality is supported. | calibration |
| N7 | **GPU/offload paths** (`-ngl`, VRAM, CUDA/Vulkan/ROCm builds) | The installed release has CPU backends only (listing above). Builds used by real consumers are unknown and may differ [INFERENCE]. | operability |
| N8 | **Live MODEL_LOADING grading by the probe** | The probe is invoked only *after* `/health` == 200 (LiveHarness: probe runs follow the "Ready captures"). The probe's `llamacpp-loading` branch is therefore never exercised against a live server. The receipt can at most show that the envelope *bytes* exist live (§4 above). It also records `loading_observed` as "never required". On a 1.1 MB model the window is short and race-dependent [INFERENCE: L1's 10:17 smoke run did catch it]. A `false` must not be read as evidence against C1's envelope either. | calibration |
| N9 | **Concurrency/slot behaviour** | `/slots` is recorded only as a status code plus an element count. The "no slot available" envelope stays a declared scope limit of C1. | calibration |
| N10 | **API-key / auth paths** | No `--api-key` is passed, so UNAUTHORIZED_SERVICE (the 401 path in server-http.cpp L260-304) is not exercised live. | calibration |

## Defects in the current design, with the smallest safe correction

**D1. `models_alias_id`, `props_alias` and `probe_model_ok` form a closed loop on argv** (N1).
- Correction: add check `models_meta_matches_gguf`. `/v1/models` `data[0].meta` already exposes `n_vocab`, `n_ctx_train`, `n_embd`, `n_params`, `size` and `ftype` (server-context.cpp L5183-5191).
- The harness can derive the expected values from the pinned GGUF header with stdlib `struct`, as done above: n_vocab 512, n_embd 64, n_ctx_train 2048, n_params 292800, size 1171200, ftype ALL_F32. It then compares them to the served `meta`.
- This binds what is *served* to the hashed file. It also closes the hash-then-mmap TOCTOU gap [INFERENCE: low risk, user-owned cache].
- LiveReceiptGate should re-derive this check from the stored `/v1/models` body instead of trusting `passed`.
- Axes: calibration ↑, operability unaffected.

**D2. The server identity is the launcher hash only** (N2).
- Correction: also record the sha256 of `libllama-server-impl.so`, `libllama.so.*` and `libggml*.so` in the realpath directory.
- Also add check `props_build_info` requiring `/props` `build_info` to equal the expected build string. README L922 gives the format `"build_info": "b(build number)-(build commit hash)"`. Take the exact expected string from L1's own observation, not from me.
- [INFERENCE] Also keep the log line naming the selected CPU backend variant. The harness's keep-regex `build|model loaded|listening|loading` may not match a "loaded CPU backend" line; L1 should verify against the copied log.

**D3. `metrics_not_enabled` passes on any non-200**, including connection refused after a crash.
- Counterexample: the server dies after `/health` 200; `/metrics` then returns a connect error and the check passes.
- Correction: require HTTP status 501, which L1 observed. Source: server-context.cpp L5303-5304 "This server does not support metrics endpoint", `ERROR_TYPE_NOT_SUPPORTED`. Record the parsed error `type`.
- Same pattern for the ready captures: a capture with a connect error should fail its check rather than read as "absent".

**D4. The envelope comparison must be semantic, not byte-level** (§4, N8).
- nlohmann/json serialises object keys sorted. README L486 shows `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}`, while the C1 context quotes the order message-first.
- If L1 or ProvenanceLedger compares the live first-503 body against a stub `body_json` by bytes or sha256, a correct implementation fails spuriously.
- Correction: compare `json.loads` equality, and record the live body sha256 separately as an observation, not as the fixture hash.

**D5. Receipt self-description.** Add a fixed `scope` object to the kama-llamacpp-live/v1 schema and have LiveReceiptGate require it verbatim. Proposed fields:
- `"model_class": "toy-f32-cpu"`
- `"exercised": ["single-model","no-sleep","no-router","no-api-key","no-inference","cpu-only"]`
- `"not_evidence_for": ["registered-consumer-health","served-model-identity-beyond-meta","performance","inference-quality","gpu-offload","live-MODEL_LOADING-verdict"]`

This stops downstream scribes (SHONEN box 2, LOG.md, knowledge files) from promoting it beyond N1–N10.
- Axis: calibration ↑. Cost: one static field.

## Tradeoffs (do not "fix"; declare them)

- **Toy model choice.** It is right for C2: fast, deterministic, cheap, and no registered-port contact. A larger model would widen the loading window and help N8, but would cost minutes, RAM and disk for marginal calibration gain. Keep the toy and keep the claims narrow.
- **Alias instead of default id.** With an alias, the default-id path (id = model file path; probe `normalize_id` strips the directory and `.gguf`, `tools/kama-probe.sh:371`) is unexercised live. Real consumers expecting `Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` likely depend on it [INFERENCE]. An optional second launch without `--alias` would cover it. Declare it as a limit unless L1 wants a second launch.
- **SHONEN box 2** (`SHONEN.md:7`). The receipt supports "lane executed a live llama.cpp endpoint lifecycle and probe reconciliation on a lane-owned toy server". It does not support box 2's real domain task, reconciling *registered* consumers, which remain DEAD. That stays `[~]` for consumer readiness.

## Limitations of this review
- I reviewed the design only; the harness and gate code were absent, so there are no line numbers in them.
- Upstream code was read at commit 704366d76 through GitHub raw, which I took to be the b11755 commit per the context. I did not independently re-verify the release↔commit mapping.
- The `ERROR_TYPE_NOT_SUPPORTED` → 501 mapping is taken from L1's observation, not from source I read.
- I ran no llama-server, probe or gate. Installs: none.
- Scratch copies of upstream files in `/tmp/kama-crit-*` were deleted after review.
