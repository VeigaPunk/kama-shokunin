# RV02 — C2 attack: late-delta leg + repaired row-introduction debt rule (lane read-only; clone/fixtures in $S)
Receipts: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/RV02AttacC2/measured/
Honest tip (baseline-tip.out): LATE_DELTA round=82 base=aaf974dbd3b6 population=103 carried=88 new=15 bad=0
exit 0; APPEND_DEBT round=82 events=68 accepted=53 late=15 pending=2 unaccepted=0 bad_rows=0
bad_declarations=0 out_of_population=0 exit 0.

## A. LATE_DELTA mutations (register byte-changed, committed; `python3 tools/round82-late-delta.py --repo . --round 82`)
| mutation | observed | verdict |
|---|---|---|
| carried row, one note byte | bad=1 `rewritten` exit 1 | refused |
| new row count 1→2 | bad=1 `cell-mismatch` (2 vs 1) exit 1 | refused |
| new row class → removal | bad=1 `cell-mismatch` exit 1 | refused |
| note `round-81 accepts round-81` | bad=2 `note-wrong-round`+`note-not-later` exit 1 | refused |
| note `round-83 accepts round-81` | bad=1 `note-wrong-round` exit 1 | refused |
| extra row, event outside population | bad=1 `extra` exit 1 | refused |
| duplicate row | bad=1 `duplicate` (lines 104/105) exit 1 | refused |
| header line edited | could-not-evaluate exit 2 | refused |
Rule inferred: a later accepting round is refused — `accepting` must EQUAL the graded round
(`accepting != round_number`), so `N > M` is necessary, not sufficient; round 83 may not close 82.

## Escape list
E1 (open, medium): the note's deletion round is unbound on BOTH legs. One new row of a round-81 event
noted `round-82 accepts round-79 "…"; accepted …` (clone 5b65b05) prints the honest lines — LATE_DELTA
bad=0 exit 0; APPEND_DEBT late=15 unaccepted=0 bad_rows=0 exit 0 (escape-both-legs.out); neither leg
compares the note's M with the event's subject round (the generator derives then drops it).
E2 (leg-local): pair-only note (`round-82 accepts round-81`, no `; reason`) — delta bad=0 exit 0, debt
`hash-mismatch` exit 1 (extra-pair-only-*.out); no claim escape, but a delta-only receipt cannot
establish note shape.
E3 (flags): `--audit-json` skips re-derivation and prints the identical line; `--to` moves the graded
revision; the delta's `--late` is a repo path. The frozen command has no flags, so the graded path is
unaffected; a receipt using them is not the frozen command.
E4 (doc, low): `round81-append-debt.py:39` promises a fallback for an unresolvable row; `:256` has none
(`.get`→None→`unbound-register` at :258), and selftest arm `row-intro-unbound` (:494) asserts that
(`--selftest` pass=25 fail=0). Behaviour intended; the docstring sentence is false.

## B. Repaired debt rule (fixtures; `--repo <fixture> --round 82 --audit-json <fixture audit>`, copy at $S)
- not-descendant: side-branch row merged in → `not-descendant`, unaccepted=1, exit 1.
- accepted: row introduced after its event → late=1 unaccepted=0 bad_rows=0 out_of_population=0, exit 0.
- unbound: row read via `--late` → `unbound-register`, exit 1, even when the event is frozen-accepted.
- graded round's events: `round-83 accepts round-82` passes N>M but the base split makes the event pending → `out_of_population=1`, exit 1; `round-82 accepts round-82` → `same-round`.
- `--late` limit: no introduction is bound; every non-empty row is `unbound-register`, only an empty file passes (exit 0 verified); it cannot demonstrate acceptance.
- "ancestor of its event" is unrepresentable with a self-consistent row (it must name the event's 40-hex → circular); the merged side branch is the nearest non-descendant placement.
No actionable finding against C2's honest target lines; both print and exit as frozen.
