VERDICT: partial — S043's spans, digest and both Gate quotes resolve verbatim, but `teaches` overstates "first SIGTERM after install ⇒ return 0" (the signal is swallowed before `start_loop` sets `running = true`) and the anchor labels lines 26-38 as `signal_handler`, whose body is 29-38.

# What I attacked

Re-opened SOURCES row S043 at lane commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`
(`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:55`, identical at that
commit and in the working tree — row sha256 `88e599805a0ac995266759a15e71086f0a1d221fbdc3cb7dba21e0f4a6536e3f`),
the two `## Gate` rows that admit it (`corpus/lessons/round-17.md:62-63`), and the
`used-by` citations. Bytes were re-fetched from the pinned commit, not from the lane's
saved copies.

# Cell-by-cell

Source under test:
`https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp`
(raw sha256 `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4`, 24572 bytes)
and `.../server-queue.cpp` (sha256 `168385b752fa70df9790f51179e34e375284a296cd44af92b41c5d25da32a2ba`).

| Cell | Verdict | Evidence |
|---|---|---|
| `id` S043 | agree | Next unused after S042; census shows 46 unique rows, no duplicate ids. |
| `source` | agree | Blob URL returns 200; GitHub tag ref `refs/tags/b11755` → `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (`type commit`), so "(release b11755)" is exact. NOTE: the anchor also cites `server-queue.cpp`, which the `source` cell does not name; it is the same pinned commit and the lane's `pins.json` pins it separately. |
| `kind` = code | agree | C++ upstream source; `code` is in the contract enum (`/home/vgpnk/Projects/shokunin/CORPUS.md:91-92`). |
| `tier` = A for this `scope` | agree | Contract: A includes "source code", scoped, never global (`/home/vgpnk/Projects/shokunin/CORPUS.md:93-95`). The scope is one process's signal path at one commit — no inflation, no `community`-as-A. |
| `scope` | agree, one omission | "single-model" is the repo's own label: `server.cpp:424` "single-model mode (NOT spawned by router)". Exclusions (router, SIGKILL, sender) are honest. Omission: install is also gated by `if (!is_run_by_cli)` at `server.cpp:527`; the ordinary binary passes real argv (`tools/server/main.cpp:4` "return llama_server(argc, argv);" → `server.cpp:122`) so it installs, but a programmatic `argv == nullptr` embedder does not (`server.cpp:133` "bool is_run_by_cli = (argv == nullptr);"). |
| `anchor` — `signal_handler` 26-38 | DISAGREE (label only) | The symbol starts at 29: `server.cpp:29` "static inline void signal_handler(int signal) {" and the body ends at 38. Lines 26-27 are the two statics the handler uses: `server.cpp:26` "static std::function<void(int)> shutdown_handler;" and `server.cpp:27` "static std::atomic_flag is_terminating = ATOMIC_FLAG_INIT;". The lane's own `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/sources/pins.json` separates them (`signal_handler_body` [29,38], `shutdown_handler_declaration` [26,27]), so the row conflates what its pin separates. The parenthetical "second signal `exit(1)` at 34" is exact. |
| `anchor` — 519-523 | agree | `server.cpp:519` "shutdown_handler = [&](int) {" through `:523` "};", in the non-router `else` branch opened at `:481`; calls `mcp_mgr.shutdown(); ctx_server.terminate();`. |
| `anchor` — 529-534 | agree | `:529` "struct sigaction sigint_action;", `:533` "sigaction(SIGINT, &sigint_action, NULL);", `:534` "sigaction(SIGTERM, &sigint_action, NULL);". |
| `anchor` — after load_model (507), is_ready (515) | agree | `:507` "if (!ctx_server.load_model(params)) {" and `:515` "ctx_http.is_ready.store(true);" both precede the install at 533-534 (single-model branch; the router branch stores readiness at 460). |
| `anchor` — start_loop 575-576, return 0 at 590 | agree | `:575` "// this call blocks the main thread until queue_tasks.terminate() is called", `:576` "ctx_server.start_loop();", `:590` "return 0;". |
| `anchor` — server-queue.cpp terminate() 132-136 | agree | `:132` "void server_queue::terminate() {", `:133` lock, `:134` "running = false;", `:135` notify_all, `:136` "}". |
| `anchor` — server.cpp raw sha256 | agree | Recomputed on the raw fetch: exact match `2143962217…f5aef4`. |
| `teaches`, clause 1: first SIGTERM after install ⇒ `return 0` | DISAGREE (narrow, code race) | True only once `start_loop()` has executed `running = true` (`server-queue.cpp:279` "running = true;"). A SIGTERM in the window [install at 534, that line] runs `terminate()` → `running = false` (`:134`), then `start_loop` overwrites it with `true`, and the loop's only exit test is `:141` "if (!running) {" → `:143` "return true;". The first SIGTERM is swallowed; the process keeps serving and a second signal exits 1, not 0. The same window also contains a post-install `return 1` path at `server.cpp:549-554` (llama-connect failure). `/health` can be 200 at `:515`, i.e. before the install, so a client acting on readiness can land in either window. No runtime repro (`[INFERENCE]`, deterministic ordering only). |
| `teaches`, clause 2: later signal ⇒ 1 | agree | `:30` test_and_set, `:33` `fprintf(stderr, "Received second interrupt, terminating immediately.\n");`, `:34` "exit(1);". |
| `teaches`, clause 3: SIGTERM before 534 ⇒ default (returncode -15) | agree, caveat | No SIGTERM handler and no SIGTERM ignore before 534 in this file (`:101` ignores only SIGPIPE). Caveat: an inherited `SIG_IGN` from the parent would change this; the claim silently assumes default disposition. |
| `teaches` trail: "README documents no exit status" | agree | Pinned `tools/server/README.md` at 704366d76: 0 hits for `SIGTERM`/`SIGINT`; no "exit status"/"exit code"/"graceful"; the three `exit` hits are option help text (":34 print usage and exit", ":79", ":206 container cleanup"). |
| `status` = mined | agree | Cited by two paths in `used-by`; `mined` requires ≥1 (`CORPUS.md:103-104`). |
| `opened` = 2026-10-20 | agree | Gate preamble: `lessons/round-17.md:56` "All sources opened 2026-10-20." |
| `recheck` = on-release | agree | Line-number anchors against a tag make a release the natural recheck; consistent with S001/S042. |
| `used-by` paths exist and cite S043 | agree | `corpus/knowledge/llamacpp-loading-lifecycle.md:153` "(… `get_health` 5288-5299), S043" and `:174` "(S043). The first signal calls `ctx_server.terminate()` (519-523)"; `corpus/lessons/round-17.md:39`, `:62`, `:63`. All exist. `corpus/README.md:238` also cites S043 but is the corpus index, not a knowledge entry or lesson, so the contract's used-by wording (`CORPUS.md:107-108`) excludes it — correctly omitted `[INFERENCE]`. |

Downstream copy: the same over-broad sentence is in
`corpus/knowledge/llamacpp-loading-lifecycle.md:174-176` "The first signal calls
`ctx_server.terminate()` (519-523), which stops the task loop" … "returns 0" — the
loop-reset race applies to it too. `[INFERENCE]` the three observed live runs
(`.ufo/waves/round-17/live/receipt-{1,2,3}.json`, rc 0, 3 ms) sent SIGTERM after loop
entry, so they neither verify nor refute the window; the residual risk is a flake in
`teardown_graceful`, not a false pass.

# Gate quotes (`corpus/lessons/round-17.md`)

| Gate row | Verdict | Evidence |
|---|---|---|
| `:62` "A first SIGTERM after handler install ends in `return 0` \| admit, scoped (S043)" | quote agree; decision inherits clause-1 defect | URL is the pinned server.cpp URL; `:575` quote "this call blocks the main thread until queue_tasks.terminate() is called" is verbatim (10 words) and located at `server.cpp:575`; `line 590` is `return 0;`. The quote grounds the loop/return, not the [534, loop-entry] window, so "admit, scoped" is scoped only in prose. |
| `:63` "A second signal exits 1 \| admit (S043)" | agree | `server.cpp lines 33-34`, quote "Received second interrupt, terminating immediately." verbatim (5 words) at `:33`; `exit(1);` exact at `:34`. URL is carried by the preceding row of the same table; access date is the table preamble. Minor: this row has no URL of its own. |
| Rule 1 completeness | minor gap | No Gate quote grounds `teaches` clause 3 (default action before line 534); the install-ordering span (529-534) appears only in the anchor. Rule 1 requires one ≤25-word quote per row, which is met, so this is a completeness nit, not a violation. |

Both quotes are ≤25 words and verbatim against the pinned bytes; no invented text.

# Commands run (exit codes)

All tool runs were in `/tmp/KamaR17.ReopenS043-clone` at `54a29268…`, never in the lane;
read-only `git show` was run in the lane.

- `git clone -q <lane> /tmp/KamaR17.ReopenS043-clone && git checkout -q 54a29268…` → printed the lane commit, exit 0.
- `curl -sS -o server.cpp -w '%{http_code} %{size_download}' https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76…/tools/server/server.cpp` → `200 24572`, exit 0; `sha256sum` → `2143962217…f5aef4`.
- Same for `server-queue.cpp` → `200 22141`; sha256 `168385b752…a2ba`.
- `curl -sS https://api.github.com/repos/ggml-org/llama.cpp/git/refs/tags/b11755` → `refs/tags/b11755 704366d76… commit`, exit 0.
- `curl -o /dev/null -w '%{http_code}' https://github.com/ggml-org/llama.cpp/blob/704366d76…/tools/server/server.cpp` → `200`, exit 0.
- `python3 final_check.py` (anchors, digest, quote verbatim/word counts, Gate rows, rename check) → 23 PASS, `EXIT=0`.
- Corpus census from `/home/vgpnk/Projects/shokunin/CORPUS.md:138-150` on the clone: 46 rows; malformed 0; enum/tier-inflation none; missing used-by none; duplicate ids none, exit 0.
- `python3 tools/sources-append-only.py --from cff9e62 --to 54a29268 --repo /tmp/KamaR17.ReopenS043-clone --json` → `"violations": []`, added S042-S046, `"ok": true`, EXIT=0.
- `git show 54a29268:corpus/SOURCES.md | awk NR==55 | sha256sum` equals the working-tree row → exit 0.
- `grep -c -i 'sigterm\|sigint' tools/server/README.md` (pinned) → `0`; `grep -n -i 'exit status\|exit code\|graceful'` → no match.
- `grep -n 'running = true\|running = false' server-queue.cpp` → `134`, `279` (and `507`, which is `server_response::terminate()`, a different class), exit 0.

# Limitations

- The swallowed-signal window is a static-code conclusion, not a runtime repro: the
  clone holds no built llama.cpp and no model, and building/running one was out of
  scope. Ordering is deterministic in the pinned bytes, so confidence is high
  `[INFERENCE]`.
- The window is small in the default configuration (sigaction → log → `start_loop`);
  it widens with `--server-connect` startup and is material only when a client signals
  on the first `/health` 200 (possible from `server.cpp:515`).
- Default-action clause assumes the process does not inherit `SIG_IGN` for SIGTERM.
- Windows `SetConsoleCtrlHandler` path (`:536-539`) not assessed; out of the row's Unix scope.
- Line numbers are those of the raw blob at `704366d76`; the GitHub blob page was
  checked only for HTTP 200, not line rendering.

# Installs

None. No tool was installed or upgraded; no pacman transaction attempted. No server or
port was started, so nothing needed teardown; `ss` was not needed.

# Scratch

Removed before finishing: `/tmp/KamaR17.ReopenS043-clone`, `/tmp/KamaR17.ReopenS043-work`,
`/tmp/tree.json`, `/tmp/reopenS043-*`. Only this Report was written in the lane.
