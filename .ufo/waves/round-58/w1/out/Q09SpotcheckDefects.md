# Round 58 routed defects spot-check

Axes: operability (C1), calibration (C2). Evidence is the frozen claim and build-tip blobs, not a final measured closure.

1. Execution-bound C1 / dead-code and unused-function no-ops — ADDRESSED within the frozen battery. `tools/round58-c1-counter.py` constructs fixtures from committed variants and runs the candidate checker as a subprocess against each committed fixture (`verdict`, `main`); `tools/round58-c1-counter.py` lines 20-25 enumerate N02 if-false and N03 unused-function, and lines 81-106 score all named cases including genuine/benign controls. Freeze requires 11/11 no-op rejection and errors=0. This directly routes R57 defect 1; it is evidence of test coverage and measurement design, not a measured pass from this seat.

2. Round-56 verdict-token misstatement in the calibration pointer — ADDRESSED by predicate. `tools/round58-c2-counter.py` lines 18-27 defines claim/maxN/manifest verdict matching and counts mismatches; lines 68-82 reads the specified fleet manifest revision and checks token equality. Frozen C2 explicitly requires the highest round, repeated including-round, and MANIFEST verdict token. Does not establish pointer correctness until measured at the accepted tip.

3. S513 disagreement / quality criterion and independent admit+reject sample — LEFT. C1/C2 are counter predicates for battery behavior and scorecard calibration; neither addresses S513, `corpus/QUALITY.md`, or independent non-author judgment. No claim in freeze covers it.

4. Round-57 erratum inconsistent quality figures and report tip mismatch — LEFT. Frozen claims only measure C1 battery no-op behavior and C2 reconciliation/pointer consistency; they do not test erratum arithmetic or report-tip alignment.

5. Untracked scratch paths / inherited audit exit and MISSION-config axis conflict — LEFT. The frozen predicates inspect neither workspace hygiene nor audit/config authority. No claim or counter evidence shows these were resolved.

Confidence: high for scope mapping (freeze predicate and counter source); no measured round-58 command was run here. Remaining gap: measured closure evidence and any integration corrections may change dispositions; findings describe only frozen claims/build tip.
