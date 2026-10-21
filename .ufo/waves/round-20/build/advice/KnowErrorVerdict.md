VERDICT: partial - knowledge draft delivered and its CPython/PIT/Stryker/lane facts observed; round-19's "citation checker exits 1 for unusable git/docs" was not reproduced (observed exit 2 for those inputs; exit 1 only via an uncaught crash)

# Scope
Assignment: draft `corpus/knowledge/error-is-not-a-verdict.md` (provenance trio first, <=60 lines) on verdict vs error vs could-not-evaluate. Lane not modified; no subagents; no lane tool run live.

# Deliverable
- `.ufo/waves/round-20/build/out/KnowErrorVerdict/error-is-not-a-verdict.md` (54 lines; `source:`/`verified-at:`/`recheck:` first). Not placed in `corpus/knowledge/` (lane write is L1's integration step).

# Sources opened (2026-10-21)
- docs.python.org/3.14 (Python 3.14.8 docs): `library/sys.html` §sys.exit ("any other object ... results in an exit code of 1"), §sys.excepthook; `library/subprocess.html` §CompletedProcess.returncode (negative `-N` = signal N, POSIX).
- stryker-mutator.io `docs/mutation-testing-elements/mutant-states-and-metrics/` (unversioned): Runtime error "not represented in your mutation score"; Timeout "counted as detected".
- github raw `hcoles/pitest` master `DetectionStatus.java` (not pinned): `RUN_ERROR(true)`, `getForErrorExitCode` (else -> RUN_ERROR), `isDetected()` returns true for RUN_ERROR. PIT counts run errors as detected; Stryker excludes them.
- Lane frozen tag 37bd4c5 read via `git show` (read-only): `tests/llamacpp-live/install-tree-grid.py:49-53,110`; `tests/llamacpp-live/check-receipt.py:2233`; `tools/citation-provenance.py` main tail and `return 2` handlers.

# Commands executed and observed exits
- `python3 -c` probe via subprocess on `/usr/bin/python3` 3.14.8: uncaught ValueError rc 1; `sys.exit("msg")` rc 1 (stderr `msg`); `sys.exit(3)` rc 3; `raise SystemExit(None)` rc 0; uncaught KeyboardInterrupt rc -2; `sh -c 'kill -9 $$'` rc -9; `kill -15` rc -15; self-SIGKILL rc -9. (exit 0 for the probe wrapper)
- `git show 37bd4c5:tools/citation-provenance.py > cp.py` (rc 0); `git show 37bd4c5:tests/llamacpp-live/install-tree-grid.py` (rc 0); `git show 37bd4c5:tests/llamacpp-live/check-receipt.py | sed -n 2225,2240p` (rc 0).
- In scratch copy of cp.py, run with `--lane` pointed at a non-git dir: rc 2 (`lane is not a git repository`). Git lane (`git init`, empty commit) with registries `[]`, `{}`, invalid JSON, `[{}]`: all rc 2 (messages: `registry must be a non-empty JSON array`, JSON decode error, `invalid registry row: {}`). Git lane with registry `[1]`: rc 1, traceback `AttributeError: 'int' object has no attribute 'get'` at `check` (cp.py line 82).
- `python3 cp.py --help` not run; `python3 itg.py --help` rc 0 (scratch only).
- Scratch `/tmp/kama-r20-KnowErrorVerdict` removed (rc 0 of rm).

# Findings
1. CPython exit 1 is overloaded: documented for non-int `sys.exit` arg; uncaught exceptions also observed as 1. A bare exit 1 is not a verdict.
2. Negative returncode is observed for SIGKILL, SIGTERM, and uncaught KeyboardInterrupt (-2). A harness-sent timeout kill is an instrument decision; an external signal is an error.
3. `citation-provenance.py` returns 1 as a real verdict (missing/mismatch/off-ref) and also 1 for an uncaught crash on a malformed registry row. Handled input failures return 2 (observed).
4. Round-19 claim "exits 1 for unusable git/docs" (`QualityCriteria.md:31`) is NOT reproduced: unusable git (non-git lane) and unreadable docs path through `return 2`. Only the uncaught `[1]` row yields 1. Not verified: whether round-19's text meant that uncaught path. Correction proposal for L1: reword to "exits 2 for handled unusable git/docs, exits 1 also for uncaught crashes".
5. `install-tree-grid.py:110` maps every gate exit 1 to `rejected`; a crashing gate would be counted as a rejection. Code-read only [INFERENCE for runtime; no crashing gate run].
6. Precedent split: Stryker excludes runtime errors from the score; PIT counts RUN_ERROR as detected. The doc recommends the Stryker rule.

# Gates / scope
- No lane file, index, or git state modified. No install or upgrade performed (python3 3.14.8 and git used as-is). No persistent process started. No network downloads beyond the doc pages.

# Out of scope / not done
- Corpus SOURCES.md rows (scouts/L1 own them); the lane's round-18 C2 selftest-kill arm and the round-19 QualityCriteria.md text were not re-opened.
- PIT mutator docs page read but unused beyond the mutator table; PIT state list taken from source, not a versioned doc.

# Check for L1 to run
- `python3 -c 'import subprocess; print(subprocess.run(["python3","-c","raise ValueError"],capture_output=True).returncode)'` -> expect 1.
- Reproduce the `[1]` registry crash in a git scratch lane (see Commands) -> expect rc 1 with AttributeError.
