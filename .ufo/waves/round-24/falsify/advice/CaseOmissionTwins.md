# CaseOmissionTwins — round-24 fresh falsification (family: genuine **omission** × promisor-marked / plain twins)

**Verdict: HOLDS.** All four rows of the assigned selection (`PG09-omission-lane-promisor`,
`PG10-omission-lane-plain`, `PG11-omission-fleet-promisor`, `PG12-omission-marker-lane`)
meet the **graded (amended) view** under the current arm; the omission is reported as a
*finding* (exit 1, `landed-omitted`, full 40-hex lane sha) and never as a refusal; the
promisor-marked variants and their plain twin produce byte-identical verdict documents
(24 of 25 document leaves identical; the only differing leaf is the fixture path
placeholder); no object was acquired; no transport was invoked; the r23 base behaviour was
reproduced exactly (3 metadata refusals) and the repair is measured on the amended target
columns, not on frozen history.

**No source defect was found in this family.** Three **fixture-level** findings (F1–F3) and
four verification-gap notes (G1–G4) are reported separately in §8/§9. Nothing in
`production/.jj/index`, the fleet, sibling lanes, operator config, routing, services or any
real object store was touched; no network/transport/execution payload was used; no tool was
installed or upgraded.

---

## 1. Pinned base and provenance

| item | value |
|---|---|
| pinned revision (detached, scratch clone) | `2e254a1763a9c08aa07fc53081287f506c447d84` |
| clone | `/fast/scratch/hyaku/kama-r24/falsify/CaseOmissionTwins` (`--no-hardlinks` from `/home/vgpnk/Projects/shokunin/kama-shokunin`) |
| clone object store | separate inodes from production (`stat`: clone `.git/objects` nlink 259 vs production 1) — no hardlinks |
| auditor (source tool) sha256 | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| grid runner sha256 | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` |
| expectations manifest sha256 | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` |
| mutation probe sha256 | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` |
| frozen r23 auditor sha256 (`0df800e8…:tools/report-landing-audit.py`) | `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` |
| oracle snapshot sha256 (pinned rev) | `1f5a469989b24b6b321b6b9a39533dad00f7e4daba80dca5f1321e888b142b0e` |
| oracle amendment sha256 | `930b087a218f880a55c4507b7f11309eae130e2b5dd2111e27d5653b39c8f82f` |
| oracle supplement-2 sha256 | `4600a8c3951d26b68ee2562d5967cecfe9b00d66443ac10e6d371956e5d34368` |
| preregistration sha256 | `6dde0d72343c9b8e64ec6e3ae4c9b382dfa3daaf9d0f6afd3f274cfac30e844c` |
| population sha256 (47 rows) | `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` |
| environment | git 2.56.0, python 3.14.8, `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseOmissionTwins` |

All four pinned digests match the values carried in my assignment (source `ea51bc35…`,
runner `b034e159…`, manifest `d86b7bea…`, mutants `6e0b9d62…`). The frozen r23 auditor
digest matches `derived_from.frozen_auditor_sha256` in the oracle snapshot, and the frozen
arm in my run was materialised from **this clone's** history
(`git -C <clone> cat-file blob 0df800e8…:tools/report-landing-audit.py`), so the historical
arm is the genuine r23 base, not a copy of a working-tree file.

**Expectation integrity — no fixture was fitted to the candidate.**

* The 44-case oracle was frozen in commit `f66b226` ("freeze independent 44-case original
  and amended oracle before candidate inspection"), i.e. **before** the candidate commit
  `ed1cc3a`; the pinned snapshot file is byte-identical to that commit's copy
  (`1f5a4699…`).
* JSON comparison of the pinned snapshot against the pinned 47-row manifest:
  **all 44 original rows byte-identical**, `drift: []`; the manifest's 3 extra rows are
  exactly the independent opaque supplement (`PG46/PG47/PG48`).
* The pinned manifest is byte-identical to the candidate's build copy
  `.ufo/waves/round-24/build/out/GridOracle/promisor-grid-expectations.json`
  (`cmp` → identical, `d86b7bea…`).
* `git log --follow` on the manifest shows exactly two commits: the freeze (`f66b226`)
  wrote the snapshot, the candidate (`ed1cc3a`) added the manifest file itself
  (`+1508` lines, 0 deletions) — the expected cells were **added**, never edited.

---

## 2. Assigned measurement — exact command, exit code

```
cd /fast/scratch/hyaku/kama-r24/falsify/CaseOmissionTwins
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseOmissionTwins \
python3 tests/report-audit/promisor-grid.py --arm both \
  --case PG09-omission-lane-promisor \
  --case PG10-omission-lane-plain \
  --case PG11-omission-fleet-promisor \
  --case PG12-omission-marker-lane --json --out out
```
**exit 0** (stdout 20272 bytes, stderr empty). Artefacts:
`.ufo/waves/round-24/falsify/out/CaseOmissionTwins/assigned.json` (+ empty `assigned.err`,
plus the grid's own `grid-out/population.json` and `grid-out/candidate.json`).

Grid summary **as observed** (not as the harness summarises it):

| arm | case | row class | exit | defects (kind, token) | met(frozen) | met(amended/live) | objects acquired | twin_equal |
|---|---|---|---|---|---|---|---|---|
| frozen | PG09-omission-lane-promisor | policy | 2 | – | **true** | **false** | `{}` | n/a (no document) |
| frozen | PG10-omission-lane-plain | control | 1 | `landed-omitted`, `1acb5ebb06054bf52d84ffdacd8727b95287f34b` | **true** | **true** | `{}` | n/a (no document) |
| frozen | PG11-omission-fleet-promisor | policy | 2 | – | **true** | **false** | `{}` | n/a (no document) |
| frozen | PG12-omission-marker-lane | policy | 2 | – | **true** | **false** | `{}` | n/a (no document) |
| current | PG09-omission-lane-promisor | policy | 1 | `landed-omitted`, `1acb5ebb06054bf52d84ffdacd8727b95287f34b` | – | **true** | `{}` | **true** (vs PG10) |
| current | PG10-omission-lane-plain | control | 1 | `landed-omitted`, `1acb5ebb06054bf52d84ffdacd8727b95287f34b` | – | **true** | `{}` | **true** (vs PG09/PG11/PG12) |
| current | PG11-omission-fleet-promisor | policy | 1 | `landed-omitted`, `1acb5ebb06054bf52d84ffdacd8727f34b` | – | **true** | `{}` | **true** (vs PG10) |
| current | PG12-omission-marker-lane | policy | 1 | `landed-omitted`, `1acb5ebb06054bf52d84ffdacd8727f34b` | – | **true** | `{}` | **true** (vs PG10) |

Frozen-arm stderr (the historical baseline, retained verbatim):

```
PG09  could-not-evaluate: <lane>:  partial clone (remote.origin.promisor)
PG11  could-not-evaluate: <fleet>: partial clone (remote.origin.promisor)
PG12  could-not-evaluate: <lane>:  partial clone (promisor pack)
PG10  (empty)
```

Current-arm stderr: **empty for all four rows**; no exit-2 at all, so no metadata refusal,
no unknown-citation refusal, no full-closure refusal.

Harness counters: `tracebacks=0`, `timeouts=0`, `harness_leaks=0` in both arms;
`violations=0`; `twin_mismatch=[]`; `twin_compared=4`; `twin_pairs_compared` =
all four cases; `withdrawn_original_failures=[]` (both arms).

---

## 3. Which view is graded here — original vs amended (withdrawn expectation kept visible)

* **Frozen** = r23 base behaviour. It is *history*, never a target: the frozen arm met its
  own `frozen` view on all four rows and met the **amended** view on only **1 of 4**
  (`amended_view_unmet = [PG09, PG11, PG12]`). That is exactly the calibration signal:
  the r23 base refused three complete promisor-marked repositories and got the plain
  control right.
* **Original** (the initial registration) — for these four rows the manifest carries **no
  `amended` override**, so per the manifest's own rule ("a case without an 'amended' entry
  uses its 'original' view") the **live graded view for PG09–PG12 *is* the original view**:
  exit 1, kinds `["landed-omitted"]`, defect `{"kind":"landed-omitted","token":"$omitted"}`,
  `reason_class: null`.
* The amendment's **withdrawal** applies only to the rows it names
  (`PG22/23/24/28/30/34/41`, plus the supplement rows `PG46/47/48`).
  **None of those rows is in my bounded selection**, so *nothing in this family is
  withdrawn* and no originally-withdrawn failed expectation has to be displayed for these
  four rows. `withdrawn_original_failures` is empty, and `met_original` is **true** for all
  four current-arm rows — i.e. the original registration's exit-1 expectation for this
  family is met, not relabelled.
* `PG09/PG11/PG12` are *policy* rows and `PG10` is a *control* (no-harm twin) row, exactly
  as the manifest declares; the current arm keeps the control's verdict identical to the
  frozen arm's (`landed-omitted` + identical token in both arms), which is the no-harm
  evidence for the repair.

---

## 4. Independent re-derivation (the fixture itself was attacked, not trusted)

The grid's own builder was not reused for the core evidence. I wrote a **separate**
builder from the written case notes (`out/CaseOmissionTwins/build_omission.py`) that
constructs the family from the spec text only:

* lane: `round-1: work` by `kama-shokunin` @author-time 1000 (cited), then
  `round-1: more` by `kama-shokunin` @1500 (**the omitted commit**);
* fleet: init @1900, then the round-1 report @2000 citing **only** the first commit;
* marks: `remote.origin.promisor=true` + `extensions.partialclone=origin` +
  `remote.origin.url=<nonexistent path>` (config) or a paired
  `objects/pack/pack-<sha>.promisor` next to its real `.pack` (marker).

**Result: my independent build is content-identical to the grid's fixture.** The commit ids
come out identical — cited `58866b563cd900df310588effe79028efc104c33` (`l1`), omitted
`1acb5ebb06054bf52d84ffdacd8727b95287f34b` (`l2`) — which is only possible with identical
trees, authors, subjects and author/committer times. The grid's observed defect token
(`1acb5ebb…`) is therefore *the omitted commit itself*, confirmed by content address, not
by trusting the harness's `$omitted` substitution.

Verified fixture facts (all four variants, independently measured):

| fact | PG09 (lane config) | PG10 (plain) | PG11 (fleet config) | PG12 (lane marker) |
|---|---|---|---|---|
| lane missing objects (`rev-list --objects --missing=print --no-lazy-fetch`, master) | `[]` | `[]` | `[]` | `[]` |
| fleet missing objects (same, HEAD) | `[]` | `[]` | `[]` | `[]` |
| cited commit `l1` present locally | yes | yes | yes | yes |
| omitted commit `l2` present locally | yes | yes | yes | yes |
| report content | cites `l1` only | same | same | same |
| report first-add author time (the cutoff) | 2000 | 2000 | 2000 | 2000 |
| omitted commit author time | 1500 (≤ cutoff ⇒ pre-cutoff) | 1500 | 1500 | 1500 |
| promisor signal | `remote.origin.promisor=true` | none | `remote.origin.promisor=true` | `pack-<sha>.promisor` marker present |
| promisor remote URL exists? | no (nonexistent path) | – | no (nonexistent path) | – |

⇒ the premise "complete promisor-marked repository" is literally true (no hole anywhere),
and the premise "genuine omitted pre-cutoff round-1 commit" is literally true (the commit
exists, is authored by `kama-shokunin`, its subject matches `round-1:`, its author time
precedes the report's first add, and it is cited **nowhere** in the report — the auditor
reports `cited_elsewhere: false`).

---

## 5. Exact finding/token pairs and content-derived reason IDs

Current arm, all four rows — identical pair, identical token:

```
("landed-omitted", "1acb5ebb06054bf52d84ffdacd8727b95287f34b")
```

Full verdict document (PG09 variant, independent run; PG10/PG11/PG12 differ only in
`.results[0].report`):

```json
{"errata_invalid": [], "errata_unmatched": [],
 "results": [{"cutoff": 2000,
              "defects": [{"cited_elsewhere": false, "corrected_by": [],
                           "kind": "landed-omitted",
                           "token": "1acb5ebb06054bf52d84ffdacd8727b95287f34b"}],
              "post_report": [], "report": "<fleet>/.ufo/reports/round-1/kama.md",
              "report_committed": true, "required": 2, "round": 1,
              "round_commits": 2, "source_url_hashes": []}],
 "summary": {"by_kind": {"landed-ambiguous": 0, "landed-omitted": 1,
                          "landed-section-missing": 0, "landed-unresolved": 0,
                          "unresolved-full-hash": 0},
             "corrected": 0, "defects": 1, "errata_invalid": 0, "errata_rows": 0,
             "errata_unmatched": 0, "post_report_commits": 0, "reports": 1,
             "required_commits": 2, "rounds": [1], "status": "failed",
             "uncorrected": 1}}
```

* `required = 2` (both round-1 lane commits are pre-cutoff candidates), `round_commits = 2`,
  `post_report = []` — consistent with the fixture facts above.
* **Content-derived reason IDs**: the kind `landed-omitted` and the full 40-hex token are
  derived from the actual lane history and the actual report text. There is **no exit-2
  reason string at all** in this family, so no `reason_class`/`names_any_of` obligation is
  triggered (`names_any_of` is absent from all four rows — correctly, since none of them
  expects a refusal). The frozen arm's refusals were metadata-class, matching the
  expectation's `frozen.reason_class = "metadata"`.
* `reason_forbidden` (`"partial clone ("`, `"promisor pack"`) — not present in any current
  arm output; the current arm produced no stderr at all.
* The finding is *not* vacuous and *not* constant: two local mutation probes (§6) flip it
  to a clean exit 0.

---

## 6. No objects acquired, no transport, and twin comparison (independently computed)

**Object acquisition.** The grid's own `objects_acquired` check is `{}` (empty set
difference) for all eight arm×case rows. I measured it independently with
`git --no-lazy-fetch cat-file --batch-all-objects --batch-check=%(objectname)` before and
after each audit run: `{"lane": [], "fleet": []}` for every variant and for all nine
combination probes in §6.3.

**No transport.** After the audits:
* no `FETCH_HEAD`, no `ORIG_HEAD`, no new packs, no new loose objects in either repo;
* `git status --porcelain` clean in both repositories of every variant;
* refs unchanged (`refs/heads/master` still at `1acb5ebb…` in the lane);
* the HEAD reflogs contain **only the fixture's own two build commits** — no `fetch`/
  `pull`/`clone` entry;
* the promisor `remote.origin.url` points at a **nonexistent** path, so any transport
  attempt would have errored rather than silently succeeded.

**Twin comparison (my own computation, independent of the grid's).** Raw stdout documents
of the four variants, normalised only for the fixture path, are byte-identical. A
leaf-by-leaf comparison of the JSON structure (25 leaves) shows **exactly one differing
leaf** per variant:

```
.results[0].report : <plain>/fleet/.ufo/reports/round-1/kama.md
                  -> <lane_config>/fleet/…   (and likewise for fleet_config, lane_marker)
```

Every substantive leaf is identical: `cutoff=2000`, `required=2`, `round_commits=2`,
`post_report=[]`, `source_url_hashes=[]`, `report_committed=true`, the defect
`(landed-omitted, 1acb5ebb…)`, `cited_elsewhere=false`, `corrected_by=[]`,
`errata_invalid=[]`, `errata_unmatched=[]`, and the whole `summary` block
(`status:"failed"`, `defects:1`, `uncorrected:1`, `by_kind` counts).

### 6.1 Non-vacuity probes (my own, not manifest rows)

| probe | construction | observed |
|---|---|---|
| cite-omitted | report additionally cites `l2` | **exit 0**, defects `[]` — the omission finding disappears when the content changes |
| no-omission | lane reset to `l1` (no second round-1 commit) | **exit 0**, defects `[]` — a lane without the omission is clean |

⇒ the exit-1 verdict in this family is produced by the genuine omission, not by the
promisor metadata, not by the fixture's shape, and not by a constant.

### 6.2 Frozen-vs-current control check (no-harm)

`PG10` (plain control) is **byte-identical in both arms**: exit 1, same kind, same token,
same document. The repair changed exactly the three promisor-marked policy rows
(refusal → correct failed verdict) and left the unmarked control untouched.

### 6.3 Cross-combination probe (my own, not a manifest row)

Nine lane/fleet mark combinations, all with the same omission fixture:

```
plain, lane_config, fleet_config, lane_marker, fleet_marker,
both_config, both_marker, lane_config_fleet_marker, lane_marker_fleet_config
```

All nine: **exit 1**, `status:"failed"`, defect `("landed-omitted",
1acb5ebb06054bf52d84ffdacd8727b95287f34b`)`, document **equal to the plain twin**,
`objects_acquired = {}`, stderr empty. The amended policy statement "promisor metadata
alone never changes a verdict" therefore holds for every combination of the metadata
signals this family can produce — including combinations the manifest does not cover
(fleet marker; lane and fleet marked at once; marker on one side and config on the other).

---

## 7. Source review (frozen → current), limited to what this family exercises

`git diff 0df800e8… 2e254a17… -- tools/report-landing-audit.py`:

* The **r23 blanket refusal was removed**: the frozen blob refused any repository with
  `extensions.partialclone`, `remote.<x>.promisor=true`, or a paired `*.promisor` marker
  (frozen lines 441–465: `partial clone (promisor pack)` / `partial clone (<key>)`).
  The current source contains **no** such refusal; the only remaining `promisor`
  occurrences are in the module docstring (lines 58–59, 134) and in the auditor's own
  selftest (lines 1176–1195).
* The replacement path is **generic, not fixture-specific**: `RepoStore` +
  `missing_reachable` + `refuse_unknown` refuse only when a *citation* cannot be resolved
  **and** is known to name content the store references but cannot serve. This family
  never reaches that path (its citation resolves; its stores have no missing objects),
  which is exactly why the four rows return exit 1 rather than exit 2 — the expected
  outcome under the amended policy ("metadata-only declarations do not establish
  incompleteness").
* `GIT_ISOLATION` still carries `--no-lazy-fetch`, `--no-replace-objects`,
  `log.showSignature=false` etc.; `git_env()` still drops inherited `GIT_*` and points
  `GIT_CONFIG_GLOBAL` at `/dev/null`. The observed absence of transport (§6) is
  consistent with that.

**No source defect was found in this family.**

---

## 8. Fixture findings (separate from source findings)

**F1 — the fixture is "complete" in the strongest sense, so this family cannot detect a
refusal that is *conditional* on a hole.** All four variants have zero missing objects
(`lane_missing=[]`, `fleet_missing=[]`). The family therefore proves *"metadata alone does
not change the verdict"*; it does **not** prove *"metadata + a hole does not change the
verdict"*. Rows PG13–PG21 and PG33–PG36 cover the hole side of the policy. No change
proposed; recorded so that no reader over-reads this family as a closure test.

**F2 — the omission fixture is fixed to a single shape: one extra round-1 commit whose
subject is `round-1: more`, authored at 1500, with the report citing the first commit by
full 40-hex sha.** Consequently the family exercises exactly one omission-detection path
(`pre` commit not matched by any `## Landed changes` abbreviation) and one citation form
(40-hex). It does **not** cover: an omission cited elsewhere in the report but outside the
`## Landed changes` section (`cited_elsewhere: true`), an omission detected by *prefix*
abbreviation (e.g. a 7-hex citation of the sibling commit), a `checkpoint(r1)`-subject
commit, or a post-cutoff sibling. These are ordinary branches of the same rule and are not
covered by any manifest row I ran. No source change proposed; listed as a manifest-coverage
gap, not a defect.

**F3 — the manifest's twin links for this family are one-directional but are graded in
both directions.** `PG09`, `PG11` and `PG12` each declare `twin: PG10`, while `PG10`
declares `twin: null`. The harness reconstructs the reverse edges (`reverse` map) and
compares all four pairs, and my independent field-by-field comparison covers the same four
pairs, so the asymmetry is harmless here. It is a manifest-ergonomics note only (a reader
of the manifest alone would expect `PG10` to name its partners).

---

## 9. Verification gaps / residual risk

**G1 — only git 2.56.0 was exercised.** The inherited **Git ≥ 2.45 prerequisite remains
open at L0**; nothing in this family depends on a post-2.45 flag: the only floor-relevant
flag used is `--no-lazy-fetch`, which already existed in the frozen base, and the
supplement's forbidden `--missing=print-info` / `--missing-only` options are not used by
anything I ran.

**G2 — the family is scoped to the amended view only.** `PG40-missing-cited-unselected-branch-object-promisor`
remains in `open_rows` (reported-not-graded by the manifest) and was not touched.

**G3 — the "withdrawn expectation" bookkeeping is *absent* in this family, by
construction.** Because none of PG09–PG12 carries an `amended` override, this family
provides **no** evidence about the withdrawal mechanics themselves (the
`withdrawn_original_failures` list is empty and `met_original == met_amended` for all four
rows). The withdrawal mechanics must be graded on the amended rows (PG22/23/24/28/30/34/41
and PG46/PG47/PG48), which are outside my bounded selection.

**G4 — the source-census/ledger supplement (S105 / the rejected S095 cross-API inference)
is L1-owned after this stage and was not verified here.** I did not re-count source rows,
did not touch `corpus/SOURCES.md` or the knowledge ledger, and make no claim about the
census being complete at this revision.

**Residual risk (honest statements).**

* *What I observed:* the four manifest rows meet the graded view at the pinned revision
  with the pinned four digests; my independent rebuild of the fixture reproduces the same
  object ids, the same premise facts and the same verdicts; nothing was acquired and no
  transport ran.
* *What I inferred:* that the policy generalises beyond the manifest rows — supported by
  the nine-combination probe and by the generic (non-fixture-specific) shape of the source
  change, but **not** proven for hole-bearing repositories, for post-2.45 git, or for the
  other 43 rows.
* *Not claimed:* no new serving capability, no higher numeric score, no closure of the
  inherited Git ≥ 2.45 prerequisite, no claim that the whole 47-row population passes
  (I ran only my 4 assigned rows).

**Hazard noted from a peer (not a defect in my family).** `KamaR23-2.CaseFleetBlobless`
reports that the *blobless* fixture's `remote.origin.url` points at a **reachable**
`file://` origin, so a manual probe without `--no-lazy-fetch` can materialise the missing
blob and turn a correct exit-2 into a false clean exit 0. **My family is not exposed to
that hazard**: the promisor fixtures point `remote.origin.url` at a *nonexistent* path, and
every probe I ran used `--no-lazy-fetch` / `--no-replace-objects`. Recorded so that no one
reads my exit-1 results as evidence against the peer lane's exit-2 result.

---

## 10. Files written (this reviewer only; no production file was modified)

* `.ufo/waves/round-24/falsify/advice/CaseOmissionTwins.md` (this report)
* `.ufo/waves/round-24/falsify/out/CaseOmissionTwins/assigned.json` — the exact assigned
  grid run (`--arm both --json`), exit 0
* `.ufo/waves/round-24/falsify/out/CaseOmissionTwins/assigned.err` — empty (stderr)
* `.ufo/waves/round-24/falsify/out/CaseOmissionTwins/grid-out/candidate.json`,
  `grid-out/population.json` — the grid's own `--out` dump
* `.ufo/waves/round-24/falsify/out/CaseOmissionTwins/build_omission.py` — my independent
  fixture builder (written from the case notes, not from the grid's builder)
* `.ufo/waves/round-24/falsify/out/CaseOmissionTwins/run_audit.py` +
  `audit-result.json` — independent audit of the four variants + the two mutation probes
* `.ufo/waves/round-24/falsify/out/CaseOmissionTwins/probe_combinations.py` +
  `combinations.json` — the nine lane/fleet mark combinations
* `.ufo/waves/round-24/falsify/out/CaseOmissionTwins/fixture-facts.json` — the measured
  fixture facts (missing/present objects, times, report text)
* `.ufo/waves/round-24/falsify/out/CaseOmissionTwins/audit.err` — empty (stderr)

Scratch only: `/fast/scratch/hyaku/kama-r24/falsify/CaseOmissionTwins/` (clone + all
fixtures + `TMPDIR` for every subprocess). Nothing in `production/.jj/index`, the fleet,
sibling lanes, operator config, routing, services or any real object store was touched; no
network, transport or execution payload was used; **no tool was installed or upgraded** in
this review (nothing needed installing).

Report: .ufo/waves/round-24/falsify/advice/CaseOmissionTwins.md
