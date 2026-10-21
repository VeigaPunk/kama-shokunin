# CaseMarkerLane — round-24 offline oracle case

Lane: `KamaR23-2.CaseMarkerLane-2` · base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
· date 2026-10-21 · scope: one offline oracle case (leaf member, no subagents).

## Verdict

**Specified and measured.** The case is fully determined before any
implementation exists: a lane repository that is *complete* but carries git's
partial-clone pack marker (`.promisor` paired with its `.pack`), with **no**
promisor remote config, must audit to the **clean verdict of the otherwise
identical full clone** — exit `0`, no findings. The base (r23) refuses it
with exit `2` (`partial clone (promisor pack)`); that refusal is the harm
this case pins down.

**This case must be graded together with a genuinely-incomplete promisor
lane.** Measured below: a repair that only stops refusing on the marker
turns unavailable evidence into a *failed* verdict on the incomplete lane.
Graded alone, this case would pass that wrong repair.

## Case specification (fixed before implementation)

| item | value |
|---|---|
| case name | `C14-promisor-marker-complete-lane` (variant `C15-…-omission`) |
| fixture | complete lane repo (all objects local) + `objects/pack/pack-<sha>.promisor` next to the real `pack-<sha>.pack`/`.idx` |
| promisor remote config | **absent** — no `extensions.partialclone`, no `remote.*.promisor` (also no `remote.*.partialclonefilter`) |
| fleet | plain, unmodified; report cites the lane commit |
| expected exit | `0` (clean) — source: the **full-clone twin**, not an assumption |
| expected findings | `[]` (no defect kinds) — same source |
| variant expectation | omission variant → exit `1`, kinds `["landed-omitted"]` — source: the omission twin |
| grading requirement | marked lane must equal its twin **exit and finding set**; "merely not exit 2" is not sufficient |
| pairing requirement | graded in the same arm as `F23-promisor-pack-without-config` (`tests/report-audit/repo-state-grid.py:195`, row at `:670`) |
| forbidden | no network transport, no repository program executed, no candidate/full suite run |

Expected values are **observed from the twin**, not asserted: the twin is the
same commit graph, the same report and the same fleet with the marker file
removed, audited by the same binary in the same run
(`evidence.json` → `A_full_clone_clean` exit 0 kinds `[]`;
`C_full_clone_omission` exit 1 kinds `["landed-omitted"]`).

## Measurements (base `0df800e`, auditor blob `da5041a8…65af1`)

`python3 .ufo/waves/round-24/build/out/CaseMarkerLane/case_marker_lane.py`
→ `evidence.json`; git `2.56.0`, python `3.14.8`.

| observation | premise | base exit | base kinds | expectation (r24) |
|---|---|---|---|---|
| `A_full_clone_clean` (twin, no marker) | ok | `0` | `[]` | — (source of truth) |
| `B_marker_lane_clean` (**the case**) | ok | **`2`** | — | exit `0`, kinds `[]` |
| `C_full_clone_omission` (twin) | ok | `1` | `["landed-omitted"]` | — (source of truth) |
| `D_marker_lane_omission` | ok | **`2`** | — | exit `1`, kinds `["landed-omitted"]` |
| `E_marker_lane_transport_sentinel` | ok | `2` | — | exit `0`, **no transport invoked** |
| `F_marker_removed_ablation` | ok | `0` | `[]` | — (see below) |
| `G_git_behaviour_parity` | — | — | — | marked ≡ twin on every auditor git read |

Base stderr for B/D/E, verbatim:
`could-not-evaluate: <lane>: partial clone (promisor pack)`

**B/D/E are the r23 harm**: a complete, fully-cited, clean lane is refused
as "could not evaluate" purely because of a metadata file.

### Premise evidence (each case, `evidence.json → observations.*.premise`)

* `no_missing_objects` — `git rev-list --objects --all --missing=print`
  yields **no** `?`-prefixed line (git's own missing-object machinery).
* `all_reachable_objects_local` — every reachable object id is in
  `git cat-file --batch-check --batch-all-objects` (3 objects clean fixture,
  6 with the extra omission commit).
* `cited_commit_present`, `cited_blob_present` — the cited commit and its
  blob resolve locally.
* `no_partialclone_config`, `no_promisor_remote_config`, `no_promisor_config`
  — the lane's config carries **no** promisor key at all.
* `pack_exists`, `idx_exists`, `promisor_exists`, `promisor_paired` — the
  marker is a *paired* `.promisor`/`.pack`/`.idx` triple, not an orphan file
  (the orphan case, `C10`, is already a passing control at
  `repo-state-grid.py:545` and is **not** this case).

### Realism premise

`git clone --filter=blob:none --no-local file://<src>` makes git itself
write `pack-c97e1b49….promisor` next to `pack-c97e1b49….pack`
(`evidence.json → observations.git_paired_marker_layout`,
`paired_layout: true`). The hand-built marker in the case reproduces git's
own partial-clone layout exactly, so the fixture is not a synthetic shape
git would never produce.

### F — marker-removal ablation (what exactly blocks the verdict)

Same marked lane, **only** the `.promisor` file removed (every other byte
unchanged) → exit `0`, kinds `[]`. So the exit-2 is caused by the marker
file alone, not by any other property of the repository.

### G — git-behaviour parity with the marker present

With the marker present, every git read the auditor performs returns
**byte-identical** output to the twin: `rev-parse --show-object-format`,
`--show-prefix`, `--is-shallow-repository`, `--verify
refs/heads/master^{commit}`, `log -z --format=%H%x00%an%x00%at%x00%s`,
`cat-file --batch-check` (plain and `^{commit}`), and the cited commit id is
the same object in both. A repaired auditor therefore reaches the twin's
verdict with the marker in place; the marker changes *metadata*, not git's
answers about present objects.

### E — no transport, no repository program

The marked lane was given `remote.origin.url=ssh://example.invalid/x.git`
and `core.sshCommand="touch <sentinel>; false"`; the sentinel file was
**never created** (`transport_ran: false`). With `--no-lazy-fetch`
(`tools/report-landing-audit.py:93`) and no promisor remote configured,
nothing can be fetched. (The base never got that far — it refused first.)

## Discriminator: this case cannot stand alone

`python3 .ufo/waves/round-24/build/out/CaseMarkerLane/naive_repair_probe.py`
→ `evidence-naive-repair.json`. Fixture: git's own blobless clone with the
promisor config keys unset — paired marker present, cited **blob genuinely
absent**.

| observation | exit | kinds | meaning |
|---|---|---|---|
| base r23 | `2` | — | `partial clone (promisor pack)` (r23 blanket refusal) |
| refusal ablated (naive repair) | **`1`** | `["unresolved-full-hash"]` | **wrong verdict**: unavailable evidence reported as proved absence |
| contract truth | `2` | — | required object unavailable → could-not-evaluate |

Consequence for the grid: the round-24 repair cannot be "delete the marker
refusal". It must (a) stop letting the marker alone decide the verdict and
(b) establish availability of the required objects. Row `F23` must keep exit
`2`, and its pinned reason (`repo-state-grid.py:704`, `"promisor pack"`)
must change to an availability-based reason — a reason pin that still names
the marker would make the repair untestable.

## Base code responsible (for the repair lane)

* `tools/report-landing-audit.py:454-457` — marker refusal
  (`p.suffix == ".promisor" and p.with_suffix(".pack").exists()` →
  `EvalError("partial clone (promisor pack)")`).
* `tools/report-landing-audit.py:458-465` — config refusal
  (`extensions.partialclone`, `remote.*.promisor`).
* `tools/report-landing-audit.py:93-96` — `GIT_ISOLATION`
  (`--no-replace-objects`, `--no-lazy-fetch`, log/signature suppression) —
  must survive the repair unchanged.
* Note the asymmetry to preserve: the *config* refusals (a promisor remote
  that can supply objects) are a different claim from the *marker* file.

## Drop-in grid fragment (candidate, not production)

`.ufo/waves/round-24/build/out/CaseMarkerLane/grid_fragment.py` — builders
`c_promisor_marker_complete_lane` / `c_promisor_marker_complete_lane_omission`
written against the round-23 grid's helper names (`pair`, `commit`,
`publish`, `report`, `g`, `require`), plus the suggested rows:

```
("C14-promisor-marker-complete-lane", "control",
 c_promisor_marker_complete_lane, 0, []),
("C15-promisor-marker-complete-lane-omission", "control",
 c_promisor_marker_complete_lane_omission, 1, ["landed-omitted"]),
```

Validated against the **existing** grid module without running its suite
(`validate_fragment.py` → `evidence-fragment-validation.json`): the
fragment's builders run under `repo-state-grid.py`'s own `run_case`
against the base auditor and give `twin-base-clean` exit `0` kinds `[]`,
`C14` exit `2` (`partial clone (promisor pack)`), `C15` exit `2` — i.e. the
fragment is syntactically and semantically drop-in, and the base fails
exactly the two rows the repair must flip.

## No fixture escaped scratch

* All fixtures built under `/fast/scratch/hyaku/kama-r24/CaseMarkerLane/`
  (run dirs `20261021T175525Z`, `…175543Z`, `…175626Z`, `…175654Z`).
* The one validation run that used `tempfile` was re-run with
  `TMPDIR=/fast/scratch/hyaku/kama-r24/CaseMarkerLane/tmp`; `/tmp` holds no
  `case-marker-*` leftovers (`ls -d /tmp/case-marker-*` → none).
* `git status --porcelain` in the lane checkout: only untracked
  `.ufo/waves/round-24/build/` (this lane's out dir) — **no tracked
  modification** (`git diff --stat` empty); the base auditor blob is
  unchanged (`da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`
  = `git cat-file blob 0df800e:tools/report-landing-audit.py`).
* No commit, no push, no `.jj`/index write, no fleet/sibling/operator
  config touched; no network transport; no repository program executed
  (sentinel absent).

## Artifacts (all under the lane's own out dir)

* `build/out/CaseMarkerLane/case_marker_lane.py` — fixture builder +
  premise checks + twin/ablation/parity observations.
* `build/out/CaseMarkerLane/evidence.json` — the observation record above.
* `build/out/CaseMarkerLane/naive_repair_probe.py` +
  `evidence-naive-repair.json` — the discriminator.
* `build/out/CaseMarkerLane/grid_fragment.py` — drop-in grid fragment.
* `build/out/CaseMarkerLane/validate_fragment.py` +
  `evidence-fragment-validation.json` — fragment validation against the
  existing grid helpers.

## Verification gaps (unrun = unverified)

* **No repaired auditor exists yet**, so the r24 expectation (exit 0 /
  kinds `[]`) is untested against an implementation; it is derived from the
  twin by construction.
* The candidate and full suites were **not** run (out of scope for this
  lane); the fragment validation executed only my own two builders plus the
  grid's `base()` twin through `run_case`.
* Fleet-side marker (the sibling case) is out of this lane's scope.
* A **promisor remote present** (config refusals at `:458-465`) was not
  exercised here — `remote.*.promisor` / `extensions.partialclone` remain
  refusals in the base and belong to the other cases.
* Marker file **content** other than zero bytes, several markers in one
  pack directory, and `objects/info/alternates` interplay with the marker
  were not tested.
* Real-network behaviour, signature verification and replace-refs were
  deliberately not exercised (offline fixture only).
