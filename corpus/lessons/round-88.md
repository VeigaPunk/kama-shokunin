# Round 88 — lesson (kama)

Base `9b4c7af16fdd4bba9e4815f4615f4b003f340747`; freeze `fb76e7f26d6582bd087935a00f8dc43af4db912f`
(`plans/round-88-claims.md`). Fresh-start round (run-15 amendment 46). Read first: the round-85, round-86
and round-87 verifier spotchecks (all `rejected-honest-stop`) and the round-83 closure (`rejected-harmed`).
Protocol re-read this round (r87 R9): `MISSION.md`, `AXES.md`, `LEARNING.md`, `CORPUS.md` §SOURCES.md
(fleet root), and this lane's `SCORECARD.md`, `PROVINCE.md`, `SKILL.md` verdict sections.

## Claims

- **C1 operability — llama.cpp router-mode readiness verdicts.** Before: the base probe graded every
  listed matching id `MODEL_OK`, including a model a router reports `unloaded` and refuses with
  `400 model is not loaded` (`.ufo/waves/round-88/controls/c1-base.out`, `mismatches=11` of 17 cells;
  `controls/pilot-live-1234.out`). After: `tools/kama-probe.sh` reads the matching entry's `status`
  object (S581). Counter `tools/round88-router-cells.py`, frozen at `fb76e7f2`.
- **C2 calibration — SCORECARD self-description vs repo state.** Before: the unedited round-42
  reconciler prints `mismatches=4 met=False` at base, three of the four caused by a duplicated live
  `calibration` row. After: one row per axis, pointer at the round-87 closure, round-88 canonical list.

## Gate

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S581 llama.cpp server README @ 704366d (b11755) | **admit** (A, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md — 2026-11-06, sha256 `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37` | "`llama-server` can be launched in a **router mode** that exposes an API for dynamically loading and unloading models." — line 1849, section "Using multiple models" | Primary docs at the exact commit of the pinned binary the counter runs; the status list (lines 2059-2121) grounds the verdict map; the live router child reproduced `unloaded`/`loaded` and the 400. |
| S582 llama.cpp server README @ master 954de24 | **reject** | https://raw.githubusercontent.com/ggml-org/llama.cpp/954de248ac6907dd05dc19f0f511ab18f2807a54/tools/server/README.md — 2026-11-06, sha256 `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137` | "The `status` object can be:" — line 2265 | Same status list as S581 but at a revision newer than the binary the lane runs; citing it would bind the verdict to text the pinned build was not compiled from. Flip: the pinned build moves past b11755. |
| `corpus/knowledge/router-mode-readiness.md` | **admit** | cites S581 + own-work receipts | — | New coverage ground (router mode was not on the coverage map); every row of its observation table is a committed receipt. |
| Round-87 C1 successor selector (`.ufo/waves/round-87/w1/out/EX01SelectorRepair/round87-rendered-cells.py`) | **reject** (not re-frozen) | — | — | Five consecutive rejected closures (r83–r87) on lane-authored prose selectors; each successor was falsified by the next round's probes. Flip: an operator ruling that a rendered-cell instrument is wanted, with an outside reference implementation (`cmark -t xml`) as the oracle rather than a lane selector. |

`status` / `recheck` / `used-by` changes this round: none on existing rows (S581, S582 are new).

## Mistakes

**M1 — five rounds on a self-referential calibration instrument.** Class: claim selection; a calibration
claim whose oracle is a lane-authored parser of the lane's own prose. Evidence: MANIFEST closures r83
(`rejected-harmed`), r84–r87 (`rejected-honest-stop`); r87 spotcheck §2 C1 ("successor passes its probe
battery but fails the frozen R4 population rule"). Captured-by: none — §9 claim sizing asks for a
do-nothing control but not for an oracle independent of the author. Fix this round: C2 counts mismatches
with an instrument last edited in round 64 (`tools/round42-selfdesc-reconcile.py`), byte-identical at base
and measured commit, and C1's live cells take their expected verdict from the serving runtime's own answer
(a real completion: 200 vs 400), not from lane text. Shown able to fail: `controls/c2-pointer-only.out`
(partial fix still `mismatches=4`) and `controls/c1-f1.out` / `c1-f2.out` (forged probes red).

**M2 — a reaped cache silently turned a green selftest red.** Class: prerequisite outside the repo.
Evidence: `controls/r78-selftest-before.out` (`LIVE_RECONCILE_SELFTEST pass=0 fail=4`, every arm
`pinned prerequisite absent: …/stories260K.gguf`); the gate at round start printed `round78-instruments
exit=1 FAIL`. Captured-by: the round78 selftest itself (exit 2 per arm, could-not-evaluate) — it caught
the absence but nothing restored it, and the SCORECARD `Retired` paragraph still cited the round-78
fixture reaching `MODEL_OK` as current. Fix: `tools/fetch-pinned-model.py` (sha256-pinned, refuses a
different file — `controls/fetch-refuse-control.out`); after it, `pass=4 fail=0`
(`controls/r78-selftest-after-fetch.out`).

**M3 — `MODEL_OK` on a listed, unloaded router model.** Class: readiness false green; a listing endpoint
read as a readiness endpoint. Evidence: `controls/pilot-live-1234.out`, `controls/c1-base.out` L01/L03.
Captured-by: none — `corpus/QUALITY.md` and the probe's v3 rule ("a model array must be present") treat
a listed id as served. Fix: C1 verdict rule; the decision row in `SKILL.md` §Round-88.

## Round-87 routed defects — disposition

| Defect | Disposition this round |
|---|---|
| R1 successor C1 re-freeze | Dropped, not re-frozen (Gate row 4; M1). |
| R2 `selfdesc` arm red | C2 makes the reconciler green at the measured commit with no instrument change. |
| R3 calibration cell stale on landing | C2 re-points the row to round-87. It goes stale again when the round-88 closure lands; that is the instrument's design (newest closure), not a defect of this round. |
| R4 `round75-instruments` `bad_rows=19` | Not worked; carried to `### Planned (round 89)` item 1. |
| R5 MT02 battery pristine `not-ok` | Not worked; carried (no round-88 claim depends on it). |
| R6 gate measured on a dirty tree | Round-88 measurements run at a committed, clean tip; receipts name the revision. |
| R7 no source-level reject | S582 rejected (Gate). |
| R8 trend grading | The report grades by LEARNING's table conditions. |
| R9 protocol re-read | Recorded at the top of this lesson. |
| R10 S580 `teaches` narrower than stated | Not worked (append-only row; a correction row needs a re-open of §4.5; carried). |
| R11 answering model per seat | Recorded from `w1-results.json` in the report when the orchestrator supplies it. |
