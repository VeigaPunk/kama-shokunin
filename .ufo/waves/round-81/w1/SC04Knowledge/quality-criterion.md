Criteria added — round 81 mistake (2026-11-04; no outside review yet)

KQ133 stays in force and binds the self-record's own numbers. This row carries the round-81 mined
class into a broader admission check: a record cites a receipt that prints another tally than the
record states. The instance is the round's own C2 instrument — the plan target and the repaired
counter print `accepted=53`, while the retained after-receipt was taken before the `accepted`
bucket repair and prints `accepted=63`, and the lesson's Freeze divergence 3 says the repair came
"before any receipt was taken".

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ134 | A record, claim or report that cites a receipt for a counter tally states the tally that receipt's own summary line prints, and the preserved receipt is one the cited module still reproduces at the revision the record names. Check: `python3 tools/round81-append-debt.py --repo . --round 81` prints `APPEND_DEBT round=81 base=e7d2fd729cf8 events=63 accepted=53 late=10 pending=<p> unaccepted=0 bad_rows=0 bad_declarations=0 out_of_population=0`, `python3 tools/round81-late-rows.py --repo . --round 81 --check` prints `LATE_ROWS check=ok rows=88`, and every cited `measured/**` receipt prints the same cells the record states. | The cited receipt prints a different tally than the record (`.ufo/waves/round-81/measured/after/debt-green.out` prints `accepted=63` against the target's `accepted=53`), a receipt produced before the counter's last repair is cited after it, a `--check` re-deriving fewer cells than the register holds is read as green, or the record reconciles two receipts without naming which one it follows. | `corpus/lessons/round-81.md` §Freeze divergences 3 and §Mistakes (`number-drift`); continuation of KQ133 from the self-record to any cited receipt |

Placement note (not part of the row): the item froze "next free number after KQ132", but KQ133
landed at `corpus/QUALITY.md:639` before this draft was written (it binds the round-80 self-record
tally against `tools/round81-selfrecord-round80.py`). This row therefore takes KQ134 so the two
checks stay separately citable; if the L1 prefers one row, KQ133's text needs only the
second check command and the acceptance-tally limit added.
