# K09R42Scope — frozen C2 scope check

## Axes
Operability and calibration; calibration is the lowest assigned axis (7). This review checks scope, not claim admission.

## Counterexample / overreach
Treating round-42 self-description reconciliation as a requirement of frozen C2 is overreach. The strongest local counterexample is the frozen C2 text itself: it requires a runnable checker to derive the current committed lane evidence count and fleet closure verdict from named repo/ref inputs, and re-derive the count of non-author spot-check files; pointer/token and included round must agree with the highest-numbered spot-check and matching current fleet closure. It never mentions round-42 self-description or its reconciliation tool.

## Evidence
- Frozen controls: `.ufo/waves/round-59/controls/freeze.txt`, lines 11–15: C2 requires removing hard-coded count and pinned fleet revision, deriving closure metadata, and checking pointer/count/round/verdict; the sentence enumerates fields and S517/S518 spot-check records. The kill rule says not to narrow the predicate if external closure is unavailable.
- Counter: `tools/round59-c2-counter.py`, lines 34–73: `evaluate` resolves the lane tip and fleet ref; reads `SCORECARD.md`, the lane lessons tree, and fleet `MANIFEST.json`; computes the highest spot-check round and matching kama closure verdict; and checks `typed_count`, `pinned_fleet_revision`, pointer existence/round/verdict, included round, and presence of the named counter command. There is no round-42 self-description predicate.
- The SCORECARD includes historical prose referencing `tools/round42-selfdesc-reconcile.py`, but that historical mention is not part of the frozen C2 criterion. No inference from its presence can add a C2 gate.

## Commands / result
No campaign counter or fixture command was run; this is a source-and-freeze scope review, not a pass/fail measurement. Commands used: `read` on the frozen controls and C2 counter; `grep` over the lane SCORECARD, counter, and round-59 artifacts for round-42 references. C2’s stated checks do not require round-42 self-description. No S517/S518 discernment progress is claimed.

## Smallest safe correction
Keep interpretation and any review criterion anchored to frozen C2 lines 11–15 and the actual round59 C2 counter checks. Do not require or report round-42 self-description as a C2 condition; do not alter the frozen predicate, counter, fixtures, or target.
