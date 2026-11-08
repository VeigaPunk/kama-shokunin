# EX02BudgetControl — round 98 C2 operability: proving the budget counter can fail

Seat: EX02BudgetControl (leaf). Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`,
`master` = `34ad44e9f783b35a804f020d6b02c48c04ade481` (round-98 freeze commit;
base `681c80a4` is its parent). Counter: `tools/round98-router-budget.py`
(bytes as frozen at `34ad44e9`; not edited, not re-graded — this seat only re-runs
its control modes as a falsification check). Scratch:
`/fast/scratch/hyaku/kama-r98/EX02BudgetControl/` (removed before yield).

No tools were installed or upgraded (python3 only, already present). No tracked
lane file was modified; no git/jj mutation was run (read-only `log`/`rev-parse`
only).

## 1. Mutant controls (new cells, `--cells new` = 6 cells)

### 1a. flat6 caught at W15-700k-nd4

Command (as assigned):

```
python3 tools/round98-router-budget.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --rev master --work /fast/scratch/hyaku/kama-r98/EX02BudgetControl \
  --cells new --control --expect caught --mutant flat6 --expect-cell W15-700k-nd4 --slow-files 72
```

Summary line (verbatim):

```
ROUTER_BUDGET98_CONTROL cells=6 cells_ok=5 mutant=flat6 slow_files=72 runs=1 expect=caught expect_cell=W15-700k-nd4 cell_ok=0 survived=0 caught=1 probe=rev probe_sha256=6f543d16b73e85ae4f9aa2dbae713879b12c1b1a9370e6b14c32d6892c39df38 rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=1
```

Exit: `0`. Wall time ~30 s. Full per-cell lines pasted from the run:

```
ROUTER_BUDGET98_CELL nat W14-900k-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.08s entries=0
ROUTER_BUDGET98_CELL nat W15-700k-nd4 ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/2.13s entries=0
ROUTER_BUDGET98_CELL nat W16-maxmeta ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.23s entries=0
ROUTER_BUDGET98_CELL nat W17-833333-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.29s entries=0
ROUTER_BUDGET98_CELL nat W18-800k-nd1 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/2.19s entries=0
ROUTER_BUDGET98_CELL nat W19-520k-nd4 ok=1 want=MODEL_UNLOADED majet/router-model-invalid/1.81s entries=0
```

(Note: the last line above is transcribed; the run's actual line read
`ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/1.81s entries=0`
— receipt file `EX02BudgetControl/flat6.out` in scratch held the verbatim output
before scratch removal; the control summary line `caught=1` is unaffected.)

### 1b. overcharge caught at W18-800k-nd1

Command (as assigned):

```
python3 tools/round98-router-budget.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --rev master --work /fast/scratch/hyaku/kama-r98/EX02BudgetControl \
  --cells new --control --expect caught --mutant overcharge --expect-cell W18-800k-nd1 --slow-files 72
```

Summary line (verbatim):

```
ROUTER_BUDGET98_CONTROL cells=6 cells_ok=4 mutant=overcharge slow_files=72 runs=1 expect=caught expect_cell=W18-800k-nd1 cell_ok=0 survived=0 caught=1 probe=rev probe_sha256=b7bdbfae4ec8757b5fcfe34874fa720955df71a187f5ddbfaca29ea3838d6219 rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=1
```

Exit: `0`. Wall time ~30 s. Per-cell lines (verbatim):

```
ROUTER_BUDGET98_CELL nat W14-900k-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/1.86s entries=0
ROUTER_BUDGET98_CELL nat W15-700k-nd4 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/1.91s entries=0
ROUTER_BUDGET98_CELL nat W16-maxmeta ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.17s entries=0
ROUTER_BUDGET98_CELL nat W17-833333-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.06s entries=0
ROUTER_BUDGET98_CELL nat W18-800k-nd1 ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/2.01s entries=0
ROUTER_BUDGET98_CELL nat W19-520k-nd4 ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/2.27s entries=0
```

Both W18 and W19 redden under `overcharge` (the counter prints `cells_ok=4`,
two reds); `--expect-cell W18-800k-nd1` is satisfied with `cell_ok=0 caught=1`.
This matches the plan's claim that W19 also catches (second row of the
`controls/c2-new-mutants.out` freeze receipt). The control is **not** a
generic "at least one red" — `expect-cell` names the cell that must redden and
the counter would print `ok=0`/exit≠0 if it did not.

## 2. Do-nothing control (17 round-97 cells, overcharge mutant)

Command (as assigned):

```
python3 tools/round98-router-budget.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --rev master --work /fast/scratch/hyaku/kama-r98/EX02BudgetControl/r \
  --cells r97set --control --expect survived --mutant overcharge --slow-files 72
```

Summary line (verbatim):

```
ROUTER_BUDGET98_CONTROL cells=17 cells_ok=17 mutant=overcharge slow_files=72 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=rev probe_sha256=b7bdbfae4ec8757b5fcfe34874fa720955df71a187f5ddbfaca29ea3838d6219 rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=1
```

Exit: `0`. Wall time ~190 s (dominated by W03-slow-x40 at 94.6 s). All 17
cells `ok=1`, including the two-invocation W10 rewrite cell and the
`budgetkill` W13 cell. `survived=1` — the overcharge probe passes the entire
round-97 set.

This reproduces the freeze-time receipt
`.ufo/waves/round-98/controls/c2-legacy-mutants.out` exactly in its verdict
(`cells=17 cells_ok=17 … survived=1 caught=0`), differing only in run duration
(the freeze run's W03 took 152 s vs 95 s here — host-speed variance, same
verdict) and `rev` (`681c80a4` at freeze vs `34ad44e9` here; the probe bytes
are identical, `probe_sha256=b7bdbfae…` in both).

## 3. Are the new cells sized past the forgery? (independent arithmetic check)

Recomputed from `MAX_STEPS = 5,000,000` with `steps = 4 + T×(5+nd)` (real) vs
`4 + T×(6+nd)` (+1/header overcharge) vs `4 + T×6` (flat6), independent of the
counter:

| cell | T | nd | real steps | +1 probe steps | real≤MAX? | over≤MAX? | flat6≤MAX? |
|------|-----|----|------------|----------------|-----------|-----------|------------|
| W18-800k-nd1 | 800,000 | 1 | 4,800,004 | 5,600,004 | yes (`invalid`) | **no** (`-`) | yes |
| W19-520k-nd4 | 520,000 | 4 | 4,680,004 | 5,200,004 | yes (`invalid`) | **no** (`-`) | yes |
| W15-700k-nd4 | 700,000 | 4 | 6,300,004 | 7,000,004 | no (`-`) | no | **yes** |
| W14-900k-nd1 | 900,000 | 1 | 5,400,004 | 6,300,004 | no | no | no |
| W17-833333-nd1 | 833,333 | 1 | 5,000,002 | 5,833,335 | no | no | no |

Both new cells sit strictly inside the +1 window the plan names
(`714,286 < T ≤ 833,332` at nd=1; `500,000 < T ≤ 555,555` at nd=4): the real
parse decides `invalid` while the +1 parse flips to `-`. The cells are sized
past the forgery, and the direction is right — they expect the decidable
verdict, so the overcharge probe reddens (verified live in 1b, both W18 and
W19 flipped to `MODEL_OK`, i.e. `-` → loadable). The flat6 catch at W15 is the
mirror image: real is undecidable (`-`, `MODEL_OK` expected) while a
constant-6 charge decides `invalid` (`MODEL_UNLOADED`) — verified live in 1a.

## 4. Are the control receipts honest?

Yes — this seat's re-runs match the freeze receipts in every verdict-bearing
field (mutant, cell set, `expect_cell`, `cell_ok`, `caught`/`survived`,
`probe_sha256`, exit):

- `flat6` → `caught=1` at `W15-700k-nd4`, `probe_sha256=6f543d16…` — matches
  `controls/c2-new-mutants.out` (freeze-time flat6 row).
- `overcharge` → `caught=1` at `W18-800k-nd1`, `probe_sha256=b7bdbfae…` —
  matches the freeze-time overcharge row (which also showed W19 red; this run
  reproduced that too).
- r97set `overcharge` → `survived=1`, `cells_ok=17`, same probe hash —
  matches `controls/c2-legacy-mutants.out` (`survived=1`, `cells_ok=17`).

Caveat on my transcription, not the receipts: the freeze at `681c80a4` also
graded the real probe (`mutant=none`) green on all six new cells, and the
other three mutants (undercharge→W14, maxmeta→W16, nopreamble→W17). This seat
was assigned only flat6, overcharge and the r97set do-nothing control, so
those rows were not re-run here; the L1's `measured/c2.out` and the freeze
file remain the record for them. Nothing in this run contradicts them.

One transcription error of mine in §1a (a stray word in the pasted W19 line)
does not touch the control summary line; the verbatim summary lines above are
copied from the run output and are the verdict-bearing strings.

## 5. Do the controls prove what the plan says they prove?

- **D2 falsifiability ("the counter can fail")**: proven by §1 — both mutant
  controls exit 0 only because the named `expect-cell` reddened with the
  expected verdict flip, with the correct probe hash per mutant. A
  counter that rubber-stamped `caught=1` without running the probe would not
  reproduce the W15/W18 verdict pairs (`MODEL_UNLOADED`↔`MODEL_OK` flips in
  opposite directions for flat6 vs overcharge), which are the actual probe
  outputs.
- **Do-nothing control**: §2 proves the 17-cell set cannot discriminate the
  +1/header forgery (all 17 green under `overcharge`, `survived=1`) while
  the new set does (§1b). That is precisely the plan's C2 control pair, and
  the two together close RV03 F5's window rather than merely asserting it.
- **Limits**: these are control runs (natural pass only, `--control`), exactly
  as the plan scopes them; they say nothing about the full predicate (both
  host loads, `cells=19`) — that is `measured/c2.out`'s job at M2, not this
  seat's. Per the plan's disclosed limit (a), none of this grades a probe
  that mis-charges non-header steps (KV, string elements); the seam the
  overcharge mutant covers is the per-header loop alone.

## Verdict

The new budget counter can fail, and in this round's own hands it did fail —
the flat6 and overcharge mutants were caught at their named cells, and the
17-cell do-nothing control survived exactly as the falsifying artifact
predicted. The cells are sized inside the +1 window on both nd=1 and nd=4
sides, and the freeze-time and measurement-time control receipts agree in
every verdict-bearing field.

Files changed: only this report
(`.ufo/waves/round-98/w1/EX02BudgetControl.md`). Scratch
`/fast/scratch/hyaku/kama-r98/EX02BudgetControl/` removed after copying
receipts into this report.
