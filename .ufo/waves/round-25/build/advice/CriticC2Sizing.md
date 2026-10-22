Verdict: C2 is sized as a fixable defect, not a reject. `observed 8` is one concrete value that one command re-derives over committed bytes, but the command counts truthy keys, not observations. K1-K3 are pilot echoes, not predictions. K6 is no prediction at all. The receipt fields leave out the declared-versus-served gap the cells exist to show. The knowledge entry needs explicit fixture-scope limits.

Seat: KamaR25.CriticC2Sizing (critic, read-only, wave 1). Access date for every source: 2026-10-22. No live llama-server was started. My item names no port range, so the fixture scope does not cover me. The only binary run was `~/.local/bin/llama-server --help` (exit 0), which opens no port.

# Attacks

## 1. The registered counting command accepts eight failed starts as `observed 8`

Counterexample: the registered C2 command (`preregistration.json:35`) counts `x.get('observed')`, which is true for any truthy value. It never checks that the five measured fields exist, that cell ids and args match K1-K8, or that the cell list has exactly 8 entries.

Command: `bash .ufo/waves/round-25/build/out/CriticC2Sizing/counting-counterexample.sh`. It builds synthetic receipts under `/fast/scratch/hyaku/kama-r25/CriticC2Sizing/receipts/`. The lane is not written. Exit 0. Output:

```
== failed-starts registered
cells 8 observed 8
== failed-starts bound
bound False server None model_sha256 None cells 8 observed 0
== nine-cells registered
cells 9 observed 8
== nine-cells bound
bound False server None model_sha256 None cells 9 observed 0
== shaped registered
cells 8 observed 8
== shaped bound
bound True server build 11755, commit 704366d76 model_sha256 270cba1b... cells 8 observed 8
```

In the `failed-starts` case, all eight cells hold `"observed": "server exited before /props answered"`, and the registered command still prints `observed 8`, which meets the target. In the `nine-cells` case, K1 is duplicated and K8 is not observed, yet it also meets `observed 8`. The target text "(of the 8 cells below)" is not enforced.

Axes: coverage (the claim value) and honesty of the after-value.

Smallest safe correction: count a cell as observed only when its id and args equal the preregistered cell and the measured fields are present with the right types. Also print the binary and model identity so the closure can see them. The bound one-liner is in `counting-counterexample.sh` (variable `BOUND`). The field names there are proposals, so match them to the schema of `tools/kama-context-capacity.py`. Proposed wording for `after_target`: `bound True ... cells 8 observed 8`.

Residual risk: the `shaped` case shows that no counting command catches fabricated values. Also commit the raw `/props`, `/slots` and `/v1/models` response bytes and the server log for each cell, and have the receipt carry their sha256 values. The replicate seat (ExecRawReplicate) can then re-check them.

This must be fixed before landing. Hardening the command later counts as narrowing only if it reduces the set. This change only makes the target harder, so it is allowed under the claim-sizing rule (`.ufo/prompts/kama-round-25.md:342-350`).

## 2. K1-K3 "predictions" copy the pilot's observations, and the timeline is not anchored

Evidence:
- `pilot.md:14-16` observed `-c 0` -> `2048 | 4 | [2048, 2048, 2048, 2048]`, kv_unified true. It also observed `-c 2048 -np 2 -no-kvu` -> 1024 and `-c 2048 -np 2 -kvu` -> 2048. `preregistration.json:38-40` "predicts" exactly these values, including the word "(auto)".
- File mtimes (`stat`, converted from -0300 to UTC):
  - `/fast/scratch/hyaku/kama25/srv.log`: 08:18:50Z. Its content is only the third configuration (`n_slots = 2, n_ctx_slot = 2048, kv_unified = 'true'`, srv.log:8).
  - `preregistration.json`: 08:21:12Z.
  - `pilot.md`: 08:21:54Z.
- `preregistration.json:5` says `"written_utc": "2026-10-22T08:31:00Z"`. That is later than the file's own mtime and later than the clock at my reads (`date -u` printed 08:24:42Z and 08:27:53Z). The stamp is false provenance.
- `pilot.md:6` says "about 08:22 UTC, before the preregistration". The file bytes cannot show that ordering: the pilot file was written after the preregistration file. Both are untracked (`git status --porcelain`: `?? .ufo/waves/round-25/pilot.md`, `?? .ufo/waves/round-25/preregistration.json`), so nothing anchors "preregistered" before the receipt.

Axes: calibration of the prediction grade, and provenance.

Smallest safe correction:
- In `prediction_grading`, split the cells: "K1-K3 pilot-observed (replication, not prediction); K4, K5, K7, K8 predicted before observation; K6 measurement only". Report prediction matches over 4 cells, never 8.
- Replace `written_utc` with the real write time, or add `"written_utc_note": "08:31 was a planned stamp; file mtime 08:21:12Z"`.
- Have L1 commit the preregistration and pilot before any committed receipt, so the order lives in history and not in a typed stamp.

## 3. K6 "unknown" is not a prediction, and pinned source already settles it

Evidence: I modelled the pinned source in `.ufo/waves/round-25/build/out/CriticC2Sizing/source-model.py` (`python3 source-model.py`, exit 0, output in `source-model.out`). The model reproduces all three pilot rows exactly and gives:

```
K6 -c 1000 -np 3 --no-kv-unified  {'total_slots': 3, 'kv_unified': False, 'kv_pool': 1536, 'n_ctx_seq': 512, 'slot_n_ctx': 512}
```

The derivation follows `src/llama-context.cpp:377-392`: pad(1000) = 1024, then 1024/3 = 341, then pad(341) = 512, so n_ctx becomes 512*3 = 1536. The server then reports 512 per slot and a pool of 1536, more than the declared `-c 1000`. The warning text says "rounding down" while the value goes up. The wave has started, so amending the preregistration now would be post-hoc. [INFERENCE] The 512/1536 values are unobserved until ExecEdgeCells or the capacity tool runs K6.

Axes: calibration. A cell that cannot be wrong adds no prediction credit.

Smallest safe correction: leave the preregistered "unknown" as written. The report should label K6 "measurement, no preregistered value". It may cite this advice report's source-derived value 512/1536 as an outside prediction made at 08:27Z, before any K6 receipt.

## 4. The receipt fields leave out the gap K05 is about: KV pool size against per-slot n_ctx

Evidence: three of the five recorded surfaces are the same number read through three endpoints:
- `/slots` n_ctx: `slot.n_ctx = n_ctx_slot();` (server-context.cpp:1437).
- `/v1/models` meta.n_ctx: `{"n_ctx", meta.slot_n_ctx}` (server-context.cpp:5186), where `slot_n_ctx = impl->n_ctx_slot()` (:4829).
- `/props` n_ctx: `{ "n_ctx", meta.slot_n_ctx }` (:5236).

Agreement among them is therefore expected and is not independent evidence. The value that differs from them, the KV pool `cparams.n_ctx`, is in no listed field:
- K5 (`-c 4096 -np 1`): pool 4096, served 2048 (`n_ctx_slot` caps at `n_ctx_train`, server-context.cpp:4662).
- K6: pool 1536, served 512.
- K7: pool 1024 (server.cpp:184).
- K8: pool 4096, served 512.

The K7 prediction "pool 1024" cannot be graded from the declared receipt fields at all. The pilot log at default verbosity contains no `llama_context:` info lines (srv.log:1-11). [INFERENCE] The pool is visible only through the warning and info lines `capping`, `rounding down` and `sizing KV pool`, or at higher verbosity.

Axes: coverage (what the entry can claim) and calibration (K7 is partly ungradeable).

Smallest safe correction: add one receipt field per cell, `log_capacity_lines`, holding every server log line that matches `n_ctx_slot|kv_unified|capping|rounding|sizing KV pool|n_ctx_seq`. Add it to the bound command's required fields. In the entry, write "three served surfaces report one value, `n_ctx_slot()`", not "three surfaces agree".

## 5. `observed 8` is thin as learning; size the learning on the entry, not the count

Finding: the source model reproduces every preregistered prediction (K4 1024, K5 2048, K7 512, K8 512). So all eight cells test whether we read b11755 correctly; they do not discover new behavior. That is honest learning only if the entry states that it is a source-confirmed rule set and puts the non-obvious results first:
- `/props` n_ctx is per slot.
- With the auto slot count (`-np` not given), the server forces 4 slots and unified KV (server.cpp:169-173). An explicit `-np` keeps the `kv_unified = false` default (common.h:580).
- An oversized `-c` is silently capped to n_ctx_train on every served surface (K5).
- A non-unified split pads per sequence and can grow the pool above `-c` (K6).

The count of 8 is a completeness gate, not a learning measure. That is acceptable under the claim-sizing rule as long as it stays a single value and the score stays `8 -> 8`, as preregistered.

Smallest safe correction: in `measure`, replace the phrase "every /slots n_ctx" with "the /slots n_ctx list" (it removes the universal word; the bound command enumerates the list anyway). Add a `learning_value` note: "entry rows each cite a pinned source line plus the receipt cell that confirms it; a row with no confirming cell is labelled source-only". Do not count prediction matches toward the claim value; `preregistration.json:52` already says this, so keep it.

## 6. A 260K-parameter fixture cannot carry an unscoped knowledge entry; the required limits

Evidence: fixture metadata from `python3 gguf-kv.py ~/.cache/kama-shokunin/models/stories260K.gguf` (exit 0, `gguf-kv.out`):
- `general.architecture = llama`, `llama.context_length = 2048`.
- `llama.block_count = 5`, `llama.embedding_length = 64`.
- `llama.attention.head_count = 8`, `llama.attention.head_count_kv = 4`.
- No sliding-window (SWA) key and no rope-scaling or YaRN key.
- sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.

Mechanisms this fixture cannot exercise, each a counterexample to generalizing:

(a) Memory fitting. `--fit` defaults to on (help text: "'off', default: 'on'"; common.h:483). For a model whose KV cache does not fit, fit can lower the context, with a floor of 4096 per stream (common.h:485; fit.cpp:426-430). An explicit `-c 0` turns that reduction off: "disable context reduction in llama_params_fit if the user explicitly requests the full context size" (arg.cpp:1647). So K1 (`-c 0`) is not the same as omitting `-c`, and on a large model the two can serve different n_ctx. On this fixture the KV cache is about 640 bytes per token [INFERENCE: 5 layers × 4 KV heads × 8 head dimensions × K and V × 2 bytes], so fit never binds.

(b) YaRN or rope scaling. `n_ctx_train` can be re-derived at load: "custom YaRN scaling detected, re-adjusting n_ctx_train" (llama-context.cpp:4115). So the K5 cap is "n_ctx_train after load", not always GGUF `context_length`.

(c) Sliding-window, hybrid and recurrent models (`--swa-full`, server-context.cpp:1340-1346): their caches are sized differently. Not exercised.

(d) One build (b11755, 704366d76). `--kv-unified-per-slot` is a recent flag ("default: unset, behavior unchanged", help text). Its behavior and the auto-slot default are build-specific.

(e) `n_ctx_train = 2048` coincides with the round number 2048 used by `-c` in K2 and K3. The fixture cannot tell "-c" from "train cap" when they are equal.

Smallest safe correction: the entry carries a `scope:` block naming build 11755/704366d76, the fixture sha256 and architecture, n_ctx_train 2048, "no SWA, no rope scaling, CPU-sized KV cache: `--fit` never binds". It also needs a `does-not-establish:` line: served n_ctx on registered consumers or large models; omitted `-c` versus `-c 0` under memory pressure; other builds; other engines. SKILL.md decision rows must quote that scope and not drop it.

# Sources (all pinned to commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, opened 2026-10-22; copies with sha256 in `/fast/scratch/hyaku/kama-r25/CriticC2Sizing/sources.sha256`)

- S-a https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp#L377-L392 — "cparams.n_ctx = GGML_PAD(cparams.n_ctx, 256);" … "cparams.n_ctx_seq = cparams.n_ctx / cparams.n_seq_max;" … "rounding down to %u" (L377, L382, L391)
- S-b https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L4654-L4663 — "context size of a single slot, capped by --kv-unified-per-slot and by the training context of the model" (L4654)
- S-c same file #L5186 and #L5236 — `{"n_ctx",       meta.slot_n_ctx},` (L5186); `{ "n_ctx",  meta.slot_n_ctx },` (L5236); #L1437 `slot.n_ctx   = n_ctx_slot();`
- S-d https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp#L169-L187 — "n_parallel is set to auto, using n_parallel = 4 and kv_unified = true" (L170); "params.n_ctx = params.n_parallel * params.kv_unified_per_slot;" (L184)
- S-e https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp#L1644-L1648 — "disable context reduction in llama_params_fit if the user explicitly requests the full context size" (L1647)
- S-f https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/common.h#L580 — "bool kv_unified        = false; // enable unified KV cache" (L580); L485 "int32_t fit_params_min_ctx = 4096;"
- S-g https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp#L4113-L4117 — "custom YaRN scaling detected, re-adjusting n_ctx_train(%u)..." (L4115)
- S-h https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp#L426-L430 — "cparams->n_ctx = std::max(cparams->n_ctx - cparams->n_ctx % align, n_ctx_min_total);" (L430)

# Files written

- `.ufo/waves/round-25/build/advice/CriticC2Sizing.md` (this report)
- `.ufo/waves/round-25/build/out/CriticC2Sizing/gguf-kv.py`, `gguf-kv.out`
- `.ufo/waves/round-25/build/out/CriticC2Sizing/source-model.py`, `source-model.out`
- `.ufo/waves/round-25/build/out/CriticC2Sizing/counting-counterexample.sh`, `counting-counterexample.out`
- Scratch: `/fast/scratch/hyaku/kama-r25/CriticC2Sizing/` (pinned source copies, `sources.sha256`, `receipts/` synthetic trees)

Tool installs: none. No llama-server child was started; no port was opened.
