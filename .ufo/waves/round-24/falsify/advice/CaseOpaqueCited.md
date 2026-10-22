# CaseOpaqueCited — PG46-opaque-tree-hides-cited-blob falsification (round 24)

VERDICT: **HOLDS** for the graded contract — with **one fixture/expectation gap (F1)**, two
minor harness observations (F2, F3) and **one low-severity source observation (S1)** reported
separately below. The assigned cell `PG46-opaque-tree-hides-cited-blob` meets its **amended**
(live) expectation on the pinned integration commit, the *frozen* r23 arm fails that very same
amended column (so the cell measures a real repair and not a frozen-history artefact), and the
refusal is content-derived, names the unavailable content, and acquires nothing. **No source
defect was found** that changes any verdict on this path.

Scope: exactly one bounded selection — `python3 tests/report-audit/promisor-grid.py --arm both
--case PG46-opaque-tree-hides-cited-blob --json` — run in a pinned scratch clone, plus read-only
static reads and **direct auditor invocations against the same registered fixture** (rebuilt with
the grid's *own* builder, unmodified) and against three benign offline twin fixtures I built
from the grid's own primitives. No other lane suite, no full grid, no mutation grid, no
execution-bearing probe, no network/transport payload. PM08 was not executed. No production file
other than this report and the `out/CaseOpaqueCited/` artifacts was written; production
`production/.jj/index`, the fleet, sibling lanes, operator config, routing, services and real
object stores were not touched.

## Pinned snapshot

| item | value |
|---|---|
| revision | `2e254a1763a9c08aa07fc53081287f506c447d84` (detached, scratch clone `--no-hardlinks`) |
| auditor `tools/report-landing-audit.py` | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| grid runner `tests/report-audit/promisor-grid.py` | sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` |
| fixed expectation manifest | sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` |
| frozen r23 auditor (from `0df800e8…`) | sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` |
| grid population sha256 | `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` (47 rows) |
| host tools | git 2.56.0, Python 3.14.8 (no install, no update) |

Scratch: `/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueCited` (clone + `tmp/` fixture roots +
raw outputs). `TMPDIR` was set to the scratch tree for every subprocess, as the grid requires
(`make_root()` refuses any `TMPDIR` outside `/fast/scratch/hyaku/kama-r24`).

## Axes and results

| # | Axis | Result |
|---|---|---|
| A1 | Assigned command, exit, in the pinned clone | PASS — exit **0**, stderr **0 bytes**, 1 graded row per arm, `violations 0` in both arms, 0 tracebacks / 0 timeouts / 0 harness leaks. Re-run once more (identical output, exit 0) |
| A2 | Actual missing / present objects asserted on the built fixture | PASS (observed) — cited blob `2f62e7ff9e9e4c2e972dab0989d414e027012348` **ABSENT** from lane *and* fleet; missing subtree `2a675c1af91c97c51f5101d6cff10bb797458ab6` **ABSENT** from lane *and* fleet; every object the audit reads is **PRESENT**: lane commit `18089c6071793e8be726676c30371c68a837ca48`, lane tip tree, `f` blob, `corpus/SOURCES.md` blob, fleet commit, fleet report blob, fleet tip tree. Store missing set = **exactly** `{2a675c1a…}` |
| A3 | The supplement's "hidden behind the missing subtree" premise really holds | PASS (observed) — the auditor's own traversal (`rev-list --objects --missing=print` over **every present object**, commit-graph off) yields the missing set `{2a675c1a…}`: the cited blob `2f62e7ff…` is **not enumerable** (it is not in the missing set at all), so its OID is genuinely knowable only through the missing subtree. The opaque set (`--filter=blob:none` walk) = `{2a675c1a…}`. The fleet store has **no** holes (both walks empty) |
| A4 | Exact finding / token pairs | PASS — the current arm produces **no verdict document** (exit 2, stdout **0 bytes**), so there are **no** defect pairs, exactly as the amended column requires (`kinds: null`, `defects: null`). The frozen arm likewise produces none. The refusal's *named* tokens are `2f62e7ff…` (the cited blob) and `2a675c1a…` (the missing subtree) |
| A5 | Content-derived reason IDs | PASS — current-arm stderr: `could-not-evaluate: round 1: unknown: unavailable required object: 2f62e7ff9e9e4c2e972dab0989d414e027012348 could be hidden behind the missing tree or commit 2a675c1af91c97c51f5101d6cff10bb797458ab6 in <lane>` — it names **both** unavailable objects (`names_any_of: ["$hidden_blob","$missing_subtree"]` satisfied), it is in the `unavailable` reason class, and it is **not** the r23 metadata refusal (`partial clone (` / `promisor pack` both absent). Frozen arm for contrast: `could-not-evaluate: <lane>: partial clone (remote.origin.promisor)` |
| A6 | No objects acquired | PASS (observed twice, two independent methods) — grid pin `objects_acquired {lane: [], fleet: []}` on both rows; independently, a **full `.git` fingerprint** (every file: path, size, sha256) of both audited repositories is **byte-identical before and after** the auditor run (lane 28 files, fleet 32 files; 0 added / 0 removed / 0 changed), no pack, no `FETCH_HEAD`, no new ref, `count-objects -v` still 5 loose / 0 in-pack |
| A7 | Actual twin document comparisons | **PARTIAL — the grid itself performs none for this cell** (`twin: null` → `twin_pairs_in_manifest: 0`, `twin_compared: 0`, `twin_pairs_compared: []`, `twins: {}`). I therefore did the comparisons myself, three of them, all against the grid's own builders/primitives (see A7a–A7c below). This is the **F1** gap |
| A8 | The refusal is caused by the absent cited blob, not by the hole alone and not by the promisor mark | PASS (observed) — the **restored-blob twin** (the *same* PG46 fixture with only the cited blob written back: `git hash-object -w` reproduces the identical OID `2f62e7ff…`; the subtree is **still** missing, the lane is **still** promisor-marked) audits **exit 0, clean, no defects**. So a missing subtree next to a *resolvable* citation does not refuse — there is no blanket closure precondition (the amendment's rule) — and the promisor mark alone changes nothing. The refusal in PG46 is therefore content-derived |
| A9 | Marked vs unmarked twin equality for this shape | PASS (observed) — two content twins with **identical OIDs** (`18089c60…` lane commit, `2f62e7ff…` blob, `2a675c1a…` subtree), nothing missing, one lane promisor-marked and one plain: both exit **0**, both clean (no defects), and their verdict documents are **equal after path normalisation** (`document_comparison_marked_vs_plain: true`). The cited blob resolves in both (`hidden_blob_present_in_lane: true`) — this is the manifest's "the complete twin resolves the blob" claim, exercised outside the grid (F1) |
| A10 | Original (withdrawn) view kept visible | PASS, with an honesty caveat — PG46's `original` column is **byte-identical** to its `amended` column (`{exit 2, kinds null, reason_class "unavailable", defects null}`; 40 of the 47 rows are in that set) because the row was registered **after** the amendment ("Registered after the amendment; there is no separate original reading"). The grid therefore reports `met_original: true`, but that flag is **vacuous** for this row and must **not** be reported as a withdrawn expectation achieved. The live target column is `amended`; the withdrawn original registration is untouched and reported here only as *not applicable* for PG46 |
| A11 | Frozen history is not the improvement | PASS — in the frozen arm PG46 **fails** the amended column (`amended_view_unmet: ["PG46-opaque-tree-hides-cited-blob"]`, `amended_view_met 0/1`) while meeting its frozen column (`met_frozen: true`, reason class `metadata`). The r23 harm this cell removes — a blanket metadata refusal of a complete-marked local repository — is therefore **measured**: r23 exits 2 for the *wrong reason*, and the current arm exits 2 for a *content-derived* reason |
| A12 | Expectation integrity (no post-hoc fitting) | PASS (observed) — the live manifest's **44 pre-inspection rows are byte-identical** to `.ufo/waves/round-24/oracle-snapshot-before-inspection.json` (`differing pre-inspection rows: []`); the live file adds exactly the 3 registered opaque cells (PG46/PG47/PG48) and keeps the same single open row (PG40). PG46's row carries the supplement's own policy reference and wording; its `frozen` column still records the r23 metadata refusal, its `original` column still records the withdrawn registration, and **no expected cell was edited to fit the candidate**. The fixture *was* changed (the builder now drops `("opaque_tree","hidden_blob")` instead of `("opaque_tree",)`); that change **tightens the fixture to the manifest's own written premise** ("the cited blob d/f is absent but its OID is hidden behind that missing subtree") rather than relaxing an expectation — see F4 for the residual risk of that edit |
| A13 | Lazy-fetch hazard reported by the sibling blobless family does not apply | PASS (observed) — PG46 uses **no** blobless clone. The lane's `remote.origin.url` is `<case dir>/absent-remote.git` and that path **does not exist on disk** (`lane_origin_url_exists_on_disk: false`), the fleet has no remote at all, and the lane's promisor facts are config-only (`extensions.partialclone`, `remote.origin.promisor=true`, no `.promisor` marker). Every content-touching probe I ran used `--no-lazy-fetch` explicitly; the `.git` fingerprint (A6) proves nothing was materialised |

## Exact commands, exits and observations

### 1. The assigned bounded selection (run twice, identical)

```
cd /fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueCited/scratch   # detached 2e254a17…
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueCited/tmp \
  python3 tests/report-audit/promisor-grid.py --arm both \
  --case PG46-opaque-tree-hides-cited-blob --json
```
exit **0** (both runs); stderr empty; `out/CaseOpaqueCited/grid-assigned-run.json`,
`…/grid-assigned-run-2.json`.

Current arm row (verbatim, trimmed):
`exit 2`, `met_amended true`, `met_original true`, `met_frozen null`, `objects_acquired {lane: [], fleet: []}`,
`traceback false`, `timed_out false`, `leaked false`, `document null`, `twin null`,
`stderr_tail: "could-not-evaluate: round 1: unknown: unavailable required object: 2f62e7ff9e9e4c2e972dab0989d414e027012348 could be hidden behind the missing tree or commit 2a675c1af91c97c51f5101d6cff10bb797458ab6 in …/current/000/lane"`.

Frozen arm row (verbatim, trimmed): `exit 2`, `met_frozen true`, `met_amended_frozen false`,
`objects_acquired {lane: [], fleet: []}`,
`stderr_tail: "could-not-evaluate: …/frozen/000/lane: partial clone (remote.origin.promisor)"`;
arm totals `graded 1, violations 0, amended_view_met 0/1, amended_view_unmet ["PG46-opaque-tree-hides-cited-blob"]`.

### 2. The independent probe (benign, offline, own fixtures)

```
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueCited/tmp \
  python3 .ufo/waves/round-24/falsify/out/CaseOpaqueCited/probe_pg46.py
```
exit **0**; full machine-readable result in `out/CaseOpaqueCited/probe-pg46.json`.

The probe imports the grid module itself (no reimplementation of the fixture), rebuilds the
registered fixture with `BUILDERS["c_opaque_tree_hides_cited_blob"]`, and then:

* object-level premises with `--no-lazy-fetch` plumbing (A2, A3);
* the pinned auditor run **directly** on that fixture (not through the grid): exit **2**,
  stdout **0 bytes** (no JSON verdict), stderr exactly the content-derived refusal quoted in A5,
  reproducing the grid's answer byte-for-byte on a second direct invocation;
* a full-`.git` fingerprint before/after (A6);
* three twin fixtures built from the grid's own `init_repo`/`commit`/`publish`/`report_text`/
  `mark_config` primitives, so the bytes — and therefore the OIDs — are identical to PG46's:
  * **restored-blob twin** (PG46 fixture + `git hash-object -w` of `opaque\n` → identical OID
    `2f62e7ff…`; subtree still missing; lane still promisor-marked): auditor **exit 0**, stderr
    empty, `defects: []`, missing set still `{2a675c1a…}` (A8);
  * **twin-marked** (nothing missing, lane promisor-marked): **exit 0**, `defects: []`;
  * **twin-plain** (nothing missing, no mark): **exit 0**, `defects: []`;
  * marked vs plain verdict documents equal after path normalisation → `true` (A9).

### 3. Fixture / expectation gaps (reported separately from source findings)

* **F1 (fixture, medium): the cell's twin claim is asserted, not graded.** The manifest row
  says *"The complete twin resolves the blob"*, but `twin: null` for PG46, so the grid performs
  **no** twin comparison on this cell (`twin_compared: 0`). No builder in the 47 produces a
  hole-free PG46-shaped fixture (a `d/f`-present, blob-citing, nothing-missing lane), so the
  claim is not exercised anywhere in the grid. I exercised it externally (A8/A9) and it holds.
  *Minimal correction (report only, not applied):* give PG46 a twin link to a hole-free
  counterpart cell, or add a builder (e.g. `c_opaque_tree_complete_twin`) plus a graded row
  whose expectation is exit 0 / `kinds: []`, so the "complete twin resolves the blob" property
  is **measured** instead of asserted in prose.
* **F2 (harness, low): a defective premise and an environment failure share the exit code.**
  The grid's own premise check for this case (`if object_exists(lane, hidden_blob) or
  object_exists(fleet, hidden_blob): raise Premise(...)`) aborts the **whole run** with
  `could-not-evaluate: fixture premise: …` and **no row at all**, i.e. process exit 2 — the same
  exit code as an environment failure and the same exit code as a legitimate row-level refusal.
  The *stderr prefixes* do distinguish them (`fixture premise:` vs `environment:` vs the row's
  `round 1: unknown: …`), but a receipt that records only the exit code cannot tell a broken
  fixture from a refusal. *Minimal correction:* have receipts quote the stderr reason class
  alongside the exit code (the prefixes already exist; no code change needed).
* **F3 (harness, low):** `check_exit2_form()` only rejects stdout that **parses as JSON**
  ("stdout carries a verdict document"); non-JSON stdout of any length is tolerated. The
  manifest wording is "no JSON verdict", so the check matches the letter of the contract, but a
  stray non-JSON dump would pass. PG46's stdout was empty, so this cell is unaffected.
* **F4 (fixture, informational): the fixture was edited after the fact.** The builder now drops
  `("opaque_tree","hidden_blob")`; before that it dropped only `("opaque_tree")`, leaving the
  cited blob in the store, so the auditor could **resolve** the citation and the cell answered
  exit 0. The edit moves the fixture **towards** the manifest's written premise and leaves the
  expected cells untouched — it does not make the fixture fit the candidate by relaxing an
  expectation. The residual risk is that the same edit also removed the only in-grid instance
  of "a resolvable blob citation next to a missing subtree" (which is now the F1 gap); my
  restored-blob twin re-establishes that shape as evidence, outside the graded population.

### 4. Source-level observation (candidate `tools/report-landing-audit.py` @ `ea51bc35…`)

* **S1 (low, no verdict change): the refusal names a hole that need not be related to the
  citation.** `opaque_hole(stores)` (`tools/report-landing-audit.py:705-714`) returns the
  **lowest** missing non-leaf object id of the **first** store that has any such hole, and
  `refuse_unknown` (`:419-448`) consults it for **every** unresolved token. The refusal is
  correctly gated (it fires only on the unresolved-citation path — A8 proves a missing subtree
  next to a resolvable citation does **not** refuse), so no clause of the amended contract is
  broken; but in a fixture with **several** holes the *named* object can be unrelated to the
  citation, which is weaker than "names the unavailable content" in the strongest sense. PG46
  has exactly one hole (`2a675c1a…`) and it genuinely hides the cited blob, so this cell can
  neither detect nor exclude the over-breadth. *Minimal correction (optional, report only):*
  prefer a hole whose subtree could contain the token when that can be determined, otherwise
  keep the deterministic lowest-id choice and state in the auditor docstring that the named
  object is *a* hole that could hide the token, not necessarily *the* one.

No other source defect was observed on this path: `unknown_citation` (`:689-702`) correctly
finds nothing for `2f62e7ff…` (the blob is invisible to the missing set by construction, which
is precisely what makes PG46 the discriminating cell for the opaque-hole route), and
`missing_reachable` (`:651-678`) reproduces exactly the set the cell's premise claims.

## Observed vs inferred

**Observed** (measured on the pinned clone): every exit code, every stderr string, every
stdout byte count, the object-level presence/absence of `2f62e7ff…`, `2a675c1a…`,
`18089c60…`, the two missing-set enumerations, the `.git` fingerprints, the twin exit codes
and document equality, the manifest's row contents and digests, the byte-identity of the 44
pre-inspection rows against the pre-inspection snapshot, and the frozen-arm contrast.

**Inferred** (from the code, not executed): that the frozen arm's exit 2 comes from the r23
metadata check (the stderr says so: `partial clone (remote.origin.promisor)`); that
`check_exit2_form`'s JSON-only stdout test is the only stdout guard; that `opaque_hole`'s
"lowest id" choice is what names `2a675c1a…` in a multi-hole store (PG46 has a single hole, so
the choice is not exercised there).

## Files written

* `.ufo/waves/round-24/falsify/advice/CaseOpaqueCited.md` — this report.
* `.ufo/waves/round-24/falsify/out/CaseOpaqueCited/probe_pg46.py` — the probe (grid builders
  reused; offline; no network; no execution payload).
* `.ufo/waves/round-24/falsify/out/CaseOpaqueCited/probe-pg46.json` — its machine-readable
  result (premises, audit, fingerprints, three twins).
* `.ufo/waves/round-24/falsify/out/CaseOpaqueCited/grid-assigned-run.json`,
  `…/grid-assigned-run-2.json` — the two runs of the assigned selection.
* Scratch (outside the repo): `/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueCited` — clone at
  detached `2e254a1763a9c08aa07fc53081287f506c447d84`, `tmp/` fixture roots, raw grid output.

Production lane `production/.jj/index`, the fleet, sibling lanes, operator config, routing,
services and real object stores were not touched. No network, transport or execution payload was
used; PM08 was not executed; no mutant was executed. No tool was installed or updated (git
2.56.0 and Python 3.14.8 were already present).

## Unverified items

- The full 47-row population was **not** run; only PG46 was executed (twice through the grid,
  once more directly against the same fixture, plus the three twin fixtures).
- The auditor's `selftest`, the grid's `--selftest` and the mutation grid were **not** run. In
  particular I did **not** re-run the mutation runner, so PM04/PM10/PM11's kill attribution
  (`PG46` appears in `PM04` and `PM10`, `tests/report-audit/promisor-mutants.py:326,432`) is a
  static reading of the pinned source, not a fresh execution. PM08 was not executed at all.
- The **frozen** arm was exercised only on this one cell; I did not diff the r23 auditor source
  against the pinned one.
- The inherited **git ≥ 2.45** prerequisite (open at L0) was not re-verified here; this host
  runs git 2.56.0.
- Whether `absent-remote.git` could be reachable in some other environment was not probed; no
  network use was permitted and none was attempted.
- S1's over-breadth in a **multi-hole** store was not executed (no such fixture exists in the
  population); the observation is a static reading of `opaque_hole()`.

Report: .ufo/waves/round-24/falsify/advice/CaseOpaqueCited.md
