# C01PatternScan — sibling pattern fit

## Finding

**No exact sibling pattern found; conditional fit via synthesis.** The closest reusable pattern is kotodama's versioned frozen-run package, but its existing manifest pins artifacts and verdicts rather than deriving a battery roster and comparing it to a preregistered roster. Do not replace C2's semantic comparison with hashes or broaden the frozen claim mid-round.

## Evidence and pointers

- Current C2 contract: `kama-shokunin/.ufo/waves/round-56/preregistration.json:18-26,29-35` defines exact equality of the AST-parsed battery `ROSTER` and prereg roster (names, designation, expected outcome), with one kill and two controls. The same file explicitly limits C2 to roster fidelity, not mutant quality beyond the C1 control.
- Current implementation: `kama-shokunin/tools/round56-prereg-check.py:34-45,47-71` reads preregistration and battery as committed blobs at `--tip`, AST-parses `ROSTER` with `ast.literal_eval`, compares exact Python values, and fails missing files. It also computes `kills`/`controls` from preregistration after equality. This is the direct roster-to-battery mechanism and is already frozen; leave it untouched.
- **Closest sibling, partial fit:** `kotodama-shokunin/tools/gates/frozen/<gate>/<baseline>/expected.json` plus `freeze.txt` records schema/version, revision, gate-script digest, input digests, expected exit/findings, and stdout digest. Example: `kotodama-shokunin/tools/gates/frozen/handoff-packet-check/r18-post/expected.json` and `freeze.txt`; the documented round-9 tamper drill reports digest failure even though the gate still emitted the same finding set. This is useful for byte identity and verdict reproducibility, not itself roster correspondence.
- **Second partial fit:** `kaidoku-shokunin/tools/round-43/c2-controls-r43.py:7-31` describes copying control tables byte-exact from a prior frozen round and checking SHA-256, while computing the score against a frozen dev arm and reference receipt. This prevents rebuilding controls from a later live state, but is domain-specific and does not parse/compare a roster.
- **Different contract, not a fit:** `kake-shokunin/.ufo/waves/round-21/measure.mjs:4-36,51-90` hard-codes expected population paths, reports found-vs-expected counts and per-file omissions, and supports committed-revision reads. It is a population census, not exact semantic roster matching.
- **Different contract, not a fit:** `mado-shokunin/quality/check-counter-discrimination.py:7-21,33-51` scores accept/reject controls and treats crashes/no verdict as errors. This is a counter-quality/discrimination battery, not a roster freeze; importing it into C2 would change the claim's scope.

## Affected axes

- **Calibration:** A future, separately preregistered check could strengthen the evidence chain by combining the existing exact semantic roster equality with a kotodama-style versioned manifest pinning the committed checker, battery, prereg bytes, and observed receipt/verdict. This would make substitutions or post-freeze drift visible without relying on report prose.
- **Operability:** No effect intended; keep C1's live-child `LD_AUDIT` probe, targets, and counter unchanged. The manifest idea is orthogonal, but it must not add runtime work to C1 or be presented as evidence that the endpoint is healthy.

## One bounded proposal

For a later round only, adopt a small frozen-run envelope around C2 evidence: record the exact source revision and SHA-256 of the checker, battery, and preregistration, plus the checker command, exit, and stdout digest. Retain the current AST-based exact roster comparison as the grade. Run a tamper control showing a changed roster or changed pinned input is rejected; keep output sorted/canonical if a parsed roster digest is recorded. This synthesizes kotodama's input+tool+verdict pins with kama's semantic AST extraction, rather than treating a whole-file digest as proof of correct correspondence.

**Fit/no-fit:** kotodama is a good *supporting provenance pattern*, not a direct drop-in; kaidoku is a supporting immutable-control pattern; kake and mado are no-fit for the correspondence predicate itself. The current C2 implementation remains the appropriate direct mechanism for this frozen wave.

## Risks and contradictions

- A byte hash proves identity, not that a roster matches the preregistration; hashing alone would regress calibration relative to the current semantic check.
- A manifest that pins only the checker/battery but not the prereg blob, commit identity, or command/output could preserve an incomplete chain. Conversely, expanding C2 to evaluate all 64 seat outcomes would exceed the explicitly frozen C2 scope and risk conflating calibration with runtime operability.
- Sibling mechanisms freeze different objects (population, controls, inputs/verdicts); there is no evidence they are interchangeable without adaptation.
- **Frozen-score tension:** the wave declares C2 calibration 7→7 and its roster predicate/kill rule are frozen. The proposed envelope is a future measurement improvement, not grounds to alter this round's predicate, counter, expected result, or score. The declared L1 is a frozen-topology planner seat; this proposal does not add a planner role.

## Verification

Static source/pointer inspection only. No sibling tools, tests, builds, counter runs, or mutations were executed. No tool was installed. No lane production files were changed; this report is the only deliverable.