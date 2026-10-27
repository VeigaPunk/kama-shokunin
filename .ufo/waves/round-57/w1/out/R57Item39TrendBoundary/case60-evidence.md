# Distinct case 60 — do trend verdicts have a fail-capable control?

Seat: R57Item39TrendBoundary (sentinel). Distinct-case evidence file, separate from the seat
report. Read-only over the lane; the fixture is a scratch artefact copied here for replay.

## Question

`LEARNING.md:33-35` defines one observable per trend. The lane's only trend instrument is
`tools/round44-verdict-ledger-audit.py`. Does any lane instrument fail a round lesson that
claims `expansion: improved`, `quality: improved`, `discernment: improved` while none of the
LEARNING observables moved?

## Method

Frozen lane parser reused by import (not re-implemented), then:

1. parse the fabricated claim with the instrument's own `read_line()`;
2. compute the instrument's population (the 68 paths `side_spec()` can ever name);
3. scan all 74 `tools/*.py` for a trend-verdict token regex, for `corpus/knowledge`, and for
   `verified-at` reads;
4. derive the three observables at the measured tip;
5. run the frozen instrument and record its exit and line.

Fixture (`fabricated-round-57-trend-claim.md`, copied beside this file):

```text
## Learning trends

- **expansion: improved** — no admitted knowledge entry and no capability row is cited.
- **quality: improved** — no `verified-at` value is refreshed and no entry is re-verified.
- **discernment: improved** — no outside non-author spot-check exists for this round.
```

Command (run from the lane root; script copied beside this file):

```
python3 case60_trend_binding.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
        --fixture fabricated-round-57-trend-claim.md
```

## Exact output (`case60.out`)

```text
case=60
repo=/home/vgpnk/Projects/shokunin/kama-shokunin
tip=16efcf5eedf4887df188790eec48afbb023e7991 (git rev-parse HEAD)
tree_dirty=1 modified_tracked=0 untracked=12
frozen_trend_instrument=tools/round44-verdict-ledger-audit.py
instrument_round_scope=10..43 n=34
instrument_trends=expansion,quality,discernment
instrument_ledger=registry/verdict-ledger.tsv
instrument_scorecard_heading='### Round-44 calibration ledger'
fixture_claims=discernment:improved;expansion:improved;quality:improved
fixture_parsed_by_frozen_parser=True
instrument_population_paths=68
fixture_in_instrument_population=0
instrument_reads_knowledge_entries=False
instrument_reads_verified_at=False
tools_total=74
tools_parsing_trend_verdicts=round44-verdict-ledger-audit.py
tools_naming_corpus_knowledge=15
tools_reading_verified_at=7
observable.expansion.knowledge_entries=36
observable.expansion.last_knowledge_addition=0e6ff7a2 2026-10-25
observable.expansion.canonical_capability_rows=11 canonical_round=49
observable.expansion.head_capability_rows=11
observable.quality.entries_verified_at_2026-10-26_or_later=1
observable.quality.entries_missing_verified_at=0
observable.quality.entries_missing_recheck=0
observable.discernment.verifier_spotcheck_lessons=43
observable.discernment.latest_outside_round=56
observable.discernment.round56_outside_trend_lines=3
  outside_line=- Expansion — unchanged: report states no new admitted knowledge or capability; source rows alone do not count.
  outside_line=- Quality — improved: C1 detects LD_AUDIT and the exact-field negative control catches the substring false positive; receipts are committed. C2 is not credited.
  outside_line=- Discernment — harmed: this outside sample disagrees with the S513 rejection, and the lesson contains no learned correction/grounded new QUALITY criterion. Rou
observable.discernment.quality_criteria_rows=98
observable.discernment.quality_rows_citing_round-56=0
ledger.rows=204 header=9 cells
ledger.rounds=10..43 n=34
ledger.closed_rounds_44..56_unledgered=13
ledger.rounds_unledgered=44,45,46,47,48,49,50,51,52,53,54,55,56
ledger.kq61_expected_rows=282 missing=78
tools_reading_knowledge_and_naming_expansion=none
instrument_run.round44_verdict_ledger_audit_exit=0
instrument_run.round44_verdict_ledger_audit_out=tip=16efcf5eedf4887df188790eec48afbb023e7991 | rows=204 valid=204 missing=0 bad=0 agree=69 overclaim=2 underclaim=16 other=0 absent=15 table_missing=0 table_extra=0 summary=1 axes=1 met=True
instrument_met_predicate=met = 204 valid rows and table exact and summary exact and axes cite.
instruments_failing_fixture=none
result=FIXTURE_SURVIVES_ALL_LANE_INSTRUMENTS
EXIT=0
```

## Tip drift during the seat

The lane advanced five times while this seat measured:
`8640e34c` → `16efcf5e` → `77e7f5ee` → `3d2d5d4d` → `8a7f19760242bbe523fa2d7d1b22528b587633c1`. The
first run (at `8640e34c`) printed the identical lines with that tip. Two later runs are
stored beside this file: `case60-at-77e7f5ee.out` (sha256
`d715e4f469559f1c3f3f156a3bff164ded29169a5e4cf2a4c380d8975d7b5223`) and
`case60-at-8a7f1976.out`. Every observable line is unchanged across the tips, including
`rows=204 valid=204 … met=True` and `instruments_failing_fixture=none`. Only the `tip=` line
differs.

## What the test shows

1. The frozen parser recognises the fabricated claims: `read_line()` maps each trend word to
   `improved`. Vocabulary alone is therefore sufficient for the instrument's evidence rule —
   no observable is consulted.
2. The only trend instrument cannot see a round-57 claim at all: its population is 68 fixed
   paths (`corpus/lessons/round-<N>-verifier-spotcheck.md` and
   `.ufo/reports/round-<N>/kama.md` for N in 10..43). `fixture_in_instrument_population=0`.
3. No other tool parses trend verdicts: `tools_parsing_trend_verdicts` is exactly one file.
   The 15 tools that name `corpus/knowledge` are coverage/self-description counters, and the
   7 that read `verified-at` read it as a provenance field, not as a quality-trend verdict.
4. The instrument's own `met` predicate is documentary: 204 valid ledger rows + an exact
   SCORECARD table + an exact summary line + an axes citation. It prints `met=True` at this
   tip while 13 closed rounds (44–56) have no ledger row — 78 rows short of KQ61's
   "each closed round's pair is ledgered".

So the fabricated claim survives every instrument. This is an evidence limit, not a verdict:
it says nothing about what the round-57 verdicts ought to be, only that a trend verdict in
this lane is currently an un-instrumented assertion whose only shipped control is scope-bound
to rounds 10–43 and blind to the LEARNING observables.

## Limits of this test

- It tests *reachability* (can an instrument see and refuse the claim), not whether any
  specific filed verdict is true.
- The fixture was never placed in the lane tree; it lives only beside this file.
- The `met=True` run is the lane's committed instrument at `16efcf5e`, with the fleet repo
  supplied as `--fleet`; a different fleet rev could change the `absent` count but not the
  round scope.
