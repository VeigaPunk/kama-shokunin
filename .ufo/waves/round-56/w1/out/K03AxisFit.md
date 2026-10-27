# K03AxisFit — distinct-axis review

**Finding:** The frozen claims target distinct axes: C1 is **operability**; C2 is **calibration**. I found no basis to collapse both into calibration. This is a scoped axis-fit judgment, not admission or a score change.

## Counterexample and evidence

The strongest counterexample to the separation is that both claims are implemented as pass/fail scripts with expected outcomes: C1 tests `env_leg` output against an `--expect` value, and C2 compares a battery roster to preregistration. Both therefore exercise measurement machinery. However, implementation form alone does not identify the axis. `AXES.md` defines operability as runnable artifacts whose commands produce stated outcomes, and calibration as self-assessment quality—gaps honestly named, confidence graded, overreach caught. It also says claims must name distinct axes.

C1's target is functional behavior of the lane's audit counter: it adds `LD_AUDIT` to `BAD_ENV` and checks that a live child carrying that variable is reported as problematic. The frozen baseline and measured receipts show the intended contrast: old counter `ld_audit=missed`, exit 0; round-56 counter `ld_audit=detected`, exit 0; deletion mutant `ld_audit=missed` (the battery expects that mutant outcome). Digests observed for `round56-replay-code-audit.py` and `round56-prereg-check.py` match the frozen hashes. The baseline counter's `BAD_ENV` omits `LD_AUDIT`; the frozen counter includes it. That is an executable behavior improvement, hence an operability fit—not a judgment about calibration of the lane's own account.

C2 targets consistency of the lane's declared measurement roster: its checker reads the committed battery AST and preregistration and requires exact roster equality plus one kill and two controls. The receipts show the intended red base (`present=0 roster_match=0 kills=0 controls=0 met=False`, exit 1) and green freeze (`present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0). This is calibration-shaped because it checks that the lane's account of its experiment matches committed measurement material, rather than improving the counter's runtime behavior.

## Caveat / smallest safe correction

C1 is narrower than general local-model-serving operability: `round56-env-leg-test.py` launches `sleep`, and the preregistration explicitly limits the claim to `env_leg`'s variable-name classifier, not successful foreign audit-DSO injection or a full replay audit refresh. Preserve that boundary in any verdict; do not inflate this to endpoint health or end-to-end serving. No axis reassignment is indicated.

C2's exact-equality test cannot detect a coordinated falsehood if preregistration and battery are both changed consistently (or a semantically defective roster whose fields still satisfy its narrow structural test). That is a limitation/tradeoff of the frozen roster-fidelity predicate, not evidence that C1 is calibration. Smallest safe correction for reporting is to state C2 as *roster fidelity only*, consistent with preregistration's explicit limitation, and avoid claiming it validates the substantive quality of the experiment. Changing its predicate now would violate the freeze.

**Axes impacted:** operability (C1; bounded behavior of the environment classifier), calibration (C2; bounded roster self-description fidelity). No evidence here supports a numeric score increase, endpoint-health improvement, or claim beyond the recorded controls.