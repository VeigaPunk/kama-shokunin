# ScoutR20Entry — round-20 context-rule passages versus X1

**Verdict:** X1 observed **per-slot 2048 with pool 8192** (X3 with `--fit off` observed 512), so it contradicts the round-20 *predictor artifact* and four round-20 analysis sentences, but **no landed corpus, SKILL or SCORECARD sentence**; the frontier lines the round advances are `corpus/README.md:295-298` and the K05 entries of the seven "still open" lines, while `:297-298` (registered consumers, other engines, loaded-weight authentication, model quality) stays unclaimed.

Seat: `KamaR25a2.ScoutR20Entry` (scout, wave 1 attempt 2). Read-only; no server; no production edit.

## 1. Observed state used for the verdict

The lane advanced from the assignment's tip `1fc41e3` to `c808ba0` (amendment 3 plus the committed C2 receipt). `git diff --stat 1fc41e3 -- <all measured files>` printed nothing and exited 0, so every passage below is byte-identical at both revisions.

The conditional in the assignment ("if X1 serves per-slot 2048") is already answered by the lane-committed receipt — I read it, I did not run it:

- `.ufo/waves/round-25/final/context-capacity-receipt.json` sha256 `fe378502e84a379badf94423ca7a34586503b410672450eaf5fb9fe3fe3c158b`
  - X1 `-np 4 --no-kv-unified`: `observed true`, `/props` 2048, `/slots` `[2048,2048,2048,2048]`, `meta.n_ctx_train` 2048, pool 8192, pool candidates `[2048,8192,8192]`
  - X3 `-np 4 --no-kv-unified --fit off`: `/props` 512, `/slots` `[512×4]`, pool 2048
  - K1 `-c 0`: `/props` 2048, `/slots` `[2048×4]`, pool 2048
- `python3 .ufo/waves/round-25/count-c2.py` → `registered 14 observed 14 bound True missing []`, exit 0.

The round-20 predictor disagrees:

- `python3 .ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py --table` exited 0; its last row is `0  4  false  2048  512`.
- Direct call `predict(0,2048,4,False,0)` → `(512, 4, False)`, exit 0.

The mechanism is `common/fit.cpp` (never in the round-20 `pins.txt`; the advice called it an unopened unknown): `fit.cpp:197` sets `n_streams` to `n_seq_max` when KV is split; `fit.cpp:267` computes `n_ctx_max = n_ctx_train * n_streams` = 8192; `fit.cpp:271-272` assigns that to an unset `n_ctx`. `llama-context.cpp:377-383` then pads 8192 and divides by 4 → 2048; `server-context.cpp:4654-4663` caps the slot at training context 2048. Fresh pins, URLs and quotes are in `out/ScoutR20Entry/evidence.md` §4.

## 2. Passage table

`Yes` means X1's observed per-slot 2048 changes that passage's truth value. `No` means the sentence survives; several "No" rows are incomplete rather than wrong, and the note says how.

| Path:line | Quote (≤25 words) | Affected by X1 |
|---|---|---|
| `corpus/knowledge/gguf-declared-identity.md:27-30` | "per-slot context is capped by --kv-unified-per-slot and the effective training context" | **No** — X1's 2048 is the capped per-slot value |
| `corpus/knowledge/gguf-declared-identity.md:31-32` | "Do not divide ctx by total_slots blindly: KV-unified and padding affect that relationship" | **No** — still a correct prohibition; X1 props/total would coincide only because the pool is 8192 |
| `corpus/knowledge/gguf-declared-identity.md:34-36` | "served n_ctx=256, training n_ctx_train=2048, and a GGUF declaration of 2048" | **No** — dated `-c 256` observation |
| `SKILL.md:658` | "declared context versus meta.n_ctx_train, not props.n_ctx equality" | **No** — comparison-target rule, unchanged |
| `SKILL.md:665-667` | "must not be computed as ctx / total_slots unconditionally" | **No** — same caution as line 31 |
| `corpus/SOURCES.md:72` | "single-model b11755 per-slot served context versus training-context metadata" | **No** — scope row |
| `corpus/lessons/round-20.md:53` | "context size of a single slot, capped by --kv-unified-per-slot and by the training context of the model" | **No** — X1's slot equals the cap |
| `corpus/lessons/round-20.md:148-150` | "Props256/slots4 remain informational with no division." | **No** — dated note |
| `SCORECARD.md:901` | "props256 informational" | **No** — dated evidence cell |
| `corpus/README.md:295-298` | "usable for historical comparison, not a new live endpoint sample" | **No** — this is the line the round advances |
| `.ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py:41-42` | "n_ctx_seq = n_ctx if kv_unified else pad256(n_ctx // n_parallel)" | **Yes** — executed `predict` returns 512; X1 observed 2048 |
| `.ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py:13-14` | "The model assumes that no --fit run lowered n_ctx" | **Yes** — fit also *raises* an unset context (probe 2048 → final 8192) |
| `.ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py:10-11` | "otherwise GGML_PAD(n_ctx / n_seq_max, 256)" | **No** — arithmetic right; input is 8192, not 2048 |
| `.ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py:120-122` | "(0, 2048, 4, False)" | **Yes** — the printed table case yields 512 |
| `.ufo/waves/round-20/build/advice/SrcServerNctx.md:4` | "/props is per-slot effective context, not ... an unconditional --ctx-size / --parallel quotient" | **No** — X1 props 2048 is the effective per-slot value |
| `.ufo/waves/round-20/build/advice/SrcServerNctx.md:6` | "n_ctx starts from explicit context size, or training context when zero" | **Yes at the server layer** — true inside `llama-context.cpp:219`, false after `fit.cpp:271-272` |
| `.ufo/waves/round-20/build/advice/SrcServerNctx.md:6` | "split KV uses GGML_PAD(n_ctx / n_seq_max, 256)" | **No** — holds for a pool of 8192 |
| `.ufo/waves/round-20/build/advice/SrcServerNctx.md:21-22` | "predicted=256 ... slots(naive ctx/slots=64)=no-match" | **No** — that receipt uses `-c 256`; the predictor behind it is the affected row above |
| `.ufo/waves/round-20/build/advice/SrcCtxTrainWarning.md:29` | "The effective per-slot size must reach D; -c 0 ... does not guarantee this when contexts are split across slots" | **No as written, qualified** — a non-guarantee; X1 shows fit closes the gap, so scope the caveat to `--fit off` (X3 = 512) |
| `.ufo/waves/round-20/build/advice/SrcCtxTrainWarning.md:30` | "Argv -c is not S, because padding can raise it" | **No, incomplete** — padding is one gap; fit is a second (X1 has no `-c` at all) |
| `.ufo/waves/round-20/build/advice/SrcCtxTrainWarning.md:36` | "-fit ... may lower an unset context to no less than 4096" | **Yes** — observed direction is raise (8192); the 4096 floor is per-stream and only in the reduce branch |
| `.ufo/waves/round-20/build/advice/KnowGguf.md:23` | "Served per-slot n_ctx is not train/slots." | **No** — 2048 ≠ 512 |
| `.ufo/waves/round-20/build/out/KnowGguf/gguf-declared-identity.md:42` | "n_ctx 0 means 'use the train context'" | **Yes at the server layer** — the landed entry dropped this sentence |
| `.ufo/waves/round-20/build/out/KnowGguf/gguf-declared-identity.md:43` | "With kv_unified, n_ctx_seq = n_ctx; otherwise n_ctx / n_seq_max, padded to 256" | **No** — formula holds |
| `.ufo/waves/round-20/build/advice/RevPropsNctx.md:18` | "every receipt has root ctx = 256, argv -c 256, and /props default_generation_settings.n_ctx = 256" | **No** — explicitly not a scaling rule |
| `.ufo/waves/round-20/build/advice/ConnectKengaku.md:21` | "every committed receipt and every kengaku capture has per-slot == total (O4/O6)" | **Yes to the premise** — X1 is 2048 per-slot against an 8192 total pool, so the "unfalsifiable" population claim falls |
| `.ufo/waves/round-20/build/advice/GgufTool.md:14` | "props.n_ctx=256 is displayed as informational and is not compared to training context 2048" | **No** — tool behavior |
| `.ufo/waves/round-20/c2/measure-reference.json:117` | "informational-only; not compared with training context" | **No** — same; also `tools/gguf-identity.py:618` |
| `.ufo/waves/round-20/build/advice/GgufReconcile.md:6` | "Classification is based on served n_ctx versus training context" | **No** — X1 served 2048 vs training 2048 is "within"; no division is applied |
| `.ufo/waves/round-20/build/out/SrcServerNctx/row-draft.md:7` | "context size of a single slot, capped by --kv-unified-per-slot and by the training context of the model" | **No** — cap statement |

Count: 30 passages; seven rows affected (`R1`, `R2`, `R4`, `R6`, `R11`, `R13`, `R16` in the JSON inventory); zero landed rows affected.

### The five prose/code corrections in words

1. `nctx-crosscheck.py:41-42` — for `ctx == 0`, `fit.cpp` has already replaced 0 with `n_ctx_train * n_streams` when fit is on; the predictor must either model `--fit` or report could-not-evaluate, as its own docstring already does for other unmodelled inputs.
2. `nctx-crosscheck.py:13-14` — the guard says "no --fit run lowered n_ctx", but the load-bearing effect here is a raise. Reword to "no --fit run changed n_ctx".
3. `SrcServerNctx.md:6` and the draft at `:42` — "0 means train context" is a statement about `llama-context.cpp:219`; the server pipeline inserts `fit.cpp:271-272`. Keep the library statement, add the parameter rewrite.
4. `SrcCtxTrainWarning.md:36` — `--fit` on an unset context sizes the pool to `n_ctx_train × n_streams`; the 4096 `fit_params_min_ctx` is a per-stream floor in the reduce branch, not a floor on the auto-size. The observed X1 pool is 8192, above it.
5. `SrcCtxTrainWarning.md:29` — keep the non-guarantee but bind it to `--fit off`: X3 (same args plus `--fit off`) is the 512 case the sentence describes.

### What the HTTP surfaces cannot show (passage consequence)

X1 and K1 agree on every context-bearing HTTP field: `/props` `default_generation_settings.n_ctx` 2048 and `total_slots` 4, `/slots` bodies byte-identical (`raw/K1.slots.body` and `raw/X1.slots.body` sha256 `6939aec1…`), `/v1/models` `meta.n_ctx` 2048 and `meta.n_ctx_train` 2048. Their raw `/props` bodies differ only in the per-run random `media_marker`; their `/v1/models` bodies differ only in the `created` timestamp. They differ in the `-v` log line `llama_context: n_ctx = 8192` versus `2048` (`raw/X1.server.log:812,1344`, `raw/K1.server.log:284,816`), and in concurrency capacity. X1 and X2 agree on every measured context field including the pool (8192); only argv differs, apart from the per-run `media_marker` and `created` values. So the round-20 crosscheck, which compared `/props`, `/slots` digests and the naive quotient, could not have distinguished these cells; the `kv_pool_n_ctx` requirement in `count-c2.py` and the last-candidate rule in amendment 3 are what make the claim checkable. This belongs in the new entry.

## 3. K05 frontier lines in `corpus/README.md`

| Line | Quote (≤25 words) | Does the round advance it |
|---|---|---|
| 63 | "no current runtime context is established" | **Partly** — a current dated lane-owned sample now exists; the snapshot-schema gap it also names remains |
| 71-72 | "Reconcile declared-vs-served context size only as a separate feature move when an authorized serving runtime permits" | **Yes** — this is that move on the lane-owned fixture (advance is conditional on L0 ratifying the fixture scope) |
| 125 | "K05 remains deferred until an authorized serving runtime exists." | **Historical** — already overtaken by the round-16 fixture; this round's sample is the current form |
| 142 | "K05 remains operator-runtime dependent." | **Historical** — dated round-12 disposition |
| 159-160 | "K05 context capacity remains dependent on an authorized serving runtime." | **Historical** — dated round-13 disposition |
| 173-174 | "K05 is still operator-runtime dependent." | **Historical** — dated round-14 disposition |
| 222 | "K05 declared-versus-served context" (round-16 still-open list) | **Partially** — the single-model configuration matrix advances; consumers and other engines do not |
| 244 | "K05 declared-versus-served context" (round-17 still-open list) | **Partially**, as above |
| 267 | "K05 declared-vs-served context" (round-18 still-open list) | **Partially**, as above |
| 295-297 | "usable for historical comparison, not a new live endpoint sample" | **Directly** — the committed receipt is a new live lane-owned sample, not a replay |
| 297-298 | "K05 across real registered consumers, other engines, loaded-weight authentication and model quality remain unclaimed" | **Not advanced** — keep this sentence intact; the round must not read as consumer or other-engine evidence |
| 313 | "K05/other-engine serving ... remain open" | **K05 half partially**; other-engine half untouched |
| 334 | "K05/other-engine serving and real registered-consumer reconciliation" | **K05 half partially**; consumers untouched |
| 355 | "K05/other-engine serving and real registered-consumer reconciliation" | **K05 half partially** |
| 388 | "K05/other-engine serving and real registered-consumer reconciliation" | **K05 half partially** |

The smallest honest frontier statement is: *advanced for one lane-owned single-model fixture across 14 registered configurations (context-pool sizing, fit, per-slot cap, concurrency); registered consumers, other engines, loaded-weight authentication and model quality remain unclaimed.*

## 4. Supersession scope — what the L1 should and should not write

No production errata is required. No landed file states the 512 prediction; the only superseded formula lives in round-20 build artifacts and advice. Specifically:

- Do **not** rewrite `corpus/knowledge/gguf-declared-identity.md:27-32`, `SKILL.md:658` or `SKILL.md:665-667`. They are correct, and X1 confirms the cap and the anti-division caution.
- Do **not** touch `corpus/README.md` historical dispositions at 125/142/159-160/173-174; they are dated statements, and the corpus rule is append-only.
- Put the supersession note in the new `corpus/knowledge/context-capacity.md` and the round lesson, naming: `nctx-crosscheck.py:13-14, 41-44, 120-122`, `SrcServerNctx.md:6`, `SrcCtxTrainWarning.md:36`, and the unlanded draft `out/KnowGguf/gguf-declared-identity.md:42`.
- State the corrected chain with source lines: `fit.cpp:195-198` (n_streams), `fit.cpp:266-273` (n_ctx_max and unset assignment), `llama-context.cpp:377-383` (pad and split), `server-context.cpp:4654-4663` (slot cap), `common.h:483,485` and `arg.cpp:1646-1648` (fit default and the `-c 0` exception), `server.cpp:169-173` (auto slots).
- Record that `--fit` is on by default and that `-c 0` disables only context *reduction* (`fit_params_min_ctx = UINT32_MAX`), not the auto-size assignment; X1 has neither `-c` nor `-c 0`.

## 5. Sources opened this round

All fetched fresh on 2026-10-22 at `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/<path>`, every `curl -sS -f -L --max-time 60` exited 0. Exact hashes, line counts and the full mechanism chain are in `out/ScoutR20Entry/evidence.md` §4. Quotes:

- `common/fit.cpp:196` — "if memory can hold more than model's trained context size, we must extend the n_ctx to hold enough n_streams" (22 words).
- `src/llama-context.cpp:380` — `cparams.n_ctx_seq = cparams.n_ctx / cparams.n_seq_max;` (8 tokens).
- `tools/server/server-context.cpp:4654` — "context size of a single slot, capped by --kv-unified-per-slot and by the training context of the model" (18 words).
- `common/common.h:483` — "whether to fit unset model/context parameters to free device memory" (10 words).
- `common/arg.cpp:1646-1648` — "disable context reduction in llama_params_fit if the user explicitly requests the full context size" (15 words).
- `tools/server/server.cpp:170` — "n_parallel is set to auto, using n_parallel = 4 and kv_unified = true" (14 words).

`server.cpp`, `arg.cpp` and `server-context.cpp` are byte-identical to the lane's round-16 snapshot (`cmp` exit 0). `fit.cpp`, `common.h`, `common.cpp` and `fit.h` are absent from that snapshot and were fetched fresh.

## 6. Remaining unknowns

- I did not run X1 or any cell; the 2048/8192 values are the L1's committed receipt (`5ea4fc44`), read by me. The counter run is mine (exit 0).
- The fit auto-size is deterministic for this model and host: the reduce branch requires `n_ctx_max > n_ctx_min_total` (8192 > 16384 false, `fit.cpp:394`), and the host-memory early return needs 1024 MiB free (`fit.cpp:323-327`). For a larger model or a tighter host the final pool can be reduced toward `4096 × n_streams`; the entry should not generalize "always 8192".
- Draft/MTP extra-model fitting (`fit.cpp:182`, `common.cpp:1259-1275`) was not traced; it does not apply to this fixture.
- Pool sharing across slots is inferred from the log and the L-cell error behaviour; this seat measured no occupancy.
- The frontier advance is conditional on L0 ratifying the round-16 lane-owned fixture scope, as the contract states.

Report: .ufo/waves/round-25/a2-build/advice/ScoutR20Entry.md
