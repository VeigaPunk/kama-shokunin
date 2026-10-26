# V1Tool — code review of tools/append-only-audit.py v2 (round 47 C1)

**Verdict: v2 is correct against its docstring and the frozen round-47 C1 contract on the lane and on the constructed fixtures (counter `met=True` at the build commit 3a09a1d93dcc16799cf6c4b48786e6440af134c4), with one real defect and two low-severity CLI flaws found outside the lane's own data: non-ASCII/tab filenames are silently dropped from the contract expansion (core.quotePath quoting vs fnmatch), `--scratch` pointing at a nonexistent dir crashes with a traceback, and `--contract` is silently ignored when `--files` is also given. Performance is bounded (600 commits × 85 files ≈ 0.6 s; lane run ≈ 4.35 s).**

Everything below was run on a `git clone --shared` of the lane at
`/fast/scratch/hyaku/kama-r47/V1Tool/lane` (scratch `S=/fast/scratch/hyaku/kama-r47/V1Tool`); fixtures are fresh repos built under `$S` with a fixture identity (verified `rev-parse --show-toplevel` per fixture). No tools were installed; only python3 and git (2.56.0) were used.

---

## Findings (by severity)

### A. [High — silent coverage loss] Non-ASCII / tab filenames are dropped from the audited file set
**Where:** `tools/append-only-audit.py` (v2 at 3a09a1d9) `expand()` lines 105–107 (`ls-tree -r --name-only` + `fnmatch.fnmatchcase`) and `numstat()` lines 165–172 (tab-split). Git's default `core.quotePath=true` emits C-quoted names (`"…"` + octal escapes) for non-ASCII, tab, quote and backslash bytes from both `ls-tree` and `diff --numstat`; the trailing `"` makes the quoted name fail the contract pattern match (e.g. `corpus/lessons/*.md`), so the file never enters `files` and its deletion events are never audited.

**Command that shows it** (repro: `out/V1Tool/repro/fx_qpaths.sh`, archived `fx_qpaths.out`):
```
== ls-tree name-only at tip ==
"corpus/lessons/caf\303\203\302\251.md"
corpus/lessons/my file.md
"corpus/lessons/tab\tfile.md"
== numstat for c2 ==
0	25	"corpus/lessons/caf\303\203\302\251.md"
0	25	corpus/lessons/my file.md
0	25	"corpus/lessons/tab\tfile.md"
== tool run (contract at tip) ==
files: ["corpus/lessons/my file.md"]
events: 1   # only the space-name file; the two quoted files lost 25 lines each
```
Deterministic mechanism (independent of the fixture):
```
fnmatch.fnmatchcase('"corpus/lessons/caf\\303\\251.md"', 'corpus/lessons/*.md') -> False
fnmatch.fnmatchcase('corpus/lessons/my file.md',      'corpus/lessons/*.md') -> True
```
Space-containing names work end-to-end (event found); quoted names fail at the fnmatch stage (silently, exit 0/1 — not exit 2).

**Proposed fix:** run `git -c core.quotePath=false ls-tree -r --name-only -z <rev>` and split on NUL for the expansion, and parse `git diff --numstat -z` records (verified layout: fields tab-separated, records NUL-separated; `fx_micro.out` `od` probe) instead of the tab-split — or unquote C-style names before fnmatch. Fix probe verified on a fixture: with `core.quotePath=false` the same tool run reports the file and its event (`deleted=25`).

**Lane impact:** none — all 85 lane filenames at the build commit are ASCII (files list contains no quoted entries), so the calibration conclusion is unaffected.

### B. [Low] `--scratch` pointing at a nonexistent dir → unhandled traceback
**Where:** `main()` line 477 `tempfile.mkdtemp(..., dir=a.scratch or ...)` sits **before** the `try:` at line 478 (the `except (AuditError, OSError)` at 492–494 only guards `audit`).
```
$ python3 tools/append-only-audit.py --selftest --scratch $S/no-such-dir
…
FileNotFoundError: [Errno 2] No such file or directory: '…/no-such-dir/aoa-…'
```
(archived `fx_tmpdir.out`). This violates the documented `2 could not evaluate` contract and prints a traceback.
**Proposed fix:** move the `mkdtemp` inside the `try`, or wrap it: `except OSError: print("could-not-evaluate: …", file=sys.stderr); return 2`.

### C. [Low/nit] `--contract` silently ignored when `--files` is given
**Where:** `main()` lines 485–490 (contract branch guarded by `files is None`); the usage line in the docstring presents them as alternatives but nothing rejects or documents the combination. Demo: with both flags, output has `files: ['LOG.md'] contract: None`.
**Proposed fix:** error on the combination (`could-not-evaluate`, exit 2) or document that `--files` wins.

### D. [Observation] Performance profile on long windows
Measured (archived `fx_perf.out` and the 1200-commit stress run):
- 600 commits × 85 files, 10 events → tool run 0.6 s (fixture build 3.3 s).
- Lane at 3a09a1d9: 303 commits, 85 files, 5 events (|D| up to 2421, windows up to ~300 commits) → direct tool run ≈ 4.35 s including all legs; counter run ≈ 4.4 s.
- Worst-case window stress: 1200 commits, one event with an 1100-commit window, |D|=25, unique blob per commit → 2.9 s.

Cost is dominated by O(commits) `git diff --numstat` subprocess spawns (one per commit over all expanded files); window held(x) computation is O(events × window × |D|) with a per-unique-blob Counter cache. Fine for the counter's 1800 s timeout at lane scale; at >50k commits expect minutes. A note, not a defect.

---

## Confirmed behaviors (evidence, no defect)

| Item | Result | Evidence |
|---|---|---|
| Binary change (numstat prints `-`) | skipped, no event, exit 0 | `fx_binary.out`: `-\t-\tcorpus/lessons/r1.md`, `events: []` |
| Rename (`--no-renames`) | deletion event on the old path (`LOG.md deleted=30`, unrestored) | `fx_rename.out` (`0 30 LOG.md` / `30 0 RENAMED.md`) |
| Declared file deleted, recreated, re-trimmed below threshold | full-delete event: restored (restored_by = recreate commit, restored_max=40 kept despite later trim); trim event: unrestored | `fx_delrecreate.out` |
| Merges (first parent) | event attributed to the deleting commit, not the merge; restore through a merge sets restored_by = merge; no phantom event when first-parent diff has no deletions | `fx_merge.out` (merge parents `4164eb6 2e02ca1`; first-parent numstat `1 0 side.txt`) |
| cat-file `--batch-check` parsing | missing/tree/commit specs → None → empty Counter; zip alignment holds across the 85-file lane run | `fx_micro.out` + lane leg |
| JSON shape vs C1 contract | event keys exactly `(commit, file, deleted, restored_max, restored_best, restored_by, status)`, ids 40-hex, summary keys `(commits, files, events, restored, partial, unrestored)`, top-level `schema/to/threshold/contract/files/commits/events/summary` | programmatic check on `lane-tool.json` |
| Counter at build commit | `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True`, exit 0; tool exit 1; 5 events exactly as preregistered (dd9f5dc6 SCORECARD 31/24; 0718b6ab LOG 2292, SCORECARD 2421/2420, QUALITY 375, README 663) | `run_lane.out`, `lane-c1.out` |
| Base control | reproduces `met=False contract=0` (contract absent at 172b8ad…) | run above |
| Selftest | `pass=15 fail=0`; `TMPDIR` and `--scratch` both honored; fixture directories removed (0 leftovers) | `fx_tmpdir.out` |
| Docstring fidelity | definitions (`files`, `deleted`, `window`, `restored_max/best/by`, `status`, exit codes) match observed behavior | all of the above |

## Verification gaps
- The counter requires the frozen round-47 base commit to exist in the repo, so I could not run it on the small fixtures (it exits `could-not-evaluate`; seen in `fx_binary.out`). Parity on F1–F4 rests on the identical code paths plus the independent lane leg (`lane_mismatch=0`).
- Finding A is shared by the counter's own expansion (`contract_files`, `round47-append-audit-v2-check.py` 264–271), so the lane leg's parity cannot catch it; ground truth (`git diff --numstat`) demonstrates the miss in the fixture.

## Absolute paths written (this seat)
- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/V1Tool.md`
- Out dir: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/V1Tool/`
  - `repro/` — fx_binary.sh, fx_rename.sh, fx_delrecreate.sh, fx_merge.sh, fx_qpaths.sh, fx_tmpdir.sh, fx_micro.sh, fx_perf.py, run_lane.sh
  - archived outputs: fx_binary.out, fx_rename.out, fx_delrecreate.out, fx_merge.out, fx_qpaths.out, fx_tmpdir.out, fx_micro.out, fx_perf.out, run_lane.out, lane-c1.out, lane-tool.json,Scratch `S=/fast/scratch/hyaku/kama-r47/V1Tool` removed before finishing.
