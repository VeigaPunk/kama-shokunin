VERDICT: confirm — `corpus/README.md:238` credits the SIGINT/SIGTERM path to S043 alone; S047 supersedes S043 for the first-SIGTERM window. Draft written at `.ufo/waves/round-18/build/drafts/readme-append.md`; not integrated, lane docs untouched.

## Behavior
- Drafted an append-only §Correction for the end of `corpus/README.md` (after line 245) that scopes S047 to the first-SIGTERM-before-`start_loop` window and leaves S043 standing for the rest.
- Drafted three provisional round-18 coverage rows (`knowledge/llamacpp-loading-lifecycle.md` §Round 18, `knowledge/loopback-listener-ownership.md`, `lessons/round-18.md`) plus a provisional frontier paragraph. Each row is marked provisional with its integration condition.
- No lane file, frozen copy, SOURCES row, or knowledge file was edited. No server was started, no port bound, no measurement run.

## Sources (opened this session; access date 2026-10-20)
- `corpus/README.md:238` (lane tip `e75cf680b53484a61709ee1b2787d8dbc6419f74`, read via `git show master:corpus/README.md`, lines 200-245): "the SIGINT/SIGTERM shutdown path and exit statuses (S043)".
- `corpus/lessons/round-17-verifier-spotcheck.md:232-233` (R3): "Append a pointer to S047."
- `corpus/SOURCES.md:59` (S047 row, git show master): "supersedes S043 — a first SIGTERM ends in `return 0` only once `start_loop` is running".
- `corpus/knowledge/llamacpp-loading-lifecycle.md:218` (git show master, §Round 17 falsify correction): "(S047, supersedes S043; static ordering, not reproduced)".
- llama.cpp 704366d76, `tools/server/server.cpp:534` (URL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp; read from the lane's pinned copy `.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/server.cpp`, sha256 `2143962217e9d627…` matches `pins.json`): "sigaction(SIGTERM, &sigint_action, NULL);".
- `server.cpp:33-34` (same pinned copy): "Received second interrupt, terminating immediately." then "exit(1);".
- `server.cpp:575` (same pinned copy): "this call blocks the main thread until queue_tasks.terminate() is called".
- `server-queue.cpp:278-279` (URL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-queue.cpp; pinned copy `.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/server-queue.cpp`, sha256 `168385b752fa70df…` matches `pins.json`): "void server_queue::start_loop(int64_t idle_sleep_ms) {" then "running = true;".
- `server-queue.cpp:132-134` (same copy): "void server_queue::terminate() {" then "running = false;".
- `server-queue.h:18` (same pinned directory): "bool running  = false;" (default false in `struct server_queue`, lines 4-18).

Reasoning chain (static, read from the bytes above): `shutdown_handler` calls `ctx_server.terminate()` (`server.cpp:519-523`), which sets `running = false` (`server-queue.cpp:134`). If that happens before `start_loop` (`server-queue.cpp:278-279`), `running` is already false and the call is a no-op; `start_loop` then sets `running = true`, so the loop never sees the stop. A later signal hits `is_terminating` and calls `exit(1)` (`server.cpp:33-34`). This is [INFERENCE] from ordering alone.

## Findings
1. R3 is real: `README:238` names S043 for the shutdown path and exit statuses, and nothing in the README points to S047. Confirmed on the lane tip.
2. The draft's correction is scoped to the first-SIGTERM window only. S043 still holds for handler registration, the second-signal `exit(1)`, and the return-0 path once the loop runs. The draft does not overstate S047 beyond that window.
3. The draft cites S047 with a pinned-copy location and the digest-matching pin. It does not claim runtime reproduction.

## Limitations / unknowns
- The window is static. Not reproduced at runtime; no seat ran a scratch server for this draft. [INFERENCE: the loop never observes the signal; unverified in practice.]
- I did not re-fetch the GitHub URLs this session; I read the lane's pinned copies, whose sha256 matches `.ufo/waves/round-17/sources/pins.json`. The access date on the URLs is 2026-10-20.
- Unknown whether `loopback-listener-ownership.md`, `lessons/round-18.md`, or the §Round 18 section of `llamacpp-loading-lifecycle.md` will land; the draft says so. The knowledge-ownership draft is not present under `build/drafts/` at the time of writing.
- The v3 receipt contract (exit codes 0/1/2/3, `passed: null` rule) is taken from the round-18 build assignment as declared, not from an opened source or a measured run. The draft labels it "declared, not yet measured".
- The S047 `## Gate` row (R1) is not in my scope and is not done here; the README draft does not depend on it, but the round-18 lesson does.
- Line numbers are from the pinned copies and the lane's `README.md`; they were verified by `sed`/`grep -n` this session.

## Installs
None. No tools were installed or updated for this item.

## Checks for L1 to run
- Integrate the draft at the end of `corpus/README.md` only after the referenced knowledge §Round 17 correction and the round-18 files exist or the provisional rows are trimmed to the entries that land. No gate or measurement is needed for a README-only append.
- Confirm line 238 is unchanged after the append (append-only rule).
