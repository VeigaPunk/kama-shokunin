VERDICT: confirm — M8→KQ23 chain is delivered with necessary-only wording; the S047 sufficiency overclaim was caught in-draft, fixed in the delivered Gate row, and disclosed, not hidden; residuals are Low and visible.

Seat: KamaR18.RevCriterion (revenger, round-18 FALSIFY, leaf). Reverse intent review: reconstruct the M8→KQ23 lesson and the reset-omission positive/negative controls, then decide whether claims were newly weakened appropriately or whether the delivery hides an S047 sufficiency overclaim.

# Method and bounds

- Read-only review. Scratch clone `/tmp/kama-r18-falsify-RevCriterion` cloned from the lane and switched to `seat/RevCriterion` at `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` (verified `git log --oneline -1` → `1c325b2 round-18: retain measured arms and repair counter classification seams`, exit 0). Measured production revision `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` inspected via `git show`.
- No edits to production/fleet/siblings, no jj/git writes in the lane, no ports bound, no listeners started, no installs (no pacman/uv/npm/cargo action), no environment dumps. Scratch removed at end; no seat-owned listener ever existed (command list contains no server/listener invocation).
- One in-kernel reproduction: KQ23 arm-A essentials re-derived from pinned bytes and applied to S043, S047, and a reset-omission mutant of S047.

# Findings

## F1 (High) — the mined chain is real and byte-grounded
- M8 as mined: `corpus/lessons/round-17.md:309` ("L1 cited a source row past what its lines prove", S043 `teaches` vs `server-queue.cpp:279`); the round-17 Gate had admitted "A first SIGTERM after handler install ends in `return 0` | admit, scoped (S043)" (`round-17.md:62`); the outside verifier row disagreed with the build-time admit and agreed with the S047 correction (`round-17-verifier-spotcheck.md:177`).
- Pinned bytes re-read by me (both fetched raw URL and clone copy `.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/`): `terminate()` 132–136 writes `running = false` at 134; `start_loop()` resets `running = true` at 279; deciding read `if (!running) {` at 141 inside `process_new_tasks`; `server.cpp` install `sigaction(SIGTERM…)` at 534, call `ctx_server.start_loop();` at 576, `return 0;` at 590. Every line the round-18 Gate rows cite is present verbatim.
- Delivered Gate rows: `corpus/lessons/round-18.md:41` admits "necessary ordering condition (S047; R1)"; `:42` rejects "Handler installed implies SIGTERM necessarily terminates with 0" with "An actual termination guarantee additionally needs locking/shutdown assumptions."

## F2 (High) — S047 is necessary-only, and the delivery says so consistently
- `corpus/SOURCES.md:59` `teaches` verbatim: "supersedes S043 — a first SIGTERM ends in `return 0` **only once** `start_loop` is running; one delivered after install (534) but before `start_loop` resets `running` (279) is lost…" — necessary shape, not a termination guarantee.
- Delivered s047-gate draft (`.ufo/waves/round-18/build/drafts/s047-gate.md`, sha256 `fa4e66e395fcf88c…`) row 1: "A handler-install → task-loop-start reset window **limits** first-SIGTERM claims | admit necessary ordering condition" — the draft's original sufficiency phrasing ("A first SIGTERM delivered after `start_loop()` begins ends the process with `return 0` | admit, scoped") is gone.
- Appended corrections use the same direction: `corpus/README.md:250-253` ("S047 supersedes S043's first-signal claim… it is not a sufficient guarantee"); `corpus/knowledge/llamacpp-loading-lifecycle.md:231-237` ("too strong if read as sufficient… Unexamined shutdown calls, mutex acquisition and platform signal behaviour still limit a general termination guarantee… a run observation, not a universal theorem").
- Delivered KQ23 (`corpus/QUALITY.md:132`) encodes it as a rule: "Necessary conditions stay necessary; a sufficient termination guarantee additionally names unexamined calls, locking and platform assumptions rather than silently assuming them away."

## F3 (High) — triad reproduces in-kernel (positive, negative, targeted mutant)
Applied KQ23 arm-A essentials (arming/handler, outcome, deciding read, every post-arming write incl. resets, window endpoints named, outcome stated inside the window) to the row cells (scope+anchor+teaches), with cited function ranges credited for writes inside them (`terminate()` 132–136 covers 134):

```
S043 (historical negative, expect REJECT) -> REJECT on: A1 handler body 29-38, A3 deciding read 141, A4 write@279, A5 endpoints 534+279, A5 outcome-in-window
S047 (positive control, expect ADMIT)     -> ADMIT
S047-mutant (reset-omission, expect REJECT) -> REJECT on: A4 write@279, A5 endpoints, A5 outcome-in-window
TRIAD (natural reading): PASS
```
- The mutant was built by deleting exactly the reset citation and window accounting from S047's `teaches` while retaining the conclusion; only the reset-related conjuncts flip, so the kill is attributable to the targeted conjunct, and S047 pristine passes (not a reject-everything rule — the KQ20/KQ23 control requirement).
- An early strict per-line extraction flagged S047 on "519-523 lambda" and "write 134"; the natural reading resolves both (134 is inside the cited `terminate()` 132–136 range; the 519–523 lambda is an arm-B closure element whose absence limits, not rejects — coherent with the delivered KQ23's own application paragraph, which records S047 as "meets A(i)–(iv), arm B not met" on `519-523`, `4792-4799`, `299-303`).

## F4 (Medium) — the draft overclaim is disclosed, not hidden
- The lesson states it outright: `corpus/lessons/round-18.md:77-78` "the first S047 Gate draft accidentally strengthened 'only once' into sufficiency. This lesson uses necessary wording."
- It was caught as a blind application of KQ23 to not-yet-reviewed text (`build/advice/RevKQ23FailCapable.md` §B1), which is exactly the non-hindsight control U6 demanded. First-draft shas are on record there (`4f5fd183…` draft, `fa4e66e3…` gate draft), and the delivered gate draft sha matches `fa4e66e395fcf88ce156e66234bb8300e2bde598de46c4564765bab752099a30`.
- Draft sha at tip: `958fe11a1a65acfc202feb6fcf0ed4414700062cd1b9058930414806e47e5f35` (quality-kq23.md) — matches the reviewer's Addendum 2, whose residual findings (R-L1 windowless applicability, R-L2 human-judgement A5, mutex relock UB) are Low/declined items, not defects in the delivered chain.

## F5 (Medium) — "pins ≠ possession" honesty is itself grounded
- `lessons/round-18.md:69-70`: "The source bytes were already pinned in round 17; merely possessing them did not catch the mistake."
- Verified: `.ufo/waves/round-17/sources/pins.json` at the S043-admitting commit `54a29268e208…` contains `server_queue_terminate` [132,136], `server_queue_process_new_tasks` [138,161], `server_queue_start_loop` [278,366] — all three ranges pinned when the overclaim was admitted. The counterfactual (KQ9/KQ6 reading alone would not have caught it) is stated with evidence.

## F6 (Medium) — append-only integrity holds around the correction
- `git diff 5e9ae6e..1c325b2e -- corpus/` has exactly one content deletion: the S047 row line, replaced in place. Cell-by-cell comparison shows only cell 10 (`used-by`) changed: `corpus/lessons/round-17.md` → `corpus/lessons/round-17.md, corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md`. All other cells byte-identical; `used-by` is a mutable cell per the registry contract, and the change is logged in the lesson ("Source bookkeeping: S047 used-by old → same plus…").
- S043's row is byte-identical across the round (verified). No `status`/`recheck`/immutable cell touched; `round-17.md` untouched (empty diff). This also repairs the reviewer's B3 (`used-by` could not reach the knowledge entry) — now it can.

## F7 (Low, residuals — visible, none hiding a sufficiency overclaim)
1. `knowledge/llamacpp-loading-lifecycle.md:214-218` retains the round-17 sentence "That holds once `start_loop` is running…" verbatim as historical text; the appended `:231-237` block explicitly overrides its sufficiency reading. Append-only convention; a reader must reach the append, but nothing is deleted or contradicted silently.
2. `tools/kama-llamacpp-live.py:120-129` (`teardown_graceful` documented_by) retains v2-era phrasing "…returns 0 — the documented graceful exit status". Pre-existing and unchanged by round 18 (lines 105–135 sha256 `a59db6e5…` identical at `5e9ae6e` and tip); the same cell bounds itself to "this shutdown code path plus the round-16 observed receipt, not on the Python row alone", and the negative-returncode branch fails. Wording-only residual.
3. No non-author admit/reject sample statement appears in the round-18 lesson or SCORECARD round-18 section; KQ23's "states the outcome inside it" remains a human judgement (KQ14 by design; reviewer R-L2 says keep with a non-author sample). The round-17 outside review exists, but KQ23 itself has not been sampled outside.
4. `corpus/QUALITY.md:125` header reads "(2026-10-20; outside round-17 R2/R4)" where the draft carried "(author-appended; no outside review yet)". The phrase means "motivated by outside R2/R4", but could be misread as outside-reviewed. Provenance is unambiguous from the lesson's routed-defects section; wording residual.
5. The mutex-relock undefined-behaviour hazard (`server-queue.cpp:133` lock inside `terminate()`; handler may run on a thread already holding `mutex_tasks`, no sigmask in pinned files) is not reproduced and is not in S047's row — correctly, since S047 is necessary-only and the Gate row 42 names "locking… assumptions" as what a guarantee would need. [INFERENCE] static only; no runtime reproduction occurred anywhere in the chain, and the lesson says so (`round-18.md:80`).

## F8 (Info) — the round applies its own KQ24 honesty to itself
The two official counting commands that could not evaluate are disclosed as exit-2 failures with regression routing, not laundered into pass (`lessons/round-18.md:139-146`). Consistent with the calibration claim's bounded shape (SCORECARD `:754-758` "not a claim of universal detector adequacy; fresh wave-2 mutants… reported separately").

# Answer to the review question
Claims are newly weakened appropriately: S043's unconditional first-SIGTERM claim is rejected on the exact node (the post-install reset and its deciding read), S047 is admitted only as a necessary ordering condition with the window named by its two cited endpoints and the outcome stated inside it, the reset-omission mutant fails while pristine S047 passes, and every layer that could carry a sufficiency reading (gate draft row 1, knowledge entry, corpus README, KQ23 text) either uses necessary wording or carries an appended correction that says the stronger reading is wrong. The one genuine sufficiency overclaim found in this round's drafts was caught by a blind application, fixed before delivery, and is recorded in the lesson. Nothing hides it. Residual limits (F7) are wording-level and visible.

# Commands and hashes
- `git clone -q <lane> /tmp/kama-r18-falsify-RevCriterion && git -C <clone> switch -q -c seat/RevCriterion 1c325b2e58…` → exit 0.
- Raw reads of pinned `server-queue.cpp` (132–136, 138–161, 270–290, 420–470, 494–515), `server.cpp` (525–600), via pinned clone copies and raw.githubusercontent at `704366d7…`.
- `grep 'running'` full-set over the five pinned server files: writes {134, 279} in `server_queue`; pre-arming initialiser `server-queue.h:18`; `server_response` members `:507`, `h:156` (different class, verified by reading the containing `server_response::terminate()`/`recv` bodies). Matches KQ23's exclusion list.
- `pins.json` extraction at `54a2926` (start_loop 278–366, process_new_tasks 138–161, terminate 132–136 present) → exit 0.
- In-kernel triad reproduction (python3, git show of S043/S047 rows at both commits, range-aware citation check) → TRIAD PASS output above.
- `sha256sum` drafts: quality-kq23.md `958fe11a1a65acfc202feb6fcf0ed4414700062cd1b9058930414806e47e5f35`; s047-gate.md `fa4e66e395fcf88ce156e66234bb8300e2bde598de46c4564765bab752099a30`.
- `git diff 5e9ae6e 1c325b2e -- corpus/` (7 files, +636/−1; the −1 is the S047 row's used-by rewrite) and `git diff 5e9ae6e 1c325b2e -- corpus/lessons/round-17.md` → empty.
- `POPEN_RETURNCODE_DOC` check: `tools/kama-llamacpp-live.py:60` cites `https://docs.python.org/3.14/…` (no `/3/` residual in tool or gate) → routed R6 item closed for the tool.
- No listener: no server, socat, nc or python socket-listen command was executed by this seat; nothing to tear down; scratch clone removed after writing this report.
