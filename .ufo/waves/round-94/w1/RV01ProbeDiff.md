# RV01ProbeDiff — C1 diff review (kama r94 w1)

## Scope
Reviewed `git diff e6f1dcce a27656a454b1a2364f8b6e55f42fbca8c2e86ee4 -- tools/kama-probe.sh tools/round94-router-budget.py`.
Extracted `ROUTER_PY` from both revisions, ran each as `python3 -c "$ROUTER_PY" <body.json> files <idx...>` over a
generated corpus, then ran the full `check --json` path (base vs M1) against a stub router for verdict-level diff.

## Commands and outputs
- `git diff e6f1dcce a27656a4 -- tools/kama-probe.sh tools/round94-router-budget.py` → 3 hunks in probe + new 554-line counter.
  Hunk 1: `MAX_STEPS, DEADLINE = 4_000_000, monotonic()+4.0` → `MAX_STEPS=4_000_000; PER_FILE_SECONDS=15.0; DEADLINE=monotonic()+PER_FILE_SECONDS`.
  Hunk 2: `gguf_parse` gains `global DEADLINE; DEADLINE = monotonic() + PER_FILE_SECONDS` (per-file reset).
  Hunk 3: `router_file_states` wrapper `timeout 8` → `timeout 60` (comment-only otherwise).
- `python3 rv01.py` (file_state corpus, 40+ cells): all single-candidate states equal base; multi-candidate
  same-file repeats equal; distinct slow files differ only where intended (see Findings).
- `python3 rv01_verdict2.py` (check --json, 18 cells): 15 PASS, 3 DIFF — all DIFFs are the intended fix.
- `loadavg` at run time: 165–218 (32-core box under heavy multi-agent load).

## Findings

### NOTE-1 (intended, not a defect): per-file deadline changes verdict on distinct-slow-file listings
`R08-distinct-slow-x4/x5/x6` cells: base returns `MODEL_OK/router-unloaded-autoload` (shared 4 s deadline starves
later candidates → undecided → loadable), M1 returns `MODEL_UNLOADED/router-model-invalid` (each file gets its own
15 s slice → all parsed → invalid). This is exactly the r93 SC02 F1/F2/F3 defect C1 closes; the counter's R08 cell
expects `MODEL_UNLOADED/router-model-invalid`. Evidence: `verdict-matrix.json`, `rv01-verdicts.out`.

### NOTE-2 (intended): `timeout 8` → `timeout 60` wrapper
The wrapper must outlast `PER_FILE_SECONDS` per distinct candidate or it re-imposes the shared-budget starvation.
60 s allows ~4 distinct slow files (counter's R08 uses exactly 4) plus overhead. A listing exceeding 60 s still fails
open (undecidable → loadable), same as base's 8 s failure mode. Disclosed in claims C1 "Disclosed limit".

### NOTE-3 (pre-existing, unchanged): stdout buffering on timeout kill
`python3 -c "$ROUTER_PY"` writes `idx\tstate` lines to a pipe; Python block-buffers stdout. If `timeout` kills the
process before normal exit, buffered output is lost → all candidates undecided → `MODEL_OK`. This mechanism is
identical in base (`timeout 8`) and M1 (`timeout 60`); not a new behavior change. The counter's cell set (max 4
distinct slows, ~12 s parse) stays well under 60 s.

### NOTE-4 (verified): SEEN memoization key is inode-identity, not path string
`SEEN` key = `(st_dev, st_ino, st_size, st_mtime_ns, st_ctime_ns)` (kama-probe.sh:599). Hard links, symlinks, and
`./`-prefixed paths to the same inode share one parse; distinct inodes each get their own deadline. Verified:
`h0.gguf` (hardlink), `s1.gguf` (symlink), `./slow.gguf` all return `invalid` with one parse; `slowA–slowE.gguf`
(distinct inodes) each parsed independently. No cross-inode memoization leak.

### NOTE-5 (verified): undecidable stays loadable (round-89 rule unchanged)
`file_state` returns `-` for: non-absolute `args[0]`, missing `args[0]` file, unreadable file (chmod 000), unknown
tensor type, version 2 GGUF, relative model path. `-` → `router-unloaded-autoload` (MODEL_OK) in `router_refine`.
Same in base and M1. Verified across 18 single-candidate cells + 6 arg-form cells.

### NOTE-6 (verified): no other behavior change in diff
The diff contains exactly 3 hunks: deadline constant split, per-file `DEADLINE` reset in `gguf_parse`, and the
`timeout` wrapper value + comment. No changes to `MAX_STEPS`, `PATH_FLAGS`, `NO_OPEN`, `SEEN` key, `file_state`
logic, `gguf_parse` parsing logic, `router_entries`, `router_refine`, or `classify`. The counter file is new
(554 lines, frozen).

## Deliverables
- `.ufo/waves/round-94/w1/out/RV01ProbeDiff/c1.diff` — the reviewed diff
- `.ufo/waves/round-94/w1/out/RV01ProbeDiff/rv01-filestates.out` — file_state corpus results (40+ cells)
- `.ufo/waves/round-94/w1/out/RV01ProbeDiff/rv01-verdicts.out` — check --json verdict matrix (18 cells)
- `.ufo/waves/round-94/w1/out/RV01ProbeDiff/verdict-matrix.json` — machine-readable verdict matrix
- `.ufo/waves/round-94/w1/RV01ProbeDiff.md` — this report

VERDICT: holds — the only behavior changes are the intended per-file deadline and timeout wrapper; all single-candidate states, arg forms, SEEN memoization, and undecidable-loadable semantics are identical to base.
