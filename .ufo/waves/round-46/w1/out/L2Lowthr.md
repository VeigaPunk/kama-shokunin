# L2Lowthr — round-46 kama, hypothesis test: below-threshold deletions in the five append-only files

**Verdict: FALSIFIED as stated.** Below the 20-line threshold the five declared append-only
files carry **61 deletion events / 213 deleted lines**; **23 of those events (71 lines) are
neither a `SOURCES.md` mutable-cell change, nor a `SCORECARD` head re-derivation, nor restored
later**. No event is wholly unexplained *somewhere at tip* (every one carries a commit subject,
a same-commit disclosure parenthetical, or a falsify-advice record), but two are not recorded in
the append-only file itself: the `S192` id aliasing (`54c6f4fe`) and the round-26 filed outcome
flip (`fd48f9a3`). The lane's own C2 contract cannot see any of this: its threshold is 20 and
its fixture asserts that a 5-line deletion yields **no** event.

## 1. Commands and receipts

Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only), audited revision
`4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`; tool is the lane's own, run read-only.
Scratch `TMPDIR=/fast/scratch/hyaku/kama-r46/L2Lowthr`.

```
$ python3 tools/append-only-audit.py --repo <lane> --to 4a2a4d55… --threshold 1
event 026eede9… SCORECARD.md deleted=1 …        (61 events below 20 + 5 at/above 20)
summary commits=294 events=66 restored=11 partial=6 unrestored=49
exit=1

$ python3 tools/append-only-audit.py --repo <lane> --to 4a2a4d55… --threshold 20
event dd9f5dc6c0e6 SCORECARD.md deleted=31 restored_at_tip=24 status=partial
event 0718b6abbda6 SCORECARD.md deleted=2417 restored_at_tip=2416 status=partial
event 0718b6abbda6 LOG.md deleted=2290 restored_at_tip=2290 status=restored restored_by=82b5e9d3…
event 0718b6abbda6 corpus/QUALITY.md deleted=375 restored_at_tip=375 status=restored restored_by=82b5e9d3…
event 0718b6abbda6 corpus/README.md deleted=663 restored_at_tip=663 status=restored restored_by=82b5e9d3…
summary commits=294 events=5 restored=3 partial=2 unrestored=0
exit=1
```

The threshold-20 run reproduces the contract text of `tools/round46-append-audit-check.py`
(5 events, same restore/partial split) exactly. The events ≥ 20 are out of scope for this seat.
`--json` output is in `thr1.json`; per-event diffs were re-read with
`git -C <lane> diff -U0 <c>^1 <c> -- <file>` and each deleted line was re-tested against the
file at `4a2a4d55` and against every later commit's blob (own recomputation, not the counter's).

Per-file split of the 61 sub-threshold events / 213 lines (outside-the-three-classes in
parentheses):

| file | events | lines | outside | outside lines |
|---|---|---|---|---|
| SCORECARD.md | 21 | 96 | 5 | 18 |
| corpus/SOURCES.md | 20 | 65 | 3 | 6 |
| LOG.md | 12 | 28 | 8 | 24 |
| corpus/README.md | 7 | 22 | 6 | 21 |
| corpus/QUALITY.md | 1 | 2 | 1 | 2 |

## 2. Classification rules used

- **A — `SOURCES.md` mutable cell**: every deleted line is a registry row whose same-commit
  successor keeps the same `id` and differs only in `status` (col 8), `recheck` (col 10) or
  `used-by` (col 11) of the header at `corpus/SOURCES.md:10` (the cells KQ22 allows,
  `corpus/QUALITY.md:123`). No row dropped.
- **B — `SCORECARD` head re-derivation**: every deleted line lies in the standing
  self-description — preamble, or a section whose heading is `Axes`, `Planned`, `Retired`,
  `Move log`, `Capabilities`, `Saturation` (the surfaces `tools/round42-selfdesc-reconcile.py`
  reconciles plus `Move log`; `## Actual round 5` and the `## Round N` log excluded).
- **C — restored later**: every deleted line text is held again by a later commit
  (`restored_by` non-null), which also covers the two pure row-move events.
- **F1 — same-commit rewrite, near successor survives** (out of A/B/C).
- **F2 — same-commit rewrite with deleted lines that have no near successor line**
  (difflib ratio < 0.6 against every added line of the same diff) (out of A/B/C).

## 3. Counts per class

| class | events | lines |
|---|---|---|
| A `SOURCES` mutable cell (status/recheck/used-by only) | 15 | 40 |
| B `SCORECARD` head re-derivation | 16 | 78 |
| C restored later | 7 | 24 |
| **F1 in-place rewrite, successor survives** | **14** | **29** |
| **F2 in-place rewrite, no near successor** | **9** | **42** |

13 of the 15 A events change only `used-by`; `0df800e8` changes only `status` (`S095` mined →
rejected); `3285cdf7` changes `status`+`used-by`. Examples: `f1e755e0` `corpus/SOURCES.md`
11 rows (S083, S089, S094-S104) used-by only; `6433390a` 6 rows used-by only; `ef76777e`
S480/S481 used-by only. B examples: `44fa5627` 9 lines (banner, Axes rows, Planned, Retired,
Capabilities mirror, Saturation); `ef76777e` 18 lines (the round-43 `## Planned` corruption
repaired); `21945c61` 3 lines (banner, calibration row, Planned). C examples: `382d11b2`
(12 rows moved, restored at `bda324bb`), `5890d1a0` (7, restored at `b784e1ab`), `83bee7fa`
/`33b167ec`/`ea72c3ea` LOG last-line re-writes restored by the next commit.

Era split: **47 events / 153 lines are at or after round 10**, when KQ7 first declared the
append-only correction rule; of those, **17 events / 49 lines are outside A/B/C** (11 F1,
6 F2). The other 14 events / 60 lines are rounds 1-5 (`c6199a25`, `83bee7fa`, `33b167ec`,
`ed135b3c`, `ea72c3ea`, `84a81304`, `47f3aedd`, `e246c40e`), before the declaration.

## 4. Every event outside the three classes (the falsifiers)

| commit | round | file | del | test | class | what the commit says it did |
|---|---|---|---|---|---|---|
| `c6199a25` | 1 | corpus/README.md | 5 | no near succ. | F2 | round-1 operability axis (census built in place of the "(empty …)" placeholder) |
| `83bee7fa` | 2 | corpus/README.md | 4 | no near succ. | F2 | round-2 |
| `ed135b3c` | r4 | LOG.md | 7 | no near succ. | F2 | Revert "HOURS.md: craft-hours ledger opened" |
| `ea72c3ea` | 3 | corpus/README.md | 3 | prose rewrite | F1 | round-3 re-census |
| `47f3aedd` | 4 | LOG.md | 1 | prose rewrite | F1 | lane-root-resolvable pointers |
| `e246c40e` | 5 | corpus/README.md | 2 | prose rewrite | F1 | round-5 runbook freshness |
| `726f737a` | 16 | corpus/README.md | 6 | no near succ. | F2 | falsify-wave repairs, doc-correction ledger |
| `ccc4bb31` | 16 | corpus/SOURCES.md | 1 | prose rewrite | F1 | S041 `anchor`+`teaches` rewritten in place |
| `f4066979` | 26 | LOG.md | 3 | no near succ. | F2 | LOG candidate count corrected |
| `fd48f9a3` | 26 | SCORECARD.md | 6 | no near succ. | F2 | calibration fixes, no depth promotion |
| `fd48f9a3` | 26 | LOG.md | 5 | no near succ. | F2 | same commit |
| `4d2e74f4` | 27 | SCORECARD.md | 4 | no near succ. | F2 | measured-commit fix, defect prose |
| `6de225c2` | 29 | SCORECARD.md | 4 | prose rewrite | F1 | SA29 citation cells `path:line` → `path lines N` |
| `9cb3abae` | 29 | LOG.md | 1 | prose rewrite | F1 | working-tree → landed-tool wording |
| `026eede9` | 30 | SCORECARD.md | 1 | prose rewrite | F1 | appended heading `## Round 30 — self-assessment corrections (recall population)` renamed |
| `54c6f4fe` | 31 | corpus/SOURCES.md | 4 | prose rewrite | F1 | S190/S191 `source`+`scope`+`anchor`+`teaches` re-mapped, row S192 dropped |
| `e97ce496` | 37 | corpus/QUALITY.md | 2 | no near succ. | F2 | "harden KQ46 wording" (heading + KQ46 row replaced, 92 s after first landing) |
| `ce41bae6` | 38 | SCORECARD.md | 3 | prose rewrite | F1 | `{{C1_AFTER_LINE}}` placeholders filled in place |
| `ce41bae6` | 38 | LOG.md | 4 | prose rewrite | F1 | `{{MEASURED_COMMIT}}` placeholders filled in place |
| `2793eb51` | 42 | corpus/README.md | 1 | prose rewrite | F1 | coverage-map cell gains full path |
| `8bc8e375` | 42 | corpus/SOURCES.md | 1 | prose rewrite | F1 | S478 `anchor`+`teaches` rewritten in place |
| `2c018107` | 42 | LOG.md | 1 | prose rewrite | F1 | round-42 C1 bullet re-worded |
| `8bee4e56` | 43 | LOG.md | 2 | prose rewrite | F1 | control/Mistakes counts re-worded |

## 5. Counterexamples tested

**(a) The strongest mechanical falsifier — `54c6f4fe` (round 31), `corpus/SOURCES.md`.**
4 lines, none a mutable cell, none restored:

```
$ git -C <lane> diff -U0 54c6f4fe^1 54c6f4fe -- corpus/SOURCES.md
-| S189 | … server-common.cpp#L1530 | code | A | every remaining request key is copied … before the schema prunes unknown or undeclared keys | …
-| S190 | … server-common.cpp#L1530 …          (source, scope, anchor, teaches)
-| S191 | … server-schema.cpp#L47 …            (source, scope, anchor, teaches)
-| S192 | … server-schema.cpp#L64 …            (row deleted)
+| S189 | … server-common.cpp#L1530 | code | A | every remaining request key is copied … before the schema keeps only what it declares … |
+| S190 | … server-schema.cpp#L47 …             (was S191)
+| S191 | … server-schema.cpp#L64 …             (was S192)
```

This is an immutable-cell rewrite plus a row removal, i.e. exactly what KQ22
(`corpus/QUALITY.md:123`) forbids without a new `supersedes` row or a knowledge entry, and it
is invisible at threshold 20. It also changes identity: `S192` later denotes a **different**
source (OpenAI Chat Completions `response_format`, from `c16fe3e5`, round-31 attempt 3), while
a citation `S192` written between `3b1e84f8` and `54c6f4fe` meant the `n_cmpl` alias row. At
tip this is `corpus/SOURCES.md:203` (S191 = the n_cmpl row) and `:204` (S192 = OpenAI). The
drop is named in the commit subject; the id reuse is not recorded in `SOURCES.md` nor in the
round-31 lesson's id table. Fix: `proposed-sources-s192-alias-note.md` (appended note, no line
moves).

**(b) The largest unrecovered loss — `ed135b3c` (2026-10-13), `LOG.md`.** 7 deleted lines,
`restored_at_tip=2`: the entire appended section

```
-L199 fallback. No failure was forced and no route/mission config was changed.   ← last-line rewrite, restored
-L200 ## 2026-10-13 — HOURS.md ledger opened                                     ← gone
-L202-L205 (4 content lines)                                                     ← gone
```

is removed by a full revert of `33b167ec` (which had added `HOURS.md` itself, 12 lines, also
gone: `git ls-tree -r --name-only 4a2a4d55… | grep -i hours` → nothing; `git grep "HOURS.md
ledger opened"` at tip → nothing). The withdrawal is disclosed by the revert subject; the
append-only `LOG.md` still lost an appended entry permanently, below the counter's threshold.

**(c) The most consequential in-place reversal — `fd48f9a3` (round 26), `SCORECARD.md:1321`
(then) → `SCORECARD.md:1373` (tip).**

```
-| C1 | depth 7 → 8 (author reading; the closure decides) | …
+| C1 | depth 7 → 7 (no promotion: after data a shortcut control also met the frozen counter, 12/12 with no error knowledge; lesson §Mistakes row 3) | …
```

A filed claim outcome changed from a claimed promotion to no promotion by rewriting the row
that was first filed at `7f84cd0e`. The same commit appends a disclosure parenthetical
(`+(Corrected before the report; the first landed text said SKILL.md held only the September
sample…)`, diff line 26) — but that parenthetical covers the SKILL.md prose, not the 7→8 → 7→7
flip: `git grep -c "author reading; the closure decides" 4a2a4d55…` → 1 hit, and it is
`.ufo/waves/round-26/w2-falsify/advice/CriticAxisAndHarm.md`, i.e. outside the append-only
file. KQ26 (`corpus/QUALITY.md:143`) asks that corrections to append-only records be appended
with the superseded text named. Fix: `proposed-scorecard-round26-note.md`.

**(d) Within-round authoring, not a loss:** `e97ce496` replaced the KQ46 heading and row 92 s
after `09b4d36e` introduced them (both 2026-10-25 05:03-05:04), before any report or lesson
filed that text; `ce41bae6`, `026eede9`, `6de225c2`, `9cb3abae`, `2793eb51`, `2c018107`,
`8bee4e56`, `f4066979`, `4d2e74f4` are same-round or placeholder-filling edits. They are
literals of the hypothesis's exclusion ("no deletion that is neither…"), not losses of filed
content.

## 6. Impacted axes

- **calibration (7)** — the lane's append-only self-description is a *≥ 20-line* claim. Below
  that line sit 61 events / 213 lines, 17 events / 49 lines of them after round 10, including
  an id-space aliasing and an in-place reversal of a filed outcome. C2 cannot see them by
  construction: its fixture (`tools/round46-append-audit-check.py`, `fixture` leg) plants a
  5-line deletion that **must** produce no event. My seat does not change C2's verdict
  (capability present, selftest/fixture/lane/table legs untouched).
- **operability (8)** — the tool is correct on its own contract: exit 1 on partial/unrestored,
  exact reproduction of both event sets, restored_by resolved (`82b5e9d3`), and it distinguishes
  restored/partial/unrestored exactly as documented. No defect found in
  `tools/append-only-audit.py`.

## 7. Smallest safe correction

1. **Restate the hypothesis** (if it is to be re-used): add two permitted classes —
   *F1, same-commit rewrite whose successor line survives* and *declared withdrawal (revert
   commit naming the reverted commit)* — and define "unexplained" as *no disclosure at tip*.
   Under that restatement the hypothesis holds; under the text as frozen it does not.
2. **Two appended notes** (full proposed text in this directory, not applied, no line moves):
   `proposed-sources-s192-alias-note.md` (the `S189-S192` remap and the `S192` id aliasing) and
   `proposed-scorecard-round26-note.md` (the superseded round-26 C1 outcome, quoted).
3. **Next freeze only** (counters are frozen this round): either run the tool at
   `--threshold 6` at round end, or add a below-20 detector that classifies events with the
   A/B/C/F rules above; a threshold of 20 leaves a 213-line band unmonitored, and the two
   defects above both live in it.

## 8. Limits of this seat

Read-only on the lane and the bare clone; no counter, preregistration or control edited; no
lane file modified; no git/jj mutation anywhere. The F1/F2 split uses a difflib ratio < 0.6
against the same-commit added lines as the "no near successor" test, then each F2 event was
read by hand; prose rewrites that reorganise a sentence (e.g. `726f737a`) are counted as
losses of the *line text*, not of the *content* — the content audit is stated per event in the
ledger `note` column. Nothing here is a verdict on C1.

## Files

- `ledger.tsv` — all 61 sub-threshold events with class + per-event mechanism.
- `class_counts.tsv`, `thr1.out`, `thr1.json`, `thr20.out` — receipts.
- `sources_cell_detail.tsv` — the non-mutable `SOURCES.md` cells (`ccc4bb31` S041, `54c6f4fe`
  S189-S192, `8bc8e375` S478) plus the blank-line move in `5890d1a0`, row by row.
- `evidence/*.diff` — the 11 diffs cited above (`fd48f9a3`, `ed135b3c`, `33b167ec`,
  `54c6f4fe`, `ccc4bb31`, `8bc8e375`, `e97ce496`, `726f737a`, `4d2e74f4`, `f4066979`).
- `proposed-sources-s192-alias-note.md`, `proposed-scorecard-round26-note.md` — proposals.
