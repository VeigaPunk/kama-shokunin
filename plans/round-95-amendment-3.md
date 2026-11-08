# Round 95 — amendment 3 (C1 repaired after the wave falsified its first revision)

Date: 2026-11-08. Author: L1 `KamaR95`. Frozen plan `plans/round-95-claims.md` (`c798e831`); amendment 1
(`719214fa`), amendment 2 (`7db1c54a`). This file records the wave's falsification of C1's first revision and the
repair, so the claim is filed on the property the repaired probe and the frozen counter actually enforce.

## What the wave falsified in the first revision (`f6325660`)

`.ufo/waves/round-95/w1/RV01ProbeDiff.md` (verdict `falsified`):

- **BLOCKER-1 — the verdict was still a wall-clock function, at the pass level.** One candidate naming one
  49M-element KV file decides `invalid` in 766 014 steps at 8.4 s user CPU; the wrapper's `timeout 35` then decided
  whether that line existed. Identical bytes and command produced `0 invalid` → `MODEL_UNLOADED
  router-model-invalid` and *no line* → `nbad=0 < ncand` → `MODEL_OK router-unloaded-autoload` across runs at
  load1 155–158. The round-94 defect was relocated from `ROUTER_PY` into the wrapper.
- **DEFECT-2 — `MAX_STEPS` did not price the parser's work.** `skip_strings` charged `steps += n // 64` after
  iterating `n` elements and never charged the per-element `unpack_from`, so a 49M-element array cost 766 014 steps
  for 8 s of CPU while a genuine 4 000 001-step parse cost ~2 s: the budget had no relation to the work, and the
  `15 s` per-candidate derivation was unsound.
- **DEFECT-3 — a reproduced regression.** `ncand` counts entries, but `file_state` parses every path occurrence, so a
  single candidate naming three distinct 200 MB files got a 35 s allowance where the round-94 probe's `timeout 60`
  finished the same listing in 30.4 s: base-green → new-red. The source comment "ncand over-estimates the work" was
  false for distinct paths.
- **NOTE-6 — the plan's own numbers.** The frozen plan describes the W03 cell as "twenty distinct slow files"
  (~50 s); the counter's committed bytes carry `SLOW_FILES = 40` (~82 s). The plan's prose was wrong, not the
  counter; recorded here rather than repaired, because the plan is frozen.

## The repair (`c810f51e`, revision M1b)

1. **Every string element costs a step** (`tools/kama-probe.sh` `skip_strings`): the bulk `n // 64` credit is gone,
   so `MAX_STEPS` bounds the parser's actual work and the budget is a function of the bytes alone.
2. **The pass allowance prices paths, not entries**: `ROUTER_PY` gained a `count` verb (the number of model-path
   occurrences across the candidate entries) and `router_file_states` runs `20 + 25 * npaths` seconds instead of
   `20 + 15 * ncand`. The three-distinct-200 MB-path shape that regressed now gets 95 s, above the round-94 probe's
   60 s constant, and still completes when the bytes decide.

## Filed property (C1)

At M1b `c810f51e`, `python3 tools/round95-router-budget.py --repo . --rev c810f51e --work <scratch>` prints
`ROUTER_BUDGET95 cells=10 mismatches=0 positive_mismatches=0 load_cells=10 load_stable=1 budget=work probe=rev …`
and exits 0 (`.ufo/waves/round-95/measured/c1-m1b.out`: `cells=10 mismatches=0 positive_mismatches=0 load_cells=10
load_stable=1 budget=work probe=rev … w03_seconds=99.7 load1_nat=137.85`, W03 graded `MODEL_UNLOADED
router-model-invalid` at 99.66 s natural and 179.25 s under the burners — inside the 1020 s path-priced allowance),
the counter's bytes identical to the freeze commit
`c798e831`; every cell's verdict and reason are identical at natural load and under the counter's synthetic CPU
load and equal that cell's frozen expectation; and the pass-level allowance is proportional to the number of model
paths the candidate entries name (the `count` verb), not to their count.

**Disclosed limits (filed, not hidden):**

- A candidate that needs more than `MAX_STEPS` (4 000 000) steps is `-` (undecidable → loadable, round-89 rule)
  **deterministically**. With per-element charging that now includes a KV array of ≥4M strings, which the
  pre-round-95 probe could decide `invalid` on an idle host. Determinism is bought with decisiveness on that shape;
  cell `W09` grades the tensors case and this note covers the string case.
- The wrapper is still a wall clock at the pass level. It is now priced by paths, but a listing of very many very
  large distinct files can still exceed it; that is a bound on the pass, not on the per-file decision.
- A slow `/props` answer still decides the verdict (round-94 SC02 F4) — routed to round 96.

## Consequence for the round

C1's first revision is **not** filed as verified: RV01 falsified it and reproduced a regression. It is filed as
verified **only** on the repaired revision and the property above, with the wave's receipt as the falsifier and the
repair commit as the delta. If the repaired counter run is not green, the claim is an honest stop and this file is
the narrowing that withdraws it.
