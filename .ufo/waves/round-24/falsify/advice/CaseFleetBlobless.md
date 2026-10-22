# CaseFleetBlobless — PG43 falsification (kama round 24, pinned `2e254a17`)

**Verdict: HOLDS for the assigned slice.** The single bounded selection
`PG43-fleet-unhydrated-blobless-report-required` meets its live (graded) expectation on the
pinned candidate, with a content-derived refusal, no verdict document, and no object
acquisition. No source defect was found in this slice. One **fixture-level** hazard (F1) and
two low-severity **expectation/manifest** observations (F2, F3) are reported separately, as
required; none of them invalidates the row.

Lane: leaf member (no subagent dispatch). Read-only production.

---

## 1. Pinned base (observed)

| item | value |
|---|---|
| clone | `/fast/scratch/hyaku/kama-r24/falsify/CaseFleetBlobless/repo` (`--no-hardlinks`, detached) |
| HEAD | `2e254a1763a9c08aa07fc53081287f506c447d84` (clean tree) |
| `tools/report-landing-audit.py` | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` (matches assignment) |
| `tests/report-audit/promisor-grid.py` | sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` (matches assignment) |
| `tests/report-audit/promisor-grid-expectations.json` | sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (matches assignment) |
| manifest | 47 rows, `population_sha256 = 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` |
| frozen auditor blob `0df800e8…:tools/report-landing-audit.py` | sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` (equals the oracle snapshot's `frozen_auditor_sha256`) |
| environment | git 2.56.0, python3 3.14.8; `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseFleetBlobless/tmp`; no tool installed or updated |

Production was not modified: the only production delta observed was the pre-existing untracked
`.ufo/waves/round-24/falsify/` tree; `production/.jj/index`, fleet, sibling lanes, operator
config, routing, services and real object stores were untouched. No network, transport or
execution payload was used (the only transport is the fixture's own local `file://` clone,
performed by the grid's builder). PM08 was not executed.

## 2. Exact commands and exit codes

```
# 1) the assigned bounded selection (both arms, single case)
cd /fast/scratch/hyaku/kama-r24/falsify/CaseFleetBlobless/repo
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseFleetBlobless/tmp \
  python3 tests/report-audit/promisor-grid.py --arm both \
  --case PG43-fleet-unhydrated-blobless-report-required --json
# exit 0

# 2) same single case, current arm only, --keep (to inspect the built fixture read-only)
TMPDIR=…/tmp python3 tests/report-audit/promisor-grid.py --arm current \
  --case PG43-fleet-unhydrated-blobless-report-required --json --keep
# exit 0

# 3) direct auditor run against the retained fixture (no grid in the loop)
cd …/tmp/promisor-grid-nqz4mssl/current/000
env -u GIT_DIR -u GIT_WORK_TREE GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
  python3 …/repo/tools/report-landing-audit.py \
  --lane-repo …/lane --fleet-repo …/fleet --rounds 1 --json --no-errata
# exit 2   (stdout 0 bytes; stderr = the refusal below)
```

## 3. Views, and which one PG43 is graded against

`PG43` has **no `amended` entry** in the manifest (`d86b7bea…`), so per the grid's
`live = expect.get("amended", expect["original"])` its graded view is the **original** row:

```
frozen:   exit 2, kinds null, reason_class "metadata",  defects null
original: exit 2, kinds null, reason_class "unavailable", defects null   <-- graded
names_any_of:     ["$report_blob", ".ufo/reports/round-1/kama.md"]
reason_forbidden: ["partial clone (", "promisor pack"]
twin: null
```

The original view is therefore **live for this row and was not withdrawn**: the grid reports
`met_original = true` for the current arm and the wave-level `withdrawn_original_failures`
bucket for this selection is **empty**. Nothing withdrawn at wave level (the round-24
unknown-from-metadata expectation) is claimed as passed by this row.

**Frozen history is history, not an improvement.** The frozen (r23) arm also exits 2, but with
the blanket metadata refusal:

```
could-not-evaluate: …/fleet: partial clone (promisor pack)
```

so `met_frozen = true` (history met) and `met_amended_frozen = **false**`. The live-view
comparison is: **frozen arm 0/1 amended-view met → current arm 1/1**; `violations = 0` in both
arms, `tracebacks = 0`, `timeouts = 0`, `harness_leaks = 0`. Exit code alone cannot separate
the two arms (both are exit 2) — the row is carried entirely by the *reason content* checks
(`reason_forbidden` + `names_any_of` + `reason_class`), which the grid applies to the current
arm only.

## 4. Premise assertions (independently inspected, `--no-lazy-fetch` everywhere)

Fixture: `c_fleet_unhydrated_blobless` = `build(root, tmp, fleet_mark="config", blobless_fleet=True)`
— no object is manually dropped; the fleet is a **real `file://` blobless partial clone** of the
fleet origin, and the lane is plain and complete.

* fleet clone config: `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`,
  `remote.origin.url=file://…/fleet-origin` (**live, local, reachable**).
* fleet clone objects present (7): commits `18f93ab8…`, `f723c76c…`; trees `b1e11739…`
  (tip tree), `d184003c…`, `d715303b…`, `e403e64d…`, `e670c1ca…`.
* fleet clone objects missing (exactly 2 blobs, `rev-list --objects --missing=print`):
  * `0cf7ed5cd6dec335553d165dc587baa224ab302b` = the **report blob** at
    `.ufo/reports/round-1/kama.md` → this is `$report_blob` (verified against
    `fleet-origin rev-parse HEAD:.ufo/reports/round-1/kama.md`) → **the required evidence is
    genuinely absent**;
  * `bfa655111293037a5564088d1a9bbca4cbcf446b` = the `notes.md` blob → unused by the audit.
* lane: plain (no promisor config), **complete** — 5 objects, `missing_objects == []`; it holds
  the cited round-1 lane commit.
* fleet clone working tree is **empty** (no `.ufo/` directory): the auditor cannot silently fall
  back to a working-tree copy of the report.

## 5. Measured observation (current arm, pinned candidate)

```
exit:            2
stdout:          0 bytes   (no verdict document → obs["document"] is null)
defects/tokens:  none — the row yields no finding/token pairs by construction (no document)
stderr:
could-not-evaluate: unavailable required object: .ufo/reports/round-1/kama.md at fleet HEAD
(tip tree b1e11739fedfb736f2936bd9addf7e4a286d462e, …/fleet): git show
HEAD:.ufo/reports/round-1/kama.md in …/fleet: rc=128 fatal: bad object
HEAD:.ufo/reports/round-1/kama.md
```

Checks against the live expectation:

* `exit 2` == expected 2 ✔
* reason class `unavailable`: stderr contains git's own `bad object` (a listed term) ✔ and the
  message is derived from the **actual failed read** of the required report, not from metadata ✔
* `reason_forbidden`: neither `partial clone (` nor `promisor pack` appears ✔ (the r23 blanket
  refusal is *not* the reason)
* `names_any_of`: the registered path `.ufo/reports/round-1/kama.md` is present ✔ (see F2 for
  the OID alternative)
* no JSON verdict on stdout, no traceback, no timeout, no harness leak ✔

**No objects acquired.** Independent check on the retained fixture: fleet object inventory
`7 → 7` across the audit; the `.git` file listing is byte-identical before/after (no
`FETCH_HEAD`, no new pack, no new loose object). The grid's own pin agrees
(`objects_acquired = {"lane": [], "fleet": []}`). Static confirmation: every auditor git call
goes through `git()` with `GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch", …)`
(`tools/report-landing-audit.py:138`, `:160-163`), so no lazy fetch is possible.

**Metadata blindness (static, source-side).** The pinned auditor contains **no** read of
`extensions.partialclone` / `remote.*.promisor` / `remote.*.partialclonefilter` outside its own
self-test (`:1176-1195`); the only mentions are the isolation flag and the doc text. The frozen
r23 auditor, by contrast, refuses on exactly that metadata
(`git cat-file 0df800e8…:tools/report-landing-audit.py | grep promisor` → line 457
`raise EvalError(f"{repo}: partial clone (promisor pack)")`). Promisor metadata therefore cannot
change the verdict in the pinned candidate — the amendment's core clause holds for this row.

**Actual twin document comparisons: none exist for this row, and none is possible.** The
manifest declares `twin: null` for PG43 and no other row names PG43 as its twin (checked over all
47 rows), so the run reports `twin_pairs_in_manifest = 0`, `twin_compared = 0`,
`twin_mismatch = []`. This is consistent, not a defect: PG43 produces no verdict document, so a
document comparison could not be performed even if a twin were declared. The *shape* (missing
fleet report → exit 2) carries its twin evidence in `PG17-missing-fleet-report-promisor` ↔
`PG18-missing-fleet-report-plain`, which register the same `names_any_of` and the same exit-2
expectation.

## 6. Findings

### F1 — FIXTURE (medium): the promisor remote of the blobless fleet is live, so the
### "unavailable required evidence" premise can be silently destroyed by a fetch-capable probe

`blobless_clone` (`tests/report-audit/promisor-grid.py:225-236`) leaves the clone's
`remote.origin.url` pointing at the **reachable** `file://…/fleet-origin`, which still holds the
report blob. Any git command issued against that clone **without** `--no-lazy-fetch` triggers a
promisor lazy fetch that materialises the missing blob — the premise vanishes and the verdict
flips.

Demonstrated A/B on two identically built fixtures (same builder, same auditor, same pinned
sources):

| fixture | state of report blob | auditor result |
|---|---|---|
| `promisor-grid-i2viosv7` | materialised by one probe `git cat-file -e HEAD:.ufo/reports/round-1/kama.md` (no `--no-lazy-fetch`); a second promisor pack `pack-9ea1ce01…` appears, object count 7 → 8 | **exit 0, "clean"** — a *false* clean verdict (defects 0, required 1) |
| `promisor-grid-nqz4mssl` | absent (verified `cat-file -e …` → ABSENT under `--no-lazy-fetch`) | **exit 2**, content-derived refusal (correct) |

Disclosure: the contaminating probe was **mine** (I ran a fetch-capable `cat-file -e` while
inspecting the first retained fixture); the grid's own machinery is safe — every probe it uses
(`missing_objects`, `object_exists`, `object_inventory`) is `--no-lazy-fetch`, and the fresh
fixture `nqz4mssl` contains exactly one pack (the clone's own) with no fetch side effects. So
this is **not** a source defect and **not** a grid defect; it is a *fixture robustness* defect:
the premise is held only by the auditor's own discipline, and any future consumer, reviewer or
mutation that touches the clone without the flag will observe a clean exit 0 for a repository
whose required report is unavailable.

Minimal correction (**fixture-only, not applied here** — production is read-only for this lane):
after the blobless clone, point the clone's `remote.origin.url` at an unreachable path (the
builder already uses `absent-remote.git` for the config-marked lane) so that a stray lazy fetch
*fails loudly* instead of succeeding silently, or assert in `build()` that the report blob is
still absent in the clone **and** in its origin before the auditor runs. This must be validated
over the whole blobless family (`PG05-hydrated-blobless-lane`, `PG06-hydrated-blobless-fleet`,
`PG43-…`); I measured only PG43.

### F2 — EXPECTATION/GRADER (low): the row is carried by the manifest-registered *path*
### alternative; the refusal does not name the missing report blob's object id

The refusal names the required **path** and the **tip tree** id
(`b1e11739…`), but not the unavailable blob id `0cf7ed5c…`. The grader's `check_exit2_form`
uses `any(n in err for n in names)`, and the manifest registers the path for PG43, so the row
passes as written. This is **not** the declined path-based loosening: the receipt
(`.ufo/waves/round-24/build/out/GridOracle/RECEIPT.md:135-150`) records that the runner
loosening which accepted *arbitrary* `HEAD:<path>` / fixture-`paths` expressions was **not
adopted**; the integrated runner `b034e159…` has no such mechanism, and the path used here is a
pre-registered `names_any_of` entry of the frozen 44-case manifest (the same entry exists for
PG17/PG18). Residual risk only: if the manifest's PG43 `names_any_of` were ever tightened to the
object id alone, the pinned auditor would fail that row, and the pinned auditor's report-read
path (`tools/report-landing-audit.py:455-464`) does not currently resolve `HEAD:<path>` to the
blob id before refusing. Reported as an observation; no change made.

### F3 — MANIFEST (low): PG43 contributes zero twin-document evidence

`PG43` is the only fleet-report-unavailability row without a declared twin, and no row names it.
For an exit-2 row with no verdict document that is structurally correct (a document comparison
would be `None`), but it means the amended clause "complete marked versus unmarked twins retain
identical substantive verdicts" is **not** exercised by this row: PG43 tests only the single-side
"required object unavailable → content-derived exit 2" behaviour. The marked/unmarked equality
for this shape rests on PG17↔PG18, which I did not run (out of my bounded selection).

### F4 — NO DEFECT (recorded for completeness): metadata alone cannot change this verdict

Statically confirmed above; and the frozen-vs-current arms differ only in the refusal's *content*
while sharing exit 2. The row is therefore sensitive to reason regressions, not to exit-code
regressions.

## 7. Residual risk and verification gaps

* Only PG43 was executed (as assigned). The 46 other rows, the grid `--selftest`, the auditor's
  own self-test, and the mutation probe were **not** run — no full-suite storm.
* F1's minimal correction was **not** applied and **not** validated across the blobless family
  (`PG05`, `PG06`); only PG43's A/B was measured.
* The contaminated fixture `promisor-grid-i2viosv7` is kept only as evidence of the A/B; it must
  not be reused for any further measurement (its premise is destroyed).
* The OID alternative of `names_any_of` was not exercised by any run (the auditor's reason never
  contains `0cf7ed5c…`); F2's residual risk is therefore *observed as a fact*, not speculative.
* Whether the unreachable-remote correction of F1 would alter the premise computation
  (`promisor_facts`, `missing_objects`) was checked statically only (no promisor-metadata read in
  the auditor; the grid's premise code is `--no-lazy-fetch` throughout) — not executed.

## 8. Files written

Production (append-only, read-only otherwise):

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseFleetBlobless.md` — this report
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseFleetBlobless/PG43-grid.json`
  — the assigned `--arm both --case PG43… --json` output (exit 0)
* `…/out/CaseFleetBlobless/direct-PG43-clean.stderr.txt`, `…/direct-PG43-clean.stdout.txt` —
  direct auditor run on the clean fixture (exit 2 / 0 bytes)
* `…/out/CaseFleetBlobless/contaminated-fixture-direct.stdout.txt`,
  `…/contaminated-fixture-direct.stderr.txt` — F1 A/B evidence (exit 0 "clean" after a lazy fetch)
* `…/out/CaseFleetBlobless/fleet-missing-objects.txt`, `…/lane-missing-objects.txt`,
  `…/fleet-config.txt` — premise evidence

Scratch (outside the repo, heavy/temporary): `/fast/scratch/hyaku/kama-r24/falsify/CaseFleetBlobless`
(clone `repo/`, `tmp/` fixtures and captures).

---

## 9. Addendum (appended after cross-lane coordination; no change to the verdict)

**A1 — F2 sharpened: the strong name is locally derivable in this exact fixture.** On the clean
retained fixture, `git --no-lazy-fetch -C <fleet> rev-parse 'HEAD:.ufo/reports/round-1/kama.md'`
returns `0cf7ed5cd6dec335553d165dc587baa224ab302b` with **rc=0** — the trees are present, so the
missing blob's id is resolvable without any fetch or blob content. The pinned auditor's refusal
does **not** carry it (`grep -c 0cf7ed5c… direct-PG43-clean.stderr.txt` → **0** matches): it
names the path and the tip tree only. So the path-only reason in PG43 is a *naming gap*, not a
physical impossibility, and the strong-name form of `names_any_of` is attainable on this shape.
Cross-lane corroboration: `KamaR23-2.DocFrontier` observed the sibling `repo-state-grid` F23
cell refusing with the absent blob OID `181389d343031fd578c6a775ce0889a8b0d` named — i.e. the
strong-name reason is already produced by another pinned path, while the
`report-landing-audit` report-read path does not produce it. No source edit made (read-only
lane); the observation is for L1's decision.

**A2 — F1 has a second, independent consequence beyond my own row (reported, not re-measured
here).** `KamaR23-2.GateMutationSelftest` reports that the committed mutation-sensitivity
artifact `build/out/MutationOracle/sensitivity-promisor-grid.json` has `pristine_unmet_cells` in
exactly the *evaporable* classes (PG15/PG16/PG19/PG20 missing-tree and PG46 opaque-tree-hides-
cited-blob). My A/B shows the evaporation is real and silent on this family's shape (a single
fetch-capable probe turns the correct exit 2 into a false exit 0 "clean", with the missing blob
now served locally). Therefore a stray probe between the pristine run and the mutant runs can
flip a would-be exit-2 refusal into exit-0 clean and silently change the kill set, independently
of that lane's own provenance finding. I did not re-measure the mutation artifact (out of my
bounded selection); I only confirm the *mechanism* on PG43.

**A3 — fixture-strengthening idea from a sibling lane (recorded for L1).**
`KamaR23-2.CaseFleetTree` uses a *bait* origin for its promisor fixtures: a valid local bare
repository that really holds the missing object, so that a lazy fetch is *detectable* (it shows
up as acquired objects) instead of succeeding silently. This is strictly stronger than my
F1 minimal correction (unreachable URL) and than a plain `absent-remote.git` URL: it keeps the
transport live yet makes any acquisition observable in the grid's own
`objects_acquired` pin. Worth considering for the whole promisor family.

**A4 — F3 corroborated cross-lane (twin links on exit-2 rows are never automatically
asserted).** `KamaR23-2.CaseReportBlob` measured the same structural fact on PG17/PG18: the
grid's twin comparison is *document*-based, so for an exit-2 row the twin link yields
`twins={'PG18-…': None}` with `twin_compared = 0` while `twin_pairs_in_manifest = 1` — the
declared twin link is never machine-asserted (that lane compared the two refusals by hand and
found them identical modulo the fixture path). This is the same mechanism behind my F3: for
PG43, which declares `twin: null` and yields no document, the row contributes **no** twin
evidence at all, and the amended "marked vs unmarked twins retain identical substantive
verdicts" clause is exercised only where a verdict document exists (or, for the exit-2 shapes,
by manual comparison outside the grader). Recorded for L1; no grid change proposed or made by
me.

**A5 — F1's A/B control is provably two distinct stores (precision, at
`KamaR23-2.GateAuditSelftest`'s request).** The caution that a "blob materialised by one stray
probe" clone is no longer the fixture one thinks one holds applies — and my A/B already records
it. In the contaminated arm (`promisor-grid-i2viosv7`) the materialisation is *measured*, not
assumed: report blob `0cf7ed5c…` is `PRESENT_NOW` under `--no-lazy-fetch`; the missing-object
walk shrank from two holes to exactly one (`?bfa65511…`, the unused `notes.md` blob); the object
inventory went 7 → 8; and a second promisor pack `pack-9ea1ce01…` appeared in the clone's
`objects/pack` (the clone's own pack is `pack-e449375b…`, present unchanged in the clean arm).
The clean arm (`promisor-grid-nqz4mssl`) still shows one pack, 7 objects and both holes, and
its auditor run acquired nothing (7 → 7, `.git` file list byte-identical). The two arms are
therefore provably different stores.

Stated precisely, the A/B demonstrates **premise-dependence, not auditor nondeterminism**: once
the missing blob is served locally, "the required report evidence is unavailable" is no longer
true, and the auditor's exit 0 is a *correct* verdict for the store it was given — the defect is
that the fixture's premise can be voided out of band, silently, by a probe that omits
`--no-lazy-fetch`. Tool-side the isolation is unconditional (per `KamaR23-2.GateAuditSelftest`:
`tools/report-landing-audit.py` has a single git subprocess site at `:162`, prefixed with
`GIT_ISOLATION` at `:138`, so no tool-internal probe can materialise a blob — consistent with
my own source reading and with the 0-acquisition measurement).

**A6 — validation anchor for the shared fix, and a second-lane corroboration of A1.** (i) The
pinned runner **already carries the pin** the shared fixture correction can be validated with:
`tests/report-audit/promisor-grid.py:808-810` raises the problem `"the audit acquired objects:
…"` and `:822-826` computes the object-set delta around the auditor run — so an unreachable-URL
(or bait-origin) correction turns any acquisition into a visible, graded failure instead of a
silent premise evaporation. (ii) `KamaR23-2.CaseReportBlob` independently corroborates A1 on the
PG17/PG18 shape: the fleet tip tree `b1e11739…` is present and `git ls-tree HEAD` lists
`100644 blob 0cf7ed5c…0302b .ufo/reports/round-1/kama.md`, i.e. the missing blob's id is
readable from present local content with **no transport**, while the pinned refusal still names
only the path + tip tree (OID occurrences in stderr: 0). Their reported minimal-correction
candidate — resolve the path id fetch-free in `audit_round` and include it in the
`required_read` reason — is the same conclusion as my A1, reached from a sibling row. Both
proposals are **reported only**; no source was edited by this lane.

**A7 — implementation constraints for the shared fixture correction** (from
`KamaR23-2.CritNoTrade-3`, recorded here so the constraint set is in one place for L1).
(a) A `remote.origin.uploadpack` trap intercepts only the **file:// and ssh** transports; an
`http(s)` remote ignores it, so the trap alone is not transport-independent — pair it with the
URL repoint to get fail-closed behaviour regardless of transport. The grid is file:// only, so
the trap suffices there today. (b) The lock must be applied **after** any intended hydration:
`hydrate()` copies object files offline, so locking the remote afterwards cannot affect PG05 /
PG06 (hydrated pair stays intact), whereas PG28 / PG43 depend on the objects staying missing and
must be locked right after `blobless_clone()`. Family-wide validation of PG05 / PG06 / PG28 /
PG43 remains **open** — no lane has executed the corrected family (this lane measured PG43
only, before any correction).

**A8 — the auditor side of F1 is measured independently (cross-lane, `KamaR23-2.CaseLaneTree`).**
On a rebuilt PG15 lane whose `remote.origin.url` was repointed at a local bare repository that
**really serves the missing tip tree**, the auditor still exits 2, acquires nothing in the lane
*or* in the remote, and the tree stays missing; the *same lane without* `--no-lazy-fetch` does
lazy-fetch the tree (trap live). That is the auditor-side counterpart of my A5: with a reachable
origin in place, the pinned auditor never materialises the missing object (all of its git calls
carry `--no-replace-objects --no-lazy-fetch`), so F1 remains a **probe-side/fixture-side**
hazard only — the graded path is unaffected. Their report cites it as F4 in
`.ufo/waves/round-24/falsify/advice/CaseLaneTree.md`; no source defect, nothing edited.

**A9 — complementary coverage: PG43 is one of the few rows that can test "the promisor remote is
never contacted" at all** (cross-lane, `KamaR23-2.CaseUnrelatedFakeLanded` and the config-marked
family generally). Their F1 observes that PG22's config-marked fixture points
`remote.origin.url` at an **absent** path, so it can falsify *metadata-independence of the
verdict* but **cannot** falsify "the promisor remote is never contacted" — with no reachable
remote there is nothing to contact, so the property is untestable in that shape. PG43's blobless
fixture is by construction the opposite case: its origin is a **live** local `file://` repository
that really holds the missing report blob, so the property *is* falsifiable there — and it holds
on the pinned candidate by my measurement: the auditor exits 2, the fleet inventory stays at 7
objects, the `.git` tree is byte-identical (no `FETCH_HEAD`, no new pack, no loose object), and
the remote's own object store is untouched. Together with A8's bait-origin run (auditor acquires
nothing even when the origin serves the object), the "never contacted" claim is exercised on a
reachable origin somewhere in the family — which the absent-remote fixtures cannot do. Recorded
for L1's coverage view; no source edit.

**A10 — precision on the no-acquisition pin (A6 corrected/qualified by
`KamaR23-2.CaseLaneTree`).** The pin's scope is narrower than A6's wording implied: the runner
compares the object inventories of the **audited lane and fleet stores only**
(`promisor-grid.py:808-810` raises the problem, `:822-826` computes the delta). It therefore
**cannot** observe (i) a failed transport attempt, (ii) a fetch that lands in the **origin**, or
(iii) any fetch performed by a probe outside the grader. With the shipped `absent-remote.git`
URL all three are unobservable **by construction**; a repointed bait origin closes the
observable half (the origin's own inventory can then also be compared, and a trap fires when the
isolation is removed). So the bait-origin proposal is not merely "a stronger variant" of the
unreachable-URL fix: it is the only form that makes a *transport-level* attempt observable
rather than merely failing, which is exactly the property my A5 needs for the control to be
trustworthy. Recorded for L1 as a fixture-level proposal owned by L1; **not applied by this
lane**, and the family-wide validation of PG05/PG06/PG28/PG43 remains open.

**A11 — isolation-side corroboration, and the exact fetch-capable door in the harness**
(cross-lane, `KamaR23-2.CodeGitBoundary`, pinned `2e254a17`). (i) On a synthetic promisor-marked
store, `git cat-file blob <missing>` / `git show HEAD:<missing>` **with the auditor's production
flags** (`--no-replace-objects --no-lazy-fetch …`) fail locally ("bad file") with **no transport
attempt**, while the same commands **without** `--no-lazy-fetch` make **three** transport
attempts — confirming at the command level what my A5/A8 showed behaviourally: the auditor's own
reads can never materialise a blob, so F1's door is a probe *outside* `GIT_ISOLATION`. (ii) The
r24 missing-object walk itself is transport-inert: `git rev-list --objects --missing=print
--no-object-names --stdin` (the walk at `tools/report-landing-audit.py:672`) is byte-identical
with and without `--no-lazy-fetch` and never contacts the remote, because `--missing=print`
suppresses the on-demand fetch — so the amendment's "bounded missing-object traversal" cannot
become a fetch. (iii) The harness door is named precisely: `tests/report-audit/promisor-grid.py`
`:99-104` `git()` carries **no timeout and no `--no-lazy-fetch`** (only `git_nofetch` `:109-111`
and its three probe call sites are safe); it is the fetch-capable helper, and it is **not**
exercised for object reads on the blobless clone by the current builders (the post-clone probes
go through `missing_objects`/`object_exists`/`object_inventory`, all `--no-lazy-fetch`) — a latent
door rather than an active one, and their F8 records the missing timeout. Recorded for L1; no
source edit by this lane.

**A12 — PG43 natively supplies what PG15/PG16 had to fake: the grid's own premise machinery is
already exercised against a *live* origin and does not materialise the blob**
(complements `KamaR23-2.CaseLaneTree` §13, which had to monkey-patch `mark_config` in a probe
process to give PG15 a live origin). PG43's builder needs no such patch: `blobless_clone()`
leaves `remote.origin.url` pointing at a reachable local bare repository from the start. After
the grid's own current-arm run on that fixture (`promisor-grid-nqz4mssl`), the premise was
**intact** — fleet inventory 7 objects, `rev-list --objects --missing=print HEAD` still lists
both holes (`?0cf7ed5c…` required report blob, `?bfa65511…` unused `notes.md` blob), exactly one
promisor pack (`pack-e449375b…`), no `FETCH_HEAD`, no loose object — and the auditor run in the
very same fixture returned the correct exit 2. The materialisation in my A/B came **only** from
my out-of-grader probe (`git cat-file -e HEAD:<path>`, no `--no-lazy-fetch`), never from the
grid. Conclusion: the grid's generic, fetch-capable `git()` (`:99-104`) is **latent** for the
blobless family as well — the post-clone object reads all go through `missing_objects` /
`object_exists` / `object_inventory` (all `--no-lazy-fetch`), and the pre-clone reads happen
while the object is still present. So for PG43 the hazard is an **observability/discipline** gap
(a stray probe, as in A5), not a premise-integrity defect in the graded path — consistent with
CaseLaneTree's refined F4.

**A13 — L1 disposition of F1 (recorded; supersedes my minimal-correction proposals).** L1's
decision, aligned with Main: the A/B is preserved as a **CHANGED INPUT** after manual
hydration — never as an unchanged-fixture verdict and never as a detector repair. The proposed
**GridAttestation** retains the **connected local origin** control (no URL repoint, no origin
deletion), keeps the no-fetch forensics, fresh case instances and the acquisition pins, and adds
explicit **pre-audit blobless/hydration premise asserts**; no frozen expected cell is rewritten.
Consequences for this lane's record: my F1 alternatives (unreachable URL, failing `uploadpack`
trap, bait origin — A3/A6/A7/A10) are **superseded** by the attestation approach; F1's
observability/discipline characterisation (A5, A8, A11, A12) stands as the evidence base, and
Main holds all hazard evidence. This lane's scope is complete: no further rebroadcast, probe or
re-measurement, and the production tree was never mutated (only the two designated falsify
paths written).

**A14 — the false-verdict symptom is body-dependent, and the probe-form precision
(cross-lane, `KamaR23-2.ConnClosure-2` §5b; artifacts `build/out/ConnClosure/probe_fixture_hazard.py` + `-result.json`).**
(i) Reproduced with the grid's own helpers (`blobless_clone`, `object_exists`, `missing_objects`),
local `file://` only: before a stray probe `object_exists` = False and `missing_objects` =
`['c2981a99…']`; one `git cat-file -e <oid>` **without** `--no-lazy-fetch` → rc 0, the blob now
present, `missing_objects` empty. The auditor **alone** is stable (exit 2 on two consecutive
runs, premise intact); the auditor **after** the stray probe returns **exit 1** with kinds
`[landed-unresolved deadbee1…]` — i.e. the content-derived refusal degenerates into a **false
FAILED** verdict, where my PG43 body degenerated into a **false clean** (exit 0). The mechanism
is identical (the premise is voided); only the *shape* of the wrong verdict depends on the report
body, so both symptoms must be expected from the same probe. (ii) Probe-form precision:
`cat-file -e HEAD:<path>` **materialises** (rc 0), `cat-file -e <oid>` **materialises** (rc 0),
and the peeled path `cat-file -e HEAD:<path>^{blob}` does **not** (rc 128, "path … does not exist
in 'HEAD'") — the peel form is safe only by accident and must not be relied on. With
`--no-lazy-fetch` every form correctly reports absence (rc 1). (iii) The path form is **not an
honest existence test** even when it succeeds: it resolves the *path* without the blob. The
grid's `object_exists` uses the raw `<oid>^{object}` peel, which *is* honest — do not relax it to
a path form. (iv) Blast radius on this lane: the r24 grid is **not** exposed — every post-clone
call inside `build()` is `object_exists` / `missing_objects` / `object_inventory` (all
`--no-lazy-fetch`), and the grid removes its temp root in a `finally`
(`promisor-grid.py:1082-1085`) unless `--keep`; no promisor marker in the lane or fleet, no
`promisor-grid-*` temp root survives my runs. (v) **One live instance of the hazard exists
outside my lane on this host** — `/tmp/repo-state-grid-4eddb0bx/current/30/` (a `--keep`-style
leftover whose blobless clone still has a reachable local origin and a still-absent blob
`6e98d181389d343031fd578c6a775ce0889a8b0d`, so its premise is currently ALIVE). I did **not**
touch it (operator hygiene, outside the lane/fleet and outside my remit to delete); it is flagged
to L1 as an operator-hygiene item, since one stray probe there turns a correct exit 2 into a
false verdict. Mitigation to state in the wave: probe a promisor-marked store only with
`--no-lazy-fetch` **and** `--no-replace-objects`, and prefer the grid's own `object_exists` /
`missing_objects` helpers over a bare git call.

**A15 — agreed general wording for a voided premise (with `KamaR23-2.ConnClosure-2`).** The two
seats measured the voided premise on **different report bodies**: my PG43 body yielded a false
**clean** (exit 0) and ConnClosure-2's body a false **failed** (exit 1, `landed-unresolved
deadbee1…`). Both are true and **neither is the general rule**: on a voided premise the verdict
becomes **undetermined**, not "the auditor produces a clean" (and not "the auditor produces a
failed"). The correct claim, for the wave record, is:

> With a required object voided by an out-of-grader probe, the auditor's verdict on the
> *unchanged* fixture is no longer determined by the missing evidence; any concrete exit code
> observed afterwards follows from the report body and the surviving local content, and the
> audit's own isolation (GIT_ISOLATION) is what keeps the graded path deterministic.

Consequently, F1's severity rests on the **premise/observability** defect (the fixture's
"unavailable required evidence" state is mutable out of band, and the refusal that depends on
it is therefore not reproducible by anyone who probes the store casually), not on any claim about
the auditor's bias. Mitigation remains two rules: isolation flags (`--no-lazy-fetch` **and**
`--no-replace-objects`) **and** probe form (raw `<oid>^{object}`, never a path form).

**A16 — F2/A1's naming gap reproduced on a second body (closure record).**
`KamaR23-2.ConnClosure-2`'s fleet-blobless refusal reads
`unavailable required object: .ufo/reports/round-1/kama.md at fleet HEAD (tip tree e01cd688…)`
— it names the **path** and the **tip tree** but never the missing blob's own id
(`0dd809a7…`), which is fetch-free derivable from the store (their substring check on the
recorded stderr). So the naming gap is **not specific to my fixture**: it reproduces on a
second, independently built fleet-blobless body, with a different tip tree and a different
missing blob id. Severity stays low and the item stays **outside r24's preregistered scope** —
named and evidenced, not proposed as a change; the L1's disposition of the r24 scope (A13)
already fixes what is in and out for this round. Closing state of the exchange: both seats
converged on the same mechanism, the same "latent door" framing, the same two-rule mitigation
and the same "verdict undetermined on a voided premise" wording; no further hazard rebroadcast
from either seat; the `/tmp/repo-state-grid-4eddb0bx/current/30/` leftover stays with L1 /
operator hygiene and was touched by neither seat.

Report: .ufo/waves/round-24/falsify/advice/CaseFleetBlobless.md
