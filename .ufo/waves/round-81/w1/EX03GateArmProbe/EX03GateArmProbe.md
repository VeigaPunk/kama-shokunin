# EX03GateArmProbe — vacuous-green control for the gate arm-8 re-point (kama round 81, w1)

**Axis judged:** operability (C2 control 3 from `plans/round-81-claims.md`).
**Verdict: control proved.** The re-point of pre-report gate arm 8
(`tools/round75-append-accepted.py` → `tools/round81-append-debt.py`, plus new arm 11
`round81-instruments`) **cannot buy a green by itself**. The arm's green is carried entirely by
`registry/append-only-late.tsv`; every configuration without the late register is red or
fail-closed.

## Revisions

- Base: `e7d2fd729cf8204c89c32534303bc9f2a97fcee4` (round-80 closure tip; graded population
  `events=63 accepted=53 unaccepted=10`).
- Lane master moved during measurement:
  `f6cb5303 → 7eeae5bc → 88b35ea5 → 4f4bf2d2 → 1b96317` (read at five points; receipts pin the
  exact sha they ran at).
- Arm module: `tools/round81-append-debt.py` blob `28a6e840` at every tip measured (introduced as
  `4649b9a0` in `f6cb5303`, updated in `7eeae5bc`). Late register blob `1971576649` (88 data rows).
- History scan `e7d2fd7..master`: `2c1faed0` plan-only; **no commit ever carries the arm module
  without `registry/append-only-late.tsv`** (both landed together in `f6cb5303`).

## Receipts (all under this seat dir; each file carries its command and exit code)

| file | what it shows |
|---|---|
| `EX03-01-gate-base-round80.txt` | base gate `--round 80`: arm 8 `round75-instruments` FAIL, `APPEND_ACCEPTED events=63 accepted=53 unaccepted=10` |
| `EX03-02-round75-counter-base.txt` | frozen round-75 counter at base: red `unaccepted=10` |
| `EX03-03/04-aux-guard-*.txt` | module fail-closed (exit 2, `could-not-evaluate`) without the frozen plan **at the audited git revision** — worktree copies do not satisfy it; never silently green |
| `EX03-05-fixture-provenance.txt` | fixture commit `686c62cd` = base `e7d2fd7` + committed plan `b2fc59fc` + committed module `28a6e840`; late-register tree entry absent |
| `EX03-06-round81-fixture-base-nolate.txt` | **primary control**: the exact current arm module at the base population, late register absent → `APPEND_DEBT round=81 base=e7d2fd729cf8 events=63 accepted=53 late=0 pending=0 unaccepted=10 bad_rows=0 bad_declarations=0 out_of_population=0`, exit 1 — byte-identical to the plan's frozen "Before (base)" line |
| `EX03-07-tip-gate-emulation-at-base.txt` | tip's re-pointed gate run against the base revision: `PRE_REPORT_ARM round75-instruments exit=2 FAIL … could-not-evaluate: no frozen plan at e7d2fd729cf8204c89c32534303bc9f2a97fcee4:plans/round-81-claims.md`; arm 11 selftest green (fixture-pure, as expected) |
| `EX03-08-round81-tip-7eeae5bc.txt` | tip: `late=10 pending=0 unaccepted=0`, exit 0 |
| `EX03-09-round75-tip-7eeae5bc.txt` | old counter still red at tip (`unaccepted=10`) — structurally unsatisfiable, byte-intact as history |
| `EX03-10-round81-selftest-tip.txt` | `APPEND_DEBT_SELFTEST pass=16 fail=0` |
| `EX03-11-round81-tip-4f4bf2d2.txt` | latest tip: `late=10 pending=1 unaccepted=0`, exit 0 (`pending=<p>` is the frozen target's free variable; a round-81 record edit is pending-class) |
| `EX03-12-round75-tip-4f4bf2d2.txt` | old counter at latest tip: `events=64 … unaccepted=11` — the re-point was structurally necessary |
| `EX03-13-gate-tip-round81.txt` | re-pointed gate at the tip: `round75-instruments exit=0 ok … APPEND_DEBT … late=10 pending=1 unaccepted=0 …`; `round81-instruments exit=0 ok … SELFTEST pass=16 fail=0` |
| `EX03-14-round81-selftest-fixture.txt` | module selftest green inside the base fixture → the red `EX03-06` line is the population grading, not a broken fixture |

## Attribution (the item's question 3)

**The green is carried by the late rows, not by the re-point.** Same module blob `28a6e840`, same
base population: late register absent → `late=0 unaccepted=10` exit 1 (`EX03-06`); late register
present → `late=10 unaccepted=0` exit 0 (`EX03-08/11/13`). The re-point changes only which counter
speaks for arm 8; the counter's verdict moves only when the 88 committed late rows exist.

**Case where the re-pointed arm would print green without `registry/append-only-late.tsv`:
none exists in this population.** Three independent blockers, each demonstrated:

1. *Gradeable fixture without the register* → red `unaccepted=10`, exit 1 (`EX03-06`).
2. *Base revision as audited* → the module requires `plans/round-81-claims.md` at the audited
   revision and fails closed exit 2; the gate surfaces that as arm-8 FAIL (`EX03-07`, `EX03-03/04`).
3. *History* → no lane commit carries the module without the register (`2c1faed0` is plan-only;
   `f6cb5303` and later have both).

Arm 11's selftest is intentionally fixture-pure (`--selftest`, 16 cases incl. no-late-register and
same-round mutants, all red-checked); it passes identically at base and tip (`EX03-07/10/14`), so
it certifies the instrument, never the debt — it cannot be used to launder a vacuous arm-8 green.

## Notes, risks, blockers

- The gate's tip run shows `failed=1`: the `selfdesc` coverage-drift arm (`PROVINCE.md cited 364
  observed 376`). Outside this item; recorded for context.
- `pending` moved 0 → 1 between `7eeae5bc` and `4f4bf2d2` as the L1 committed round-81 record
  edits; the frozen target line specifies `pending=<p>`, and `unaccepted=0`/exit 0 hold at both.
- Lane tip moved five times during measurement; every receipt names the exact sha and clone it ran
  in (`$S/clone-base`, `clone-base2`, `clone-tip`, `clone-tip2` — scratch, since deleted).
- Fixture commits (`686c62cd`) exist only inside the scratch clone `clone-base`; the lane tree was
  never written to. No git write ran in the lane; no installs/upgrades were needed (python3/git
  only, pacman untouched per orchestrator pause).
- Dispatch trailer asked for the report at `.ufo/waves/round-81/w1/EX03GateArmProbe.md`; per the
  hard write-scope rule (seat dir only) it is filed here as
  `.ufo/waves/round-81/w1/EX03GateArmProbe/EX03GateArmProbe.md`.
