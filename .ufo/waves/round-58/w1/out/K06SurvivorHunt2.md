# K06SurvivorHunt2 — vacuous `--counter` survivor

Axes: operability (C1). Calibration/C2 is not implicated.

## Counterexample and evidence

Checker source `tools/round58-battery-exec-check.py` lines 73–77 records every argv submitted to `subprocess.run` and supplies a canned successful result; lines 130–131 count any argv containing the literal `--counter`; lines 204–208 count a `run` frame as executed solely when that count is >=1. No executable identity, argument semantics, exit behavior, output consumption, or assertion/result binding is required.

I exercised the checker's child harness directly with two scratch batteries, against frozen build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`:

- `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round58-battery-exec-check.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a --harness /fast/scratch/hyaku/kama-r58/K06SurvivorHunt2/echo.py --harness-out /fast/scratch/hyaku/kama-r58/K06SurvivorHunt2/echo.json; echo echo_rc=$?` → `echo_rc=0`; receipt: `{"frames": [{"fn": "run", "label": "vacuous-echo", "sub": 1, "counter": 1}], "error": null}`.
- Same command with `true.py` and `true.json` → `true_rc=0`; receipt: `{"frames": [{"fn": "run", "label": "vacuous-true", "sub": 1, "counter": 1}], "error": null}`.

The probes demonstrate the exact execution predicate accepts both vacuous legs. `/bin/true --counter` is in fact not a valid useful counter invocation; the harness does not execute it at all. This was child-harness mode, not a complete outer `--repo` evaluation, so I do not claim either toy file itself satisfies the separate frozen roster/kills/controls predicate.

## Smallest safe correction

Bind observed invocation evidence to the actual check the leg is meant to perform, rather than merely presence of a token: require the expected executable/script and the leg-specific argument/receipt contract, and require the leg's asserted outcome to be evaluated. For the frozen battery this can be a narrow allowlist of its expected `python3 <round56-env-leg-test.py> --counter <expected counter> --expect <expected value>` invocation plus observed assertion/exit checks. Preserve genuine and benign-rewrite behavior by normalizing only irrelevant argv differences; do not reject on spelling or source hashes alone. Then rerun frozen C1 genuine/3 benign/11 no-op suite. This survivor is outside the preregistered 11 and is a reported limit, not a retroactive predicate change.
