# S02LlamaCppSpec — pinned llama.cpp completions contract

Source fetched directly: `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md` (tag b11755). Relevant anchor: **“POST `/v1/completions`: OpenAI-compatible Completions API”** under “OpenAI-compatible API Endpoints”; adjacent **“Timings and context usage”** and `/completion` sections clarify shared semantics.

## Gate quote (≤25 words)
> “Given an input `prompt`, it returns the predicted completion. Streaming mode is also supported.” — `tools/server/README.md`, “POST `/v1/completions`: OpenAI-compatible Completions API”

## Contract details observed at pinned tag
- **POST `/v1/completions`**: README delegates options to OpenAI Completions API documentation and warns it makes no strong compatibility claim. It explicitly says `/completion`-specific features (e.g. `mirostat`) are supported. The adjacent non-OAI `/completion` specification documents `prompt` as string, token array, mixed token/string sequence, or object; `n_predict` is max generated tokens (default -1, infinity); `temperature` defaults 0.8; `seed` defaults -1 (random). Treat these as documented `/completion` options, not proof every alias/option is an exact OAI request contract.
- **Response**: README's OAI completions section does not enumerate the response object fields. The shared OAI API “Timings and context usage” section shows a `timings` object with `cache_n`, `prompt_n`, `prompt_ms`, `prompt_per_token_ms`, `prompt_per_second`, `predicted_n`, `predicted_ms`, `predicted_per_token_ms`, `predicted_per_second`; and a standard `usage` object with `completion_tokens`, `prompt_tokens`, `total_tokens`, `prompt_tokens_details.cached_tokens`.
- **system_fingerprint**: not specified in the README's OAI completion section or timing/usage example; no guarantee found in this source.
- **Error body shape**: not specified for `/v1/completions` in the README. Do not infer it from the separate `/health` 503 example (`{"error":{"code":503,"message":"Loading model","type":"unavailable_error"}}`), which is explicitly the health endpoint's body.

## Local relevance
Observed `tools/kama-completion-live.py:160-166` sends request path `/v1/completions` and records `prompt`, `n_predict`, `temperature`, and `seed` as its request inputs. Its imported `tools/kama-llamacpp-live.py` is the local dependency. This source check does not establish endpoint runtime behavior or a response/error schema beyond the upstream documentation above.

No tools installed/updated. No live request run. Scratch directory created at `/fast/scratch/hyaku/kama-r62/w/S02LlamaCppSpec`; removal pending before yield.
