# FalsifyFailure — round-15 falsification

Attack: the harness's error handling must never count a missing fixture or bad subprocess JSON as a pass.
Targets: `tests/ollama-corpus-guard/check.py` (harness) and `.ufo/waves/round-14/measure.py` (runner, child-JSON path).
Method: static reading only, plus plain metadata counts (`jq` lengths, `find -type l`). I did not execute the harness, runner, classifier, or any test. I installed nothing.

## Verdict: PASS — no counterexample in the committed candidates

I found no path in the committed harness and runner where a missing fixture or unparseable or ill-typed subprocess JSON ends as `finding_id: clean` / exit 0. Three low-severity residuals are listed below. They are notes for how L1 reads the gate. None is a defect in the committed pair, and none is a request for a new feature.

## Evidence: missing inputs fail closed

| Input | Where | Outcome |
|---|---|---|
| Runner file absent | `check.py:720-721` | `HarnessError` → `error_document`, `test_failed`, exit 1 |
| Classifier absent | `check.py:722-723` | same |
| No `*.json` in the matrix directory | `check.py:144-147` | same |
| Matrix file unreadable, not UTF-8, or not JSON | `check.py:127-136` | same |
| Matrix document not an array, bad entry, duplicate test id, fewer than 16 distinct names, or expectation that does not match its names | `check.py:150-223` | collected into `problems`, then one `HarnessError` (nothing is skipped silently) |
| Matrix parses but has zero tests | `check.py:224-225` | `HarnessError` |
| `--only` matches no test | `check.py:725-730` | `HarnessError` |
| `tests/ollama-evidence/cases.json` missing, malformed, or without an `expected_exit: 0` template | `check.py:236-254` | `HarnessError` (no other fixture is substituted) |
| Marker or audit file missing or unreadable after the run | `check.py:343-344` precreated; `count_lines`/`read_audit` return `None` | `None != 0` or `None != total` adds a reason; `test_record` and `grade` both add explicit "missing or unreadable" reasons |
| Runner timeout or failure to start | `check.py:379-411` → `test_record` | the record is hard-coded `"passed": False` (`check.py:460`) |
| Any other exception (cleanup, encoding, recursion) | `check.py:738-740` | catch-all → `test_failed`, exit 1 |
| Empty records | `check.py:641` | `clean = bool(records) and failed == 0` |

## Evidence: bad subprocess JSON fails closed

**Harness grading the runner's stdout (`check.py:494-511`):**
- If stdout is not valid JSON, `JSONDecodeError` adds a reason. That is enough to fail the record (`check.py:622`, `passed = not reasons`).
- If stdout is valid JSON but not an object (array, number, or string), `result_payload = {}`. Every expectation then sees `None`:
  - `verdict_exit` is checked against 1 or 0 (`:531`, `:579`).
  - `passed`, `failed`, and `total` are checked against the expected counts.
  - In the rejected branch, `null_exit_records` stays `None` and is compared with `!= total` (`:558`).

  So an unparsed or non-dict payload cannot meet either the rejected or the accepted expectation.
- Exit code, marker count, and audit or Popen counts are graded separately from the payload (`:529`, `:563-575`, `:577`, `:596-603`). A forged or partial payload therefore cannot hide a spawn: a nonzero marker count or Popen count still fails a rejected control.

**Runner grading the classifier child's stdout (`measure.py:259-325`):**
- Invalid JSON sets `detail` ("child stdout is not one JSON object"), which becomes a reason.
- A JSON value that is not an object sets "child JSON is not an object".
- An object without a string `finding_id` sets "child JSON has no string finding_id".
- A `verdict_exit` that is a bool or not an int stays `None`. It then fails the check against the process exit (`:283-284`, `:312-314`).
- The child runs with `text=True, errors="replace"` (`measure.py:246-248`), so bytes that are not valid UTF-8 cannot raise outside the handled path. They at worst become replacement characters, and that fails the JSON or field checks.
- A record passes only when it has no reasons. The run is clean only when `records and failed == 0` (`measure.py:395-397`).

Fixture metadata counted: 12 regular files, 50 test ids, 50 unique, 27 `expected_rejected: true` and 23 `false`. `find -type l` returned no symlinks.

## Residuals (low; how L1 reads the gate, not harness defects)

1. **Matrix completeness is not pinned inside the harness.**
   - The harness reads whatever `*.json` files exist (`check.py:141-143`). If 11 of the 12 files are deleted, it still runs the remaining tests and can report `clean` with a smaller `total`.
   - A dangling symlink named `*.json` is dropped silently by the `is_file()` filter (`:142`).
   - The harness does report `matrix_sources` and `total`. Smallest safe correction, on the gate side only: L1 accepts `clean` only with `total == 50`, the 12 expected `matrix_sources`, and no `--only`.
   - Impacted axis: operability evidence (it could under-count coverage). Current state: there is no counterexample, because all 12 files are present and none is a symlink.

2. **Count and exit checks in `grade` use plain `==`/`!=`, so JSON booleans and floats alias integers.**
   - In Python, `true == 1`, `false == 0`, and `16.0 == 16`.
   - The harness also does not check the runner payload's `schema`.
   - The committed runner always emits ints from `len()`/`sum()` and the `EXIT_*` constants (`measure.py:395-418`, `:451-454`), so the committed pair has no counterexample.
   - This only matters if a different `--runner` is substituted, and the harness `LIMITS` already disclaim nonconforming or malicious runners. I judge this a tradeoff, not a fixable defect for this round.

3. **`check.py -h`/`--help` exits 0 with plain-text help.**
   - argparse's help action raises `SystemExit(0)`, which `except Exception` does not catch (`check.py:717-741`). This mirrors the runner finding HarnessReview F4.
   - Smallest safe correction, on the gate side only: L1 treats a run as clean only when stdout parses as JSON with `schema == kama-corpus-guard-test/v1` and `finding_id == "clean"`. Exit code 0 alone is not enough.

## Impacted axes
- **Operability:** the claim holds. The only exposure is residuals 1 and 3 if L1 checks the exit code alone.
- **Numeric:** unaffected; the score stays 7.

Report: .ufo/waves/round-15/falsify/advice/FalsifyFailure.md — static falsification of fail-closed handling for missing fixtures and bad JSON; PASS with 3 low gate-reading residuals; no checks executed; no tools installed.
