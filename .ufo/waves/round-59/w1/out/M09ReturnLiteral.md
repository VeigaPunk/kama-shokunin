# M09ReturnLiteral — round 59 mutation probe: return capture → constant True

Axes: operability, calibration. Advisory only; falsification seat, not the judge.
Attacked claim/clause: C1-r59 outcome-binding sentence (freeze.txt): "each named `run`/mutant leg is accepted only when its own named expected outcome is tied to that leg's actual observed field/value and exit"; kill rule: "any genuine leg rejected, any outcome-unbound control accepted, any eval error → claim not met". Detector: `tools/round59-c1-counter.py` at frozen tip `aca8d0067ea25627c5015c2193c843965148bc8e`.

Mutation (single behavior-bearing point, isolated scratch clone only): in the battery's `run()`, the captured leg outcome `ok = p.returncode == 0 and exact_field_match(fields, "ld_audit", expected)` is computed honestly but the return literal is mutated: `return ok` → `return True`. Call shape, capture logic, `assert_mutant_breaks_detection` untouched. Probe ran twice because the first site is invisible to the detector.

## Detector baseline (pristine bytes)
- `python3 tools/round59-c1-counter.py --repo <lane> --tip aca8d0067ea25627c5015c2193c843965148bc8e --work <scratch>/work --out <scratch>/c1-pristine.out` → exit 0, `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; output sha256 `84856a06eaeeda4f77952a52ec328618e49e8ea2035dc5523bf616142746cf48`; matches frozen control `controls/c1-candidate-final.out`.
- Standalone fault matrix: `python3 <checker@tip> --repo <lane> --tip aca8d00...` → exit 0, `runs=5 passed=5/5 met=True` (all four legs `returned_true: true` at baseline, faulted leg `false` under each of the 4 injected faults).

## Probe A — SURVIVED (coverage finding, tools path)
- Mutant: `tools/round56-env-leg-battery.py` line 46 `return ok` → `return True`; blob `1f4ebff0a62cc9e09d90c6a2f44b613c7027235b` → `cb55a5386caa8657cbc6802521dcc737a81ece05`; file sha256 `69b77a6a64f2667757842c2471ddc256d12ceb5ccca6df0a57b88bbe17ab51c5` → `e9790d5ea2815b4097295a6eff6877015ce225e041ac000a3a5268a4c3ab49d3`; scratch commit `300d324f28c054b94c0d0f2a9aa0061860c058de` (parent `aca8d00...`).
- Expected detector: C1 counter rejects (exit 1).
- Actual: `python3 tools/round59-c1-counter.py --repo <scratch clone> --tip 300d324f... --work <scratch>/work-mutant` → exit 0, `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True` — identical verdict shape to pristine. **Verdict: SURVIVED.**
- Cause (from counter source): for every one of the 20 fixtures, `files[BATTERY]` is overwritten with a blob from `tests/round58-battery-variants/*` or `tests/round59-battery-variants/*`; the tip's `tools/round56-env-leg-battery.py` blob is read then discarded. The mutated tools path never enters any fixture.
- Cross-check: the checker's standalone fault matrix (which does read the tools path) catches the same mutant: `--repo <clone> --tip 300d324f...` → exit 1, `passed=2/5 met=False`; faults `base-old-counter`/`round56-counter`/`m-drop-ldaudit` fail (battery exit stays 0, faulted leg `returned_true: true`); `mutant-assert` fault passes (function unmutated).
- Reading: a coverage gap in the detector's input surface, not a kill-rule miss — the frozen counter is defined over the variants-dir fixtures. No contract change proposed; survivor reported as finding. `tools/round56-env-leg-battery.py` is consumed only by the checker's own main() path, so the two "genuine" copies must stay byte-identical or the checker/counter quietly diverge (they are identical at `aca8d00...`: both sha256 `69b77a6a...`).

## Probe B — KILLED (true behavior-bearing point: variants-dir genuine battery)
- Mutant: `tests/round58-battery-variants/genuine.py` (byte-identical to the tools battery at tip) line 46 `return ok` → `return True`; blob `1f4ebff0...` → `cb55a538...`; probe tip `ea8497aceefc641a38af1071b7fcc23e0715d584`, `git diff --stat aca8d00... HEAD` = exactly this one file. Fixture commit identity `m09-returnliteral` used only inside the scratch clone/fixture; `git rev-parse --show-toplevel` asserted equal to the fixture dir before each commit.
- Expected detector: C1 counter rejects the genuine fixture.
- Actual: `python3 tools/round59-c1-counter.py --repo <scratch clone> --tip ea8497ac... --work <scratch>/work-mutantB` → exit 1, `genuine=0/1 benign=3/3 noop_rejected=16/16 errors=0 met=False`, `detail: genuine reject exit=1`; every other line identical to pristine. **Verdict: KILLED.**
- Fault matrix (checker on a counter-style fixture carrying the mutant battery, tip `096e77f7...`): exit 1, `passed=2/5 met=False`. Baseline passes (`exit=0`, all legs `returned_true: true` — the mutant is invisible at baseline). Faults `base-old-counter`, `round56-counter`, `m-drop-ldaudit`: `passed=false` — the battery's exit stays 0 AND the faulted leg's `returned_true` stays true, failing both the `exit == 1` and `not returns_ok[fault]` clauses. Fault `mutant-assert`: `passed=true` (that function was not mutated; its honest return still propagates).
- Distinct fault class: existing controls N06 (`run()` early-`return True`) and N10 (`run = lambda: True`) also destroy the leg's subprocess call, so they die at baseline via the `calls_ok` clause; N12/N14 discard results at the call site with honest returns. This mutant keeps the exact genuine call shape and honest capture and is caught **only** by the one-leg fault-injection legs. The fault matrix is the sole kill path for this class — evidence it does real work; weakening it would admit a baseline-invisible constant-True return battery.

## Restoration evidence
- `git -C <clone> checkout --detach aca8d00...` → `status --porcelain` empty, `diff --quiet aca8d00...` clean (`WORKTREE-EQUALS-PRISTINE-TIP`); both battery paths sha256 back to pristine `69b77a6a64f2667757842c2471ddc256d12ceb5ccca6df0a57b88bbe17ab51c5`.
- Restored detector run `--repo <clone> --tip aca8d00...` → exit 0; output sha256 `84856a06...` — byte-identical to the pristine baseline (`RESTORED-OUTPUT-IDENTICAL-TO-PRISTINE`).

## Bounds
No lane source edited, no lane commits; all mutations in `/fast/scratch/hyaku/kama-r59/M09ReturnLiteral/` (clone + fixture, removed after this report). No tool installs (python3/git sufficient). TMPDIR set to the scratch dir for every detector run. C2 untouched (calibration not exercised by this seat).
