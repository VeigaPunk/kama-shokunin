# MT21C2SelfdescSkip - C2 attack: selfdesc conjunct (round 63, kama)

Seat: mutation-tester, leaf (no dispatch). Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09`
(round-63 freeze amendment 1). Advisory finding only; no verdict on the C2 claim.
Receipts: `.ufo/waves/round-63/w1/out/MT21C2SelfdescSkip/`.
Tools installed: none (no installs or upgrades in this seat).

## Result (headline)

| run | counter | selfdesc_mismatches | met | verdict |
|---|---|---|---|---|
| unmutated (tip blob = 03a6a1d) | round63-c2-counter.py | 8 | False | as expected |
| mutant A: drop `selfdesc == 0` conjunct | committed clone T=05c21564 | 8 (computed, ignored) | True | SURVIVED |
| mutant B: `selfdesc_mismatches` returns 0 on nonzero reconciler exit | committed clone T=48bb3349 | 0 | True | SURVIVED |

Verbatim counter output (one line each, exit code on the next line):

```
unmutated: population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False   (exit=1)
mutA:      population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=True   (exit=0)
mutB:      population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=True   (exit=0)
```

- The unmutated counter is **False** at the committed tip, and it is False for exactly one reason:
  every other conjunct is green (baseline met: covered 12/12, mismatches 0, sensitive 12/12,
  sens_selftest 4/4, controls_rejected 12/12, errors 0). The reconciler's 8 is the only term
  holding `met` at False.
- Both mutants flip the counter to **met=True** at a tip whose reconciler reports 8 mismatches.
  Under the recipe rule, each is a SURVIVED mutant: the defect is present and the counter says met.

## Why the mutants survive (the defect in the counter / control set)

1. `selfdesc` is referenced in exactly three places in `round63-c2-counter.py`: the call at
   line 525, the conjunct at line 528 (`selfdesc == 0`), and the printed field at line 539.
   `controls()` never mutates the self-description, and none of the 12 control families
   names it. So the conjunct has no control that can reject its own removal. The 12 families
   (drop, rename, binding, verdict, quote, free, weak, notobs, hostbusy, duprow, observed,
   canon-drop) all act on registry or canonical-list text.
2. The sensitivity self-test (4 planted verdict functions) covers only the verdict function, not
   the reconciler gate.
3. `selfdesc_mismatches` (lines 466-476) already returns the printed count on a nonzero exit,
   so the gate depends on the reconciler's stdout alone. Mutant B makes the gate read 0 whenever
   the reconciler exits nonzero, which is the exact case where it reports mismatches.

Consequence: any future edit that drops or zeroes the selfdesc term keeps all 12 controls green
and the counter reports met=True at a tip with 8 known self-description mismatches. The
counter's "met" is only as strong as this one conjunct, and the control set does not test it.
(This is a counter/control-set finding, not a verdict on whether C2 is or is not met.)

Note for the L1: the freeze's rule "all 12 control families rejected" does not cover this
conjunct. Any fix (for example a 13th family that plants a reconciler-count or nonzero-exit
failure and requires met=False) changes the frozen control set, so it is for the planner to
decide; I have not proposed or applied one in the lane.

Unit check of mutant B's defect path (`unit-selfdesc.py`, receipt in out dir): with a stub
reconciler that exits 1 and prints no count, `selfdesc_mismatches` returns **None** unmutated
(so `selfdesc == 0` is False) and **0** under mutant B. So mutant B also converts a reconciler
crash (not only a reported mismatch) into a passing gate.

## Reconciler: working tree, tip, and scratch clones

Reading `tools/round42-selfdesc-reconcile.py` (and its import of
`tools/round41-scorecard-reconcile.py` from the script's own directory):

- Source reads are git-object reads at the tip: `git cat-file -p <tip>:<path>`,
  `git cat-file -e`, `git ls-tree --name-only <tip>`, and `git archive <tip>` into a temp export
  for the round-41 `run` facts. No file under `--repo` is opened from the working tree.
- So it does **not** need the repo working tree. Tested in scratch clone `clone-wt` at 03a6a1d:
  - E1 dirty worktree (uncommitted PROVINCE.md line and an added SCORECARD head line that would
    otherwise clear the `banner` item), `--tip 03a6a1d...`: `mismatches=8 maxN=63 met=False` (exit 1).
  - E1b same tree, `--tip HEAD`: `mismatches=8 maxN=63 met=False`.
  - E3 edits staged in the index, `--tip HEAD`: `mismatches=8 maxN=63 met=False`.
  - E2 edits staged, `--tip no-such-rev-xyz`: `could-not-evaluate: git rev-parse --verify
    no-such-rev-xyz^{commit}: fatal: Needed a single revision` (exit 2). An unresolvable tip does
    not fall back to the index.
- The lane itself (dirty: PROVINCE.md, corpus/SOURCES.md, corpus/knowledge/completion-request-plane.md
  modified by others) gives `mismatches=8` at `--tip 03a6a1d...` (`reconcile-lane-tip-03a6a1d.txt`).
- A scratch clone does **not** change the answer: the lane run, the clone run inside the unmutated
  counter (`selfdesc_mismatches=8`), and the dirty clone (E1) all give 8.
- Its only non-git input is its own script directory (for the round-41 import), so a clone with its
  own copy of `tools/` gives the same answer at the same commit. The counter always runs the
  reconciler from the tip's archived `tools/`, so the counter's answer depends only on the tip.

## Mutation recipe and bounds

- Clones: `$S/clone` (base), `$S/clone-mA`, `$S/clone-mB`, `$S/clone-wt`, `$S/clone-base-tools`
  under `/fast/scratch/hyaku/kama-r63/w/MT21C2SelfdescSkip`. Each asserted with
  `git rev-parse --show-toplevel`. Mutants are committed in their own clone as seat identity; patches in the out dir.
- Mutant A patch (`mutA.patch`): `met = (baseline and selfdesc == 0` becomes `met = (baseline`.
- Mutant B patch (`mutB.patch`): inserts `if p.returncode != 0: return 0` before the regex in `selfdesc_mismatches`.
- Each counter ran from its clone's `tools/` with `--repo <clone> --tip <clone HEAD> --work <scratch>`,
  with `TMPDIR` set to the scratch tmp dir. Live bound runs used the counter's own ports (no registered
  consumer ports, no foreign llama-server touched). The unmutated run took 43 s; mutants A and B took
  about 45-100 s each (live bound runs: llamacpp, context-capacity, ollama).
- No lane, fleet, sibling, or lane-index mutation; no commit or push in the lane; `shokuknow` not touched.
- Foreign llama-servers listed by `pgrep` (ports 1234, 45669, and two others not mine) were left alone.
- Scratch root removed before yield (after receipts were copied to the out dir).

## Summary tally

`mutants=2 killed=0 survived=2 inconclusive=0; unmutated met=False (selfdesc_mismatches=8, all other conjuncts green); mutA met=True; mutB met=True`
