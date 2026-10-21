# Round-21 learning-trend verdicts — DRAFT (ScribeTrends seat, advisory; L1 integrates)

Measured commit: `b76727f31e522763ce24e43d6ec86d21b507a11f` (clean committed; `runs/b76727f3/`).
Round start: `7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d`. Vocabulary: `LEARNING.md` §The three trends (`/home/vgpnk/Projects/shokunin/LEARNING.md`), no scalar.
Range counted: `git --no-pager log 7a6bc91..b76727f` (4 lane commits: a29bb84, 1471344, 4e75d9e, b76727f; exit 0).

| Trend | Verdict | One-line basis |
|---|---|---|
| expansion | **unchanged** | 0 new admitted `knowledge/` entries; 9 new SOURCES rows are not expansion under `CORPUS.md` rule 4; no new kind, no frontier entry, no SCORECARD capability. |
| quality | **improved** (bounded; one citation gap named) | One admitted entry deepened with a provenance trio; its round-19 scope note kept visible and marked historical; the old "pin unchanged on retarget" statement re-measured by the frozen arm. |
| discernment | **unchanged** | No outside admit/reject spot-check and no "spot-check result" in the `## Gate`; the only "non-author" label in the lesson is a lane-dispatched build seat. |

## expansion — unchanged

Evidence (all from executed commands in this draft's session):
- `git --no-pager diff --name-status 7a6bc91 b76727f -- corpus/knowledge` → `M corpus/knowledge/llamacpp-loading-lifecycle.md` only; no `A` line. Diff hunk `@@ -320,3 +320,43 @@`: an appended supplement to an existing entry, not a new entry. `CORPUS.md` rule 4 counts admitted `knowledge/` entries; count = 0.
- SOURCES census (`fr-sources-census` exit 0): rows 65 → 74; tier A 62 → 70, B 0 → 1, C 3; status mined 52 → 60, queued 6 → 7, rejected 7. Rows carry no quota (`CORPUS.md` rule 4: "a short registry ... beats a long one"), so the +9 rows do not move expansion.
- Kind histogram (awk over `git show <rev>:corpus/SOURCES.md`): before docs 40, dataset 1, community 3, spec 4, own-work 5, code 12; after docs 47, dataset 1, community 3, spec 5, own-work 5, code 13. No kind value is new.
- `git --no-pager diff --stat 7a6bc91 b76727f -- corpus/README.md SCORECARD.md LOG.md` → empty. No frontier entry, no capability admitted.

Pro-argument considered and rejected: eight new `mined` tier-A rows on soname/symlink identity. That is row growth; the trend counts knowledge entries on uncovered coverage-map ground. The soname identity extends the existing `llamacpp-loading-lifecycle.md` entry (its round-19 TreeCap note), so the ground is not shown uncovered. [INFERENCE: "not uncovered" is a reading of the coverage map, not a recount.]

Would flip to `improved` with: a new admitted entry citing one of S066–S074 on a coverage-map row marked uncovered, or a README frontier move.

## quality — improved (bounded)

Evidence:
- `corpus/knowledge/llamacpp-loading-lifecycle.md` gains `## Round-21 supplement` (diff `@@ -320,3 +320,43 @@`) with `source:`, `verified-at:` and `recheck:` lines (provenance trio, `CORPUS.md` rule "A new knowledge entry opens with its provenance trio"; the supplement is an append, so the trio sits in the appended block).
- The round-19 scope statement is kept and marked: "The round-19 scope note above stays historical: `install_tree_sha256` still pins regular files only". Not silently stale.
- Re-measurement of the old claim: `runs/b76727f3/c2-grid-both.stdout` (exit 1 declared, observed 1) — frozen arm: link cells 0/13 detected, subdir 0/1, regular 3/3, type 1/1, null quiet 1/1. Frozen `needed-retarget-*` cells report `changed: false`. Current arm: link 13/13, subdir 1/1. This re-confirms the old statement that a retarget leaves the frozen pin unchanged, and shows the new arm differs.
- `QUALITY.md` appended KQ28 and KQ29 with `lessons/round-21.md` as the motivating lesson (`git --no-pager diff -U0 ... -- corpus/QUALITY.md`).
- Declared-exit recount: 28/28 met (python recount of `recipe.json` vs `runs/b76727f3/*.exit`, printed `met 28 of 28`, exit 0).

Named defect (citation gap, not a false claim) — fix by appended correction, not rewrite:
- The supplement's glibc-hwcaps ordering statement ("which the loader searches before the directory itself (observed by the round-21 LinksLoaderProof seat)") cites no SOURCES row. Its `source:` line cites S066, S067, S068 only. `QUALITY.md` KQ6 requires a documentation claim to cite an opened row at its section.
- Documentation does support the claim, at a different anchor: `curl -sSL https://man7.org/linux/man-pages/man8/ld.so.8.html` (man-pages 6.19, exit 0) contains, in the NOTES section (after the `NOTES` heading near line 624 of the fetched HTML; the example is at line 679), `search path will be glibc-hwcaps/x86-64-v3:glibc-hwcaps/x86-64-v2:.`. S067's anchor is §DESCRIPTION steps (4)–(5), not NOTES. A correcting row or a dated appended anchor would close KQ6.

Limits: one admitted entry touched. The audit's 9 historical fleet-report defects are corrected in `registry/report-landing-errata.tsv`, which is not a corpus entry and is not counted here.

Would flip to `unchanged` if: the citation gap were scored as a KQ6 failure on an admitted entry (it is not false; the entry's own scope note is accurate).

## discernment — unchanged

Evidence:
- `corpus/lessons/round-21.md` `## Gate` (lines 34–50): candidates, decisions, quotes, census-before. No spot-check result line. `CORPUS.md` §Rules added requires each `lessons/round-<N>.md` `## Gate` to carry "spot-check result". `grep -niE 'spot|agree|disagree|non-author|outside' corpus/lessons/round-21.md` returns lines 4, 67, 100 only; none records a sample, an agree or a disagree.
- `LEARNING.md` §Discernment: "A subagent the lane dispatched is still the lane." Every round-21 seat is lane-dispatched (`falsify/dispatch.json`, `build/record.json`). The lesson's M5 "captured-by: non-author build reviewers" therefore does not satisfy the bar [INFERENCE: dispatch provenance read from the files named; not re-audited line by line].
- Criteria added with lesson behind them: KQ28, KQ29 cite `lessons/round-21.md`; no criterion without a lesson. So no "harmed" by the criterion rule.
- Rejections: candidate rejections are logged with reasons in the lesson `## Gate` table (for example "reject `-e` as the mechanism", "reject that claim; admit S069 as counterexample"). Rejections are recorded; none is spot-checked.

Would move to `improved` with: a named non-author (fresh reviewer or operator) sample of at least one admit and one reject, recorded `agree`/`disagree` with reasons in the round lesson. Would be `unprovable-but-better` only through that same named reviewer.

## Not verdicts, but flagged for the L1

- `validate` W04 warnings rose from 6 (S031, S043, S056, S060, S064, S065; `.ufo/waves/round-21/sources/validate-before.txt`) to 8 (+S067 shares `ld.so.8.html` with S057; +S071 shares `git-cat-file` with S033; `runs/b76727f3/fr-sources-validate.stdout`, exit 0). The lesson records neither warning; `grep -n W04` on the lesson and SKILL returns nothing.
- `LOG.md` has no round-21 entry at `b76727f` (last round heading is round 20, line 1199; `git diff --stat 7a6bc91 b76727f -- LOG.md` empty).
