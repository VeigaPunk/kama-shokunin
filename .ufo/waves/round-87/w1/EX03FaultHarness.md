# EX03FaultHarness — round 87, wave 1 (C2 operability, fault harness)

## Scope

- Seat: EX03FaultHarness (leaf, executor). Judged on operability. Milestone: kama r87 w1.
- Deliverable: `round87-gate-arm-faults.py` (full file) in the out dir, for the L1 to copy to `tools/round87-gate-arm-faults.py`.
- The harness does not depend on EX02's arm. Its self-test uses a minimal round-83-pattern arm that I applied only in my scratch clone of `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659`.
- Out dir: `.ufo/waves/round-87/w1/out/EX03FaultHarness/`. No lane-tree, tracked, or fleet-root file was written. No git mutation was run in the lane; the clone was set up with `git clone --shared`, then `checkout --detach` in my own clone. The toplevel was asserted first.
- Tools installed or upgraded: none. Only `git 2.56.0` and `Python 3.14.8` were used, already present.

## Commands and outputs

Revision measured: `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659` (verified with `git -C $S/wt rev-parse HEAD`). The clone also carries an uncommitted minimal arm in `tools/pre-report-gate.py`, saved as `test-minimal-arm-scratch-clone.diff` (73 lines).

1. Clone and base instrument selftests (exit 0 each; receipts `base-selftest-*.out`):
   - `python3 tools/round86-rendered-cells.py --selftest` → `RENDERED_CELLS_SELFTEST pass=17 fail=0`, exit 0
   - `python3 tools/round86-mutant-owners.py --selftest` → `DEBT_MUTANT_OWNERS_SELFTEST pass=13 fail=0`, exit 0
   - `python3 tools/round86-pin-origin.py --selftest` → `PIN_ORIGIN_SELFTEST pass=7 fail=0`, exit 0
2. Compile check: `python3 -m py_compile round87-gate-arm-faults.py` → exit 0.
3. Arm present (clone + minimal arm): `python3 $H --repo $S --work $TMPDIR/work-present` → exit 0 (`test-arm-present.out`):
   ```
   CONTROL arm=round86-instruments ok=True exit=0 detail=... 3x ok
   FAULT 1 target=round86-rendered-cells.py killed (arm ok=False exit=1) ...
   FAULT 2 target=round86-mutant-owners.py killed (arm ok=False exit=1) ...
   FAULT 3 target=round86-pin-origin.py killed (arm ok=False exit=1) ...
   ARM14_FAULTS faults=3 killed=3 escaped=0
   exit=0
   ```
4. Arm absent (frozen gate from `git -C <lane> show 94e8fe7b…:tools/pre-report-gate.py`, no arm): `python3 $H --repo $A --work $TMPDIR/work-absent` → exit 1 (`test-arm-absent.out`):
   ```
   CONTROL arm=round86-instruments missing
   FAULT 1 ... escaped (arm missing)   [x3]
   CONTROL_RED
   ARM14_FAULTS faults=3 killed=0 escaped=3
   exit=1
   ```
5. Default `--work` (under `$TMPDIR`), arm present: exit 0, `ARM14_FAULTS faults=3 killed=3 escaped=0`. No `round87-arm14*` directory remained in `$TMPDIR` (grep exit 1, i.e. no match).
6. `env -u TMPDIR` guard: prints `TMPDIR is unset; pass --work <dir> (the harness never uses /tmp)`, exit 1. Confirms no `/tmp` fallback.
7. `grep -n /tmp $H` → two hits, both in the docstring and in the TMPDIR-unset error text (exit 0). No code path writes to `/tmp`.
8. Cleanup: `rm -rf -- /fast/scratch/hyaku/kama-r87/EX03FaultHarness` → exit 0. Directory gone (`ls` exit 2).

Run time: about 110–140 s per full run with a populated arm, because each of the four `gate.evaluate()` calls runs the full arm set (about 30–35 s each). This is a known cost; the harness runs no extra checks beyond that.

## Findings

- F1. Harness behaviour matches the spec for both cases tested. Arm present: `killed=3 escaped=0`, exit 0 (evidence: `test-arm-present.out`). Arm absent: `CONTROL_RED`, `killed=0 escaped=3`, exit 1 (evidence: `test-arm-absent.out`).
- F2. Each kill is explained. The FAULT line carries the arm's own detail, so the operator sees the stub's summary, e.g. `missing valid final selftest summary: FAULT_STUB pass=0 fail=1` for the seeded instrument. The other two instruments stay `ok` in each run, so each fault is isolated.
- F3. Prefix independence. The stub prints `FAULT_STUB pass=0 fail=1`. It can never satisfy `<PREFIX> pass=N fail=0` for any prefix, so the harness does not need EX02's prefixes. My minimal arm used `RENDERED_CELLS_SELFTEST`, `DEBT_MUTANT_OWNERS_SELFTEST`, `PIN_ORIGIN_SELFTEST`, the prefixes the base selftests print.
- F4. Control semantics. A red control prints `CONTROL_RED` and exit 1 even when kills happen. The faults still run and are counted, so the output shows the same kill/escape picture as the absent case, but the exit code blocks a false green.
- F5. Missing-arm semantics. A missing arm counts as escaped (spec). A gate exception in `evaluate()` is also recorded as escaped, with the exception text in the line. Caveat: this crash path was not exercised by any test here.
- F6. Scratch hygiene. The harness creates a private `arm-*` directory under `--work` and removes it in `finally`. With the default `--work`, it also removes the `round87-arm14-faults-*` directory it created. With a user `--work`, the empty `--work` parent is left in place. My two test `work-*` parents were removed by hand.
- F7. Integration requirements for the L1 (not verified here, since EX02's file is not in my clone):
  - The arm must be named exactly `round86-instruments` in `evaluate()`'s `arms` list.
  - `evaluate(repo, round_no, tip=..., tools_dir=...)` must keep its base signature. It does at `94e8fe7b` (`pre-report-gate.py:593`).
  - The three script names the harness replaces must be the ones the arm runs: `round86-rendered-cells.py`, `round86-mutant-owners.py`, `round86-pin-origin.py`. Each must be resolved from `tools_dir`, not from `repo/tools`, for the faults to bite.

## Deliverables

- `.ufo/waves/round-87/w1/out/EX03FaultHarness/round87-gate-arm-faults.py` (6633 bytes, executable): the full harness.
- `.ufo/waves/round-87/w1/out/EX03FaultHarness/test-arm-present.out`: arm-present run, exit 0.
- `.ufo/waves/round-87/w1/out/EX03FaultHarness/test-arm-absent.out`: arm-absent run, exit 1.
- `.ufo/waves/round-87/w1/out/EX03FaultHarness/test-minimal-arm-scratch-clone.diff`: the minimal round-83-pattern arm used for the self-test (scratch clone only, not a tools deliverable).
- `.ufo/waves/round-87/w1/out/EX03FaultHarness/test-commands.txt`: exact commands.
- `.ufo/waves/round-87/w1/out/EX03FaultHarness/base-selftest-round86-*.out` (three files): the base selftest receipts.

VERDICT: harness delivered and verified in both cases at 94e8fe7b (arm present `ARM14_FAULTS faults=3 killed=3 escaped=0` exit 0; arm absent `CONTROL_RED`, `killed=0 escaped=3` exit 1); operability of the C2 arm itself is not measured here because EX02's arm is not in my clone.
