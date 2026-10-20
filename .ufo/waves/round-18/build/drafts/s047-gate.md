# Draft: round-18 lesson `## Gate` rows for S047 (append-ready; L1 integrates)

Target: `corpus/lessons/round-18.md` (not yet present; L1 creates it and appends this section). `corpus/lessons/round-17.md` is not edited.

S047 was opened in round 17 (`corpus/SOURCES.md:59`; `corpus/lessons/round-17.md:224`) without a Gate row; this Gate row is appended in round 18.

## Gate

All sources opened 2026-10-20. Quotes are verbatim and at most 25 words.

| Candidate | Decision | Source, location, quote |
|---|---|---|
| A first SIGTERM delivered after `start_loop()` begins ends the process with `return 0` | admit, scoped (S047) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-queue.cpp lines 132-134 "void server_queue::terminate() {" then "running = false;"; lines 141-143 "if (!running) {" then "return true;"; server.cpp line 575 "this call blocks the main thread until queue_tasks.terminate() is called"; line 590 `return 0;` |
| A SIGTERM delivered after the handler is installed and before `start_loop()` sets `running = true` ends the process | reject; the unscoped S043 reading is superseded (S047) | server.cpp lines 529-534 install the handler ("sigaction(SIGTERM, &sigint_action, NULL);"); server.cpp line 576 "ctx_server.start_loop();"; server-queue.cpp line 134 "running = false;" is overwritten by line 279 "running = true;" in "void server_queue::start_loop(int64_t idle_sleep_ms) {" (line 278) before the loop reads it at line 141 |

Notes to the rows above:

- Row 2 consequence is [INFERENCE], code-derived and not run: the loop leaves only when `running` is false (server-queue.cpp lines 299-303 and 322-323), so a first signal in that window should be consumed and the server should keep serving. A second signal exits 1 ("Received second interrupt, terminating immediately." then `exit(1);`, server.cpp lines 30-34). No lane probe covers this window.
- Unknown: how long the window between server.cpp line 534 and line 576 lasts (lines 535-575 were not read in this session), and whether any receipt depends on the round-17 S043 reading. Not checked here.
- Pin check: the local pinned copy `.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/server-queue.cpp` has sha256 168385b752fa70df9790f51179e34e375284a296cd44af92b41c5d25da32a2ba, equal to `pins.json`; the fetched blob shows the same lines 132-136 and 278-280.
