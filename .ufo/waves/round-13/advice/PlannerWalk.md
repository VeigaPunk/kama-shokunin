# Round 13 — bounded KQ15 planning walk

## Axis and authority

`SCORECARD.md` §Round 12 (lines 285–309) records the assigned axes as operability + calibration, with calibration 7 below operability 8; it keeps calibration at 7 → 7 and disclaims conversion of this evidence repair into a universal mastery score, new serving surface, runtime validation, or coverage expansion (299–304). Its planned outside non-author sampling of round-12 decisions is now represented by the outside spot-check; its future serving-domain direction is not a claim for this bounded correction. Stay on calibration C1 only. Do not invent or report an axis increase.

## Two routed propositions and evidence

1. **Finding IDs are distinct; exit classes are not.** `corpus/QUALITY.md:49` says mismatch, snapshot tamper, and unavailable source have “distinct nonzero exits.” The round-12 implementation's module contract maps `source_mismatch` to exit 1 and `snapshot_tampered` / `source_unavailable` to exit 2 (`.ufo/waves/round-12/fidelity.py:24–25, 55–63, 317–319`); those are three stable, distinct finding IDs with only two nonzero exit classes. The committed receipt records the same mapping: `acceptance.json` before = `1/source_mismatch`, pin-only tamper = `2/snapshot_tampered`, unavailable source = `2/source_unavailable` (outer receipt is an observation, not a new run; corroborated by verifier spot-check lines 81–93).
2. **Capture and comparison use different commands.** KQ15 currently names `git show <pinned-commit>:<source-path>` as the comparator. Round-12's `fidelity.py:271–279` retrieves comparison bytes with `git cat-file blob`; `reproduce.py:79–80` independently obtains the source blob with `cat-file blob`. The round-12 fidelity note says the snapshot was generated from `git show` raw stdout while the gate compares against `git cat-file blob` raw stdout (`.ufo/waves/round-12/advice/Fidelity.md:26–40`); the lesson likewise says capture with `git show` and independent comparison with `git cat-file blob` (`corpus/lessons/round-12.md:13–17`). Round-12 source docs and receipts are historical evidence, not fresh execution here.

The outside D1 explicitly routes an appended KQ15 wording correction, says not to rewrite historical criterion/receipt bytes or change correct code to fit the wording, and separately routes quality attribution to the D4 knowledge interpretation (`corpus/lessons/round-12-verifier-spotcheck.md:147–149`).

## Minimum correction and limits

Append **KQ16** superseding only KQ15's two inaccurate formulations; preserve the rest of KQ15 and its history. Preserve these exact audit literals:

- `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`
- `capture: git show; comparison: git cat-file blob`

Any probe-side literal assertions are bounded documentation-conformance checks, not proof of exit semantics, command behavior, or overall criterion quality. Inspect the round-12 source and retained receipt as the separate evidence chain; do not re-execute `fidelity.py` or its selftest. The fixed before/after denominator is the two D1 wording defects (2 → 0), not all of KQ15, all criteria, or the corpus. A one-criterion, one-source-path correction risks overfitting to this case: it does not establish generalized review accuracy, other-source-path behavior, broader Git command semantics, runtime/serving operability, or capability acquisition. No gate/build/test/linter/formatter/smoke check was run for this walk.

Quality attribution, if the round discusses it, must credit the stronger existing `served-identity-crosswalk` interpretation identified by D4—explicit source wording vs inference and lane-registry supersession vs upstream supersession, with the failure cases and MODEL_OK restatement—not D1 gate/snapshot machinery alone (`round-12-verifier-spotcheck.md:122`; `round-12.md:63–66`).

No LSP device/server route was exposed in this session; this note relies on exact source, criterion, lesson, and retained-receipt reads, not grep output as semantic proof.
