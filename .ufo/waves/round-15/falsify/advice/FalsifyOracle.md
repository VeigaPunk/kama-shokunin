# FalsifyOracle — round 15

Verdict: **no fail finding.** The harness grades against the literal `expected_rejected`, runs the real runner CLI, and reaches the real domain classifier. No expected value is recomputed from what is observed.

Candidate: commit `70af36c`. `tests/ollama-corpus-guard/check.py` is tag `#2C84` and matches HEAD. `.ufo/waves/round-14/measure.py` has sha256 `46c5866d…5257` and matches HEAD. No checks were executed; everything below comes from reading files plus metadata counts on the matrix JSON.

## Axes
oracle literalness · real-runner fidelity · real-classifier fidelity · discriminating power · fail-closed matrix

## Evidence

1. **The graded oracle is literal.**
   - `grade()` reads `expected_rejected = test["expected_rejected"]` (check.py:479). It branches only on that value (528/576).
   - `expected.total` is `len(names)` from the input. It never comes from runner output.
   - Every observed value (exit, `verdict_exit`, passed/failed/total, error, `tool_present`, `observed_exit`, marker and audit counts) is compared against those fixed values. None of them is assigned into an expectation.
   - The text of all 12 matrix files contains only JSON literals `true` or `false`: 27 true and 23 false across 50 test ids.
   - Every value is a Python `bool`, and no test id is duplicated across files.

2. **The cross-check in `load_matrix` is a precondition, not a substitution.**
   - Lines 192–211 compute stripped-distinct counts only to *reject a malformed matrix*: fewer than 16 distinct names, a rejected control with no duplicate, or a valid control that has one. The derived value never replaces the literal.
   - I recomputed the counts independently, using the runner's own `declared` rule (non-blank `strip()`) and an NFC variant.
   - For all 50 entries, harness-distinct, runner-unique and NFC-unique are equal, there are 0 blank names, and each literal matches whether the entry actually contains a duplicate.

3. **The real runner CLI is used.**
   - The launcher sets `sys.argv[0]=RUNNER` and runs `runpy.run_path(RUNNER, run_name="__main__")` (check.py:282-283).
   - The arguments are the runner's real flags, `--tool <wrapper> --cases <cases.json>` (362-371).
   - The runner's `__file__`-relative defaults (measure.py:55-58) resolve to the real path. The launcher catches no exceptions, so the runner's exit status passes through unchanged.

4. **The real classifier is used.**
   - The wrapper writes one marker line, then runs `runpy.run_path(TOOL, "__main__")`, where TOOL is `tools/kama-ollama-evidence.py`.
   - The classifier's `prog` is hardcoded (line 450). It uses `SCRIPT=Path(__file__)` only in its selftest (395), and it imports no sibling modules. The wrapper's different `argv[0]` therefore does not change its output.
   - For valid controls, `passed==total` requires every case to match the committed fixture's literal `expected_exit` and `expected_finding` (template `loaded_same_digest`, index 0 of `tests/ollama-evidence/cases.json`). It also requires the domain schema, readiness and scope (measure.py:299-323).

5. **The matrix can tell the fixed runner from the old one.**
   - `.ufo/waves/round-15/frozen/measure-before.py` (sha `fda61e00…`, source commit `6e348e2`) differs from HEAD only by the two guard lines (358-359).
   - All 27 rejected entries have at least 16 runner-unique names. The old runner would therefore measure them and exit 0 with marker and Popen counts equal to `len(names)`, which fails the rejected expectations. [INFERENCE from source; not executed.]

6. **Process observation fits Python 3.14.7.**
   - The valid branch checks only `subprocess.Popen` count == total, not total process events. Extra `os.posix_spawn` or `os.fork` events cannot cause a false failure, and the runner passes `cwd`, so CPython uses `fork_exec`.
   - The rejected branch requires the marker count, the process-event count and the Popen count all to be 0.

## Non-defects noted (no action needed)

- **Blank names.** The harness counts a stripped-blank `""` toward its 16-name minimum, but the runner's `declared` list leaves it out. No committed entry has a blank name. If one did, the `DUPLICATE_REASON in error` check (537) would still catch a masked minimum. Impact: none.
- **Shared predicate.** The matrix precondition uses the same `strip()`+set predicate as the guard. That is the contract the guard must meet, and `ValidBoundaries_16DistinctPlusCaseVariantN00Accepted` (literal `false`) checks that the guard does not casefold.

## Smallest safe correction
None required.

## Tooling
No installs or updates.
