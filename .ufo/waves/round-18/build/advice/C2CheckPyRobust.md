VERDICT: confirm — decoder-limit JSON now records per-row failures; timed-out probes and same-group descendants are terminated.

# Findings

- `tests/probe-verdicts/check.py:406-409` catches `ValueError` and `RecursionError` from `json.loads`, returning a malformed-output reason with the exception class. The existing `grade()` path stores that reason in the row's `error`, leaves `passed: false`, and returns normally. This covers the 60,000-level nesting and 5,000-digit integer in `falsify/advice/MalformedNonUtf8.md:8-10` (“60,000 nested arrays”; “5,000-digit integer”).
- `tests/probe-verdicts/check.py:279-297` launches the probe with `start_new_session=True`, sends `SIGKILL` to its process group on timeout, kills the direct child if still live, drains/reaps it, then re-raises `TimeoutExpired`. The existing grade branch continues to record `probe timed out after …s` and `passed: false`. This addresses `falsify/advice/TimeoutPath.md:19-23` (“subprocess.run(... timeout=PROBE_TIMEOUT)”) and the surviving child observed at `:35-41` (“sleep 120”).
- `tests/probe-verdicts/check.py:554-595,598-628` extends `--selftest`: both decoder-limit payloads go through `grade()` and produce non-empty row errors; a valid successor row passes; a timed shell wrapper with a same-process-group child records the timeout and its delayed marker remains absent. Existing selftest keys and the regular result schema remain; selftest fields are additive. The graders and exit table were not changed.

# Delivered files

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/KamaR18.C2CheckPyRobust-2/check.py` — SHA-256 `12367de62efafa02641c4acb497e50f1be5019b54879a9ac6da13efd5f8071a5`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/KamaR18.C2CheckPyRobust-2/check.py.diff` — SHA-256 `104a74147c9b3d0c195941c8f95ea7822811a3c9eb656c4ef882faa7a739c308`; unified diff is against `.ufo/waves/round-18/frozen/tests_probe-verdicts_check.py`.

# Verification

All commands ran against the isolated `/tmp/kama-r18-C2CheckPyRobust-2` clone, not the lane worktree:

- `python3 -m py_compile /tmp/kama-r18-C2CheckPyRobust-2/tests/probe-verdicts/check.py` — exit 0.
- `python3 /tmp/kama-r18-C2CheckPyRobust-2/tests/probe-verdicts/check.py --selftest --probe /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh --json` — exit 0; 72/72 matrix rows passed. Selftest passed; both malformed payloads were recorded with errors, the successor row passed, and timeout cleanup passed (`child_completed: false`).
- `python3 /tmp/kama-r18-C2CheckPyRobust-2/tests/probe-verdicts/check.py --json --probe /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` — exit 0; 72 tests, 72 passes, 0 failures.
- `ss -ltnp` after the full run — exit 0; no listener matched any of the checker run's recorded ports. Other listeners on different ports were left untouched.
- Delivery `diff -u` returned 1 as expected because the delivered checker differs from the frozen copy; the diff was written and hashed above.

# Limitations and blockers

- Group cleanup covers children still in the probe's process group. A deliberately detached child (`setsid()`/`setpgid()`) can escape this signal; if it retains the captured pipes, the post-kill `communicate()` may wait for those pipes to close. The selftest covers a same-group child, not detached-process containment.
- The new parser guard handles the observed `ValueError` and `RecursionError`; it is not a blanket catch for resource failures such as `MemoryError` or arbitrary faults outside `json.loads`.
- LSP was unavailable: requesting `xd://lsp` returned `No such tool: xd://lsp`; no LSP definitions/references/refactors were available. No installs or updates were performed.