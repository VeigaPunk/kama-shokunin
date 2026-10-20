VERDICT: confirm — round-17.md `## Gate` has no S047 row (R1 holds); the drafted round-18 Gate rows match pinned server-queue.cpp 132-134, 141-143, 278-279 and server.cpp 33-34, 534, 575-576, 590.

# Scope
- Owned file: `.ufo/waves/round-18/build/drafts/s047-gate.md` (sha256 fa4e66e395fcf88ce156e66234bb8300e2bde598de46c4564765bab752099a30). Report: this file. No lane doc, frozen copy, or round-17 lesson was edited. No server was started; no port was bound; no installs.
- Date of access for every source below: 2026-10-20.

# Findings
1. R1 confirmed. `corpus/lessons/round-17.md` `## Gate` (lines 54-79) has S043 rows (lines 62-63) and no S047 row. S047 appears only at round-17.md:224 and :309 (`corpus/lessons/round-17-verifier-spotcheck.md:225-228` routes R1). Round-18 lesson file `corpus/lessons/round-18.md` does not exist yet, so the draft targets a file L1 creates.
2. Source opened: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-queue.cpp (fetched via its raw mirror; identical lines to the pinned copy). Pinned copy `.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/server-queue.cpp` sha256 168385b752fa70df9790f51179e34e375284a296cd44af92b41c5d25da32a2ba equals `.ufo/waves/round-17/sources/pins.json`.
   - `terminate()` at lines 132-136; `running = false;` at line 134. Quote: "void server_queue::terminate() {" (132).
   - `start_loop(int64_t idle_sleep_ms)` at lines 278-280; `running = true;` at line 279 (no lock taken there). Quote: "void server_queue::start_loop(int64_t idle_sleep_ms) {" (278).
   - Loop exit test `if (!running) {` / `return true;` at lines 141-143 (`process_new_tasks`); loop calls at 299-303 and 322-323.
3. Source opened: server.cpp (pinned, `.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/server.cpp`). `shutdown_handler` assigned 519-523 with comment "this will unblock start_loop()"; `sigaction(SIGTERM, &sigint_action, NULL);` at 534; comment "this call blocks the main thread until queue_tasks.terminate() is called" at 575; `ctx_server.start_loop();` at 576; `return 0;` at 590; `signal_handler` 29-38 with `exit(1);` at 34.
4. Decision in the draft: the S043-style candidate ("a first SIGTERM after handler install ends in return 0") is split. A signal after `start_loop()` begins is admitted, scoped (S047). A signal after the handler install (534) and before `start_loop()` sets `running = true` (279) is rejected: the stored `running = false` is overwritten before the loop reads it.

# Limits and unknowns
- The window consequence (server keeps serving until a second signal, which exits 1) is [INFERENCE] from code reading; no binary was run and the lane has no probe for it.
- Not read: server.cpp lines 535-575, so the window length is unknown.
- Not checked: whether any receipt or frozen probe depends on the S043 reading.
- Round-17 spotcheck R2 and R3 are out of this draft's scope.

# Installs
None.

# Artifacts
- `.ufo/waves/round-18/build/drafts/s047-gate.md` (draft for L1).
- `.ufo/waves/round-18/build/advice/ScribeS047Gate.md` (this report).
