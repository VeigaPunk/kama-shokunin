# CaseConfigTwins — PG01/PG02/PG07/PG08 falsification (kama round 24, pinned `2e254a17`)

**Verdict: HOLDS for the assigned slice (4/4 rows met; no falsification).** The bounded
selection `PG01-complete-lane-promisor-config`, `PG02-complete-fleet-promisor-config`,
`PG07-complete-lane-plain`, `PG08-complete-fleet-plain` meets its live (graded) expectation on the
pinned candidate: exit 0, **no findings**, no reason string at all, no object acquisition, and
**byte-identical verdict documents** for the marked/unmarked twins. The frozen (r23) arm still
refuses the two marked rows with the blanket metadata reason — i.e. the frozen history is met
**and** the live target was missed by the frozen arm, so the improvement is real and not a
history-replay.

No **source** defect was found in this slice. Three **fixture / evidence-labelling** findings
(F1–F3) are reported separately as required; none of them invalidates a row, and none of them
changed an expected cell.

Lane: leaf member (no subagent dispatch). Read-only production.

---

## 1. Pinned base (observed)

| item | value |
|---|---|
| scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/CaseConfigTwins` (`git clone --no-hardlinks` from `/home/vgpnk/Projects/shokunin/kama-shokunin`), detached |
| HEAD | `2e254a1763a9c08aa07fc53081287f506c447d84` (tree `90d19f20e02caf0c7a52e152f020e98e3c416af3`), working tree clean |
| production HEAD (read-only `rev-parse`) | `2e254a1763a9c08aa07fc53081287f506c447d84` — the pinned commit is present in the production repo |
| `tools/report-landing-audit.py` | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` (matches the assignment) |
| `tests/report-audit/promisor-grid.py` | sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` (matches) |
| `tests/report-audit/promisor-grid-expectations.json` | sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (matches) |
| `tests/report-audit/promisor-mutants.py` | sha256 `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` (matches the assignment's mutation-probe id) |
| frozen blob `0df800e8…:tools/report-landing-audit.py` | sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` — **equals** `oracle-snapshot-before-inspection.json → derived_from.frozen_auditor_sha256` |
| manifest population | 47 rows, `population_sha256 = 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` — **equals** the retained `build/out/GridOracle/candidate.json` value (manifest unchanged since the build wave) |
| environment | git 2.56.0, python3 3.14.8, `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseConfigTwins/tmp`; **no tool installed or updated** (nothing was needed) |

Production was not modified: only the append-only artifact paths under
`.ufo/waves/round-24/falsify/{advice,out}/CaseConfigTwins/` were written. `production/.jj/index`,
fleet, sibling lanes, operator config, routing, services and real object stores were untouched.
No network, transport or execution payload was used; the only "transport" is git's local
filesystem access inside the fixture root. **PM08 was not executed** (the retained mutation
artifact records it as `static-only-not-executed`, consistent with the wave rule).

## 2. Exact commands and exit codes

```
# 1) the assigned bounded selection (both arms, exactly these four rows)
cd /fast/scratch/hyaku/kama-r24/falsify/CaseConfigTwins
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseConfigTwins/tmp \
  python3 tests/report-audit/promisor-grid.py --arm both \
    --case PG01-complete-lane-promisor-config \
    --case PG02-complete-fleet-promisor-config \
    --case PG07-complete-lane-plain \
    --case PG08-complete-fleet-plain --json
# exit 0        (stdout = 16 131 bytes of JSON; stderr empty)

# 2) the same four rows with --keep, so the built fixtures stay inspectable (read-only)
TMPDIR=…/tmp python3 tests/report-audit/promisor-grid.py --arm both \
    --case PG01-… --case PG02-… --case PG07-… --case PG08-… --json --keep
# exit 0        (grid_root = /fast/scratch/hyaku/kama-r24/falsify/CaseConfigTwins/tmp/promisor-grid-4938o91u)

# 3) independent direct run (no grid in the loop) with a logging git shim
TMPDIR=…/tmp bash /fast/scratch/hyaku/kama-r24/falsify/CaseConfigTwins/mycheck/check.sh
# audit_rc=0    (stdout = the verdict document; stderr empty; 22 logged git calls)
```

Artifacts of (1)/(2)/(3) are under
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseConfigTwins/`.

**Determinism:** runs (1) and (2) are two independent executions of the same bounded selection.
After normalising the grid-root path that appears inside the *frozen* arm's refusal text, the two
runs differ in **0** of the compared fields (exit, defects, raw_defects, kinds,
objects_acquired, timed_out, traceback, leaked, met_amended, met_frozen, met_original, document,
twin_equal, stderr_tail) across all 8 arm×row observations.

## 3. Views — which one these four rows are graded against

None of PG01/PG02/PG07/PG08 carries an `amended` entry in the manifest, so the grid's
`live = expect.get("amended", expect["original"])` (`promisor-grid.py:830`) grades them against
the **original** row, which for these rows is identical to the amended policy:

```
PG01-complete-lane-promisor-config (policy, builder c_complete_lane_config, twin PG07)
  frozen:   exit 2, kinds null, reason_class "metadata",  defects null
  original: exit 0, kinds [],   reason_class null,         defects []      <-- graded (== amended)
  reason_forbidden: ["partial clone (", "promisor pack"]
PG02-complete-fleet-promisor-config (policy, builder c_complete_fleet_config, twin PG08)  — same shape
PG07-complete-lane-plain  (control, builder c_complete_lane_plain)  frozen exit 0 / original exit 0 / defects []
PG08-complete-fleet-plain (control, builder c_complete_fleet_plain) frozen exit 0 / original exit 0 / defects []
```

**The withdrawn expectation does not touch this family.** The withdrawn prospectively item is
`preregistration.json expected_after[3]` (unknown citation in a metadata-marked repository ⇒
exit 2), and the snapshot's `amendment.amended_rows` lists it as changed for
PG22/PG23/PG24/PG28/PG30/PG34/PG37/PG41 — **none of them in my selection**. For these four rows
`original == amended`, nothing is withdrawn, and the grid's `withdrawn_original_failures`
bucket for my selection is **empty** while `met_original = true` on every row. I therefore claim
nothing about the withdrawn item, and I did not relabel any withdrawn failure as passed.

**Manifest fidelity (no expected cell was touched).** I compared the candidate manifest
(`d86b7bea…`) against the authoritative pre-inspection oracle
(`.ufo/waves/round-24/oracle-snapshot-before-inspection.json`):

* all **44** snapshot rows are **field-for-field identical** to the manifest (0 diffs over
  `kind/builder/policy_ref/notes/frozen/original/amended/twin/reason_forbidden/names_any_of`);
* the **8** `amendment.amended_rows` entries of the snapshot are byte-identical to the
  manifest's `amended` entries;
* the manifest's 3 extra rows `PG46-opaque-tree-hides-cited-blob`,
  `PG47-opaque-tree-with-unresolved-fabricated-token`,
  `PG48-opaque-unused-tree-no-unresolved-token` are exactly the three rows of
  `oracle-supplement-2.json` (expectations 2 / 2 / 0; the two refusals carry
  `reason_class "unavailable"`), added without altering the original 44;
* `population_sha256` is unchanged from the retained build artifact.

## 4. Premise assertions (independently inspected, `--no-lazy-fetch` on every probe)

`c_complete_lane_config` / `c_complete_fleet_config` / `c_complete_lane_plain` /
`c_complete_fleet_plain` all call `build(root, tmp, lane_mark=…/fleet_mark=…)`: one lane commit
(author time 1000) with `corpus/SOURCES.md` + `f`, one fleet init commit (1900) and the fleet
report commit (2000) carrying `.ufo/reports/round-1/kama.md` that cites the lane commit.

Observed in the retained fixture root (`current/000…003`; inspected read-only, evidence copied
into `out/CaseConfigTwins/direct/premise-dump.txt`, and the temporary root deleted afterwards —
it is re-creatable with the command in §2), all probes `--no-lazy-fetch`:

| row | marked store | config actually applied | lane objects / missing | fleet objects / missing |
|---|---|---|---|---|
| PG01 (000) | **lane** | `remote.origin.promisor=true`, `extensions.partialclone=origin`, `remote.origin.url=<…>/absent-remote.git` | 5 / `[]` | 9 / `[]` |
| PG02 (001) | **fleet** | same three keys on the fleet | 5 / `[]` | 9 / `[]` |
| PG07 (002) | none | — | 5 / `[]` | 9 / `[]` |
| PG08 (003) | none | — | 5 / `[]` | 9 / `[]` |

* **Nothing is actually missing** in any of the four fixtures: `rev-list --objects
  --missing=print` reports **no** `?`-prefixed id in any of the eight stores — the premise
  "complete repository, promisor metadata only" is real, not nominal.
* **The four fixtures are content-identical stores.** All four lanes have HEAD
  `58866b563cd900df310588effe79028efc104c33` and the same 5 objects (blobs
  `051975b0ced83169116c235e7691c0a1a8313300`, `56d7b323865c731da81e0225cf109d66f0480919`;
  trees `1c13e47ce9f8088dc933a80123cf6a8ee2fa701d`, `742d4d0bab77465d98175117a92c2d1940c23680`;
  commit `58866b56…`); all four fleets have HEAD `18f93ab89cc2c01b191efa72b0721eb6e023be6b`
  and 9 objects. **Only the promisor config differs** between a marked row and its twin — so any
  verdict difference could only ever come from the metadata. (This also means the peer-reported
  blobless hazard — a reachable `file://` origin that a stray probe can lazy-fetch — does not
  apply here: this family's remote points at a nonexistent local path, so a stray probe would
  fail loudly instead of silently evaporating the premise. My own probes were isolated anyway.)

## 5. Measured observation (current arm, pinned candidate)

| row | exit | defects (kind,token) | raw defects | kinds | objects acquired | traceback/timeout/leak | `met_amended` | twins |
|---|---|---|---|---|---|---|---|---|
| PG01 | **0** | `[]` | `[]` | `[]` | `{lane: [], fleet: []}` | none | **true** | `PG07 → true` |
| PG02 | **0** | `[]` | `[]` | `[]` | `{lane: [], fleet: []}` | none | **true** | `PG08 → true` |
| PG07 | **0** | `[]` | `[]` | `[]` | `{lane: [], fleet: []}` | none | **true** | `PG01 → true` |
| PG08 | **0** | `[]` | `[]` | `[]` | `{lane: [], fleet: []}` | none | **true** | `PG02 → true` |

Arm summaries (selection of four rows): current arm `graded=4, violations=0, tracebacks=0,
timeouts=0, harness_leaks=0, twin_compared=4, twin_mismatch=[], withdrawn_original_failures=[]`;
frozen arm `graded=4, violations=0, amended_view_met=2/4, amended_view_unmet=[PG01, PG02]`.

**Exact finding/token pairs:** the expected pair set is `[]` and the observed pair set is `[]`
(`defects` and `raw_defects` both empty, `kinds == []`). There is no finding to name and no
content-derived reason to name: the current arm's `stderr_tail` is the **empty string** for all
four rows, so the `reason_forbidden` list (`"partial clone ("`, `"promisor pack"`) is
trivially satisfied and the `reason_class`/`names_any_of` checks do not apply (they only bite on
exit 2).

**Actual twin document comparisons (not asserted, computed):** the grid compares the
path-normalised verdict documents, and both directions were compared:

```
PG01 document == PG07 document  → true
PG02 document == PG08 document  → true
PG01 document == PG02 document  → true   (all four are the same JSON)
```

The single document produced by all four rows:

```json
{"errata_invalid": [], "errata_unmatched": [],
 "results": [{"cutoff": 2000, "defects": [], "post_report": [],
   "report": "<fleet>/.ufo/reports/round-1/kama.md", "report_committed": true,
   "required": 1, "round": 1, "round_commits": 1, "source_url_hashes": []}],
 "summary": {"by_kind": {"landed-ambiguous":0,"landed-omitted":0,"landed-section-missing":0,
   "landed-unresolved":0,"unresolved-full-hash":0}, "corrected":0, "defects":0,
   "errata_invalid":0,"errata_rows":0,"errata_unmatched":0,"post_report_commits":0,"reports":1,
   "required_commits":1,"rounds":[1],"status":"clean","uncorrected":0}}
```

Two anti-robbery details in that document, both observed rather than inferred:

* `required = 1` and `round_commits = 1` — the **marked** store was really enumerated and its
  commit really matched the citation. A candidate that "passed" by skipping or downgrading a
  promisor-marked repository would show `required = 0`. The twin rows and the marked rows agree
  exactly on this number.
* `report` names the **actual fleet fixture path** (my direct run:
  `/fast/scratch/…/mycheck/case1/fleet/.ufo/reports/round-1/kama.md`), so the audit ran against
  the repositories it was given — one canonical runtime, no rerouting, no substitution.

## 6. Frozen history is met, but it is not the improvement

The frozen (r23) arm, same fixtures:

```
PG01 → exit 2  "could-not-evaluate: …/lane: partial clone (remote.origin.promisor)"  met_frozen = true, met_amended_frozen = FALSE
PG02 → exit 2  "could-not-evaluate: …/fleet: partial clone (remote.origin.promisor)" met_frozen = true, met_amended_frozen = FALSE
PG07 → exit 0  clean                                                               met_frozen = true, met_amended_frozen = true
PG08 → exit 0  clean                                                               met_frozen = true, met_amended_frozen = true
```

So the r23 blanket metadata refusal is *history* (`met_frozen = true` on both marked rows) and
**fails the live target** (`met_amended_frozen = false` on both). The improvement is measured on
the amended target columns: frozen 2/4 → current 4/4, `violations = 0` in both arms for this
selection. The frozen arm's exit 2 carries `reason_class "metadata"` and the frozen expectation
for PG01/PG02 is exactly that blanket refusal, so the frozen score is not being credited as
progress. The reason strings above are the r23 *metadata* class — exactly what the candidate
no longer emits.

**Static confirmation of metadata blindness (source-side).** The pinned auditor reads
`extensions.partialclone` / `remote.*.promisor` / `remote.*.partialclonefilter` **only inside its
own self-test** (`tools/report-landing-audit.py:1175-1195`); the audit path has no metadata-based
refusal (`check_history_repo` at `:616` checks object format, top level, shallowness and
grafts only). The frozen auditor, by contrast, refuses on exactly that metadata
(`git cat-file 0df800e8…:tools/report-landing-audit.py | grep promisor` → `:457`
`raise EvalError(f"{repo}: partial clone (promisor pack)")` and the config test at `:462-463`).

## 7. Independent no-acquisition / no-transport measurement (outside the grid)

I rebuilt a PG01-equivalent fixture with the candidate's own builder
(`BUILDERS["c_complete_lane_config"]`), put a logging `git` shim first on `PATH` (it logs argv
and execs the real git), and ran the pinned auditor directly with `--no-errata` (the flag the
grid itself uses for this family):

```
audit_rc=0 ; stdout = the verdict document ; stderr = 0 bytes
22 git calls logged:
  calls WITHOUT --no-lazy-fetch ......... 0
  transport-family calls (fetch/fetch-pack/ls-remote/clone/push) ... 0
  invocations containing "remote" or "url" ......................... 0
  calls naming the MARKED lane store .... 12
  calls naming the fleet store ......... 10
  object inventory lane ................ 5 → 5   (byte-identical before/after)
  object inventory fleet ............... 9 → 9   (byte-identical before/after)
  FETCH_HEAD ........................... absent in both stores
  refs ................................. refs/heads/master only (unchanged)
```

Subcommand histogram (all prefixed `--no-replace-objects --no-lazy-fetch`): 6 ×
`cat-file --batch-check`, 2 × `rev-parse --show-prefix`, 2 × `--show-object-format`, 2 ×
`--is-shallow-repository`, 2 × `--git-path info/grafts`, 1 × `show HEAD:.ufo/reports/…`, 1 ×
`rev-parse --verify refs/heads/master^{commit}`, 1 × `rev-parse --verify HEAD^{commit}`, 1 ×
`ls-tree … -- corpus/SOURCES.md`, 1 × `log -z --format=…`, 1 × `log --diff-filter=A …`, 1 ×
`for-each-ref`, 1 × `cat-file blob 051975b0…`.

So: no object was acquired, no transport was invoked, no repository-configured program ran, and
the promisor-marked store was read through the ordinary plumbing path (12 calls) — the verdict is
not produced by ignoring the marked repository.

Source-side corroboration: the pinned auditor has exactly **one** git subprocess site
(`tools/report-landing-audit.py:162`, `subprocess.run(["git", *GIT_ISOLATION, "-C", str(repo),
*args])`), and `GIT_ISOLATION` (`:138`) is prepended to every call, so no internal probe can
materialise an object; the only `git config` write in the whole file is the self-test's
`core.sshCommand` trap at `:1187`, and no audit-path code reads promisor metadata at all.

## 8. Mutation sensitivity for this family (retained evidence, not re-executed)

From the committed `.ufo/waves/round-24/build/out/MutationOracle/sensitivity-promisor-grid.json`
(read-only):

* `PM01-blanket-metadata-refusal` is **killed**, and among the rows that detect it are exactly my
  two policy rows — `PG01` (exit 2 vs expected 0, stderr
  `… partial clone (remote.origin.promisor)`) and `PG02` (same on the fleet). **This family is
  the detector set for the r24 repair.** The two plain controls PG07/PG08 are unaffected by that
  mutant, as a no-harm twin pair should be.
* `PM08-remove-no-lazy-fetch-gate` is recorded `static-only-not-executed`
  (`--no-lazy-fetch present before=True after=True`); I did not execute it, per the wave rule.
* The candidate copy the mutation harness used
  (`.ufo/waves/round-24/build/out/AuditRepair/report-landing-audit.py`) has sha256 `ea51bc35…`,
  **identical** to the committed `tools/report-landing-audit.py` — one canonical runtime, no
  rerouted or divergent build.

## 9. Findings

### F1 — FIXTURE (medium): this family's "exit 0 clean" is only reachable with the errata ledger
### disabled; the fixture lane has no `registry/report-landing-errata.tsv`

The grid runs the auditor with `--no-errata` for every cell that does not exercise the ledger
(`promisor-grid.py:694-699`: `use_errata = bool(built.get("errata"))`, and `run_auditor` appends
`--no-errata` otherwise). The four builders in my family create no errata ledger, so the fixture
lane has no `registry/report-landing-errata.tsv`. My **first** independent direct run — which
omitted `--no-errata`, i.e. the auditor's default flag set — refused:

```
could-not-evaluate: git show 58866b563cd900df310588effe79028efc104c33:registry/report-landing-errata.tsv
in …/lane: rc=128 fatal: path 'registry/report-landing-errata.tsv' does not exist in '58866b56…'
   (audit_rc=2)
```

This is **pre-existing behaviour, not an r24 regression**: the frozen auditor's `load_errata` is
the same (`git cat-file 0df800e8…:tools/report-landing-audit.py` lines 374-384, byte-equivalent to
the current `:530-540`), and it fails the same way on a lane without a ledger. It affects **both
twins identically**, so the twin comparison and the amended expectation are unaffected; it only
means the "exit 0 clean" claim for PG01/PG02/PG07/PG08 is a statement about the **promisor
dimension under `--no-errata`**, not about the auditor's default invocation.

Minimal correction (**fixture-only; not applied — production is read-only for this lane**):
either have `build()` create an empty `registry/report-landing-errata.tsv` in the lane (so the
default flag set exercises the cell), or state in the manifest `notes` that these four rows are
measured with the ledger disabled. **Do not change the expected cells** — the amended expectation
(exit 0, no findings) is right for the promisor dimension and remains untouched.

### F2 — EVIDENCE LABELLING (low): the retained `build/out/GridOracle/candidate.json` is a
### *pre-repair baseline*, not the candidate's grid result

In the pinned commit, `.ufo/waves/round-24/build/out/GridOracle/candidate.json` records
`auditor_sha256 = {"frozen": "da5041a8…", "current": "da5041a8…"}` — **both** arms ran the r23
blob. Its "current" arm therefore shows the blanket refusal (PG01/PG02 exit 2,
`met_amended = false`, 33 violations) — that is the *r23* behaviour measured twice, not the
repaired candidate. It is honest about itself (the digests say so), but the file name
`candidate.json` invites being cited as "the candidate's grid result". My live run of the same
pinned commit with the candidate auditor (`ea51bc35…`) is the candidate-arm measurement, and for
these four rows it is 4/4 met, 0 violations.

Minimal correction (evidence only, no code): when the wave cites a grid result, cite the
`auditor_sha256` map with it, or name the file as the baseline it is. Recorded for L1; nothing
edited.

### F3 — HARNESS REPORTING (low): `withdrawn_original_failures` over-claims withdrawal

`promisor-grid.py:1029-1030` computes the bucket as

```python
withdrawn = [r["case"] for r in rows
             if r["arm"] == "current" and r["met_original"] is False]
```

i.e. **every** failure of the *original* view is filed as "withdrawn", whether or not that row's
original view was actually superseded by an amendment. For PG01/PG02 the original view **is** the
live view (no `amended` entry), so a failure there would be reported as a withdrawal that never
happened — the opposite of the wave's "keep the withdrawn expectation visible, never relabel it
as passed" discipline (here it would relabel an *unmet live* row as withdrawn).

No live impact in my selection: the current arm met the original view on all four rows
(`met_original = true`), so the bucket is empty and `violations` (computed from `met_amended`) is
the authoritative count — nothing is under-counted. Minimal correction (reporting only, not
applied): split the bucket into "original view superseded by an amendment and failed" versus
"original view still live and failed", and count the latter under `violations` as well.

### F4 — NO DEFECT (recorded for completeness): the metadata cannot change a verdict

Static: the pinned auditor reads promisor metadata only in its own self-test (`:1175-1195`); the
frozen auditor refused on it (`:457`, `:462-463`). Dynamic: the marked and unmarked rows are the
same 5/9-object stores with the same verdicts and the same documents (§4, §5). The amended
clause "promisor metadata alone never changes a clean/failed verdict" holds for this family with
no residual doubt.

## 10. Residual risk and verification gaps

* **Only the four assigned rows were executed.** The other 43 rows of the 47-row population, the
  grid `--selftest`, the auditor's own `--selftest` and the mutation probes were **not** run — no
  full-suite storm. In particular I did **not** measure whether the candidate meets the full
  amended population.
* The retained mutation artifact reports `pristine_unmet_cells = [PG15, PG16, PG19, PG20, PG46]`
  — five cells the candidate does not meet, including `PG46` (a supplement-2 opaque row). That is
  **outside my family**; I read the retained artifact but did not re-measure it, and I claim
  nothing about those rows beyond what the artifact says.
* F1's minimal correction was **not** applied and **not** validated on other families; only this
  family's four builders were considered.
* The inherited Git ≥ 2.45 prerequisite (L0-owned) was not exercised: my environment is git
  2.56.0, so the `--no-lazy-fetch` floor was never tested at the boundary.
* The grid's `--keep` fixture root under my scratch was inspected read-only and deleted after the
  evidence was copied into `out/CaseConfigTwins/direct/`; every probe I ran against it used
  `--no-lazy-fetch`.
* Whether the `absent-remote.git` URL of the config-marked fixtures should instead point at a
  *bait* origin (a valid local repo that really holds the objects) so that any acquisition would
  be observable rather than merely failing — the idea raised by a sibling lane — was **not**
  tested here; for this family it is unnecessary, because the stores are complete and nothing is
  fetchable by construction.

## 11. Files written

Production (append-only; nothing else in the repo was touched):

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseConfigTwins.md` — this report
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseConfigTwins/grid.json` — the assigned `--arm both --case … --json` output (exit 0)
* `…/out/CaseConfigTwins/grid.stderr` — empty (0 bytes)
* `…/out/CaseConfigTwins/grid-keep.json`, `…/out/CaseConfigTwins/grid-keep.stderr` — the second, `--keep` run (exit 0) used for premise inspection and for the determinism comparison
* `…/out/CaseConfigTwins/direct/audit.stdout` — the independent direct auditor run's verdict document (exit 0)
* `…/out/CaseConfigTwins/direct/audit.stderr` — empty (0 bytes)
* `…/out/CaseConfigTwins/direct/git-calls.log` — the 22 logged git invocations (no-transport proof)
* `…/out/CaseConfigTwins/direct/lane-objs.before`, `…/lane-objs.after`, `…/fleet-objs.before`, `…/fleet-objs.after` — object inventories around the direct run (5→5, 9→9)
* `…/out/CaseConfigTwins/direct/premise-dump.txt` — promisor config, HEADs, object counts and missing-object lists of the eight stores
* `…/out/CaseConfigTwins/direct/check.sh` — the exact independent check script that produced the above

Scratch (heavy/temporary, outside the repo): `/fast/scratch/hyaku/kama-r24/falsify/CaseConfigTwins`
(clone root, `tmp/` fixture roots, `mycheck/`).

Report: .ufo/waves/round-24/falsify/advice/CaseConfigTwins.md
