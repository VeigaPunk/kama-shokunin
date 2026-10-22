# ConnMetrics — round-24 falsify lane: independent before/after counting command

**Verdict: HOLDS (one output-schema defect found; one number-discipline correction
recorded).** The 47-cell manifest and the candidate's amended-view score are
mutually consistent, and the "restored verdicts" can be separated from
"unchanged exit-2 with a corrected reason" by a command that recomputes every
number from the recorded rows instead of trusting the grid runner's summary
fields. No grid run was executed in this lane: every number below is
recomputed from retained artifacts (see §7 *Observed vs inferred* and §9
*Unverified*).

---

## 1. The counting command

```
python3 .ufo/waves/round-24/falsify/out/ConnMetrics/promisor-grid-count.py \
    --before   <grid.json> --before-arm frozen \
    --after    <grid.json> --after-arm current \
    [--manifest tests/report-audit/promisor-grid-expectations.json] \
    [--cells-out cells.tsv] [--json]
```

* `<grid.json>` is the document written by
  `python3 tests/report-audit/promisor-grid.py --arm both --json --out DIR`
  (file `DIR/candidate.json`), or any such document. `--before` and `--after`
  may be the **same** file: the runner always grades the r23 base blob in the
  `frozen` arm, so one both-arms document already carries before *and* after.
* Exit 0 = the count was produced; exit 2 = `could-not-evaluate:` on stderr
  (missing arm, unreadable document, two arms graded against different
  expectation manifests, disjoint cell sets).
* `--selftest` checks the bucket classifier over synthetic rows (5/5 ok).
* The command is deterministic: cells are sorted by name, all counts are
  integers, no timestamps, no network, no subprocess, no git.

**What it computes (and what it refuses to compute).** It never uses the
runner's `amended_view_met` / `amended_view_unmet` summary fields for a
verdict (see §3), and it never derives the exit-2 *form* check from the
recorded stderr, because a row keeps only the last 300 characters of stderr
(§3.2). Every verdict it reports is either the runner's own per-row flag
(where the row carries one) or a recomputation from the raw observations
(exit, kinds, defects, reason class, traceback/timeout/leak flags,
object-acquisition flag).

---

## 2. Data walk: the 47 manifest cells

Manifest `tests/report-audit/promisor-grid-expectations.json`, schema
`kama-promisor-grid-expectations/2`, sha256
`d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`
(byte-identical to `.ufo/waves/round-24/build/out/GridOracle/promisor-grid-expectations.json`).

| what | observed |
|---|---|
| graded cells | 47 (`PG01`–`PG39`, `PG41`–`PG48`) |
| row classes | 30 `policy` + 17 `control` |
| open (ungraded) row | `PG40-missing-cited-unselected-branch-object-promisor` — reported, never graded; excluded from every count here |
| declared twin pairs | 25 |
| views | `frozen` (r23 base history), `original` (the withdrawn registration), `amended` (live policy) |
| cells carrying an `amended` override | 10 (PG22, PG23, PG24, PG28, PG30, PG34, PG37→null, PG41, PG46, PG47) |
| effective expectation (amended, else original) | 20 × exit 0, 13 × exit 1, 14 × exit 2 |
| reason classes in the effective view | `unavailable` on all 14 exit-2 cells; `null` on the other 33 |
| frozen column | 30 policy cells expect exit 2 / reason class `metadata`; controls 7 × exit 0, 6 × exit 1, 4 × exit 2 (`unavailable`) |
| population sha256 | `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` |

Arithmetic check of the effective view (manifest data, no run): policy
13/8/9 (exit 0/1/2), control 7/5/5 → 20/13/14 = 47.

---

## 3. Data walk: the output schema

Runner `tests/report-audit/promisor-grid.py` at the pinned revision, sha256
`b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa`.

```
doc     : arms, auditor_sha256, expectations_sha256, frozen_revision, grid,
          open_rows, population_sha256, population_size, timeout_seconds
doc.arms.<arm> : rows, graded, violations, violating_cases,
          amended_view_met, amended_view_total, amended_view_unmet,
          withdrawn_original_failures, twin_pairs_in_manifest, twin_compared,
          twin_pairs_compared, twin_mismatch, tracebacks, timeouts,
          harness_leaks
doc.arms.<arm>.rows[i] : arm, case, kind, row_class, exit, met, met_frozen,
          met_original, met_amended, met_amended_frozen, kinds, defects,
          raw_kinds, raw_defects, expected_exit, expected_kinds,
          expectation{frozen,original,amended}, document, twin, twins,
          twin_equal, traceback, timed_out, leaked, objects_acquired,
          stderr_tail
```

### 3.1 Defect — the current-arm summary fields are structurally constant

`promisor-grid.py:1034-1043` computes

```python
baseline = [r for r in graded
            if r["arm"] == "frozen" and r["met_amended_frozen"]]
...
"amended_view_met":   len(baseline),
"amended_view_total": len(graded),
"amended_view_unmet": sorted(r["case"] for r in graded
                             if r["arm"] == "frozen" and not r["met_amended_frozen"]),
```

The filter pins `arm == "frozen"`, so in the **current** arm's block the
three fields are always `0`, `47` and `[]` — for every run, met or not.
Observed in the recorded candidate run (all 47 cells met, `violations: 0`):
`amended_view_met = 0`, `amended_view_unmet = []`. A reader who quotes
`amended_view_met` as the candidate's amended score quotes **0/47 for a
perfect run**. The current arm's amended score exists only as the per-row
`met_amended` flags; the counter in §1 recomputes it.

Minimal correction (not applied — read-only lane): report the current arm's
score from its own rows, e.g. add
`"amended_view_met_current": sum(1 for r in rows if r["arm"] == "current" and r["met_amended"])`
and the matching `amended_view_unmet_current`, or make the three fields
arm-local. The manifest (`d86b7bea…`) needs no change.

### 3.2 Second schema limit — the exit-2 form check is not re-derivable

A row keeps `stderr_tail = err.strip()[-300:]`. For the candidate's refusals
the tail starts mid-message, so the `could-not-evaluate:` prefix and the
full reason are gone; `document` only records the *absence* of a verdict
document. Consequence: an independent auditor can recompute exit, kinds,
defects and the reason *class* from a row, but cannot re-derive the
current-arm form pin (prefix / no-document / not-the-metadata-refusal /
names-the-unavailable-object). That part is only trustworthy through the
runner's own `met_amended` flag. The counter therefore never re-derives it
and says so.

### 3.3 Runner version matters for the baseline number

Two runner versions exist in the tree:

| runner | sha256 | exit-2 naming pin |
|---|---|---|
| `tests/report-audit/promisor-grid.py` (integrated at the pinned revision) | `b034e159…` | narrow: the refusal must contain one of the cell's `names_any_of` ids |
| `.ufo/waves/round-24/build/out/GridOracle/promisor-grid.py` (GridOracle's frozen artifact) | `5e96fa60…` | wide: the id **or** a `<oid>:<path>` / `HEAD:<path>` expression naming a fixture path (Correction 4b) |

Both contain the PG46 fixture fix and the cross-repo fix. The recorded
candidate runs used the integrated runner `b034e159…`, and the candidate's 14
exit-2 cells satisfy the *narrow* pin (observed in the recorded stderr
tails). A baseline re-measured under `5e96fa60…` can differ (§5).

---

## 4. The separation (before = r23 base, after = candidate `ea51bc35…`)

Buckets are computed per cell from the before/after rows and the amended
expectation. Full per-cell table: `.ufo/waves/round-24/falsify/out/ConnMetrics/cells.tsv`.

| bucket | n | meaning |
|---|---|---|
| `restored_verdict` | **21** | before: exit 2 (the r23 blanket metadata refusal) → after: a substantive exit 0/1 verdict that meets the amended view |
| `exit2_reason_corrected` | **9** | before: exit 2 → after: exit 2 (still a refusal), reason class changed `metadata` → `unavailable` (content-derived) |
| `unchanged_exit2` | **4** | before: exit 2 → after: exit 2, reason class unchanged (the plain-store twins were already content-derived) |
| `unchanged_verdict` | **12** | before: exit 0/1 → after: the same exit 0/1 (the no-harm control twins) |
| `verdict_to_refusal` | **1** | before: exit 1 → after: exit 2 — **PG34**, the declared policy change of amendment `prospective_expected[2]` applied to every store; not a regression |

Cells:

* `restored_verdict` (21): PG01, PG02, PG03, PG04, PG05, PG06, PG09, PG11,
  PG12, PG22, PG23, PG24, PG26, PG28, PG30, PG31, PG35, PG39, PG41, PG44,
  PG48.
* `exit2_reason_corrected` (9): PG13, PG15, PG17, PG19, PG21, PG33, PG43,
  PG46, PG47.
* `unchanged_exit2` (4): PG14, PG16, PG18, PG20.
* `unchanged_verdict` (12): PG07, PG08, PG10, PG25, PG27, PG29, PG32, PG36,
  PG37, PG38, PG42, PG45.
* `verdict_to_refusal` (1): PG34.

Arithmetic: 21 + 9 + 4 + 12 + 1 = 47. No cell is `unmet_after`.

**Withdrawn original-view failures (reported separately, never counted as
achieved):** 7 — PG22, PG23, PG24, PG28, PG30, PG34, PG41. These are exactly
the cells the amendment changed; the original reading (`unknown citation in
a promisor-backed repository ⇒ exit 2`) stays withdrawn and is not relabelled
passed. The counter reports them in their own field, outside every verdict
count.

**Twin equality:** 25 declared pairs, `twin_mismatch: []` in the recorded
candidate run.

---

## 5. The three headline numbers, kept apart

| number | what it is | value |
|---|---|---|
| **frozen history 47/47** | the r23 base scored on the **frozen** column (its own behaviour against its own history) | 47/47 met |
| **amended baseline 16/47** | the same r23 base scored on the **amended** view with the **frozen-arm** grading rule (no exit-2 form check): 0/30 policy, 16/17 control (PG34 unmet) | 16/47 met |
| **amended after 47/47** | the candidate scored on the amended view: 30/30 policy, 17/17 control | 47/47 met |

### 5.1 16/47 and 14/47 are two different measurements — do not quote them as one

Measured on the same r23 base rows: the frozen-arm grading rule yields
**16/47**; the runner's *current*-arm rule (exit-2 form check on) yields
**14/47**. The two cells that flip are **PG16-missing-lane-tree-plain** and
**PG20-missing-fleet-tree-plain** (measured from the recorded flags, not
inferred): the r23 base's own git failure message for those two cells does
not contain the object id the current-arm pin demands, so the form check
rejects them, while the reason class (`bad file` / `not a tree object`) is in
the `unavailable` bag and therefore passes the frozen-arm rule.

The 14/47 is visible in the counter's *self-consistency* run (command 3):
there the "after" side is the r23 base itself in the current role, and the
counter reports `amended after 14/47`. The counter's dedicated
`amended_baseline_current_role` field reports "not measurable" whenever the
before rows carry no current-arm verdict (the frozen arm's rows do not), and
says so rather than guessing.

Consequences:

1. The **baseline** must be quoted with its rule: "16/47 with the frozen-arm
   rule (historical baseline)" and "14/47 with the current-arm rule" are
   different figures for the same code.
2. GridOracle's Correction 2 names *PG14 and PG16* as the differing pair.
   The recorded flags locate the flip at *PG16 and PG20*. (Correction 2's
   text also lists the two plain exit-2 cells whose r23-base message falls in
   the `unavailable` bag, which are four cells in total: PG14, PG16, PG18,
   PG20.) Reported as a factual correction; the conclusion (16 vs 14) is
   unchanged.
3. The 14/47 was measured on the pre-Correction-4b runner; under the widened
   naming pin (`5e96fa60…`) the r23 base may score differently. Not measured
   in this lane (would require a grid run).

---

## 6. Reproduction — exact commands, exits, findings

Base directory for every command below:
`/home/vgpnk/Projects/shokunin/kama-shokunin`.

| # | command | exit | finding |
|---|---|---|---|
| 1 | `python3 .ufo/waves/round-24/falsify/out/ConnMetrics/promisor-grid-count.py --selftest` | 0 | `selftest 5/5 ok` — all five buckets reachable and distinct |
| 2 | `python3 .ufo/waves/round-24/falsify/out/ConnMetrics/promisor-grid-count.py --before .ufo/waves/round-24/build/out/GridOracle/candidate.json --before-arm frozen --after .ufo/waves/round-24/falsify/out/MutOverRefusal/pristine.grid.json --after-arm current --manifest tests/report-audit/promisor-grid-expectations.json --cells-out .ufo/waves/round-24/falsify/out/ConnMetrics/cells.tsv --json > .ufo/waves/round-24/falsify/out/ConnMetrics/report-A-before-after.json` | 0 | frozen history **47/47**; amended baseline **16/47** (0/30 policy, 16/17 control); amended after **47/47** (30/30, 17/17); buckets 21/9/4/12/1; withdrawn 7; twin mismatch 0 |
| 3 | same counter with `--before .ufo/waves/round-24/build/out/GridOracle/candidate.json --after .ufo/waves/round-24/build/out/GridOracle/candidate.json --after-arm current` (→ `report-B-selfcheck.json`) | 0 | **self-consistency**: both arms ran the *same* auditor `da5041a…`; frozen history 47/47, frozen column after **47/47**, amended baseline 16/47 (frozen rule), amended after **14/47** (current role) → buckets `restored_verdict 0`, `exit2_reason_corrected 0`, `unmet_after 31`. The counter cannot manufacture a restoration from identical code |
| 4 | same counter with `--after .ufo/waves/round-24/falsify/out/MutResolution/restored-grid/candidate.json` (→ `report-C-cross-artifact.json`) | 0 | identical bucket counts and identical per-cell verdicts to run 2 — reproducible across a second peer artifact |
| 5 | `sha256sum tools/report-landing-audit.py tests/report-audit/promisor-grid.py tests/report-audit/promisor-grid-expectations.json` | 0 | `ea51bc35…` (the audited tool), `b034e159…` (runner), `d86b7bea…` (manifest) — matches the pinned values in the round context |
| 6 | `git rev-parse HEAD` in the scratch clone | 0 | `2e254a1763a9c08aa07fc53081287f506c447d84` (detached, scratch only) |

---

## 7. Observed vs inferred

**Observed** (recomputed from recorded artifacts, byte-hashed):

* the candidate's amended-view score 47/47 (30/30 policy, 17/17 control) and
  `violations: 0` — from three independent peer runs of the candidate at the
  pinned revision whose per-cell signatures are byte-identical
  (`MutOverRefusal/pristine.grid.json`, `MutRedundantAll/pristine.grid.json`,
  `MutResolution/restored-grid/candidate.json`; all
  `auditor_sha256 = ea51bc35…`, `expectations_sha256 = d86b7bea…`,
  `population_sha256 = 612b0a74…`);
* the r23 base's amended-view scores 16/47 (frozen rule) and 14/47 (current
  rule), and the two flipping cells PG16/PG20;
* the bucket assignment of all 47 cells;
* the seven withdrawn original-view failures;
* the runner-summary defect of §3.1 (measured as `amended_view_met = 0` in a
  run where all 47 cells met);
* the runner-version divergence of §3.3 (46 changed lines; the wide naming
  pin only in `5e96fa60…`).

**Derived by arithmetic from the manifest** (no run): the 30/17 policy/control
split, the 20/13/14 effective expectation distribution, the 25 declared twin
pairs, the 10 cells carrying an amended override.

**Inferred** (flagged, not used in any count): that the bucket boundaries
chosen here are the ones the L1 wants; a different but defensible taxonomy
(e.g. counting PG34 inside `exit2_reason_corrected`) would move one cell
between two rows and change no headline number.

---

## 8. Files written (all under the sanctioned falsify area)

| path | what |
|---|---|
| `.ufo/waves/round-24/falsify/advice/ConnMetrics.md` | this report |
| `.ufo/waves/round-24/falsify/out/ConnMetrics/promisor-grid-count.py` | the counting command (executable; `--selftest` included) |
| `.ufo/waves/round-24/falsify/out/ConnMetrics/cells.tsv` | the 47-cell table: bucket, before/after exit, reason classes, expectation, flags |
| `.ufo/waves/round-24/falsify/out/ConnMetrics/report-A-before-after.json` | machine-readable result of the headline comparison |
| `.ufo/waves/round-24/falsify/out/ConnMetrics/report-B-selfcheck.json` | machine-readable self-consistency result (identical code both arms) |
| `.ufo/waves/round-24/falsify/out/ConnMetrics/report-C-cross-artifact.json` | machine-readable cross-artifact reproduction |

Nothing outside those paths was written; no production file, no lane
configuration, no `.jj` index, no fleet, no object store was touched. The
scratch clone `/fast/scratch/hyaku/kama-r24/falsify/ConnMetrics/base`
(`git clone --no-hardlinks`, detached at `2e254a1763a9c08aa07fc53081287f506c447d84`)
was used for read-only hashing and diffing.

**Tooling:** no package was installed or updated in this lane (nothing was
needed); the counter is plain `python3` (standard library only).

---

## 9. Unverified / out of scope

1. **No grid run was executed here.** The lane assignment is the counting
   command; the sanctioned full measurement remains the L1's
   `--arm both --json` run. The numbers above are recomputations over
   retained artifacts, not new measurements.
2. The **before-side artifact** (`.ufo/waves/round-24/build/out/GridOracle/candidate.json`)
   was produced by the pre-Correction-1/2/4 runner: its rows carry no
   `met_amended_frozen`, no `objects_acquired` and no `raw_defects`. The
   baseline 16/47 was therefore recomputed from the raw observations, and it
   reproduces GridOracle's independently reported 16/47 exactly — but the
   after-Correction-4b fixture set was not re-measured in this lane.
3. The **14/47** current-role baseline was measured on the pre-Correction-4b
   runner; under the widened naming pin the figure may move. Unmeasured
   here.
4. `PG40` (the open, ungraded row) is excluded from all counts by
   construction; the counter refuses arms whose cell sets differ.
5. The counter's `defects` comparison is skipped (and reported as
   `unresolved-placeholder`) for cells whose expectation still carries a
   `$name` fixture placeholder, because a grid row does not carry the sha map
   that resolves it. Affected: PG09, PG10, PG11, PG12, PG22, PG23, PG24,
   PG25, PG37, PG38, PG39, PG41, PG42 — for those cells the *kinds* and
   *exit* checks still apply.
6. Not checked in this lane (other lanes' territory): the mutation
   sensitivity, the single-cell case behaviour, the source-level correctness
   of the auditor, and the inherited Git ≥ 2.45 prerequisite (still open at
   L0).

**Report:** `.ufo/waves/round-24/falsify/advice/ConnMetrics.md`
