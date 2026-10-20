# FalsifyValidBoundaries — round-15 (scoped evidence)

Scope: `tests/ollama-corpus-guard/ValidBoundaries.json` (6 cases), the matrix guard in
`tests/ollama-corpus-guard/check.py` (`load_matrix`, lines 192–211), the grader in
`check.py` (`grade`, lines 478–624), and the runner predicate in
`.ufo/waves/round-14/measure.py` (`corpus_problems` 350–364, `run` 367–425,
per-case path `measure_case` 211–347). No checks, tests, or runner executions were run.
No tools were installed or updated.

## Result

No falsifying finding. The fixture, the matrix guard, and the runner's duplicate and
minimum predicate agree on all six cases, and the rejected cases can only reach the
rejection branch before any child is created.

## Fixture cross-check (hand count of `ValidBoundaries.json`)

| Case (line) | Items | Distinct stripped | Envelope | expected_rejected | Consistent |
|---|---|---|---|---|---|
| Exactly16UniqueArrayAccepted (3–24) | vb00–vb15 = 16 | 16 | array | false | yes |
| ThirtyTwoUniqueArrayAccepted (26–63) | vw00–vw31 = 32 | 32 | array | false | yes |
| Object16UniqueAccepted (65–86) | vo00–vo15 = 16 | 16 | object | false | yes |
| 16DistinctPlusCaseVariantN00Accepted (88–110) | n00–n15 + N00 = 17 | 17 (case-sensitive) | array | false | yes |
| 16DistinctPlusExactDuplicateLastRejected (112–134) | vd00–vd15 + vd00 = 17 | 16 | array | true | yes |
| 16DistinctPlusExactDuplicateFirstRejected (136–158) | ve00,ve00,ve01–ve15 = 17 | 16 | array | true | yes |

- Every rejected case has exactly 16 distinct names, so it is the minimum-boundary duplicate
  case the assignment requires. Its duplicate is exact, not whitespace- or case-based.
- Every accepted case has at least 16 distinct names and no duplicate.
- Test ids are unique. A directory grep for `ValidBoundaries_` ids found only this file.

## Matrix guard (`check.py` 192–211)

- `stripped = [item.strip()...]`, `distinct = len(set(stripped))`. This matches the runner
  predicate's `name.strip()` + `set`, so the two sides use the same notion of distinctness.
- `distinct < 16` rejects the matrix entry, so the minimum cannot mask the duplicate guard.
- `expected and distinct == len(stripped)` rejects a rejected-control with no duplicate.
- `not expected and distinct != len(stripped)` rejects a valid control with a duplicate.
- All six fixtures pass these checks under the hand count above.

## Runner predicate (`measure.py`)

- `corpus_problems` (350–364): duplicate if `len(declared) != unique`; minimum if
  `unique < 16`. For the rejected fixtures the reason string is `duplicate case names`,
  which is the substring `check.py` grades on (`DUPLICATE_REASON`, line 537).
- `run` (367–425): `load_cases` → `tool_present` → `corpus_problems`. When corpus problems
  exist, the `if corpus:` branch writes unmeasured records and never reaches the
  `elif tool_present:` branch that calls `measure_case` → no `tempfile` directory, no
  `subprocess.run`. Verdict: `EXIT_FAIL` (1). `result["error"]` contains
  `corpus: duplicate case names; ...`.
- Accepted cases: 16 or 17 distinct, no duplicate → no corpus problem → each name gets a
  child via `measure_case`. The object envelope unwraps `{"cases": [...]}` in `load_cases`
  (lines 120–123), so the envelope matches.

## Rejected-case grading (`check.py` 528–575)

For each rejected case the grader requires: exit 1, `verdict_exit` 1, error containing
`duplicate case names`, `passed` 0, `failed` == `total` == `len(names)`, `tool_present`
True, `observed_exit` null on every record, marker count 0, audit process-event count 0,
and audit `subprocess.Popen` count 0. Reading the code path, the corpus branch performs no
spawn before the rejection (the launcher's audit hook is installed before `runpy`, so any
spawn would be counted). No spawn appears in `load_cases`, `corpus_problems`, or the
unmeasured-record builder. The predicate and grader agree.

## Bounded observations (not falsifying; no fix proposed)

1. **Blank or non-string names are outside the duplicate guard.** `corpus_problems` only
   counts entries whose `name` is a non-blank string (measure.py 352–355). Such entries
   cannot trigger `duplicate case names` and do not count toward the 16 minimum. They are
   measured as `case-NN`. `ValidBoundaries.json` has no such entries, and the matrix
   generator always supplies string names, so this boundary is not reachable from the
   committed matrix. The claim "duplicate corpora rejected" holds only for string-named
   corpora.
2. **Distinctness is case-sensitive and strip-only.** `n00` and `N00` are distinct, and the
   fixture expects acceptance. Both the runner and the matrix guard agree, so the matrix is
   self-consistent. If the authoritative notion of duplicate were case-insensitive or
   Unicode-normalized, both sides and the fixture would be wrong together, and the matrix
   would not detect it. Contract-definition risk only; the other falsifiers cover the
   Unicode variants.
3. **Rejected grading checks a substring, not sole cause.** `check.py` requires
   `duplicate case names` to appear in `error`, but does not assert that the minimum
   reason is absent. For these fixtures the minimum is not triggered (exactly 16 distinct),
   so nothing is masked here.

## Verification gaps

- Nothing was executed; the claims above are from reading the cited lines.
- Runtime behavior of the classifier on the accepted template and the actual audit
  output were not observed. L1 owns the single post-wave run.
