Advisory for round 49 (NOT applied; the preregistration, counters and controls are frozen).
Round-48 seat X1Stable, C1 evidence: graded/ungraded are tip-indexed under v3's window-maximum
eligibility, and `restored_max` can fall as the tip advances. Two pieces of text/code that would
make the frozen artifacts state exactly what they enforce.

1. `preregistration.json` C1 `limits` — append one sentence (current text ends
   "... The threshold stays 20: sub-threshold deletions are not graded."):

   "Under v3's region carve-out the per-event graded/ungraded split is not a property of the
    event but of the tip: an exempt title is eligible when the maximum of its line count over
    the window ending at <to> reaches the parent's count, so any later commit that regrows the
    section (even with new text) moves those deleted lines from graded to ungraded, and a
    `restored` event can become `ungraded` with exit 0 (selftest t_exempt_gutted_then_regrown).
    graded can only shrink and ungraded can only grow as the tip advances with a fixed contract
    file, so a claim's graded/ungraded numbers are only re-verifiable at its own tip, and
    `restored_max` is not monotone in the tip once eligibility can change (fixture case B:
    24 -> 10). Reading the contract from <to> (the default) instead of a fixed file makes the
    split depend on the contract revision as well."

2. `tools/round48-append-audit-v3-check.py`, stable leg (lines 747-758) — the equality over
   (`deleted`, `graded`, `ungraded`, `restored_max`, `restored_best`) is content-sensitive:
   a correct v3 reports "changed" when the lane regrows an exempt section between
   STABLE_BASE (33e0058) and the tip, and stable=0 then reads as a tool defect. Cheapest
   non-vacuous hardening that keeps the leg strict for the *tool* while separating lane
   content: keep the equality for `deleted`/`graded` and require instead
   (`ungraded` at tip >= `ungraded` at base AND `graded` at tip <= `graded` at base) —
   i.e. compare the direction the definition guarantees — and, when the strict equality
   fails, print the tip commit that made the section eligible so the failure is attributable
   to lane content rather than to the tool. (Either way the leg must not be relaxed to
   "any event exists at the base": V1Ctr closed that vacuity.)

   Note: the counter is frozen; this is round-49 material, and changing it is a calibration
   move (it would make the leg's semantics match v3's definition), not a fix to a defect in
   the measured claim.
