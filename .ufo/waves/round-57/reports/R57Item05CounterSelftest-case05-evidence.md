# R57Item05CounterSelftest — distinct case 5 evidence (independent verification)

Separate evidence file for seat `E03CounterSelftest`, produced by a different path than the
harness under test: the harness derives its expectations in-process and calls the instrument
itself; this file reads the raw instrument receipts after the fact and re-derives the two
graded facts with standalone `git` commands. No new instrument run and no new fixture was
created for this file after the L1 stop request; every output below is from this session's
recorded execution.

## 1. Pinned state

| Item | Value |
|---|---|
| Lane frozen base (round-57 receipts `controls/base-c1.out`, `base-c2-frozen.out`) | `b89bdab2cc114735ec5d331c6c610134258f7864` |
| Pre-repair C1 checker (`git show 7c873d7:tools/round56-prereg-check.py`) | sha256 `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` (= `counter_sha256` frozen in round-56 `preregistration.json` C2) |
| Committed C1 repair (`git show 7b74e2f:tools/round56-prereg-check.py`) | sha256 `dee6f922d0d93b10512f9a799b94f36a1e0f080404a525e08121a223b2e90ced` |
| Committed C2 counter (`git show 7b74e2f:tools/round42-selfdesc-reconcile.py`) | sha256 `9736923ec3086c6e56512cd67fa7c00a22cbb8ac63022bef45a676f2200f9ef0` |
| Fixture tips | `measured/R57Item05CounterSelftest/out/fixtures.json` |

## 2. C2 fact re-derivation, standalone commands

Declared count, read from the frozen-base blob (exact substring from the calibration row):

```
$ git show b89bdab2:SCORECARD.md   # calibration row, verifier-spotcheck run fact
'glob.glob(\'corpus/lessons/*verifier-spotcheck.md\')))"` → `42` (outside closures on record…'
```

Observed population at the same commit:

```
$ git ls-tree -r --name-only HEAD corpus/lessons | grep -c 'verifier-spotcheck\.md$'
43
```

Independent verdict: `declared=42`, `observed=43`, therefore the self-description count is
stale at the frozen base by one. This matches fixture `c2-base` (`tip 059afa6b…`) and contradicts
nothing in `controls/freeze-amendment.txt` ("expects 42 but the actual committed outside verifier
spotcheck count is 43").

maxN re-derivation, standalone: the committed SCORECARD's round headings at the frozen base are
`## Round 1 … ## Round 56` (`grep -cE '^## Round [0-9]+' SCORECARD.md` → 57 headings including
the duplicate-cased historical entries), so the heading maximum is 56, and the counter printed
`maxN=56` at base. The frozen pre-amendment phrase "reports maxN=56 instead of expected 46" is
therefore not reproducible as a stale-maxN statement; the fixture pair `c2-maxn-trim`
(headings ≤46 → instrument prints 46) and `c2-maxn-inflated` (appended `## Round 99` → instrument
prints 99) shows the field tracks the tree in both directions. `46` is what a trimmed tree
yields, not a fact of the frozen base.

## 3. Post-hoc tabulation of raw receipts (not produced by the harness)

Source receipts: `out/evidence-c1.txt` (instrument × fixture raw stdout/exit) and
`out/evidence-c2.txt`.

C1 — predicate: genuine must be `met=True` exit 0; each no-op shape must be `met=False` exit≠0.

| Instrument | genuine | deadcode | unusedfn | literal | stale-roster | absent | badjson |
|---|---|---|---|---|---|---|---|
| `prereg-pre-repair` (frozen c7b0d787) | green | **green (defect)** | **green (defect)** | **green (defect)** | red | red | exit 2 |
| `prereg-candidate` (7b74e2f) | green | **green (survivor)** | **green (survivor)** | red | red | red | exit 2 |
| `ref-c1-execbind` | green | red | red | red | red | red | exit 2 |
| `noop-c1-instrument` | green | **green** | **green** | **green** | **green** | **green** | **green** |

Independent verdict: the frozen checker is defeated by a literal-only no-op (round-56 receipt
`c2-noop-control.out` is reproduced); the committed repair defeats only that shape and remains
green when the same literal-label calls exist but cannot execute. The reference reachability
instrument is the only one of the four that separates all seven fixtures. Tabulation agrees with
`out/c1/*.out` verdicts (pre-repair failed=3, candidate failed=2, reference failed=0, noop
failed=7).

C2 — predicate: stale tree red, repaired tree green, re-staled tree red, maxN equals the heading
maximum, missing SCORECARD exit 2.

| Instrument | base (42/43) | fixed (43/43) | fixed−lesson (43/42) | maxN trim | maxN inflated | no SCORECARD |
|---|---|---|---|---|---|---|
| `selfdesc-committed` | `mismatches=1 met=False` exit 1 | `mismatches=0 met=True` exit 0 | `mismatches=1` exit 1 | `maxN=46` | `maxN=99` | exit 2 |
| `ref-c2-witness` | same, plus `sc_sha256`/`declared`/`observed` | same, plus witness | same, plus witness | `maxN=46` | `maxN=99` | exit 2 |
| `frozen-noop` | `mismatches=0 met=True` exit 0 (**false green**) | green | **green (false)** | `maxN=46` (coincidence) | **`maxN=46` (stale)** | **exit 0 (false)** |

Independent verdict: the committed counter's arithmetic is sound on this defect; the no-op
control is false-green on the stale tree, the re-staled tree and the missing-file case, and is
caught only by the inflated-maxN and fail-closed checks. Witness fields distinguish a genuine
green from a hardcoded one.

## 4. What this file adds over the harness receipts

* The C2 declared/observed pair is re-derived with `git show` + `git ls-tree` only; the harness
  recomputes it in Python. Both give `42` vs `43` at the frozen base.
* The maxN claim is checked against the committed heading population rather than against a
  fixture expectation, which is how the "56 instead of 46" wording was shown to describe a
  trimmed tree, not the frozen base.
* The C1 verdicts are tabulated from raw instrument stdout, so a bug in the harness's expectation
  table would show up here as a disagreement. None was found.
