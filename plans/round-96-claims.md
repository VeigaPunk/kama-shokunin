# Round 96 — frozen claims (kama)

Base revision `5d43528badc31ad6c0ca1848c00561f531924e4d` (lane `master` at round start,
round-95 admitted). L1 `KamaR96`. Frozen in the commit that adds this file together with the three
counters it names, so "counter bytes identical to the freeze commit" is checkable rather than asserted.
Every control named below is committed in that same commit.

Closure history read before declaring (`corpus/lessons/round-95-verifier-spotcheck.md`): round 95 was
admitted on narrowed claims — C1's wide sentence ("verdict is a function of the bytes") was falsified by
its own wave and filed only on three properties. The spot-check routed six defects to round 96; this
round's three claims close five of them with separable measurements and keep the sixth (slow `/props`,
r94 SC02 F4) disclosed and routed again, unchanged.

Axes (SCORECARD `## Axes`): operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7.
Lowest non-retired: depth / calibration / adjacency (7). **C2 works depth**, **C3 works calibration**,
**C1 works operability** (the lane's assigned axis pair). No axis is claimed as improved by speed; C1
claims decisiveness only.

## Receipts: freeze-time vs measurement-time

Round-95's M4 defect was a receipt committed while its producer was still writing it. This plan therefore
separates receipts again, and a measurement receipt is committed only after its producer exits:

- **Freeze-time (must exist at F, committed with this plan):** `controls/census-start.out`,
  `controls/c1-base.out`, `controls/c2-base.out`, `controls/c3-base.out`, `controls/sources-opened.out`.
- **Measurement-time (committed with M1/M2/M3, named in LOG.md and the report, never required at F):**
  `measured/c1.out`, `measured/c2.out`, `measured/c3.out`, `census-end.out`.

## C1 — operability: the step budget decides 700 000-tensor files, and the instrument cannot pass without load evidence

**Predicate (one sentence, same in the counter's docstring and in the receipt label):**

`python3 tools/round96-router-budget.py --repo . --rev <M1> --work <scratch>` prints
`ROUTER_BUDGET96 cells=12 mismatches=0 positive_mismatches=0 load_cells=12 load_stable=1 budget=work probe=rev …`
and exits 0 at the measured commit M1, the counter's bytes identical to this freeze commit.

- **Before.** (a) Round-95 SC02 F1 (amendment 4): the tip spends **6 steps per tensor header**, so a
  700 000-tensor file needs 4 200 000 steps > `MAX_STEPS` (4 000 000) and grades `-` (undecidable →
  loadable): the probe graded `MODEL_OK/router-unloaded-autoload` for all such fixtures while the router
  oracle reported failure. The effective tensor ceiling was ≈666 666, not the `MAX_TENSORS = 1 000 000`
  the plan's disclosed limit (a) named — a false sentence in committed code. (b) CR01 DEFECT-3: with
  `--skip-load` the counter set `loaded = natural`, so the summary still printed `load_cells=10
  load_stable=1` with no second pass — a receipt that misstates what ran. (c) CR01 DEFECT-1: `KILL = 400`
  was tighter than the probe's own derived pass limit for W03 (`20 + 25 * 40 = 1020` s), so one last cell
  could never finish.
- **After.** `MAX_STEPS` is raised to 5 000 000, so a 700 000-tensor header (6 × 700 000 = 4 200 000
  steps) parses to a decision. The probe's disclosed-limit comment is corrected to the arithmetic the
  code actually enforces (6 steps per tensor header; ceiling ≈833 333 tensor headers) and cites S618
  (below). The counter: `KILL = 1200` s (above the worst-case derived limit 1020 s + read overhead);
  with `--skip-load` the summary prints `load_cells=0 load_stable=0 load_note=skipped` and the predicate
  cannot be met (exit 1 always); the frozen docstring states `20 + 25 * npaths` (routed defect 3).
- **Cells (12, frozen in the counter's docstring):** W01 slow×1, W02 eight distinct slow, W03 forty
  distinct slow (the load-independent discriminator: the round-95 probe truncates / un-decides W03's
  slow files at its `MAX_STEPS`), W04 valid×8, W05 seven slow then one valid, W06 missing×8, W07 forty
  distinct fast invalid, W08 eight hard links to one slow inode, W09 a file declaring 1 200 000 tensors
  (disclosed `-`), W10 a same-size in-place rewrite with mtime restored (ctime key), **W11-700k** one
  700 000-tensor file with no data section → `MODEL_UNLOADED/router-model-invalid`, **W12-strings** a
  file whose string-array element count exceeds `MAX_STEPS` → `MODEL_OK/router-unloaded-autoload`
  (disclosed `-`, exercises the step budget's far side).
- **Do-nothing control:** `controls/c1-base.out` — the same counter at the round-95 tip revision
  `5d43528badc31ad6c0ca1848c00561f531924e4d` with `--burners 0` (two natural passes; with `--skip-load`
  the predicate is structurally unreachable). It must redden W11 (the 700 000-tensor file grades
  `MODEL_OK`, not `MODEL_UNLOADED`). A green base run means the counter cannot discriminate and the claim
  is void. Receipt committed with this plan.
- **Kill rules:** K1 `mismatches>0` or `load_stable=0` or `cells!=12` at M1; K2 a harm suite regresses
  against the base harm receipt the M1 commit carries (same suite list as round 95); K3 the counter
  changes after this commit.
- **Disclosed limits (before data).** (a) A candidate whose declared tensor count exceeds `MAX_TENSORS`
  or that needs more than `MAX_STEPS` stays `-` (undecidable → loadable) — W09/W12 grade that as the
  disclosed expectation, not as a fix. (b) The ceiling ≈833 333 is derived from 6 steps per tensor
  header; KV/string work also charges steps, so the effective ceiling is slightly lower — the comment
  says so. (c) A slow `/props` answer still decides the verdict (r94 SC02 F4) — routed, not claimed.
  (d) The pass-level wrapper is still a wall clock (SC01) — routed, not claimed.

## C2 — depth (lowest axis, 7): the step-cost table names the ceiling the code enforces

**Predicate:**

`python3 tools/round96-depth-audit.py --repo . --rev <M2>` prints
`DEPTH_AUDIT checks=<c> mismatches=0 met=True` and exits 0 at the measured commit M2, the counter's bytes
identical to this freeze commit.

- **Before.** SKILL.md §Round 95 names a ceiling of 1 000 000 tensors that the code never enforced (the
  binding ceiling was ≈666 666 at 6 steps per tensor header), and no section states the per-header step
  cost as a table a reader can act on without re-reading the parser. Depth needs: decision figures
  with real thresholds and a named error signature in the prose, not only in code.
- **After.** SKILL.md gains a §Round 96 correction carrying the step-cost table (tensor header = 6
  steps: name `u64`+skip 2, `nd` `u32` 1, dims `u64` 1, `tt`+offset 2; `MAX_STEPS` 5 000 000; ceiling
  ≈833 333 headers; 700 000-tensor file worked example; error signature `-` = undecidable →
  loadable), citing S618.
- **Do-nothing control:** `controls/c2-base.out` — the same counter at the base revision 5d43528b:
  the step-cost table does not exist and the ceiling sentence still says 1 000 000 — `mismatches>0`,
  exit 1. Receipt committed.
- **Kill rules:** K1 the counter changes after this commit; K2 the table's arithmetic no longer matches
  the probe's constants; K3 S618 does not resolve with `status` not `rejected`.
- **Sourced:** S618 (`ggml/include/ggml.h` @ b12177) and S619 (`gguf-py/README.md` @ b12177), both
  opened this round, ground the GGUF header layout the step table prices. The gguf.cpp reconsideration
  (already S129) is rejected as a duplicate.

## C3 — calibration: every disclosure the lane repeats matches the bytes it sits beside

**Predicate:**

`python3 tools/round96-disclosure-audit.py --repo . --rev <M3>` prints
`DISCLOSURE_AUDIT checks=<d> mismatches=0 met=True` and exits 0 at the measured commit M3, the counter's
bytes identical to this freeze commit.

- **Before (the defect).** The spot-check routed two filing defects: the probe's disclosed-limit
  sentence named a ceiling the code did not enforce (amendment 4 F1), and the SCORECARD
  `router-byte-decided` capability row cites evidence at `f6325660` (the first revision) while the claim
  was filed at M1b `c810f51e` — a stale evidence pointer though the tip receipt is green. The
  round-95 counter's frozen docstring still printed `20 + 15 * ncand` while the probe used
  `20 + 25 * npaths`.
- **What the counter grades.** (1) the corrected ceiling sentence in the probe's comment agrees with the
  `MAX_STEPS` value in the probe's bytes at that revision (6 steps per tensor header); (2) the new
  counter's docstring formula (`20 + 25 * npaths`) matches the shell wrapper's literal; (3) the
  `router-byte-decided` capability row's evidence commit resolves as a git object and lies at or before
  the tip (no pointer to a revision that never landed). C1's counter bytes are immutable after F, so
  the docstring check binds against `tools/round96-router-budget.py` at F.
- **Do-nothing control:** `controls/c3-base.out` — the same instrument at the base revision 5d43528b:
  the old ceiling sentence still present, the old evidence pointer still stale — `mismatches>0`, exit 1.
  Receipt committed.
- **Kill rules:** K1 `mismatches>0` at M3; K2 the counter changes after this commit; K3 a check is
  true of the base revision too (the instrument cannot discriminate).
- **Disclosed limit.** The audit grades consistency of filings with the bytes beside them, not the
  truth of each filing's prose; the wave's non-author read remains the semantic gate.

## Separability, sources, carried defects, frontier step

- C1's counter reads only `tools/kama-probe.sh`; C2's reads `SKILL.md`, the probe's constants and
  the S-rows; C3's reads the probe's comment, the frozen counter's bytes and the SCORECARD capability
  rows. Each verifies with the others unlanded (C2/C3 check consistency of filings with the bytes at
  whatever revision they are run against; they do not depend on M1's verdicts).
- **Sourced claim:** C2 (S618, S619 opened this round).
- **Frontier step (§2b):** `corpus/SOURCES.md` census before → after is recorded with
  `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`; the lesson
  `corpus/lessons/round-96.md` carries `## Gate` (each new row's URL, access date and ≤25-word located
  quote, plus one rejection) and `## Mistakes` (class · evidence · captured-by · fix). Rows: 357 →
  359 at the time of writing.
- **Carried, not claimed:** R1/D2 `round75-instruments` red (`APPEND_DEBT … bad_rows=19`, L0 r87/r89
  open); the `round78-instruments` live-reconcile red caused by the host's non-lane Ollama listener on
  8080; the slow `/props` verdict (r94 SC02 F4, still live); the pass-level wrapper is still a wall
  clock (SC01).
