# K12NoTrade — Round 59 claim falsification

Axes: **operability, calibration**. This is a falsification review, not admission or a score change.

## Counterexample / evidence

The frozen C2 clause requires a real outside-closure spot-check record for both S517 and S518 and says missing current external verdict means the claim is not met (freeze.txt lines 12–15). The supplied context explicitly states that S517/S518 are not yet recorded and that no kama r58 closure row exists; latest committed closure is r57 `rejected-honest-stop`. Yet the recorded current-HEAD C2 run reports `met=True` with `maxN=57 manifest=rejected-honest-stop`, `rows=44 mismatches=0` (controls/c2-after-current-head.out lines 1–3). It therefore establishes agreement with the latest existing closure, not the required current external discernment/spot-check progress.

The baseline counter did fail as required: recorded `c2-base.out` says `met=False`, three mismatches (typed_count, pinned_fleet_revision, count_command). But the successful measured run cannot satisfy the frozen positive requirement while its named S517/S518 records are absent. A genuine counter pass over existing data is not evidence that absent outside observations exist.

C1 recorded candidate output reports genuine 1/1, benign 3/3, no-op controls rejected 16/16, zero errors, `met=True` (controls/c1-candidate-final.out lines 1–23). I found no contrary C1 evidence in these artifacts; this does not excuse the C2 defect or substitute for independent re-execution.

## Verdict

**Do not admit the combined claim.** Attacked claim/clause: frozen C2 calibration sentence and kill rule (freeze.txt lines 13–15), specifically its required real S517/S518 spot-checks and current external verdict. Operability C1 evidence is consistent with its frozen predicate but cannot offset calibration harm. No verdict on unrun checks; I did not run either counter.

## Smallest safe correction

Keep the frozen predicate unchanged. Obtain and commit source-checked S517 and S518 outside-closure admit/reject spot-check records plus the matching current fleet closure entry, then rerun the already frozen C2 counter against the specified lane tip and explicit fleet HEAD. Until those prerequisites exist, report calibration unmet and no discernment progress; do not infer success from r57.

Commands executed for evidence: `pwd; find /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-59 -type f -printf '%p\\n'` (exit 0; enumerated artifacts). No counter command run. No tools installed.