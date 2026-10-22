# C2 knowledge entry accuracy — sentence table

Seat: KamaR25a2.ReviewerEntryClaims (wave 2, falsify), 2026-10-22.
Target: `corpus/knowledge/context-capacity.md` at fa3b62ae6475d111eb466d79af616aeebb08bbb9 (lane tip at dispatch). Line numbers below are that blob's lines. I audited the tip blob, not the working copy; the working copy has already diverged (diff recorded in the advice report) and fixes most findings.

Method: every factual sentence checked against (a) the committed receipt `.ufo/waves/round-25/final/context-capacity-receipt.json` (5c95c8f, verified ancestor of fa3b62ae; worktree bytes identical), (b) the 70 raw files under `final/raw/` (all 70 sha256 values re-computed and matched to the receipt), (c) fresh fetches of the pinned llama.cpp sources at 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad (fetched 2026-10-22 into `/fast/scratch/hyaku/kama-r25a2w2/ReviewerEntryClaims/src/`, 9 files, 26730 lines), and (d) the lane/sibling files the entry cites. `count-c2.py` executed on committed bytes over the committed receipt: `registered 14 observed 14 bound True missing []`, exit 0.

Abbreviations: R = receipt; `raw/<C>.server.log` etc. under `.ufo/waves/round-25/final/raw/`; SRC = my scratch fetch of the pinned source file (line numbers = pinned file lines).

## Header (lines 1-17)

| Line(s) | Sentence (condensed) | Verdict | Evidence |
|---|---|---|---|
| 1 | Sources S106-S113 + S060, all pinned to 704366d76 (b11755) | supported | SOURCES.md rows 118-125 and row 72 (S060), all URLs pinned to 704366d76; S060 used-by includes this entry; lesson round-25 Gate table opened 2026-10-22 |
| 2 | 14 cells observed 2026-10-22T09:36:51Z to 09:36:59Z, torn down in same run | **wrong (timestamps)** — F1 | R started_utc 09:42:42.438Z, ended_utc 09:42:50.502Z; per-cell min started 09:42:42.481Z, max stopped 09:42:50.463Z. 09:36:51-09:36:59 matches the superseded first receipt (5ea4fc44) per amendment-3/4 chronology, not the committed receipt the entry names. Teardown part is supported: all 14 teardown.port_closed true, child_returncode 0. Worktree line 2 fixes |
| 2 | sources opened this round | supported | SOURCES.md S106-S113 `opened` cells = 2026-10-22 |
| 3 | recheck policy | policy, not a factual claim | consistent with tool docstring (dated sample) |
| 7 | GGUF declares training context 2048 | supported | raw/K1.server.log:57 `print_info: n_ctx_train = 2048`; models meta n_ctx_train 2048 in all 14 bodies |
| 7-12 | server serves two numbers (KV pool, per-slot ceiling); endpoints do not tell them apart | supported (wording loose — endpoints report only the per-slot number; pool only in the log) | bodies show only slot values; pool appears only in log lines; worktree rewords |
| 10-12 | two launches report identical endpoints, pools differ fourfold | supported | K1 vs X2 capacity values identical (see line 136 row); pools 2048 vs 8192 (R kv_pool_n_ctx) |
| 14-16 | each cell ran llama-server … --host 127.0.0.1 --port <free> --no-webui --offline -v <args>; observed not predicted | supported | R argv per cell, e.g. K1 argv exactly that form with port 47400; ports 47400-47419 |
| 17 | pool = last `llama_context: n_ctx = N` line of the raw log | supported | count-c2.py POOL last-match rule (`pools[-1] == kv_pool_n_ctx`); X1 log has 2048 (line 283) then 8192 (812, 1344); R X1 pool 8192 |

## Cell table (lines 21-33)

| Line | Cell | Verdict | Evidence |
|---|---|---|---|
| 23 | K1 `-c 0`: 2048 per slot, 4 slots, pool 2048 unified | supported | R: props 2048, slots [2048×4], pool 2048; K1 log `kv_unified = 'true'` |
| 24 | K2: 1024, 2, pool 2048 | supported | R; K2 log `n_ctx = 2048`, `n_ctx_seq = 1024`, `kv_unified = 'false'`, size line "1024 cells, 2/2 seqs" |
| 25 | K3: 2048, 2, pool 2048 | supported | R |
| 26 | K4: 1024, 1, pool 1024 | supported | R |
| 27 | K5: 2048, 1, pool 4096 | supported | R; K5.server.log:283 (n_ctx = 4096), :295 warning |
| 28 | K6: 512, 3, pool 1536, measurement only | supported | R; K6.server.log:282 warning "rounding down to 1536", :284 n_ctx = 1536, :285 n_ctx_seq = 512; amendment-1: K6 carries no prediction |
| 29 | K7: 512, 2, pool 1024; round-20 model implies 2048 | supported | R; K7 log `kv_unified = 'false'`, sizing line "…= 2 * 512 = 1024"; round-20 pad256(n_ctx_train) = 2048 |
| 30 | K8: 512, 4, pool 4096 | supported | R |
| 31 | X1: 2048, 4, pool 8192; contradicts round-20 (512) | supported | R; predict() traced: pad256(2048)/4 → 512 |
| 32 | X2: 2048, 4, pool 8192; same endpoints as K1 with 4× pool | supported | R; body comparison below (line 136 row) |
| 33 | X3: 512, 4, pool 2048; replicates round 20; isolates fit | supported | R; predict() for X3 = 512 (fit not modeled) |

## Provenance paragraph (lines 35-41)

| Line(s) | Sentence (condensed) | Verdict | Evidence |
|---|---|---|---|
| 35-36 | round-20 matches are replication/calibration evidence, not new knowledge | framing, consistent with preregistration prediction_grading | preregistration C2 prediction_grading |
| 36-38 | K4-K8 predictions (preregistration) and X/L predictions (amendment 2) "written from source before the attempt-2 runs"; K1-K3 copied the pilot | **unsupported in part / misleading** — F6 | K1-K3 pilot: supported (amendment-1 correction 2). But K6 carries no prediction (preregistration K6 "unknown"; amendment-1), X1/X2 predictions came from a critic who had seen attempt-1 cell values, and errata-attempt-2 withdraws prediction credit for K4/K5/K7/K8 because the author had read attempt-1 values. "Before the attempt-2 runs" alone is true. Worktree lines 39-43 fix |
| 38-41 | attempt-1 record at 5388b7cf held E09 (`-np 2`, no `-c`) serving 2048 per slot; X1 first admitted statement, not first observation | supported | `git show 5388b7cf:.ufo/waves/round-25/build/out/ExecEdgeCells/raw/E09-np2-noc/record.json`: argv `-np 2` (no `-c`), slots_n_ctx [2048,2048], models meta n_ctx 2048; X1 is the only registered cell of that shape |

## Endpoint bullets (lines 43-67)

| Line(s) | Sentence (condensed) | Verdict | Evidence |
|---|---|---|---|
| 43-45 | /props default_generation_settings.n_ctx, every /slots n_ctx and /v1/models meta.n_ctx all read n_ctx_slot() (server-context.cpp 1437, 5186, 5236; S060) | supported | SRC tools_server_server-context.cpp:1437 `slot.n_ctx = n_ctx_slot();`, :4829 `slot_n_ctx = impl->n_ctx_slot()` (meta source), :5186 models meta `{"n_ctx", meta.slot_n_ctx}`, :5236 props `{"n_ctx", meta.slot_n_ctx}`; n_ctx_slot() def at :4655 |
| 46-47 | in all 14 cells the three raw bodies carry one value; /slots one entry per total_slots | supported | per-cell jq over all 28 body files: props single value; slots arrays equal-valued, length = total_slots (also enforced by count-c2.py); models `data` has exactly 1 entry (K1 checked) with meta.n_ctx = props value in all 14 |
| 48-49 | per-slot ceiling = per-sequence context capped by --kv-unified-per-slot and training context (S060) | supported | SRC server-context.cpp:4654-4663 (min of n_ctx_seq, per_slot, n_ctx_train) |
| 49-51 | K5: pool 4096, ceiling 2048, "the only trace is a log warning n_ctx_seq (4096) > n_ctx_train (2048)" | **imprecise** — F5 | warning verified at raw/K5.server.log:295; but the cell's own -v log also prints the pool at K5.server.log:283 (`n_ctx = 4096`), so "only trace" holds only at default verbosity — and even at default verbosity K7's info line prints a pool value (see line 139-141 row). Worktree keeps this bullet's wording |
| 52-54 | padding to 256; split: per-seq = pool/slots padded again; pool reset to per-seq × slots (S107 377-392) | supported | SRC src_llama-context.cpp:377 GGML_PAD(n_ctx,256); :380-383 split division + pad; :389-392 pool reset + warning |
| 55-57 | K6: -c 1000, 3 split slots → 512 per slot, 1536 pool, larger than declared; log says "rounding down to 1536" while value went up | supported | raw/K6.server.log:282,284,285 exactly |
| 58-59 | -np unset → 4 slots and unified (S108, server.cpp 169-174) | supported | SRC tools_server_server.cpp:170-173 (SRV_TRC + n_parallel = 4; kv_unified = true); K1 log `kv_unified = 'true'` |
| 59-60 | giving -np keeps default split (S110; common.h 580) | supported | SRC common_common.h:580 `bool kv_unified = false;` (README words the -kvu default "enabled if number of slots is auto"); K2/K4/K7 logs `kv_unified = 'false'` |
| 61-63 | --kv-unified-per-slot N without -c sizes pool to slots × N even when split (S108 179-186; S112 only README sizing promise) | supported | SRC server.cpp:179-186 predicate + `params.n_ctx = n_parallel * kv_unified_per_slot` (no kv_unified condition); README grep "pool\|sized": only line 165 promises sizing; K7 split pool 1024 |
| 63-64 | flag name suggests unified cache; does not require one | supported | K7 log `kv_unified = 'false'` with the sizing applied |
| 65-67 | KV cache one stream per sequence when split, one when unified; size log prints cells per stream (S113 84, 144, 301-304) | supported | SRC src_llama-kv-cache.cpp:84 `n_stream(unified ? 1 : n_seq_max)`; :144 `v_cells[s].resize(kv_size)`; :301-304 log prints kv_size as "cells"; K2 log "1024 cells, 2/2 seqs" (per stream), K1 "2048 cells, 4/1 seqs" |

## Fit section (lines 69-97)

| Line(s) | Sentence (condensed) | Verdict | Evidence |
|---|---|---|---|
| 71-74 | "When `-c` is unset and `--fit` is on (the default), the fit step … sets the context to the training context times the number of streams" | **wrong as stated** — F2 | Unconditional; K7 in the same table (line 29, `-c` unset, fit on, split) has pool 1024, not 2048×2: SRC server.cpp:179-186 sizes n_ctx = 1024 before fit (K7 log sizing line), so fit's `n_ctx_auto` (SRC common_fit.cpp:198 `n_ctx_auto = cparams->n_ctx == 0`) never fires. True only when the context is still 0 at fit time (X1, K1). Worktree lines 77-87 fix ("raises the context only when the context is still 0 … K7 is the exception") |
| 71-72 | fit runs before the model loads (S111, common.cpp 1245-1276) | supported | SRC common_common.cpp:1245 `if (params.fit_params) {`, :1270-1276 common_fit_params call, :1279 llama_model_load_from_file after |
| 72-74 | context = training context × streams; one stream unified, one per slot split (S106 195-198, 266-273) | supported (for the still-zero case) | SRC common_fit.cpp:197 `n_streams = kv_unified ? 1 : max(1, n_seq_max)`; :266-267 n_ctx_max = min(hp_nct × n_streams, UINT32_MAX); :270-272 assignment under n_ctx_auto |
| 76-79 | X1 raw log: fit probe n_ctx = 2048 (line 283), serving context 8192 (lines 812 and 1344), before `load_model: initializing` (line 1610) | supported | raw/X1.server.log: 283 = `n_ctx = 2048`; 812 = `n_ctx = 8192`; 1344 = `n_ctx = 8192`; 1610 = `load_model: initializing, n_slots = 4, n_ctx_slot = 2048, kv_unified = 'false'` (all four line numbers exact) |
| 80-82 | X3: pool 2048, 512 per slot; fit off → unset context falls back to training context and is split (S107 line 219); isolates fit | supported | R X3 (512, 4, 2048); SRC src_llama-context.cpp:219 `n_ctx == 0 ? hparams.n_ctx_train : params.n_ctx` |
| 83-86 | incomplete rule lives in round-20 wave evidence: SrcServerNctx.md line 6 and nctx-crosscheck.py predict() (line 41), returning 512 for X1 | supported | raw read of SrcServerNctx.md:6 (split-division rule); nctx-crosscheck.py:37-41 traced: n_ctx = pad256(2048), n_ctx_seq = pad256(2048/4) = 512, return min(512, 2048) = 512 |
| 88-89 | under `--fit off` (X3) the round-20 value holds | supported | predict() gives 512 = observed 512 |
| 90-91 | on the other ten registered config cells round 20 agrees with the observation | supported | predict() traced by hand for K1-K8, X2, X3 vs observed per-slot values (2048,1024,2048,1024,2048,512,512,512,2048,512) — all agree. Traced by hand, not executed against this receipt (script targets the round-18 receipt schema) |
| 91-92 | gguf-declared-identity.md ("do not divide blindly") not wrong; now points here | supported | corpus/knowledge/gguf-declared-identity.md:31-34 ("Do not divide `ctx` by `total_slots` blindly… Round 25: … `corpus/knowledge/context-capacity.md`") |
| 93-94 | the tool does not re-implement a formula: observes, records pool from the log | supported | tools/kama-context-capacity.py KV_POOL_RE extraction from log_lines; no sizing formula present |
| 95-97 | `-c 0` ≠ omitting `-c`: `-c 0` disables fit's context reduction (S110, arg.cpp 1646-1649); no visible difference on this fixture | supported | SRC common_arg.cpp:1647-1648 (value == 0 → `fit_params_min_ctx = UINT32_MAX`, comment "disable context reduction"); also SRC server.cpp:181 (sentinel skips -kvups sizing); no reduction observed in any cell |

## Load section (lines 99-130)

| Line(s) | Sentence (condensed) | Verdict | Evidence |
|---|---|---|---|
| 101-104 | L cells: two /completion requests, 1000-token prompt as flat token-id list, n_predict 600, ignore_eos true, cache_prompt false, no streaming | supported | tools/kama-context-capacity.py:443-448 (payload: n_predict 600, ignore_eos True, cache_prompt False, stream False); :488-507 /tokenize first 1000 ids; R L records prompt_tokens 1000, n_predict 600 |
| 108 | L1: concurrent, start gap 0.1 ms, both open together; both HTTP 500, `server_error`, `Context size has been exceeded.` | supported | R L1: statuses 500/500; error_type "server_error" both; error text exact both; t_start gap 6444.795245721−6444.795129594 = 0.000116 s ≈ 0.12 ms; intervals overlap |
| 109 | L2: both 200, 600 tokens each, not truncated | supported | R L2: 200/200, tokens_predicted 600, truncated false |
| 110 | L3: one after the other; both 200, 600 tokens, not truncated | supported | R L3: request_mode "sequential"; second t_start (6446.218968970) after first t_end (6446.218917841); 200/200/600/false |
| 112-114 | order of events: "the server first halves the batch and retries; when a batch of one still fails it sends `Context size has been exceeded.` to every processing slot, clears them and stops" (S109 4294-4341) | **incomplete** — F4 | SRC server-context.cpp:4334-4337: `if (!try_clear_idle_slots()) { n_batch /= 2; }` — the server first tries to purge idle cached slots (helper :1810-1835) and only halves when none was purged; the error fan-out/clear/stop at :4318-4330 is exact. No effect on L1 (fresh server, cache_prompt false, no idle cached prompts). Worktree lines 131-135 fix |
| 115-117 | both L1 slots released at n_tokens = 1025 (L1.server.log lines 1849-1866); 2 × 1025 overflows the 2048 pool; both admitted requests failed, not only the newer one | supported | raw/L1.server.log:1850 `send_error: task id = 2 … Context size has been exceeded.`, :1855 `release: id 0 … n_tokens = 1025`, :1863 `send_error: task id = 3 …`, :1865 `release: id 1 … n_tokens = 1025` (all within 1849-1866) |
| 118-120 | replicate seat saw the same outcome in 3 of 3 fresh-server runs per L cell | supported | .ufo/waves/round-25/a2-build/advice/ExecLoadReplicate.md table: L1 3× both 500; L2 3× both 200; L3 3× both 200 |
| 121-125 | "The limit is the pool total, not a full per-slot context"; L1 and L2 same endpoints; L2 pool 4× larger; L2 changes size and layout together; shared 8192 pool not run | supported as observation; the generalization is an inference stated as fact — F9 | Observed values supported (R). But at the tip the direct evidence is one equal-size request pair, and the entry itself notes L2 conflates pool size and layout; the "is the pool total" generalization goes beyond it. The worktree (lines 142-167) labels the inference and adds falsify-wave cells (shared 8192 unified, 2048/3072/4096 pools, n_predict boundary) that support it directly |
| 126-128 | L3 shows overlap needed; covers only cache_prompt false; server default is true | supported | SRC common_common.h:637 `cache_prompt = true`; SRC tools_server_README.md:596 "Default: `true`" |
| 129-130 | tested scope: two requests 1000 + 600 tokens, pool ratio 1:4 | supported | R pools 2048 vs 8192 |

## Endpoints/verbosity section (lines 132-146)

| Line(s) | Sentence (condensed) | Verdict | Evidence |
|---|---|---|---|
| 134-136 | no field of /props, /slots, /v1/models carries pool or layout at these flags (S112 documents none; S060 lists fields); K1 and X2 return identical values on all three; /metrics not read | supported (wording nit — F7) | byte-compare K1 vs X2: props differ only `media_marker`, models differ only `created` (both launch-volatile), /slots byte-identical; all capacity fields equal. "Identical values" is true for values, not bytes; worktree lines 178-180 reword precisely. Tool fetches only /health /props /slots /v1/models (docstring) — /metrics not read |
| 137-139 | startup `load_model: initializing, n_slots…, n_ctx_slot…, kv_unified…` shows layout at default verbosity; pool info line needs `-lv 4` or `-v` | supported | K2/K7 logs carry the line; ExecVerbosityControl.md: "first prints at `-lv 4` (trace)"; amendment-2 honesty note: absent at `-lv 3` |
| 139-141 | at default verbosity a pool value appears only in warnings such as K6's and K5's | **imprecise** — F5 (same finding) | K7's default-verbosity info line `--kv-unified-per-slot: sizing KV pool to … = 2 * 512 = 1024` also prints a pool value (K7 log line 1). Worktree lines 183-187 fix this sentence ("only in some launches … and in K7's info line") but keep the K5 bullet's "only trace" |
| 141-143 | a wave seat compared plain and -v for K1, K6, X1; no served value changed | supported | ExecVerbosityControl.md verdict + diff table (only media_marker/created differ; both volatile between plain runs too) |
| 144-146 | consumer advice: ask for launch flags or the verbose log | advice, consistent | follows from the above |

## Scope and does-not-establish (lines 148-174)

| Line(s) | Sentence (condensed) | Verdict | Evidence |
|---|---|---|---|
| 150-151 | build 11755 only; the three flags/auto default/fit step are build-specific | supported (bounded claim) | all SRC citations are at 704366d76; no other build tested |
| 151-154 | fixture sha256 270cba1b…256d; arch llama; train 2048; no sliding-window; no rope-scaling keys; CPU only; single-model; unregistered loopback ports; one child at a time | supported | R model_sha256 matches; raw/K1.server.log:54 `print_info: arch = llama`, :57 n_ctx_train = 2048, :66 `n_swa = 0`; no rope_scaling lines in the log and n_ctx_orig_yarn = 2048 (indirect — GGUF keys not re-parsed this session); :108-113 and :298 layers on device CPU; single `-m`; R port_range [47400,47419], port_refusal_set [8080,34113]; cells strictly sequential with teardown between |
| 155-157 | "Fit never lowers a context here: its reduction needs a training context above `--fit-ctx` (4096 by default) **or** a cache that does not fit in memory (S106, fit.cpp 393-394), and neither holds" | **wrong ("or" → "and"; line cite off)** — F3 | SRC common_fit.cpp: the reduction branch exists only inside `if (global_surplus < 0)` (line 384, memory short) **and** `if (n_ctx_max > n_ctx_min_total)` (line 393, train × streams > fit-ctx × streams, i.e. train > fit-ctx); the else at :397-403 logs "no change" when train ≤ fit-ctx even with memory pressure. Default 4096 verified (SRC common_common.h:485; README:91; SRC common_arg.cpp:2935-2936). "Neither holds for this fixture" is true. Worktree lines 207-214 fix ("only when projected memory misses its target and the training context is above --fit-ctx … (S106, fit.cpp 384 and 393-394)") |
| 158-159 | on large models free device memory decides; values do not transfer | supported (inference, correctly scoped) | follows from the fit.cpp branch structure |
| 163-164 | no consumer port probed | supported | R port_refusal_set [8080, 34113]; all ports in 47400-47419 |
| 165-166 | fit can lower an unset context when the cache does not fit, floor `--fit-ctx` per stream (S106 426-430) | supported | SRC common_fit.cpp:267-268 n_ctx_min_total = n_ctx_min × n_streams; :427-429 clamp `std::max(n_ctx − n_ctx % align, n_ctx_min_total)` |
| 167-168 | YaRN re-adjust untested (S107 4113-4117); fixture has no scaling keys | supported | SRC src_llama-context.cpp:4113-4117 re-adjust block; K1 log shows n_ctx_orig_yarn = 2048 |
| 169-170 | other builds/engines/router/context shift/prompt caching untested; L cells disabled prompt caching | supported | payload cache_prompt false; SRC common_common.h:578 `ctx_shift = false` default |
| 171 | receipt is a dated sample of torn-down children | supported | R teardown fields; all children reaped rc 0, ports closed |
| 172-174 | shared 8192 unified pool, split-cache concurrency, `-c 0` split: none run (at tip) | supported at tip | no such cells in R (the falsify wave has since run the first; worktree lines 227-231 move it into supporting cells) |

## Related lane evidence (lines 176-185)

| Line(s) | Sentence (condensed) | Verdict | Evidence |
|---|---|---|---|
| 178-182 | kengaku capture: build b1-d7bd3bf; flags `--ctx-size 16384 --fit off --kv-unified --parallel 2`; /slots 2 × 16384; r10-scout-endpoint.md lines 33 and 67 | supported | /home/vgpnk/Projects/shokunin/kengaku-shokunin/corpus/evidence/round10-fleet/r10-scout-endpoint.md:33 (full cmdline contains all four flags; `--version` → "build 1, commit d7bd3bf"), :67 ("unified KV ⇒ each slot reports the **full** 16384, not 16384/2"); curl outputs 2 slots × n_ctx 16384 |
| 183 | "a per-slot ceiling of 16384 on one shared 16384-cell pool, the L1 shape" | unlabeled inference — F8 | Applies b11755 sizing semantics to another build with no pool log; plausible and consistent with `--kv-unified --ctx-size 16384`, but it is the reviewer's/lane's inference, not a kengaku-recorded observation. Worktree line 240-241 labels it `[INFERENCE: no pool log exists for that build]` |
| 184-185 | X1 supersession does not apply: `-c` explicit, fit off, cache unified | supported | server.cpp:179-186 needs n_ctx == 0 for pre-sizing; fit.cpp:198 needs n_ctx == 0 for the raise; all three conditions hold in the kengaku argv |

## Totals

- **Wrong:** 3 sentences (F1 timestamps; F2 unconditional fit rule; F3 "or" vs "and" in fit reduction).
- **Incomplete/imprecise/misleading:** 5 (F4 decode order; F5 "only trace"/"only in warnings"; F6 prediction provenance; F7 "identical values"; F9 pool-total generalization) + 1 unlabeled inference (F8).
- **Supported:** every other factual sentence, including all 11 cell rows, all cited source lines and line numbers, all raw-log line references, the request records, and the fixture-scope facts.
- Claim value untouched: committed counter bytes over committed receipt → `registered 14 observed 14 bound True missing []`, exit 0; 70/70 raw-file sha256 match the receipt.
