# Round 99 — amendment 1 (pre-measurement; wave-1 findings)

Recorded before any scored measurement: when this file was written, the only committed receipts were
the freeze-time controls; no `measured/*.out` existed except `measured/c1.out`, which is superseded
by this amendment's re-measured C1 receipt. The round-99 wave's attack seats falsified stated
wordings and exposed instrument gaps in all three claims. This amendment (i) hardens each instrument
where a demonstrated forgery passed, (ii) narrows each claim to what its instrument enforces, and
(iii) re-freezes the counters at this commit. Kill rule K1 in each claim now refers to **this**
commit's bytes; M1 = M2 = M3 = this commit. Every `falsifies-wording` row in
`claim-falsification.tsv` cites this file.

## A1 — C1 (operability)

**Artifacts.** `w1/EX01Counter.md` (predicate-line mismatch: the frozen sentence omitted
`population_shaped=1`; an emptied selection passes vacuously; a fabricated CONTROL line with zero
`_CELL` lines passes; no committed grader-level negative arm), `w1/MT01Mutants.md` F1/F6 (same; a
grader with `refused=1` hardcoded reproduces the positive receipt), `w1/RV02Counter.md` rows 4/5/7/9/10
(a same-count renamed/replaced/injected cell or a coordinated shrink passes the count guard; row 10
the empty selection is "complete"), `w1/SC01Recon.md` (the same predicate-line omission; the
census-start receipt carries neither an exit token nor a row count; the committed
`sources/s627-arg-models-autoload.txt` had no SOURCES row).

**Changes.**
- `tools/round99-router-budget.py`: the control mode compares the **selected id set** to the ids the
  pass actually ran (`population_ok = bool(want_ids) and set(want_ids) == set(natural)`); the control
  line prints `selected_ids=` and `ran_ids=`. An empty, short, renamed, substituted or injected
  population cannot pass.
- `tools/round99-control-population.py`: `population_shaped=1` requires the mutant line's
  `selected_ids` to be exactly the six `new` cells, `ran_ids` exactly those six minus the dropped
  cell, `population_ok=0`, and at least `ran` `_CELL` lines; the positive line's `selected_ids` and
  `ran_ids` must both be the six and its `_CELL` stream at least six lines. A fabricated CONTROL line
  (zero cells) and a hardcoded `refused=1` (the base negative arm) are refused.
- Required controls: `controls/c1-before.out` (round-98 counter accepts the one-line drop, exit 0),
  `controls/c1-candidate-mutant.out` (successor refuses, exit 1), `controls/c1-positive.out`
  (complete population accepted, exit 0), `controls/c1-grader-base.out` (the grader against the
  round-98 counter prints `refused=0 … met=False`, exit 1 — the grader-level negative arm).

**Predicate (same sentence in the plan, the grader/docstring and the receipt).**
`python3 tools/round99-control-population.py --repo . --rev <M1> --work <scratch>
--counter tools/round99-router-budget.py` prints a `CONTROL_POP99` line carrying
`selected=6 ran=5 mutant_control_exit=1 mutant_ok=0 refused=1 positive_exit=0 positive_ok=1
complete=1 mutant_cell_lines=5 positive_cell_lines=6 population_shaped=1 met=True` and exits 0 at M1.

**Before → after.** The round-98 counter's control on the one-line drop runs five of six cells and
prints `cells=5 … survived=1 ok=1`, exit 0 (`controls/c1-before.out`). The round-99 control on the
same mutation prints `selected=6 ran=5 selected_ids=<6 ids> ran_ids=<5 ids> population_ok=0 ok=0`,
exit 1 (`controls/c1-candidate-mutant.out`); unmodified it prints `population_ok=1 ok=1`, exit 0
(`controls/c1-positive.out`). A grader-level negative run against the round-98 counter prints
`refused=0 … met=False`, exit 1 (`controls/c1-grader-base.out`).

**New limits.** (a) The guard binds cell **ids**, not fixture content: a cell whose id is unchanged
but whose fixture is replaced passes (RV02 row 5). (b) A counter that hardcodes its own
`population_ok=1` or fabricates a full `_CELL` stream is a lying subject; the grader can only bind
the stream length and the ids. (c) Control mode only: the natural 19-cell predicate is round 98's
and is not re-run by C1. (d) The grader exercises only the six-cell `new` set and the single W14
drop. (e) `--expect-cell` is not exercised by the grader.

**Kill rules.** K1 the graded counter/grader bytes change after this amendment commit; K2 met=False
at M1; K3 the round-98 predecessor also refuses the drop; K4 the unmodified successor refuses a
complete population; K5 the grader-level base arm prints met=True.

## A2 — C2 (calibration)

**Artifacts.** `w1/CR01Records.md` §4/§7 (eight meaning-changing mutations pass the freeze bytes; the
`--tree` census defect; the verdict line is not required in the corrections), `w1/EX02Records.md`
§3.1–3.2 (the freeze counter cannot run its own `--tree` forge; forgeries B2, C2, D, D2, G, H, K, L,
M, N, J, V, O escape), `w1/MT01Mutants.md` F2/F3 (post-freeze byte drift; the docstring's
`mismatches=9` contradicts its own 10), `w1/SC01Recon.md` (the frozen `--tree` mode cannot grade any
tree; the `--rev` predicate works with frozen bytes at a scratch clone carrying the corrections).

**Changes.**
- The `read_bytes_at` repair: the two historical census revisions always come from `git show`, also
  under `--tree`. With the freeze bytes, `--tree` compared the tree's tip `SOURCES.md` against both
  frozen constants, so no tree could make the forged control valid (EX02 §3.1).
- Twelve checks hardened exactly as the counter's docstring states: per-file after-block rules
  (1/2), per-file pointers (3), segment-scoped attribution with derived populations (4/6), a
  line-joined SB01→EX02BudgetControl clause (5), line-scoped, revision-bound, single-line census
  groups (7), git-bound census re-derivation (8), the exact verdict line and six-arm phrase in each
  file plus the receipt's re-derived FAIL arms (9), a single `## Mistakes` and a paragraph carrying
  the carried M3 record (10), the exact counts phrase plus the re-derived 12/0 (11), and the derived
  population (12).
- The forged control is run two ways: `controls/c2-forged.out` (materialized tree with the old
  counts) and `controls/c2-forged-rev.out` (a scratch `git clone --shared` in which the forged M2 is
  committed and graded with `--rev`; no frozen byte is edited). The twelve-variant matrix is
  `controls/c2-forge-matrix.out`.
- `claims.json`/the plan sentence is narrowed: the counter grades the twelve **mechanical**
  propositions over committed bytes. It does not read negation or prose intent (an M/N-style
  sentence whose tokens are present but negated passes the token checks), it does not authenticate
  a committed receipt (a forged gate receipt whose six FAIL arm names match the expected six passes
  check 9), and it does not grade the fleet report. The non-author read remains the semantic gate
  (KQ14/QUALITY).

**Predicate.** `python3 tools/round99-record-audit.py --repo . --rev <M2> --work <scratch>` prints
`RECORD_AUDIT99 checks=12 mismatches=0 met=True rev=<M2>` and exits 0 at M2; at base `439fdb3d` it
prints `mismatches=10` and exits 1.

**Carried red.** `tools/round90-reason-rows.py` is red at base and at this commit
(`bound=0 unbound=24 receipt=stale`, the receipt is bound to probe sha `1e21c1fb` from six probe
changes ago); `SCORECARD.md:311/5840/5944` still publish `bound=24 unbound=0` and are routed for a
round-100 correction. C3 does not deepen it: no row is added to the frozen reason-codes table (CN01).

**New limits.** (a) Tokens with negated meaning pass (semantic gate). (b) A forged gate receipt
inside a materialized tree is outside the claim. (c) Check 7 requires the labelled base/tip line
shape; a different wording fails even with the right numbers. (d) The two census revisions and the
round-98 results file are the frozen evidence; the tip's own rows are not graded. (e) Check 4's
segment ends at the first period after the non-attack list, so a correction that writes extra names
after that period is not attributed.

**Kill rules.** K1 the graded counter's bytes change after this amendment commit; K2 mismatches>0 at
M2; K3 the base control is green; K4 any of the twelve forged variants passes; K5 the `--rev` forged
replay and the `--tree` forged control disagree.

## A3 — C3 (depth)

**Artifacts.** `w1/RV01Wording.md` F1 (exit code printed, never graded; an unread-but-exit-0 probe
passes), F2 (U4 does not isolate the role predicate), F3 (field-absent router document ungraded), F4
(non-boolean field ungraded; a truthiness mutant grades `"false"` as `MODEL_OK` exit 0), F5 (HTTP
status not consulted), `w1/MT01Mutants.md` F5 (the absent-field mutant flips the verdict; no cell),
`w1/EX03Autoload.md`, `w1/CN01Overlap.md` §4 (a row under the frozen `## Probe reason codes` table
cannot bind to the round-90 capture; the reason belongs in the decision table), `w1/SC01Recon.md`
receipt 10 (the candidate's bare `router_autoload "$port"; ra=$?` breaks `set -e` on the plain-call
subcommands: `listeners`/`consumers` abort with no row on an unread or explicit-off `/props`,
rc=2/rc=1 where the base emitted a row and rc=0).

**Changes.**
- `tools/round99-autoload-states.py`: eight cells — U1 slow, U2 oversize, U3 non-JSON, U4
  non-router document, **U5 router document with the field absent**, **U6 non-boolean field
  (`"false"` string)**, **U7 wrong-role document with an explicit false**, plus P1 explicit-off —
  and (verdict, reason, **exit**) grading.
- The candidate probe changes in one place: `router_autoload` is called inside a condition
  (`if router_autoload "$port"; then ra=0; else ra=$?; fi`), so `set -e` is exempt on the
  plain-call subcommands; the tri-state logic is unchanged. A regression control
  `controls/c3-plaincall.out` runs `listeners` against stubs in the on/off/non-router scenarios for
  the base and the candidate: all rc 0, with the candidate's non-router reason the new vocabulary
  and the off/on reasons unchanged.
- `SKILL.md`: the Round-88 decision table gains the unread row (before the historical last row) and
  a `## Round 99 unread-autoload reason (owner: kama)` section. The round-90 `## Probe reason codes`
  table is left **byte-identical**: a 25th row there cannot bind (the round-90 capture has no cell
  that omits or corrupts `/props`), and adding it would deepen a repairable red into an unrepairable
  one (CN01's measured A/B/C fixtures). The new section says so and points at the decision row.
- Sources: S627 (`common/arg.cpp:3682`, the only writer of `params.models_autoload`) is admitted and
  cited by the entry and the SKILL section, closing SC02's orphan-receipt finding; S628
  (`tests/unit/test_router.py:23`) is **rejected** — the path is HTTP 404 at b12177, so the seat's
  claimed assertion cannot be re-opened. Census 363 -> 368 (A 345->348, C 7->9; mined 325->328,
  rejected 30->32).

**Predicate.** `python3 tools/round99-autoload-states.py --repo . --rev <M3> --work <scratch>`
prints `AUTOLOAD_STATES99 cells=8 mismatches=0 base_mismatches=7 flips=7 stable=1 met=True
rev=<M3> probe_sha256=<sha>` and exits 0 at M3; at base `439fdb3d` it prints `mismatches=7` and
exits 1.

**New limits.** (a) Stub-fed, not a live router. (b) The probe does not consult the `/props` HTTP
status: a non-200 body that parses as a router document is graded as its explicit state, and no
cell sends a non-200 answer. (c) Without `python3` the router-refine path is never entered
(`router_entries`/`router_file_states` bail first), so both probes print `MODEL_OK/matched` — the
`router_autoload` unread branch is unreachable through the CLI; the plan's earlier "base returned
off" wording is withdrawn. (d) `/props?model=` and per-request `?autoload=` are not modelled. (e) A
`models_autoload:true` body is outside the unread cells and is protected only by the round-98
19-cell regression. (f) The new reason is not a row of the frozen reason-codes table (see above).

**Kill rules.** K1 the graded probe/counter bytes change after this amendment commit; K2
mismatches>0 at M3; K3 the base control is green; K4 P1 flips; K5 the round-98 19-cell regression
shows any mismatch; K6 the plain-call control shows any scenario's rc or off/on reason differing
from the base.
