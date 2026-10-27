# X01C1Replay — Round 59 C1 falsification

Axes: operability (8) and calibration (7, assigned lowest). Attacked claim/clause: frozen C1 predicate `tools/round59-c1-counter.py` — "C1-r59 each round-56 battery leg is accepted only when its own named expected outcome is tied to that leg's actual observed field/value and exit; genuine leg coverage=3/3, enumerated negative controls fail, 0 evaluation errors", together with the frozen sentence's enumerated forbidden leg shapes (freeze base 8f7f58cd, control commit 5d957d24).

Measured tip: `aca8d0067ea25627c5015c2193c843965148bc8e` (C1 counter/checker pass). Fleet HEAD `/home/vgpnk/Projects/shokunin` at `3f3dd97345ef1aedfdaec818c9e58675d4f41e3f` (read only). No source edits, no commits, no installs.

## 1. Frozen counter at the measured tip — as designed, met

```sh
export TMPDIR=/fast/scratch/hyaku/kama-r59/X01C1Replay/tmp
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip aca8d0067ea25627c5015c2193c843965148bc8e \
  --work /fast/scratch/hyaku/kama-r59/X01C1Replay/c1work \
  --out  /fast/scratch/hyaku/kama-r59/X01C1Replay/c1-at-measured.out
```

Exit `0`. Output verbatim:

```
tip=aca8d0067ea25627c5015c2193c843965148bc8e
predicate=C1-r59 outcome-binding checker accepts genuine+3/3 benign and rejects 16/16 no-ops, errors=0
genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True
detail: genuine accept exit=0
detail: B1-rename-comment accept exit=0
detail: B2-helper-leg accept exit=0
detail: B3-concat-labels accept exit=0
detail: N01-calls-removed reject exit=1
detail: N02-if-false reject exit=1
detail: N03-unused-function reject exit=1
detail: N04-early-return reject exit=1
detail: N05-env-guard reject exit=1
detail: N06-run-body-noop reject exit=1
detail: N07-mutant-assert-noop reject exit=1
detail: N08-main-not-invoked reject exit=1
detail: N09-empty-loop reject exit=1
detail: N10-run-rebound reject exit=1
detail: N11-try-else reject exit=1
detail: N12-ignore-leg-result reject exit=1
detail: N13-wrong-leg-expected reject exit=1
detail: N14-ignore-mutant-result reject exit=1
detail: N15-duplicate-leg-label reject exit=1
detail: N16-decoy-counter-call reject exit=1
```

Reproduced twice, byte-identical (`sha256 84856a06eaeeda4f77952a52ec328618e49e8ea2035dc5523bf616142746cf48`); TMPDIR and `--work` both under the seat scratch root. Genuine fixture is byte-identical to the live battery: `sha256(tests/round58-battery-variants/genuine.py @tip) = sha256(tools/round56-env-leg-battery.py @tip) = 69b77a6a64f2667757842c2471ddc256d12ceb5ccca6df0a57b88bbe17ab51c5`. Counter blob `a766c871255712f23517a2e4e846ab2ec35e6224` and checker blob `64e91f64c05f057f7ae97c50b784aca642f63e59` at the tip equal the worktree bytes (`git hash-object`), so the run is on the frozen instrument.

## 2. Attack: the enumerated routed-argv control is absent and survives

The frozen sentence names five forbidden leg shapes; four are present in the population (N12 discard, N15 duplicate label, N13 swap `--expect`, N16 decoy `--counter`) plus A5 confirms result reuse is killed. The fifth — "routes its argv to `python3 other-script --counter`" — is **not** in the 16. N16 only *adds* a second decoy call, which the checker's `len(calls) == 1` rule happens to catch; it never inspects argv[0] or the test path, so a leg whose own argv is *routed* is accepted.

I built the variant the frozen sentence names and scored it with the frozen checker under a fixture built exactly as `tools/round59-c1-counter.py` builds one (same five blobs at `aca8d006`, `git init` + `git -c user.name=… commit` inside the fixture, `git rev-parse --show-toplevel` asserted equal to the fixture dir, `TMPDIR` under seat scratch):

```diff
-    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", expected],
+    p = subprocess.run(["python3", "other-script", "--counter", str(counter), "--expect", expected],
```

Checker `tools/round59-battery-outcome-check.py --repo <fixture> --tip HEAD` exit **0**:

```
runs=5 passed=5/5 errors=0 met=True
```

and with a *real, committed* script as the route (`str(TEST)` -> `str(pathlib.Path(OLD))`, i.e. `tools/round54-replay-code-audit.py`, which exists at the tip), again exit **0**, `runs=5 passed=5/5 errors=0 met=True`. Both runs report every per-leg `"call": true, "returned_true": true` at baseline, so the checker cannot see which executable the leg invoked. N16's `len(calls)==1` guard is defeated by routing instead of appending: the count stays 1.

This is kill rule item "any enumerated control missing" plus "any outcome-unbound control accepted". The routed leg's pass/fail is produced by a script the frozen sentence disqualifies, and the counter's own summary cannot express the variant because its control list is a closed 16-name tuple.

## 3. Attack: the named leg's *declared* outcome is not bound

The checker derives each leg's expected state from argv (`--expect`) and from the counter file named in argv (`result_for` reads `BAD_ENV`), never from the round-56 roster literal. `ROSTER` in `tools/round56-env-leg-battery.py` declares `base-old-counter: missed`, `round56-counter: detected`; the checker requires only that each leg's own argv expectation match its own synthesized observation. A coherent swap of both the counter and the expectation therefore passes:

```diff
-    results.append(run("base-old-counter", OLD, "missed", OUT / "base-c1.out"))
-    results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))
+    results.append(run("base-old-counter", NEW, "detected", OUT / "base-c1.out"))
+    results.append(run("round56-counter", OLD, "missed", OUT / "build-c1.out"))
```

Checker exit **0**, `runs=5 passed=5/5 errors=0 met=True`. In a real run the leg labelled `base-old-counter` tests the round-56 counter and the leg labelled `round56-counter` tests the round-54 baseline; the battery still prints four passing legs. The frozen predicate's "genuine leg coverage=3/3" and "that leg's own named expected outcome" are therefore not established: only label self-consistency is. This is an outcome-unbound control accepted.

## 4. Attack: the mutant-assert clause is not enforced

The frozen sentence: "`assert_mutant_breaks_detection` must specifically assert the mutant's `missed` observation against `detected` and observe exit 1." Dropping the observation half while keeping exit 1:

```diff
-    ok = p.returncode == 1 and fields.get("ld_audit") == "missed"
+    ok = p.returncode == 1
```

Checker exit **0**, `runs=5 passed=5/5 errors=0 met=True`, baseline `mutant-assert: call true, returned_true true`. The harness synthesizes `rc = 0 if expected == observed else 1`, so it cannot construct the case the frozen clause names (exit 1 without the `missed` observation); the clause is unobserved.

## 5. Corroborating limits (reported, not scored as decisive)

- Field/exit conjunct separability: `ok = exact_field_match(fields, "ld_audit", expected)` (exit half dropped) and `ok = p.returncode == 0` (field half dropped) both produce checker exit 0, `runs=5 passed=5/5`. The harness correlates `ld_audit` and exit perfectly, so neither conjunct is independently observed. Under the current `round56-env-leg-test.py` exit convention these variants do not change today's real verdict, so I record them as a model limit rather than a second kill.
- Benign overfit: a semantics-preserving change of the leg-result representation (`return ok` -> `return 1 if ok else 0`, still valid for `all(results)`) produces checker exit **1**, `runs=5 passed=0/5`, with all three run legs `"returned_true": false` at baseline. The three accepted benign fixtures (B1 comment/local rename, B2 pass-through helper, B3 compile-time label concatenation) are all confined to `main()`; none changes the return representation, so `benign=3/3` overstates benign robustness. This is calibration evidence against `returned is True` overfitting, not a predicate kill (the claim enumerates B1–B3 only).
- Sanity control: discarding one leg's result and appending another leg's result (`results.append(results[1])`) is rejected (exit 1, `passed=4/5`), confirming result reuse is covered by the fault matrix.
- Counter observability: the summary prints one aggregate `genuine=1/1` line, not per-leg coverage or the 16 control names; "coverage 3/3" is only visible inside the checker JSON.

## Verdict

**C1 not met at `aca8d006` under its own kill rule.** The frozen instrument reports `met=True` (exit 0), but the control population is incomplete against the frozen sentence: the enumerated "routes its argv to `python3 other-script --counter`" shape is absent and the same frozen checker accepts it (twice: literal `other-script`, and an existing committed script as route), and an outcome-unbound control — legs whose counter/expectation are coherently swapped so the declared roster outcome no longer binds — is accepted. The `assert_mutant_breaks_detection` "must specifically assert the mutant's `missed` observation" clause is also accepted without the observation. Because the counter, kill rule and fixtures are frozen after data, this round cannot add the missing variants; it is an honest-stop finding, not a fix.

No discernment progress is claimed: the external S517/S518 spot-check is not recorded, and external entries are out of scope for this seat. No build/lint/test/formatter run (editing-wave rule); the checker executions above are the counter's own commands. No installs, no version changes. Scratch `/fast/scratch/hyaku/kama-r59/X01C1Replay/` (driver `run_variant.py`, generator `make_variants.py`, eight variant files, two counter outputs) removed after the run; lane tracked files clean (`git status --porcelain` tracked entries = 0). Files written: this report only.
