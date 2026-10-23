## Gate

Fresh fetch date: 2026-10-23. Each row URL below is pinned to commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`. Every quote is literal source text from the fresh raw-file fetch and is under 25 whitespace-delimited words. The line-numbered grep proof is shown per row.

### Fresh-fetch and snapshot digest comparison

Each command was `mkdir -p /fast/scratch/hyaku/kama-r26/ScribeSourcesStartup/sources && curl -fLsS <raw URL> -o <scratch file> && sha256sum <scratch file>`; each completed successfully (exit 0). A `sha256sum` command over the eight corresponding files in `.ufo/waves/round-26/sources/llama.cpp-704366d/` also completed successfully (exit 0). Every fresh-fetch digest matched its lane snapshot digest:

| file | raw fresh-fetch SHA-256 | lane snapshot SHA-256 | result |
|---|---|---|---|
| `common.cpp` | `d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4` | `d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4` | equal |
| `gguf.cpp` | `7505d6a434dc740941a682fd3b476ef9bd9893ab76adf18c9969daa528bd5be5` | `7505d6a434dc740941a682fd3b476ef9bd9893ab76adf18c9969daa528bd5be5` | equal |
| `llama.cpp` | `8058a140d444b67bf64a1ce393d241dfd60080f4b117130c6f82e637e2109233` | `8058a140d444b67bf64a1ce393d241dfd60080f4b117130c6f82e637e2109233` | equal |
| `llama-model-loader.cpp` | `7975d83406627e405d36876472495c6111696e70db66c65a629d6213ec54fc04` | `7975d83406627e405d36876472495c6111696e70db66c65a629d6213ec54fc04` | equal |
| `arg.cpp` | `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d` | `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d` | equal |
| `server.cpp` | `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4` | `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4` | equal |
| `server-http.cpp` | `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb` | `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb` | equal |
| `server-context.cpp` | `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` | `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` | equal |

The seven requested source paths were fetched, plus `server-context.cpp`, whose line 1223 is explicitly assigned for S138. `llama-model-loader.cpp` was fetched and hash-compared as requested; it is not a separate row in the assigned ten-row list.

### Per-row quote and line-numbered grep proof

- **S130** — URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/common.cpp#L1423; accessed 2026-10-23. Quote: `failed to load model '%s'` (5 words; common.cpp:1423). Grep pattern `failed to load model`; proof: `1423:        COM_ERR("failed to load model '%s'\n", params.model.path.c_str());`
- **S131** — URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp#L1021; accessed 2026-10-23. Quote: `failed to open GGUF file '%s' (%s)` (7 words; gguf.cpp:1021). Grep pattern `failed to open GGUF file`; proof: `1021:        GGML_LOG_ERROR("%s: failed to open GGUF file '%s' (%s)\n", __func__, fname, strerror(errno));`
- **S132** — URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp#L482; accessed 2026-10-23. Quote: `invalid magic characters: '%c%c%c%c', expected 'GGUF'` (6 words; gguf.cpp:482). Grep pattern `invalid magic characters`; proof: `482:                GGML_LOG_ERROR("%s: invalid magic characters: '%c%c%c%c', expected 'GGUF'\n", __func__, c0, c1, c2, c3);`
- **S133** — URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama.cpp#L433; accessed 2026-10-23. Quote: `failed to load model` (4 words; llama.cpp:433). Grep pattern `failed to load model`; proof: `433:            LLAMA_LOG_ERROR("%s: failed to load model\n", __func__);`
- **S134** — URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp#L830; accessed 2026-10-23. Quote: `error: invalid argument: %s` (4 words; arg.cpp:830). Grep pattern `error: invalid argument`; proof: `830:                throw std::invalid_argument(string_format("error: invalid argument: %s", arg.c_str()));`
- **S135** — URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp#L1223; accessed 2026-10-23. Quote: `error: invalid argument: %s` (4 words; arg.cpp:1223). Grep pattern `error: invalid argument`; proof: `1223:            throw std::invalid_argument(string_format("error: invalid argument: %s", arg.c_str()));`
- **S136** — URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp#L876; accessed 2026-10-23. Quote: `error while handling argument` (5 words; arg.cpp:876). Grep pattern `error while handling argument`; proof: `876:                    "error while handling argument`
- **S137** — URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.cpp#L517; accessed 2026-10-23. Quote: `couldn't bind HTTP server socket, hostname: %s, port: %d` (9 words; server-http.cpp:517). Grep pattern `couldn't bind HTTP server socket`; proof: `517:            SRV_ERR("couldn't bind HTTP server socket, hostname: %s, port: %d\n", host.c_str(), port);`
- **S138** — URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L1223; accessed 2026-10-23. Quote: `failed to load model, '%s'` (5 words; server-context.cpp:1223). Grep pattern `failed to load model`; proof: `1223:            SRV_ERR("failed to load model, '%s'\n", params_base.model.path.c_str());`
- **S139** — URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp#L510; accessed 2026-10-23. Quote: `exiting due to model loading error` (6 words; server.cpp:510). Grep pattern `exiting due to model loading error`; proof: `510:            SRV_ERR("%s", "exiting due to model loading error\n");`
