# Item 4 — census gate on a scratch mirror + append block (2026-10-26)

Lane read-only; everything runs in `/fast/scratch/hyaku/kama-r50/X1Assimilation`.
Mirror = `git clone --shared` of the lane at `97c864bead3ee4a2f629574e77263d33834ec98a`
(round-50 build), full tree so `used-by` paths resolve as the census resolves them
(`dir = dirname(SOURCES.md)/..`). The staged package's knowledge tree
(`shokuknow/merge/kama/knowledge/corpus/`, `…/amendments/corpus/`) is copied into
the mirror at its repo-relative path before the gate runs.

## Append block construction (`build-append-block.py`, scratch-only)

142 staged rows in, rules applied per row, every decision logged in
`append-decisions.json`:

| rule | rows | meaning |
|---|---|---|
| adopted | 119 | parsed to exactly 11 cells, id free, no E04, recheck normalized |
| R1 unparseable | 10 | cannot be split into 11 cells by an anchored parser: S368, S406, S409, S410, S415, S419, S454, S455, S459, S468 (8-13 cells before the status cell — pipes inside `anchor`/`teaches`) |
| R2 id collision | 9 | S330 S333 S334 S335 S346 S347 S352 S353 S363 — already mined in the lane (item 1) |
| R3 url+scope already in registry | 4 | S331 (lane S196), S340 (S205), S341 (S206), S344 (S209) — byte-identical `scope` cell, would be census E04 |
| R5 cell holds a pipe | 0 | none after recheck normalization |
| R6 used-by dropped | 0 | all cited knowledge files exist once the merge tree is mirrored |

Field-count reality of the staged package as shipped: 52 rows are 11 cells, 81 are
12, 2 are 13, 1 is 14, 2 are 15, 4 are 17 — i.e. **90 of 142 rows are census E01
(>11 columns)** because the `recheck` cell carries `curl … \| grep -c …` prose.
The 119-row block is what remains after normalizing `recheck` to the leading
cadence token (`90d`, or a bare ISO date, or the symbolic word) and recording the
stripped prose per row in `append-decisions.json`.

## Runs (from /home/vgpnk/Projects/shokunin)

1. Unmodified lane tip (baseline):

       $ bash scripts/sources-census.sh validate "$S/lane"
       exit=1
       3 E11 · 1 W01 · 93 W04
       file	E11	S496 missing used-by corpus/lessons/round-50.md
       file	E11	S497 missing used-by corpus/lessons/round-50.md
       file	E11	S498 missing used-by corpus/lessons/round-50.md

2. Mirror + 119-row append block inserted at the end of the `## Registry` table
   (before `## Paths`):

       $ bash scripts/sources-census.sh validate --file "$S/lane/corpus/SOURCES.md"
       exit=1
       3 E11 · 12 W01 · 123 W04
       file	E11	S496 missing used-by corpus/lessons/round-50.md
       file	E11	S497 missing used-by corpus/lessons/round-50.md
       file	E11	S498 missing used-by corpus/lessons/round-50.md

       $ bash scripts/sources-census.sh census --file "$S/lane/corpus/SOURCES.md"
       file	rows	358   (239 registry rows + 119 appended; no duplicate id)
       file	tier.A	313   tier.B 30   tier.C 15
       file	status.mined 337   status.queued 10   status.rejected 11

   **The append block adds zero E-codes.** The exit code is identical, and the
   E-set is the same three pre-existing E11s (the known integration item: the
   round-50 lesson the three new rows name has not landed). New warnings only:
   11 new W01 (tier-C mined with a real used-by: S407 S421 S423 S427 S429 S431
   S438 S439 S441 S463 S469 — plus the pre-existing S481) and 30 new W04
   (same URL, different scope).

3. Integration simulation — the same mirror, plus an empty
   `corpus/lessons/round-50.md` placeholder in the scratch clone only (the file
   the scribe lands at integration; this is a simulation, not a lane file):

       $ bash scripts/sources-census.sh validate --file "$S/sim/corpus/SOURCES.md"
       exit=0
       file	ok	$S/sim/corpus/SOURCES.md
       12 W01 · 123 W04   (warnings do not affect status)

So the append block itself is gate-clean: **exit 0** once the known missing
round-50 lesson exists; with today's tree it is **exit 1**, fully attributable to
the three S496/S497/S498 `used-by` misses and to nothing the block adds.

## Caveat on scope

The block is a *gate-measurement* artifact, not a merge proposal: it drops the 9
already-adopted ids and the 4 E04 duplicates, normalizes `recheck` and copies the
merge knowledge tree. The census cannot see whether a row's quote is faithful —
that is the item-3 hand-check, and it is not satisfied by a green census.
