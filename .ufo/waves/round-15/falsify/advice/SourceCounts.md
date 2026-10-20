# SourceCounts — registry rows before/current attack (round 15)

**Verdict: PASS.** No fail finding. The committed registry change is exactly
`S034` added + `S012.used-by` touched. All other 362 existing cells are
byte-identical, no ID is removed or renumbered, and a plain reimplementation of
the census row rules yields the same single pre-existing `W04` before and after
— no new `E` or `W` finding. No gate, test, build or lint was executed.

## Inputs (read-only)

| Item | Value |
|---|---|
| Current `corpus/SOURCES.md` | HEAD `70af36c2b15b46d3b4b3c15ef20459cff640dfaf`, blob `4df10f5f979330b8b73493bd6c42f8a5a1486cdb`; worktree `git hash-object` identical; 93 lines |
| Before `corpus/SOURCES.md` | `HEAD~1` = `6e348e28943849aceb08d6954dee92be48ce9ba8`, blob `5366af75e9252197d8081844e0e587be79607f63` |
| Diff shape | `17 insertions, 1 deletion` (`git diff --numstat`); the single deleted line is the old S012 row line |
| Before census receipt | `.ufo/waves/round-15/sources-before-census.json`: rows33, A30/B0/C3, mined23/queued5/rejected5, missing0; file mtime 05:02:26, before the SOURCES.md write 05:12:17 |
| Before validate receipt | `.ufo/waves/round-15/sources-before-validate.json`: only `W04 S031 duplicate url docs.ollama.com/api/tags across scopes`, exit 0 |

`HEAD~1` is the round-15 start commit named by `.ufo/waves/round-15/frozen/manifest.json`
(`source_commit 6e348e28…`, `sha256 fda61e00…`) and by SCORECARD.md. The
"before" receipts therefore describe this exact committed baseline, not an
unrecorded intermediate state.

## Row census — plain parse under the census row rules

Rules mirrored from `scripts/sources-census.sh`: heading state (`## Registry`
opens, any other `##`/`#` closes), `^ {0,3}\|` rows, header and separator rows
skipped, `split('|')`, NF==13, cells trimmed.

| Metric | Before | Current |
|---|---|---|
| Registry rows | 33 | 34 |
| Unique IDs | 33 | 34 |
| Duplicate IDs | 0 | 0 |
| Row-shaped sources outside `## Registry` (E12) | 0 | 0 |
| NF==13 rows | 33/33 | 34/34 |
| ID set | S001–S033 | S001–S034, contiguous |
| Tier A / B / C | 30 / 0 / 3 | 31 / 0 / 3 |
| Status mined / queued / rejected | 23 / 5 / 5 | 24 / 5 / 5 |

Added: `S034` only. Removed: none. Existing row order unchanged; `S034` is the
last Registry row (line 46), immediately before `## Paths` (line 48).

## Cell invariance on the 33 pre-existing rows

- 33 rows × 11 cells = **363 cells compared; 362 identical, 1 changed**.
- 32 of 33 existing rows are **raw-line identical**; only `S012` differs.
- The only touched cell is `S012.used-by`:
  - old: `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md, corpus/knowledge/ollama-evidence-replay.md`
  - new: old three paths + `corpus/lessons/round-15.md`
- `S012.status/opened/recheck` and every other cell of the row are unchanged.
- `S031` is unchanged in this round (its round-14 used-by addition is already in
  the before baseline); `S011` remains unchanged.

## Added row S034 — cell and claim check

Observed row (`corpus/SOURCES.md:46`):

- `id=S034`; `kind=own-work`; `tier=A`; `status=mined`; `opened=2026-10-20`;
  `recheck=every round`; `used-by=corpus/lessons/round-15.md`.
- `source` names `.ufo/waves/round-15/frozen/measure-before.py` and calls it the
  preserved exact baseline of `.ufo/waves/round-14/measure.py`.
- `scope` limits the claim to the original `corpus_problems` guard code, not a
  vendor/API/runtime contract.
- `anchor` cites `corpus_problems` lines 350–362 of `.ufo/waves/round-14/measure.py`
  at start commit `6e348e2`.
- `teaches` asserts the guard rejects only `if unique < MINIMUM_UNIQUE_CASES:`
  and never compares declared-name count to unique count, so ≥16 distinct
  stripped names plus duplicates passes preflight.

Verification of every material clause:

1. Frozen copy sha256 `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`
   equals `git show 6e348e2:.ufo/waves/round-14/measure.py`, and equals the
   `frozen/manifest.json` digest. The file is tracked in HEAD.
2. In that blob, `def corpus_problems` spans lines 350–362; `MINIMUM_UNIQUE_CASES = 16`
   is at line 66; the predicate `if unique < MINIMUM_UNIQUE_CASES:` is at line
   358; `declared` is used only to build the set (lines 351–356), so the
   declared-count comparison is absent — the `teaches` claim is exact.
3. Ordering: `run()` calls `corpus_problems(cases)` at frozen line 372; a
   non-empty result records every case as unmeasured at lines 375–378, before
   any `measure_case` child branch (line 379 onward). "Passes preflight" is
   therefore accurate for `unique >= 16` with duplicates.
4. Parser validity: `kind` in enum, tier A, status mined, `opened` is today
   (not future), `recheck` matches the symbolic cadence rule, `used-by` path
   exists on disk. `source` contains no `http(s)` URL, so it contributes no
   URL/scope pair to E04 or W04.

## Census-rule replay before vs current (reimplementation, not executed)

The same rules as `row_pass`/`usedby_findings` were reimplemented for URL
normalization, URL+scope tracking, enums, opened-date bounds, recheck forms,
E10/W01/W02/W03, and used-by existence:

- Before: 1 finding — `W04 S031 duplicate url docs.ollama.com/api/tags across scopes`.
- Current: identical 1 finding, same ID and URL.
- No E01–E12 finding, no new warning; every mined `used-by` path resolves.
- This matches both round-15 before receipts and the round-14 final validate.

## Prose additions checked

- 15 inserted prose lines, all under the existing correction/search-log prose
  block (`## Leads (unopened)`, line 80 onward); none is a row-shaped line and
  none falls inside `## Registry`.
- Claim "one new own-work row S034": true.
- Claim "Only existing S012 used-by gains `corpus/lessons/round-15.md`; its old
  three knowledge paths and every other existing cell remain unchanged": true
  at cell granularity and raw-line granularity.
- Claim "S034 is opened in round15, not covered by the introduction's round10
  date": true (`opened=2026-10-20`; introduction line unchanged).

## Non-blocking observations / remaining unknowns

1. **No post-addition sources receipt.** The wave recorded only `sources-before-*`
   (33 rows, 05:02). No `sources-final-*` exists for round-15; the current
   census (34 rows, A31/B0/C3, mined24/queued5/rejected5) is derivable only by
   parsing. Round-15 docs correctly label rows33 as the before state, and
   SCORECARD.md's "counts appended after execution" has no appended sources
   count, so no stale count claim was found — but current-state row evidence is
   parse-only.
2. **Anchor resolves against the start commit, not the mutable file.** The
   current `.ufo/waves/round-14/measure.py` (HEAD blob `46c5866d…`) spans
   `corpus_problems` at lines 350–364: the repair inserts two lines, the unique
   predicate moves to line 360, and `S034.anchor`'s 350–362 range covers the
   pre-repair blob. The row qualifies "at start commit 6e348e2" and the
   `source` cell names the frozen copy, so this is unambiguous; the anchor must
   not be re-resolved against the repaired worktree file.
3. `S034.source`'s primary pointer is a wave-local frozen copy. It is committed
   and manifest-pinned, so it is durable while tracked; it is not an external
   source, which the `own-work` kind and scope explicitly acknowledge.
4. `recheck=every round` is contract-valid symbolic cadence; overdue mode will
   emit a `cadence` line for it (same class as existing symbolic rows), not an
   overdue finding.
5. Cosmetic only: new prose has `Identified2`/`screened2` spacing and `round15`
   instead of `round-15`. No contract or row effect.
6. Not established here (outside this seat, no checks run): that the ps page was
   actually re-fetched in round 15, and that the repaired guard rejects
   duplicate corpora before children. Those are covered by source-reopen and
   harness lanes respectively.

## Tooling

No tool install or update; nothing to record.

Report: .ufo/waves/round-15/falsify/advice/SourceCounts.md
