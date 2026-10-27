# L3Slice ledger audit

Tip: `138af25b963450b6520794995605fa7dbbcd87e0`. Rows below are the 27 ledger entries whose `file` column is exactly `SCORECARD.md` or `registry/report-landing-errata.tsv`. Each hash matched exactly one deleted line after removing one trailing CR. `Class ok?` is yes for every row: each deleting commit is not a `Revert "…"` commit and the matching deletion's hunk adds lines, hence the defined mechanical class is `in-place-edit`.

| Commit12 | File | SHA12 | Class ok? | Kind | Append correction instead? / restore now? | Same line elsewhere at tip? |
|---|---|---|---|---|---|---|
| 1471344b4c8b | registry/report-landing-errata.tsv | 287af57410f5 | yes | Reworded/replaced erratum: omitted landed hash reconciled to report evidence | Yes: append correction under self-declared append-only ledger rule. Restore stale row: no. | no |
| 1471344b4c8b | registry/report-landing-errata.tsv | aa792b393d96 | yes | Reworded/replaced erratum: omitted measured hash reconciled to report evidence | Yes; restore stale row: no. | no |
| 1471344b4c8b | registry/report-landing-errata.tsv | aaa567f70573 | yes | Wording correction: malformed splice diagnosis refined to distinguish two referents | Yes; restore stale row: no. | no |
| fd48f9a3b7ca | SCORECARD.md | 0c1676eaf369 | yes | Wording/qualification correction in round-26 narrative; sentence fragment joined to corrected narrative | Yes under A-corr for graded dated content; restore fragment: no. | no |
| fd48f9a3b7ca | SCORECARD.md | 15aa490748c2 | yes | Wording correction/qualification in round-26 narrative | Yes; restore old wording: no. | no |
| fd48f9a3b7ca | SCORECARD.md | 3de9465b0dd2 | yes | Wording correction in round-26 narrative | Yes; restore fragment: no. | no |
| fd48f9a3b7ca | SCORECARD.md | 457a818b3424 | yes | Structural sentence rewrite; joins runtime distinction with corrected round-26 result | Yes; restore old sentence: no. | no |
| fd48f9a3b7ca | SCORECARD.md | 49c5aa1749f8 | yes | Corrected round-26 adjacency/capability summary | Yes; restore stale summary: no. | no |
| fd48f9a3b7ca | SCORECARD.md | 6fcf98b1150c | yes | Measured claim correction (7→8 replaced by 7→7/no promotion) | Yes; preserve the former claim as a named correction rather than revive it. No restoration of the false claim. | no |
| 4d2e74f421bc | SCORECARD.md | 268ee1234cb7 | yes | Wording correction/qualification to round-27 KQ37 and defect explanation | Yes; restore old wording: no. | no |
| 4d2e74f421bc | SCORECARD.md | 356d86cd22ca | yes | Structural move/clarification: completed qualification replaces dangling continuation | Yes; restore fragment: no. | no |
| 4d2e74f421bc | SCORECARD.md | abe18109f369 | yes | Measured claim pointer corrected from report-time lane tip to measured receipt/commit | Yes; retain correction history, not stale pointer. | no |
| 4d2e74f421bc | SCORECARD.md | e7bba99195f5 | yes | Wording correction: false “neither meets nor misses” is superseded by explicit miss/correction | Yes; do not restore erroneous conclusion. | no |
| 6de225c289b7 | SCORECARD.md | 3502bbf0366e | yes | Re-anchored pointer: fleet `MISSION.md:29` made explicit as `MISSION.md` line 29 | Yes; restore old ambiguous anchor: no. | no |
| 6de225c289b7 | SCORECARD.md | a155b71a51fe | yes | Re-anchored pointer: bare lesson filename made lane-relative | Yes; restore old bare anchor: no. | no |
| 6de225c289b7 | SCORECARD.md | f6d247ad2f6d | yes | Re-anchored pointer: report path location corrected | Yes; restore old anchor: no. | no |
| 6de225c289b7 | SCORECARD.md | f7e86820f210 | yes | Re-anchored pointer: bare tool filename made lane-relative | Yes; restore old anchor: no. | no |
| 026eede9f46a | SCORECARD.md | 411a05910b4e | yes | Structural move/reorganization: round-30 self-assessment heading split into corrected heading and separate census/claim section | Yes for graded dated section; restore obsolete heading: no. | no |
| ce41bae692c8 | SCORECARD.md | 38865018fee1 | yes | Measurement placeholders replaced with observed C1 values/commit/receipt | Yes for graded dated section; restore placeholders: no. | no |
| ce41bae692c8 | SCORECARD.md | 9ae1b415152e | yes | Measurement placeholders replaced with observed C3 values/commit/receipt | Yes; restore placeholders: no. | no |
| ce41bae692c8 | SCORECARD.md | e4e9343d20b7 | yes | Measurement placeholders replaced with observed C2 values/commit/receipt | Yes; restore placeholders: no. | no |
| ef76777e5fbd | SCORECARD.md | b28cbdd7da31 | yes | Re-anchored planned-section pointer, updated to the live round-43 measured-results section | Yes for graded section; restore stale pointer: no. | no |
| ef76777e5fbd | SCORECARD.md | bb9019946103 | yes | Re-anchored planned-section pointer; old round-5 plan retained under history | Yes; restore stale pointer: no. | no |
| 42ea1204aef3 | SCORECARD.md | bf5869828bfa | yes | Re-anchored pointer to round-47 plan; old plan retained in history | Yes; restore stale pointer: no. | no |
| 42ea1204aef3 | SCORECARD.md | ed5ff78ef347 | yes | Structural move: measured-results block moved out of planned/head pointer sentence; corrected planned pointer supplied | Yes; restore old pointer: no. | no |
| 1c030f182834 | SCORECARD.md | f49564c40558 | yes | Current-authority banner updated from round 49 to round 50 and history claim amended | Yes for graded banner; old authority is stale, do not restore. | no |
| db6bfa8d9354 | SCORECARD.md | e3fe531f0788 | yes | Placeholder replaced with measured round-50 result and receipts | Yes for graded dated section; restore placeholder: no. | no |

“Append correction instead” follows the lane's declared A-corr behavior: corrections are appended with superseded text/revision named (QUALITY KQ26); SCORECARD's contract specifically says dated round sections append-only, while its named re-derived head sections are region-exempt. The old lines are not verbatim at the tip; the identified changes are corrected, superseded, pointer-repaired, or placeholder-filled material, not a demonstrated loss of still-valid substantive content. Thus no line should be literally restored now. This is a procedural A-corr concern, not evidence that the mechanical class is wrong.