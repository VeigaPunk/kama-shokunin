VERDICT: confirm — llama.cpp 704366d sources pinned; `/health` ready body is exactly `{"status":"ok"}`, SIGTERM→graceful→`return 0`, second signal→`exit(1)`.

# Item
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/sources/pin.py` — read-only `urllib` GET of six server files at commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`, raw copies saved under `llama.cpp-704366d/tools/server/`, all 26 pins located by string search (anchor regex + brace/span expansion; zero hardcoded line numbers), written to `pins.json`. Script exits 2 if any pin misses; rerun cleanly after a locator fix, final run: 26/26 pinned, no `missing_pins`.

# Fetched files (url → sha256, bytes)
All under `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/`:

| file | sha256 | bytes |
|---|---|---|
| tools/server/server.cpp | `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4` | 24572 |
| tools/server/server-context.cpp | `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` | 264205 |
| tools/server/server-http.cpp | `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb` | 37318 |
| tools/server/README.md | `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37` | 119661 |
| tools/server/server-queue.cpp | `168385b752fa70df9790f51179e34e375284a296cd44af92b41c5d25da32a2ba` | 22141 |
| tools/server/server-queue.h | `d77a3eac479e8ad772b325db643225ea3e68a9715709e375d859295c31161924` | 9324 |

All six saved copies re-verified: sha256 and byte size match `pins.json`. server-queue.{cpp,h} added because the shutdown path's primitives (`server_queue::terminate`/`start_loop`) live there — the four named files only call them.

# Located pins (file:lines, verbatim ≤25w)

**Signal registration** — `server.cpp:529-534`:
```
sigint_action.sa_handler = signal_handler;
sigaction(SIGINT, &sigint_action, NULL);
sigaction(SIGTERM, &sigint_action, NULL);
```
Windows path `server.cpp:536-539` (SetConsoleCtrlHandler → CTRL_C_EVENT → `signal_handler(SIGINT)`).

**Handler body — first vs second signal** — `server.cpp:29-38`:
```
if (is_terminating.test_and_set()) {
    fprintf(stderr, "Received second interrupt, terminating immediately.\n");
    exit(1);
}
shutdown_handler(signal);
```
First signal → `shutdown_handler(signal)`; second → `exit(1)` (hard exit, skips clean_up).

**shutdown_handler assignment (single-instance mode)** — `server.cpp:519-523`:
```
shutdown_handler = [&](int) {
    mcp_mgr.shutdown();
    // this will unblock start_loop()
    ctx_server.terminate();
};
```
Router-mode variant `server.cpp:462-469` sets `stopping`, calls `mcp_mgr.shutdown()`, `ctx_http.stop()`. Declaration `server.cpp:26-27`; `llama_server_terminate()` (external trigger) `server.cpp:47-51`; `signal(SIGPIPE, SIG_IGN)` `server.cpp:100-101`.

**Return after shutdown (exit status 0)** — `server.cpp:575-590`:
```
// this call blocks the main thread until queue_tasks.terminate() is called
ctx_server.start_loop();
clean_up();
ctx_http.join();
...
    return 0;
}
```
Status propagates `server.cpp:122-124` (`const int result = llama_server(...); ... return result;`). Error exits `return 1` at model-load failure `server.cpp:507-511`, HTTP start failure `server.cpp:455-458`/`495-497`.

**`/health` route + ready body** — registration `server.cpp:278-279` (`ex_wrapper(routes.get_health)`, "public endpoint (no API key check)"); handler `server-context.cpp:5288-5299`:
```
this->get_health = [this](const server_http_req &) {
    // error and loading states are handled by middleware
    auto res = create_response(true);
    ...
    res->ok({{"status", "ok"}});
```
Body literal at `server-context.cpp:5297`: `res->ok({{"status", "ok"}});`.

**Loading envelope** — `server-http.cpp:307-328` `middleware_server_state`: when `!is_ready`, non-frontend paths get `res.status = 503` body `{"error": {"message": "Loading model", "type": "unavailable_error", "code": 503}}`. `is_ready` set true only after `routes.update_meta(ctx_server)` post `load_model` (`server.cpp:515`). Public set `server-http.cpp:251-254`.

**Docs contract** — `README.md:479-490`: 503 body `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}` while loading; 200 body `{"status": "ok" }` "the model is successfully loaded and the server is ready."

**Shutdown primitives** — `server-context.cpp:4797-4799` `void server_context::terminate() { impl->queue_tasks.terminate(); }`; `server-queue.cpp:132-136` `server_queue::terminate`: `running = false; condition_tasks.notify_all();`; `server-queue.cpp:138-161` `process_new_tasks` returns `true` (terminate) on `!running`; `server-queue.cpp:278-366` `start_loop` breaks the loop on that; declaration `server-queue.h:78`.

**Edge: GCP health remap** — `server-http.cpp:834-837`: `AIP_HEALTH_ROUTE` env can re-register `"/health"` handler at another path — a v2 harness should not assume `/health` is the only health route. [INFERENCE] also note `middleware_server_state` admits `/health` *is* blocked by the 503 gate during loading (it's not in `frontend_paths`), consistent with README.

# C2 implications (advice, for the C2LiveTool seat)
- Ready `/health` body is exactly `{"status":"ok"}` — a `degraded`/`loading` 200 is non-conforming; 503 during load is the documented loading envelope (exact 503 JSON above).
- Graceful teardown on SIGTERM: handler → `shutdown_handler` → `ctx_server.terminate()` → `queue_tasks.terminate()` → `running=false` → `start_loop` breaks → `clean_up()` → `return 0`. So a graceful SIGTERM exit is rc 0 **only after** `sigterm_sent`; a second signal forces `exit(1)` — "kill it harder" yields rc 1, not 0.
- `Popen.returncode` semantics: `0` = exited normally; negative `-N` = killed by signal N (SIGKILL'd → `-9`), per Python subprocess docs — needed so the gate can distinguish `exit(0)` from `-9`/`-15`. [INFERENCE: cite docs.python.org/3/library/subprocess.html for the SOURCES row; pinning Python docs was not in my item scope.]

# Outputs
- `…/round-17/sources/pin.py` (script, stdlib only)
- `…/round-17/sources/pins.json` (6 files: url/sha256/bytes/saved_as; 26 pins: file, 1-based line ranges, locator spec, verbatim)
- `…/round-17/sources/llama.cpp-704366d/tools/server/{server.cpp,server-context.cpp,server-http.cpp,README.md,server-queue.cpp,server-queue.h}` (raw byte-identical copies)

# Limitations
- Brace-matching locator strips `"…"`/`'…'` literals and `//` comments per line — crude but deterministic; C++ block comments spanning lines could mis-balance (none present in pinned regions).
- GitHub REST tree API was rate-limited (403); server-queue paths were discovered by direct candidate-path probing of raw.githubusercontent.com — no content impact, all fetches commit-pinned.
- Pins are line ranges in pinned-commit files; if upstream moves code the anchors, not the numbers, carry the identity.
- No ports bound, no llama-server run, no lane gates touched.

# Installs
None. `python3` stdlib (`urllib.request`, `hashlib`, `re`, `json`) only — per pacman-pause ruling nothing was installed.
