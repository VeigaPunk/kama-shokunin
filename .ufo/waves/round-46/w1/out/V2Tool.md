# V2Tool — code review of `tools/append-only-audit.py` (round 46, C2 calibration)

**Verdict: functionally correct against its docstring and the frozen C2 counter contract — 16/16 fixture probes pass, it matches the counter's independent recomputation (selftest=1 fixture=1 lane=1 on a fixture it cannot know), and on the lane at 0163fea2 it reproduces the 5 claimed events exactly (0.75 s, 640 read-only git calls, repo untouched). Findings below are robustness/edge defects; none affects the frozen calibration claims at current lane scale.**

Reviewed: working-tree `tools/append-only-audit.py` (clean vs HEAD; last touched at lane commit 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050, as claimed). Contract: docstring of the tool (L1–32) + counter `tools/round46-append-audit-check.py` docstring. Environment: git 2.56.0, Python 3.14.8. No tools were installed or upgraded (system git/python only). All fixtures were built under `/fast/scratch/hyaku/kama-r46/V2Tool/` (removed at the end); every fixture asserted `git rev-parse --show-toplevel` == fixture dir before the first commit; the lane was only ever read.

## Findings by severity

### F1 — Medium: `--selftest` with a bad `--scratch` crashes with a traceback, exit 1, no `AOA_SELFTEST` line
- **Where:** `tools/append-only-audit.py:306` — `root = tempfile.mkdtemp(prefix="aoa-", dir=a.scratch or tempfile.gettempdir())` runs before any error handling; the directory is never `makedirs`-created.
- **Command:** `python3 tools/append-only-audit.py --selftest --scratch /fast/scratch/hyaku/kama-r46/V2Tool/nope-nope-nope`
- **Output:** rc=1, stderr tail `FileNotFoundError: [Errno 2] No such file or directory: '.../nope-nope-nope/aoa-8saikomm'`, no `AOA_SELFTEST` line (probe P6b, receipt-correctness.txt).
- **Impact:** the C2 counter's selftest leg treats rc≠0 as fail (leg=0), so a typo'd `--scratch` silently turns a calibration run into `selftest=0` instead of a clean `could-not-evaluate`. The frozen counter guards the same step: `round46-append-audit-check.py:192-193` does `os.makedirs(root, exist_ok=True)` before its mkdtemp.
- **Fix:** wrap the L306 mkdtemp in `try/except OSError` → print `could-not-evaluate: ...` to stderr and return 2 (or `makedirs(exist_ok=True)` like the counter).

### F2 — Medium: non-UTF-8 bytes in diff content crash the audit with exit 1 + traceback instead of exit 2
- **Where:** `tools/append-only-audit.py:51` — `_git` uses `subprocess.run(..., text=True)` (strict decode); `main` catches only `AuditError` (L315–319).
- **Fixture:** LOG.md with 30 lines containing raw byte `0xff`, 25 then deleted (≥ threshold).
- **Command/Output:** probe P9 → rc=1, `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 106: invalid start byte`. Docstring L30 promises "2 could not evaluate".
- **Lane exposure (observed):** all five declared files at 0163fea2 decode as UTF-8 cleanly (SCORECARD 229367 B, LOG 179864 B, QUALITY 81708 B, README 48113 B, SOURCES 214192 B) — latent, not currently triggered.
- **Fix:** catch `UnicodeDecodeError` in `main` → `could-not-evaluate`, exit 2 (minimal, contract-preserving). `errors="surrogateescape"` in `_git` would keep byte-exact line matching but changes matching semantics vs the frozen counter for non-UTF-8 files — out of frozen scope this round.

### F3 — Low: `--files ","` (any all-empty value) silently reverts to the five declared files
- **Where:** `tools/append-only-audit.py:82` (`files = files or FILES`) + `:314` (parse yields `[]`).
- **Fixture/Output:** probe P8 — LOG.md event + notes.md losing 30 lines; `--files ','` → `files=[the five declared]`, `events=[LOG.md]`, rc=1. A user passing an empty/garbled list gets the default audit instead of an error.
- **Fix:** argparse error (exit 2) when the parsed list is empty.

### F4 — Low: performance — O(commits) subprocesses + O(events × later-commits) blob reads; fine at lane scale, quadratic-ish worst case
- **Where:** `:97` one `diff --name-only` per commit; `:101` one `-U0` diff per changed file (runs even when deletions end below threshold); `:109`/`:113` per-event `later_blobs` batch-check + one `cat-file blob` **per distinct later blob** until the restorer is found.
- **Measured** (single-run serial, receipt-perf.txt + trace-perf-*.txt):
  - 400 commits, 0 events: 0.72 s, 802 git calls (399 name-only + 399 `-U0` + 4).
  - 400 commits, 1 unrestored event at c80 with churn: 0.96 s, 1122 calls (~320 `cat-file blob` reads).
  - lane 0163fea2 (292 commits, 5 events): 0.75 s, 640 calls — far under the counter's 1800 s timeout.
- **Worst case:** N commits × E unrestored events with per-commit churn → ~N×E blob spawns (e.g. 5k × 5 ≈ 25k spawns ≈ 40–75 s). Still within timeout, but the fix is cheap.
- **Fix:** (a) one persistent `git cat-file --batch` reader instead of per-blob spawns; (b) `git diff --numstat` once per commit to get deletion counts and skip `-U0` for non-candidates; (c) optionally a single `git log --topo-order --reverse --parents --raw` pass for the changed-set loop.

### F5 — Low: `--files` values are used as pathspecs (L97/L101) but compared literally (L99) — silently skips files
- **Observed instances** (probes P11, P12; receipt-quoted-path.txt):
  - path containing `"`: `git diff --name-only` C-quotes it (`"we\"ird.md"`), the literal compare misses → **event silently missed, rc=0**.
  - `--files corpus` (a directory): the pathspec matches `corpus/QUALITY.md`, the literal compare skips it → 0 events, rc=0.
- Declared five files are unaffected (plain ASCII, no pathspec metacharacters); only reachable via `--files`.
- **Fix:** compare against `git diff --name-only -z` (NUL-separated, unquoted) output, or set `-c core.quotePath=false` for the diff calls.

### F6 — Info (shared with the frozen counter, not a divergence): `---`-prefixed deleted lines are excluded
- `:102` `x.startswith("-") and not x.startswith("---")` also drops content lines whose text begins with `--` (diff renders them `---…`). The counter's recompute uses the identical filter, so tool and counter agree (probe P10a: 30 `--x…` lines deleted → no event; P10b counter lane leg = 1). A file losing ≥ 20 lines each starting with `--` produces no event. Contract-defined ("the `---` header excluded", docstring L15) — a known blind spot, not fixable in the frozen round.

### F7 — Info (shared): empty deleted lines count as deletions and always match at tip
- An empty line's diff line is `-` → `dele` gets `""`; the trailing `""` from `split("\n")` on any nonempty tip blob always matches → purging 25 empty lines yields a "restored" event (probe P10a README: deleted=25 restored_at_tip=25 restored). Identical in the counter. Agreement holds; semantics quirk only.

## Verified invariants (no finding)
- **Paths with spaces work end-to-end** (P1: event detected, `restored_by` correct). `cat-file --batch-check` parsing is robust: missing specs echo `<spec> missing` (with spaces → >2 tokens → None; receipt-batchcheck-raw.txt); existing blob → `<oid> blob` (2 tokens); tree spec → None.
- **Missing paths:** file removed at tip → unrestored event, `restored_by` null (P2); never-existed file → no events, rc=0 (P2).
- **Root commits:** no parent, no deletions; `--to <root>` → commits=1, no events (P3).
- **Merges:** diff vs first parent — a merge whose *result* deletes lines vs first parent IS an event (P4a: merge deleted=31, side deleted=30); octopus merge picks parent[0] correctly (P4b: exactly 2 events, both deleted=30, parents `[m, main, b1, b2]`).
- **Exit codes:** 2 for missing repo / bad `--to` / threshold 0 / negative / non-int; 1 with events; 0 without (P5). Selftest: 10 cases pass, rc=0, `AOA_SELFTEST pass=10 fail=0`.
- **TMPDIR / --scratch honored** (P6a, white-box spy on `tempfile.mkdtemp`): `dir=$S/tmpA` with TMPDIR set, `dir=$S/tmpB` with `--scratch`; fixtures removed on exit. Invalid TMPDIR silently falls back to /tmp (P6c, stdlib behavior).
- **JSON shape vs C2 contract** (P7): exact top-level keys `{to, threshold, files, commits, events, summary}`; event keys exactly the 6; `commit`/`restored_by` 40-hex or null; `to` = full hex of `--to` (short sha expands); rc agreement; text render matches docstring format.
- **Counter agreement on a blind fixture** (P10b, receipt-c2cross.txt): frozen counter on a fixture containing the tool at tip reports `selftest=1 fixture=1 lane=1` (table=0 expected — no SCORECARD in fixture), i.e. the tool matches the independent recomputation including the counter's own random fixture.
- **Lane reproduction** (receipt-lane.txt, lane-events.json, trace-lane.txt): at 0163fea2 exactly 5 events — LOG 2290/2290, QUALITY 375/375, README 663/663 all restored by 82b5e9d3; SCORECARD 2416/2417 partial; dd9f5dc6 SCORECARD 24/31 partial; rc=1; 0.75 s; 640 git calls, all read-only (rev-parse/rev-list/diff/cat-file only); `git status --porcelain` identical before/after.

## Residual risk / verification gaps
- I did not run the full C2 counter against the lane (L1's integration leg owns that); my counter run covers tool-vs-recompute agreement on my own fixture only.
- Perf timings are single-run on a busy host; the git-call counts (GIT_TRACE) are exact, timings indicative.
- Shallow/grafted repos: truncated history appears as root commits (no deletions counted) — not probed; irrelevant for the lane (full 292-commit history).
- F2/F5 are reachable only through content/paths the declared five do not currently contain (verified UTF-8-clean at 0163fea2).

## Evidence files (all under the out dir)
`probe.py` (16 probes), `perf.py`, `lanesmoke.py`, `receipt-correctness.txt`, `receipt-c2cross.txt`, `receipt-perf.txt`, `receipt-lane.txt`, `receipt-batchcheck-raw.txt`, `receipt-quoted-path.txt`, `lane-events.json`, `trace-lane.txt`, `trace-perf-a.txt`, `trace-perf-b.txt`, `trace-perf-b2.txt`, `trace-perf-c.txt`.
