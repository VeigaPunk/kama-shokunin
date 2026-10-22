# CaseWrongType — PG38/PG39 falsification (kama round 24, pinned `2e254a17`)

**Verdict: HOLDS for the assigned slice.** Both graded rows of fixture family WrongType
(`PG38-wrong-type-citation-plain`, `PG39-wrong-type-citation-promisor`) meet their live
(graded) expectation on the pinned candidate: exit 1, exactly one
`landed-unresolved` defect whose token is the cited blob OID, no
`unresolved-full-hash`, no refusal, no object acquisition, and a byte-identical
twin verdict document. **No source defect was found in this slice.**

One **medium fixture/expectation coverage gap** (F1) and three low/informational
observations (F2, F3, F5) are reported separately from source findings, as required;
none of them invalidates either row. F1 is a *missing assertion*, not a wrong one:
the pinned source already behaves correctly in the uncovered situation.

Lane: leaf member (no subagent dispatch). Read-only production.

---

## 1. Pinned base (observed)

| item | value |
|---|---|
| clone | `/fast/scratch/hyaku/kama-r24/falsify/CaseWrongType/repo` (`git clone --no-hardlinks` from `/home/vgpnk/Projects/shokunin/kama-shokunin`, detached) |
| HEAD | `2e254a1763a9c08aa07fc53081287f506c447d84` (`git rev-parse HEAD`, clean tree) |
| production HEAD at report time | `2e254a1763a9c08aa07fc53081287f506c447d84`; `git status --short` shows only the untracked `.ufo/waves/round-24/falsify/` and `.ufo/waves/round-24/fixes/` trees (pre-existing; no tracked-file change) |
| `tools/report-landing-audit.py` | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` (matches the assignment's source tool) |
| `tests/report-audit/promisor-grid.py` | sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` (matches the assignment's runner) |
| `tests/report-audit/promisor-grid-expectations.json` | sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (matches the assignment's manifest) |
| `tests/report-audit/promisor-mutants.py` | sha256 `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` (matches the assignment's mutation probe) |
| frozen auditor blob `0df800e8…:tools/report-landing-audit.py` | sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` (equals the oracle snapshot's `frozen_auditor_sha256`) |
| manifest population | 47 rows, `population_sha256 = 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` |
| environment | git 2.56.0, python3 3.14.8; `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseWrongType/tmp`; **no tool installed or updated** (no pacman / uv / cargo / npm transaction was needed or performed) |
| transport | none. No network, no `http(s)`/`ssh`/`file://` remote, no execution payload. PM08 was not executed. |

Scratch only: the clone, the grid root, the mutant copies and all probe fixtures live under
`/fast/scratch/hyaku/kama-r24/falsify/CaseWrongType/`. Production `.jj/index`, fleet, sibling
lanes, operator config, routing, services and real object stores were not touched.

## 2. Exact commands and exit codes

```
# 1) the assigned bounded selection (both arms, exactly the two family rows)
cd /fast/scratch/hyaku/kama-r24/falsify/CaseWrongType/repo
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseWrongType/tmp \
  python3 tests/report-audit/promisor-grid.py --arm both \
  --case PG38-wrong-type-citation-plain --case PG39-wrong-type-citation-promisor --json
# exit 0   (stderr: empty, 0 bytes)

# 2) the same selection, re-run with --out so the candidate/population records persist
… --json --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseWrongType
# exit 0   (stderr: empty, 0 bytes)   -> reproducible, identical verdicts

# 3) case-strength: mutant A (scratch copy of the auditor only)
python3 tests/report-audit/promisor-grid.py --arm current \
  --current …/probe/mutant-audit.py --case PG38-… --case PG39-…
# exit 1   violations=2  (both rows NOT-MET)

# 4) case-strength: mutant B (scratch copy of the auditor only)
python3 tests/report-audit/promisor-grid.py --arm current \
  --current …/probe/mutant2-audit.py --case PG38-… --case PG39-…
# exit 0   violations=0  (both rows met -> the gap in F1)

# 5) direct auditor runs against locally built fixtures (no grid in the loop)
python3 …/repo/tools/report-landing-audit.py --lane-repo <fixture>/lane \
  --fleet-repo <fixture>/fleet --rounds 1 --json --no-errata
# PG38 exit 1, PG39 exit 1, PG38+opaque exit 1, PG39+opaque exit 1 (stderr empty)
# mutant B on PG38+opaque / PG39+opaque: exit 2 (false refusal, see F1)
```

## 3. Which view PG38/PG39 are graded against, and the withdrawn expectation

`PG38` and `PG39` have **no `amended` entry** in the manifest `d86b7bea…`, so per the grid's
`live = expect.get("amended", expect["original"])` (`promisor-grid.py:830`) their graded view is
the **original** row:

| case | kind | graded (original) expectation | frozen (r23) expectation | twin |
|---|---|---|---|---|
| `PG38-wrong-type-citation-plain` | `control` | exit 1, kinds `["landed-unresolved"]`, defects `[{landed-unresolved, $blob}]` | exit 1, `["landed-unresolved"]`, `$blob` | – |
| `PG39-wrong-type-citation-promisor` | `policy` | exit 1, kinds `["landed-unresolved"]`, defects `[{landed-unresolved, $blob}]` | exit 2, reason_class `metadata` | `PG38` |

`$blob` resolves through `resolve_token()` to the fixture's `f` blob OID
(`promisor-grid.py:686`); it is **`56d7b323865c731da81e0225cf109d66f0480919`** in both rows
(the fixture file content is the constant `"fixture file\n"`, so the OID is deterministic —
see F5).

The **withdrawn** preregistration rule (`expected_after[3]`: "a missing citation in any
promisor-backed repository is unknown, not proved absent: exit 2") does **not** apply to this
family: both rows' citations resolve to an object that is *present*, so the rule was never
triggered here. Observed on the current arm: `met_original = true` for both rows and
`withdrawn_original_failures = []` — **nothing of the withdrawn expectation is being counted as
passed**. The frozen arm, by contrast, does not meet the amended view for `PG39`
(`amended_view_unmet = ["PG39-wrong-type-citation-promisor"]`), which is the historical baseline
the repair is measured against — the r23 auditor refused with the metadata reason
`could-not-evaluate: …/lane: partial clone (remote.origin.promisor)`. Frozen history met is
not improvement; the improvement is visible only in the **amended** column of the **current**
arm, where both rows are met.

## 4. Observed outcome — premises, objects, findings, twin comparison

Premises, read back from the built fixtures with the grid's own `--no-lazy-fetch` helpers
(`missing_objects` / `object_exists` / `object_inventory`), not inferred from the verdict:

| fact | PG38 | PG39 |
|---|---|---|
| lane promisor-backed | false | **true** (`extensions.partialclone`, `remote.origin.promisor`) |
| fleet promisor-backed | false | **true** (same) |
| lane missing objects (`rev-list --missing=print`) | `[]` | `[]` |
| fleet missing objects | `[]` | `[]` |
| cited blob present in lane | **true** | **true** |
| cited blob present in fleet | false | false |
| cited blob object type | `blob` | `blob` |
| `lane_missing`/`fleet_missing` in the recorded premise | `[]` / `[]` | `[]` / `[]` |

Finding / token pairs (current arm, both rows, identical):

```
exit = 1
defects = [["landed-unresolved", "56d7b323865c731da81e0225cf109d66f0480919"]]
kinds   = ["landed-unresolved"]        (no "unresolved-full-hash")
summary.status = "failed"   uncorrected = 1
stderr = ""                            (no could-not-evaluate, no reason ID needed)
```

* **Content-derived reason IDs:** not exercised in this family — the live expectation is a
  *failed verdict*, not a refusal, so there is no `could-not-evaluate:` reason and no
  `reason_class`/`names_any_of` requirement on these two rows. (Verified: `stderr` is 0 bytes in
  the current arm for both rows.) The refusal *form* (typed prefix, no verdict document,
  reason naming the unavailable object) is therefore not asserted by these rows.
* **No objects acquired:** `git cat-file --batch-all-objects` inventories taken immediately
  before and after each auditor run are identical — `objects_acquired = {"lane": [], "fleet": []}`
  in both arms and both rows. Independently re-verified on the retained fixtures. The marked
  repository's `remote.origin.url` points at a nonexistent path (`<tmp>/absent-remote.git`), so
  any fetch attempt would fail loudly, and the auditor issues every git call with
  `GIT_ISOLATION` (`--no-lazy-fetch`, `--no-replace-objects`).
* **Twin document comparison (actual, not vacuous):** the raw stdout of the two runs differs
  (the fixture paths differ); after the grid's path normalisation the two verdict documents are
  **byte-identical** (`twins = {"PG39…": true}` / `{"PG38…": true}`, `twin_equal = true`,
  `twin_pairs_compared = ["PG38-wrong-type-citation-plain", "PG39-wrong-type-citation-promisor"]`,
  `twin_mismatch = []`). I reproduced this independently outside the grid: the two raw
  documents differ only in the fixture path; normalised they are equal
  (`RAW-DOC-IDENTICAL-AFTER-PATH-NORMALISATION: True`,
  `RAW-DOC-BYTES-DIFFER-BEFORE-NORMALISATION: True`). In the **frozen** arm the comparison is
  correctly `None` for both rows: `PG39` produced no verdict document (refusal), so there is
  nothing to compare — `twin_compared = 0` there.
* Grid-level hygiene for this selection: `tracebacks = 0`, `timeouts = 0`, `harness_leaks = 0`,
  `violations = 0` (current arm), `violations = 0` (frozen arm against its own view).

## 5. Mechanism (static source check) and case strength

**Mechanism** (`tools/report-landing-audit.py`): the fixture's Landed section cites a blob OID
that is present locally. `audit_round` resolves it twice: the 40-hex `FULL` scan with **no
peel** (`lookup(stores, full_tokens)`) yields `found` — which is why there is **no**
`unresolved-full-hash` defect — and the Landed-section scan with peel `^{commit}`
(`lookup(stores, [...], "^{commit}")`, auditor `:487`) yields
`wrongtype`. Observed git behaviour on the fixture (`git cat-file --batch-check`, rc 0):

```
56d7b323…  blob 13                                       <- bare: the object is here
56d7b323…^{commit}  missing                              <- the peel cannot be satisfied
56d7b323…^{}  blob 13                                    <- the object is a blob, not a commit
```

The auditor's own `lookup()` (called directly on the built fixtures, same `RepoStore` pair the
audit uses) returns `{"56d7b323…": "wrongtype"}` for the peeled pass and `{"56d7…": "found"}` for
the bare pass — identical in PG38 and PG39, i.e. **promisor metadata changes nothing about the
local resolution**, exactly as the amendment requires. `wrongtype` is a *proved local mismatch*:
`refuse_unknown` short-circuits on it (`:430`), so no refusal is raised and the defect is
reported as `landed-unresolved` (`:496-498`). The same mechanism holds for a **tree** citation
(verified on the fixture's tip tree `1c13e47c…`: `…^{commit} missing` / `…^{} tree 62`), so the
oracle's "a known-present blob/tree that merely fails commit peeling" clause is implemented
type-agnostically.

**Case strength (mutation, scratch copies of the auditor only):**

* **Mutant A** (`offer(token, "unknown" if line.endswith(" missing") else "absent")` at
  `:249-250`) — the wrong-type classification weakened to "absent". Because `RANK` ranks
  `absent` 0 < `wrongtype` 1, the status stays `absent`, the fleet store (which does not hold
  the blob) then re-offers `unknown` for the same token through the `status[token] == "absent"`
  guard at `:222`, and the audit refuses with the false reason
  `could-not-evaluate: round 1: unknown: unavailable required object: 56d7b323… is present but
  its content cannot be served`. **The grid kills it:** exit 1, `violations=2`, both rows
  NOT-MET. ⇒ *the two rows really do discriminate "known wrong type" from "cannot decide"*, and
  they are not satisfiable by a source that degrades the classification.
* **Mutant B** (`if state in ("found", "ambiguous", "wrongtype"):` → `("found", "ambiguous"):` at
  `:430`) — the refusal short-circuit no longer recognises a proved wrong-type object. **The
  grid does not kill it:** exit 0, `violations=0`, both rows still met. On a locally built
  wrong-type + unrelated-hole fixture the same mutant refuses (exit 2) with the demonstrably
  false reason "could be hidden behind the missing tree or commit 33fd12ec…". This is the gap
  recorded as **F1**.

## 6. Findings

### Source findings: none in this slice

No source defect was found in the WrongType family. The pinned auditor classifies the
wrong-type citation correctly, keeps promisor metadata inert, acquires no objects, emits one
content-derived finding with the exact token, and produces twin-identical documents. **No
source edit is proposed.** (The two mutants above are scratch-only probes; no production file was
modified.)

### Fixture / expectation findings (reported separately, as required)

**F1 — medium, coverage gap: no graded row combines a wrong-type citation with an unrelated
opaque hole.** `oracle-supplement-2.json`'s `not_unresolved` clause names exactly this
combination — "A known-present blob/tree that merely fails commit peeling is not an absent
citation; it keeps the normal wrong-type finding **even when unrelated opaque holes exist**" —
and the amendment requires that "Incomplete but locally sufficient repositories are not refused
merely because an unrelated historical blob, branch, or unused file is missing". Neither
`PG38` nor `PG39` (nor any of the 47 rows) contains a wrong-type citation in a repository that
also carries an unrelated missing tree/commit: `c_wrong_type_citation_plain` /
`c_wrong_type_citation_promisor` are `build(root, tmp, wrong_type=True)` with **no `drop`**
(`promisor-grid.py:628-634`), and `wrong_type` appears nowhere else in the grid
(`promisor-grid.py:388` is its only other use).
*Evidence.* Mutant B (above) passes both graded rows with `violations=0`, yet on a fixture built
by the pinned grid's own builder — `build(root, tmp, wrong_type=True, unused_tree=True,
lane_mark="config", fleet_mark="config", drop=("unused_tree",))`, i.e. the cited blob
`56d7b323…` still present, an unrelated missing subtree `33fd12ec…` in the lane — it produces
`exit 2` with `could be hidden behind the missing tree or commit 33fd12ec…`. The **pinned
source gets this right** (`exit 1`, `landed-unresolved`, stderr empty, on both the plain and the
promisor-marked variant), so this is a *missing assertion*, not a wrong verdict.
*Minimal correction candidate (report only; no edit).* Add one policy row to the manifest and
one builder, e.g. `PG49-wrong-type-citation-unrelated-opaque-hole-promisor`, builder
`build(root, tmp, wrong_type=True, unused_tree=True, lane_mark="config", fleet_mark="config",
drop=("unused_tree",))`, graded expectation `exit 1`, `kinds ["landed-unresolved"]`, `defects
[{landed-unresolved, $blob}]`, `twin` a plain counterpart — plus the matching expectation row
in `oracle-snapshot-before-inspection.json`/the supplement if L1 wants it oracle-anchored. The
row must be registered as an *addition* (the 44-case snapshot stays immutable), and the grid
would then report `population_size = 48` with a new `population_sha256`.

**F2 — low, expectation bookkeeping: `PG39`'s live expectation is filed under the withdrawn
column.** `PG39`'s `policy_ref` is "oracle-amendment-1.json prospective_expected[3]" but the
expectation itself sits in the `original` key with no `amended` entry, so the graded view is
nominally the "original" row. The *substance* is identical (exit 1, one `landed-unresolved` /
`$blob` defect, no `unresolved-full-hash`), so the grade is correct and nothing withdrawn is
being counted as passed. The bookkeeping consequence is that the grid's
`withdrawn_original_failures` list cannot distinguish "a row whose original registration was
withdrawn" from "a row whose expectation never changed"; here that list is empty in the current
arm, so no mislabelling occurs. The pattern is manifest-wide, not `PG39`-specific: only 10 of
the 47 rows carry an explicit `amended` entry (37 do not, including `PG38`/`PG39`).

**F3 — low, fixture realism: `PG39`'s promisor marking is a synthetic label, not a partial
clone.** `mark_config` sets `extensions.partialclone=origin`, `remote.origin.promisor=true` and
`remote.origin.url=<tmp>/absent-remote.git`, but there is **no `remote.origin.fetch` refspec**,
no filter remote and no `.promisor` marker files. The auditor's predicate
(`promisor_facts`: config / filter / promisor_true / markers) is satisfied, so the row does
exercise "promisor metadata present" — and the nonexistent remote makes it fail-closed for
transport — but a reader must not read `PG39` as "a real partial clone was audited". For this
family it is immaterial: every object is present locally and the audit never transports. (The
real blobless-clone shape is the sibling family's, e.g. `PG43`.)

**F5 — informational, token strength: the wrong-type token is the same OID in every grid row.**
The fixture's cited file content is the constant `"fixture file\n"` in `build()`
(`promisor-grid.py:330`), so the blob OID `56d7b323…` is identical in `PG38`, `PG39` and in
every other row built from the same helper. The grader still compares the emitted token against
the fixture's *actual* OID (`resolve_token`), so a source that emitted a different token would
fail; but a source that emitted this fixed OID unconditionally would pass. Low impact; noted
for the manifest only.

*(F4 — checked and not a finding.)* The wrong-type citation is only placed in the
`## Landed changes` section. A wrong-type OID placed elsewhere in the report (e.g. the Notes
section) is scanned by the 40-hex `FULL` pass **without** a peel, resolves `found`, and yields
no defect at all — which is consistent with the audit's contract (a hash outside the Landed
section is an existence claim, not a landed-commit claim) and is the `PG41` family's territory,
not a WrongType gap.

## 7. Residual risk and verification gaps

* **Residual risk (uncovered, but currently correct):** the "wrong-type citation + unrelated
  opaque hole" combination (F1) is unprotected by the grid. The pinned source is correct there
  (observed exit 1 on both plain and promisor-marked constructions); a future change to
  `refuse_unknown` could break it without any row noticing. This is the one item I would put in
  front of L1.
* **Residual risk (cross-store sensitivity):** the wrong-type verdict depends on the `RANK`
  ladder (`wrongtype` 1 > `absent` 0) *and* on the `status[token] == "absent"` guard at `:222`
  that stops a second store from re-offering `unknown` for the same token. Mutant A shows that
  degrading the classification is caught; but the interaction is subtle and is exercised only
  incidentally, by the fleet store happening not to hold the blob.
* **Not verified here (out of scope for this slice):** the other 45 grid rows; the mutation
  suites `promisor-mutants.py` / `isolation-mutants.py`; the auditor's own `--selftest`; the
  historical-parity run; the open row `PG40` (contested traversal scope, deliberately not
  graded). This lane ran **only** the two assigned rows plus the two scratch mutants over them.
* **Not verified (inferred, not executed):** that the same holds for a wrong-type *tag* object
  and for a wrong-type object present in only one of the two audited stores; the type-agnostic
  `wrongtype` classification makes both likely, but neither was executed.
* **Peer hazard noted (not applicable here):** `KamaR23-2.CaseFleetBlobless` reports that a
  blobless fixture's reachable `file://` origin lets a stray non-`--no-lazy-fetch` probe
  materialise missing blobs and silently evaporate the premise. This family uses **no**
  blobless clone and every probe I ran is `--no-lazy-fetch`-isolated (the grid's
  `missing_objects`/`object_exists`/`object_inventory` helpers and the auditor's `GIT_ISOLATION`);
  the before/after object inventories confirm nothing was materialised.

## 8. Files written; unverified items

Written (absolute):

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseWrongType.md` — this report.
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseWrongType/candidate.json` — the assigned run's candidate record (both arms, the two rows).
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseWrongType/population.json` — the 47-row manifest as loaded by the grid.
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseWrongType/probe-out.json` — my independent premise/lookup/mutant observations for the four locally built fixtures.
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseWrongType/mutant-diffs.txt` — the two scratch mutants as unified diffs against the pinned auditor.

Not written: any production file. No production source, expectation, fixture, lane index, fleet,
routing, service or object store was modified; the only production delta is this lane's own
report and artifact tree under `.ufo/waves/round-24/falsify/`.

Unverified items are listed in §7; the load-bearing claims of this report (the two graded
rows' exits, kinds, tokens, premises, twin equality, zero object acquisition, and both mutant
outcomes) were each observed directly, with the command and exit code recorded in §2.

## 9. Concurrent production delta observed (not attributable to this lane)

At the end of this lane, `git status --short --untracked-files=no` in production shows one
tracked-file modification that this lane did **not** make:

```
 M .ufo/waves/round-24/build/advice/GridOracle.md      (mtime 2026-10-21 16:54:48 -0300)
```

It is an append-only **proposal** (L1's "Correction 5", `fixes/GridMetrics/`) that landed while
this lane was running; my lane wrote only under `.ufo/waves/round-24/falsify/`. Two of its
points corroborate observations already recorded here: (i) the per-arm amended-view metrics were
wrong (`amended_view_met` counted only `met_amended_frozen` rows, so the **current** arm always
reported 0 — my §4 reads the per-row `met_amended`/`violations` fields, which are correct, and
does not rely on that summary counter); (ii) the withdrawn/failed bookkeeping conflation I noted
as **F2** is exactly what Correction 5(b) separates (`original_view_unmet` vs
`withdrawn_original_failures` restricted to rows whose original and amended expectations
differ). For this family the two rows' original and amended views agree, so they are *not*
withdrawals under either reading — `withdrawn_original_failures = []` and `met_original = true`
for both rows on the current arm. The proposal leaves the expectation manifest unchanged
(`d86b7bea…`, 47 rows), so **F1's recommended row addition is still open**; note that adding a
row changes `population_size`/`population_sha256` and, per the immutability rule, must be
registered as an *addition* to the 44-case snapshot rather than an edit of it.

Report: .ufo/waves/round-24/falsify/advice/CaseWrongType.md
