# Distinct case 24 — independent stale-maxN check

Seat `R57Item03CounterRepair`. This file is the separate evidence file for the assigned distinct case ("test the assigned case independently"). It shares no code with `run.sh`, `maxn-cases.py` or the prototype's `live_lines`; the checker `case24-independent.py` re-derives every value with its own scanners and builds its own fixture. Raw transcript: `receipts/case24-independent.out`.

## Method

1. Read `SCORECARD.md` at three pinned commits with `git show <commit>:SCORECARD.md` (read-only).
2. Derive maxN twice with different code:
   - regex over every raw line matching `^## Round (\d+)` (what the frozen counter does);
   - an independent line state machine that tracks fence character/length and multi-line HTML comments, then takes the max over live headings.
3. Assert the frozen claim's `46` is not tree-derived at the base: locate a historical commit where 46 was the live max, and inspect the frozen no-op control's source.
4. Build a fresh fixture (base SCORECARD + a restored fenced block carrying `## Round 99`), commit it under scratch, assert `git rev-parse --show-toplevel` is the fixture dir, then run the frozen and prototype counters against it.

## Exact output (`receipts/case24-independent.out`, exit 0)

```
rev|regex_maxN|state_machine_maxN
4340cf2f68ebbfb618086e16825c2e7effd7fa58|46|46
b89bdab2cc114735ec5d331c6c610134258f7864|56|56
8640e34cad02adcd247ba0862da63f6fb2aab0df|57|57
noop_literal_46= True
noop_reads_tree= False
fixture_toplevel_matches= True
fixture_base_exit=1
fixture_base_summary=r41=36 banner=1 planned=2 retired=0 saturation=0 caps=0 receipts=9 readme=1 province=14 rel=0 mismatches=63 maxN=99 met=False
fixture_build_exit=1
fixture_build_summary=r41=36 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=9 readme=1 province=14 rel=0 mismatches=60 maxN=56 met=False
stale_fixture_base_maxN=99 stale_fixture_build_maxN=56
case24_ok= True
```

## Findings

- `46` is the live maxN at `4340cf2f` (round 46); at the frozen round-57 base `b89bdab2` the live maxN is `56`, and at `8640e34c` it is `57` (round-57 section committed). The claim's "expected 46" therefore names a historical value, not a value derivable from the measured tree.
- `46` is also the literal printed by `.ufo/waves/round-57/controls/c1-noop.py`, a file that opens no tree bytes and spawns nothing. A checker keyed to 46 accepts that no-op and rejects the real counter (`receipts/naive-gate46-noop.out`, `receipts/naive-gate46-real-base.out`).
- The latent staleness this seat repairs is real and independently reproduced: a fenced restored heading inflates the frozen counter to `maxN=99` (and drags the derived `### Planned (round 100)` requirement), while the fence-aware prototype reports `maxN=56` and requires `### Planned (round 57)`. The fixture is incomplete by design (SCORECARD only), so both runs are red on the other facts; the compared metric is the derived maxN.
- Live-heading positive control: an unfenced `## Round 99` yields 99 in both counters (`receipts/*-fixture-live-stale.out`), so the repair does not hardcode 56.

## Scope note

This case tests the assigned stale-maxN defect only. Canonical-row selection (`canon()`) is untouched and still selects a fenced stale canonical table (`receipts/canon-scope-limit.out`); that belongs to the canonical-binding seats.

Report: .ufo/waves/round-57/w1/out/R57Item03CounterRepair/case24-independent.md
