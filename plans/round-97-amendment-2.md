# Round 97 — amendment 2 (wave-1 findings: the live count defect, the prose surfaces, the class caveats)

Recorded `2026-11-08` after wave 1 landed and before the round's measurements were re-taken. Trigger
artifacts (this round's own wave, under `.ufo/waves/round-97/w1/out/`):

- **`RV01SelfAssess/RV01SelfAssess.md` §2.1 (BLOCKER)** — the lane repeats "three graded probe
  forgeries" while the frozen C2 population is four cells (W14–W17) and four mutants; C1 is green on
  the false count. §2.2–§2.4, §2.5–§2.12: three false-self-assessment shapes pass, counter docstrings
  are ungraded, the capability pointer accepts any ancestor, S621 last-wins, a deleted adjacency file
  passes with the empty digest, and the receipts are not revision-bound.
- **`CR01Boundary/CR01Boundary.md`** — the §Round 97 file-level sentence is false for files with KV
  entries (KV work charges ≥4 steps) and for rank > 4 (the probe returns `invalid` before pricing);
  the counter hardcodes `PREAMBLE = 4` and `5 + nd`; a seventh correct row still exits 0.
- **`CR02Wording/CR02Wording.md`** — clause-by-clause: C1 is green on a probe whose comment states
  `5 + nd` while the parser charges a flat 6; C2's control sentence says "three" of four; the
  `caught=1` predicate is ∃-red, not the named cell; C3's "six rows" is not enforced.

## Corrections (the frozen sentence is narrowed to what the instrument enforces, never widened)

**A. The live count defect (BLOCKER).** The lane's own self-assessments are corrected to four:
`SCORECARD.md` depth row, `SKILL.md` §Round 97, `tools/round97-router-budget.py`'s docstring, and
`plans/round-97-claims.md`'s remaining "three" sentences. The wave brief's "16 cells" (the dispatch
`context`, taken before W17 landed) is disclosed in the report as a pre-freeze count; the dispatch
is not rewritten.

**B. C1 counter v2 (`tools/round97-self-assessment-audit.py`, 18 checks).** Added or strengthened,
each answering a named artifact:

- checks 7–8: the probe comment must carry **all five** ceilings (nd = 0..4), and **no line that says
  "binding" may name 1 000 000 or 6 steps/header** (RV01 §2.2 A1–A3; CR01's KV-free class is separate).
- check 9: scoped to the §Round 96 correction section and its five table rows recomputed from
  `MAX_STEPS` (RV01 §2.8 D7b).
- check 15: the two round-97 counters' docstrings state the probe's `MAX_STEPS`, `MAX_META` and the
  `4 + T x (5 + nd)` formula (RV01 §2.3 B1).
- check 16: the count statements agree with the counter's sets — SCORECARD's depth row, SKILL's
  §Round 97 and the counter docstring each name W14–W17 and say four, checked against
  `len(NEW_CELLS)` and `len(MUTANTS)` parsed from the counter source (RV01 §2.1 D4/D6b).
- check 17: SOURCES ids are unique (RV01 §2.5 E3) and the adjacency file exists before its digest is
  compared (RV01 §2.6 E1b).
- check 18: the capability row's **both** commits are ancestors, the pointer strictly precedes the
  graded revision, and **both** evidence paths exist at the pointer (RV01 §2.4 C1/C2/C3b).
- check 19: the probe's tensor loop charges exactly the declared four call sites
  (`skip(u64())  # name`, `nd = u32()`, `ne = [u64() for _ in range(nd)] or [1]`,
  `tt, off = u32(), u64()`) and no other `need`/`rd`/`u64`/`u32`/`skip` call (RV01 §2.2; CR02 clause 5;
  a flat-6 or 6+nd parser fails the set equality).
- output line gains `rev=<resolved>` (RV01 §2.12), so the receipt is revision-bound by content.
- kill rule K3 is restated: it fires when the **whole counter** is green at base (the do-nothing
  control), not per check — checks 4–5/12–14 were already true at base and are the claim's
  "unchanged surfaces" (RV01 §2.9).
- disclosed limit added: checks 13–14 grade the receipt needles, not every quoted number (RV01 §2.10).

**C. C3 counter v2 (`tools/round97-depth-boundary-audit.py`) and SKILL prose.**

- The audit exits 1 unless `rows == 6` (CR02 C3 clause 1; CR01's seventh-row fixture) and prints
  `rev=`.
- `SKILL.md` §Round 97 states the class the rows cover: **a KV-free file at rank ≤ 4**; KV work
  charges ≥4 steps per entry and rank > 4 returns `invalid` before pricing (CR01 §1). The table rows
  are unchanged and still recompute.
- The audit requires the section to state the KV caveat and the rank bound (literal tokens `KV` and
  `nd > 4`), and cites S620/S621 there.
- The claim sentence is narrowed to: the six rows recompute from the probe's `MAX_STEPS` and the
  declared `5 + nd` formula for the KV-free, rank ≤ 4 class; it does not certify the parser's charge
  (check 19 and C2's W14/W15 do that for the probe's behavior).

**D. C2 counter v2 (`tools/round97-router-budget.py`).**

- Docstring counts corrected to four cells / `cells=17`.
- New `--expect-cell <id>` for controls: `caught` now means the **named** cell is red (flat6 → W15,
  undercharge → W14, maxmeta → W16, nopreamble → W17), and `survived` on the legacy set stays
  "every selected cell ok". The receipt prints `expect_cell=… cell_ok=…` (CR02 C2 clause 4).
- The claim's control sentence is restated as **two control files, four mutants**, and `caught=1`
  means the named cell is red; other red cells are listed, not claimed.
- The predicate sentence is restated with the amended command (`--slow-files 72`, amendment 1).
- K1 is restated to bind the **counter's bytes**; the predicate command is a separate, amended
  sentence.

**E. Receipts.** All control and measured receipts are re-produced by the amended bytes at the
amendment commit; the earlier C2 measured receipt (`controls/c2-could-not-evaluate.out`) is kept as
the record of the host-speed refusal. The C1/C3 base controls are re-run with v2 (the base mismatch
count may change; the receipt is what v2 prints at `40763bd2`).

**F. Frozen sentence, cells and targets.** C1's target is restated as "the 18 named surfaces"; C2's
target is unchanged (`cells=17 mismatches=0 positive_mismatches=0 load_stable=1`) with the amended
command; C3's target is unchanged (`rows=6 mismatches=0 met=True`). No target is widened. No claim is
withdrawn.

## Amendment 2 addendum (same day, after the remaining wave seats settled)

The seats that landed after the first amendment draft (RV02BudgetCells, MT01Forgeries, RV03Intent,
EX01SelfAssessControl, EX02BudgetControl) found three more defects in the C2 counter and two in its
receipts, all repaired here before any claim measurement:

- **The `nopreamble` patch was a fixed point** (RV02 F2, MT01 F2): `steps[0] += 0 if steps[0] < 4
  else 1` never increments from zero, so the mutant charged **no** steps and was an
  `undercharge`-class probe, not a preamble drop (its receipt reddened W14/W15/W17). The patch now
  counts calls independently (`calls[0] += 1; steps[0] += 0 if calls[0] <= 4 else 1`); measured:
  the true drop reds **only** W17 (`cells_ok=3`), the isolating shape RV02's shape A described.
- **`--runs 0 --allow-clock` printed the frozen summary and exited 0 with no probe graded** (RV03
  F2/F6): `all([])` is true and `--allow-clock` disables the margin guard. `--runs < 1` is now a
  usage error (exit 64), and both summaries print `runs=<n>`.
- **The receipts could not prove their own command** (RV02 F4): the W03 cell label said `x40` at 72
  entries and the summary did not echo `--slow-files`. Cell details now print `entries=<n>` and the
  summaries print `slow_files=<n> runs=<n>`.
- **`KILL = 1200` was below the derived pass limit for 72 paths** (`20 + 25 x 72 = 1820 s`, RV02 F7):
  raised to 3600.
- **Stale `1.5 x` guard sentence** (RV02 F3, RV03 F10): the docstring now states 1.25, the value the
  code enforces.
- Disclosed, not repaired: `--probe-file` grades arbitrary bytes and the four new cells are
  one-sided (three expect `-`); the lower bound is pinned by legacy W11 in the same predicate run,
  and an override probe is bound only by `probe_sha256` (RV03 F4/F5, MT01 F3).

Amendment 1's "before any C2 cell scored" is corrected to "before any cell's verdict counted toward
the claim": the exit-2 run printed natural cells `ok=1` but scored no `mismatches`/`positive` value
and never ran the load pass (RV02 F8).
