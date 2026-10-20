# GuardHarness (KamaR15.GuardHarness-3) — corpus-guard test harness landed

Scope: owned only `tests/ollama-corpus-guard/check.py` (new). No runner,
fixture, receipt, or sibling file was edited. No tests were run per the
wave rule; only `ast.parse` syntax checks were performed on my own file.
Every behavior claim below is from code construction, not execution.

## Files changed

- `tests/ollama-corpus-guard/check.py` — new stdlib-only CLI
  (`kama-corpus-guard-test/v1`).

## Behavior implemented

- CLI: `--runner PATH` (default `.ufo/waves/round-14/measure.py` resolved
  relative to the repo root, not to cwd), `--selftest` (runs the same
  committed literal matrix — it is the only mode), `--only TEST` (exact
  test-id match; zero matches fails closed with `test_failed`, exit 1).
- Matrix: every sorted sibling `*.json` in `tests/ollama-corpus-guard/` is
  loaded as a JSON array of `{name, names, envelope, expected_rejected}`.
  Distinct test ids enforced across files; per-test validation requires a
  non-empty string `name`, non-empty string `names`, `envelope` in
  `array|object`, boolean `expected_rejected`, and >=16 distinct stripped
  names (rejected controls must contain a real duplicate —
  `distinct < len`; valid controls must be all-distinct). Missing
  dir/empty/malformed matrix → `finding_id: test_failed`, exit 1,
  `error` set, `total: 0`.
- Staging per test (in `test-NNN` dirs under one `TemporaryDirectory`):
  corpus = deep clone of the first `expected_exit == 0` fixture of
  `tests/ollama-evidence/cases.json` (`loaded_same_digest`, 51-case file
  observed) with only `name` replaced per `names` entry; written as a bare
  array or `{"cases": [...]}` per `envelope`.
- Invocation: `sys.executable -I -B <launcher> --tool <wrapper> --cases
  <cases>` with a minimal env (`PATH`, `HOME`, `TMPDIR`, `LANG`, `LC_ALL`;
  HOME/TMPDIR inside the test dir so runner temp lands in the removed
  tree). Timeout = `30 * len(names) + 120s`. Runner path is always passed
  through the launcher, never defaulted inside the runner — correct for
  the frozen-snapshot relocation case.
- Grading:
  - `expected_rejected: true` requires exit 1, `verdict_exit` 1, `error`
    containing `duplicate case names`, `passed == 0`, `failed == total ==
    len(names)`, `tool_present is True`, `observed_exit` null on all
    records, marker count 0, and all audited process events 0
    (`runner_process_events == 0`; Popen count == 0 also asserted).
  - `expected_rejected: false` requires exit 0, `verdict_exit == 0`,
    `passed == total == len(names)`, `failed == 0`, marker count
    `len(names)`, `runner_popen_events == len(names)` (total event count
    deliberately not bound — implementations may emit
    os.posix_spawn/fork events too).
  - Non-JSON stdout, timeouts, spawn errors → failed record with reasons.
- Spawn observations (both precreated empty so absent != zero):
  - `classifier_marker.txt` — wrapper appends one line then
    `runpy.run_path(kama-ollama-evidence.py, "__main__")`; real classifier
    executes, exit code propagates, no fake classification.
  - `runner_audit.txt` — launcher installs `sys.addaudithook` recording
    `subprocess.Popen`, `os.system`, `os.posix_spawn*`, `os.fork*`,
    `os.exec*` event names, then `runpy.run_path(runner, "__main__")`.
    The real runner file executes; no import-only substitute.
  - Paths are embedded with `repr()`; generated scripts catch nothing.
- Records carry `expected`, `observed` (exit, payload fields,
  `classifier_invocations`, `runner_process_events`,
  `runner_popen_events`, `runner_event_histogram`, `runner_event_list`,
  `null_observed_exit_records`), `child_count` (marker lines), `command`,
  full `runner_stdout`/`runner_stderr`, parsed `runner_result` (the whole
  per-case result document for independent recounting of names, unique
  counts, literal child exits and findings), plus `stdout_tail`/
  `stderr_tail` (600 chars), `passed`, `reasons`. Failure-path records
  (timeout/spawn errors) retain tails only.
- Result: `runner_sha256` (audited target), `classifier_sha256` (domain
  tool), `source_cases_sha256` and `source_template` (cloned fixture
  name) reported separately; `finding_id` clean/test_failed;
  `verdict_exit` 0/1; `clean` requires `total > 0`.

## Contract deltas incorporated mid-flight

- Parent AttackSentinel: launcher audit-hook layer added; negative
  controls require both marker0 and process_event_count0; positive
  controls bind `subprocess.Popen == len(names)` (histogram exposed, total
  event count not bound to names per second note).
- HarnessSafety H1–H6: minimal runner env with HOME/TMPDIR inside temp;
  `repr()` path embedding; precreated marker/audit; `tool_present` +
  all-null `observed_exit` required for rejections; totals bound to
  literal `len(names)`; `--only` no-match fails; timeout sized
  `30*n + 120s` (runner kills its own 30s children; no process-group kill
  added — documented in LIMITS).
- L1 integration corrections applied: `load_template()` fallback removed —
  no `expected_exit == 0` fixture means HarnessError, never a silent
  nonzero-expectation substitute; rejected controls must contain a real
  stripped duplicate (`distinct < len`); rejected grading also asserts
  payload `verdict_exit == 1` matching the process exit.
- Operator ruling: all pacman transactions paused host-wide; no installs
  were needed or attempted for this slice.
- FindingExit evidence preservation applied: records now retain full
  `runner_stdout`/`runner_stderr` and the parsed `runner_result` document
  (parsed == stdout by construction, both retained for independent
  recount); `source_cases_sha256` and `source_template` added top-level;
  docstring claim bounded to the committed literal matrix rather than a
  universal corpus guarantee.

## Limitations / risks

- `ast.parse` syntax check only; no execution, per wave rule. L1 runs
  the matrix after the falsify wave.
- The rejected-path substring `duplicate case names` binds to GuardRepair's
  committed reason text (confirmed present at measure.py:358-359 via
  HarnessSafety's static read; I read corpus_problems pre-repair and did
  not re-read post-edit).
- Audit hook sees only events raised inside the runner process;
  grandchildren spawned by grandchildren are unattributed (LIMITS text).
- `--selftest` is an explicit flag but the matrix always runs; there is no
  second mode, per the contract's "runs same committed literal matrix".
- No tools installed; no pacman/uv/npm actions taken.

## Report

Report: .ufo/waves/round-15/build/advice/GuardHarness.md
