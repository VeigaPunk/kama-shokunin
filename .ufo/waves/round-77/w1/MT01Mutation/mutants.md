# MT01 round-77 mutation certification

Axes: operability and calibration.

Read the entire frozen `plans/round-77-claims.md`; no predicate was changed. Observed lane master: `7d60e2ab58866a0366937d61c9712483be57b36e`; declared base: `cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7`.

## Read-time result

All three assigned module paths were absent when read. Per the assignment's absent-module rule, their attempted unmutated selftests are recorded below. An exit-2 missing-file failure is inconclusive, not a killed mutant or a selftest tally of zero.

| Module | Named source arms | Unmutated selftest | Mutants | Verdict |
|---|---|---|---|---|
| round77-citation-baseline.py | unavailable: source absent | exit 2; no tally | none | inconclusive |
| round77-append-registers.py | unavailable: source absent | exit 2; no tally | none | inconclusive |
| round77-selfrecord-round76.py | unavailable: source absent | exit 2; no tally | none | inconclusive |

## Commands, actual errors, and receipts

Command: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round77-citation-baseline.py --selftest`

Exit: 2. Stdout: empty. Stderr:

```text
python3: can't open file '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round77-citation-baseline.py': [Errno 2] No such file or directory
```

Receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/MT01Mutation/round77-citation-baseline.py.selftest.json`

Command: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round77-append-registers.py --selftest`

Exit: 2. Stdout: empty. Stderr:

```text
python3: can't open file '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round77-append-registers.py': [Errno 2] No such file or directory
```

Receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/MT01Mutation/round77-append-registers.py.selftest.json`

Command: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round77-selfrecord-round76.py --selftest`

Exit: 2. Stdout: empty. Stderr:

```text
python3: can't open file '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round77-selfrecord-round76.py': [Errno 2] No such file or directory
```

Receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/MT01Mutation/round77-selfrecord-round76.py.selftest.json`

## Mutant and survivor lists

No mutants could be constructed: none of the three sources existed at read time. No per-arm PASS/FAIL or mutant diff is available. Survivor list: not evaluated (not an empty certified survivor set). Frozen-plan arm names are not substituted for source-enumerated arms.

## Restoration and cleanup

No source bytes were copied or mutated; before/mutated/restored hashes are unavailable because the source files were absent. Lane tools and frozen plan were untouched. The scratch directory `/fast/scratch/hyaku/kama-r77/MT01Mutation` was removed by the driver in `finally` after its three JSON receipts were written into this wave directory. No tools were installed or updated.
