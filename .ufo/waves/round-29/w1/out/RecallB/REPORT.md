# RecallB — extractor recall, SCORECARD 721–1441 and SHONEN.md

Scope: `SCORECARD.md` lines 721–1441 and all of `SHONEN.md` at base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`. Compared with `count-c1.py --list` (`all_statements`, 69 rows, all in SCORECARD.md; 49 of them on lines ≥ 721). SHONEN.md is 12 lines and contributes 0 extracted statements.

These rows are limits of the frozen extractor. They are not base statements and are not counted in `unresolved`.

## Totals

| | missed | hold at W | do not hold |
|---|---:|---:|---:|
| P | 2 | 2 | 0 |
| H | 6 | 6 | 0 |
| N | 0 | 0 | 0 |
| C | 26 | 26 | 0 |
| T | 2 | 2 | 0 |
| Q | 4 | 3 | 1 |
| **all** | **40** | **39** | **1** |

Wrong-path binds among statements the extractor did emit in this slice: **0**. No H or N is extracted on lines ≥ 721. Every extracted P path is the path written in the token.

The one failure is Q at SCORECARD.md:901, span `declared2048 = captured training2048`. At its writing revision `92b146253fd3a8c4bfade94c909dc63b13d6f4a8`, `git grep -F` finds that span only in `SCORECARD.md`, which the Q check excludes.

Detail: `missed.json` (40 objects: line, class, text, W, holds, evidence). Every `holds` value was recomputed with the frozen class check (`merge-base --is-ancestor`, `sha256` of the named blob, `nlines`, committer `%ct`, `git grep -F` with the counter's excludes).

## Why the extractor misses them

- **C is same-line and adjacency-bound.** `RE_CWORD` needs `at|base|tip|commit|commits|epoch|revision|rev|measured`, then a space, then an optional backtick, then the hex, on that line. Wrapped citations drop the trigger onto the previous line (773, 875, 983, 1007, 1061, 1074, 1130, 1284). A word in between also drops them (`measured tree`, `epoch is`). Other citing words are invisible: `start`, `frozen`, `since`, `master`, a bare heading id, `(245a37f)`, and a `git cat-file -e REV:path` object name.
- **H requires `` `path.EXT` sha256|md5 hex `` on one line.** This slice uses `SHA-256`, a following line, a basename with no extension (`SHA256SUMS`), or an ellipsis (`da5041a8…5af1`, `6501737c…6588`, `a38faefe…49a5`).
- **P has no comma list and no elided path.** `:187,194` keeps only 187. `at :689` has no path; the path is `SKILL.md` from the previous pointer.
- **T has no second clock and no date-less clock.** `09:42:50Z` continues `2026-10-22T09:42:42Z`. `08:35:54Z` has no date on the line; the date is 2026-10-23 from the section and from `75b78bb4`'s committer time `08:38:16Z` in the same sequence.
- **Q requires a backtick span.** Parentheses and one blockquote carry measurement text the backtick rule never sees.

## SHONEN.md

No `path:L`, no md5/sha256 of a named file, no line-count, no cited lane commit, no dated time, no backtick measurement span. Nothing to miss.

## Examined and not listed

- Date-only headings `(2026-10-20)` and the like are not class T (no clock).
- `tools/server/server-schema.cpp` `@704366d76` (line 1418) is upstream; the frozen rule skips `@`. Not a lane commit.
- `` `1cb5a41b…` `` (line 849) does not resolve (`git rev-parse` fails). The sentence calls it a blob beside commit `1b85a24`, which is listed.
- `population_sha256` `f29fab8d…364a` (line 1157) is `sha256` of the in-memory `CASES` table in `tests/report-audit/repo-state-grid.py` (`population()`), not a blob. No blob at W has that digest. Not class H. The auditor abbreviation on line 1156 is class H and is listed (`tools/report-landing-audit.py`).
- `fb367e9e…` (line 972) is the stale expected constant, not the digest of `c2/measure.py` (that file's sha256 at W is `c9a4f336…`). The file digest in the same sentence is line 974 and is listed.
- Run-directory names (`runs/0957ce61`, `runs/c7311039`, …) are paths, not commit citations. The commit citations beside them are listed.
- Prose `exit 0`, `**21/21**`, and similar are not quoted measurement spans.
- Already extracted, so not misses: the seven in-slice mismatches (P 740, Q 823, Q 824, Q 833, Q 834, P 1349, P 1375). Two of those P tokens are bare paths that do not resolve, while a longer file does: `corpus/lessons/round-17-verifier-spotcheck.md` has 276 lines at the line-740 revision (the token omits `corpus/lessons/`), and `.ufo/waves/round-26/count-c1.py` has 423 lines at the line-1375 revision (the token is `count-c1.py`; the sentence says round-26). The extractor bound the literal token both times. That is the author's path, not a second path the regex chose.

No tools installed.
