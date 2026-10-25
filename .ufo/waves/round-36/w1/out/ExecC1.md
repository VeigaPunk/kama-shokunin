# ExecC1

Tool not edited. Predicate not changed. No subagent spawned.

## noop

command: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6`

line: `uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`

exit: 1

## selftest

command: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6 --selftest`

line: `SELFTEST empty_met=False bad_met=False words=20 pass=1`

second stdout line: `empty uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`

exit: 0

## files changed

None in the tool or corpus. This report is the only write.

## behavior

Noop at the frozen tip prints met False and exits 1. Selftest prints pass=1 and exits 0. Both stdout bodies match `.ufo/waves/round-36/controls/c1-noop.out` and `.ufo/waves/round-36/controls/c1-selftest.out`.

## exact evidence

- noop line: `uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`
- noop exit: 1
- selftest line: `SELFTEST empty_met=False bad_met=False words=20 pass=1`
- selftest exit: 0

## remaining risks

None for this seat. The do-nothing control is met False, as already printed. That is not a tool defect found by this run.

## blockers

None.
