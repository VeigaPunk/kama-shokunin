VERDICT: confirm - the frozen arm misclassifies aborts; patched arm requires complete enumeration.

Axes: calibration (assigned 7; addressed); operability (assigned 8; unchanged).

## Evidence

- Frozen checkout: `37bd4c5bd456a2f8a54d3312c28495c321715856` (rev-parse exit 0). Original `survivors.py` SHA-256: `ac934794af1eee8067ea11f7f8cc31702ea7dfad257fec2649f2d638477bac75`; the retained selftest's measured-commit counter has identical bytes.
- Frozen `.ufo/waves/round-18/c2/survivors.py:931-956` looks only for the expected literal on a `FAIL` line before returning `killed`; it does not require mutant-side enumeration evidence.
- Patched-arm command `python3 /tmp/kama-r20-CloseKama18.SurvivorsArmEnum-2/arm_regression_probe.py` exited 0. An actual child printing the same AO-blank target `FAIL` line and exiting 1 without a summary is `inconclusive`; the retained complete target case (36 passed + 6 FAIL lines = 42) remains `killed`. A truncated `1/42` summary plus one `FAIL` line is `inconclusive`.
- Baseline totals are pinned to retained evidence: `runs/c2-counter-selftest.stdout` has `60/60 checks passed` and its measured counter blob matches the frozen source. The exact append-only subject hash at the frozen revision is `4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d`; retained C2 evidence for those same bytes records `42/42` baseline and AO-blank exit 1 / `36/42`. Full original stdout bytes are not retained; the test uses its six captured failure lines and final summary.
- Three new `check()` assertions imply a patched counter selftest total of `63/63`, if all pass [INFERENCE: retained actual baseline 60 plus three added checks]. The full selftest was intentionally not run.

## Deliverables and scope

- Final patched counter: `build/out/CloseKama18.SurvivorsArmEnum-2/survivors-patched-final.py` (SHA-256 `c4c29c5a1d5d8a3981bfff58934d59c03cbb8f76f1dcf540edd8556ec4813890`).
- Final transcript: `build/out/CloseKama18.SurvivorsArmEnum-2/arm-regression-transcript-final.txt`. The earlier `survivors-arm-enum.patch`, `survivors-patched.py` and transcripts are preliminary; these final artifacts supersede them.
- JSON completion requires the baseline's declared count/coverage fields and gate/escape keys; text completion requires matching denominator and `passed + FAIL-case-lines == total`.
- [INFERENCE / risk] The strict JSON baseline count rule will make the retained FC-f6cache mutant (wrapper_checks 32 vs baseline 35) inconclusive despite its target problem; JSON-baseline matching was retained as the scoped policy.
- No lane source was modified. No full C2 measurement, counter selftest, build, lint, or formatter ran. No tool was installed. No LSP device is mounted; source inspection used `read`/`grep`.
