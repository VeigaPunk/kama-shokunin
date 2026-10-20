# PlannerWalk — Kama round 11 C1 bounded data-walk

## Scope and axes

Read-only inspection of one legacy file (`corpus/knowledge/served-model-identity.md`), its frozen baseline record, the current axis binding, and the existing provenance measurement design. No implementation/corpus edits, builds, tests, linters, formatters, check commands, or runtime/network contact. No tool installed or upgraded; install record: none.

Current roster authority is `../shokunin.conf:52`: Kama is assigned **operability + calibration**, not the historical `MISSION.md` example. `.ufo/waves/round-11/claims.json:4-13` identifies calibration as the lowest live assigned axis (7; operability 8), assigns C1 to calibration, and explicitly keeps the score unchanged because a field-count denominator is not a calibration-quality denominator. The provenance change therefore supports an observable calibration artifact but does not itself establish a score delta or runtime freshness.

## Evidence chain and smallest measurement

- `.ufo/waves/round-11/legacy-baseline.json:1-82` is the fixed nine-file denominator: each entry records `source`, `verified-at`, and `recheck` as missing (27 required fields total). The selected `corpus/knowledge/served-model-identity.md` entry at lines 65-72 pins 1,221 original bytes with SHA-256 `294e1192181837cfbc31480c07c005cc012cbd7de7852c6ca58bb1d36d4b630b` and all three fields missing.
- The selected file's original lines 1-37 are historical `/health`, `/props`, `/slots`, and `/metrics` command/output text. Its appended supplement at lines 39-44 now states the source is the retained historical sample (line 40), that the 2026-10-20 review was metadata/history-only with no endpoint contact (line 41), and that re-probing requires later authorization (line 42). Thus the smallest per-file presence delta is **0/3 → 3/3** for this one sample; this is a static reading of the baseline and current lines, not an executed counter or proof for the other eight files.
- The corpus contract confirms the temporal boundary: `corpus/README.md:9-14` says entries are dated records of what was observed then, not proof an endpoint serves today. The sample's explicit no-live-revalidation wording is consistent with that rule.
- `measure.py:7-13,38-58,215-324` defines the intended aggregate: enumerate baseline entries, check required fields in the appended region and SHA-256 of each original byte prefix, and report counts. It explicitly does not certify endpoint health/identity/freshness. The claimed whole-set target in `claims.json:10-13` is **27 missing fields → 0**, with prefixes preserved; this bounded inspection confirms only the selected file's three fields are now present. I did not verify the current file's first 1,221 bytes against the baseline, nor the other eight files, so global zero-missing and post-append prefix preservation remain unconfirmed by this report.

**Smallest falsifying control (proposed, not run):** on an isolated copy of the selected file/tree, remove only its appended column-zero `recheck:` line. The gate should report `missing_fields=1`, `prefix_violations=0`, and exit 1. `measure.py:445-450` already encodes a missing-field case with the expected failure; `measure.py:460-468` separately encodes a one-byte original-prefix mutation control. These are source-level expected outcomes, not observed runs here.

## Findings, severity, and smallest repair

1. **Medium — scoped evidence cannot establish the global C1 after-state.** The baseline establishes the fixed 9 × 3 denominator, while this walk observes only one current file. It would be an overclaim to conclude `27 → 0` or prefix preservation for all nine from this sample. Smallest repair for the parent acceptance record: run the existing baseline-driven measurement once across all nine and retain `legacy_files`, `missing_fields`, and `prefix_violations`; include the one-field scratch negative control above. No global verdict is made here.
2. **No defect observed in the selected metadata's temporal framing.** The actual review date is distinguished from the old 2026-09-28 sample date; the text expressly disclaims live revalidation and bounds future recheck to authorization (`served-model-identity.md:40-42`). Keep this distinction; do not relabel C1 as freshness or infer current serving state.
3. **No score correction proposed.** Current axes and the declared lowest-axis score are sourced as above. The existing `SCORECARD.md:209-213` also marks calibration unchanged at 7; retain that value absent an objective calibration denominator.

## Confidence and limits

High confidence in the baseline record, current visible trio, axis binding, and documented measurement semantics. No independent confirmation of all-nine after-count or current prefix hashes; no endpoint freshness conclusion. The task is not a public-source-opening role, so no public URL was opened or quoted. No checks were run.