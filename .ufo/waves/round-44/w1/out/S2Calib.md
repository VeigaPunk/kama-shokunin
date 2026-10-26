# S2Calib — round 44, C2 calibration analysis

**Verdict: the calibration pattern is explained and the two drafts are written; the frozen draft's figures reproduce at `agree 61 / overclaim 3 / underclaim 8 / other 15 / absent 15` and become `63 / 2 / 7 / 15 / 15` after two line corrections in round-25's spot-check — the 7 underclaims are all discernment ordering pairs, and the 2 remaining overclaims are both expansion credited before admission.**

Lane: kama. Claim: C2 (`tools/round44-verdict-ledger-audit.py`, calibration 7→7). Seat: leaf, read-only on the lane and the fleet; the only writes are the two deliverables under
`.ufo/waves/round-44/w1/out/S2Calib/` and this report. No counter, preregistration or control was edited.

## Method

The draft (`c2/draft-ledger.tsv`) was used only as a map. For all 204 keys I re-read the
cited line at the frozen revision with the counter's own `read_line` (imported, not
re-implemented), enumerated every other line in each file that carries the same trend's
verdict, and re-read the rounds where the pattern was load-bearing (10, 11, 12, 14–19, 24,
25, 27–29, 33–35, 37, 38, 39, 40, 43) in full. Ordering evidence comes from
`git log --diff-filter=A`.

## Commands and outcomes

| # | command | exit | outcome |
|---|---|---|---|
| 1 | `python3 .ufo/waves/round-44/tools/check-fragment.py c2 w1/out/S2Calib/fragment.tsv /fast/scratch/hyaku/kama-r44/S2Calib/chk` (run twice, identical stdout; second run persisted to `check-fragment.out`) | 0 | `rows=204 valid=204 missing=0 bad=0 agree=63 overclaim=2 underclaim=7 other=15 absent=15 table_missing=24 table_extra=0 summary=0 axes=0 met=False`; 21 fragment rows all `VALID` |
| 2 | `python3 <import of tools/round44-verdict-ledger-audit.py read_line> over the draft` | — | 0 of 204 draft rows rejected by the frozen reader; 17 cited lines carry ≥2 verdict words; 12 cited lines carry a negated or back-quoted verdict word |
| 3 | `git -C <fleet> log --diff-filter=A --format=%ci -- .ufo/reports/round-N/kama.md b0fd7b7f` and `git -C kama-shokunin log --diff-filter=A --format=%ci -- corpus/lessons/round-N-verifier-spotcheck.md 9d9cc93` | 0 | 30 rounds with both files: report always first; lag min 0.0 min (r10), median 9.7 min, max 257.6 min (r36); no negative |
| 4 | `git -C kama-shokunin cat-file -e 9d9cc93:corpus/lessons/round-2{0,1,2,3}-verifier-spotcheck.md` | 1 | `does not exist` for all four |
| 5 | `git -C <fleet> show b0fd7b7f:.ufo/reports/round-38/kama.md \| grep -n -i "expansion\|quality\|discernment"` | 0 | no match; `# Trends` at line 38 lists axis names |

## Figures

| reading | agree | overclaim | underclaim | other | absent | n |
|---|---|---|---|---|---|---|
| draft as filed | 61 | 3 | 8 | 15 | 15 | 72 |
| draft + round-25 line corrections | 63 | 2 | 7 | 15 | 15 | 72 |

`n = agree + overclaim + underclaim`; `absent` keys are outside `n` (the counter's own
definition). Mismatch-table rows: 26 as drafted, 24 corrected.

## Findings

**F1 — two draft rows cite a quotation or a negated word instead of the verdict sentence (defect in the draft, not in the frozen counter).**
`c2/draft-ledger.tsv` round 25:
- `25 quality outside` cites `corpus/lessons/round-25-verifier-spotcheck.md:193`
  (`entry's fact false or stale, so quality is not harmed.`) and records `harmed`. The
  closure's verdict sentence is line 187 `**Quality: unchanged.**`
- `25 discernment outside` cites `:200` (`The SCORECARD trend line (discernment improved,
  quality unchanged-to-improved) contradicts the report (both unchanged).`) and records
  `improved`. The verdict sentence is line 194 `**Discernment: unchanged.**`; line 200
  quotes SCORECARD's line in order to contradict it.

Command that shows it: `git -C kama-shokunin show 9d9cc93:corpus/lessons/round-25-verifier-spotcheck.md | sed -n '180,201p'`.
Proposed fix: cite `187` with `unchanged` and `194` with `unchanged`, as in
`w1/out/S2Calib/fragment.tsv` (both scored `VALID`, receipt command 1). Effect: `agree
61→63, overclaim 3→2, underclaim 8→7`, table 26→24 rows.

**F2 — the frozen reader is negation-blind and subject-blind (frozen; reported, not fixed).**
`tools/round44-verdict-ledger-audit.py:98-112` (`read_line`) attaches a verdict word to the
nearest preceding trend word with no negation and no subject check, so
`quality is not harmed` → `harmed` (round 25 line 193), `No axis was harmed` → `harmed`
for discernment (round 33 line 222), and `the r34 report blob is unchanged` → `unchanged`
for quality (round 35 lines 62 and 113). Consequence: `other=15` is a *line-reading*
count, not fifteen disagreements — on a first-word, first-subject reading 9 of the 15 are
ordering underclaims (rounds 12, 14, 15, 16, 17, 18, 27, 29, 39) and 6 agree (rounds 24,
33, 34-expansion, 35-quality, 37-quality, 43-quality). Proposed handling (no counter
change): the SCORECARD evidence column states what each second word does, which is what
the draft block in `draft.md` does. Per-row map: `w1/out/S2Calib/mismatch-map.tsv`.

**F3 — round 35's outside `quality` row is not independent evidence.**
`corpus/lessons/round-35-verifier-spotcheck.md:113` is a prefix-extension of
`…/fleet .ufo/reports/round-35/kama.md:62` (identical through "The do-nothing control
fails.", plus "The new S211 reason error is routed…"). The ledger still counts it as an
outside row. Command: `git -C kama-shokunin show 9d9cc93:corpus/lessons/round-35-verifier-spotcheck.md | sed -n '113p'` beside `git -C .. show b0fd7b7f:.ufo/reports/round-35/kama.md | sed -n '62p'`.
No fix available inside the frozen population; it must be stated where the figures are
read as evidence of independent agreement.

**F4 — rounds 20–23 have no outside trend verdict anywhere (12 absent rows).**
No `corpus/lessons/round-2{0,1,2,3}-verifier-spotcheck.md` at base; the closures are fleet
`MANIFEST.json` entries for lane kama (rounds 20, 21, 22, 23, dated 2026-10-21) carrying
`admitted` and no `trends` field. The lane records the same at
`corpus/lessons/round-22.md:95-102`. This is a closure-surface gap, not a lane omission;
the ledger's `absent` note must say so, since a bare `absent` reads as a missing row.

**F5 — round 38 filed axis verdicts in the trend slot (3 absent rows).**
`.ufo/reports/round-38/kama.md:38-43` heads a section `# Trends` and lists calibration,
coverage, operability, freshness, depth, adjacency. No line carries `expansion`, `quality`
or `discernment`. Correctly absent; worth naming because it is the only round that
substituted vocabularies, and a future reader will otherwise look for a missing file.

**F6 — the brief's prototype figure does not reproduce as phrased.**
"7 of the 8 underclaims are discernment (self unchanged, outside improved)" does not hold
of the draft as filed: 8 of 8 underclaims are discernment `unchanged`→`improved` (rounds
10, 11, 19, 25, 34, 35, 40, 43), and 7 of the 8 filed bytes name the owed outside act
(round 25's does not — its reason is the C1 axis misfiling). It reproduces exactly after
F1's corrections: 7 underclaims, all discernment, all naming the owed act. The
`fragment.tsv` receipt is the corrected reading.

**F7 — SCORECARD table trap for the integrator.**
The counter parses only a row's first four cells and requires **set equality** with the
mismatch set: an `absent` key or an agreeing key in the table sets `table_extra>0`, and a
missing mismatch key sets `table_missing>0`. The table must therefore hold 24 rows (26 if
F1 is not applied), not all 102 keys, and the `absent` figure lives only in the summary
line. Summary shape must be exactly
`agreement=<a>/<n> overclaim=<o> underclaim=<u> other=<x> absent=<k>` with `n = a+o+u`,
on one line inside the section.

**F8 — two integration legs outside the draft's scope.**
The `## Axes` calibration row must name `registry/verdict-ledger.tsv` (`axes=1`), and the
heading must be exactly `### Round-44 calibration ledger`; KQ58 cites
`corpus/lessons/round-44.md` §Calibration, which does not exist yet and must carry the
ordering evidence plus the two expansion overclaims, or the criterion cites nothing.

## Drafts delivered (item S2Calib, a and b)

`w1/out/S2Calib/draft.md` holds:

- **(a)** a paste-ready SCORECARD section `### Round-44 calibration ledger` with header
  `| round | trend | self | outside | class | evidence |`, the 24 corrected mismatch rows
  with `file:line` evidence, the figures line with `<a>/<n> <o> <u> <x> <k>` placeholders,
  and five interpretation paragraphs: every underclaim is an ordering pair (with the
  30-round first-add table and the closures' own sentences), both overclaims are expansion
  credited before admission (rounds 19, 28, each quoted), `other` is two-voiced lines and
  what each second word does, `absent` is a surface gap (rounds 20–23, round 38), and what
  the ledger does not show (closure generosity, reader blindness, the three-row swing from
  line choice alone).
- **(b)** one QUALITY.md criterion candidate, **KQ58** (next free id after KQ57), in the
  file's `## Criterion added — round N: <title>` + four-column table format, turning the
  observed bias into a rule: a verdict resting on a later act is filed `unchanged` with
  the act named; the pair is ledgered with `git log --diff-filter=A` ordering evidence and
  classified as an ordering pair or a defect; the ledger row cites the verdict sentence;
  `mixed` rows are explained, not counted as disagreements.

## The pattern, in one paragraph

In all 30 rounds with a closure file, the fleet report's first-add commit precedes the
lane spot-check's first-add commit (median 9.7 min; round 10, the same landing second).
LEARNING.md grades discernment `improved` on an act — "the spot-check agrees with the gate
on admits *and* rejects" (`LEARNING.md:35`) — performed by a non-author *after* the report
lands, and its §Discernment (`:40-47`) rules the lane's own seats out ("A subagent the
lane dispatched is still the lane"). So a lane filing before its closure cannot honestly
write `improved`: it would be self-attestation or a guess. `unchanged` plus the owed act
is the only true verdict, and every closure confirms it in its own words ("the author's
honest pending-sample `unchanged` for closure only", `round-12-…:123`; "The lane's
\"unchanged\" was correct at write time, pending this act", `round-19-…:172`). The
overclaims are a different mechanism: expansion credited before an admitted artifact
exists (round 19's source row, round 28's wave evidence), which LEARNING.md's expansion row
does not admit and both closures say so at the point of grading.

## Out of scope / not touched

- C1 (freshness re-check at b11889), the lane tree, the counters, the preregistration and
  the controls: read only, never edited.
- No counter was run; only the seat helper `check-fragment.py` (command 1), which scores a
  fragment in its own throwaway clone.
- No product or judge change; no commit, push or jj operation in the lane or fleet.
- Tooling: nothing installed or upgraded (no pacman, no uv/npx), so nothing to record.
- Scratch `/fast/scratch/hyaku/kama-r44/S2Calib` removed at close; no `/tmp` path is cited.

## Artifact paths

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S2Calib/draft.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S2Calib/fragment.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S2Calib/check-fragment.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S2Calib/line-map.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S2Calib/mismatch-map.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S2Calib/timing.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S2Calib.md`
