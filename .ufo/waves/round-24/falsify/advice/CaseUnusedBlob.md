# CaseUnusedBlob — PG35/PG36 promisor-grid falsification (round 24)

VERDICT: **HOLDS** for the graded contract. No source defect was found in
`tools/report-landing-audit.py` at `2e254a17` on the surface this family exercises. Five
fixture-level observations/weaknesses are reported separately below (F1–F5); none of them
changes the graded verdict of these two rows.

Scope: exactly one bounded selection — `python3 tests/report-audit/promisor-grid.py --arm
both --case PG35-unused-missing-blob-promisor --case PG36-unused-missing-blob-plain --json` —
run twice (once plain, once with `--keep --out` so the built fixtures could be inspected
directly), plus the read-only static reads and five direct auditor invocations against the
kept fixtures needed to assert the premises, the missing/present objects, the finding/token
pairs, the no-acquisition property, the twin comparison and a complete-plain reference
document. No other lane suite, no full grid, no mutation grid, no `--selftest`, no
execution-bearing probe, no network/transport payload (PM08 was **not** executed; it is
static-only). No production file other than this report and the `out/` artifacts was
written; production `production/.jj/index`, fleet, sibling lanes, operator config, routing,
services and real object stores were not touched.

## Axes and results

| # | Axis | Result |
|---|---|---|
| A1 | Assigned command, exit, in the pinned clone | PASS — exit 0, stderr empty, 2 graded rows, 0 violations in both arms |
| A2 | Actual missing / present objects asserted on the built fixture | PASS (observed) — unused blob `b2c475fedd466685003f05a02c7bd772186c0429` ABSENT from the lane store; lane commit `9bad795e8e7cbabfa1b3e699c5b461ad62271391`, its trees and both present blobs PRESENT; exactly one hole in the lane, zero in the fleet |
| A3 | PG35 (promisor-marked) vs PG36 (plain) is a content-identical twin | PASS (observed) — identical lane commit, identical 6-object lane inventory, identical missing blob, identical fleet report blob `f3c586507ddcede8ee52163a25299570c16d7199`; the **only** difference is the lane promisor config |
| A4 | Exact finding/token pairs | PASS — `defects []`, `raw_defects []`, `kinds []` in the current arm for both rows (expected `defects: []`, `kinds: []`); there is no token to resolve |
| A5 | Content-derived reason IDs | VACUOUS for the current arm — it refuses nothing on either row (exit 0, empty stderr), so no reason string exists to classify; the **frozen** arm's reason is the forbidden r23 metadata refusal (`partial clone (remote.origin.promisor)`), which the current arm does not reproduce. `reason_forbidden` is therefore satisfied vacuously, not by a substitute reason |
| A6 | No objects acquired | PASS (observed three times) — grid pin `objects_acquired {lane: [], fleet: []}` on all four rows; independently, a full sha256 snapshot of both `.git` directories taken before and after three further direct auditor runs is **byte-identical** (no new object, no pack, no `FETCH_HEAD`, no ref or config change) |
| A7 | Actual twin document comparison | PASS (observed) — grid `twins {PG36: true}` / `twins {PG35: true}`, `twin_equal true`, `twin_mismatch []`; independently, the two normalized verdict documents are equal, **and** both are equal to a freshly built complete-plain fixture's document (no hole, no promisor config) |
| A8 | Original (withdrawn) view kept visible | PASS — PG35/PG36 carry **no** `amended` key in the manifest, so the graded "amended" column is byte-identical to the "original" column; the current arm reports `withdrawn_original_failures: []` and `met_original: true` for both rows. The withdrawn expectation (unknown citation ⇒ exit 2) belongs to other rows and is **not** relabelled here |
| A9 | Frozen (r23) baseline retained and unchanged | PASS — frozen arm PG35 exit 2 with the metadata reason (exactly what the frozen view pins), PG36 exit 0; `amended_view_unmet: ["PG35-unused-missing-blob-promisor"]` in the frozen arm records the r23 harm the repair removes, and it stays visible |

## Snapshot, digests, environment (observed)

```
clone:  git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin \
            /fast/scratch/hyaku/kama-r24/falsify/CaseUnusedBlob/scratch
        git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84
HEAD  =  2e254a1763a9c08aa07fc53081287f506c447d84   (detached; tracked worktree clean,
        only untracked scratch `tmp/`)
```

| Item | Digest / value | Cross-check |
|---|---|---|
| pinned revision | `2e254a1763a9c08aa07fc53081287f506c447d84` | matches the assignment |
| source tool `tools/report-landing-audit.py` | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | matches the assignment's source tool; equals the grid's reported `auditor_sha256.current` |
| runner `tests/report-audit/promisor-grid.py` | sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | matches the assignment's runner |
| manifest `tests/report-audit/promisor-grid-expectations.json` | sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | matches the assignment's manifest; equals the grid's `expectations_sha256` |
| mutation probe `tests/report-audit/promisor-mutants.py` | sha256 `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` | matches the assignment's mutation probe (read only, not executed) |
| frozen auditor (r23 base blob `0df800e8…`) | sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` | equals `derived_from.frozen_auditor_sha256` pinned inside the expectations file and the grid's `auditor_sha256.frozen` |
| population | `population_sha256 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`, `population_size 47` | fixed47 population (original44 unchanged + 3 independent opaque cells), unchanged by this run |
| toolchain | `git version 2.56.0` (≥ the inherited 2.45 floor), `Python 3.14.8` | pre-existing; **no install or update was performed** in this lane |

## A1 — the assigned command (observed)

```
$ cd /fast/scratch/hyaku/kama-r24/falsify/CaseUnusedBlob/scratch
$ TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseUnusedBlob/scratch/tmp \
    python3 tests/report-audit/promisor-grid.py --arm both \
      --case PG35-unused-missing-blob-promisor \
      --case PG36-unused-missing-blob-plain --json
EXIT=0     (stderr empty, 0 bytes)

$ ... same command with --keep --out .../out/CaseUnusedBlob
EXIT=0     (stderr empty)
```

Grid summary (observed):

```
frozen : graded=2 violations=0 tracebacks=0 timeouts=0 harness_leaks=0
         amended_view_met=1/2  amended_view_unmet=["PG35-unused-missing-blob-promisor"]
         withdrawn_original_failures=[]  twin_mismatch=[]
current: graded=2 violations=0 tracebacks=0 timeouts=0 harness_leaks=0
         amended_view_unmet=[]  withdrawn_original_failures=[]  twin_mismatch=[]
         twin_pairs_compared=["PG35-unused-missing-blob-promisor","PG36-unused-missing-blob-plain"]
```

Per-row observations (observed):

| Row | arm | exit | defects / raw_defects | kinds | expected (live column) | met |
|---|---|---|---|---|---|---|
| PG35-unused-missing-blob-promisor | current | 0 | `[]` / `[]` | `[]` | exit 0, kinds `[]`, defects `[]` | `met_amended true`, `met_original true` |
| PG36-unused-missing-blob-plain | current | 0 | `[]` / `[]` | `[]` | exit 0, kinds `[]`, defects `[]` | `met_amended true`, `met_original true` |
| PG35-…-promisor | frozen | 2 | n/a (no document) | n/a | frozen pins exit 2, reason_class `metadata` | `met_frozen true`, `met_amended_frozen false` |
| PG36-…-plain | frozen | 0 | `[]` / `[]` | `[]` | frozen pins exit 0 | `met_frozen true`, `met_amended_frozen true` |

Frozen PG35 stderr (exact, observed):
`could-not-evaluate: …/frozen/000/lane: partial clone (remote.origin.promisor)` — the r23
metadata blanket refusal, i.e. exactly the harm the round-24 repair removes. The current arm
produces **no stderr at all** on either row, so the r23 reason is not reproduced.

Verdict document (both current rows, identical after path normalization): one round, report
committed, `cutoff 2000`, `round_commits 1`, `required 1`, `defects []`, `status "clean"`,
`errata_rows 0` — a real audit ran, not an empty or short-circuited document.

## A2/A3 — the fixture premises, asserted directly on the kept fixtures (observed)

The second run (`--keep`) left the built fixtures at
`…/scratch/tmp/promisor-grid-3k6dqa2a/{current,frozen}/{000,001}/`; `current/000` = PG35
(marked), `current/001` = PG36 (plain). Every **object-reading** probe (`cat-file`,
`rev-list --objects --missing=print`, `cat-file -e`) used `git --no-lazy-fetch
--no-replace-objects`; the remaining probes (`rev-parse`, `ls-tree`, `for-each-ref`,
`config --list`) read refs, trees and config only and cannot materialise a blob. All probes
ran with `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1` (no network, no
transport, no repository program).

| Assertion | PG35 (current/000) | PG36 (current/001) |
|---|---|---|
| lane refs | `refs/heads/master 9bad795e8e7cbabfa1b3e699c5b461ad62271391` | identical |
| lane store size | 6 objects | 6 objects — the **same** object list (content-addressed ⇒ identical) |
| lane objects | `051975b0…` blob (corpus/SOURCES.md), `56d7b323…` blob (`f`), `b2c475fe…` blob (**missing**), `742d4d0b…`/`85bb469a…`/`dfe44fa5…` trees, `9bad795e…` commit | identical |
| unused blob `notes/unused.txt` | oid `b2c475fedd466685003f05a02c7bd772186c0429`, loose object file **ABSENT** | identical (ABSENT) |
| availability probe `cat-file -e b2c475fe…^{object}` | exit 128 (absent) | identical |
| grid premise `missing_objects(lane, "refs/heads/master")` | `["b2c475fedd46…"]` — **the premise does see the hole** | identical |
| grid premise `missing_objects(fleet, "HEAD")` | `[]` | identical |
| `rev-list --objects --missing=print` over all present roots | `?b2c475fedd46…` (exactly one hole) | identical |
| `rev-list --objects --missing=print --filter=blob:none` over all present roots | `[]` — the hole is a **blob**, so the opaque set is empty | identical |
| audited tree of the cited commit (`ls-tree -r HEAD`) | `corpus/SOURCES.md`→`051975b0…`, `f`→`56d7b323…`, `notes/unused.txt`→`b2c475fe…` — the hole is **inside the audited closure** | identical |
| lane promisor metadata | `remote.origin.promisor=true`, `extensions.partialclone=origin`, `remote.origin.url=…/absent-remote.git` (a non-existent local path) | **none** |
| fleet promisor metadata | none | none |
| fleet store | 9 objects, no hole; report blob `f3c586507ddcede8ee52163a25299570c16d7199`, body `# kama round 1 / ## Landed changes / - 9bad795e…` | identical |
| frozen-arm fixtures | identical object lists, same missing blob; frozen/000 carries the same promisor config, frozen/001 none | identical |

So the two fixtures are content-identical twins whose only difference is the lane promisor
configuration, and the four fixtures (2 arms × 2 cases) are byte-identical in content — the
frozen-vs-current difference is attributable to the auditor source alone, not to fixture
drift.

## A4/A6/A7 — independent re-verification outside the grid's own bookkeeping (observed)

Five distinct direct invocations of the pinned auditor against the kept fixtures (read-only,
local, exactly the argv the grid uses, `cwd` = fixture dir; the complete-plain reference
fixture was additionally rebuilt and re-run once for the evidence dump):

```
$ python3 tools/report-landing-audit.py --lane-repo …/current/000/lane \
      --fleet-repo …/current/000/fleet --rounds 1 --json --no-errata     EXIT=0  stderr 0 bytes
$ python3 tools/report-landing-audit.py --lane-repo …/current/001/lane \
      --fleet-repo …/current/001/fleet --rounds 1 --json --no-errata     EXIT=0  stderr 0 bytes
$ … same two rows without --no-errata                                   EXIT=2  (see F3)
$ … complete-plain reference fixture (no hole, no promisor config)      EXIT=0  stderr 0 bytes
```

- **Finding/token pairs**: both documents carry `results[0].defects == []`,
  `summary.by_kind` all zero and `summary.status "clean"` — exactly the expected
  `defects: []` / `kinds: []`. There is no token to resolve; the single citation
  `9bad795e…` is present and resolves (`found`).
- **Twin comparison**: the two normalized documents are equal, and the *complete-plain
  reference* document (built with the grid's own `build(root, tmp)` helper: no hole, no
  promisor config, premise `lane_missing []`) is equal to **both**. The missing unused blob
  and the promisor metadata therefore change nothing in the substantive verdict.
- **No objects acquired**: a sha256 snapshot of every file in `lane/.git` and `fleet/.git`
  taken before and after the direct runs is identical (`lane_git_changed []`,
  `fleet_git_changed []`): no new object, no pack, no `FETCH_HEAD`, no ref, no config
  change. The promisor remote URL points at a non-existent local path
  (`…/absent-remote.git`), so no fetch could even have succeeded; every one of my probes
  used `--no-lazy-fetch`.
- **Static cross-check of the isolation**: `GIT_ISOLATION = ("--no-replace-objects",
  "--no-lazy-fetch", …)` is prepended to **every** `git` call of the auditor
  (`tools/report-landing-audit.py:138`, `:162`), so `--no-lazy-fetch` is on the auditor's
  own invocations, not only on the grid's probes. Read statically only — PM08 was **not**
  executed.

## Why exit 0 is the correct verdict here (observed source, not inference)

- The report's single citation is the lane master commit `9bad795e…`, which is present, so
  `lookup()` answers `found` and `refuse_unknown()` skips it
  (`tools/report-landing-audit.py:430-431`). The store-wide missing-object diagnosis is
  therefore never computed for this fixture: `store.missing()` is reached only from
  `unknown_citation()` / `opaque_hole()` (lines 698 and 714), i.e. only for a citation that
  no audited repository resolves.
- The hole is a **blob**, so the `--filter=blob:none` walk reports an empty opaque set
  (observed), and `opaque_hole()` therefore returns `(None, None)` — no missing tree or
  commit could hide a name.
- The auditor never needs the blob: it reads the lane log (`round_commits`), the fleet
  report blob and `corpus/SOURCES.md`; `notes/unused.txt` is never read.
- This is exactly the amended contract, `oracle-amendment-1.json` `prospective_expected[4]`
  ("Incomplete but locally sufficient repositories are not refused merely because an
  unrelated historical blob, branch, or unused file is missing") together with
  `prospective_expected[0]`/`[3]` (promisor metadata alone never changes a clean/failed
  verdict; marked and unmarked twins keep identical substantive verdicts).

## Fixture weaknesses (reported separately from source findings)

**F1 (medium) — the graded expectation is insensitive to the hole's presence.** The premise
*is* recorded correctly (the grid's `missing_objects(lane, "refs/heads/master")` returns
`["b2c475fedd46…"]`, because this family's hole sits inside the audited closure), but the
builder never **asserts** it: no `Premise` is raised if the drop step silently stopped
removing the blob (contrast `c_opaque_tree_hides_cited_blob` and `c_cross_repo_found_promisor`,
which do assert their premises). Consequently a regression in the drop step would leave
PG35/PG36 exit 0, twin-equal and `met`, i.e. the rows would keep passing without the
property they are named for. The rows' real discriminating power is the **promisor-metadata**
axis (frozen exit 2 with `partial clone (remote.origin.promisor)` vs current exit 0), which
is genuinely exercised; the "unused hole does not block" axis is exercised only in the
sense that the hole is present in the fixture as built today.
Minimal correction (not applied — production is read-only for this lane): in
`c_unused_missing_blob_promisor` / `c_unused_missing_blob_plain`, after the drop, require
that `notes/unused.txt`'s blob is absent while the lane commit, the tip tree and the fleet
report blob are present (the pattern already used for `cited_hidden_blob` and
`cross_repo`), so that a drop regression fails the premise (exit 2) instead of silently
passing.

**F2 (low) — this family exercises only one of the three "unrelated hole" shapes.** The
amendment names "an unrelated historical blob, branch, or unused file". PG35/PG36 cover the
*unused file* shape, and (because the file sits in the cited commit's tree) they cover the
stronger "hole inside the audited closure that the audit never reads" shape as well. The
*historical* and *branch* shapes live in other rows — `PG31/PG32` (unselected branch) and
`PG44/PG45` (unused tree) — which are outside this bounded selection and were **not**
executed by me; this report says nothing about them.

**F3 (low) — the fixture lane has no errata ledger, so the audit is only runnable with
`--no-errata`.** Observed: with the ledger path enabled (no `--no-errata`), both rows exit
2 with `could-not-evaluate: git show 9bad795e…:registry/report-landing-errata.tsv in
…/current/000/lane` (the lane has no `registry/report-landing-errata.tsv`). This is the
auditor's documented design (`load_errata()` reads the ledger from the lane tip unless
`--no-errata`/`--errata` is given), and the grid compensates explicitly
(`run_auditor`: "--no-errata only when the cell does not exercise the ledger"). Because
**both twins refuse identically**, there is no asymmetry and no no-harm violation; but the
graded rows never exercise the ledger path, so an errata-path defect would not be visible
in this family.

**F4 (low, discriminating power of the twin check) — the verdict document has no field that
could differ between a promisor-marked and an unmarked repository.** Consequently
twin-equality is guaranteed by construction whenever the marked run returns a clean exit;
the twin column can only fail if the marked run produced a different *verdict*. The
meaningful twin signal in this family is therefore the frozen-vs-current contrast, not the
marked-vs-unmarked one.

**F5 (low, version-sensitive, source behaviour not defect at the observed version) — the
"a blob hole is not an opaque hole" classification depends on git's behaviour under
`rev-list --filter=blob:none --missing=print`.** Observed at git 2.56.0: the plain
`--objects` walk prints `?b2c475fe…` while the `--filter=blob:none` walk prints nothing,
so `opaque_hole()` sees no opaque hole. If another git in the supported range (≥ 2.45)
listed *missing blobs* under the `blob:none` filter, the same fixture would be classified
as having an opaque hole and PG35 would flip to a false exit 2. The local `git-rev-list(1)`
man page documents `--missing=print` as "a debug option to help with future 'partial
clone' development"; the auditor sticks to the pre-existing `--missing=print` /
`--filter=blob:none` primitives and does **not** use the newer `--missing=print-info` /
`--missing-only`, which is exactly what `oracle-supplement-2.json`'s `version_constraint`
requires. The behaviour is not pinned by the contract, so it remains a version-dependent
assumption on the inherited Git ≥ 2.45 prerequisite (still open at L0).

## Source findings

**None.** On the surface this family exercises — a promisor-*config*-marked lane, a missing
blob inside the audited commit's tree that the audit never reads, one resolvable citation —
`tools/report-landing-audit.py` at `2e254a17` produces the ordinary clean verdict, refuses
nothing, names no metadata reason, acquires nothing, and produces a verdict document
identical both to its unmarked twin's and to a hole-free reference's. I did not find a defect
to correct in the source.

## Observed vs inferred

- Observed (executed and read back): every exit code, every stderr byte, every digest, the
  four fixture layouts, the missing/present status of each object, the premise values, the
  two `--missing=print` walks, the defect/token lists, the object inventories and full `.git`
  snapshots before/after, the normalized and reference documents, the grid's per-row grades,
  the twin comparison, the errata-on/errata-off pair.
- Inferred (source reading, not executed): that the store-wide missing-object diagnosis is
  never computed for this fixture (from the `refuse_unknown` → `unknown_citation` /
  `opaque_hole` control flow), that the auditor never reads `notes/unused.txt` (from the
  reads it performs: lane log, fleet report blob, `corpus/SOURCES.md`), and that the
  auditor's own git calls all carry `--no-lazy-fetch` (from `GIT_ISOLATION`; read statically
  only — PM08 was not executed).

## Residual risk / verification gaps

1. **F1 stands**: the graded expectation for PG35/PG36 does not depend on the hole being
   present. My independent premise probe establishes that the hole **is** present in the
   fixtures as built today; a future builder regression that silently stopped deleting the
   blob would not be caught by these rows.
2. **F5 stands**: the blob-hole-vs-opaque-hole classification is a git-version assumption
   verified only at git 2.56.0. The inherited Git ≥ 2.45 prerequisite is still open at L0;
   no other git version was exercised (installing one would have been a system mutation,
   which this lane forbids).
3. The "no objects acquired" evidence rests partly on the promisor remote pointing at a
   non-existent local path, so a *successful* lazy fetch is impossible here. The observable
   evidence is "no fetch happened and no object appeared", which is the pin the round
   contract requires, but it cannot distinguish "never attempted" from "attempted and
   failed" (the latter would also surface as exit 2 and fail the row).
4. The blobless-clone hazard reported by a sibling lane (`KamaR23-2.CaseFleetBlobless`: a
   `file://` blobless clone can materialise missing blobs under any probe lacking
   `--no-lazy-fetch`) does **not** apply to this family: PG35's lane is a plain local
   repository with promisor *config* only, whose remote URL is a non-existent path, and
   every probe I ran used `--no-lazy-fetch`.
5. `--selftest`, the full 47-row grid, `repo-state-grid.py`, the mutation grid and the
   auditor's own selftest were **not** run (out of scope for this bounded lane).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseUnusedBlob.md` (this report)
- `…/falsify/out/CaseUnusedBlob/grid-PG35-PG36.json` — assigned run stdout (both arms, 2 cases)
- `…/falsify/out/CaseUnusedBlob/grid-PG35-PG36-keep.json` — second run with `--keep` (fixtures retained for direct inspection)
- `…/falsify/out/CaseUnusedBlob/grid-PG35-PG36.stderr.txt` — empty stderr capture (0 bytes)
- `…/falsify/out/CaseUnusedBlob/population.json`, `…/candidate.json` — the grid's own `--out` dump (population sha `612b0a74…`, 47 rows)
- `…/falsify/out/CaseUnusedBlob/independent-assertions.json` — my independent measurements: fixture object inventories, premise values, both `--missing=print` walks, promisor config, direct-run exit/defect/status, `.git` before/after snapshot equality, errata-on/off pair, and the three equal documents (PG35, PG36, complete-plain reference)

Scratch (outside the repo): `/fast/scratch/hyaku/kama-r24/falsify/CaseUnusedBlob`
(clone + `scratch/tmp/` retained fixtures + direct-run outputs; `TMPDIR` was set inside it
for every subprocess).

Production lane `production/.jj/index`, fleet, sibling lanes, operator config, routing,
services and real object stores were not touched. No network, transport or execution payload
was used; PM08 was not executed. No tool was installed or updated (git 2.56.0 and Python
3.14.8 were already present).

## Unverified items

- The full population (47 rows) was not run; only PG35 and PG36 were executed, twice each
  (grid run + `--keep` grid run), plus direct auditor invocations against the kept fixtures.
- The frozen (r23) arm was exercised only through the grid's frozen blob `0df800e8…`; I did
  not diff the r23 auditor source against the pinned one beyond reading its refusal message.
- No mutation was executed against these rows (the mutants were read, not run).
- The auditor's `selftest` and the grid's `--selftest` were not run.
- Rows PG31/PG32, PG37, PG41/PG42, PG44/PG45 and the opaque family PG46–PG48 were **not**
  executed and are not covered by this report.
- The `file://` blobless-clone hazard was not probed in this lane (no blobless fixture is
  built by this family; no network use was permitted and none was attempted).

Report: .ufo/waves/round-24/falsify/advice/CaseUnusedBlob.md
