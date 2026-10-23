# VerifyA1Time — round-29 attempt-1 A1-time narrative

Seat: VerifyA1Time (kama w2). Read-only on the lane except this report. No tools installed. No git index writes.

Axes: (1) committer date of `75b78bb4`; (2) `corpus/lessons/round-29.md` states edit call `08:37:23.720Z` and result `08:37:23.732Z`; (3) SCORECARD.md round-29 section states the same pair. Keep a pass only if the quoted text is in the working tree that attempt 1 left.

## Verdict

| Check | Result |
|---|---|
| `git log -1 --format='%H %cI' 75b78bb4` committer date is `2026-10-23T05:38:16-03:00` | **PASS** |
| Lesson A1-time correction states call `08:37:23.720Z` and result `08:37:23.732Z` | **PASS** |
| SCORECARD.md round-29 section states that same pair | **FAIL** |

Overall: the inherited narrative is only half-confirmed. The lesson has the millisecond pair; neither SCORECARD round-29 heading does.

## Command output (observed)

Repo: `/home/vgpnk/Projects/shokunin/kama-shokunin`. HEAD at check: `513eba3ba51a142c9936553e3a85918345eb5c4c`.

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin log -1 --format='%H %cI' 75b78bb4
75b78bb4900aae1edcdb6b229bb8c572c20fcbce 2026-10-23T05:38:16-03:00

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse 75b78bb4
75b78bb4900aae1edcdb6b229bb8c572c20fcbce

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin log -1 --format='commit %H%nauthor %aI%ncommitter %cI%nsubject %s' 75b78bb4900aae1edcdb6b229bb8c572c20fcbce
commit 75b78bb4900aae1edcdb6b229bb8c572c20fcbce
author 2026-10-23T05:38:16-03:00
committer 2026-10-23T05:38:16-03:00
subject round-28: C1 amendment A1 (generic-conversion refusal in clause e) before any data row lands; A1 pilot receipts
```

Abbreviated `75b78bb4` resolves to full hash `75b78bb4900aae1edcdb6b229bb8c572c20fcbce`. Author date equals committer date. `%cI` matches the required `2026-10-23T05:38:16-03:00` (08:38:16Z).

Working-tree status of the two narrative files (attempt-1 leftovers, not edited by this seat):

```
 M SCORECARD.md
?? corpus/lessons/round-29.md
```

## Lesson (PASS)

File (untracked): `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-29.md`, snapshot tag `9381`.

Repairs table row 2 (line 70) points at the append and records the committer date, not the millisecond pair:

```
| 2 | A1 time | corrected by appended record below; frozen bytes untouched | `w1/out/ScribeA1TimeCorrection/evidence.txt`; `git log -1 --format=%cI 75b78bb4` = `2026-10-23T05:38:16-03:00` |
```

The A1-time correction itself (lines 79–84) does state both timestamps:

```
**Round-28 A1 amendment-time correction (append-only; drafted by ScribeA1TimeCorrection).** The
frozen `.ufo/waves/round-28/preregistration.json` `pre_data_amendment_A1` text says "Written
2026-10-23 ~08:45Z"; that time is wrong. The authoring record logs the A1 edit call at
08:37:23.720Z and its result at 08:37:23.732Z, and commit `75b78bb4` is dated 08:38:16Z. This
correction leaves the frozen bytes untouched. It does not imply A1 preceded all data evaluation:
DataG01 ran A0-counter functions at 08:35:54Z, before the edit (`w1/out/ExecTimingTranscript/`).
```

Exact strings present: `08:37:23.720Z` (edit call) and `08:37:23.732Z` (result).

## SCORECARD round-29 (FAIL)

File (modified, unstaged): `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md`, snapshot tag `76F7`.

Two round-29 sections, both read in full (lines 1443–1498):

- `## Round 29 — self-assessment corrections` (line 1443) — eleven SA29 rows. No A1 time text.
- `## Round 29 — self-assessment evidence at writing (calibration); round-28 repairs (2026-10-23, attempt 1)` (line 1466) — C1 table plus repairs paragraph.

`grep` of `08:37:23` over the whole SCORECARD.md: **no matches**. The repairs sentence (lines 1495–1496) only names the misdate, it does not state the call or result times:

```
Repairs (routed by `corpus/lessons/round-28-verifier-spotcheck.md`, not claims): items 1-9,
lesson §Repairs. Mined mistake: `tools/prereg-time-check.py` missed the round-28 A1 misdate; fixed
```

The C1 evidence cell points at `corpus/lessons/round-29.md` but does not itself state `08:37:23.720Z` or `08:37:23.732Z`. A pointer is not the statement the item asked to confirm.

`git diff -U0 -- SCORECARD.md` hunks that mention Round 29 / A1 contain the same prose and no millisecond timestamps. The unstaged round-29 block is the attempt-1 narrative under check.

## Adjacent (not one of the two required texts)

Working-tree `LOG.md` round-29 (modified, lines 1846–1847) says `edit 08:37:23Z, commit 08:38:16Z`, whole seconds only. It does not split call `.720Z` from result `.732Z`. Not a substitute for the SCORECARD miss.

## Confidence and gaps

Confidence high on all three checks: command output and file text were read this turn. Not done, and not required: re-opening the round-28 authoring transcript to re-prove that `.720Z`/`.732Z` are true of the edit. This seat checks whether the attempt-1 narrative states them, and whether the committer date matches.
