VERDICT: confirm — every v3 exit-path obligation is currently unmet, and two undeclared codes (exit 0 via `--help`, exit 1 via an uncaught pre-launch `OSError`) can be returned with no receipt at all.

# Recon — every exit path of `tools/kama-llamacpp-live.py main()` (frozen copy, sha256 0efd1723…46ac)

Frozen source read: `.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py` (1423 lines).
Behavioural witnesses were run in a scratch lane root under
`/tmp/kama-r18-ScoutToolExitPaths` (copies of the frozen tool, `kama-probe.sh` and
`registry/endpoint-consumers.tsv`; a 12-byte fake model; a `#!/bin/sh sleep 30`
fake server) and the scratch tree is removed. No lane file, receipt or port was touched;
no llama-server was started by this seat.

## 1. Exit-path table

`R` = writes a receipt. `✎` = the v3 contract must change this path. Line numbers are the
frozen file's.

| # | Line(s) | Trigger | R | Exit today | Note |
|---|---------|---------|---|-----------|------|
| 1 | 995 | `build_parser().parse_args(argv)`, usage error | no | 2 | argparse `SystemExit(2)`; before any receipt exists |
| 2 | 995 | `--help` | no | **0** ✎ | argparse `SystemExit(0)`; **exit 0 = "pass" with no receipt** (observed `rc=0`) |
| 3 | 1000-1002 | no `llama-server` on PATH | no | 2 | |
| 4 | 1004-1007 | server not executable | no | 2 | |
| 5 | 1008-1011 | model missing | no | 2 | |
| 6 | 1012-1015 | probe missing | no | 2 | |
| 7 | 1017 | model exists but unreadable (`EACCES`/I/O) | no | **1** ✎ | unguarded `model_sha = sha256_file(args.model)`; observed `rc=1` + `PermissionError` traceback (defect) |
| 8 | 1018-1023 | model digest mismatch | no | **3** ✎ | `return 3`; outside the declared set {0,1,2}; advertised at 954 `mismatch -> exit 3` |
| 9 | 1025-1037 | `SetupError` in identity/registry/port setup | no | 2 | `registry-unreadable`, `port-in-use`, `no-free-unregistered-port` |
| 10 | 1038-1040 | `OSError` in the same block | no | 2 | |
| 11 | 1100-1102 | self-hash `OSError` | — | n/a | swallowed by design (`pass`) |
| 12 | 1113-1115 | `signal.signal` install, unguarded | no | 1 | `ValueError` if called off the main thread [INFERENCE] |
| 13 | before 1114 | SIGINT/SIGTERM/SIGHUP before handlers installed | no | 130/143/129 | default disposition; no receipt [INFERENCE] |
| 14 | 1119-1122 | temp-log `mkstemp` fails | **yes** | 2 | receipt with `setup_error=log-mkstemp-failed:…` and 3 **false** checks (observed, see §4-E6) |
| 15 | 1137-1140 → 1247 | `Popen` raises (bad interpreter etc.) | **yes** | 2 | observed `setup_error=unexpected:FileNotFoundError`, 3 false checks (§4-E7) |
| 16 | 1144-1156 | `readiness_loop` not ready (`ready-timeout`, early exit, ownership) | **yes** | 2 | `SetupError(fail)` |
| 17 | 1159-1162 | `verify_live` pre-captures fails | **yes** | 2 | |
| 18 | 1209-1212, 1216-1219 | `verify_live` before/after probes fails | **yes** | 2 | ✎ checks already built at 1175-1237 are **dropped** (only stored at 1239) |
| 19 | 1239-1240 | normal completion | **yes** | 0 / 1 | ✎ `exit_code = 0 if all(c['passed'] for c in checks) else 1` — dead assignment, always overwritten at 1376-1378 |
| 20 | 1241-1243 | `SetupError` | **yes** | 2 | |
| 21 | 1244-1246 | `Terminated` (SIGINT/TERM/HUP via the handler) | **yes** | 2 | teardown still runs in the `finally` |
| 22 | 1247-1249 | any other `Exception` in the try | **yes** | 2 | `setup_error=unexpected:<Type>` |
| 23 | 1250-1383 | **`BaseException` anywhere in the try or the `finally`** (KeyboardInterrupt, SystemExit, MemoryError) | **no** ✎ | 130 / *its own code* / 1 | finally completes, exception propagates past 1389; **`SystemExit(0)` becomes exit 0 with no receipt** (observed §4-E5/E5b) |
| 24 | 1265-1281 | `teardown` raises `Exception` | **yes** | 2 | fallback `td` at 1270-1280 does not unlink the log |
| 25 | 1286-1301 | last-chance `killpg`/`wait` raises | **yes** | 2 | `internal_fault` |
| 26 | 1369-1374 | any `internal_fault` | **yes** | 2 | |
| 27 | 1375-1378 | normal recompute from `receipt['checks']` | **yes** | 0 / 1 | ✎ `c.get('passed') is True` per check: a `null` check must map to 2, not 1 |
| 28 | 1379-1383 | last guard while recomputing | **yes** | 2 | |
| 29 | 1393-1394 | first `_emit` succeeds | **yes** | exit_code | the only normal receipt write |
| 30 | 1395-1404 | `Terminated` during emit → retry once | maybe | 2 | unreachable: handlers are `SIG_IGN` from 1258-1259 [INFERENCE] |
| 31 | 1406-1409 | `_emit` `OSError` (cannot write / broken stdout pipe) | no | 2 | evidence destroyed, code still 2 |
| 32 | 1410-1413 | `_emit` other `Exception` | no | 2 | |
| 33 | 1414-1416 | handler restore (unguarded) | — | — | a raise here replaces the exit code with a traceback [INFERENCE] |
| 34 | 1417-1418 | `not emitted` | no | 2 | |
| 35 | 1419, 1423 | `return exit_code` / `sys.exit(main())` | **yes** | 0/1/2 | |

**Receipt-write sites: exactly two calls**, `_emit(receipt, args.out)` at 1393 and the retry at
1402, both after the big `try/finally`. `_emit` (973-991) writes atomically with a sibling
`.kama-live-*` temp and `os.replace` (978-983), unlinking the temp only on `OSError`
(984-989); with `--out` absent it writes to stdout (990). Every exit in rows 1-13 and rows
23/31/32/34 produces **no receipt**.

## 2. The v3 obligations that do not exist yet

1. **✎ 50** `SCHEMA = 'kama-llamacpp-live/v2'` — v3 bump missing.
2. **✎ 830-832** `_check` hard-coerces: `'passed': bool(passed), 'observed': observed}`.
   There is no `evaluated` key and no way to express `passed: null`, so a not-evaluated
   check is indistinguishable from a failed one (R4's root).
3. **✎ 1345-1352** the loading check collapses `None` before `_check` sees it:
   `receipt.get('loading_observed') is True` / `and loading_envelopes_all(bodies) is True`.
   With zero 503s that is `False`, not `None`; `observed.not_evaluated_reason` has no source.
4. **✎ 1376-1378** the final exit predicate is
   `0 if all(... c.get('passed') is True ...) else 1` — one branch for "false" and "null".
   v3 needs three: any `False` → 1; else any null/`evaluated:false` → 2; else 0.
5. **✎ 1023** `return 3` for a digest mismatch (contract set is {0,1,2}); the help string at
   954 documents the extra code.
6. **✎ 1017** the model self-hash sits outside every `try`; an `OSError` there exits **1**,
   which v3 reserves for "a check is false".
7. **✎ 1117-1383** no `BaseException` guard. `except Exception` at 1247 does not catch
   `KeyboardInterrupt`/`SystemExit`; the emit block at 1389 is plain sequential code after
   the `finally`, so it is skipped. `controls.py` already assumes this: its K6 wrapper ends
   `except BaseException:` → `rc = 4` (`frozen/tests_llamacpp-live_controls.py:283-284`).
8. **✎ 1310-1366** the epilogue appends `teardown_graceful`, `teardown_port_closed`,
   `loading_envelope_graded` unconditionally, even when nothing was launched (E6/E7 below),
   recording `passed=False` for checks that were never evaluated.
9. **✎ 1333-1341** `teardown_port_closed` requires `port_refuses is True` **and**
   `port_listener_ownership == 'child'`. A child that died before the first HTTP contact
   leaves ownership `'unproven'`, so a provably closed port is reported as a **failed** check.
10. **✎ 1239** `receipt['checks'] = checks` happens only at the end; a `SetupError` at
    1212/1219 discards up to five already-evaluated checks and the receipt then reports only
    the epilogue four.
11. **✎** no top-level `outcome` field exists anywhere in the tool or gate
    (`grep -n outcome` → only prose) although v3 requires `{"pass","fail","not-evaluated","setup-error"}`.
12. **✎ 1240** is a dead verdict assignment (overwritten at 1376-1378 in every reachable
    path); remove it so one site computes the verdict.
13. **✎ 60** the only Python doc citation is `https://docs.python.org/3/library/subprocess.html`
    (used at 123); v3 requires `/3.14/`.
14. Row 2 (`--help` → 0, no receipt): the tool's "exit 0 = pass" promise is false unless the
    gate is made to require a receipt unconditionally.

## 3. Temp-log lifecycle

- Created at **1119-1120** `tempfile.mkstemp(prefix='kama-llamacpp-live-', suffix='.log')`
  (default temp dir; `TMPDIR` is also in `CHILD_ENV_KEYS`, line 84).
- Handed to the child as `stdout`/`stderr` (1130-1131 inside `popen_kwargs` at 1128), parent closes its copy at **1140**.
- Removed **only** at **824** `os.unlink(log_path)`, inside `teardown`'s nested `finally`
  (807-825), and `teardown` is called **only** at **1267**.
- Guard gaps [INFERENCE, narrow]: `out['port_refuses'] = _port_refuses(port)` at **804** is
  outside the try that owns the unlink; and main's fallback `td` at 1270-1280 never unlinks.
  A fault between 806 and 822 (or a `BaseException` raised before 1265, e.g. in the
  `SIG_IGN` loop at 1258) therefore leaks the log while `SystemExit`/`KeyboardInterrupt`
  also skip the receipt. Observed on this host: the KI, SystemExit, Popen-failure and
  mkstemp-failure runs all left **zero** extra `/tmp/kama-llamacpp-live-*.log` files
  (instrumented `teardown` entered and its own file was gone on return).

## 4. Observed runs (scratch copies of the frozen file; all exits quoted verbatim)

- **E1 unreadable model** (chmod 000): `rc=1`, `PermissionError: [Errno 13] … 'unreadable.gguf'`,
  no receipt → row 7.
- **E2 digest mismatch**: `rc=3`, `refusing to launch`, no receipt → row 8.
- **E3 `--help`**: `rc=0`, no receipt → row 2.
- **E4 no args**: `rc=2` (usage), no receipt → row 1.
- **E5 `KeyboardInterrupt` raised inside `readiness_loop`**: `MAIN_ESCAPED type=KeyboardInterrupt`,
  `receipt_exists=False`; teardown ran and removed its log → row 23.
- **E5b `SystemExit(0)` at the same point**: `MAIN_ESCAPED type=SystemExit`, `receipt_exists=False`
  → as a process this is **exit 0 with no receipt** → row 23.
- **E6 `mkstemp` fails (ENOSPC)**: `rc=2`, receipt `schema='kama-llamacpp-live/v2'`,
  `setup_error='log-mkstemp-failed:[Errno 28] No space left on device'`, checks
  `teardown_graceful=False`, `teardown_port_closed=False`, `loading_envelope_graded=False`,
  `model_unchanged=True` — three never-evaluated checks recorded as false → obligations 2/8.
- **E7 `Popen` fails (shebang to a missing interpreter)**: `rc=2`,
  `setup_error=unexpected:FileNotFoundError`, `port_refuses=True` yet
  `teardown_port_closed=False` (ownership stayed `'unproven'`) → obligations 8/9.
- **E8 R4 isolation** (all observations stubbed good, teardown synthetic-graceful):
  - zero loading 503: `loading_observed False`, ten checks `True`,
    `loading_envelope_graded passed=False`, `MAIN_RETURNED rc=1` → **R4 reproduced**;
  - exact loading envelope: `rc=0`, check `True`;
  - non-exact loading envelope: `rc=1`, check `False` (correct).
  The 1/0/1 triple proves the zero-loading exit 1 is attributable to the null→false
  collapse at 1347-1348 plus the single-branch predicate at 1376-1378, not to the harness.

## 5. Limits / remaining unknowns

- Row 12 (off-main-thread `signal.signal`) and row 33 are not exercised; no suite calls
  `main()` off the main thread today.
- The log-leak window in §3 was reasoned, not triggered; every reachable fault I ran cleaned
  its log.
- `Terminated` during emit (row 30) is dead by construction (`SIG_IGN` at 1258-1259); I did
  not attempt to force it.
- I did not grade the gate's treatment of these receipts (other seats own `check-receipt.py`);
  rows 19/27/29 are the tool side only.

## Installs

None. pacman untouched (host-wide pause respected); no `uv`/`npm`/binary install was needed.
