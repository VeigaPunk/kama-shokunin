# CaseOpaquePositive — PG48-opaque-unused-tree-no-unresolved-token

**Verdict: HOLDS (amended view), with two fixture/inventory defects reported separately.**

The amended local-object contract is met by the pinned candidate: PG48 is exit 0, no
findings, no verdict deviation, no object acquisition, and the verdict document is
byte-identical to both the unmarked twin and the complete twin. The exit 0 is
discriminating, not vacuous: it is killed by an eager blanket-closure precondition,
and it is refused (exit 2, content-derived) as soon as a citation is actually
unresolved or as soon as the missing subtree is actually required.

Two defects are in the **fixture/inventory layer**, not the source layer. One is a
real gap in mutation coverage accounting (PM11's `expect_rows` names PG48, but the
mutant does not fail PG48, and the runner's `attributed` check cannot see it). The
other is a reporting-key defect in the grid's own summary counters that makes the
current arm look like it met 0 of 1 amended rows when it met 1 of 1.

---

## 1. Scope and pinned base

| Item | Value |
|---|---|
| Pinned commit | `2e254a1763a9c08aa07fc53081287f506c447d84` (detached in scratch clone) |
| Scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/repo` (`--no-hardlinks` from `/home/vgpnk/Projects/shokunin/kama-shokunin`) |
| Scratch base observed | `git rev-parse HEAD` → `2e254a1763a9c08aa07fc53081287f506c447d84`; `git status --porcelain` empty at checkout |
| `tools/report-landing-audit.py` | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` (matches the pinned source tool) |
| `tests/report-audit/promisor-grid.py` | sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` (matches the pinned runner) |
| `tests/report-audit/promisor-grid-expectations.json` | sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (matches the pinned manifest) |
| `tests/report-audit/promisor-mutants.py` | sha256 `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` (matches the pinned mutation probe) |
| Population | 47 cases; `population_sha256` `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` |
| Grid root / TMPDIR | `/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/tmp` (per-subprocess `TMPDIR` set) |
| Production tree | **not modified** — `sha256sum tools/report-landing-audit.py` in `/home/vgpnk/Projects/shokunin/kama-shokunin` still `ea51bc35…`; only `.ufo/waves/round-24/falsify/{advice,out}/CaseOpaquePositive*` were written |

No tool was installed or updated. No network, no transport, no execution payload.
PM08 was **not** executed (static-only); no PM08 probe was run.

---

## 2. The assigned bounded measurement

```
cd /fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/repo
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/tmp \
  python3 tests/report-audit/promisor-grid.py --arm both \
  --case PG48-opaque-unused-tree-no-unresolved-token --json
```

**Exit 0.** Repeat runs ×3: exit 0, 0, 0 — deterministic.

### Frozen arm (r23 base `0df800e8…`, history — never a target)

- exit **2**, `met_frozen = true`
- stderr: `could-not-evaluate: …/frozen/000/lane: partial clone (remote.origin.promisor)`
- `objects_acquired`: lane `[]`, fleet `[]`
- `met_amended_frozen = false` → correctly listed in `amended_view_unmet`. This is the
  r23 blanket metadata refusal, i.e. the defect being repaired. **The frozen arm's
  `met_frozen = true` is history, not improvement.**

### Current arm (pinned candidate `ea51bc35…`)

- exit **0**, `met_amended = true`, `met_original = true`
- `defects = []`, `raw_defects = []`, `kinds = []`, `raw_kinds = []`
- `stderr_tail` empty; stdout carries the verdict document
- `objects_acquired`: lane `[]`, fleet `[]`
- `tracebacks = 0`, `timeouts = 0`, `harness_leaks = 0`
- `violations = 0`, `violating_cases = []`
- `withdrawn_original_failures = []`

**Verdict document (exact, from `grid-pg48.json`):**

```json
{"summary": {"by_kind": {"landed-ambiguous": 0, "landed-omitted": 0,
                         "landed-section-missing": 0, "landed-unresolved": 0,
                         "unresolved-full-hash": 0},
             "corrected": 0, "defects": 0, "errata_invalid": 0,
             "errata_unmatched": 0, "errata_rows": 0, "post_report_commits": 0,
             "reports": 1, "required_commits": 1, "rounds": [1],
             "status": "clean", "uncorrected": 0},
 "results": [{"cutoff": 2000, "defects": [], "post_report": [],
              "report": "<fleet>/.ufo/reports/round-1/kama.md",
              "report_committed": true, "required": 1, "round": 1,
              "round_commits": 1, "source_url_hashes": []}]}
```

**Exact finding/token pairs: none.** The amended expectation for PG48 is
`exit 0, kinds [], reason_class null, defects []`; observed `defects []`, `kinds []`.
There is no finding/token pair to report — that *is* the finding: zero findings.

---

## 3. Premise asserted against the actual objects (not inferred)

The grid's own premise machinery reports `lane_missing: ["2a675c1af91c97c51f5101d6cff10bb797458ab6"]`.
I verified this against the real store rather than trusting the summary.

From `auditor-machinery.json` (the shipped auditor module imported and interrogated directly):

| Fact | Observed |
|---|---|
| Missing subtree oid | `2a675c1af91c97c51f5101d6cff10bb797458ab6` |
| `missing_subtree_present_in_store` | **false** (`cat-file -e` → absent) |
| Lane commit `18089c6071793e8be726676c30371c68a837ca48` present | true |
| Tip tree present | true |
| `f` blob present | true |
| `corpus/SOURCES.md` blob present | true |
| Lane store object count | 6 (3 blob, 1 commit, 2 tree) |
| Fleet store object count | 9, `fleet_missing = []` |
| `lane_missing` (auditor's own `missing_reachable`) | `[2a675c1a…]` |
| `lane_opaque` (auditor's own opaque subset) | `[2a675c1a…]` |
| Tip tree really references the missing subtree | **true** — `ls-tree` of the lane commit lists `040000 tree 2a675c1af91c97c51f5101d6cff10bb797458ab6\td` |
| `opaque_hole()` | returns the lane store and oid `2a675c1a…` |
| `lookup()` of the cited lane commit | `{"18089c60…": "found"}` |
| `fake_present` (fabricated token in store) | false |

So the premise is real: the tip tree genuinely points at an absent subtree; the
subtree genuinely is absent; and every cited token genuinely resolves locally.
**Observed, not inferred.**

---

## 4. Twin document comparison

The manifest leaves `PG48.twin = null` (unlike PG01↔PG07 etc.), so the grid performs
**no** twin comparison for this row (`twin_pairs_in_manifest: 0`, `twin_compared: 0`).
I performed the comparison the supplement's wording implies ("same correct clean
twin verdict") by building both twins independently:

| Twin | Construction | exit | defects | Document identical to PG48? |
|---|---|---|---|---|
| **A — graded fixture** | `c_opaque_unused_tree_clean` (promisor config + missing `d/` subtree) | 0 | `[]` | — |
| **B — unmarked twin** | same fixture, **no** promisor metadata (`lane_promisor: false`) | 0 | `[]` | **yes** (`twin_B_document_equal: true`) |
| **C — complete twin** | same fixture, the `d/` subtree **present** (`lane_missing: []`) | 0 | `[]` | **yes** (`twin_C_document_equal: true`) |

`C` was compared field by field: `twin_C_field_diff: []` — every field of the
normalised document matches, not merely the exit code. This is the substantive
"promisor metadata alone never changes the verdict" and "an unrelated hole does not
block" property, verified on PG48 with actual document comparison rather than exit
comparison alone.

---

## 5. Discriminating power — the exit 0 is not vacuous

A fixture that passes for the wrong reason is the main risk for a positive cell.
Three controls, each on a locally rebuilt fixture:

### 5a. Negative control — same fixture + one unresolved fabricated token
`build(lane_mark="config", opaque_tree=True, fake_notes=True, drop=("opaque_tree",))`

```
exit 2
could-not-evaluate: round 1: unknown: unavailable required object:
0123456789abcdef0123456789abcdef01234567 could be hidden behind the missing
tree or commit 2a675c1af91c97c51f5101d6cff10bb797458ab6 in …/lane
```

- content-derived: names **both** the unresolved token and the opaque hole
- `reason_is_metadata_refusal: false`
- `reason_names_missing_tree: true`, `reason_names_fake_token: true`
- no JSON verdict document on stdout
- `objects_acquired`: lane `[]`, fleet `[]`

This is the amendment's rule in action: the same missing subtree that is harmless
in PG48 becomes decisive once a citation is actually unresolved.

### 5b. Required-hole complement — the missing tree is one the audit *does* read
Same fixture shape, but the dropped subtree is `corpus/` (which holds
`corpus/SOURCES.md`, a required read) instead of the unused `d/`:

```
exit 2
could-not-evaluate: unavailable required object:
53764ec1c1af39f576092693c6630dc25ee84805:corpus/SOURCES.md
(tip tree 85b3b6d151c1b3bd56dde91103562d48eca6700a) in …/lane:
git ls-tree … rc=1 error: Could not read 04c318ea5a25ff98d94c479933d412eee748d0d9
```

- `reason_names_missing_tree: true`, `reason_is_metadata_refusal: false`
- `reason_class_unavailable: true`
- control with nothing dropped: exit 0, `status: "clean"`

So PG48's exit 0 is a consequence of the hole being genuinely unused, not of the
auditor being blind to holes.

### 5c. Eager blanket-closure precondition — PG48 *does* kill it
To test whether PG48 can detect the forbidden behaviour itself, I applied a probe
mutation to a **scratch copy** of the auditor (production untouched) that computes the
hole set eagerly for every audited store and refuses whenever any hole exists:

```
grid_exit 1, mutated_exit 2, mutated_met_amended false
violating_cases: ["PG48-opaque-unused-tree-no-unresolved-token"]
stderr: could-not-evaluate: …/lane: unknown: unavailable required object:
        2 hole(s) in the store
grader problems: ["exit 2 != 0", "reason does not name the unavailable object"]
```

PG48 kills the eager blanket-precondition mutant. It has genuine discriminating
power against exactly the prohibition the amendment states ("Never use any
missing-object state as an unconditional audit precondition").

---

## 6. No acquisition, no transport

The git-call trace of the graded fixture was captured with a logging `PATH` shim
(22 calls). Every call carries the isolation flags:

```
--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8
-c log.follow=false -c log.showRoot=true -c log.showSignature=false
-c log.mailmap=false
```

- `calls_naming_missing_oid`: **[]** — the missing subtree is never even named on
  the wire, let alone fetched
- `calls_with_transport`: **[]** (verb filter `fetch|pull|clone|remote|upload-pack|ls-remote|http|ssh` → 0 hits over 22 calls)
- `objects_acquired`: lane `[]`, fleet `[]` (independent before/after
  `--batch-all-objects` inventory, from both the grid and my own probe)

**Lazy-fetch hazard, checked explicitly** (a sibling lane reported a hazard where a
non-isolated probe materialises a missing blob in a file:// blobless clone): PG48's
lane is *config*-marked with `remote.origin.url` pointing at a path that does not
exist. An **unisolated** `git cat-file -e` on the missing subtree fails with
`fatal: '…/absent-remote.git' does not appear to be a git repository` and the hole
**survives** (`hole_survives_unisolated_probe: true`). So the hazard does not apply
to this fixture family, and my probes were `--no-lazy-fetch`-isolated throughout.

---

## 7. Expectation integrity — no retrofitting of the expected cells

| Check | Result |
|---|---|
| The 44 original snapshot cases vs the shipped table | **byte-identical** (per-case JSON comparison, 0 differences) |
| Shipped table minus the 44 snapshot cases | exactly `PG46`, `PG47`, `PG48` — the three independent opaque cells |
| Pre-candidate build artifact `build/out/GridOracle/promisor-grid-expectations.json` (47 cases) vs shipped table (47 cases) | **0 differences** — no expected cell was edited to fit the candidate |
| `oracle-snapshot-before-inspection.json` `amended_rows` vs shipped `amended` | all 7 rows match; `PG37` is `null` in both (still an open row, not silently filled) |
| Chronology | snapshot frozen `f66b226` 15:04:12 → supplement `aacbd520` 15:12:55 → candidate `ed1cc3a` 15:14:18 → integration `2e254a1` 16:45:11. The supplement **precedes** the candidate |
| `population_size` | 47 = original 44 + 3 independent opaque cells ✔ |

**The withdrawn original expectation stays visible.** PG48's `original` view is
`exit 0` — identical to `amended` for this row, because PG48 has no unresolved
citation at all (its whole point). The withdrawal of `expected_after[3]` therefore
bites only on the seven rows the amendment enumerates (PG22, PG23, PG24, PG28,
PG30, PG34, PG41); PG48 is not one of them and is **not** relabelled passed from a
withdrawn row. `withdrawn_original_failures = []` because PG48 satisfies both
views, not because a failure was reclassified.

---

## 8. Findings

### F-1 (fixture/inventory, medium) — PM11's `expect_rows` names PG48, but the mutant does not fail PG48

`tests/report-audit/promisor-mutants.py` registers PM11-any-hole-refusal with
`expect_rows` including `"PG48"`. PM11 patches `RepoStore.missing` to raise whenever
the store reports any hole. On PG48 the candidate **never consults the hole set**:
every citation resolves, so `refuse_unknown` takes no hole branch and
`store.missing()` is never called.

Verified two ways:

- Reproducing the shipped PM11 mutation on a scratch copy and re-running only PG48:
  `mutated_exit 0`, `mutated_met_amended true`, `PG48_kills_PM11: false`.
- The build wave's own record
  `.ufo/waves/round-24/build/out/MutationOracle/sensitivity-promisor-grid.json` shows
  PM11 `killed=True` but `failed_rows` =
  `[PG22, PG33, PG34, PG37, PG41, PG42, PG47]` — **PG48 is not among them**, despite
  being in `expect_rows`.

The runner's attribution check is `all(expected_match(f, expected) for f in failed)` —
it verifies that every *failed* row is in `expect_rows`, but never that every row in
`expect_rows` actually fails. So the over-broad declaration is invisible to the
runner and is credited as `attributed: true`.

**Minimal correction (do not apply without L1):** PM11's `expect_rows` should drop
`PG48` (and re-check the other listed rows), or PG48 should be given its own mutant
whose over-refusal fires on the eager path — which §5c proves already kills PG48.

**No source defect.** The candidate's behaviour is correct: PG48 is a positive cell
whose premise (no unresolved token) means the hole is never relevant, and the eager
probe confirms the cell still kills a genuine blanket precondition.

### F-2 (grid reporting, medium) — the current arm's `amended_view_*` counters are computed from a frozen-arm-only filter

In `promisor-grid.py` `main()`:

```python
baseline = [r for r in graded if r["arm"] == "frozen" and r["met_amended_frozen"]]
doc["arms"][arm] = {
    ...
    "amended_view_met": len(baseline),
    "amended_view_total": len(graded),
    "amended_view_unmet": sorted(r["case"] for r in graded
                                 if r["arm"] == "frozen" and not r["met_amended_frozen"]),
```

Both filters test `r["arm"] == "frozen"`. When `arm == "current"` no row satisfies
it, so on the current arm `amended_view_met` is **always 0** and `amended_view_unmet`
is **always `[]`** — regardless of how many current rows actually met the amended
view. Observed on the assigned run:

```
current arm: amended_view_met 0, amended_view_total 1, amended_view_unmet []
             violations 0, violating_cases [], per-row met_amended true
```

Read literally, the current arm "met 0 of 1 amended rows" while the same row
reports `met_amended: true` and the arm reports 0 violations. A consumer reading
`amended_view_met`/`amended_view_unmet` for the current arm is reading a
structurally-empty field. The authoritative per-row `met_amended` and the arm's
`violations`/`violating_cases` are correct and are what the PG48 verdict above rests
on.

**Minimal correction (do not apply without L1):** compute the current arm's counters
from `r["arm"] == "current"` and `r["met_amended"]` (and keep the frozen-arm
baseline separate), e.g. report `amended_view_met`/`amended_view_unmet` per arm from
that arm's own rows.

This is a reporting/honesty defect in the grid's summary, not a grading defect —
`violations` and `violating_cases` are computed correctly and independently of
these counters.

### F-3 (fixture, low) — PG48 has no declared twin, so the manifest's twin machinery covers none of the three opaque cells

`PG46.twin`, `PG47.twin`, `PG48.twin` are all `null`, and no other case declares
PG48 as a twin. The grid therefore performs zero twin document comparisons for the
entire opaque family (`twin_pairs_in_manifest: 0`, `twin_compared: 0` on the
assigned run) even though the supplement's wording for PG48 is "same correct clean
twin verdict". §4 supplies that comparison by hand and it passes, but the shipped
harness does not enforce it for these three cells.

**Minimal correction (do not apply without L1):** give PG48 (and PG46/PG47, where a
twin is meaningful) a declared twin row so the harness's existing `twins`/
`twin_equal` machinery enforces the claim.

### F-4 (source, informational) — no source defect found in this cell

The candidate's hole diagnosis behaves exactly as the amended contract requires on
this fixture: `missing_reachable` reports the hole in both the `missing` and
`opaque` subsets (so the diagnosis machinery *does* see it), but the verdict path
does not consult it when no citation is unresolved, and it refuses with a
content-derived reason the moment either a citation is unresolved (§5a) or the
missing object is actually required (§5b). Nothing in this cell indicates a source
bug, and no source correction is proposed.

---

## 9. Residual risk and verification gaps

- **Mutation coverage accounting is not trustworthy as it stands.** F-1 shows one
  row in `expect_rows` that does not fail. Other rows in the same lists may be in
  the same condition; I checked only PM11/PG01/PM07 for PG48. A full re-derivation
  of every `expect_rows` list against actual `failed_rows` is **not** done here
  (out of my single-bounded-cell scope) and is L1's to run.
- **PM08 was not executed** (static-only, forbidden in this wave). The `--no-lazy-fetch`
  isolation was instead confirmed by the direct git-call trace (§6), which is
  behavioural evidence for the flag's presence on every call, but it is not the
  PM08 probe and does not substitute for it.
- **The `objects_acquired` check is inventory-diff based**
  (`cat-file --batch-all-objects` before/after). It detects objects that appear in
  the store; it cannot detect a fetch that is served from a local pack and produces
  no net new object id. §6's trace covers that gap for this cell (zero transport
  verbs over 22 calls).
- **Git floor**: this host runs git 2.56.0 and `--no-lazy-fetch` is supported here,
  so the inherited Git ≥ 2.45 prerequisite is satisfied *on this machine*. The
  prerequisite remains open at L0 for the fleet generally; I did not verify it
  elsewhere.
- **Only PG48 was exercised.** PG46 and PG47 are separate cells owned by other
  lanes; my §5a negative control resembles PG47 but is my own construction, not a
  run of PG47, and I make no claim about PG46/PG47's status.
- **`amended_view_met` on the frozen arm is meaningful** (it counts frozen rows
  that would already meet the amended view) and correctly reads 0 for PG48; the
  defect in F-2 is confined to the current arm's counters.

---

## 10. Files written

**Report** (this file):
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseOpaquePositive.md`

**Artifacts** — `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseOpaquePositive/`

| File | Contents |
|---|---|
| `grid-pg48.json` | the assigned grid run (`--arm both --case PG48… --json`), exit 0 |
| `probe-pg48.json` | independent fixture rebuild: object presence/absence, twin B/C documents and field diff, acquisition deltas |
| `control-trace-negctl.json` | 22-call git trace via PATH shim + negative control (unresolved fabricated token → exit 2) |
| `sensitivity-required-hole.json` | required-hole complement (exit 2) and no-hole control (exit 0) |
| `eager-blanket-probe.json` | eager blanket-precondition probe → PG48 killed |
| `pm11-pg48.json` | shipped PM11 mutation on a scratch copy → PG48 not killed (F-1) |
| `grader-verdict.json` | the shipped grader's own problem strings for both arms |
| `auditor-machinery.json` | auditor's `missing_reachable` / `opaque_hole` / `lookup` on the PG48 fixture |
| `lazy-fetch-hazard.json` | unisolated-probe hazard check + git version |
| `probe_pg48.py`, `control_pg48.py`, `sens_pg48.py`, `mach_pg48.py`, `eager_pg48.py`, `pm11_pg48.py`, `grade_pg48.py`, `haz_pg48.py` | the exact probe sources, so every number above is reproducible |

Heavy scratch/temp: `/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/`.

**Not written / not touched**: production `tools/`, `tests/`, lane `production/.jj/index`,
fleet, sibling clones, operator config, routing, services, real object stores.
Production auditor sha256 verified unchanged after all probes.

---

## 11. Summary

| Question | Answer |
|---|---|
| Does the pinned candidate meet PG48's amended expectation? | **Yes** — exit 0, zero defects, zero kinds, clean document, no acquisition |
| Are the finding/token pairs exactly as expected? | **Yes** — there are none; expected `[]`, observed `[]` |
| Are the premise objects real (missing/present as asserted)? | **Yes** — verified against the store, not inferred |
| Is the exit 0 discriminating? | **Yes** — killed by the eager blanket precondition; refused when a citation is unresolved or the hole is required |
| Is it a genuine twin match? | **Yes** — identical documents (field-by-field) for both the unmarked and the complete twin |
| Any source defect? | **None found in this cell** (F-4) |
| Any fixture/inventory defect? | **Yes** — F-1 (PM11 `expect_rows` over-broad), F-2 (current-arm `amended_view_*` counters structurally empty), F-3 (opaque cells declare no twin) |

Report: .ufo/waves/round-24/falsify/advice/CaseOpaquePositive.md
