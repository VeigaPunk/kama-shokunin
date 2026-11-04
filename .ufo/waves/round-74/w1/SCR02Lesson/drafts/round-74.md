# Round 74 lesson — kama (DRAFT SKELETON, seat SCR02Lesson)

Draft for the L1 to land as `corpus/lessons/round-74.md` after the report tip.
Written mid-wave: it cites the frozen plan, prior-round committed paths and the
round-74 assimilation receipts only — no round-74 wave receipt is cited with a
tip claim or a 40-hex revision token, so nothing here can make the round's own
C2 claim pass red. `## Claims` and `## Wave` belong to the L1 and are not
created here. Freeze: `plans/round-74-claims.md`, base `868dd701` (per the
plan's own header; the lane master at this draft's writing is later — the L1
re-anchors). Carry-in: the round-73 non-author closure
(`corpus/lessons/round-73-verifier-spotcheck.md`) graded round 73 an honest
stop and routed six defects; its §6 items 1, 2, 5 are this round's C1/C2/C3,
item 3 is recorded in the SCORECARD calibration row, item 4 stays disclosed on
the routed queue, and item 6 is mined below as mistake 2.

## Gate

Candidates considered this round. Row wording is SCR01Sources' draft
(`.ufo/waves/round-74/w1/SCR01Sources/drafts/SOURCES-S546-row.md`); the
retained-bytes reference, access date and located quote are filled from that
seat's committed artifacts and independently spot-checked below. Per mistake 2,
the mirror census must record exit 0 BEFORE the L1 appends anything to
`corpus/SOURCES.md` this round.

| Row / candidate | Located quote (≤25 words) | Verdict |
|---|---|---|
| `os-release(5)` — new row **S546** (next id after the registry maximum S545; SCR01's derivation, draft at `.ufo/waves/round-74/w1/SCR01Sources/drafts/SOURCES-S546-row.md`); `https://man7.org/linux/man-pages/man5/os-release.5.html`, accessed 2026-11-04; retained bytes sha256 `c7ba68ea45180c33bad72a3b47cf09e3d6d34d0a5313a5acf73a14fc64f8a74e` at `.ufo/waves/round-74/w1/SCR01Sources/source/os-release.5.html` | "A lower-case string (no spaces or other characters outside of 0–9, a–z, ".", "_" and "-") identifying the operating system, excluding any version information and suitable for processing by scripts" (§OPTIONS, `ID=` entry, lines 187–194 of the retained HTML; present verbatim in the retained bytes — this seat's spot-check: `python3` tag/entity strip + substring search on the retained file → found) | **admit (pending gate)** — C3's triple rests on the `ID=` field semantics: the distribution component is what `ID=` names, excluding version; the row grounds the claim's knowledge entry `corpus/knowledge/host-block-base-revision.md`. Status stays queued until SCR01Sources' scratch-mirror census records exit 0 (its seat-text step 5) and the L1 appends after it — mistake 2's ordering is the precondition |
| `shokuknow/merge/kama/` package (assimilation) | not re-opened this round; the round-74 id-collision check ran: `.ufo/waves/round-74/assimilation/summary.out` → `reg_ids=285 staged_ids=142 collisions=9 quarantine_rows=7` (colliding ids S330 S333 S334 S335 S346 S347 S352 S353 S363; quarantine slice S200 S202 S206 S210 S211 S224 S230, all `payload-absent`) | **Assimilation: none** — no `merge/kama/` entry was re-grounded in round 74, so no row it carries is admitted (CORPUS rule 1, same class as round 73's gate decision; the id-collision receipt pointer is `.ufo/waves/round-74/assimilation/summary.out`, per-id list in the sibling `collisions` file). Flip: a later round that re-opens an entry in full and passes the per-entry PROVINCE.md scope and QUALITY.md bar checks |
| `considerthese/2026-10-26.md` proposals | proposal 4 (the morning pin-gap line per pinned engine) landed in round 73 as KQ122 plus the seat receipt `.ufo/waves/round-73/w1/SCR02Knowledge/pin-watch.out`; proposals 1–3 (append-deletion morning flag, proposal tracking table, shortcut-counter tally) are daily-pass workflow, not lane-round work | **nothing adopted** — proposal 4 is recorded as landed in round 73, not re-adopted here; proposals 1–3 remain daily-pass suggestions. Disposition: re-opened, considered, none adopted this round |

## Mistakes

Class · evidence pointer · captured-by · fix.

1. **The seat count drifted between the spec's prose and its items array, and
   nothing caught it.** The round-73 wave spec's `milestone` says "14 seats"
   while its `items` array carries 15 entries; the `context` goal prose repeats
   the 14. The dispatch ran 15 seats (the array is what the harness dispatches)
   and the closure counted 15 from the array, so the record self-healed without
   ever naming the split — a number that is a *structural fact* was carried by
   prose from an earlier wave shape. Evidence pointer:
   `.ufo/waves/round-73/w1-spec.json` (milestone names 14 at line 3; the items
   array at lines 14–150 has 15 objects). Re-derivation, run this seat:

   ```
   $ python3 -c "
   import json, re
   with open('.ufo/waves/round-73/w1-spec.json') as f:
       d = json.load(f)
   print('items count      :', len(d['items']))
   for field in ('milestone', 'context'):
       hits = re.findall(r'(\d+)\s+seats?\b', d[field], re.IGNORECASE)
       print('prose %-10s : %s' % (field, hits))
   print('context still names 14 while items carries 15:',
         len(d['items']) == 15 and '14' in re.findall(r'(\d+)\s+seats?\b', d['context'], re.IGNORECASE))
   "
   items count      : 15
   prose milestone  : ['14']
   prose context    : ['14']
   context still names 14 while items carries 15: True
   ```

   (committed as `.ufo/waves/round-74/w1/SCR02Lesson/r73-drift-derivation.out`).
   Captured-by: none — the r73 wave had no instrument comparing prose to array.
   Fix: `tools/round74-seat-count-check.py --spec` recomputes the count from
   `len(items)` and fails when a prose field (`milestone`, `context`) names a
   different count via a `N seats`/`N seat` token. Red demo on the real r73
   bytes: `.ufo/waves/round-74/w1/SCR02Lesson/r73-spec.out` (exit 1, finding
   names both fields); green on this round's spec (13 items, prose names 13):
   `.ufo/waves/round-74/w1/SCR02Lesson/r74-spec.out` (exit 0).

2. **The registry append preceded the first exit-0 scratch-mirror census.**
   The round-73 Frontier append ran while the mirror gate was red: the seat's
   own receipt records the candidate-in-place mirror census as
   `mode=mirror-preland exit=1` (three E11 findings naming the not-yet-existing
   lesson), the append documented from the receipt's header lines, and the
   first `mode=mirror-* exit=0` only afterwards, as a post-landing replication.
   The L1 authorised the append mid-state and the gate turned green within the
   window — honest, disclosed, but the ordering "exit 0 before touching the
   lane file" did not hold, and no gate failed because of it. Evidence pointer:
   `corpus/lessons/round-73-verifier-spotcheck.md` §6 item 6, against
   `.ufo/waves/round-73/w1/SCR01Sources/census.out` (append header lines 2 and
   4; `mode=mirror-preland exit=1` line 8; first `mode=mirror-* exit=0` at
   line 16). Captured-by: none — recorded by the closure as a routed defect,
   not caught by any instrument. Fix: the round-74 runbook orders
   mirror-census-exit-0 before append (SCR01Sources' seat text makes the exit-0
   mirror gate a precondition of any append, and the L1 appends only after it),
   and `tools/round74-seat-count-check.py --census-order DIR` makes the class
   executable: it scans a round dir's committed `*.out` receipts for the first
   `mode=mirror-* exit=0` line and the first registry-append marker (`sha256
   before=…after=` or the `corpus/SOURCES.md append` header) and fails when the
   exit-0 census postdates the append. R73 ordering replay, run this seat:
   `.ufo/waves/round-74/w1/SCR02Lesson/census-order-r73.out` (exit 1:
   "first exit-0 mirror census at w1/SCR01Sources/census.out:16 postdates the
   registry-append marker at w1/SCR01Sources/census.out:2"). Selftest
   (`.ufo/waves/round-74/w1/SCR02Lesson/selftest.out`) covers the honest
   ordering green, the r73 replay red, a flip guard proving the green is not
   vacuous, and both missing-population exit-2 arms.
