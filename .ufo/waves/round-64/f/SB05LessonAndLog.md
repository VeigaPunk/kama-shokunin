# SB05LessonAndLog — round 64 wave f (kama): draft lesson §Mistakes/§Wave results and the LOG entry

Seat: SB05LessonAndLog (leaf, advisory; no subagent dispatch). Axis: calibration. Milestone: draft lesson and LOG.
Scope: drafts only. No lane source file was edited, no commit, no verdict on C1 or C2.

## Behavior

Two drafts, both in `.ufo/waves/round-64/f/out/SB05LessonAndLog/`:

- `lesson-round-64-draft.md` — the five requested `## Mistakes` rows (M-A … M-E), each in the lane's
  class · evidence pointer · captured-by · fix format, plus a 42-row `## Wave results` table for wave b
  (role, survivors found at the freeze instrument, disposition at the amended tip) and an attribution note.
- `log-round-64-draft.md` — the `LOG.md` round-64 entry text (14 lines, facts only, every line with a pointer),
  plus six notes for the L1 on defects in the landed text.
- `intent-to-add-mechanism.txt` — the scratch-fixture receipt for the `git add -N .` mechanism (see M-E).

Nothing was run against the C1 or C2 counters: this seat drafts prose, and every counter line quoted is a
committed or on-disk receipt that I re-read rather than re-executed. No tool was installed; no pacman transaction.

## Gates

| Gate | Result |
|---|---|
| Lane reads only | yes — no lane file written except this seat's own report + out dir |
| No commit / no `git add` / no `git add -N` in the lane | yes — `git ls-files -s` shows 0 index entries with the empty blob `e69de29b` that are absent from the HEAD tree, i.e. no intent-to-add residue |
| No fleet-root tracked file written | yes — `LOG.md` and `SCORECARD.md` untouched; the LOG entry is a draft in my out dir |
| No scratch left behind | yes — `/fast/scratch/hyaku/kama-r64/f/SB05LessonAndLog` removed after the receipts were copied |
| Facts verified | every pointer in the drafts is a path:line I read; four pointer corrections were made after re-reading (receipt line numbers, the LOG range, the seat-name count, the `byte-pinned` line) |

## Touched surfaces

Written (mine only):
- `.ufo/waves/round-64/f/SB05LessonAndLog.md` (this report)
- `.ufo/waves/round-64/f/out/SB05LessonAndLog/lesson-round-64-draft.md`
- `.ufo/waves/round-64/f/out/SB05LessonAndLog/log-round-64-draft.md`
- `.ufo/waves/round-64/f/out/SB05LessonAndLog/intent-to-add-mechanism.txt`

Read: `.ufo/waves/round-64/controls/freeze.txt`, `.ufo/waves/round-64/controls/*` receipts,
`.ufo/waves/round-64/b/*.md` (42 reports), `.ufo/waves/round-64/b/b-results.json`,
`.ufo/waves/round-64/measured/**`, `.ufo/waves/round-64/f/**`, `corpus/lessons/round-64.md`, `corpus/QUALITY.md`,
`corpus/SOURCES.md`, `SCORECARD.md`, `LOG.md`, `scripts/hyaku/jj-lane.sh`, `.ufo/reports/round-64/kama.md`.

## Findings

1. **Four of the five requested rows already exist at the tip**, written by the L1 at `23f341c8`: rows 1, 2, 3, 4 and 8
   of `corpus/lessons/round-64.md` are the socket-bound counter, the over-strong kill rule, the wrong idle rule, the
   cap-text/code mismatch and the `git add -N .` incident. My draft re-derives each against the wave-b files and
   tightens every pointer to a path:line; it creates nothing new.
2. **The `tracked=1536` figure has no committed receipt.** A lane-wide and fleet-wide search returns only the lesson
   row itself (`:38`), the fleet report's summary line (`.ufo/reports/round-64/kama.md:13`) and the wave-f item text
   — no `jj-lane.sh state` output was committed. The *mechanism* is independently reproducible and I reproduced it
   in a scratch fixture (`scripts/hyaku/jj-lane.sh:180` counts porcelain lines matching `^[ MADRCU][MADRCU ]`;
   `git add -N .` emits exactly those ` A` lines: 20 paths → `tracked=20`). The row should say so rather than cite
   a number with no artifact behind it.
3. **The AMENDMENT section names only 21 of the 42 wave-b seats** (20 by prefix, plus X03 inside the range
   "X02-X05"). Nine of the other 21 carry a survivor — MT02, MT07, MT09, MT12, RV01, CR01, CR02, CR04, SN01 — and
   their findings reach the amended instrument only through the amendment's generic clauses, not through a named
   fix. The `## Wave results` table marks each disposition, including three that no amendment covers: MT09's T03b,
   CR04's S1 and RV01's tool-side H1/H2 (the amendment explicitly left the tool byte-identical).
4. **The freeze's own control count is internally inconsistent**: the amended C1 sentence inside `freeze.txt:156, 159`
   reads "all 89 targeted controls" / "sum 89" while AMENDMENT 1a (`:192`) says the amended sentence reads 91 and
   `EXPECT_FAMILIES` sums to 91 — which is what the counter at `23b3fdb1` has (30 families, sum 91, computed).
5. **The freeze's C1 sentence is not byte-enforced.** `freeze.txt:21` says "the byte-pinned tools/kama-completion-live.py"
   and `:147` says "loading nothing from the tip", but the counter at `23b3fdb1` has no digest of the tool (only
   `MODEL_SHA` / `SERVER_SHA` at lines 56–57) and still reads the tool text and both forge patches from the tip blob.
   Wave-b CR01PredicateCode findings A and I are not named in any amendment and are not closed by one.
6. **The landed lesson has a structural defect**: rows 11 and 12 sit *after* the `## Wave results` heading
   (`corpus/lessons/round-64.md:42`, rows at `:47` and `:48`), so two Mistakes rows are not inside the Mistakes list.
7. **One landed statement is now false**: `corpus/lessons/round-64.md:44` says `MT06MapsLib` "wrote no report file,
   `ls b/MT06MapsLib.md` → no such file"; the file exists at the tip (187 lines, landed byte-exact from the fleet
   root at `361c620c`). The sentence describes attempt 1 and should be corrected or dated.
8. **The landed LOG entry's wave-f clause is stale**: `LOG.md:2535` says wave f was "stopped by the operator wrap-up
   with no reports" — attempt 1. Attempt 2 dispatched 42 seats on 2026-10-30 07:29:38
   (`.ufo/waves/round-64/f.ready.dispatched`) and seat reports are landing under `.ufo/waves/round-64/f/`; there is
   no `f-results.json` yet, so my LOG draft lands no wave-f finding and says "in flight".
9. **The wave-f attempt-2 measured receipts are untracked** (`.ufo/waves/round-64/measured/attempt2/`, the new
   `.ufo/waves/round-64/f/` reports): they resolve on disk but not in history, and must not be staged with
   `git add -N .` (see finding 2).

## Out of scope / not done

- No counter run, so no claim is scored and no verdict on C1 or C2 is offered or implied.
- No edit to `corpus/lessons/round-64.md`, `LOG.md`, `SCORECARD.md` or any other lane file: the drafts are proposals.
- No verdict on the wave-f attempt-2 seats' findings: 22 seat reports exist under `.ufo/waves/round-64/f/` at the
  time of writing, with no results file, so the wave is unsettled and the lesson draft covers wave b only, as the
  seat item specifies.
- The freeze's `89` vs `91` inconsistency (finding 4) and the unenforced "byte-pinned" clause (finding 5) are
  reported, not repaired: amending the frozen text is the L1's call, and the freeze says a rule change after seats
  scored must be a numbered amendment disclosed as such.

## Artifacts

- `.ufo/waves/round-64/f/out/SB05LessonAndLog/lesson-round-64-draft.md`
- `.ufo/waves/round-64/f/out/SB05LessonAndLog/log-round-64-draft.md`
- `.ufo/waves/round-64/f/out/SB05LessonAndLog/intent-to-add-mechanism.txt`

Wave-b tally (the one-line output this item's table is built on): seats=42 (mutation-tester 13, executor 10,
scout 6, critic 4, reviewer 3, scribe 3, connector 2, sentinel 1), all 42 returned output with note=null so 0 dead
seats are inferable; seats named in the freeze's AMENDMENT section=21 of 42; seats whose freeze-instrument finding
reaches the amended instrument only through a generic clause=9 (MT02, MT07, MT09, MT12, RV01, CR01, CR02, CR04,
SN01); acknowledged limits in the freeze=5 (freeze.txt:175-180); wave-f attempt 2=42 seats dispatched 2026-10-30
07:29:38, results file=0, wave not settled.
