VERDICT: partial — the newly supplied Gate is correctly necessary-only and the KQ23 reset/read accounting is exhaustive and byte-exact, but the integrated S043 README correction overstates supersession and drops the window endpoints, the in-window outcome, the surviving post-start `return 0` path and the static-only caveat; one knowledge inference is unsound evidence even though the receipts do prove its conclusion.

# Scope and method
Read-only. Reviewed the pushed lane master `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` (`git cat-file -t` → commit; subject "round-18: retain measured arms and repair counter classification seams"). No clone was needed because no runtime/gate experiment was named or run. No server, socket, port, install or package transaction occurred. Nothing written except this report.

Sources read at their pinned bytes, `.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/`:
- `server-queue.cpp` sha256 `168385b752fa70df9790f51179e34e375284a296cd44af92b41c5d25da32a2ba`
- `server.cpp` sha256 `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4`
- `server-queue.h` sha256 `d77a3eac479e8ad772b325db643225ea3e68a9715709e375d859295c31161924`
- `server-context.cpp` sha256 `dd1de0f26536ce3e…` (matches the value the build review recorded).
All three named hashes match `.ufo/waves/round-17/sources/pins.json` (`grep -n "server" pins.json`, exit 0). Commands used: `grep -n "running" …` (every file), `sed -n` on the cited ranges, `nl -ba`, and `git show 1c325b2:<doc>` for corpus text.

# Confirmed (no attack lands)
1. **R1 baseline holds.** `corpus/lessons/round-17.md` §Gate at lines 54–79 contains the two S043 rows (62–63) and no S047 row; S047 appears only at `:224` and `:309`. The round-18 lesson's claim "Existing S047 receives its missing Gate row here, not by editing round 17's lesson" (`lessons/round-18.md:36-37`) is true.
2. **The integrated Gate is a necessary condition, not a sufficiency/termination claim.** `lessons/round-18.md:41` admits "necessary ordering condition (S047; R1)"; `:42` rejects "Handler installed implies SIGTERM necessarily terminates with 0" and says "An actual termination guarantee additionally needs locking/shutdown assumptions"; `:71-80` says "KQ23 admits that bounded condition, not a guarantee of successful shutdown" and names unexamined shutdown calls, locking and platform signal assumptions, and "no runtime reproduction of that window occurred". `knowledge/llamacpp-loading-lifecycle.md:232-237` repeats the necessary-only framing. I found no surviving sufficiency wording in the *integrated* Gate or lesson. The pre-integration draft's sufficiency wording is flagged separately (F3).
3. **KQ23 write accounting is complete for `server_queue::running`.** The member is private (`server-queue.h:15-18`, `private:` at 16), so writes can only come from `server_queue` methods. `grep -n "running"` over all pinned server files returns:
   - `server-queue.cpp:134` `running = false;` inside `server_queue::terminate()` (132–136, under `mutex_tasks` at 133);
   - `server-queue.cpp:279` `running = true;` at the top of `start_loop()` (278–280, no lock taken);
   - `server-queue.h:18` `bool running  = false;` default initializer (pre-arming: `server.cpp:213` constructs `server_context ctx_server;`, `server-context.cpp:4785` ctor, `:957` `server_queue queue_tasks;`, all before `sigaction` at 534);
   - `server-queue.cpp:507` `running = false;` is `server_response::terminate()` operating on the *different* private member `server_response::running` (`server-queue.h:156`, `private:` at 155) and is correctly excluded; 431/463 are reads of that same different member.
   So the post-arming writer set is exactly {134, 279}; the lesson's "both writes (134,279)" is accurate and not a sampling.
4. **The read/outcome accounting is exact.** The termination decision is `if (!running) { … return true; }` at `server-queue.cpp:141-143`; the outer loop's only exit is `:301-302` (`if (process_new_tasks(false)) { break; // terminate`); other reads (322, 337, 339, 355) send control back to 141, and 196 is the worker-thread read. The outcome `return 0;` at `server.cpp:590` is reached only after `start_loop()` returns (576 → `server-context.cpp:4792-4795`) and `clean_up()`/joins (578-582). The handler chain is whole at the pinned bytes: `signal_handler` 29-38 (`shutdown_handler(signal);` at 37) → `shutdown_handler` 519-523 (`ctx_server.terminate();` at 522) → `server_context::terminate()` `server-context.cpp:4797-4799` (`impl->queue_tasks.terminate();`) → `server-queue.cpp:132-136`.
5. **R3's mechanical requirements are met.** `corpus/README.md:238` is byte-unchanged, and `git diff e75cf68..1c325b2 -- corpus/README.md` is one pure-addition hunk after line 245 (`@@ -243,3 +243,26 @@`; no `-` lines). The append names S047 and points at `lessons/round-18.md` (README:249-253). `SOURCES.md:59` carries the scoped `teaches` ("only once `start_loop` is running; one delivered after install (534) but before … (279) is lost … later signal exits 1 … Static ordering; not reproduced at runtime") and the old→new `used-by` addition is recorded at `lessons/round-18.md:147`.
6. **The runs did not hit the window — provable from retained artifacts, but not by the reason the knowledge gives.** All three receipts (`.ufo/waves/round-18/live/receipt-{1,2,3}.json`, schema `kama-llamacpp-live/v3`, outcome `pass`) record `teardown = {alive_at_teardown_start: true, sigterm_sent: true, sigkill_sent: false, returncode: 0, term_wait_ms: 3}`. `tools/kama-llamacpp-live.py:798-829` sends exactly one SIGTERM, waits `TERM_GRACE = 10.0` s (`:73`), then SIGKILLs. A first signal lost in the [534, 279] window leaves the process alive → `-9` with `sigkill_sent: true`; a signal before 534 takes the default disposition → `-15`. `returncode 0` therefore excludes both, and is the deciding citation.

# Findings

## F1 — MEDIUM. The integrated README correction drops the window and the surviving half of S043.
`corpus/README.md:249-253` as landed: "**S047 supersedes S043's first-signal claim**: a post-install signal can be overwritten by `start_loop()` resetting `running`; … S043 still identifies the registration and second-signal exit path; it is not a sufficient guarantee."
Against the reviewed draft `.ufo/waves/round-18/build/drafts/readme-append.md`, four load-bearing parts were lost in integration:
- "for one path only";
- both window endpoints (`server.cpp:534`, `server-queue.cpp:279`);
- the outcome inside the window ("is lost: the server keeps serving, and a later signal exits 1");
- "S043 still stands for … the return-0 path once `start_loop` is running (`server.cpp:575-590`)", and "The window is a static ordering reading and has not been reproduced at runtime."

Consequences, in this round's own terms:
- KQ23 (`corpus/QUALITY.md:132`) requires the claim to name the interval by its two cited statements. The README paragraph names no line number and no outcome, so it is exactly KQ23's "a scoped label names no window" shape, one document removed from the lesson that gets it right. A reader of the map alone cannot tell which post-install signals are affected (the existential "can" is true but uninformative) and is left with the false impression that S043's first-signal claim is wholly dead, when the post-279 `return 0` path is still correct.
- The README also loses the static-only caveat, so the map presents an unqualified code claim with no reproduction status; the lesson and knowledge carry that caveat, but the map does not.
This is a documentation/calibration defect, not a code or runtime defect, and it does not refute C1/C2. It is repairable only by an appended correction (README is append-only; do not edit 249-253).

## F2 — MEDIUM-LOW. The knowledge's window-exclusion inference is unsound; the receipts' `returncode 0` is the evidence it should cite.
`knowledge/llamacpp-loading-lifecycle.md:218-220`: "The harness signals only after `/health` 200, the readiness captures and both probe runs, so its runs did not hit that window, but `/health` 200 (server.cpp:515) does not by itself prove the handler is installed."
The "so" does not follow:
- `/health` 200 is set at `server.cpp:515`, *before* the handler install at 534, so it proves neither handler install nor `start_loop` entry — the sentence itself concedes the first half and then uses the same observation for the stronger second half.
- The readiness captures and probe runs are served by the HTTP thread (`server-http.cpp`), concurrently with the main thread's 534→576 segment; they do not sequence the main thread.
- That segment is not empty: listen-address logging (543-545), optional `server_connect connect_proc; connect_proc.start(params, ctx_http.port)` (547-555, whose own comment at 547 describes a child startup health check), and in child mode `child.setup`/`child.notify_to_router` (569-573). `server-connect.h` is included (`server.cpp:1`) but is not in the pinned tree, so the call's blocking time cannot be bounded from pinned bytes; the draft's open question ("lines 535-575 were not read") is now narrowed, not closed.
The *conclusion* is true and is proved by the retained receipts' `returncode 0` (see Confirmed 6). Fix: append a correction replacing the observation-order reason with the receipt fields, or state the order argument as [INFERENCE] and cite `returncode 0` as the deciding evidence.

## F3 — LOW. The committed pre-integration draft still carries the sufficiency wording the lesson fixed.
`.ufo/waves/round-18/build/drafts/s047-gate.md:13` (sha256 `fa4e66e395fcf88ce156e66234bb8300e2bde598de46c4564765bab752099a30`, unchanged at the tip): "A first SIGTERM delivered after `start_loop()` begins ends the process with `return 0` | admit, scoped (S047)". That is the exact sufficiency reading `RevKQ23FailCapable.md` B1 flagged and the lesson (`:77-78`) says was caught; the integrated Gate fixed it, the committed draft did not. Anyone reading `build/drafts/` as the lane's Gate gets the overclaim. Low because the draft is labelled "L1 integrates" and the lesson is the admitted artifact, but it is a committed contradiction inside the same wave.

## F4 — LOW. The KQ23 positive/negative controls are not reproducible from retained runs.
`lessons/round-18.md:74-78` says the targeted negative control ("remove the reset citation/accounting … reject") and the blind counterexample are recorded in `build/advice/RevKQ23FailCapable.md`; that file shows them as in-memory Python tables (C1–C5), not a retained command. `.ufo/waves/round-18/runs/commands.json` has 32 commands and **zero** occurrences of "KQ23" (`grep -ril kq23 runs/` → no output, exit 1). The lesson discloses "in-memory", so this is a reproducibility limit, not a hidden claim; but no later verifier can re-run the A1–A5 classification from the official artifacts, and the A5 check is a hand judgement over prose (RevKQ23 U5).

## Notes (not finds)
- `lessons/round-18.md:42` compresses the reset to "`server-queue.cpp:279` resets the handler's `running = false;` at 134". 279 writes `true`; it overwrites 134's `false`. The intended reading is clear from `:41` and `:71-73`, but the clause is one parse away from inverting the state (the exact error KQ23 targets). Worth tightening.
- `:86` says "S043 reject" while `:42` says "reject S043's overclaim". KQ23 rejects S043's *unscoped claim*; the row's other cells (registration, second-signal `exit(1)`, pre-534 `-15`) remain correct and are untouched. The shorthand is defensible in context but reads as a source rejection.
- The `shutdown_handler` body (519-523) and the `server-context.cpp:4797-4799` hop are not cited in S047's anchor or in the lesson's KQ23 sentence; they are on the T→O chain and remain an A6-style limit (RevKQ23 recorded it; the lesson covers it generically as "unexamined shutdown calls"). Not a rejection.

# Limits
- Static review only. No llama-server was run, no port bound, no window reproduced; the runtime consequence remains [INFERENCE] exactly as the lesson states.
- I did not re-fetch the GitHub blobs; I read the lane's pinned copies, whose sha256 match `pins.json` for the three files above.
- `server-connect.h`, `common` headers and `main.cpp` are not pinned; statements about them are marked unknown, not judged.
- The README's appended v3/NOT-EVALUATED paragraph (`:255-257`) was not re-audited beyond its KQ24 wording; that is another seat's scope.

# Installs, processes, ports
- Installs/updates: none.
- Servers/listeners started: none; no port was opened, so no teardown proof is owed. No clone and no `/tmp/kama-r18-falsify-ReopenS047` scratch directory was created.
- No git write, no `jj`, no lane-index/fleet change; only `git show`/`git diff` reads.

# What would change the verdict
- F1/F2 would drop if L1 appends a correction that names both window endpoints and the in-window outcome, preserves the post-279 `return 0` path and the static-only status in the README, and replaces the knowledge's observation-order "so" with the receipts' `returncode 0`. F3 would drop if the draft is superseded (or its overclaim marked as superseded in place, per KQ22). None of these changes any code, and none affects C1 or C2.
