# Draft SOURCES row — S1xx (common/fit.cpp @ 704366d76)

Claim C2 (sourced claim), round 25 attempt 2. Draft only; status `queued`
until the L1 cites it. No edit to `corpus/SOURCES.md` was made.

## Registry row (exact 11-column format of corpus/SOURCES.md)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S1xx | llama.cpp common/fit.cpp @ 704366d76 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp | code | A | how llama-server at commit 704366d76 sizes served KV context when n_ctx is unset (n_ctx_train x n_streams for a split cache) and when fit reduces it; not runtime observation, not HTTP surfaces, not other builds | line 270 comment + line 272 assignment: "llama_context would use only hp_nct in total for n_ctx == 0, resolve the context before measuring anything else:" -> `cparams->n_ctx = n_ctx_max;`; n_streams definition line 197; max/min totals lines 267-268; reduction branch lines 393-394, 426-430, 447-455; raw file sha256 1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58 | An unset context is resolved before measuring: n_ctx_max = min(n_ctx_train x n_streams, UINT32_MAX) with n_streams = 1 if KV unified else max(1, n_seq_max), and cparams->n_ctx = n_ctx_max; reduction to n_ctx_min_total (= min(n_ctx_min x n_streams, UINT32_MAX)) happens only in auto mode when n_ctx_max > n_ctx_min_total, by linear interpolation rounded down to align = 256 x n_streams and floored at n_ctx_min_total; a user-set context is never changed here. | queued | 2026-10-22 | on-release | — |

## Gate record

- URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp
  (fetched raw: https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp)
- Access date: 2026-10-22
- Fetch command: `curl -fsSL -o fit.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp`
  — exit code 0, file 1113 lines.
- sha256 (raw file): `1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58`
- Located quote (at most 25 words), line 270:
  `llama_context would use only hp_nct in total for n_ctx == 0, resolve the context before measuring anything else:`
  (18 words) — followed at line 272 by `cparams->n_ctx = n_ctx_max;`.
- Secondary located quote, line 428:
  `round down context for CUDA backend, keep it divisible by the number of streams:`
  (14 words) — followed at lines 429-430 by `align = 256 * n_streams` and
  `cparams->n_ctx = std::max(cparams->n_ctx - cparams->n_ctx % align, n_ctx_min_total);`.

## What the source does not establish

1. It does not establish that this code path is what the running b11755 server
   observes. Fit is gated by caller files (server.cpp lines 180-184 reuse
   `params.fit_params_min_ctx`; arg.cpp defines the flags); observed `/props`,
   `/slots` and `/v1/models` values are runtime behavior, not source behavior.
2. It does not establish the default minimum context: `n_ctx_min` is a function
   parameter (fit.cpp line 182/886); the llama-server default 4096 lives in
   common/common.h line 485 (`fit_params_min_ctx = 4096;`), fetched fresh, sha256
   8bcc5708...4a9.
3. It does not establish that `-c 0` disables reduction; that is arg.cpp lines
   1646-1649 (`fit_params_min_ctx = UINT32_MAX` when the ctx-size value is 0).
4. It does not establish the actual per-slot split of a shared pool at runtime.
   It states the total `cparams->n_ctx` and the `n_streams` multiplier; slot
   division and serving live elsewhere (server-context.cpp) and are runtime
   observations.
5. It does not establish when reduction triggers on a real host: the branches
   depend on memory probing (`common_get_device_memory_data_impl`) and margins,
   which require a live run to observe.
6. It does not establish behavior of any other commit or build, nor unified-KV
   serving details beyond `n_streams = 1`, nor router-mode behavior.
