# Promisor mutant anchors at fa3b62ae (read-only check)

Command, run in my clone at fa3b62ae with PYTHONDONTWRITEBYTECODE=1:

    python3 tests/report-audit/promisor-mutants.py --anchors tools/report-landing-audit.py --json

Exit 0. Raw JSON: /fast/scratch/hyaku/kama-r25a2w2/ReviewerRoutedDefects/promisor-anchors-tip.json (scratch).

| mutant | applicable matches | alternatives | compiles | note |
|---|---|---|---|---|
| PM01-blanket-metadata-refusal | 1 | 2 | true | |
| PM02-blanket-unknown-refusal | 1 | 1 | true | |
| PM03-skip-required-object-availability | 1 | 2 | true | |
| PM04-accept-unavailable-referenced-object | 2 | 2 | true | |
| PM05-ignore-second-repo | 2 | 2 | true | |
| PM06-swallow-actual-read-error | 1 | 1 | true | |
| PM07-full-all-missing-gate | 1 | 3 | true | |
| PM08-no-lazy-fetch-review-only | 0 | 0 | none | review-only, skipped (manual note, no source assertion) |
| PM09-peel-bare-full-hash-lookup | 1 | 1 | true | |
| PM10-ignore-opaque-nonleaf-missing | 1 | 1 | true | |
| PM11-any-hole-refusal | 1 | 1 | true | |

Reading: every executable promisor mutant has at least one applicable match at the tip, so no executable promisor
anchor is stale. C1 (the isolation instrument) does not measure this instrument; this check does, at fa3b62ae only.
PM08 has no source assertion by design, so "applicable 0" is expected there.
