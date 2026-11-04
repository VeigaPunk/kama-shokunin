# C1 round-77 self-record — the four repairs, exact old → new text

Owner: integration (L1). None of these repairs is applied to the lane by seat EX01C1Selfrecord;
each was applied only inside the scratch clone
`/fast/scratch/hyaku/kama-r78/EX01C1Selfrecord/clone` (since deleted), where the landed counter
then printed the frozen line
`SELFRECORD_R77 claims=6 mismatches=0 corrected=4 unbacked=0`, exit 0
(receipt `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-78/w1/EX01C1Selfrecord/scratch-run.out`).

Value strings are the frozen ones from `plans/round-78-claims.md` §C1. The four correction
blocks below are what the counter parses in `corpus/lessons/round-78.md` §Corrections; seat
SC02Lesson has already drafted equivalent blocks in the lane worktree
(`corpus/lessons/round-78.md`), and every `old` in them re-derives at the sealed revision
`6c1550a14babaca092cfcc3106f792d695652200` under the landed counter.

## F3 — `SKILL.md` `| Pre-report gate |` row (line 309 at the sealed revision and at master)

Old (verbatim, the current committed row — `git show 6c1550a14babaca092cfcc3106f792d695652200:SKILL.md` line 309):

```text
| Pre-report gate | gate: `python3 tools/pre-report-gate.py --repo . --round N --tip master` (eight arms, fixed order: selfdesc reconciler, newest-closure counter, receipt-pointer audit, worktree-landing check, round-scope counter, round-worktree cleanliness, arm 7 `round74-v2` composing `tools/round74-selfdesc-canon.py`, `tools/round74-receipt-claim-binding.py` and `tools/round74-province-host-drift.py`, and arm 8 `round75-instruments` composing `tools/round75-interpretation-pins.py`, `tools/round75-survivor-probe.py` and `tools/round75-append-accepted.py`; an absent module fails its arm closed, never vacuously green) | 0 iff all eight arms green and `uncommitted=0`, i.e. the line reads `PRE_REPORT round=<N> arms=8 failed=0 uncommitted=0`; 1 names every failed arm; 2 CLI misuse; 3 re-entry refusal | `python3 tools/pre-report-gate.py --selftest` → `PRE_REPORT_SELFTEST pass=18 fail=0` (round-75 measurement; the five-, six- and seven-arm readings `arms=5`/`arms=6`/`arms=7` stay readable as their rounds' records) | Removed temp fixtures only |
```

New (verbatim; the same text is already drafted, uncommitted, in the lane worktree `SKILL.md`
by that file's owner — the counter was calibrated against these exact bytes in the clone):

```text
| Pre-report gate | gate: `python3 tools/pre-report-gate.py --repo . --round N --tip master` (nine arms, fixed order: selfdesc reconciler, newest-closure counter, receipt-pointer audit, worktree-landing check, round-scope counter, round-worktree cleanliness, arm 7 `round74-v2` composing `tools/round74-selfdesc-canon.py`, `tools/round74-receipt-claim-binding.py` and `tools/round74-province-host-drift.py`, arm 8 `round75-instruments` composing `tools/round75-interpretation-pins.py`, `tools/round75-survivor-probe.py` and `tools/round75-append-accepted.py`, and arm 9 `round77-instruments` composing `tools/round77-citation-baseline.py`, `tools/round77-append-registers.py` and `tools/round77-selfrecord-round76.py`; the retired `round76-instruments` arm no longer runs; an absent module fails its arm closed, never vacuously green) | 0 iff all nine arms green and `uncommitted=0`, i.e. the line reads `PRE_REPORT round=<N> arms=9 failed=0 uncommitted=0`; 1 names every failed arm; 2 CLI misuse; 3 re-entry refusal | `python3 tools/pre-report-gate.py --selftest` → `PRE_REPORT_SELFTEST pass=22 fail=0` (round-77 measurement, receipt `.ufo/waves/round-77/measured/after/gate-selftest.out`; the five-, six-, seven- and eight-arm readings stay readable as their rounds' records) | Removed temp fixtures only |
```

Why: the gate module's own `ARM_ORDER` carries nine arms with `round77-instruments` newest
(verified by AST read of `tools/pre-report-gate.py`, worktree == sealed), and the round-77
committed receipt prints `PRE_REPORT_SELFTEST pass=22 fail=0`.
Correction values: old `gate=arms:8/word:eight/newest:round77-instruments/tally:18` →
new `gate=arms:9/word:nine/newest:round77-instruments/tally:22`.

## F4 — `SCORECARD.md` §Round 77 record: append one sentence (last pointer wins; no bytes rewritten)

Old (the record's last freeze-divergence sentence, `SCORECARD.md` §Round 77, at master):

```text
**Freeze divergence recorded.** The C3 plan bullet named the closure-sealed boundary without
naming the record-path set; the counter uses the inherited round-76 set (PROVINCE.md is work) and
therefore derives `work-tip = 0e01f32f…`. That is the divergence that produced the third
correction and the miss; it is documented in `corpus/lessons/round-77.md` §Mistakes 4.
```

New (append at the end of the Round 77 section, immediately before the
`## Superseded head bytes (round 77; …)` heading):

```text
Freeze-divergence pointer correction (2026-11-04): the C3 predicate/ruling divergence is
documented in `corpus/lessons/round-77.md` §Freeze divergences item 3; the earlier
§Mistakes 4 pointer named the L1 mutating-git breach and stays as filed history.
```

Why: §Mistakes 4 of the sealed lesson is the L1's mutating-git breach; the C3
predicate/ruling divergence (the counter's record-path-set reading) is §Freeze divergences
item 3 of the same lesson. The counter reads the record's LAST `corpus/lessons/round-77.md`
§-pointer sentence, so the append supersedes the stale pointer.
Correction values: old `pointer=section:Mistakes 4` → new `pointer=section:Freeze divergences item 3`.

## F5 — `corpus/knowledge/register-cutoff-split.md`: append one `source-correction:` line

Append (the entry's existing `source:` line, which cites plans/tools paths and asserts no
external source, stays as filed history):

```text
source-correction: S073 — git-log `--diff-filter` added-path selection (https://git-scm.com/docs/git-log, opened 2026-10-21, `corpus/SOURCES.md:85`) supplies the introduction-discovery mechanics this entry describes; correcting the earlier "no external source is asserted" scoping, appended 2026-11-04.
```

Why: F5 requires every round-77-added knowledge entry to carry a `source:` or
`source-correction:` line citing at least one `S###` row id. S073 (the git-log `--diff-filter`
row, verified at `corpus/SOURCES.md:85`, status mined) holds exactly the added-path-selection
ground the entry's introduction-discovery reasoning rests on.
Correction values: old `provenance=missing:corpus/knowledge/register-cutoff-split.md` →
new `provenance=missing:none`.

## F6 — `corpus/README.md`: append the two coverage-map rows

Append (a new section at end of file, so no existing line moves — the round-10 rule):

```text
## Coverage map — round 78 addition (C1 self-record repairs)

Appended rather than inserted, so no existing line moves (the rule the round-10 addition states).

| Entry | Covers | Round |
|---|---|---|
| `corpus/knowledge/baseline-receipt-binding.md` | Round-77 baseline receipt introduction ancestry and introduction-to-tip byte identity | 78 |
| `corpus/knowledge/register-cutoff-split.md` | Round-77 independent register introductions, exclusive carriage classes and rotation rejection | 78 |
```

Why: F6 requires a coverage-map row for every round-77-added knowledge entry; at the sealed
revision neither entry had one. The entry cell names `corpus/knowledge/<name>` (the round-78
README rows already landed in the worktree by that file's owner use the same cell form; the
counter accepts both `knowledge/<name>` and `corpus/knowledge/<name>` cells).
Correction values: old
`coverage-map=missing:corpus/knowledge/baseline-receipt-binding.md,corpus/knowledge/register-cutoff-split.md`
→ new `coverage-map=missing:none`.

## The four correction blocks — `corpus/lessons/round-78.md` §Corrections

Exact shape the counter parses (one bullet + one prose line per block; `at` must be the sealed
revision). SC02Lesson's landed worktree draft carries the same values:

```text
- `corrected F3` old=`gate=arms:8/word:eight/newest:round77-instruments/tally:18` new=`gate=arms:9/word:nine/newest:round77-instruments/tally:22` at=`6c1550a14babaca092cfcc3106f792d695652200` date=`2026-11-04`
  The sealed row declared the retired eight-arm gate and the round-75 tally; the landed gate module carries nine arms with `round77-instruments` newest and the round-77 receipt prints `PRE_REPORT_SELFTEST pass=22 fail=0`.
- `corrected F4` old=`pointer=section:Mistakes 4` new=`pointer=section:Freeze divergences item 3` at=`6c1550a14babaca092cfcc3106f792d695652200` date=`2026-11-04`
  The record's last pointer sentence named §Mistakes 4, which holds the L1 mutating-git breach; the C3 predicate/ruling divergence is §Freeze divergences item 3.
- `corrected F5` old=`provenance=missing:corpus/knowledge/register-cutoff-split.md` new=`provenance=missing:none` at=`6c1550a14babaca092cfcc3106f792d695652200` date=`2026-11-04`
  The register-cutoff entry now carries an appended `source-correction:` line citing S073, whose added-path ground is the entry's introduction-discovery mechanics.
- `corrected F6` old=`coverage-map=missing:corpus/knowledge/baseline-receipt-binding.md,corpus/knowledge/register-cutoff-split.md` new=`coverage-map=missing:none` at=`6c1550a14babaca092cfcc3106f792d695652200` date=`2026-11-04`
  Appended coverage-map rows index both round-77 entries in `corpus/README.md`; appended, so no existing line moves.
```

## Verification

- All four `old` values re-derive at the sealed revision under the landed counter (see the
  derived= fields in `clone-pristine.out` / `clone-norepair.out` in this directory, and the
  committed enumeration `.ufo/waves/round-78/measured/before/c1-facts.out`, which they match).
- With the four blocks present but NO repairs, the clone prints
  `SELFRECORD_R77 claims=6 mismatches=4 corrected=0 unbacked=0`, exit 1
  (`clone-norepair.out` — the plan's do-nothing control).
- With blocks + repairs, the clone prints the frozen line, exit 0 (`scratch-run.out`).
