VERDICT: partial — ready body and graceful SIGTERM exit are code-verified at 704366d76; SIGTERM-during-load and router behaviour are code-order inferences, not run.

# ScribeKnowledgeTeardown — round 17 BUILD

Owned output: `.ufo/waves/round-17/build/drafts/knowledge-teardown.md` (append-ready section "Ready body and graceful teardown (round 17)"). No lane doc, SOURCES row, frozen copy, or receipt was edited.

## Findings (all sources opened this session, access date 2026-10-20)

1. Ready body. `tools/server/server-context.cpp:5297` — "res->ok({{"status", "ok"}});" (`get_health`, lines 5288-5299). `ok()` at 4868-4870 stores `safe_json_to_str(response_data)`. Lane receipt `.ufo/waves/round-16/live/receipt.json:21-33` holds `{"status":"ok"}`, 15 bytes, sha256 `a29ee2b1…d288`; I recomputed that digest over the 15 bytes and it matches. README `tools/server/README.md:489` shows `{"status": "ok" }` with spaces: documentation only, so checks should compare parsed JSON.
2. Readiness gate. `tools/server/server-http.cpp:307-328` answers `/health` with the 503 "Loading model" body while `is_ready` is false; `server.cpp:515` sets `is_ready` true after `load_model` (507).
3. SIGTERM. `tools/server/server.cpp:534` — "sigaction(SIGTERM, &sigint_action, NULL);". This block (527-534) runs after `load_model` (507). The only SIGTERM reference in the pinned `tools/server`, `common`, `src`, `ggml` trees is line 534.
4. Handler behaviour. `server.cpp:29-37`: first signal → `shutdown_handler`; second → "Received second interrupt, terminating immediately." and `exit(1)`. Single-model shutdown `519-523` → `ctx_server.terminate()` → `server-queue.cpp:132-136` sets `running=false`; loop breaks at `server-queue.cpp:299-302`; `server.cpp:578-590` runs clean-up, joins, `return 0`. Entry `tools/server/main.cpp`: `return llama_server(argc, argv);`.
5. Graceful exit status at this commit = 0 (code-derived). Model-load failure = 1 (`server.cpp:507-512`). The README §GET `/health` (lines 479-490) documents no exit status; no other exit-code doc was opened.
6. Python: https://docs.python.org/3/library/subprocess.html §`Popen.returncode` — "A negative value -N indicates that the child was terminated by signal N (POSIX only)." The harness starts the child with `start_new_session=True` (`tools/kama-llamacpp-live.py:904`), as an argv list (909, no shell), and sends `os.killpg(proc.pid, signal.SIGTERM)` (666). So `-15` = default-disposition SIGTERM death, `-9` = SIGKILL, `0` = `llama_server` returned 0.
7. Receipt teardown (`receipt.json:403-417`): returncode 0, sigterm_sent true, sigkill_sent false, term_wait_ms 3. Its three kept log lines do not include the handler's clean-up line (`server.cpp:484`, "cleaning up before exit..."). The harness's log-reduction rule was not opened, so the absence is unexplained. This matters for the C2 check: `returncode 0` alone does not prove the signal caused the exit.

## Limits and unknowns

- One build (b11755 = 704366d76, S038), CPU x86-64, `-t 1 -c 256`, fixture stories260K (sha256 270cba1b…d256bd), one sampled run. Not consumer health; ports 8080/34113 untouched.
- SIGTERM during model load: not run. By code order the default action should apply → `-15` [INFERENCE from code order; not run].
- Router mode: handler also installed after `load_startup_models()` (`server.cpp:472` before 527) [INFERENCE from code order; not run].
- The installed launcher `~/.local/opt/llama-b11755/llama-server` was not confirmed to be built from this `main.cpp`; the receipt shows only the argv path.
- The pinned tree was fetched from the codeload tarball `llama-704366d.tar.gz`, sha256 c2d31d5f462e899b580327d242c4fa6e61b704bcbd9dbcf6d4e7698ba3700749 (not an official asset digest). The pinned-directory files `server.cpp` (2143962…), `server-http.cpp` (24ede17…), `README.md` (714c067…) and `server-context.cpp` (dd1de0f…) match `.ufo/waves/round-16/sources/llama.cpp-704366d/pins.json` / sha256 checks run this session. `server-queue.cpp` (168385b7…) and `main.cpp` (7ec68458…) are tarball-only and not in pins.

## Provisional registry rows for L1

- S042 — llama.cpp `tools/server/server.cpp` + `main.cpp` @ 704366d76 (signal install, shutdown, exit 0), code, tier A, scope single-model b11755.
- S043 — llama.cpp `tools/server/server-context.cpp` + `server-queue.cpp` @ 704366d76 (ready body, `terminate()`), code, tier A.
- S044 — Python `subprocess` docs §`Popen.returncode` (negative -N = signal), docs, tier A; the served page is the 3.15 dev docs.

## Installs / updates

None. Used `curl` and `tar` (system binaries) to fetch the tarball and docs into `/tmp/scribe-r17`; that scratch directory is removed at the end of this run. No experiments were run (no llama-server started, no ports bound).

## Files touched

- Written: `.ufo/waves/round-17/build/drafts/knowledge-teardown.md`, this report.
- Not touched: corpus, SOURCES, frozen copies, receipts, `.ufo/state/`, and every other lane path.
