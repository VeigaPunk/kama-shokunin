# Change map b11906 -> b11909 (ggml-org/llama.cpp), seat U2Server, round 47

Verdict: **no file under tools/server/ or common/ (so not common/arg.cpp) changed between b11906 and b11909; none of the receipt statements can change; 5 of the 91 on-release registry rows cite a changed file (src/llama-context.cpp, src/llama-kv-cache.cpp), and in each the cited text is byte-equal and only line numbers shift.**

Method: `git clone --bare --filter=blob:none https://github.com/ggml-org/llama.cpp.git` into scratch, then read-only git. Tags checked with `git ls-remote`: b11906=4d71b42fd87d (A), b11907=4b851fbee886, b11908=a4699400e3cc, b11909=caa8191df159 (B), b11910=63b4b303bd87. A is an ancestor of B. Raw lists: commits.txt, stat.txt, changed-files.txt (same dir).

## 1. Commits (`log A..B`, 3, linear; each is exactly one tag step)
```
caa8191df 2026-10-26T08:21:14-07:00 hexagon: MUL_MAT_ID row skipping optimizations and improvements (#31169)   [b11909, 1 file]
a4699400e 2026-10-26T16:21:25+02:00 llama : move no_alloc out of llama_hparams (#31141)                        [b11908, 30 files]
4b851fbee 2026-10-26T16:19:47+02:00 models : replace ggml_tensor** out-params with output structs (#31142)    [b11907, 7 files]
```

## 2. Changed files (`diff --stat A B`): 38 files, all status M, 641+/452-
- ggml/src/ggml-hexagon/htp/matmul-ops.c (250): Qualcomm Hexagon DSP backend; not built in the ubuntu-x64 release asset path used by the receipts.
- src/ (28 files): llama-context.cpp, llama-hparams.h, llama-kv-cache{,-dsa,-dsa-iswa,-dsv4,-iswa,-msa}.{cpp,h}, llama-memory{,-hybrid,-hybrid-idx,-hybrid-iswa,-recurrent}.{cpp,h}, llama-model.{cpp,h}, llama-moe-cache.{cpp,h}, llama.cpp, models/{deepseek4,deepseek41,dflash,glm5-next,hy-v4,models.h,qwen4exp}.cpp. Content: `no_alloc` moves from `llama_hparams` to `llama_model::no_alloc()` (= `params.no_alloc`), a new `llama_memory_params.no_alloc` and a shared `llama_memory_bufs` helper replace per-cache dummy-buffer code; model graph builders return output structs instead of `ggml_tensor**`.
- tests/llama-context/cases-kv.cpp (+49).
- Not touched: tools/ (tree e0cf320ab8, identical at A and B), common/ (tree 3b01489f22, identical), include/ and ggml/include (identical), .github, CMake, scripts (0 changed paths).

## 3. tools/server/ and common/arg.cpp
- `git diff --stat A B -- tools common include ggml/include`: empty. `git log A..B -- tools/server common`: 0 commits. Tree ids tools/server = bb7cdb4c71c9 and common/arg.cpp blob = 9706b3ac58d5 at both A and B.
- Nothing in tools/server reads `hparams.no_alloc` (0 hits at B). tools/ and common/ only use the public `llama_model_params.no_alloc` (include/llama.h:355, unchanged); the internal move does not alter its meaning.
- Hence every statement the live receipts check is unchanged at the source level, at B as at A (receipt statement -> site at B):
  - health body `{"status":"ok"}` 200: server-context.cpp get_health ~5609-5618 (pinned span L5288-5299 at 704366d)
  - loading 503 envelope: server-http.cpp middleware ~315-326 (pinned L314-325)
  - /v1/models `owned_by` "llamacpp": server-context.cpp:5503 (router path server-models.cpp:2315, 2385); id = --alias
  - /metrics 501: server-context.cpp:5625 (`ERROR_TYPE_NOT_SUPPORTED`, "Start it with `--metrics`"; error type maps to 501)
  - /props build_info and model_alias: tools/server and common/build-info inputs unchanged. The value `b11909-caa8191df` in receipt-1 is the release build's own, correct for B.
  - SIGTERM shutdown: server.cpp 318-325 `server_install_signal_handlers()` -> sigaction(SIGTERM, signal_handler); handler -> `shutdown_handler` (645-648) -> `ctx_server.terminate()`; `start_loop()` returns at 670-671. Unchanged A->B.
- Runtime (non-source) caveat: the src/ edits touch KV-cache and context construction used by every model load, including stories260K (llama arch -> `llama_kv_cache`, so `llama_memory_bufs::emplace`). Reading the diff, normal (no_alloc=false) behaviour is unchanged: the same `ggml_backend_alloc_ctx_tensors_from_buft` + `ggml_backend_buffer_clear` calls, only moved into the helper. The three b11909 receipts are the runtime evidence that the lifecycle still passes; no HTTP-facing text depends on these files.

## 3b. Observation for the receipts' documented_by (not caused by b11909)
The checks `health_ready`, `loading_envelope_graded`, `teardown_graceful` cite raw URLs at **704366d76f8748cf9ad3df62a464bfcc8d1ae6ad** (b11889 era) with line numbers L5288-5299, L314-325, L529-534/519-523/575-590, not at b11906/b11909. Mapped to B: get_health is at ~5609 (text equal), the 503 middleware at ~315 (text equal), but the pinned server.cpp span 519-534 is **not present verbatim at B**: commit f3269ef96 "server: refactor server entrypoint (#31113)" (2026-10-24, within the 704366d..b11906 range) moved the SIGTERM install into `server_install_signal_handlers()` (server.cpp 318-325) and calls it from 544 and 651. The SIGTERM behaviour is the same; the citation is stale. Registry row S037 (tools/server/server.cpp, release ranges 506-525 and 619-641) already carries the b11906 server.cpp text; server.cpp is identical A->B, so it carries to b11909. Total tools/server + common/arg.cpp churn between pin 704366d and B: 20 commits (c6fb3b5be, 224d94c02, 63412d873, b3fa69955, f3269ef96, 21ec30714, 184f65360, d814cbb88, a5d22276b, 1f4c2eeaa, 261700b89, 9a3b91c68, 5c0b49a23, 1242be66f, ead9f3205, 7e3eeee04, 5a9a34d88, 4e201388c, 1ba568c5a, d80619397); all predate b11906 and were already read in round 46 (registry rows). Proposed fix: have a future receipt generation take its documented_by URL/lines from the b11909 row (server-http.cpp 315-326, server.cpp 318-325 + 645-648), or key them to the registry row ids.

## 4. Registry rows citing a changed file (registry/release-recheck-b11906.tsv, 91 rows, all release=b11906)
All 91 `release_blob` values equal the A blob of their path (checked with `git rev-parse A:path`); 16 distinct paths; 14 of them are byte-identical at B. Reading set for the next freshness round (b11909 or later): **5 rows**, two files:

| row | path | pin lines (b11906) | b11909 lines | note |
|---|---|---|---|---|
| S107 | src/llama-context.cpp | 225,387-403,419-427,4132-4136 | 225,387-403,419-427,4133-4137 | text equal; +1 shift after new line 492 |
| S132 | src/llama-context.cpp | same as S107 | same as S107 | same; also depends on common/fit.cpp (identical) |
| S130 | src/llama-context.cpp | 2642 (+ deps 192, 342, 618) | 2643 (192, 342, 619) | text equal |
| S113 | src/llama-kv-cache.cpp | 65-98,142-145,233-244,301-304,1222-1234 | 65-100,144-147,235-246,289-292,1197-1209 | 65-98 contains the signature edit (new `bool no_alloc` param at 67, `ctxs_bufs(no_alloc)` init at 86); cited statements (n_stream line 84->85, shared-source kv_size 92-97->94-99) text equal; size-log 301-304 text equal (block moved up 12 lines) |
| S135 | src/llama-kv-cache.cpp | 142-145,233-234,301-304 | 144-147,235-236,289-292 | text equal; also the ctor's `ctxs_bufs` ownership changed; the size log still prints K+V MiB / kv_size / layers / n_seq_max |

Per-range check: new line = old + cumulative hunk offset; for each range the old and new text compared equal (kv-cache 65-98 excluded by the signature hunks, where only lines 67 and 83 changed/ added). So the expected verdict for all five is **holds, text-equal with line renumbering** (S113 'holds-reworded' possible because of the signature hunk).

S116 (tools/server/server-context.cpp) cites src/llama-context.cpp only in prose; its anchored file is identical, so it is not in the reading set. The other 85 rows cite files whose A and B blobs are identical (tools/server/*, common/arg.cpp, common/common.cpp, common/fit.cpp, ggml/src/gguf.cpp, gguf-py/gguf/gguf_reader.py, tools/quantize/README.md), and a freshness round at b11909 can carry them by blob identity.

## 5. Limits
- Per-line equality was computed from the git diff hunks, not by re-reading each registry claim; the verdicts for the five rows are inferences from text equality, not new human readings.
- Receipts' runtime behaviour at b11909 was not exercised by this seat (no replay run).
