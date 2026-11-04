# SCR02Lesson — round 74, wave 1 (lesson draft + seat-count check tool)

Seat axes: **calibration**. Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`,
master `b0b903a0854365fbf4d1ba4d18ae9a66052cce4f` at every receipt header below
(freeze base per the plan header: `868dd701`). Scratch
`/fast/scratch/hyaku/kama-r74/SCR02Lesson` (deleted before yield; the tool
honours TMPDIR and every fixture landed under it). No mutating git/jj command
was run anywhere; no byte-frozen tool was touched; no tool was installed (none
needed — stdlib only).

## What was built

1. `tools/round74-seat-count-check.py` (new, 294 lines, sha256
   `e52d2183fa4cabec83eba1c3177f17434ce6f44e1e4280eedc42aafe7f03a227`).
   Two arms plus a selftest:
   - `--spec PATH` recomputes the seat count from `len(spec["items"])` and
     fails (exit 1) when a prose field (`milestone`, `context`) names a
     different count via a `(\d+)\s+seats?\b` token (case-insensitive).
     Findings print as
     `SEAT_COUNT_CHECK_FINDING number-drift <field>: prose names <p> seats, items carries <n>`,
     then one `SEAT_COUNT_CHECK spec=<p> items=<n> prose_counts=<...> verdict=ok|drift` line.
   - `--census-order DIR` scans a round dir's committed `*.out` receipts for
     the first `mode=mirror-* exit=0` line and the first registry-append
     marker (a line carrying both `sha256 before=` and `after=`, or naming the
     `corpus/SOURCES.md append`), flattened in (relpath, line-no) order, and
     fails (exit 1) when the exit-0 mirror census postdates the append marker.
   - Exit map: 0 clean, 1 findings, 2 could-not-evaluate (CLI misuse, unreadable
     spec/no items array, missing census or append population). `--selftest`
     builds all fixtures under `$TMPDIR` — no hardcoded `/tmp`.
2. Lesson draft `.ufo/waves/round-74/w1/SCR02Lesson/drafts/round-74.md`
   (`## Gate` with the three frozen-plan candidates filled; `## Mistakes` with
   the two routed rows). The real `corpus/lessons/round-74.md`, the r73 spec
   and every other lane file were not touched.

## Gate candidate facts (verified from committed bytes, not copied from peers)

- **S546 os-release(5).** Registry has no os-release row (`grep -i os-release
  corpus/SOURCES.md` → no match, exit 1); registry maximum is S545
  (`grep -o 'S5[0-9][0-9]' corpus/SOURCES.md | sort -u | tail -1` → S545;
  285 `| S` rows), so the next id is S546 — the direction SCR01Sources derived
  in its draft `.ufo/waves/round-74/w1/SCR01Sources/drafts/SOURCES-S546-row.md`,
  which exists at this report. The retained bytes
  `.ufo/waves/round-74/w1/SCR01Sources/source/os-release.5.html` sha256
  `c7ba68ea45180c33bad72a3b47cf09e3d6d34d0a5313a5acf73a14fc64f8a74e`; my own
  tag/entity-stripped substring search on the retained file finds the quoted
  `ID=` sentence verbatim ("identifying the operating system, excluding any
  version information and suitable for processing by scripts"). The draft row
  cites it as §OPTIONS `ID=` entry, lines 187–194 of the retained HTML.
- **Assimilation none.** `.ufo/waves/round-74/assimilation/summary.out`:
  `reg_ids=285 staged_ids=142 collisions=9 quarantine_rows=7` (ids S330 S333
  S334 S335 S346 S347 S352 S353 S363; quarantine S200 S202 S206 S210 S211
  S224 S230). Same class as round 73's gate decision: no entry re-grounded, so
  none admitted; id-collision receipt pointer recorded in the draft.
- **considerthese/2026-10-26.md.** Proposal 4 (morning pin-gap line) is
  recorded as landed in round 73 (`corpus/QUALITY.md` KQ122 references it;
  receipt `.ufo/waves/round-73/w1/SCR02Knowledge/pin-watch.out`); proposals
  1–3 are daily-pass workflow. Disposition: re-opened, none adopted.

## Commands run, with observed output

Selftest (fixtures under scratch via TMPDIR):

```
$ TMPDIR=/fast/scratch/hyaku/kama-r74/SCR02Lesson/fixtures PYTHONDONTWRITEBYTECODE=1 \
    python3 tools/round74-seat-count-check.py --selftest
SEAT_COUNT_CHECK_SELFTEST_ARM spec-drift-red got=1 want=1 PASS
SEAT_COUNT_CHECK_SELFTEST_ARM spec-clean-green got=0 want=0 PASS
SEAT_COUNT_CHECK_SELFTEST_ARM spec-clean-not-vacuous got=0 want=0 PASS
SEAT_COUNT_CHECK_SELFTEST_ARM spec-noitems-exit2 got=2 want=2 PASS
SEAT_COUNT_CHECK_SELFTEST_ARM spec-absent-exit2 got=2 want=2 PASS
SEAT_COUNT_CHECK_SELFTEST_ARM census-honest-green got=0 want=0 PASS
SEAT_COUNT_CHECK_SELFTEST_ARM census-r73-ordering-red got=1 want=1 PASS
SEAT_COUNT_CHECK_SELFTEST_ARM census-flip-guard-red got=1 want=1 PASS
SEAT_COUNT_CHECK_SELFTEST_ARM census-nocensus-exit2 got=2 want=2 PASS
SEAT_COUNT_CHECK_SELFTEST_ARM census-noappend-exit2 got=2 want=2 PASS
SEAT_COUNT_CHECK_SELFTEST pass=10 fail=0
# exit=0
```
(committed: `selftest.out`. The honest/census fixture families also prove the
green is not vacuous: swapping the two lines of the honest fixture flips it
red — `census-flip-guard-red`.)

Required red demo, real r73 spec bytes:

```
$ PYTHONDONTWRITEBYTECODE=1 python3 tools/round74-seat-count-check.py \
    --spec .ufo/waves/round-73/w1-spec.json
SEAT_COUNT_CHECK_FINDING number-drift milestone: prose names 14 seats, items carries 15
SEAT_COUNT_CHECK_FINDING number-drift context: prose names 14 seats, items carries 15
SEAT_COUNT_CHECK spec=.ufo/waves/round-73/w1-spec.json items=15 prose_counts=14,14 verdict=drift
# exit=1
```
(committed: `r73-spec.out`. Raw derivation pasted in the lesson draft and
committed as `r73-drift-derivation.out`: `items count: 15; prose milestone:
['14']; prose context: ['14']`.)

Required green run, real r74 spec:

```
$ PYTHONDONTWRITEBYTECODE=1 python3 tools/round74-seat-count-check.py \
    --spec .ufo/waves/round-74/w1-spec.json
SEAT_COUNT_CHECK spec=.ufo/waves/round-74/w1-spec.json items=13 prose_counts=13,13 verdict=ok
# exit=0
```
(committed: `r74-spec.out`.)

R73 census-ordering replay (mistake 2's red demo on committed bytes):

```
$ PYTHONDONTWRITEBYTECODE=1 python3 tools/round74-seat-count-check.py \
    --census-order .ufo/waves/round-73
SEAT_COUNT_CHECK_FINDING census-order first exit-0 mirror census at w1/SCR01Sources/census.out:16 postdates the registry-append marker at w1/SCR01Sources/census.out:2
SEAT_COUNT_CHECK census_order dir=.ufo/waves/round-73 census_exit0_first=w1/SCR01Sources/census.out:16 append_first=w1/SCR01Sources/census.out:2 verdict=ordering-violation
# exit=1
```
(committed: `census-order-r73.out`. Ground truth cross-check, independent of my
tool: the only `^mode=mirror-` lines in the whole round-73 tree are
`census.out:8 mode=mirror-preland exit=1` and `census.out:16
mode=mirror-postland exit=0`; the append markers are `census.out:2` (`#
corpus/SOURCES.md append, round-73 Frontier step`) and `census.out:4`
(`sha256 before=… after=…`). The closure's §6 item 6 wording ("the append
preceded the first exit-0 mirror") matches the receipt exactly.)

CLI misuse:

```
$ PYTHONDONTWRITEBYTECODE=1 python3 tools/round74-seat-count-check.py
usage: round74-seat-count-check.py [-h] [--spec PATH] [--census-order DIR] [--selftest]
# exit=2
```

## Notes and limits

- Marker scan is `*.out`-only, so report tables (e.g. `SCR01Sources.md`'s
  fenced "exit=0" summary) cannot pollute the ordering; cross-file order uses
  deterministic (relpath, line-no) flattening — the r73 replay lives in one
  file and is robust to that choice.
- The seat token is deliberately narrow (`N seats`/`N seat`); other count
  phrasings are outside this instrument's population, as the lesson states.
- No disagreement with the freeze: the plan's Frontier step names exactly the
  two lesson mistakes and the three `## Gate` candidates this draft fills.
- The S546 row's `status` stays queued until SCR01Sources' mirror census
  records exit 0 and the L1 appends — per mistake 2, the ordering is the
  gate, and this seat's `--census-order` arm is the replayable check for it.

## Files written (exact)

- `tools/round74-seat-count-check.py` (new instrument)
- `.ufo/waves/round-74/w1/SCR02Lesson/drafts/round-74.md` (lesson draft)
- `.ufo/waves/round-74/w1/SCR02Lesson/{selftest,r73-spec,r73-drift-derivation,r74-spec,census-order-r73}.out` (receipts, each first line `# rev=b0b903a0854365fbf4d1ba4d18ae9a66052cce4f`)
- `.ufo/waves/round-74/w1/SCR02Lesson/report.md` (this report)
- Trailer: `.ufo/waves/round-74/w1/SCR02Lesson.md`
