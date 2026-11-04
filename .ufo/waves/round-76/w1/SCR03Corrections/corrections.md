# rev=1a85a991fce5b76b60f88a5cab3df98d253b1a4a
# Round-76 correction paste blocks — SCR03Corrections

Drafted 2026-11-04. Calibration is the target axis; append-only integrity is the guard. Each destination and insertion instruction below is metadata, not part of the paste text. Paste the `### Correction` block and its `#### Superseded bytes` subsection into the named destination, preserving all original bytes. These are correction drafts, not counter receipts or execution evidence.

### SCORECARD province-digest

Destination: `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md`.
Insertion: after the §Round 75 `Axis harm check:` population paragraph (frozen-base line 4065), before `**Capabilities — canonical list as of round 75**`.

### Correction (2026-11-04) — province-digest

Supersedes: SCORECARD.md:4065, §Round 75 population sentence, the `PROVINCE.md` digest and its `(unchanged)` assertion at `rev=c9ab73d842051db5f8320bced4357bf13cf14108`.
Revision: c9ab73d842051db5f8320bced4357bf13cf14108
Corrected: af459acfa975d418a389f0ce19b8f1f40dd7e08d15c7eb0e9f2eb27e45d45697

`PROVINCE.md` at that revision has 322 lines and sha256 `af459acfa975d418a389f0ce19b8f1f40dd7e08d15c7eb0e9f2eb27e45d45697`. The line count matches; the filed sha256 `0e8dc562f99367c3668c5ac2375c49828efa3152aa61fc235f28e896b271b5c4` and `(unchanged)` are superseded, not silently repaired. Provenance: `.ufo/waves/round-76/measured/before/c2-facts.out`, recorded at `rev=b06cc612711560c53eef3ec21484c6963601262f`; this is a round-76 correction to round-75 prose.

#### Superseded bytes (held verbatim; original paragraph remains)

The following exact excerpt of the original line is history, not the live digest:

``````text
`PROVINCE.md` 322 lines sha256 `0e8dc562f99367c3668c5ac2375c49828efa3152aa61fc235f28e896b271b5c4` (unchanged).
``````

Live correction: §Correction (2026-11-04) — province-digest above.

### LOG log-worktip

Destination: `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md`.
Insertion: after the final paragraph of §Round 75, ending `adjacency 7).`; preserve the original opening paragraph.

### Correction (2026-11-04) — log-worktip

Supersedes: LOG.md:3002, §Round 75 opening paragraph's work tip `b8ed256829589a13a0ba2249a8ae9e2b8800fb5a`.
Revision: c9ab73d842051db5f8320bced4357bf13cf14108
Corrected: c9ab73d842051db5f8320bced4357bf13cf14108

The round-75 last non-record work commit is `c9ab73d842051db5f8320bced4357bf13cf14108`, not the earlier filed `b8ed256829589a13a0ba2249a8ae9e2b8800fb5a`. The round-75 SCORECARD opening already names the corrected work revision. The base and freeze revisions remain unchanged. This is a round-76 retrospective correction, not a new round-75 execution receipt.

#### Superseded bytes (held verbatim; original paragraph remains)

``````text
freeze `0908bab5cbf0ab6b435144fc525a3e18443dc08f`); work tip `b8ed256829589a13a0ba2249a8ae9e2b8800fb5a`.
``````

Live correction: §Correction (2026-11-04) — log-worktip above.

### LOG log-mistakes

Destination: `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md`.
Insertion: immediately after the appended log-worktip correction, after the original §Round 75 paragraph.

### Correction (2026-11-04) — log-mistakes

Supersedes: LOG.md:3017, §Round 75 lesson description's `four mistake classes`.
Revision: b06cc612711560c53eef3ec21484c6963601262f
Corrected: 5

The round-75 lesson carries five mistake classes: items 1–4 in `## Mistakes` and item 5, `record-cites-control`, in `## Mistakes (continued)`. The filed `four mistake classes` omits the continued item. Provenance: `.ufo/waves/round-76/measured/before/c2-facts.out` and `corpus/lessons/round-75.md:145-162`. This correction does not revise the historical text or claim the fifth class was in the original four-item tally.

#### Superseded bytes (held verbatim; original paragraph remains)

``````text
criteria and the round-74 coverage-map block. Lesson: `corpus/lessons/round-75.md` (four mistake classes,
``````

Live correction: §Correction (2026-11-04) — log-mistakes above.

### SCORECARD closure-pointer

Destination: `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md`.
Insertion: after the complete `## Axes` table (including its adjacency row), before `### Historical axes table (round-3 assessment; superseded in round 41)`; retain the original calibration row verbatim.

### Correction (2026-11-04) — closure-pointer

Supersedes: SCORECARD.md §Axes, calibration row, `latest outside closure` pointer naming `corpus/lessons/round-74-verifier-spotcheck.md` (frozen-base line 18).
Revision: b06cc612711560c53eef3ec21484c6963601262f
Corrected: corpus/lessons/round-75-verifier-spotcheck.md

The newest outside closure at the named base revision is `corpus/lessons/round-75-verifier-spotcheck.md`, review date 2026-11-04, round 75. This supersedes only the calibration row's latest-closure pointer, not its historical run facts, score 7, or older closure dispositions. Provenance: `.ufo/waves/round-76/measured/before/c2-closure.out`, which reports `round=75 row_names=corpus/lessons/round-74-verifier-spotcheck.md row_current=false` and exit 1. This appendix is not evidence that the original table row has been rewritten or that the newest-closure counter now passes.

#### Superseded bytes (original row retained)

Exact superseded substring of the calibration row:

``````text
latest outside closure `corpus/lessons/round-74-verifier-spotcheck.md`
``````

Live correction: §Correction (2026-11-04) — closure-pointer above. The contract exempts §Axes from historical append-only grading, but this draft nevertheless appends rather than rewrites.

### LOG log-tally

Destination: `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md`.
Insertion: immediately after the appended log-mistakes correction, after the original §Round 75 paragraph.

### Correction (2026-11-04) — log-tally

Supersedes: LOG.md:3016, §Round 75 `round75-instruments` gate-selftest assertion `PRE_REPORT_SELFTEST pass=18 fail=0`.
Corrected: historical-unbacked

Fact class: an unbacked historical execution tally, not a re-derived passing run. No committed round-75 wave receipt backs the asserted `PRE_REPORT_SELFTEST pass=18 fail=0`; the round-76 base receipt `.ufo/waves/round-76/measured/before/c2-tally.out` records zero matches. The old tally remains as filed history but is withdrawn as receipt-backed evidence. A later run cannot establish that the round-75 execution occurred.

Round-76 receipt destination for re-establishing receipt-backed selftest practice: `.ufo/waves/round-76/measured/after/pre-report-selftest.out`. This destination is proposed by SCR03, not an observed or committed receipt at draft time. Receipt-backed practice is not yet re-established by this correction: only the actual output of `python3 tools/pre-report-gate.py --selftest`, captured with its measured revision and exit at that path, can establish the new run. No new tally, receipt revision or passing outcome is asserted here.

#### Superseded bytes (held verbatim; original paragraph remains)

``````text
`round75-instruments` (`PRE_REPORT_SELFTEST pass=18 fail=0`), S547 (`gitattributes(5)`), three QUALITY
``````

Live correction: §Correction (2026-11-04) — log-tally above; the new receipt, when actually captured, proves only the round-76 run. This block is ready to append as a truthful withdrawal, but is not a completed receipt-bound C2 correction until L1 captures the new receipt and appends its actual revision and tally.
