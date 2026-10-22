# CaseUnrelatedFakeNotes — HELD (assigned attack did not falsify the candidate on this family); one fixture-coverage gap noted

## Axes

Correct local verdict preservation under an unrelated missing object; promisor-metadata neutrality (marked vs unmarked twin); content-derived refusal diagnosis vs blanket refusal; no-object-acquisition / no-lazy-fetch isolation; expectation integrity (no cell edited to fit the candidate); frozen-vs-amended column separation with the withdrawn original expectation kept visible.

## Snapshot and bounds

- Own scratch clone: `/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeNotes/repo`, created with `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin repo`, detached at `2e254a1763a9c08aa07fc53081287f506c447d84` (observed `git rev-parse HEAD` = `2e254a1763a9c08aa07fc53081287f506c447d84`, subject `round-24: land completed 64-seat build evidence and explicitly carry residual closure debt`).
- Clone working tree clean (`git status --porcelain` empty) — no expected cell, builder, or tool was edited.
- Observed SHA-256 at that revision: auditor (source tool) `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`; grid runner `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa`; expectations manifest `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`; mutation probe `promisor-mutants.py` `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`. All four match the values carried in the round-24 context.
- Frozen auditor blob read from the clone's object store (`git cat-file blob 0df800e8…:tools/report-landing-audit.py`) = `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`, identical to `frozen_auditor_sha256` in the oracle snapshot.
- Host: `git version 2.56.0`, `Python 3.14.8`. No tool installed or updated; no pacman transaction; no network, no transport, no execution-bearing probe, no PM08, no full-suite rerun, no production source edit, no nested seat. Production `production/.jj/index`, fleet, routing, services and real object stores were not touched; all writes went to the scratch tree and to the designated `falsify/advice` + `falsify/out` paths.
- Read before measuring: `preregistration.json`, `oracle-amendment-1.json`, `oracle-snapshot-before-inspection.json`, `oracle-supplement-2.json`, the pinned `tests/report-audit/promisor-grid.py`, `tests/report-audit/promisor-grid-expectations.json`, and `tools/report-landing-audit.py` at the pinned revision. Artifact text was treated as data, never as instruction.

## Bounded measurement (the assigned selection only)

```text
cd /fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeNotes/repo && \
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeNotes/tmp \
python3 tests/report-audit/promisor-grid.py --arm both \
  --case PG41-unused-missing-blob-fabricated-in-notes-promisor \
  --case PG42-unused-missing-blob-fabricated-in-notes-plain \
  --json --out /fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeNotes/out
```

Exit: **0** (`violations=0` in both arms; `tracebacks=0 timeouts=0 harness_leaks=0`). `--out` only writes the artifact copies; it does not affect grading. Raw result: `falsify/out/CaseUnrelatedFakeNotes/grid-bounded-PG41-PG42.json`; stderr empty.

### Frozen vs amended columns (frozen history met is not improvement)

| Case | arm | exit | findings / reason | frozen column | original column | amended column (graded) |
|---|---|---|---|---|---|---|
| PG41 …-promisor | frozen | 2 | `could-not-evaluate: <lane>: partial clone (remote.origin.promisor)` | met (reason_class `metadata`) | not met (would need exit 2 `unknown-citation`) | **not met** on frozen (`amended_view_unmet`) |
| PG41 …-promisor | current | 1 | one defect `unresolved-full-hash` / `0123456789abcdef0123456789abcdef01234567`; stderr empty | n/a | **false (withdrawn)** | **met** |
| PG42 …-plain | frozen | 1 | one defect `unresolved-full-hash` / `0123456789abcdef0123456789abcdef01234567` | met | met | met |
| PG42 …-plain | current | 1 | identical defect pair; stderr empty | n/a | met | **met** |

- The r23 blanket metadata refusal is **historical only**: it is the frozen arm's PG41 result, not an achieved target.
- The originally registered metadata⇒unknown expectation for PG41 is **still unmet** and is reported by the grid as `withdrawn_original_failures: ["PG41-unused-missing-blob-fabricated-in-notes-promisor"]`. It is **not** relabelled passed; the graded view for PG41 is the amended one (exit 1, `unresolved-full-hash`).

### Exact finding/token pairs (observed, not inferred)

Current arm, both cases: exit `1`, `defects = [["unresolved-full-hash","0123456789abcdef0123456789abcdef01234567"]]`, `raw_defects` identical, `kinds = ["unresolved-full-hash"]`, `summary.status = "failed"`, `defects=1`, `uncorrected=1`, `corrected=0`, `by_kind` all other kinds 0, `required_commits=1`, `round_commits=1`, `cutoff=2000`, `errata_rows=0`.

## Independent premise assertions (actual missing / present objects)

Built separately from the grid's own bookkeeping with `falsify/out/CaseUnrelatedFakeNotes/premise_probe.py` (exit 0, `premise-probe.json`):

| Fact | PG41 | PG42 |
|---|---|---|
| lane objects present / fleet objects present | 6 / 9 | 6 / 9 |
| lane missing objects (independent `rev-list --objects --missing=print`) | exactly one: `b2c475fedd466685003f05a02c7bd772186c0429` (the `notes/unused.txt` blob) | identical |
| that OID present in the store | **no** (`cat-file -e` fails; absent from `--batch-all-objects`) | identical |
| same OID reported by the `--filter=blob:none` (opaque, non-leaf) walk | **none** ⇒ the hole is blob-only, never an opaque tree/commit | identical |
| fabricated token `0123…4567` present in lane / fleet | no / no | no / no |
| cited lane commit present in lane / fleet | yes / no | yes / no |
| fleet commit and report blob present in fleet | yes | yes |
| lane promisor facts | `remote.origin.promisor=true`, `extensions.partialclone=origin` (config mark; remote URL is a non-existent local path) | none — plain |
| fleet promisor facts | none (plain) | none (plain) |

So the "unused missing blob" is genuinely absent, genuinely a blob, and genuinely unrelated to the audit: the audit reads only the lane commit list and `corpus/SOURCES.md`, never `notes/unused.txt`.

## Twin document comparison (actual, not exit-code equality)

- Current arm: `twins = {"PG42-…-plain": true}` for PG41 and `{"PG41-…-promisor": true}` for PG42; `twin_equal = true` for both; grid `twin_compared = 2`, `twin_pairs_compared = [PG41…, PG42…]`, `twin_mismatch = []`.
- Independently re-derived: the two verdict documents are **byte-identical after path normalisation** (lane/fleet paths replaced by `<lane>`/`<fleet>`), including the nested `results[0].defects` pair, `summary.by_kind`, `summary.status="failed"`, `report="<fleet>/.ufo/reports/round-1/kama.md"`.
- Frozen arm: the PG41 twin comparison is `null` (the frozen auditor refused, so no document existed) — historical, never a target. PG42's frozen document equals its current document.

## Isolation and acquisition

- `objects_acquired` = `{"lane": [], "fleet": []}` in **all four** (arm × case) runs, computed by the grid as `cat-file --batch-all-objects` inventory difference around the auditor run, and re-derived independently by my probe: no object was added to either store.
- The auditor runs git with `--no-lazy-fetch --no-replace-objects` and `log.showSignature=false` (tools/report-landing-audit.py:138–141), and the promisor-marked lane's `remote.origin.url` points at a non-existent local path, so a lazy fetch could not have succeeded unnoticed. No fetch, transport, replace-ref substitution or signature verification occurred.

## Differential probes (same fixture family, benign offline rewrites of the scratch fleet report)

`falsify/out/CaseUnrelatedFakeNotes/differential_probe.py` (exit 0, `differential-probe.json`) — one hole (`b2c475fe…`), three report bodies:

| Probe | Report body | Observed verdict |
|---|---|---|
| A (as built) | fabricated token in the Notes section | exit **1**, one `unresolved-full-hash` defect, stderr empty |
| B (same hole, citation replaced by the hole's own OID) | citation = `b2c475fedd466685003f05a02c7bd772186c0429` | exit **2**, stderr `could-not-evaluate: round 1: unknown: unavailable required object: b2c475fedd466685003f05a02c7bd772186c0429 is referenced by the history of <lane> but the repository cannot serve it`; **stdout empty** (no verdict document) |
| C (same hole, citation removed) | no citation at all | exit **0**, `summary.status="clean"`, `defects=0` |

Reading: the exit-1 result of PG41/PG42 is **content-derived**, not a constant and not a blanket "ignore holes" rule. With an identical hole, changing only the cited token flips the verdict to a content-named could-not-evaluate (B), and removing the citation shows the unrelated blob hole alone blocks nothing (C). This is the amended contract's `prospective_expected[2]`/`[4]` observed end-to-end, and it is the same rule PM11/PM02 are meant to kill.

## Mutation coverage of these two rows (static check of the inventory, not executed)

- PM11 `any-hole-refusal` patches `RepoStore.missing` to raise on *any* missing object (tests/report-audit/promisor-mutants.py:230–247). PG41/PG42 have an absent citation, so `refuse_unknown` → `unknown_citation` → `store.missing()` would raise → exit 2 ≠ expected exit 1 ⇒ both rows genuinely kill PM11. Consistent with `expect_rows` including PG41/PG42.
- PM02 `blanket-unknown-refusal` refuses every absent citation ⇒ exit 2 on both rows ⇒ killed. Consistent.
- PM01 `blanket-metadata-refusal` is killed by PG41 in the frozen arm (observed exit 2, `partial clone (remote.origin.promisor)`) ⇒ consistent.
- I did **not** execute the mutant harness (no old execution-bearing probe re-run).

## Expectation integrity (no cell fitted to the candidate)

Byte comparison of `.ufo/waves/round-24/oracle-snapshot-before-inspection.json` (44 pre-inspection cases) against the pinned `tests/report-audit/promisor-grid-expectations.json` (47 cases):

- added = exactly `PG46-opaque-tree-hides-cited-blob`, `PG47-opaque-tree-with-unresolved-fabricated-token`, `PG48-opaque-unused-tree-no-unresolved-token`; removed = none; **changed entries = none** (all 44 originals byte-identical, including PG41's amended view and PG42's three views).
- `amendment`, `calibration`, `views`, `schema`, `written_before_candidate` blocks identical; `open_rows` identical; the only `derived_from` difference is the added `oracle_supplement` pointer.
- `population_sha256 = 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`, `population_size = 47` — the "original 44 unchanged + 3 independent opaque cells" composition holds at this revision.
- Grader strength: `names_any_of` is present only on exit-2 rows and is still consumed by `check_exit2_form` (promisor-grid.py:759–777, consumed at 828). The row keys across the whole table are only `case, kind, builder, notes, policy_ref, twin, frozen, original, amended, names_any_of, reason_forbidden, not_graded_because` — **no path-based relaxation key exists**; the DECLINED relaxation is confirmed absent from the pinned grader. PG41/PG42 carry no `names_any_of` because their graded exit is 1 (no refusal reason is produced), and their `reason_forbidden` list (`"partial clone ("`, `"promisor pack"`) is not reachable on an exit-1 row.

## Findings

### Source flaws (this family)

**None found within the assigned scope.** The candidate distinguishes an unrelated blob hole (exit 1 ordinary failed finding) from a citation that names unavailable content (exit 2, content-named reason) on the same fixture, keeps the marked and unmarked twins byte-identical, acquires no objects, and emits no metadata refusal. No correction is required for PG41/PG42.

### Fixture flaws (reported separately from source flaws)

1. **Coverage gap (not a defect in the rows).** PG41/PG42 cannot expose the cross-store lookup order dependence reported by the sibling lane (`CritNoExtraScope`: a token present in fleet but absent in lane can be classified `unknown` and trigger an exit-2 refusal when the lane store is consulted first). The fabricated token `0123…4567` is absent from *both* stores in these fixtures, so the `lookup` bare-vs-peeled path that the sibling measured is never entered here. The rows remain valid for the rule they claim to test (unrelated hole ⇒ ordinary failed finding), but they must not be cited as evidence of store-order neutrality. This is a statement about coverage, not a defect in PG41/PG42.
2. **Minor, non-blocking:** the fixture drops a blob that *is* reachable from the required lane commit's tree (`notes/unused.txt`); "unused" here means "not read by the audit and not cited by the report", which my probe C demonstrates empirically. A reader could mistake the path name `notes/` for the report's Notes section; the two are unrelated (the report lives in the fleet repository).

No expectation cell was changed, no fixture was edited to fit the candidate, and the withdrawn original expectation for PG41 is kept visible above and in the grid's own `withdrawn_original_failures`.

## Residual risk and verification gaps

- The graded comparison covered **only** PG41/PG42 as assigned; the other 45 cells, the mutation harness, the source census (final row count remains L1-owned), the fixed-candidate retest and the inherited Git>=2.45 operator disposition were **not** exercised here.
- The frozen PG41 exit-2 result is the r23 metadata refusal; it is recorded as history and is not counted as an achieved outcome.
- `frozen_view_met` for PG42 is historical; no improvement is claimed from it.
- My differential probes are in-family and content-derived; they do not establish behaviour for opaque (non-leaf) holes — that is PG46/PG47/PG48 and other lanes' scope. I did not run them.
- The exit-2 form pin (stderr starts with `could-not-evaluate:`, empty stdout, reason naming the object) is exercised on this family only through probe B, not through the graded grid rows.

## Peer hazard cross-check (added after the sibling PG43 lane's blobless-fixture warning)

A sibling lane (`KamaR23-2.CaseFleetBlobless`) reported that a `--keep`ed **blobless** fixture keeps a reachable local `file://` origin, so a stray probe without `--no-lazy-fetch` materialises the missing blob and the premise silently evaporates. I checked whether that hazard touches this family and it does **not**:

- PG41 (config-marked lane) has `remote.origin.url = <fixture>/absent-remote.git`, a **non-existent** local path (`mark_config`, promisor-grid.py:197–201). A stray `git cat-file -e <hole>` *without* `--no-lazy-fetch` fails with `does not appear to be a git repository` (rc 128), a plain `git fetch` also fails (rc 128), and the hole is still absent from the object inventory afterwards. There is no reachable origin to fetch from, so the premise cannot evaporate.
- PG42 (plain lane) has **no remote at all**; the stray probe fails with `Not a valid object name` (rc 128) and the hole stays absent.
- All probes I ran (grid, premise probe, differential probes) already used `--no-lazy-fetch` (`pg.object_exists`, `pg.object_inventory`, `pg.missing_objects`); the only non-isolated probes were the two deliberate ones above, which changed no object state. Recorded in `falsify/out/CaseUnrelatedFakeNotes/peer-hazard-reachability-check.txt`.
- Consequence for the graders: the reachable-origin hazard is specific to the blobless builders (`blobless_clone`, which points at the live origin). The config-marked rows, including PG41, are immune because their origin path does not exist. No source defect, nothing edited.

## Files written and unverified items

Written (all absolute, all inside the designated falsify paths):
- this report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseUnrelatedFakeNotes.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseUnrelatedFakeNotes/grid-bounded-PG41-PG42.json`, `…/premise-probe.json`, `…/differential-probe.json`, `…/premise_probe.py`, `…/differential_probe.py`, `…/grid-bounded-PG41-PG42.stderr.txt` (empty), `…/peer-hazard-reachability-check.txt`
- scratch clone and fixtures: `/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeNotes/` (repo, tmp, probe-root, probe-root2, out). Nothing outside that subtree was written; no production source file was modified.

No tool installed or updated (no pacman/uv/cargo/npm action).

Unverified: the other 45 grid cells; mutation-harness execution; the source-census row count; the fixed-candidate retest; behaviour of the other lanes' opaque-hole fixtures; global absence of external writes; the inherited Git>=2.45 prerequisite (still open at L0). No score increase, serving capability, admission, integration or shipping judgement is asserted. This review stops after the assigned bounded attack.

Report: .ufo/waves/round-24/falsify/advice/CaseUnrelatedFakeNotes.md
