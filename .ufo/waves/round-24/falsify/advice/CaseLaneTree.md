# CaseLaneTree — PG15/PG16 falsification (kama round 24, pinned `2e254a17`)

**Verdict: HOLDS for the assigned slice.** Both rows of the LaneTree family
(`PG15-missing-lane-tree-promisor`, `PG16-missing-lane-tree-plain`) meet their live (graded)
expectation on the pinned candidate: exit 2, a typed `could-not-evaluate:` refusal, a
content-derived reason that names the unavailable tip tree, no verdict document on stdout, no
object acquisition and no transport. The promisor-marked row and its plain no-harm twin produce
a byte-identical refusal after path normalisation, so promisor metadata changed nothing.
**No source defect was found in this family.** Four **fixture/grader-level** observations
(F1–F4) are reported separately below, as required; none of them invalidates the rows.

Lane: leaf member — no subagent dispatch. Read-only production.

---

## 1. Pinned base (observed)

| item | value |
|---|---|
| clone | `/fast/scratch/hyaku/kama-r24/falsify/CaseLaneTree/repo` (`git clone --no-hardlinks`, detached) |
| HEAD | `2e254a1763a9c08aa07fc53081287f506c447d84` (clean tree, `git status --porcelain` empty) |
| `tools/report-landing-audit.py` | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` (matches assignment) |
| `tests/report-audit/promisor-grid.py` | sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` (matches assignment) |
| `tests/report-audit/promisor-grid-expectations.json` | sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (matches assignment) |
| manifest | 47 rows, `population_sha256 = 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` |
| frozen auditor blob `0df800e8…:tools/report-landing-audit.py` | sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` (equals the oracle snapshot's `frozen_auditor_sha256`) |
| environment | git 2.56.0, python3 3.14.8; `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseLaneTree`; no tool installed or updated |

Production was not modified: in the pinned clone `git status --porcelain` shows only the
untracked `.ufo/waves/round-24/falsify/` artifact tree and the pre-existing untracked
`.ufo/waves/round-24/fixes/`; **no tracked file changed**. This clone contains no
`production/` directory, so no lane index (`production/.jj/index`), fleet, sibling lane,
operator config, routing, service or real object store was read or written by this lane. No
network, transport or execution payload was used; the only transport exercised was a **local
file path** git remote I created inside the scratch tree as a trap (§5, F4). No expectation cell
was edited and no fixture was made to fit the candidate.

## 2. Views and grading target for this family

Read before measuring: `.ufo/waves/round-24/preregistration.json`,
`oracle-amendment-1.json`, `oracle-snapshot-before-inspection.json`, `oracle-supplement-2.json`.

* The committed fixed table is the **44-case snapshot, byte-identical**, plus the **3 independent
  opaque cells** (`PG46-opaque-tree-hides-cited-blob`, `PG47-opaque-tree-with-unresolved-fabricated-token`,
  `PG48-opaque-unused-tree-no-unresolved-token`) = 47. Verified by comparing the committed
  `promisor-grid-expectations.json` against the `.ufo` snapshot: `ufo-only: []`,
  `content-differing shared cases: []`, `repo-only: [PG46, PG47, PG48]`. The 44 shared rows are
  therefore not re-written after the candidate.
* `PG15`/`PG16` have **no `amended` entry**; the grid grades them with the `original` view
  (`live = expect.get("amended", expect["original"])`), i.e. exit 2 / `reason_class: unavailable`.
  The L1 amendment's `amended_rows` list covers PG22/23/24/28/30/34/37/41 only, so the
  withdrawal (preregistration `expected_after[3]`, unknown-citation ⇒ exit 2) **does not touch
  this family**: there is no withdrawn expectation here to keep visible, and none was relabelled.
* The `frozen` view (r23 base `0df800e8`) is history, never a target; it is reported below only
  as the measured baseline.

## 3. Commands run (exact)

```
$ cd /fast/scratch/hyaku/kama-r24/falsify/CaseLaneTree/repo
$ TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseLaneTree \
    python3 tests/report-audit/promisor-grid.py --arm both \
      --case PG15-missing-lane-tree-promisor --case PG16-missing-lane-tree-plain --json
exit 0        (stdout → out/grid.json, stderr → out/grid.stderr, empty)
```

Grid result (from `out/grid.json`):

| arm | case | exit | `met_amended` | `met_frozen` | `met_original` | acquired | traceback/timeout/leak |
|---|---|---|---|---|---|---|---|
| current | PG15 | 2 | **true** | – | **true** | lane `[]`, fleet `[]` | none |
| current | PG16 | 2 | **true** | – | **true** | lane `[]`, fleet `[]` | none |
| frozen | PG15 | 2 | – | true | – | lane `[]`, fleet `[]` | none |
| frozen | PG16 | 2 | – | true | – | lane `[]`, fleet `[]` | none |

`current` arm: `graded=2 violations=0`, `withdrawn_original_failures=[]`, `twin_mismatch=[]`,
`tracebacks=0 timeouts=0 harness_leaks=0`.
`frozen` arm: `amended_view_met=1/2`, `amended_view_unmet=['PG15-missing-lane-tree-promisor']`
— i.e. the r23 base refused PG15 for the **wrong reason** (§6).

Two further bounded, offline probes (scripts and outputs under
`.ufo/waves/round-24/falsify/out/CaseLaneTree/`):

```
$ python3 probe_lanetree.py     # independent object census + both arms + twin text compare
exit 0
$ python3 probe2_transport.py   # git-call shim + live local trap remote + isolation control
exit 0
```

## 4. Independently asserted facts (not taken from the grid's own report)

### 4.1 Actual missing / present objects (own census, `--no-lazy-fetch` throughout)

| object | OID | lane | fleet |
|---|---|---|---|
| lane tip commit | `58866b563cd900df310588effe79028efc104c33` | **present** | absent |
| lane tip **root tree** | `1c13e47ce9f8088dc933a80123cf6a8ee2fa701d` | **ABSENT** | absent |
| `f` blob | `56d7b323865c731da81e0225cf109d66f0480919` | present | absent |
| `corpus/SOURCES.md` blob | `051975b0ced83169116c235e7691c0a1a8313300` | present | absent |
| fleet report blob | `0cf7ed5cd6dec335553d165dc587baa224ab302b` | absent | present |
| fleet tip tree | `b1e11739fedfb736f2936bd9addf7e4a286d462e` | absent | present |

`git rev-list --objects --missing=print --no-object-names` over `refs/heads/master` (lane) and
`HEAD` (fleet) returns exactly `['1c13e47ce9f8088dc933a80123cf6a8ee2fa701d']` for the lane and
`[]` for the fleet — in **both** PG15 and PG16. The two fixtures are byte-equivalent except for
the promisor config: PG15 lane config = `remote.origin.promisor=true`,
`extensions.partialclone=origin`, `remote.origin.url=<tmp>/absent-remote.git`
(`promisor_facts_lane.promisor_backed = true`); PG16 lane config has none of these
(`promisor_backed = false`). The fleet is plain in both.

### 4.2 Exact verdict / reason pairs (current arm)

Both rows, character-for-character apart from the lane path:

```
could-not-evaluate: unavailable required object: 58866b563cd900df310588effe79028efc104c33:corpus/SOURCES.md (tip tree 1c13e47ce9f8088dc933a80123cf6a8ee2fa701d) in <lane>: git ls-tree 58866b563cd900df310588effe79028efc104c33 -- corpus/SOURCES.md in <lane>: rc=128 fatal: not a tree object
```

* exit `2`; stdout empty (no verdict document, not even a JSON one).
* finding/token pairs: **none** — these are refusal rows; `observed_defects` returns `None`
  (stdout is not a verdict document), matching the expectation rows (`kinds: null`,
  `defects: null`).
* reason class: `unavailable` (matched terms present in the text: `unavailable`,
  `not a tree object`), reason is content-derived, **not** the r23 metadata refusal
  (neither `partial clone (` nor `promisor pack` occurs — `stderr_has_metadata_refusal = false`).
* the reason **names the unavailable object**: the missing tip tree
  `1c13e47ce9f8088dc933a80123cf6a8ee2fa701d` (the grader's `names_any_of: ["$tip_tree"]`).
  It is obtained from the commit header (`root_tree()` → `git log -1 --format=%T`), which is
  still readable when the tree object itself is absent.
* objects acquired: none, in either store, in either arm (`before`/`after` inventory diff).

### 4.3 Twin comparison (actual)

Both rows produce **no verdict document**, so the grid's document comparison is vacuous here
(`document: None` for both ⇒ `twins: {'PG16…': None}`, `twin_equal: None`,
`twin_compared=0`, `twin_pairs_compared=[]`). I therefore compared the refusals themselves:
after normalising the case directory, the current-arm stderr of PG15 and PG16 are **identical**
(`current_stderr_equal_after_path_normalisation = true`). The frozen arm's two stderrs are
*not* identical (PG15 = the r23 metadata refusal, PG16 = the raw `ls-tree` error), so the pair
does discriminate — but only in the frozen arm (see F1).

## 5. No-lazy-fetch / no-transport, measured rather than assumed

* **Every** git the auditor spawns was captured with a PATH shim. 13 calls, and
  `calls_without_no_lazy_fetch = []`: all carry
  `--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8 -c log.follow=false
  -c log.showRoot=true -c log.showSignature=false -c log.mailmap=false`. The verbs used were
  only `rev-parse`, `for-each-ref`, `ls-tree`, `log`; **no** `fetch`, `clone`, `remote-*`,
  `upload-pack` or URL transport appeared.
* **Live trap**: I rebuilt the PG15 lane with `remote.origin.url` pointing at a *local* bare
  repository that really serves the missing tree (reachable from `refs/heads/master`,
  `uploadpack.allowAnySHA1InWant=true`). Result: exit `2`, stdout empty, the reason still names
  the tip tree, **objects acquired: lane `[]`, remote `[]`**, and the tree remained missing in
  the lane. The refusal is therefore produced by the isolation, not by a dead remote.
* **Isolation control**: in the *same* promisor-marked lane, one `git cat-file -e <tree>`
  **without** `--no-lazy-fetch` did lazy-fetch the tree
  (`objects_acquired_lane_without_isolation = ['1c13e47c…']`, trap live). This confirms the
  trap can fire, i.e. the no-fetch result in the previous bullet is a real measurement.
* This corroborates the in-source selftest cases `promisor-metadata-keeps-the-local-verdict` and
  `promisor-remote-is-never-contacted` (`tools/report-landing-audit.py`, ~line 1191-1195).

## 6. Frozen (r23) baseline — history, not a target

* PG15 frozen: `could-not-evaluate: <lane>: partial clone (remote.origin.promisor)` — the blanket
  r23 metadata refusal, exactly what the round-24 repair removes. It meets the *frozen*
  expectation (`reason_class: metadata`) and **fails the amended/original view**
  (`amended_view_unmet` lists PG15). This is the measured harm the repair addresses.
* PG16 frozen: `could-not-evaluate: git ls-tree … rc=128 fatal: not a tree object` — the right
  *substance* but an untyped message that does not name the unavailable object and does not carry
  the `unavailable required object:` prefix. It is counted as “meeting the amended view” only
  because the frozen arm is scored with `form_check=False` and an empty names list (F2).

## 7. Source behaviour (cited, not paraphrased)

* `tools/report-landing-audit.py:280-284` `required_read(what, exc)` →
  `EvalError("unavailable required object: {what}: {exc}")` — the content-derived refusal.
* `:365-382` `load_source_urls()` wraps the `git ls-tree <tip> -- corpus/SOURCES.md` read and
  re-raises through `required_read`, adding `(tip tree <oid>)` via `root_tree()` (`:266-278`).
  This is the *right* discrimination: an **absent** SOURCES path returns `None` (legacy
  repository), an **unreadable** tree refuses — the audit cannot tell “absent” from
  “cannot be read” when the tree itself is gone.
* `:616-632` `check_history_repo()` — the r23 blanket partial-clone refusal (config /
  `remote.*.promisor` / `.promisor` marker) is **removed** in the candidate; the docstring now
  states that a partial clone is not a refusal.
* `:138-139` `GIT_ISOLATION` keeps `--no-replace-objects --no-lazy-fetch` on every call.
* The tip tree is genuinely **required**: the audit must read the committed
  `corpus/SOURCES.md` blob at the lane tip to classify 40-hex source URLs before scanning the
  report; the path cannot be enumerated without the tree, so exit 2 is the correct
  “required evidence unavailable” verdict, not a guessed absence.

## 8. Findings — fixture / grader level (no source defect)

**F1 (medium, harness coverage gap).** The PG15↔PG16 twin check is vacuous in the grid: both
rows are exit-2 refusals with no verdict document, so `document` is `None`, `twin_equal` is
`None`, and the run reports `twin_compared=0`, `twin_pairs_compared=[]` for this pair. A
twin regression that changed only the refusal *wording* would not be caught by the grid's twin
machinery; only by the per-row `names_any_of`/reason-class checks. The substantive twin evidence
exists only out of band (§4.3). *Minimal suggestion (not applied):* when both partners of a twin
pair are refusals, compare the normalised refusal text instead of the absent document. No
change was made to the grid.

**F2 (low, measurement nuance).** The frozen arm is scored against the amended view with
`names=[]` and `form_check=False` (`promisor-grid.py` `run_case`), so the frozen baseline
counts PG16 as “meeting the amended view” although the r23 message is untyped and does not
name the missing object. The `amended_view_met 1/2` counter therefore overstates the r23
agreement for this family. Nothing is mis-concluded about the candidate itself (the current arm
is scored with the full form/name check and passes).

**F3 (low, expectation granularity).** `names_any_of: ["$tip_tree"]` is satisfied by any refusal
text that merely mentions the tip-tree OID; the row does not check that the refusal is *about*
that object rather than quoting it. In practice the current reason names it as the unavailable
object (`unavailable required object: … (tip tree <oid>)`), so the row is sound here; a stricter
expectation could require the OID to appear in the `unavailable required object:` clause.

**F4 (low, fixture observability).** PG15's promisor remote points at a **nonexistent** path
(`<tmp>/absent-remote.git`, created by `mark_config`), and PG16 has no remote at all. A lazy
fetch could therefore never succeed inside the shipped fixture, so the row as shipped cannot
detect a lazy-fetch regression: it would fail, not fetch, and the audit would still exit 2 for
the right reason. The no-lazy-fetch property of this family is only decidable after replacing
the remote with a servable local one — which I did in §5 (trap live, control fires). *Minimal
suggestion (not applied):* let the LaneTree builder point `remote.origin.url` at a local bare
repository that serves the history, so the row is transport-observable. The same gap applies to
PG16, where no remote exists at all. This is a fixture limitation, not a source defect — the
candidate's isolation holds under the stricter test.

**F5 (informational, no correction proposed).** PG15/PG16 are graded by the `original` view
(no `amended` entry) and the withdrawn preregistration clause (`expected_after[3]`,
unknown-citation ⇒ exit 2) does not apply to them. The withdrawal is therefore not exercised
here and must not be counted as achieved by this family.

## 9. Residual risk / verification gaps

* Only the two assigned rows were executed. The r23 behaviour on other missing-object shapes
  (missing fleet report/tree, missing ancestor, unselected branch, opaque trees) was **not**
  executed — out of this lane's bounded selection.
* The frozen-baseline comparison for this family is limited to the two rows; the r23 base was
  read from the pinned blob `0df800e8…`, never from a working-tree path.
* The trap remote in §5 is a **local bare repository on the local filesystem** (`file`-style
  path, no network). Whether some other environment could make `absent-remote.git` reachable was
  not probed; no network use was permitted and none was attempted.
* The `--keep`ed fixtures of this family were probed exclusively through `--no-lazy-fetch`
  helpers (the hazard reported by `CaseFleetBlobless` for the blobless family does not apply
  here, but the discipline was kept).
* The inherited `git >= 2.45` prerequisite remains open at L0 (git 2.56.0 present locally);
  nothing in this lane changes that disposition.
* The source census / source-ledger supplement (S105 and the rejected S095 cross-API inference)
  is L1-owned after this stage; this lane verified only that the **44 shared expectation rows are
  byte-identical** between the `.ufo` snapshot and the committed table and that the 3 opaque
  cells are additive.

## 10. Verdict summary

* **PG15-missing-lane-tree-promisor** — HOLDS. exit 2, typed `could-not-evaluate:`, content-derived
  reason `unavailable required object: … (tip tree 1c13e47c…)`, no verdict document, 0 objects
  acquired, no transport (measured with a live trap), reason names the unavailable object, no
  metadata wording.
* **PG16-missing-lane-tree-plain** — HOLDS. Identical exit and identical refusal text after path
  normalisation: promisor metadata changed nothing (the no-harm twin property).
* **Source defects in this family: none found.** Fixture/grader observations F1–F5 are reported
  separately above; none invalidates either row, and no production file was edited.

## 11. Files written (all absolute paths under the pinned repo)

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseLaneTree.md` (this report)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseLaneTree/grid-pg15-pg16.json`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseLaneTree/probe-census-and-verdicts.json`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseLaneTree/probe-transport-and-git-calls.json`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseLaneTree/probe_lanetree.py`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseLaneTree/probe2_transport.py`
* scratch/heavy: `/fast/scratch/hyaku/kama-r24/falsify/CaseLaneTree/{repo,work,probe2,out,frozen-audit.py,probe_lanetree.py,probe2_transport.py}`

No tool was installed or updated during this lane; no pacman/uv/cargo/npm transaction was made.

Report: .ufo/waves/round-24/falsify/advice/CaseLaneTree.md

## 12. Cross-reference with `CaseFleetBlobless` (appended, append-only)

`CaseFleetBlobless` (PG43) reports the same fixture hazard from the blobless side: a probe
without `--no-lazy-fetch` materialises the missing object and voids the premise, turning an
exit-2 refusal into a false exit 0. Its A8 and my F4 are the two halves of one statement, and
they are complementary:

* Their hazard is **probe-side**: a stray manual probe in a `--keep`ed fixture can destroy the
  premise the row is supposed to measure. My §5 is **auditor-side**: with a live, servable
  origin the pinned auditor still refuses (exit 2), acquires nothing in the audited store *or*
  in the origin, and leaves the object missing; only the explicit omission of
  `--no-lazy-fetch` makes the object materialise. Together these place the hazard strictly
  probe-/fixture-side; the graded path (the grid's own `run_auditor`, which always isolates)
  is unaffected.

* Sharpening of their note (2): the grid's no-acquisition pin
  (`tests/report-audit/promisor-grid.py:808-810`, with the before/after inventory at
  `:822-826`) compares the **object inventories of the audited lane and fleet stores only**. It
  therefore cannot see (a) a transport *attempt* that fails, (b) a fetch that lands in the
  *origin* repository, or (c) a fetch performed by any probe outside the grader. In the shipped
  LaneTree fixture the origin is the nonexistent `absent-remote.git` path, so (a) and (b) are
  unobservable by construction. My bait-origin rebuild closes the observable half: the origin's
  inventory was also unchanged (`objects_acquired_remote = []`), and the trap did fire when the
  isolation was removed (control in §5), so the pinned auditor's no-fetch behaviour is a
  measurement, not an artifact of a dead remote.

* Scope note for the shared record: my bait-origin test is a **local rebuild of the fixture in
  scratch**, not a change to the shipped builder, and it exercises the *source* transport
  behaviour, not a new expectation cell. No expectation cell, builder or expectation was edited
  in production by this lane, and the PG15/PG16 verdicts are unchanged (HOLDS). The suggestion
  that a repointed bait origin be added to the A/B-class builders (PG15/16/19/20/28/43) is
  recorded as a fixture-level proposal owned by L1, not applied here.


Report: .ufo/waves/round-24/falsify/advice/CaseLaneTree.md

## 13. Family-specific closure of the harness fetch-capability question (appended)

`CaseFleetBlobless` F1 identified the harness helper `promisor-grid.py` `git()` (≈:99-104) as
fetch-capable (no `--no-lazy-fetch`, no timeout). I tested whether that latent capability can
void **this** family's premise, with a live origin instead of the shipped nonexistent path.

Method (`probe3_grid_premise.py`, scratch only; the harness was used unmodified except for a
monkey-patched `mark_config` in the probe process that repoints `remote.origin.url` at a local
bare repository that really serves the lane history):

* the grid's own `c_missing_lane_tree_promisor` builder ran to completion against that live
  origin;
* result: `premise_lane_missing = ['1c13e47ce9f8088dc933a80123cf6a8ee2fa701d']`,
  `tip_tree_present_in_lane_after_build = false`, 4 objects in the lane, origin serving the tree;
* the auditor on that live-origin fixture: **exit 2**, stdout empty, reason still
  `unavailable required object: … (tip tree 1c13e47c…)`, `objects_acquired_lane = []`,
  `objects_acquired_origin = []`, tree still missing.

Finding (F4 refinement, fixture level): for the LaneTree family the harness's fetch-capable
helper is **latent and not exercised** — every post-drop object read in `build()` goes through
`git_nofetch` / `object_exists` / `object_inventory`, and the pre-drop reads happen while the
object is still present. The premise survives a live origin, and the auditor still refuses
without acquiring anything. PG16 has no promisor configuration at all, so no lazy-fetch path
exists in that fixture. This does not change the shipped-fixture observability gap recorded in
F4 (the `absent-remote.git` URL still makes the transport level unobservable in the shipped
form); it establishes that the gap is an observability limitation, **not** a premise-integrity
defect for this family, and that the hazard `CaseFleetBlobless` measured for PG43 does not
generalise to PG15/PG16 without an out-of-grader probe. No production file was edited.


Report: .ufo/waves/round-24/falsify/advice/CaseLaneTree.md

## 14. Corroboration from `CaseFleetBlobless` A12 (appended)

`CaseFleetBlobless` A12 reaches the same conclusion for the blobless family **natively**, without
the monkey-patch my §13 needed: `blobless_clone()` leaves `remote.origin.url` pointing at a
reachable local bare repository, so the grid's own premise machinery already runs against a live
origin — and after the grid's own current-arm run the PG43 premise was intact (fleet inventory
7 objects; `rev-list --objects --missing=print HEAD` still listing both holes `?0cf7ed5c…` and
`?bfa65511…`; exactly one promisor pack; no `FETCH_HEAD`; no loose object) with the correct
exit 2. The materialisation in their A/B came only from an out-of-grader probe, never from the
grid. For PG43 the fetch-capable helper (`promisor-grid.py:99-104`) is therefore latent too, and
the hazard is an observability/discipline gap (their A5) rather than a premise-integrity defect
in the graded path — the same refined F4 this lane landed for PG15/PG16, obtained natively
rather than by patch. Two independent routes, one conclusion: no source defect, graded path
intact, both verdicts HOLDS.


Report: .ufo/waves/round-24/falsify/advice/CaseLaneTree.md
