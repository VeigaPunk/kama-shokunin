VERDICT: C2 as preregistered does not yet clear the learning bar. All eight cells' per-slot values are already predicted by the lane's own round-20 formula tool, so observing them only confirms what the lane already holds. Smallest safe fix: the new entry and tool must add the pool-versus-slot relation, the memory-fit step for an unset context, and the fact that the HTTP surfaces cannot show how many requests can run at full context at once.

Seat: KamaR25.CriticLearningBar (critic, claim C2, read-only). Base 147f5bdd3228ab712520b5f377346cb2d9a64769 (`git log -1 --format=%H` in the lane printed this hash, exit 0). Access date for every source: 2026-10-22. No llama-server was started. One offline binary, `llama-fit-params`, was run; it opens no port.

## Axes

- Coverage (C2's axis): does the new entry hold ground the admitted corpus did not hold?
- Calibration (side effect): do the cell predictions measure anything, or only reproduce a known formula?
- Provenance: does the new entry rest on newly opened source rows, or only re-cite S060?
- Single authority: does the new tool become a second formula alongside round-20's `nctx-crosscheck.py`?

## Counterexample 1: the eight cells reproduce knowledge the lane already has

What is already held (direct reads):

- `corpus/knowledge/gguf-declared-identity.md:27-32`. Per-slot context is capped by `--kv-unified-per-slot` and the training context. `/props` `n_ctx` is the per-slot value, and `/v1/models` carries `n_ctx_train`. It also says "Do not divide `ctx` by `total_slots` blindly: KV-unified and padding affect that relationship."
- `SKILL.md:665-667` repeats this: "`/props` per-slot `n_ctx` is not training context and must not be computed as `ctx / total_slots` unconditionally (S060)."
- `.ufo/waves/round-20/build/advice/SrcServerNctx.md:6` already gives the full rule. Padding to 256 comes from `src/llama-context.cpp:219,377-393`. A unified cache gives `n_ctx_seq = n_ctx`, and a split cache gives `GGML_PAD(n_ctx / n_seq_max, 256)`. Auto slot count resolves to 4 slots with a unified cache (`server.cpp:169-174`). It also shows the split-mode round-up example.
- `.ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py:37-44` puts that rule into code (`predict()`).

The measurement: `python3 .ufo/waves/round-25/build/out/CriticLearningBar/cell-predictions.py` (exit 0) imports the round-20 `predict()` and runs it on K1-K8. The output is in `cell-predictions.out`:

```
cell  args                                                r20_slot source_slot source_pool slots kv_unified fair_share agree
K1    -c 0                                                2048     2048        2048        4     true       512        yes
K2    -c 2048 -np 2 --no-kv-unified                       1024     1024        2048        2     false      1024       yes
K3    -c 2048 -np 2 --kv-unified                          2048     2048        2048        2     true       1024       yes
K4    -c 1024 -np 1                                       1024     1024        1024        1     false      1024       yes
K5    -c 4096 -np 1                                       2048     2048        4096        1     false      2048       yes
K6    -c 1000 -np 3 --no-kv-unified                       512      512         1536        3     false      512        yes
K7    -np 2 --kv-unified-per-slot 512                     512      512         1024        2     false      512        yes
K8    -c 4096 -np 4 --kv-unified --kv-unified-per-slot 512 512     512         4096        4     true       512        yes
X1    -np 4 --no-kv-unified                               512      2048        8192        4     false      2048       NO
X2    -c 8192 -np 4 --no-kv-unified                       2048     2048        8192        4     false      2048       yes
X3    -c 2048 (auto slots)                                2048     2048        2048        4     true       512        yes
```

(The header is abbreviated here. In the script, `fair_share` is named `concurrent_guarantee_per_slot`.)

- The round-20 formula already predicts all eight preregistered per-slot values. Matching on K1-K8 replicates held knowledge. It does not cover new ground. The pilot (`pilot.md:12-16`) already observed K1-K3.
- K6 is labeled "unknown" in `preregistration.json:43`, but the lane's own committed formula determines it from source: per-slot 512, pool 1536. Grading K6 as a "learned" outcome would be false provenance. The preregistration needs no edit (no narrowing). The closure must simply not present K6 as discovery.
- The receipt fields in `preregistration.json:33` cannot see the pool. They are `/props` `n_ctx`, `total_slots`, `/slots` `n_ctx`, `n_ctx_train`, and the `n_ctx_slot`/`kv_unified` log line. In a peer's K1 trial (`/fast/scratch/hyaku/kama-r25/ExecRawReplicate/trial.props`, `.slots`, `.models`), the top-level `/props` keys include no pool or `kv_unified` field. `grep -n -i 'unified\|pool'` over the three bodies exited 1 (no match). At default verbosity the log has only the `n_ctx_slot` line; the `llama_context: n_ctx` line is absent (see `/fast/scratch/hyaku/kama25/srv.log` lines 1-11 and `ExecRawReplicate/k1-trial.log:8`). So K5 (pool 4096, served 2048) and K6 (pool 1536, requested 1000) look identical to "pool equals slot × slots" in every recorded field.

Impacted axes: coverage. A restatement plus eight confirmations is not "admitted knowledge on uncovered ground" (`/home/vgpnk/Projects/shokunin/.scratch/goal-20261022-hyaku-12h.md:145-147`). Calibration is also affected: prediction hits look like learning but are replication.

## Counterexample 2: the existing lane formula is wrong for an unset context with a split cache, and no K cell tests that case

Source (llama.cpp at 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, opened 2026-10-22; hashes in `out/CriticLearningBar/sources.sha256`):

- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp lines 195-196: "with non-unified kv, we need to take into account n_streams … we must extend the n_ctx to hold enough n_streams". Lines 197 and 271-272 set `n_streams = kv_unified ? 1 : n_seq_max`, and when `n_ctx == 0` they set `cparams->n_ctx = n_ctx_train * n_streams`.
- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/common.h line 483: "whether to fit unset model/context parameters to free device memory" (default `true`). Line 485 sets the minimum context for reduction to 4096. Line 580 sets `kv_unified = false` as the default.
- The server reaches this path through `server-context.cpp:1217` (`common_init_from_params`), then `common.cpp:1419`, then `common.cpp:1245-1276` (`if (params.fit_params) … common_fit_params(...)`).

Offline observation on the same build: `/home/vgpnk/.local/opt/llama-b11755/llama-fit-params -m ~/.cache/kama-shokunin/models/stories260K.gguf <args>` (model sha256 `270cba1b…d256d`). The tool's `-np` default does not unify the cache (`common.h:580`). Output is in `out/CriticLearningBar/fit-params.out`:

- `-np 4` printed `-c 8192 -ngl -1` (exit 0)
- `-c 0 -np 4` printed `-c 8192 -ngl -1` (exit 0)
- `-c 2048 -np 4` printed `-c 2048 -ngl -1` (exit 0)
- `-np 1` printed `-c 2048 -ngl -1` (exit 0)
- Every `-kvu`/`-no-kvu` variant printed `error: invalid argument` (exit 1). The flag is server-only, so these runs are not evidence.

[INFERENCE, not served] For `llama-server -np 4 --no-kv-unified` with `-c` unset or 0 (X1), the source path gives pool 8192 and per-slot 2048. Round-20 `predict()` returns 512. Its table row `0 4 false 2048 512` (printed by `nctx-crosscheck.py --table`, exit 0) is wrong for this binary. The round-20 docstring (`nctx-crosscheck.py:13`) excludes only cases where "--fit run lowered n_ctx". It misses that fit also raises an unset context by the number of streams.

Impacted axes: coverage and single authority. This is the clearest way to supersede a weaker entry, but none of K1-K8 can show it. K1 is unified (one stream, so no difference). K7 sizes the pool from the per-slot flag before fit runs (`server.cpp:177-186`). Every other cell sets `-c`.

## Counterexample 3: identical HTTP surfaces can hide a fourfold difference in capacity under load

- K1 (`-c 0`, auto) and X2 (`-c 8192 -np 4 --no-kv-unified`) both predict `/props` `n_ctx` 2048, `total_slots` 4, four `/slots` entries of 2048, and `/v1/models` `meta.n_ctx` 2048. K1 shares one 2048-token pool across four slots. X2 gives each slot its own 2048-token stream. [INFERENCE: only the K1 side has been observed, in the pilot and the peer trial.]
- When a shared pool fills, every running request fails, not just the newest. https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp line 4301: `err = "Context size has been exceeded.";`. Lines 4318-4320 send that error to every slot that is processing. Lines 4334-4339 first retry with a halved batch.
- `/props` exposes neither the cache layout nor the pool size. Its fields are at `server-context.cpp:5229-5245`, and `total_slots` is at line 5244. The only external signal is the startup log `kv_unified = 'true'` (`server-context.cpp:1392-1393`).

This is the real "declared versus served" gap at frontier K05: the advertised `n_ctx` limits one request; it does not promise that capacity for concurrent requests. The admitted corpus never says this. `gguf-declared-identity.md:31` only says "do not divide blindly".

## Minor findings

- `src/llama-context.cpp:391` logs "n_ctx is not divisible by n_seq_max - rounding down to %u", but in K6 the value rises from 1024 to 1536. The entry should quote the number, not the word "down".
- `--kv-unified-per-slot` caps and sizes the pool even when the cache is not unified (K7: split, pool 1024, per-slot 512; `server.cpp:177-186`, `server-context.cpp:4658-4659`). The flag name implies otherwise, so this is worth one sentence.
- The fit reduction only applies when `n_ctx_train` is above 4096 (`common/fit.cpp:394`, `common.h:485`). The stories260K model (`n_ctx_train` 2048) can never show it. The served context of real consumer models (32k-128k training contexts) can depend on free device memory when `-c` is unset. The entry must state this boundary and must not generalize from the fixture.
- Peers already cover the padding and auto-slot rules (scratch directories for SrcCtxPadding, SrcLlamaContextSeq, SrcArgKvuDefault, SrcServerSlotsAuto, SrcArgPerSlot). No admitted SOURCES row cites `src/llama-context.cpp` or `common/fit.cpp`. S037 (`server.cpp`) is scoped to start-up order and S060 to `server-context.cpp`. `grep` over `corpus/SOURCES.md` found 105 rows and none for those two files.

## What the new entry must add to be more than a restatement

To qualify as "a stronger entry superseding a weaker one", `corpus/knowledge/context-capacity.md` should state each of these with an opened source row and a quote:

1. **Pool versus slot.** A two-number model: the KV pool (`llama_context` `n_ctx`) and the per-slot ceiling (`n_ctx_slot`). Include the rule that resolves the pool from `-c`, slot count, cache layout, the per-slot flag and fit (`server.cpp:169-186`, `common/fit.cpp:195-198,266-273`, `src/llama-context.cpp:377-392`). Without the pool, it repeats `gguf-declared-identity.md:27-32`.
2. **Load guarantee.** The per-slot `n_ctx` limits a single request. With a unified cache, slots share the pool, and a full pool fails every running request (`server-context.cpp:4301,4318-4320`). Two launches with identical `/props`, `/slots` and `/v1/models` can differ fourfold in full-context concurrency (K1 versus X2).
3. **Visibility limit.** No HTTP field shows the cache layout or pool. Default logs show the layout but not the pool. A consumer cannot infer concurrent capacity from the endpoint alone.
4. **Supersession.** Say explicitly that this entry supersedes the round-20 formula for an unset context with a split cache. Name `nctx-crosscheck.py`'s 512 row as wrong and give the corrected value with the fit source.
5. **Boundary.** Memory-dependent fit reduction applies only above `--fit-ctx` (4096), so the fixture cannot show it. Real consumers can, so it remains frontier.

## Smallest safe corrections (no narrowing, no change to the preregistered claim value)

- Keep K1-K8 and their measure as registered. In the closure, report K1-K8 prediction hits as replication of round-20 lane knowledge (`prediction_grading`, `preregistration.json:52`), not as discovery. Do not call K6 learned.
- Add the pool to each cell's receipt. It is visible only in the `llama_context` log line, which default verbosity omits. Either capture it with a higher `-lv` (verbosity level unverified here) or record the source-derived pool as "derived, not observed". Record the K6 warning text and the K5 two warnings as observed log lines.
- As supporting evidence outside the claim value, run one extra unregistered cell, X1 (`-np 4 --no-kv-unified`, no `-c`), labeled unregistered. Its `/props` `n_ctx` decides between round-20's 512 and the source-path 2048 with one launch. Optionally add X2 to show identical surfaces with K1.
- `tools/kama-context-capacity.py` must not become a second formula next to `nctx-crosscheck.py`. It should model the fit step (`common/fit.cpp:266-273`) and per-slot pool sizing (`server.cpp:179-186`), and output the pool and per-slot values. It should return could-not-evaluate when `n_ctx_train` is above `--fit-ctx` and `-c` is unset (memory-dependent). It should name round-20's `predict()` as superseded, with its X1 row as the control that must disagree.
- If the entry claims new provenance, open SOURCES rows for `src/llama-context.cpp` (lines 377-392) and `common/fit.cpp` (lines 195-198, 266-273) at 704366d76. S060 alone covers only the slot cap.

Which of these is a defect and which is a tradeoff: the eight cells all replicating held knowledge is a tradeoff for the judge (the claim value stays honest). Presenting them as new learning would be a defect. The missing fit step in any copied formula is a fixable defect.

## Files written

- `.ufo/waves/round-25/build/advice/CriticLearningBar.md` (this report)
- `.ufo/waves/round-25/build/out/CriticLearningBar/cell-predictions.py` (compares round-20 `predict()` with the source-complete rule)
- `.ufo/waves/round-25/build/out/CriticLearningBar/cell-predictions.out` (its output, exit 0)
- `.ufo/waves/round-25/build/out/CriticLearningBar/fit-params.out` (`llama-fit-params` tails)
- `.ufo/waves/round-25/build/out/CriticLearningBar/sources.sha256` (pinned raw hashes; `server-context.cpp` `dd1de0f2…2329` equals S060's hash)
- Scratch: `/fast/scratch/hyaku/kama-r25/CriticLearningBar/src/*` (raw pinned sources), `/fast/scratch/hyaku/kama-r25/CriticLearningBar/fit-*.out`

Tools installed or updated: none.
