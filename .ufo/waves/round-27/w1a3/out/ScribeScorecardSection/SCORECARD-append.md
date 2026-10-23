VERDICT: partial — C1 was withdrawn before data; X1 awaits a named non-author reviewer, and no score is promoted.

## Round 27 — live error-signature counter calibration (2026-10-23, attempt 3)

Prior score snapshot: depth 7, calibration 7, adjacency 7 (`SCORECARD.md:1314-1318`).
| Claim | Axis | Before → after | Verdict | Evidence |
|---|---|---|---|---|
| C1 (measured) | depth | 7 → 7 | withdrawn before data; no data result | `.ufo/waves/round-27/a3/plan.json:6-8`; `corpus/lessons/round-27.md:13-20` |
| X1 (exploratory) | calibration | 7 → 7 | pending named non-author reviewer | `.ufo/waves/round-27/a3/plan.json:10-18`; `corpus/lessons/round-27.md:22-30`; `corpus/knowledge/echo-discriminating-counters.md:7-12,39-54`; `corpus/QUALITY.md:219`; `corpus/SOURCES.md:148-149` |

X1 records method knowledge only: decoded-request echoes are refused and at most one row is credited per message frame; it does not establish live-data discrimination (`.ufo/waves/round-27/count-c1.py:343-372,586,708-709`; `corpus/knowledge/echo-discriminating-counters.md:56-68`).

No score promotions. Other scores remain held at the last recorded values: operability 8, freshness 8, coverage 9, adjacency 7 (`SCORECARD.md:1354-1355`).

### Repairs — round-26 spot-check defects

1. D1 — Appended LOG correction preserves history: `LOG.md:1728-1745`; routed defect `corpus/lessons/round-26-verifier-spotcheck.md:233`; repair note `corpus/lessons/round-27.md:34-35`.
2. D2 — A3 counter checks decoded request surfaces and shared frames; KQ37 codifies the rule. Pre-data controls were met only vacuously because no data seat ran: `.ufo/waves/round-27/count-c1.py:343-372,586,708-709`; `corpus/QUALITY.md:219`; `corpus/lessons/round-27.md:36-39`.
3. D3 — Help/version pins committed; README retains a provenance caveat: `.ufo/waves/round-27/repairs/d3-r26-shortcut-pins/README.json:2-17`; pinned files are in the same directory.
4. D4 — Dead-seat error lines committed with extraction metadata: `.ufo/waves/round-27/repairs/d4-r26-dead-seat-errors/README.json:2-4`; `.ufo/waves/round-27/repairs/d4-r26-dead-seat-errors/KamaR26CtlDoNothing.error-lines.jsonl` (and the Junk/NoReader files); `corpus/lessons/round-27.md:45-48`.
5. D5 — Lesson clarifies commit-vs-tree semantics; original round-26 receipts remain unedited: `.ufo/waves/round-26/final/c1-tip.out:2`; `.ufo/waves/round-26/final/c2-kq36-tip.out:2`; `corpus/lessons/round-27.md:49-58`; `corpus/lessons/round-26-verifier-spotcheck.md:197`.
6. D6 — Gate reasons corrected, including the three round-18 files and error-label wording: `corpus/lessons/round-27.md:59-69`; routed defect `corpus/lessons/round-26-verifier-spotcheck.md:238`.
7. D7 — S138 corrects S133's closing-line anchor to 1835: `corpus/SOURCES.md:150`; `corpus/lessons/round-27.md:70-71`.
8. D8 — Still open; `count-c2.py` receipt-cell trust defect not fixed: `corpus/lessons/round-27.md:72-74`; `corpus/lessons/round-26-verifier-spotcheck.md:240`.
