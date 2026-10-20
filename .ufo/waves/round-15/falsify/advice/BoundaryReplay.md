# BoundaryReplay — round-15 falsification (read-only)

Seat: `KamaR15.BoundaryReplay` (leaf, no dispatch). Scope: connection of the R1 duplicate-corpus guard repair to the existing replay path in `.ufo/waves/round-14/measure.py`. No checks, tests, or child processes were run. Reads only.

## Evidence read

- Candidate diff against the frozen pre-repair copy (`.ufo/waves/round-15/frozen/measure-before.py`, source commit `6e348e2`, sha256 `fda61e00…b60d` per `frozen/manifest.json`). The only change is two added lines in `corpus_problems`:
  ```
  if len(declared) != unique:
      problems.append("duplicate case names")
  ```
  (`measure.py:357-359`). Nothing else differs. CLI schema, minimum check, and classification code are unchanged.
- `corpus_problems` (`measure.py:350-364`) builds `declared` from every fixture whose `name` is a string with non-empty `strip()`, appends the stripped name, and sets `unique = len(set(declared))`. Missing or non-string names are excluded from both counts. The check is therefore the stated "existing stripped names" convention and adds no new name-normalization API.
- `run()` (`measure.py:367-425`) calls `load_cases` (`:370`) and then `corpus_problems` (`:374`) before any branch that can spawn a child. Branch order: `if corpus:` (`:377-380`, records unmeasured with `corpus:` reason, no child), `elif tool_present:` (`:381-385`, the only path to `measure_case` and therefore `subprocess.run`, `:240`), `else` (`:386-393`, unsupported, no child). A duplicate corpus therefore never reaches `subprocess.run`, regardless of tool presence.
- `main()` (`:477-489`) is the only caller of `run()`. `error_result` (`:428-457`) spawns nothing. No other code path reaches `measure_case`.
- Output on the rejected path: `total` = fixture count, `passed` = 0, `failed` = total, `verdict_exit` = 1, `error` = `"corpus: duplicate case names; …"`, and `unique_case_names` = stripped distinct count. This matches the spec's "reject before any child" and "fixture count, not computed denominator" requirements.
- Valid path: a corpus with no duplicates and `unique >= 16` yields no `corpus` problems and proceeds through the unchanged `elif tool_present` branch. Measurement is retained.

## Connection to the existing replay (no new API)

- The guard reuses `load_cases` output, the existing `name` field, and the existing `MINIMUM_UNIQUE_CASES` constant. It adds no import, flag, schema field, or child-facing contract.
- The repair does not alter `measure_case`, `child_environment`, the argv list (`:230-235`), or any record field. The `unsupported`/`invalid` branches are untouched.

## Divergence noted (not a defect of the repair)

- The classifier's own selftest (`tools/kama-ollama-evidence.py:359-365`, `run_selftest`) checks duplicates on raw `name` (no `strip()`), and checks total `len(document) >= MIN_CASES`, not unique names. `measure.py` checks stripped duplicates and unique count. For a corpus with names `"x"` and `"x "`, the classifier selftest accepts while `measure.py` now rejects. This is the fail-closed direction and matches the spec's "stripped names" rule. It is a second authority, not a bypass of the guard.
- Fixtures with no string name are excluded from both measures. They run as `case-NN` in `measure.py` and are not counted toward the 16-unique floor. This is pre-existing behavior and the repair does not change it.

## Findings

- No concrete source or fixture evidence of a bypass: every child-spawning path in `measure.py` is downstream of the guard in `run()`.
- No capability inflation: the diff adds one rejection reason and no new output or claim.
- Verdict for this attack: **no defect found in the repair's connection to the replay path.**

## Limits

- Nothing was executed. Conclusions rest on static reading of the frozen diff and the candidate source.
- The candidate sha256 was not recomputed. The diff is from the source text I read, not from a hash check.
- The fixture names were read from `tests/ollama-evidence/cases.json` as data only (51 names, all distinct as read). L1 must confirm uniqueness by executing the guard, which I did not do.

## Tooling

No installs, upgrades, or pacman transactions were performed by this seat.
