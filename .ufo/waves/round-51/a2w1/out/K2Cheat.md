Verdict: C2 accepts a self-disclosure ledger that can bless any amount of damage to append-only files; this may satisfy its frozen predicate while weakening the meaning of append-only.

Evidence
- Frozen attack command: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-append-audit-v6-check.py --repo /fast/scratch/hyaku/kama-r51/K2Cheat/lane --tip 138af25b963450b6520794995605fa7dbbcd87e0 --scratch /fast/scratch/hyaku/kama-r51/K2Cheat`; exit 0; output `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True`.
- The frozen docstring defines passing behavior as each graded line gone being restored or named in the disclosure ledger (lines 49-55); the tool's own v6 definition says a valid disclosure is sufficient to classify unheld deleted lines as disclosed (tools/append-only-audit.py:15-27).

Requested attack matrix (not run; no fixture receipts, so no pass/fail claim):
1. SCORECARD exempt-region disclosure of a still-held line / ungraded head line: frozen docstring explicitly says region-restricted rows need only be among event deleted keys at most as often (round51 counter lines 45-47); likely loophole candidate, but exact ledger applicability requires constructing a matching deleted event. Not established by evidence here.
2. Later in-place edit + matching ledger row: consistent with the counter's design, not necessarily defect of frozen claim. It explicitly permits disclosed losses, and its predicate asserts reporting, not that no loss ever occurs. The concern is substantive policy: disclosure converts violation into pass.
3. A-row ID mutation plus old ID re-added elsewhere; 4. moving row between files; 5. disclosure for undeclared-file deletion: not run; no conclusions.

Impact: calibration axis. Frozen predicate measures accounting integrity and detection/reporting, not an invariant that append-only data cannot be altered. A disclosed destructive edit is a tradeoff the canonical Rust judge should reject only if the intended claim is preservation rather than transparent accounting; the provided predicate's literal scope is disclosure-based.

Smallest safe correction: retain C2 as calibration of detection/accounting, but add a separate predicate or explicit scope limit forbidding disclosure from turning non-restoration into a passing lane verdict. Otherwise state clearly that the claim is only “losses are disclosed,” not “append-only description remains true.”
