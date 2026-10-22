# CaseCrossRepo — independent falsification of the PG26/PG27 fixture family

Lane: CaseCrossRepo (round 24, fresh falsification). Leaf member: no subagents
dispatched, no production file edited, no full suite re-run.

**Verdict: HOLDS for the graded family** (both cells meet the live amended
view; the marked/unmarked twin pair is byte-identical; no objects acquired; no
transport). **One fixture/harness defect found, in the runner's JSON summary
only** (misleading `amended_view_met` for the current arm — grading is
unaffected). **No source defect found in the audited source for this family.**

---

## 1. Pins observed (read-only, scratch only)

| item | value |
|---|---|
| scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/CaseCrossRepo` (`git clone --no-hardlinks` of `/home/vgpnk/Projects/shokunin/kama-shokunin`) |
| checked-out base | detached `2e254a1763a9c08aa07fc53081287f506c447d84` (clean tree; production `HEAD` identical) |
| git | 2.56.0 |
| auditor (current) | `tools/report-landing-audit.py` sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| runner | `tests/report-audit/promisor-grid.py` sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` |
| manifest | `tests/report-audit/promisor-grid-expectations.json` sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` |
| frozen auditor blob | `0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py` sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` |
| grid `expectations_sha256` | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (identical to the manifest bytes) |
| grid `population_sha256` | `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` (identical to the value filed by the L1/GridOracle) |

Scratch/temp for every subprocess: `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseCrossRepo/tmp`.
No change to production `.jj/index`, fleet, siblings, routing, services or any
real object store. No tool installed or updated.

---

## 2. The bounded selection I was assigned

```
cd /fast/scratch/hyaku/kama-r24/falsify/CaseCrossRepo && \
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseCrossRepo/tmp \
python3 tests/report-audit/promisor-grid.py --arm both \
  --case PG26-cross-repo-found-promisor --case PG27-cross-repo-found-plain --json
```

**exit 0**, stderr empty. (Re-run with `--keep --out` to retain the fixtures:
exit 0, grid root `/fast/scratch/hyaku/kama-r24/falsify/CaseCrossRepo/tmp/promisor-grid-7hjz49nm`.)

### Exact observed rows

| arm | case | exit | findings (kind, token) | met (its view) | objects acquired | traceback/timeout/leak |
|---|---|---|---|---|---|---|
| current | PG26-cross-repo-found-promisor | **0** | `[]` (raw `[]`, kinds `[]`) | `met_amended=true`, `met_original=true` | lane `[]`, fleet `[]` | none |
| current | PG27-cross-repo-found-plain | **0** | `[]` (raw `[]`, kinds `[]`) | `met_amended=true`, `met_original=true` | lane `[]`, fleet `[]` | none |
| frozen (r23 base) | PG26-cross-repo-found-promisor | **2** | no document; stderr `could-not-evaluate: …/lane: partial clone (remote.origin.promisor)` | `met_frozen=true`, `met_amended_frozen=false` | lane `[]`, fleet `[]` | none |
| frozen (r23 base) | PG27-cross-repo-found-plain | **0** | `[]` | `met_frozen=true`, `met_amended_frozen=true` | lane `[]`, fleet `[]` | none |

Current arm: `violations=0`, `violating_cases=[]`, `twin_mismatch=[]`,
`twin_pairs_compared=["PG26-cross-repo-found-promisor"]`, `tracebacks=0`,
`timeouts=0`, `harness_leaks=0`, `withdrawn_original_failures=[]`.
Frozen arm: `violations=0`, `amended_view_met=1/2`,
`amended_view_unmet=["PG26-cross-repo-found-promisor"]` — the retained r23
blanket-refusal baseline.

**Withdrawn-expectation visibility.** For this family the *original* view and
the *amended* view are identical (both `exit 0, kinds [], defects []`); the
manifest rows for PG26 and PG27 are **byte-identical** to
`.ufo/waves/round-24/oracle-snapshot-before-inspection.json` (verified
field-by-field, §5). No expectation was withdrawn, relabelled or rewritten in
this family, and `withdrawn_original_failures` is empty — correctly. The
*frozen* (r23 base) expectation `exit 2 / reason_class=metadata` is retained in
the manifest and is still observable in the frozen arm above; it is historical
behaviour, never counted as achieved. No withdrawn-failed expectation is being
hidden here.

---

## 3. Premises asserted independently of the harness

Read directly from the kept fixture (`current/000` = PG26, `current/001` =
PG27):

* lane config: `remote.origin.promisor=true`, `extensions.partialclone=origin`,
  `remote.origin.url=<grid>/current/000/absent-remote.git` — **that path does
  not exist** (no network target, no local remote).
* fleet config: no promisor key at all (the twin differs from PG26 in exactly
  this one respect; every commit, tree and the report are identical).
* lane history: one commit `58866b56…` (`round-1: work`, author
  `kama-shokunin`, t=1000). Fleet history: `f723c76c…` (`fleet: init`,
  author `fleet`, t=1900) and `42153ed9…` (`round-1: report`, t=2000).
* report `.ufo/reports/round-1/kama.md` cites **both** the lane commit and
  `f723c76c41609df00704d93c29bd44408dcbdd2e`.
* `f723c76c…` **absent** in the lane (`cat-file -e --no-lazy-fetch
  --no-replace-objects` → no), **present** in the fleet (type `commit`).
* **no missing objects**: lane `rev-list --objects --missing=print
  refs/heads/master` → none; fleet over `HEAD` → none. Both stores are
  locally complete; the lane's promisor marking is metadata only.
* the fabricated token `0123456789abcdef0123456789abcdef01234567` is absent
  from both stores.

So the premise of both cells is exactly what the manifest claims: *the
citation exists only in the second audited repository, and the lane is
promisor-marked yet complete*.

## 4. Twin comparison and no-acquisition, re-measured outside the harness

I re-ran the candidate auditor myself against the two kept fixtures
(`--rounds 1 --json --no-errata`), rather than trusting the harness's own
comparison:

* exit 0 on both; stderr empty; `summary.status="clean"`; every
  `by_kind` counter 0; `results[0]` = `{round 1, cutoff 2000, required 1,
  round_commits 1, post_report [], report_committed true, source_url_hashes []}`.
* **normalized twin documents equal: True** (lane/fleet paths replaced by
  `<lane>`/`<fleet>`; the harness reports `twins={"PG27-…": true}`,
  `twin_equal=true`).
* object inventory (`cat-file --batch-all-objects | sha256`) **before == after**
  in both stores of both cells:
  lane `1d84dbc08c7c27f95bb923b813ab7880f6bba568f7492c29afe5332b61313800`,
  fleet `6b74174dd26f6e775aa0bd68cc9a05a74e80a2aa269c86b384762c6525796a65`.
  Nothing was acquired.
* **transport trap**: on a copy of the PG26 fixture I set
  `remote.origin.uploadpack` to a marker-writing script. Auditor exit 0,
  clean, **marker not created** → the promisor remote was never contacted.
  (Consistent with the source: every git call carries
  (`--no-lazy-fetch --no-replace-objects`, `tools/report-landing-audit.py:138-141`).

## 5. The cells are not vacuous (bounded non-vacuity probe)

The risk with this family is that the fixture passes for the wrong reason (the
cross-repository citation never has to be resolved). I checked this with one
bounded probe on a **scratch copy** of the auditor (production untouched):
the `PM05-ignore-second-repo` mutation, `for store in stores:` →
`for store in stores[:1]:` in `lookup()`.

* PG26 fixture → **exit 1**, `status failed`, findings exactly
  `('unresolved-full-hash','f723c76c41609df00704d93c29bd44408dcbdd2e')` and
  `('landed-unresolved','f723c76c41609df00704d93c29bd44408dcbdd2e')`.
* PG27 fixture → **exit 1**, `status failed`, the identical two pairs.

The cross-repository citation is therefore load-bearing in both cells: a
candidate that consults only the first audited repository fails them loudly
instead of passing vacuously. This also confirms that the integrated runner
`b034e159…` really contains GridOracle's cross-repository fixture repair
(`build()` appends the fleet's own commit to the report's Landed section and
asserts the premise) — that repair is what makes PG26/PG27 discriminate at
all; before it, `cross_repo=True` was accepted and never read.

Manifest integrity for this family: the PG26/PG27 manifest rows are
**byte-identical** to the pre-inspection oracle snapshot rows, and all 44
snapshot rows are present unchanged in the 47-cell manifest (the 3 extra cells
are `PG46/PG47/PG48`, the independent opaque-tree supplement). No expected
cell was changed to make the fixture fit the candidate.

---

## 6. Findings

### Fixture / harness flaws (separate from source flaws)

**F1 — MEDIUM (reporting only, no effect on grading): the current arm's
`amended_view_met` counter is structurally always 0.**
`tests/report-audit/promisor-grid.py:1031-1042`:

```python
baseline = [r for r in graded
            if r["arm"] == "frozen" and r["met_amended_frozen"]]
doc["arms"][arm] = {…
    "amended_view_met": len(baseline),
    "amended_view_total": len(graded),
    "amended_view_unmet": sorted(r["case"] for r in graded
        if r["arm"] == "frozen" and not r["met_amended_frozen"]), …}
```

`baseline` selects only frozen-arm rows, but the counter is written into
**every** arm's summary. The current arm therefore always reports
`"amended_view_met": 0` with `"amended_view_total": 2` — which reads as
"0 of 2 rows met the amended view" — while `violations=0` and
`violating_cases=[]` correctly say the opposite. In my run the current arm
printed `amended_view_met: 0, amended_view_total: 2, amended_view_unmet: []`.
A reader (L1 or a downstream summary) can easily read that pair as a failure.
Minimal correction (no expectation touched): score the count per arm, e.g.

```python
met = ([r for r in graded if r["met_amended"]] if arm == "current"
       else [r for r in graded if r["met_amended_frozen"]])
"amended_view_met": len(met),
"amended_view_unmet": sorted(r["case"] for r in graded if r not in met),
```

The same defect is present in the GridOracle out copy
(`build/out/GridOracle/promisor-grid.py`, sha256 `5e96fa60…`), so it is not a
composition artefact of the L1's integration. Grading itself is unaffected:
`live_fail`/`frozen_fail` use `met_amended`/`met_frozen` per row.

**F2 — LOW (fixture realism, disclosed): the cross-repository device is a
fleet commit cited in the report's "## Landed changes" section.**
`build()` appends the fleet's own `fleet: init` commit to the Landed list, so
that the citation can only be resolved by consulting the second audited
repository. A real kama report lists *lane* commits in that section, so the
fixture report is not shaped like a production report. It is disclosed in
`build/advice/GridOracle.md:356-363` and it is sufficient (PM05 bites, §5),
but a reader must not take the fixture report as a realistic report shape.

**F3 — LOW (harness, informational): `reason_forbidden` on PG26 lists only the
two r23 phrases** (`"partial clone ("`, `"promisor pack"`), and the row has no
`names_any_of`. That combination is *stricter*, not weaker: with an empty
`names` list, `check_exit2_form`'s "reason does not name the unavailable
object" test can never be satisfied, so **any** current-arm refusal of PG26
would be flagged. No change proposed; recorded because it also means the
"content-derived reason" contract is not *exercised* by this family (see
gaps).

**F4 — INFORMATIONAL, outside this lane: the GridOracle RECEIPT's summary
table is stale.** `build/out/GridOracle/RECEIPT.md:11` still lists the runner
as `d6aa4e74…` (46189 B) "final, frozen", while the committed out copy is
`5e96fa60…` (47480 B) and the integrated runner is `b034e159…` (46583 B). The
later sections of the same append-only receipt (lines 96-97, 134-149) disclose
the move and the L1's composition. No action proposed; provenance only.

### Source flaws (the audited source: `tools/report-landing-audit.py`)

**None found for this family.** The behaviour PG26/PG27 assert is implemented
by exactly the intended mechanism: `run()` builds both stores
(`tools/report-landing-audit.py:765-766`, `build_store(lane_repo, tip)` and
`build_store(fleet_repo, fleet_tip)`), and `lookup()` iterates **all** stores
(`for store in stores:` at `tools/report-landing-audit.py:211`) merging the
statuses by `RANK` (`absent < wrongtype < unknown < ambiguous < found`). The
cross-repository citation is a plain `found` in the fleet, so the Landed
section yields no finding, `refuse_unknown()` is not reached, and the run ends
clean. Promisor metadata has no path into any verdict: the only occurrences
of "promisor" in the tool are the module docstring (lines 57-65), a comment
(lines 134-136, 660) and the selftest (lines 1176-1195) — there is no
metadata-based refusal branch left to trip. No content-derived-reason path is
involved in a clean verdict, so none is claimed here.

---

## 7. Residual risk and verification gaps

* **Not exercised by this family:** the content-derived **reason ID** contract.
  PG26/PG27 expect a clean verdict, so no refusal reason is produced and
  `check_exit2_form`'s "the reason names the unavailable object" clause is
  never run for these two rows. The reason-class/ID contract is exercised by
  other cells (unavailable-object rows), which are outside my assignment and
  were **not** re-run by me.
* The frozen arm's `twin_equal` is `null` for both rows because PG26's frozen
  run exits 2 with no verdict document; a frozen-arm twin comparison is
  therefore impossible for this pair (there is no document to compare). Not a
  defect, but it means "the twins compare equal" is a current-arm-only fact.
* I did **not** re-run the full 47-cell grid, the mutation suite, the
  selftest, the historical-parity check, or any other cell; my measurement is
  the two assigned cells plus their fixtures.
* The inherited `git >= 2.45` floor (the floor the frozen base already
  documented) remains open at L0 and is not addressed by this lane; the host
  here has git 2.56.0, so the `--no-lazy-fetch`/`--missing=print` primitives
  were available in this measurement.
* The PM05 probe is a **single** mutation on a scratch copy of the auditor
  (`tools/report-landing-audit.py` in the scratch clone). It demonstrates that
  the cross-repository citation is load-bearing; it is not a mutation-coverage
  claim for the whole family or the tool.
* **Peer-reported fixture hazard, checked and found not to reach this family**
  (`KamaR23-2.CaseFleetBlobless`, PG43 lane): a *blobless* clone keeps a
  reachable `file://` origin, so any probe **without** `--no-lazy-fetch`
  materialises the missing blobs and the premise silently evaporates (their
  A/B: blob absent → exit 2 content-derived refusal; blob materialised by one
  stray `git cat-file -e HEAD:<path>` → exit 0 "clean"). PG26/PG27 are not
  blobless clones: `mark_config()` writes only promisor **config** plus
  `remote.origin.url=<grid>/current/00N/absent-remote.git`, a path that does
  not exist, and the lane is object-complete (`--missing=print` → none in
  both stores), so there is no missing object a lazy fetch could be asked for.
  Every probe I ran carried `--no-lazy-fetch` (presence checks:
  `cat-file -e --no-lazy-fetch --no-replace-objects`; inventory:
  `cat-file --batch-all-objects`); the only object reads without that flag
  were `git log --all`/`rev-parse` on the lane and `cat-file -t` on the
  *unmarked* fleet, all over complete histories. Independent proof of
  non-materialisation: the object-inventory digest was identical before and
  after every auditor run (lane `1d84dbc0…`, fleet `6b74174d…`). The hazard
  is a **manual-inspection hazard for `--keep`ed blobless fixtures**, not a
  source defect; no source defect was found in the audited source for this
  family. Flagged here so the next reader of a `--keep`ed fixture in this
  family repeats the `--no-lazy-fetch` discipline.

## 8. Files written and unverified items

Written (all under the round-24 falsify area, append-only, production
untouched):
* `.ufo/waves/round-24/falsify/advice/CaseCrossRepo.md` (this report)
* `.ufo/waves/round-24/falsify/out/CaseCrossRepo/grid-both-arms-pg26-pg27.json`
* `.ufo/waves/round-24/falsify/out/CaseCrossRepo/grid-both-arms-pg26-pg27-keep.json`
* `.ufo/waves/round-24/falsify/out/CaseCrossRepo/independent-pg26-verdict.json`
* `.ufo/waves/round-24/falsify/out/CaseCrossRepo/independent-pg27-verdict.json`
* `.ufo/waves/round-24/falsify/out/CaseCrossRepo/pm05-mutant-pg26.json`
* `.ufo/waves/round-24/falsify/out/CaseCrossRepo/pm05-mutant-pg27.json`
* `.ufo/waves/round-24/falsify/out/CaseCrossRepo/fixture-verification.txt`

Scratch only (outside the repo): the clone and its Git metadata at
`/fast/scratch/hyaku/kama-r24/falsify/CaseCrossRepo`, the kept grid root
`…/tmp/promisor-grid-7hjz49nm`, the mutated auditor copy at
`…/mutant/audit-pm05.py` and the transport-trap copy at `…/trap/`.

Unverified: the other 45 cells; the reason-class/ID contract; the mutation
suite; historical parity; the source census; the inherited `git >= 2.45`
operator disposition. No score increase, serving capability, admission,
integration or shipping judgement is asserted, and nothing was edited in
production.

Report: .ufo/waves/round-24/falsify/advice/CaseCrossRepo.md
