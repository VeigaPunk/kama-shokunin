# Round 96 — amendment 6 (W13 grades that the cap is load-bearing)

Date: 2026-11-08. Author: L1 `KamaR96`. Amendment 5 `20317286`-line; this amendment lands the one cell
wave-1 `MT01ProbeMutants` proved missing.

## The gap, measured

MT01 built four probe mutants and ran every frozen cell against each:

| mutant | cells | verdict |
|---|---|---|
| M1-nostepcap (budget removed) | 12/12 identical | **SURVIVED** |
| M3-noheadercharge (per-header charging removed) | 12/12 identical | **SURVIVED** |
| M4-maxmeta100m | 12/12 identical | **SURVIVED** |
| M5-noctime | 12/12 identical | **SURVIVED** |

Cause: every frozen fixture's *complete* parse also ends `-`, and `file_state` maps both `ok` and `-` to
`-`, so no cell can tell a bounded parse from an unbounded one. MT01 also proposed the would-kill
fixture (`WK-budget`): a file whose capped parse is `-` but whose uncapped parse reaches a deliberately
wrong tensor offset and returns `invalid`.

## The cell

`W13-budget-kill` — `budgetkill.gguf`, 54 000 083 B: the same 6 000 000 × 9-byte interleaved string array
as W12, followed by one tensor header (name `t0`, nd 1, ne 1, F32) whose declared offset is `1 << 40`.
Expectation `MODEL_OK/router-unloaded-autoload` (the capped state is `-`).

Measured through the probe's own `Runner`/`Stub` at `tools/kama-probe.sh`:

```
capped  (MAX_STEPS = 5 000 000): MODEL_OK/router-unloaded-autoload           0.72 s
uncapped(MAX_STEPS = 10**12):     MODEL_UNLOADED/router-model-invalid       0.87 s
```

So the mutant MT01 showed surviving now reddens W13: the cell grades the cap's *existence*, not only the
700 000-tensor outcome. `cells=` becomes 13; the C1 predicate is restated in this amendment.

## Predicate (C1, supersedes amendment 5's line for C1)

`python3 tools/round96-router-budget.py --repo . --rev <M1> --work <private> --slow-files 96` prints
`ROUTER_BUDGET96 cells=13 mismatches=0 positive_mismatches=0 load_cells=13 load_stable=1` and exits 0;
the base control (`--rev 5d43528b --burners 0 --allow-clock`) prints `cells=13 mismatches=1
positive_mismatches=1` with W11-700k red and every other cell green.

## Still disclosed, not repaired (round 97)

- M3 (per-header charging removed) still survives: the fixture set has nothing between the 833 332-header
  ceiling and `MAX_TENSORS = 1 000 000`, so a probe that stopped charging per header would pass. The fix
  is a W14 in that band, which needs its own timing measurement (a 900 000-header file costs ~5.4 M steps
  of CPU).
- M4 (`MAX_META` lowered) and M5 (ctime removed from the memo key) survive for the reasons round 95
  recorded (no cell reaches a >100 MiB header; the rewrite cell re-reads in a fresh process).
