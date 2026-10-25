# CriticC1Noop

Axis: calibration. Attacked object: the C1 do-nothing control at tip `e5a8ececf3d60fd53b36bb74299693a29e8f74b6`. The counter was not edited. The predicate was not retargeted.

## Re-run

Command:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6
```

Line:

```
uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False
```

Exit code: `1`.

That stdout is byte-identical to `.ufo/waves/round-36/controls/c1-noop.out` (one line, trailing newline, no exit code stored in the control file). Exit `1` is the counter's documented not-met code, not usage (`2`) and not a crash.

## Verdict

This control does not meet the target. The counter is not shown wrong by this control.

The target is the C1 predicate being met: `met True` and exit `0`. The kill in this seat is one-directional: if do-nothing met that target, the counter would be wrong. It does not. `met False` with `uncorrected 4` is the required do-nothing result at a tip where `corpus/lessons/round-36.md` is absent. Reproducing the recorded control is not itself a defect; treating reproduction as "meets the target" would invert the kill.

## Counterexample

Attempted: do-nothing at the frozen base satisfies C1, so the counter is wrong.

It fails. Independent of the counter's own print:

- `git cat-file -e e5a8ececf3d60fd53b36bb74299693a29e8f74b6:corpus/lessons/round-36.md` exited `128` with `path 'corpus/lessons/round-36.md' does not exist`. The empty lesson is absence, not a substituted file.
- `git rev-parse e5a8ececf3d60fd53b36bb74299693a29e8f74b6:corpus/lessons/round-35.md` is `428f1f8a0e8871022f7c1e8ea47e50ba5a8d6412`, the counter's `LESSON_BLOB`.
- `git -C /home/vgpnk/Projects/shokunin rev-parse HEAD:.ufo/reports/round-35/kama.md` is `6d8f317378ba6048d8a3dfb4944adaf24f341eea`, the counter's `REPORT_BLOB`.
- `git rev-parse --verify e5a8ececf3d60fd53b36bb74299693a29e8f74b6` returned that same id.

So `lesson_unchanged 1` and `report_unchanged 1` are re-derived pins, and the fail is only `uncorrected 4`. Blob drift is not hiding inside this `met False`. No second authority disagrees with the control file.

## Impacted axes

Calibration: no fixable defect on this control. Do-nothing does not pass. This is not a tradeoff the L1 must reject, and it is not a reason to change the predicate.

This seat does not certify the positive arm. A later tip with real correction rows is outside this re-run.

## Smallest safe correction

None. Do not edit the counter.
