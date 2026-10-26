Verdict: KQ65 sample delivered — 138 hand-labeled claim-outcome lines from all 12 rounds (34-45) on both sides, each byte-verified against the revision it cites (138/138, 0 mismatches); no reader written, no counter run.

# S8Sample3 — KQ65 hand-read sample control (round 46, lane kama)

Scope: round-45 closure D1 asks that a hand-read sample for a future claim-outcome reader be
committed before any new reader exists. This seat produced the sample only. Nothing in the lane
was executed, edited, committed or scored; the lane and the fleet repo were read with `git show`.

## What was read

| Side | Path pattern | Rev read | Rounds | Exit |
|---|---|---|---|---|
| self | `.ufo/reports/round-<N>/kama.md` | `9b676be886e1e2a428fa81321a05a16363ca68ac` (fleet HEAD of `9b676be88 round-45: hyaku closure dispatch for mado`) | 34-45 (12/12 present) | 0 |
| outside | `corpus/lessons/round-<N>-verifier-spotcheck.md` | `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` | 34-45 (12/12 present) | 0 |

Commands (one per file, all exit 0):
`git -C /home/vgpnk/Projects/shokunin show HEAD:.ufo/reports/round-<N>/kama.md` and
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050:corpus/lessons/round-<N>-verifier-spotcheck.md`.
Byte counts: fleet reports 58-372 lines each, closures 80-220 lines each; 24 files, 450 092 bytes,
copied to `sources/` with `sources.sha256`. Both revisions are the ones the item names, so no
`HEAD`-drift question arises; every round 34-45 has a closure file, therefore the rounds 20-23
`MANIFEST.json` branch of the item was not used.

## Deliverable

`sample.tsv` — 9 columns exactly as the item lists them
(`round claim side path rev line outcome class text`), 138 rows.
`sha256 039bc76db24c73d8846b992378381f79aa5f8b761aafe9435e4aefb6c5d589b9`.

Provenance check (the one program this seat ran over the data; it copies bytes and compares them,
it classifies nothing and writes no reader):

```
$ python3 - <<'EOF'   # for each (path, rev, line): `git show <rev>:<path>` split, compare row text
checked 138 mismatches 0 []
EOF
```
138/138 rows are byte-equal to the cited revision's line; 0 duplicate (path,line) pairs; every
row has 9 tab fields. Lines were chosen by hand, round by round, after reading every file end to
end; the counters were never executed, so nothing in the sample depends on a lane instrument.

## Shape (what a future reader is scored against)

- 59 self rows, 79 outside rows. Claims: C1 56, C2 55, C3 14, `C1;C2` 9, `C1;C2;C3` 4.
- Outcomes: met 103, not-met 25, unprovable 6, mixed 3, partial 1.
- Classes: measurement-only 62, table-row 36, outcome-word 23, multi-claim-line 13, other 4.

Four traps, quantified — these are the reason the sample exists:

1. **85 of 138 rows carry no literal `C1`/`C2`/`C3` token.** A `\bC[123]\b` reader reaches
   only 53/138 = 38.4 % recall. The missing 85 are identified only by subsection scope, e.g.
   `f36:109-121` (round-36 measurement bullets), `f41:74-83`, `f42:65-80`, `f43:51-62`,
   `f44:78-95`, `c34:34-47`.
2. **55 of 138 rows contain no `met` token.** They state the outcome as a gate tally
   (`f34:149` `registered 12 unregistered 0 defective 0`; `c34:46`, `c34:47`), as a verdict
   word (`c34:40` `verified (re-measured)`; `c40:49` `unprovable`), or as an axis row carrying
   the claim id (`c41:55-56`, `c42:74-76`, `c43:72-74`, `c44:75-76`, `c45:113-114`). A
   `met`-token reader reaches at most 83/138 = 60.1 %.
3. **8 rows are physical fragments of a wrapped counter output** — round 36 puts `met` on one
   line and `False`/`True` on the next: `f36:109-112` (C1) and `f36:118-121` (C2). Neither line
   alone is a complete statement; a line-at-a-time reader must join them.
4. **30 rows carry two or more `met` tokens on one line.** 13 of them fold a base state and a tip
   state into the same line — `f34:148`, `f35:41`, `f35:42`, `f37:30`, `f37:31`, `f38:11`,
   `f38:15-17`, `f38:48-50`, `c43:34` — and the row's outcome is the tip state while the base
   state on the same line is `not-met` for the same claim. The other 17 use the second token for
   a second state of the same value (`f40:35`), the kill-rule phrase (`f43:52`), a capability
   census (`f41:83`, `f42:73`), a limit sentence (`f43:57`, `f45:46-47`) or a line covering
   several instruments (`c38:31-33`, `f42:80`, `f44:95`).

`boundary.tsv` holds the 32 lines I rejected with a reason each (control receipts, counter
selftests, counter limits, axis trends that do not state a claim status, regression lines for
other rounds' instruments, non-claim census statements, one out-of-population reading).
Nothing was left unlabeled.

## Findings

**F1 (design, not a lane defect): two frozen class values have no in-population example.**
`qualified-met-not-admitted` and `manifest-field` do not occur in rounds 34-45. No line in the 24
sources both states `met` and refuses admission: `grep -n -i 'not admitted' sources/*.md` returns
four hits — `c40:105` and `f40:296` (both already sampled as `mixed`), the out-of-population
reading at `c45:129`, and the `NOT met` line at `f45:47`. A reader calibrated on this
sample alone can never be tested on those two classes, while round-45 D1 asks for "every
phrasing class". Proposed fix for the next round that freezes a reader (not this one): extend
the population to the closures that contain the class, or narrow KQ65's class list to the five
classes with members here. Evidence commands (both exit 0):
`git -C kama-shokunin show 4a2a4d55:corpus/lessons/round-31-verifier-spotcheck.md | grep -n 'not admitted'`
→ line 44 (`met on frozen counter but no-op control also meets it — not admitted`);
`… round-25-verifier-spotcheck.md | grep -n 'not a calibration axis-move'` → line 20;
fleet `.ufo/reports/round-31/kama.md:81` at `9b676be8` reads
`Verdict: **met on the frozen counter; NOT admitted**`.

**F2 (schema gap): the outcome enum has no `unverified`.** Round 40 files both claims as
`unverified`/`verified` (`f40:14`, `f40:15`) and closure 40/45 rule `unprovable` on the same
facts (`c40:49`, `c45:88`, `c45:114`). I mapped `unverified` → `unprovable` and recorded the
mapping in `notes.md`; a reader frozen against the six-value enum needs the same rule stated, or
the two rounds will score as label errors. Evidence: `f40:14` "C1 — unverified"; `c40:49`
"Ruling: **unprovable.**".

**F3 (data): the round-34 self side states C2 only as a gate tally.** `f34:149` is the whole
self-side C2 outcome for round 34 — no `met` word, no other claim-outcome line for C2 in the
file. `git show 9b676be8:.ufo/reports/round-34/kama.md | grep -n 'met '` returns lines 21
(predicate prose), 87 ("L2 floor is met") and 148 (C1's `met True`/`met False` cell) — none is a
C2 outcome. This is a true positive a `met`-token reader loses (trap 2 above); it is not a lane
error under round 34's frozen counter, which prints the gate tally rather than a `met` flag.

**F4 (label call, documented not hidden):** three rows are arguable and are kept as labeled —
`f37:46` excluded (axis trend that mentions "the C1 counter"), `f40:293` included
(`unprovable`/`other`, because it states "C1's measurement failure … not counted as a pass"),
`c39:33` labeled `partial` (C1's attempt-1 receipt is not reproducible while the substance is
met in `c39:32`). Moving any of the three changes the population by one row; a reader scored
against this sample should be judged with that tolerance stated.

## Constraints observed

- No reader written, no claim counter run, no scoring of any claim this round.
- Lane and fleet repos read-only; no `git add/commit/checkout/stash/reset`, no jj command, no
  write outside `out/S8Sample3/`. No subagents, no service start, no `agent://all`.
- No tool installed or upgraded (nothing needed); pacman not run.
- Scratch `/fast/scratch/hyaku/kama-r46/S8Sample3` removed after the sources were copied into the
  out directory; no `/tmp` path is cited as evidence.

## Files written (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample3.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample3/sample.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample3/boundary.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample3/notes.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample3/sources.sha256`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample3/sources/round-<N>-{fleet-report,closure}.md` (24 files)
