# Draft: append to corpus/knowledge/llamacpp-loading-lifecycle.md

Owner: ScribeKnowledgeTeardown (round 17, BUILD). Draft only; L1 integrates.
Provisional sources (L1 assigns final ids and registry rows): S042, S043, S044.
Access date for every source below: 2026-10-20.

## Ready body and graceful teardown (round 17)

Scope: llama.cpp b11755 = commit 704366d76, single-model mode, x86-64 Linux CPU build,
`-t 1 -c 256`, fixture `stories260K.gguf` (sha256 270cba1b…d256bd, S039). One lane-owned
run at 2026-10-20T14:06:27Z (round-16 receipt). It is not evidence about any registered
consumer, router mode, sleep, GPU, or any other build.

### Exact ready body

- Source: `get_health` returns `res->ok({{"status", "ok"}});` (S043,
  `tools/server/server-context.cpp:5288-5299`, the call at 5297). `ok()` stores
  `safe_json_to_str(response_data)` (S043, `tools/server/server-context.cpp:4868-4870`).
- Observed on the lane run: HTTP 200, `Content-Type: application/json; charset=utf-8`,
  `Content-Length: 15`, body `{"status":"ok"}` (15 bytes, sha256
  `a29ee2b15c494311c52521766e44af56a3ad2248e7a8ab465e5206463c13d288`), recorded at
  `.ufo/waves/round-16/live/receipt.json:21-33`. The digest was recomputed over those 15
  bytes this round and matches.
- The README's `{"status": "ok" }` (S035, `tools/server/README.md:489`) has spaces and a
  trailing space. It is documentation, not the byte body. A check should compare the parsed
  JSON object to exactly `{"status": "ok"}`, with no extra keys, not the raw bytes.
- A 200 answer is reachable only after the readiness gate opens. The gate answers
  `/health` with the 503 loading body while `is_ready` is false (S036,
  `tools/server/server-http.cpp:307-328`, applied to every path by 354). So a 200
  `{"status":"ok"}` means `is_ready` was set true (S037, `tools/server/server.cpp:515`).
- A 200 with any other body (for example `{"status":"degraded"}`) is not the ready body and
  is not documented by the README. The code emits only the `ok` form on this route.

### SIGTERM handling and graceful exit status

- Handler install: `sigaction(SIGTERM, &sigint_action, NULL);` at
  `tools/server/server.cpp:534` (S042), in the block at 527-534 that runs only after
  `if (!ctx_server.load_model(params))` at 507 and `ctx_http.is_ready.store(true);` at 515.
  Across the pinned `tools/server`, `common`, `src` and `ggml` trees the only SIGTERM
  reference is line 534; `signal(SIGPIPE, SIG_IGN)` at 101 is the only other disposition
  set in that file.
- First signal: `signal_handler` (S042, `tools/server/server.cpp:29-37`) calls
  `shutdown_handler`. Second signal: it prints "Received second interrupt, terminating
  immediately." and calls `exit(1)` (`server.cpp:30-34`).
- Single-model shutdown (`server.cpp:519-523`): `mcp_mgr.shutdown();` then
  `ctx_server.terminate();`. `terminate()` sets `running = false` (S043,
  `tools/server/server-queue.cpp:132-136`), and the loop breaks on that
  (`server-queue.cpp:299-302`, "break; // terminate"). The main thread then runs `clean_up()`
  (`server.cpp:578`), joins the HTTP thread (579), and returns 0 (`server.cpp:590`).
- Entry point: `int main(...) { return llama_server(argc, argv); }`
  (`tools/server/main.cpp`, S042 tarball copy).
- Graceful exit status at this commit: **0**, code-derived. The §GET `/health` section of
  the README documents no exit status (S035, lines 479-490). No other exit-code
  documentation was opened this round. A model-load failure returns 1
  (`server.cpp:507-512`); a second interrupt exits 1.
- Lane observation (`receipt.json:403-417`): `returncode 0`, `sigterm_sent true`,
  `sigkill_sent false`, `term_wait_ms 3`, `port_refuses true`. The harness sends
  `os.killpg(proc.pid, signal.SIGTERM)` (`tools/kama-llamacpp-live.py:666`) to a child started
  with `start_new_session=True` (line 904), as an argv list (no shell; line 909), and
  SIGKILLs only after `TERM_GRACE` (10 s).

### What a negative Popen returncode means

- Python documents: "A negative value `-N` indicates that the child was terminated by
  signal `N` (POSIX only)." (S044, `subprocess.html` section `Popen.returncode`). With
  `shell=True` the value is the shell's status and may map to 128+N instead; the harness
  does not use a shell.
- So, for this harness: `0` means `llama_server` returned 0 (the graceful path above, or a
  self-exit); `-15` means the process died to SIGTERM with the default disposition (no
  llama.cpp handler installed); `-9` means it was SIGKILLed; `1` means a load failure or a
  second interrupt.
- Consequence for the teardown check: `returncode 0` plus `sigterm_sent true` does not prove
  the signal caused the exit. The proof would be the handler's own log line
  `cleaning up before exit...` (`server.cpp:484`). That line is absent from the three
  kept lines in `receipt.json:403-411`, but the harness's log-reduction rule was not opened
  this round, so its absence is not yet explained.

### Limits

- One build (b11755 = 704366d76, S038), one CPU, one fixture model, one sampled run. The
  receipt is dated; the recheck is on release.
- Not run: SIGTERM delivered during model load. By code order (`server.cpp:507` before the
  handler at 534), a SIGTERM then should take the default action and give `returncode -15`
  [INFERENCE from code order; not run]. The lane run tears down only after its ready phase
  (the probe order is described in the corpus entry, lines 142-143; the harness flow was not
  re-read this round), so this path was not exercised.
- Not verified: router mode. Its handler is also installed after `load_startup_models()`
  (`server.cpp:472` before 527) [INFERENCE from code order; not run].
- Not verified: that the installed `~/.local/opt/llama-b11755/llama-server` launcher is built
  from this `tools/server/main.cpp` and forwards signals identically (the receipt shows
  only the argv path).
- Not consumer health: registered endpoints 8080 and 34113 were never contacted; the run
  shows that this fixture server, on an unregistered port, became ready and tore down.

## Sources (provisional)

- S042 — llama.cpp `tools/server/server.cpp` and `tools/server/main.cpp` @ 704366d76.
  URL https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp
  (local `.ufo/waves/round-16/sources/llama.cpp-704366d/server.cpp`, sha256
  2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4). Quote: "sigaction(SIGTERM, &sigint_action, NULL);" (server.cpp:534).
- S043 — llama.cpp `tools/server/server-context.cpp`, `server-queue.cpp` @ 704366d76.
  URL https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp
  (sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329). `server-queue.cpp` was
  taken from the codeload tarball (sha256 c2d31d5f462e899b580327d242c4fa6e61b704bcbd9dbcf6d4e7698ba3700749), not the pinned directory.
  Quote: "res->ok({{\"status\", \"ok\"}});" (server-context.cpp:5297).
- S044 — Python `subprocess` documentation, §`Popen.returncode`.
  URL https://docs.python.org/3/library/subprocess.html (fetched 2026-10-20; copy sha256
  f6d48eb534364a97de5767657917a6f35621651e9b9d88ba471807939bda9b08). Quote: "A negative value -N indicates that the child was terminated by signal N (POSIX only)."
  The served page is the 3.15 development build of the docs.
- Existing rows reused: S035 (README §GET `/health`, lines 479-490), S036 (`server-http.cpp:307-328`),
  S037 (`server.cpp:493-515`), S038 (release b11755 asset digest), S039 (fixture digest), S041 (round-16 receipt).
