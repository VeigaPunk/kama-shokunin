# CaseHydratedTwins — independent falsification of fixture family HydratedTwins

Scope: fixture family `HydratedTwins` = `PG05-hydrated-blobless-lane`,
`PG06-hydrated-blobless-fleet`, `PG07-complete-lane-plain`,
`PG08-complete-fleet-plain` only. Read-only w.r.t. production; pinned clone,
scratch-only, offline, no network/transport payloads, no execution payloads.

## Verdict

**HOLDS (4/4).** On the pinned commit every one of the four graded rows meets
the live **amended** target columns of the fixed expectation table, with
identical substantive verdicts between each promisor-marked case and its
plain twin, **zero objects acquired**, no timeout, no traceback, no harness
leak, and no metadata/unknown/full-closure refusal anywhere in the current arm.

- **Source flaws found in this family: none.** (Section 7)
- **Fixture/harness flaws found: 3 + 1 coverage gap + 1 reporting quirk.** None of
  them changes any verdict of these four rows in this revision; they are
  robustness/degeneracy risks for future revisions. (Section 8)
- **No originally withdrawn failed expectation is hidden in this family:** the
  four rows carry no `amended` entry, so `original == amended` for all four,
  and `met_original` is **true** for all four in the current arm — the
  withdrawal list (`withdrawn_original_failures`) is **empty** for this
  selection. (Section 6)

## 1. Snapshot

| item | value |
|---|---|
| pinned revision (detached HEAD in my scratch clone) | `2e254a1763a9c08aa07fc53081287f506c447d84` |
| clone | `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r24/falsify/CaseHydratedTwins/repo` then `git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84` |
| subject | `round-24: land completed 64-seat build evidence and explicitly carry residual closure debt` |
| source tool `tools/report-landing-audit.py` | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` (matches contract `ea51bc35…`) |
| runner `tests/report-audit/promisor-grid.py` | sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` (matches contract `b034e159…`) |
| manifest `tests/report-audit/promisor-grid-expectations.json` | sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (matches contract `d86b7bea…`) |
| mutation probe `tests/report-audit/promisor-mutants.py` | sha256 `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` (matches contract `6e0b9d62…`; **not executed by me**, out of scope) |
| frozen auditor blob (`0df800e896f6bce285a81e794ad4ae1d1e6c3a71`) | sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` (matches the oracle snapshot's `frozen_auditor_sha256`) |
| expectations table population | `population_sha256 = 612b0a74f3eebaa9…`, `population_size = 47` (original 44 unchanged + 3 independent opaque cells `PG46/PG47/PG48`; `PG40` is an `open_row`, not graded) |
| environment | git `2.56.0`, linux 7.2.11-arch1-1, python3 (stdlib only) |
| scratch | `/fast/scratch/hyaku/kama-r24/falsify/CaseHydratedTwins` (`TMPDIR` for every subprocess set to `…/CaseHydratedTwins/tmp`) |

No production file was modified: production `.jj/index`, fleet, sibling worktrees,
operator config, routing and services were untouched. Only my own advice/out
paths under `.ufo/waves/round-24/falsify/` were written.

## 2. Commands and exits (exact)

```
$ cd /fast/scratch/hyaku/kama-r24/falsify/CaseHydratedTwins/repo
$ TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseHydratedTwins/tmp \
  python3 tests/report-audit/promisor-grid.py --arm both \
    --case PG05-hydrated-blobless-lane \
    --case PG06-hydrated-blobless-fleet \
    --case PG07-complete-lane-plain \
    --case PG08-complete-fleet-plain \
    --json --out /fast/scratch/hyaku/kama-r24/falsify/CaseHydratedTwins/out
EXIT=0            # stderr empty
```

```
$ cd /fast/scratch/hyaku/kama-r24/falsify/CaseHydratedTwins
$ TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseHydratedTwins/tmp python3 probe.py > out/probe.json
EXIT=0            # stderr empty
```

```
$ python3 /fast/scratch/.../repo/tools/report-landing-audit.py --lane-repo pg05u/lane --fleet-repo pg05u/fleet --rounds 1 --json --no-errata
could-not-evaluate: unavailable required object: 58866b563cd900df310588effe79028efc104c33:corpus/SOURCES.md (051975b0ced83169116c235e7691c0a1a8313300) in …/pg05u/lane: git cat-file blob 051975b0ced83169116c235e7691c0a1a8313300 in …/pg05u/lane: rc=128 fatal: git cat-file 051975b0ced83169116c235e7691c0a1a8313300: bad file
EXIT=2

$ python3 …/tools/report-landing-audit.py --lane-repo pg06u/lane --fleet-repo pg06u/fleet --rounds 1 --json --no-errata
could-not-evaluate: unavailable required object: .ufo/reports/round-1/kama.md at fleet HEAD (tip tree b1e11739fedfb736f2936bd9addf7e4a286d462e, …/pg06u/fleet): git show HEAD:.ufo/reports/round-1/kama.md in …/pg06u/fleet: rc=128 fatal: bad object HEAD:.ufo/reports/round-1/kama.md
EXIT=2
```

(The last two runs are my own *scratch variants* of the same builders with
hydration switched off — a bounded discriminating measurement, see §4/§5. They
are **not** graded rows; I added no row and changed no expected cell.)

## 3. Graded results vs the live amended target columns

Live view for these four rows = `amended` if present else `original`
(`oracle-amendment-1.json.amendment.amended_rows` lists only
`PG22, PG23, PG24, PG28, PG30, PG34, PG37, PG41`, **not** these four), so the
graded column for PG05–PG08 is the `original` column, unchanged from the
initial registration.

| row | kind | expected (live/amended) exit | expected kinds | expected defects | observed exit | observed kinds | observed defects (uncorrected) | observed raw defects | met (amended) | met (original) |
|---|---|---|---|---|---|---|---|---|---|---|
| PG05-hydrated-blobless-lane | policy | 0 | `[]` | `[]` | **0** | `[]` | `[]` | `[]` | **true** | **true** |
| PG06-hydrated-blobless-fleet | policy | 0 | `[]` | `[]` | **0** | `[]` | `[]` | `[]` | **true** | **true** |
| PG07-complete-lane-plain | control | 0 | `[]` | `[]` | **0** | `[]` | `[]` | `[]` | **true** | **true** |
| PG08-complete-fleet-plain | control | 0 | `[]` | `[]` | **0** | `[]` | `[]` | `[]` | **true** | **true** |

Exact finding/token pairs: **there are none** — every row produced
`defects = []` and `raw_defects = []` (no finding at all, and no
errata-corrected finding hidden in the raw list: `errata_rows = 0`,
`errata_invalid = []`, `errata_unmatched = []`). The verdicts are
`summary.status = "clean"`, `defects = 0`, `uncorrected = 0`, `corrected = 0`,
`by_kind` all zero, `rounds = [1]`, `required_commits = 1`, `cutoff = 2000`,
`post_report_commits = 0`.

Grid roll-up (observed): current arm `graded=4 violations=0 violating_cases=[]`,
`tracebacks=0 timeouts=0 harness_leaks=0`, `withdrawn_original_failures=[]`,
`twin_compared=4`, `twin_mismatch=[]`. No exit-2 refusal occurs in the current
arm for this family, so the "content-derived reason ID" contract is vacuously
satisfied here; the content-derived refusal form is exercised by my §2
variants (reason names the actual missing blob OID / report path + tip tree).

## 4. Independent premise assertions (observed, not inferred)

The grid's `run_case()` **never checks** the `premise` dict that `build()`
computes (only `--selftest` does, for one unrelated case), so I asserted the
premises myself with `--no-lazy-fetch`/`--no-replace-objects`-safe probes
(`git cat-file --batch-all-objects`, `rev-list --objects --missing=print`).

| fixture | promisor config observed | `.promisor` marker | objects present | missing reachable ids | blobs present |
|---|---|---|---|---|---|
| PG05 lane (hydrated blobless) | `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none` (**no** `extensions.partialclone`) | `pack-8ec4199c31969802bfbaf3125ec1188555d936cb.promisor` (paired with its `.pack`) | 5 | **`[]`** | `f` blob ✓, `corpus/SOURCES.md` blob ✓ |
| PG05 lane, same builder **without** hydration (my variant) | identical promisor config | identical marker | 3 | `051975b0ced83169116c235e7691c0a1a8313300`, `56d7b323865c731da81e0225cf109d66f0480919` | `f` blob ✗ |
| PG05 fleet (plain) | none | none | 9 | `[]` | — |
| PG06 fleet (hydrated blobless) | `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none` | `pack-e449375be95f9ab711e11564e43ca29052405204.promisor` | 9 | **`[]`** | report blob ✓ |
| PG06 fleet, **without** hydration (my variant) | identical | identical | 7 | `0cf7ed5cd6dec335553d165dc587baa224ab302b`, `bfa655111293037a5564088d1a9bbca4cbcf446b` | report blob ✗ |
| PG07 lane (plain) | none | none | 5 | `[]` | — |
| PG08 fleet (plain) | none | none | 9 | `[]` | — |

Consequences (all **observed**):

1. The blobless construction is genuine, not simulated: with hydration off the
   promised blobs are **absent** from the clone, i.e. `--filter=blob:none` over
   the local `file://` transport really excluded them.
2. Hydration **is load-bearing**: the unhydrated lane twin refuses with a
   content-derived reason naming the missing `corpus/SOURCES.md` blob
   (`051975b0…`) and the unhydrated fleet twin refuses naming the missing
   report blob. Therefore PG05/PG06 do discriminate "hydrated" from
   "unhydrated"; they are not vacuous.
3. After hydration the reachable closure is **complete** (`missing == []`), which
   is exactly the amended policy's precondition for a local verdict — and the
   current auditor returns the ordinary clean verdict rather than a refusal.
4. The clone's `remote.origin.url` still points at the **live, reachable**
   `file://…/lane-origin` directory (the origin is not deleted), so a lazy
   fetch was physically possible during the audit. It was **not** taken
   (§5). This is the same hazard `KamaR23-2.CaseFleetBlobless` reported from
   the fleet side; I confirm it applies to the lane side too, and that all of
   my probes were `--no-lazy-fetch`-safe (grid helpers `object_exists`,
   `object_inventory`, `missing_objects` are all no-lazy-fetch; the auditor
   carries `--no-replace-objects --no-lazy-fetch …` in its `GIT_ISOLATION`,
   `tools/report-landing-audit.py:137-138`). Post-run re-check: the unhydrated
   scratch clones still lack their blobs (lane 3 objects, fleet 7) — no stray
   probe materialised them, so my two exit-2 refusals are genuine and no
   false "clean" could have been produced by materialisation.

## 5. No-acquisition and isolation evidence

`objects_acquired` (inventory diff of `git cat-file --batch-all-objects`
before/after each audit) is **empty in every run**: `{'lane': [], 'fleet': []}`
for all four graded current-arm rows, for all four frozen-arm rows, and for my
four probe variants. No timeout (30 s grid deadline; the auditor's own is
shorter), no `Traceback`, no surviving process bound to a case directory
(`harness_leaks = 0`).

Version-floor check (oracle-supplement-2 `version_constraint`): **observed**, no
`--missing=print-info` and no `--missing-only` anywhere in the pinned source;
the auditor uses the pre-existing primitives only —
`rev-list --objects --missing=print --no-object-names` plus a second
`--filter=blob:none` walk (`tools/report-landing-audit.py:651-677`). No floor
raise.

## 6. Twin comparison and withdrawn expectations

- Grid twin links: `PG05 ↔ PG07`, `PG06 ↔ PG08`; current arm
  `twin_pairs_compared = [PG05, PG06, PG07, PG08]`, `twin_mismatch = []`,
  `twin_equal = true` for every row.
- **My independent pairwise check** of the four normalised verdict documents
  (grid-style path normalisation to `<fleet>`/`<lane>`): all 6 pairs equal.
  The documents are **substantive**, not trivially empty — each contains one
  result row with `report`, `cutoff`, `required`, `round`, `round_commits`,
  `post_report`, `source_url_hashes`, plus the full `summary` block
  (`status: clean`, all `by_kind` counters zero).
- Frozen arm: `PG05` and `PG06` exit **2** with the historical r23 reason
  `could-not-evaluate: …/lane: partial clone (promisor pack)` (metadata class),
  `PG07`/`PG08` exit **0**. `met_frozen = true` for all four (history
  preserved, never a target). The frozen auditor meets the **amended** view on
  **2/4** rows; the two unmet are exactly `PG05-hydrated-blobless-lane` and
  `PG06-hydrated-blobless-fleet` — i.e. the entire repair delta of this family
  is "promisor-marked but locally complete ⇒ ordinary local verdict".
- Withdrawn original expectations: **none in this family.** `PG05–PG08` carry
  no `amended` entry, so `original == amended`; `met_original = true` for all
  four and `withdrawn_original_failures = []`. The withdrawal of
  `expected_after[3]` (unknown-citation ⇒ exit 2) lives in the other seven
  amended rows and is untouched by this family. **Nothing here is relabelled
  passed**: the rows that the amendment changes are not in my selection, and
  the original view of my four rows was met literally (exit 0, no findings).

## 7. Findings — source (`tools/report-landing-audit.py` @ `2e254a1`)

**None.** Evidence:

- No blanket metadata refusal: the two promisor-marked, locally complete
  clones (config promisor + paired `.promisor` marker + real `file://` blobless
  provenance) both audit as ordinary clean runs (exit 0), whereas the frozen
  auditor refused exactly these two with `partial clone (promisor pack)`.
- No blanket full-closure/unknown refusal: the required reads resolve locally
  and the verdicts equal the plain twins' verdicts field for field.
- Refusals, when the required object really is unavailable, are
  **content-derived** and name the object: `unavailable required object:
  <tree>:corpus/SOURCES.md (<blob oid>)` and `unavailable required object:
  .ufo/reports/round-1/kama.md at fleet HEAD (tip tree <oid>)` — no guessed
  empty data, no verdict document on stdout (exit 2 carries the refusal on
  stderr only).
- No acquisition, no transport invocation, no replace-ref substitution, no
  config-caused hang; existing global Git isolation and deadlines preserved.

## 8. Findings — fixture / harness (reported separately from source flaws)

**F1 (medium, robustness / silent degeneracy). The two blobless builders never
assert their own premise.** `build()` computes `premise["lane_missing"]`,
`premise["fleet_missing"]` and the promisor flags, but `run_case()` ignores
them; only `--selftest` checks a premise, for `lane_mark="config"` (not for any
blobless case). Consequence: if `hydrate()` regressed, or the environment's git
stopped honouring `--filter=blob:none`, PG05/PG06 would silently degrade into
"plain clone + promisor config" — i.e. a duplicate of PG01/PG02 — and would
still grade green. Minimal correction (not applied): in
`c_hydrated_blobless_lane`/`c_hydrated_blobless_fleet`, capture the clone's
missing-id list **before** hydration and require it to be non-empty, then after
hydration require `promisor_facts(clone)["promisor_backed"] is True` and
`missing_objects(clone, <root>) == []`, raising `Premise` otherwise.

**F2 (low, fixture clarity / dead parameter). `lane_mark="config"` /
`fleet_mark="config"` are inert for the two blobless cases.** `mark_config()`
is applied to the pre-clone repository, which is then `shutil.move`d to
`lane-origin`/`fleet-origin` and replaced by a fresh
`git clone --filter=blob:none --no-checkout`; the audited clone never inherits
the origin's config. Observed clone config: `remote.origin.promisor=true`,
`remote.origin.partialclonefilter=blob:none`, **no `extensions.partialclone`**
(the origin still carries `extensions.partialclone=origin` and
`remote.origin.url=<absent-remote.git>`). The case is still valid — the
promisor-ness is real, coming from the clone flags plus the paired
`.promisor` marker — but the fixture's own note implies the origin's config
makes the clone promisor-backed, and it does not. Minimal correction: drop the
`lane_mark`/`fleet_mark` argument from the two blobless builders, or state in
the builder comment that the promisor evidence is the clone's own
`remote.origin.promisor` + `.promisor` marker.

**F3 (low, incomplete copy). `hydrate()` copies only the origin's *loose*
objects**, ignoring `objects/pack/*`; the note claims "copying the origin's
object files". With the current builder the origin is always loose, so it
works (observed: closure complete, `missing == []`), but a packed origin would
silently under-hydrate and the case would flip to exit 2. Minimal correction:
also copy the origin's `*.pack`/`*.idx`/`*.promisor`, or assert afterwards that
the clone's object inventory covers the origin's.

**F4 (low, coverage gap in the graded population).** The family pins the
*hydrated* twin of a blobless clone, but the graded table has **no
lane-side unhydrated blobless row** (the fleet side is pinned by
`PG43-fleet-unhydrated-blobless-report-required`). My §2 variant shows the
lane-side unhydrated behaviour is a content-derived exit 2 naming the missing
`corpus/SOURCES.md` blob, which is exactly the amended policy's
"unavailable required object ⇒ exit 2" rule; that behaviour is currently
unpinned for the lane. I did **not** add a row: the fixed-47 population is
L1-owned and adding one would change it.

**F5 (low, harness reporting quirk).** In the *current* arm the grid prints
`amended_view_met = 0 / amended_view_total = 4`, which reads like a failure but
is not one: `baseline` only counts rows with `arm == "frozen"`, so the current
arm's amended-view counters are always `0/N`. The current-arm truth is in
`rows[*].met_amended` (all `true` here) and in `violations = 0`. Minimal
correction: compute the current arm's amended-view counters from the current
rows, or label the counter "frozen baseline".

## 9. Observed vs inferred

Observed (executed, quoted above): grid exit 0 and every per-row exit/kind/
defect/twin/acquisition field; the four frozen-arm refusals with their exact
text; the promisor configs and `.promisor` markers read from the fixture
`.git/config` files; object inventories and `rev-list --objects
--missing=print` missing-id lists; the presence/absence of the `f`,
`corpus/SOURCES.md` and report blobs; the two exit-2 content-derived refusals
of my unhydrated variants; all four sha256 artifact digests; the absence of
`--missing=print-info`/`--missing-only` in the pinned source; the identical
normalised documents.

Inferred (labelled, not claimed as measured): that a future `hydrate()` or git
behaviour change could silently degenerate PG05/PG06 (F1/F3) — this is a
reading of the harness code, not an executed failure; that the lane-side
unhydrated behaviour should be pinned (F4, policy argument).

## 10. Unverified items (explicitly not claimed)

- The **mutation probe** `promisor-mutants.py` (`6e0b9d62…`) was **not**
  executed — outside my assigned bounded selection.
- The **full 47-case grid** and `--selftest` were **not** run — outside my
  selection; my four-row run is the only grid execution.
- The **Git >= 2.45 inherited prerequisite** (open at L0) is not exercised here:
  the environment's git is `2.56.0`. No claim about older git.
- Only `git 2.56.0` was exercised; the blobless construction depends on the
  local transport honouring `uploadpack.allowFilter` (the builder sets it on
  the origin) — not tested against other git versions or transports.
- **No source defect was proved in any other family**; my source section is
  scoped to what these four rows exercise (promisor metadata + locally
  complete closure + twin equivalence + no acquisition).
- I did not verify L1's integration state, the fleet, sibling worktrees or
  `.jj/index`; I touched only my own scratch and my own advice/out paths.
- No tool was installed or updated in this lane (no pacman/uv/cargo/npm
  action): the measurement needed only git and python3 stdlib.

## 11. Files written

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseHydratedTwins.md` (this file).
- Evidence (optional out dir): `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseHydratedTwins/`
  `grid.json` (grid `--json` output), `candidate.json` + `population.json`
  (grid `--out` artifacts), `probe.json` (my independent premise probe),
  `probe.py` (the probe script).
- Scratch (not production): `/fast/scratch/hyaku/kama-r24/falsify/CaseHydratedTwins/`
  (`repo/` pinned clone, `tmp/` TMPDIR, `probe/` my fixture variants,
  `out/` raw run outputs).

## 12. Bottom line for L1

The HydratedTwins family holds at `2e254a1763a9c08aa07fc53081287f506c447d84`:
promisor metadata over a locally complete closure yields the *same* clean
verdict as the plain twins, with no acquisition and no metadata refusal, while
the frozen r23 auditor refuses exactly these two cases — so the family's
measured repair delta is real and correctly attributed. The weaknesses are in
the **fixtures/harness**, not in the audited source: the blobless builders do
not assert their own premise (F1), carry an inert `*_mark="config"` argument
and no `extensions.partialclone` in the audited clone (F2), hydrate loose
objects only (F3), leave the lane-side unhydrated refusal unpinned (F4), and
the current arm prints a misleading `amended_view_met 0/N` counter (F5).

Report: .ufo/waves/round-24/falsify/advice/CaseHydratedTwins.md
