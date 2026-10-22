source: S106 (common/fit.cpp), S107 (src/llama-context.cpp), S108 (tools/server/server.cpp auto slots and pool sizing), S109 (tools/server/server-context.cpp full-cache decode path), S110 (common/arg.cpp context, fit and slot options), S111 (common/common.cpp fit call), S112 (tools/server/README.md), S113 (src/llama-kv-cache.cpp), S060 (served per-slot value), all at llama.cpp commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad (release b11755); live receipt `.ufo/waves/round-25/final/context-capacity-receipt.json`; corpus/lessons/round-25.md Gate
verified-at: 2026-10-22 — sources opened this round; 14 fixture cells observed 2026-10-22T09:42:42Z to 09:42:50Z (receipt commit 5c95c8f111a981e316cd4933e38fc363e51f8604) on the lane-owned fixture, torn down in the same run
recheck: on-release — reopen the pinned sources and re-run `python3 tools/kama-context-capacity.py --out <receipt>` when the installed llama.cpp build changes; a receipt is a dated sample, never present service state

# Declared versus served context capacity: pool, slot and concurrency

A GGUF header declares a training context (2048 for the lane fixture). At
build 11755 a llama-server has two capacity numbers: the **KV pool**
(`llama_context: n_ctx`, the whole cache) and the **per-slot ceiling**
(`n_ctx_slot`, the most one request may use). Its `/props`, `/slots` and
`/v1/models` endpoints report only the second. On this fixture two launches
(K1 and X2) report the same values there while their pools differ fourfold
(2048 and 8192); two concurrent 1600-token requests failed on the K1
configuration (L1) and passed on the X2 configuration (L2).

Cell ids below refer to the committed receipt. Each cell ran
`llama-server -m stories260K.gguf --host 127.0.0.1 --port <free> --no-webui
--offline -v <args>`; the values are observed, not predicted. The pool is the
last `llama_context: n_ctx = N` line of that cell's raw log.

## Two numbers: the KV pool and the per-slot ceiling

| cell | args | /props n_ctx (per slot) | total_slots | KV pool (log) | what the cell adds |
|---|---|---|---|---|---|
| K1 | `-c 0` | 2048 | 4 | 2048 (unified) | per-slot replicates the round-20 rule and the pilot |
| K2 | `-c 2048 -np 2 --no-kv-unified` | 1024 | 2 | 2048 | per-slot replicates round 20 and the pilot |
| K3 | `-c 2048 -np 2 --kv-unified` | 2048 | 2 | 2048 | per-slot replicates round 20 and the pilot |
| K4 | `-c 1024 -np 1` | 1024 | 1 | 1024 | replicates round 20 |
| K5 | `-c 4096 -np 1` | 2048 | 1 | 4096 | per-slot replicates; the pool value is new to the corpus |
| K6 | `-c 1000 -np 3 --no-kv-unified` | 512 | 3 | 1536 | measurement only; pool new to the corpus |
| K7 | `-np 2 --kv-unified-per-slot 512` | 512 | 2 | 1024 | per-slot replicates; pool new (the round-20 model implies 2048) |
| K8 | `-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512` | 512 | 4 | 4096 | per-slot replicates; pool new |
| X1 | `-np 4 --no-kv-unified` | 2048 | 4 | 8192 | contradicts the round-20 rule (512) |
| X2 | `-c 8192 -np 4 --no-kv-unified` | 2048 | 4 | 8192 | per-slot replicates; same endpoints as K1 with 4 times the pool |
| X3 | `-np 4 --no-kv-unified --fit off` | 512 | 4 | 2048 | per-slot replicates round 20; isolates fit as the X1 cause |

Matches with the round-20 rule are replication and calibration evidence, not
new knowledge. The K4-K8 predictions (preregistration) and the X and L
predictions (amendment 2) were written before the attempt-2 runs, but not
blind: X1 and X2 came from a critic who had seen attempt-1 cell values, and
the prediction credit for K4, K5, K7 and K8 was withdrawn because the author
had read attempt-1 values (`.ufo/waves/round-25/errata-attempt-2.json`).
K1-K3 copied the pilot. The attempt-1 record (committed at
5388b7cf as a cancelled-attempt record) already held an edge cell E09
(`-np 2`, no `-c`) serving 2048 per slot, so X1 is the first admitted
statement of that behavior, not the first observation.

- `/props` `default_generation_settings.n_ctx`, every `/slots` `n_ctx` and
  `/v1/models` `meta.n_ctx` all read one function, `n_ctx_slot()`
  (server-context.cpp 1437, 5186, 5236; S060), so their agreement is expected
  and is not independent evidence. In each of the 14 cells the three raw
  bodies carry one value, and `/slots` has one entry per `total_slots`.
- The per-slot ceiling is the per-sequence context, capped by
  `--kv-unified-per-slot` and by the training context (S060). K5 shows the cap:
  the pool is 4096 (`-c 4096`), the served ceiling is 2048, and the only trace
  is a log warning `n_ctx_seq (4096) > n_ctx_train (2048)`.
- The context is padded to a multiple of 256; with a split cache the
  per-sequence context is the pool divided by the slot count, padded again,
  and the pool is then reset to per-sequence times slots (S107, lines 377-392).
  K6: `-c 1000` on 3 split slots serves 512 per slot from a 1536 pool, larger
  than the declared 1000. The log says "rounding down to 1536" while the
  value went up; quote the number, not the word.
- Leaving `-np` unset makes the server use 4 slots and a unified cache
  (S108, server.cpp 169-174). Giving `-np` keeps the default split cache
  (S110 declares the `-kvu` default "enabled if number of slots is auto").
  K4 and K7 give `-np` without a cache flag and log `kv_unified = 'false'`.
- `--kv-unified-per-slot N` without `-c` sizes the pool to slots times N even
  when the cache is split (S108, server.cpp 179-186; S112 is the only README
  sizing promise). K7: split cache, pool 1024, 512 per slot. The flag name
  suggests a unified cache; it does not require one.
- The KV cache keeps one stream per sequence when split and one when unified;
  its size log prints cells per stream (S113, llama-kv-cache.cpp 84, 144,
  301-304).

## Fit raises a zero split context to the training context per slot (corrects the round-20 rule for that case only)

With `--fit` on (the default; S110 declares the handler, the default value
itself is in `common/common.h`, which has no SOURCES row), the fit step runs
before the model loads for every launch (S111, common.cpp 1245-1276; K2 with
`-c 2048` also logs a fit pass). It raises the context only when the context
is still 0 at that point (no `-c`, or `-c 0`, and no `--kv-unified-per-slot`,
which sizes the context before fit runs; S108, server.cpp 179-186). Then it
sets the context to the training context times the number of streams: one
stream for a unified cache, one per slot for a split cache (S106, fit.cpp
195-198 and 266-273). K7 is the exception in this receipt: no `-c`, fit on
and a split cache, but `--kv-unified-per-slot 512` sizes the pool to 1024 and
fit leaves it there.

- X1 (`-np 4 --no-kv-unified`, no `-c`): pool 8192, 2048 per slot. Its raw
  log (`final/raw/X1.server.log`) shows the fit probe first (`n_ctx = 2048`,
  line 283), the fit step's own re-measure at 8192 (line 812, inside the fit
  pass [INFERENCE from log order]) and the serving context `n_ctx = 8192`
  (line 1344) before `load_model: initializing` (line 1610).
- X3 (the same with `--fit off`): pool 2048, 512 per slot. With fit off the
  unset context falls back to the training context and is split (S107,
  line 219). The pair X1/X3 isolates fit as the cause.
- **Supersession, for this one case.** The incomplete rule is in round-20 wave
  evidence, not in an admitted entry: `.ufo/waves/round-20/build/advice/SrcServerNctx.md`
  line 6 and `.ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py`
  `predict()` (line 41), which returns 512 for X1 because it splits the bare
  training context and models fit only as something that can lower a
  context. For build 11755 on this fixture, with no `-c`, no
  `--kv-unified-per-slot`, fit on and a split cache, the observed per-slot
  value is the training context (2048), not 512 (X1). Under `--fit off` (X3)
  and with `--kv-unified-per-slot` (K7) the round-20 per-slot value holds.
  `-c 0` with a split cache was not run; the source predicts the X1 value
  [INFERENCE]. On the other ten registered config cells round 20's per-slot
  value agrees with the observation; round 20 models no pool, and the pool it
  implies for K7 (2048) differs from the observed 1024.
  The admitted `corpus/knowledge/gguf-declared-identity.md`
  ("do not divide blindly") is not wrong; it now points here for the rule.
  `tools/kama-context-capacity.py` does not re-implement a formula: it
  observes, and records the pool from the log.
- An explicit `-c 0` is not the same as omitting `-c`: `-c 0` disables fit's
  context reduction (S110, arg.cpp 1646-1649). On this fixture fit never
  reduces anything, so the difference does not show here.

## On a shared pool, concurrent requests can run out of cells below the per-slot ceiling

The per-slot number limits one request. It does not promise that capacity to
several requests at once. The L cells sent two `/completion` requests, each a
1000-token prompt as one flat list of token ids, with `n_predict` 600,
`ignore_eos` true, `cache_prompt` false and no streaming:

| cell | args | mode (recorded request times) | result |
|---|---|---|---|
| L1 | `-c 0` (one 2048 pool, 4 slots) | concurrent, start gap 0.1 ms, both open together | both HTTP 500, `server_error`, `Context size has been exceeded.` |
| L2 | `-c 8192 -np 4 --no-kv-unified` | concurrent | both HTTP 200, 600 tokens each, not truncated |
| L3 | `-c 0` | one after the other | both HTTP 200, 600 tokens each, not truncated |

- Order of events (S109, server-context.cpp 4294-4341 and 1810-1835): when
  decoding finds no free KV space the server first tries to purge idle slots
  that still hold a cached prompt; if none is purged it halves the batch and
  retries; when a batch of one still fails it sends `Context size has been
  exceeded.` to every
  processing slot, clears them and stops. In L1 both slots were released at
  `n_tokens = 1025` (`final/raw/L1.server.log` lines 1849-1866): 2 × 1025
  cells overflow the 2048 pool. Both admitted requests failed, not only the
  newer one. The replicate seat
  (`.ufo/waves/round-25/a2-build/advice/ExecLoadReplicate.md`) saw the same
  outcome in 3 of 3 fresh-server runs per L cell.
- On a shared pool the cells ran out before either request reached its
  per-slot ceiling: each L1 request failed at 1025 tokens, about half of its
  2048 ceiling, when 2 × 1025 exceeded the 2048 pool. Both requests were the
  same size, so L1 does not separate a limit on the summed cells from an
  equal share per request; the source supports the summed reading (S113: a
  unified cache keeps all sequences in one stream), untested with unequal
  requests. Each request is still capped by its per-slot ceiling. On a split
  cache each request is held to its own stream [INFERENCE from S113; not run
  under load]. L1 and L2 report the same endpoints (per slot 2048, 4 slots);
  L2's pool is four times larger, but L2 also changes the cache layout.
- Supporting cells from the falsify wave, not part of the claim count (same
  request pair, `-c 0` or `--kv-unified`, 4 slots):
  - Shared pool 8192 (`-c 8192 -np 4 --kv-unified`): both HTTP 200 in 3 of 3
    runs, as L2. So the layout is not the cause.
  - Shared pools of 2048 and 3072 fail (both HTTP 500, released at 1025 and
    1537 tokens each); 4096 passes (one run each). With every endpoint value
    held equal, only the pool total flips the outcome.
  - Boundary on the 2048 pool: with `n_predict` 25 both requests pass in 2
    of 2 runs (1024 tokens each, the pool exactly full); with 26 both fail
    in 3 of 3. The 1025th token of each request is the first the pool cannot
    hold.
  - Shared pool 8192 with `--kv-unified-per-slot 512`: both requests are
    rejected up front with HTTP 400 `exceed_context_size_error` (1000 tokens
    exceed 512), so the smaller per-slot ceiling applies first.
  Evidence: `.ufo/waves/round-25/a2-falsify/advice/ExecSharedPool8192.md`
  and `ExecBoundaryPool.md`, with raw logs under their `out/` folders.
- L3 shows the L1 failure needs overlap: the same requests one after the
  other succeed. It covers only `cache_prompt` false (the server default is
  true) and says nothing about freeing cells across slots.
- Tested: two requests with 1000-token prompts, `cache_prompt` false, no
  streaming. No claim is made for other request counts or prompt sizes.

## What the three endpoints cannot show

- No field of `/props`, `/slots` or `/v1/models` carries the KV pool or the
  cache layout at these flags (S112 documents none; S060 lists the fields).
  K1 and X2 return the same capacity values (`n_ctx`, `total_slots`, slot
  entries) on all three; they differ only in fields that change per launch
  (`media_marker`, `created`). `/metrics` was not read.
- The startup line `load_model: initializing, n_slots = …, n_ctx_slot = …,
  kv_unified = '…'` shows the layout at default verbosity. The pool info line
  (`llama_context: n_ctx = N`) needs `-lv 4` or `-v`. At default verbosity a
  pool value appears only in some launches: in warnings such as K6's
  "rounding down to 1536" or K5's `n_ctx_seq (4096) > n_ctx_train`, and in
  K7's info line `--kv-unified-per-slot: sizing KV pool to … = 1024`. A wave
  seat compared
  plain and `-v` launches for K1, K6 and X1 and found no served value changed
  (`.ufo/waves/round-25/a2-build/advice/ExecVerbosityControl.md`).
- So a consumer that reads only these endpoints cannot know how many
  concurrent requests of a given size will fit. Ask for the verbose startup
  log (`llama_context: n_ctx` and `kv_unified`). Launch flags are a weaker
  substitute: every option involved can also come from an environment
  variable (`LLAMA_ARG_CTX_SIZE`, `LLAMA_ARG_N_PARALLEL`,
  `LLAMA_ARG_KV_UNIFIED`, `LLAMA_ARG_KV_UNIFIED_PER_SLOT`, `LLAMA_ARG_FIT`,
  `LLAMA_ARG_FIT_CTX`; S110), and where fit can lower the context the result
  also depends on free memory at launch.

## Scope

Read only at build 11755 (commit 704366d76); whether other builds treat
`--kv-unified-per-slot`, the auto slot default and the fit step the same is
unknown. Fixture `stories260K.gguf`,
sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`,
architecture llama, training context 2048, no sliding-window and no
rope-scaling keys, CPU only, single-model mode, unregistered loopback ports,
one child at a time. Fit never lowers a context here: it lowers a context of
0 only when projected memory misses its target and the training context is
above `--fit-ctx` (4096 by default) (S106, fit.cpp 384 and 393-394), and
neither holds for this fixture. On large models with a split cache fit first
raises a context of 0 to training context × slots and then, if memory is
short, lowers it toward `--fit-ctx` per stream; with a unified cache it can
only lower. Free memory at launch decides, so these fixture values do not
transfer.

## Does not establish

- Served context or concurrency on the registered consumers or on large
  models; no consumer port was probed.
- What fit does on a model whose cache does not fit (it can then lower an
  unset context, with a floor of `--fit-ctx` per stream, S106 426-430).
- Behavior when the training context is re-adjusted at load (YaRN; S107
  4113-4117); the fixture has no scaling keys.
- Other builds, other engines, router mode, context shift or prompt caching
  (the L cells disabled prompt caching and did not test context shift).
- Present service state: the receipt is a dated sample of torn-down children.
- A split cache under concurrent load with small per-slot streams, unequal
  concurrent requests on a shared pool, and the `-c 0` split case: none was
  run.
- Launches where fit stops before resolving the context, for example
  `-sm tensor` (fit.cpp 183-184) [INFERENCE, not run].

## Related lane evidence

The sibling lane kengaku committed captures of the production 34113 server
(another build, b1-d7bd3bf): launch flags `--ctx-size 16384 --fit off
--kv-unified --parallel 2`, `/slots` showing 2 × 16384 (kengaku
`corpus/evidence/round10-fleet/r10-scout-endpoint.md`, lines 33 and 67, read
by `.ufo/waves/round-25/a2-build/advice/ConnectorSiblingOverlap.md`). That is a
per-slot ceiling of 16384 on, read with b11755 semantics, one shared
16384-cell pool, the L1 shape [INFERENCE: no pool log exists for that build]. It is
historical, other-build evidence, not a kama observation. The X1 supersession
does not apply to it: `-c` is explicit, fit is off and the cache is unified.
