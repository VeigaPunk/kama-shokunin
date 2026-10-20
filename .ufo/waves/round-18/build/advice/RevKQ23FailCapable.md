VERDICT: partial — A predicate-and-writer test rejects S043, admits S047 and rejects the targeted mutant. Revised KQ23 (`0cacdbcb…`) still admits S043's overclaim once it cites the lane's pins (C2), and its path-completeness accept control misses on-path calls.

Seat: KamaR18.RevKQ23FailCapable (read-only reviewer, round 18 BUILD). Lane root `/home/vgpnk/Projects/shokunin/kama-shokunin`; every path below is relative to it unless absolute.

# Inputs (read-only, pinned)

- llama.cpp 704366d76 pinned copies, `.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/`:
  - `server.cpp`: sha256 `2143962217e9d627…`
  - `server-queue.cpp`: sha256 `168385b752fa70df…`
  - `server-queue.h`: sha256 `d77a3eac479e8ad7…`
  - `server-context.cpp`: sha256 `dd1de0f26536ce3e…`
  - These hashes match `pins.json`, S043 and S047.
- `main.cpp` is not in `pins.json`. I fetched it from https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/main.cpp (sha256 `7ec684588e04538c…`). Line 4 is `return llama_server(argc, argv);`.
- Drafts reviewed, pinned by sha256 at read time (they may change after this review):
  - `.ufo/waves/round-18/build/drafts/quality-kq23.md`: `4f5fd183b0ee9e22…`
  - `.ufo/waves/round-18/build/drafts/s047-gate.md`: `fa4e66e395fcf88c…`
- Motivation:
  - `corpus/lessons/round-17.md:309` (M8): "falsify scout re-open (KQ6 locates the section; nothing requires reading the whole control path)".
  - `corpus/lessons/round-17-verifier-spotcheck.md:229-230` (R2): "Add a KQ citing round-17 M8, or state why not."

# 1. The criterion test (drafted for R2)

**Applies to:** a `kind` = code row, or a knowledge sentence resting on one, whose `teaches` states what a trigger T leads to: an exit status, a state or a response. Applicability is decided by this rule, never by whether the row calls itself "code-derived".

**Node set — derived by a closure rule, not chosen by the applier:**
- (a) the statement that arms T, and the handler body;
- (b) the outcome statement O;
- (c) the read that selects the branch toward O after T;
- (d) every write to the state that (c) reads which can run after T is armed. Find these writes by a full-set search of the pinned files (count first, KQ9). A write that completes before arming is excluded, and the reviewer records why.

**Admission conjuncts:**
- A1 cites (a).
- A2 cites (b).
- A3 cites (c).
- A4 cites every writer in (d).
- A5: if a writer in (d) can undo T's effect, `teaches` or `scope` names that window by its two cited statements and states the outcome inside it. A5 is a human judgement. Its mechanical proxy (both line numbers appear in the claim text) is necessary but not sufficient; see C4.

**Limit conjunct:**
- A6: every call on the T→O chain is cited, or is listed in `scope` as an assumption. Failing A6 limits the row; it does not reject it.

**Citation rule:** each range lies inside one function of the sha256-pinned bytes. Whole-file ranges do not count.

**Required controls (KQ20's identity-control principle, `corpus/QUALITY.md:121`: "with an unfaulted identity control on the same rows that must pass (so a reject-everything gate cannot score)"):**
- an accept arm that passes A1-A5;
- the accept arm minus exactly the reset writer, which must fail;
- the historical negative S043, which must fail.

## Node set derived at 704366d76 (pinned bytes)

- **T's effect.**
  - `server.cpp:37` "shutdown_handler(signal);"
  - → `:519-523` (`:522` "ctx_server.terminate();")
  - → `server-context.cpp:4798` "impl->queue_tasks.terminate();"
  - → `server-queue.cpp:134` "running = false;"
- **O.** `server.cpp:590` "return 0;" is reached only when `ctx_server.start_loop()` (`:576`) returns.
  - The outer loop's only exit is `server-queue.cpp:301-302`: "if (process_new_tasks(false)) {" … "break; // terminate".
  - That exit needs `:143` "return true;" under `:141` "if (!running) {". So (c) = 141.
- **Full-set search for `server_queue::running`.** String literals were stripped, and accesses were assigned to their owning class.
  - Writes:
    - `server-queue.h:18` "bool running  = false;"
    - `server-queue.cpp:134`
    - `server-queue.cpp:279` "running = true;"
  - Reads: 141, 196, 322, 337, 339, 355.
  - `server_response`'s own `running` (`server-queue.h:156`, `server-queue.cpp:507`) is a different member and is excluded.
- **`h:18` runs before arming.**
  - `server.cpp:213` "server_context ctx_server;"
  - → `server-context.cpp:4785` "server_context::server_context() : impl(new server_context_impl()) {}"
  - → `:957` "server_queue    queue_tasks;"
  - All of this precedes arming at `server.cpp:534` "sigaction(SIGTERM, &sigint_action, NULL);".
- **Result:** (d) = {134, 279}. Line 279 undoes 134, so the window is [`server.cpp:534`, `server-queue.cpp:279`].

# 2. Application to the S043 admit and to S047

| Conjunct | S043 (`corpus/SOURCES.md:55`) | S047 (`corpus/SOURCES.md:59`) |
|---|---|---|
| A1 arming + handler | pass — "`signal_handler` lines 26-38"; "`sigaction` for SIGINT and SIGTERM 529-534" | pass — "`signal_handler` 29-38 (statics 26-27), handler install 529-534" |
| A2 outcome 590 | pass — "`return 0;` at 590" | pass — "`return 0;` 590" |
| A3 deciding read 141 | **FAIL** — the only loop citation is the call site "`start_loop` 575-576" | pass — "tests `if (!running)` at 141-143" |
| A4 writers 134, 279 | **FAIL** — "`tools/server/server-queue.cpp` `terminate()` 132-136" covers 134; nothing covers 279 | pass — "`start_loop()` sets `running = true` at 278-280" plus "`terminate()` 132-136 sets `running = false`" |
| A5 window named | **FAIL** — `teaches` "A first SIGTERM after the handler is installed ends in `return 0`". Gate `corpus/lessons/round-17.md:62` says "admit, scoped (S043)", but `.ufo/waves/round-17/falsify/advice/ReopenS043.md:54` notes it is "scoped only in prose" | pass — `teaches` "one delivered after install (534) but before `start_loop` resets `running` (279) is lost"; `scope` "including the window between handler install and task-loop start" |
| A6 assumptions | limit — uncited: `server-context.cpp:4792-4799`, `server.cpp:483-491`/`579`/`122-124`, `main.cpp:3-5`; no assumption list | limit — uncited: `server.cpp:519-523`, `server-context.cpp:4792-4799`, `server.cpp:483-491`/`579`/`122-124`, `main.cpp:3-5`; no assumption list |
| **Verdict** | **REJECT** (A3, A4, A5) | **ADMIT on A1-A5; LIMIT on A6** |

- S043 is rejected on exactly the node the re-open seat found: `ReopenS043.md:33` "True only once `start_loop()` has executed `running = true` (`server-queue.cpp:279` "running = true;")."
- S047's `teaches` is a necessary condition ("a first SIGTERM ends in `return 0` only once `start_loop` is running"), and the cited lines support it.

# 3. Controls

How I ran them: in-memory Python. The S043/S047 cells were parsed from `corpus/SOURCES.md`, and the nodes come from the pinned bytes. No file was written.

Columns A1-A6 below show each case's results in order (P = pass, F = fail).

| Case | A1-A6 | Verdict | What it shows |
|---|---|---|---|
| S043 | P P F F F F | reject | the historical negative fails |
| S047 | P P P P P F | admit (A6 limit) | an accept arm exists, so the test is not reject-everything |
| C1: S047 with "278-280" and "(279)" removed | P P P F F F | reject | the targeted conjunct (A4) is load-bearing; the M8 mutant is killed |
| C2: S043 plus the lane's own round-17 pins `start_loop` 278-366 and `process_new_tasks` 138-161, `teaches` unchanged | P P P P F F | reject, **only by A5** | "read and cite the functions" alone would pass M8's defect |
| C3: S043 `teaches` with whole-file ranges, one-function cap on | F F F F F F | reject | — |
| C3u: same as C3, cap off | P P P P F F | A1-A4 pass trivially | the range cap is necessary |
| C4: C3u plus "Lines 534 and 279 were read." | P P P P P F | admit (A6 limit) | the A5 token proxy is gameable; A5 must be a human, non-author reading |
| C5: S047 plus 519-523, 483-491, 579, 122-124, 4792-4799, `main.cpp` 3-5 | P P P P P P | admit | A6 can be satisfied |

C2 is not hypothetical. At commit `54a2926`, the same commit that wrote the S043 admit at `corpus/lessons/round-17.md:62`, `.ufo/waves/round-17/sources/pins.json` already pinned two functions verbatim:
- `server_queue_start_loop` `[[278, 366]]`, containing "running = true;";
- `server_queue_process_new_tasks` `[[138, 161]]`, containing "if (!running) {".

Commands: `git show 54a2926:…pins.json` parsed for both pins, and `git log -S'| S043 |'` → `54a2926`. So the bytes had been read and pinned, and M8 still happened.

# 4. Review of the drafted KQ23 (`quality-kq23.md`, sha `4f5fd183…`)

## F1 — High: no accept arm

- At `quality-kq23.md:15` the draft limits S047: "Applied as written, KQ23 also limits S047 (`corpus/SOURCES.md:59`), which cites 7 of the 12 nodes."
- No row is shown to pass, so the demonstration cannot tell KQ23 apart from a reject-everything rule. That is the failure KQ20 forbids (`QUALITY.md:121`).
- The S043 rejection is confounded. S043's misses include `server-context.cpp:4792-4799`, `server-queue.cpp:299-303` and `main.cpp:3-5`, and S047 misses those same nodes. So the rejection does not show that the M8-specific node (279) is what fails S043.

## F2 — High: the literal wording can't be satisfied, not even by the draft's own path

- `quality-kq23.md:11` requires the path "has been read at the pinned bytes and every function on it cited". Its printed path (`:13`) lists callee bodies such as `server-context.cpp:4797-4799`, yet it still leaves out functions that are on the path:
  - the callee of `server.cpp:520` "mcp_mgr.shutdown();", which runs before `terminate()`. The range `519-523` covers only the call site; the body is neither pinned nor cited;
  - `:578` "clean_up();" and its body `483-491`, absent entirely;
  - `:579` "ctx_http.join();", absent entirely.
  - (`:123` "common_log_flush(common_log_main());" is inside the printed `server.cpp:94-125` node, but the counted set drops that node; see F3.)
- Its clause "each write and each read of any flag or state the path depends on" fails S047 on several counts:
  - S047 cites 1 of the 6 reads of `running` (141; not 196, 322, 337, 339 or 355), and does not cite the `h:18` write.
  - `mutex_tasks` (`server-queue.h:30` "std::mutex mutex_tasks;") is state the handler depends on (`server-queue.cpp:133`), and no row cites it.
- Read literally, every row is limited (reject-all). Applied selectively, the applier's chosen list decides the outcome.

## F3 — Medium: node counts can't be reproduced

- The printed path has 11 nodes, including `server.cpp:94-125`. Against it, S043 covers 4 of 11 and S047 covers 5 of 11.
- "6 of these 12" (`:13`) and "7 of the 12" (`:15`) only come out with a set the draft never lists: drop `94-125`, add `529-534` and `575-576`. I computed both counts.

## F4 — Medium, keep and generalise

- "including the write that resets it" (`:11`) and "cites a flag's write without the reset that can undo it" (Reject cell) are the conjuncts that catch M8. Keep them.
- Generalise them to "every post-arming write, found by full-set search", and add the A5 window rule. S047 passes both.

## F5 — Low

- The draft's path starts at `main.cpp:3-5`, which is not in `pins.json`. That conflicts with its own "read at the pinned bytes".
- Either pin `main.cpp` (sha `7ec68458…` above) or stop the path at `server.cpp:122-124` (pinned as `entry_return_propagates_status`).

# 5. Blind application beyond the motivating case

I applied the test to text that has not been reviewed yet, to check it can fail on something other than the case that motivated it.

## B1 — Medium: `s047-gate.md:13` overstates S047

- The draft admits "A first SIGTERM delivered after `start_loop()` begins ends the process with `return 0` | admit, scoped (S047)".
- That is a sufficiency claim. S047 makes only a necessary one ("only once `start_loop` is running").
- Under A6 it is limited by load-bearing nodes it does not cite:
  - `server.cpp:520` `mcp_mgr.shutdown();` (body not read);
  - `server-queue.cpp:133` "std::unique_lock<std::mutex> lock(mutex_tasks);";
  - after the loop, `server.cpp:578-579`;
  - for "ends the process", `server.cpp:122-124` → `main.cpp:4`.
- The handler can run on a thread that already owns `mutex_tasks`:
  - signal(7), https://man7.org/linux/man-pages/man7/signal.7.html: "If more than one of the threads has the signal unblocked, then the kernel chooses an arbitrary thread to which to deliver the signal."
  - Lock sites: `server-queue.cpp:29` (post), `:140`, `:321`.
  - No signal masking appears in the pinned server files (grep for sigmask/sigprocmask/SIG_BLOCK found nothing).
- When that happens, the outcome is undefined:
  - https://en.cppreference.com/w/cpp/thread/mutex/lock: "If lock is called by a thread that already owns the mutex, the behavior is undefined: for example, the program may deadlock."
  - https://man7.org/linux/man-pages/man3/pthread_mutex_lock.3p.html Relock column: "DEFAULT │ non-robust │ undefined".
- [INFERENCE] I did not reproduce this at runtime.
- Suggested fix: phrase row 1 as a necessary condition, or list the assumptions.

## B2 — Low: the round-17 knowledge correction has the same overstatement

- `corpus/knowledge/llamacpp-loading-lifecycle.md:214-215`: "That holds once `start_loop` is running".
- This is committed text, so it needs an appended correction, not an edit.

## B3 — Low: S047's `used-by` is incomplete

- S047's `used-by` is only `corpus/lessons/round-17.md`, but `corpus/knowledge/llamacpp-loading-lifecycle.md:218` cites "(S047, supersedes S043; static ordering, not reproduced)".
- `/home/vgpnk/Projects/shokunin/CORPUS.md:107` says: "`used-by` — repo-relative paths of the knowledge entries or lessons citing the row".
- `used-by` can be changed in place (`CORPUS.md:116`), with the old→new change logged in the round lesson.
- Until it is fixed, a KQ23 check that combines a row with its `used-by` entries misses this knowledge entry.

# 6. What would make the criterion unfalsifiable

- **U1 — "Read" proven by having the bytes.** Evidence that bytes were fetched or pinned (pins, "read at the pinned bytes") passes rows whose claim ignores a writer they cite. C2, with the commit-`54a2926` pins, shows this. Require the claim to account for each writer (A4 + A5).
- **U2 — "Whole" without a closure rule.** If the applier lists the nodes, the outcome is whatever they list: literal "whole" limits everything, and selective use is arbitrary (F2, F3). Derive the node set by (a)-(d).
- **U3 — Unbounded ranges.** Whole-file ranges cover every node (C3u). Cap each citation to one function.
- **U4 — "scoped" without a named window.** S043's "admit, scoped" absorbed the counterexample (`round-17.md:62`; `ReopenS043.md:54`). Under A5, a scoped decision that names no window counts as unscoped.
- **U5 — A token-only window check.** C4 passes by mentioning "534 and 279". The question "does `teaches` assert the outcome inside the window?" stays a human judgement (KQ14), and should come from a non-author sample. `round-17.md:311` says "still no non-author admit/reject sample".
- **U6 — Only the hindsight case.** Showing the rule fails on S043, with the already-known line 279, cannot fail the criterion itself. It also needs the accept arm (S047), the targeted mutant (C1) and one blind application (B1).
- **U7 — Self-labelled applicability.** If KQ23 binds only rows that call themselves "code-derived", a row escapes by dropping the label. Make applicability mechanical: `kind` = code plus a trigger→outcome `teaches`.
- **U8 — No semantic floor.** The handler calls library functions that are not signal-safe:
  - `server.cpp:33-34` fprintf/`exit(1)`;
  - `:37` → `server-queue.cpp:133` mutex.
  - https://en.cppreference.com/w/cpp/utility/program/signal lists as undefined: "call to any library function, except for plain lock-free atomic operations and the following signal-safe functions".
  - Without a stated floor (for example "glibc/libstdc++ behaviour assumed"), every signal claim either dies on undefined behaviour (reject-all) or silently ignores it. Each of these signal claims needs a stated floor.
- **U9 — Citations that `used-by` doesn't reach.** If knowledge-entry citations count but `used-by` can't reach them (B3), a mechanical check of a row plus its `used-by` entries can't evaluate them.

# 7. Suggested KQ23 row (advice; L1 decides)

| KQ23 | A code-derived behavioural claim (`kind` code; its `teaches` states what a trigger T — signal, request or call — leads to) is admitted only when the row, or a knowledge entry in its `used-by`, cites at sha256-pinned bytes, each range inside one function: (a) the statement arming T and the handler body; (b) the outcome statement; (c) the read that selects the branch toward the outcome after T; (d) every write to the state that read tests which can run after T is armed, found by a full-set search of the pinned files (count first, KQ9); a write completed before arming is excluded with its reason. When a write in (d) can undo T's effect, `teaches` names that window by its two cited statements and says what happens inside it (a non-author reading). Calls on the T→outcome path that are not cited are listed in `scope` as assumptions; without that list the claim is limited, not admitted. Shown both ways at 704366d76: S043 fails (c) `server-queue.cpp:141`, (d) `:279` and the window; S047 passes (a)–(d) and the window, limited on assumptions; S047 without 278-280 fails (d). | Bytes were pinned or read but the claim ignores a cited writer (round 17 pinned `start_loop` 278-366 in `54a2926`, the commit that admitted S043); a range spans a whole file or several functions; the applier picks the node set instead of (c)–(d); a `scoped` decision names no window; a live run that never lands in the window is offered as verification; the only demonstration is the motivating case; a sufficiency claim rests on a necessary-condition row. | `lessons/round-17.md` M8 (line 309); `lessons/round-17-verifier-spotcheck.md` §5 R2; `.ufo/waves/round-17/falsify/advice/ReopenS043.md` |

# Limitations

- Everything here is static. No llama-server was run, so the window (A5) and the deadlock in B1 are not reproduced [INFERENCE for runtime consequences].
- The A5 proxy and the citation extractor are heuristics over prose cells. I hand-checked their output against the quoted cells:
  - The extractor picked up two harmless spurious lines (S043 "15" from "-15"; S047 "17" from "round-17"). Neither is a node.
  - S047's `teaches` "(279)" names no file; the file comes from its anchor.
- (c) requires only the deciding read (141). Reads 322/337/339/355 just wake the loop and send control back to 141, and 196 is the worker thread's read. A stricter applier could demand them; that would be F2 again.
- `mcp_mgr.shutdown()`, `server_stream_session_manager_stop()`, `ctx_http.stop()/join()` bodies are not pinned and were not read. They are listed as uncited, not judged.
- The cppreference and man7 pages are current pages accessed 2026-10-20, not pinned revisions.

# Commands run (all exit 0 unless noted)

- `sha256sum server.cpp server-queue.cpp server-queue.h` (pinned dir) and `wc -l`.
- `curl -sS …/704366d7…/tools/server/main.cpp | cat -A -n` and `| sha256sum`.
- `git -C <lane> log --format=… -- .ufo/waves/round-17/sources/pins.json`; `log -S'server_queue_start_loop'`; `log -S'| S043 |'` → 54a2926; `log -S'| S047 |'` → 5e9ae6e.
- `git -C <lane> show 54a2926:…/pins.json | python3` (pins present: True/True).
- `git -C <lane> diff --quiet master -- …/pins.json` → 0.
- `curl` man7 signal(7), signal-safety(7), pthread_mutex_lock(3p) and cppreference signal and mutex/lock pages, piped to python3 text extraction.
- In-memory Python (eval kernel) for the node set, the full-set search, the conjuncts and controls C1-C5, and the draft sha256s. No files were written.

# Installs and scratch

- Installs: none. No pacman, uv, npm or cargo action.
- Scratch: none. No `/tmp` files and no clone; no server was started and no port was bound, so no teardown was needed.
- The only file written is this Report.

# Addendum — the revised draft (`quality-kq23.md` sha256 `0cacdbcbe07da7a4…`, 42 lines)

I re-read the draft after the scribe's IRC note. Its arm A admits M8's overclaim when the row cites the lane's own pins, and its B accept control fails B's own wording (R-A1, R-B1).

## Resolved

- **F3.** There is now one 15-node list, and both counts reproduce:
  - S043: 6/15 (N03, N04, N06, N07, N08, N15)
  - S047: 7/15 (N03, N06, N07, N08, N10, N11, N15)
- **F1, partly.** Arm A now isolates the deciding set: "S047 cites N06, N10, N11 and the window endpoints (N07, N08), so **S047 meets A**", and S043 fails A.
- **F2, partly.** N13 `clean_up` 483-491 and N14 578-579 were added, and `mcp_mgr.shutdown()` is now named as unread.

## Remaining

### R-A1 — High: arm A checks citations only, and admits M8's defect

- Its Reject cell reads: "A is not met when a row cites the outcome and the handler but omits a read, a post-arming write, or the window's endpoints."
- Control C2 keeps S043's `teaches` unchanged and adds the `54a2926` pins (`start_loop` 278-366, `process_new_tasks` 138-161). It then cites the read at 141, the writers 134 and 279, and the endpoints 534 and 279, so it **meets A** (computed: read, writers and endpoints all True).
- The draft then says "A row that meets A and fails B is limited to its A claim: the deciding-set claim stands", which keeps the overclaim.
- Fix: move "the 'scoped' label does not name the failing window" from B into A, and apply it to `teaches`/`scope`, not to the Gate label. The claim text must name the window and state the outcome inside it.

### R-A2 — High: "every read" has a literal reading that fails S047

- "Every read of the state that decides the outcome" can be read literally.
- Read that way, S047 fails A: it cites only 141 of the six reads (141, 196, 322, 337, 339, 355), so arm A again has no accept row.
- Fix: "the read that selects the branch toward the outcome".

### R-A3 — Medium: the "full-set" search covers only one file

- The draft says "a full-set search of `server-queue.cpp` for `running` finds exactly these two writes".
- Across the pinned files there are three. `server-queue.h:18` "bool running  = false;" is excluded only because it runs before arming (`server.cpp:213` → `server-context.cpp:4785`, `:957`).
- Fix: search all the pinned files and record that exclusion.

### R-B1 — Medium: the 15-node accept control does not meet B's wording

B says "Every function on the path … is cited … or is listed as an unread callee". The 15-node list misses:

- **Functions on the path in pinned files:**
  - `server_queue::worker_stop` (`server-queue.cpp:209-220`, called at `:365` after the loop exit; `:219` "worker.thread.join();");
  - `server_http_context::stop()` (`server-http.cpp:548`) and `join()` (`:556`) — only their call sites, 487 and 579, are cited;
  - `server_context::get_llama_context` (`server-context.cpp:4801`, called at `server.cpp:584`).
- **Callees outside the pinned files, not listed as unread:**
  - `server_stream_session_manager_stop()` (`server.cpp:486`)
  - `llama_backend_free()` (`:490`)
  - `common_memory_breakdown_print()` (`:586`)
  - `common_log_flush()` (`:123`)

"The rule is a set containment over the list" replaces B's wording with the list the applier chose (U2). Two possible fixes:

- State B's closure — for every call in a cited body on the executed path, cite the callee's body if it is pinned, otherwise list it as unread — and generate the list from that closure.
- Or turn B into a disclosure obligation, kept in a path ledger that the row or Gate references.

### Minor

- The window is declared as "[534, 279]", but its endpoints are given as "(N07, N08)". N08 is the 575-576 call; the :279 endpoint is N10.
- N01 `main.cpp:3-4` is still outside the pinned directory the draft names (F5).

## How I checked

- In-memory recomputation of the 15-node coverage, and of arm A under both readings of "every read":
  - deciding-read reading: S043 F, S047 P, C1 F, C2 **P**;
  - every-read reading: S047 F, C2 F.
- Read of `server-queue.cpp:209-220` and `:365`.
- grep for `server_http_context::stop`/`join` in the pinned `server-http.cpp`.
- No files were written apart from this Report.

# Addendum 2 — the second revision (`quality-kq23.md` sha256 `958fe11a1a65acfc…`, 35 lines)

I re-read the draft after the scribe's second IRC note and re-derived its closure list from the pinned bytes. I found no further High defects. Two Low findings and two items stay open for L1.

## Every first-round finding is now resolved

- **F1.** Arm A(i) binds the claim text: "The claim text (`scope` or `teaches`) names the window by two endpoints, each cited by line, and states the outcome inside it." Control C2 (S043's unchanged `teaches` plus the `54a2926` pins) now fails arm A(i), because it never states an outcome inside the window.
- **F2/R-A2.** Arm A(iii) is now "The read that selects the branch toward the outcome is cited", and the application names `:141-143`.
- **F3.** The single node list is gone; arm B's list is generated by a closure rule, and both applications are on the record.
- **F5/R-A3.** Arm A(ii) searches "every pinned file", and the exclusions are named: `server-queue.h:18` initialiser, `:507`/`h:156` `server_response`.
- **F5.** `main.cpp:3-4` is now labelled "[URL; not in `pins.json`]".
- **R-B1/U2.** Closure C expanded `worker_stop` (`server-queue.cpp:209-220`), `worker_loop` (`163-207`), `process_new_tasks` (`138-161`), `stop`/`join` (`server-http.cpp:548-554`, `556-567`) and `get_llama_context` (`server-context.cpp:4801-4803`), and names the unread callees.

## Spot-checks of closure C against the pinned bytes

- Boundary anchors: `server-context.cpp:1557-1559` ("queue_tasks.on_new_task"), `:1560-1562` ("on_update_slots"), `:1563-1565` ("on_sleeping_state") — all correct.
- Boundary ranges: `process_single_task` starts at `:2821` ("bool process_single_task(...)") and ends at `:3191` ("return true;"); `handle_sleeping_state` (`:1064-1080`); `update_slots` (`:3256` "void update_slots()"); all consistent.
- `get_llama_context` (`:4801-4803`) returns `impl->ctx_tgt` and expands to nothing, as the draft says.
- `stop` (`server-http.cpp:548-554`) and `join` (`:556-567`) match; `:551` `srv->stop()` and `:564` `pimpl->pool->shutdown()` are correctly UNREAD (types not pinned).
- Full-set search of `running` over the other pinned files: only log strings and one comment. The writer set {134, 279} with exclusions {h:18, :507, h:156} stands.
- Verdicts reproduce: S043 fails A(i)-(iv); S047 meets A(i)-(iv); S047's B fails on the unlisted C elements.

## Residual (Low)

- **R-L1.** Applicability is now "a code-derived behavioural claim **about a window**". A windowless claim could dodge KQ23. Suggest "a code-derived claim that a trigger T leads to an outcome", which then defines its window when a writer can undo T.
- **R-L2.** "states the outcome inside it" stays a human judgement (by design; KQ14). Keep it with a non-author sample; `round-17.md:311` notes there is "still no non-author admit/reject sample".

## Still open for L1 (outside this draft)

- The committed `knowledge/llamacpp-loading-lifecycle.md:214-215` sentence "That holds once `start_loop` is running" still overstates S047's necessity claim as sufficiency; it needs an appended correction.
- The handler can run on a thread that already holds `mutex_tasks` (`server-queue.cpp:133`; lock sites `:29`, `:140`, `:321`). POSIX leaves that relock undefined ("DEFAULT │ non-robust │ undefined", pthread_mutex_lock(3p)). Arm B's closure cannot surface this, because primitives are "a named class not admitted as evidence". Any round-18 Gate row for S047 should keep the necessary-condition shape ("only once `start_loop` is running") or list this as an assumption.

## How I checked

- Read of the revised draft; sha256 `958fe11a…`; 35 lines.
- Read of the pinned ranges above; grep for `running` over `server.cpp`, `server-context.cpp`, `server-http.cpp`.
- No files were written apart from this Report.
