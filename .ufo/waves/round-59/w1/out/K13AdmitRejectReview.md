# K13AdmitRejectReview — Round 59

## Axes
Operability; calibration (7, lowest assigned).

## Counterexample and evidence
The round-59 Gate does not yet establish a fresh non-author sampling result: `corpus/lessons/round-59.md` is absent (read returned “not found”), and `.ufo/waves/round-59/w1/out/` contains no lesson-gate record. The existing `corpus/lessons/round-58.md` is only author-side evidence. Its lines 14–16 label S517 and S518 ADMIT and describe their source checks; line 20's “Spot-check set” is a proposed set, not a recorded independent verdict. It explicitly carries forward no new reject; the S513 reject is said to be superseded/overturned, not a current reject result. Therefore the Gate's requirement for at least one non-author admit AND reject is unsubstantiated by available records.

Pending decisions: **S517** (independent re-open/quote check), **S518** (independent re-open/quote and S512 search), and **S513** (whether the prior reject is reopened/retained or overturned for the scoped claim). No external S517/S518 spot-check is recorded; no discernment progress is claimed.

Commands/output/evidence: `read .../corpus/lessons/round-59.md` → not found; `glob .../corpus/lessons` → includes round-58 and prior lessons, no round-59; `read .../corpus/lessons/round-58.md` → lines 14–20 describe author-side admissions and a proposed spot-check set, not independent outcomes. No counter command was run; this review does not represent it as passed.

## Impact and smallest safe correction
Impacts calibration through unsupported evidence for the non-author sampling predicate; operability insofar as the Gate cannot currently be used to distinguish independent decisions from author assertions. Smallest safe correction: record the independent S517, S518, and S513 decisions with reviewer identity/role, exact source/claim scope, evidence checked, and explicit ADMIT/REJECT outcomes. Until a non-author reject is actually recorded alongside an admit, do not treat this Gate criterion as met. Frozen claims/controls remain untouched.

No installs or updates.