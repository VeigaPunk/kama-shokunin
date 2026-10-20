VERDICT: confirm — at 704366d76 the first SIGINT/SIGTERM sets a sticky flag and runs a shutdown handler that unblocks the inference loop; the main thread then closes the listener, joins and returns **0**; any later SIGINT/SIGTERM prints a marker and calls **exit(1)**.

# ScoutLlamaSignalShutdown — b11755 SIGINT/SIGTERM registration, first/second signal, exit status

Question: how does llama.cpp 704366d76 handle SIGINT/SIGTERM (registration, first signal, second signal, exit status), for C2's `teardown_graceful` predicate.

Source read: `tools/server/server.cpp`, `tools/server/main.cpp`, `tools/server/server-queue.cpp`,
`tools/server/server-http.cpp`, `vendor/cpp-httplib/httplib.cpp` at commit
704366d76f8748cf9ad3df62a464bfcc8d1ae6ad (release b11755), fetched raw from GitHub and
hashed locally. `server.cpp` sha256 `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4`
equals the digest already pinned in SOURCES row S037; `server-http.cpp`
`24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb` equals S036's. The
installed binary reports `version: 0.7.0-dev (build 11755, commit 704366d76)`, and its
implementation library `~/.local/opt/llama-b11755/libllama-server-impl.so`
(sha256 `e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed`) contains the three
literals cited below — so this reading describes the installed subject, not a neighbouring build.

## 1. Answers

### Registration — one `sigaction` pair, only when `argv` is non-null

- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp#L526-L534
  — "register signal handler if not running by CLI"; "sigaction(SIGINT, &sigint_action, NULL); sigaction(SIGTERM, &sigint_action, NULL);"
- Registration is conditional on `!is_run_by_cli`, where `is_run_by_cli = (argv == nullptr)`
  (`server.cpp#L133` — "bool is_run_by_cli = (argv == nullptr);"). `tools/server/main.cpp` passes
  real `argv`, so the `llama-server` binary **does** install the handlers
  (https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/main.cpp#L3-L5 —
  "return llama_server(argc, argv);"). [INFERENCE] Anything embedding the server in-process with
  `argv == nullptr` keeps the default dispositions, so SIGTERM there is an uncaught signal.
- `sa_flags = 0` and an empty `sa_mask` (`server.cpp#L529-L532`): no `SA_RESTART`, no signals
  blocked during the handler. SIGPIPE is ignored separately at startup
  (`server.cpp#L101` — "Ignore SIGPIPE so the server does not crash if a child (MCP server, tools runtime) exits while we are writing to its stdin").
- **Ordering matters:** the `sigaction` calls sit *after* both branch bodies, i.e. after
  `ctx_http.start()` and after `load_model`/`load_startup_models` (`server.cpp#L507-L526`), and
  after `ctx_http.is_ready.store(true)` (`#L515`). A SIGTERM during model load therefore reaches
  no handler — it terminates by default action (negative returncode, no `clean_up`). [Observed
  from control flow, not run.]

### First signal — sticky flag + shutdown handler, then a normal `return 0`

- `server.cpp#L26-L30` — "static std::atomic_flag is_terminating = ATOMIC_FLAG_INIT;" and
  `if (is_terminating.test_and_set()) {`. The flag is process-lifetime sticky and is **never
  cleared**; `test_and_set()` returns false exactly once per process.
- `server.cpp#L37` — "shutdown_handler(signal);" — the handler runs on whatever thread took the
  signal.
- Single-model mode (the lane's mode) `server.cpp#L519-L523`:
  "mcp_mgr.shutdown();" … "this will unblock start_loop()" … "ctx_server.terminate();".
  The handler lambda takes `(int)` and **ignores the signal number**, so SIGINT and SIGTERM are
  indistinguishable downstream.
- `server_context::terminate()` is `impl->queue_tasks.terminate()`
  (https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L4797-L4799),
  which sets `running = false; condition_tasks.notify_all();`
  (https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-queue.cpp#L132-L136).
  `start_loop` then breaks and calls `worker_stop()` (`server-queue.cpp#L278` onward).
- The main thread continues at `server.cpp#L575-L590`: "this call blocks the main thread until queue_tasks.terminate() is called";
  then `clean_up()` (which logs "cleaning up before exit..." at `#L484`, then
  `ctx_http.stop(); ctx_server.terminate(); mcp_mgr.shutdown(); llama_backend_free();` at
  `#L487-L490`), then `ctx_http.join()` (`#L579`) and finally `return 0;` (`#L590`).
- Router mode differs only in the handler body: `ctx_http.stop()` is called directly
  (`server.cpp#L462-L468`), which ends `ctx_http.join()`; the same `clean_up()`/`return 0` tail runs.

### Second signal — immediate `exit(1)`, deliberately

- `server.cpp#L30-L34` — "in case it hangs, we can force terminate the server by hitting Ctrl+C twice";
  "Received second interrupt, terminating immediately."; `exit(1);`.
- Because the flag is sticky, *any* later SIGINT/SIGTERM — not just a rapid double tap, and
  regardless of which signal arrived first — takes the `exit(1)` branch.
- [INFERENCE] `exit()` is not async-signal-safe (POSIX), and the first-signal path itself calls
  non-async-signal-safe code (`std::function`, mutexes in `mcp_mgr.shutdown()` and
  `server_queue::terminate()`). The authors' "in case it hangs" comment is the acknowledgement of
  that hazard; a hang, not a clean teardown, is the reason the escape hatch exists.

### Exit status after a graceful shutdown — exactly `0`

- `server.cpp#L590` — "return 0;", returned through `llama_server(...)` (`server.cpp#L122-L124`)
  to `main` (`main.cpp#L3-L5`). No path from the signal handler returns another value:
  graceful shutdown ⇒ `0`; second signal ⇒ `exit(1)` ⇒ `1`; bind/model-load/connect failure ⇒
  `return 1` (`server.cpp#L457`, `#L496`, `#L510`, `#L550`); uncaught exception in `clean_up`
  (e.g. from `mcp_mgr.shutdown()`) escapes `main` ⇒ `std::terminate` ⇒ abort, i.e. negative
  returncode. [INFERENCE for the exception branch; no catch exists between `main` and the
  `llama_server` call.]
- Python's sign convention is what makes `returncode == 0` (not `is not None`) the right
  predicate: "A negative value -N indicates that the child was terminated by signal N (POSIX only)."
  (https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode).
- Round-16 own-work receipt agrees with the source: `.ufo/waves/round-16/live/receipt.json` teardown
  = `{"returncode": 0, "sigterm_sent": true, "sigkill_sent": false, "term_wait_ms": 3}`.

### The listening socket closes on this path, but that fact cannot grade the path

- `server_http_context::stop()` calls `srv->stop()`
  (https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.cpp#L548-L554),
  and cpp-httplib 0.62.0 (`vendor/cpp-httplib/httplib.h#L11` — `CPPHTTPLIB_VERSION "0.62.0"`)
  implements it as "Release the listening socket whether or not the accept loop is running …
  close_socket(sock);"
  (https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/vendor/cpp-httplib/httplib.cpp#L9067-L9075).
- Crucially the harness observes `port_refuses` **after** `proc.wait()` returned, and the kernel
  closes every fd at process death anyway — so *any* exit, including SIGKILL, yields
  `port_refuses true`. Port refusal is downstream of both exits and discriminates neither.

### Companion datum (not this axis): the ready body has one construction site

- `GET /health` builds its payload from `res->ok({{"status", "ok"}})` (`server-context.cpp#L5288-L5298`)
  and `ok()` sets `status = 200; data = safe_json_to_str(response_data);`
  (`server-context.cpp#L4868-L4871`); the loading-window 503 envelope is emitted earlier by
  middleware (`server-http.cpp#L307-L328`, already S036). Exact-byte grading of the ready body is
  the ProbeHealthBody seat's axis; this seat only records that the ready payload is a single
  literal, so it has no drift surface. [INFERENCE on serialized whitespace: `safe_json_to_str`
  calls `json::dump_safe`, which is not defined in the vendored `vendor/nlohmann/json.hpp` at this
  commit, so the exact dump call site was not inspected here.]

## 2. Sequence in single-model mode (the lane's mode)

| step | where | effect |
|---|---|---|
| listen + `is_ready` true | `server.cpp#L494-L515` | `/health` answers; handler not yet installed |
| install SIGINT/SIGTERM | `server.cpp#L526-L541` | from here on signals are graceful |
| first signal | `#L29-L37`, `#L519-L523` | sticky flag, `queue_tasks.terminate()` |
| loop unblocks | `server-queue.cpp#L132-L144` | `running=false` ⇒ `process_new_tasks` returns true |
| clean up | `server.cpp#L483-L491`, `#L578` | `ctx_http.stop()` closes listener, backend free |
| join | `server.cpp#L579` | listener threads + worker pool shut down |
| return | `server.cpp#L590` | exit status `0` |
| second signal at any later point | `#L30-L35` | marker on stderr, `exit(1)` |

## 3. Derived C2 predicate (`teardown_graceful`, receipt `kama-llamacpp-live/v2`)

Pass iff **all** of the following, each with its citation:

1. `captures.health.status == 200` was observed before teardown — `is_ready.store(true)`
   (`server.cpp#L515`) precedes handler installation (`#L526`), so any window in which `/health`
   is not yet 200 is also a window with no handler: a pre-ready SIGTERM legitimately dies by
   default action. [INFERENCE] The converse gap (`/health` already 200, handler not yet installed)
   is a few instructions wide and cannot be hit by a teardown that follows two completed probes.
   On `setup_error`/ready-timeout paths, emit no `teardown_graceful` row (or a separate,
   differently-worded one) instead of failing it.
2. `teardown.sigterm_sent is True` — the child handler ignores the signal number
   (`server.cpp#L519`), so the harness's own record is the only attribution evidence.
3. `teardown.sigkill_sent is False` — a SIGKILL exit is `returncode -9` and can never be graceful.
4. `teardown.returncode == 0` — citation `server.cpp#L590` + `main.cpp#L3-L5`; explicitly **not**
   `is not None` (v1's defect: `tools/kama-llamacpp-live.py:1026`).
5. `teardown.term_wait_ms` is an int and `< TERM_GRACE * 1000` — a hung shutdown is what the
   second-signal escape exists for (`server.cpp#L31-L34`).
6. `receipt.port_listener_ownership == 'child'` — already recorded at post-probes
   (`tools/kama-llamacpp-live.py:976-977`), i.e. the child owned the LISTEN socket immediately
   before the signal; this is the ownership proof v1 has but `teardown_port_closed` never reads
   (`:1030-1032`).
7. Optional discriminator: no `Received second interrupt, terminating immediately.` in
   `teardown.log_lines` (`server.cpp#L33`).

And keep `teardown_port_closed` as `port_refuses is True **and** port_listener_ownership == 'child'`,
never as graceful evidence (see §1, last bullet).

**Blocker for clause 7 as written today:** `LOG_KEEP` is
`re.compile(r'build|model loaded|listening|loading', re.IGNORECASE)`
(`tools/kama-llamacpp-live.py:66`) and non-matching lines are dropped at `:705`. Both useful
markers are therefore absent from the receipt: `Received second interrupt…` and
`operator(): cleaning up before exit...` (located on the child's stderr, quoted in
`.ufo/waves/round-17/build/drafts/probe-sigterm-exit.md`). [INFERENCE] v2 should widen the keep
regex (e.g. `interrupt|cleaning up`) if it wants either marker; `listening on %s`
(`server.cpp#L543-L544`) is already kept and already appears in the round-16 receipt.

## 4. Correction to peer advice: case (d) does not test a second signal

`ProbeSigtermExit.md` item 4 states "A second SIGTERM during shutdown is absorbed harmlessly
(rc 0, ~10 ms)". That is not supported, and the code says the opposite (§1). Its own draft
(`build/drafts/probe-sigterm-exit.md:24`) reports case (d) as `exit_ms` `10.1, 10.1, 10.1, 10.1, 10.1`
with the 10 ms gap, while single-signal runs exit in `3.1-3.2 ms`; and all 25 runs produced no
`interrupt` text. Reading: the process was already dead when the second signal was sent (ESRCH on
the second `kill`), and the flat 10.1 ms is the deliberate 10 ms sleep dominating the measurement,
not shutdown latency. [INFERENCE, high confidence: the zero-variance 10.1 ms plus the absent
stderr marker — `fprintf` precedes `exit(1)` at `server.cpp#L33-L34`, so a live second delivery
would have printed it.] Consequence: do **not** relax `teardown_graceful` on the strength of
case (d); a second signal is `exit(1)`, and clause 7 is a real discriminator.

## 5. Candidate SOURCES row (for L1/Scribe to append — not written here)

Next free id is S042 (S041 is the current last row). Append only; the contract permits later edits
to `status`/`recheck`/`used-by` only.

```
| S042 | llama.cpp SIGINT/SIGTERM shutdown path @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp | code | A | how a b11755 llama-server process handles SIGINT/SIGTERM and what exit status a graceful shutdown returns, at commit 704366d76 only; not other builds, not Windows console events | server.cpp 26-38 (sticky flag, handler, second-signal `exit(1)`), 133 (`is_run_by_cli = (argv == nullptr)`), 519-523 (single-model shutdown handler; signal number ignored), 526-541 (`sigaction` SIGINT/SIGTERM, `sa_flags = 0`), 543-545 (`listening on` log), 575-590 (`start_loop` → `clean_up` → `join` → `return 0`); tools/server/main.cpp 3-5; tools/server/server-context.cpp 4797-4799; tools/server/server-queue.cpp 132-136; tools/server/server-http.cpp 548-554; vendor/cpp-httplib/httplib.cpp 9067-9077; raw sha256 server.cpp 2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4, main.cpp 7ec684588e04538c5f9d44cda54e67780cf68b19c3c2660699df632f5c55fe4c, server-context.cpp dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329, server-queue.cpp 168385b752fa70df9790f51179e34e375284a296cd44af92b41c5d25da32a2ba, server-http.cpp 24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb, httplib.cpp 516c58994baa9bcc3b5616f453710c0b4d2d341ac473f788fcfb029f8548caa5 | The first SIGINT/SIGTERM (registered only when argv is non-null, i.e. the llama-server binary) sets a sticky flag and unblocks the inference loop, after which the main thread closes the listener, joins and returns 0; every later SIGINT/SIGTERM prints `Received second interrupt, terminating immediately.` and calls `exit(1)`, and no handler is installed until after model load. | mined | 2026-10-20 | on-release | corpus/knowledge/llamacpp-loading-lifecycle.md |
```

Cross-check value: the `server.cpp` and `server-http.cpp` digests above are the ones already
recorded in S037 and S036, so this row cannot silently drift from the previously mined bytes.

## Limitations

- Source-only for the runtime claims: no server was started from this seat (read-only, no ports).
  `returncode 0` and `exit(1)` are derived from code and corroborated by the round-16 receipt
  (`returncode 0`, `sigterm_sent true`, `sigkill_sent false`, `term_wait_ms 3`); the only local
  executions were `llama-server --version` (no bind) and `sha256sum`/`grep -a` over the installed
  files.
- The "SIGTERM during load ⇒ negative returncode" statement is read from the registration order
  (`server.cpp#L507-L526`); the peer's case (c) could not stage a true loading window either.
- Windows `CTRL_C_EVENT` handling (`server.cpp#L535-L540`) was not analysed; irrelevant to this host.
- Recovery/`is_terminating` reset: none exists; every post-first signal is fatal, per `#L30`.

## Installs

None. Python 3 stdlib, GNU coreutils and `curl` only; pacman pause untouched.

## Files written

- `.ufo/waves/round-17/build/advice/ScoutLlamaSignalShutdown.md` (this report)
