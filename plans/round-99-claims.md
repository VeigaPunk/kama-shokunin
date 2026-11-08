# Round 99 — frozen claims (kama)

Base revision `439fdb3d41b55e5b9e6d7c480d17f2c428bae978` (lane `master` at round start; round 98
closed `ok` — all three claims verified at `160e22dd`, expansion unchanged, quality/discernment
improved; `corpus/lessons/round-98-verifier-spotcheck.md`). L1 `KamaR99`. Frozen in the commit that
adds this file, the three instruments it names, the source rows and every freeze-time control, so
"the graded bytes are the freeze commit's bytes" is checkable rather than asserted.

Closure history read before declaring (the four most recent kama closures: r95 `ok`, r96
`rejected-honest-stop`, r97 `ok`, r98 `ok`, and the round-98 non-author spot-check's seven routed
defects). The standing failure class remains a frozen counter going green on a property NARROWER
than the claim's wording, with the falsifying artifact produced by the round's own wave. The
round-98 spot-check also routed concrete record defects (stale wave-seat counts, a miscalled fifth
seat, a mislabelled census sentence, an under-enumerated gate receipt and a lesson record outside
`## Mistakes`) that this round answers.

Axes (SCORECARD `## Axes`): operability 8, freshness 8, depth 7, coverage 9, calibration 7,
adjacency 7. Lowest non-retired: depth / calibration / adjacency (7). No stagnation waiver:
calibration and depth are below the 8 saturation line. **C1 works operability** (assigned axis),
**C2 works calibration** (lowest axis), **C3 works depth** (lowest axis). Claims are causally
separable: C1 reads only the two budget-counter files and its own fixtures; C2 reads only the lane's
record files, the round-98 results file, the gate receipt and the census script; C3 reads only the
probe and its own loopback stubs. No claim's verification needs another claim's fix.

## Receipts: freeze-time vs measurement-time

- **Freeze-time (committed with this plan):** `controls/census-start.out`, `controls/c1-before.out`,
  `controls/c1-candidate-mutant.out`, `controls/c1-positive.out`, `controls/c2-base.out`,
  `controls/c3-base.out`, `controls/c3-candidate.out`, `controls/counter-literal-scan.out`,
  `sources/s624-*.txt`, `sources/s625-*.txt`, `sources/s626-*.txt`.
- **Measurement-time (committed with M1/M2/M3):** `measured/c1.out`, `measured/c2.out`,
  `measured/c3.out`, `controls/c2-forged.out`, `controls/c3-regression.out`,
  `controls/census-end.out`.

## C1 — operability (assigned axis): the budget counter's control mode refuses a selected population it did not run

**Predicate (one sentence, same in the grader's docstring and in the receipt label):**

`python3 tools/round99-control-population.py --repo . --rev <M1> --work <scratch>
--counter tools/round99-router-budget.py` prints

    CONTROL_POP99 counter=tools/round99-router-budget.py drop=W14-900k-nd1 patch_removed=1
    selected=6 ran=5 mutant_cells=5 mutant_cells_ok=5 mutant_control_exit=1 mutant_ok=0 refused=1
    positive_cells=6 positive_exit=0 positive_ok=1 complete=1 met=True

and exits 0 at the measured commit M1 (the freeze commit, where the counter bytes live).

- **Before (the defect).** Round 98's control mode printed the number of cells it ran
  (`cells=16`) but never compared it to the selection: lesson M2 records the first control receipt
  of the repaired cell set printing `cells=16` after `W01-slow-x1` was dropped, with `ok=1` and exit
  0. The round-98 spot-check routed the counter-level fix (`n != len(selected)`) as still open.
  Reproduced at base: the round-98 counter with the `W14-900k-nd1` tuple removed from its cells list
  runs five of the six selected cells and prints `ROUTER_BUDGET98_CONTROL cells=5 cells_ok=5 …
  survived=1 ok=1`, exit 0 (`controls/c1-before.out`).
- **After.** `tools/round99-router-budget.py` computes `selected`, `ran` and `population_ok` in the
  control path and returns 0 only when the run set equals the selection. The same dropped-cell
  mutation reads `selected=6 ran=5 population_ok=0 … ok=0`, exit 1
  (`controls/c1-candidate-mutant.out`); the unmodified counter reads `selected=6 ran=6
  population_ok=1 … ok=1`, exit 0 (`controls/c1-positive.out`). The grader applies the byte drop to
  both counter files, reads them from `git show <rev>:<path>`, and prints the predicate line.
- **Mutation (one line, frozen):** remove the single cells-list line beginning `("W14-900k-nd1",`.
  Applied to a scratch copy through `tools/round99-control-population.py`; never to a tracked file.
- **Do-nothing control:** `controls/c1-before.out` — the round-98 counter's own control on the same
  mutation exits 0 (`cells=5 … ok=1`) and the grader prints `refused=0 met=False` exit 1 when run
  against it. A green base run means the population check cannot discriminate and the claim is void.
- **Kill rules:** K1 the graded counter/grader bytes change after the freeze commit; K2
  `met=False` at M1; K3 the round-98 predecessor also refuses the dropped-cell control (no
  before-measurement exists); K4 the unmodified round-99 counter refuses a complete population
  (`complete=0`, blanket refusal, not a gain).
- **Disclosed limits.** (a) The check compares counts, not cell identity: a cell replaced by a
  different cell of the same name count passes. (b) Only the six-cell `new` set is exercised; the
  17-cell `r97set` control keeps round 98's semantics plus the same count rule. (c) The natural
  19-cell predicate and every cell expectation are round 98's, unchanged in behaviour; this file
  adds no cell. (d) The grader mutates the counter's source text; it does not grade a counter
  handed a different cells list at run time. (e) The 19-cell natural pass is not re-run by C1 (it is
  C3's regression control at M3).

## C2 — calibration (lowest axis, 7): the lane's round-98 records agree with the committed wave evidence on twelve enumerated propositions

**Predicate:**

`python3 tools/round99-record-audit.py --repo . --rev <M2> --work <scratch>` prints
`RECORD_AUDIT99 checks=12 mismatches=0 met=True rev=<resolved>` and exits 0 at M2.

- **Before (the defect).** The round-98 spot-check routed five record defects: (1) `SCORECARD.md`
  and `LOG.md` say "10 reported, 2 dead" while `.ufo/waves/round-98/w1-results.json` carries 12
  results with non-empty outputs and lesson M3 records both named seats settling; (2) `LOG.md`
  credits "SB01-equivalent prose carried by the lesson" as the fifth building seat, and the
  SCORECARD attack list omits `RV03Intent`; (3) `corpus/lessons/round-98.md:28` labels the base
  census figures "at HEAD"; (4) the round-98 M3 record sits outside `## Mistakes`; (6) the gate
  receipt `PRE_REPORT round=98 arms=14 failed=6 uncommitted=1` names six failed arms and the
  round-98 erratum lists five, omitting `round-clean`. At base the frozen counter prints
  `mismatches=10` and exits 1 (`controls/c2-base.out`).
- **After.** Twelve checks over the appended round-99 corrections and the round-99 lesson:
  1–2 the SCORECARD and LOG correction blocks (after the stale lines) state **12 reported, 0 dead**;
  3 both name `SCORECARD.md:6431` and `LOG.md:4040`; 4 the text states **7 attack** and names the
  seven attack-role seats, and **5 non-attack** and names the five others — each population derived
  by the counter from the results file, not from the correction; 5 EX02BudgetControl is named
  against the `SB01-equivalent` misattribution; 6 RV03Intent is named; 7 the round-99 lesson states
  the census correction base `681c80a4` → 361 rows (A 344, B 11, C 6; mined 324, queued 8, rejected
  29) and round-98 tip `649bb2e9` → 363 rows (A 345, B 11, C 7; mined 325, queued 8, rejected 30);
  8 both groups re-derive with `scripts/sources-census.sh census` over `git show <rev>:corpus/SOURCES.md`;
  9 the gate verdict line and all six failed arms re-derive from the committed receipt and are
  named, `round-clean` included; 10 the round-99 `## Mistakes` section carries the round-98 M3
  `sampling` record; 11 the results file re-derives seats=12/results=12/dead=0 and the correction
  states `12 seats` and `12 results`; 12 the 7/5 split is the counter's derived population.
- **Do-nothing control:** `controls/c2-base.out` — 10 mismatches, exit 1 at base.
- **Forgery control (measurement-time):** `controls/c2-forged.out` — a scratch mirror whose
  correction states the old "10 reported, 2 dead" (and whose census sentence keeps the mislabel)
  must fail the same checks; run with `--tree <scratch>`.
- **Kill rules:** K1 the counter's bytes change after the freeze commit; K2 `mismatches>0` at M2;
  K3 the base control is green; K4 the forged correction passes.
- **Disclosed limits.** (a) Check 7's shape is a labelled base/tip regex over the lesson sentence;
  a different wording that omits the labels fails even if the numbers are right. (b) The counter
  grades the named propositions and the correction's values — it does not grade the fleet report
  (outside the lane repo) or prose outside the named surfaces. (c) The literal tokens
  `SCORECARD.md:6431`, `LOG.md:4040`, `SB01-equivalent` and the seat names are presence checks whose
  *values* are bound by checks 4/9/11's re-derivation; a correction could carry these tokens beside
  an unrelated true-sounding narrative. (d) The census rows change with round-99's own S624–S626
  append; the counter grades the two *frozen historical revisions*, never the tip.

## C3 — depth (lowest axis, 7): the probe's reason vocabulary separates an unread `/props` autoload flag from an explicit off state

**Predicate:**

`python3 tools/round99-autoload-states.py --repo . --rev <M3> --work <scratch>` prints
`AUTOLOAD_STATES99 cells=5 mismatches=0 base_mismatches=4 flips=4 stable=1 met=True rev=<resolved>
probe_sha256=<sha>` and exits 0 at M3.

- **Before (the defect).** The probe's `router_autoload()` returns success only for
  `{"role":"router","models_autoload":true}` and failure for every other outcome, so a `/props`
  that timed out, exceeded the 4 MiB cap, was not JSON, or carried no explicit autoload field is
  graded exactly like a router that answered `models_autoload:false`: `MODEL_UNLOADED` /
  `router-unloaded` ("check /props before sending POST /models/load"). Round 94's closing wave
  routed this as SC02 F4 ("a slow /props answer still decides the verdict; settle the vocabulary
  for an unread autoload flag"). At base all four unread cells read `MODEL_UNLOADED/router-unloaded`
  (`controls/c3-base.out`, `mismatches=4`).
- **After.** `tools/kama-probe.sh` (candidate `candidates/kama-probe.r99.sh` until M3) returns a
  tri-state from `router_autoload()`: 0 explicit on, 1 explicit off (a valid router props document
  whose field is `false`), 2 unread. A matching `unloaded`, not-failed entry on an unread answer now
  reads `MODEL_UNLOADED` / **`router-autoload-unread`**; the verdict stays fail-closed and the exit
  code is unchanged. `SKILL.md` gains the reason row and the round-99 decision row.
- **Five live cells** (stub router on a free loopback port; one `unloaded`, not-failed entry with an
  existing local `status.args[0]`): U1 slow `/props` (6.5 s, probe `--timeout 5`), U2 4.5 MiB body
  (over the 4 MiB cap), U3 non-JSON body, U4 valid JSON without the router role or field — each
  `MODEL_UNLOADED/router-autoload-unread` at the tip and `router-unloaded` at base; P1 explicit
  `models_autoload:false` — `router-unloaded` at base and tip (positive control: a blanket rename
  fails it). Tip: `mismatches=0 base_mismatches=4 flips=4 stable=1`; base:
  `mismatches=4 flips=0 stable=5` (`controls/c3-candidate.out`, `controls/c3-base.out`).
- **Grounding (SOURCES.md rows opened this round).** S624 `tools/server/server-models.cpp:2030`
  builds the bare `/props` body with `{"models_autoload", params.models_autoload}`; S625
  `common/common.h:705` defaults that field to `true`, so an "off" answer is an explicit
  `--no-models-autoload` state, never an absence. S626 is a rejected lead (the README option table
  names the flag, not the props JSON field). The new knowledge entry
  `corpus/knowledge/router-props-autoload.md` and the SKILL row cite S624/S625.
- **Regression control (measurement-time):** `controls/c3-regression.out` — the frozen round-98
  counter at M3 prints `ROUTER_BUDGET98 cells=19 mismatches=0 positive_mismatches=0 load_cells=19
  load_stable=1`, exit 0 (the vocabulary change moves no cell expectation).
- **Do-nothing control:** `controls/c3-base.out` — `mismatches=4`, exit 1.
- **Kill rules:** K1 the graded probe/counter bytes change after the freeze commit; K2
  `mismatches>0` at M3; K3 the base control is green; K4 the P1 cell flips at the tip (blanket
  rename); K5 the round-98 19-cell regression shows any mismatch.
- **Disclosed limits.** (a) The cells are stub-fed HTTP answers, not a live llama.cpp router; the
  real `/props` shape is grounded in S624/S625 but not re-observed. (b) The vocabulary change does
  not change the verdict or exit code — an unread autoload stays fail-closed drift; a future
  undecided→loadable decision is a different claim. (c) Without `python3` the probe keeps its
  pre-round-99 behaviour (the function returns 2 only when `HAVE_PY` is set; absent python3 the
  candidate returns unread, while the base returned off — the regression control runs the frozen
  round-98 counter, whose cells all carry python3). (d) `/props?model=` and per-request
  `?autoload=` are still not modelled. (e) A valid JSON body that is a router document but omits
  the field is graded unread (the lane's rule: "off" requires an explicit false).

## Separability, sources, carried defects, frontier step

- **Separability.** C1's grader touches `tools/round99-{router-budget,control-population}.py` and
  scratch copies only. C2's counter touches four committed record files, the results file, the gate
  receipt and the census script. C3's counter touches the probe and loopback stubs. No claim reads
  another's files or receipts.
- **Frontier step (§2b).** `corpus/SOURCES.md`: three rows opened this round (S624 admit, S625
  admit, S626 reject; URLs at tag b12177, digests and located quotes in
  `.ufo/waves/round-99/sources/`); census start `controls/census-start.out` (exit 0, 363 rows);
  census end with the append (exit 0 required). One mistake mined into `corpus/lessons/round-99.md`
  `## Mistakes` (the round-98 wave accounting written from a directory scan instead of
  `w1-results.json`, M1; plus the census mislabel M2 and the carried M3 placement record). C3 is
  the sourced claim (S624/S625).
- **Assimilation.** `merge/kama/` holds no `/props` autoload theme; `Assimilation: none` is the
  report line. `considerthese/2026-11-08.md` proposal 2 (a counter-requires-its-own-claim scan) is
  mined as a pre-freeze scan over the three new counters; its result is committed as
  `controls/counter-literal-scan.out` and recorded in the lesson.
- **Carried unchanged (not claimed):** the slow `/props` *verdict* (still fail-closed drift;
  C3 changes only the vocabulary), the `round75-instruments` red with `bad_rows=19` (L0 r87/r89
  open), the `round78-instruments` red from the host's non-lane Ollama listener on 127.0.0.1:8080,
  the pass-level wall-clock wrapper (SC01), the ctime memo shape, the C1 checks 13–14 receipt-needle
  limit, and the pre-report gate's standing reds (`selfdesc`, `newest-closure`, `round-scope`,
  `round-clean` on the gate's own untracked receipt, `round75-instruments`, `round78-instruments`).

## Wave plan (recorded for the report)

One v1 wave of 12 seats under `ufo-wave-policy.json` (band 8–16): 6 attack seats (RV01 wording, RV02
counter, CR01 records, MT01 mutants, SN01 bounds, CN01 overlap) and 6 building seats (SC01 recon,
SC02 sources, EX01 counter, EX02 records, EX03 autoload, SB01 entry); 1 connector, no planner (the L1
holds the planner seat per the validator ruling). Seats never commit, never edit tracked files.
