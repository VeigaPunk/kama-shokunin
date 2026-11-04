# EX04Selfrecord — round 84 w1

Axis: calibration; fixed eight-fact population, six stale and two holds.

## Deliverable

`round84-selfrecord-round83.py` is ready for L1 to land at `tools/round84-selfrecord-round83.py`. It reads sealed declarations via git show, HEAD receipt/lesson/fix witnesses via git show, and BASE witnesses to freeze classification. Missing corrections produce six mismatches and six unbacked facts. Holds and unknown facts reject corrections. Corrected facts require exactly one ISO-dated line, exact old/new/BASE tokens and a whole new token in a non-lesson tip fix outside restatements. Per-fact states are holds/corrected/stale; exits 0/1/2 distinguish answered, mismatched, unreadable.

## Evidence

- `red-selfrecord.out`: `SELFRECORD_R83 claims=8 mismatches=6 corrected=0 unbacked=6`, exit 1.
- `selftest.out`: `SELFRECORD_R83_SELFTEST pass=16 fail=0`, exit 0. Includes clean committed fixture, missing lesson, wrong old, hold/unknown corrections, excluded correction-block token, wrong revision, duplicate, invalid date, lesson fix, near-token, dirty worktree, sealed drift, witness rewrite, absent receipt.
- `commands.json`: both requested sequences, argv/cwd/exits. `README.md`: commands, architecture, limits, serialization, integration guidance and self-evaluation.
- Initial receipts retained honestly: first red exposed a population-substring extraction mistake; final code uses a boundary and fixtures include the shadow key. Superseded initial receipts are explicitly labeled.

## Risks / integration requirements

F2 is one comma-joined token for window and falls. L1 explicitly requested F3's four-component delta token including bad count, rather than frozen table's three-component shorthand; README discloses this divergence. Scribe SCR01LessonSources received exact serialization. No frozen plan bytes changed.

Only own out directory changed. Scratch clones/fixtures removed. No installations, production edits, external state changes, commit/push, builds, linters or formatters. Requested red/selftest only; parent owns integrated-green and full gate verification. LSP unavailable in exposed inventory. No blocker to scoped implementation. Report lives here to obey out-only boundary, not the conflicting trailer path.
