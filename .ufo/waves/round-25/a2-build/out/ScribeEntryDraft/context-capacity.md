source: llama.cpp commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad (= release b11755), files fetched fresh on 2026-10-22: `src/llama-context.cpp` (sha256 2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5), `common/fit.cpp` (1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58), `common/common.h` (8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9), `common/arg.cpp` (bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d), `tools/server/server.cpp` (2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4), `tools/server/server-context.cpp` (dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329). SOURCES rows for these files are opened at admission (KQ31; no committed row currently cites `src/llama-context.cpp` or `common/fit.cpp`). Observation source: the committed receipt `.ufo/waves/round-25/final/context-capacity-receipt.json` (expected; counted by the registered `count-c2.py`)
verified-at: 2026-10-22 — source reads and fixture metadata as dated; live cell observations are **pending** the committed receipt, so observed values below are the preregistered predictions, each marked `pending cell <id>`, filled by the L1 from the receipt
recheck: on-release — reopen the pinned sources and re-run a gated receipt when the installed llama.cpp build changes; the receipt is a dated sample, never present service state

# Declared versus served context capacity: pool, slot, and concurrency

The GGUF header declares a training context of 2048 for the fixture. What a
llama-server actually serves is described by two numbers that the HTTP APIs
almost never tell apart: the **KV pool** (`n_ctx`, the whole cache) and the
**per-slot ceiling** (`n_ctx_slot`, the most one request can use). A server
can advertise one value and serve a very different concurrency.

## Two numbers: the KV pool and the per-slot ceiling

- The context is a single `n_ctx` value, padded to a multiple of 256
  (`src/llama-context.cpp:377`). If the KV cache is unified, the per-sequence
  context equals the pool (`llama-context.cpp:379-380`); if it is split, the
  per-sequence context is `GGML_PAD(n_ctx / n_seq_max, 256)` (`llama-context.cpp:382-383`).
- When the split contexts do not add up to the padded pool, the pool is raised
  to the per-sequence context times the number of sequences
  (`llama-context.cpp:389-391`). The warning text says "rounding down to %u"
  (`llama-context.cpp:391`) even when the value rises: e.g. a requested
  1000-token context on 3 split sequences becomes a 1536-token pool
  (predicted `pending cell K6`: pool 1536, per-slot 512; measurement only, no
  preregistered prediction). Quote the number, not the word "down".
- The served per-slot ceiling is
  `min(llama_n_ctx_seq, --kv-unified-per-slot if > 0, n_ctx_train)`
  (`tools/server/server-context.cpp:4654-4663`). "Training context" here is the
  value after load-time adjustment, not necessarily the GGUF header
  (`llama-context.cpp:4113-4117`, YaRN re-adjustment; see scope).
- The pool is resolved before serving, in this order (`tools/server/server.cpp:169-186`):
  1. If `-np` is unset (auto), the server forces 4 slots and unified KV
     (`server.cpp:169-174`). If `-np` is given, the default cache is split:
     `kv_unified = false` (`common/common.h:580`).
  2. If `--kv-unified-per-slot N` is set, `-c` is unset/0, and fit reduction is
     not disabled, the pool is sized to `n_parallel * N` before anything else
     (`server.cpp:179-186`). This happens even when the cache is split, so the
     flag's name overstates its effect: K7 (split, `--kv-unified-per-slot 512`)
     predicts pool 1024, per-slot 512 (`pending cell K7`).
  3. Otherwise the pool comes from `-c`, or from fit when `-c` is unset (next
     section), or from the training context by default (`llama-context.cpp:219`).
- Each served surface reports the same per-slot value (`n_ctx_slot()`), so
  their agreement is expected, not independent evidence: `/slots` `n_ctx`
  (`server-context.cpp:1437`), `/v1/models` `meta.n_ctx`
  (`server-context.cpp:5186`) and `/props` `default_generation_settings.n_ctx`
  (`server-context.cpp:5236`) all read `slot_n_ctx = n_ctx_slot()`
  (`server-context.cpp:4829`). `/props` `total_slots` is `params.n_parallel`
  (`server-context.cpp:5244`); `/v1/models` `meta.n_ctx_train` is separate
  (`server-context.cpp:5187`).

## Fit raises an unset context before anything else measures it

When `-c` is unset (0), the fit step runs before context creation and can
*raise* the context, as well as lower it:

- `n_streams = kv_unified ? 1 : max(1, n_seq_max)` and `n_ctx_auto = (n_ctx == 0)`
  (`common/fit.cpp:195-198`).
- With `n_ctx == 0`, `cparams->n_ctx` is set to `n_ctx_train * n_streams`
  before memory is measured (`common/fit.cpp:266-273`): "llama_context would
  use only hp_nct in total for n_ctx == 0, resolve the context before measuring
  anything else".
- So a split cache with an unset context grows the pool by the number of
  streams, and each slot still gets the full training context. Prediction:
  `pending cell X1` (`-np 4 --no-kv-unified`) pool 8192, per-slot 2048.
- With `--fit off`, no raising happens: the unset context falls back to the
  training context (`llama-context.cpp:219`) and is split: `pending cell X3`
  pool 2048, per-slot 512. If X1 serves 2048 and X3 serves 512, fit is the
  cause (author inference from the same source; unverified).
- **Supersession.** The round-20 formula tool `nctx-crosscheck.py` computes
  per-slot 512 for X1 (its `predict()` treats an unset context as the bare
  training context and splits it: `nctx-crosscheck.py:38-44`). That row is
  wrong for this build for the unset-split case; its docstring excludes only
  "--fit run lowered n_ctx", not fit raising an unset context
  (`nctx-crosscheck.py:13`). The X1 cell is the control that must disagree
  with the round-20 value and agree with the fit source.

## Full-context concurrency is limited by the pool, not by the per-slot number

A per-slot `n_ctx` limits one request; it does not promise that capacity for
concurrent requests. With a unified cache, all slots share one pool:

- When a request cannot find space in the KV cache, the server sets
  `err = "Context size has been exceeded."` (`server-context.cpp:4301`) and
  sends that error to **every slot that is processing**
  (`server-context.cpp:4318-4320`), then retries with a halved batch
  (`server-context.cpp:4334-4339`). A full shared pool fails the running
  requests, not just the newest one.
- Two identical-looking launches differ fourfold in full-context concurrency:
  K1 (`-c 0`, auto: one 2048-token pool shared by 4 slots) and X2
  (`-c 8192 -np 4 --no-kv-unified`: each slot its own 2048-token stream) both
  predict `/props` `n_ctx` 2048, `total_slots` 4, four `/slots` entries of
  2048 and `n_ctx_train` 2048 (`pending cell K1`, `pending cell X2`).
- Load cells (two concurrent POST `/completion` requests, each a 1000-token
  prompt given as token ids, `n_predict 600`, `ignore_eos true`,
  `cache_prompt false`): prediction for `pending cell L1` (`-c 0`, shared pool;
  2 × 1600 cells exceed 2048, so at least one request ends with an error
  (`Context size has been exceeded` or equivalent); `pending cell L2`
  (`-c 8192 -np 4 --no-kv-unified`) both complete with HTTP 200; `pending cell
  L3` (`-c 0`, same two requests sent one after the other) both complete with
  HTTP 200, so the L1 failure is concurrency, not request size.

## What the HTTP surfaces cannot show

- No HTTP field exposes the KV pool size or the cache layout. `/props` has
  `default_generation_settings.n_ctx` and `total_slots`
  (`server-context.cpp:5236,5244`); `/slots` has per-slot `n_ctx`
  (`server-context.cpp:1437`); `/v1/models` has `meta.n_ctx` and
  `meta.n_ctx_train` (`server-context.cpp:5186-5187`). None of them is the
  pool.
- The startup log names the layout (`kv_unified = 'true'`,
  `server-context.cpp:1392-1393`), but the pool value (`llama_context: n_ctx`)
  appears only at full verbosity `-v`; at `-lv 3` it is absent
  (observed in the L1 planning walk, `.ufo/waves/round-25/preregistration-amendment-2.json`
  honesty note 11). Every registered cell therefore runs with `-v` and the
  receipt requires the pool line.
- A consumer reading the endpoints alone cannot tell K1 from X2, and cannot
  infer how many full-context requests can run at once. The declared
  per-slot `n_ctx` is a single-request ceiling.

## Scope

This entry is tied to: build 11755 = commit 704366d76 (one build,
`--kv-unified-per-slot` and the auto-slot default are build-specific); the
lane fixture `stories260K.gguf`, sha256
`270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`,
architecture `llama`, `llama.context_length` 2048 (`n_ctx_train` 2048), 5
blocks, 64 embedding dims, GGUF v3 (metadata read by `tools/gguf-identity.py`,
exit 0); the metadata carries no sliding-window key and no rope-scaling/YaRN
key, so the K5 cap is the plain training-context cap; CPU-only, single-model
mode, unregistered loopback ports, one child at a time. Fit never binds on
this fixture: context reduction runs only when projected free memory is below
margin (`common/fit.cpp:375-393`) and, for auto contexts, only when
`n_ctx_max > n_ctx_min_total` (`fit.cpp:393-394`); the fixture's KV cache is
about 640 bytes per token [INFERENCE: 5 layers × 4 KV heads × 8 head
dimensions × K and V × 2 bytes], so the projection always fits and `--fit`
cannot lower a context here. `-c 0` additionally disables fit reduction
(`common/arg.cpp:1646-1648`), which only matters on models whose cache does
not fit.

## Does not establish

- Served `n_ctx` or concurrency on the registered consumers or on large
  models (consumer ports were never probed; large models can hit the
  memory-dependent fit path that this fixture cannot show).
- That omitting `-c` equals `-c 0` under memory pressure: they differ exactly
  in whether fit reduction is disabled (`arg.cpp:1646-1648`), which only shows
  on models with a KV cache that does not fit.
- Other builds, other engines, router mode, sleep, or the README's
  documentation of these flags (code is cited where it differs).
- Any behavior when `n_ctx_train` is re-adjusted at load (YaRN, `llama-context.cpp:4113-4117`): the fixture has no scaling keys, so no `n_ctx_train` re-adjustment is exercised here. The K5 cap is plain training-context cap for this fixture; on scaled models it is the post-load value.
- That the receipt's counts describe present service state: a receipt is a
  dated sample of a torn-down fixture run.

## Cell prediction status

| cell | args | predicted pool / per-slot | status |
|---|---|---|---|
| K1 | `-c 0` | 2048 / 2048 (unified, auto 4 slots) | pilot-replicated |
| K2 | `-c 2048 -np 2 --no-kv-unified` | 2048 / 1024 | pilot-replicated |
| K3 | `-c 2048 -np 2 --kv-unified` | 2048 / 2048 | pilot-replicated |
| K4 | `-c 1024 -np 1` | 1024 / 1024 | predicted |
| K5 | `-c 4096 -np 1` | 4096 / 2048 | predicted |
| K6 | `-c 1000 -np 3 --no-kv-unified` | 1536 / 512 | measurement only (outside source-derived value) |
| K7 | `-np 2 --kv-unified-per-slot 512` | 1024 / 512 | predicted |
| K8 | `-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512` | 4096 / 512 | predicted |
| X1 | `-np 4 --no-kv-unified` | 8192 / 2048 | source-derived prediction (supersedes round-20 512) |
| X2 | `-c 8192 -np 4 --no-kv-unified` | 8192 / 2048 | source-derived prediction |
| X3 | `-np 4 --no-kv-unified --fit off` | 2048 / 512 | author inference, unverified |
| L1 | `-c 0` | shared 2048; ≥1 request error | source-derived prediction |
| L2 | `-c 8192 -np 4 --no-kv-unified` | both HTTP 200 | source-derived prediction |
| L3 | `-c 0` (sequential) | both HTTP 200 | source-derived prediction |

Prediction matches are calibration evidence, not the claim value; the claim
value is the observed count from the committed receipt (`registered 14
observed 14 bound True`). K1-K3 reproduce the pilot's observed rows
(`pilot.md:12-16`); K6 carries no preregistered prediction.
