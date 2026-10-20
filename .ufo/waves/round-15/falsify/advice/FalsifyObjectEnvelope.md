# FalsifyObjectEnvelope — round-15 falsification (read-only)

Scope: `tests/ollama-corpus-guard/ObjectEnvelope.json` and the final runner predicate
`.ufo/waves/round-14/measure.py` (`corpus_problems` L350-364, called from `run()` L374).
Also read `tests/ollama-corpus-guard/check.py` for matrix loading and grading.
No checks, tests, or runners were executed. Reading only. No tools installed.

## Verdict

No defect attributable to `ObjectEnvelope.json` or to the runner duplicate predicate for
the committed fixture. One low-severity divergence between the matrix loader and the runner
predicate (Finding 1) is not exercised by any committed fixture.

## Invariant checks on ObjectEnvelope.json

| Test | Entries | Distinct stripped | Duplicate present | expected_rejected | envelope |
|---|---|---|---|---|---|
| `ObjectEnvelope_duplicate_n14_trailing` | 17 (n00..n15, n14) | 16 | `n14` at idx 14 and 16 | true | object |
| `ObjectEnvelope_duplicate_n14_adjacent` | 17 (n00..n15, n14 doubled) | 16 | `n14` at idx 14 and 15 | true | object |
| `ObjectEnvelope_valid_16_unique` | 16 (n00..n15) | 16 | none | false | object |

- Negatives have exactly 16 stripped distinct names, so the minimum guard
  (`measure.py` L360; `check.py` L194) does not fire and the duplicate guard is isolated.
  The fixture contains no whitespace variants; stripping is not exercised here.
- Duplicates are real: `load_matrix` (`check.py` L201-206) rejects a `true` control with no
  duplicate, and L207-211 rejects a `false` control with a duplicate. The fixture passes both.
- Envelope: all three are `object`. `check.py` L354-355 wraps them as `{"cases": [...]}`.
  `measure.py` `load_cases` L122-123 accepts that shape. Envelope is not otherwise tied to
  `expected_rejected` by the loader; that is by design, not a defect.
- Test ids are unique across the 12 sibling matrices (grep of `"name"` fields; no
  `ObjectEnvelope_*` collisions).

## Runner predicate (final)

- `corpus_problems` strips each declared name, counts `len(set)` against `len(declared)`, and
  flags `duplicate case names`. The min check uses `unique < 16`.
- `run()` computes `corpus` at L374 and, when non-empty, emits unmeasured records for every
  case (L377-380) and skips the `tempfile` / `measure_case` / child loop (L381-385). So no
  child is started on the rejection path.
- Unmeasured records set `observed_exit: None` (`unmeasured_record` L167), matching the
  `null_observed_exit_records == total` check in `check.py` L558.
- `main()` (L477-489) performs no subprocess before `run()`. `tool.is_file()` and
  `sha256_file` are not process creation.

Conclusion: for the committed fixture, a duplicate corpus is rejected before any child
process on this path, and the valid 16-unique control reaches the measurement loop.

## Mutation reasoning (not executed)

Each mutant below would be caught by the ObjectEnvelope matrix as described:

- Duplicate guard removed: trailing and adjacent tests measure 17 cases, marker count 17 ≠ 0, exit 0 ≠ 1. Caught.
- Guard moved after the child loop: marker count > 0. Caught.
- Guard only checks adjacent pairs: trailing test survives and is measured. Caught by the trailing test.
- Guard only applies when `unique < 16`: 16-unique duplicate tests are measured. Caught.
- Guard applies only to the array envelope: `load_cases` raises on `{"cases": ...}` and the error lacks `duplicate case names`. Caught by both object tests.
- Raw (unstripped) comparison: NOT caught by ObjectEnvelope (no whitespace variants). Covered elsewhere by name (`PrependDuplicate-padded-strip-collision`, `WhitespaceCollision-*`, `TabCollision-*`); those files were not re-read here.
- `unique` taken from `len(cases)` instead of `len(declared)`: same value for these fixtures; not caught here (no nameless entries committed).

## Findings

1. **LOW — blank-name divergence between loader and runner.**
   - `check.py` L165-181 only requires each `names` item to be a `str`, so `""` and whitespace-only names pass. L192-193 counts them as a stripped distinct value.
   - `measure.py` `corpus_problems` L353-355 drops blank names from both `declared` and `unique`.
   - Consequence: a matrix control can meet the matrix's `>= 16 distinct` floor while the runner sees fewer than 16 unique names. Such a control can still be graded as a rejection, because the runner's joined error (L378) includes `duplicate case names` alongside the minimum message. The duplicate reason is genuinely emitted, but the test then is not a >=16-unique corpus test in the runner's own terms, which is the stated claim.
   - No committed fixture contains a blank or whitespace-only name (grep of the matrix directory found none). Severity low; not reachable from the committed matrix.
   - Note: `check.py` L70 and `measure.py` L66 duplicate the constant `16` without sharing it. Drift risk only.

## Residual gaps

- ObjectEnvelope does not exercise whitespace stripping or nameless entries (see mutation table).
- Tool-absent with duplicates is not exercised by the matrix; the harness always stages the tool. The corpus check still precedes the tool check in `run()`, so this is not a gap for the child-process claim.

## Tooling record

None installed or updated. No pacman operations performed (host-wide pacman pause in effect).
