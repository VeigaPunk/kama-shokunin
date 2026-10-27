# R57Item23CounterRepair — minimal stale-count counter repair (case 44)

Axes: calibration (primary), operability. Scope: isolated scratch prototype only; no shared or
source writes, no commits/pushes, no fleet or sibling mutations, no installs (pacman paused per
`/home/vgpnk/.omp/agent/RULES.md`; nothing needed installing). Scratch:
`/fast/scratch/hyaku/kama-r57/R57Item23CounterRepair/`.

## Claim under test, and the pre-data correction

Delivered seat text: “C1 calibration — repair the stale canonical capability row count, counter
currently reports maxN=56 instead of expected 46; before output mismatch=1.”

Pre-data correction, committed before any seat evidence: `controls/freeze-amendment.txt`
(commit `7c873d7b4e3839489a93d6334cdf93fe5d34d19f`), SCORECARD §Round 57 pre-data row, and
`corpus/lessons/round-57.md` order the claims as: operability = round-56 prereg checker no-op;
calibration = the stale self-description verifier-spotcheck count (expected `42`, observed `43`).
This seat attacks the **stale-count artifact** named in both versions; the C1/C2 label ordering is
reported as conflicting and not resolved here.

## Finding 1 — “expected 46” is itself stale; maxN=56 is tree-derived and correct

Independent derivation at the frozen base `b89bdab2cc114735ec5d331c6c610134258f7864`
(`r8_derivation.out`):

```text
spotcheck_files_at_base=43
scorcard_literal_at_base=42
round_headings_at_base=57
maxN_at_base=56
latest_measured_round_at_base=56
noop_literal=print("mismatches=0 maxN=46 met=True")
```

`46` is not derivable from the tree. It exists only as (a) the round-46-era regression value
`SCORECARD.md:2676` `round-42 self-description counter mismatches=0 maxN=46 met=True`, (b) the
historical banner `SCORECARD.md:2744` `Latest measured round: 46`, and (c) the hardcoded literal in
the frozen no-op `controls/c1-noop.py`. The counter derives `maxn` from every
`^## Round (\d+)` heading (`tools/round42-selfdesc-reconcile.py:167-168`) and requires the head to
say `Latest measured round: <maxN>` (`:190`); at HEAD `3d2d5d4d` the same frozen counter derives
`maxN=57` once the Round 57 section exists (`r7_lane_head.out`).

Forcing `46` would therefore require deleting Round 47–56 history **and** would fail the banner
check. The `mutround` receipt below shows the rule: adding a `## Round 58` heading yields
`maxN=58`, `banner=1`, `planned=2`, `mismatches=3`, exit 1. `46` is rejected, not repaired to.

## Finding 2 — the actual stale count is the calibration census `42`, and the minimal repair is one token

Base receipts are byte-identical on the lane repo at the pinned base and on an isolated fixture
exported from that same commit:

```text
r1_base_lane.out     tip=b89bdab2…  r41=1 … mismatches=1 maxN=56 met=False
                                    detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
r2_base_fixture.out  tip=2665285…   (same line, same detail)   exit=1
```

Independent census at the same commit: 43 `corpus/lessons/*verifier-spotcheck.md` blobs against a
row literal of `42` (`r8_derivation.out`).

Prototype repair in isolated scratch: re-anchor that one literal in the calibration evidence row
from `42` to `43`; **counter bytes unchanged** (sha256
`9736923ec3086c6e56512cd67fa7c00a22cbb8ac63022bef45a676f2200f9ef0`). The build-fixture diff is
exactly one insertion and one deletion, no other file or line (`r8_build_diff_excerpt.out`).

```text
r3_build.out  tip=750c555…  r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=56 met=True   exit=0
```

Canonical heading semantics are preserved: `canon()` still selects the highest
`canonical list as of round N` marker — round 49, 11 rows, first-working rounds
`[10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47]` — identical between base and build
(`r5_semantics_base.out`, `r5_semantics_build.out`). No canonical row was added, removed, or
renamed. “Canonical capability row count” in the delivered text is 11 and did not change; no
tree-derived evidence makes it 46.

## Controls

No-op (`r4_noop.out`): the frozen `controls/c1-noop.py` prints `mismatches=0 maxN=46 met=True`,
exit 0. The script has 3 lines, 0 imports, no file-access names, only the `print` call
(`r4_noop_shape.out`), and emits the same line from another cwd (`r4_noop_cwd2.out`). It reads
nothing, so neither its `met=True` nor its `46` is evidence; it is the stale literal the wave text
mistook for an expectation.

Mutation receipts (`r6_*.out`), each on its own committed fixture:

| mutant | change | result | exit |
|---|---|---|---|
| `mut42` | count back to `42` | `r41=1`, detail expects `42` | 1 |
| `mut44` | count `44` | `r41=1`, detail expects `44` | 1 |
| `mutrow` | canonical row `sources-registry` → `sources-registry-x` | `caps=1`, canon (round 49) row set differs | 1 |
| `mutround` | added `## Round 58` heading | `maxN=58 banner=1 planned=2 mismatches=3` | 1 |

Production cross-check with the same frozen counter bytes (`r7_*.out`): lane at
`7b74e2f2515a6f598918488fa5144658ff29925f` → `mismatches=0 maxN=56 met=True`, exit 0; lane at
`3d2d5d4d6cba3028ec5358832a67f192cc0e41ec` → `mismatches=0 maxN=57 met=True`, exit 0.

## Exact commands

```bash
# frozen counter bytes from the base tip
git -C <lane> show b89bdab2cc114735ec5d331c6c610134258f7864:tools/round42-selfdesc-reconcile.py > bin/round42-selfdesc-reconcile.py
git -C <lane> show b89bdab2cc114735ec5d331c6c610134258f7864:tools/round41-scorecard-reconcile.py > bin/round41-scorecard-reconcile.py
# isolated base fixture (guarded: git rev-parse --show-toplevel must print the fixture dir)
git -C <lane> archive b89bdab2cc114735ec5d331c6c610134258f7864 | tar -x -C fixtures/base && cd fixtures/base && git init -q . && git add -A && git -c user.name=seat -c user.email=seat@local commit -qm base
python3 bin/round42-selfdesc-reconcile.py --repo <lane> --tip b89bdab2cc114735ec5d331c6c610134258f7864 --out receipts/r1_base_lane.out
python3 bin/round42-selfdesc-reconcile.py --repo fixtures/base --tip HEAD --out receipts/r2_base_fixture.out
# build fixture: calibration row 42 -> 43 only, then
python3 bin/round42-selfdesc-reconcile.py --repo fixtures/build --tip HEAD --out receipts/r3_build.out
# no-op and mutants
python3 bin/c1-noop.py
python3 bin/round42-selfdesc-reconcile.py --repo fixtures/mut42 --tip HEAD --out receipts/r6_mut42.out
python3 bin/round42-selfdesc-reconcile.py --repo fixtures/mutrow --tip HEAD --out receipts/r6_mutrow.out
```

## Evidence

All receipts under
`.ufo/waves/round-57/measured/R57Item23CounterRepair/`
(`MANIFEST.txt` pins every fixture tip and both counter sha256 values):
`r1_base_lane.out`, `r2_base_fixture.out`, `r3_build.out`, `r4_noop.out`, `r4_noop_cwd2.out`,
`r4_noop_shape.out`, `r5_semantics_{base,build}.out`, `r6_mut{42,44,row,round}.out`,
`r7_lane_{repaired_7b74,head}.out`, `r8_derivation.out`, `r8_build_diff_excerpt.out`, and each
`.exit` file. Case 44 independent evidence:
`.ufo/waves/round-57/reports/R57Item23CounterRepair-case44.md`.

## Limits and risks

- Base claim measured at pinned `b89bdab2…`; the lane advanced during the run
  (`3d2d5d4d…` → `8a7f1976…`), so every receipt names its tip.
- The delivered C1/C2 ordering conflicts with the pre-data amendment; both are quoted, neither is
  resolved here.
- The minimal repair is a data re-anchor, not a counter-code change: the counter already derives
  `maxN` and already enforces head agreement; forcing `46` would weaken or break that binding.
- Not exercised here (out of this seat’s item): the full wave battery; the S515 source reopen
  (owned by source seats — lane authors only advise); the admit/reject spot-check (outside
  closure, advisory only). No shared files were written.
- Traceability note: after this seat’s runs, another seat relocated the frozen
  `controls/{c1-noop.py,noop-c1.out,noop-c2.out}` out of `controls/` (a `controls/noop-fixture/`
  directory appeared). This seat had already copied the script to scratch before the move, so
  `r4_noop.out` is from the frozen bytes; the relocation is not this seat’s change and was not
  remediated.

Report: .ufo/waves/round-57/w1/out/R57Item23CounterRepair.md
