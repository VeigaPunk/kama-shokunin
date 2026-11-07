# Round 93 — frozen claims (kama)

Base revision `5af794958b0fc08f574aa2e67650282269549b02` (lane `master` at round start; `jj-lane.sh state`
ahead=0 behind=0 tracked=0 untracked=0). L1 `KamaR93` (holds the §3 planner seat). Frozen in the commit that adds
this file; nothing below changes after that commit. Every control named here was executed before this file was
committed; its receipt is committed with it under `.ufo/waves/round-93/controls/`.

Closure history read before declaring: `corpus/lessons/round-92-verifier-spotcheck.md` (r92 **rejected-honest-stop**:
C2 verified, C1 not verified — K2 fired on R01/R08 through wave-1 SC01; routed R1–R6), r91 rejected-honest-stop
(K2 on T07), r90 and r89 admitted, r88 rejected (MANIFEST). Both claims answer routed defects: C1 is round-92 wave-1
SC02 F6 (a load-dependent false green on the router model-file check, carried at base); C2 is R2 (superseding rows
for R01 and R08 under KQ149, every setter named or excluded, not prose only) and R3 (a counter shown able to fail on
the R01/R08 class before it counts).

Axes (SCORECARD `## Axes`): operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. Lowest
non-retired: depth / calibration / adjacency (7). C2 works depth.

## C1 — operability: the router model-file verdict does not change when entries repeat a model file

**Predicate (one sentence, same in counter docstring and receipt label):**
`python3 tools/round93-router-repeat.py --repo . --rev <M1> --work <scratch>` prints
`ROUTER_REPEAT cells=10 mismatches=0 positive_mismatches=0 probe=rev …` and exits 0 at the measured commit M1, the
counter's bytes identical to this freeze commit.

- Cells (counter docstring): a stub autoload router lists the expected model `good` as `unloaded` N times. R01–R04:
  every entry names one slow invalid GGUF (150 000 tensor infos, data truncated), N = 1, 8, 64, 2048 → each of 3 runs
  `MODEL_UNLOADED` / `router-model-invalid` within 20 s; R05: 64 entries through 33 path strings of that file (a
  symlink, `dir/` + `./`×k); R06: 64 entries `-m ok.gguf --mmproj slow.gguf`. Positive cells P01 (64× a valid file →
  `MODEL_OK` / `router-unloaded-autoload`), P02 (63× slow invalid then one distinct valid file → `MODEL_OK`), P03
  (64× missing → `router-model-missing`), P04 (missing then slow → `router-model-missing`); R01 and P cells are the
  `positive_mismatches` population (harm).
- Do-nothing control: base probe `controls/c1-base.out` (load 48: R02–R06 `MODEL_OK` / `router-unloaded-autoload` on
  all three runs, `mismatches=5 positive_mismatches=0`, exit 1; `controls/c1-base-v0.out`, the first run at load 21
  with a four-alias R05, had R02 green — the flip count moves with host load, which is the defect).
- Forgery and positive controls (`controls/c1-forgeries.py` → `controls/c1-forgeries.out`, `--probe-file`, print
  `probe=override`, can never meet the predicate): P0 the candidate drafted before freeze
  (`controls/c1-candidate-probe.sh`) passes 10/10; F1 fail-closed (an undecided candidate counts as bad) → P02 red;
  F2 memo keyed by the path string → R05 red; F3 a fresh 4 s deadline per file, no memo → R04 red; F4 only the first
  8 candidates checked → P02 red.
- Rule to implement (intent; the claim is judged only by the counter): `ROUTER_PY` parses one regular file once per
  call, keyed by its identity (device, inode, size, mtime), so repeats cost nothing and every candidate naming it gets
  the same state. Undecidable stays loadable (round-89 rule unchanged).
- Kill rules: K1 `positive_mismatches>0` at M1; K2 a harm suite regresses against `controls/harm-base.out`
  (`controls/harm.sh`: `tests/probe-verdicts/check.py`, `tools/test-snapshot.sh`, `round89-unloadable-cells.py`,
  `round90-hostile-answers.py`, operator router 1234 GET, `round91-answer-time.py`, `round92-linear-paths.py`), or the
  probe-bound round-90 reason receipt is not re-captured with identical triples (KQ148); K3 the counter changes after
  this commit.
- Disclosed limit (before data): a listing that names many *distinct* slow files still shares the one deadline;
  undecided candidates stay loadable by the round-89 rule. Held-out shapes are the wave's.

## C2 — depth (lowest axis, 7): every port and slot-count setter of the pinned llama-server named, R01/R08 superseded

**Predicate:**
`python3 tools/round93-setter-rows.py --repo . --rev <M2> --work <scratch>` prints
`SETTER_ROWS population=<n> rows=<n> bound=<n> unbound=0 missing=0 duplicates=0 fabricated=0 … derived_disagree=0
decisions=2 decisions_bound=2 … skill=rev` with n ≥ 40 and exits 0 at the measured commit M2, the counter's bytes
identical to this freeze commit.

- Population (frozen, mechanical): every line of `common/` and `tools/server/` (`*.cpp`, `*.h`, `*.hpp`) in the pinned
  b12177 codeload archive (sha256 `f50a52f4…`) matching the counter's `POP_RE` (48 lines at the freeze). Rows: `SKILL.md`
  `## Listen port and slot-count setters (round 93 revision)`, one P-row per population line (text = archive bytes,
  parameter, scope, condition, effect, value, source) and two decision rows R16 (port, supersedes R01) and R17
  (n_parallel, supersedes R08) whose overriding-row set equals the P-rows with effect `overrides` and whose decision
  names each. Derived checks for `common/arg.cpp` rows: the enclosing option block's first long option is in the
  condition and its `set_examples` list is the scope.
- Do-nothing control: base `rows=0 missing=48`, exit 1 (`controls/c2-base.out`).
- Forgery and positive controls (`controls/c2-forgeries.py` → `controls/c2-forgeries.out`, 12/12 as expected): P0 the
  candidate section (`controls/c2-candidate-section.md`, rows S600–S603 `controls/c2-candidate-sources.md`) binds 48/48
  and both decisions; V1 the round-92 R01/R08 decisions with no overriding rows → `decisions_bound=0` (the R01/R08
  class, closure R3); V2 a dropped preset row → `missing=1`; V3 a fabricated line → `fabricated=1`; V4 a wrong preset
  name → `derived_disagree=1`; V5 a wrong scope → `derived_disagree=1`; V6 a wrong value → `value-literal`; V7 the AIP
  override relabelled `copies` → R16 `overriding-set`; V8 altered text → `text`; V9 a preset left out of R17 →
  R17 `overriding-set`; V10 corrupt archive → exit 2. **Disclosed limit L1 (binds):** a trace string relabelled as an
  override and added to R17 binds — the counter cannot tell a string from an assignment; that, every non-`arg.cpp`
  condition and effect, and every decision's wording are the K2 reviewer read.
- Sourced: new rows S600 (`common/http.h`), S601 (`tools/server/server-connect.cpp`), S602
  (`tools/server/server-http.h`), S603 (`tools/server/server-models.h`), all @ b12177, opened this round; S593, S596–S599
  re-opened this round (digests equal, `controls/sources-opened.out`).
- Kill rules (any one → C2 not verified): K1 the counter changes after this commit; K2 a non-author reviewer finds a
  P-row whose parameter, condition, effect or value misstates its source line, or an R16/R17 decision that states a
  port or slot count for a start that another population row shows is set otherwise (reported per row); K3 a row cites
  a source not opened this round.
- Disclosed limit (before data): the population is a line pattern; a setter that writes the value through another
  name (struct copy, reference) is graded only through the rows its value passes. A non-author finding of such a
  setter that changes what R16/R17 state is K2.

## Separability, sources, carried defects

- C1's counter never reads `SKILL.md` or `SOURCES.md`; C2's counter never runs the probe. Either verifies with the
  other unlanded.
- Sourced claim: C2 (S600–S603 new; S593, S596–S599 re-opened).
- Carried from the r92 closure: R1 (`round75-instruments` `bad_rows=19`, L0 r87/r89 open) stays open, not claimed;
  R2 and R3 are C2; R4 (`json_array` quadratic path, C2-counter gaps CR01/MT01) routed to round 94 — round 93 takes
  SC02 F6 instead, a false green ahead of a constant-factor cost; R5 (report author date) — the report is authored
  after the final lane push; R6 (RV02 NOTE-1, R03 wording) carried.
