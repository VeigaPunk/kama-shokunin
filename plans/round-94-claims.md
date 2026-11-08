# Round 94 — frozen claims (kama)

Base revision `e6f1dccecbad6dea44a129dabc928822c458e824` (lane `master` at round start; `jj-lane.sh state`
ahead=0 behind=0 tracked=0 untracked=0). L1 `KamaR94` (holds the §3 planner seat). Frozen in the commit that adds
this file; nothing below changes after that commit. Every control named here was executed before this file was
committed; its receipt is committed with it under `.ufo/waves/round-94/controls/`.

Closure history read before declaring (fresh start under Amendment 58): `corpus/lessons/round-93-verifier-spotcheck.md`
(r93 **rejected-honest-stop**: C1 not verified — wave-1 SC02 showed the shared 4 s `ROUTER_PY` deadline still flips
`MODEL_OK` to `MODEL_UNLOADED` under synthetic host load; C2 not verified — K2 fired on P05–P07 labels and R16's
router-child clause; routed R1–R7), r92 rejected-honest-stop (K2 on R01/R08), r91 rejected-honest-stop. All three claims
answer routed defects and one new measured one: C1 is r93 wave-1 SC02 F1/F2/F3 (deadline-bound verdict still load-
dependent after the repeat memo); C2 is r93 verifier R2/R3/R7 in form (superseding rows and a counter that grades the
mechanism, not the wording) plus the M8 config.ini/cli-server gap; C3 is the new frontier-step curation with the S604
opening this round requires.

Axes (SCORECARD `## Axes`): operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. Lowest
non-retired: depth / calibration / adjacency (7). C2 works depth. C1 works operability (the lane's assigned axis pair
includes operability; freshness/calibration/adjacency stay at their recorded scores).

## C1 — operability: the router model-file verdict is stable under two host loads (per-file parse budget)

**Predicate (one sentence, same in counter docstring and receipt label):**
`python3 tools/round94-router-budget.py --repo . --rev <M1> --work <scratch>` prints
`ROUTER_BUDGET cells=<n> mismatches=0 positive_mismatches=0 load_cells=<k> load_stable=1 probe=rev …` and exits 0 at the
measured commit M1, the counter's bytes identical to this freeze commit. The counter grades the probe at two host loads
— natural and one synthetic `stress-ng`/`yes`-class CPU+IO load it applies itself — and requires the verdict on every
cell to be identical at both loads.

- Cells (counter docstring): the round-93 repeat battery plus the gap cells wave-1 CR01/MT01 routed (R05b hard links,
  P02 at 2048 candidates, same-basename/same-size/same-mtime collision pair, one entry naming one file twice, a
  two-invocation rewrite cell, an undecided-parse cell, 16 symlinks). Verdict expectation per cell is the round-93 rule:
  `MODEL_UNLOADED` / `router-model-invalid` for a slow invalid GGUF, `MODEL_OK` / `router-unloaded-autoload` for a valid
  one, `router-model-missing` for absent paths. The shared 4 s `DEADLINE` is replaced by a per-candidate budget: each
  `gguf_parse` call gets its own deadline slice (`MAX_STEPS` unchanged, wall-clock per file), so a slow file cannot
  consume the budget of later candidates; a candidate that exceeds its own slice stays `-` (undecided) and the
  round-89 rule "undecidable stays loadable" still applies per file, not per call.
- Do-nothing control: base probe `controls/c1-base.out` — the r93 counter's `positive_mismatches=1` reproduction under
  synthetic load (`w1/SC02ProbeVerdictSweep.md` F1) is the falsification this claim removes; the r93 counter itself is
  not re-run (it is frozen history).
- Forgery and positive controls (`controls/c1-forgeries.py` → `controls/c1-forgeries.out`, `--probe-file`, print
  `probe=override`, can never meet the predicate): P0 the candidate drafted before freeze passes every cell at both
  loads; F1 a per-call (not per-file) deadline → the synthetic-load cell red; F2 a memo keyed by path string → the
  hard-link cell red; F3 undecided counted as invalid → the valid-file positive cell red; F4 the deadline removed
  entirely → the hostile-header cell (r90 S587) red.
- Kill rules: K1 `positive_mismatches>0` or `load_stable=0` at M1; K2 a harm suite regresses against
  `controls/harm-base.out` (same suites as round 93: `tests/probe-verdicts/check.py`, `tools/test-snapshot.sh`,
  `round89-unloadable-cells.py`, `round90-hostile-answers.py`, operator router 1234 GET, `round91-answer-time.py`,
  `round92-linear-paths.py`, `round93-router-repeat.py`); K3 the counter changes after this commit.
- Disclosed limit (before data): a listing that names many *distinct* slow files can still exceed the wall-clock the
  counter allows per run (the counter's own 20 s cell budget, not the probe's); undecided candidates stay loadable by
  the round-89 rule. The claim is verdict stability across two loads, not a bound on total parse time.

## C2 — depth (lowest axis, 7): the setter sweep covers the config.ini route and the non-server entry points

**Predicate:**
`python3 tools/round94-setter-sweep.py --repo . --rev <M2> --work <scratch>` prints
`SETTER_SWEEP population=<n> rows=<n> bound=<n> unbound=0 missing=0 duplicates=0 fabricated=0 derived_disagree=0
entry_points=<e> decisions=<d> decisions_bound=<d> …` and exits 0 at the measured commit M2, the counter's bytes
identical to this freeze commit. The population extends the round-93 `POP_RE` line set with the `config.ini` route
(`common_params_apply_system_config`, `common/preset.cpp` `load_from_ini`/`apply_to_params`, `common/arg.h`
`operator<` argv-order) and the entry-point dimension: rows carry an `entry` cell naming which parsed program the row
governs (`llama-server`, `llama-cli` embedded server, router child, `llama-connect`, or `all common_params_parse`
callers), and the decision rows R18/R19 state the port and slot count per entry point, superseding R16/R17.

- Population (frozen, mechanical): every line of every `*.cpp`, `*.h`, `*.hpp` file under `common/` and `tools/` of
  the pinned b12177 archive matching `POP_RE` **plus** the config-route pattern (`load_from_ini`, `apply_to_params`,
  `apply_system_config`, `config.ini`, `fs_get_config_directory`, `operator<` in `common/arg.h`, `get_environment` in
  `tools/server/server-models.cpp`) **plus** the entry-point anchors (`cli-server.h` `start(`, `server.cpp`
  `server_role_detect`, `server-models.cpp` `update_args`/`get_environment`, `server-connect.cpp` `start(`). Rows:
  `SKILL.md` `## Listen port and slot-count setters (round 94 revision)` — P-rows for the round-93 population
  corrected per KQ151 (P05–P07 relabelled under a `declares-unregistered`-class label the section defines), new
  P-rows for the config-route and entry-point lines, and decision rows R18 (port per entry point, supersedes R16) and
  R19 (n_parallel per entry point, supersedes R17) whose overriding set equals the P-rows marked `overrides` for that
  parameter and entry point.
- Do-nothing control: base `rows=0 missing=<n>`, exit 1 (`controls/c2-base.out`).
- Forgery and positive controls (`controls/c2-forgeries.py` → `controls/c2-forgeries.out`): P0 the candidate section
  binds every population row and both decisions; V1 the round-93 table verbatim → `missing` on the new population and
  `decisions_bound=0` on R18/R19; V2 a dropped config-route row → `missing=1`; V3 a fabricated line → `fabricated=1`;
  V4 a wrong entry-point label → `entry-point` finding; V5 the argv-order rule omitted from R18's decision text →
  `decision-wording` finding; V6 a config.ini setter marked `unrelated` → `derived_disagree` or `label` finding.
- Sourced: this round opens S604 (`common/preset.cpp` @ b12177 — `load_from_ini`/`apply_to_params`/`operator<` order)
  and re-opens S596–S599, S600–S603 (digests equal, `controls/sources-opened.out`); the Gate block in
  `corpus/lessons/round-94.md` records URL, access date and ≤25-word located quote per row.
- Kill rules: K1 the counter changes after this commit; K2 a non-author reviewer finds a P-row whose parameter,
  entry point, condition, effect or value misstates its source line, or an R18/R19 decision that states a port or
  slot count for an entry point another population row shows is set otherwise (the config.ini route is first-class:
  a decision that omits it is K2); K3 a row cites a source not opened this round.
- Disclosed limit (before data): the population is a line pattern; a setter that writes the value through another
  name (struct copy, reference, env-var indirection inside `get_environment`) is graded only through the rows its
  value passes. The counter checks label membership and set equality, not prose truth — the K2 read is the semantic
  gate, as in round 93.

## C3 — calibration: the frontier-step census and lesson land with the round's own receipts

**Predicate:** the round's `corpus/SOURCES.md` census command
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` exits 0 at
the measured commit M3, `corpus/lessons/round-94.md` carries `## Gate` and `## Mistakes`, and the report's
Sources & frontier section pastes both census outputs (before: rows=343, exit 0 — `controls/census-start.out`;
after: rows=<n>, exit 0). This claim verifies the frontier step itself: at least one new S-row opened this round is
cited by a claim (C2's S604), at least one rejection is recorded with reason and flip, and one mistake is mined with
class · evidence · captured-by · fix.

- This is the calibration-axis move: the round's own self-assessment artifacts (SCORECARD planned rows, census,
  lesson) are re-derived by command, not asserted.
- Kill rules: census exit nonzero at M3; `## Gate`/`## Mistakes` absent; a new row's `opened`/`recheck`/`used-by`
  cells violate the census schema; the report omits either census output.

## Separability, sources, carried defects

- C1's counter never reads `SKILL.md` or `SOURCES.md`; C2's counter reads `SKILL.md` + `corpus/SOURCES.md` but never
  runs the probe; C3 reads only `corpus/` and the census script. Each verifies with the others unlanded.
- Sourced claim: C2 (S604 new; S596–S603 re-opened). C3 is the frontier step that carries the census.
- Carried from the r93 closure: R1 (`round75-instruments` `bad_rows=19`→`21`, L0 r87/r89 open) stays open, not claimed;
  R4 partially answered by C1's successor cells; R5 (report author date) — the report is authored after the final
  lane push; R6 (RV02 NOTE-1, R03 wording) carried; R7 answered by writing the terminal gate receipt outside the
  graded tree (`.ufo/waves/round-94/measured/gate-final.out` is committed before the report, and the receipt grades
  `--round 94` whose scope excludes the receipt path itself — see report).
