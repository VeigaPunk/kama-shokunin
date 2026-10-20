Append the following to the END of `corpus/README.md` (after the current last line, 245). Do not edit line 238 or any earlier line: corrections are appended, as the lane's §Correction blocks at lines 226-233 show.

## §Correction — round 18 (SIGINT/SIGTERM scope; routed by `lessons/round-17-verifier-spotcheck.md` R3)

Line 238's row credits "the SIGINT/SIGTERM shutdown path and exit statuses" to S043 alone. S047 supersedes S043 for one path only. A first SIGTERM delivered after the handler install (`server.cpp:534`) and before `start_loop` sets `running = true` (`server-queue.cpp:279`) is lost: the server keeps serving, and a later signal exits 1 (`server.cpp:33-34`). S043 still stands for the handler registration (`server.cpp:519-534`), for the second-signal `exit(1)`, and for the return-0 path once `start_loop` is running (`server.cpp:575-590`). Source: llama.cpp 704366d76, `tools/server/server-queue.cpp` (S047), accessed 2026-10-20. The window is a static ordering reading and has not been reproduced at runtime. Knowledge: `knowledge/llamacpp-loading-lifecycle.md` §Round 17 falsify correction.

## Round-18 coverage rows (provisional: keep a row only if its file is integrated by L1)

| Entry | Covers | Round |
|---|---|---|
| `knowledge/llamacpp-loading-lifecycle.md` §Round 18 | the first-SIGTERM window scoped in §Correction — round 18 above; the declared `kama-llamacpp-live/v3` receipt contract (`loading_envelope_graded` may be `passed: null` only when no loading 503 was observed; tool exits 0 pass, 1 false, 2 could-not-evaluate; gate exit 3 NOT-EVALUATED). Provisional: the contract is declared in the round-18 build spec and is not yet measured on the lane tip | 18 |
| `knowledge/loopback-listener-ownership.md` | how a Linux harness proves that a loopback listener belongs to its child, from `/proc/net/tcp` and `/proc/net/tcp6` LISTEN rows, the socket inode and `/proc/<pid>/fd` links, including the tcp6 host-byte-order address form. Provisional: exists only if L1 integrates the knowledge-ownership draft; that draft is not yet present under `build/drafts/` | 18 |
| `lessons/round-18.md` | C1/C2 gate decisions, the round-17 routed-defect dispositions R1-R3 as they land, and the round-18 mined mistake. Provisional: the file does not exist at lane tip `e75cf680b53484a61709ee1b2787d8dbc6419f74` | 18 |

Frontier disposition (provisional): the v3 receipt's live grading of a loading server on the pinned build is not yet run; the first-SIGTERM window is static only (not reproduced); the registered consumers remain unprobed, as in the round-17 paragraph above. Nothing in this round has yet been measured on the lane tip, so these rows state intent, not results.
