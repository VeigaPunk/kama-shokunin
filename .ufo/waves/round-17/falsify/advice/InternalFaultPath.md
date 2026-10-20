VERDICT: partial — ordinary Exception receipts improve, but BaseException escapes, leaked logs, and uncovered emission/restoration faults falsify the blanket internal-fault guarantee.

# InternalFaultPath — scoped falsification advice

Recommendation only; no admission, integration, lane implementation edit, routing change, or alternative assistant runtime was invoked.

## Target, axes, and identity

Attacked C2's receipt-on-internal-fault and lifecycle-cleanup promises in `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py`, specifically every exception-handler region of `main()` at `54a29268e2083caa2b1e0d54ee1e7d90961302f3`. Compared the actual scoped diff against `cff9e62`; did not rerun or dispute the reported frozen/current control totals or three real b11755 runs.

Axes named: **receipt persistence, child-group termination, handler restoration, temporary-log deletion, and exit-code integrity**, under operability; claim precision is the calibration concern. No axis score or saturation judgment is made.

- Reviewed tool SHA-256: `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`.
- Interpreter: Python `3.14.8`; `ss`: iproute2 `7.2.0`.
- Ran **48 isolated subprocess cases**, including one good fake-server baseline and 47 fault/signal cases, against the exact clone. The baseline produced exit 0 and all 11 receipt checks passed.
- Reused `/tmp/KamaR17.InternalFaultPath-clone/tests/llamacpp-live/controls.py` K0 fake source and model bytes; readiness, HTTP captures, ownership checks, and the real cloned probe ran normally before each post-readiness injection. No real llama-server or model was started.
- Snapshots below were taken **before** the reviewer's independent kill, signal restoration, and log removal. Thus a later parent-death signal or external cleanup cannot be mistaken for the tool doing its own cleanup.

## Findings, by severity

### P1 — BaseException bypasses the purported outer receipt/restoration epilogue; teardown escapes leave a listener alive

Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1247-1250,1267-1282,1385-1416`; quote at 1268: `except Exception as exc:`.

The run and teardown guards catch `Exception`, not `BaseException`. More importantly, the emitter/restorer at 1389–1416 is a **later statement**, not a finally enclosing 1117–1383. An exception propagating out of that earlier try/finally never enters it. This falsifies the new promise at lines 21–24, not just an incidental diagnostic.

Observed:

- `readiness:KeyboardInterrupt`, `readiness:SystemExit`, and `readiness:BaseException`: teardown did stop the child and delete the log, but **no receipt**, **all three handlers still SIG_IGN**, and `main()` escaped instead of returning 2.
- `teardown:KeyboardInterrupt`, `teardown:SystemExit`, and `teardown:BaseException`: **no receipt, live child/listener, retained log, all three handlers SIG_IGN**, and an escape. The last-chance kill at 1286 is never reached.
- `ignore:KeyboardInterrupt`: escape at 1259 occurs before teardown; the child/listener and log survive and the three installed tool handlers are not restored.
- `teardown_after:KeyboardInterrupt` and `rehash:KeyboardInterrupt` also skip receipt/restoration even though teardown had already stopped the child and removed its log.

Actual SIGINT, SIGTERM, and SIGHUP during the run are distinct: all three were translated to `Terminated`, produced receipts, restored handlers, removed logs, stopped the child, and returned 2. The direct KeyboardInterrupt injections must not be misreported as evidence that ordinary SIGINT delivery fails.

[INFERENCE] The remedy needs a lifetime-wide cleanup/restoration boundary; adding more sibling `except Exception` blocks cannot cover propagation past the separate epilogue. Whether to remap or re-raise BaseException should be made explicit, but receipt/cleanup/restoration must not depend on normal fallthrough.

### P2 — Even the successfully caught teardown-fault case leaks its temporary log

Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:771-827,1264-1309`; quote at 824: `os.unlink(log_path)`.

The unlink finally begins only at 807. Failures in process waiting or the port check at 804 occur before that protected region, and `main()` has no independent unlink for `log_path` after catching teardown's exception.

Observed `teardown:RuntimeError`, `teardown:OSError`, and `teardown:Terminated`: receipt written with the correct `internal:<type>`, exit 2, handlers restored, child stopped by SIGKILL — **but the log still existed**. The RuntimeError receipt recorded `returncode=-9`, `sigkill_sent=true`, `port_refuses=true`, and a failing `teardown_graceful`; the retained log was not a process-reaping race.

The more concrete internal-helper injections `wait:OSError` and `port_refuses:RuntimeError` also left the log behind. In contrast, raising RuntimeError **after** the original teardown returned did not leak a log. This locates the hole before teardown's own unlink finally, not in the reviewer's observer.

[INFERENCE] Log removal needs independent ownership in a finally covering all exits from the child lifetime, not solely the log-reduction tail of teardown.

### P2 — Ordinary exceptions still escape through two emission-epilogue holes

Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1391-1405`; quote at 1404: `except (OSError, Terminated):`.

- `end_clock:RuntimeError`: the second `_utc_now()` call at 1391 is outside the inner emitter guard. It escaped with wrapper exit 1 and no receipt. Child/log cleanup had completed; handlers were restored by 1414.
- `emit_retry:RuntimeError`: the first `_emit` raised `Terminated`; the retry at 1402 raised RuntimeError. The retry guard excludes it, so it escaped with wrapper exit 1 and no receipt. The sibling `except Exception` at 1410 does not catch exceptions raised inside the prior except handler.
- Direct `_emit` RuntimeError/OSError were correctly converted to return 2, but wrote no receipt. A first Terminated followed by a successful emit wrote the annotated receipt and returned 2; repeated Terminated/OSError returned 2 without a receipt. Direct BaseException subclasses and retry KeyboardInterrupt escaped while still restoring handlers.

No failure to write to an actually unavailable destination is counted here as an independently fixable guarantee of persistence: receipt-write failure is explicitly an exit-2 condition at lines 19–20. The actionable escape is the inconsistent exception boundary, and the broad receipt promise needs to acknowledge unavoidable publication failure.

### P2 — Signal installation and restoration are not exception-safe as a lifecycle

Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1113-1117,1414-1416`; quote at 1416: `signal.signal(sig, handler)`.

- `install:RuntimeError` injected on the second handler installation escaped before the main try. No child/log existed, but SIGINT retained the tool handler, SIGTERM/SIGHUP remained original, and no receipt was written; wrapper exit 1.
- `restore:RuntimeError` injected on the first restoration escaped after publication. All three handlers remained ignored. The already-written receipt contained **no setup_error/internal_fault**, while `main()` escaped with wrapper exit 1 instead of returning 2.

These are bounded fault-injection results, not a claim that normal `signal.signal` commonly fails. They show that the claimed restore-on-every-escape guarantee is not implemented, including ordinary Exception failures. [INFERENCE] A restore loop must at least attempt the remaining handlers when one restoration fails; installation must be inside the restoration scope.

### P3 — A caught rehash OSError contradicts the unconditional internal-fault/exit-2 description

Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1357-1365`; quote at 1360: `f'rehash-error:{exc}'`.

Observed `rehash:OSError`: receipt written, child stopped, handlers restored, log removed, but **return 1**, `setup_error=null`, `internal_fault=null`, and `model_sha256_post="rehash-error:injected-rehash"`. Only `model_unchanged` failed. RuntimeError at the same operation instead produced `internal:RuntimeError` and return 2.

The rehash-OSError conversion is inherited code, not a newly introduced behavior. The new blanket promise at lines 21–24 and the capability description in `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:573` need to describe this exception or the classification must change. This is not evidence of model-byte mutation: it is an I/O failure encoded as a failed subject/integrity check.

## Exhaustive main() exception-region inventory

Line numbers in this inventory refer to `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py` at the pinned commit. It enumerates the syntactic guards and unguarded phase boundaries, rather than claiming to enumerate every possible allocator/hardware failure. Outcomes assume no independent second fault unless stated. **S = [INFERENCE], source-only execution projection; named cases are observed in the next table.** `stopped` concerns this fixture's one-process child group; descendant-process coverage is not claimed.

| Region | Exception disposition | Receipt / child / handlers / log / return |
|---|---|---|
| 995 parser; 998–1015 path checks | S: argparse can SystemExit(0/2); explicit missing-path returns 2 before receipt/handlers/resources | No receipt; no child/log; handlers untouched; not uniformly exit 2 |
| 1017 initial model hash; 1018–1023 mismatch | Observed initial OSError escapes; S: digest mismatch returns 3 | No receipt or child/log; handlers untouched; OSError wrapper 1, mismatch 3 |
| 1025–1040 identity/registry/port preflight | OSError and SetupError return 2 without a receipt (server-hash OSError observed); S: other exceptions escape | No child/log or handler mutation |
| 1042–1098 receipt construction/source_bindings/argv | source_bindings RuntimeError observed escaping; S: other construction/clock exceptions likewise unguarded | No receipt, child, log, or handler mutation |
| 1099–1102 tool self-hash | S: OSError swallowed, self-hash remains null; others unguarded | No child/log yet; eventual exit is not forced to 2 |
| 1103–1115 env construction and handler installation | Outside lifecycle try; partial installation failure observed | No child/log; no receipt; already-installed handlers not restored; escape |
| 1118–1122 mkstemp OSError | Converted to SetupError, then 1241 | Receipt yes; no child/log created; handlers restored; return 2 |
| 1123–1141 fdopen/Popen/log close | Popen OSError observed caught by 1247; S: fdopen and close Exception use same path; close has its own finally | Receipt yes and log removed if teardown succeeds; child stopped if created; handlers restored; return 2 |
| 1171–1174 health JSON ValueError/TypeError | S: swallowed into health_body=None, not classified as an internal fault | Normal receipt/teardown; failed health check may return 1, not mandatory 2 |
| 1143–1240 body, caught at 1241–1243 | SetupError records exc.code | Receipt yes; child stopped/log removed; handlers restored; return 2 |
| 1143–1240 body, caught at 1244–1246 | Terminated records terminated:...; actual three OS signals also observed | Receipt yes; child stopped/log removed; handlers restored; return 2 |
| 1143–1240 body, caught at 1247–1249 | Other Exception records unexpected:<type> | Receipt yes; child stopped/log removed; handlers restored; return 2 |
| 1117–1249 body BaseException | Not caught; 1250 finally runs, then exception continues before emitter | Receipt no; healthy teardown stops child/removes log; handlers remain ignored; escape |
| 1257–1261 ignore-handler loop | Exception stored as internal_fault; BaseException not caught | RuntimeError: receipt/stop/restore/remove/2; KeyboardInterrupt: no receipt or cleanup, handlers remain installed, escape |
| 1263; 1304 condition; 1309 plain receipt assignments | S: outside their neighboring try guards; no broad enclosing emission/restore finally | An escaping fault here skips emission/restoration; child/log state depends on how far shutdown progressed |
| 1264–1282 teardown call and fallback-record construction | Inner Exception catch creates fallback; outer Exception catches fallback construction failure | Ordinary injected teardown exceptions: receipt/stop/restore/2, but log retained; BaseException before teardown work: live child, no receipt/restore/unlink, escape |
| 1286–1301 last-chance kill/reap | Kill ProcessLookupError/PermissionError/OSError swallowed; wait TimeoutExpired swallowed; other Exception sets internal_fault | Double RuntimeError injection left a live listener but emitted a receipt, restored handlers, and returned 2; no independent second kill path; log retained |
| 1304–1308 fallback port probe | Exception stored as internal_fault; S: BaseException not caught | Receipt and return 2 for regular Exception if later stages work; child/log cleanup already attempted; no extra unlink |
| 1310–1368 checks/loading grade/rehash | Outer Exception stored as internal_fault | Check RuntimeError and rehash RuntimeError: receipt/stop/restore/remove/2; rehash KeyboardInterrupt skips receipt/restore |
| 1357–1360 rehash OSError special case | OSError encoded as rehash-error string instead of internal_fault | Receipt/stop/restore/remove, return 1 on otherwise-good run |
| 1369–1383 final exit derivation | S: Exception guard sets internal_fault/setup_error/exit 2; BaseException and faults in the guard's own assignments still unguarded | Conditional on emission working; no independent resource cleanup in this guard |
| 1391 ended_utc assignment | Inside restoration finally, outside emitter except | Clock RuntimeError: no receipt, child stopped/log removed, handlers restored, escape 1 |
| 1392–1413 first emit | Terminated retries; OSError/Exception return 2; BaseException propagates | Direct OSError/RuntimeError: no receipt, stop/restore/remove/2; BaseException: no receipt but restore, escape |
| 1401–1405 retry emit | Catches only OSError/Terminated | Success: annotated receipt/2; caught retry errors: no receipt/2; RuntimeError or KeyboardInterrupt retry: no receipt/escape; stop/restore/remove in all tested retry cases |
| 1414–1416 restore loop | No except, aborts on first failure | Restoration RuntimeError after successful publication: receipt yes, child stopped/log removed, all handlers still ignored, escape 1 |
| Logging in preflight/emit except handlers | S: print itself is outside another error guard | A stderr write failure can replace the handled error; only the emitter region has the restoration finally |

The helper's own log-unlink finally (822–826) swallows OSError, so [INFERENCE] an actual unlink failure can also leave a log without being recorded as internal_fault. The matrix does not inject unlink failure. The `_child_running` helper (749–756) turns a poll Exception into False, so [INFERENCE] inability to establish liveness is not proof that the child group stopped.

## Observed subprocess matrix

`Return` is the value returned by main, or `escape <type>`. `OS rc` is the native child-wrapper result. `R` = all three original handlers restored; `I` = all three ignored; `T` = all three tool handlers remain; partial values are ordered SIGINT/SIGTERM/SIGHUP. `Log` describes the state before reviewer cleanup. `n/a` means no log or child was created. Raw KeyboardInterrupt OS status (-2) is after the wrapper's independent restoration/cleanup; it is **not** a claim about the exact exit status of the uninstrumented CLI with dirty handlers. Every non-baseline injection listed has a fired marker.

| Case | Return | OS rc | Receipt | Child group | Handlers | Log | Receipt setup_error |
|---|---|---:|---|---|---|---|---|
| `baseline:none` | 0 | 0 | yes | stopped | R | removed | `—` |
| `readiness:SetupError` | 2 | 2 | yes | stopped | R | removed | `injected-setup-error` |
| `readiness:Terminated` | 2 | 2 | yes | stopped | R | removed | `terminated:injected-termination` |
| `readiness:RuntimeError` | 2 | 2 | yes | stopped | R | removed | `unexpected:RuntimeError` |
| `readiness:OSError` | 2 | 2 | yes | stopped | R | removed | `unexpected:OSError` |
| `readiness:KeyboardInterrupt` | escape KeyboardInterrupt | -2 | NO | stopped | I | removed | `—` |
| `readiness:SystemExit` | escape SystemExit | 7 | NO | stopped | I | removed | `—` |
| `readiness:BaseException` | escape BaseException | 1 | NO | stopped | I | removed | `—` |
| `signalrun:SIGINT` | 2 | 2 | yes | stopped | R | removed | `terminated:signal 2` |
| `signalrun:SIGTERM` | 2 | 2 | yes | stopped | R | removed | `terminated:signal 15` |
| `signalrun:SIGHUP` | 2 | 2 | yes | stopped | R | removed | `terminated:signal 1` |
| `teardown:RuntimeError` | 2 | 2 | yes | stopped | R | RETAINED | `internal:RuntimeError` |
| `teardown:OSError` | 2 | 2 | yes | stopped | R | RETAINED | `internal:OSError` |
| `teardown:Terminated` | 2 | 2 | yes | stopped | R | RETAINED | `internal:Terminated` |
| `teardown:KeyboardInterrupt` | escape KeyboardInterrupt | -2 | NO | ALIVE | I | RETAINED | `—` |
| `teardown:SystemExit` | escape SystemExit | 7 | NO | ALIVE | I | RETAINED | `—` |
| `teardown:BaseException` | escape BaseException | 1 | NO | ALIVE | I | RETAINED | `—` |
| `teardown_after:RuntimeError` | 2 | 2 | yes | stopped | R | removed | `internal:RuntimeError` |
| `teardown_after:KeyboardInterrupt` | escape KeyboardInterrupt | -2 | NO | stopped | I | removed | `—` |
| `emit:RuntimeError` | 2 | 2 | NO | stopped | R | removed | `—` |
| `emit:OSError` | 2 | 2 | NO | stopped | R | removed | `—` |
| `emit:KeyboardInterrupt` | escape KeyboardInterrupt | -2 | NO | stopped | R | removed | `—` |
| `emit:SystemExit` | escape SystemExit | 7 | NO | stopped | R | removed | `—` |
| `emit:BaseException` | escape BaseException | 1 | NO | stopped | R | removed | `—` |
| `emit_after:RuntimeError` | 2 | 2 | yes | stopped | R | removed | `—` |
| `emit_retry:success` | 2 | 2 | yes | stopped | R | removed | `terminated:injected-termination` |
| `emit_retry:OSError` | 2 | 2 | NO | stopped | R | removed | `—` |
| `emit_retry:Terminated` | 2 | 2 | NO | stopped | R | removed | `—` |
| `emit_retry:RuntimeError` | escape RuntimeError | 1 | NO | stopped | R | removed | `—` |
| `emit_retry:KeyboardInterrupt` | escape KeyboardInterrupt | -2 | NO | stopped | R | removed | `—` |
| `ignore:RuntimeError` | 2 | 2 | yes | stopped | R | removed | `internal:RuntimeError` |
| `ignore:KeyboardInterrupt` | escape KeyboardInterrupt | -2 | NO | ALIVE | T | RETAINED | `—` |
| `restore:RuntimeError` | escape RuntimeError | 1 | yes | stopped | I | removed | `—` |
| `install:RuntimeError` | escape RuntimeError | 1 | NO | n/a | T/R/R | n/a | `—` |
| `port_refuses:RuntimeError` | 2 | 2 | yes | stopped | R | RETAINED | `internal:RuntimeError` |
| `backstop:RuntimeError` | 2 | 2 | yes | ALIVE | R | RETAINED | `internal:RuntimeError` |
| `wait:OSError` | 2 | 2 | yes | stopped | R | RETAINED | `internal:OSError` |
| `wait:KeyboardInterrupt` | escape KeyboardInterrupt | -2 | NO | stopped | I | RETAINED | `—` |
| `rehash:RuntimeError` | 2 | 2 | yes | stopped | R | removed | `internal:RuntimeError` |
| `rehash:OSError` | 1 | 1 | yes | stopped | R | removed | `—` |
| `rehash:KeyboardInterrupt` | escape KeyboardInterrupt | -2 | NO | stopped | I | removed | `—` |
| `check:RuntimeError` | 2 | 2 | yes | stopped | R | removed | `internal:RuntimeError` |
| `end_clock:RuntimeError` | escape RuntimeError | 1 | NO | stopped | R | removed | `—` |
| `mkstemp:OSError` | 2 | 2 | yes | n/a | R | n/a | `log-mkstemp-failed:injected-mkstemp` |
| `launch:OSError` | 2 | 2 | yes | n/a | R | removed | `unexpected:OSError` |
| `model_hash:OSError` | escape OSError | 1 | NO | n/a | R | n/a | `—` |
| `server_hash:OSError` | 2 | 2 | NO | n/a | R | n/a | `—` |
| `bindings:RuntimeError` | escape RuntimeError | 1 | NO | n/a | R | n/a | `—` |

## Direct listener and traceback evidence

The following `ss -ltnp` lines were recorded before external cleanup (each invocation exit 0). The snapshot after cleanup had no matching listener and the tracked Popen was reaped in every case.

### `teardown:KeyboardInterrupt`

```text
LISTEN 0      5          127.0.0.1:34185      0.0.0.0:*    users:(("python3",pid=3707397,fd=3))
```

### `teardown:BaseException`

```text
LISTEN 0      5          127.0.0.1:36809      0.0.0.0:*    users:(("python3",pid=3710614,fd=3))
```

### `ignore:KeyboardInterrupt`

```text
LISTEN 0      5          127.0.0.1:39545      0.0.0.0:*    users:(("python3",pid=3722344,fd=3))
```

### `backstop:RuntimeError`

```text
LISTEN 0      5          127.0.0.1:32821      0.0.0.0:*    users:(("python3",pid=3724636,fd=3))
```

### Trace: `teardown:KeyboardInterrupt`

```text
Traceback (most recent call last):
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 181, in child
    result['main_return'] = mod.main(argv)
                            ~~~~~~~~^^^^^^
  File "/tmp/KamaR17.InternalFaultPath-clone/tools/kama-llamacpp-live.py", line 1267, in main
    td = teardown(proc, port, log_path)
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 110, in teardown
    trip('teardown')
    ~~~~^^^^^^^^^^^^
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 57, in trip
    raise cls('injected-' + label)
KeyboardInterrupt: injected-teardown
```

### Trace: `emit_retry:RuntimeError`

```text
Traceback (most recent call last):
  File "/tmp/KamaR17.InternalFaultPath-clone/tools/kama-llamacpp-live.py", line 1393, in main
    _emit(receipt, args.out)
    ~~~~~^^^^^^^^^^^^^^^^^^^
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 164, in emit
    trip('emit', 'Terminated')
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 53, in trip
    raise mod.Terminated('injected-termination')
live_under_test.Terminated: injected-termination

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 181, in child
    result['main_return'] = mod.main(argv)
                            ~~~~~~~~^^^^^^
  File "/tmp/KamaR17.InternalFaultPath-clone/tools/kama-llamacpp-live.py", line 1402, in main
    _emit(receipt, args.out)
    ~~~~~^^^^^^^^^^^^^^^^^^^
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 166, in emit
    trip('emit_retry')
    ~~~~^^^^^^^^^^^^^^
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 57, in trip
    raise cls('injected-' + label)
RuntimeError: injected-emit_retry
```

### Trace: `end_clock:RuntimeError`

```text
Traceback (most recent call last):
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 181, in child
    result['main_return'] = mod.main(argv)
                            ~~~~~~~~^^^^^^
  File "/tmp/KamaR17.InternalFaultPath-clone/tools/kama-llamacpp-live.py", line 1391, in main
    receipt['ended_utc'] = _utc_now()
                           ~~~~~~~~^^
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 141, in clock
    trip('end_clock')
    ~~~~^^^^^^^^^^^^^
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 57, in trip
    raise cls('injected-' + label)
RuntimeError: injected-end_clock
```

### Trace: `restore:RuntimeError`

```text
Traceback (most recent call last):
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 181, in child
    result['main_return'] = mod.main(argv)
                            ~~~~~~~~^^^^^^
  File "/tmp/KamaR17.InternalFaultPath-clone/tools/kama-llamacpp-live.py", line 1416, in main
    signal.signal(sig, handler)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 95, in sigset
    trip('restore-handler')
    ~~~~^^^^^^^^^^^^^^^^^^^
  File "/tmp/KamaR17.InternalFaultPath-probes/faults.py", line 57, in trip
    raise cls('injected-' + label)
RuntimeError: injected-restore-handler
```

## Residual risk and verification gaps

- **Finite controls are not universal fault coverage.** `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:260-287,319-321,560-563` injects only teardown RuntimeError for K6 and considers any nonzero+receipt a rejection. It does not assert exact return 2, pre-wrapper-exit child death, restored signal dispositions, or log deletion. Therefore the reported current 0 accepted-bad can be true while the findings above remain true; this review does not change that recorded count.
- **No LSP device is mounted.** `read(xd://lsp)` returned `No such tool: xd://lsp` and listed mounted devices without lsp. Consequently status, references, definition, and diagnostics could not be requested, and there was no cold indexing result to interpret. Used exact-file textual fallback for definition/caller review (CLI `sys.exit(main())`, K6 importlib wrapper, and its dispatch), not semantic proof from grep.
- These tests exercised real subprocesses and loopback HTTP, but **not b11755**, descendant process trees, privilege-denied kills, kernel uninterruptible states, disk-full publication, logging-write failure, FD exhaustion, or every BaseException subclass. Source-only projections are explicitly marked. The observed double-fault backstop case is not a production occurrence-rate claim.
- The 42 launched fake-server ports, recorded by the wrapper, excluded both 8080 and 34113 and every registry consumer port. At most one fake existed at a time; all bound only 127.0.0.1. No registered port was contacted or bound. The before/after ss checks did not connect to any service.
- Canonical-runtime selection, same-identity rerouting, saturation, and resume_continuity_v1 are not changed by this scoped tool diff and were not attacked here. No resume path or alternate runtime was invoked, and no claim about those contracts is made.
- All failed test obligations are reported rather than repaired: the assignment permits only this report in the lane. The preflight model-hash OSError escape is inherited behavior and appears in the inventory/matrix, not misattributed to the round's new code.

## Exact executed shell commands and exit codes

All lane code executions were in the required clone and used `PYTHONDONTWRITEBYTECODE=1`; none ran from the lane working directory. Read/glob/grep device calls are source inspection, not shell executions.

1. Cwd `/tmp`, exit **0**:
   ```sh
   git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.InternalFaultPath-clone && git -C /tmp/KamaR17.InternalFaultPath-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3
   ```
2. Cwd `/home/vgpnk/Projects/shokunin/kama-shokunin`, read-only, exit **0**:
   ```sh
   git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tools/kama-llamacpp-live.py
   ```
3. Cwd `/tmp/KamaR17.InternalFaultPath-clone`, exit **0**:
   ```sh
   python3 --version && ss --version
   ```
4. Same clone cwd, initial listener inventory, exit **0**:
   ```sh
   ss -ltnp
   ```
5. Same clone cwd, matrix driver, exit **0**, final stdout `completed=48`:
   ```sh
   PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/KamaR17.InternalFaultPath-probes/faults.py
   ```
   The exact driver is preserved below. It invokes `sys.executable` (`python3`) with absolute script path, `-B`, `--child`, and each matrix case; each subprocess's exact native exit code is in the matrix. It sets TMPDIR to that case's absolute sandbox path and PYTHONDONTWRITEBYTECODE=1 without printing environment values. Each of its 96 `ss -ltnp` calls (two per case) exited 0; `all_external_cleanup_passed=true` in the retained results projection. All 48 per-case post-cleanup observations had no owned listener or live tracked child.
6. Same clone cwd, exit **0**:
   ```sh
   sha256sum /tmp/KamaR17.InternalFaultPath-clone/tools/kama-llamacpp-live.py /tmp/KamaR17.InternalFaultPath-probes/faults.py /tmp/KamaR17.InternalFaultPath-probes/results.json
   ```
   Recorded hashes, in that order:
   ```text
   0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac
   efb1ba5b4cbc8aaf4af19d31e341567754d7520c7d5821c7c4797c9011e79de2
   979e9eaee425b2448147accd075fc371ca1c8773b5817b70ccea964b41676bd2
   ```
7. Cwd `/tmp`, final cleanup and listener confirmation, exit **0**:
   ```sh
   rm -rf -- /tmp/KamaR17.InternalFaultPath-clone /tmp/KamaR17.InternalFaultPath-probes && test ! -e /tmp/KamaR17.InternalFaultPath-clone && test ! -e /tmp/KamaR17.InternalFaultPath-probes && ss -ltnp
   ```
   Both scratch roots were absent; the final listener list contained no owned fake-server PID. Other seats' and host listeners were not touched. The report's reproduction text was retained in memory before removal; no scratch evidence is presented as a still-existing file.

## Installs and write boundary

**Installs/updates: none.** Existing Python and iproute2 sufficed; no pacman transaction, service restart, or privileged host mutation occurred.

Only lane write: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/falsify/advice/InternalFaultPath.md`. All code/data scratch and the clone were removed before this report was written. No lane tool, gate, or counting command ran against the lane working directory; no jj or lane Git write was used. A tooling-only QA notice was sent through `xd://report_issue` because a raw read omitted the final LF; the script reproduced below restores that LF and matches the recorded script digest.

## Reproduction appendix — exact tested driver

Save these bytes plus a final LF to `/tmp/KamaR17.InternalFaultPath-probes/faults.py`, after recreating the pinned clone with command 1. The script's parent creates its per-case fixture directories; execute command 5 from the clone. It automatically removes the leaked logs/processes after recording each pre-cleanup snapshot, but reproducing the review should also remove both scratch roots with command 7. This appendix is test machinery, not a proposed lane implementation.

```python
#!/usr/bin/env python3
"""Scoped reviewer fault probes; never modifies the checkout under test."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path('/tmp/KamaR17.InternalFaultPath-clone')
WORK = Path('/tmp/KamaR17.InternalFaultPath-probes')
TOOL = ROOT / 'tools/kama-llamacpp-live.py'
PROBE = ROOT / 'tools/kama-probe.sh'
SIGS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def child(case):
    wd = WORK / case.replace(':', '-')
    mod = load('live_under_test', TOOL)
    stage, _, kind = case.partition(':')
    old = {sig: signal.getsignal(sig) for sig in SIGS}
    originals = {
        'signal': signal.signal, 'killpg': os.killpg,
        'mkstemp': tempfile.mkstemp, 'popen': subprocess.Popen,
        'hash': mod.sha256_file, 'clock': mod._utc_now,
        'ready': mod.readiness_loop, 'teardown': mod.teardown,
        'emit': mod._emit, 'port_refuses': mod._port_refuses,
        'check': mod._check, 'bindings': mod.source_bindings,
    }
    result = {'case': case, 'fired': [], 'main_return': None, 'escaped': None,
              'receipt': False, 'child_pid': None, 'port': None}
    procs, logs, calls = [], [], {}

    def trip(label, exception=kind):
        result['fired'].append(label + ':' + exception)
        if exception == 'SystemExit':
            raise SystemExit(7)
        if exception == 'SetupError':
            raise mod.SetupError('injected-setup-error')
        if exception == 'Terminated':
            raise mod.Terminated('injected-termination')
        cls = {'RuntimeError': RuntimeError, 'OSError': OSError,
               'KeyboardInterrupt': KeyboardInterrupt,
               'BaseException': BaseException}[exception]
        raise cls('injected-' + label)

    def popen(argv, *a, **kw):
        if argv[0] == str(wd / 'srv/fake_server.py'):
            if stage == 'launch':
                trip('launch')
            proc = originals['popen'](argv, *a, **kw)
            procs.append((proc, proc.poll, proc.wait))
            result['child_pid'] = proc.pid
            result['port'] = int(argv[argv.index('--port') + 1])
            if stage == 'wait':
                first = True
                original_wait = proc.wait
                def wait(*wa, **wk):
                    nonlocal first
                    if first:
                        first = False
                        trip('wait')
                    return original_wait(*wa, **wk)
                proc.wait = wait
            return proc
        return originals['popen'](argv, *a, **kw)

    def mkstemp(*a, **kw):
        is_log = kw.get('prefix') == 'kama-llamacpp-live-'
        if is_log and stage == 'mkstemp':
            trip('mkstemp')
        fd, path = originals['mkstemp'](*a, **kw)
        if is_log:
            logs.append(path)
        return fd, path

    def sigset(sig, handler):
        if stage == 'install' and sig == signal.SIGTERM and callable(handler):
            trip('install-second-handler')
        if stage == 'ignore' and handler == signal.SIG_IGN:
            trip('ignore-handler')
        if stage == 'restore' and handler == old.get(sig):
            trip('restore-handler')
        return originals['signal'](sig, handler)

    def ready(*a, **kw):
        answer = originals['ready'](*a, **kw)
        result['readiness_reached'] = answer[3]
        if stage == 'readiness':
            trip('readiness')
        if stage == 'signalrun':
            result['fired'].append('signalrun:' + kind)
            os.kill(os.getpid(), getattr(signal, kind))
        return answer

    def teardown(*a, **kw):
        if stage in ('teardown', 'backstop'):
            trip('teardown')
        answer = originals['teardown'](*a, **kw)
        if stage == 'teardown_after':
            trip('teardown_after')
        return answer

    def killpg(pid, sig):
        if stage == 'backstop' and sig == signal.SIGKILL:
            trip('killpg')
        return originals['killpg'](pid, sig)

    def port_refuses(*a, **kw):
        calls['port_refuses'] = calls.get('port_refuses', 0) + 1
        if stage == 'port_refuses' and calls['port_refuses'] == 1:
            trip('port_refuses')
        return originals['port_refuses'](*a, **kw)

    def file_hash(path):
        if Path(path) == wd / 'model.gguf':
            calls['model_hash'] = calls.get('model_hash', 0) + 1
            if stage == 'model_hash' and calls['model_hash'] == 1:
                trip('model_hash')
            if stage == 'rehash' and calls['model_hash'] == 2:
                trip('rehash')
        if stage == 'server_hash' and Path(path) == wd / 'srv/fake_server.py':
            trip('server_hash')
        return originals['hash'](path)

    def clock():
        calls['clock'] = calls.get('clock', 0) + 1
        if stage == 'end_clock' and calls['clock'] == 2:
            trip('end_clock')
        return originals['clock']()

    def check(cid, *a, **kw):
        if stage == 'check' and cid == 'teardown_graceful':
            trip('check')
        return originals['check'](cid, *a, **kw)

    def bindings():
        if stage == 'bindings':
            trip('bindings')
        return originals['bindings']()

    def emit(*a, **kw):
        calls['emit'] = calls.get('emit', 0) + 1
        n = calls['emit']
        if stage == 'emit':
            trip('emit')
        if stage == 'emit_after':
            originals['emit'](*a, **kw)
            trip('emit_after')
        if stage == 'emit_retry':
            if n == 1:
                trip('emit', 'Terminated')
            if kind != 'success':
                trip('emit_retry')
        return originals['emit'](*a, **kw)

    subprocess.Popen, tempfile.mkstemp = popen, mkstemp
    signal.signal, os.killpg = sigset, killpg
    mod.readiness_loop, mod.teardown = ready, teardown
    mod._port_refuses, mod.sha256_file = port_refuses, file_hash
    mod._utc_now, mod._check = clock, check
    mod.source_bindings, mod._emit = bindings, emit
    model = wd / 'model.gguf'
    argv = ['--server', str(wd / 'srv/fake_server.py'), '--model', str(model),
            '--model-sha256', hashlib.sha256(model.read_bytes()).hexdigest(),
            '--alias', 'internal-fault-review', '--probe', str(PROBE),
            '--ready-timeout', '8', '--out', str(wd / 'receipt.json')]
    try:
        result['main_return'] = mod.main(argv)
    except BaseException as exc:
        result['escaped'] = type(exc).__name__
        result['traceback'] = traceback.format_exc()
        raise
    finally:
        # Snapshot BEFORE the reviewer reaps anything or restores handlers.
        result['handlers'] = {
            sig.name: ('restored' if signal.getsignal(sig) == old[sig]
                       else 'ignored' if signal.getsignal(sig) == signal.SIG_IGN
                       else 'tool-handler') for sig in SIGS}
        result['logs_remaining'] = [p for p in logs if Path(p).exists()]
        result['child_alive'] = any(poll() is None for _, poll, _ in procs)
        result['child_returncodes'] = [poll() for _, poll, _ in procs]
        receipt = wd / 'receipt.json'
        if receipt.exists():
            doc = json.loads(receipt.read_text())
            result.update(receipt=True, setup_error=doc.get('setup_error'),
                          internal_fault=doc.get('internal_fault'),
                          failed=[c['id'] for c in doc['checks']
                                  if not c['passed']], teardown=doc['teardown'])
        result['calls'] = calls
        before = subprocess.run(['ss', '-ltnp'], capture_output=True, text=True)
        result['ss_before_cleanup_exit'] = before.returncode
        result['own_listener_before_cleanup'] = [
            ln for ln in before.stdout.splitlines()
            if result['port'] and any(
                token == '127.0.0.1:' + str(result['port'])
                for token in ln.split())]
        signal.signal, os.killpg = originals['signal'], originals['killpg']
        subprocess.Popen, tempfile.mkstemp = originals['popen'], originals['mkstemp']
        for proc, poll, wait in procs:
            if poll() is None:
                originals['killpg'](proc.pid, signal.SIGKILL)
                wait(timeout=5)
        for sig, handler in old.items():
            originals['signal'](sig, handler)
        for path in logs:
            Path(path).unlink(missing_ok=True)
        result['external_cleanup_child_alive'] = any(
            poll() is None for _, poll, _ in procs)
        after = subprocess.run(['ss', '-ltnp'], capture_output=True, text=True)
        result['ss_after_cleanup_exit'] = after.returncode
        result['own_listener_after_cleanup'] = [
            ln for ln in after.stdout.splitlines()
            if result['port'] and any(
                token == '127.0.0.1:' + str(result['port'])
                for token in ln.split())]
        (wd / 'snapshot.json').write_text(json.dumps(result, indent=2) + '\n')
    return result['main_return']


CASES = ['baseline:none']
CASES += ['readiness:' + e for e in
          ('SetupError', 'Terminated', 'RuntimeError', 'OSError',
           'KeyboardInterrupt', 'SystemExit', 'BaseException')]
CASES += ['signalrun:' + e for e in ('SIGINT', 'SIGTERM', 'SIGHUP')]
CASES += ['teardown:' + e for e in
          ('RuntimeError', 'OSError', 'Terminated', 'KeyboardInterrupt',
           'SystemExit', 'BaseException')]
CASES += ['teardown_after:' + e for e in ('RuntimeError', 'KeyboardInterrupt')]
CASES += ['emit:' + e for e in
          ('RuntimeError', 'OSError', 'KeyboardInterrupt', 'SystemExit',
           'BaseException')]
CASES += ['emit_after:RuntimeError']
CASES += ['emit_retry:' + e for e in
          ('success', 'OSError', 'Terminated', 'RuntimeError', 'KeyboardInterrupt')]
CASES += ['ignore:' + e for e in ('RuntimeError', 'KeyboardInterrupt')]
CASES += ['restore:RuntimeError', 'install:RuntimeError']
CASES += ['port_refuses:RuntimeError', 'backstop:RuntimeError']
CASES += ['wait:OSError', 'wait:KeyboardInterrupt']
CASES += ['rehash:' + e for e in ('RuntimeError', 'OSError', 'KeyboardInterrupt')]
CASES += ['check:RuntimeError', 'end_clock:RuntimeError',
          'mkstemp:OSError', 'launch:OSError', 'model_hash:OSError',
          'server_hash:OSError', 'bindings:RuntimeError']


def parent():
    controls = load('controls_source', ROOT / 'tests/llamacpp-live/controls.py')
    rows = []
    for case in CASES:
        wd = WORK / case.replace(':', '-')
        srv = wd / 'srv'
        srv.mkdir(parents=True)
        fake = srv / 'fake_server.py'
        fake.write_text(controls._fake_source('k0', srv / 'fake.pid'))
        fake.chmod(0o755)
        (wd / 'model.gguf').write_bytes(controls.MODEL_BYTES)
        env = dict(os.environ)
        env.update(TMPDIR=str(wd), PYTHONDONTWRITEBYTECODE='1')
        cmd = [sys.executable, '-B', str(Path(__file__).resolve()), '--child', case]
        cp = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT),
                            env=env, timeout=40)
        (wd / 'stderr.txt').write_text(cp.stderr)
        (wd / 'stdout.txt').write_text(cp.stdout)
        snap = json.loads((wd / 'snapshot.json').read_text())
        snap.update(wrapper_exit=cp.returncode, command=cmd,
                    stderr_tail=cp.stderr[-1500:])
        rows.append(snap)
        print(json.dumps({k: snap.get(k) for k in
                         ('case', 'main_return', 'escaped', 'wrapper_exit',
                          'receipt', 'child_alive', 'handlers', 'logs_remaining',
                          'setup_error', 'internal_fault', 'fired')}), flush=True)
        if snap['external_cleanup_child_alive'] or snap['own_listener_after_cleanup']:
            raise RuntimeError('reviewer cleanup failed for ' + case)
    data = {'tool_sha256': hashlib.sha256(TOOL.read_bytes()).hexdigest(),
            'python': sys.version.split()[0], 'rows': rows}
    (WORK / 'results.json').write_text(json.dumps(data, indent=2) + '\n')
    print('completed=' + str(len(rows)), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(child(sys.argv[2]) if len(sys.argv) > 1 and sys.argv[1] == '--child'
             else parent())
```
