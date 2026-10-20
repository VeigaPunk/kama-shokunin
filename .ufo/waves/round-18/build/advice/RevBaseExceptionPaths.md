VERDICT: confirm — frozen v2 lets runtime BaseExceptions bypass receipt publication; BaseExceptions during teardown can also bypass child cleanup and log deletion.

# Axes

Operability: receipt publication, process-group teardown/reaping, temporary-log deletion, signal-handler restoration, and exit-code integrity. Calibration: keep the guarantee scoped to the lifecycle run and distinguish intended argparse exits from internal failures.

## Findings, by severity

### P1 — Runtime `BaseException` skips the receipt epilogue

Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py:1241-1250` catches `SetupError`, `Terminated`, and `Exception`, but not `BaseException`; quote: `except Exception as exc: # F1: unexpected post-launch failure -> exit 2`. The later receipt emitter and handler restoration are at `:1385-1419`; its comment says `receipt write + handler restore run outside the try/finally`.

A `KeyboardInterrupt`, `SystemExit`, or `GeneratorExit` escaping the run body still executes the `finally` at `:1250`, but then unwinds `main()` before reaching the emitter at `:1389`; it therefore returns no receipt. In the normal path through that `finally`, handlers are first changed to `SIG_IGN` at `:1257-1261`; because the restoration loop is in the skipped epilogue (`:1414-1416`), those dispositions are not restored. This directly falsifies the frozen module's blanket “never an escaped traceback without a receipt” claim at `:21-24`.

### P1 — A `BaseException` during teardown can skip both the kill backstop and log unlink

Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py:786-827` performs wait/port work before entering the log-unlink `finally` at `:807-826`; quote at `:805-806`: `the temp file is unlinked even when reduction raises`. This protection covers reduction only, not an exception from the earlier `proc.wait()` at `:789` or `_port_refuses()` at `:804`. In `main()`, teardown is caught only as `Exception` at `:1264-1282`, while the last-chance kill/reap is later at `:1286-1301`.

Thus a `BaseException` propagating from teardown is not caught, aborts the outer `finally`, and skips the last-chance kill/reap and receipt write. If it occurs before the helper's unlink `finally`, the temporary log also remains. [INFERENCE] If the child has not exited when the interruption arrives, it can remain live because the SIGKILL backstop is not reached. This is a source-control-flow finding; no fault-injection run was performed for the frozen copy.

### P2 — Runtime guard begins after unreceipted preflight and handler setup

Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py:1017-1044` hashes inputs and constructs the receipt before the lifecycle `try` at `:1117`; quote at `:1017`: `model_sha = sha256_file(args.model)`. Handler installation is also before that `try` (`:1113-1117`). A `BaseException` in those steps escapes without a receipt; partial handler installation would not be restored. [INFERENCE] These paths have no child or temp log yet, unlike the teardown paths above.

The parser at `:994-995` intentionally runs before lifecycle setup. Keep its ordinary `argparse` `SystemExit` behavior (help/usage) outside the internal-fault conversion.

## Minimal lifecycle structure and `SystemExit` mapping

After parsing CLI arguments, place the lifecycle run under one encompassing `try/except BaseException`, recording unexpected runtime faults as `internal:<type>` and setting the tool result to exit 2. Put teardown, process-group kill/reap fallback, log unlink, and signal-handler restoration in a guaranteed cleanup `finally`; cleanup faults must be recorded without preventing the remaining cleanup steps. Publish the receipt only after cleanup and fault classification. In particular, teardown itself must not be able to raise past the cleanup boundary before the kill/reap and unlink attempts.

For `SystemExit` raised during that runtime lifecycle, write the receipt as an internal fault (at minimum `setup_error: internal:SystemExit`) and return exit 2, regardless of `SystemExit.code`; do not let `SystemExit(0)` masquerade as success or preserve a conflicting status. Preserve parser-generated exits by keeping argument parsing outside that guard. The Python 3.14 docs state: `If the value is an integer, it specifies the system exit status` (https://docs.python.org/3.14/library/exceptions.html#SystemExit). That is why the runtime exception must be normalized explicitly rather than allowed to propagate. `KeyboardInterrupt` and `GeneratorExit` follow the same catch rule because they derive from `BaseException`, not `Exception`.

## Residual risk and verification gaps

- Static review only; no runtime/fault-injection checks were run and no source files were changed.
- The `lsp` device is not mounted (`read xd://lsp` returned “No such tool”); references, definition, and diagnostics were unavailable. Findings above rely on direct inspection of the frozen source and Python documentation, not grep as semantic proof.
- Receipt publication cannot be guaranteed if its destination/stdout itself fails; that failure must still produce exit 2 where possible, without claiming a successfully written receipt.
- No tools were installed or updated.
