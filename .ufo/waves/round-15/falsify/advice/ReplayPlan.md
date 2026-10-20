# ReplayPlan — displaced duplicate overfit check

## Finding

The inspected predicate is not keyed to a fixture ID, case-name literal, or index. In `measure.py:350–364`, `declared` contains each nonblank string name after `strip()`, `unique = len(set(declared))`, and the new condition rejects when `len(declared) != unique`. For any repeated name in that declared-name domain, regardless of its value or position, the list has more entries than its set; moving or renaming the duplicate consistently does not change that relation. The existing 16-unique floor remains separate.

## Evidence chain

- **Changed source:** `.ufo/waves/round-14/measure.py:350–364` has the general cardinality predicate. The frozen pre-repair `.ufo/waves/round-15/frozen/measure-before.py:350–362` has only `unique < MINIMUM_UNIQUE_CASES`, so it would not detect either of the following fixtures from the minimum check alone.
- **Displaced duplicate fixture:** `tests/ollama-corpus-guard/DistantDuplicate.json:2–40` declares `n00` first, then `n01` through `n31`, then `n00` again: 33 entries and 32 distinct names, with `expected_rejected: true`. This exercises a repeated name separated from its first occurrence by 31 intervening names, not a name-specific or adjacent-only rule.
- **Second cardinality/envelope:** `DistantDuplicate.json:42–65` repeats `m00` at the end of a 17-name object-envelope corpus with 16 distinct names, also marked rejected. `measure.py:120–127` accepts both an array and an object containing a `cases` array.
- **Non-rejection counterpart:** `DistantDuplicate.json:66–104` contains the 32 distinct names `n00`–`n31` and marks the corpus `expected_rejected: false`; this distinguishes duplicate presence from a blanket rejection of the large corpus.
- **Ordering:** `run()` calls `corpus_problems(cases)` at `measure.py:374`. A nonempty result takes `:377–380` and creates unmeasured records; only the empty-result/tool-present branch at `:381–385` calls `measure_case()`. The inspected child `subprocess.run()` is inside `measure_case()` at `:239–251`. Thus the source path places this generic rejection before that child call. This is static control-flow evidence, not an observed run.

## Divergences and limits

- I did not run the runner or matrix. Fixture `expected_rejected` values and the predicted paths are not runtime observations; actual rejection and zero-process behavior remain for the authorized integration verification.
- The guarantee is specifically over dictionary cases with nonblank string `name` values after `strip()`. Missing, non-string, and blank names are omitted from `declared`; this check does not claim to identify those as repeated declared names. Identity remains case-sensitive and is not otherwise normalized.
- No `lsp` device is mounted (`xd://lsp` reported no such tool), so the call path was inspected directly in the named source; no grep-based caller claim is used.

## Confidence

High that the source predicate is name- and position-independent within its declared-name domain, and that the two literal distant fixtures distinguish the repaired predicate from the frozen minimum-only guard. Runtime behavior remains unverified here.

Report: .ufo/waves/round-15/falsify/advice/ReplayPlan.md
