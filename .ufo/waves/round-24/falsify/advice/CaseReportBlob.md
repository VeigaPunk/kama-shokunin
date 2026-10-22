# CaseReportBlob — round-24 FRESH falsification, family ReportBlob

Scope: fixture family `ReportBlob` = `PG17-missing-fleet-report-promisor` (policy) and
`PG18-missing-fleet-report-plain` (control twin). Bounded selection only; read-only
production; leaf member (no subagents dispatched).

## Verdict

**HOLDS** (both rows) on the **amended** (live) target columns, for the current source at
the pinned revision. No source flaw and no fixture-data flaw found in scope. Two
harness/manifest coverage observations and one grading-method note are reported below;
none of them changes a verdict.

| row | arm | exit | met_frozen | met_amended_frozen | met_original | met_amended (live) | violations |
|---|---|---|---|---|---|---|---|
| PG17-missing-fleet-report-promisor | frozen | 2 | true | **false** | n/a | n/a | 0 |
| PG17-missing-fleet-report-promisor | current | 2 | n/a | n/a | true | **true** | 0 |
| PG18-missing-fleet-report-plain | frozen | 2 | true | true | n/a | n/a | 0 |
| PG18-missing-fleet-report-plain | current | 2 | n/a | n/a | true | **true** | 0 |

Whole-run result of the assigned command: **exit 0** (`violations: 0` in both arms,
`tracebacks: 0`, `timeouts: 0`, `harness_leaks: 0`).

Frozen history met is *not* counted as improvement: the only substantive delta versus the
frozen arm is **PG17's reason class**, which moved from the r23 blanket metadata refusal
(`partial clone (remote.origin.promisor)`) to the content-derived unavailable-object reason.
PG18 is unchanged (no-harm twin) and the exit code is 2 in all four rows.

## Environment and provenance (all digests observed in my own scratch clone)

Scratch clone: `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin`
→ `/fast/scratch/hyaku/kama-r24/falsify/CaseReportBlob`, then
`git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84` (detached, exact base
observed; `git rev-parse HEAD` = `2e254a1763a9c08aa07fc53081287f506c447d84`).

| artifact | observed sha256 | contract |
|---|---|---|
| `tools/report-landing-audit.py` (source tool) | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | `ea51bc35…` ✔ |
| `tests/report-audit/promisor-grid.py` (runner) | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | `b034e159…` ✔ |
| `tests/report-audit/promisor-grid-expectations.json` (manifest) | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | `d86b7bea…` ✔ |
| `tests/report-audit/promisor-mutants.py` (mutation probe) | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` | `6e0b9d62…` ✔ |
| frozen auditor blob `0df800e8:tools/report-landing-audit.py` | `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` | manifest `derived_from.frozen_auditor_sha256` ✔ |

Host `git version 2.56.0`. `TMPDIR` was set per subprocess to
`/fast/scratch/hyaku/kama-r24/falsify/CaseReportBlob` (inside the grid's required
`SCRATCH = /fast/scratch/hyaku/kama-r24` root). Production was not modified: `git status
--porcelain` in `/home/vgpnk/Projects/shokunin/kama-shokunin` shows only the pre-existing
untracked `.ufo/waves/round-24/falsify/`, and `git diff --stat HEAD` is empty.

## Commands executed (exact)

```
cd /fast/scratch/hyaku/kama-r24/falsify/CaseReportBlob
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin CaseReportBlob   # exit 0
git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84                      # exit 0
git --version                                                                              # git version 2.56.0
git cat-file -t 0df800e896f6bce285a81e794ad4ae1d1e6c3a71                                # commit
git cat-file blob 0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py | sha256sum
sha256sum tools/report-landing-audit.py tests/report-audit/promisor-grid.py \
          tests/report-audit/promisor-grid-expectations.json tests/report-audit/promisor-mutants.py
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseReportBlob \
  python3 tests/report-audit/promisor-grid.py --arm both \
    --case PG17-missing-fleet-report-promisor \
    --case PG18-missing-fleet-report-plain --json                 # exit 0
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseReportBlob \
  python3 verify_pg17_pg18.py                                       # exit 0 (independent re-derivation)
```

`verify_pg17_pg18.py` is my own scratch script: it imports the **pinned grid's own
builders** (`c_missing_fleet_report_promisor`, `c_missing_fleet_report_plain`) so the
fixture is byte-identical to the graded one, then asserts the missing/present objects
directly and runs the pinned auditor, capturing the **full** stderr (the grid keeps only a
300-char tail). No network, no transport, no repository program, no execution payload.

## Actual missing / present objects (asserted directly, both rows)

| fact | PG17 (promisor) | PG18 (plain) |
|---|---|---|
| fleet promisor-marked | true (`remote.origin.promisor`, `extensions.partialclone`, absent remote url) | false |
| lane promisor-marked | false | false |
| lane missing objects (`rev-list --objects --missing=print --no-lazy-fetch`) | `[]` (lane complete) | `[]` |
| fleet missing objects | `['0cf7ed5cd6dec335553d165dc587baa224ab302b']` (exactly one) | `['0cf7ed5cd6dec335553d165dc587baa224ab302b']` |
| fleet HEAD tree lists the report blob | `100644 blob 0cf7ed5c…0302b  .ufo/reports/round-1/kama.md` | same |
| report blob present in fleet store (`cat-file -e`) | **no** | **no** |
| report blob present in lane store | **no** | **no** |
| fleet tip tree `b1e11739fedfb736f2936bd9addf7e4a286d462e` | present (`tree`) | present |
| lane commit `58866b563cd900df310588effe79028efc104c33` | present (`commit`) | present |
| `git show HEAD:.ufo/reports/round-1/kama.md` in fleet | rc=128 `fatal: bad object HEAD:.ufo/reports/round-1/kama.md` | same |

So the required report evidence is *referenced by the fleet tip tree and absent from every
audited store*: the refusal is forced by content, not by a policy choice, and it is
identical in the marked and unmarked fleet.

## Exact finding / token pairs and content-derived reason

Both rows exit **2** and emit **no verdict document** (`stdout` = 0 bytes,
`stdout_is_json` = false), therefore there are **no finding/token pairs at all**
(`defects: null`, `kinds: null`; the live expectation for both rows is
`kinds: null, defects: null` with `reason_class: "unavailable"`). The refusal's
content-derived identifiers are the only output:

```
could-not-evaluate: unavailable required object: .ufo/reports/round-1/kama.md at fleet HEAD
(tip tree b1e11739fedfb736f2936bd9addf7e4a286d462e, <fleet repo>): git show
HEAD:.ufo/reports/round-1/kama.md in <fleet repo>: rc=128 fatal: bad object
HEAD:.ufo/reports/round-1/kama.md
```

Identical text for PG17 and PG18 up to the fixture path segment. Source path:
`audit_round()` → `git show HEAD:<rel>` fails → `required_read(<rel> at fleet HEAD (tip tree
…), exc)` → `EvalError` → `main` prints `could-not-evaluate: …`
(`tools/report-landing-audit.py:328-334, 455-464, 1314`).

Grader properties, all observed as satisfied by the current arm:
`stderr` starts with `could-not-evaluate:` ✔; stdout carries no verdict document ✔;
reason class `unavailable` matched by the genuine terms `unavailable` and `bad object` ✔;
forbidden reasons `partial clone (` and `promisor pack` **absent** ✔ — the promisor
metadata does not appear in the reason at all; `names_any_of` satisfied by
`.ufo/reports/round-1/kama.md` ✔ (the strong `names_any_of` grader is met; the
`$report_blob` alternative is *not* what carried it — see finding M2).

## No objects acquired

`objects_acquired` = `{"lane": [], "fleet": []}` for **all four** rows (both arms, both
cases), computed by the harness as the set difference of `git cat-file
--batch-all-objects --batch-check=%(objectname)` before and after the audit.

Independent positive control (my scratch script, deliberately *un*-isolated git in the
promisor-marked PG17 fleet):

```
git -C <fleet> show HEAD:.ufo/reports/round-1/kama.md
→ fatal: '<...>/absent-remote.git' does not appear to be a git repository
   fatal: Could not read from remote repository.
   fatal: bad object HEAD:.ufo/reports/round-1/kama.md
```

i.e. without isolation git *does* try the promisor remote, while the auditor's
`GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch", …)` (`tools/report-landing-audit.py:138-141`,
applied to every git call at line 156-165) produced `fatal: bad object` and acquired
nothing. The promisor remote in the fixture points at a non-existent local directory, so
no network transport is even possible here.

## Twin document comparison — what actually happened

**No twin document comparison was executed for this family.** In the grid output, both
current rows carry `twins: {"PG18-missing-fleet-report-plain": None}` /
`{"PG17-missing-fleet-report-promisor": None}`, `twin_equal: null`, and the arm summary
shows `twin_pairs_in_manifest: 1`, `twin_compared: 0`, `twin_pairs_compared: []`,
`twin_mismatch: []`. Cause: both rows exit 2 with empty stdout, so
`normalise_document()` returns `None` and the twin block records "not comparable"
(`promisor-grid.py` twin block; `results[partner] = None` → `twin_equal = None`).

Consequence for the record: the manifest's declared twin link `PG17 ↔ PG18` is **not**
verified by any automated document comparison; the no-harm twin property for this family
rests entirely on the two per-row expectations (exit 2, `reason_class: unavailable`,
forbidden metadata reasons). My own manual comparison of the two refusals shows them
identical except for the fixture path segment (`stderr_equal_raw: false`, differing only
in the `.../PG17-missing-fleet-report-promisor/fleet` vs
`.../PG18-missing-fleet-report-plain/fleet` segments) — so the substance holds, but the
harness does not assert it. **A claim of "twin document equality verified for PG17/PG18"
would be unsupported; the correct claim is "twin equivalence verified manually, by me".**

## Original vs amended view (and the withdrawn expectation)

The manifest row for both PG17 and PG18 has **no `amended` entry**, so per the manifest's
own rule ("a case without an 'amended' entry uses its 'original' view") the live view is
identical to the original view: `exit 2`, `reason_class "unavailable"`, `kinds: null`,
`defects: null`.

* Current arm: `met_original = true` and `met_amended = true` for **both** rows →
  `withdrawn_original_failures: []` for this selection. **Neither PG17 nor PG18 carries a
  withdrawn expectation**, so nothing here is relabelled as passed.
* The withdrawn set (`PG22`, `PG23`, `PG24`, `PG28`, `PG30`, `PG34`, `PG41`, plus
  `PG37` with `amended: null`) lies outside my selection and stays visible and unchanged
  in the manifest; I did not grade it.
* Manifest integrity check (independent of the grid run): the 44 rows of
  `.ufo/waves/round-24/oracle-snapshot-before-inspection.json` are byte-identical in the
  shipped manifest across `kind, builder, policy_ref, notes, frozen, original, twin,
  names_any_of, reason_forbidden` (**0 field diffs**), and the manifest adds exactly the 3
  independent opaque cells `PG46-opaque-tree-hides-cited-blob`,
  `PG47-opaque-tree-with-unresolved-fabricated-token`,
  `PG48-opaque-unused-tree-no-unresolved-token` → `population_size = 47`, matching the
  fixed47 contract (original44 unchanged + 3 opaque cells). `PG17`/`PG18` rows are
  byte-identical to the snapshot rows.

## Findings by severity

### M1 — [medium, harness/manifest coverage, not source] The declared twin link of this family is never compared
`promisor-grid.py` computes twin equality from the verdict *document* only; for exit-2 rows
there is no document, so `twin_compared` is `0` while `twin_pairs_in_manifest` is `1`. A
reader of the arm summary could mistake `twin_mismatch: []` for "twins verified".
*Minimal correction (reported, not applied):* in the twin block, fall back to a
path-normalized stderr comparison when both documents are `None` (or expose
`twin_reason_compared`), so a refusal-pair twin is asserted rather than silently skipped;
and/or mark exit-2 twin pairs in the manifest as reason-compared so
`twin_pairs_compared` is not silently `[]`.

### M2 — [low, expectation precision] The `$report_blob` alternative of `names_any_of` is dead on this path
`names_any_of = ["$report_blob", ".ufo/reports/round-1/kama.md"]` resolves `$report_blob` to
`0cf7ed5cd6dec335553d165dc587baa224ab302b`, but the current auditor's report-read refusal
names the *path* and the *fleet tip tree id*, never the missing blob's object id
(`observed: names_any_of_match = {sha: false, path: true}`). The row passes because the
grader is `any_of` and the path alternative is present — the strong `names_any_of` grader
is met, and the later path-based relaxation was not needed. But a future tightening to
"must name the missing object id" would fail on this source. No change proposed to the
expectation (I did not modify any expected cell).

### M3 — [low, grading method] `reason_class` is a whole-stderr substring test, so the fixture path can satisfy a class term
`REASON_CLASSES` matching is `t in err.lower()`. In my scratch run the case directory name
`PG17-missing-fleet-report-promisor` contributes the substring `missing` twice to stderr.
In the graded grid run the fixture path is `promisor-grid-<rand>/<arm>/<nnn>/<repo>`, which
contains no class term, so PG17/PG18's class was carried **only** by the genuine
content-derived terms `unavailable` (from `unavailable required object`) and `bad object`
(from git's own message). No row outcome depends on the path artifact; recorded because it
weakens the class test in general.

### Fixture flaws vs source flaws
* **Fixture data (PG17/PG18): no flaw found.** The premise is minimal and exactly on point:
  one missing object (the fleet report blob), lane complete, lane commit present, fleet tip
  tree present, PG17's fleet promisor-marked and PG18's plain, and the missing blob is
  absent from *both* audited stores, so the exit-2 verdict is forced. It is deliberately
  distinct from the neighbouring families (PG15/16/19/20 missing tree, PG33/34 missing
  *cited* blob, PG43 fleet unhydrated blobless).
* **Source: no flaw found in scope.** The refusal path is content-derived end to end and
  never consults promisor metadata for the verdict; the marked fleet (PG17) and the plain
  fleet (PG18) are refused for the same substantive reason, which is exactly the amended
  contract ("metadata alone never changes the verdict; a missing object actually required
  by an audit read is exit 2 with a content-derived reason").

## Observed vs inferred

* **Observed**: exit codes (2/2/2/2), the full stderr of the current arm for both rows,
  the frozen arm's stderr tails, stdout emptiness (0 bytes) and non-JSON-ness, the
  premise missing lists, promisor facts, object presence/absence via `cat-file -e` and
  `ls-tree`, the before/after object-inventory deltas (empty), twin results
  (`None`/`null`, `twin_compared: 0`), the met_frozen / met_amended_frozen / met_original /
  met_amended flags, `withdrawn_original_failures: []`, `violations: 0`, the manifest↔snapshot
  equality (0 diffs, 47 rows), the four contract digests, and that an un-isolated git *does*
  attempt the promisor remote while the auditor does not.
* **[INFERENCE]** that the refusal is "content-derived" in the intended sense: the reason
  embeds the actually-requested path, the fleet tip tree id read from the commit header, the
  exact git command, its rc and git's message — all taken from the failing read, not from
  promisor metadata or from a fixed string.
* **[INFERENCE]** that no network transport occurred: the promisor remote url points at a
  non-existent local directory, the auditor's calls carry `--no-lazy-fetch`, and no object
  was acquired. I did **not** instrument sockets.

## Residual risk and verification gaps

1. The harness does not assert twin equivalence for this family (M1); the twin claim for
   PG17/PG18 rests on my manual comparison only.
2. `names_any_of` is met through the path alternative (M2); the missing object id never
   appears in the refusal text for this read path.
3. The Git floor (`>= 2.45`) is untouched by this measurement: the host has git 2.56.0, so
   nothing here exercises the `--no-lazy-fetch` availability boundary or the rejected
   `--missing=print-info` / `--missing-only` prohibition. The inherited Git>=2.45
   prerequisite remains **open at L0**.
4. Only these two rows were exercised (by assignment). The other 45 graded rows, the open
   row PG40, the mutation probe `6e0b9d62…` and the selftest were **not** run by me.
5. The frozen arm was measured only for these two rows; the "amended_view_met: 1/2" figure
   in the frozen arm refers to this selection alone, not to the suite.
6. No serving capability, no higher numeric score, no admission, integration or shipping
   judgment is asserted anywhere in this report. Read-only production throughout: the only
   production writes are this report and the optional out-directory artifacts listed below.

## Files written

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseReportBlob.md` (this report; append-only, created fresh — the file did not exist).
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseReportBlob/grid-pg17-pg18.json` (`1e14a66ce2eb78e044c35217e887e5640bf37926b5f12984c2cfa3f0e4960af3`) — the assigned command's `--json` output.
* `…/out/CaseReportBlob/grid-pg17-pg18.err` (`e3b0c442…`, empty) — the assigned command's stderr.
* `…/out/CaseReportBlob/verify-out.json` (`db13e531b76294d23402f3fa2d76569d177749107ddb9e6b030057a852950cd1`) — my independent re-derivation (missing/present objects, full stderr, acquisition delta, twin comparison).
* `…/out/CaseReportBlob/verify_pg17_pg18.py` (`02d0109c60fbdad8dae11c5e8e2570ccae1c7646ae828b095f82a1786c3916b5`) — my scratch verification script.
* Scratch only (not production evidence): `/fast/scratch/hyaku/kama-r24/falsify/CaseReportBlob/` (clone, `grid-pg17-pg18.*`, `verify-out.json`, `verify_pg17_pg18.py`, temp fixture roots created by the two runs).

No tool was installed or updated; no pacman/`uv`/`cargo`/`npm` transaction was performed.
No source file was edited — no production edit was made or proposed as an applied change.

Report: .ufo/waves/round-24/falsify/advice/CaseReportBlob.md

## Addendum — cross-lane hazard from `KamaR23-2.CaseFleetBlobless` (PG43) checked against this family

A peer reported that in the **blobless-clone** fixtures (PG43 family) `remote.origin.url`
points at a *reachable* local `file://` origin, so any git probe **without**
`--no-lazy-fetch` materialises the missing blobs, silently evaporating the premise and
turning a correct exit 2 into a false "clean" exit 0.

Checked against **PG17/PG18 specifically**: this family's promisor marking is
`mark_config()` — `remote.origin.url` = `<tmp>/absent-remote.git`, a **non-existent**
directory, not a reachable origin. Therefore the hazard does not apply here, and the one
deliberately un-isolated probe in my verification script could not materialise anything:
its stderr was `fatal: '<...>/absent-remote.git' does not appear to be a git repository`
followed by `fatal: bad object HEAD:.ufo/reports/round-1/kama.md`, and the post-probe
assertion still reports the report blob `0cf7ed5cd6dec335553d165dc587baa224ab302b`
**present: false** in the fleet store (`git cat-file -e` rc≠0), with
`objects_acquired = {"lane": [], "fleet": []}`.

Residual note: my PG17/PG18 conclusions therefore do **not** depend on the reachability
of a promisor remote, but any future extension of this family to a real `file://` origin
must keep `--no-lazy-fetch` on every probe (the grid's own `missing_objects`,
`object_exists` and `object_inventory` helpers already do).

Report: .ufo/waves/round-24/falsify/advice/CaseReportBlob.md

## Addendum 2 — M2 is actionable, not merely descriptive (corroborated cross-lane)

A peer lane (`KamaR23-2.CaseFleetBlobless`, PG43) reports that on this same exit-2
report-read shape the missing report blob's id **is** locally derivable without any fetch:
`git --no-lazy-fetch rev-parse 'HEAD:.ufo/reports/round-1/kama.md'` → `0cf7ed5cd6dec335553d165dc587baa224ab302b`
(rc=0).

That is consistent with what I already observed in PG17/PG18 and recorded in the object
table above: the fleet tip tree `b1e11739fedfb736f2936bd9addf7e4a286d462e` is **present**,
and `git ls-tree HEAD` lists `100644 blob 0cf7ed5c…0302b  .ufo/reports/round-1/kama.md`.
So the missing object's id is readable from present local content, with no transport, while
the pinned refusal names only the path and the tip tree id (grep of the OID in the PG17
stderr: 0 matches).

Consequence for M2, stated precisely: the `$report_blob` alternative of
`names_any_of` is unreachable on this code path, but it is **not** unreachable in
principle — the id is one fetch-free `rev-parse` away. Minimal candidate correction
(reported, not applied, no source edited): in `audit_round()`, when
`git show HEAD:<rel>` fails, resolve the path's id with
`git --no-lazy-fetch rev-parse HEAD:<rel>` and include it in the `required_read` reason
(e.g. `unavailable required object: <rel> at fleet HEAD (tip tree <tree>, blob <oid>)`),
so the refusal names the missing object itself rather than only its path. Until that
happens, the honest claim about PG17/PG18 remains: the strong `names_any_of` grader is met
through the path alternative only.

## Addendum 3 — source-ledger note (no change from this slice)

No source file was edited in this slice, so no source-ledger row was added, changed or
retired by me. `S105` (which records the explicit rejected S095 cross-API inference) is
present at this revision in `corpus/SOURCES.md`, `corpus/lessons/round-24.md` and
`corpus/knowledge/error-is-not-a-verdict.md`; the original S095 "teaches" row stays filed
and the mutable used-by cells reconciled — unchanged by me. The final source-census
verification at the current row count remains L1-owned after this stage.

Report: .ufo/waves/round-24/falsify/advice/CaseReportBlob.md
