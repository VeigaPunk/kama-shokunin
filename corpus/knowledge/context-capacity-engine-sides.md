source: S478 — vLLM `vllm/v1/core/kv_cache_utils.py` @ tag v0.32.0 — https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/v1/core/kv_cache_utils.py (sha256 af4164bca819f1cdc416077522a7019936fd38a523a482283eb91b08dae0e57a, copy `.ufo/waves/round-42/c3/vllm-v0.32.0-kv_cache_utils.py`); S479 — llama.cpp `tools/server/server-models.cpp` @ commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad — https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-models.cpp (sha256 9c5a6f2cc7997a3a409482c53119a2462e8c409ddf001cc568a9a8740e708b4a, copy `.ufo/waves/round-42/c3/llamacpp-704366d7-server-models.cpp`)
verified-at: 2026-10-25 — both files fetched 2026-10-25T21:06:04Z by the round-42 L1 (`curl -fsSL`), line numbers below read from the committed copies
recheck: on-release — re-fetch both URLs at the then-current pin and re-run `python3 tools/round42-capacity-audit.py --repo . --tip HEAD`; a new vLLM tag or a new llama.cpp pin makes every line number here a sample, not a law

# Declared versus served context capacity: what two engines' own source publishes

Ground: frontier item K05, declared-versus-served context capacity (`corpus/README.md` §Frontier). The lane's measured entry, `corpus/knowledge/context-capacity.md`, is llama.cpp b11755 on a lane-owned fixture: two capacity numbers (the KV pool and the per-slot ceiling), with the API reporting only the second. This entry adds what two engines' source says about *which numbers they compute and where they print them*. It is a source reading, not a measurement: no server was run for it, the lane still holds no vLLM runtime, and K05 across real registered consumers stays runtime-blocked.

## vLLM at v0.32.0: the served number is derived, then logged beside the declared one

- The memory-derived quantity is a block count: `num_blocks = available_memory // bytes_per_block` (`kv_cache_utils.py:1627`), after which `may_override_num_blocks` can replace it with `num_gpu_blocks_override` when that option is set (`kv_cache_utils.py:1230-1236`). So the served pool can be an operator override, not a measurement of memory.
- The token capacity the engine reports is *derived from the declared length*: `get_kv_cache_capacity` returns `int(max_concurrency * max_model_len)` (`kv_cache_utils.py:2308`), where `max_concurrency` is the number of `max_model_len`-long requests whose blocks fit in the pool (`get_max_concurrency_for_kv_cache_config`, `kv_cache_utils.py:1195-1227`, the minimum over the device pool and, when present, the host pool). The "capacity in tokens" is therefore not a second independent measurement: it equals the pool expressed in units of the declared per-request length.
- `update_kv_cache_capacity` stores `kv_cache_size_tokens` and `kv_cache_max_concurrency` on the cache config (`kv_cache_utils.py:2321-2322`) and prints all three numbers in one line: `"%s KV cache size: %s tokens, Maximum concurrency for %s tokens per request: %.2fx"` (`kv_cache_utils.py:2328`) — the served token capacity, the declared `max_model_len`, and their ratio.

Reading for an operator: on vLLM the startup log is the single place where the declared per-request length and the served pool meet; the log line is the evidence to capture, and a tool that only reads a declared length (a model card or a config) sees one half. Whether the HTTP model listing exposes `kv_cache_size_tokens` is not established here and is not claimed.

## llama.cpp at 704366d7: the router's model listing publishes the declared (training) context as `context_length`

- The handler `get_router_models` (`server-models.cpp:2329`) builds one JSON object per model and adds `context_length` only when the loaded metadata reports a positive training context: `if (meta.n_ctx_train > 0) {` followed by `model_info["context_length"] = meta.n_ctx_train;` (`server-models.cpp:2378-2379`).
- The key is llama.cpp's own: `max_model_len` occurs 0 times in `server-models.cpp` (`grep -o max_model_len <copy> | wc -l` → 0, 2026-10-25). A client that reads only `max_model_len` finds no declared capacity in this listing; that is a statement about the key a client reads, not about the engine.
- The value is the GGUF *training* context (`n_ctx_train`), the same quantity the lane's fixture reports as `n_ctx_train` in its own measured cells (`corpus/knowledge/context-capacity.md`, `corpus/knowledge/gguf-declared-identity.md`); it is not the per-slot ceiling and not the pool.
- Scope: this is the router-mode listing handler. Whether the single-model server's `/v1/models` body uses the same code path is not read in this file and is not claimed; the lane's measured b11755 fixture cells remain the evidence for that surface.

## What the two readings establish together

| engine | declared side | served side | where it is printed or returned |
|---|---|---|---|
| vLLM v0.32.0 | `max_model_len` | `kv_cache_size_tokens = int(max_concurrency * max_model_len)` from `num_blocks` | one startup log line (`kv_cache_utils.py:2328`) |
| llama.cpp 704366d7 | `context_length = n_ctx_train` (router listing, only when > 0) | the pool and per-slot numbers the lane measured in `context-capacity.md` | router listing (`server-models.cpp:2379`); pool in the server log |

A K05 comparison needs the declared value under each engine's own key name and the served value from the engine's own log, not from the OpenAI-shaped fields. Both sides are now documented for these two engines; the comparison on a live registered endpoint still needs an authorised serving runtime.

## Limits

- Two source files at two pins. SGLang, Ollama, TGI and the llama.cpp single-model server are not read here.
- Source reading only; the vLLM figures were not reproduced by running vLLM, and v0.32.0 is the lane's `pin-watch` pin for vLLM (`registry/engine-pins.tsv`), so a newer tag can change these lines.
- The staged shokuknow amendments that proposed this ground (`merge/kama/knowledge/corpus/knowledge/context-capacity-amendment-2026-10-23-r5.md` and `...-2026-10-24-r7.md`) were re-grounded, not copied: this entry corrects two of their simplifications (the vLLM token figure is derived from `max_model_len`, not read straight off the block count; the llama.cpp listing is the router handler, not a general card). Reasons and quotes: `corpus/lessons/round-42.md` §Gate.
