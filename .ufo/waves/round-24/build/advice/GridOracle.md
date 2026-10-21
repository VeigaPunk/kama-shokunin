# GridOracle — round-24 promisor completeness grid (oracle lane)

**Verdict: delivered.** An executable promisor grid (47 graded cells + 1 reported
open cell) with a frozen, per-arm expectation manifest. The L1's 44-case
snapshot is carried byte-identical; three disclosed supplement cells are
appended. The frozen arm (r23 base blob) meets 47/47 expectations; the current
arm was exercised only against the **r23 base** (not against any candidate) and
shows the r23 harm (33 unmet cells, 32 withdrawn original-view failures). No
candidate was inspected, measured or fitted by this lane.

## Files

| what | path (absolute) | sha256 / size |
|---|---|---|
| runner | `/fast/scratch/hyaku/kama-r24/GridOracle/tests/report-audit/promisor-grid.py` | sha256 `037959d9e76706cc24929e1953d70b5de6ae0eb165b16ee407e0c9ebe321390f` (42048 B) |
| manifest | `/fast/scratch/hyaku/kama-r24/GridOracle/tests/report-audit/promisor-grid-expectations.json` | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (45580 B) |
| runner copy | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/GridOracle/promisor-grid.py` | same bytes |
| manifest copy | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/GridOracle/promisor-grid-expectations.json` | same bytes |
| unified patch (both new files) | `…/build/out/GridOracle/promisor-grid.patch` | 2580 diff lines, applies to the base tree |
| population artifact | `…/build/out/GridOracle/population.json` | population sha256 `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` |
| candidate artifact | `…/build/out/GridOracle/candidate.json` | the both-arms run below (current arm = r23 base, **not** the candidate) |
| this report | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/advice/GridOracle.md` | — |

Scratch clone: `/fast/scratch/hyaku/kama-r24/GridOracle` (`git clone --no-hardlinks`
of the lane, HEAD `d1b9d95`, base tool blob `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
= sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`).
No production file of the lane was touched; nothing was committed or pushed.

## CLI and exit contract

```
python3 tests/report-audit/promisor-grid.py [--arm frozen|current|both]
        [--current PATH] [--frozen-path PATH] [--case NAME]... [--json]
        [--out DIR] [--selftest] [--keep]
```

* `--current` defaults to `tools/report-landing-audit.py` beside the lane
  repository; the frozen arm always reads the **blob** `0df800e:tools/report-landing-audit.py`
  out of the repository with `git cat-file` (never a live working-tree path).
* Exit **0** every graded cell of every selected arm met its live expectation;
  **1** at least one did not; **2** could not evaluate (fixture premise,
  harness or environment, including ENOSPC/EDQUOT).
* `--selftest` checks the harness only (11 cases, all ok): unique cell ids,
  builders present, reason classes known, population stability, and the
  premise machinery on a marked-complete and a holed fixture.
* One grid-owned root per run under `/fast/scratch/hyaku/kama-r24`
  (`TMPDIR` honoured only when it is under that path); never `/tmp`.
* `--out DIR` writes `population.json` and `candidate.json`.

### Row schema (per arm, `doc["arms"][<arm>]["rows"]`)

`case`, `kind` (`contract` for the manifest's policy cells, `control` for the
no-harm twins — the vocabulary the mutation runner grades), `row_class` (the
manifest's own kind), `met` (bool, the live view), `met_frozen`, `met_original`,
`met_amended`, `exit`, `expected_exit`, `kinds`, `expected_kinds`, `defects`
(exact `(kind, token)` pairs), `expectation` (frozen/original/amended views),
`document` (the normalised verdict document), `twins`/`twin_equal` (marked
versus unmarked twin equality), `traceback`, `timed_out`, `leaked`,
`stderr_tail`.

Views: **frozen** = r23 base behaviour (history); **original** = the first
registration (preregistration `expected_after[3]` literal) — reported, and
withdrawn for the rows the amendment changes, never counted as achieved;
**amended** = the live policy of `.ufo/waves/round-24/oracle-amendment-1.json`.
The grid grades `frozen` + `amended`.

## Expectation manifest: immutability and chronology

1. The manifest was written **before any candidate existed**; its 44 registered
   cells are byte-identical to the L1's frozen snapshot
   `.ufo/waves/round-24/oracle-snapshot-before-inspection.json`
   (sha256 `1f5a469989b24b6b321b6b9a39533dad00f7e4daba80dca5f1321e888b142b0e`).
   The extension script asserts that identity before writing.
2. `.ufo/waves/round-24/oracle-amendment-1.json` (landed `123640b`) supersedes
   **expectation [3] only**. Its effect is carried in the `amended` view; the
   original reading stays in the `original` view and is reported as
   *withdrawn / not achieved*, never relabelled as passed.
3. `.ufo/waves/round-24/oracle-supplement-2.json` (landed `aacbd520`, before the
   L1 inspected the candidate) adds three **new** cells with their own source
   and rule text; no registered cell was rewritten.
4. No candidate was inspected or executed by this lane. The current arm was
   run against the **r23 base** (the same blob as the frozen arm) to validate
   the harness path only; those numbers are the r23 harm, not a candidate
   result. Chronology note: a work-in-progress candidate's behaviour was
   auto-reported in the wave by the CaseMissingFleetTree lane after the first
   amendment; this lane did not read, run or fit to it.

## Original → amended crosswalk (every diff, with its source)

| cell | original (withdrawn) | amended (live) | source / construction reason |
|---|---|---|---|
| PG22 unknown-citation-incomplete-promisor | 2 (`unavailable-or-unknown`) | 1, pairs `landed-unresolved`+`unresolved-full-hash` | amendment 1: the fabricated token is **not** in the bounded missing set, so it is not known to name unavailable referenced content; the unrelated hole must not refuse |
| PG23 unknown-citation-complete-promisor | 2 (`unknown-citation`) | 1, same pairs | amendment `prospective_expected[0],[3]`: metadata alone never changes the verdict; complete marked = complete unmarked twin |
| PG24 unknown-citation-fleet-promisor | 2 (`unknown-citation`) | 1, same pairs | same, marking side irrelevant |
| PG28 unhydrated-blobless-lane | 2 (`unavailable`) | 0, no defects | L1 crosswalk: "lane unhydrated UNUSED f blobs must not CNE"; the fixture carries no `corpus/SOURCES.md`, so no missing blob is one the audit reads (the required-blob shape stays in PG13 and PG43) |
| PG30 errata-corrected-missing-sha-promisor | 2 (`unknown-citation`) | 0, no defects | amendment: authorized errata matching must keep working; the historical round-20 witness (`0957ce61…` spliced sha) |
| PG34 missing-cited-blob-plain | 1 (`unresolved-full-hash`) | 2 (`unavailable`) | amendment `prospective_expected[2]` applied to **every** store (token-scoped rule): the citation names referenced content the store lacks, so its absence is not proved — the declared non-promisor policy row |
| PG41 unused-missing-blob-fabricated-in-notes-promisor | 2 (`unknown-citation`) | 1 (`unresolved-full-hash`) | amendment: an unrelated unavailable object is not a blanket precondition |
| PG46/47/48 (new) | — (registered after the amendment) | 2 / 2 / 0 | supplement 2 (`aacbd520`): a missing non-leaf tree may conceal dependency names, so an **unresolved** citation is unevaluable; with every citation resolved the clean twin verdict stands |
| PG25 unknown-citation-plain | 1 (both kinds) | unchanged | plain store: absence is provable |
| PG13/15/17/19/21 missing required object | 2 (`unavailable`) | unchanged | expected_after[2]: never guessed absence |
| PG01–PG12, PG26/27, PG29, PG31/32, PG33, PG35/36, PG37, PG38/39, PG42–PG45 | unchanged | unchanged | complete marked = complete unmarked twin; omission stays a finding; unrelated holes never refuse |

Exit-2 form pin applied to **every** current-arm refusal: stderr starts with
`could-not-evaluate:`, stdout carries no verdict document, the reason is
content-derived (never `partial clone (` / `promisor pack`), and the stderr
names the unavailable object id or the required path where the manifest says so.
Reason *classes* are substring bags (`metadata`, `unavailable`,
`unknown-citation`, `unavailable-or-unknown`), never one brittle literal.

## Fixture construction and safety

* Local synthetic fixtures only: fresh `git init -b master` repositories, one
  grid-owned root per run under `/fast/scratch/hyaku/kama-r24`, no network
  transport, no execution marker, no repository program, no remote beyond a
  **nonexistent local path** (`remote.origin.url=<tmp>/absent-remote.git`).
  The only transport used is the local `file://` clone required by the
  blobless-cell specification (`git -c protocol.file.allow=always clone
  --filter=blob:none --no-checkout`); hydration copies the origin's object
  files, never a fetch.
* Every fixture root is checked **before** the first `.git` write: it must be
  inside the grid root and must not exist or must be empty; after `git init`
  the runner asserts `rev-parse --show-toplevel` equals the fixture root
  (r23 M4: a fixture write must never reach an enclosing repository).
* Object paths are derived from `rev-parse --absolute-git-dir`, never from
  `rev-parse --git-path` (which is relative and can retarget the enclosing
  repository — the r23 M4 mechanism).
* Completeness/absence is asserted with `git --no-lazy-fetch rev-list --objects
  --missing=print --no-object-names <root>` (the `?<oid>` lines) plus
  `cat-file -e`; the premise of every cell (promisor marking on/off, the exact
  missing set, the fabricated token's absence) is verified before the auditor
  runs, so a fixture that failed to establish its condition is a harness
  could-not-evaluate (exit 2), never a pass.
* The auditor runs in its own session; the process group is killed in a
  `finally` on every path (the auditor's own 20 s timeout is shorter than the
  grid's 30 s, so the group would otherwise survive — r23 M7). After each cell
  the runner scans `/proc` for processes still bound to the cell directory: a
  survivor is a harness leak → exit 2, never exit 1. Measured: 0 leaks, 0
  timeouts, 0 tracebacks in every run.
* No `--missing=print-info` / `--missing-only` (the supplement's version
  constraint): only `--missing=print`, available since Git 2.45.

## Measurements run by this lane

```
python3 tests/report-audit/promisor-grid.py --selftest            # 11/11 ok
python3 tests/report-audit/promisor-grid.py --arm frozen --json    # 47/47 met, violations 0
python3 tests/report-audit/promisor-grid.py --arm both --json      # frozen 0 violations;
                                                                   # current arm = r23 base:
                                                                   # 33 unmet cells (the harm),
                                                                   # 32 withdrawn original-view failures
```

The open cell `PG40-missing-cited-unselected-branch-object-promisor` (traversal
scope for diagnosing an unresolved token: all refs versus selected roots) is
**reported, not graded**; the r23 base gives exit 2 on it.

## Unrun / unverified

* No candidate measurement: the L1's integrated run with
  `--current <candidate>` is the first execution of the amended view against a
  candidate. This lane's current-arm numbers are the r23 base.
* The retained r23 grid (`tests/report-audit/repo-state-grid.py`) was **not**
  re-run here; its policy-row expectation changes (F06/F23 reason pins, F27,
  T01) are recorded in `build/advice/ConnNoHarm.md` and
  `build/advice/RevBoolean.md`, not applied by this lane.
* The plain-store variants of the three supplement cells (the rule is
  store-independent, but the L1 registered three cells) are not in the
  manifest.
* Mutation sensitivity is MutationOracle's lane; this grid only exposes the
  row schema and the `--case` selector needed for single-cell probes.
* No install was needed; no tool was added or updated (nothing to record for
  the tooling directive).

## Crosswalk for the L1's integrated run

1. `python3 tests/report-audit/promisor-grid.py --arm both --json --out <dir>`
   with `--current` pointing at the candidate: the frozen arm must stay 47/47,
   the current arm must meet the `amended` view; the `original` view's
   failures are reported as withdrawn, not as violations.
2. Any later change to a registered cell must be appended with a named
   rationale and a disclosed revision (never a silent oracle fit). The three
   supplement cells already carry their source (`supplement` section of the
   manifest) and the 44 registered cells are asserted byte-identical to the
   L1's snapshot by `GridOracle-scratch/add_supplement.py`.

**Report:** `.ufo/waves/round-24/build/advice/GridOracle.md`

---

## Correction 1 (L1 source review, after the frozen oracles)

The original report above is preserved unchanged. This section records the
narrow correction and the confirmations the L1 asked for. No expected value
changed; the manifest bytes are unchanged (sha256
`d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`).

**Defect.** `object_exists()` probed availability with a plain
`git cat-file -e` (no `--no-lazy-fetch`, no `--no-replace-objects`). In a real
blobless fixture that probe could reach the promisor remote (a lazy fetch),
i.e. the harness itself could attempt a transport — violating premise
isolation even though the probe only ever asked about the fabricated token
`FAKE`.

**Correction (runner only, sha256 now
`1a785b2866b42b13be9ed160f2425b516c5a57994f9ff7a61f8a643de27a2e5c`):**

1. Every availability probe now carries the auditor's isolation:
   `git --no-lazy-fetch --no-replace-objects -C <repo> cat-file -e <oid>`.
   `missing_objects()` already used `--no-lazy-fetch`; the object-inventory
   probe added below uses it too. No other probe in the runner touches the
   object store.
2. **No-object-acquisition pin, before and after every run.** The runner now
   takes the full object inventory of both audited repositories
   (`git --no-lazy-fetch cat-file --batch-all-objects --batch-check=%(objectname)`)
   immediately before the auditor starts and again immediately after it
   stops, and records the difference per row as `objects_acquired`
   (`{"lane": [...], "fleet": [...]}`). A non-empty difference is a graded
   failure ("the audit acquired objects"), for every cell and both arms: an
   auditor that fetched, or a harness that acquired, is caught mechanically
   rather than inferred from an exit code. Measured on the four cells
   re-checked after the correction (PG01, PG05, PG07, PG28): `objects_acquired
   = {"lane": [], "fleet": []}` in all four.

**Twin comparison: exact target and denominator.** The comparison is
*document equality between a marked cell and its unmarked twin*: the verdict
document the auditor prints (JSON), with the two fixture paths replaced by the
placeholders `<lane>` and `<fleet>`, compared field by field
(`json.dumps(..., sort_keys=True)` equality). The manifest declares **25
distinct twin pairs** (`twin_pairs_in_manifest` in the run summary); a pair is
*comparable* only when **both** sides produce a verdict document — under the
r23 base the marked side refuses (exit 2, no document), so 0 pairs are
comparable in the frozen arm and the comparison is vacuous there. Under a
repaired auditor the marked side produces a document and the pair becomes
comparable; the summary reports `twin_pairs_compared` (the pairs actually
compared) and `twin_mismatch` (the pairs whose documents differ). A mismatch
is a graded failure. The plain-side rows carry the reverse link, so a pair is
checked from both directions.

**Frozen 47/47 is not an improvement baseline.** The frozen column is the r23
base's own historical behaviour measured against itself (47/47 met, 0
violations). It is a regression guard for the *historical* column only: it says
the frozen column of the manifest describes the r23 base, nothing more. The
comparison that matters is the current arm against the **amended** view
(33 cells unmet by the r23 base — the harm), and, inside that arm, the
marked-versus-unmarked twin equality, which is where the repair is actually
claimed.

**Not re-run.** The full suite was deliberately **not** re-run after this
correction (L1 instruction); only `--selftest` and the four cells named above
were executed, all met. The L1's integrated run is the first full execution of
the corrected runner.

**Artifact note.** `candidate.json` and `population.json` in the out directory
were produced by the run **before** this correction (the manifest is
unchanged, so the population hash `612b0a74…` still holds); they therefore
lack the new `objects_acquired` field. The L1's integrated run regenerates
both.

---

## Correction 2 (L1 static harness review, before the first candidate execution)

The original report and Correction 1 above are preserved unchanged. The
manifest bytes are **unchanged** (sha256
`d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`); only the
runner changed (new sha256 in the out directory). No expected value was
changed; one *semantic grade clarification* is disclosed below, as the L1
required.

**(1) The errata ledger was never exercised.** `run_case` computed
`extra = [] if expect.get("errata") else []` — always empty — and
`run_auditor` therefore always appended `--no-errata`. PG29/PG30 (the
authorized errata matching) were audited with the ledger switched off, so the
historical workflow was not tested at all. Fix: the ledger is enabled per
cell (`--no-errata` is passed only when the cell does not use it), decided by
the builder's own flag (`built["errata"]`), never by the manifest, so the
44 registered cells keep their bytes.

*Fixture defect found by that fix:* the spliced token was built as
`lane_commit[:15] + "894ef21bc863486bcb35b56c"` — a **39**-hex string, because
the historical tail was mistyped with one character missing. The auditor's
40-hex scanner therefore never saw it and the cell was vacuously clean. The
tail is now the exact historical remainder
(`0957ce619789d13` + `d894ef21bc863486bcb35b56c` = 40 hex, the round-20 errata
token from `registry/report-landing-errata.tsv`), and the builder now refuses
to build a cell whose spliced token is not 40 hex or which exists in an
audited repository (premise failure ⇒ exit 2). Measured after the fix:
PG29 exits 0 with the **raw** defect
`(unresolved-full-hash, 58866b563cd900dd894ef21bc863486bcb35b56c)` present
and **corrected by the errata row**, and the uncorrected defect set empty.

*Grade clarification (disclosed, not a silent change):* the manifest's
`defects` / `kinds` pins are applied to the **uncorrected** defect set
(defects with an empty `corrected_by`), while the **raw** set (uncorrected +
errata-corrected) is reported per row as `raw_defects` / `raw_kinds`. A cell
whose expectation is "exit 0, no defects" therefore means "no *uncorrected*
defects", and a corrected defect can still be present in the raw document.
This is exactly the L1's "pin uncorrected pairs vs raw pairs separately"; the
registered cells' `defects: []` fields keep their bytes and their meaning.

**(2) Twin mismatches could never fail.** `live_fail` / `frozen_fail` were
computed *before* the twin comparison ran. Fix: the failure lists are now
computed after it, and a pair whose documents differ is a graded failure in
either arm. The exact comparison and its denominator are in Correction 1
(marked cell versus unmarked twin, verdict documents with the fixture paths
replaced by `<lane>` / `<fleet>`, 25 declared twin pairs, a pair comparable
only when both sides produce a document).

**(3) An unknown `--case` ran nothing and exited 0.** Fix: the requested names
are checked against the manifest before anything runs; an unknown name is
`could-not-evaluate: unknown case(s): …` with **exit 2** (measured: exit 2).

**(4) The frozen arm is now also scored against the amended view.** Every
frozen row carries `met_amended_frozen` (graded without the current-arm
exit-2 form check, because the r23 metadata refusal is legitimate history),
and the arm summary reports `amended_view_met` / `amended_view_total` /
`amended_view_unmet`. Measured on the frozen arm (47 cells):

* **16 / 47** cells meet the amended view — **0 / 30 policy cells** and
  **16 / 17 control cells**;
* the single unmet control is PG34 (a plain store whose cited blob is
  missing: the r23 base exits 1, the amended view is exit 2 — the declared
  non-promisor policy change);
* this is the **historical baseline** the repair is measured against, not a
  target. The L1's expected "14/47" differs by two cells from my 16/47: the
  two plain exit-2 cells PG14 and PG16 are counted as met because the r23
  base's own git failure message ("bad file", "not a tree object") falls in
  the `unavailable` reason class, while their marked twins (PG13, PG15) are
  refused on metadata and therefore are not. The exact definition used is
  "exit + kinds + defects + reason class"; the cell list is in
  `amended_view_unmet`.

**Re-run.** The full suite was **not** re-run on the candidate; the frozen arm
was re-run (4 s, 47/47 met on the frozen column, 16/47 on the amended view, 0
tracebacks, 0 leaks, 0 timeouts, 0 objects acquired) and four cells were
probed explicitly (PG29, PG30, PG01, PG07).

---

## Correction 3 (coverage gap found by the MutationOracle sensitivity pass)

Reported by MutationOracle-2 after its pass over the grid: mutant
**PM05-ignore-second-repo survived**. Confirmed and fixed — the gap was in
the grid, not in the runner.

**Defect.** `build()` accepted a `cross_repo=True` option but never read it:
the only occurrences of the name were the two call sites
(`c_cross_repo_found_promisor`, `c_cross_repo_found_plain`). PG26/PG27 were
therefore built exactly like PG07/PG08 (a complete marked/plain pair with the
citation in the lane), so they could not distinguish "resolved in the second
audited repository" from "resolved in the first": a candidate whose lookup
consulted only the first repository still passed both cells, and no other cell
in the 47 exercised cross-repository resolution.

**Fix (fixture only, no manifest change).** With `cross_repo`, the report's
`## Landed changes` section now also cites the **fleet's own commit**
(`fleet: init`, author `fleet`), which exists only in the fleet: the lane
does not hold it, so the citation can only be resolved by consulting the
second audited repository. The builder asserts the premise before the
auditor runs — the token must be absent from the lane and present in the
fleet, otherwise the cell is a harness could-not-evaluate (exit 2) — and
records it as `premise.cross_repo_token`.

**Re-check.**

| cell | fixture | frozen arm (r23 base) | candidate build (AuditRepair, sha256 `b5a5ce8c…`) |
|---|---|---|---|
| PG26-cross-repo-found-promisor | lane promisor-marked, citation only in the fleet | exit 2 (r23 metadata refusal) — the frozen expectation | **exit 0, kinds [], defects []** |
| PG27-cross-repo-found-plain | both plain, citation only in the fleet | **exit 0, kinds [], defects []** | **exit 0, kinds [], defects []** |

Both cells keep their registered expectations (exit 0, kinds []) and the
pristine candidate still meets them; no objects were acquired
(`objects_acquired = {"lane": [], "fleet": []}`). The mutation PM05 is now
killable: a lookup that consults only the first audited repository finds the
cited token missing and the cell exits 1 instead of 0, in both the marked and
the plain twin.

Only PG26/PG27 pass `cross_repo`; the other 45 cells are unaffected, and the
manifest bytes are unchanged (sha256 `d86b7bea…`). The runner's new sha256 is
`d6aa4e74aa1f7dd56167dc8d7e2907642764ea67c8eaf0e419a684f338debdca`.

**Not re-run.** The full suite was not re-run (L1 instruction); the changed
cells, the selftest and the two-cell candidate probe were executed.

---

## Integration receipt (append-only)

Full receipt: `.ufo/waves/round-24/build/out/GridOracle/RECEIPT.md`.

* Final artifacts, frozen: runner `promisor-grid.py` sha256
  `d6aa4e74aa1f7dd56167dc8d7e2907642764ea67c8eaf0e419a684f338debdca`
  (46189 B); manifest `promisor-grid-expectations.json` sha256
  `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`
  (45580 B, unchanged).
* The runner moved from the L1's integrated `cca76aa3…` to `d6aa4e74…` for
  **one** reason: the MutationOracle coverage gap — `build()` accepted
  `cross_repo=True` and never read it, so PG26/PG27 could not separate
  "resolved in the second audited repository" from "resolved in the first"
  and mutant PM05-ignore-second-repo survived. The fix cites the fleet's own
  commit (present only in the fleet) and asserts the premise before the run.
  Reverting exactly those two hunks reproduces `cca76aa3…` byte for byte, so
  the delta is exactly `promisor-grid.cross-repo-fix.patch`.
* No expectation changed; the manifest bytes are unchanged. Bounded evidence:
  selftest 11/11; frozen arm PG27 exit 0 kinds [], PG26 exit 2 (the r23
  metadata refusal = its frozen expectation); the candidate build
  `b5a5ce8c…` meets PG26 and PG27 with exit 0, kinds [], no objects
  acquired. No full suite, no candidate sweep.
* Freeze: the two artifacts are the lane's final state; any later correction
  must be appended with a named rationale and a source, never silently
  applied. The L1 remains the single integration owner; this lane writes no
  production file.

---

## Correction 4 (L1 source diagnosis of the PG46 exit 0)

**The 47-cell manifest is byte-unchanged**: sha256
`d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` — the same
bytes the L1 integrated. Both changes below are in the **runner** and in the
**fixture**, never in the expectation.

**(a) PG46 fixture: the cited blob under the missing subtree was still
present.** `c_opaque_tree_hides_cited_blob` dropped only `opaque_tree` (the
subtree), so the blob itself stayed in the store; the auditor could therefore
*resolve* the cited token (as a blob) and the cell answered exit 0. The
supplement's fixture requires the subtree **and** the cited blob to be absent
("the cited blob d/f is absent but its OID is hidden behind that missing
subtree"). Fix: the cell now drops `("opaque_tree", "hidden_blob")`; the drop
map carries `hidden_blob -> lane`; and the builder asserts the premise before
the auditor runs — with lazy fetching disabled — that the cited hidden blob is
absent from both audited repositories, otherwise the cell is a harness
could-not-evaluate (exit 2). PG47 (fabricated token) and PG48 (all citations
resolved) are unchanged.

**(b) The exit-2 "names the unavailable content" pin was narrower than the
L1's own rule.** The rule is "stderr must name the unavailable object id
(40-hex) **or the required path whose object is unavailable**". The manifest
listed only the *tree object id* for the four tree cells, so a refusal that
names the unread content as a path expression
(`<commit>:corpus/SOURCES.md`, `HEAD:.ufo/reports/round-1/kama.md`) was
rejected even though it carries a 40-hex id *and* the required path. Instead
of touching the frozen manifest, the rule is now implemented in the runner:
the refusal passes when it contains one of the cell's listed ids **or** a
`<oid>:<path>` / `HEAD:<path>` expression whose path is one of the fixture's
declared paths (`corpus/SOURCES.md`, `f`, `.ufo/reports/round-1/kama.md`, …,
recorded per fixture as `paths`). The manifest's `names_any_of` fields are
untouched.

**Bounded verification (no full suite).**

| cell | frozen arm (r23 base) | candidate `b5a5ce8c…` |
|---|---|---|
| PG15-missing-lane-tree-promisor | exit 2, met | exit 2, met |
| PG16-missing-lane-tree-plain | exit 2, met | exit 2, met |
| PG19-missing-fleet-tree-promisor | exit 2, met | exit 2, met |
| PG20-missing-fleet-tree-plain | exit 2, met | exit 2, met |
| PG46-opaque-tree-hides-cited-blob | exit 2, met | **exit 2, met** (was exit 0 with the defective fixture) |
| PG47-opaque-tree-with-unresolved-fabricated-token | exit 2, met | exit 2, met |

`--selftest` 11/11. The five cells MutationOracle reported as unmet by the
pristine candidate are met: four were an over-strict pin of mine and one was a
defective fixture of mine. **No candidate gap remains** in that set.

**New runner sha256** (the manifest hash is unchanged): see the receipt.
