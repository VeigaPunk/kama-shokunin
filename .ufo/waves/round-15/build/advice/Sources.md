# Sources-3 — round-15 scoped advice

## Edit 1 — S012 `used-by` append

File: `corpus/SOURCES.md` (only file owned this lane). Single `used-by` cell append on
row S012; every other cell, row, and section unchanged. No immutable receipt/history
edits.

**Old `used-by` cell (S012):**
`corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md, corpus/knowledge/ollama-evidence-replay.md`

**New `used-by` cell (S012):**
`corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md, corpus/knowledge/ollama-evidence-replay.md, corpus/lessons/round-15.md`

### Source open

- URL: https://docs.ollama.com/api/ps — re-opened 2026-10-20 (this round).
- Page: OpenAPI 3.1.0, info.version 0.1.0, GET `/api/ps`, "List running models".
- Located quote (5 words), `responses.'200'.description`: "Models currently loaded into
  memory".

### Why the append is appropriate

`corpus/lessons/round-15.md` Gate row "Loaded metadata or green replay/guard tests prove
present inference readiness → reject" grounds itself on "Reopened S012 documents loaded
memory only; no real runtime sampled and readiness remains unknown". The page re-open
confirms `/api/ps` enumerates models *currently loaded into memory* — loaded-state
metadata, not an inference-readiness attestation. The lesson uses S012 exactly as a
sourced boundary rejection, so it is a legitimate used-by entry.

## Edit 2 (parent-directed) — new row S034

Parent (KamaR15) directed: open `.ufo/waves/round-15/frozen/measure-before.py`
(preserved exact baseline) and add the next unused row S034, `own-work`, tier `A`,
scoped to the original corpus-guard code only. Done — appended as the last registry
row (after S033); no other cell touched.

- Source opened: `.ufo/waves/round-15/frozen/measure-before.py`,
  `corpus_problems` lines 350–362 (baseline of `.ufo/waves/round-14/measure.py`
  at start commit 6e348e2), opened 2026-10-20.
- Located quote (4 words), line 358: `if unique < MINIMUM_UNIQUE_CASES:`
- Row cells: kind `own-work` · tier `A` · status `mined` · opened `2026-10-20` ·
  recheck `every round` (same convention as own-work row S030) · used-by
  `corpus/lessons/round-15.md`.
- teaches: the guard rejects only when the unique-name count falls below
  `MINIMUM_UNIQUE_CASES`; it never compares declared-name count to unique count, so
  ≥16 distinct stripped names plus duplicates passes preflight — the defect C1
  repairs. This sources the C1 diagnosis itself; S012 only supports the domain
  readiness boundary. No vendor authority is claimed by or for this row.

## Boundary kept

- S012 supports only the readiness boundary: loaded metadata ≠ readiness. The C1
  duplicate-corpus guard is kama's own code policy enforced by the repaired runner and
  measured by red/green tests; it is **not** an Ollama API guarantee and is not
  attributed to S012 (the lesson's "Opened source" section states the same). S034 is
  own-work evidence for that diagnosis, not external authority.
- No endorsement of C1 mechanics, fixture counts, or runner correctness; this lane made
  no measurements and ran no verification commands.

## Limitations

- Docs pages are undated; the S012 `opened` cell retains its recorded 2026-10-19
  first-access date per existing convention (round-14 clarification documents re-opens
  without mutating `opened`). S034's `opened` is 2026-10-20, its first open.
- No registry prose/clarification paragraph or search-log entry was added this round;
  the assignments limited edits to the S012 used-by cell and the S034 row. If L1 wants
  a matching "Round-15 used-by addition / row addition" clarification block mirroring
  the round-12/13/14 pattern, that is a one-paragraph follow-up.
- No tools installed; none needed.

Report: .ufo/waves/round-15/build/advice/Sources.md
