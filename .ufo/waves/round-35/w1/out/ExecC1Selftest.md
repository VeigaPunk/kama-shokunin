# ExecC1Selftest

Seat: ExecC1Selftest. Axis: calibration. Tools not edited. No git add/commit/checkout. No subagent. Predicates not changed. MISSION.md not edited. Axis authority not touched.

Sealed batch: 2026-10-24T21:24:43-03:00. An earlier run in the same minute printed the same counter lines and exit codes.

Tool bytes at measurement (sha256), unchanged across the batch:

- `tools/round35-statement-audit.py` `ca7e099dd5e9814567f7cbdba445338606626498cf43b79d4f398aaf51261723`
- `tools/round35-coverage-audit.py` `ff5318494c01cd545455d386f65b9dcfdd64d361d4e94e98454081a7cb55d013`

`git status --porcelain` on those two paths: both `??` (untracked). This seat did not stage them. `corpus/lessons/round-35.md` was absent (`LESSON_EXISTS=0`, 0 bytes), so the C1 count read empty lesson text.

`--selftest` without `--repo` never reaches the selftest body: both scripts require `--repo` (exit 2). Selftests were therefore also run with `--repo`. Coverage `--selftest` does not score `--tip`; it always loads base `719655f12517a9ce6b1a5ca44316897fed8420b0`. A combined `--tip --selftest` invocation is not a substitute for the tip count. Outputs below are combined stdout and stderr.

## Commands, outputs, exit codes

### C1 count

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin
```

```
uncorrected 4 false_corrections 0 report_unchanged 1 met False
```

exit 1

### C1 `--selftest` without `--repo`

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-statement-audit.py --selftest
```

```
usage: round35-statement-audit.py [-h] --repo REPO [--lesson LESSON]
                                  [--selftest]
round35-statement-audit.py: error: the following arguments are required: --repo
```

exit 2

### C1 `--repo` and `--selftest`

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --selftest
```

```
SELFTEST missing_met=False bad_met=False pass=1
```

exit 0

### C2 count at frozen tip

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 719655f12517a9ce6b1a5ca44316897fed8420b0
```

```
named 0 file_exists 0 cited_row 0 met False
```

exit 1

### C2 `--selftest` without `--repo`

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --selftest
```

```
usage: round35-coverage-audit.py [-h] --repo REPO [--tip TIP] [--selftest]
round35-coverage-audit.py: error: the following arguments are required: --repo
```

exit 2

### C2 `--repo` and `--selftest`

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --selftest
```

```
SELFTEST base_met=False junk_met=False pass=1
base named 0 file_exists 0 cited_row 0 met False
```

exit 0

### C2 `--repo`, `--tip`, and `--selftest`

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 719655f12517a9ce6b1a5ca44316897fed8420b0 --selftest
```

```
SELFTEST base_met=False junk_met=False pass=1
base named 0 file_exists 0 cited_row 0 met False
```

exit 0

## Behavior

- C1 count: `met False`, exit 1. `uncorrected 4`, `false_corrections 0`, `report_unchanged 1`. Same line as `.ufo/waves/round-35/controls/c1-noop.out`. Not the preregistered target line `uncorrected 0 false_corrections 0 report_unchanged 1 met True`.
- C1 is a working-tree snapshot of `corpus/lessons/round-35.md`, not a commit pin. At this batch the file was absent, which is why all four ids are uncorrected and there are no false-correction rows. `report_unchanged 1` is the tool's fleet-blob check, not a separate rev-parse by this seat.
- C1 selftest with `--repo`: `pass=1`, exit 0. Same line as `.ufo/waves/round-35/controls/c1-selftest.out`. Exit 0 here means the selftest passed, not that the C1 claim is met (`missing_met=False`).
- C2 count at `719655f12517a9ce6b1a5ca44316897fed8420b0`: `named 0 file_exists 0 cited_row 0 met False`, exit 1. Same line as `.ufo/waves/round-35/controls/c2-base.out`. Matches the frozen clause that none of the three hold at that base. Not the target line `named 1 file_exists 1 cited_row 1 met True`.
- C2 selftest with `--repo`: `pass=1`, exit 0. Same two lines as `.ufo/waves/round-35/controls/c2-selftest.out`. Adding `--tip` did not change that output. `base_met=False` while `pass=1`.
- These tools print predicate satisfaction. They do not print the scorecard integers 7 or 9.

## Files changed

- `.ufo/waves/round-35/w1/out/ExecC1Selftest.md` (this report only)

## Remaining risks

- Both counters still report `met False`. That is the measured baseline, not a selftest failure.
- A later writer of `corpus/lessons/round-35.md` can move the C1 count without this seat re-running. C2 at the frozen tip cannot, unless the commit object changes.
- A literal `--selftest` with no `--repo` exits 2 and does not run the selftest body.

## Blockers

None for this seat.
