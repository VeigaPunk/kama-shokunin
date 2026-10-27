# K04OverclaimScope — Round 58 wording scope

Axes: operability (C1) and calibration (C2). Review is limited to whether claims exceed their frozen counter predicates; it does not dispute the counters' outputs.

## Findings and exact narrower wording

1. **Freeze C1 sentence, lines 6–9:** “battery-roster checker” plus “accepts the genuine … battery” and “rejects … no-op variants” may be read as evidence that the checker binds real execution or proves the battery's behavior. The counter actually evaluates the battery under its harness/profile hook against one genuine fixture, three rewrites, and the 11 enumerated variants. The roster-literal parenthetical and explicit finite list bound the no-op population; they do not establish general resistance to unlisted no-ops or authentic production execution.
   **Suggested report wording:** “Under the counter's hermetic `__main__`/profile-hook harness, the checker accepted the genuine round-56 battery and 3/3 specified behavior-preserving rewrites, rejected 11/11 enumerated no-op variants with the roster literal intact, and recorded 0 evaluation errors. This result is limited to these fixtures and harness; it does not prove general no-op resistance or production execution.”

2. **Freeze C2 sentence, lines 19–22:** “reports 0 mismatches” is appropriately tied to the named tool; the remainder claims only pointer, round-number and verdict-token agreement against a named manifest revision. No overclaim is apparent if the report retains that exact boundary. Avoid upgrading this to “calibration is correct,” “outside review is validated,” or independent judgment: the counter verifies string/pointer consistency, not the review's substantive quality or provenance beyond the specified manifest token.
   **Suggested report wording:** “At the measured tip, `round42-selfdesc-reconcile.py` reported 0 mismatches, and the counter found the calibration row's latest-closure path, repeated round number and verdict token consistent with its specified highest-numbered lesson and pinned fleet manifest. This is a bounded textual-consistency check, not validation of the closure's judgment.”

3. **SCORECARD edit:** the visible current SCORECARD has round 57 as latest and no round-58 results section; its planned round-58 text is prospective, not a result claim. Thus there is no observed round-58 SCORECARD result sentence to flag. Round 57's C1 explicitly says it does not assert runtime effects were executed; preserve that qualification. Do not report that a round-58 SCORECARD sentence overclaims absent evidence of such an edit.

## Evidence / checks

- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show e4891d8a4c9c70e97124980c2ec9aee5762a7f0a:.ufo/waves/round-58/controls/freeze.txt` — exit 0; confirms exact frozen C1/C2 wording and predicates above.
- Read `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md` lines 3149–3163 — round 57 outcomes and round-58 plan; no round-58 outcome section present in the visible current file.
- Finding attacks overbroad interpretation of C1 (operability and calibration evidence boundary) and potential overstatement of C2 (calibration); C2 frozen sentence itself is bounded. Limits outside frozen variants remain limits, not grounds to change the predicate.
