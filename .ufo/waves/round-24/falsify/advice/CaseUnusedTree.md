# CaseUnusedTree — independent falsification of the UnusedTree family (PG44 / PG45)

**Verdict: HOLDS.** The amended (live) expectation for both rows is met at the pinned
revision; the rows are not vacuous, the missing object is a genuine unavailable tree,
the verdict is content-equal to the plain twin and to a hole-free twin, nothing is
acquired, and the rows carry real mutation-kill power. Two low-severity precision
notes are recorded below (one about the mutation inventory, one about a pair that is
labelled "control" while carrying the same hole). No source defect was found in this
family's scope; no expectation cell was changed; no production file was edited.

---

## 1. Pinned base, artifacts and digests (observed)

| item | value | how observed |
|---|---|---|
| pinned revision | `2e254a1763a9c08aa07fc53081287f506c447d84` (`round-24: land completed 64-seat build evidence and explicitly carry residual closure debt`, 2026-10-21T16:45:12-03:00) | `git rev-parse HEAD` in the scratch clone |
| clone | `/fast/scratch/hyaku/kama-r24/falsify/CaseUnusedTree/repo`, `git clone --no-hardlinks` + `git checkout --detach 2e254a1…` | clone is clean (`git status --porcelain` empty) |
| source tool `tools/report-landing-audit.py` | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | `sha256sum`; matches the pin given in the assignment |
| runner `tests/report-audit/promisor-grid.py` | sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | `sha256sum`; matches the pin |
| manifest `tests/report-audit/promisor-grid-expectations.json` | sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | `sha256sum`; matches the pin |
| mutation probe `tests/report-audit/promisor-mutants.py` | sha256 `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` | `sha256sum`; matches the pin |
| frozen auditor (r23 base `0df800e8…`) | sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` | grid output; equal to `oracle-snapshot-before-inspection.json:derived_from.frozen_auditor_sha256` |
| population | `population_size=47`, `population_sha256=612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` | grid output |
| host | git 2.56.0, Python 3.14.8 | `git --version`, `python3 --version` |
| source ledger | `corpus/SOURCES.md` has **105** rows; `S105` = "explicit rejection record for the cross-API inference in S095" | `grep -c '^| S[0-9]' corpus/SOURCES.md`; S105 line read. Unchanged by me; final census verification stays L1-owned. |

Production was not touched: `git rev-parse HEAD` in
`/home/vgpnk/Projects/shokunin/kama-shokunin` is still `2e254a1…`; the only new
untracked content is under `.ufo/waves/round-24/falsify/` (this report and my
`out/CaseUnusedTree/` artifacts).

## 2. Commands and exit codes (exact)

```
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin \
    /fast/scratch/hyaku/kama-r24/falsify/CaseUnusedTree/repo            # rc 0
git -C …/repo checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84   # rc 0
# TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseUnusedTree/tmp
python3 tests/report-audit/promisor-grid.py --arm both \
    --case PG44-missing-unused-tree-promisor \
    --case PG45-missing-unused-tree-plain --json                       # rc 0
python3 /fast/scratch/hyaku/kama-r24/falsify/CaseUnusedTree/verify_unused_tree.py   # rc 0
python3 /fast/scratch/hyaku/kama-r24/falsify/CaseUnusedTree/verify2_calls.py        # rc 0
python3 tests/report-audit/promisor-mutants.py \
    --case PG44-missing-unused-tree-promisor --case PG45-missing-unused-tree-plain \
    --only PM01-blanket-metadata-refusal --only PM07-full-all-missing-gate \
    --only PM11-any-hole-refusal --json                                 # rc 0 (1 of 3 killed)
python3 tests/report-audit/promisor-grid.py --arm current \
    --current /fast/scratch/hyaku/kama-r24/falsify/CaseUnusedTree/eager-refusal-audit.py \
    --case PG44-missing-unused-tree-promisor --case PG45-missing-unused-tree-plain --json
                                                                          # rc 1 (2 violations, intended)
```

Grid JSON: `…/falsify/out/CaseUnusedTree/grid-pg44-pg45.json` (stderr file empty).

## 3. Measured grid rows (observed, not inferred)

| case | kind | arm | exit | defects (kind,token) | kinds | stderr | met_frozen | met_original | met_amended | twin_equal | objects_acquired |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PG44-missing-unused-tree-promisor | policy | current | **0** | `[]` | `[]` | empty | – | true | **true** | **true** | lane `[]`, fleet `[]` |
| PG45-missing-unused-tree-plain | control | current | **0** | `[]` | `[]` | empty | – | true | **true** | **true** | lane `[]`, fleet `[]` |
| PG44 | policy | frozen (r23) | 2 | n/a | n/a | `could-not-evaluate: …/lane: partial clone (remote.origin.promisor)` | true | – | false | `null` (no document) | `[]`/`[]` |
| PG45 | control | frozen (r23) | 0 | `[]` | `[]` | empty | true | – | true | `null` | `[]`/`[]` |

Arm summary: current — `violations=0`, `graded=2`, `twin_compared=2`,
`twin_pairs_compared=["PG45-missing-unused-tree-plain"]`, `twin_mismatch=[]`,
`withdrawn_original_failures=[]`, `tracebacks=0`, `timeouts=0`, `harness_leaks=0`.
Frozen — `violations=0`, `amended_view_unmet=["PG44-missing-unused-tree-promisor"]`
(the r23 blanket refusal, history only).

**Target columns compared (amended view).** PG44/PG45 carry **no** `amended` entry in
the amendment's `amended_rows` (that list is PG22, PG23, PG24, PG28, PG30, PG34,
PG37→`null`, PG41), so by the snapshot's own rule (`oracle-snapshot-before-inspection.json`,
`views.amended`: *"a case without an 'amended' entry uses its 'original' view"*) both rows
are graded against their `original` view, which for them is identical to the amended one:
`exit 0`, `kinds []`, `reason_class null`, `defects []`. Observed: `exit 0`, `kinds []`,
`defects []`, empty stderr. **Met.**

**Withdrawn expectation kept visible.** The withdrawn row is preregistration
`expected_after[3]` ("a missing citation in any promisor-backed repository is unknown …
exit2 unless resolved locally by another audited repository", withdrawn prospectively by
`oracle-amendment-1.json`). **PG44/PG45 do not exercise it**: neither fixture contains
any unresolved citation (the fleet report cites exactly one commit, which resolves
locally). For this family the withdrawn row is *not applicable* — it is neither failed
nor counted as achieved — and the graded contract is the amendment's
`prospective_expected[4]/[5]` ("Incomplete but locally sufficient repositories are not
refused merely because an unrelated historical blob, branch, or unused file is missing";
"Missing objects actually required by audit reads remain could-not-evaluate exit2, with
content-derived reason"). The r23 `frozen` row for PG44 (exit 2, metadata reason) is
history, never a target.

## 4. Actual missing / present objects (independent plumbing, not the grid's own report)

Rebuilt the graded fixture with the pinned grid's own builder
(`c_missing_unused_tree_promisor` / `c_missing_unused_tree_plain`) and then verified
with independent `git` plumbing (all probes `--no-lazy-fetch`):

* The premise is **non-vacuous**: exactly one object is missing from the lane store —
  `33fd12ece1ea4ddfb346b902ea84aa4972ff9495`, which the tip tree
  `893b53187fb301128c0256e8413107863fd5aa31` lists as `040000 tree 33fd12ec…  extra`
  (i.e. the *unused* subtree). `git cat-file -e 33fd12ec…^{tree}` → **rc 128** (absent);
  `git rev-list --objects --missing=print` → `?33fd12ec…` and nothing else;
  grid premise `lane_missing = ["33fd12ec…"]`, `fleet_missing = []`.
* Every object the audit actually reads is **present**: lane commit `17627ab6…`, tip tree
  `893b5318…`, `f` blob `56d7b323…`, `corpus/SOURCES.md` blob `051975b0…`, fleet report
  blob `f2e76964…`, fleet tip tree `e016c532…` (all `cat-file -e` → rc 0).
* The store holds 6 objects; the `extra/leaf.txt` blob survives its missing parent tree
  (present but unreachable). The hole is a genuine **tree** hole, not a blob hole.
* Promisor marking is real and confined to the lane: `lane_promisor=true`,
  `fleet_promisor=false`; `remote.origin.url` = `<fixture>/absent-remote.git`, which
  **does not exist** (`Path.exists() == False`).

## 5. Actual twin document comparison (not a proxy)

* Grid-level: `PG44.twins["PG45-missing-unused-tree-plain"] = true` and
  `PG45.twins["PG44-missing-unused-tree-promisor"] = true`; both rows' normalised
  verdict documents are byte-equal (paths replaced by `<lane>`/`<fleet>`).
* Independent level (my own runs): the normalised documents of **PG44 (promisor, hole)**,
  **PG45 (plain, hole)** and a **hole-free complete twin** (`unused_tree=True`, no drop)
  are all equal — `pg44_equals_pg45 = true`, `pg44_equals_complete = true`. The verdict
  is therefore not an artefact of the hole and not an artefact of the promisor metadata.
* The **git call sequences are identical** between the promisor and the plain fixture
  (22 calls each, `call_diff` empty both ways, `call_sequence_identical_pg44_pg45=true`):
  promisor metadata changes **no operation**. No call names the missing subtree
  (`names_missing_tree = []`), and the missing-object walk is never even invoked
  (no `rev-list` among the 22 calls) because every citation resolves — the diagnosis is
  lazy and on-demand, exactly as the source docstring claims.

## 6. Reason IDs / content-derived refusal form

* Current arm: **no refusal at all** (exit 0, empty stderr), so there is no reason string
  to grade; the rows' `reason_forbidden` list (`"partial clone ("`, `"promisor pack"`) is
  vacuous in the current arm and is exercised only in the frozen arm, where the r23
  metadata reason is correctly reproduced (and correctly forbidden for the current arm).
* Counterfactual, probe-built (section 8): the refusal that a hole-precondition
  regression produces is content-derived and names the store:
  `unknown: unavailable required object: 2 hole(s) in the store`. (The count "2" is my
  probe's own artefact — it adds the `missing` and `opaque` sets, which overlap in the
  single hole — not a product behaviour.)

## 7. No acquisition, no transport, no leak

* Grid: `objects_acquired = {lane: [], fleet: []}` for **all four** rows (current + frozen).
* Intercepted call list (PATH wrapper around `git`): 22 calls, **all** carrying
  `--no-lazy-fetch` **and** `--no-replace-objects`
  (`no_lazy_fetch_calls = 22`, `no_replace_calls = 22`); zero `git fetch` / `clone` /
  `upload-pack` / `ls-remote` invocations (the earlier "transport" hits were false
  positives from the `--no-lazy-fetch` flag text itself). The promisor remote points at a
  non-existent path, so even a stray fetch could not materialise anything; the hole is a
  tree, so no path probe could re-create it either.
* No traceback, no timeout, no harness leak in either arm.
* Source-side isolation confirmed statically: `GIT_ISOLATION = ("--no-replace-objects",
  "--no-lazy-fetch", …)` on every git call, inherited `GIT_*` stripped, `GIT_CONFIG_GLOBAL=os.devnull`,
  `GIT_CONFIG_NOSYSTEM=1`, `GIT_TIMEOUT=20` (`tools/report-landing-audit.py:138–170`).
  Consequence for an auditor of this evidence: `GIT_TRACE=1` is neutralised, so the
  call sequence had to be captured with a PATH wrapper (that is what was done).

## 8. Mutation / regression sensitivity of these two rows (measured)

Restricted to `--case PG44 --case PG45` (no full-suite rerun):

| mutant | status on my rows | failed rows | reading |
|---|---|---|---|
| `PM01-blanket-metadata-refusal` | **killed** (attributed, `unexpected_rows=[]`) | PG44 (exit 2, `partial clone (remote.origin.promisor)`) | PG44 alone detects the r23-style metadata refusal |
| `PM07-full-all-missing-gate` | survived | – | as the manifest itself declares (redundant on a candidate that already traverses from every present object) |
| `PM11-any-hole-refusal` | survived | – | **the lazy** over-refusal form is invisible to PG44/PG45 (see note F4) |

To measure the *eager* form of the forbidden unconditional hole precondition I built a
scratch-only patched auditor (`eager-refusal-audit.py`, inserts a hole precondition right
after the stores are built) and ran the grid with `--current` pointing at it:

* PG44 → **exit 2**, `met_amended=false`, reason `unknown: unavailable required object: 2 hole(s) in the store`
* PG45 → **exit 2**, `met_amended=false`, same reason
* grid rc = 1, `violating_cases = ["PG44-missing-unused-tree-promisor", "PG45-missing-unused-tree-plain"]`

So the rows do carry detection power against the eager hole-precondition regression the
amendment forbids; they cannot see the lazy variant (§9, F4).

## 9. Findings

### Source flaws

**None found in this family's scope.** The current implementation refuses nothing on
promisor metadata, resolves every citation locally, reads no missing object, acquires
nothing, and returns the twin verdict. The one mechanism that could have produced a
blanket refusal (`RepoStore.missing()` / `opaque_hole()`) is reached only from
`refuse_unknown()` for a citation that is *not* resolved — it is never a precondition
(`tools/report-landing-audit.py:419–452`, `651–717`).

### Fixture / manifest precision notes (separate from source flaws)

* **F4 (low, mutation inventory precision).** `PM11-any-hole-refusal`'s semantic text
  claims "an unused tree hole next to fully resolved citations keeps the clean verdict",
  and its `expect_rows` list includes PG44 and PG45 — but under PM11's *lazy* patch those
  two rows **cannot** violate (the diagnosis is never invoked when every citation
  resolves): measured, PM11 → survived with `failed_rows=[]` on my rows. The listing is
  inert rather than false (the harness attributes a kill only when the failed rows are a
  subset of `expect_rows`), so it cannot manufacture a false kill; but it over-states
  this family's detection power. Minimal correction (not applied, production untouched):
  drop `PG44`/`PG45` from PM11's `expect_rows` and say in its semantic that the
  *eager* form is caught by PG44/PG45 while the *lazy* form is caught by the
  fabricated-citation rows (PG22/PG25/PG37/PG41/PG42). The same inertness applies to
  PM07's PG44/PG45 entries, where the manifest already admits the mutant is redundant.
* **F5 (informational, pair shape).** PG45 is labelled `kind: "control"` but carries the
  *same* missing tree as PG44, so the pair proves metadata-independence (correct and
  sufficient) and does **not** by itself prove the hole is unused — PG45 is equally
  holed. The "hole is unused" half of the claim is carried by the amended expectation
  (exit 0 with the hole present) and, in my independent work, by the hole-free twin
  comparison in §5. No change needed; recorded so the pair is not read as more than it is.
* **F6 (informational, `reason_forbidden` vacuity in the current arm).** PG44's
  `reason_forbidden` guard ("partial clone (", "promisor pack") only bites when the row
  refuses; in the current arm it never refuses, so the guard is exercised only by the
  frozen arm. Not a flaw: the current arm's refusal form is covered by `check_exit2_form`
  on the rows that do refuse (PG33/PG34/PG46/PG47).

## 10. Residual risk and verification gaps

* **Population-wide claim not re-measured here.** Only PG44/PG45 were run, by instruction.
  The "47/47" property of the fixed47 set remains L1's to assert; my two rows are met.
* **Git floor (inherited L0 prerequisite) still open.** Host git is 2.56.0. The
  `--filter=blob:none --missing=print` walk that classifies non-leaf holes is **not
  exercised by PG44/PG45** (the diagnosis is never invoked there), so this family gives no
  evidence about the Git>=2.45 floor of that walk — it is exercised only by the opaque
  rows (PG46/PG47/PG48) and by PG22/PG24.
* **Mutation coverage beyond my rows.** Only PM01/PM07/PM11 were run, restricted to my
  two cases; PM08 was not executed (static-only, forbidden by the contract) — I verified
  the `--no-lazy-fetch` flag statically instead (present on all 22 intercepted calls).
* **Python drift.** Host Python 3.14.8 while `S095` pins 3.14.9 (already flagged in
  r23 evidence). Behaviour on 3.14.9 is unverified; it does not affect the PG44/PG45
  logic, which is git-plumbing bound.
* **Frozen-arm caution.** The frozen auditor was read as a blob from `0df800e8…` in the
  pinned clone, exactly as the grid does; I did not check out or execute the r23 tree.
* **Fixture hazard raised by a sibling** (`CaseFleetBlobless`: a blobless clone keeps a
  reachable `file://` origin, so a probe *without* `--no-lazy-fetch` can materialise a
  missing blob and make a premise evaporate): **not applicable to this family** — PG44/PG45
  use `mark_config()` whose `remote.origin.url` is an **absent** path, and the dropped
  object is a tree that no path probe can re-create. Every probe I ran used
  `--no-lazy-fetch` (the one exception, `GIT_TRACE=1`, was neutralised by the auditor's
  own env, so it changed nothing). I corroborated this to the peer.

## 11. Files written

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseUnusedTree.md` (this report)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseUnusedTree/grid-pg44-pg45.json` (+ `.stderr`, empty)
* `…/out/CaseUnusedTree/verify-unused-tree.json` — premise + object-state + hole-free/defect-variant comparisons
* `…/out/CaseUnusedTree/verify2-git-calls.json` — intercepted git call sequences, doc equality
* `…/out/CaseUnusedTree/mutants-myrows.json` (+ `.err`) — PM01/PM07/PM11 restricted to my rows
* `…/out/CaseUnusedTree/probe-eager-refusal.json` (+ `.err`) — eager hole-precondition probe (rc 1, 2 violations)

Scratch only (never production): `/fast/scratch/hyaku/kama-r24/falsify/CaseUnusedTree/{repo,tmp,verify,verify2,verify_unused_tree.py,verify2_calls.py,eager-refusal-audit.py}`.

No tool was installed or updated in this lane (nothing needed installing; git 2.56.0 and
Python 3.14.8 were already present). No network transport was used, no service or config
was mutated, no lane `production/.jj/index`, fleet, routing or operator configuration was
touched.

Report: .ufo/waves/round-24/falsify/advice/CaseUnusedTree.md
