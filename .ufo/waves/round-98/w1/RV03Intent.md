# RV03Intent — round-97 counter reverse-engineering and round-98 control gaming

Seat: RV03Intent (leaf, no subagents). Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Plan read first: `plans/round-98-claims.md` §§C2 (frozen) and mirrored `claims.json` C2.
Comparisons: `tools/round97-router-budget.py` (703 lines) vs `tools/round98-router-budget.py`
(726 lines). Receipts: `.ufo/waves/round-98/controls/c2-legacy-mutants.out`,
`.ufo/waves/round-98/controls/c2-new-mutants.out`. All findings are static + short
bounded checks in scratch (`/fast/scratch/hyaku/kama-r98/RV03Intent/`, since removed);
no fixture full runs were needed, because every gaming question is answerable from
`apply_mutant`, the `--control` branch, and the arithmetic tables the counter itself prints.

Verdict up front: **the round-98 budget controls are honestly sized and honestly receipted
for the frozen predicate.** Every gaming path I could construct either (a) exits 2
(`could-not-evaluate`) instead of printing `survived=1`, (b) requires a CLI combination the
frozen predicate command does not use, or (c) requires editing the counter itself (out of
scope, and K1 would void the claim). No path prints `survived=1` for an overcharge probe
that lacks the intended +1/header arithmetic. The two genuine fragilities are
`--probe-file` override binding (disclosed limit g) and the `n == 0 ⇒ survived = 1`
arithmetic (unreachable via CLI). Details and proof trails below.

## 1. What the round-97 counter was built to enforce

The round-97 counter (`tools/round97-router-budget.py`, predicate `ROUTER_BUDGET97
cells=17`) grades the probe's step-budget arithmetic from the **decidable side only**:
seventeen fixtures whose full parse is also `-` (the round-96 failure class: four probe
mutants — flat6, undercharge, maxmeta, nopreamble — survived all 13 round-96 cells because
every fixture's complete parse is also `-`). Round 97 added four new cells (W14–W17) that
expect `-` (loadable): a probe that stops charging per header, charges a flat 6, caps
MAX_META at 100 MiB, or drops the 4 preamble steps flips at least one cell to `invalid`
and is caught. W17 pins the preamble (833,333 headers at nd=1: 4+6·833333 = 5,000,002 >
5,000,000, real `-`; without the 4 preamble steps 4,999,998 ≤ budget, `invalid` → caught).

Its own closure left the dual window open (plan §C2 "Before" / RV03 F5): a probe charging
**one extra step per header (6+nd instead of 5+nd)** stays on the same side of
MAX_STEPS as the real parse on *all seventeen* fixtures — every one is already `-` under
the +1 parse — so the 17-cell set passes it. The round-97 ceilings as stated (833,332 /
555,555) are false for that probe: its true nd=1 ceiling is 714,285 headers.

## 2. Behavioural difference table (round-97 → round-98)

`diff -u` is 260 lines; only the rows below are behavioural. Everything else is
docstrings, labels (`ROUTER_BUDGET97*` → `ROUTER_BUDGET98*`), and the two new fixtures.

| # | Area | round-97 | round-98 | Behavioural effect |
|---|---|---|---|---|
| 1 | Cell count | `CELLS = 17` | `CELLS = 19` | Predicate `cells=` field and `want_cells` check become 19. |
| 2 | `NEW_CELLS` | 4 cells (W14–W17) | 6 cells (+W18, W19) | `--cells new` now grades 6 cells; W18-800k-nd1 (800k, nd=1) and W19-520k-nd4 (520k, nd=4), both expecting `invalid`. |
| 3 | `R97_CELLS` | absent (no such set) | `LEGACY_CELLS \| {W14..W17}` (17 cells) | New `--cells r97set` choice selects exactly the round-97 set; used by the do-nothing control. |
| 4 | Mutants | 4 (flat6, undercharge, maxmeta, nopreamble) | 5 (+`overcharge`) | `overcharge` anchors on `for _ in range(n_tensors):` (exactly once in the 681c80a4 probe; verified count=1) and inserts a loop-top `steps[0] += 1`. The four old mutants are byte-identical anchors/replacements (verified programmatically). |
| 5 | New fixtures | 11 | 13 (+t800k.gguf@800k/nd1, +m520k4.gguf@520k/nd4) | Both write `gguf(T,1,False)` / `gguf(T,1,False,nd=4)`; the counter's byte-oracle labels both `invalid` (verified: `build_fixtures` oracle run in scratch succeeds; step arithmetic below). |
| 6 | `--cells` choices | all/legacy/new | all/legacy/new/r97set | No new way to select an empty set; the smallest selection is `new` (6 cells). |
| 7 | `--mutant` choices | 5 (incl. none) | 6 (+overcharge) | — |
| 8 | Exit codes | 0/1/2/64 | identical | No change (same line structure; verified by grep). 64 = usage, 2 = could-not-evaluate, 1 = not met, 0 = met. |
| 9 | Summary fields | `ROUTER_BUDGET97 cells=… budget=work probe=…` | same fields, `ROUTER_BUDGET98` | Field set unchanged (mismatches, positive_mismatches, load_cells, load_stable, budget=work, probe, mutant, slow_files, runs, probe_sha256, base_sha256, rev, w03_seconds, load1_nat, burners). Predicate string gains `--slow-files 72` (plan disclosed limit e). |
| 10 | `--control`/`--expect-cell` | present | unchanged | Same branch (lines 653–675 ≈ 631–652 in r97). `--expect-cell` must be in the selected set, else `could-not-evaluate` + return 2. |
| 11 | Oracle | `fixture_class` from written bytes | same function + 2 more `checks` entries | The oracle recomputes `4 + T·(5+nd) ≤ 5,000,000`; t800k (4,800,004 → `invalid`) and m520k4 (4,680,004 → `invalid`) pass. |
| 12 | Fixture modes | — | `--cells new` ⇒ `n_slow = 0` (no legacy cells ⇒ no slow files) | New-cell control receipts show `entries=0`; legacy/`r97set` receipts show `entries=72`. W10-rewrite exists only when slow files exist. This is pre-existing behaviour (r97 had the same gate at line 456), extended unchanged. |

Arithmetic check (recomputed from the counter's own parameters, scratch run):

| Fixture | real `4+T·(5+nd)` / ≤5M | +1 probe `4+T·(6+nd)` / ≤5M | Same side? |
|---|---|---|---|
| slow 600k nd1 (W01–03) | 3,600,004 in | 4,200,004 in | yes |
| mid 700k nd1 (W11) | 4,200,004 in | 4,900,004 in | yes |
| t900k nd1 (W14) | 5,400,004 out | 6,300,004 out | yes |
| mid4 700k nd4 (W15) | 6,300,004 out | 7,000,004 out | yes |
| edge 833333 nd1 (W17) | 5,000,002 out | 5,833,335 out | yes |
| **t800k nd1 (W18)** | **4,800,004 in (`invalid`)** | **5,600,004 out (`-`)** | **FLIPS** |
| **m520k4 nd4 (W19)** | **4,680,004 in (`invalid`)** | **5,200,004 out (`-`)** | **FLIPS** |

Both new cells sit strictly inside the +1 window (714,286 < T ≤ 833,332 at nd=1;
500,000 < T ≤ 555,555 at nd=4). A probe overcharging ≥+2 is caught with even larger
margin (2·800,000+4,800,004 > budget). The graded mutant is +1; the class is ≥+1.

## 3. Gaming attempts: can `--control --expect survived` print `survived=1` fraudulently?

Tried eight constructions. Read the cited lines; where stated, executed the counter's own
functions in scratch (imports only — no fixture runs needed beyond `build_fixtures` oracle).

- **G1 — Silent no-op mutant (anchor mismatch).** `apply_mutant` counts each anchor; ≠1 ⇒
  `CannotEvaluate` (lines 577–586). Main catches it and returns 2 (lines 697–699). Executed:
  empty anchor ⇒ `CannotEvaluate: mutant overcharge: anchor appears 0 times`; duplicate
  anchor ⇒ same. **Not gameable.** A mutant patch that does not apply is exit 2, never a
  silently-unmutated `survived=1`. (At 681c80a4 all five anchors occur exactly once.)
- **G2 — `--control --expect survived --mutant none`.** The usage guard (line 613) only
  rejects `mutant==none` *combined with* `expect==caught`. So `--control --expect survived
  --mutant none --cells new` runs and prints `survived=1` for the *real* probe. This is
  exactly line 1 of `c2-new-mutants.out` (`cells=6 cells_ok=6 mutant=none … survived=1`),
  which the plan requires as the baseline before the five mutant lines. It is a legitimate
  control row, **not** a forgery of the overcharge claim: the receipt is honest that
  `mutant=none` and `probe_sha256` is the unmutated probe's sha. It cannot be read as
  evidence about overcharge. **Honest, disclosed by the receipt itself.**
- **G3 — Empty selection (`survived = int(0 == 0) = 1`).** Arithmetically the CONTROL branch
  sets `survived=int(n_ok == n)` (line 656), so `n == 0` would give `survived=1`,
  `caught=0`, `ok=1`, return 0. **Unreachable via CLI:** `--cells` has four fixed choices
  (min 6 cells: `new`), `--expect-cell` out-of-set explicitly returns 2 (lines 660–664),
  and `evaluate_pass` filtering only removes cells not in the selected set. A forged
  counter edit could do it; that is out of scope (K1 voids the claim). This is the correct
  hardening demand: the counter *does* carry the vacuous-truth shape, but reachability is
  zero through any flags the predicate or the controls use. Flagged as the one latent
  fragility.
- **G4 — `--probe-file` override.** With `--probe-file`, `probe=override` and the printed
  `probe_sha256` is the sha of the supplied file's bytes *after* any `--mutant` patch
  (line 643). Nothing binds an override file to the `rev`. The plan discloses this as
  limit (g) ("grades an override probe bound only by probe_sha256") and the frozen
  predicate command does not use `--probe-file`. In control mode an operator could run a
  correct-arithmetic probe via `--probe-file` and report "survived" — but the receipt would
  say `probe=override`, and the sha chain (§4) shows the frozen receipts used `probe=rev`.
  **Disclosed, not a predicate hole.**
- **G5 — `--allow-clock` / wall-clock probes.** A probe containing `DEADLINE` raises
  `CannotEvaluate` unless `--allow-clock` (line 644–645) ⇒ exit 2. With `--allow-clock`
  it is explicitly the red control. The predicate doesn't pass it; if it tried without
  it, exit 2. **Closed.**
- **G6 — `--runs < 1`.** Explicit usage error, return 64 (lines 616–618). Control mode
  forces `runs=1` regardless. **Closed.**
- **G7 — Fixture oracle mislabel (t800k/m520k4).** `fixture_class` (lines 313–346)
  recomputes the step class from the written bytes; `build_fixtures` raises
  `CannotEvaluate` on any mismatch (lines 466–469). I executed the builder in scratch:
  ok (`fixture_class` agrees on both new fixtures) — the oracle labels them `invalid` as
  designed. A mislabel would exit 2, never silently grade `-`. **Closed.**
- **G8 — `--cells new` survival.** `--control --expect survived --cells new` with a buggy
  probe invisible on those 6 cells prints `survived=1` — by design; the predicate
  re-grades all 19 cells plus the loaded pass (which `--control` never runs: line 653).
  The predicate command has no `--control`, so byte-identical control output cannot be
  passed off as the predicate (different labels: `ROUTER_BUDGET98_CONTROL` vs
  `ROUTER_BUDGET98`). **Closed by label separation.**

Conclusion on the seat question: **no gaming path exists within the frozen command and
flags.** Every way to get `survived=1` without the intended arithmetic either exits 2/64,
is labelled in the receipt (`mutant=none`, `probe=override`, `expect=survived`), or
requires editing the counter (K1). The only residue is the unreachable vacuous-truth shape
(G3) and the disclosed override path (G4).

## 4. Exit codes: does `--control` return 0 on empty set or fixture failure?

No in both cases:

- `n == 0`: unreachable (G3). If it were reached, CONTROL would indeed return 0 — this
  is the latent shape worth a one-line `if n == 0: return 2` guard in a future round, but
  it is not reachable through `--cells` choices and no such option exists.
- Fixture build failure: `CannotEvaluate` ⇒ `return 2` (lines 697–699). `build_fixtures`
  oracle mismatch, missing `rev`, missing probe file, anchor failure, and `--expect-cell`
  out-of-set all land here. Exit-code map (identical in r97 and r98): `0` predicate met /
  control `ok=1`; `1` not met / mismatch; `2` could-not-evaluate; `64` usage.
- A *passing* control prints `exit:0` in the frozen receipts (both files end with `exit:0`).

## 5. Do the control receipts prove what the plan says?

Plan §C2-Controls: (i) `c2-legacy-mutants.out`: the 17 round-97 cells with the overcharge
mutant: `survived=1`. (ii) `c2-new-mutants.out`: six new cells with the real probe
`survived=1`, and with each mutant `--expect-cell` naming the cell that must redden,
each `cell_ok=0 caught=1`. Checked line by line:

- **Legacy receipt (18 lines).** All 17 cells `ok=1` (W01–W17 incl. W10-rewrite), CONTROL
  line: `cells=17 cells_ok=17 mutant=overcharge slow_files=72 runs=1 expect=survived …
  survived=1 caught=0 probe=rev … ok=1`. Proves exactly what §5(i) says: the old cell set
  cannot discriminate the +1 probe. No more, no less — the receipt is honest about being
  a *survival* proof.
- **New-mutants receipt (50 lines).** Seven CONTROL lines:
  - L7 `mutant=none expect=survived cells=6 cells_ok=6 survived=1` — real probe green on
    all six new cells (baseline; proves W18/W19 don't false-redden the real probe).
  - L14 `mutant=flat6 expect_cell=W15-700k-nd4 cell_ok=0 caught=1` (cells_ok=5; only
    W15 redden) — plan match.
  - L21 `mutant=undercharge expect_cell=W14-900k-nd1 cell_ok=0 caught=1` (cells_ok=3;
    W14, W15, W17 redden).
  - L28 `mutant=maxmeta expect_cell=W16-maxmeta cell_ok=0 caught=1` (cells_ok=5).
  - L35 `mutant=nopreamble expect_cell=W17-833333-nd1 cell_ok=0 caught=1` (cells_ok=5).
  - L42 `mutant=overcharge expect_cell=W18-800k-nd1 cell_ok=0 caught=1` (cells_ok=4;
    W18+W19 redden, W14–W17 green per-cell lines 36–39).
  - L49 `mutant=overcharge expect_cell=W19-520k-nd4 cell_ok=0 caught=1` (cells_ok=4).
  Every expect-cell matches the plan's kill-rule mapping. All lines `probe=rev` at
  `rev=681c80a4…`, `slow_files=72`, `runs=1`.
- **Sha chain (independent recomputation in scratch).** Applying the counter's own
  `apply_mutant` to the probe at `681c80a4` reproduces every `probe_sha256` in both
  receipts exactly (all six mutants, incl. none/overcharge/flat6/undercharge/maxmeta/
  nopreamble — see scratch output, "MISMATCH" count zero). The receipts are therefore
  genuine outputs of *this* counter against *this* probe bytes, not hand-written.
  This is the strongest evidence that the controls are honest.
- **What the receipts do *not* prove:** the loaded pass (controls are natural-only; the
  predicate must still show `load_stable=1` on `cells=19`), and no receipt has a
  predicate line yet (`measured/` is empty — measurement happens at M1/M2/M3). Any claim
  now in the present tense about `load_stable` would be unproven. `claims.json` correctly
  still says `"measured": "pending"` on C2.

## 6. Round-97 contract reconstructed (the invariant the counter must hold)

Highest-value reference for a future attack: the round-97 counter holds *one* invariant —
"a probe whose per-header charge is not exactly 5+nd flips at least one cell." Round 97
enforced the **upper** side (charges too little, or a flat 6, decide `invalid` where the
real probe grades `-`). The +1 probe is the only missed direction because no round-97
fixture was `(decidable, +1-undecidable)`. Round 98 closes it by adding exactly the
decidable-side pairs (W18, W19). The residual disclosed limits are real, not boilerplate:
non-header step charges (KV, string elements) are ungraded; the ctime memo shape is
unobservable (one parse per invocation); slow `/props` and the pass wall clock are routed,
not fixed. Do not attack those — they are outside the freeze.

## 7. Residual risk ledger

| # | Risk | Severity | Reachable? |
|---|---|---|---|
| R1 | Vacuous truth `survived=0==0` in CONTROL (line 656) | low | no (G3) — recommend a `n==0 → 2` guard next round |
| R2 | `--probe-file` unbound to rev | low | only if invoked (G4); disclosed, predicate doesn't |
| R3 | `--control --expect survived --mutant none` is a valid "survived" string | info | legitimate (G2), labelled in receipt |
| R4 | Counts: 19 vs "six new cells" naming | info | consistent: NEW_CELLS=6 by count, R97_CELLS=17, CELLS=19 |

No fabrication: every number above was recomputed or grep-verified in scratch; rejected
constructions are listed with the exit code that stops them.
