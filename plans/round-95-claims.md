# Round 95 — frozen claims (kama)

Base revision `2011161d5e5612fa953708cf54084b7f10ce99b1` (lane `master` at round start; `jj-lane.sh state`
ahead=0 behind=0 tracked=0 untracked=0). L1 `KamaR95` (holds the §3 planner seat). Frozen in the commit that adds
this file together with the three counters it names, so "counter bytes identical to the freeze commit" is
checkable rather than asserted. Every control named below is committed in that same commit.

Closure history read before declaring (`corpus/lessons/round-94-verifier-spotcheck.md`, r93 and r92 spot-checks):
round 94 was `rejected-honest-stop` because C1's frozen counter met a property NARROWER than the claim's sentence
(load-independence on 19 fixtures, while a single slow file and a 20-file listing still flipped), and C2's counter
met while a non-author read falsified three of its decisions. Both rounds named more receipts in the plan than they
committed (M5) and froze predicates whose metrics their counters never printed (M6). Round 95 therefore declares
claims whose wording is exactly what a counter enforces, and adds a counter that grades the plan itself.

Axes (SCORECARD `## Axes`): operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. Lowest
non-retired: depth / calibration / adjacency (7). C2 works depth, C3 works calibration, C1 works operability (the
lane's assigned axis pair). No axis is claimed as improved by C1's speed; C1 claims decisiveness only.

## Receipts: freeze-time vs measurement-time

Round 94's M5 defect was a plan that named twelve receipts, none of which existed at its own freeze. This plan
therefore separates them, and C3 grades exactly the first class.

- **Freeze-time (must exist at F, committed with this plan):** `controls/census-start.out`, `controls/c1-base.out`,
  `controls/c2-base.out`, `controls/c3-base.out`, `controls/c1-discriminator-guard.out`,
  `controls/sources-opened.out`, `controls/c2-section-candidate.md`.
- **Measurement-time (committed with M1/M2, named in LOG.md and the report, never required at F):** harm-base.out,
  harm-tip.out, measured/c1.out, measured/c2.out, census-end.out.

## C1 — operability: the router file-state verdict is a function of the file's bytes, and the pass limit is derived from the candidate count

**Predicate (one sentence, same in the counter's docstring and in the receipt label):**

`python3 tools/round95-router-budget.py --repo . --rev <M1> --work <scratch>` prints
`ROUTER_BUDGET95 cells=10 mismatches=0 positive_mismatches=0 load_cells=10 load_stable=1 budget=work probe=rev …`
and exits 0 at the measured commit M1, the counter's bytes identical to this freeze commit.

- **Before.** `ROUTER_PY` bounded a candidate's parse with a wall clock: one shared 4 s call deadline before round
  94, a 15 s per-file slice after it. Either way the same bytes graded `invalid` on an idle host and `-`
  (undecided → loadable, round-89 rule) under load, which is a `MODEL_OK` false green for a model that can never
  load; and the pass ran under a constant `timeout 60`, so a listing of N distinct slow files truncated at 60 s and
  the truncated candidates stayed loadable (round-94 closure routed defects D3/SC02 F2, F3, CR01 F3/F8, MT01 M02/M10).
- **After.** The clock is removed from the decision. Work is bounded deterministically — `MAX_STEPS` (4 000 000)
  counts the parser's read/seek steps and `MAX_META` (512 MiB) caps the header position — and the pass limit is
  `20 + 15 * ncand` seconds, where `ncand` is the number of candidate entries in the listing.
- **Cells (10, frozen in the counter's docstring):** W01 slow×1, W02 eight distinct slow, W03 twenty distinct slow
  (the discriminator: the round-94 probe truncates this pass), W04 valid×8, W05 seven slow then one valid, W06
  missing×8, W07 forty distinct fast invalid, W08 eight hard links to one slow inode, W09 a file declaring
  1 200 000 tensors (disclosed `-`), W10 a same-size in-place rewrite with mtime restored (ctime key).
- **Do-nothing control:** `controls/c1-base.out` — the same counter at the round-94 probe revision
  `a27656a454b1a2364f8b6e55f42fbca8c2e86ee4` with `--allow-clock --burners 64`. It must redden W03 (truncated pass
  graded `MODEL_OK`) and/or a load cell; a green base run means the counter cannot discriminate and the claim is
  void. Receipt committed with this plan.
- **Counter self-defect closed:** round-94's counter asked the BASE probe to classify its own fixtures and exited 2
  when that probe could not answer under load (SC02 F1: 25/41 attempts). This counter has a byte-level
  `fixture_class()` oracle that never consults a probe.
- **Kill rules:** K1 `mismatches>0` or `load_stable=0` or `cells!=10` at M1 (this is the counter's own exit
  condition — round 94's K1 named a narrower condition than its counter enforced); K2 a harm suite regresses
  against the base harm receipt the M1 commit carries (`tests/probe-verdicts/check.py`, `tools/test-snapshot.sh`,
  `round89-unloadable-cells.py` with `LLAMA_CACHE`/`HF_HOME` isolated, `round90-hostile-answers.py`,
  `round91-answer-time.py`, `round92-linear-paths.py`, `round93-router-repeat.py`); K3 the counter changes after
  this commit.
- **Disclosed limits (before data).** (a) A candidate whose declared tensor count exceeds `MAX_TENSORS` or that
  needs more than `MAX_STEPS` stays `-` (undecidable → loadable) — W09 grades that as the disclosed expectation,
  not as a fix. (b) The claim is decisiveness on the frozen cells, not a bound on total parse time: W03 spends
  ~50 s of CPU at 20 distinct slow files by construction. (c) A slow `/props` answer still decides the verdict
  (round-94 SC02 F4) — routed, not claimed, because the honest verdict for an unread autoload flag is a
  vocabulary question this round does not settle. (d) The wrapper is a *derived* ceiling, not an unbounded one: a
  listing of very many distinct slow files still has a wall-clock limit at `20 + 15*ncand`.

## C2 — depth (lowest axis, 7): the setter sweep admits the carriers that set a value without naming it, and decides per entry point

**Predicate:**

`python3 tools/round95-setter-sweep.py --repo . --rev <M2> --work <scratch>` prints
`SETTER_SWEEP95 population=106 rows=106 bound=106 unbound=0 missing=0 duplicates=0 fabricated=0
derived_disagree=0 entries=7 decisions=9 decisions_bound=9 met=True` and exits 0 at the measured commit M2, the
counter's bytes identical to this freeze commit.

- **Before.** Round 94's population could not see three carriers: the config.ini section scoping that decides which
  sections reach the caller (`[default]`, `[*]`), the `common_params` whole-struct copy at
  `tools/cli/cli-server.h:43` that carries llama-cli's own `port`/`n_parallel` into its embedded server, and the
  `params_base.n_parallel` realisation reads. Its decision model was one `R18`/`R19` row per parameter, silent for
  the `cli` and `router-child` entries its own vocabulary defines (round-94 SC01 F1/F2).
- **After.** Population 92 → 106 lines (14 new rows, P93–P106); the decision model is one `R20` row per entry point
  for `port` and one `R21` row per entry point for `n_parallel`, for every entry that owns a `default`/`overrides`
  row (server, cli, router-child, shared, other) — 9 decision rows whose id sets are graded for exact equality
  against the bound rows and whose decision text must carry the entry's precedence tokens (`[default]`+`[*]` for
  shared, `LLAMA_ARG_PORT`+`AIP_HTTP_PORT` for router-child, `server_params` for cli, `--port`/`--parallel` for
  server, `auto` for router, `own` for other).
- **What the claim does NOT say.** It is an instrument-coverage claim: the table now decides each governed entry
  point and its rows name the carriers. It does not assert that every row's prose is true — the source bytes are
  copied verbatim and graded, and a non-author read remains the semantic gate (round 94's K2 is retained as an
  attack, not as this claim's predicate).
- **Do-nothing control:** `controls/c2-base.out` — the same counter at the base revision, where the round-95
  section does not exist: `population=106 rows=0 bound=0 missing=106 met=False`, exit 1. Receipt committed.
- **Kill rules:** K1 the counter changes after this commit; K2 a bound P-row's text, source or derived cells no
  longer match the pinned `b12177` archive; K3 a decision row's id set stops equalling its entry's setter rows.
- **Sourced:** S616 (`tools/server/server-context.cpp` @ b12177, sha256 `e0e43f22…a973`) and S617
  (`tools/server/server-schema.cpp` @ b12177, sha256 `7f4d7c35…6b54`), both opened this round, cite the rows the
  realisation reads land; S593, S596, S604, S606, S613–S615 are re-opened to keep every cited row's scope.
- **Disclosed limit (before data).** The population is a line pattern: a setter that writes the value through a
  name outside the pattern's tokens (a reference alias, an env-var indirection inside `get_environment`) is graded
  only through the rows its value passes. `realises` rows consume a value and choose none, so they never enter a
  decision id set.

## C3 — calibration: the freeze carries the receipts it names and the tokens its instruments print

**Predicate:**

`python3 tools/round95-freeze-audit.py --repo . --rev <F>` prints
`FREEZE_AUDIT receipts=<n> present=<n> missing=0 tokens=<m> matching=<m> cited=<c> unresolved=0 met=True` and exits
0 at the freeze commit F (this commit), the counter's bytes identical to F.

- **Before (the defect).** Round 94's plan named 12 receipt paths; at its freeze commit `285f1783` **none** of them
  existed and its named `tools/round94-setter-sweep.py` did not exist either, so every "control executed before the
  freeze" sentence in that plan was unfalsifiable from the repo (lesson M5). One frozen predicate quoted
  `entry_points=<e>`, a metric that counter never printed (M6).
- **What the counter grades.** (1) every repo-relative path the plan names under the round's wave directory exists
  at `--rev`; (2) on every plan line that names a counter, every `token=<…>`/`token=<n>` assignment appears
  literally in that counter's committed bytes; (3) every `S###` the plan cites resolves to a Registry row at that
  revision with `status` not `rejected`.
- **Do-nothing control:** `controls/c3-base.out` — the same instrument on the round-94 plan at its own freeze
  commit `285f1783`: `receipts=12 present=0 missing=12`, the named counter absent, S604 unresolved, exit 1. Receipt
  committed.
- **Kill rules:** K1 missing>0 or token-missing>0 or unresolved>0 at F; K2 the counter changes after this commit;
  K3 `--selftest` no longer prints `FREEZE_AUDIT_SELFTEST pass=5 fail=0`.
- **Disclosed limit.** The audit grades *presence and literal tokens*, not receipt content: a committed file that
  does not contain what its name promises (round-94's `c1-forgeries.out` class) passes. The content gate stays the
  counter's own grading and the non-author read.

## Separability, sources, carried defects, frontier step

- C1's counter reads only `tools/kama-probe.sh`; C2's reads `SKILL.md`, `corpus/SOURCES.md` and the pinned archive
  and never runs the probe; C3's reads `plans/round-95-claims.md`, the counters' bytes and the S-rows. Each
  verifies with the others unlanded.
- **Sourced claim:** C2 (S616, S617 opened this round; S593/S596/S604/S606/S613–S615 re-opened).
- **Frontier step (§2b):** `corpus/SOURCES.md` census before → after is recorded with
  `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`; the lesson `corpus/lessons/round-95.md`
  carries `## Gate` (each new row's URL, access date and ≤25-word located quote, plus one rejection) and
  `## Mistakes` (class · evidence · captured-by · fix). Rows: 355 → 357 at the time of writing.
- **Carried, not claimed:** R1/D2 `round75-instruments` red (`APPEND_DEBT … bad_rows=19`, L0 r87/r89 open); the
  `round78-instruments` live-reconcile red caused by the host's non-lane Ollama listener on 8080; round-94's C1
  residual (a slow `/props` deciding the verdict) and C2 residual R20/R21 prose truth (the counter now decides per
  entry point; the prose read remains with the closure).
