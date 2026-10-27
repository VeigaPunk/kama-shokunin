# F27C2IndependentControls — C2
- W1 K01 do-nothing registry reproduced: 14/14 covered, 5 evaluated, `met=True`; controls rejected 35/35.
- Honest-shaped reference fixture: same score and same control counts; it is not independent truth validation.
- Predicate swap across two live rows: `met=True`; controls unchanged (tautology 1/1, flips 5/5, quotes 14/14, drops 14/14, tamper 1/1).
- Promote not-observable row to live: `met=True`, 6 evaluated; controls still reject.
- Demote live row to not-observable: `met=False` (4 live rows); threshold, not semantic binding, explains result.
- Rejection under perturbation shows mutation response only; it cannot prove unmutated predicates are true or relevant to their quoted lines.
- Evidence: `w2/out/F27C2IndependentControls/findings.md`; frozen predicates/claims unchanged; no lane bytes changed; no runtime invoked.