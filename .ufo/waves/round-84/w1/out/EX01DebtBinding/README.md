# EX01DebtBinding — C1(a)

Axes: operability (bind the note to the event subject); compatibility (preserve existing grade behavior when the subject is unavailable); scope (tool only, no register or gate edits).

## Deliverable

`round81-append-debt.py` is the byte-complete replacement for `tools/round81-append-debt.py`. `replacement.diff` is its patch against scratch HEAD `eb03a64bcd8e2faab0f4f9bcdc55bfc5c1ed2c85` (the lane master tip observed before cloning). Only grade's injected subject binding, main's cached git-subject resolver, the selftest helper parameter, and the two requested arms changed. The optional callable preserves existing callers. A resolved mismatch refuses the row after same-round checking and continues; None preserves normal grading. No production lane file was changed.

## Retained receipts

- `selftest.out`: `APPEND_DEBT_SELFTEST pass=31 fail=0`, exit 0; 29 existing arms plus `note-subject-mismatch` and `note-subject-unresolvable`.
- `fixture.out`: exit 1, exactly one `APPEND_DEBT_FINDING note-wrong-deletion-round`; detail says note deletion round 78 differs from subject round 79. Summary: `events=76 accepted=53 late=22 pending=0 unaccepted=2 bad_rows=1 bad_declarations=0 out_of_population=0`. Two additional count-short findings are retained, not suppressed: the refused event and the already-unaccepted round-83 event.
- `real-register.out`: exit 1, `events=76 accepted=53 late=22 pending=0 unaccepted=1 bad_rows=10 bad_declarations=0 out_of_population=0`. The ten stale rows remain unknown-event; the unaccepted event is `96e28374593be13833aebeb70150877f58f4aadc`. This is NOT a green real-register claim; register rotation and acceptance belong to C1(b/c), outside this slice.
- `red-debt-fixture-before.out`: verbatim copy of `.ufo/waves/round-84/measured/before/red-debt-fixture.out`, whose recorded invocation at freeze revision `2d49bf705a2f2f8b45da973407cbb0b2ce2f8fd2` exited 1 with `bad_rows=0 unaccepted=1` and no binding finding. This pre-fix command was not rerun.
- `replacement.diff`: exact `git diff HEAD -- tools/round81-append-debt.py` output, exit 0 (status separately recorded in `commands.json`).
- `commands.json`: exact argv, cwd, actual exit codes, and receipt names for the isolated runs; `install-scratch.out` records replacement copy exit 0.

## Commands and exit codes

Preparation shell (exit 0):

```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master && S=/fast/scratch/hyaku/kama-r84/EX01DebtBinding; mkdir -p "$S" && git clone --shared -q /home/vgpnk/Projects/shokunin/kama-shokunin "$S/wt" && git -C "$S/wt" rev-parse --show-toplevel && mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-84/w1/out/EX01DebtBinding && echo OUTDIR-OK
```

The root assertion printed `/fast/scratch/hyaku/kama-r84/EX01DebtBinding/wt`. No manual git mutations or commits were run after cloning. Existing selftest fixture git operations ran only under the seat's scratch root with their built-in root assertion.

Input copies shell (exit 0):

```sh
cp /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round81-append-debt.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-84/w1/out/EX01DebtBinding/round81-append-debt.py && cp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-84/measured/before/red-debt-fixture.out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-84/w1/out/EX01DebtBinding/red-debt-fixture-before.out
```

Run cwd: `/fast/scratch/hyaku/kama-r84/EX01DebtBinding/wt`; environment `TMPDIR=/fast/scratch/hyaku/kama-r84/EX01DebtBinding`. Exact Python subprocess argv are also in `commands.json`.

```sh
cp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-84/w1/out/EX01DebtBinding/round81-append-debt.py /fast/scratch/hyaku/kama-r84/EX01DebtBinding/wt/tools/round81-append-debt.py
# exit 0
python3 tools/round81-append-debt.py --selftest
# exit 0
python3 tools/round81-append-debt.py --repo . --round 84 --late .ufo/waves/round-84/fixtures/late-wrong-subject.tsv
# exit 1
python3 tools/round81-append-debt.py --repo . --round 84
# exit 1
git -C /fast/scratch/hyaku/kama-r84/EX01DebtBinding/wt diff HEAD -- tools/round81-append-debt.py
# exit 0
```

Cleanup shell (exit 0, EXIT trap executed after receipts were retained):

```sh
S=/fast/scratch/hyaku/kama-r84/EX01DebtBinding; trap 'rm -rf -- "$S"' EXIT; test "$S" = /fast/scratch/hyaku/kama-r84/EX01DebtBinding
```

No other shell commands were executed. File reads and the surgical replacement/diff-artifact edits used the dedicated tools. No tools installed or updated. No build, lint, formatter, gate, mutation test, or network request run. LSP definitions/references/refactors were unavailable: no LSP tool is mounted in this seat's inventory; text anchors were used instead.

## Integration boundary

The L1 should land only the replacement tool and perform the integrated C1 gate and real-register checks after sibling register/gate work. The full C1 predicate is not claimed here. The known remaining red register is retained evidence, not a blocker to the scoped replacement.
