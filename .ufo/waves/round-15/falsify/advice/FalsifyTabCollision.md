# FalsifyTabCollision: tests/ollama-corpus-guard/TabCollision.json

Scope: static reading only. No tests, builds, or runner/check executions were run. No installs were performed.

## Verdict

No fail finding. Both fixtures in `TabCollision.json` satisfy the matrix loader predicate in `check.py` and the final runner predicate in `.ufo/waves/round-14/measure.py`, as far as the source reads. The analysis below is analytic, not executed.

## Fixture facts

| case | envelope | expected_rejected | raw entries | distinct after `str.strip()` | duplicate |
|---|---|---|---|---|---|
| TabCollision-tab-wrapped-duplicate-array | array | true | 17 (n00..n15, `"\tn09\t"`) | 16 | `"\tn09\t"` -> `n09`, collides with index 9 |
| TabCollision-tab-wrapped-unique-array | array | false | 17 (n00..n15, `"\tn16\t"`) | 17 | none |

Source: `tests/ollama-corpus-guard/TabCollision.json:1-50`. The `\t` sequences are JSON escapes, so the strings contain real tab characters.

## Predicate walk

1. **Matrix loader (`check.py:139-226`).**
   - Duplicate case: `distinct`=16 is not `<16`, so it passes the minimum-corpus gate. `expected and distinct == len(stripped)` compares 16 with 17, so it is accepted as a rejected control.
   - Unique case: `distinct`=17 and `len`=17, so `not expected and distinct != len` is false. It is accepted as a valid control.
   - `envelope` is `array`, and `expected_rejected` is a bool. Both pass validation.
2. **Clone and stage (`check.py:348-360`).** Each name is written as `case["name"]` into a bare JSON array, because the envelope is `array`. `ensure_ascii=False` keeps the tabs as JSON escapes, which read back as tabs.
3. **Runner loader (`measure.py:109-128`).** A bare list is accepted (`isinstance(document, list)`).
4. **Final runner predicate (`measure.py:350-364`, consumed at `measure.py:367-385`).**
   - `declared` collects `name.strip()` for every non-empty string name.
   - Duplicate case: `declared` has 17 entries, `unique`=16. `len(declared) != unique` appends `"duplicate case names"`. `unique`=16 passes the `< 16` check, so the only reason is the duplicate reason.
   - `run()` evaluates `corpus_problems` at line 374. When `corpus` is non-empty, it builds `unmeasured_record` for each case and skips the `tempfile` and `measure_case` branch. No child is spawned. `observed_exit` is `None` for all 17 records (`measure.py:167`).
   - Unique case: `declared`=17, `unique`=17, no problems. The `elif tool_present` branch runs `measure_case` once per case, with one `subprocess.run` each (`measure.py:240`). That gives 17 wrapper invocations and 17 `subprocess.Popen` audit events.
5. **Grader (`check.py:478-604`).**
   - Rejected expectation: requires exit 1, `verdict_exit` 1, `"duplicate case names"` in `error`, `passed`=0, `failed`=total=17, `tool_present` True, 17 null `observed_exit` records, marker count 0, audit process events 0, and Popen events 0. The runner path above produces each of these values.
   - Valid expectation: requires exit 0, verdict 0, `passed`=17, `failed`=0, marker count 17, and Popen events 17. The per-case `subprocess.run` gives exactly 17 Popen events, and the template (`tests/ollama-evidence/cases.json`, first `expected_exit: 0` case at line 14) provides a passing clone source.
6. **Boolean/envelope correspondence.** `expected_rejected` true pairs with the duplicate corpus and false with the unique corpus. Both use the bare-array envelope, so the correspondence holds for this file.

## Boundary observations (not defects)

- The duplicate fixture sits exactly on the minimum boundary: 16 distinct stripped names with 17 entries. The rejection therefore comes from the duplicate guard alone. It does not depend on the minimum guard.
- The unique fixture uses 17 names, one above the minimum. It is a valid control for the duplicate guard, but not a boundary test for the minimum.

## Low-severity predicate asymmetry (not exercised by TabCollision)

- `check.py` counts every `item.strip()`, including empty or whitespace-only strings, as a distinct name. The runner's `corpus_problems` excludes empty names from `declared`. The two predicates can therefore disagree for fixtures containing empty names.
- Under this asymmetry, the harness fails closed:
  - An `expected_rejected: true` fixture whose duplicate exists only among empty names is not flagged by the runner, so the runner measures its children. The grader then requires exit 1, which fails.
  - An `expected_rejected: false` fixture with fewer than 16 non-empty distinct names may pass `check.py` but be rejected by the runner. The grader then requires exit 0, which fails.
- No committed fixture in `tests/ollama-corpus-guard/*.json` was found to contain empty names in the reading performed. This is an observation about the predicate, not a finding against TabCollision.

## Residual risk and verification gaps

- The clean-measurement claim for the unique case depends on the real classifier returning the template's `expected_exit` and `expected_finding` for each clone. That is unobserved here and needs the L1 run.
- The audit hook counts only `subprocess.Popen` and listed process prefixes in the runner process. It does not attribute grandchildren, as `check.py` LIMITS already state.

## Tooling record

No tools were installed or updated. No pacman transaction was attempted (host-wide pacman pause in effect).
