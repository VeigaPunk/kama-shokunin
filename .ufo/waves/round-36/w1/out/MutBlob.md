# MutBlob — pinned r35 blobs vs live rev-parse

Judged axis: calibration. Predicate not retargeted. Neither `corpus/lessons/round-35.md` nor `.ufo/reports/round-35/kama.md` was rewritten.

## Comparison (write-time)

Constants in `tools/round36-statement-audit.py` lines 25–26:

```
LESSON_BLOB = "428f1f8a0e8871022f7c1e8ea47e50ba5a8d6412"
REPORT_BLOB = "6d8f317378ba6048d8a3dfb4944adaf24f341eea"
```

```RESULTS
[1] lesson blob at the pinned tip
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse e5a8ececf3d60fd53b36bb74299693a29e8f74b6:corpus/lessons/round-35.md
428f1f8a0e8871022f7c1e8ea47e50ba5a8d6412
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD
9014843cb7de8fbe87a97954c13832b67d55f046
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin merge-base --is-ancestor e5a8ececf3d60fd53b36bb74299693a29e8f74b6 HEAD
exit 0

[2] fleet report blob at fleet HEAD (same command block as the id below)
$ git -C /home/vgpnk/Projects/shokunin rev-parse HEAD:.ufo/reports/round-35/kama.md
6d8f317378ba6048d8a3dfb4944adaf24f341eea
$ git -C /home/vgpnk/Projects/shokunin rev-parse HEAD
58b035be0e7363df617f48a9b12f9859f1736eae

[3] lane-source detector, same tip
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6
uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False
EXIT:1
```

Both live ids equal the constants. `lesson_unchanged 1` and `report_unchanged 1` agree with that equality. `met False` is not a blob miss: `uncorrected` is 4.

An earlier atomic sample in this seat, before the probe, already had the same report blob at a different fleet HEAD (`4da3b3760398e59eaf675346abc4b8db118b22a7` → `6d8f317378ba6048d8a3dfb4944adaf24f341eea`). The counter does not pin a fleet commit. It calls `git_blob(FLEET, "HEAD", ".ufo/reports/round-35/kama.md")`. HEAD moved during this seat; the blob id did not, in the two atomic samples above. That is not a freeze.

`git status --porcelain` for `corpus/lessons/round-35.md`, `tools/round36-statement-audit.py` (lane), and `.ufo/reports/round-35/kama.md` (fleet) was empty at write time. Both ids are blob objects (`git cat-file -t`).

## What the counter does if either blob differs

It does not rewrite either file. The unchanged test is string equality after `git rev-parse`, not a worktree read:

```python
lesson_unchanged = 1 if lesson_blob == LESSON_BLOB else 0
report_unchanged = 1 if report_blob == REPORT_BLOB else 0
met = (
    uncorrected == 0
    and false_corrections == 0
    and lesson_unchanged == 1
    and report_unchanged == 1
)
```

(`tools/round36-statement-audit.py` lines 128–135. `emit` prints all four fields. Non-selftest `main` returns 0 only if `met` else 1.)

If the lesson rev-parse differs from `LESSON_BLOB`, `lesson_unchanged` becomes 0. If the fleet-HEAD report rev-parse differs from `REPORT_BLOB`, `report_unchanged` becomes 0. The other flag is not touched. Either 0 forces `met` False and exit 1 on the counting command, including the case where every correction row would otherwise hold. A failed rev-parse returns `None` (`git_blob`, lines 61–70), and `None` is not the pin, so the flag is 0. The printed line does not distinguish a missing object from a different id. Both are fail-closed.

At this tip that force is redundant. `uncorrected` is already 4, so `met` is already False and the exit is already 1. A blob mismatch changes the corresponding flag and does not change `met` or the exit code. That last sentence is what the probe executed for the lesson pin. The report-pin branch is the next comparison in the same conjunction; it was not given its own mutant.

`--selftest` does not consult either unchanged flag. It was not the assigned detector and was not run.

## Mutation probe

Claim challenged: a live blob id that differs from the pin is visible to the counting command's pass/fail. Plausible defect: at the do-nothing tip it is not, because `met` is already false.

| field | value |
| --- | --- |
| mutant | scratch copy only. One byte, file offset 1126: `LESSON_BLOB` final hex `2` → `3` (`428f1f8a0e8871022f7c1e8ea47e50ba5a8d6412` → `428f1f8a0e8871022f7c1e8ea47e50ba5a8d6413`). `cmp -l` printed `1126  62  63`. Lane source not edited. |
| expected detector | `python3 <bytes> --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6` |
| pristine output | `uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False` exit 1 |
| mutated output | `uncorrected 4 false_corrections 0 lesson_unchanged 0 report_unchanged 1 met False` exit 1 |
| restored output | same as pristine, exit 1 |
| verdict | inconclusive, not killed. Baseline already exit 1 / `met False`. Exit and `met` did not move. The flag did (`lesson_unchanged` 1 → 0). Coverage finding only: while `uncorrected != 0`, blob drift is invisible to the exit code and visible on the flag. Not permission to change the contract or the predicate. |

Mutated scratch sha256 (before restore): `93d8f89251888dbf51e4db37d008882aaf3ea68efc333430e033de60ee177146`.

## Restoration evidence

| bytes | sha256 |
| --- | --- |
| lane source before probe | `886e4598269f6546752783f3297db1b4f1a494e8c5d80c4c410eddf338c3db53` |
| scratch pristine | same |
| scratch after restore | same |
| lane source after probe | same |

`cmp` after restore: scratch == pristine == `tools/round36-statement-audit.py`. Post-restore scratch detector matched the pristine line. Post-probe rev-parse still printed `428f1f8a0e8871022f7c1e8ea47e50ba5a8d6412` and `6d8f317378ba6048d8a3dfb4944adaf24f341eea`. Seat log: `.ufo/waves/round-36/w1/out/MutBlob/probe.log`. Restored scratch remains at `.ufo/waves/round-36/w1/out/MutBlob/round36-statement-audit.py`.

Stopped after this one probe.
