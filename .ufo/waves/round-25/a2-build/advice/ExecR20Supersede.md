# ExecR20Supersede — advice (round 25, attempt 2, wave 1)

Verdict: round-20 `nctx-crosscheck.py` predict() agrees with the amendment-2 source-derived values on 9 of 10 graded config cells and disagrees on X1 (predict 512 vs amendment 2048), confirming the supersession target; the round-20 rule is wrong for an unset context with a split (non-unified) KV cache, and the only copy of the rule in lane scope is the round-20 script itself.

Method: imported `predict()` unchanged from `.ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py`, evaluated on all 11 amendment-2 config cells with `n_ctx_train = 2048` (stories260K.gguf), compared against the source-derived per-slot values in `preregistration-amendment-2.json`. No llama-server child was started (no port probed, no server launched).

## Table (cell -> round-20 value -> amendment value -> agree)

Script: `.ufo/waves/round-25/a2-build/out/ExecR20Supersede/eval-round20-predict.py`, run 2026-10-22, exit 0.

| cell | args (registered) | round-20 predict per-slot | amendment per-slot | agree |
|---|---|---|---|---|
| K1 | `-c 0` | 2048 | 2048 (training context) | yes |
| K2 | `-c 2048 -np 2 --no-kv-unified` | 1024 | 1024 | yes |
| K3 | `-c 2048 -np 2 --kv-unified` | 2048 | 2048 | yes |
| K4 | `-c 1024 -np 1` | 1024 | 1024 | yes |
| K5 | `-c 4096 -np 1` | 2048 | 2048 (capped at training) | yes |
| K6 | `-c 1000 -np 3 --no-kv-unified` | 512 | none (amendment: unknown, recorded as observed) | N/A |
| K7 | `-np 2 --kv-unified-per-slot 512` | 512 | 512 | yes |
| K8 | `-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512` | 512 | 512 | yes |
| X1 | `-np 4 --no-kv-unified` | 512 | 2048 (source path, CriticLearningBar) | **NO** |
| X2 | `-c 8192 -np 4 --no-kv-unified` | 2048 | 2048 | yes |
| X3 | `-np 4 --no-kv-unified --fit off` | 512 | 512 (author inference) | yes |

Load cells L1/L3 reuse the K1 args, L2 reuses the X2 args; their round-20 values are identical to those rows (2048/1024 not applicable — they are request-behavior cells, not rule cells).

## Finding 1 — X1: round-20 is wrong (supersession trigger)

`predict(0, 2048, 4, False, 0)` at `nctx-crosscheck.py:38-44` returns 512: unset ctx (`ctx=0`) falls back to `n_ctx_train` (2048), padded to 2048, then split non-unified across 4 parallel slots -> `pad256(2048//4) = 512`. Amendment-2 X1 asserts the served per-slot value is 2048 (pool 8192) via the fit path in `common/fit.cpp` (an unset context with a split cache is fitted to `n_ctx_train * n_streams`). The two disagree; per amendment-2 C2.learning_artifacts this is the explicit supersession note for round-20 `nctx-crosscheck.py`. The amendment source-derived value is taken as authoritative for this comparison; a live server run (executor bench) is the final arbiter, out of scope for this read-only seat.

## Finding 2 — X3: round-20 cannot see `--fit` at all

The round-20 parser `launch_settings()` (`nctx-crosscheck.py:47-71`) raises `Unusable("argv element '--fit' is not modelled")` on the X3 args `-np 4 --no-kv-unified --fit off` (probed, exit 0 print). So the round-20 tool cannot evaluate X3 as a receipt; the 512 that matches the amendment is the plain split value and does not model fit off. The rule copy does not know `--fit` exists.

## Finding 3 — K6 has no amendment value

K6 (`-c 1000 -np 3 --no-kv-unified`) is deliberately ungraded in amendment 2 ("unknown: padding of n_ctx and per-sequence division; recorded as observed"). round-20 predicts 512. Agree column is N/A; K6 is a pure measurement cell.

## Finding 4 — copies of the rule

Grep of the lane paths for `n_ctx_slot|kv_unified|per_slot|n_ctx_seq|pad256|GGML_PAD|nctx-crosscheck|n_ctx_train` and secondary pass `per-slot|per_slot|slot_n_ctx|n_ctx_seq|kv-unified` + `n_ctx|ctx_size|nctx`:

- tools/ — no matches. No tool implements or copies the rule.
- tests/ — no matches. Fixture JSON data only (`tests/llamacpp-live/check-receipt.py:1733-1734`, `controls.py:305`, `probe-verdicts/EnvelopeShapes.json:154`, `ReadyControls.json:20` are values, not a rule).
- SKILL.md — `SKILL.md:664-667` only: an admonition that `/props` per-slot `n_ctx` "must not be computed as `ctx / total_slots` unconditionally (S060)". Warning against the naive rule; not a copy.
- corpus/knowledge/ — `gguf-declared-identity.md:27-32` and `:40-44` prose describing the `n_ctx_slot()` cap and the same division warning; other files only record served values (e.g. `served-model-identity.md:21` n_ctx 16384 of a foreign consumer). No computation copy.
- corpus/SOURCES.md — rows S058/S060 (`SOURCES.md:71-72`) cite the upstream llama.cpp lines (4654-4663 etc.); citations, not copies.
- The only implementation of the rule is the round-20 artifact itself: `nctx-crosscheck.py` `predict()` lines 38-44, `pad256()` lines 34-35, `launch_settings()` lines 47-71, `table()` lines 118-125, next to `pins.txt` and `row-draft.md` in `.ufo/waves/round-20/build/out/SrcServerNctx/`.

Conclusion: no lane file copies the rule; the supersession note (amendment-2 learning artifact) should point at the single round-20 location above.

## Files written

- `.ufo/waves/round-25/a2-build/out/ExecR20Supersede/eval-round20-predict.py` (evaluator; imports round-20 predict() unchanged)
- `.ufo/waves/round-25/a2-build/advice/ExecR20Supersede.md` (this report)

## Evidence

- Round-20 source imported from `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py` (read at lines 34-44, 47-71, 118-125).
- Amendment-2 cells and values from `preregistration-amendment-2.json` C2.cells_added and `preregistration.json` C2.cells.
- Evaluator run: exit 0, table above.
- `launch_settings` probe on all 11 args: K1-K8, X1, X2 parse identical to the registered args; X3 raises Unusable on `--fit`.
- No server started; no port touched; no tools installed.

## Risks / blockers

- The amendment source-derived X1 value (2048) is a source reading, not a live observation; the executor bench run of X1 is the binding evidence. This seat did not run a server, per assignment.
- K7's amendment pool wording ("pool 1024") differs from the formula's padded pool (2048); the per-slot value (512) is what the rule outputs and it agrees. Pool sizing is log-only evidence for the executor bench.
