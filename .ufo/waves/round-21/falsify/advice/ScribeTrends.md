VERDICT: partial - trends drafted: expansion unchanged, quality improved (one citation gap named), discernment unchanged; SHONEN boxes stay [~] with pointers; two lane items open.

# ScribeTrends — round-21 trend verdicts and SHONEN lines (draft)

Scope: draft the three learning-trend verdicts (`LEARNING.md` §The three trends) and SHONEN box pointers from `corpus/lessons/round-21.md` and `runs/b76727f3/`. Measured commit `b76727f31e522763ce24e43d6ec86d21b507a11f`; round start `7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d`. Read-only on the lane; no SHONEN.md, LOG.md or lesson edit. Full drafts: `.ufo/waves/round-21/falsify/out/ScribeTrends/trend-verdicts.md` and `shonen-lines.md`.

## Verdicts

| Trend | Verdict | Basis (executed unless marked) |
|---|---|---|
| expansion | unchanged | 0 new admitted `knowledge/` entries (`git --no-pager diff --name-status 7a6bc91 b76727f -- corpus/knowledge` → `M` only); +9 SOURCES rows are not expansion (`CORPUS.md` rule 4); no new source kind; README/SCORECARD/LOG unchanged. |
| quality | improved (bounded) | `llamacpp-loading-lifecycle.md` gains a provenance-trio supplement; round-19 scope note kept and marked historical; frozen arm re-measured (`c2-grid-both.stdout`): link 0/13, the old "pin unchanged" statement re-confirmed. KQ28/KQ29 appended. Declared exits 28/28 (recount, exit 0). |
| discernment | unchanged | No spot-check result in `## Gate` (required by `CORPUS.md`); `grep -niE 'spot\|agree\|disagree\|non-author\|outside'` on the lesson → lines 4, 67, 100, none a sample. "Non-author build reviewers" (M5) are lane-dispatched (`LEARNING.md`: "still the lane") [INFERENCE from dispatch files]. |

## Findings for the L1

1. **Quality citation gap (KQ6).** Supplement line 347 states the glibc-hwcaps search order, attributed to a seat observation; `source:` cites S066–S068 only. `ld.so(8)` supports it: `curl -sSL https://man7.org/linux/man-pages/man8/ld.so.8.html` (man-pages 6.19, exit 0) shows `glibc-hwcaps/x86-64-v3:glibc-hwcaps/x86-64-v2:.` in NOTES (line 679 of fetched HTML). S067 anchors §DESCRIPTION steps (4)–(5), not NOTES. Fix: an appended correction naming the NOTES anchor.
2. **W04 disclosure.** Duplicate-URL warnings rose 6 → 8: S067 (shares `ld.so.8.html` with S057) and S071 (shares `git-cat-file` with S033). `fr-sources-validate` exit 0 (`runs/b76727f3/fr-sources-validate.stdout`); the lesson records neither warning.
3. **Missing spot-check.** `lessons/round-21.md` `## Gate` lacks the spot-check result; discernment cannot move without a named non-author sample (≥1 admit, ≥1 reject).
4. **LOG.md has no round-21 entry** (last heading round 20, line 1199). SHONEN box 2's round-21 pointer is the receipt path only until the L1 writes the entry.
5. **PROVINCE.md silent on fleet-report reading.** `tools/report-landing-audit.py` reads `/home/vgpnk/Projects/shokunin/.ufo/reports/round-N/kama.md` and fleet/lane git objects (SKILL.md row: "stdout only; reads lane and fleet git objects"); PROVINCE.md was not changed (no fleet/.ufo/reports/git log/landing match). Box 4's "PROVINCE.md still accurate" is therefore not re-established by round 21.
6. **Working tree differs from the measured commit.** `git status` at the end of this session shows ` M tools/report-landing-audit.py` (+15/-1 against `1471344`); the file's mtime is `2026-10-21 08:19:36 -0300`, after the measured commit `b76727f` (08:13:58 -0300). I did not edit it. The C1 numbers in `runs/b76727f3/` describe the committed file, not this one. The L1 must re-measure or revert before admitting C1 (`recipe` requires a clean tree; `run.py` refuses otherwise).

## SHONEN (drafted, all `[~]`)

- Box 1 SKILL.md: pointer to `SKILL.md` lines ~674–696 (round-21 decision row + checklist addition; S066, S067 cited).
- Box 2 LOG.md / live: pointer to `runs/b76727f3/live-receipt.json` (11 checks; pinned gate exit 0; wrong-links-pin exit 1); LOG entry pending.
- Box 3 executable: `recipe.json` + `run.py` + `commands.json`; recipe sha256 `9d68997d…`; 28/28 recount; no non-author rerun.
- Box 4 cross-domain: caveat per finding 5; keep `[~]`.
- No `[x]`: no outside spot-check exists for any box.

## Commands run (exit)

- `git --no-pager log --format=... 7a6bc91..b76727f` → 0 (4 commits).
- `git --no-pager diff --stat` / `--name-status` over corpus, SKILL, LOG, SCORECARD, README, PROVINCE → 0 (LOG/SCORECARD/README/PROVINCE empty).
- Python recount recipe vs `runs/b76727f3/*.exit` → `met 28 of 28`, exit 0.
- Python recount of `c2-grid-both.stdout` per arm → frozen link 0/13, subdir 0/1; current 13/13, 1/1 (exit 0).
- `grep` on the lesson, SOURCES, QUALITY, LOG, PROVINCE, SKILL (exit 0 with matches; exit 1 on empty greps, noted above).
- `curl -sSL` ld.so(8) → 0; `grep -c hwcaps` → 5 matches.

## Tooling

- Installed nothing. `curl` (already present) used for one read-only fetch of man7 ld.so(8).

## Limits / cleanup

- Quotes in the lesson's Gate were not re-verified (SourcesConformance's scope).
- [INFERENCE] "not uncovered" for the soname ground reads the coverage map by hand, not by recount.
- Scratch `/tmp/kama-r21-ScribeTrends` removed at end of run.
