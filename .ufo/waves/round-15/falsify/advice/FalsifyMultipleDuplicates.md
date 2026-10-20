# FalsifyMultipleDuplicates: round-15 attack on tests/ollama-corpus-guard/MultipleDuplicates.json

Scope: static reading only. No gate, test, or runner execution. No tools installed or updated (no pacman, no uv, no binaries).

## Verdict

No fail finding against MultipleDuplicates.json or the runner duplicate predicate for the committed fixture. Two latent divergences are recorded as residual risk, neither reachable from any committed matrix file.

## Fixture checks (tests/ollama-corpus-guard/MultipleDuplicates.json)

| test | envelope | names | stripped distinct | duplicate present | expected_rejected |
|---|---|---|---|---|---|
| MultipleDuplicates_tail_n01_n03_n01_array | array | 19 (n00..n15, then n01, n03, n01) | 16 | yes (n01 x3, n03 x2 repeats) | true |
| MultipleDuplicates_tail_n01_n03_n01_object | object | 19 (same) | 16 | yes | true |
| MultipleDuplicates_valid_distinct16_array | array | 16 (n00..n15) | 16 | no | false |
| MultipleDuplicates_valid_distinct16_object | object | 16 (n00..n15) | 16 | no | false |

- Negatives: 16 stripped-distinct names meet MINIMUM_UNIQUE_CASES=16, so the minimum-corpus guard cannot fire and only the duplicate guard decides the outcome. This is the intended isolation.
- Valid controls: exactly 16 distinct, which is the boundary value and passes both guards.
- Envelope and boolean correspondence: each duplicate case is paired with expected_rejected true; each distinct case with false. Both envelopes (array and object) are covered for both polarities.
- Hygiene: the file is pure ASCII. Grep for non-ASCII bytes, leading or trailing padding inside quoted names, and internal padding returned no matches inside the names. Test ids are unique across the sibling matrix files.

## Runner predicate (.ufo/waves/round-14/measure.py)

- corpus_problems (lines 350-364) strips each declared name, counts the set, and appends "duplicate case names" when len(declared) != unique. For the negatives, declared=19 and unique=16, so the rejection fires. The unique=16 check does not fire because 16 is not below 16.
- run() (lines 367-425) calls corpus_problems before any spawn. The only subprocess.run is at line 240, inside measure_case, and measure_case is reached only from the elif tool_present branch after the corpus branch. Module import has no process-creation side effects (imports only; grep found subprocess used at 240 and 252 alone).
- On rejection, every record is unmeasured_record, so observed_exit is None and passed is False. The record count equals len(cases) = len(names), which matches check.py's null_exit_records == total requirement.
- The error string is "corpus: duplicate case names; ...", so the substring check in check.py grade (line 537) matches.
- load_cases accepts both a bare array and an object with a "cases" array, matching check.py's two envelopes.
- check.py load_matrix (lines 192-211) enforces the same 16-minimum and the expected-boolean correspondence, so a mislabeled fixture fails closed at load time rather than producing a false pass.

## Residual risks (latent, not triggered by committed fixtures)

1. Blank-name divergence. check.py counts stripped empty strings as distinct names (item.strip() with no non-empty filter), while the runner's corpus_problems excludes blank names from declared (name.strip() kept only when non-empty). Concrete hypothetical: names n00..n15 plus two "" entries, expected_rejected true. load_matrix accepts it (17 distinct, duplicate present). The runner does not reject it, since declared has 16 unique and no duplicate, so it measures 18 cases and grade fails the test. This is fail-closed (the harness reports a failure, it does not falsely pass), but the two definitions of "distinct stripped name" disagree. No committed fixture contains a blank name. Fixing it is out of scope for this round and is recorded only.
2. Fallback-name collision. case_name returns "case-NN" for blank or missing names, and the runner does not check those fallbacks against explicit names. An unnamed case at index 3 alongside an explicit "case-03" would not be flagged. Not reachable from the matrix, since check.py always writes the literal names entry into the cloned case name.

## Verification gaps

- The positive path requires the real classifier to measure the cloned template cleanly (passed == total, verdict 0). That is not established by this static read and was not executed, per instructions.
- The fail-closed behavior of residual risks 1 and 2 is inferred from source reading, not observed.
- Whitespace-variant fixtures in sibling files (PrependDuplicate "  n15  ", WhitespaceCollision " n04 ", TriplicateName " n08"/"n08 ") were noted in passing and are owned by other falsifiers; not analyzed here.

## Tooling record

None. No installs, updates, or pacman transactions were performed in this lane.
