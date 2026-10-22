VERDICT: The L1-L3 design measures a real limit, but it does not yet prove the stated claim. L1's prediction is weak enough that an off-mechanism outcome would pass it. Overlap and request outcome are not in the counted fields. L2 changes two variables at once. "Full-context" is the wrong name for what fails. Seven fixable defects follow (D1-D7), with no claim-count change. Sibling L-cell runs fit the source path and show no falsifying outcome.

Seat: KamaR25a2.CriticLoadCells (critic, claim C2, read-only, wave 1). Access date for every source: 2026-10-22. No llama-server was started by this seat. I read the sibling ExecLoadReplicate scratch logs and receipt as data only.

## Axes

- Validity: does an L-cell outcome come from the shared-pool mechanism and nothing else?
- Calibration: is each prediction sharp enough that a wrong mechanism would miss it?
- Provenance: do the receipt and quoted log lines come from the server lifetime that served the counted requests?
- Coverage: is the knowledge statement worded at the scope the cells support?

## Sources (fetched fresh, pinned)

All files are from `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/<path>`. Hashes are in `out/CriticLoadCells/sources.sha256`. `tools/server/server-context.cpp` has sha256 `dd1de0f2…2329`; `cmp` shows it is byte-identical to the round-16 snapshot (exit 0). The exact quoted lines are in `out/CriticLoadCells/source-lines.txt`.

| id | path:line | quote (25 words or fewer) |
|---|---|---|
| A | tools/server/server-context.cpp:4298-4301 | `if (n_batch == 1 && ret == 1) {` … `err = "Context size has been exceeded.";` |
| B | tools/server/server-context.cpp:4318-4320 | `for (auto & slot : slots) {` / `if (slot.is_processing()) {` / `send_error(slot, err);` |
| C | tools/server/server-context.cpp:4335-4336 | `if (!try_clear_idle_slots()) {` / `n_batch /= 2;` |
| D | tools/server/server-context.cpp:2170 | `send_error(const int id_task, const std::string & error, const enum error_type type = ERROR_TYPE_SERVER, …` |
| E | tools/server/server-common.cpp:107-109 | `case ERROR_TYPE_SERVER:` / `type_str = "server_error";` / `code = 500;` |
| F | tools/server/server-context.cpp:2027 | `if (!params_base.ctx_shift && slot.prompt.n_tokens() + 1 >= slot.n_ctx) {` |
| G | tools/server/server-context.cpp:3374 | `if (slot.state == SLOT_STATE_GENERATING && slot.prompt.n_tokens() + 1 >= slot.n_ctx) {` |
| H | common/common.h:578 | `bool ctx_shift         = false; // context shift on infinite text generation` |
| I | common/common.h:636-638 | `n_cache_reuse       = 0;` / `cache_prompt        = true;` / `cache_idle_slots    = true;  // save and clear idle slots upon starting a new task` |
| J | tools/server/server-context.cpp:3777-3779 | `// if we don't cache the prompt, we have to remove all previous tokens` / `n_past = 0;` |
| K | tools/server/server-context.cpp:2851-2854 | `if (slot == nullptr) {` … `SRV_DBG("no slot is available, defer task, id_task = %d\n", id_task);` |
| L | tools/server/server-context.cpp:1724, 1766-1773 | `if (slot.is_processing()) {` … `// find an empty slot, or the one that has been least recently used` |
| M | tools/server/server.cpp:169-173 | `if (params.n_parallel < 0) {` … `params.n_parallel = 4;` / `params.kv_unified = true;` |
| N | tools/server/server-http.cpp:152 | `pimpl->n_threads_http = std::max(params.n_parallel + 4, static_cast<int32_t>(std::thread::hardware_concurrency() - 1));` |
| O | tools/server/server-context.cpp:2893-2895 | `if (params_base.kv_unified) {` / `// [TAG_IDLE_SLOT_CLEAR]` / `slot.prompt_clear();` |
| P | tools/server/server-context.cpp:4655-4662 | `int n_ctx_slot() const {` … `return std::min(res, llama_model_n_ctx_train(model_tgt));` |
| Q | tools/server/server-context.cpp:4973, 5006 | `bool stream = json_value(data, "stream", false);` … `// in streaming mode, the first error must be treated as non-stream response` |
| R | tools/server/server-context.cpp:4957-4960 | `if (task.params.n_cmpl > 1) {` … `task.add_child(task.id, rd.get_new_id());` |
| S | src/llama-context.cpp:1940, 1952-1954 | `case LLAMA_MEMORY_STATUS_FAILED_PREPARE:` … `failed to find a memory slot for batch of size %d` … `return 1;` |
| T | src/llama-kv-cache.cpp:1037-1038, 1062 | `// for non-continuous slots, we test the tokens one by one` … `bool can_use = cells.is_empty(idx);` |
| U | common/common.h:458 | `int32_t n_batch               =  2048; // logical batch size for prompt processing` |
| V | tools/server/server-common.cpp:970-972 | `// If add_bos is true, we only add BOS, when json_prompt is a string, or the first element … is a string.` |

## Mechanism traced from source (the basis for each defect)

- The unified pool (L1, L3: `-c 0`, auto 4 slots, unified per M) holds 2048 cells, one per token, searched cell by cell (T). A batch that cannot find enough free cells returns 1 (S). The server first tries to clear idle slots, then halves the batch (C). At batch 1 it sends `Context size has been exceeded.` (A) to every slot that is processing (B). The default error type gives HTTP 500 `server_error` (D, E). No admission check compares the pool with the sum of requests. The only size checks are per slot (F, G and the 3676 prompt check against `slot.n_ctx`).
- Arithmetic [INFERENCE from source, then matched by observation]: both 1000-token prompts fit in one batch (2000 tokens, within `n_batch` 2048 per U) and in the 2048-cell pool. Each later step adds one cell per slot, so the pool fills after 24 decoded tokens each, and the 25th fails. Both slots fail together.
- Observed by sibling ExecLoadReplicate (`/fast/scratch/hyaku/kama-r25a2/ExecLoadReplicate/L1-rep1.log`, final lifetime): line 3708 `release: id  0 | task 1 | stop processing: n_tokens = 1025` and line 3722 `release: id  1 | task 2 | stop processing: n_tokens = 1025`. Every L1 repetition shows the same in both lifetimes (`out/CriticLoadCells/log-observations.txt`). Both requests got HTTP 500 with the exact text, in all 3 repetitions (`a2-build/out/ExecLoadReplicate/l-cells-receipt.json`).

## Defects in the L-cell design

### D1. The L1 prediction is weaker than the source and accepts the wrong mechanism (calibration, validity)

Amendment 2's L1 prediction is "at least one request ends with an error (`Context size has been exceeded` or equivalent)". The source predicts more than that: both requests fail (B), with HTTP 500 and `type` `server_error` (D, E), with that exact text (A), mid-generation, at slot `n_tokens = 1025`. The weak wording accepts outcomes that contradict the mechanism:

- one 200 response with 600 tokens plus one 500 (this contradicts B, which broadcasts the error to every processing slot);
- a 400 `exceed_context_size_error` (that is a per-slot admission check, server-context.cpp:3676-3681, not the pool);
- a 400 from invalid token ids (vocab is 512, `tokenizer.ggml.tokens len=512` in `build/out/CriticC2Sizing/gguf-kv.out`; ids outside 0-511 are rejected at server-common.cpp:887 and server-context.cpp:1917). L1, L2 and L3 would then all fail, and L1 alone would still "match".

What would expose it: any of those status or text patterns graded as a hit. Observed: 6 of 6 L1 requests returned 500 with the exact text, so the sharper prediction also holds.

Correction: grade L1 against "both requests 500 `server_error` with the exact text, both released at `n_tokens = 1025`". Keep the registered string as written, and record the sharper source-derived form as the graded prediction. An outcome of one success and one failure is a mechanism miss, not a hit.

### D2. Overlap is assumed, not recorded in the counted fields (validity)

count-c2.py lines 59-69 check only that `request_mode` equals "concurrent" (a label the client chooses) and that each request has an integer `status`, `prompt_tokens` 1000 and `n_predict` 600. On this fixture one request lives about 135-141 ms: L3-rep1.log line 1197 (launch at 0.270 s) to line 11428 (release at 0.411 s); receipt `elapsed_s` is 0.126-0.131. If the second request launches after the first one releases, the unified idle-slot clear (O) or reuse of the same slot frees the cells. L1 then behaves like L3: both 200. That result would be read as falsifying the claim when it only shows that the requests never overlapped. A busy host or a client that sends serially over one connection can easily open a 140 ms gap.

What would expose it: the server log line `launch_slot_ … processing task` for the second task appearing after the `release … stop processing` line of the first task. Observed: launches came 32 µs apart (L1-rep1.log:1213 and 1237) and 102 µs apart (lines 3091 and 3115), so overlap held. That evidence lives only in scratch logs. The receipt rows carry `elapsed_s` but no send times and no launch or release lines (`log-observations.txt`, last section).

Correction: for each request, record the client send and receive times on a monotonic clock. For each load cell, keep the two `processing task` lines and the two `stop processing` lines from the serving lifetime. The closure should require that the second launch precedes the first release before L1 is read either way.

### D3. The load cells vary two things at once, so L2 cannot attribute the failure to sharing (validity, coverage)

L1 uses a 2048 pool that is unified. L2 uses an 8192 pool split into four 2048 streams. Pool size and layout both change. Per the source, the failure condition is "cells used by all running requests exceed the pool" (S, T), and sharing as such plays no part. [INFERENCE, not run] A unified 8192 pool (`-c 8192 -np 4 --kv-unified`) would let both requests pass: 3200 cells fit, and the per-slot cap is `min(n_ctx_seq, n_ctx_train)` = 2048 (P).

The converse case has a cost. A split cache with small streams turns the same overload into per-request truncation that reports success. [INFERENCE, not run] With K2's shape (`-c 2048 -np 2 --no-kv-unified`, per-slot 1024), F stops each request when `n_tokens + 1 >= 1024`. The result is HTTP 200, `truncated` true, `stop_type` limit, about 24 tokens. A status-only record reads that as success.

What would expose it: an unregistered shared-8192 control in which both requests pass. That would show pool total, not sharing, causes L1's failure. A K2-shaped concurrent run returning 200 with `tokens_predicted` below 600 would show the split-layout failure mode.

Correction: word the knowledge entry as "a unified pool is one budget for the sum of every running request's prompt and decoded tokens. Overload fails all running requests with HTTP 500. A split cache bounds each request separately and truncates with HTTP 200." Optionally run those two controls as unregistered supporting cells. The registered count does not change.

### D4. "Full-context" is the wrong name. 1000 + 600 is not what fails, and the 600 only widens the overlap window (coverage, calibration)

At failure each request used 1025 of a 2048 per-slot context, which is 50%. Neither request was near full context, and n_predict 600 never came into play. The binding quantity is 2 × 1000 prompt cells + 2 × 24 decoded cells = 2048.

The sizing still has two good properties. The 1600 tokens per request stay below the per-slot 2048, so L3 can pass. The 600 tokens stretch each request's life to about 140 ms, which helps overlap (D2). So the cells are valid. The statement "shared pool limits concurrent full-context requests" is the part that is mislabeled.

Boundary falsifier [INFERENCE from source plus observation]: L3 shows `n_tokens = 1599` at release (L3-rep1.log:11428), so the last sampled token is never decoded. Each request therefore takes prompt + n_predict - 1 cells. Two concurrent 1000-token prompts should then pass with n_predict 25 (2 × 1024 = 2048) and fail with n_predict 26. If 25 fails, the "sum of cells must fit in the pool" law has an unmodelled reserve or padding. That would be knowledge, not a hidden miss.

Correction: rename the statement to "the sum of concurrent requests' tokens is bounded by the KV pool, not by per-slot n_ctx × slots". Record the 1025 failure point as observed. Optionally add the 25/26 boundary pair as unregistered supporting cells.

### D5. Counted fields cannot tell success from truncation or from an in-stream error (validity)

count-c2.py line 66 accepts any integer `status`. Two outcomes defeat a status-only read:

- Truncation: a 200 with `truncated` true and fewer than 600 tokens (D3).
- Streaming: per Q, only an error that arrives *before the first token* becomes the HTTP status. L1's error comes after 24 generated tokens, so [INFERENCE, not run] with `"stream": true` both L1 requests would report HTTP 200 and the error would travel inside the stream.

The sibling harness sent non-stream requests (`stream` default false, Q) and recorded `tokens_predicted` 600 for every 200. This defect is therefore latent, not realized. A different harness, or the capacity tool, could still trip it.

What would expose it: L1 rerun with `"stream": true` showing status 200 for both requests.

Correction: the receipt records `stream` false explicitly. Every 200 row carries `tokens_predicted` 600 and `truncated` false. Every 500 row carries `error.type` and `error.message`. The closure, or a stricter counter, requires these.

### D6. Log provenance: two server lifetimes per scratch log, and the counter accepts the fit-probe line (provenance)

- `a2-build/out/ExecLoadReplicate/load_replicate.py:94` contains `logf = open(logpath, "ab", buffering=0)`. All 9 scratch logs hold 2 lifetimes (`grep -c 'load_model: initializing'` gives 2 per file; `log-observations.txt`).
- The L1 excerpt quoted in `a2-build/advice/ExecLoadReplicate.md`, L1-rep1.log lines 1737-1840, comes from the *first* lifetime, the pre-fix pass. The committed rows come from the final pass, which starts at line 2960.
- The receipt's L1 `log_lines` begin with first-lifetime lines (timestamp 0.00.013.498).
- Each lifetime prints `llama_context: n_ctx` twice. The first print comes from the fit probe (line 284), before `common_fit_params: successfully fit` (line 549). The second is the serving context (line 816). count-c2.py lines 55-57 accept *any* matching line.

All L values agree across both passes and both prints, so no number changes here. The binding is still to "some line in some lifetime".

What would expose it: a cell where the fit probe and the serving context differ, or a first pass run with different arguments. Either would pass the counter with the wrong pool.

Correction: write each run's log fresh (open with "wb", or slice from the last `load_model: initializing`). Re-quote L1 lines from the final lifetime (for example L1-rep1.log:3704, 3708, 3722). Bind `kv_pool_n_ctx` to the last `llama_context: n_ctx` before `load_model: initializing` in the serving lifetime.

### D7. Request shape must stay one flat token array per HTTP request, with no n_cmpl (validity)

A request with `n_cmpl` above 1 (R), or a prompt given as an array of arrays (server-common.cpp:1118-1126), creates several tasks. They share prompt cells through child slots, which changes the cell count. The counter would still see "two request records". A flat integer array adds no BOS token (V), so `prompt_tokens` 1000 really means 1000 cells. Observed: the sibling sent flat arrays from `/tokenize`, and the log shows `task.n_tokens = 1000` (L1-rep1.log:1245, 1249).

Correction: record the request body shape in the receipt: a flat list, `n_cmpl` absent, `cache_prompt` false, `ignore_eos` true.

## Concerns checked and refuted (not defects)

- **Requests failing to overlap.** This is possible in principle (D2), but it did not happen in any of the 6 L1 runs. The second launch came 32-102 µs after the first, both prompts entered the same batch, and both failed.
- **Context shift hiding the limit.** It cannot. It is off by default (H). Even when enabled it acts only on the per-slot test `n_tokens + 1 >= slot.n_ctx` (G, F), which 1025 or 1600 against 2048 never reaches, and it never consults the pool. Observed: 0 `context shift` lines in all 9 logs, and every release line shows `truncated = 0`.
- **Cache reuse hiding the limit.** It cannot. With `cache_prompt` false, `n_past` is 0 (J). `n_cache_reuse` defaults to 0 (I). Separate slots are separate sequences, and identical prompts share no cells unless R applies. Observed: L2 and L3 timings show `cache_n` 0 and `prompt_n` 1000.
- **The server queueing the second request.** It does not. Auto mode gives 4 slots (M). A busy slot is skipped and the least recently used free slot is taken (L). Deferral happens only when no slot is free (K). The HTTP thread pool has at least n_parallel + 4 threads (N). Observed: L1-rep1.log:1225 `selected slot by LRU` for slot 1, and 0 `defer task` lines in all 9 logs.
- **L3 passing for the wrong reason.** It passes because the same slot drops its own cells. The second request is routed by prompt similarity to slot 0 (L3-rep1.log:11450, `f_sim_best = 1.000`, `f_keep = 0.625`), and with `cache_prompt` false it starts from `n_past` 0 (J). L3 therefore shows that the pool frees cells between sequential requests. It does not test freeing cells across slots, and the entry should not claim that.

## What would falsify "the pool limits concurrent requests"

Each outcome below assumes overlap was proven (D2):

1. L1: both requests 200 with 600 tokens each and `truncated` false. This falsifies the claim.
2. L1: one 200 with 600 tokens and one 500. This falsifies the collective-failure part (B).
3. L1: a 400 `exceed_context_size_error`. This shows an admission check exists, which is a different mechanism.
4. A unified 8192 control fails while L2 passes. This shows sharing itself, not pool size, is the limit. That contradicts S and T.
5. The n_predict 25/26 boundary does not split pass from fail. The cell arithmetic would then be wrong.
6. L3 fails. The failure would then be about request size, not concurrency.

The sibling runs observed none of 1, 2, 3 or 6 in 3 repetitions per cell. Outcomes 4 and 5 were not run (unverified).

## Smallest safe correction set (no claim-count change, no narrowing)

1. Grade L1 against the sharp source form (D1).
2. Add overlap evidence and per-request outcome fields to the load-cell receipt (D2, D5, D7).
3. Use one log per lifetime and bind the pool value to the serving context (D6).
4. Reword the knowledge statement to "sum of concurrent tokens is bounded by the pool; unified overload fails all running requests with 500; split overload truncates with 200", and drop "full-context" (D3, D4).
5. Optional unregistered supporting cells: a unified 8192 control, a K2-shaped concurrent run, and the n_predict 25/26 boundary pair.

The count-c2.py target `registered 14 observed 14 bound True` stands, and none of these changes it. They decide whether the L observations support the learning statement.

Defect or tradeoff: D1, D2, D5, D6 and D7 are fixable defects. D3 and D4 are wording defects that become false provenance if the entry keeps "shared" or "full-context" as the cause. None of them is a tradeoff the judge must reject.

## Files written

- `.ufo/waves/round-25/a2-build/advice/CriticLoadCells.md` (this report)
- `.ufo/waves/round-25/a2-build/out/CriticLoadCells/extract.sh` (regenerates the two files below; run exit 0)
- `.ufo/waves/round-25/a2-build/out/CriticLoadCells/source-lines.txt` (exact pinned source lines cited above)
- `.ufo/waves/round-25/a2-build/out/CriticLoadCells/log-observations.txt` (lifetime, context-shift, defer and error counts for the 9 sibling logs; launch, release and slot-choice lines; harness log mode; receipt request keys)
- `.ufo/waves/round-25/a2-build/out/CriticLoadCells/sources.sha256` (hashes of the 10 pinned raw files used)
- Scratch: `/fast/scratch/hyaku/kama-r25a2/CriticLoadCells/src/*` (raw pinned sources, GitHub tree listing)

No server started, no port used. Tools installed or updated: none.
