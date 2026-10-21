VERDICT: confirm - Stryker documents runtime errors as non-verdict errors excluded from its mutation score.

## Observed source
- Live page: https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/ (fetched 2026-10-21; HTTP 200, 27,068 bytes; `curl` exit 0).
- Source file: `stryker-mutator/mutation-testing-elements/docs/mutant-states-and-metrics.md`, `master`. Latest file-touching commit: `a56f265c77c1cc811b10f0bae73ec1b0083d52a9`, authored 2023-04-14T11:40:53Z. Retrieved Markdown agrees with the live page.
- Exact definitions in §Mutant states:
  - **Killed:** “When at least one test failed while this mutant was active, the mutant is killed.”
  - **Runtime error:** “The running of the tests resulted in an error (rather than a failed test).” Stryker gives runner failure (including `OutOfMemoryError`) and, for dynamic languages, unparsable mutant code as examples.
  - **Survived:** all tests passed with the mutant active. **No coverage:** the mutant is not covered by tests and survives as a result.
  - **Timeout:** running tests with the mutant active timed out; Stryker counts it as detected. **Compile error:** the mutant caused a compile error.
  - **Ignored:** not tested because it is ignored; it does not count against the score but appears in reports. **Pending:** generated but not run, a temporary state.
- **Score treatment:** Runtime errors are not represented in the score. Stryker defines `valid = detected + undetected`, `invalid = runtime errors + compile errors`, and `mutation score = detected / valid * 100`; thus runtime errors are excluded from the denominator. Compile errors are likewise excluded; ignored and pending are not in `valid` either.

## Draft SOURCES row (tier applies only to this precedent scope)
| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 assigns | Stryker Mutation Testing Elements — https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/ | docs | A | Stryker's own mutant outcome taxonomy and mutation-score treatment; not a universal lane verdict contract | §Mutant states (Killed, Runtime error, Compile error), §Metrics (Valid, Invalid, Mutation score); `docs/mutant-states-and-metrics.md` @ `a56f265c77c1cc811b10f0bae73ec1b0083d52a9` (2023-04-14) | Stryker distinguishes a failed-test Killed verdict from Runtime error and excludes runtime errors from the mutation score. | queued | 2026-10-21 | 90d | — |

Located quote (14 words; §Mutant states → Runtime error; source revision/date above): “The running of the tests resulted in an error (rather than a failed test).”

## Evidence commands (all executed)
- `curl -sS -o /tmp/kama-r20-SrcStrykerStates/page.html -w 'http=%{http_code} bytes=%{size_download}\n' 'https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/'` — HTTP 200, 27,068 bytes; exit 0.
- `gh api 'repos/stryker-mutator/mutation-testing-elements/commits?path=docs/mutant-states-and-metrics.md&per_page=1' --jq '.[0] | [.sha, .commit.author.date, (.commit.message | split("\n")[0])] | @tsv'` — `a56f265c77c1cc811b10f0bae73ec1b0083d52a9`, `2023-04-14T11:40:53Z`; exit 0.
- `gh api repos/stryker-mutator/mutation-testing-elements/contents/docs/mutant-states-and-metrics.md --jq '.content' | base64 -d` — returned source Markdown; exit 0.
- No tool installed or updated.

[INFERENCE] This is precedent supporting the conceptual distinction between an observed failing-test verdict and a tool/runtime error; Stryker's taxonomy does not by itself establish the lane's verdict policy.