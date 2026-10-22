Verdict: defect found. 15 overclaims in `corpus/knowledge/context-capacity.md` and SKILL.md `### Round-25 decision rows` at fa3b62ae6475d111eb466d79af616aeebb08bbb9. Four are high or medium: a cell in the entry's own receipt (K7) contradicts the fit rule, the supersession scope and SKILL row 2; the "pool total" rule is stated for every cache layout although only one shared-pool test with equal requests was run; the `verified-at` window belongs to the superseded receipt; and "ask for the launch flags" leaves out the environment variables and free memory that also set capacity. The C2 count (`registered 14 observed 14 bound True missing []`) is not affected. This is a problem of wording and scope, not of observation.

# CriticEntryOverclaim — kama round 25 attempt 2, wave 2 (falsify)

Seat: fresh critic identity, read-only. No llama-server started and no port touched. No tool installed or upgraded. Lane bytes read with `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show fa3b62ae…:<path>`. Pinned llama.cpp sources fetched fresh (access date 2026-10-22) from `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/<path>`, every `curl -fsSL` rc=0. The sha256 values and located lines are in `out/CriticEntryOverclaim/sources-and-checks.txt`. The fit.cpp and server.cpp digests equal the ones a2-build ConnectorSiblingOverlap recorded.

Every command below exited 0 unless stated otherwise.

## Findings, most severe first

### F1 (high): K7 contradicts the fit rule, the supersession scope and SKILL row 2

The claims:
- Entry 71-74: "When `-c` is unset and `--fit` is on (the default), the fit step … sets the context to the training context times the number of streams."
- Entry 87-89: "For build 11755 with an unset context, fit on and a split cache, the observed value is 2048."
- SKILL.md:687, symptom "`-c` unset, `-np` given, split cache". It gives the verdict "With `--fit` on (default) the pool becomes training context × slots" and the action "Do not use the round-20 `nctx-crosscheck.py` value for this case; it gives 512 and is superseded."

The counterexample is in the committed receipt. K7 (`-np 2 --kv-unified-per-slot 512`) has no `-c`, runs with fit at its default (on), and has a split cache. It observed pool 1024 and 512 per slot, not 4096 and 2048:
- `final/raw/K7.server.log:9` reads "--kv-unified-per-slot: sizing KV pool to n_parallel * kv_unified_per_slot = 2 * 512 = 1024".
- `final/raw/K7.server.log:1084` reads "n_slots = 2, n_ctx_slot = 512, kv_unified = 'false'".

The source explains why. At server.cpp:179-184 the server sets `params.n_ctx` before fit runs. Fit raises the context only `if (n_ctx_auto)`, where `n_ctx_auto = cparams->n_ctx == 0` (fit.cpp:198, 271-272). On K7, round 20's per-slot value (512) is correct (`a2-build/out/CriticLearningBarA2/r20-vs-observed.out`, K7 `slot_agree yes`). So SKILL row 2's "superseded" also wrongly covers K7, and X3, where the row's own verdict says round 20 holds.

There are two more boundaries, both from source and not run [INFERENCE]:
- `-c 0` also gives fit a context of 0, because the default `n_ctx` is 0 (common.h:457). With a split cache it would therefore also be raised. Entry 95-97 makes it look as if `-c 0` and an omitted `-c` differ only in reduction.
- `-sm tensor` makes fit throw at fit.cpp:183-184, before the raise. The exception is caught as a warning (fit.cpp:894-896), so in that case "fit on" does not lead to the raise.

Impacted axes: coverage (the content of the learning claim) and the supersession boundary.

Replacement text:
- Entry heading at line 69: `## Fit raises a zero split context to the training context per slot (corrects the round-20 rule for that case only)`
- Entry lines 71-74:
  > When the context resolves to 0 (no `-c`, or `-c 0`, and no `--kv-unified-per-slot`, which sizes the context before fit runs; S108, server.cpp 179-186) and `--fit` is on (the default), the fit step runs before the model loads (S111, common.cpp 1245-1276). It first sets the context to the training context times the number of streams: one stream for a unified cache, one per slot for a split cache (S106, fit.cpp 195-198 and 266-273). On a model whose cache does not fit in memory it may then lower that value (see Scope). K7 is the exception in this receipt: no `-c`, fit on and a split cache, but `--kv-unified-per-slot 512` sizes the pool to 1024 and fit leaves it there.
- Entry lines 87-91, from "For build 11755":
  > For build 11755 on this fixture, with no `-c`, no `--kv-unified-per-slot`, fit on and a split cache, the observed per-slot value is the training context (2048), not 512 (X1). Under `--fit off` (X3) and with `--kv-unified-per-slot` (K7), the round-20 per-slot value holds. `-c 0` with a split cache was not run; the source predicts the X1 value [INFERENCE]. On the other ten registered config cells, round 20's per-slot value agrees with the observation (see F4 for the pool).
- Entry, add after line 97:
  > Both an omitted `-c` and `-c 0` reach fit with a context of 0 (common.h 457). `-c 0` also turns off fit's reduction and the `--kv-unified-per-slot` pool sizing (server.cpp 179-181).
- SKILL.md:687, the whole row:
  > | No `-c` (or `-c 0`), no `--kv-unified-per-slot`, `-np` given, split cache | The verbose startup log (`llama_context: n_ctx = N`); launch flags plus `LLAMA_ARG_*` environment only as a fallback | With `--fit` on (default) and a cache that fits in memory, the pool becomes training context × slots and each slot gets the full training context (S106; X1: 8192 pool, 2048 per slot). With `--fit off` the training context is split (X3: 2048, 512). With `--kv-unified-per-slot N` the pool is slots × N (K7: 1024, 512) | With fit on, do not use the round-20 `nctx-crosscheck.py` per-slot value (512); it is superseded for this case only and still matches X3 and K7. `-c 0` with a split cache was not run. |

### F2 (high): "the pool total" is stated for every layout and rests on one test with equal requests

The claims:
- Entry heading at line 99: "A shared pool limits concurrent requests by its total size."
- Entry 121: "The limit is the pool total, not a full per-slot context."
- SKILL.md:688 verdict: "Concurrent requests are bounded by the pool total, not by the per-slot number". The action reads "Size concurrent use from the pool and the request sizes, never from `total_slots` alone".

There are three counterexamples:
1. The SKILL clause has no scope. With a split cache, the KV cache keeps one stream per sequence (`n_stream(unified ? 1 : n_seq_max)`, llama-kv-cache.cpp:84). `try_clear_idle_slots()` also returns at once when the cache is not unified (server-context.cpp:1810-1815). So a request on a split cache is held to its own stream, which is the per-slot value. Spare cells in other streams do not help it [INFERENCE from source; the entry's own line 173 says a split cache under concurrent load was not run]. For a split cache, `total_slots` × per-slot is the right sizing rule, and the action says the opposite.
2. L1 sent two requests of the same size (1000 + 600 each). A limit on the summed cells (2 × 1025 > 2048) and an equal share per active request (1025 > 2048 / 2) predict the same failure. Only unequal requests separate the two, for example 1500 + 400, which sums to 1900. The source supports the summed reading (one stream when unified), but no run tested it. The sibling falsify outputs `a2-falsify/out/ExecBoundaryPool/results-summary.md` and `ExecSharedPool8192/` also use equal pairs only (they are unadmitted wave-2 output and are named here only as context).
3. "The limit is X, not the per-slot context" suggests that only one limit applies. In fact both apply: a request is capped by `n_ctx_slot()` (server-context.cpp:4655-4662), and the requests share the pool.

Impacted axes: coverage (the claim is generalised beyond one request size and one layout).

Replacement text:
- Entry heading at line 99: `## On a shared pool, concurrent requests can run out of cells below the per-slot ceiling`
- Entry lines 121-125:
  > - On a shared pool the cells ran out before either request reached its per-slot ceiling. Each L1 request failed at 1025 tokens, about half of its 2048 ceiling, when 2 × 1025 exceeded the 2048 pool. Both requests were the same size, so L1 does not separate a limit on the summed cells from an equal share per request. The source supports the summed reading (S113: a unified cache keeps all sequences in one stream), but it was not tested with unequal requests. Each request is still capped by its per-slot ceiling as well. On a split cache each request is held to its own stream, and spare cells in other streams do not help it [INFERENCE from S113; not run under load]. L1 and L2 report the same endpoints (per slot 2048, 4 slots), and L2's pool is four times larger. L2 changes the pool size and the cache layout together, so it does not separate the two; a shared 8192 pool was not run.
- SKILL.md:688, verdict and action cells:
  > On a shared (unified) pool, concurrent requests draw on the same cells. When together they need more cells than the pool holds, every processing request fails with HTTP 500 `Context size has been exceeded.` (S109; L1: two equal 1000 + 600 token requests both failed at 1025 tokens each on a 2048 pool; L2, split 8192, and L3, sequential, both 200). On a split cache each request is limited to its own per-slot stream [INFERENCE, S113]. Tested only with two equal 1000 + 600 token requests | On a unified cache, size concurrent use from the pool and the request sizes. On a split cache, size it from the per-slot value. Never use `total_slots` alone. Escalate a consumer that assumes more. |

### F3 (medium): the `verified-at` window belongs to the superseded receipt

The claim, entry line 2: "14 fixture cells observed 2026-10-22T09:36:51Z to 09:36:59Z".

The evidence:
- The committed receipt (5c95c8f1, the one the C2 counter scores) has `started_utc` 2026-10-22T09:42:42.438Z and `ended_utc` 09:42:50.502Z. Its first cell, K1, started at 09:42:42.481Z.
- 09:36:51.264Z to 09:36:59.400Z is the window of the earlier receipt at 5ea4fc44. Amendment 4 says that receipt scores 11 of 14.
- SCORECARD.md:1287 has the right window (09:42:42Z to 09:42:50Z).

Impacted axes: provenance (a false date in the entry header). Replacement for line 2:
> verified-at: 2026-10-22 — sources opened this round; 14 fixture cells observed 2026-10-22T09:42:42Z to 09:42:50Z (receipt commit 5c95c8f1) on the lane-owned fixture, torn down in the same run

### F4 (medium): "round 20 agrees on the other ten cells" is contradicted by the entry's own K7 row

The claim, entry 90-91: "On the other ten registered config cells round 20 agrees with the observation."

The evidence: entry line 29 says of K7 "the round-20 model implies 2048", and the observed pool was 1024. In `a2-build/out/CriticLearningBarA2/r20-vs-observed.out` the K7 row reads `r20_pool 2048 obs_pool 1024 pool_agree NO`. Round 20's `predict()` (nctx-crosscheck.py:38-44) returns only a per-slot value, so "agrees" holds only for the per-slot number.

Replacement (already part of the F1 text; it can also stand alone):
> On the other ten registered config cells, round 20's per-slot value agrees with the observation. Round 20 models no pool, and the pool it implies for K7 (2048) differs from the observed 1024 (`a2-build/out/CriticLearningBarA2/r20-vs-observed.out`).

### F5 (medium): "ask for the launch flags" assumes the flags are enough

The claims:
- Entry 145-146: "Ask for the launch flags or the verbose startup log."
- SKILL.md:689 action: "Require the verbose log line or the launch flags as evidence".
- SKILL.md:687 first check: "The launch flags and the verbose startup log".

The counterexample: every option that sets capacity also has an environment variable at this build. In arg.cpp they are `LLAMA_ARG_CTX_SIZE` (1651), `LLAMA_ARG_KV_UNIFIED_PER_SLOT` (1659), `LLAMA_ARG_KV_UNIFIED` (1734), `LLAMA_ARG_N_PARALLEL` (2556), `LLAMA_ARG_FIT` (2894) and `LLAMA_ARG_FIT_CTX` (2940). A launch with no capacity flags can still be any of the 14 cells. Round 20's own cross-check refuses `LLAMA_ARG_` environment as unmodelled (nctx-crosscheck.py:47-50). Also, when fit can lower the context, the result depends on free memory at launch, and no flag records that (fit.cpp:384-430).

Replacement for entry lines 144-146:
> So a consumer that reads only these endpoints cannot know how many concurrent requests of a given size will fit. Ask for the verbose startup log (`llama_context: n_ctx` and `kv_unified`). Launch flags are a weaker substitute: every option involved can also come from an environment variable (`LLAMA_ARG_CTX_SIZE`, `LLAMA_ARG_N_PARALLEL`, `LLAMA_ARG_KV_UNIFIED`, `LLAMA_ARG_KV_UNIFIED_PER_SLOT`, `LLAMA_ARG_FIT`, `LLAMA_ARG_FIT_CTX`; S110). Where fit can lower the context, the result also depends on free memory at launch.

Replacement for the SKILL.md:689 action:
> Require the verbose log line as evidence. Launch flags count only together with the `LLAMA_ARG_*` environment and only where fit cannot lower the context. Without them the pool is unknown.

### F6 (medium): fit's reduction needs both conditions, but the entry says "or"

The claim, entry 155-157: "its reduction needs a training context above `--fit-ctx` (4096 by default) or a cache that does not fit in memory (S106, fit.cpp 393-394)".

The source: the reduction block runs only inside `if (global_surplus < 0)` (fit.cpp:384, the memory shortfall). Inside that block it also needs `if (n_ctx_auto)` and `if (n_ctx_max > n_ctx_min_total)` (393-394), and `n_ctx_min_total` is `--fit-ctx` × streams (268). Both conditions are required. On this fixture the conclusion ("fit never lowers") still holds. The "or" would mislead on a large model whose cache fits: it predicts a reduction that the source does not make. Line 158 ("free device memory decides whether fit raises or lowers") also blurs the order: with a split cache, fit always raises first and then may lower; with a unified cache it never raises.

Replacement for entry lines 155-159:
> Fit never lowers a context here. It lowers a context of 0 only when projected memory misses its target and the training context is above `--fit-ctx` (4096 by default) (S106, fit.cpp 384 and 393-394), and neither holds for this fixture. On large models with a split cache, fit first raises a context of 0 to training context × slots and then, if memory is short, lowers it toward `--fit-ctx` per stream. With a unified cache it can only lower. Free memory at launch decides, so these fixture values do not transfer.

### F7 (medium): prediction provenance is stated as "from source"

The claim, entry 36-38: "The K4-K8 predictions (preregistration) and the X and L predictions (amendment 2) were written from source before the attempt-2 runs."

The evidence comes from `errata-attempt-2.json`:
- corrections[1]: "X1 and X2 come from CriticLearningBar (advice written … after attempt-1 K-cell runs existed and citing them)".
- corrections[2] withdraws "the prediction credit that amendment 1 gave K4, K5, K7 and K8, because the author had read attempt-1 K-cell values first".

Replacement for entry lines 35-38, up to "K1-K3 copied the pilot.":
> Matches with the round-20 rule are replication and calibration evidence, not new knowledge. The K4-K8 predictions (preregistration) and the X and L predictions (amendment 2) were written before the attempt-2 runs, but not blind. X1 and X2 came from a critic who had seen attempt-1 cell values, and the prediction credit for K4, K5, K7 and K8 was withdrawn because the author had read attempt-1 values (`errata-attempt-2.json`). K1-K3 copied the pilot.

### F8 (medium): the opening paragraph presents a fourfold full-context difference as observed

The claims:
- Entry 7-12: "What a llama-server serves is two numbers that its HTTP endpoints do not tell apart".
- "Two launches can report identical endpoints and still differ fourfold in how many full-context requests they can run at once."

The evidence:
- The paragraph is universal over llama-server, but only build 11755 and three endpoints were checked; `/metrics` was not read (entry 136).
- Nothing ran full-context (2048-token) requests concurrently. L2 ran two 1600-token requests. "Fourfold" is the pool ratio of K1 to X2 (2048 to 8192), and the number of full-context requests is inferred from it.
- "Do not tell apart" undersells the gap: the endpoints do not report the pool at all.

Replacement for entry lines 7-12:
> A GGUF header declares a training context (2048 for the lane fixture). At build 11755 a llama-server has two capacity numbers: the **KV pool** (`llama_context: n_ctx`, the whole cache) and the **per-slot ceiling** (`n_ctx_slot`, the most one request may use). Its `/props`, `/slots` and `/v1/models` endpoints report only the second. On this fixture two launches (K1 and X2) report the same values there while their pools differ fourfold (2048 and 8192). Two concurrent 1600-token requests failed on the K1 configuration (L1) and passed on the X2 configuration (L2). That four full-context requests fit at once on X2 follows from the pool size but was not run.

### F9 (low): the order of events leaves out the idle-slot purge, and "stops" is ambiguous

The claim, entry 112-115: "when decoding finds no free KV space the server first halves the batch and retries; … clears them and stops."

The source and log:
- At server-context.cpp:4335-4336, `if (!try_clear_idle_slots()) { n_batch /= 2; }`. On a unified cache the server first purges idle slots that still hold a cached prompt, and halves only if nothing was purged. This matters under the default `cache_prompt` true, which L3 did not cover.
- After the error the server goes back to idle: `final/raw/L1.server.log:1884` reads "update_slots: all slots are idle". It exits only on the tool's SIGTERM (receipt L1 teardown: `sigterm_sent true`, `child_returncode 0`).

Replacement:
> Order of events (S109, server-context.cpp 4294-4341 and 1810-1815): when decoding finds no free KV space, the server on a unified cache first purges idle slots that still hold a cached prompt. If none was purged (always the case on a split cache), it halves the batch and retries. When a batch of one still fails, it sends `Context size has been exceeded.` to every processing slot, clears them and drops that decode step. The server then returns to idle (`final/raw/L1.server.log` line 1884); serving a later request was not tested.

### F10 (low): "at default verbosity a pool value appears only in warnings"

The claim, entry 139-141.

The counterexample: K7 logs a pool value at info level, `final/raw/K7.server.log:9` "--kv-unified-per-slot: sizing KV pool to … = 1024". It is printed by `SRV_INF` (server.cpp:185), the same macro as the `load_model: initializing` line (server-context.cpp:1392), which ExecVerbosityControl saw at default verbosity. Whether the K7 line prints at default verbosity was not run [INFERENCE]. a2-build CriticLearningBarA2.md:84 raised the same point and it was not taken up.

Replacement:
> At default verbosity a pool value appears only in some launches: in warnings such as K6's "rounding down to 1536" or K5's `n_ctx_seq (4096) > n_ctx_train`, and in the info line `--kv-unified-per-slot: sizing KV pool to … = 1024` (K7). That line uses the same log macro as the `load_model` line; its default-verbosity print was not run.

### F11 (low): "identical values on all three"

The claims are at entry 136 and SKILL.md:689. The evidence: K1 and X2 `/props` differ in `media_marker`, which is random per launch, and `/v1/models` differ in `data[0].created`. A JSON diff of the two `/props` bodies exited 1 and showed only the `media_marker` difference.

Replacement:
> K1 and X2 return the same capacity values (`n_ctx`, `total_slots`, slot entries) on all three. They differ only in fields that change per launch (`media_marker`, `created`).

### F12 (low): Scope calls the features "build-specific" without evidence

The claim, entry 150-151: "`--kv-unified-per-slot`, the auto slot default and the fit step are build-specific." No other build was read, so "specific" claims that they are absent or different elsewhere. Kengaku's other build already shows unified per-slot behaviour.

Replacement:
> `--kv-unified-per-slot`, the auto slot default and the fit step were read only at this build; whether other builds behave the same is unknown.

### F13 (low): another build's pool is stated as a fact

The claims:
- Entry 183-184: "That is a per-slot ceiling of 16384 on one shared 16384-cell pool, the L1 shape."
- SKILL.md:188-190 (next to the target): "`--ctx-size 16384` only because that launch also set `--kv-unified`: both slots share one 16384-cell pool".

The evidence: the build is b1-d7bd3bf, and no pool log exists for it. The pool is inferred from b11755 semantics, which the entry's own Scope says do not transfer to other builds.

Replacements:
- Entry: "Read with b11755 semantics, that is a per-slot ceiling of 16384 on one shared 16384-cell pool, the L1 shape [INFERENCE: no pool log exists for that build]."
- SKILL.md:188-190: "(consistent with `--parallel 2`, `--ctx-size 16384` and `--kv-unified`; under b11755 semantics both slots share one 16384-cell pool, not logged for that build; see `corpus/knowledge/context-capacity.md`)."

### F14 (low): SKILL row 1 lists a field that does not read `n_ctx_slot()`

At SKILL.md:686 the First-check column lists "`/v1/models` `meta.n_ctx_train`", and the verdict says "the three endpoints read one function". `meta.n_ctx_train` is the model's training context (`llama_model_n_ctx_train`). The `n_ctx_slot()` field is `meta.n_ctx` (server-context.cpp:5186, and entry line 44). The fix is to replace "`/v1/models` `meta.n_ctx_train`" with "`/v1/models` `meta.n_ctx` (and `meta.n_ctx_train` for the training context, a separate value)".

### F15 (low): fit can abort before the raise

Add this bullet to entry "Does not establish":
> Launches where fit aborts before resolving the context, for example `-sm tensor` (fit.cpp 183-184, caught as a warning at 894-896). The source predicts the round-20 split there [INFERENCE, not run].

## Checked and holding

- Raw bodies, all 14 cells: `/props` `n_ctx` equals every `/slots` `n_ctx` and `/v1/models` `meta.n_ctx`, and the `/slots` length equals `total_slots`. Checked with a python3 loop over `git show` of `final/raw/*.body`. Entry 46-47 holds.
- Raw-log line numbers: X1 lines 283 (2048), 812 and 1344 (8192) and 1610 (`load_model`), and L1 lines 1849-1866 (both released at `n_tokens = 1025`), all match.
- Source citations re-read at the pinned commit: fit.cpp 195-198 and 266-273; server.cpp 169-174 and 179-186; llama-context.cpp 219 and 377-392; arg.cpp 1646-1649; common.h 580; llama-kv-cache.cpp 84, 144 and 301-304; server-context.cpp 4294-4341 and 4655-4662; README 165. Each says what the entry says, apart from the scope problems above.
- `gguf-declared-identity.md:33-34` points to this entry, so entry 91-92 holds.
- `tools/kama-context-capacity.py` has no prediction or formula code (searched for predict, expect and formula: no hits), so entry 93-94 holds.
- ExecLoadReplicate saw 3 of 3 runs per L cell (advice lines 20-45), so entry 119-120 holds. ExecVerbosityControl compared K1, K6 and X1, so entry 141-143 holds.
- The "Does not establish" list (entry 161-174) and the L-section line "No claim is made for other request counts or sizes" (129-130) are correctly scoped. They contradict the unscoped headline and SKILL wording in F1 and F2, which is why those findings matter.
- The LOG.md round-25 entry (lines 1635-1672) is observational and has none of these overclaims.

## Smallest safe correction

Apply the replacement text for F1, F2, F3 and F5 (entry lines 2, 69-74, 87-91, 99, 121-125, 144-146 and SKILL.md:687-689). Those four change what a reader would do. F4 and F6-F15 are wording fixes to the same two files and SKILL.md:188-190. None needs a new run. Two points would need runs to move from [INFERENCE] to observed, and the entry only has to label them, not test them: unequal concurrent requests on a shared pool (F2), and `-c 0` with a split cache (F1).

## Files written

- `.ufo/waves/round-25/a2-falsify/advice/CriticEntryOverclaim.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/CriticEntryOverclaim/sources-and-checks.txt` (source digests, located lines, receipt checks)
- Scratch, outside the lane: `/fast/scratch/hyaku/kama-r25a2w2/CriticEntryOverclaim/src/` (nine pinned llama.cpp source files)

No tool was installed or upgraded. No llama-server child was started. No lane production file, git index or jj state was touched.
