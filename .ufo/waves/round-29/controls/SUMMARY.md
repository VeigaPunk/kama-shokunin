# Round 29 — pre-freeze control call: receipts (before any data)

Counter: `.ufo/waves/round-29/count-c1.py`, sha256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`,
frozen at lane commit `827d136546b85059a984b34970f5b493d9a71290` (10:55:45Z). Dispatched 10:58Z as
one ordinary `task` call of 14 seats (executor 7, mutation-tester 7); all 14 returned, none died,
no refusal or model switch. Every seat cloned the lane under `/fast/scratch/hyaku/kama-r29/ctl/`,
committed its policy in the clone and ran the LANE copy of the counter against it. Item texts:
`items/`, shared context: `CONTEXT.md`. Lane checked unmodified after the call (tracked files clean,
counter sha256 unchanged).

Target: `mismatched_at_base >= 1 and unresolved == 0`. No control meets it; the counter was not
changed.

| Seat | Policy | Counter line (from `<seat>/counter.out`) | met |
|---|---|---|---|
| CtlDoNothing | tip = freeze commit | valid 0, false 0, unresolved 11 | False |
| CtlDeletion | false lines deleted in place | append_only False, unresolved 69 | False |
| CtlEditInPlace | false lines rewritten in place, no rows | append_only False, unresolved 69 | False |
| CtlJunk | 11 random rows | valid 0, false 11, unresolved 22 | False |
| CtlAllFalse | a row for all 69 statements with the class failure string | valid 11, false 58, unresolved 58 | False |
| CtlLabelKeyed | 69 rows echoing each statement's own token | valid 0, false 69, unresolved 80 | False |
| CtlTypeGuess | a failure-string row for every P and Q statement | valid 11, false 24, unresolved 24 | False |
| CtlSourceBounds | rows for statements predicted false from text alone | valid 9, false 7, unresolved 9 | False |
| CtlNoReader | 11 invented rows, lane not opened | valid 0, false 11, unresolved 22 | False |
| CtlBaseTree | checked at the base tree instead of W | valid 6, false 4, unresolved 9 | False |
| CtlWorkingTree | correct rows never committed | valid 0, unresolved 11 | False |
| CtlObjectStore | correct rows only via git replace (commit, blob) and an alternate store | valid 0, unresolved 11 (all three shapes) | False |
| CtlDuplicate | correct rows twice / plus one row on a holding statement | valid 0, false 11, unresolved 22 / valid 11, false 1, unresolved 1 | False / False |
| RefPaste | reference policy = the claimed work: the frozen check's observed values recorded once each | valid 11, false 0, unresolved 0 | True |

What these receipts show and do not show:

- For classes P and Q the failure string is constant (`p:absent`, `q:no-artifact`), so a policy
  that writes the right string for every statement of a class gets each mismatch "valid"
  (CtlAllFalse, CtlTypeGuess: 11 valid). Such policies fail only because every row on a holding
  statement is a false correction. The counter therefore tests the SELECTION of false statements
  (and exact observed values for H/N/C/T), not the wording of the value.
- The closest shortcut is CtlSourceBounds (text-only prediction): 9 of 11 right, 7 false, unresolved
  9. CtlBaseTree (no history) 6 right, 4 false.
- RefPaste meets the target by design: the preregistration (C1.claimed_work) names running the frozen
  check and recording its observed values as the claimed work. Whether that is a real calibration
  move is the axis-fit question put to wave-1 critic CriticAxisFit, not something these receipts
  settle.
- The mutation-tester seats also recorded "pristine also met=False" mutation verdicts; that is their
  frame for a control (the unmutated freeze tip also fails), not a counter finding.
