# RecallB — frozen extractor misses (not counted)

Scope: SCORECARD.md lines 721–1441 and all of SHONEN.md at `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`, against `count-c1.py --list` (69 statements, 0 in SHONEN, 49 on SCORECARD lines ≥ 721). Rows below are extractor limits. They are not base statements and must not be added to `unresolved`.

Machine list: `.ufo/waves/round-29/w1/out/RecallB/missed.json`. Totals and the not-counted boundary: `.ufo/waves/round-29/w1/out/RecallB/REPORT.md`.

## Totals

40 missed statements: C 26, H 6, Q 4, P 2, T 2, N 0. **39 hold** at the writing revision under the frozen class check; **1 does not**. Wrong-path binds of statements the extractor did emit in this slice: 0.

The failure is Q SCORECARD.md:901, `declared2048 = captured training2048`. At `92b146253fd3a8c4bfade94c909dc63b13d6f4a8` that span occurs only in SCORECARD.md (`q:no-artifact`).

## Limits (why 40 rows exist)

- C is one line and one immediate trigger word (`at|base|tip|commit|commits|epoch|revision|rev|measured`). A trigger on the previous line, a word in between (`measured tree`, `epoch is`), or another citing word (`start`, `frozen`, `since`, a heading id, `(245a37f)`, `REV:path` in `git cat-file`) is invisible.
- H requires `` `path.EXT` sha256|md5 <hex> `` on one line. `SHA-256`, a digest on the next line, `SHA256SUMS` (no extension), and ellipsis abbreviations are invisible. The six H rows were checked as sha256 of the file the sentence names; all six match at W.
- P does not take `:187,194` (194 missed; 187 is extracted and holds) or an elided `:689` (`SKILL.md` from the previous pointer; nlines 1133 ≥ 689, so P holds). Line 689 is not the "Context size has been exceeded" sentence; the P check does not read the line.
- T misses the end clock `09:42:50Z` of a range whose start is extracted, and the date-less `08:35:54Z` (date 2026-10-23 from the section and from `75b78bb4` committer `08:38:16Z`). Both are ≤ W's committer time.
- Q misses measurement text that is not a backtick span (parentheses at 1018 and 1369, the line-1270 blockquote, the line-901 table cell). Three of those four occur in a non-excluded blob; 901 does not.

SHONEN.md: no statement of the six classes.

Not listed, on purpose: date-only headings; upstream `@704366d76`; unresolved blob prefix `1cb5a41b`; `population_sha256` `f29fab8d…364a` (hash of in-memory CASES, no matching blob); run-directory names; unquoted `exit 0` prose; the seven already-extracted mismatches in this slice (P 740 and P 1375 are literal short paths — `corpus/lessons/round-17-verifier-spotcheck.md` and `.ufo/waves/round-26/count-c1.py` would satisfy a line check, but the extractor bound the token as written).
