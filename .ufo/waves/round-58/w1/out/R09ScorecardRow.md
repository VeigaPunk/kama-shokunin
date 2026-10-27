# R09ScorecardRow — calibration review

Axes: calibration; operability (scope check). Reviewed committed build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`, frozen C2 and the first `## Axes` calibration row.

## Finding

No new false statement found in the calibration row. The row's 44 spotcheck figure, capability and instrument selftests, reconcile-counter pointers, and latest-outside-closure pointer all re-derive at the build tip. C2 resolves the pointer to round 57 and token `rejected-honest-stop`, matching highest lesson N=57 and the frozen fleet MANIFEST revision. The counter reports zero mismatches and `met=True`. This conclusion is bounded to the row's stated facts and frozen predicate; it is not a broader truth/relevance endorsement of the calibration score.

## Verification

All commands run with `TMPDIR=/fast/scratch/hyaku/kama-r58/R09ScorecardRow` and an isolated shared clone of the lane at the build tip; scratch removed before report.

- `python3 tools/round58-c2-counter.py --repo "$S/repo" --tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a --manifest-rev 941acf70583a2b3a1d33460b31967e0efd291f3e` → `claim=N=57 token=rejected-honest-stop maxN=57 manifest=rejected-honest-stop; r42=0 missing=0 stale=0 verdict=0 including=0 mismatches=0 met=True`; exit 0.
- `python3 tools/capability-repertoire-audit.py --selftest` → `CAP_SELFTEST pass=2 fail=0`; exit 0.
- `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `44`; exit 0.
- `python3 tools/instrument-agreement.py --selftest` → four expected case results; `IA_SELFTEST pass=4 fail=0`; exit 0.
- `python3 tools/round41-scorecard-reconcile.py` → `axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True`; exit 0.
- `python3 tools/round42-selfdesc-reconcile.py` → `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=57 met=True`; exit 0.

The counter also printed `tip=e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`. No actionable finding remains in scope.