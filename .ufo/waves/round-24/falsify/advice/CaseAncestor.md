# CaseAncestor — independent attack on fixture family Ancestor (`PG21-missing-ancestor-promisor`)

Round 24, FRESH FALSIFICATION of integrated commit `2e254a1763a9c08aa07fc53081287f506c447d84`.
Read-only production. L1 holds the planner. Lane bounds: leaf member, no subagent dispatch.

## Verdict

**HOLDS (with one fixture-grade defect reported separately from any source defect).**

The bounded selection passes, the amended target column is met, the frozen history is *not*
being presented as the improvement, and the withdrawn expectation remains visible. The
ancestor-family behaviour is correct on every axis I could measure: actual missing/present
objects, exact finding/token pairs, content-derived reason IDs, no objects acquired, and
marked-vs-unmarked substantive equality (which I had to build myself, because the manifest
registers no plain twin for this family — see Finding 1).

The one defect is in the **fixture/manifest layer**, not in the audited source: PG21's
declared `expect_rows` attribution in the mutation manifest is not backed by PG21's own
behaviour. PG21 does not discriminate the mutant it is credited with discriminating.

---

## Environment, pins and provenance (all observed, not inferred)

Scratch clone, `--no-hardlinks`, detached at the pinned revision:

```
/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/repo
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin repo
git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84
git rev-parse HEAD  -> 2e254a1763a9c08aa07fc53081287f506c447d84
git status --porcelain -> (empty)
```

Digest chain, computed in the pinned clone. All four task-stated pins match, and the frozen
auditor digest matches the digest recorded in `oracle-snapshot-before-inspection.json`:

| Artifact | sha256 | Task pin | Match |
|---|---|---|---|
| `tools/report-landing-audit.py` (source) | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | `ea51bc35…` | yes |
| `tests/report-audit/promisor-grid.py` (runner) | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | `b034e159…` | yes |
| `tests/report-audit/promisor-grid-expectations.json` (manifest) | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | `d86b7bea…` | yes |
| `tests/report-audit/promisor-mutants.py` (mutationprobe) | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` | `6e0b9d62…` | yes |
| frozen auditor `0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py` | `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` | `da5041a8…` in snapshot `derived_from.frozen_auditor_sha256` | yes |

Grid self-reported, from the bounded run: `expectations_sha256 = d86b7bea…` (identical to the
manifest file), `population_sha256 = 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975dddbff8dd2ed88`,
`population_size = 47`. `git version 2.56.0` (floor 2.45 satisfied on this host; the inherited
prerequisite remains open at L0 and is not claimed here).

No installs, no system mutations, no network, no transport, no repository program. The only
`git` calls I issued directly were local plumbing against scratch fixtures.

---

## The bounded selection (exactly as assigned)

```
cd /fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/repo
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor \
  python3 tests/report-audit/promisor-grid.py --arm both \
  --case PG21-missing-ancestor-promisor --json
exit=0
```

`arms.current.violations = 0`, `violating_cases = []`, `graded = 1`.
`arms.frozen.violations = 0` with `amended_view_unmet = ["PG21-missing-ancestor-promisor"]`
— i.e. the frozen r23 behaviour is retained as history and is explicitly **not** the target.
`withdrawn_original_failures = []` for this row (correct: PG21 has no distinct `amended`
entry, so its live view is its `original` view, and that view is met).

Per-row observation, `arm=current`:

```
exit=2  traceback=false  timed_out=false  leaked=false
objects_acquired: {"lane": [], "fleet": []}
stderr_tail: could-not-evaluate: unavailable required object: the kama history of
  daf9cd57385ab48dcfd6e72042aa5359885c95c9: git log -z --format=%H%x00%an%x00%at%x00%s
  daf9cd57... rc=128 error: Could not read afd3257b25052e44aef6265698d0f36643897d48
  fatal: Failed to traverse parents of commit daf9cd57...
document=null  defects=null  raw_defects=null
met_amended=true  met_original=true
```

`arm=frozen` on the same fixture: `exit=2`, stderr
`could-not-evaluate: <lane>: partial clone (remote.origin.promisor)`, `met_frozen=true`,
`met_amended_frozen=false`. The frozen arm fails the amended view for the right reason — its
refusal is the r23 metadata refusal, which the amended view forbids.

**Frozen-history-is-not-improvement, checked explicitly.** `met_frozen=true` (history retained)
and `met_amended_frozen=false` (history does not satisfy the live target) are reported as two
separate fields; the grid's own frozen arm is scored against the amended view as a baseline,
never as a target. Nothing in the row or in the report relabels the frozen pass as the
round-24 improvement.

---

## Assertions required by the assignment

### A. Actual missing / present objects — observed, independent of the grid's own scoring

Kept fixture (`--keep`, root `promisor-grid-w36uvh1u/current/000`), probed with
`--no-lazy-fetch` plumbing:

* lane tip commit `daf9cd57385ab48dcfd6e72042aa5359885c95c9` — **present** (`round-1: work`)
* tip tree `1c13e47ce9f8088dc933a80123cf6a8ee2fa701d` — **present**; contains
  `corpus` tree `742d4d0b…` (blob `051975b0…` = `# sources / fixture: no registry rows`)
  and blob `56d7b323…` = `fixture file`
* ancestor commit `afd3257b25052e44aef6265698d0f36643897d48` — **absent**. It is the parent
  recorded in the tip's own commit header (`parent afd3257b…`), so it is a true *ancestor*
  of the audited tip, not a sibling or a dangling object.
* `git --no-lazy-fetch rev-list --objects --missing=print refs/heads/master` lists exactly one
  missing id: `?afd3257b25052e44aef6265698d0f36643897d48`. **No other hole exists.**
* fleet: all 9 objects present, zero missing, and the fleet is **not** promisor-marked
  (`git config --local --list` shows no `promisor`/`partialclone` key) — the fleet is the
  control side, as the builder intends.
* lane is promisor-marked by **config only**: `remote.origin.promisor=true`,
  `extensions.partialclone=origin`, `remote.origin.url=<tmp>/absent-remote.git` (that path
  does not exist), and `objects/pack/` is empty (no `.promisor` markers).

The missing ancestor is a **non-leaf** hole, and the auditor classifies it as such:
`missing_reachable(lane, tip)` → `missing={afd3257b…}`, `opaque={afd3257b…}`, and
`opaque_hole()` names that same id. This matches the supplement's rule that a missing
tree/commit conceals the names below it.

### B. Exact finding / token pairs

For PG21 there is no verdict document at all (`document=null`, `defects=null`,
`raw_defects=null`, stdout is 0 bytes). The finding/token pair that *would* be reported is
correctly suppressed. The auditor's own reason names the unavailable object id
`afd3257b…`, which the grid's `names_any_of: ["$ancestor"]` resolves to exactly that sha.
The ancestor is also what the audit *needs*: with the ancestor restored, the same report
produces exactly one defect, `("landed-omitted", "afd3257b25052e44aef6265698d0f36643897d48")`
— i.e. the ancestor is a round-1 lane commit by `kama-shokunin` whose omission is genuinely
undeterminable when the commit cannot be read. That is precisely the amended contract's
"missing object actually required by audit reads ⇒ exit 2 with content-derived reason".

### C. Content-derived reason IDs

The refusal reason is content-derived, not metadata-derived and not a guess:

* starts with `could-not-evaluate:` (the typed refusal prefix),
* names the **unavailable object id** `afd3257b25052e44aef6265698d0f36643897d48`,
* contains **none** of the forbidden r23 metadata phrases — checked literally:
  `partial clone (` absent, `promisor pack` absent,
* carries no verdict document on stdout.

For contrast, the frozen auditor on the *same* fixture says `partial clone
(remote.origin.promisor)` — the r23 blanket refusal. The amended view rejects that; the
current source does not produce it.

### D. No objects acquired, no transport

`objects_acquired = {"lane": [], "fleet": []}` in the grid row, and independently in every
probe I ran (before/after `cat-file --batch-all-objects` inventories, both empty deltas).
The lane contains exactly 7 loose objects and the fleet 9 — unchanged by the audit. No
`FETCH_HEAD`, no `shallow`, no `ORIG_HEAD`, no new pack appeared in the lane's `.git`. The
promisor remote URL points at a non-existent path, so a fetch could not have succeeded even
if attempted; the auditor additionally carries `--no-lazy-fetch` in `GIT_ISOLATION` on its
single `subprocess.run` git call site (`tools/report-landing-audit.py:138`, `:162`), which is
the only git invocation in the file.

### E. Actual twin document comparisons — **the manifest registers none for this family**

This is the substantive gap. PG21 is one of only four `policy` rows with `twin: null`, and
unlike PG43/PG46/PG47 it is the only *missing-required-object* policy row with no plain
counterpart at all. Because PG21's expected exit is 2, the grid's document comparison would
in any case be vacuous: `normalise_document` returns `None` for a refusal (no stdout), and the
comparator sets `results[partner] = None` whenever either side has no document, so
`twin_equal` is `None`, never `False`. I confirmed this structurally for the manifest: the
five exit-2/exit-2 twin pairs (PG13↔PG14, PG15↔PG16, PG17↔PG18, PG19↔PG20, PG33↔PG34) are
all **vacuous** — `twin_pairs_compared` can never contain them.

So I built the twin the manifest does not declare, using the grid's own builder and its own
`normalise_document`, and compared:

| variant | exit | document (path-normalised) | defects | acquired |
|---|---|---|---|---|
| marked + ancestor missing | 2 | `null` | — | `{}` |
| **unmarked + ancestor missing** | 2 | `null` | — | `{}` |
| marked + ancestor present | 1 | identical to next row | `landed-omitted/afd3257b…` | `{}` |
| unmarked + ancestor present | 1 | identical to previous row | `landed-omitted/afd3257b…` | `{}` |

Results: `missing-marked|missing-unmarked` → `same_exit: true`, `same_document: true`
(both `None`), `same_defects: true`, `acquired` empty on both sides, stderr differing only
in the fixture path. `present-marked|present-unmarked` → `same_exit: true`,
`same_document: true` (byte-identical after the grid's path normalisation),
`same_defects: true`. **Promisor metadata alone does not change the verdict in either
direction**, which is the amended contract's core requirement, now actually observed for
this family.

---

## Finding 1 (fixture/manifest layer) — PG21 does not discriminate PM03, yet is credited with it

`tests/report-audit/promisor-mutants.py` lists `PG21` in PM03's
`expect_rows` (`PM03-skip-required-object-availability`, semantic: "a missing required
commit/tree/blob/report object is could-not-evaluate (exit 2), never a clean or failed
verdict"). Running the probe restricted to PG21:

```
PM03-skip-required-object-availability status: survived
failed_rows: []
=> PG21 discriminates PM03? False
```

And across the PM03-relevant rows (PG13, PG15, PG17, PG19, PG33, PG21) PM03 is killed by
**PG33 only**; PG21 is not among the killers.

Why: PM03 neutralises the store's *missing-object computation*
(`self._missing = missing_reachable(...)` → `set()` / `(set(), set())`). PG21's refusal does
not come from that computation at all — it comes from `round_commits`' `git log` on the tip
failing with rc=128 while traversing parents, which `required_read` converts into
`unavailable required object: …`. Removing the missing-object computation cannot change a
refusal that is already produced by a failed *required read*. PM03's removal is only
observable on rows whose verdict is produced by the missing-object machinery.

Severity: **medium, fixture-layer, non-blocking.** The runner's own semantics tolerate it —
`attributed` is computed over `failed ⊆ expect_rows`, and an over-broad `expect_rows` never
manufactures a kill, so no mutant is credited on PG21's account and no verdict is
misreported. But the manifest asserts a discriminating relationship PG21 does not have, and
the `expect_rows` list for PM03 (and for PM06, PM01) reads as if PG21 were a probe of the
required-object-availability rule when it is not. **Minimal correction (not applied):**
either remove `"PG21"` from PM03's `expect_rows`, or add a fixture whose verdict is produced
by the missing-object computation rather than by a failed required read — e.g. a variant
where the missing ancestor is *not* the tip's parent but is still referenced by the lane
history, so the read succeeds and only the diagnosis path decides.

Everything PG21 *does* discriminate, it discriminates genuinely: restricted to PG21 alone it
kills **PM01-blanket-metadata-refusal** (the mutant's `partial clone (promisor metadata)`
fails the amended view's reason-class and forbidden-phrase checks) and
**PM06-swallow-actual-read-error** (the mutant returns exit **0** with `kinds=[]` — a false
"clean" verdict where exit 2 is required). Both kills are correctly attributed, with
`unexpected_rows: []`. So the row is not inert; its credit list is merely over-broad.

### Finding 1b (fixture/manifest layer, lower severity) — no plain twin registered for PG21

`PG21-missing-ancestor-promisor` has `twin: null` and the manifest contains no
`PG21-missing-ancestor-plain` case, while every comparable missing-object family has one
(PG13/14, PG15/16, PG17/18, PG19/20, PG31/32, PG33/34, PG44/45). The amendment requires
that "complete marked versus unmarked twins … retain identical substantive verdicts", and for
this family the marked/unmarked equality is presently only checkable outside the grid (I
checked it outside, above, and it holds). Adding `c_missing_ancestor_plain` plus a
`PG2x-missing-ancestor-plain` control row would make the amended twin clause self-enforcing
for this family instead of externally asserted. Note that even with such a row the current
document comparator would stay vacuous for two refusing sides — a comparator that compared
`(exit, reason_class, named object ids)` rather than the stdout document would be needed for
refusal rows to carry twin signal.

---

## No source defect found in the Ancestor family

I looked specifically for a source-side flaw and did not find one:

* **Refusal is caused by the hole the audit needs, not by a blanket precondition.** Variant
  E (grandparent missing instead of parent, marked lane) → exit 2, reason names the missing
  grandparent. Variants F/G (hole on an *unselected* side branch, marked and unmarked) →
  **exit 0 clean**, no refusal. The refusal therefore tracks the required read, not "any
  hole", which is exactly the amended rule.
* **No blanket metadata refusal.** Marked and unmarked produce identical verdicts in both
  the missing and present shapes (table above); the frozen r23 base, by contrast, refuses
  the *marked-present* fixture with `partial clone (remote.origin.promisor)` where the
  current source correctly returns exit 1.
* **The r23 behaviour is preserved as history, not claimed as the target** (see above).
* **The withdrawn expectation stays withdrawn.** The preregistration's `expected_after[3]`
  (unknown-citation ⇒ exit 2 in any metadata-marked repository) is superseded by
  `oracle-amendment-1.json`; the grid scores PG21 against its `original`/`amended` view and
  reports original-view failures in a separate `withdrawn_original_failures` field. For
  PG21 that field is empty and `met_original=true`, which is right — PG21's row was never
  part of the withdrawn set. I did **not** relabel any withdrawn expectation as passed, and
  PG21's own row is not one of the withdrawn rows.
* **Expectation cells were not moved to fit the candidate.** The 44 pre-registered cases in
  `promisor-grid-expectations.json` are byte-for-byte identical to the 44 in
  `oracle-snapshot-before-inspection.json` (I diffed them field by field: `differing cases: []`).
  The only additions are the three independent opaque cells PG46/PG47/PG48 from
  `oracle-supplement-2.json`, and I verified each of those three rows' live expectation
  against the supplement's stated `expected_exit` (2, 2, 0 — all MATCH) and against its
  builder name.
* **Grader strength.** The grader remains `names_any_of` with `$`-token resolution; I
  confirmed PG21's live check resolves `$ancestor` to the concrete sha
  `afd3257b25052e44aef6265698d0f36643897d48` and that the forbidden-phrase list
  (`partial clone (`, `promisor pack`) is enforced on the current arm. No path-based
  relaxation is present in this row.
* **Grader-vs-source coupling, checked.** The grid's `met_amended` for PG21 depends on
  `names_any_of` matching a sha that appears in stderr. I verified *why* it appears: the
  auditor's own prefix names the **tip** (`the kama history of daf9cd57…`), while the
  missing ancestor's id appears in the embedded `git` diagnostic
  (`Could not read afd3257b…`). The id is genuinely the unavailable object's, and the
  refusal is content-derived, but the grader's token check is satisfied through git's
  message text rather than through an auditor-authored id. That is adequate here (the token
  is real and content-derived, and `unavailable required object` is present in the
  auditor's own words), and it is not a false pass — but it is worth recording as a
  coupling: if a future git release reworded that diagnostic, PG21's `names_any_of` check
  would fail for a reason unrelated to the audit's behaviour. The auditor's stronger,
  self-authored naming paths (`root_tree`, `opaque_hole`, `unknown_citation`) are not
  exercised on this row.
* **Fixture hazard inherited from the peer report.** I re-verified independently that this
  fixture is *not* exposed to the lazy-fetch materialisation hazard: the lane's
  `remote.origin.url` points at a non-existent `absent-remote.git`, and there is no
  `objects/pack/` and no reachable `file://` origin, so a stray non-`--no-lazy-fetch` probe
  cannot materialise the ancestor. (I confirmed that even a deliberate probe *without*
  `--no-lazy-fetch` leaves the ancestor missing.) The hazard flagged by
  `KamaR23-2.CaseFleetBlobless` is specific to the blobless-clone families, which use a
  reachable local `file://` origin; PG21 uses `mark_config` with an absent remote and is
  not affected.

---

## Scope discipline

* Only the assigned bounded selection was run against the grid:
  `--arm both --case PG21-missing-ancestor-promisor --json` (plus one `--keep` re-run of the
  same single case for fixture inspection, and the mutation probe restricted to
  `--case PG21-missing-ancestor-promisor`). No full-suite sweep was executed.
* No network, no transport, no repository program, no execution payload. `PM08` was **not
  executed** — it is static-only in the manifest, and I confirmed it is reported
  `static-only-not-executed` (its `--no-lazy-fetch` marker check was never run as a
  mutation).
* No production file was edited: `git status --porcelain` in the pinned clone is empty; the
  only writes are this report and the artifacts under `falsify/out/CaseAncestor/`.
* No lane production `.jj/index`, fleet, sibling, operator config, routing, service or real
  object store was touched. All heavy scratch and `TMPDIR` targets were under
  `/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor`.
* Source-ledger supplement at this pinned revision: `corpus/SOURCES.md` carries **105**
  distinct `S…` rows; `S105` records the explicit rejected S095 cross-API inference
  (`S105.json`: `"rejected_inference": "bytes.decode default documents subprocess text mode
  or TextIOWrapper default"`, `"prior_rejection": "S095 remains filed and rejected…"`), and
  `S095` remains filed at `corpus/SOURCES.md:107`. The source-census final verification is
  L1-owned after this stage and is not asserted here.
* No score increase, serving capability, admission, integration or shipping judgement is
  asserted. This is a verdict on one fixture family only.

## Files written

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseAncestor.md` (this report)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseAncestor/`
  * `pg21.json`, `pg21.stderr` — the assigned bounded selection (exit 0)
  * `keep.json`, `keep.stderr` — the `--keep` re-run of the same single case
  * `grid-pg21/` — the runner's own `population.json` / `candidate.json`
  * `direct.stdout`, `direct.stderr` — the current auditor run directly against the kept fixture
  * `mut_pg21.json` — mutation probe restricted to PG21
  * `twin_probe.py`, `twin_probe.json` — the missing plain twin (marked/unmarked × missing/present)
  * `twin_doc_probe.py`, `twin_doc.json` — path-normalised document comparison
  * `deep_probe.py`, `deep.json` — deeper-ancestor and unselected-side-hole variants
  * `frozen_probe.py`, `frozen.json` — frozen r23 base on all four variants
  * `promisor_grid_py.py` — byte-copy of the pinned runner, imported unmodified

## Unverified / residual risk

* The **frozen-arm** behaviour on the plain (unmarked) ancestor-missing fixture is exit 2
  with a content-derived reason, and it therefore *satisfies* the amended view on that
  variant. I verified this directly. It is a property of the r23 base on an unmarked repo,
  not a hole in PG21 (which is marked and whose frozen arm correctly fails the amended view
  with the metadata refusal). I did not enumerate whether any other r24 row is sensitive to
  this; that is outside this family.
* Whether the missing ancestor should be *recoverable* from the tip's own commit header (the
  parent id is present in the tip object) is a design question I did not adjudicate; the
  auditor's read of the lane history genuinely fails, so exit 2 is correct under the amended
  contract as written.
* `expect_rows` semantics for PM03/PM06/PM01 were read from
  `tests/report-audit/promisor-mutants.py` (`attributed` over `failed ⊆ expect_rows`); I
  did not run the full mutation inventory against the full 47-row grid, only the PG21-scoped
  and PM03-scoped subsets.
* The audit's own `selftest` (`tools/report-landing-audit.py --selftest`) and the
  `isolation-mutants.py` suite were not executed; they are outside this family and outside
  the assigned bounded selection.
* Whether `absent-remote.git` could be reachable in another environment was not probed; no
  network use was permitted and none was attempted.

Report: .ufo/waves/round-24/falsify/advice/CaseAncestor.md
