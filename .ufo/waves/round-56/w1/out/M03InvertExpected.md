# M03InvertExpected — C1 positive-control expectation mutation

## Result

**KILLED by the behavioral battery.** Inverting the positive-control run's expected outcome from `detected` to `missed` makes the live round-56 counter return `ld_audit=detected`, while the test expects `missed`; its leg exits 1 and the battery exits 1. Pristine and restored copies both exit 0. The mutant does not change any shared/lane files; all mutated copies and test receipts were under this seat's `/fast/scratch/hyaku/kama-r56/M03InvertExpected/` scratch.

## Mutant and detector

- **Assigned mutant (driver EXPECT):** in a private copy of `tools/round56-env-leg-battery.py`, change only the `round56-counter` `run()` argument from `"detected"` to `"missed"` (the `ROSTER` literal remains unchanged). The copy's `OUT` and internal scratch paths were redirected to this seat's scratch so execution could not write to shared measured outputs. No test logic or expected-result check was altered.
- **Expected detector:** execute the battery driver; the positive-control leg fails its exact expected-value/exit check and battery exits 1.
- **Observed detector:** as expected. Baseline: all 3 legs pass, `battery_exit=0`. Mutant: baseline passes, positive-control prints `ld_audit=detected exit=1 -> fail`, kill leg passes, `battery_exit=1`. Restored: all 3 legs pass, `battery_exit=0`.

Command (each invocation ran `python3 <copy-of-battery>.py` from the seat scratch; environment set `TMPDIR=/fast/scratch/hyaku/kama-r56/M03InvertExpected/tmp`):

```text
== d1-pristine
base-old-counter: ld_audit=missed exit=0 -> pass
round56-counter: ld_audit=detected exit=0 -> pass
m-drop-ldaudit: ld_audit=missed exit=0 -> pass
battery_exit=0

== d1-mutA-expect-missed
base-old-counter: ld_audit=missed exit=0 -> pass
round56-counter: ld_audit=detected exit=1 -> fail
m-drop-ldaudit: ld_audit=missed exit=0 -> pass
battery_exit=1

== d1-restored
base-old-counter: ld_audit=missed exit=0 -> pass
round56-counter: ld_audit=detected exit=0 -> pass
m-drop-ldaudit: ld_audit=missed exit=0 -> pass
battery_exit=0
```

## ROSTER field distinction

The positive-control `expected` is also declared in the battery's `ROSTER` literal, which the driver does not consult. As an additional probe, changing only that literal from `detected` to `missed` leaves all three behavioral driver legs green (`battery_exit=0`); the frozen `round56-prereg-check.py` rejects the resulting committed-blob fixture with `roster_match=0`, `met=False`, exit 1. Its pristine fixture is green (`roster_match=1`, exit 0), while the driver-argument mutant's fixture stays green at the roster checker. This shows the EXPECT-as-driver mutation is killed by the battery, and the ROSTER-only mutation by C2; it does **not** claim the battery driver itself evaluates ROSTER.

The paired D2 outputs are in `receipts/d2-*.console`. Scratch fixtures were initialized as isolated git repositories and each was checked with `git rev-parse --show-toplevel` equal to its fixture path before the fixture commit. Checker command: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round56-prereg-check.py --repo <scratch-fixture> --tip HEAD`.

## Hashes and restoration

- Committed battery before and after: `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c`.
- Frozen counter before and after: `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` (matches preregistration).
- Frozen prereg checker before and after: `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` (matches preregistration).
- Restored scratch copy before restored run and after: `0727f2f92a44b643a4a57366101d35558104679e720c24325a1a291fb04afa89` (equal on both measurements).
- No tools installed.

Raw run receipts, fixture-checker outputs, verdict, and unified mutant diffs are included in this seat's `receipts/` directory. Pristine behavior passed, so this probe is conclusive; the expectation-inversion mutant is **killed**.
