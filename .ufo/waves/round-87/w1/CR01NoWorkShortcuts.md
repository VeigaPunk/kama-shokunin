# CR01NoWorkShortcuts — kama r87 w1 falsification of C1 and C2

## Scope
- Seat: CR01NoWorkShortcuts (leaf, no delegation). Judged on calibration (C1) and operability (C2).
- Freeze measured: `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659` (clone detached there; `rev-parse --show-toplevel` checked before every write).
- Frozen claims read in full: `plans/round-87-claims.md`. Controls read: `.ufo/waves/round-87/controls/`.
- Attacks built in scratch only. Scratch clone and all seed trees removed before this report (`rm -rf` exit 0; path absent).
- Scratch commits (C1 cases) were created by plumbing only (`read-tree`/`update-index`/`write-tree`/`commit-tree` on a private index file); no ref moved, nothing committed, pushed or fetched in the lane. Revisions: see `receipts/revisions.txt`.
- The C2 fault harness `tools/round87-gate-arm-faults.py` and the candidates EX01/EX02/EX03 are NOT present in the lane at seat time (`w1/out/` contains no candidate files). Harness results below use a stand-in I wrote to the frozen C2 predicate-2 spec (`attacks/harness-sim.py`); the L1 must re-run against the real harness.
- Tools installed: none. No pacman, no network.

## Commands and outputs (exit codes; full text in receipts/)
1. Freeze baseline, round-86 counter: `python3 tools/round86-rendered-cells.py --repo <clone> --rev 94e8fe7b…` → `RENDERED_CELLS facts=3 mismatches=2 gate=1 closure=0 disposition=0 newest_gate=86 newest_closure=86`, exit 1 (matches control `c1-live-before.out`).
2. Freeze probe battery: `python3 .ufo/waves/round-87/controls/c1-probes.py tools/round86-rendered-cells.py` → `escapes=3 control=red`, exit 1 (matches control).
3. Freeze selftest: `python3 tools/round86-rendered-cells.py --selftest` → exit 0.
4. Gate predicate-1 runs (`receipts/p1-<variant>.out`), `python3 attacks/gate-<variant>.py --repo <clone> --round 87 --tip master`:
   - honest reference: `PRE_REPORT round=87 arms=14 failed=3 uncommitted=0`, arm line `round86-instruments exit=0 ok … RENDERED_CELLS_SELFTEST pass=17 fail=0 | DEBT_MUTANT_OWNERS_SELFTEST pass=13 fail=0 | PIN_ORIGIN_SELFTEST pass=7 fail=0`; exit 1 (the three remaining reds are base-red arms, not this claim; base had failed=4).
   - always-ok, leak, cheat: same shape, arm line `ok`, `arms=14`; exit 1 for the same base-red reason.
5. Stand-in harness: `python3 attacks/harness-sim.py attacks/gate-<variant>.py <clone>` (`receipts/h-<variant>.out`):
   - honest: `ARM14_FAULTS faults=3 killed=3 escaped=0`, `CLEAN_CONTROL arm=ok`, exit 0.
   - always-ok: `ARM14_FAULTS faults=3 killed=0 escaped=3`, `CLEAN_CONTROL arm=ok`, exit 1.
   - leak: `ARM14_FAULTS faults=3 killed=0 escaped=3`, `CLEAN_CONTROL arm=ok`, exit 1.
   - cheat: `ARM14_FAULTS faults=3 killed=3 escaped=0`, `CLEAN_CONTROL arm=not-ok`, exit 1.
6. C1 cases (`receipts/c1-cases.out`), all with `--rev`:
   - (a) SCORECARD-only rev `e78e7430…`: `mismatches=1 … disposition=0`, exit 1; probes `escapes=3 control=red`, exit 1.
   - (b) hardcoded selector at freeze: `mismatches=1 … closure=0`, exit 1; at rev `e78e7430…`: `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=86 newest_closure=86`, exit 0; probes `escapes=0 control=red`, exit 0.
   - (b) M1 (newer closure `round-87` committed, row unchanged) rev `275bce93…`: hardcoded `mismatches=0 … newest_closure=86` exit 0 (wrong: newest is 87); round-86 counter `mismatches=2 … newest_closure=87` exit 1.
   - (b) M2 (stale round-85 visible row, literal only inside `<!-- -->`) rev `0e672188…`: hardcoded `mismatches=0` exit 0; round-86 counter `mismatches=2` exit 1.
   - freeze control with round-86 counter: exit 1, red.

## Findings

### C1 (a) SCORECARD-only edit, no selector repair — NOT admitted
- Calibration row edited to name `corpus/lessons/round-86-verifier-spotcheck.md` and `round86 rejected-honest-stop` (`attacks/SCORECARD.a.md:18`).
- Predicate 1 fails: `disposition=0`, `RENDERED_CELLS_FINDING disposition row does not name \`round86 rejected-harmed\`` (`receipts/c1-cases.out` section (a)). Cause: `disposition_of()` (`tools/round86-rendered-cells.py:265`) takes the first fixed-order word found anywhere in the closure body; `corpus/lessons/round-86-verifier-spotcheck.md:25` contains `rejected-harmed`, so the oracle never reads the verdict token (`verdict \`rejected-honest-stop\``, closure line 76 area).
- Predicate 2 fails: `escapes=3 control=red`, exit 1.
- Predicates that pass: none. The cell is not the blocker; the unrepaired oracle is. The SCORECARD cell cannot be made green without R2 (verdict-line token) in the successor.
- Minimal control that closes it: none needed beyond the frozen predicates; they already refuse. Note for the successor: R2 must read the verdict-line token, and a probe asserting that a body word before the verdict does not decide the disposition is the P-B probe, which already exists.

### C1 (b) hardcoded literal selector — ADMITTED by both predicates
- Variant: round-86 counter with `grade()` short-circuited to `mismatches=0` iff SCORECARD contains `corpus/lessons/round-86-verifier-spotcheck.md` and `round86 rejected-honest-stop` (`attacks/hard.py`, tail section). Fallback to a fixed `mismatches=1` otherwise.
- Predicate 1: PASS at rev `e78e7430…` (exact facts line, exit 0). Predicate 2: PASS (`escapes=0 control=red`, exit 0). The probe fixtures never contain the literal, so P-A/P-B/P-C and the control all read red.
- Caught by neither predicate: predicate 1 only grades the live tree, which is the one the literal matches; predicate 2's probes do not contain the literal. The frozen kill rules ("escape", "green control", "mismatches>0 at R") do not fire.
- Attacks the frozen predicates miss, all caught by the rendered round-86 counter (exit 1) and missed by the hardcoded one (exit 0):
  - M1 newer closure without row change → hardcoded also reports the wrong `newest_closure=86`.
  - M2 stale visible row with the literal hidden in an HTML comment → hardcoded passes; rendered identity (rule of the counter's own docstring) rejects it.
- Minimal control that closes it: add to `controls/c1-probes.py` two must-be-red probes on the live-tree shape: P-D newer `round-87` closure committed with the row unchanged; P-E stale visible row with the literal only inside `<!-- -->` or a fence. A hardcoded selector escapes both; the rendered counter is red on both (exit 1). This is a new probe, so it belongs to a later round's claim or the L1's integration decision; it must not edit the frozen probes in place.

### C2 always-ok arm `round86-instruments` — admitted by predicate 1, caught by predicate 2 (stand-in)
- Arm body returns `ok`, `exit=0` without running any selftest (`attacks/gate-ok.py`).
- Predicate 1: PASS. Line `PRE_REPORT_ARM round86-instruments exit=0 ok round86-instruments always ok (scratch attack)`, verdict `arms=14`. Harm rule holds (failed 4 → 3).
- Predicate 2: FAIL under the stand-in harness: `ARM14_FAULTS faults=3 killed=0 escaped=3`, exit 1. Its arm never reads the seeded tools dir, so no fault can kill it. Caught, provided the real harness is written per the frozen spec.
- Minimal control already in the frozen design: predicate 2's kill count. Add a clean-tools control (see below) to make the harness self-checking.

### C2 tools-path leak (arm runs repo `tools/` even when `tools_dir` is given) — admitted by predicate 1, caught by predicate 2 (stand-in)
- Arm resolves scripts from `os.path.join(repo_path, "tools")` instead of `tools_path` (`attacks/gate-leak.py`).
- Predicate 1: PASS (repo tools are the default `tools_dir`, arm `ok`, `arms=14`).
- Predicate 2: FAIL: `ARM14_FAULTS faults=3 killed=0 escaped=3`, exit 1. Caught because the seeded faults live only in the scratch tools tree handed to `evaluate()`.
- Minimal control: assert in the harness (or the gate) that each arm `argv` path begins with the resolved `tools_dir` (the `argv` field is already in each arm dict in `evaluate()`).

### C2 harness-aware cheat (found while testing the leak; not in the brief) — ADMITTED by both frozen predicates
- Arm returns `ok` when `tools_dir` is None and `not ok` when `tools_dir` is given (`attacks/gate-cheat.py`).
- Predicate 1: PASS (no `tools_dir` on the real run; arm `ok`, `arms=14`).
- Predicate 2: PASS as written: `ARM14_FAULTS faults=3 killed=3 escaped=0`, exit 0 on that line. The frozen predicate has no no-fault control, so "every fault kills" is satisfied by an arm that fails whenever the harness calls it.
- Caught only by the clean-tools control: `CLEAN_CONTROL arm=not-ok`, exit 1 (honest variant: `CLEAN_CONTROL arm=ok`).
- Minimal control that closes it: add to the harness one run with an unmodified tools copy that must leave `round86-instruments` ok. The stand-in harness does this (`attacks/harness-sim.py`); the frozen predicate 2 text should be amended to require it. Note the amendment changes the frozen predicate, so it is the L1's decision.

## Deliverables (in `.ufo/waves/round-87/w1/out/CR01NoWorkShortcuts/`)
- `receipts/c1-cases.out` — all C1 case outputs with exit codes.
- `receipts/p1-{honest,ok,leak,cheat}.out` — gate predicate-1 runs.
- `receipts/h-{honest,ok,leak,cheat}.out` — stand-in harness runs.
- `receipts/revisions.txt`, `receipts/rev-list.txt` — the scratch revisions cited.
- `attacks/` — `hard.py` (C1 b), `gate-{honest,ok,leak,cheat}.py` (C2 variants), `harness-sim.py` (stand-in fault harness), `mkrev.sh` (plumbing commit builder), `SCORECARD.a.md`, `SCORECARD.m2.md`, `r87closure.md` (fixture cells).

## Ledger for the L1
- C1 as frozen: predicate 2 catches the unrepaired and hardcoded cases only through the probes that exist; the hardcoded literal selector passes both predicates. Recommend the probes P-D/P-E above before counting C1 verified.
- C2 as frozen: always-ok and tools-leak are caught by predicate 2 if the real harness is written per spec; the harness-aware cheat passes both predicates. Recommend the clean-tools control before counting C2 verified.
- Re-run once the real candidates land: `python3 .ufo/waves/round-87/controls/c1-probes.py tools/round87-rendered-cells.py`, `python3 tools/round87-gate-arm-faults.py --repo .`, and the attacks above against the integrated tree.

VERDICT: C1 is not admitted by the SCORECARD-only shortcut, but a hardcoded literal selector passes both frozen predicates; C2's always-ok and tools-leak arms are caught by the harness only if built per spec, and a harness-aware arm passes both frozen predicates unless a clean-tools control is added.
