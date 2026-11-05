# EX02GateArmWire — C2 operability: `round86-instruments` as gate arm 14 (kama r87 w1)

## Scope
- Wired arm 14 `round86-instruments` into `tools/pre-report-gate.py` in a scratch clone (`git clone --shared` + `checkout --detach 94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659`). Uncommitted candidate edit; no commit, add, stash, reset or push.
- Revision measured: `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659` (= master = freeze) plus the uncommitted candidate edit to `tools/pre-report-gate.py`. Toplevel assertion before every git read/write: `git -C <wt> rev-parse --show-toplevel` = `<wt>`.
- Not in scope: the fault harness `tools/round87-gate-arm-faults.py` (EX03), C1 (selector, SCORECARD cell).
- Tools installed/upgraded: none. Subagents dispatched: none.

## Commands and outputs
1. Round-86 selftest final summaries (the prefixes ROUND86_MODULES uses), each run as `python3 tools/<script> --selftest`:
   - `round86-rendered-cells.py` exit=0, last line `RENDERED_CELLS_SELFTEST pass=17 fail=0`
   - `round86-mutant-owners.py` exit=0, last line `DEBT_MUTANT_OWNERS_SELFTEST pass=13 fail=0`
   - `round86-pin-origin.py` exit=0, last line `PIN_ORIGIN_SELFTEST pass=7 fail=0`
2. Gate on the candidate: `python3 tools/pre-report-gate.py --repo <wt> --round 87 --tip master` → exit=1 (`run.out` lines 2-17):
   - `PRE_REPORT_ARM round86-instruments exit=0 ok` (run.out:15; all three sub-counters `exit=0 ok`)
   - `PRE_REPORT round=87 arms=14 failed=4 uncommitted=0` (run.out:16)
   - the four failing arms: `selfdesc`, `newest-closure`, `round-scope`, `round75-instruments`
3. Gate selftest: `python3 tools/pre-report-gate.py --selftest --work <scratch>/selftest-work` → `PRE_REPORT_SELFTEST pass=43 fail=0`, exit=0 (run.out:678-679).
4. Base comparison (freeze-commit gate file, 13 arms, same tree): `base-gate.out` → `PRE_REPORT round=87 arms=13 failed=4 uncommitted=0`, exit=1; failing arms `selfdesc`, `newest-closure`, `round-scope`, `round75-instruments`. Base selftest (`base-selftest.out`) → `PRE_REPORT_SELFTEST pass=35 fail=0`, exit=0. 43 − 35 = 8 new checks.
5. `git -C <wt> diff --stat -- tools/pre-report-gate.py` → `1 file changed, 116 insertions(+), 21 deletions(-)`. Full diff: `gate.diff`.
6. `cmp <wt>/tools/pre-report-gate.py <out>/pre-report-gate.py` → identical.

## Findings
F1 — C2 predicate 1 holds: arm 14 is green (run.out:15), `arms=14` appears in the verdict line (run.out:16), and the line `PRE_REPORT_ARM round86-instruments exit=0 ok` is printed.
F2 — Harm rule holds: every arm that is ok at base is ok at the candidate. Base-ok arms `receipt-audit`, `worktree-landing`, `round-clean`, `round74-v2`, `round77-instruments`, `round78-instruments`, `round81-instruments`, `round82-instruments`, `round83-instruments` are all `ok` in run.out:4,5,7,8,10-14. ARM_ORDER prefix unchanged; the new entry is last.
F3 — Arm 14 fails closed, shown by the gate's own selftest: red stub (`RENDERED_CELLS_SELFTEST pass=2 fail=1`) → `round86-instruments exit=1 FAIL`; each instrument deleted → `missing <script>`; each instrument replaced by a foreign summary → `exit=0 FAIL missing valid final selftest summary` (run.out lines around 580-676; 8 new checks, all PASS).
F4 — `round-scope` FAIL in the scratch clone is the candidate's own uncommitted edit: its only finding is `ROUND_SCOPE_V2_FINDING stray tools/pre-report-gate.py status= M` (run.out:6; the base run shows the same finding). After the L1 commit this finding is expected to clear. [INFERENCE: not measured on a committed tree.]
F5 — The other three failing arms are not C2 and are unchanged from base: `selfdesc` (closure_ptr: calibration row round-85 vs newest round-86, a C1 cell), `newest-closure` (STALE_CALIBRATION round-85), `round75-instruments` (APPEND_DEBT arm; INTERPRETATION_PINS and SURVIVORS2 green). Note: `controls/c2-gate-before.out` records `round75-instruments exit=2`; in this clone both base and candidate runs give exit=1. Same failing set; the exit-code difference is unexplained by this change (the control was measured on the lane tree at 362b0d4a).
F6 — Pre-existing staleness left untouched: `PREDICATE` constant (line 243) still reads `arms=11`; `evaluate()` docstring says "Run the seven arms". Both predate this change; the PREDICATE is the frozen receipt sentence, so changing it is an L1 decision.

## Changed lines and reasons (candidate line numbers; full text in gate.diff)
- Arm list, docstring (L56-58): new listing `14 round86-instruments` with its three scripts and `--selftest`. Reason: spec step 4 (verdict prose), arm order documented.
- Docstring (L13): `arms=13` → `arms=14` (the verdict sentence now prints 14). Reason: spec step 4.
- Docstring (L18-19): `arm 13's round-83 pair compose` → `arm 12's round-82 pair, arm 13's round-83 pair and arm 14's round-86 trio compose`. Reason: arm composition prose.
- Docstring (L26-27): appended `from round 84 through 86 it printed arms=13, and from round 87 on it prints arms=14`. Reason: arm-count history; the round-84 history is kept.
- Docstring (L130): output-format example `arms=13` → `arms=14`. Reason: current output format.
- Docstring fixture list (L162, L170, L175, L180): cases (h), (n), (q), (t) `verdict arms=13` → `arms=14`. Reason: these are green fixtures; under 14 arms their verdict is 14, so the expectation would be wrong otherwise.
- Docstring (L219-225, new paragraph "Round 87 adds arm 14"): describes the arm, the three summary prefixes, fail-closed rule, and the four new cases. Reason: spec step 4.
- Constant `ROUND86_MODULES` (new, after ROUND83_MODULES): three `(script, prefix)` pairs from the executed selftests above. Reason: spec step 1.
- `ARM_ORDER` (L270-273): the arm list gains `"round86-instruments"` as last entry (`"round83-instruments",` → plus new line). Reason: spec step 3.
- Function `_round86_instruments` (new, after `_round83_instruments`): same body as round 83 with `ROUND86_MODULES` and name `round86-instruments`. Reason: spec step 2.
- `evaluate()` (L753, new line): `arms.append(_round86_instruments(tools_path, repo_path, depth))` after the round-83 call. Reason: spec step 3.
- Selftest `_STUB_R86` (new, after `_STUB_APPEND_EXEMPT`) and its write loop (after the round-76 stubs): one parametrized stub per round-86 module (`__PREFIX__` replaced with the module's prefix; red via `red("round86-instruments")`). Reason: without fixture stubs every green fixture would fail on arm 14 missing.
- Selftest `want_line` (9 pre-existing green fixtures; originals 1169, 1215, 1226, 1284, 1309, 1341, 1445, 1467, 1487): `arms=13` → `arms=14`. Reason: green fixture expectations under 14 arms; these are fixture expectations, not historical receipts.
- Selftest new block (after the round-83 loop, before `total =`): green (want_line arms=14), red, each instrument deleted, each instrument replaced by a foreign summary. Reason: spec step 2 fail-closed wiring.
- `main()` description (L1621-1622): `(arms=13 from round 84)` → `round-86 instrument trio (arms=14 from round 87)`. Reason: CLI description reflects the arm count.
- Unchanged historical occurrences: L26 "round 79-80 arms=10", L203 "from round 84 they carry arms=13", L212 "arms=13 (round 84 on)". Reason: record earlier rounds' verdict prose; not rewritten.

## Deliverables (`.ufo/waves/round-87/w1/out/EX02GateArmWire/`)
- `pre-report-gate.py` — full candidate file (cmp-identical to the clone).
- `gate.diff` — `git diff` of `tools/pre-report-gate.py` at the freeze commit (321 lines).
- `run.out` — gate run output and exit (EXIT=1) plus the gate's own selftest output and exit (EXIT=0).
- `base-gate.out`, `base-selftest.out` — base comparison receipts (freeze-commit gate file).
- Scratch `/fast/scratch/hyaku/kama-r87/EX02GateArmWire/` removed after the receipts were copied.

VERDICT: C2 arm 14 `round86-instruments` wired and green (arms=14, selftest 43/0, harm rule holds, no base-ok arm red); the gate's own verdict is still exit 1 on four pre-existing reds (selfdesc, newest-closure, round-scope from the uncommitted edit, round75-instruments), and the fault harness was not run here.
