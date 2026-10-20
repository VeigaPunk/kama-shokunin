VERDICT: partial — the code supports the ready body and exit 0 only under stated preconditions; "documented", a bare `return 0` cite and "harness-initiated" overclaim

Seat: KamaR17.CriticSourcedClaim-2 (read-only critic). Source copies read: the round-16 pinned tree `.ufo/waves/round-16/sources/llama.cpp-704366d/` (sha256s in `.ufo/waves/round-16/sources/pins.json`). `tools/server/main.cpp` at 704366d76 was fetched to /tmp (sha256 `7ec68458…fe4c`, 5 lines) and the copy deleted afterwards. Python docs were read live at `/3/` (which renders "Python 3.15.0 documentation") and `/3.14/` (3.14.8, the host's `python3 --version`). `round-17/sources/` is still empty, so this report attacks the planned rows, not any committed rows.

## Axes
- calibration: does each cited line support exactly the predicate it is attached to?
- operability: does the predicate fail on the misbehaviour without failing a correct llama-server?

## Claim A — "ready body exactly {"status":"ok"}": SUPPORTED, but only as an identity check, and only if it compares JSON

1. The handler can emit only one 200 body. `server-context.cpp:5297` reads `res->ok({{"status", "ok"}});`. Before that, 5288-5290 are `this->get_health = …` and `// error and loading states are handled by middleware`. The only other `/health` answer is the middleware's 503 (`server-http.cpp:307-326`, the S036 row).
   - Consequence [INFERENCE]: a real b11755 server cannot produce `{"status":"degraded"}`. So the exact-body check can only fail when the listener is not this llama-server (a fake, a different build, or a foreign listener). That makes it fail-capable against impostors and controls, which is legitimate. The row must not say it detects llama.cpp unhealthiness, because llama.cpp has no such 200 state.
2. The README bytes differ from the wire bytes. `README.md:489` shows ``Body: `{"status": "ok" }` `` (extra spaces). The wire form comes from `server-context.cpp:4870` `data = safe_json_to_str(response_data);` and then `server-common.cpp:1696` `return data.dump_safe();`. The round-16 receipt observed `{"status":"ok"}`.
   - Counterexample: a check or gate that byte-compares against the README text rejects a correct server.
   - The C2LiveTool spec's "JSON object equality" is the right form. The row should cite 5297 for the literal and README:479-490 only for the meaning ("model is successfully loaded").
3. A 200 does not mean the model is resident:
   - `server-context.cpp:5290` is `create_response(true)` (bypass_sleep), and 5292 says `// this endpoint can be accessed during sleeping`. With `--sleep-idle-seconds` set, `/health` answers 200 ok while the model is unloaded.
   - In router mode `server.cpp:460` sets `is_ready.store(true)` before any model loads (S037).
   - The row's scope must say "single-model mode, sleep disabled (`arg.cpp:3852` `-1 = disabled`)". The harness passes neither flag [INFERENCE: default not opened in `common.h`].
4. `/health` 200 does not prove the SIGTERM handler is installed. `server.cpp:515` `ctx_http.is_ready.store(true);` runs before `sigaction(SIGTERM, …)` at `server.cpp:534`. See B3.

## Claim B — "graceful SIGTERM exits 0": CODE-DERIVED under preconditions; NOT documented; line 590 alone overclaims

1. **"Documented" is false.** The C2LiveTool item text calls returncode 0 "llama-server's documented graceful exit". Grepping the pinned README for signal|terminat|shutdown|exit finds only `--help`/`--list-devices` "and exit", the tools-runtime "clean up on server exit" text, and router `stop-timeout` (lines 34, 79, 206, 1966). None of these is a SIGTERM exit status.
   - Smallest correction: write "code-derived exit status 0" everywhere (DOC strings, SOURCES `teaches`, SKILL rows). The sibling draft `build/drafts/knowledge-teardown.md:52` already says "code-derived".
2. **The exit status flows through more than one line.** The chain is:
   - `main.cpp:4` `return llama_server(argc, argv);`
   - `server.cpp:590` `return 0;`
   - which is reached only after `server.cpp:576` `ctx_server.start_loop();` returns
   - which happens when `queue_tasks.terminate()` is called (`server-context.cpp:4797-4798`).

   Citing line 590 proves only "every return of start_loop gives 0". The claim that rc 0 means a signal was handled needs the full list of terminate callers at this commit:
   - (a) `shutdown_handler` → `ctx_server.terminate()` (`server.cpp:519-523`), called from `signal_handler` (`server.cpp:29-38`) for SIGINT **or** SIGTERM (533-534).
   - (b) `llama_server_terminate()` (`server.cpp:47-51`). This is the CLI-only path (`is_run_by_cli = (argv == nullptr)`, server.cpp:133).
   - (c) the router child monitor: `server-models.cpp:2089-2091` "exit command received, exiting..." → `shutdown_handler(0);`. Reachable only when `LLAMA_SERVER_ROUTER_PORT` is set (`server-models.cpp:1987-1988`).

   The harness env allowlist (`tools/kama-llamacpp-live.py:73`, PATH/HOME/LANG/LC_ALL/TMPDIR) and the argv launch exclude (b) and (c). The row must name these preconditions, or rc 0 overclaims.
3. **The handler is registered late.** It is installed at `server.cpp:526-541`, after `load_model` at 507. A SIGTERM before line 534 takes the default action: Python reports `-15`, and the process does not exit 0.
   - The window includes the whole loading phase.
   - It also includes a short gap after `is_ready` (515), when `/health` already answers 200.
   - Consequence [INFERENCE]: in the real harness, probes run between ready and teardown, so the gap is not hit in practice. On setup-failure paths (ready-timeout, loading), `-15` is the correct, source-predicted behaviour, not a subject defect. `teardown_graceful` must be scoped to "SIGTERM after the `listening on` line".
   - Usable marker: `server.cpp:543-545` `SRV_INF("listening on %s\n", …)` is printed after the sigaction. The current `LOG_KEEP` regex (`kama-llamacpp-live.py:66`, `build|model loaded|listening|loading`) already keeps it, and the round-16 receipt has `llama_server: listening on http://127.0.0.1:37527`. Grade "listening line present before SIGTERM" as the precondition. A `model loaded` line (server.cpp:517) does not prove the handler is installed.
4. **Other exit paths the row must exclude:**
   - A second signal gives `server.cpp:34` `exit(1);` ("Received second interrupt, terminating immediately.").
   - `server.cpp:507-511` (load failure), 494-497 (HTTP start) and `server-http.cpp:824` (GCP route conflict, env-gated `AIP_*`, excluded by the allowlist) give 1.
   - Destructors and backend teardown after `return 0` are not covered by any source line. Exit 0 then rests on the round-16 observation only (`returncode 0, term_wait_ms 3`) [INFERENCE].
5. **"Harness-initiated" cannot be proven from any source.** Any SIGINT/SIGTERM from any sender takes path (a) and exits 0. Examples: a peer seat's `pkill llama-server` while ~15 sibling seats run llama-servers concurrently [INFERENCE], or an operator. The receipt's `sigterm_sent` records the harness's intent, not the cause of the exit. The draft `knowledge-teardown.md:72-74` says the same.

## Claim C — the Python returncode docs: they support "negative = signal death" and expose a live defect in the teardown guard

1. Supported: "A negative value `-N` indicates that the child was terminated by signal `N` (POSIX only)." (`subprocess.html#subprocess.Popen.returncode`, identical in 3.14 and 3.15). So `-9` means SIGKILL and `-15` means default-disposition SIGTERM.
2. Not supported: anything about exit 0. That is llama.cpp's behaviour (Claim B), so the docs row must not be cited for "graceful exits 0".
3. **Counterexample to the "alive at teardown" proof.** The docs say returncode is "set by a call to the poll(), wait(), or communicate() methods". They also say "A `None` value indicates that the process hadn't yet terminated at the time of the last method call." The guard reads that cached attribute:
   - `kama-llamacpp-live.py:663` `if proc.returncode is None:  # F5: killpg only while child is alive`, then 664 `out['sigterm_sent'] = True`.
   - Failure sequence: a child (or fake) self-exits with 0 after the last `proc.poll()` (`verify_live`, line 539), for example right after answering the final probe. Line 663 still sees `None`, records `sigterm_sent true`, and `os.killpg` hits a zombie's group without error. `wait()` then returns 0, so `teardown_graceful` passes on a self-exit.
   - Planned control K3 ("self-exit rc 0", `build/drafts/skill-round17.md:11`) catches this only if the fake exits **before** the last poll. A fake that exits on its final request survives.
   - Smallest correction: `alive_at_teardown_start = proc.poll() is None`, evaluated immediately before `killpg`. Set `sigterm_sent` only when it is true and `killpg` did not raise. Add a control whose fake exits 0 after its last answered request. A residual race between `poll()` and `killpg` remains and must be stated in the DOC string.
4. Version pin: the `/3/` URL now renders "Python 3.15.0 documentation", but the harness runs Python 3.14.8. Pin `https://docs.python.org/3.14/library/subprocess.html#subprocess.Popen.returncode`. The quoted text was checked identical in 3.14 and 3.15. The row must not attach to a moving `/3/` page.

## Impacted axes
- calibration: the B1 "documented" wording, the B2 single-line cite and the B5 "harness-initiated" claim each overclaim. C3 is a false-provenance path in the receipt itself.
- operability: without the B3 scope, `teardown_graceful` reports a subject failure for source-predicted `-15` deaths during setup failures. The C3 defect lets a self-exiting subject pass.

## Smallest safe corrections (for L1)
1. Health row: anchor `server-context.cpp:5288-5299` (literal at 5297), `server-common.cpp:1695-1696` (serialisation) and README:479-490 (meaning). Scope: single-model, sleep disabled. Predicate: JSON equality. Label: identity check against non-llama listeners.
2. Shutdown row: anchor `main.cpp:3-5`, `server.cpp:29-38, 519-523, 526-541, 575-590` and the terminate-caller list (`server.cpp:47-51`, `server-models.cpp:1986-1988, 2089-2097`). Teaches: "exit 0 is code-derived. It requires SIGINT/SIGTERM after line 534, argv launch and no `LLAMA_SERVER_ROUTER_PORT`. A second signal exits 1. Before registration the default action gives -15." Drop "documented".
3. Tool: precondition "listening line observed before SIGTERM". Use `poll()`-based `alive_at_teardown_start`. Keep a docs-cited `-N` interpretation.
4. Python row: the pinned 3.14 URL, quoting the two returncode sentences. Cite it only for `None` and negative values.

## Limitations
- This was static reading only. No llama-server or fake was started; `ss -ltnp` was not needed. The empirical exit codes are the ProbeSigtermExit seat's work.
- `dump_safe` was not opened, so the compact form rests on round-16 observation. The default of `sleep_idle_seconds` was read from `arg.cpp`'s help string, not from `common.h`.
- The GitHub raw fetch of `main.cpp` was not re-pinned into the lane. The SourcePinsTeardown seat should add `tools/server/main.cpp` to its pins.

## Installs
None.
