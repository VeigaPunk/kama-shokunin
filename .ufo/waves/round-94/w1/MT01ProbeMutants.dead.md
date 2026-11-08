# MT01ProbeMutants — settled dead by the dispatcher, delivered late (kama r94 w1)

Seat role: mutation-tester (attack). Spawned 2026-11-07T23:42:06 with the rest of wave `w1`.

**Settlement.** The orchestrator's dispatcher lost its handle in a kernel restart mid-wave
(`handles['MT01ProbeMutants']` was `None`, not a hung agent), so the seat was settled as **dead** at
the wave close and its `w1-results.json` row carries
`<output unavailable: FileNotFoundError('Output not found: MT01ProbeMutants-5…')>`. It was never
replaced (protocol: never replace a dead seat).

**Late delivery.** The agent kept running after the settle and wrote its artifacts at 01:43–01:45:
`.ufo/waves/round-94/w1/MT01ProbeMutants.md` (10 358 B) and
`.ufo/waves/round-94/w1/out/MT01ProbeMutants/` (129 files: `mutants/M01..M14` + diffs, `mutants.tsv`,
`logs/`, `direct/`, `scripts/`). This file records both facts: the seat is dead in the round census,
and its artifact exists and is reconciled in `claim-falsification.tsv`.

**What its artifact reports** (verbatim sources in the report file): 14 single-point mutants of the M1
probe run through the frozen C1 counter — 7 killed, 7 survived; 4 survivors are coverage gaps with
separating inputs (an 8-distinct-slow-file listing for the per-invocation budget M02, a mid-invocation
same-size rewrite with restored mtime for the ctime-less key M12, a 2M-tensor sparse header for M14,
a ~20-file listing that reaches the 60 s wrapper for M10); M04/M05/M11 are measured equivalents (the
MAX_STEPS and wall bounds are crossed within ±10 % of each other). It also reports BLOCKER-1 (the
frozen plan's F1 control — "a per-call (not per-file) deadline → the synthetic-load cell red" — does
not hold: that shape is green at load1 323), DEFECT-2 (`controls/c1-forgeries.py` does not exist),
DEFECT-4 (`round89-unloadable-cells.py` is unrunnable after 00:11 unless `LLAMA_CACHE`/`HF_HOME`
point at an empty dir, because a cache-sourced router model makes its identity guard abort), NOTE-1
(the counter's cell budget is 30 s, not the plan's "20 s"), NOTE-2 (K1 as worded is narrower than the
counter's exit condition: `bad>0` also exits 1).
