VERDICT: confirm — Python 3.14 docs state KeyboardInterrupt/SystemExit/GeneratorExit derive from BaseException; the frozen tool has zero `except BaseException` and every KeyboardInterrupt/SystemExit path I exercised escaped with exit 130/9 and no receipt.

# ScoutPyBaseException — C1 (operability), BaseException / exit-code contract

Lane root: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Frozen tool read at
`.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py` (never edited). Host
`python3 -V` → `Python 3.14.8`.

## 1. Doc citations (accessed 2026-10-20)

URL: <https://docs.python.org/3.14/library/exceptions.html> (redirects to
`https://docs.python.org/3.14/builtins/exceptions.html`). Page title:
"Built-in Exceptions — Python 3.14.8 documentation" — the 3.14 title is confirmed.

Class hierarchy (verbatim, <=25-word quotes):

- `KeyboardInterrupt`: "The exception inherits from `BaseException` so as to not be
  accidentally caught by code that catches `Exception`".
- `SystemExit`: "It inherits from `BaseException` instead of `Exception` so that it
  is not accidentally caught by code that catches `Exception`."
- `GeneratorExit`: "It directly inherits from `BaseException` instead of `Exception`
  since it is technically not an error."
- `BaseException` is "The base class for all built-in exceptions. It is not meant to
  be directly inherited by user-defined classes (for that, use `Exception`)."

Advice on catching it (same page):

- KI note: "Catching a `KeyboardInterrupt` requires special consideration. Because it
  can be raised at unpredictable points, it may, in some circumstances, leave the
  running program in an inconsistent state."
- KI advice: "It is generally best to allow `KeyboardInterrupt` to end the program as
  quickly as possible or avoid raising it entirely."
- `SystemExit` semantics: "When it is not handled, the Python interpreter exits; no
  stack traceback is printed." and "If the value is an integer, it specifies the
  system exit status".
- Derivation advice: "programmers are encouraged to derive new exceptions from the
  `Exception` class or one of its subclasses, and not from `BaseException`."

The docs never recommend a blanket `except BaseException`; the only stated rationale
for the split is that these three must not be swallowed by `except Exception`. Any
catch in C1 must therefore be deliberate, narrow, and terminate promptly.

## 2. Complete handler inventory (frozen tool)

Counts: `except Exception` = 11, `except BaseException` = **0**, bare `except:` = 0,
occurrences of the strings `KeyboardInterrupt`/`SystemExit` = **0**.

| line | clause | enclosing scope / phase |
|---|---|---|
| 375 | `except Exception:` (`# pragma: no cover - best effort hardening`) | `_preexec_pdeathsig` (forked **child** before exec; not parent control flow) |
| 755 | `except Exception:` | `_child_running` (teardown/backstop helper) |
| 1247 | `except Exception as exc:  # F1` | **main body** try (launch, readiness, captures, probes, verdict) |
| 1260 | `except Exception as exc:` | `finally`: SIG_IGN installation loop |
| 1268 | `except Exception as exc:` | `finally`: **`teardown(proc, port, log_path)` call** |
| 1281 | `except Exception as exc:` | `finally`: outer guard of the teardown block |
| 1300 | `except Exception as exc:` | `finally`: last-chance SIGKILL backstop |
| 1307 | `except Exception as exc:` | `finally`: `port_refuses` backstop |
| 1367 | `except Exception as exc:` | `finally`: teardown checks / model rehash block |
| 1379 | `except Exception as exc:  # last guard: never escape the finally` | `finally`: fault accounting + exit recompute |
| 1410 | `except Exception as exc:` | post-`finally` emit block (`_emit` fault) |

Every other handler is a typed catch (`OSError`, `ValueError`, `TypeError`,
`ConnectionRefusedError`, `subprocess.TimeoutExpired`, `ProcessLookupError`,
`PermissionError`, `Terminated`, `SetupError`, `urllib.error.*`) — lines 186, 192,
198, 211, 253, 267, 296, 298, 340, 358, 361, 413, 416, 420, 424, 490, 670, 688, 699,
723, 732, 765, 767, 784, 790, 795, 799, 816, 825, 984, 987, 1035, 1038, 1101, 1121,
1173, 1241, 1244, 1292, 1298, 1359, 1395, 1404, 1406. None of them is
`BaseException`, so none can catch KI or SE.

Structural fact that matters more than the count: the receipt emit at lines 1389-1412
is **after** the `try`/`finally` (`finally` starts line 1250), so any BaseException
that escapes the `finally` skips the receipt entirely. The comment at 1379 ("never
escape the finally") is true only for `Exception`.

## 3. Observed escape behaviour on this host (frozen tool, /tmp scratch)

Method: frozen tool loaded by `importlib` from a scratch tree containing the real
`registry/endpoint-consumers.tsv`; real `llama-server` b11755 + fixture
`stories260K.gguf`; loopback ephemeral port; one method monkeypatched per run.
No lane files touched; no process left (`pgrep -af llama-server` → none,
`ss -ltnp` → no listener; child is also covered by `PR_SET_PDEATHSIG`).

| injected fault | exit | receipt written | observed traceback site |
|---|---|---|---|
| `RuntimeError` in `teardown` (today's K6 shape) | **2** | yes, `internal_fault=internal:RuntimeError` | caught at 1268 |
| **`KeyboardInterrupt` in `teardown`** | **130** | **no** | `main` line 1267 |
| **`KeyboardInterrupt` during setup** (`sha256_file`, line 1017) | **130** | **no** | before handlers installed (1113-1115) |
| **`SystemExit(9)` in body** (`readiness_loop`) | **9** | **no** | past 1247 |
| argparse `--help` | 0 | no (correct) | `SystemExit(0)` at 995 |
| argparse usage error | 2 | no (correct) | `SystemExit(2)` at 995 |
| gate `check-receipt.py`: `KeyboardInterrupt` in `json.load` (line 1382) | **130** | n/a | escapes `except (OSError, ValueError)` at 1383 |

Micro-reproduction on 3.14.8: `raise KeyboardInterrupt` uncaught → exit **130**;
`except BaseException` catches KI and `SystemExit(7)`; catching then `sys.exit(2)`
yields 2 while still allowing the receipt write.

Python 3.14.8 exits 130 for an uncaught KeyboardInterrupt — outside the tool's
declared {0,1,2} and the gate's {0,1,2,3}. That is the exact contract breach R4's
"internal fault incl. BaseException" clause names.

## 4. Phase map — what escapes a KeyboardInterrupt, and why

Phases of `main` (line 994):

1. **Parse** (995). `argparse` raises `SystemExit(0|2)`: exits 0 / 2 receiptless.
   This is correct behaviour and must stay so.
2. **Pre-handler setup** (1002-1115): executable/model/probe checks return 2
   (1002-1015), model sha 1017, setup block 1025-1040, receipt assembly 1049-1103,
   handler install 1113-1115. **No KI handler exists here**; SIGINT still has its
   default disposition, so Ctrl-C during hashing/port-pick/registry read escapes
   with exit 130 and no receipt. Window is short but real (observed, row 3 above).
3. **Body** (1117-1248). Ctrl-C is converted by `_term_handler` (1110-1111) into
   `Terminated`, caught at 1244 → exit 2. A *programmatic* KI or a `SystemExit`
   raised by an injected/renamed helper is not caught by 1241/1244/1247 and escapes
   (observed exit 9 for `SystemExit(9)`), skipping emit.
4. **Finally** (1250-1386). The first action is to set SIGINT/SIGTERM/SIGHUP to
   SIG_IGN (1257-1259), so a second Ctrl-C cannot corrupt shutdown — good. But the
   guards at 1260/1268/1281/1300/1307/1367/1379 are `except Exception`, so a KI
   raised inside `teardown` (or a monkeypatched teardown, which is precisely the
   K6 control shape) aborts the whole rest of the `finally`: **the backstop kill at
   1286 never runs** and only `PR_SET_PDEATHSIG` reaps the child. No receipt.
5. **Emit** (1389-1412). Signals are ignored, so Ctrl-C is safe; a programmatic
   BaseException inside `_emit`/`json.dumps` would escape 1410 (exit 130, no
   receipt).

`SystemExit` additionally escapes from any place in 3-5 where a helper calls
`sys.exit()` or raises it; the contract classifies that as an internal fault → exit 2
with a receipt.

## 5. Consequences for C1 (actionable)

- **Exit arithmetic is already wrong for null checks.** `_check` (830-832) does
  `bool(passed)`, collapsing `None` to `False`; there is no `evaluated` field
  (`grep -c evaluated` → 0). Exit is computed twice as all-true-else-1:
  1240 `exit_code = 0 if all(c['passed'] ...) else 1` and 1376-1377
  `0 if all(... is True ...) else 1`. Null therefore lands on 1, never 2 (R4).
  A v3 fix needs `_check` to preserve `None`, plus a three-way result:
  any `False` → 1; else any null/unevaluated → 2; else 0.
- **Catch set.** Replacing `Exception` with `BaseException` at 1247 and at the
  shutdown guards (1268, 1281, 1300, 1307, 1379, and at least 1410) is the minimum
  to satisfy "internal fault incl. BaseException → exit 2". Keep `SetupError` and
  `Terminated` handlers ahead of it (1241, 1244).
- **Do not widen the catch over `parse_args` (995).** `except BaseException` there
  would turn `--help` (`SystemExit(0)`) into exit 2 and a bogus receipt — verified
  that `SystemExit` is caught by `BaseException`. Scope the catch below 995.
- **Emit ordering.** Because emit is outside the `try`/`finally`, a BaseException
  escaping the `finally` skips it. Either move the emit to the tail of the
  `finally`, or wrap the whole body in `except BaseException` that records
  `internal:<Type>`, sets exit 2, and falls through to the existing emit block.
- **Bound the catch.** Per the docs' warning (inconsistent state), after catching KI
  do only bounded work: no unbounded waits, one receipt write, exit. `teardown`
  already uses timeouts; keep it that way.
- **K6 / controls.** The K6 wrapper at `tests_llamacpp-live_controls.py:284`
  (`except BaseException:`) maps an escape to rc 4, so a KI-in-teardown control
  fails until the tool itself returns exactly 2. Tightening K6 to "exit exactly 2"
  is satisfied by the tool-side fix, not by the wrapper.
- **Gate.** `tests_llamacpp-live_check-receipt.py:1383` catches only
  `(OSError, ValueError)`; a KI during a read exits 130, not the documented
  "unreadable" 2 [INFERENCE that 2 is the intended mapping — the contract lists 2
  as unreadable and 3 as not-evaluated, and 130 fits neither].
- **GeneratorExit**: no generator is live across the try body, so it is not an
  operationally reachable path [INFERENCE from mechanism]; no special handling
  needed beyond the BaseException catch.

## 6. Limitations

- Live runs used the frozen tool with one symbol monkeypatched per run; they
  exercise the real handler/emit structure but the injection point is synthetic
  (the same technique K6 already uses).
- Signal-delivered Ctrl-C in the body was not exercised end-to-end; that path is
  grounded in the handler at 1110-1111 plus the `except Terminated` at 1244.
- The exit-130 mapping for uncaught KI is observed on this host only (3.14.8); the
  exceptions page documents the hierarchy, not the shell status.
- `SystemExit(9)` was injected via `readiness_loop`; no in-tree call raises
  `SystemExit` in the body, so that row proves the class gap, not a known trigger.

## 7. Installs

None. No tooling was installed or upgraded; scratch tree
`/tmp/kama-r18-ScoutPyBaseException-2` removed after the runs, no processes or
listeners left behind.
