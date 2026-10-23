Verdict: Three grounded mistake candidates are drafted; this is advice only, and no product lesson or README was edited.

## Axes and scope

Axes considered: chronology/provenance, seat accounting, artifact custody, and the specified C1 depth surface. The first three are incident classes, not proposed SCORECARD axis names. I mined the round-23 and round-24 lessons, round-24 and round-25 verifier spot-checks, round-25 lesson, current round-26 preregistration, and its recorded Git history. No subagent was dispatched and no tools were installed.

## Exact observations

- `corpus/lessons/round-25.md:53` records that round-25 amendments 2 and 3 had `written_utc` values later than their commits; it states amendment 1 had corrected the same class, and that critics caught the recurrence.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%h %cI %s' -- .ufo/waves/round-26/preregistration.json` returned:
  - `a23c0e0 2026-10-23T00:32:54-03:00 round-26: control wave receipts (AllFalse break under A0), pre-data amendment A1 (help/version exclusion in clause f), L1-run dead-seat controls, wave-1 spec`
  - `f071209 2026-10-23T00:20:14-03:00 round-26: preregistration timestamp correction (clock guesses replaced by commit times)`
  - `a12850c 2026-10-23T00:19:43-03:00 round-26: pre-data amendment A0 to the C1 counter clause (g), refrozen; before and pilot receipts re-run`
  - `a4a159c 2026-10-23T00:18:51-03:00 round-26: freeze C1 (depth) counter, preregistration, pinned 704366d sources, before receipts; resolve round-25 late falsify-seat outputs (routed defect 1)`
  - The tool returned these lines but did not expose a separate numeric shell exit status.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show a4a159c3:.ufo/waves/round-26/preregistration.json` showed historical `frozen_at_utc` as `2026-10-23T03:45Z`.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show a12850c5:.ufo/waves/round-26/preregistration.json` showed the same historical frozen value and A0's `2026-10-23T03:55Z`. These conflict with the corresponding commit times above.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show f071209a0f956680b5722e09242e784a1644e216:.ufo/waves/round-26/preregistration.json` showed the corrected values. The current `.ufo/waves/round-26/preregistration.json:6` records `03:18:51Z` for `a4a159c3`; `:29` records `03:19:43Z` for `a12850c5` and explicitly says the former `03:45Z`/`03:55Z` were wrong clock guesses. `git show -s --format='commit %H%ncommitter-date %cI%nsubject %s' f071209a0f956680b5722e09242e784a1644e216` returned commit `f071209a0f956680b5722e09242e784a1644e216`, committer date `2026-10-23T00:20:14-03:00`, subject `round-26: preregistration timestamp correction (clock guesses replaced by commit times)`. These Bash calls returned output; no numeric exit status was separately exposed.
- `corpus/lessons/round-25-verifier-spotcheck.md:49,55-61` says the closure observed 42 uncommitted paths under `.ufo/waves/round-25/a2-falsify/`, written after the last lane commit and before completion, and directed the lane to resolve them. Lines `:75-78` say the wave-2 reservation was released while 18 seats were still running although the report claimed it was held; `:228-229` routes the reservation defect and says to hold it until every seat returns.
- `.ufo/waves/round-26/preregistration.json:44` labels round-25 spot-check defects 1-7 as repair work items, not claims. The round-26 history's `a4a159c` subject also mentions resolving late falsify-seat outputs; neither is treated here as proof that every repair passed a gate.
- The read of `corpus/README.md` ended at line 400 with the round-25 Frontier disposition; no README edit was made. A search of current `SKILL.md` for `Round-26 live error signatures` returned “No matches found” at observation time, so `frontier.md` deliberately calls this a target surface and makes no landed-count claim.
- `mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/ScribeLessonMistakes` returned no text. The Bash tool did not expose a numeric exit status.

## Findings and artifacts

The three table rows, with evidence pointers, capture status, proposed fixes and discriminating fail-capable controls, are in `.ufo/waves/round-26/w1-build/out/ScribeLessonMistakes/mistakes.md`. The append-only frontier draft is in `.ufo/waves/round-26/w1-build/out/ScribeLessonMistakes/frontier.md`.

Only these permitted artifacts were written:
- `.ufo/waves/round-26/w1-build/out/ScribeLessonMistakes/mistakes.md`
- `.ufo/waves/round-26/w1-build/out/ScribeLessonMistakes/frontier.md`
- `.ufo/waves/round-26/w1-build/advice/ScribeLessonMistakes.md` (this report)

## Gates and limits

No counter, live llama-server, build, test, linter, or source-fetch run was performed. Proposed failure controls in `mistakes.md` are not execution evidence. The current landing count and repair disposition are unverified in this scoped scribe work. I did not modify `corpus/lessons/round-26.md`, `corpus/README.md`, `SKILL.md`, the frozen counter, or any other product surface. No installs or updates occurred.
