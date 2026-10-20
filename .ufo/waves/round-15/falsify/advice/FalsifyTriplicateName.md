# FalsifyTriplicateName — round-15 falsification report

Scope: `tests/ollama-corpus-guard/TriplicateName.json` against the final runner predicate
(`.ufo/waves/round-14/measure.py` `corpus_problems`/`run`) and the matrix predicate
(`tests/ollama-corpus-guard/check.py` `load_matrix`/`grade`). Read-only. No checks, tests,
builds, or installs were run. Tools installed: none.

## Verdict on the assigned fixture

No defect found in `TriplicateName.json`. Each row was read and counted.

| Row (line) | Envelope | Items | Stripped distinct | Duplicate present | expected_rejected | Consistent |
|---|---|---|---|---|---|---|
| `TriplicateName_array_n08_triplicated_separated` (2-26) | array | 18 (n01-n16 + n08, n08) | 16 | yes (n08 x3) | true | yes |
| `TriplicateName_object_n08_triplicated_separated` (27-51) | object | 18 | 16 | yes | true | yes |
| `TriplicateName_array_n08_triplicated_adjacent` (52-76) | array | 18 (n01-n07, n08 x3, n09-n16) | 16 | yes | true | yes |
| `TriplicateName_array_n08_triplicated_strip_equivalent` (77-101) | array | 18 (n01-n16, " n08", "n08 ") | 16 | yes (after strip) | true | yes |
| `TriplicateName_array_16_distinct_no_duplicate` (102-124) | array | 16 | 16 | no | false | yes |
| `TriplicateName_object_16_distinct_no_duplicate` (125-147) | object | 16 | 16 | no | false | yes |

- Every negative has exactly 16 stripped distinct names, which is the minimum. The
  boundary is hit exactly, so it neither trips `distinct < 16` nor leaves a masked case.
- Positive controls have 16 distinct names, so `len(stripped) == distinct`.
- Envelope values are `array` or `object`, and `expected_rejected` values are JSON booleans.
- Test ids are unique. A grep of `tests/ollama-corpus-guard` finds the six ids only in this
  file.
- `check.py` `load_matrix` (lines 192-211) enforces all of this at load time, in both
  directions: a negative with no duplicate, or a control with one, is a `HarnessError`.
  The fixture therefore cannot silently grade the wrong way.

## Runner predicate (final `measure.py`)

- `corpus_problems` (350-364): `declared` collects `name.strip()` for dict cases whose
  stripped name is non-empty. `len(declared) != unique` appends `"duplicate case names"`
  (358-359). `unique < 16` appends the floor message (360-363).
- `run` (367-425): `load_cases` only reads bytes and parses JSON. `corpus` is evaluated at
  374-377. The `if corpus:` branch (377-380) emits `unmeasured_record` per case with
  `observed_exit: None` and returns. Only the `elif tool_present:` branch reaches
  `measure_case` and the `subprocess.run` (382-385). The rejected corpora therefore spawn
  no child before the guard fires.
- Exit and verdict: `verdict = EXIT_FAIL (1)` when any record fails. `main` returns that
  code. Error string is `"corpus: duplicate case names"`, which satisfies
  `DUPLICATE_REASON` in `grade` (check.py 536-540).

Consistency with `grade` for `expected_rejected: true` (check.py 528-575):
exit 1, verdict 1, error contains `duplicate case names`, passed 0, failed = total = len(names),
`tool_present` true (the wrapper exists), null `observed_exit` on every record, marker 0,
audit process events 0, Popen events 0. Each of these is produced by the corpus branch as read.

## Findings

### F1 — medium: rejected-branch "zero child" claim is weaker than stated (audit prefix gap)
- Evidence: `check.py` `PROCESS_EVENT_PREFIXES` (79-85) = `subprocess.Popen`, `os.system`,
  `os.posix_spawn`, `os.fork`, `os.exec`. `os.spawn*` (`os.spawnv`, `os.spawnl`, ...) is
  not listed. The docstring (lines 30-32, 36-38) states the rejected-branch requirement as
  "before ANY child classifier process is spawned" and "runner process event count 0".
- Concrete attack shape (not run): a runner that, on a rejected corpus, calls
  `os.spawnv(os.P_WAIT, sys.executable, [sys.executable, CLASSIFIER, ...])` directly, not
  through the test wrapper. The wrapper marker stays 0 because the wrapper is never used.
  `subprocess.Popen` count stays 0. Process-event prefixes do not match `os.spawn*`. Every
  rejected-row assertion would still pass.
- Confidence: the code path is confirmed by reading. That CPython raises an audit event
  named `os.spawn` is [INFERENCE] from memory of the audit-events table. I could not
  confirm it here: the stdlib `.py` sources do not contain it and a literal grep of
  `libpython3.14` returned nothing, which is inconclusive.
- Impact on `TriplicateName.json`: none directly; the fixture is correct. Impact is on the
  harness claim for all rejected rows. Note that LIMITS (72-98) already disclaims
  grandchildren and helpers; the gap here is a direct classifier spawn by the runner.
- Bounded remedy for L1 to consider (no feature expansion): either add `"os.spawn"` to the
  prefix tuple, or narrow the docstring claim to "no subprocess.Popen/os.system/posix_spawn/
  fork/exec events".

### F2 — low: blank-name policy disagrees between matrix predicate and runner guard
- Matrix (`check.py` 192-194): `stripped = [item.strip() ...]`, and `distinct = len(set(stripped))`
  counts `""` as a distinct value.
- Runner (`measure.py` 353-356): blank or whitespace-only names are skipped from `declared`,
  so they never count toward duplicates.
- Concrete divergence: 16 real names plus two `""` entries.
  - Matrix: distinct = 17, len = 18, so it validates as `expected_rejected: true`.
  - Runner: declared = 16, unique = 16, no duplicate, so it measures 18 cases. The
    matrix row would then fail with an exit mismatch. The runner accepts a corpus with
    duplicate blank names.
- Not covered by any committed row: `TriplicateName.json` has no blank names. No other
  matrix file in the directory has blank names either. This is a coverage gap plus a
  predicate mismatch, not a fixture defect.

### F3 — info: envelope and shape coverage is uneven (not a defect)
- Object-envelope negatives exist only for the "separated" shape. "Adjacent" and
  "strip_equivalent" are array-only. Both positive controls exist for both envelopes.
- Envelope handling is envelope-independent in `load_matrix` and in runner `load_cases`
  (dict with `cases` list), so no predicate gap follows. Listed for completeness only.

## Residual risk and verification gaps
- All conclusions are from source reading and fixture counting. Nothing was executed.
- The rejected-branch argument relies on the runner's `if corpus:` placement (377) being
  before `subprocess.run` (382-385), as read above.
- F1's `os.spawn` audit-event name is unverified in this environment.
- For L1: run `check.py --selftest` once after all edits. Expect the six TriplicateName
  rows to grade pass. Do not treat that as proof against F1 or F2, since neither is
  exercised by a committed row.
