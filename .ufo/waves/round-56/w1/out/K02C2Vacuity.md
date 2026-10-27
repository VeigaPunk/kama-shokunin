# K02C2Vacuity — Round 56 falsification

Axes: operability; calibration.

## Probes and evidence

Used frozen checker `tools/round56-prereg-check.py`; SHA-256 observed `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`, matching preregistration.

1. **Do-nothing/base-tip control:**
   ```
   python3 tools/round56-prereg-check.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e10b6d39af450e8d652be9ac2986768b531fe13f --out <scratch>/probeA-base.out
   ```
   Output: `tip=e10b6d39af450e8d652be9ac2986768b531fe13f; present=0 roster_match=0 kills=0 controls=0 met=False`; exit 1. Do-nothing/base does **not** reach target.

2. **Freeze positive control:** same command at tip `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`. Output: `present=1 roster_match=1 kills=1 controls=2 met=True`; exit 0.

3. **Mismatched roster / one-field designation flip:** Created a scratch-only git fixture with the committed freeze battery and preregistration, verified fixture root before commits. Changed only battery ROSTER `m-drop-ldaudit.designation` from `kill` to `control`; checker reported `present=1 roster_match=0 kills=1 controls=2 met=False`; exit 1. Mismatch does **not** reach target; the frozen one-field designation kill is effective.

4. **Mismatched expected-outcome flip:** Changed only battery entry `m-drop-ldaudit.expected` from `missed` to `detected`; output `present=1 roster_match=0 kills=1 controls=2 met=False`; exit 1.

5. **Boundary / limitation probe (not the required mismatch):** Changed that `expected` value identically in both fixture battery and fixture preregistration. Output `present=1 roster_match=1 kills=1 controls=2 met=True`; exit 0. This is consistent with C2's stated contract (fidelity of the committed battery to preregistration, not semantic validation of the frozen outcome); it is not evidence that a mismatched roster passes. If semantic correctness of expected outcomes is desired in a future claim, the independent authority must be fixed before scoring and validated against an execution receipt. Do not retrofit that broader claim into this frozen C2.

All probe receipts are alongside this report: `probeA-base.out`, `probeA-freeze.out`, `probeB0-fixture-green.out`, `probeB1-desig.out`, `probeB2-expect.out`, `probeB3-sync.out`. Existing L1 receipts also observed: base C1 `ld_audit=missed`, exit 0; freeze C1 `ld_audit=detected`, exit 0; mutant `ld_audit=missed`, exit 0; base C2 `present=0`, `met=False`, exit 1; freeze C2 `present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0.

## Defect assessment

No observed defect against the assigned vacuity checks: the absent-file/base control and both single-file roster mismatches return nonzero and `met=False`; the frozen checker reaches its target only with the matching freeze roster. Boundary: synchronized changes to both sources are outside C2's specified fidelity predicate. No tools installed. Scratch `/fast/scratch/hyaku/kama-r56/K02C2Vacuity/` removed before report.