# MT01Mutants75 — mutation test of the three round-75 instruments (kama r75 w1)

Seat: MT01Mutants75 · Lane: kama-shokunin · Date: 2026-11-04
Freeze commit `0908bab5cbf0ab6b435144fc525a3e18443dc08f`; lane HEAD at report time `b8ed2568` (base revision `dc58e51315e79d36df5fc530c95fbd3aecbf7593`).

## MUTANTS75 summary

```
MUTANTS75 tools/round75-interpretation-pins.py applied=9 killed=5 escaped=4
MUTANTS75 tools/round75-survivor-probe.py     applied=8 killed=5 escaped=3
MUTANTS75 tools/round75-append-accepted.py    applied=9 killed=7 escaped=2
```

All three tools were present and landed (committed in `10f37171`); nothing is reported `not-landed`.

## Method

- Workspace: one `git clone --shared` of the lane at `/fast/scratch/hyaku/kama-r75/MT01Mutants75/clone`; all mutants were applied to copies inside that clone (`clone/tools/`). **The lane tree was never edited.** Mutant copies were restored to pristine bytes after each matrix (`restored_matches_pristine: true` in every result JSON).
- Provenance of tested bytes: sha256 of pristine copies == lane worktree == `HEAD` blob == clone copy, verified for all three tools after the runs:
  - `round75-interpretation-pins.py` `fac5ffbb8c2e6eb0e135581353352c59fa605beb68fd9abded1295cc61ec0d21`
  - `round75-survivor-probe.py` `255515165653d90cd30be6274b7baeb4c027e90f4ca9cad15b838ea2d625e989`
  - `round75-append-accepted.py` `f289966732a0c3fd728af59bdb2734bcc94b7ed34ac2b4f36393328ef237612d`
- Detector legs per mutant: (1) the module's own `--selftest` (pins run with `--repo <lane>` so its predicate arm reads the frozen plan), and (2) the module's real-lane command (`--repo /home/vgpnk/Projects/shokunin/kama-shokunin`). Classification: **killed** if some selftest arm goes red or the real-lane run goes red; **escaped** otherwise. All 26 anchors asserted `count == 1` before patching (no anchor errors).
- Pristine baselines (same two legs, unmutated bytes):
  - pins: selftest `pass=3 fail=0` exit 0; real run `INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0` exit 0.
  - survivors: selftest `pass=5 fail=0` exit 0; real run `SURVIVORS2 mutants=5 killed=5 escaped=0` exit 0 (all five mutants killed on the named arms).
  - accepted: selftest `pass=12 fail=0` exit 0; real run exit 1 `bad_declarations=1` (SCORECARD exempt-pointer finding) — the lane was still mid-repair at baseline time; EX03's fix landed in `b8ed2568` before the mutant matrix ran, and every mutant real-leg ran against `bad_declarations=0`. The baseline red makes the real-leg detector inconclusive for the baseline itself; per-mutant real-leg results below are deltas against the green lane and are attributed only where the output line differs from pristine (see C6 note).
- Raw harness output: `raw/*.json` (full argv, rc, stdout/stderr tails per leg), `raw/C6-rl-full.txt`, `raw/patch-diffs.md` (exact per-mutant unified diffs), `raw/mutate.py` (the harness).

## Matrix — tools/round75-interpretation-pins.py (applied=9 killed=5 escaped=4)

| Mutant | Class | Selftest | Real-lane | Verdict | Detector |
|---|---|---|---|---|---|
| A1-declared-flip | comparison flip (`declared`: `==`→`!=`) | rc1, `declared-and-kill FAIL` | rc1, `declared=0` | **killed** | selftest + real |
| A2-kill-rule-drop | comparison flip (`killed`)/input-trust: drop `mutant != declared` | rc1, `cheat-escaped FAIL` (cheat line `killed=2 escaped=0`) | rc0 clean | **killed** | selftest (cheat arm) |
| A3-finding-exit-to-0 | exit flip (finding→0) | rc1, `cheat-escaped FAIL` (CHEAT exit=0) | rc0 | **killed** | selftest (cheat arm) |
| A4-clean-exit-to-1 | exit flip (clean→1) | rc1, 2 arms FAIL | rc1 (clean line, exit 1) | **killed** | selftest + real |
| A5a-grade-one-pin | scope cut (grade P1 only, `][:1]`) | rc1, `cheat-escaped FAIL` (cheat prints `pins=1`) | rc0 `pins=1 declared=1 killed=1 escaped=0` | **killed** | selftest (cheat arm) |
| A5b-fake-P2-leg | scope cut/input-trust: P2 pin hardcoded `observed=0 mutant=1 mutant_ok=True` | rc0 `pass=3 fail=0` | rc0, byte-identical clean line | **ESCAPED** | — |
| A6-trust-P2-observed | input-trust: `"observed": pristine["exit"]`→`0` | rc0 `pass=3 fail=0` | rc0, identical clean line | **ESCAPED** | — |
| A7-oracle-declared-and-kill | selftest-oracle tamper (`declared-and-kill`→`True`) | rc0 `pass=3 fail=0` | rc0 | **ESCAPED** | — |
| A8-oracle-predicate | selftest-oracle tamper (`predicate`→`True`) | rc0 `pass=3 fail=0` | rc0 | **ESCAPED** | — |

### Escapes (exact patches)

A5b (full P2-dict rewrite):
```diff
-         "observed": pristine["exit"], "mutant": mutant["exit"],
-         "mutant_ok": mutant["exit"] == 1 and
-                       "RECEIPT_CLAIM_V2_FINDING stale-revision " in mutant["stdout"],
+         "observed": 0, "mutant": 1, "mutant_ok": True,
```
A6:
```diff
-         "observed": pristine["exit"], "mutant": mutant["exit"],
+         "observed": 0, "mutant": mutant["exit"],
```
A7:
```diff
-            ("declared-and-kill", clean["exit"] == 0), ("cheat-escaped", cheat_ok)]
+            ("declared-and-kill", True), ("cheat-escaped", cheat_ok)]
```
A8:
```diff
-("predicate", plan_predicate(repo) == PREDICATE),
+("predicate", True),
```

Escape analysis (A5b/A6 share one root): the selftest's only composed-counter cheat perturbs **P1's declared reading** (`DECLARED_TOTAL = 3 → 5`). No arm composes a variant that fakes or hardcodes the **P2 revision-mention leg**, so a counter that skips the P2 mutant leg or trusts its inputs prints the exact claimed line and `pass=3 fail=0`. **Arm that should exist:** `cheat-p2-escaped` — compose a second variant by replacing the anchor `"observed": pristine["exit"], "mutant": mutant["exit"],` with hardcoded values and require the selftest to go red (fixture: none beyond the existing `--work` variant composition; the clean fixture build is reused).

Escape analysis (A7/A8): no arm is ever negatively validated — nothing proves `declared-and-kill` or `predicate` **can** fail, so oracle tampering ships green. **Arm that should exist:** `oracle-liveness` — run `plan_predicate` against a one-word-doctored copy of the plan under `--work` (a repo dir containing `plans/round-75-claims.md` with one token changed) and require the arm expression to evaluate False there; same injected-fault pattern for `declared-and-kill` (doctored clean document with `observed != declared` must make the arm's expression False).

## Matrix — tools/round75-survivor-probe.py (applied=8 killed=5 escaped=3)

| Mutant | Class | Selftest | Real-lane | Verdict | Detector |
|---|---|---|---|---|---|
| B1-killed-flip | comparison flip (`killed`: `== 1`→`!= 1`) | rc1, `complete-kills`+`green-mutant FAIL` | rc1, `killed=0 escaped=5` | **killed** | selftest + real |
| B2-arm-check-drop | input-trust: kill = red exit, expected arm unchecked | rc1, `wrong-arm FAIL` | rc0 `killed=5` (arms uncertified) | **killed** | selftest (`wrong-arm`) |
| B3-finding-exit-to-0 | exit flip (finding→0) | rc1, 4 arms FAIL (`empty-list-cheat` among them) | rc0 | **killed** | selftest |
| B4-clean-exit-to-1 | exit flip (clean→1) | rc1, all 5 arms FAIL | rc1 | **killed** | selftest + real |
| B5-skip-pristine-verdict | scope cut: `grade(pristine.returncode, …)`→`grade(0, …)` | rc0 `pass=5 fail=0` | rc0, identical output | **ESCAPED** | — |
| B6-skip-mutant-leg | scope cut: mutant copy written unmutated | rc0 `pass=5 fail=0` | rc1, 5× `SURVIVORS2_FINDING <m> mutant_exit=0 arm=none`, `killed=0 escaped=5` | **killed** | real-lane |
| B8-oracle-complete-kills | selftest-oracle tamper (`complete-kills`→`True`) | rc0 `pass=5 fail=0` | rc0 | **ESCAPED** | — |
| B9-summary-line-hardcode | output-oracle: summary `print` hardcoded | rc0 `pass=5 fail=0` | rc0, identical line | **ESCAPED** | — |

### Escapes (exact patches)

B5:
```diff
-        doc = grade(pristine.returncode, rows, MUTANTS)
+        doc = grade(0, rows, MUTANTS)
```
B8:
```diff
-        "complete-kills": grade(0, rows, MUTANTS)["exit"] == 0,
+        "complete-kills": True,
```
B9:
```diff
-    print("SURVIVORS2 mutants={mutants} killed={killed} escaped={escaped}".format(**doc))
+    print("SURVIVORS2 mutants=5 killed=5 escaped=0")
```

Escape analysis (B5): `selftest()` exercises only `grade()` with synthetic rows; the wiring in `probe()` — that the **real** pristine returncode reaches `grade` — is untested, and `doc["pristine_exit"]=0` also suppresses the pristine FINDING line. **Arm that should exist:** `probe-pristine-red` — run the CLI (or `probe()`) against a fixture repo whose committed target module's selftest fails one arm, and require `SURVIVORS2_FINDING pristine` + exit 1. **Fixture:** a bare git repo under `--work` holding a copy of `tools/round74-receipt-claim-binding.py` with one deliberately broken arm, committed (the probe clones committed bytes).

Escape analysis (B8): `complete-kills` is the only check without a case that must see it FAIL. **Arm that should exist:** `complete-kills-liveness` — synthetic rows with one `mutant_exit=0` must make `grade(...)["exit"] == 1` and the check expression False (fixture: none; synthetic rows like the existing `green-mutant` case).

Escape analysis (B9): the printed claim line is never compared against `doc`; a hardcoded summary prints green on any lane while the exit stays honest (receipt line and exit can disagree). **Arm that should exist:** the pins-style composed-counter cheat (`cheat-escaped` analog) — a source-anchored variant whose `grade()` counts differently must move the printed `SURVIVORS2` line and the exit together (fixture: none beyond the variant; run with `--repo <lane>`).

## Matrix — tools/round75-append-accepted.py (applied=9 killed=7 escaped=2)

Real-legs ran on the green lane (`bad_declarations=0`, `events=53 accepted=53`).

| Mutant | Class | Selftest | Real-lane | Verdict | Detector |
|---|---|---|---|---|---|
| C1-accepted-unconditional | comparison flip (`accepted`: guard→`if True`) | rc1, `missing-entry FAIL` | rc0 | **killed** | selftest |
| C2-unaccepted-zero | comparison flip (`unaccepted`→`0`) | rc1, `missing-entry FAIL` | rc0 | **killed** | selftest |
| C3-bad-rows-drop | comparison flip (`bad_rows += 1`→`+= 0`) | rc0 `pass=12 fail=0` | rc0 | **ESCAPED** | — |
| C4-finding-exit-to-0 | exit flip (verdict→`return 0`) | rc1, 11 cases FAIL | rc0 | **killed** | selftest |
| C5-clean-exit-to-1 | exit flip (verdict negated) | rc1, 12 cases FAIL | rc1 | **killed** | selftest + real |
| C6-grade-one-event | scope cut (`pending` truncated to first event) | rc0 `pass=12 fail=0` | rc1, `events=1 accepted=1 unaccepted=0 bad_rows=388` + 388 hash-mismatch FINDINGs | **killed** | real-lane |
| C7-accept-any-row | input-trust: any row naming a pending event is covered | rc1, `wrong-hash FAIL` | rc0 | **killed** | selftest |
| C8-bad-declarations-zero | input-trust (`bad_declarations`→`0`) | rc1, `bad-declaration FAIL` | rc0 | **killed** | selftest |
| C9-oracle-and-to-or | selftest-oracle tamper (`and`→`or` in case check) | rc0 `pass=12 fail=0` | rc0 | **ESCAPED** | — |

### Escapes (exact patches)

C3:
```diff
     def bad(kind, detail, key=None):
         nonlocal bad_rows
-        bad_rows += 1
+        bad_rows += 0
```
C9:
```diff
-        ok = actual == want and (finding is None or any(f["class"] == finding for f in result["findings"]))
+        ok = actual == want or (finding is None or any(f["class"] == finding for f in result["findings"]))
```

Escape analysis (C3 — passes for the wrong reason): the `restored-event` negative control **replaces** the honest row with the mutated row, so the honest event is left uncovered and `unaccepted=1` carries the expected exit 1; `bad_rows` is never the sole red signal in any of the 12 cases. On a register that fully covers all pending events **plus one stray restored-key or unknown-commit row**, `bad_rows` is the only signal that flips the verdict — and the mutant cannot produce it. **Arm that should exist:** `stray-bad-row` — `register([good_row, restored_key_row])` (and the unknown-commit variant) over the same single-event data, requiring exit 1 with `restored-event`/`unknown-event` finding and `unaccepted=0 bad_rows=1` (fixture: none; extend the in-memory case list).

Escape analysis (C9): the case harness `ok = actual == want and (finding …)` is itself unvalidated — `and`→`or` passes all 12 cases regardless of `grade()`'s behavior. **Arm that should exist:** `oracle-liveness` — one deliberately mis-expected case (e.g., honest data expected `exit=1`) must produce `FAIL` and `fail>0`; equivalently a composed counter variant with `verdict → 0` must be flagged by the harness (fixture: none).

## Observations for the L1

1. **Systematic gap:** the pins module has a composed-counter cheat arm (`cheat-escaped`); survivors and accepted have no analog, and none of the three modules negatively validates its own selftest oracle. Seven escapes, all in selftest-oracle, composed-counter, or leg-wiring space; none is a fixture gap — six of the seven missing arms need no new repo fixture (the exception is B5's red-pristine clone fixture).
2. **C6 attribution:** the C6 real-leg red is mutant-caused, not lane-state: its stdout has 388 `hash-mismatch` findings and zero `bad-declaration` findings, and all mutant real-legs ran after `b8ed2568` landed `bad_declarations=0` (the summary line scrolled out of the retained 6 KB tail in the matrix JSON; full stdout retained at `raw/C6-rl-full.txt`).
3. **Mid-wave flakiness note (no action):** at 02:21 I hashed pre-commit working bytes of pins/accepted (`5172c054…`, `09b9cace…`); by 02:22 the committed bytes were on disk and are what every matrix run used (verified four-way: pristine == worktree == HEAD blob == clone). The tools changed once more in neither file after `10f37171`.
4. **Disagreement/none:** I did not need to invoke the freeze-disagreement rule; all behaviors matched the frozen predicates. `tools/round74-*.py`, `append-only-audit.py`, the plan, and all sibling files were only read.
5. **Tooling authorization:** no tools were installed or upgraded (none needed). No pacman transactions.

## Dead ends

- First baseline batch was a no-op: the harness was invoked with file *paths* where it requires the tool *filename* (argparse `choices`), and the wrapper `; echo EXIT=$?` masked the argparse exit. Detected because `results/` stayed empty; re-run correctly. No other dead ends.

## Bounds compliance

- Writes: this report, `../MT01Mutants75.md`, and `raw/` under my seat dir — nothing else in the lane. No git/jj mutation anywhere (lane git use: read-only `status/log/diff/show/rev-parse`; the only `git clone/init/commit` ran inside my scratch by the tools' own fixture builders and the probe's clone of the lane).
- Scratch: `/fast/scratch/hyaku/kama-r75/MT01Mutants75/` — removed after copying receipts into `raw/`. No live clone remains outside it.
