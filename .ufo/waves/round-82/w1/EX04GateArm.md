# EX04 — the vacuous-green control and the round-82 gate arm proposal (executor report)

Milestone: kama r82 w1. Judged on: operability. Seat EX04GateArm.
Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` read-only for this seat; the gate was not edited and no
production file was touched. Every path below is absolute or relative to the lane as stated.
Tips used: lane `master` = `bacae0726d7c53455bd083bc6d478bbcd6e7fffc` (read with `git -C … rev-parse master`;
git HEAD in the lane is detached and was never read from `@{u}`); base `aaf974dbd3b6adb2ef914dc7293cda92b4e05551`;
sealed `1b64f66ddea89c57b71165eacd14b0e1d6f24e11`.
Scratch root `$S = /fast/scratch/hyaku/kama-r82/EX04GateArm` (deleted before yield; receipts copied to this seat dir).
Tooling installs: none needed.

## 1. Base control: the frozen round-81 chain at `aaf974db`

Scratch clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/clone"` then
`git -C "$S/clone" checkout --detach aaf974db…`; `git -C "$S/clone" rev-parse --show-toplevel` printed
`/fast/scratch/hyaku/kama-r82/EX04GateArm/clone` before any use. Nothing was copied from the lane worktree:
all four runs use the clone's own files at the base.

| id | command (cwd = `$S/clone`) | exit | line |
|---|---|---|---|
| A | `python3 tools/round81-append-debt.py --repo . --round 82` | 2 | `could-not-evaluate: no frozen plan at aaf974dbd3b6adb2ef914dc7293cda92b4e05551:plans/round-82-claims.md` |
| B | `python3 tools/round81-append-debt.py --repo . --round 81` | 0 | `APPEND_DEBT round=81 base=e7d2fd729cf8 events=63 accepted=53 late=10 pending=5 unaccepted=0 bad_rows=0 bad_declarations=0 out_of_population=0` |
| C | `… --round 81 --late $S/empty.tsv` (header only) | 1 | `APPEND_DEBT round=81 base=e7d2fd729cf8 events=63 accepted=53 late=0 pending=5 unaccepted=10 bad_rows=0 bad_declarations=0 out_of_population=0` |
| D | `… --round 81 --late $S/one-row.tsv` (header + first real row) | 1 | `APPEND_DEBT round=81 base=e7d2fd729cf8 events=63 accepted=53 late=0 pending=5 unaccepted=10 bad_rows=1 bad_declarations=0 out_of_population=0` |

(a) The round-82 plan is absent at `aaf974db` (`plans/` newest is `round-81-claims.md`), so the round-82 label is
unevaluable there — exit 2, not a red line. Per the item I ran `--round 81` instead and recorded its line (B): it is
green, `late=10`, `pending=5` (the five round-81 record-edit events are post-base and out of its graded population).

(b) Empty late-register fixture: the exact finding class is `APPEND_DEBT_FINDING count-short` — 88 lines over 10
unaccepted events (9 distinct event commits; e.g. `count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d
corpus/lessons/round-79.md <sha>: missing 1`). `bad_rows=0` because the header-only register has no rows to reject.
I also fed **one real row** through the same `--late` switch (D): it produces exactly one
`APPEND_DEBT_FINDING unbound-register late line 2: …` (`bad_rows=1`) on top of the same 88 `count-short` lines.
That is the "unbound" the item names: `--late` sets `late_intro = None` and never calls `blame_rows`, so no supplied
row can carry an introducing commit and none can accept anything.

Why neither run can be green without the late rows (one paragraph): the counter's population is the frozen audit's
undeclared deletions, and an event is scored only through a committed `registry/append-only-late.tsv` row whose OWN
introducing commit is a strict descendant of the event commit — nothing else in the tree can substitute. With
`--round 82` at the base it cannot even evaluate, because the plan that carries the base revision does not exist yet
(A). With `--round 81` it is green only because the ten round-81 late rows are committed in that tree; that
population is not the round-82 debt — the five round-81 record-edit events (`cf28c470`, `37484391`, `50c711ec`,
`93cdfd60`, `017c34ca`, 9+1+3+1+1 = 15 undeclared lines) are post-base for round 81 and the base register holds 88
rows with zero rows for them (measured). Remove the rows and the same counter turns those ten previously-late events
into `unaccepted=10` (C); pass rows around the committed register and they are `unbound-register` and accept nothing
(D). So green is reachable only by committed per-row bytes with resolvable introductions. Corroboration from the
frozen round: `.ufo/waves/round-82/measured/before/c2-debt-base.out` = `unaccepted=5` with 15 `count-short` findings,
and `…/c2-late-delta-base.out` = `carried=88 new=15 bad=15` with 15 `LATE_DELTA_FINDING missing`.

Retained receipts: `receipts/ex04-base-debt-r82.out`, `receipts/ex04-base-debt-r81.out`,
`receipts/ex04-empty-late.out`, `receipts/ex04-one-row-late.out` (all under this seat dir).

## 2. Arm-12 spec for `tools/pre-report-gate.py` (verified at the tip; the arm is committed at `5fe3c58c`)

**Which commands.** Arm 12 `round82-instruments` runs exactly two commands, cwd = `--repo`, scripts resolved from
`<repo>/tools` (or `--tools-dir`):

    python3 tools/round82-selfrecord-round81.py --selftest
    python3 tools/round82-late-delta.py --selftest

Each must exit 0 and its LAST non-empty line must fully match its own `<PREFIX> pass=N fail=0`
(`SELFRECORD_R81_SELFTEST`, `LATE_DELTA_SELFTEST`); an absent module is `missing <script>`, a nonzero exit or a red,
foreign or malformed summary is `missing valid final selftest summary: <line>`. The third command the item lists,
`python3 tools/round81-append-debt.py --repo <repo> --round 82`, is **not** part of arm 12: it is arm 8
`round75-instruments`' third member (`ROUND75_MODULES` key `append-debt`, `{round}` substituted) and is the round's
live debt leg. Duplicating it inside arm 12 would run the audit twice and conflate wiring with data.

**ARM_ORDER position.** `ARM_ORDER` = the five `ARM_SPECS` names (`selfdesc`, `newest-closure`, `receipt-audit`,
`worktree-landing`, `round-scope`) + `round-clean` + `round74-v2`, `round75-instruments`, `round77-instruments`,
`round78-instruments`, `round81-instruments`, `round82-instruments`. Arm 12 is index 11 (12th and last), after
`round81-instruments`; `round-clean` stays the 6th; `evaluate()` appends arm 12 last, and `render()` prints in that
order. Measured: `PRE_REPORT round=70 arms=12 failed=0 uncommitted=0`.

**Expected verdict lines (measured in the tip selftest).**

- green: `PRE_REPORT round=70 arms=12 failed=0 uncommitted=0`
  (`PRE_REPORT_ARM round82-instruments exit=0 ok round82-selfrecord-round81.py exit=0 ok SELFRECORD_R81_SELFTEST pass=18 fail=0 | round82-late-delta.py exit=0 ok LATE_DELTA_SELFTEST pass=12 fail=0`)
- red: `PRE_REPORT round=70 arms=12 failed=1 uncommitted=0`, detail `SELFRECORD_R81_SELFTEST pass=2 fail=1`
- missing: `PRE_REPORT round=70 arms=12 failed=1 uncommitted=0`, detail `missing round82-selfrecord-round81.py`
- selftest total: `PRE_REPORT_SELFTEST pass=29 fail=0`, exit 0 (0 FAIL lines)

**Every place that must change** (all in `tools/pre-report-gate.py` unless noted; line numbers at the tip):

Already present and matching the spec: docstring predicate quote `arms=12` (:13); arm-count history "from round 82 on
it prints `arms=12`" (:25); numbered list entry `12 round82-instruments` with both scripts (:50-51); output spec
(:123); rounds narrative (:196); `PREDICATE` prose naming arm 12's counter pair (:233-235); `ARM_ORDER`
(:250-252); `ROUND82_MODULES` (:327-330); `_round82_instruments` (:517-545); `evaluate()` append (:655);
`VERDICT_RE` keys (:266-267) and `_DEFECT_ARMS` keys (:285-286); fixture stubs (:881, :892); selftest cases (z)
green/red/missing (:1391-1409); `main()` argparse description (:1427).

Still stale and therefore still to change:

1. `PREDICATE` constant's target line still reads `arms=11` (:223) although its own prose names arm 12 and the
   docstring says the same sentence is the PREDICATE — must read `arms=12`.
2. Docstring Exit sentence: "across all ten arms" (:107) → twelve.
3. Docstring selftest legend: (h) :155, (n) :163, (q) :168, (t) :173 each say ``verdict `arms=11` `` — measured
   green cases print `arms=12`; the legend stops at (u) and has no entries for the arm-11 case or the arm-12 (z) cases.
4. Docstring wiring-tally sentence "move the selftest tally 22 -> 26" (:204) → the measured tally is 29, or drop the
   number.
5. Selftest case comment (:1369) "(x) green arm-11 stubs: the arm passes and the verdict carries ten arms" — the
   label is `round78-instruments-green` and the verdict carries twelve arms.
6. Inert registrations: `round81-instruments-debt`, `round82-instruments-selfrecord`, `round82-instruments-late-delta`
   in `VERDICT_RE`/`_DEFECT_ARMS` can never fire because `_round77/78/81/82_instruments` build their detail with
   `_last_line`, not `_detail`; either drop them or route the runner through `_detail`. (The `round76-*` keys are
   documented retired-arm history and stay.)

**Arm-count assertions that would break.** `check()` asserts `[a["name"] for a in result["arms"]] != ARM_ORDER`, which
is dynamic and auto-adapts; the arm-count failures are the eight literal
`want_line="PRE_REPORT round=70 arms=12 failed=0 uncommitted=0"` strings — they break if arm 12 is dropped from
`ARM_ORDER` or not appended in `evaluate()` (the verdict would print 11). There is no `len(arms) == 12` literal: the
verdict interpolates `arms={len(arms)}` (:658). No instrument parses the SKILL row's arm count; `fact_f3` of
`tools/round82-selfrecord-round81.py` reads SKILL at the sealed revision and witnesses `arms=11` from the round-81
gate receipt, so the round-81 receipt stays valid and the live row may say twelve.

**One-line SKILL.md registry edit.** `SKILL.md` line 309 (the `Pre-report gate` row) is currently malformed: 6 cells
in a 5-column table (7 pipes), its exit map still says "all ten arms … `arms=10 failed=0`", its self-test cell still
says `pass=26`, and the arm-11/arm-12 text was appended after the closing write-scope cell. Replace that single line
with the 5-cell row stored verbatim in `EX04.json` (`part_2_arm12_spec.skill_row_edit.proposed_row`): arms 11 and 12
folded into cell 2, exit map `arms=12`, `PRE_REPORT_SELFTEST pass=29 fail=0` with receipt
`.ufo/waves/round-82/measured/after/gate-selftest.out`, one `Removed temp fixtures only` write-scope cell. The cited
receipt must be committed in the same or an earlier commit or `gate-registry-check.py` grades the row
`missing-path`. Verified by simulation in `$S/clone-tip`: the row parses as 5 cells and
`python3 tools/gate-registry-check.py` prints `registered 101 unregistered 10 defective 0`, identical to the
unmodified tip (`receipts/gate-registry-check-tip.out`, `receipts/registry-check-proposed-row.out`; the 10
unregistered are pre-existing round-76/79/80/81 counters, none of them round-82).

Note the tension with the frozen plan's prose: it says the SKILL row is updated in place to *eleven* arms. That
sentence describes the round-81 record's correction (F3, graded at the sealed revision); at the round-82 tip the gate
has twelve arms, so eleven would make the live registry row false. Twelve is the correct live value.

## 3. Tip measurements used for the spec check (read-only, scratch clone)

- `python3 tools/pre-report-gate.py --selftest --work $S/st-work` → exit 0, `PRE_REPORT_SELFTEST pass=29 fail=0`
  (`receipts/gate-selftest-tip.out`).
- `python3 tools/round82-selfrecord-round81.py --selftest` → exit 0, `SELFRECORD_R81_SELFTEST pass=19 fail=0`
  (the gate stub prints 18; only the prefix and `fail=0` are graded).
- `python3 tools/round82-late-delta.py --selftest` → exit 0, `LATE_DELTA_SELFTEST pass=12 fail=0`.
- `python3 tools/round81-append-debt.py --repo . --round 82` at the tip → exit 0,
  `APPEND_DEBT round=82 base=aaf974dbd3b6 events=68 accepted=53 late=15 pending=2 unaccepted=0 bad_rows=0 bad_declarations=0 out_of_population=0`.
- `python3 tools/round82-late-delta.py --repo . --round 82` at the tip → exit 0,
  `LATE_DELTA round=82 base=aaf974dbd3b6 population=103 carried=88 new=15 bad=0`.

## 4. Risks and blockers

- The tip already carries the 15 round-82 rows, so the vacuous-green control ("the arm is red at the freeze tip on the
  debt leg, `unaccepted=5`") is no longer reproducible at the current tip; it is provable at the base (runs A–D) and
  from the committed pre-data receipt `.ufo/waves/round-82/measured/before/c2-debt-base.out` (`unaccepted=5`, 15
  count-short findings). Wiring still buys no data: arm 12 runs only `--selftest` against stub fixtures, so it is
  green regardless of the round's rows.
- If the L1 reverts the SKILL row to eleven arms (plan prose), the row will contradict the tip gate (`arms=12`);
  F3 is sealed-bound and the live row should say twelve.
- No blockers. No production edits, no commits, no installs; `$S` removed after receipts were copied.
