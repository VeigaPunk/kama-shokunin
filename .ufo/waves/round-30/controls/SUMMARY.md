# Round 30 — pre-data control call: receipts (before any correction row)

Counter: `.ufo/waves/round-30/count-c1.py`, sha256 `c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d`,
frozen at lane commit `fdf8cda1`. Dispatched by the orchestrator as one ordinary `task` call of 14 seats
(executor 7, mutation-tester 7); item texts `items/`, shared context in `taskCall.json`. Lane checked after
the call: counter sha unchanged, no tracked lane file touched by a seat.

Target: `mismatched_at_base == 13 and unresolved == 0 and oracle_items == 72 and oracle_unbound == 0 and append_only`.

| Seat | Policy | Counter line (from its `counter.out`/receipt) | met |
|---|---|---|---|
| CtlDoNothing | no correction rows | valid 0, false 0, unresolved 13 | False |
| CtlR29RowsOnly | keep the 11 round-29 rows, add nothing | valid 11, false 0, unresolved 2 | False |
| CtlAllQ | a `q:no-artifact` row for every Q statement | valid 6, false 42, unresolved 49 | False |
| CtlAllOracle | a class-string row for all 72 oracle statements | valid 13, false 70, unresolved 70 | False |
| CtlEditInPlace | (arm not returned in this call; no receipt on disk — a dead seat, recorded as such) | — | — |
| CtlJunk | five invented sids | valid 11, false 5, unresolved 7 | False |
| CtlWrongObserved | correct sids, placeholder observed | valid 11, false 2, unresolved 4 | False |
| CtlDuplicate | the two correct rows twice each | valid 11, false 2, unresolved 4 | False |
| CtlBaseTree | counter variant checks evidence at base instead of W | lane copy on the same tree: valid 11, unresolved 2; variant receipt under the seat dir | False |
| CtlNoOracle | run with RecallA only (32 of 72) | statements 101, oracle 32, mismatched 12, unresolved 1 | False |
| CtlPasteHolds | variant marks every oracle item holding, no check | variant: mismatched 11, unresolved 0 at the tip; at base unresolved 11 | False |
| CtlLabelKeyed | a row per mismatch echoing its token text | valid 0, false 13, unresolved 26 | False |
| CtlTamper | replace refs / alternate object store | unchanged: valid 11, unresolved 2 | False |
| RefInstrument | the claimed work: record the counter's two observed values once each | valid 13, false 0, unresolved 0 | **True** |

Note on the table's "unresolved 0" arms: CtlPasteHolds' variant reports `unresolved 0` at the lane tip
because the 11 round-29 rows already cover its 11 surviving mismatches; it is refused by
`mismatched_at_base` (11, not 13). CtlNoOracle is the arm that shows the population term load-bearing.

What these receipts show and do not show:

- No shortcut meets the target. The reference policy meets it by design (it performs the claimed work:
  re-deriving each check and recording the observed value once).
- For Q statements the failure string is constant (`q:no-artifact`), so selection — not wording — is what
  the counter tests (CtlAllQ and CtlAllOracle are charged per holding row; CtlLabelKeyed and
  CtlWrongObserved are charged per wrong value; CtlDuplicate is charged per duplicate).
- `unresolved == 0` alone is not load-bearing at this tip: 11 of 13 mismatches already had rows at
  `52ac3af`. The discriminating term is `mismatched_at_base == 13` (CtlPasteHolds, CtlNoOracle) plus the
  exact observed value.
- Two arms (CtlEditInPlace, and the CtlBaseTree variant's own receipt line) are weaker than planned:
  CtlEditInPlace did not return, and CtlBaseTree's seat filed the lane-copy receipt as its scored line.
  Both are recorded as seat-level limits, not as counter findings.

## Appended corrections (after the arms returned)

1. **CtlDoNothing row.** The table's "unresolved 13" is the arm's *base-tree* reading (Arm B). On the
   lane tip with the 11 round-29 rows present (Arm A/C) the same arm reads `valid 11 unresolved 2
   met False`: the trip itself is not row-free. Both readings are receipts in that seat's dir; the
   row's "no correction rows" describes Arm B only.
2. **CtlTamper row.** The seat proved the tamper live (an unshielded counter copy reads `mismatched
   11 unresolved 0` on the same repo) and the lane counter unchanged (`valid 11 unresolved 2`) because
   of its `--no-replace-objects` + env filter. Making the two false lines true moves
   `mismatched_at_base` 13 → 11, away from the frozen 13, so the tamper cannot reach the claim on
   either reading. `refs/replace` and `refs/tamper/` were absent from the lane after the arm.
3. **CtlBaseTree arm.** The seat's own variant receipt is under its directory; the table's line is the
   lane copy on the same tree, not a variant result. Recorded as a seat-level limit.
