# CaseSourceBlob — independent falsification of the PG13/PG14 fixture family

Lane: CaseSourceBlob (round 24, fresh falsification of `2e254a1763a9c08aa07fc53081287f506c447d84`).
Leaf member: no subagents dispatched, no production file edited, no full suite re-run,
no tool installed or updated.

**Verdict: HOLDS for the graded family.** Both cells meet the live (amended) view:
PG13 and PG14 each exit 2 with a content-derived `could-not-evaluate:` refusal that
names the exact unavailable object, no verdict document, no objects acquired, no
transport. The r23 blanket metadata refusal exists only in the frozen arm, i.e. as
history. **Four fixture/grader findings** (the strongest: the runner's twin-equality
control is structurally vacuous for exit-2 rows, so the twin claim for this pair is
*asserted, not measured*) and **no source defect** that falsifies the amended
contract for this family.

---

## 1. Pins observed (read-only, scratch only)

| item | value |
|---|---|
| scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/CaseSourceBlob/repo` (`git clone --no-hardlinks` of `/home/vgpnk/Projects/shokunin/kama-shokunin`) |
| checked-out base | detached `2e254a1763a9c08aa07fc53081287f506c447d84`, tree clean (`git status --porcelain` empty) |
| git | 2.56.0 (host), so `--no-lazy-fetch` / `--missing=print` were available to this measurement |
| auditor (current) | `tools/report-landing-audit.py` sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| runner | `tests/report-audit/promisor-grid.py` sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` |
| manifest | `tests/report-audit/promisor-grid-expectations.json` sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` |
| frozen auditor blob | `0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py` sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` |
| grid `expectations_sha256` | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (the manifest bytes) |
| grid `population_sha256` | `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`, `population_size 47` — identical to the value filed by the L1/GridOracle (`build/out/GridOracle/population.json`) |

Scratch/temp for every subprocess: `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseSourceBlob/tmp`.
No change to production `.jj/index`, fleet, siblings, operator config, routing,
services or any real object store. PM08 was not executed (static reading only).

---

## 2. The bounded selection I was assigned

```
cd /fast/scratch/hyaku/kama-r24/falsify/CaseSourceBlob/repo && \
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseSourceBlob/tmp \
python3 tests/report-audit/promisor-grid.py --arm both \
  --case PG13-missing-lane-blob-promisor --case PG14-missing-lane-blob-plain --json
```

**exit 0**, stderr empty. Raw JSON: `out/CaseSourceBlob/grid-both-arms-pg13-pg14.json`.

### Exact observed rows

| arm | case | exit | findings (kind, token) | met (its view) | objects acquired | traceback/timeout/leak |
|---|---|---|---|---|---|---|
| current | PG13-missing-lane-blob-promisor | **2** | none — no verdict document (`defects=null`, `raw_defects=null`, `kinds=null`, `document=null`) | `met_amended=true`, `met_original=true` | lane `[]`, fleet `[]` | none |
| current | PG14-missing-lane-blob-plain | **2** | none — no verdict document | `met_amended=true`, `met_original=true` | lane `[]`, fleet `[]` | none |
| frozen (r23 base) | PG13-missing-lane-blob-promisor | **2** | none; stderr `could-not-evaluate: …/lane: partial clone (remote.origin.promisor)` | `met_frozen=true`, `met_amended_frozen=false` | lane `[]`, fleet `[]` | none |
| frozen (r23 base) | PG14-missing-lane-blob-plain | **2** | none; stderr `could-not-evaluate: git cat-file blob 051975b0…: bad file` | `met_frozen=true`, `met_amended_frozen=true` | lane `[]`, fleet `[]` | none |

Current arm summary: `graded=2`, `violations=0`, `violating_cases=[]`,
`withdrawn_original_failures=[]`, `tracebacks=0`, `timeouts=0`, `harness_leaks=0`.
Frozen arm summary: `violations=0`, `amended_view_met=1/2`,
`amended_view_unmet=["PG13-missing-lane-blob-promisor"]` — the retained r23 baseline,
history and not a target.

**Frozen history is not improvement.** In r23 the *marked* twin was refused for the
metadata while the *plain* twin was refused for the object; the two rows therefore
disagreed on the reason. At the pinned base both rows refuse for the same
content-derived reason (§7). That is the repair this family is graded on.

**Withdrawn-expectation visibility.** For PG13/PG14 the *original* view and the
*amended* view are identical (`exit 2`, `kinds null`, `defects null`,
`reason_class "unavailable"`), so no expectation of this family was withdrawn; the
row is not relabelled passed from a withdrawal. The globally withdrawn expectation
(preregistration `expected_after[3]`, unknown-citation ⇒ exit 2) stays withdrawn and
is **not** counted as achieved anywhere in my measurement — `withdrawn_original_failures=[]`
because no row of this family carries it.

---

## 3. Builders, premises and the fixed expectation (source inspection)

* Builder PG13 = `c_missing_lane_blob_promisor` → `build(lane_mark="config", drop=("sources_blob",))`.
* Builder PG14 = `c_missing_lane_blob_plain` → `build(drop=("sources_blob",))`.
* `build()` (promisor-grid.py:333-473): writes `corpus/SOURCES.md` + `f` into the lane,
  commits one lane commit (`round-1: work`, author `kama-shokunin`, `@1000`); the fleet
  publishes `.ufo/reports/round-1/kama.md` at `@2000` citing that commit;
  `mark_config()` then sets `remote.origin.promisor=true`,
  `extensions.partialclone=origin` and `remote.origin.url=<case>/absent-remote.git`
  (**a non-existent local path**) for PG13 only; `drop_object()` unlinks the loose
  object of the lane's `corpus/SOURCES.md` blob.
* Fixed expectation (landed manifest, byte-identical to the pre-candidate oracle —
  §8): PG13 `frozen {exit 2, reason_class "metadata"}`, `original`/`amended`
  `{exit 2, kinds null, defects null, reason_class "unavailable"}`,
  `names_any_of ["$sources_blob", "corpus/SOURCES.md"]`,
  `reason_forbidden ["partial clone (", "promisor pack"]`, `twin "PG14-missing-lane-blob-plain"`;
  PG14 the same minus `reason_forbidden`, `twin null`.
* Auditor path that makes this a *required* read: `run()` calls
  `load_source_urls(lane_repo, tip)` (report-landing-audit.py:767); that reads the
  committed `corpus/SOURCES.md` blob with `cat-file blob` (line 382) and, on failure,
  raises `required_read(...)` (line 384) → `EvalError` → `main()` prints
  `could-not-evaluate: …` and returns 2 (lines 1313-1314). The registry decides which
  40-hex tokens inside source URLs are exempt from `unresolved-full-hash`, so it is
  evidence the audit reads, not decoration.

---

## 4. Independent premise assertions (my own probe, not the grader's)

I rebuilt both fixtures with the grid's own builders and asserted the premises
myself (`out/CaseSourceBlob/independent-premise-probe.json`, `out/CaseSourceBlob/probe.py`).
Every probe used `git --no-lazy-fetch --no-replace-objects`; no probe can lazy-fetch.

| assertion | PG13 (promisor) | PG14 (plain) |
|---|---|---|
| `lane_missing` (own `--no-lazy-fetch` walk) | `["051975b0ced83169116c235e7691c0a1a8313300"]` — exactly one object | identical |
| `fleet_missing` | `[]` | `[]` |
| `lane_promisor` | **true** (`extensions.partialclone=origin`, `remote.origin.promisor=true`, `remote.origin.url=…/absent-remote.git`) | **false** (no promisor key at all) |
| `fleet_promisor` | false | false |
| `sources_blob` `051975b0…` present? | **no** (absent) | **no** (absent) |
| `tip_tree` `1c13e47c…` present? | yes | yes |
| lane commit `58866b56…` present? | yes | yes |
| `f` blob `56d7b323…` present? | yes | yes |
| fleet report blob `0cf7ed5c…` present? | yes | yes |
| fleet tip tree `b1e11739…` present? | yes | yes |
| fabricated token `0123456789ab…` present? | no (lane), no (fleet) | no, no |
| worktree copy of `corpus/SOURCES.md` | present on disk | present on disk |

The fixture therefore differs between the twins **only** in the promisor metadata, and
the only unavailable object in each is the required registry blob. The worktree copy
being present shows the refusal comes from the missing *object*, not from a missing
file: the auditor reads committed bytes only (`cat-file blob`).

---

## 5. Exact finding/token pairs and content-derived reason IDs

* **Finding/token pairs: the empty set, for both rows, in both arms.** Exit 2 ⇒
  `stdout` is empty, no JSON verdict document is emitted, so the grader's
  `observed_defects()` returns `None` for `defects`/`raw_defects` and `kinds` is
  `None`. The expectation for both rows is `kinds: null, defects: null` — i.e. the
  contract is "no verdict at all", and that is exactly what was observed. There is no
  clean (exit 0) and no failed (exit 1) verdict in either cell.
* **Content-derived reason (current arm, identical modulo the fixture path):**

```
could-not-evaluate: unavailable required object: 58866b563cd900df310588effe79028efc104c33:corpus/SOURCES.md
  (051975b0ced83169116c235e7691c0a1a8313300) in <case>/lane: git cat-file blob
  051975b0ced83169116c235e7691c0a1a8313300 in <case>/lane: rc=128 fatal: git cat-file
  051975b0ced83169116c235e7691c0a1a8313300: bad file
```

  It names the unavailable object **three** ways: the pinned tip commit, the required
  path `corpus/SOURCES.md`, and the blob id `051975b0…`; both `names_any_of`
  alternatives are present (`"corpus/SOURCES.md" ∈ stderr` and
  `"051975b0ced83169116c235e7691c0a1a8313300" ∈ stderr`). It is *not* the r23
  metadata refusal (`"partial clone ("` absent, `"promisor pack"` absent), and it
  falls in the `unavailable` reason class (terms hit: `unavailable`, `missing`,
  `bad file`). It is a read-failure reason, not a guessed empty result.
* Frozen-arm reasons for comparison: PG13 `partial clone (remote.origin.promisor)`
  (metadata class — the r23 defect), PG14 `git cat-file blob 051975b0…: bad file`
  (object class, no path/oid naming wrapper in r23).

---

## 6. No objects acquired, no transport

* Grid rows: `objects_acquired {lane: [], fleet: []}` for all four rows; `grade()`
  treats any acquired object as a violation — none.
* My own before/after `cat-file --batch-all-objects` inventory around each auditor run:
  `acquired {lane: [], fleet: []}` **and** `lost {lane: [], fleet: []}`.
* Post-audit lane `.git` state: no `FETCH_HEAD`, no `objects/pack` directory, only
  `refs/heads/master`, 4 loose objects (the restored control object was removed again;
  see §7). The promisor remote is a non-existent local path, so no fetch was even
  possible; the auditor's `GIT_ISOLATION` (report-landing-audit.py:138-140) carries
  `--no-lazy-fetch` and `--no-replace-objects` on every git call.

---

## 7. The actual twin comparison (the one the runner does not perform)

The manifest declares PG13 ↔ PG14 as a twin pair, but the runner's twin control is
**structurally vacuous for exit-2 rows**: `normalise_document()` returns `None` when
stdout is not a verdict document, and `main()` sets `results[partner] = None` and then
`"twins": {"PG14-missing-lane-blob-plain": null}`, `"twin_equal": null` for both rows,
with `twin_compared=0` and `twin_pairs_compared=[]` in the arm summary. No
document-level comparison happened; the runner reported "no mismatch" because it
compared nothing.

I therefore computed the twin equality myself at the **reason** level:

| comparison (current arm) | result |
|---|---|
| exit equal (2 vs 2) | yes |
| stdout verdict documents | both absent → equal |
| stderr equal modulo the fixture path | **yes** — byte-identical string, naming the same tip commit, the same path and the same blob id |

Frozen arm, same computation: stderr **not** equal (metadata refusal on the marked
twin vs object refusal on the plain twin) — the r23 defect this round repairs.

**Content-derived control (does the refusal come from the hole or from the
metadata?).** On private copies of both fixtures I restored the missing blob object
offline (`git hash-object -w` of the fixture's own SOURCES bytes, copied as a loose
object; the restored id reproduces the dropped id exactly,
`restored_oid_matches=true`) and re-ran the current auditor on the **same
promisor-marked lane**:

* PG13 with the blob restored → **exit 0**, `status "clean"`, `defects 0`,
  `required_commits 1`, empty stderr;
* PG14 with the blob restored → **exit 0**, same clean document.

So the refusal is caused by the unavailable required object, **not** by promisor
metadata: promisor metadata alone does not refuse a complete lane (the amended
contract's core clause). The restored object was deleted again afterwards and the
fixture re-verified as missing (`control_after_restore_removed_again=false`, i.e.
absent), so the graded state is unchanged. The graded grid run was executed *before*
this control, on separate fixture instances.

---

## 8. Expectation integrity: no drift, no silent fixture fitting

* The landed manifest has **47** rows; the pre-candidate oracle snapshot
  (`oracle-snapshot-before-inspection.json`) has **44**. The three added rows are
  exactly the three bases of `oracle-supplement-2.json`
  (`PG46-opaque-tree-hides-cited-blob`, `PG47-opaque-tree-with-unresolved-fabricated-token`,
  `PG48-opaque-unused-tree-no-unresolved-token`).
* Every one of the 44 original rows is **identical in every graded and ungraded
  column** between the pre-candidate snapshot and the landed manifest
  (`shared_row_semantic_diffs: []`, `shared_row_form_only_diffs: []`, artifact
  `out/CaseSourceBlob/expectation-integrity.json`): `frozen`, `original`, the live
  view, `kind`, `builder`, `twin`, `names_any_of`, `reason_forbidden`, `policy_ref`,
  `notes`. PG37 — the one row whose `amended_rows` entry is an explicit `null` in the
  snapshot — resolves to the same values in the landed manifest (`amended` there
  equals the snapshot's `original`).
* **PG13 and PG14 rows are byte-identical** to the pre-candidate oracle
  (`pg13_row_identical: true`, `pg14_row_identical: true`). No expected cell was
  changed to fit the candidate; the fixture was not made to fit the candidate.
* **Grader strength**: the row-key universe of the whole table is
  `[amended, builder, case, frozen, kind, names_any_of, notes, original, policy_ref,
  reason_forbidden, twin]` — **no relaxation/path key exists**, and the DECLINED
  path-based loosening is absent from the pinned runner. `names_any_of` is resolved
  at promisor-grid.py:828 and consumed by `check_exit2_form`
  (promisor-grid.py:759-777, called from `grade()` at 801) as
  `any(name in stderr for name in resolve_token(name))`: a strong any-of over the
  object id and the registered path, not a path-only fallback.

---

## 9. Findings

### Fixture / grader (the runner and its manifest, not the audited source)

**F1 — medium — the twin-equality control is vacuous for exit-2 rows, so the twin
claim of this pair is asserted, not measured.** `promisor-grid.py:860`
(`normalise_document`) feeds the `main()` twin block at lines 1009-1014, which
compares *verdict documents*; an exit-2
row has none, so `twin_equal` is `None` and the row is not counted as compared
(`twin_compared=0`). A candidate that refused the marked twin with one reason and the
plain twin with another reason would still be graded "met" on both rows (each row is
independently pinned on exit/class/name, but their *equality* is never tested).
Minimal correction, not applied: compare the refusal reason as well when no document
exists — e.g. keep a `reason` field in `obs` (normalised stderr: strip the fixture
path, keep the object ids) and set `twin_equal` from `(exit, document or reason)`
equality. My own reason-level comparison (§7) is the substitute measurement for this
pair today; it does hold.

**F2 — medium — the row observation carries no fixture premise, so the fixture
shape is never asserted by the runner.** `build()` computes `premise`
(`lane_missing`, `fleet_missing`, `lane_promisor`, `fleet_promisor`, `fake_present`)
but `run_case()` drops it: the JSON rows contain no premise field, and no check
compares the premise with what the row claims to be. Consequently nothing pins
(a) that PG13's lane is promisor-marked and PG14's is not, (b) that exactly one
object is missing, or (c) that the twin pair differs *only* in the metadata. A
builder regression that dropped a different object, or marked both lanes, would still
be graded "met" on both rows. Minimal correction, not applied: put `built["premise"]`
into `obs` and add per-row premise expectations (e.g. `lane_promisor: true/false`,
`lane_missing_count: 1`) to the manifest. I asserted all of this myself today
(§4) — the fixture is correct as built.

**F3 — low — `names_any_of` also accepts the registered path, so the grader pins
"name the object" only partially.** For PG13/PG14 the accepted alternatives are the
object id *or* the string `corpus/SOURCES.md`; a canned refusal that names the path
but no object id would satisfy the grader. The observed reason names both the path
and the blob id `051975b0…`, so the substance holds; only the tolerance is looser
than "strong". This is the *pre-candidate* registered expectation (unchanged by the
candidate), not a candidate-introduced relaxation; no expectation change is proposed
here without L1.

**F4 — low — asymmetric `reason_forbidden` between the twin pair.** PG13 carries
`["partial clone (", "promisor pack"]`; its plain control PG14 carries none. The
r23 metadata phrasing is therefore not explicitly forbidden on the plain row. It
remains excluded in practice by the `unavailable` reason-class vocabulary (the
phrase `partial clone (remote.origin.promisor)` matches none of its terms), but a
hybrid message such as `partial clone (…): missing object` would pass PG14 while
failing PG13. Low impact; flagged for L1, no cell changed.

### Source (`tools/report-landing-audit.py` at `ea51bc35…`)

**No source defect found that falsifies the amended contract for this family.**
The behaviour observed is exactly the registered behaviour: an actually-required
object that cannot be read ⇒ `could-not-evaluate` exit 2 with a content-derived
reason naming the object; promisor metadata alone changes nothing (control §7); no
object is acquired; no transport is invoked.

**F5 — informational — the refusal message renders the required path with the tip
commit id instead of the branch name.** `run()` passes `tip` (the pinned commit) into
`load_source_urls(lane_repo, tip)` (report-landing-audit.py:767), so the message
reads `…:58866b563cd900df310588effe79028efc104c33:corpus/SOURCES.md (…)` where the
branch form would be `master:corpus/SOURCES.md`. Cosmetic; the message stays
content-derived and names the blob id. No correction proposed (a change here would
touch every `required_read` message and is not needed by the contract).

**F6 — informational — the registry read is refused unconditionally, even when the
audited report contains nothing the registry could exempt.** In this fixture the
SOURCES.md content has no registry rows and the report has no source URL, so the
registry could not change any verdict; the audit still refuses (exit 2). This is the
conservative direction ("never guessed empty data") and it matches the registered
expectation for PG13/PG14 (exit 2, `unavailable`), so it is *not* a defect — but if
the intent were "refuse only when the unread object could change a verdict", the
current source over-refuses. Recorded as a design question for L1, not a finding
against the contract.

---

## 10. Residual risk and verification gaps

* **Only these two cells were measured.** The other 45 cells, the mutation suite,
  the harness selftest, the historical-parity check, the source census and the
  inherited `git >= 2.45` operator disposition (still open at L0) were **not**
  verified by me; no full-suite storm was run.
* **F1 leaves a real hole in the runner for every exit-2 pair** (not just this one):
  the twin-equality control never executes on a refusal row. For PG13/PG14 I closed
  it by hand (reason-level equality); the other exit-2 pairs are unverified by me.
* **F2 leaves the premise unasserted for every row** of the table; my probe
  asserted it for these two rows only.
* The `names_any_of` check is a substring test over stderr: it proves that a name
  appears, not that the reason was *derived* from the failed read. For these rows
  the reason carries the underlying `git cat-file` error text, which is stronger
  evidence than the check requires.
* My control probe (§7) mutated private fixture copies in scratch only; the graded
  grid run was executed first and on separate instances, and the control copies were
  restored to the graded state afterwards. Production was never touched.
* No claim is made about serving capability, numeric score, admission, integration
  or shipping; nothing was edited in production. The originally withdrawn
  unknown-from-metadata expectation remains withdrawn / not achieved and is not
  relabelled passed.

---

## 11. Files written and unverified items

Written (all under the round-24 falsify area; append-only; production untouched):

* `.ufo/waves/round-24/falsify/advice/CaseSourceBlob.md` (this report)
* `.ufo/waves/round-24/falsify/out/CaseSourceBlob/grid-both-arms-pg13-pg14.json` — raw grid JSON of the assigned selection
* `.ufo/waves/round-24/falsify/out/CaseSourceBlob/independent-premise-probe.json` — my own premise/behaviour/twin/control measurements
* `.ufo/waves/round-24/falsify/out/CaseSourceBlob/expectation-integrity.json` — 44-row / +3-supplement diff against the pre-candidate oracle
* `.ufo/waves/round-24/falsify/out/CaseSourceBlob/probe.py` — the probe script (reproducible)

Scratch only (outside the repo): the clone and its Git metadata at
`/fast/scratch/hyaku/kama-r24/falsify/CaseSourceBlob/repo`, the grid root under
`…/CaseSourceBlob/tmp`, the probe fixtures under `…/CaseSourceBlob/probe-root`, and
the extracted frozen auditor at `…/CaseSourceBlob/frozen-audit.py`.

Unverified: the other 45 cells; the mutation suite; the harness selftest; the
historical-parity check; the source census; the inherited `git >= 2.45` prerequisite
(L0, open). No tool was installed or updated during this lane.

Report: .ufo/waves/round-24/falsify/advice/CaseSourceBlob.md
