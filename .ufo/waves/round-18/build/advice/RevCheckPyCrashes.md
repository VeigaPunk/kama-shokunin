VERDICT: partial — both decoder-limit probes still abort the matrix; timeout grading is correct, but a spawned sleep survives.

# Scope and axes

Axes: **calibration** (malformed probe output must be an ordinary failed row, not abort the measurement) and **operability** (timed-out probes must not leave descendants running).

Reproduced against current `check.py` at lane tip `e75cf680b53484a61709ee1b2787d8dbc6419f74` in `/tmp/kama-r18-RevCheckPyCrashes-2`. Each checker run used only `AuthAndDead.closed-port-connection-refused`, an isolated wrapper probe, `--json`, and Python 3.14.8. The two decoder-limit cases and non-UTF-8 control ran concurrently; the escaped-child timeout ran concurrently in its own process group. The timeout child's process-group evidence was captured before cleanup; then the checker group was SIGKILLed and confirmed empty. Scratch clone and probes were removed.

## Findings

### P2 — JSON recursion and integer-limit errors traceback instead of becoming failed rows

`/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:379-391` documents malformed output as “per-row failure, never a traceback,” but catches only `json.JSONDecodeError` around `json.loads`. `grade()` invokes this parser at `:460`; `main()` catches only `HarnessError` around the matrix at `:643-647`, and emits the JSON document only after grading succeeds at `:666-669`.

Reproductions (wrapper output was a JSON object with 60,000 nested arrays, then an object containing a 5,000-digit integer):

```text
deep: exit 1; stdout empty
Traceback (most recent call last):
  File "/tmp/kama-r18-RevCheckPyCrashes-2/tests/probe-verdicts/check.py", line 676, in <module>
    sys.exit(main())
             ~~~~^^
  File "/tmp/kama-r18-RevCheckPyCrashes-2/tests/probe-verdicts/check.py", line 644, in main
    records = [grade(entry, probe) for entry in entries]
               ~~~~~^^^^^^^^^^^^^^
  File "/tmp/kama-r18-RevCheckPyCrashes-2/tests/probe-verdicts/check.py", line 460, in grade
    row, why_bad = probe_output_row(proc.stdout)
                   ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
  File "/tmp/kama-r18-RevCheckPyCrashes-2/tests/probe-verdicts/check.py", line 389, in probe_output_row
    doc = json.loads(stdout)
  File "/usr/lib/python3.14/json/__init__.py", line 352, in loads
    return _default_decoder.decode(s)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^
  File "/usr/lib/python3.14/json/decoder.py", line 345, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/json/decoder.py", line 361, in raw_decode
    return self.scan_once(s, idx)
           ~~~~~~~~~~~~~~^^^^^^^^
RecursionError: Stack overflow (used 8140 kB) while decoding a JSON array from a unicode string

huge: exit 1; stdout empty
Traceback (most recent call last):
  File "/tmp/kama-r18-RevCheckPyCrashes-2/tests/probe-verdicts/check.py", line 676, in <module>
    sys.exit(main())
             ~~~~^^
  File "/tmp/kama-r18-RevCheckPyCrashes-2/tests/probe-verdicts/check.py", line 644, in main
    records = [grade(entry, probe) for entry in entries]
               ~~~~~^^^^^^^^^^^^^^
  File "/tmp/kama-r18-RevCheckPyCrashes-2/tests/probe-verdicts/check.py", line 460, in grade
    row, why_bad = probe_output_row(proc.stdout)
                   ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
  File "/tmp/kama-r18-RevCheckPyCrashes-2/tests/probe-verdicts/check.py", line 389, in probe_output_row
    doc = json.loads(stdout)
  File "/usr/lib/python3.14/json/__init__.py", line 352, in loads
    return _default_decoder.decode(s)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^
  File "/usr/lib/python3.14/json/decoder.py", line 345, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/json/decoder.py", line 361, in raw_decode
    return self.scan_once(s, idx)
           ~~~~~~~~~~~~~~^^^^^^^^
ValueError: Exceeds the limit (4300 digits) for integer string conversion: value has 5000 digits; use sys.set_int_max_str_digits() to increase the limit
```

Both were ordinary checker process tracebacks, not parseable JSON records; thus the matrix run ends before its result document is emitted. By contrast, a `nonutf8` wrapper returned exit 1 and a parseable one-row failure with `error` beginning `malformed probe output: stdout is not JSON`; strict decode handling at `check.py:280-287` works.

Fix: make `probe_output_row()` turn the decoder's `RecursionError` and integer-conversion `ValueError` into its ordinary `(None, reason)` malformed-output result (in addition to `JSONDecodeError`). Do not let such probe-controlled parse failures escape `grade()`.

Detection: add deep-nesting and 5,000-digit-integer variants to F8. `fault-controls.py:171-187` currently enumerates empty-array, rows-empty, row-not-object, row-null, non-JSON, and non-UTF-8 only. Existing F8 targets `error` (`:167-170`); `classify_run()` requires exit 1, parseable checker JSON, false rows, and the target conjunct (`:482-538`). Thus the existing detector will reject the current traceback/empty-stdout behavior and pass only once each case produces a failed row with an `error`.

### P2 — timed-out probe leaves a spawned descendant alive

`/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:275-287` runs `bash <probe>` via `subprocess.run(..., timeout=PROBE_TIMEOUT)`. On timeout, `grade()` records a failed row and returns at `:447-451`, but there is no probe process-tree cleanup. The existing F7 wrapper replaces Bash with one Python process (`/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:197-198`) and only calls `time.sleep(...)` (`:239-240`), so it does not exercise an external descendant.

Wrapper action: start `sleep 120` in the background with stdout/stderr redirected, write its PID to a marker, then wait. Observed result: checker exit 1 after 30.072 s; its JSON was parseable and had the expected failed row (`error: "probe timed out after 30s"`, `probe_exit: null`, `passed: false`). Before cleanup, `ps -eo pid,ppid,pgid,stat,args` showed:

```text
checker PID / process-group ID: 3071423
3071447 3071413 3071423 S    sleep 120
```

PID 3071447 was still live in the checker's process group after the checker returned. The reproduction harness then SIGKILLed only its owned process group; the child's PID and that process group were absent afterward. No listener or server was started.

Fix: run the probe in its own process session/group, and on timeout signal the whole probe group and reap it; merely adding `start_new_session=True` while retaining `subprocess.run`'s direct-child timeout kill is insufficient.

Detection: retain F7's existing requirement that the timed-out row exit with a parseable failed row and targeted `error`, and add a child-spawning timeout case that records the child PID and asserts it is no longer live after the check returns. Cleanup the PID on failure too. Current `classify_run()` only judges JSON/row conjuncts (`fault-controls.py:482-538`); `run_check()` starts a new session for the whole checker and only kills that group when the separate `CHECK_RUN_TIMEOUT` expires (`:346-368`), so neither currently asserts descendant cleanup.

# Verification gaps and limitations

- `xd://lsp` is unavailable in this environment (“No such tool”); no LSP status, references, definition, or diagnostics could be obtained. I used direct source lines plus the end-to-end scratch reproductions; no grep result is treated as semantic proof.
- Did not run the full fault-controls matrix, build, linter, or lane measurement; this review only reproduces the specified cases and inspects the related control paths.
- No tools were installed or updated.
