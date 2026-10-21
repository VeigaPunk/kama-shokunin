# Proposed SOURCES row (L1 assigns the final ID/status)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S058 | llama.cpp server context and model metadata @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp | code | A | llama.cpp single-model GET `/props` effective per-slot `default_generation_settings.n_ctx` and GET `/v1/models` `data[0].meta.n_ctx` / `n_ctx_train`; not a claim that slot context equals training context | `n_ctx_slot()` lines 4654-4663; metadata projection lines 4847-4849 and 5183-5188; `/props` projection lines 5229-5245; raw sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329 | `/props.default_generation_settings.n_ctx` is the per-slot context capped by the model training context (and optional `--kv-unified-per-slot`), while `/v1/models.data[0].meta.n_ctx_train` is a separate field. | queued | 2026-10-21 | on-release | — |

**Located quote (18 words):** “context size of a single slot, capped by --kv-unified-per-slot and by the training context of the model” — `tools/server/server-context.cpp:4654`, commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`.

**Census note:** The canonical URL is already S042's source URL under a different scope, so adding this distinct scope will produce W04 (cross-scope duplicate URL); `scripts/sources-census.sh` says W04 does not affect clean lanes (lines 32-33). Do not treat W04 as a validation failure.
