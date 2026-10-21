source: docs.python.org/3.14 (Python 3.14.8 docs) `library/sys.html` §sys.exit, §sys.excepthook; `library/subprocess.html` §run, §CompletedProcess.returncode, §CalledProcessError.returncode; stryker-mutator.io `docs/mutation-testing-elements/mutant-states-and-metrics/` §Mutant states, §Metrics; github.com/hcoles/pitest (master) `pitest/src/main/java/org/pitest/mutationtest/DetectionStatus.java` (RUN_ERROR, getForErrorExitCode, isDetected); lane frozen tag 37bd4c5 via `git show`: `tests/llamacpp-live/install-tree-grid.py:49-53,110`, `tools/citation-provenance.py` (main tail, `return 2` handlers, `sys.exit(main())`)
verified-at: 2026-10-21 — docs and PIT source fetched 2026-10-21 (PIT at master, not a pinned revision; Stryker page unversioned); CPython probes on host `/usr/bin/python3` 3.14.8, Linux 7.2.11-arch1-1; lane probes in scratch against tag 37bd4c5 tools
recheck: on-release — refetch the three doc pages and PIT DetectionStatus.java, rerun the probes in the Probes block after any Python, lane-instrument or mutation-tool change

# A verdict, an error and could-not-evaluate are three outcomes

An instrument may report KILLED/REJECTED/ACCEPTED only when it observed the subject's verdict. A crash, a signal, an unusable input or an early-abort selftest is an error or could-not-evaluate. An exit code alone cannot carry that distinction.

## Exit 1 is overloaded in CPython

- Documented: `sys.exit(arg)` with an object other than an integer or None "results in an exit code of 1"; the docs call `sys.exit("some error message")` "a quick way to exit a program when an error occurs" (sys.exit).
- Uncaught exceptions: the interpreter calls `sys.excepthook` (sys.excepthook). The section does not state the status; exit 1 is observed below [INFERENCE for the general case].

Observed (host CPython 3.14.8):

| Case | returncode |
|---|---|
| uncaught `ValueError` | 1 |
| `sys.exit("msg")` | 1 |
| `sys.exit(3)` | 3 |
| `raise SystemExit(None)` | 0 |
| uncaught `KeyboardInterrupt` | -2 |
| child `kill -9 $$` / self-SIGKILL | -9 |
| child `kill -15 $$` | -15 |

A Python exit 1 therefore means "a verdict was printed" or "the program crashed". Only a parsed verdict line can separate the two.

## Negative returncode = signal

subprocess docs: "A negative value `-N` indicates that the child was terminated by signal `N` (POSIX only)." Such a status is not a verdict about the subject unless the harness sent the signal on purpose (a timeout kill is an instrument decision, see the mutation precedent below). An external SIGKILL, OOM kill or SIGINT is an error.

## Lane evidence (frozen 37bd4c5)
- `tools/citation-provenance.py`: handled failures (non-git lane, missing or empty registry, invalid JSON, `[{}]` row) exit 2 (observed: all rc 2). The final `return 0 ... else 1` is the verdict for missing/mismatch/off-ref. A registry row `[1]` reaches `row.get` uncaught and exits 1 with a traceback (observed rc 1, `AttributeError` at `check`). The same code therefore emits exit 1 for both a verdict and a crash.
- `tests/llamacpp-live/install-tree-grid.py:110`: `status = "rejected" if code == 1 else "error" if code in (2, 3) else "accepted"`. The gate's real verdict is stdout starting `INVALID ` with exit 1 (`tests/llamacpp-live/check-receipt.py:2233`). A crashing gate with exit 1 is counted as `rejected` [INFERENCE from the code; no crashing gate was run].

## Mutation-testing precedent

- Stryker (docs): Killed = "at least one test failed"; Timeout is "counted as detected"; Runtime error = "an error (rather than a failed test)", "not represented in your mutation score". Invalid = runtime + compile errors, excluded from valid; score = detected / valid.
- PIT (DetectionStatus.java, master): `RUN_ERROR(true)`, `MEMORY_ERROR(true)`, `TIMED_OUT(true)`; `getForErrorExitCode` maps OOM to MEMORY_ERROR, TIMEOUT to TIMED_OUT, everything else to RUN_ERROR; RUN_ERROR's javadoc is "Something went wrong ... probably bad", yet `isDetected()` returns true. PIT counts run errors as detected; Stryker excludes them. This repo follows Stryker's rule, not PIT's.

## Rules for lane instruments

1. A verdict requires a parsed verdict line plus an exit code from the instrument's documented verdict set.
2. Any other exit (uncaught 1, signal, unknown code, handled 2/3) is error or could-not-evaluate. It never increments killed/rejected counts.
3. Exit 1 alone is never a verdict.
4. An early-abort or unusable-input path is not a verdict, even when it prints the target literal.

## Probes (scratch, exit observed)

```
python3 -c 'import subprocess; print(subprocess.run(["python3","-c","raise ValueError"],capture_output=True).returncode)'  # 1
python3 -c 'import subprocess; print(subprocess.run(["sh","-c","kill -9 $$"]).returncode)'                            # -9
git show 37bd4c5:tools/citation-provenance.py > cp.py; python3 cp.py --lane <git-lane> --registry <reg with "[1]"> --docs x  # rc 1 traceback
```
