# CaseMarkerTwins — round-24 fresh falsification (family: promisor **marker** + plain twins)

**Verdict: HOLDS.** All four rows of the assigned selection meet the *amended*
view under the current arm; the marker signal is live (not inert); the marked
and unmarked twins produce byte-identical verdict documents; no object was
acquired; the r23 base behaviour was reproduced exactly on all four rows and
the repair is measured on the amended view, not on frozen history. No source
defect was found in this family. Three **fixture-level** findings (F1–F3) and
one coverage note (F4) are reported separately below; F1 is the only one that
gates a future extension of the manifest.

---

## 1. Pinned base and provenance

| item | value |
|---|---|
| pinned revision (detached, scratch clone) | `2e254a1763a9c08aa07fc53081287f506c447d84` |
| clone | `/fast/scratch/hyaku/kama-r24/falsify/CaseMarkerTwins` (`--no-hardlinks` from `/home/vgpnk/Projects/shokunin/kama-shokunin`) |
| working tree at HEAD | clean (`git status --short` → only untracked scratch artefacts) |
| auditor (source tool) sha256 | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| grid runner sha256 | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` |
| expectations manifest sha256 | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` |
| mutation probe sha256 | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` |
| frozen r23 auditor sha256 (`0df800e8…:tools/report-landing-audit.py`) | `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` |
| oracle snapshot file sha256 (at pinned rev) | `1f5a469989b24b6b321b6b9a39533dad00f7e4daba80dca5f1321e888b142b0e` |
| population sha256 (47 rows) | `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` |
| environment | git 2.56.0, python 3.14.8 |

All four pinned digests match the values carried in my assignment
(source `ea51bc35…`, runner `b034e159…`, manifest `d86b7bea…`, mutants
`6e0b9d62…`). The frozen r23 auditor digest matches the digest recorded in
the oracle snapshot's `derived_from.frozen_auditor_sha256`.

**Expectation integrity (no fixture fitted to the candidate).**

* The expectations file did **not** exist at the r23 base
  (`git cat-file -e 0df800e…:tests/report-audit/promisor-grid-expectations.json`
  → *absent*), and the 44-case oracle was frozen in commit `f66b226`
  ("freeze independent 44-case oracle before candidate inspection"), i.e.
  **before** the candidate commit `ed1cc3a`.
* The four rows I grade are **byte-identical** to their rows in the freeze
  commit's snapshot: `git show f66b226:.ufo/waves/round-24/oracle-snapshot-before-inspection.json`
  is byte-identical to the pinned copy (`1f5a4699…`), and the JSON
  comparison of all 44 original rows against the current 47-row manifest gives
  `44-case drift: []`.
* The 3 extra rows (`PG46/PG47/PG48`) are the independent opaque supplement
  of commit `aacbd52` (`.ufo/waves/round-24/oracle-supplement-2.json`, 3 rows)
  — added as a supplement, not as a rewrite.
* The pinned manifest and the candidate's build copy
  `.ufo/waves/round-24/build/out/GridOracle/promisor-grid-expectations.json`
  are identical.

---

## 2. Assigned measurement — exact command, exit code

```
cd /fast/scratch/hyaku/kama-r24/falsify/CaseMarkerTwins
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseMarkerTwins/tmp \
python3 tests/report-audit/promisor-grid.py --arm both \
  --case PG03-complete-lane-promisor-marker \
  --case PG04-complete-fleet-promisor-marker \
  --case PG07-complete-lane-plain \
  --case PG08-complete-fleet-plain --json
```
**exit 0** (stdout 16113 bytes, stderr empty).
Artefact: `.ufo/waves/round-24/falsify/out/CaseMarkerTwins/assigned.json`.

Grid summary as observed (not as the harness summarises it):

| arm | violations | amended view met | amended view unmet | twin mismatch | tracebacks | timeouts | harness leaks |
|---|---|---|---|---|---|---|---|
| frozen (r23 base) | 0 | **2 / 4** | `PG03-complete-lane-promisor-marker`, `PG04-complete-fleet-promisor-marker` | none | 0 | 0 | 0 |
| current (`ea51bc35…`) | **0** | see note | none | none | 0 | 0 | 0 |

*Reading note (harness, see F3):* for the **current** arm the manifest's
`amended_view_met` counter reads `0 / 4` **by construction** — that counter is
computed only over the frozen arm (`promisor-grid.py:1031-1039`,
`baseline = [r for r in graded if r["arm"] == "frozen" and r["met_amended_frozen"]]`).
The current arm's pass signal is `violations == 0`; `amended_view_unmet` is
empty and every row carries `met_amended = True`.

---

## 3. Row-by-row observations (current arm)

All four rows: **exit 0**, stderr empty (no reason of any kind, so neither the
r23 metadata phrases nor a guessed empty-data reason), stdout carries a verdict
document, `results[].defects == []`.

| row | builder | marking observed | exit | kinds | defects (kind,token) | amended view | met |
|---|---|---|---|---|---|---|---|
| PG03-complete-lane-promisor-marker | `c_complete_lane_marker` | lane `pack-82f1f971….promisor` paired with `pack-82f1f971….pack`; fleet unmarked | 0 | `[]` | `[]` | exit 0 / kinds `[]` / defects `[]` | yes |
| PG04-complete-fleet-promisor-marker | `c_complete_fleet_marker` | fleet `pack-6702f67d….promisor` paired with `pack-6702f67d….pack`; lane unmarked | 0 | `[]` | `[]` | exit 0 / kinds `[]` / defects `[]` | yes |
| PG07-complete-lane-plain | `c_complete_lane_plain` | none | 0 | `[]` | `[]` | exit 0 / kinds `[]` / defects `[]` | yes |
| PG08-complete-fleet-plain | `c_complete_fleet_plain` | none | 0 | `[]` | `[]` | exit 0 / kinds `[]` / defects `[]` | yes |

Frozen arm (historical baseline, reproduced, not a target): PG03 → exit 2,
`could-not-evaluate: …/lane: partial clone (promisor pack)`; PG04 → exit 2,
`could-not-evaluate: …/fleet: partial clone (promisor pack)`; PG07/PG08 →
exit 0 with a document. `met_frozen` is True on all four rows, i.e. the r23
behaviour is preserved exactly and the repair is an **improvement on the
amended view** (2/4 → 4/4), the delta landing on precisely the two marker rows.

**Withdrawn expectations stay visible.** For this family the amendment changes
nothing: `original == amended` for all four rows (verified by JSON comparison),
so `withdrawn_original_failures` is empty **legitimately**. The original
(pre-amendment) expectation for PG03/PG04 — *exit 0, no findings* — is the row
the r23 base failed and the current arm now **achieves**; it is not relabelled
as withdrawn. Nothing in this family was withdrawn, and no originally
withdrawn failed expectation was suppressed.

---

## 4. Independent assertions (my own checks, not the harness's verdict)

`out/CaseMarkerTwins/verify_marker_twins.py` → **exit 0, 76 checks, 0 failed**
(`out/CaseMarkerTwins/verify.out`). It rebuilds the four fixtures with the
pinned grid's own builders and then asserts, independently:

1. **Actual missing/present objects.** The audited closure is complete in every
   case: harness premise `lane_missing == []` and `fleet_missing == []`, and
   *my own* store-wide traversal (every present commit/tree/tag used as a root,
   `--objects --missing=print`, plus a second `--filter=blob:none` walk, both
   `--no-lazy-fetch`) finds `missing=[] opaque=[]` for lane and fleet in all
   four cases (lane roots 3, fleet roots 7). The fabricated token
   `0123456789abcdef0123456789abcdef01234567` is absent from both stores in
   every case.
2. **The marker is a real, git-conformant marker.** The `.promisor` file is
   `pack-<sha>.promisor` sitting next to `pack-<sha>.pack`/`.idx` — exactly
   git's own convention (vendored git source
   `.ufo/waves/round-24/build/out/SrcPromisorCode/packfile.c.v2.56.0:726-748`:
   for a pack `pack-<hex>.idx` git sets `pack_promisor = 1` when
   `pack-<hex>.promisor` exists). The marker is therefore a **live signal**,
   not inert: the r23 base refused both marked fixtures precisely on it
   (`frozen-audit.py:454-457`, same pairing test).
3. **Content-derived verdicts, not metadata shortcuts.** The verdict document
   is substantive: `cutoff 2000`, `required 1`, `round_commits 1`,
   `report_committed true`, `by_kind` all zero, `errata_unmatched []`,
   `errata_invalid []`, `status clean`. Cross-checked through a second reader
   path (`summary.by_kind` / `summary.uncorrected` / `errata_*`), not only
   through the grader's `results[].defects` reader.
4. **No objects acquired.** Object inventory
   (`cat-file --batch-all-objects`) before/after each audit is identical for
   lane and fleet in all four rows and in both arms: `{'lane': [], 'fleet': []}`.
5. **Actual twin document comparisons.** After path normalisation, the four
   documents are **byte-identical** (one distinct value, hash
   `-8355794781220971072`): PG03 ≡ PG07, PG04 ≡ PG08, and additionally
   PG03 ≡ PG04 ≡ PG07 ≡ PG08. The grid's own `twin_equal` is True for all
   four rows (`twin_compared 4`, `twin_pairs_compared` lists all four) — the
   comparison was not vacuous, because all four cases were selected in the
   same run.
6. **Identity of the twins is real, not nominal.** All four fixtures carry the
   same content: lane commit `58866b563cd900df310588effe79028efc104c33`,
   fleet init `f723c76c41609df00704d93c29bd44408dcbdd2e`, fleet tip
   `18f93ab89cc2c01b191efa72b0721eb6e023be6b`; the fleet report cites exactly
   the lane commit and the `## Landed changes` section is present.

**Non-vacuity probe** (`out/CaseMarkerTwins/probe_nonvacuity.py` → exit 0,
output `probe_nonvacuity.out`). PG03/PG04 alone cannot distinguish
"marker-aware" from "marker-blind always-clean", because both fixtures are
clean. Building the *same* shapes with the report amended (on a copy) to cite
a fabricated token, the current auditor returns **exit 1** with the identical
defect pairs in all three shapes:

```
marked lane (PG03 shape)  exit=1  [('landed-unresolved','0123…4567'),
                                   ('unresolved-full-hash','0123…4567')]
plain  lane (PG07 shape)  exit=1  [identical]
marked fleet(PG04 shape)  exit=1  [identical]
acquired={'lane': [], 'fleet': []} in all three
```

So the exit 0 on a marked store is **content-derived**; there is no
"marked → clean" shortcut. (Manifest row `PG12-omission-marker-lane` — a
marker with a genuine defect — also exists in the fixed47 and closes the same
hole at manifest level; it is outside my assigned selection and I did not run
it.)

---

## 5. Findings — fixture flaws (reported separately from source flaws)

### F1 (LOW→MEDIUM for future manifest growth) — the marker variant cannot be combined with a missing object, so no `marker × hole` row exists

*Observation.* The fixed47 contains exactly two marker rows: PG03 (clean) and
PG12 (omission). There is **no** row combining the marker with a missing
required object or with an unrelated missing object, although the amendment
applies the availability rule to *every* store regardless of metadata
(`oracle-amendment-1.json` prospective_expected[1]/[4]).

*Root cause (builder-level, reproduced twice).* In
`tests/report-audit/promisor-grid.py` the marking block (lines ~398-406)
runs **before** the removal block (lines ~408-427):

* mark-then-drop → `drop_object` (lines 240-245) refuses:
  `Premise: …/lane: object 051975b0ced83169116c235e7691c0a1a8313300 is not
  loose, cannot remove it` (after `mark_markers` the objects live in a pack);
* drop-then-mark → `mark_markers` (line 206) fails:
  `git repack -a -d -q … fatal: unable to read 051975b0ced83169116c235e7691c0a1a8313300`.

So the gap is not a manifest omission alone: the current builder cannot
express the row.

*Minimal correction (NOT applied to production — reported only).* Build the
promisor pack from the objects that **are** present instead of repacking the
whole closure, then write the paired marker:
`git cat-file --batch-all-objects --batch-check=%(objectname)` →
`git pack-objects <gitdir>/objects/pack/pack` → write
`pack-<sha>.promisor` (git's convention, cited above); apply the `drop` list
before the marking so `drop_object` still finds loose objects. No new git flag
is involved — note that `git repack -h` on 2.56 has **no** `--missing`
option, so `repack --missing=…` is not an available route and the
oracle-supplement-2 version constraint (do not raise the Git floor) is
respected. I verified this construction works end to end:
`out/CaseMarkerTwins/probe_marker_holes.py` → exit 0.

*What the source does in the untested combinations (measured, not inferred).*
With the corrected construction the current auditor is metadata-blind and
correct in both combinations:

| probe | exit | reason / verdict | identical to plain twin? |
|---|---|---|---|
| marker + **required** blob missing | 2 | `could-not-evaluate: unavailable required object: 58866b56…:corpus/SOURCES.md (051975b0ced83169116c235e7691c0a1a8313300) in <lane>: git cat-file blob …` — names the missing object and the path it was read from | **yes** (byte-identical to the plain twin's reason after path normalisation) |
| marker + **unrelated** blob missing | 0 | clean, no findings | **yes** |

So F1 is a **coverage gap in the fixture family, not a source defect**: the
source already behaves correctly in both combinations. Recommendation for the
L1: add the two marker×hole rows once the builder can express them; the
expected cells are `exit 2` (content-derived, naming the object) and `exit 0`
respectively, each equal to its plain twin.

### F2 (LOW) — the marker family cannot exercise the transport / lazy-fetch hazard

PG03's marked lane and PG04's marked fleet declare **no remote at all**
(`git remote -v` empty, asserted in all four cases). Consequently "no
transport" for these two rows is guaranteed by the fixture, not by the
auditor's isolation: with no promisor remote there is nothing for a lazy
fetch to reach. The transport trap lives elsewhere — in the auditor's own
selftest (`tools/report-landing-audit.py:1174-1195`, `core.sshCommand` trap
file plus `promisor-remote-is-never-contacted`) and in the *config* family
PG01/PG02, which configures `remote.origin.url` to an absent path (other
reviewers' scope). This is also why the marker family is immune to the hazard
a sibling reported for the blobless family (a reachable `file://` origin plus
one stray non-`--no-lazy-fetch` probe materialises missing blobs): there is no
origin here.

### F3 (LOW, harness readability) — the current arm's `amended_view_met` reads 0/4

`promisor-grid.py:1031-1039` computes the `amended_view_met` counter over the
frozen arm only, so in a `--arm both` JSON the current arm shows
`amended_view_met: 0, amended_view_total: 4` even when every row is met. The
current arm's real pass signal is `violations: 0` / `amended_view_unmet: []`.
A reader who looks only at `amended_view_met` for the current arm will read
total failure. Not a correctness defect (frozen history met is deliberately not
the target), but it should be stated explicitly wherever this JSON is quoted.

### F4 (INFO, coverage dependency) — this family alone cannot kill an "always clean for marked stores" mutant

Both marker fixtures are clean, so PG03/PG04 alone do not distinguish
"marker-aware and correct" from "marker-blind and always clean". I closed
this with the non-vacuity probe of §4 (marked and plain shapes fail
identically on a fabricated citation). At manifest level the same closure
comes from `PG12-omission-marker-lane` (marker + omission ⇒ exit 1
`landed-omitted`), which is in the fixed47 and is in another reviewer's
selection. The mutation manifest agrees: `PM01-blanket-metadata-refusal`
lists `PG03, PG04, PG07, PG08` among its `expect_rows`, and its semantic names
the paired `.promisor`+`.pack` signal explicitly
(`tests/report-audit/promisor-mutants.py:251-261`).

---

## 6. Source flaws

**None found in the MarkerTwins family.** The current auditor contains **no**
promisor inspection at all: `check_history_repo` refuses only a non-sha1
object format, a non-top-level repo, a shallow repository and an effective
grafts file, with the explicit comment *"A partial clone is not a refusal:
what it declares changes no verdict, only the availability of the objects it
can serve decides"* (`tools/report-landing-audit.py:616-633`). Every git call
runs under `GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch", …)`
(line 138), so no lazy fetch, replace substitution or signature verification
is reachable. The verdict therefore cannot be conditioned on promisor
metadata, which is exactly what the amended contract demands, and it is
confirmed empirically by the identical marked/plain documents of §4.5.

---

## 7. Residual risk / verification gaps

1. **Untested combination.** `marker × missing object` is not in the fixed47
   (F1). The source was measured there by a scratch probe and behaves
   correctly, but no *manifest row* enforces it; a future candidate could
   regress there without any row noticing.
2. **Transport hazard not covered by these rows** (F2) — covered elsewhere
   (auditor selftest trap, config family), not here.
3. **Only git 2.56.0 was exercised.** The inherited Git ≥ 2.45 prerequisite
   remains open at L0; nothing in this family depends on a post-2.45 flag
   (`--no-lazy-fetch` is the only floor-relevant flag, already in the frozen
   base), and my F1 correction deliberately avoids `--missing=*` options that
   the supplement forbids.
4. **`amended_view_met` misread risk** (F3) for downstream report writers.
5. **PG12 was not run** (outside my bounded selection); my §4 non-vacuity
   probe substitutes for it inside this family but is not a manifest row.
6. **The `open_rows` entry `PG40-missing-cited-unselected-branch-object-promisor`**
   is reported-not-graded by the manifest and was not touched here.

---

## 8. Files written (this reviewer only; no production file was modified)

* `.ufo/waves/round-24/falsify/advice/CaseMarkerTwins.md` (this report)
* `.ufo/waves/round-24/falsify/out/CaseMarkerTwins/assigned.json` — the exact
  assigned grid run (`--arm both --json`), exit 0
* `.ufo/waves/round-24/falsify/out/CaseMarkerTwins/assigned.err` — empty (stderr)
* `.ufo/waves/round-24/falsify/out/CaseMarkerTwins/verify_marker_twins.py`
  and `verify.out` — the 76-check independent verification (exit 0, 0 failed)
* `.ufo/waves/round-24/falsify/out/CaseMarkerTwins/probe_nonvacuity.py` and
  `probe_nonvacuity.out` — marked vs plain under a genuine defect
* `.ufo/waves/round-24/falsify/out/CaseMarkerTwins/probe_marker_holes.py` and
  `probe_marker_holes.out` — marker × hole combinations (F1)
* `.ufo/waves/round-24/falsify/out/CaseMarkerTwins/frozen-audit.py` — the r23
  base auditor blob used for the historical arm
* `.ufo/waves/round-24/falsify/out/CaseMarkerTwins/grid-out/` — the grid's own
  `population.json` / `candidate.json` from the `--out` variant

Scratch only: `/fast/scratch/hyaku/kama-r24/falsify/CaseMarkerTwins/`
(clone + fixtures + `TMPDIR` for every subprocess). Nothing in
`production/.jj/index`, the fleet, sibling lanes, operator config, routing,
services or any real object store was touched; no network or transport was
used; no tool was installed or upgraded in this review.

Report: .ufo/waves/round-24/falsify/advice/CaseMarkerTwins.md
