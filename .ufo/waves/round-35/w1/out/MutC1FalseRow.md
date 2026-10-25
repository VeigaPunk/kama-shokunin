# MutC1FalseRow

Seat: MutC1FalseRow. Axis judged: calibration. No tool install. MISSION.md not edited; axis authority not touched. Predicate not changed.

## Mutant

Scratch lesson (not `corpus/lessons/round-35.md`): `.ufo/waves/round-35/w1/out/MutC1FalseRow/false.md`

sha256 `0d3d45b10baaf5bfd5a774d15099d5c02469d19cad143ad7d7fda5c5ef149138` (152 bytes). Wrong tokens, one per id: `true`, `22 was correct`, `processes are still live`, `note present`.

```
| R34-MAP | true | still on the map |
| R34-R33COUNT | false | 22 was correct |
| R34-LIVE | processes are still live |
| R34-MANIFEST | note present |
```

The counter was not edited. `tools/round35-statement-audit.py` sha256 before and after: `ca7e099dd5e9814567f7cbdba445338606626498cf43b79d4f398aaf51261723`.

## Expected detector

A false correction must not meet C1. Expected: `false_corrections 4`, `met False`, exit 1. `met True` would be a counter defect.

## Output

Pristine (no `corpus/lessons/round-35.md`; lesson_exists False):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin
uncorrected 4 false_corrections 0 report_unchanged 1 met False
PRISTINE_EXIT:1
```

Mutated:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --lesson /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-35/w1/out/MutC1FalseRow/false.md
uncorrected 4 false_corrections 4 report_unchanged 1 met False
MUTATED_EXIT:1
```

Restored canonical path (lesson still absent; same command as pristine):

```
uncorrected 4 false_corrections 0 report_unchanged 1 met False
RESTORED_CANONICAL_EXIT:1
canonical_lesson_absent 1
```

## Verdict

Killed. Not a counter defect. `met` stayed False. The mutation-specific signal is `false_corrections` 0 → 4: all four wrong-token rows were classified as false corrections, not accepted. Baseline `met False` is the frozen do-nothing state, not evidence the rows were ignored.

No contract change. Scratch lesson kept as the probe artifact (tasking did not mark it disposable). Counter bytes not restored because they were not mutated.

## Restoration evidence

- Counter sha256 identical before and after the probe: `ca7e099dd5e9814567f7cbdba445338606626498cf43b79d4f398aaf51261723`.
- Lesson sha256 unchanged after the detector run: `0d3d45b10baaf5bfd5a774d15099d5c02469d19cad143ad7d7fda5c5ef149138`.
- `corpus/lessons/round-35.md` still absent. Canonical detector output matches the pristine run.
- Read-only `git status --porcelain -- tools/round35-statement-audit.py` printed `?? tools/round35-statement-audit.py`. This seat did not write or stage that file. No git add, commit, or jj mutation.
