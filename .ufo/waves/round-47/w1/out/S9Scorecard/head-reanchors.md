# S9Scorecard — head re-anchors round 47 must make

Line numbers are at `46a924e0` (the lane's tip when this seat ran; build
`3a09a1d9`). "Read by" names the leg of the frozen head counters that reads
the line; "truth" means no counter reads it but the tree contradicts it.

| # | Line | Now | Required | Read by | Evidence |
|---|---|---|---|---|---|
| 1 | `SCORECARD.md:6` | "**Current authority (round 46):**" … "Latest measured round: 46." … "kept current in rounds 43, 44, 45 and 46;" | "…(round 47)… Latest measured round: 47. … kept current in rounds 43, 44, 45, 46 and 47;" | r42 `banner` (`Latest measured round: <maxN>`); the other two fragments are truth | `reconcile42-final-a.out`: `detail: banner: head lacks 'Latest measured round: 47'` |
| 2 | `SCORECARD.md:18` | "→ 32 (outside closures on record)" | "→ 33" | r41 `run` fact | `ls corpus/lessons/*verifier-spotcheck.md \| wc -l` → 33; `reconcile41-final-a.out`: `run_bad=1`, `detail: calibration run … no stdout line == '32'` |
| 3 | `SCORECARD.md:18` | "latest outside closure `corpus/lessons/round-45-verifier-spotcheck.md` (rejected-honest-stop; re-anchored round 46)" | "…round-46-verifier-spotcheck.md` (admitted; re-anchored round 47)" | truth | `corpus/lessons/round-46-verifier-spotcheck.md:13`: `Verdict: **admitted** (status ok, admitted true)` |
| 4 | `SCORECARD.md:18` | last cell "evidence re-anchored round 45" | "…round 47" | truth | the row's facts change this round |
| 5 | `SCORECARD.md:53` | "The live plan is `### Planned (round 47)` at the end of this file" | "(round 48)" | r42 `planned`; `planned-pointer-check.py` for contiguity | `reconcile42-final-a.out`: `detail: planned: section does not name '### Planned (round 48)'` |
| 6 | `SCORECARD.md:130` | the append-only-audit row describing "the lane's five append-only self-description files" | the v2 row from `canon-round-47.md` (contract-declared set, numstat-equal deletions, window maximum) **plus a new `live-receipt-replay` row** | r42 `caps` (names must equal the canon) | `reconcile42-final-a.out`: `detail: caps: head names [… 10 names …] != canon (round 47) [… live-receipt-replay …]` |
| 7 | `SCORECARD.md:117` | "Mirror of the round-46 canonical capability list that §Round 46 carries" | "round-47" / "§Round 47" | truth (`caps` reads names) | `caps=0` at final-b with the canon block as of 47 |
| 8 | `SCORECARD.md:57` (§Retired) | "None. 6 axes and 10 capabilities remain active." | "None. 6 axes and **11** capabilities remain active." | r42 `retired` | `reconcile42-final-a.out`: `detail: retired: does not state '11 capabilities'` |
| 9 | `SCORECARD.md:136` (§Saturation) | "capability first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46 (highest canonical list)" | same list **plus `, 47`** | r42 `saturation` | `reconcile42-final-a.out`: `detail: saturation: does not state 'first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47'` |
| 10 | `SCORECARD.md:136` (§Saturation) | "(kept current in round 46)" / "A capability entered in round 46, so the window is not exhausted either." | "(kept current in round 47)" / "A capability entered in round 47, so the window is not exhausted either." | truth | an 11th capability enters this round, so the window's last entry moves |
| 11 | `PROVINCE.md:17` | "`tools/append-only-audit.py` with `tools/round46-append-audit-check.py` (append-only audit of the five append-only self-description files: …; round 46)" | `registry/append-only-contract.tsv` + `tools/round47-append-audit-v2-check.py` in the append-only clause, and a `tools/kama-live-replay.py` clause (full text in `head-reanchors.diff`, byte-identical to seats S9Cap's companion edit) | r42 `province` | `reconcile42-final-a.out`: three `detail: province: PROVINCE.md lacks …` lines |
| 12 | `SCORECARD.md:17` (coverage row) | "surface list `PROVINCE.md` sha256 659a5101… (186 lines)" | "sha256 929f3e3eef20fa90429ca0c5a96a63821cff6aeca912ac55bad3a82b4bd3a079 (186 lines)" | r41 `HASH` | forced by #11; `reconcile41-without-coverage-reanchor.out`: `hash_bad=1`, `detail: coverage sha256 PROVINCE.md cited 659a5101… observed 929f3e3e…` |
| 13 | `SCORECARD.md:16` (depth row) | "`SKILL.md` sha256 1ad95066… (1442 lines); `grep -c '^## '` → 34" | **only if SKILL.md gains the round-47 registry rows**: sha256 from the applied bytes, line count, `## ` count. Probe with seat S9Skill's rows: `682fba3bf87ea43cb5494fb00ae091c92eed50b49e6ebd00e3484d29876a2616`, 1463 lines, "→ 35". **The lane's working tree at report time carried the L1's own rows: `ddb80f6e275d345badd2fd554b0759842d8287387a4579affe71143e0e783555`, 1463 lines, 35 headings** (measured, uncommitted) | r41 `HASH`, `LINES`, `RUN` | `reconcile41-with-skill-rows.out` (`hash_bad=1 lines_bad=1 run_bad=1`); re-anchored in `reconcile41-depth-reanchored.out` (`mismatches=0`); working-tree read: `sha256sum SKILL.md`, `wc -l < SKILL.md`, `grep -c '^## ' SKILL.md` |

**Row 13 is computed from the applied blob, never from a working-tree file
that still has unstaged edits** — the counter reads `SKILL.md` at the audited
commit, so the sha256/line/heading facts must be those of the final bytes, e.g.
`git show :SKILL.md | sha256sum` and `git show :SKILL.md | grep -c '^## '`
after staging, or the same reads at the measured commit after the fact. The
`ddb80f6e…`/1463/35 figures above are a working-tree reading and are labelled
as such.

## What stays put, verified rather than assumed

- **Score vector** `operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7` — C1 is 7 → 7 and C2 8 → 8, so no score cell moves and `r41` stays `score_bad=0`. The capability entry is a table event, not a score move.
- **Capacity count is not the capability count**: `6 axes` in §Retired is unchanged.
- **`## Planned` pointer contiguity** — the round-47 section and its plan are appended at EOF (after `### Planned (round 47)` at `SCORECARD.md:2677`), never inside the pointer sentence: `planned-pointer-final-b.out` → `met=True`, exit 0. The failing shape is reproduced in `planned-pointer-inside-pointer-demo.out` (a block inserted mid-sentence → `pointer: … lacks the contiguous …`, exit 1), which is round-43 D1 and the round-46 repeat.
- **No ledger regression** — `digest-ledger.py scan` at final-b: `tokens=113 blob=99 external_ok=7 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0` (`digest-ledger-final-b.out`); `hexrun-census.py scan`: `tokens=1776 distinct=283 … unknown=22` (`hexrun-census-final-b.out`), the same unknown count as the build (`unknown=22`).

## Validation state

| Variant | Clone commit | r41 | r42 | pointer |
|---|---|---|---|---|
| section only (`final-a`) | `7ba2c796bf604d426c9c3a61d0652f5b30d88624` | `mismatches=1 met=False` (exit 1) | `r41=1 banner=1 planned=1 retired=1 saturation=1 caps=1 province=3 mismatches=9 maxN=47 met=False` (exit 1) | `met=True` (exit 0) |
| section + all head re-anchors (`final-b`) | `1d9102972faf84d38ee0a78e37ded85193ad040c` | `mismatches=0 met=True` (exit 0) | `mismatches=0 maxN=47 met=True` (exit 0) | `met=True` (exit 0) |
| final-b with #12 reverted | `b0c499be00d2a9a2b7f2daf47f1e6a25e0eaf464` | `hash_bad=1 mismatches=1 met=False` | — | — |
| final-b + S9Skill SKILL rows, #13 not applied | `c77e00c94ffa817fd7de6af4dfa3c253f122e342` | `hash_bad=1 lines_bad=1 run_bad=1 mismatches=3` | — | — |
| the same, #13 applied | `afbef463cf9acf315ca3df7515c110701ca83e6b` | `mismatches=0 met=True` | `mismatches=0 met=True` | — |

All five are commits in a throwaway `git clone --shared` of the lane under
`/fast/scratch/hyaku/kama-r47/S9Scorecard/lane`, deleted before this seat
finished; the lane itself was never written.
