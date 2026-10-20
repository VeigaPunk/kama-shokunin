VERDICT: confirm — both required sentences exist verbatim (3.12–3.15) and the local stdlib shows the exact hang path round-16 M3 hit.

# Scout: `BaseServer.shutdown()` and `subprocess.run(timeout=)`

Question: cite the exact doc sentences grounding round-16 M3 (harness hang). Read-only; no lane command, port, or measurement run.

## Q1 — `BaseServer.shutdown()` deadlock sentence

- URL: `https://docs.python.org/3.14/library/socketserver.html#socketserver.BaseServer.shutdown` (3.14 stable = local runtime; identical wording at `/3/` = 3.15.0 dev, and at 3.12/3.13).
- Quote (16 words): "shutdown() must be called while serve_forever() is running in a different thread otherwise it will deadlock."
- Preceding sentence (11 words): "Tell the serve_forever() loop to stop and wait until it does."

Mechanism, observed in local CPython 3.14.8 (`/usr/lib/python3.14/socketserver.py`):
- `serve_forever` sets `self.__is_shut_down` only in its `finally` (`:245`), i.e. the event is signalled when the loop actually exits.
- `shutdown()` sets `self.__shutdown_request = True` (`:254`) then calls `self.__is_shut_down.wait()` (`:255`) with no timeout.
- If `serve_forever` never started, no code path ever calls `.set()`, so `wait()` blocks forever. The doc sentence is the normative statement; the source is the mechanism.

## Q2 — `subprocess.run(timeout=)` kill-on-timeout sentence

- URL: `https://docs.python.org/3.14/library/subprocess.html#subprocess.run`
- Quote (13 words): "If the timeout expires, the child process will be killed and waited for."
- Follow-on (19 words): "you are not guaranteed to see a timeout exception until at least after however long process creation takes."

Mechanism, local stdlib (`/usr/lib/python3.14/subprocess.py`): on `TimeoutExpired`, `run()` calls `process.kill()` (`:559`) then, on the non-Windows branch, `process.wait()` (`:570`) before re-raising.

## Adjacent sentences from the same two pages (useful to C1/C2)

- `#subprocess.Popen.wait` (21 words): "This will deadlock when using stdout=PIPE or stderr=PIPE and the child process generates enough output to a pipe" — a second hang route for any harness that pipes a server's output and calls `wait()` without draining.
- `#subprocess.Popen.returncode` (15 words): "A negative value -N indicates that the child was terminated by signal N (POSIX only)." Directly relevant to C2's `teardown_exited`: a non-`None` returncode proves only that termination was detected (`polls`/`wait`/`communicate`), not that the harness caused it.
- `#subprocess.Popen.terminate` (11 words): "On POSIX OSs the method sends SIGTERM to the child."
- `#subprocess.Popen.kill` (10 words): "On POSIX OSs the function sends SIGKILL to the child."

## Tie to round-16 M3

- `tests/probe-verdicts/check.py:309-315` builds `ThreadingHTTPServer` and starts `threading.Thread(target=server.serve_forever, daemon=True)`; the in-code comment at `:312-313` already restates the doc rule ("without it the socket listens but never accepts and shutdown() below would block forever").
- `tests/probe-verdicts/check.py:354` calls `server.shutdown()` in `finally`, which is exactly the un-timed `__is_shut_down.wait()` path.
- `.ufo/waves/round-16/falsify/advice/CriticMistakesFailCapable.md:43` replaced that `.start()` with `pass`: `--only` run under `timeout 40` → "exit 124 after 40 003 ms, no output". That is the doc-predicted deadlock reproduced, and it shows the zero-request guard cannot catch it because the block is in `finally`.
- `corpus/lessons/round-16.md:173-176` records the correction: "a stub without serve_forever still hangs on shutdown()"; actual backstops are the 30 s per-probe and 600 s per-run timeouts, so M3 stays open.

## Implications for the C1 repair [INFERENCE]

- Guarding request count before `shutdown()` does not remove the hang: the block is the `shutdown()` call itself. A fail-capable harness needs `serve_forever` proven started before any `shutdown()` (or must avoid `shutdown()` when the thread is not live), plus an outer per-probe timeout that converts a hang into a recorded per-row failure rather than a killed run.

## Implication for C2 [INFERENCE]

- `run(timeout=)` is a legitimate backstop against a hung child (it SIGKILLs), but by construction it cannot evidence graceful SIGTERM handling; a v2 receipt must record which path ran (`terminate()` vs `kill()`) rather than infer politeness from a present returncode.

## Limitations

- Doc text verified on 2026-10-20 by fetch; identical wording confirmed in 3.12, 3.13, 3.14 and 3.15 (docs.python.org/3/ currently serves 3.15.0 dev). Local runtime is Python 3.14.8, so 3.14 URLs are cited as primary.
- No hang was re-run in this seat (read-only; measurement belongs to L1). The 40 003 ms observation is quoted from round-16 advice, not reproduced here.
- Whether `daemon=True` changes the deadlock: it does not set the event, so it only affects interpreter-exit joining, not `shutdown()` blocking — [INFERENCE] from `socketserver.py:225,245,254-255`.
- C2's llama.cpp `/health` and signal-path sources are out of scope for this seat.

Installs/upgrades: none. Ports bound: none. Files written: this report only.
