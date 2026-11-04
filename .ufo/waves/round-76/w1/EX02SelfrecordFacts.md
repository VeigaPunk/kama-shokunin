# EX02 — C2 self-record facts

Axes: calibration correctness, value-binding sensitivity, historical-byte preservation.

## Files changed

- `tools/round76-selfrecord-facts.py`
- `.ufo/waves/round-76/w1/EX02SelfrecordFacts/before.out`
- `.ufo/waves/round-76/w1/EX02SelfrecordFacts/selftest.out`
- `.ufo/waves/round-76/w1/EX02SelfrecordFacts/correction-template.txt`
- This report.

## Behavior

The module carries the frozen C2 predicate verbatim, grades ten checks over eight facts, and reads committed Git blobs only. Digest/line pairs use the SCORECARD population revision; source rows use the census pattern; knowledge entries retain the actual `engine-sides`/`processes` filter. Mistakes include both lesson sections. Newest closure selection imports the committed round-69 implementation unchanged, with since-round 63.

Work-tip derivation reads the LOG freeze, walks the first-parent commit graph and excludes the inherited round-72 record paths. It seals round 75 at the first introduction of its outside closure, preventing round-76 work from changing the historical answer. PROVINCE.md remains non-record for this derivation. This boundary is an implementation interpretation: the plan gives no explicit historical upper-bound algorithm beyond the round-75 fact population. The worktip-graph fixture forks before closure publication and inserts later real work, rather than hardcoding c9ab73d8.

Corrections use dated `### Correction (YYYY-MM-DD) — <id>` blocks, after their original same-file declaration, with `Supersedes`, `Revision`, `Corrected`, and (for tally) `Receipt` fields. The frozen plan declares semantic correction conditions, not a literal block grammar. Templates supply four exact accepted-value candidates and one honest unbacked tally disclosure. A wrong correction stays a finding. A tally correction may explicitly state `historical-unbacked; PRE_REPORT_SELFTEST pass=N fail=0`, but requires that exact actual tally in its named committed wave receipt. Merely stating `unbacked` never turns the claim green.

The selftest implements red-at-base, correction-wrong-value, correction-value-bound, worktip-graph, and cheat-zeros. Fixture repositories are raw Git object stores written within explicit --work; no Git mutation command is issued. The fixture subtree is removed in finally.

## Retained evidence

Read the complete frozen plan and all four c2 base receipts before implementation.

Executed the required base counting measurement:

`python3 tools/round76-selfrecord-facts.py --repo <absolute-lane> --rev b06cc612711560c53eef3ec21484c6963601262f`

Retained byte output and exit in `EX02SelfrecordFacts/before.out`:

`SELFRECORD_FACTS claims=8 mismatches=5 unbacked=1 corrected=0`

Exit 1. Findings: province-digest, log-worktip, log-mistakes, log-tally, closure-pointer. No additional build/lint/test/formatter run is claimed.

## Blockers and parent checks

1. The higher-priority fleet rule reserves editing-wave selftest execution for the parent. `selftest.out` explicitly says NOT_RUN; it is not a fabricated passing receipt. Parent must execute the recorded selftest command and replace it with actual output and status.
2. No committed round-75 gate tally backs the asserted 18/0 (confirmed by the frozen measurement); no round-76 gate-selftest receipt candidate was available in the wave tree. L1 must retain an actual gate-selftest receipt, commit it, then supply its observed tally, revision and path in the log-tally correction. The fifth template intentionally remains unbacked rather than inventing a receipt or promising clean=0. SCR03Corrections and Main were notified.
3. Parent should run the frozen counting command after committing the appended corrections, and verify the named selftest arms. `--rev` permits base measurement without touching worktree or branch state.

No self-record, frozen plan/module, external substrate, PATH directory or global configuration was edited. No tools installed or upgraded. No scratch subtree was created during this leaf run; runtime fixture cleanup is implemented. LSP was unavailable in the mounted tool inventory, so no symbol query/refactor was claimed.

## Self-evaluation

Accuracy 4/5: base output matches the five independent frozen findings; selftest behavior is not yet exercised. Completeness 3/5: implementation and templates are present, but the parent-owned selftest run and real gate receipt are missing prerequisites, explicitly not claimed complete. Clarity 4/5: exact commands, grammar and missing receipt are documented. Actionability 4/5: parent has the command and four ready blocks; tally requires observed committed evidence. Conciseness 4/5: report retains the historical-boundary interpretation and verification conflict needed for review. Overall 3.8/5. Highest-impact actions: run parent selftest; bind an actual gate tally; review the closure-sealed worktip boundary against the frozen wording. Would the user agree: only if these outstanding prerequisites remain explicit rather than being represented as a passing wave.
