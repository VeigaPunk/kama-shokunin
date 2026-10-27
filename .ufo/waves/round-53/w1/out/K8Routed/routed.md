# K8Routed — routed-defect completeness, round 53 (attack+frontier wave)

Verdict: **no routed item is silently dropped.** Every R1–R4 item, both operator items, the three
orchestrator notes and the four SHONEN promotion boxes has either landed bytes in the build
(`c22602bd8d83ab26349d1087e916ca537ee4f9d1`), a live seat in wave kama-r53-w1, or an explicit
disclosed limit in the frozen preregistration. Two soft spots need L1 attention at integration so
they do not become silent drops at the measured commit: (a) the ed135b3c operator ruling must be
*forwarded* (lane cannot file L0 itself), and (b) the C1 carried limits must be re-stated in
SCORECARD §Round 53 / Planned (round 54) — the build discloses them only in the preregistration.

Method: read-only git over a `--shared` clone at `/fast/scratch/hyaku/kama-r53/K8Routed/lane`;
all file:line citations are from that clone (build `c22602bd`, base `4229ea1b`). No counter was run
(completeness review only). Wave outputs are not yet committed (wave in flight), so "wave seat"
rows name the dispatched seat from `.ufo/waves/round-53/w1/spec.json` / `build_spec.py`.

## 1. R1 — S505 wrong source anchor (round-52-verifier-spotcheck.md §6 line 134)

- **Routed to:** lane. Closure asked: append a correction, do not rewrite S505 in place.
- **What the build did:** answered exactly as asked.
  - `corpus/SOURCES.md:262` — new row **S509** "reject, corrected anchor (supersedes S505)":
    quote at line 491, `get_executable_path()` from 401, `ggml_backend_load_best` from 480,
    `GGML_BACKEND_DIR` 488–489, 7-word quote. S505 itself untouched (still says 422–439).
  - `corpus/lessons/round-53.md` Gate row for S509 (lines 20–21 of the lesson file).
  - Text copy `.ufo/waves/round-53/c1/ggml-backend-reg.cpp.b11909` (598 lines, in the build).
  - The closure's second half (seat S5Ggml's "21 words" miscount, captured-by-none) is queued in
    seat W1Mistakes' item (build_spec.py:159, mistake row 1).
- **Remains for integration:** lesson §Mistakes row (W1Mistakes), lesson §Errata R1 answer
  (W5Routed), a QUALITY row / anchor-sampling check so a wrong anchor fails something
  (scout S6Anchors dispatched this round), SKILL §Round-53 registry.
- **Silent drop:** no.

## 2. R2 — carried C1 limits (§6 lines 135–140)

Sub-item-by-sub-item against the frozen preregistration
(`.ufo/waves/round-53/preregistration.json` `limits`) and `measured/c1-build.out`:

| R2 sub-item | Round-53 build disposition | Evidence |
|---|---|---|
| libraries load by path (K2Design) | **CLOSED.** `code_mappings()` in `tools/kama-llamacpp-live.py:774` records every executable mapping; replay `verify_code()` hashes archive members from the stream; the counter reads `/proc/<pid>/mem` itself and compares with its own archive download. Receipt: 8 archive libraries byte-equal ×3 runs (`measured/c1-build.out` lines 5/8/11: libllama-server-impl.so, libggml-base.so.0.27.0, libggml.so.0.27.0, libggml-cpu-zen4.so, …). | lesson round-53 Claims; counter docstring "code the round-52 sealed leg, unchanged" |
| model load by path (K2Design) | **NOT closed — disclosed.** Prereg limit 3: "the model mapping (round-50 leg, path-bound) is not byte-compared." `measured/c1-build.out` contains no model byte comparison (grep `gguf|model` → 0 in the code lines). Round-52's `### Planned (round 53)` item 1 named "and for the model" (SCORECARD.md:3018); the build narrowed this at the freeze and the limit names it, so it is disclosed, not dropped. W5Routed's errata item explicitly asks which limits the build narrows vs keeps. | preregistration.json limits[2] |
| memfd from host install meets (J5HostMemfd); next reference counter-owned extraction | **NOT closed — disclosed.** Prereg limit 1: a replay whose bytes came from the host's byte-identical install "still meets … bytes, not provenance, are compared." The counter's own download is the reference, but identical bytes compare equal. Seat **J6HostMemfd** dispatched to confirm/refute and name what would distinguish it. | preregistration.json limits[0]; build_spec.py:99 |
| the download is not observed | **NOT closed — disclosed** (same limit 1). K1Cheat's round-53 seat re-argues the cheat shape. | preregistration.json limits[0] |
| `vm.memfd_noexec=2` hosts cannot run the replay | **Carried.** S502 basis unchanged; the round-53 counter still needs the memfd server (its `sealed` leg is the round-52 leg). Seat **S5Limits** scouts limits. | counter docstring lines 34–35; SCORECARD.md:3047 |
| round-50 carried: probe PATH execution, model bytes rewritten after mapping, kills during download/readiness | **Carried**, untouched by the build. S5Limits item includes them ("carried limits" scout). | build_spec.py:103 area |

- **Remains for integration:** SCORECARD §Round 53 "What `met=True` does not show" must carry the
  open sub-items verbatim, and `### Planned (round 54)` must name the survivors (witness of the
  replay's archive stream for provenance; model mapping compare). Until that lands, the limits
  live only in the preregistration — that is the one place a silent drop could creep in at the
  measured commit.
- **Silent drop:** none today; flag set as above.

## 3. R3 — C2 limits and mutation coverage (§6 lines 141–145)

All four round-52 C2 limits are properties of the **round-52 A-corr instrument**
(`tools/round52-append-restore-check.py`), which the round-53 build does not touch
(`git diff 4229ea1b..c22602bd --stat` lists only round-53 counters/tools).

| R3 sub-item | Round-53 disposition |
|---|---|
| restoration is byte retention, not visibility (HTML comment passes; K4Cheat) | **Carried.** Round-53 C2 is a different claim (cited paths). W5Routed errata must say "carried". |
| counter `exempt=` simpler than the tool's (L2Slice, 4 SCORECARD lines) | **Carried.** No change to the round-52 counter. |
| counter fixtures kill only 2 of 8 tool mutants (M5Fixtures) | **Carried.** No change. |
| `corr_lost` counts contract-graded lines only (K7Calib) | **Carried.** Seat **K7Calib** re-argues the framing this round. |

- The round-53 C2 claim adds its **own** disclosed limits (prereg limits 4–5): resolution means
  path-exists, not that the cited file says what the sentence claims; surfaces other than
  SCORECARD/SHONEN/SKILL are out of scope (K6Scope seat probing the latter).
- **Silent drop:** no; all four are round-52-instrument limits and stay answered by the W5Routed
  errata + lesson.

## 4. R4 — seat-report immutability instrument (§6 line 146)

- **Round-52 state:** Mistakes #8 (`corpus/lessons/round-52.md` row 8) — nine committed seat
  reports rewritten in place; `seat-report-immutability.py` planned, not landed.
- **What the build did:** nothing (no new tool in the build stat).
- **Wave:** seat **X9Immut** (build_spec.py:169) is turning the round-52 prototype into a
  lane-ready tool (`--repo --rev --rounds`, TMPDIR-honouring, exit 0/1/2, selftest with a scratch
  fixture, real run over rounds 46–52). This is also the unfinished half of round-52's
  `### Planned (round 53)` item 2 — the cited-path half landed as
  `tools/round53-cited-path-check.py`; the immutability half has no bytes yet.
- **Remains for integration:** land X9Immut's tool under `tools/`, register it in SKILL, add a
  QUALITY row, and put it in the regression battery. If X9Immut's output is not integrated, R4
  silently carries to round 54 — watch item.
- **Silent drop:** no seat missing; integration pending.

## 5. Operator item — ed135b3c restored canon (§6 line 147)

- **Routed to:** operator ruling (may withdrawn canon be held as restored history?).
- **What the build did:** nothing in lane files (LOG.md untouched by the build; the restored
  block still sits at `LOG.md:2358`, and `LOG.md:2428` records the reversal of round 51's
  disclosure choice).
- **Wave:** seat **Rv1Ed135** (revenger) reconstructs the five lines and drafts a one-line L0
  question `kama | round-53 | <question>` (build_spec.py:189); W1Mistakes rows it as mistake (3);
  W5Routed answers it in Errata.
- **Remains:** the L0 question must actually be *handed to the operator* — the lane cannot write
  the fleet root LOG. If Rv1Ed135's draft stops at the seat report, this item is dropped for the
  second consecutive round (round 52: "routed it only in its report and filed no L0 line").
  **This is the highest-risk open item.**
- **Silent drop risk:** real; L1 must surface the drafted L0 in the round report.

## 6. Operator carried L0 (§6 line 148)

- planner seat under the policy-v2 validator (`kama | round-39`); MISSION axes pair
  (`kama | round-35`); parked worktree (`kama | round-41..43`).
- **What the build did:** nothing (fleet-level items; lane build cannot and does not touch them).
- **Wave:** no seat re-opens them; W5Routed's errata item names "the carried L0s" so the round-53
  lesson keeps them visible.
- **Silent drop:** no — carried by design; lesson Errata is the integration checkpoint.

## 7. Operator promotion — SHONEN boxes (§6 lines 149–153)

All four boxes are still `[~]` in `SHONEN.md` at the build (lines 7–19); the build does not touch
SHONEN.md. Closure said boxes 1/2/4 look non-author-checkable, box 3 needs a non-author
fresh-session run.

| Box | Round-53 coverage |
|---|---|
| 1: gate `registered 50 … defective 0` + instrument registry | Wave seat **X6Battery** reruns the gate/battery at the build; SKILL §Round-53 instrument registry lands at integration (known item). |
| 2: three witnessed sealed-memfd replays (`measured/c1.out`) | Round-52 evidence persists committed; the round-53 counter keeps the sealed leg "unchanged, for EACH receipt" (`tools/round53-replay-code-audit.py:35`), and `measured/c1-build.out` shows `sealed=1 sealedruns=3/3`. No new witness seat — not required. |
| 3: fresh-session run, non-author | Seat **X4Fresh** dispatched this round (replay from docstrings only; names every lane-tree sibling needed) — directly closes the evidence gap the closure named. |
| 4: PROVINCE.md unchanged | Seat **Sc3Province** dispatched (adjacency/operability scout). |

- **Remains:** promotion decision is operator-owned ("I marked nothing" — round-52 closure). The
  L1 can present box 1/2/4 evidence plus X4Fresh's box-3 result in the round report; nobody seats
  the promotion itself, correctly.
- **Silent drop:** no.

## 8. Orchestrator notes (from the round-53 build_spec / dispatch)

### 8a. sealed_fd() selftest mutants M09/M10/M11 (survived round 52)

- Round-52 fact: `M3Live/c1-matrix.tsv` rows M09–M11 all `met=True` on the round-52 tree
  (M09 forges `file_seals` OSError → `return 15`; M10 forges `nlink=0`; M11 forges
  `seals = SEALS_ALL`; diffs in `round-52/w1/out/M3Live/diffs/`).
- **What the build did:** nothing to their target — `git diff 4229ea1b..c22602bd --
  tools/kama-llamacpp-live.py` touches only `code_mappings()` (new), `_code_mappings_selftest()`
  (new), `_selftest()` wiring, and main; `sealed_fd()` (:861), `file_seals()` (:853),
  `server_exe()` (:731) and `_server_fd_selftest()` (:1713) are byte-identical to the base.
  So the three mutants still apply verbatim and the round-52 `_server_fd_selftest` status quo is
  the question.
- **Wave:** seat **M4SealedFd** re-applies each mutant at the build, runs `--selftest`, writes
  killing selftest cases for any survivor (full text, fails-on-mutant/passes-on-pristine).
- **Remains:** integrate M4SealedFd's killing cases into the tool's selftest + QUALITY/lesson rows.
- **Silent drop:** no.

### 8b. kama-probe.sh /tmp under read-only /tmp (round-52 seat Sen2Scratch F1)

- **Already closed at round-52 integration:** `tools/kama-probe.sh:1128` —
  `TMP_ROOT=$(mktemp -d "${KAMA_PROBE_TMPDIR:-${TMPDIR:-/tmp}}/kama-probe.XXXXXX")  # round 52
  (seat Sen2Scratch): honour TMPDIR`. The build leaves it untouched.
- **Round-53 exposure check:** neither round-53 counter references kama-probe.sh (grep → no
  hits), and neither counter nor the two changed tools hardcodes `/tmp` (grep `"/tmp|/tmp/'` over
  `round53-replay-code-audit.py`, `round53-cited-path-check.py`, `kama-live-replay.py`,
  `kama-llamacpp-live.py` → no hits outside TMPDIR handling).
- **Wave:** seat **Sen2Scratch** re-runs the round-52 bwrap read-only-/tmp watcher against the
  round-53 C1 counter with TMPDIR pointed at the seat scratch — confirms the fix holds under the
  new counter.
- **Remains:** receipt integration only.
- **Silent drop:** no.

### 8c. provider exhaustion — record dead seats

- This is a process obligation, not bytes: when provider rate-limits kill wave seats, the L1 must
  record them (cf. fleet reports round-16/17 recording dead seats; round-52 w1-results.json
  format `seats 70, results 70`).
- **What the build did:** the dispatch registry exists (`.ufo/waves/round-53/w1/dispatch.json`,
  66 members, `counts {spawn:66, resume:0, total:66}`) as the bookkeeping mechanism; no seat is
  dead as of the build commit; no seat is tasked with it (correctly — it is the L1's).
- **Remains:** at WAVE-DONE the L1 writes w1-results + the round report and must record any dead
  seats there (name, provider failure, reseat or not). Nothing in the lane records
  provider-exhaustion deaths automatically.
- **Silent drop risk:** only if the L1 omits it at completion; flag for the end-of-wave report.

## 9. Cross-cutting integration checklist (so nothing above rots)

The following are the known integration items this review depends on; all are uncommitted as of
the build tip `bc8e6e7f`: SCORECARD §Round 53 + measured results + `### Planned (round 54)`;
LOG entry; QUALITY rows; README frontier; SKILL §Round-53 instrument registry; lesson
§Mistakes (W1Mistakes) and §Errata (W5Routed). The two items this review adds beyond the known
list: (1) **forward the drafted ed135b3c L0 question to the operator**, and (2) in §Round 53's
limits text, name the model-mapping compare and the archive-stream witness as the round-54
carries for R2 (per prereg limits 1 and 3).
