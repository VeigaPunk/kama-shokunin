# R57Item10AxisFit — case 31 evidence (independent test)

Separate evidence file for the seat's distinct case 31: an independent, reproducible test of claim
separability and axis attribution for round-57 C1/C2. Main report:
`.ufo/waves/round-57/reports/R57Item10AxisFit-case31.md`. Machine-readable receipt:
`.ufo/waves/round-57/reports/R57Item10AxisFit-case31-receipts/separability.json`; source re-open
receipt: `…-receipts/sources-reopen.json`.

Environment: `Python 3.14.8`, `git version 2.56.0`, no installs. Fixture scratch
`/fast/scratch/hyaku/kama-r57/R57Item10AxisFit/cloneA` (removed after these receipts were copied
here). `TMPDIR` pointed into that scratch for `git archive` exports.

## Why a fixture

The two round-57 claims were both repaired in one commit (`7b74e2f2`), so the live lane tip cannot
show whether either claim survives the other's repair being absent. The test rebuilds each
combination as its own revision in a clone and runs each claim's own checker **from that revision's
blob**.

Method note (calibration): the first attempt invoked `tools/round56-prereg-check.py` from the clone
worktree for every variant, so all variants ran the same (new) checker. Those results are discarded
and not reported. The reported run materialises each variant's checker blob and invokes that file.

## Construction (exact)

```
git clone --quiet --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin cloneA
# V0 = 8640e34cad02adcd247ba0862da63f6fb2aab0df (lane HEAD at clone time)
git checkout -q -b c2-only  V0 && git checkout b89bdab2 -- tools/round56-prereg-check.py && commit
git checkout -q -b c1-only  V0 && git checkout b89bdab2 -- SCORECARD.md                && commit
git checkout -q -b noop-new V0 && write no-op battery                                   && commit
git checkout -q -b noop-old V0 && git checkout b89bdab2 -- tools/round56-prereg-check.py
                                && write no-op battery                                   && commit
git checkout -q -b c1-only-noop c1-only && write no-op battery                          && commit
```

The no-op battery is the preregistered `ROSTER` literal plus `def main(): return 0` — the exact
counterexample shape from `.ufo/waves/round-56/measured/c2-noop-control.out`.

Fixture revisions:

```
master        8640e34cad02adcd247ba0862da63f6fb2aab0df  V0 (both repairs)
c2-only       45787c3082480b987e5fd4583f406f18fb87eb63  C2 repair only
c1-only       2e3a79e469cd95288d3efde5ffdbb48a51fcd6e9  C1 repair only
noop-new      cfc3b36737d669efbf5b88164a25ea9ab16a889f  no-op battery, repaired checker
noop-old      7984b4c5d36d31bfe858155de89d0e33708339ac  no-op battery, pre-repair checker
c1-only-noop  cce4199de3d5bb670ddb96e832d38b7cda35eaba  C1 repair, stale count, no-op battery
unreachable-all-labels  e77179adbd21a0a336f0fda4659c0c1147a2a8db  unreachable calls naming every label
unreachable-mismatch    a483db246fe636741140849cb063bd66e0b93dad  unreachable calls, one label not a roster name
```

Blob hashes (sha256):

```
prereg checker b89bdab2  c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853
prereg checker 8640e34c  dee6f922d0d93b10512f9a799b94f36a1e0f080404a525e08121a223b2e90ced
battery genuine          69b77a6a64f2667757842c2471ddc256d12ceb5ccca6df0a57b88bbe17ab51c5
battery no-op            53e37c5c926005bede3c31e970501eaa28ad661629aa03acb1cfdbfd46c7172b
SCORECARD b89bdab2       9a8d594b18db8d7b31675ef3a31ff3e70e364ca66816e2489bc8b3c35d29dd35
SCORECARD 8640e34c       883b91b59d372fa8873b8ba15e3fca624d0ff60efc13803bf9689be140a8163d
```

## Exact outputs

Each variant ran
`python3 <variant-checker.py> --repo cloneA --tip <variant rev>` (C1) and
`python3 cloneA/tools/round42-selfdesc-reconcile.py --repo cloneA --tip <variant rev>` (C2).

```
V0_both_repairs 8640e34c
  C1 exit 0: present=1 roster_match=1 kills=1 controls=2 met=True
  C2 exit 0: r41=0 … mismatches=0 maxN=57 met=True

c2only_old_prereg_new_count 45787c30
  C1 exit 0: present=1 roster_match=1 kills=1 controls=2 met=True
  C2 exit 0: r41=0 … mismatches=0 maxN=57 met=True

c1only_new_prereg_old_count 2e3a79e4
  C1 exit 0: present=1 roster_match=1 kills=1 controls=2 met=True
  C2 exit 1: r41=1 … mismatches=1 maxN=56 met=False
            detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)

noop_under_new_checker cfc3b367
  C1 exit 1: present=1 roster_match=1 kills=1 controls=2 met=False
  C2 exit 0: r41=0 … mismatches=0 maxN=57 met=True

noop_under_old_checker 7984b4c5
  C1 exit 0: present=1 roster_match=1 kills=1 controls=2 met=True      <-- false green reproduced
  C2 exit 0: r41=0 … mismatches=0 maxN=57 met=True

c1only_plus_noop cce4199d
  C1 exit 1: present=1 roster_match=1 kills=1 controls=2 met=False
  C2 exit 1: r41=1 … mismatches=1 maxN=56 met=False
```

## Pass conditions and result

- Separability of C1: holds iff a no-op battery flips `met=True`→`met=False` under the checker
  repair, and the genuine battery stays `met=True`. Observed: `7984b4c5` `met=True` (before) →
  `cfc3b367` `met=False` (after); genuine accepted at `8640e34c`, `45787c30`, `2e3a79e4`.
- Separability of C2: holds iff `mismatches=0` at a revision where C1's repair is absent and
  `mismatches=1` where C2's repair is absent. Observed: `45787c30` `mismatches=0` (C1 repair absent);
  `2e3a79e4` and `cce4199d` `mismatches=1`.
- C1 independent of C2's repair: `cce4199d` rejects the no-op (`met=False`, exit 1) while the count
  is still `mismatches=1`.
- **Result: the two predicates are causally separable on distinct axes (C1 operability, C2
  calibration) — matching the amended freeze and the final lesson, not the dispatch packet.**

## Attribution finding carried by this test

The measured `maxN` is `56` with the pre-repair SCORECARD and `57` with the round-57 SCORECARD
(a `## Round 57` heading exists at `8640e34c`). `maxN` is the greatest `^## Round (\d+)` heading
(`tools/round42-selfdesc-reconcile.py:167-168`); the canonical capability table has 11 rows at both
tips. The packet's “maxN=56 instead of expected 46” therefore names no measured quantity; `46` is the
literal printed by `controls/c1-noop.py` (committed blob at `8640e34c`; the working
tree deletes that file at report time — a sibling repair, not this seat's).

## Predicate strength (extra variants; corroborates case 51)

Two further batteries carrying the exact `ROSTER` literal, both run with the repaired checker:

```
unreachable calls, every roster label present as a string first arg, all after `return` in main()
  rev e77179adbd21a0a336f0fda4659c0c1147a2a8db
  exit 0: present=1 roster_match=1 kills=1 controls=2 met=True      <-- content, not execution

unreachable calls whose third label is not a roster name
  rev a483db246fe636741140849cb063bd66e0b93dad
  exit 1: present=1 roster_match=1 kills=1 controls=2 met=False
```

Receipts: `…-receipts/unreachable-all-labels.json`, `…-receipts/unreachable-check.json`. The
`executed` term is `expected <= invoked` over an `ast.walk` call inventory
(`tools/round56-prereg-check.py:61-71`, `met` at :76, at `8640e34c`), so reachability is not tested. This agrees with
`R57Item30AxisFit-case51.md` §4; it qualifies the operability claim's after-state wording but does not
affect separability.

## Limits

- The fixture pins the lane at `8640e34c`; the lane advanced to `3d2d5d4d` during the seat. The
  fixture is reproducible from the construction steps above.
- `round42-selfdesc-reconcile.py` runs the round-41 counter's `RUN` facts in a `git archive` export;
  those runs executed from the fixture's `TMPDIR`, read-only with respect to the lane.
- Scratch was removed after copying these receipts and `separability.json`; no lane commit was made.

Report: .ufo/waves/round-57/reports/R57Item10AxisFit-case31-evidence.md
