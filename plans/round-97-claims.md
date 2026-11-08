# Round 97 — frozen claims (kama)

Base revision `40763bd2ca1e3f99881247eaa9f5e3ef3b596653` (lane `master` at round start, round-96
closed `rejected-honest-stop`). L1 `KamaR97`. Frozen in the commit that adds this file together with
the three counters it names, the corrected disclosures it measures and every freeze-time control, so
"counter bytes identical to the freeze commit" is checkable rather than asserted.

Closure history read before declaring (`corpus/lessons/round-96-verifier-spotcheck.md`): round 96 was
`rejected-honest-stop` because C3's stated sentence ("every disclosure the lane repeats matches the
bytes beside it") was falsified by the probe's ceiling comment and S618's `teaches` cell while the
frozen C3 counter stayed green — it *required* the false string. Seven defects were routed; this round
closes routed defects 1 (the false disclosure and the literal-presence counter), 2 (the `SHONEN`
re-filing, in the report), 3 (the identity restatement, in the counters' docstrings and the report)
and 6 (ledger width), and keeps 4/5/7 disclosed and routed.

Axes (SCORECARD `## Axes`): operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7.
Lowest non-retired: depth / calibration / adjacency (7). No stagnation waiver: calibration and depth
are below the 8 saturation line. **C1 works calibration**, **C2 works operability** (the lane's
assigned pair), **C3 works depth**. Claims are causally separable: C1 reads SCORECARD/SKILL/probe
comment/SOURCES; C2 reads only `tools/kama-probe.sh` and its own fixtures; C3 reads only `SKILL.md`,
the probe's `MAX_STEPS` and the two registry rows.

## Receipts: freeze-time vs measurement-time

A measurement receipt is committed only after its producer exits.

- **Freeze-time (committed with this plan):** `controls/census-start.out`, `controls/c1-base.out`,
  `controls/c2-legacy-mutants.out`, `controls/c2-new-mutants.out`, `controls/c3-base.out`,
  `controls/sources-opened.out`.
- **Measurement-time (committed with M1/M2/M3):** `measured/c1.out`, `measured/c2.out`,
  `measured/c3.out`, `controls/census-end.out`.

## C1 — calibration (lowest axis, 7): the lane's graded self-assessments match the repo

**Predicate (one sentence, same in the counter's docstring and in the receipt label):**

`python3 tools/round97-self-assessment-audit.py --repo . --rev <M1>` prints
`SELF_ASSESS97 checks=18 mismatches=0 met=True rev=<resolved>` and exits 0 at the measured commit
M1; the numbers are those of amendment 2, which strengthened the counter after wave 1 (RV01, CR01,
CR02).

- **Before (the defect).** (a) SCORECARD's live `depth` row declares `SKILL.md` sha256
  `340ef84b…` with 2254 lines and `grep -c '^## ' SKILL.md` → 58, while the tree at base has 2441
  lines and 59 sections and a different digest — three self-assessment cells that no longer describe
  the file; (b) the probe's ceiling comment states "the binding ceiling is 6 steps per tensor header"
  while the parser prices `5 + nd` (round-96 closure routed defect 1); (c) S618's `teaches` cell
  repeats the constant 6; (d) `SKILL.md` cites only S618, not the corrected row. The round-96 C3
  counter was green on all of this because check 1 required the exact string "6 steps per tensor
  header" (`tools/round96-disclosure-audit.py:57-60`).
- **After.** The 14 graded surfaces match: the probe comment states `5 + nd` and every per-rank ceiling derived from `MAX_STEPS`;
  `SKILL.md` cites S620 (spec) and S621 (append-only correction of S618) and carries all five
  ceilings; S621's `teaches` opens `supersedes S618 —` with the `5 + nd` arithmetic; SCORECARD's
  `depth` row matches the committed `SKILL.md` bytes; the round-96 identity and receipts quoted in
  SCORECARD are true.
- **Checks (18, frozen in the counter's docstring; amendment 2 added 4 and strengthened 3):** depth
  row digest / line count / section count; adjacency row exists with its digest / pipe count; the
  `router-byte-decided` capability row's pointer and "measured against" commits both ancestors, the
  pointer strictly earlier, both evidence paths present at the pointer; the probe's `5 + nd`
  sentence, no constant-6 sentence, and no "binding" line naming 1,000,000 or 6 steps/header; all
  five per-rank ceilings in the probe comment; the §Round 96 table's five rows recomputed; S621's
  supersession cell; S620's spec/A/mined cells; the round-96 identity and C1 receipt summary;
  the round-96 C2/C3 receipt needles; the two round-97 counters' docstrings against the probe's
  constants and the `4 + T x (5 + nd)` formula; the count statements (four cells/mutants, `cells=17`,
  W14–W17) in SCORECARD's depth row, SKILL §Round 97 and the counter docstring; SOURCES id
  uniqueness; the probe's tensor-loop and preamble charge sites.
- **Do-nothing control:** `controls/c1-base.out` — the same counter at base `40763bd2`. Expected
  `mismatches=10` with v2 (the stale depth cells, the capability row's relative evidence path, the
  constant-6 sentence and missing ceilings, the missing S620/S621 rows, and the count/docstring
  checks). A green base run means the counter cannot discriminate and the claim is void.
- **Kill rules:** K1 the counter's bytes change after the amendment-2 commit (the freeze the
  measurement binds to); K2 `mismatches>0` at M1; K3 the whole counter is green at base (the
  do-nothing control) — checks that were already true at base (the adjacency row, the round-96
  identity and receipts) are the claim's unchanged surfaces, not a discriminator (RV01 §2.9).
- **Disclosed limits.** The audit grades exactly the 14 named surfaces; other SCORECARD rows
  (the operability/freshness/coverage/calibration prose, the superseded rows, PROVINCE.md) are not
  graded, and the wave's non-author read remains the semantic gate. S618 stays `mined` as history
  (CORPUS.md rule 2: corrections are new rows).

## C2 — operability (assigned axis): the budget counter grades four probe forgeries the 13-cell set misses

**Predicate:**

`python3 tools/round97-router-budget.py --repo . --rev <M2> --work <scratch> --slow-files 72`
(amendment 1: the W03 host-speed parameter; the guard fired at 55.0 s with the default count)
prints
`ROUTER_BUDGET97 cells=17 mismatches=0 positive_mismatches=0 load_cells=17 load_stable=1 budget=work …`
and exits 0 at M2; and the three control receipts print `survived=1` for the 13 legacy cells and
`caught=1` for the three new cells, one per mutant.

- **Before (the defect).** Round-96's closing wave (MT01 G1) proved four probe variants survive
  every one of the 13 cells because every fixture's complete parse is also `-`: the unbounded
  budget, per-header charging removed, `MAX_META` lowered to 100 MiB, and the ctime memo component
  removed. Round-96's W13 closed only the unbounded-budget class; a green 13-cell receipt therefore
  did not prove the disclosed arithmetic. This round's four graded mutants are the per-header
  removal (`undercharge`), a constant 6 steps/header (`flat6`), the 100 MiB cap (`maxmeta`) and a
  preamble-drop (`nopreamble`, this round's own shape); the ctime shape is unobservable.
- **After.** Four cells past the old set: **W14-900k-nd1** (900 000 headers at nd=1 → 5 400 004
  steps > `MAX_STEPS`, `-`) catches a probe that stopped charging per header; **W15-700k-nd4**
  (700 000 at nd=4 → 6 300 004 steps, `-`) catches a constant-6 probe (4 200 000 → `invalid`);
  **W16-maxmeta** (160 MiB KV string + a bad tensor → `invalid` at 512 MiB) catches the 100 MiB cap;
  **W17-833333-nd1** (833 333 headers at nd=1 → 5 000 002, `-`) catches a probe that does not charge
  the four preamble steps (4 999 998 → `invalid`).
  The mutants are byte patches of the probe under claim, anchored exactly once and refused when the
  anchor does not match; `--control --expect survived|caught` gives the survival and catch receipts.
- **Cells (17, frozen in the counter's docstring):** the 13 round-96 cells unchanged plus W14, W15,
  W16, W17; both host loads in the predicate; natural-only in the controls.
- **Do-nothing control:** two files. `controls/c2-legacy-mutants.out` — the 13-cell set with each
  of the four mutants: `survived=1` (the old set cannot discriminate). `controls/c2-new-mutants.out`
  — the four new cells with the real probe (`survived=1`) and with each mutant, `--expect-cell`
  naming the cell that must redden: `flat6` → W15-700k-nd4, `undercharge` → W14-900k-nd1,
  `maxmeta` → W16-maxmeta, `nopreamble` → W17-833333-nd1, each `cell_ok=0 caught=1`. A
  `cell_ok=1` receipt means the counter is void for that mutant.
- **Kill rules:** K1 the counter's bytes change after the amendment-2 commit; K2
  `positive_mismatches>0` or `load_stable=0` or `cells!=17` at M2; K3 any mutant's named cell is
  green on the new set or any legacy cell is red on the legacy set.
- **Disclosed limits.** (a) The four named forgery classes are the graded ones; a probe that
  charges a wrong number of steps inside a single header (not preamble, header, dims, or cap) is not
  graded, and a probe that reddens a different cell is not credited to the named one (the control
  names its cell). (b) The ctime memo component is not graded: the probe parses each path once
  per invocation, so no listing can rewrite an inode between two parses of one process — the shape is
  unobservable from the outside, not merely untested. (c) A slow `/props` answer still decides the
  verdict (r94 SC02 F4), routed again unchanged. (d) The pass-level wrapper is still a wall clock
  (SC01), routed unchanged. (e) The predicate command carries amendment 1's `--slow-files 72`;
  K1 binds the counter's bytes, not the command sentence. (f) The four new cells are one-sided
  (three expect `-`), so their `survived=1` alone does not pin the budget's lower bound; the
  predicate's legacy W11 does, in the same run. (g) `--probe-file` grades an override probe bound
  only by `probe_sha256`; `--allow-clock` and `--runs < 1` are refused or excluded from the
  predicate (amendment 2 addendum).

## C3 — depth (lowest axis, 7): the step-budget boundary table states the two rank classes

**Predicate:**

`python3 tools/round97-depth-boundary-audit.py --repo . --rev <M3>` prints
`DEPTH_BOUNDARY97 rows=6 checks=10 mismatches=0 met=True rev=<resolved>` and exits 0 at M3;
`rows != 6` exits 1 (amendment 2).

- **Before.** The round-96 table states the per-rank ceilings but not the two boundary classes the
  round-97 counter grades, and its prose cannot answer "does this file decide?" for the named files
  (900 000 tensors at nd=1; 700 000 at nd=4). The reader must re-parse the probe.
- **After.** `SKILL.md` §Round 97 correction carries six boundary rows for a KV-free file at rank
  ≤ 4 (KV work charges ≥4 steps per entry; `nd > 4` is `invalid` before pricing) — (833,332, nd=1) `invalid`,
  (833,333, nd=1) `-`, (900,000, nd=1) `-`, (700,000, nd=4) `-`, (555,555, nd=4) `invalid`,
  (555,556, nd=4) `-` — each with `steps = 4 + T x (5 + nd)`, the `<=`/`>` comparison against
  `5,000,000` and the verdict; it cites S620 (spec) and S621 (the corrected code row).
- **Do-nothing control:** `controls/c3-base.out` — the same counter at base: the section is absent,
  `rows=0` and `mismatches>0`, exit 1.
- **Kill rules:** K1 the counter's bytes change after the freeze; K2 any row's arithmetic or verdict
  does not recompute from the probe's `MAX_STEPS`; K3 a required row is missing.
- **Disclosed limit.** The table grades the six named boundary classes and every row present in the
  section; it is not a proof over all `(T, nd)` pairs, which the per-rank ceiling formula already
  covers in the round-96 table.

## Separability, sources, carried defects, frontier step

- **Sourced claim:** C1 and C3 rest on S620 (GGUF spec @ ggml `57e2c2ca`) and S621 (`ggml.h` @
  b12177, supersedes S618), both opened this round; the Gate block carries the digest and quote.
- **Frontier step (§2b):** census before → after recorded with
  `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`; rows 358 → 361
  (S619 rejected, S620 admitted, S621 correction of S618). The lesson carries `## Gate` (two admits — S620 and the S621
  correction — and two rejects — S619 and the 404 path — with every new row's URL/access date/quote) and `## Mistakes` M1–M4.
- **Assimilation:** none from `merge/kama/`; `considerthese/2026-11-07.md` proposal 3 is mined as
  `QUALITY.md` KQ152 (a file-identity memo is not frozen without a mutation receipt).
- **Carried, not claimed:** R1 `round75-instruments` red (`APPEND_DEBT … bad_rows=19`, L0 r87/r89
  open); the `round78-instruments` red from the host's non-lane Ollama listener on 127.0.0.1:8080
  (re-checked this round: still listening); the slow `/props` verdict (r94 SC02 F4); the pass-level
  wall-clock wrapper (SC01); the ctime memo shape (unobservable, disclosed above).
