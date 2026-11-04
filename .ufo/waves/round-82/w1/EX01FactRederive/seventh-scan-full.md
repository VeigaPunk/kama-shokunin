# EX01 seventh-fact scan — every other declared numeric fact in the §Round 81 record

Scan surface (sealed `1b64f66d` unless noted): SCORECARD.md §Round 81 lines 4891-4951 +
`#### round-81 correction` block; LOG.md §Round 81 lines 3352-3417 (three appended corrections);
SKILL.md pre-report-gate row line 309; plus the appended `#### round-82 correction` block at the
tip (SCORECARD.md:4952-4960) and the tip LOG round-82 corrections (LOG.md:3452-3462).

## A. Numeric declarations that re-derive green against their cited receipt

| declaration (sealed bytes) | receipt | receipt prints |
|---|---|---|
| C1 row `SELFRECORD_R80_ENUM claims=6 stale=6 corrected=0` | `measured/before/c1-enum.out` | identical line |
| C1 row `SELFRECORD_R80 claims=6 mismatches=0 corrected=6 unbacked=0` | `measured/after/c1-green.out` | identical line |
| C1 row `pass=13 fail=0` (F6) | `measured/after/c1-selftest.out` | `pass=13 fail=0` |
| C1 row `mismatches=6` (no-corrections) | `measured/control/c1-no-corrections.out` | `mismatches=6`, exit 1 |
| C2 row before `events=63 accepted=53 late=0 pending=0 unaccepted=10 bad_rows=0 bad_declarations=0 out_of_population=0` | `measured/before/debt-base.out` | identical line |
| C2 row after, columns `events=63 accepted=53 late=10 unaccepted=0 bad_rows=0 bad_declarations=0 out_of_population=0` | `measured/after/debt-green.out` | all equal |
| §Round 81 `Frontier: registry 297 → 302 rows` | `corpus/SOURCES.md` S-row count at sealed/base | 302 |
| correction block `pass=9 -> pass=11` | `.ufo/waves/round-80/measured/after/c1-selftest.out` | `pass=11 fail=0` |
| correction block `pass=6 -> pass=12` | `.ufo/waves/round-80/measured/after/c3-selftest.out` | `pass=12 fail=0` |
| correction block `round-79 gate failed=0 -> failed=1` | `.ufo/waves/round-79/measured/after/c2-gate.out` | `failed=1`, `EXIT=1` |
| dispositions `final-tip-recheck.out` names rev `08eb6949` | `.ufo/waves/round-80/measured/after/final-tip-recheck.out` | `# rev: 08eb6949…` |
| dispositions `round 81 adds four distinct URLs` | S558/S559/S560/S561 (S562 shares S560's URL) | 4 distinct |
| §Gate `PRE_REPORT round=81 arms=11 failed=0 uncommitted=0` | `measured/after/gate.out` | identical line |
| §Gate `APPEND_DEBT_SELFTEST pass=22 fail=0` | `measured/after/debt-selftest.out` + `gate.out` | `pass=22 fail=0` at that receipt |
| §Gate `PRE_REPORT_SELFTEST pass=26 fail=0` | `measured/after/gate-selftest.out` | `pass=26 fail=0` |
| §Gate base control `unaccepted=10` | `measured/before/debt-base.out` | `unaccepted=10`, exit 1 |
| LOG C2 `88 committed rows` / `ten round-79/80 events` | `registry/append-only-late.tsv` @ sealed | 88 data rows / 10 distinct (commit,file) pairs |
| LOG wave `14 seats (3 executor, 3 scribe, 2 scout, 1 connector, 2 reviewer, 2 critic, 1 mutation-tester)` | `.ufo/waves/round-81/w1-results.json` | exactly those 14 and counts |
| LOG `LOG-CORRECTION … old=failed=0 new=failed=1` | `.ufo/waves/round-79/measured/after/c2-gate.out` | `failed=1` |
| LOG `LOG-CORRECTION … old=pass=16 new=pass=22` | module @ `2880af05` / `debt-selftest.out` | `pass=22` |
| tip `LOG-CORRECTION … old=pass=22 new=pass=25` | module @ tip `round81-append-debt.py --selftest` | `APPEND_DEBT_SELFTEST pass=25 fail=0` |
| tip `LOG-CORRECTION … claim=C2 pending=1 -> pending=4` | `debt-green.out` | `pending=4` |

## B. Numeric declarations stale against their receipt but already answered by a committed correction

| declaration | stale value vs receipt | answered by |
|---|---|---|
| LOG §Round 81 C2 bullet `selftest pass=16 fail=0` | receipt prints `pass=22` | `LOG-CORRECTION … old=pass=16 new=pass=22` (LOG.md:3410 sealed) |
| LOG §Round 81 C2 bullet after-line `pending=0` | receipt prints `pending=4` | `LOG-CORRECTION … pending=0 -> pending=1` (LOG.md:3388 sealed); that new value is itself stale — graded as F5 |
| §Round 81 §Gate / head operability row `pass=22` | tip module prints `pass=25` | tip `LOG-CORRECTION … old=pass=22 new=pass=25` (LOG.md:3454 tip) |

These three are correction-answered, not omissions: the record names each superseded value.

## C. The one live numeric statement contradicted by the tree (NOT receipt-bound, NOT graded)

Tip `SCORECARD.md:4958` (inside the appended `#### round-82 correction` block that sits in the
§Round 81 region, immediately before `## Round 82` at line 4962):

    - `log81-frontier-rows=302` — the `LOG.md` §Round 81 frontier line said 301; the tip registry holds 302.

The claim "the tip registry holds 302" is false at the commit that writes it, `962bd251`
(2026-11-04): that same commit adds S563–S565, so `corpus/SOURCES.md` carries **305** rows there
(parent `5fe3c58c`: **302**). The round's own record names the divergence —
`corpus/lessons/round-82.md:85-92` (freeze divergence 5): "301 (declared) → 302 (base) → 305 (tip)".
The corrected token `log81-frontier-rows=302` is still right for the sealed/base witness, and the
counter binds F2 to the base revision (`registry-base-bound` selftest arm), so the token is graded
green while the prose sentence is wrong. Not a seventh graded fact; it is prose drift in a
correction block, and no receipt is cited for it.

## Verdict

No seventh *receipt-stale, uncorrected* numeric fact exists in the §Round 81 section: every
remaining numeric declaration either re-derives against its receipt (A) or is a superseded value
named by a committed correction (B). The only tree-contradicted live numeral is the correction
prose at SCORECARD.md:4958 (C).
