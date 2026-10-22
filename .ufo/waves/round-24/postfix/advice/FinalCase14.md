# FinalCase14 — PG14-missing-lane-blob-plain (current arm only)

**VERDICT: holds at pin 92063cf — no falsification found for this cell.** The candidate keeps the
real unavailable-object refusal and its strong identity (typed `could-not-evaluate:`, content-derived
reason naming the dropped blob, no verdict document, no acquisition, no metadata substitute).
Recommendation only: no score promotion, no self-admission; the original unknown clause stays
WITHDRAWN/NOT-ACHIEVED and Gitfloor H2 stays open.

## Setup (observed)
- Clone `--no-hardlinks` of `/home/vgpnk/Projects/shokunin/kama-shokunin` → `/fast/scratch/hyaku/kama-r24/postfix/FinalCase14/clone`, detached at `92063cfc60e217fa7e2098c568578119b16a1b95` (origin kept, local file origin intact).
- Pin-verified bytes: `tools/report-landing-audit.py` `b9be4f42…3b26f`, `tests/report-audit/promisor-grid.py` `30483830…f270`, `promisor-grid-expectations.json` `d86b7bea…14cd1` (47 cases, 1 open row), `isolation-mutants.py` `eace4f56…2a00`, `promisor-mutants.py` `971c3ecb…f200`, both `StoreLocalPresence/*.py` match the registered producer hashes.
- Builder inspected: `promisor-grid.py:623 c_missing_lane_blob_plain → build(root,tmp,drop=("sources_blob",))` — plain lane (no `lane_mark`), same fixture as PG13 minus promisor metadata; frozen row saved at `out/expectation-row-PG14.json` (live view = original = exit 2 / kinds null / defects null / reason_class `unavailable`; `names_any_of ["$sources_blob","corpus/SOURCES.md"]`; `twin: null`).
- `TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase14/tmp` (existing, owned, unique) for every role execution; no fallback to a shared root.

## Executed (bounded: 1 grid cell + 1 diagnostic control, no full grid)
1. `python3 tests/report-audit/promisor-grid.py --arm current --case PG14-missing-lane-blob-plain --json` → exit 0, stderr empty. Raw: `out/grid-current-PG14.json`.
2. Independent probe `out/probe-pg14.py` (rebuilds the pinned grid's own fixture, runs the pinned auditor with the grid's argv, captures FULL stdout/stderr; `out/probe-pg14.json`).
3. Discrimination control (diagnostic only, NOT a graded cell): same builder without the dropped blob → `out/probe-pg14.json:cases.control-complete-lane-plain`.

## Decisive observations (current arm, PG14)
- Grid row: `exit=2`, `problems=[]`, `amended_problems=[]`, `original_problems=[]`, `met_amended=true`, `met_original=true`, `met=true`; `defects=null`, `raw_defects=null`, `kinds=null`, `document=null`; `objects_acquired {lane:[], fleet:[]}`; `traceback=false`, `internal_error=false`, `timed_out=false`, `leaked=false`. Arm summary: `graded=1, violations=0, violating_cases=[]`, `amended_view_met=1/1`, `original_view_unmet=[]`, `withdrawn_original_failures=[]`, `tracebacks=0, timeouts=0, harness_leaks=0`.
- Premise (probe): lane `promisor_backed=false` (no `extensions.partialclone`, no `remote.*.promisor`, no `.promisor` marker, no remote at all), lane missing exactly `051975b0ced83169116c235e7691c0a1a8313300` (= `corpus/SOURCES.md`), lane commit `58866b563cd900df310588effe79028efc104c33` present, fleet missing `[]`, fleet report blob present.
- Refusal identity (full stderr, probe): `could-not-evaluate: unavailable required object: 58866b56…:corpus/SOURCES.md (051975b0ced83169116c235e7691c0a1a8313300) in <lane>: git cat-file blob 051975b0… rc=128 fatal: git cat-file 051975b0…: bad file` — prefix `could-not-evaluate:`, both strong names present (blob OID **and** `corpus/SOURCES.md`), no `partial clone (`/`promisor pack` (no metadata substitute), no `could-not-evaluate: internal:`, no traceback. Source path: `tools/report-landing-audit.py:343 required_read` ← `:428 load_source_urls` (the actual required read of the committed SOURCES blob), i.e. content-derived, not the scoped missing cache.
- No verdict document: stdout length 0 (both grid `document=null` and probe); `observed_defects` = None.
- No acquisition: `objects_acquired` empty in grid and probe (auditor `GIT_ISOLATION` includes `--no-lazy-fetch --no-replace-objects`); the lane has no remote, so no fetch path exists.
- Determinism: two consecutive direct runs give byte-identical stdout (0 bytes) and stderr, exit 2/2 (`out/determinism-pg14.txt`).
- Discrimination control: identical fixture with the blob present → exit 0, a normal verdict document (`defects: []`, `summary.defects 0`, `required 1`, `round_commits 1`, `source_url_hashes []`), stderr empty, no acquisition. So the refusal is caused by the genuinely missing required blob; the new scoped missing cache did not install a blanket precondition, and the new per-store/canonical lookup still resolves the cited lane commit.
- Twin handling: PG14's manifest `twin` is `null`; grid reports `twin_pairs_in_manifest=0`, `twin_compared=0`, `twin_mismatch=[]`. A refusal has no verdict document (`document=null`), therefore **no twin equality is claimed or observed** — two missing documents are not compared.

## Residuals / verification gaps (not exercised by this cell)
- Only the current arm was run, by instruction; the frozen (r23 base) arm for PG14 was not measured here, and its amended-view status is not asserted by me.
- The new `fatal`-cause branch (`EvalError.fatal` → `root_tree` skip) was NOT exercised: PG14's cause is `rc=128` (non-fatal), so `root_tree` still ran. Its effect on refusal identity (tip-tree naming) is untested by this cell.
- Sibling paths that the required-read/fatal-cause/scoped-cache changes touch (PG13 promisor twin, PG15/16 missing lane tree, PG17/18 missing fleet report/tree, PG45/48 unused-hole cases) were not executed here; PG14 exercises only the missing-lane-blob required-read path. Ungraded open row PG40 and Gitfloor H2 are untouched; no manifest/grid/auditor/data byte was modified.
- No tools installed or upgraded (none needed).
