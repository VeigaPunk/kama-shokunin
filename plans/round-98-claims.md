# Round 98 — frozen claims (kama)

Base revision `681c80a4e3c745c22559f74b2c2a1917bdc66fc6` (lane `master` at round start, round-97
closed `ok` — all three claims verified, expansion unchanged, quality/discernment improved;
`corpus/lessons/round-97-verifier-spotcheck.md`). L1 `KamaR98`. Frozen in the commit that adds this
file together with the three counters it names and every freeze-time control, so "counter bytes
identical to the freeze commit" is checkable rather than asserted.

Closure history read before declaring (the three most recent kama closures, MANIFEST rounds indices
1532/1538/1559/1570 — r94 `ok` attempt 2, r95 `ok`, r96 `rejected-honest-stop`, r97 `ok`):
the standing failure class is still a frozen counter going green on a property narrower than the
claim's stated wording, with the falsifying artifact produced by the round's own wave before filing.
Round 97 admitted all three claims, but its own closing wave (RV03 F5) left one named window open:

- **the +1/header overcharge window.** A counter that grades only the budget's UPPER side can be met
  by a probe that charges one step extra per header (6+nd instead of 5+nd): RV03 R3 showed such a
  probe passes all 17 cells, because every fixture's +1 parse stays on the same side of MAX_STEPS
  as the real parse. The round-97 C1/C2 ceilings state 833,332/555,555 as binding; for the +1 probe
  they are false (its nd=1 verdict flips between 714,286 and 800,000 headers). Round 98 closes that
  window with cells whose real parse decides (`invalid`) and whose +1 parse cannot (`-`), plus the
  heading-count blindness the round-97 audit carried (its check 16 never read the section heading,
  so the live "three graded forgeries" heading passed while the body said four).

Axes (SCORECARD `## Axes`): operability 8, freshness 8, depth 7, coverage 9, calibration 7,
adjacency 7. Lowest non-retired: depth / calibration / adjacency (7). No stagnation waiver:
calibration and depth are below the 8 saturation line. **C1 works calibration**, **C2 works
operability** (the lane's assigned pair), **C3 works depth** — the same axis split as round 97, on
successor instruments. Claims are causally separable: C1 reads SCORECARD/SKILL/probe-comment/SOURCES;
C2 reads only `tools/kama-probe.sh` and its own fixtures; C3 reads only `SKILL.md`'s table, the
probe's `MAX_STEPS` and the registry rows. No probe behaviour changes: the probe bytes are the
instrument under claim, not a fix target.

## Receipts: freeze-time vs measurement-time

A measurement receipt is committed only after its producer exits.

- **Freeze-time (committed with this plan):** `controls/census-start.out`, `controls/c1-base.out`,
  `controls/c2-legacy-mutants.out`, `controls/c2-new-mutants.out`, `controls/c3-base.out`,
  `controls/sources-opened.out`.
- **Measurement-time (committed with M1/M2/M3):** `measured/c1.out`, `measured/c2.out`,
  `measured/c3.out`, `controls/census-end.out`.

## C1 — calibration (lowest axis, 7): the lane's graded self-assessments match the repo, heading included

**Predicate (one sentence, same in the counter's docstring and in the receipt label):**

`python3 tools/round98-self-assessment-audit.py --repo . --rev <M1>` prints
`SELF_ASSESS98 checks=20 mismatches=0 met=True rev=<resolved>` and exits 0 at the measured commit
M1; the counter's bytes never change after the freeze commit (kill rule K1).

- **Before (the defect).** (a) `SKILL.md`'s `### Round 97 correction` HEADING reads "the three
  graded forgeries" while the frozen round-97 population was four mutants and four cells (RV01 §2.1,
  fixed in the round-97 body prose by amendment 2 but never in the heading line); the round-97 audit
  cannot see it because `section()` excludes the heading at `start + 1`. (b) The round-97 body prose
  "four probe variants survive all 13 of its cells" and SCORECARD's depth row "four graded probe
  forgeries" describe only the round-97 mutants; after C2 adds the overcharge mutant and W18/W19
  they are false again unless rolled forward. (c) No surface names the overcharge mutant or W18/W19
  at base, so a self-assessment that omitted them would stay green.
- **After.** Twenty graded surfaces match: checks 1–18 are the round-97 eighteen carried forward
  (depth/adjacency rows, capability pointer, probe comment arithmetic and ceilings, §Round 96 table,
  S620/S621, round-96 identity and receipt needles, docstring constants, count agreement against the
  counter's own sets, unique SOURCES ids, the tensor-loop charge sites) with the count numbers
  rolled to six new cells / five mutants / `cells=19`; check 19 grades the heading's count word
  against the counter's parsed mutant count; check 20 names the overcharge surface (MUTANTS parses
  to five including `overcharge`; depth row and §Round 97 body name `overcharge`, W18 and W19).
- **Do-nothing control:** `controls/c1-base.out` — the same counter at base `681c80a4`. Expected
  `mismatches>0`, exit 1 (the heading word `three` vs five mutants; the count/docstring surfaces
  still name four/twenty-17; W18/W19 and `overcharge` absent everywhere). A green base run means
  the counter cannot discriminate and the claim is void.
- **Kill rules:** K1 the counter's bytes change after the freeze commit; K2 `mismatches>0` at M1;
  K3 the whole counter is green at base (the do-nothing control).
- **Disclosed limits.** The audit grades exactly the 20 named surfaces; other SCORECARD rows and
  prose elsewhere are not graded, and the wave's non-author read remains the semantic gate.

## C2 — operability (assigned axis): the budget counter grades the overcharge probe the 17-cell set misses

**Predicate:**

`python3 tools/round98-router-budget.py --repo . --rev <M2> --work <scratch> --slow-files 72`
prints `ROUTER_BUDGET98 cells=19 mismatches=0 positive_mismatches=0 load_cells=19 load_stable=1
budget=work …` and exits 0 at M2, and the control receipts print `survived=1` for the 17 round-97
cells under the overcharge mutant and `caught=1` for each new cell under its named mutant.

- **Before (the defect).** Round-97's closing wave (RV03 F5) proved a probe charging one extra step
  per header passes all 17 cells: every round-97 fixture's +1 parse is on the same side of
  MAX_STEPS as its real parse. Its true nd=1 ceiling is 714,285 headers, not 833,332. This round's
  new mutant is the +1/header overcharge (`overcharge`, a loop-top `steps[0] += 1` patch); the
  round-97 mutants are re-graded on the 19-cell set as regression.
- **After.** Two cells past the old set, both expecting the decidable verdict the overcharge probe
  cannot produce: **W18-800k-nd1** (800 000 headers at nd=1 → real 4 800 004 steps ≤ MAX_STEPS,
  `invalid`; +1 probe needs 4 + 7×800 000 = 5 600 004 → `-`) and **W19-520k-nd4** (520 000 at nd=4
  → real 4 680 004, `invalid`; +1 needs 5 200 004 → `-`). The mutants are byte patches of the probe
  under claim, anchored exactly once and refused when the anchor does not match; `--control
  --expect survived|caught --expect-cell <id>` names the cell that must redden. New cells are
  two-sided in the sense the round-97 four are not: they expect `invalid` (decidable), so a probe
  that stops charging entirely also reddens them (it decides `invalid` too — no: an undercharged
  probe still decides `invalid`, green; the overcharge probe decides `-`, red; the flat-6 probe
  charges 6/header → needs 4 800 004 at nd=1, stays `invalid`, green — the overcharge class is
  exactly the `+1` window 714,286 < T ≤ 833,332 at nd=1 and 500,000 < T ≤ 555,555 at nd=4, and both
  new cells sit strictly inside it).
- **Cells (19, frozen in the counter's docstring):** the 17 round-97 cells unchanged plus W18, W19;
  both host loads in the predicate; natural-only in the controls. `--cells r97set` selects the 17
  round-97 cells for the do-nothing control.
- **Do-nothing control:** two files. `controls/c2-legacy-mutants.out` — the 17 round-97 cells
  (`--cells r97set`) with the overcharge mutant: `survived=1` (the old set cannot discriminate).
  `controls/c2-new-mutants.out` — the six new cells with the real probe (`survived=1`) and with each
  mutant, `--expect-cell` naming the cell that must redden: flat6 → W15-700k-nd4,
  undercharge → W14-900k-nd1, maxmeta → W16-maxmeta, nopreamble → W17-833333-nd1,
  overcharge → W18-800k-nd1 (and W19-520k-nd4), each `cell_ok=0 caught=1`. A `cell_ok=1` receipt
  means the counter is void for that mutant.
- **Kill rules:** K1 the counter's bytes change after the freeze commit; K2 `positive_mismatches>0`
  or `load_stable=0` or `cells!=19` at M2; K3 any mutant's named cell is green on the new set or
  any round-97 cell is red on the old set.
- **Disclosed limits.** (a) The five named forgery classes are the graded ones; a probe that
  charges a wrong number of non-header steps (KV, string elements) is not graded. (b) The ctime
  memo component is not graded: the probe parses each path once per invocation, so no listing can
  rewrite an inode between two parses of one process — the shape is unobservable from the outside,
  not merely untested. (c) A slow `/props` answer still decides the verdict (r94 SC02 F4), routed
  again unchanged. (d) The pass-level wrapper is still a wall clock (SC01), routed unchanged.
  (e) The predicate command carries the host-speed parameter `--slow-files 72`; K1 binds the
  counter's bytes, not the command sentence. (f) W18/W19 expect `invalid`: they pin the overcharge
  class from the decidable side; they do not pin the budget's lower bound (W11 does, in the same
  run). (g) `--probe-file` grades an override probe bound only by `probe_sha256`; `--allow-clock`
  and `--runs < 1` are refused or excluded from the predicate.

## C3 — depth (lowest axis, 7): the step-budget boundary table grades the overcharge window rows

**Predicate:**

`python3 tools/round98-depth-boundary-audit.py --repo . --rev <M3>` prints
`DEPTH_BOUNDARY98 rows=8 checks=<c> mismatches=0 met=True rev=<resolved>` and exits 0 at M3;
`rows != 8` exits 1.

- **Before.** The round-97 table's six rows are all on the budget's far side (each is already `-`
  under the +1 probe — RV03 F5: the +1 probe stays green on every one). The table cannot answer
  "does this file decide?" for the overcharge window: 800 000 headers at nd=1 (real 4 800 004,
  `invalid`; +1 probe 5 600 004, `-`) and 520 000 at nd=4 (real 4 680 004, `invalid`; +1 probe
  5 200 004, `-`).
- **After.** `SKILL.md` §Round 97 correction carries eight boundary rows (the six round-97 rows
  unchanged, plus (800,000, nd=1) `invalid` and (520,000, nd=4) `invalid`), each with
  `steps = 4 + T x (5 + nd)`, the `<=`/`>` comparison against `5,000,000` and the verdict; it cites
  S620 (spec), S621 (the corrected code row) and S622 (the spec's header struct, opened this round,
  grounding the four preamble steps as the header struct's four fields).
- **Do-nothing control:** `controls/c3-base.out` — the same counter at base: the section carries
  six rows, so `rows=6` and `mismatches>0`, exit 1.
- **Kill rules:** K1 the counter's bytes change after the freeze; K2 any row's arithmetic or verdict
  does not recompute from the probe's `MAX_STEPS`; K3 a required row is missing.
- **Disclosed limit.** The table grades the eight named boundary classes and every row present in
  the section; it is not a proof over all `(T, nd)` pairs, which the per-rank ceiling formula
  already covers in the round-96 table. The overcharge window is one step of width per header; a
  probe overcharging by two or more steps is caught by the same cells (2×800 000 + 4 800 004 >
  6 400 000 both cells) — the graded mutant is +1, the class is ≥+1.

## Separability, sources, carried defects, frontier step

- **Sourced claim:** C3 rests on S622 (GGUF spec `57e2c2ca` header struct, `gguf_header_t`:
  magic/version/tensor_count/metadata_kv_count — the four preamble fields) and S620, both with the
  spec row S620 opened in round 97 and the header row opened this round; the Gate block carries
  digests and quotes. C1/C2 rest on the probe bytes (own-work instrument).
- **Frontier step (§2b):** census before → after recorded with
  `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`; rows 361 → 363
  (S622 admitted, S623 rejected). The lesson carries `## Gate` (one admit — S622 — and one reject —
  S623 — with every new row's URL/access date/quote) and `## Mistakes`. At least one sourced claim:
  C3 cites S622, opened this round.
- **Assimilation:** none from `merge/kama/` this round. `considerthese/2026-11-08.md` proposals are
  read this round; at most one still-unimplemented proposal will be mined as a lesson note or a
  QUALITY row citing `considerthese/2026-11-08.md` + date (proposal 1, the gate-receipt continuity
  check, is the candidate; its reflection is a pointer, not evidence).
- **Carried, not claimed:** R1 `round75-instruments` red (`APPEND_DEBT … bad_rows=19`, L0 r87/r89
  open); the `round78-instruments` red from the host's non-lane Ollama listener on 127.0.0.1:8080
  (re-checked this round); the slow `/props` verdict (r94 SC02 F4); the pass-level wall-clock
  wrapper (SC01); the ctime memo shape (unobservable, disclosed above); the round-97 C1 checks
  13–14 receipt-needle limit (RV01 §2.10, carried from the round-97 closure).
