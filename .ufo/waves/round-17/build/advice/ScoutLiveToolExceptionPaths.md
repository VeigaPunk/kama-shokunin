VERDICT: n/a — read-only enumeration; the round-16 `KeyError('returncode')` escape is still present and file-identical, and every exception path in `main()` is now mapped to receipt/exit.

# Scope

`tools/kama-llamacpp-live.py` sha256 `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4` (1078 lines) — byte-identical to the sha the round-16 review inspected (`ReviewLiveHarnessCode.md:4`), so its M4 finding still applies verbatim. Static reading only; no execution (read-only seat). The one empirical datum is quoted, not reproduced.

# The escape (round-16 M4) — confirmed present

Mechanism, exact lines:

1. `tools/kama-llamacpp-live.py:1019` calls `teardown(proc, port, log_path)` inside the outer `finally`.
2. `:1020-1021` catches **any** `Exception` from it and stores a dict with exactly one key: `receipt['teardown'] = {'error': f'{type(exc).__name__}: {exc}'}`.
3. `:1023` tests only `if receipt['teardown'] is not None:` — true for the error dict — then `:1026` evaluates `receipt['teardown']['returncode'] is not None` → `KeyError('returncode')`. `:1027`/`:1028` would read the same missing keys.
4. The `try` at `:1016` has no `except`; the only handler below is `finally:` at `:1042` (exit-code recompute, `:1043-1045`), which does not swallow. The KeyError therefore propagates out of the outer `finally` (`:1010`) and out of `main()`.
5. Consequences: `:1049` (`ended_utc`), `:1052` (`_emit`) and `:1069-1073` (handler restore, `emitted`, return) are **never reached** — no receipt at all, no `ended_utc`, `emitted` untouched, and (relevant only to in-process callers) SIGINT/SIGTERM/SIGHUP are left as `SIG_IGN` because restore happens solely at `:1070-1071`.

`[INFERENCE]` interpreter exit status on that path is 1 (uncaught exception), not 2, and the only stderr is the traceback. Round-16 measured exactly this: `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:34` — "`ESCAPED KeyError KeyError('returncode')`, `receipt_written False`".

**Reachability.** `teardown()` (`:656-712`) is otherwise defensive, so this is a latent landmine rather than a hot path:

| teardown site | covered by | residual |
|---|---|---|
| `:664-667` `os.killpg(SIGTERM)` | `except (ProcessLookupError, PermissionError, OSError)` (all OSError) | none |
| `:671-672` `proc.wait(TERM_GRACE)` | `except subprocess.TimeoutExpired` `:672` | any other exception type from `wait` is uncaught |
| `:676` `killpg(SIGKILL)` | same OSError tuple `:676` | none |
| `:679-681` `proc.wait(5)` | `TimeoutExpired` swallowed at `:680` | `returncode` stays `None` (D-state) → check fails, no raise |
| `:686-691` port probe | `ConnectionRefusedError`→True, `OSError`→False | none |
| `:694` `open(log_path, 'rb')` | `except OSError` `:701` | `TypeError` if `log_path` were `None` — unreachable from `main()` (mkstemp always precedes Popen) |
| `:704-706` log reduce | none needed | regex/slice only |
| `:708-709` unlink | `except OSError: pass` | none |

So without monkeypatching (round-16's method) or a future edit, the reachable triggers are a non-`TimeoutExpired` from `proc.wait` and any `BaseException`-adjacent bug in teardown. Once triggered, the failure mode is total receipt loss, which is precisely the C2 "receipt always written on internal faults, exit 2" target.

# Full exception ledger for `main()` (772-1078)

Receipt column = is a receipt emitted (stdout or `--out`)? Exit = process status.

## Pre-receipt (no receipt object exists; all deliberate unless noted)

| lines | trigger | handler | receipt | exit |
|---|---|---|---|---|
| 773 `args = build_parser().parse_args(argv)` | bad argv / `--help` → `SystemExit` | none (SystemExit) | no | 2 / 0 |
| 776-780 `if not server_arg:` | no `llama-server` on PATH | explicit `return 2` | no | 2 |
| 782-785 | server not a file / not executable | `return 2` | no | 2 |
| 786-789 | model missing | `return 2` | no | 2 |
| 790-793 | probe missing | `return 2` | no | 2 |
| **795 `model_sha = sha256_file(args.model)`** | OSError (EACCES, file removed after the 786 stat, EISDIR race) | **none — the `try` starts at 803** | **no** | **1, traceback** |
| 796-801 | digest mismatch | `return 3` | no | 3 |
| 803-812 | `SetupError` from `refused_ports` (:200) or `pick_port` (:236, :238, :246, :254) | `except SetupError` :813 | no | 2 |
| 804-812 | OSError from hashing / registry read | `except OSError` :816 | no | 2 |

`795` is a genuine hole: existence is checked, readability is not, and the check sits 8 lines above the only `try` that could map it.

## Receipt built, before the main `try` (820-888)

- `:822` `_utc_now()` and `:860-870` argv assembly are exception-free.
- `:871-874` self-hash guarded: `except OSError: pass  # self-hash unverifiable is recorded as null, not fatal`.
- `:887` `old_handlers[sig] = signal.signal(sig, _term_handler)` — raises `ValueError` if `main()` is called off the main thread → traceback, exit 1, no receipt `[INFERENCE: only affects imported/in-process callers; the CLI is single-threaded]`.
- A signal delivered between `:887` and `:889` invokes `:882-883` `raise Terminated(f'signal {signum}')` **outside any try** → traceback, exit 1, no receipt, and no teardown is needed (child not yet launched). `[INFERENCE: microsecond window]`

## Inside the main `try` (889-1009) — receipt is always emitted here *unless the finally raises*

| lines | trigger | handler | exit |
|---|---|---|---|
| 891-894 | `tempfile.mkstemp` OSError → `raise SetupError(f'log-mkstemp-failed:{exc}') from exc` | `except SetupError` :1001 | 2 |
| 895 `log_file = os.fdopen(log_fd, 'wb')` | OSError/ValueError from fdopen | generic :1007 → `unexpected:<Type>` | 2 |
| 908-911 | `subprocess.Popen` OSError (ENOENT, EPERM, fork EAGAIN); `finally: log_file.close()` may mask it | **generic :1007 → `unexpected:OSError`** (never mapped to SetupError) | 2 |
| 914-918 | `readiness_loop` returns `ownership` outside `{True,False,None}` → `KeyError` on the map at :916-918 | generic :1007 `[INFERENCE: unreachable with current callee]` | 2 |
| 924 `raise SetupError(fail)` | `fail` from :496 `server-exited-early-rc{rc}`, :500/:513 ownership codes, :504/:517 `ready-timeout` | :1001 | 2 |
| 930, 972, 979 `raise SetupError(err)` | `verify_live` codes: :540 `child-exited-rc{rc}`, :543-545 `port-listener-not-our-child` / `port-listener-ownership-unproven` | :1001 | 2 |
| 933 `captures.pop('_models_doc')` | KeyError if `ready_captures` shape changes | generic :1007 `[INFERENCE: current callee always sets it, :585]` | 2 |
| 937/957/961 | KeyError on capture keys | generic :1007 `[INFERENCE: :567-608 always sets health/props/metrics/slots]` | 2 |
| 973/629 | `subprocess.run` OSError (bash absent from the allowlisted `PATH`) | generic :1007 | 2 |
| 981 `ok_probe, bad_probe = receipt['probes']` | ValueError if the list length ≠ 2 | generic :1007 `[INFERENCE: unreachable — the loop at 968-974 appends both or raises first]` | 2 |
| any bytecode | `Terminated` from `_term_handler` :882-883 | `except Terminated` :1004 → `terminated:signal N` | 2 |

Also uncaught but routed here from callees: `readiness_loop`'s own `finally: conn._close()` (`:518-519`) — a raise from `conn.close()` replaces the function's return and lands in :1007 as `unexpected:<Type>`.

## The outer `finally` (1010-1045) — where receipts die

| lines | trigger | handler | receipt | exit |
|---|---|---|---|---|
| 1014-1015 `signal.signal(sig, signal.SIG_IGN)` | ValueError off-main-thread | none | no | 1 |
| 1019-1021 | any `Exception` from `teardown` → one-key dict | caught, then **crashes at 1026** | **no** | **1 (KeyError)** |
| 1026-1028 | keyed reads `returncode`, `sigkill_sent` | none | — | — |
| 1029-1032 | `port_refuses` read; skipped/crashed on the error dict | none | — | — |
| 1033-1036 `sha256_file(args.model)` | OSError → `rehash-error:{exc}` string | caught :1035; `model_unchanged` fails | yes | 1 |
| 1037-1040 `_check('model_unchanged', ...)` | `DOC[check_id]` KeyError if a new id lacks a DOC row (`:714-717`, DOC at :78-119) | none → escapes the finally | no | 1 `[INFERENCE: only if C2 adds an undocumented check id]` |
| 1042-1045 | recompute `exit_code` **only** when `setup_error is None`; runs even on the KeyError path, then the KeyError keeps propagating | finally | — | — |

Two branches matter for C2's repair:
- `:1017` `if log_path is not None or proc is not None:` — after a `log-mkstemp-failed` SetupError both are `None`, so teardown is skipped entirely and the receipt carries `teardown: null` plus exactly one check (`model_unchanged`). `check-receipt.py:53-64,614-616` then reports nine absent required checks; `:177-179` rejects the non-null `setup_error` anyway.
- After a **Popen failure** (`:909`) with `log_path` set and `proc is None`, teardown runs: `:663` `if proc.returncode is None:` is guarded by `if proc is not None:` (`:662`), so `returncode` stays `None` while the port probe against the released bind(:0) port (`pick_port` `:248-255`) yields `port_refuses: True` → **`teardown_port_closed` passes with no child ever existing**; only `teardown_exited` fails. This is the strongest instance of the vacuity C2 is chartered to remove.

## Epilogue (1047-1074)

| lines | trigger | handler | receipt | exit |
|---|---|---|---|---|
| 1049 | `_utc_now()` — exception-free | — | — | — |
| 1052 `_emit` OSError (missing parent dir, EACCES, ENOSPC, `--out` is a directory, BrokenPipe on stdout) | `except OSError` :1065-1068 prints `cannot write receipt` | **no receipt** (the only channel failed) | 2 |
| 1052 | `json.dumps(..., allow_nan=False)` `:756-758` ValueError (NaN/Inf) or TypeError (non-serialisable) | **none — :1065 catches OSError only** | no | 1 traceback `[INFERENCE: latent; no NaN/Inf source observed in receipt fields]` |
| 1054-1064 `except Terminated` + one retry | signals are `SIG_IGN` from :1015 until :1070-1071, so this arm **cannot fire from the installed handlers** | — | — | dead code `[INFERENCE]` |
| 1069-1071 | handler restore, runs on every path that reaches here | finally | — | — |
| 1072-1073 `if not emitted: return 2` | second explicit exit-2-without-receipt branch | — | no | 2 |
| 1071→1074 | signal after restore raises `Terminated` outside any try | none | receipt already written | 1 `[INFERENCE: microsecond window]` |

# Exit-code summary

- **0** only via `:1000` / recompute `:1044` with all checks passed and no `setup_error`.
- **1** via check failure (`:1000`, `:1044`), or via any of the traceback escapes: `:795`, `:887`, `:1015`, the KeyError at `:1026`, `json.dumps` at `:1052`, post-restore signal at `:1071`.
- **2** via the deliberate pre-receipt returns (`:780,785,789,793,815,818`), every `SetupError`/`Terminated`/generic handler (`:1001-1009`), and `_emit` OSError (`:1065`,`:1072`).
- **3** only for model digest mismatch (`:801`).

# Adjacent non-exception escape worth folding into C2

`verify_live` returns ownership `None` on the child-exit branch (`:539-540`), and `main()` stores it raw at `:928`, `:970`, `:977`, overwriting the valid `child|foreign|unproven` mapping written at `:916-918`. Round-16's receipt shows the result: `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:149-151` — "`port_listener_ownership: null`, which the gate rejects". Not an exception, but an error-return path that silently breaks the receipt schema.

# Limitations

- No execution: all reachability claims are static except where round-16's fault injection is quoted. No llama-server, fake server, or port was touched; nothing was installed.
- `[INFERENCE]` markers above flag interpreter behaviour (exit 1, traceback), dead-code arms, and unreachable-but-keyed reads.
- Did not evaluate `check-receipt.py`'s v2 requirements beyond the one shape point; that is another seat's assignment.

# Installs

None.
