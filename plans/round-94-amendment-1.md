# Round 94 — amendment 1 (post-freeze narrowing, Amendment 59 ledger)

Date: 2026-11-08. Author: L1 `KamaR94a2`. Frozen plan: `plans/round-94-claims.md` (commit
`285f17832d0e26364366bbf19888d68f1838249b`). This file does not rewrite the frozen plan; it records
the narrowing the pre-file falsification ledger points at for each claim whose STATED WORDING a
wave-1 artifact falsified while its frozen counter still met its predicate.

Amendment 59 rule applied: "(i) amend the frozen claim down to the enforceable property, citing the
artifact, and then file; or (ii) file an honest stop whose deliverable IS the narrowing."

## C1 operability — **honest stop** (the deliverable is this narrowing)

Filing verdict: **not verified**. The frozen predicate reproduces (below), but three independent wave
seats (SC02 F1/F2/F3, CR01 F3/F6/F7/F8, MT01 BLOCKER-1 and its four survivor families) falsify the
claim's stated property and the plan's own F1 control, and no measurement this round reddens the M02
shape. Amendment 59 branch (ii) applies: the round's deliverable for C1 is this narrowing plus the
routed coverage work, not an admission.

The claim that would have been admitted, had the control fired, was: "the probe's file-state verdict
is identical across the two host loads the frozen counter applies, on its frozen 19-cell fixture set"
— with the residual classes named below excluded. It is not admitted this round.

Falsified wording: "makes the router file-state verdict **load-stable**" (claims.json C1 `name`),
and the plan's disclosed limit sentence that scopes the miss to "the counter's own 20 s cell budget,
not the probe's".

Artifacts: `.ufo/waves/round-94/w1/SC02BudgetSweep.md` F1/F2/F3/F4.
- F2: a 400 000-tensor invalid GGUF (2.4 M of the 4 M MAX_STEPS; 1.6 M steps of headroom) parses to
  `invalid` at low load and `-` (undecided → loadable) when its parse straddles the per-file 15.0 s
  wall slice: measured `invalid, invalid, -, -` over four alternating runs at load1 418–443. The
  per-file budget relocates the round-93 shared-deadline defect to a per-file wall clock; it does
  not make the verdict load-independent outside the counter's fixture band.
- F3: `timeout 60` over the whole `files` pass truncates a listing of 40 distinct slow files
  (rc=124, 33/40 state lines), and `nbad(33) < ncand(40)` then grades `MODEL_OK /
  router-unloaded-autoload`; the same listing at `timeout 600` grades `MODEL_UNLOADED /
  router-model-invalid` (232 s). The base probe false-greens the same listing at 5.76 s.
- F4: a `/props` answer slower than 5 s turns a healthy 4-entry router into `MODEL_UNLOADED /
  router-unloaded` (props_delay=6), pre-existing at base.
- F1: the counter's sanity gate uses the **5af79495** probe (r93 base, shared 4.0 s deadline); under
  host load that gate cannot classify its own 150 000-tensor fixture and the counter exits 2 before
  any cell, so the predicate is unreachable on a loaded host. Both `BASE` and the claims' stated base
  carry the shared 4 s deadline, so the gate is unsound under either choice.

Narrowed claim (this is what round 94 claims, and what the counter enforces): the probe's file-state
verdict is identical across the two host loads **the frozen counter applies, on its frozen 19-cell
fixture set** (`cells=19 mismatches=0 positive_mismatches=0 load_cells=19 load_stable=1`), where
before the change the same counter graded the base probe unstable (`mismatches=3
positive_mismatches=0 load_stable=0`, R04 and T01 flips at load1 197.96). The claim does **not**
assert load-stability for a single file whose parse time straddles the 15 s slice, nor for a listing
of ≥~40 distinct slow files that exceeds the probe's 60 s wrapper, nor for a `/props` answer slower
than 5 s. Those three remain open defect classes routed to round 95: a deterministic
work-proportional budget (not a wall clock), a wrapper ceiling derived from the file count, and a
`/props` timeout that is not a verdict.

Do-nothing control (this round, on this host): `tools/round94-router-budget.py --rev e6f1dcce
--burners 32 --runs 1` → `cells=19 mismatches=3 positive_mismatches=0 load_cells=19
load_stable=0 … load1_nat=197.96`, exit 0 (`PREFILE` receipt: the closing line is pasted in the
report's Before → after section). The measured commit M1 reproduces the frozen receipt
(`cells=19 mismatches=0 positive_mismatches=0 load_stable=1`, `load1_nat=141.70 burners=32`).

## C2 depth — **not verified**

Falsified: the K2 condition in the frozen plan ("a non-author reviewer finds … an R18/R19 decision
that states a port or slot count for an entry point another population row shows is set otherwise").

Artifacts: `.ufo/waves/round-94/w1/SC01SetterSweep.md` F1/F2/F3 and
`.ufo/waves/round-94/w1/CN01SiblingOverlap.md` F4.

SC01 F2 is the firing case: R18 states that a router child's port is the router-assigned free port,
while population rows P62/P66 (`server-http.cpp:96/125`, `AIP_HTTP_PORT` / `AIP_MODE=PREDICTION`)
show the child inherits the router's environment (`server-models.cpp:288`→`:399`, P72/P76) and that
the AIP override wins over the free port — measured: the child logged "overriding server port 39547
with AIP_HTTP_PORT 18230" and failed to bind; `--port 18260` with `AIP_HTTP_PORT=18262` listened on
18262. SC01 F1 adds that R19 is silent for the `cli` and `router-child` entries its own Entry
vocabulary defines, and that the section's "1 slot" prose for `llama-cli` is wrong in general
(measured 1/4/5/6/0 and auto→4). SC01 F3 adds that the config.ini prose overstates how a named
section reaches the process's params. CN01 F4 adds that kama's own registry violated R18's citation
duty (fixed this round: `registry/endpoint-consumers.tsv` rows 35–37).

Verdict: C2's counter predicate is met (`SETTER_SWEEP 92 92 2 92 0 0 0 0 derived_checked=47
derived_disagree=0 decisions=2/2 pop=92 met=True`, exit 0 at M2) and its state is admitted only as
an instrument; the **claim is not verified**. The corrected readings land in `SKILL.md` §Round 94
correction (c1/c2/c3) as superseding prose, not as rewritten frozen rows. Routed to round 95: R20
(slot count per entry point incl. `cli` and `router-child`, with the `cli-server.h:43`
whole-struct carrier and `server-context.cpp:1489` realisation as population rows), R21 (R18
precedence: env inherited into the child beats `LLAMA_ARG_PORT` and argv), and a population pattern
that admits whole-struct copies.

## C3 calibration — verified after a one-token repair

Falsified-in-part wording: "≤25-word located quote per row" for S604 — the quote sits at
`common/preset.cpp:151`, not 150; both `corpus/SOURCES.md:359` and this lesson's Gate row said 150.

Artifact: `.ufo/waves/round-94/w1/CN02SourceFrontier.md` F1 (and
`.ufo/waves/round-94/w1/SB01LessonDraft.md` DEFECT-1, same finding, independent seat).

Repair: 150 → 151 in `corpus/SOURCES.md` and `corpus/lessons/round-94.md`; the census re-validates
(exit 0, 355 rows, no new E/W finding). The rest of C3 holds as declared: census 343 → 355 rows,
exit 0 at M3; `## Gate` and `## Mistakes` present; both census outputs pasted in the report.

## Ledger

`.ufo/waves/round-94/claim-falsification.tsv` records one row per (claim, wave artifact), covering
every attack seat that produced an artifact this round and the residual seat that did not.

## Addendum (2026-11-08, after the late-arriving MT01 artifact)

`w1/MT01ProbeMutants.md` (the wave's dead seat — lost handle, settled dead, artifact written late)
adds four falsifications to the C1 record above and one to the plan's own control text:

- The plan's F1 control sentence ("a per-call (not per-file) deadline → the synthetic-load cell red")
  is **false**: mutant M02 (the reset moved from `gguf_parse` into the `files` loop) scores
  `mismatches=0 positive_mismatches=0 load_stable=1`, exit 0 at load1 323.04. Its separating input is
  one invocation naming 8 distinct slow invalid GGUFs (R08 uses 4, and four fit inside a single 15 s
  budget). This matches CR01's F3_shared_deadline survivor byte-for-byte in shape.
- Four further survivor classes with measured separating inputs: a mid-invocation same-size rewrite
  with restored mtime (ctime-less key), a 2 M-tensor sparse header (count overflow graded invalid), a
  ~20-file listing that reaches the 60 s wrapper, and the per-invocation budget above. M04/M05/M11 are
  measured **equivalents** (the MAX_STEPS and wall bounds are crossed within ±10 % of each other),
  not gaps.
- The plan's "counter's own 20 s cell budget" is wrong: `tools/round94-router-budget.py:108` is
  `BUDGET = 30.0`.
- K1 as worded ("positive_mismatches>0 or load_stable=0") is narrower than the counter's exit
  condition: `mismatches>0` alone also exits 1 (M06: `mismatches=3 positive_mismatches=0
  load_stable=1`, exit 1). The predicate's `exit 0` requirement is what catches that class.
- `round89-unloadable-cells.py` (named as a K2 harm suite) is unrunnable after 00:11 unless
  `LLAMA_CACHE`/`HF_HOME` point at an empty dir: a cache-sourced router model created by another seat
  makes its identity guard abort (rc=2). The round's harm re-run therefore used
  `LLAMA_CACHE`/`HF_HOME` overrides, and the round-89 baseline is recorded at M1 as
  `cells=11 mismatches=0 positive_mismatches=0`, exit 0.

Net effect on the claim: unchanged in direction, wider in the disclosed residual set. C1 remains
"predicate met on the frozen 19 cells; wording narrowed"; the residual classes routed to round 95 are
now: per-invocation budget (M02), ctime-less memo key (M12), count overflow (M14), 60 s wrapper
(M10/F3), a single file's own 15 s slice (SC02 F2 / MT01 NOTE-3), the counter's sanity gate (SC02 F1),
and a slow `/props` (SC02 F4).
