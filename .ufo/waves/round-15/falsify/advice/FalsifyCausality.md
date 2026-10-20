# FalsifyCausality: frozen runner vs current runner

Scope: static comparison of `.ufo/waves/round-15/frozen/measure-before.py` against `.ufo/waves/round-14/measure.py`, plus a check that the classifier did not change. I ran no gates or tests. The only inputs were reads, `diff`, `sha256sum`, `git` metadata, and counts of JSON names.

**Verdict: no counterexample found.** The change is the intended guard and nothing else. The classifier and the original corpus are byte-identical to HEAD.

## Evidence

1. **Frozen copy matches the committed runner.**
   - `measure-before.py` sha256 is `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`.
   - That value equals `frozen/manifest.json:4`. It also equals `git show HEAD:.ufo/waves/round-14/measure.py | sha256sum`.
   - `diff --no-index` between the frozen copy and the HEAD blob returns rc 0.

2. **The change is exactly two added lines.**
   - `diff -u frozen/measure-before.py round-14/measure.py` has one hunk, `@@ -355,6 +355,8 @@`.
   - The added lines, at current `measure.py:358-359`, are `if len(declared) != unique:` and `problems.append("duplicate case names")`.
   - The check is inserted before the unchanged `<16` minimum check.
   - The name source is unchanged: `declared` still holds `name.strip()` for non-blank string names (`:351-355`).
   - Nothing else in the file differs: docstring, `LIMITS`, constants, `run()`, `measure_case()`, `child_environment()`, `case_name()`, `load_cases()`, `main()`. Sizes are 491 → 493 lines; current sha256 is `46c5866d73a4f875353ff59c6929615149a1f4f4acf69b0b07deeb99d5445257`.

3. **The classifier is unchanged.**
   - `tools/kama-ollama-evidence.py` blob `d38e2ae6…` matches the index.
   - Its sha256 is `38d1f5d2…fb02`, which equals the round-14 receipt `tool_sha256` that sibling audits cite.
   - `git diff HEAD --quiet -- tools/ tests/ollama-evidence/` returns rc 0.
   - `git diff HEAD --name-only -- ':!*.md'` lists only `.ufo/waves/round-14/measure.py`.

4. **The duplicate check runs before any child process.**
   - The runner starts a child process in only one place: `subprocess.run` at `:240`, inside `measure_case`.
   - `run()` calls `corpus_problems` at `:374`.
   - When `corpus` is non-empty, `run()` goes to `unmeasured_record` (`:377-380`) and never reaches the `elif tool_present:` loop that calls `measure_case` (`:381-385`).
   - In that case `error` is set to `"corpus: duplicate case names…"` (`:421-422`) and `verdict_exit` is `EXIT_FAIL`, because every record has `passed: False`.

5. **The frozen runner was the actual cause of the bug, and the new fixtures isolate it.**
   - I recounted all 50 fixture entries in `tests/ollama-corpus-guard/*.json` (12 files), stripping names the same way the runner does.
   - Every `expected_rejected: true` entry has at least 16 unique stripped names. The frozen check (`unique < 16`) therefore cannot reject any of them; only the new check can. Counts:
     - 28 entries have `unique` = 16.
     - 1 entry (DistantDuplicate array) has `unique` = 32.
   - Every `expected_rejected: false` entry has `declared == unique ≥ 16`. Both runners accept these, so there is no regression on valid boundaries.
   - Valid entries that must stay accepted include TabCollision-unique (17/17) and ValidBoundaries case-variant (17/17).

6. **The red control cannot be mistaken for something else.**
   - `check.py:362-371` always passes `--tool` and `--cases` explicitly. Without that, the frozen copy's relocated `LANE` default (`WAVE.parents[2]` under `round-15/frozen` → `.ufo`) would point at a missing tool.
   - The rejection grade (`check.py:528-575`) requires all of the following:
     - `error` contains the literal `"duplicate case names"` (`:69`), which the frozen runner never emits.
     - `tool_present is True`.
     - Zero classifier markers.
     - Zero audited process events or `Popen` calls.
   - A missing-tool failure or a minimum-count failure therefore cannot count as a duplicate rejection.

7. **Valid measurement of the original corpus is preserved.**
   - The default `tests/ollama-evidence/cases.json` is unchanged from HEAD and has 51 entries, 51 names and 51 unique stripped names.
   - On that corpus the new check is false, so the run takes the same `measure_case` path as before.

## Tradeoff (not a defect)

- **Same path, different bytes.** The repair edits `.ufo/waves/round-14/measure.py` in place, and the round-14 `acceptance.json` command still names that path. Re-running it now runs the repaired runner, and the output schema `kama-round-14-measure/v1` is unchanged, so the output alone does not show which runner produced it. `corpus/lessons/round-15.md:111-118` already records the measured-commit blob `7830045…` and sha256 `fda61e…`. The smallest safe correction is for the round-15 receipt to also pin the final repaired sha256 (`46c5866…`, if the file is not edited again).
- **No Unicode or case normalization.** NFC/NFD and case variants still count as distinct names. That is the specified stripped-name policy (lesson `:91-92`), not a defect in this change.

## Impacted axes

Operability (C1 guard): the fix is supported by this evidence. Numeric 7 → 7: unaffected. Classifier and runtime claims: unaffected.

## Tooling

No installs or upgrades.
