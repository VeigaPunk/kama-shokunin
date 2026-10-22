# CaseOpaqueFake — PG47 opaque-tree-with-unresolved-fabricated-token falsification (round 24)

VERDICT: **HOLDS** for the graded contract. The single assigned cell meets its live
**amended** column under the pinned candidate (exit 2, content-derived could-not-evaluate,
no verdict document, no objects acquired, no metadata refusal), while the **frozen** r23 arm
meets only its frozen column and *fails* the same amended column — so the row measures a real
repair, not a frozen-history artefact. **No source defect was found** in
`tools/report-landing-audit.py` on the surface this family exercises. **Six fixture /
expectation-metadata weaknesses (F1–F6) and one runner reporting quirk (F7)** are reported
separately below; F2 bounds what this row alone can prove, and F1 means the row contributes
nothing to the twin machinery.

Scope: exactly one bounded grid selection —
`python3 tests/report-audit/promisor-grid.py --arm both --case PG47-opaque-tree-with-unresolved-fabricated-token --json`
— run in a pinned scratch clone, plus read-only static reads of the builder / premise /
expectation source and four **benign offline fixtures of my own** (no network, no transport,
no execution payload, no repository program) needed to assert the actual missing/present
objects, the finding/token pairs, the reason identity, the no-acquisition property and the
discrimination the row itself cannot show. No other lane suite, no full grid, no mutation
grid, no execution-bearing probe. PM08 (no-lazy-fetch deletion) was **not** executed — static
only. No production file other than this report and the `out/` artifacts was written;
production `production/.jj/index`, the fleet, sibling lanes, operator config, routing,
services and real object stores were not touched. No tool was installed or updated.

---

## 1. Pins observed (read-only; scratch only)

| item | value |
|---|---|
| scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueFake/repo` — `git clone --no-hardlinks` of `/home/vgpnk/Projects/shokunin/kama-shokunin`, detached at `2e254a1763a9c08aa07fc53081287f506c447d84` (clean tree) |
| production HEAD | `2e254a1763a9c08aa07fc53081287f506c447d84` (identical; read-only check) |
| git | 2.56.0 (observed; the inherited `Git >= 2.45` prerequisite stays open at L0) |
| auditor (current) | `tools/report-landing-audit.py` sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` — matches the briefed source pin `ea51bc35…` |
| runner | `tests/report-audit/promisor-grid.py` sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` — matches `runner b034e159…` |
| manifest | `tests/report-audit/promisor-grid-expectations.json` sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` — matches `manifest d86b7bea…` |
| mutation probe | `tests/report-audit/promisor-mutants.py` sha256 `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` — matches `mutationprobe 6e0b9d62…` |
| grid-reported `expectations_sha256` | `d86b7bea…` (identical to the manifest bytes) |
| grid `population_sha256` | `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` (47 rows, 1 open row) |
| frozen auditor | blob `0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py`, sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` — equals `preregistration.json → derived_from.frozen_auditor_sha256` |

Heavy scratch/temp for every subprocess: `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueFake`.
Nothing was written outside that subtree except this report and the designated `out/` artifacts.

---

## 2. The assigned bounded selection

```
cd /fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueFake/repo && \
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueFake \
python3 tests/report-audit/promisor-grid.py --arm both \
  --case PG47-opaque-tree-with-unresolved-fabricated-token --json
```
**exit 0** (stderr empty, 0 bytes). Same command with `--keep` → **exit 0**.

Per-arm result (grid JSON, `out/CaseOpaqueFake/grid-bounded-PG47.json`):

* **frozen arm** — exit **2**, stdout empty, `document: null`,
  stderr `could-not-evaluate: <lane>: partial clone (remote.origin.promisor)`;
  `met_frozen: true`, **`met_amended_frozen: false`**, `objects_acquired {lane: [], fleet: []}`,
  no traceback / timeout / harness leak.
* **current arm** — exit **2**, stdout empty, `document: null`, `defects: null`, `kinds: null`,
  stderr
  `could-not-evaluate: round 1: unknown: unavailable required object: 0123456789abcdef0123456789abcdef01234567 could be hidden behind the missing tree or commit 2a675c1af91c97c51f5101d6cff10bb797458ab6 in <lane>`;
  `met_amended: true`, `met_original: true`, `objects_acquired {lane: [], fleet: []}`,
  no traceback / timeout / harness leak.
* `violations: 0` in both arms; `withdrawn_original_failures: []`; frozen arm
  `amended_view_unmet: ["PG47-opaque-tree-with-unresolved-fabricated-token"]`.

---

## 3. Axes and results

| # | Axis | Result |
|---|---|---|
| A1 | Assigned command, exit, pinned clone | **PASS** — exit 0, stderr empty, `violations 0` in both arms, 0 tracebacks / 0 timeouts / 0 harness leaks, 1 graded row per arm |
| A2 | Actual missing / present objects asserted | **PASS (observed, independently rebuilt)** — the lane store is missing **exactly one** object id, `2a675c1af91c97c51f5101d6cff10bb797458ab6`, the **non-leaf tree `d`**; the blob under it (`2f62e7ff…`) is **PRESENT** but its *name* is hidden behind the missing tree; the fleet's missing set is **empty**; the fabricated token `0123…4567` exists in **neither** store. The missing set is identical in the two grid-style walks (`--missing=print` and `--filter=blob:none --missing=print`) → the hole is a **tree**, not a leaf |
| A3 | Premise is the one the oracle describes | **PASS** — builder `c_opaque_tree_fabricated_token` = `build(lane_mark="config", opaque_tree=True, fake_notes=True, drop=("opaque_tree",))` (`tests/report-audit/promisor-grid.py:665-667`): the report carries `fake <FAKE>` in its Notes section and the landed section cites the lane commit. The lane is promisor-marked by **config** (`remote.origin.promisor=true`, `extensions.partialclone=origin`, `remote.origin.url=<absent path>`); the fleet is plain |
| A4 | Exact finding / token pairs | **PASS** — the current arm produces **no verdict document** (exit 2, stdout empty), so there are **no** defect pairs, exactly as the amended column requires (`kinds: null`, `defects: null`). The pair the refusal *would* have been is measured directly in my variant B: `("unresolved-full-hash", "0123456789abcdef0123456789abcdef01234567")` |
| A5 | Content-derived reason IDs | **PASS** — the refusal names **both** the unresolved token and the missing tree oid, is in the `unavailable` reason class, starts with `could-not-evaluate:`, and is **not** the r23 metadata refusal (`partial clone (` and `promisor pack` both absent). Frozen arm for contrast: `partial clone (remote.origin.promisor)` |
| A6 | No objects acquired | **PASS (two independent methods)** — grid pin `objects_acquired {lane: [], fleet: []}` on both arms; independently, a **full `.git` fingerprint** (every file: path, size, mtime_ns, sha256) of both audited repositories is **byte-identical before and after** the current-arm run (lane 29 files, fleet 29 files; added 0 / removed 0 / changed 0) — no pack, no loose object, no `FETCH_HEAD`, no alternates. `git status --porcelain` on both repos is empty after the run |
| A7 | Actual twin document comparison | **PASS as a stated gap, not as evidence** — the manifest registers **no twin** for PG47 (`"twin": null`), so the harness computed **nothing**: `twins: None`, `twin_equal: None`, `twin_pairs_in_manifest 0`, `twin_compared 0`, `twin_pairs_compared []` for both arms. The row therefore contributes **zero** twin evidence (see F1) |
| A8 | Original (withdrawn) view kept visible | **PASS** — PG47 is a **supplement-2** row registered *after* the amendment, so its `original` column is byte-equal to its `amended` column (exit 2 / `unavailable`); `met_original: true` is therefore trivially the same statement as `met_amended: true` and **is not** the withdrawn preregistration reading. The withdrawn reading (preregistration `expected_after[3]`) is **not** registered for PG47 and is **not** counted as achieved anywhere in this row; it lives in the snapshot's calibration rows `PG22, PG23, PG24, PG28, PG30, PG34, PG41` (none of them PG47) |
| A9 | Frozen history is not the improvement | **PASS** — in the frozen arm the row **fails** the amended column (`met_amended_frozen: false`, `amended_view_unmet: ["PG47…"]`) while meeting its frozen column (`met_frozen: true`). The r23 base reached exit 2 for the **wrong reason** (promisor metadata); the candidate reaches exit 2 for a **content-derived** reason. Same exit, different contract |
| A10 | Expectation integrity (no post-hoc fitting) | **PASS** — the live manifest's **44 original rows are byte-identical** to `oracle-snapshot-before-inspection.json` (per-case JSON comparison: `differing case rows: []`; `open_rows` identical), and the live file adds exactly the three registered opaque cells **PG46 / PG47 / PG48** → the fixed47 population is *original44 unchanged + 3 independent opaque cells*, as briefed. PG47 was not edited to fit the candidate |
| A11 | The row is load-bearing | **PASS (static + filed receipt)** — `PM10-ignore-opaque-nonleaf-missing` (the mutant that drops the "a missing tree/commit may conceal the dependency names" rule) is attributed to `PG33, PG34, PG46, PG47` (`tests/report-audit/promisor-mutants.py:432`) and the filed build-wave receipt records it as **killed (1) — PG47** (`build/advice/MutationOracle.md:171`): **PG47 is the only cell that kills PM10**. I did **not** re-run the mutation harness (out of scope); that kill map was measured with the build-wave runner (`5e96fa60…`), not with the pinned runner (`b034e159…`) |
| A12 | Lazy-fetch hazard (peer-reported for the blobless family) does not apply | **PASS (observed)** — PG47's marked lane points `remote.origin.url` at `<case dir>/absent-remote.git`, which **does not exist on disk** (`exists_on_disk: no`), and the fleet has no remote at all; so no probe can materialise the dropped tree. Every content-touching probe I ran used `--no-lazy-fetch` explicitly (peer `KamaR23-2.CaseFleetBlobless` reported the hazard for the blobless clone, whose origin *is* reachable at `file://`) |
| A13 | Isolation / deadline preserved | **PASS (static)** — every git call in the auditor goes through the single helper `git()` (`tools/report-landing-audit.py:156-162`) with `GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch", …)` and `GIT_TIMEOUT = 20`; no replace-ref substitution, no lazy fetch, no signature display, a per-call deadline, and a hang is an `EvalError`, never a verdict |

---

## 4. What PG47 alone cannot show — my own benign offline fixtures

PG47 is a single cell whose expectation is *exit 2*, so on its own it cannot distinguish a
correct implementation from several wrong ones (see F2). I therefore rebuilt the fixture
**independently** (my own script, my own repositories, no grid builder, no network) and ran
the **pinned** auditor against four benign variants:

| variant | fixture | auditor result | defects | objects acquired |
|---|---|---|---|---|
| **A** (replica of PG47) | promisor lane, missing non-leaf tree `d` (`2a675c1a…`), blob under it present, fabricated token `0123…4567` in the report Notes | **exit 2** — `could-not-evaluate: round 1: unknown: unavailable required object: 0123…4567 could be hidden behind the missing tree or commit 2a675c1af91c97c51f5101d6cff10bb797458ab6` | none (no document) | none |
| **B** (no hole) | same, but the tree `d` is **present** | **exit 1** | `("unresolved-full-hash", "0123…4567")` | none |
| **C** (unrelated blob hole) | same as B, plus an **unrelated missing blob** (`b2c475fe…`); the blob:none walk reports **no** opaque id | **exit 1** | `("unresolved-full-hash", "0123…4567")` | none |
| **D** (known-present blob cited, hole present) | missing tree `d` present in the store's history, and the landed section cites the **present blob** `56d7b323…` (wrong type for a commit) | **exit 1** | `("landed-unresolved", "56d7b323…")`, `("landed-omitted", "18089c60…")` | none |

What this establishes, beyond the single row:

1. The refusal is **hole-conditioned, not blanket**: without the opaque hole the same
   fabricated token in the same promisor-marked lane is an ordinary **failed** finding
   (variant B). The candidate therefore does **not** implement the withdrawn preregistration
   reading (`expected_after[3]`: "a missing citation in any promisor-backed repository is
   unknown ⇒ exit 2"), and it does not implement a blanket metadata refusal.
2. A **blob-only** hole does not block (variant C): the missing blob is absent from the
   `--filter=blob:none` walk, so the opaque set is empty and the audit keeps its verdict.
3. A **known wrong type** keeps its failed finding **even with an opaque hole present**
   (variant D) — the supplement's `not_unresolved` rule holds on the pinned source.
4. No variant acquired a single object.

Variant A reproduces the grid's fixture **bit-for-bit in the relevant ids** (same missing
tree `2a675c1a…`, same hidden blob `2f62e7ff…`, same lane commit `18089c60…`), because the
fixture is deterministic (fixed author dates `@1000`/`@2000`, fixed contents).

---

## 5. Fixture / expectation-metadata flaws (separate from source findings)

**F1 (medium) — PG47 has no registered twin, so the twin machinery is a no-op for this row.**
The manifest's PG47 entry carries `"twin": null` (as do PG46 and PG48), and the grid's twin
comparison is computed only for manifest-declared pairs (`promisor-grid.py`, the `twin_links`
/ `reverse` / `by_case` block). Observed on both arms: `twins: None`, `twin_equal: None`,
`twin_pairs_in_manifest 0`, `twin_compared 0`. The supplement text itself says a complete
twin exists for PG46 ("The complete twin resolves the blob"), yet **no** opaque row registers
one. Consequence: the no-harm twin property (a marked repository must reach the same
substantive verdict as its complete unmarked twin) is **unmeasured for the whole opaque
family** by the grid; only my independent variants A/B/D carry that evidence. *Minimal
correction (reported, not applied):* register `PG48` (or a complete-twin cell) as PG47's
`twin`, or add a premise/observation assertion that the marked cell's verdict equals the
complete twin's verdict on the shared fields.

**F2 (medium) — PG47's expectation has low standalone discriminating power, and `original`
== `amended`.** The row pins `exit: 2`, `reason_class: "unavailable"`, `names_any_of:
["$fake", "$missing_subtree"]` — an **"any of"** — with a broad reason-class term list
(`missing`, `absent`, `not found`, `unavailable`, …, `promisor-grid.py:57-84`). Consequently
at least three **wrong** candidate behaviours satisfy PG47 as written:
(a) refuse on *every* unresolved citation in a promisor-backed repository (the withdrawn
reading); (b) refuse on *any* missing object as a blanket closure precondition; (c) exit 2
with any message that happens to contain either the token **or** the tree oid. Only the
combination with the sibling opaque cell PG48 (and with PG41/PG22) discriminates (a) from
the candidate. My variants B/C/D supply exactly that missing discrimination for the pinned
candidate. Second, because PG47's `original` column is byte-equal to its `amended` column,
`met_original: true` is **vacuous** for this row: it does not report a withdrawn failure and
must not be read as evidence that the withdrawn expectation was met.

**F3 (low) — the graded JSON never exposes the fixture premise.** `build()` computes
`premise` (`lane_missing`, `fleet_missing`, `lane_promisor`, `fleet_promisor`,
`fake_present`) but `run_case()` does not copy it into the observation, so the emitted
`candidate.json` contains **no** missing/present object set. A reviewer cannot verify from
the graded artifact that the hole was a *tree* (non-leaf) rather than a leaf, nor that the
hidden blob was present — the two facts the whole row turns on. I had to rebuild the fixture
to assert them (§4). *Minimal correction (reported, not applied):* copy `premise` into the
observation row.

**F4 (low) — the premise does not assert the non-leaf classification.** `premise["lane_missing"]`
is a flat list from a root-scoped `rev-list --objects --missing=print` walk; nothing in the
grid asserts that the missing id is a tree/commit rather than a blob, and nothing asserts
that the blob under the missing subtree is still present (PG47's builder drops **only**
`opaque_tree`, so the hidden blob survives). A builder change that also dropped the hidden
blob would silently turn PG47 into PG46's shape (a cited, absent blob) without any premise
failing. *Minimal correction (reported, not applied):* add the opaque/non-leaf walk to the
premise (as `missing_reachable` does in the source) and assert the hidden blob's presence.

**F5 (low) — the notes contradict the columns.** PG46's and PG47's `notes` say *"Registered
after the amendment; there is no separate original reading"*, yet both rows still carry an
`original` block (identical to `amended`). `grade()` reads `expect["original"]` for the
withdrawn-view score, so the withdrawn-view report for those rows is vacuous (F2).

**F6 (info) — manual-probe hazard (corroborated by peer `KamaR23-2.CaseFleetBlobless`).**
Any probe of a kept fixture must pass `--no-lazy-fetch`; in the *blobless* family the
origin is reachable at `file://`, so a stray `git cat-file -e` can materialise the missing
object and silently evaporate the premise. PG47 is **not** exposed (its promisor remote URL
points at a path that does not exist on disk — A12), but the habit is recorded here because
the opaque rows are the ones a reviewer is most likely to poke at by hand.

**F7 (low, runner reporting only; grading unaffected) — the per-arm summary counters are
misleading for the current arm.** `amended_view_met` / `amended_view_total` /
`amended_view_unmet` are computed from the **frozen-arm** rows only
(`baseline = [r for r in graded if r["arm"] == "frozen" and r["met_amended_frozen"]]`), so in
the current arm they read `amended_view_met 0 / 1` and `amended_view_unmet []` **regardless of
the current arm's own result**; the meaningful current-arm score is the per-row
`met_amended: true`. A reader taking the summary at face value would read "0 of 1 amended
rows met" for the arm that actually met it. (Sibling lane `KamaR23-2.CaseCrossRepo` flagged
the same quirk independently.) *Minimal correction (reported, not applied):* compute those
counters per arm.

---

## 6. Source findings — `tools/report-landing-audit.py` (sha256 `ea51bc35…`)

**S1 — no defect found on this surface.** The path PG47 exercises is
`refuse_unknown()` → `unknown_citation()` (exact/prefix match against the store's missing
set) → else `opaque_hole()` (the missing ids reported by a `--filter=blob:none
--missing=print` walk, i.e. the **non-leaf** holes) → `EvalError` naming the token *and* the
hole (`tools/report-landing-audit.py:419-448`, `:651-716`, `:635-650`). It is consulted **only** for a
citation that resolves nowhere, so it is never an unconditional precondition — confirmed
independently by variants B, C and D (§4). The reason is content-derived, the document is
suppressed, nothing is fetched, nothing is written.

**S2 (minor, scope disclosure — not a PG47 failure) — the missing-object diagnosis is
rooted store-wide, not at the pinned root.** `missing_reachable()` walks from
`present_roots()` = **every** present commit/tree/tag object of the store
(`cat-file --batch-all-objects`), not only the audited root; the docstring says so
explicitly ("over all its present objects, reachable or not"). In PG47 the hole lies inside
the pinned root's tree, so **this row cannot discriminate a root-scoped walk from a
store-wide one** — the contested scope is exactly the open row `PG40-missing-cited-unselected-branch-object-promisor`
(manifest `open_rows`, "reported, not graded"), and the filed build-wave receipt records
that `PM07-full---all-missing-gate` **survives** for the same reason (the candidate is
already store-wide, so the mutant is observationally identical). Consequence: an unrelated
dangling tree/commit hole anywhere in an audited store would also make an unresolved citation
unevaluable, with the reason naming that hole. This is the candidate's declared scope, is
recorded as an open row, and is **not** exercised differently by PG47 — I flag it so L1 does
not read PG47 as evidence for or against the scope choice.

**S3 (observation, no defect) — the refusal replaces a would-be failed verdict.** Under
variant B the same citation is an ordinary `unresolved-full-hash` failure; with the opaque
hole present the audit cannot decide, so it refuses instead of asserting absence. That is
the amended contract's "unevaluable" wording (a locally unevaluable citation is *not* a
proved absence) and it matches the supplement's rule, but it means the row can never show
that the fabricated token is genuinely absent — only that local evidence cannot decide.

---

## 7. Commands, exits and findings (exact)

| # | command (cwd) | exit | observation |
|---|---|---|---|
| 1 | `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueFake/repo` | 0 | clone completed ("done.") |
| 2 | `git -C …/repo checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84` | 0 | `HEAD is now at 2e254a1`; `git rev-parse HEAD` → `2e254a1763a9c08aa07fc53081287f506c447d84`; `git status --porcelain` empty |
| 3 | `TMPDIR=…/CaseOpaqueFake python3 tests/report-audit/promisor-grid.py --arm both --case PG47-opaque-tree-with-unresolved-fabricated-token --json` | **0** | frozen: exit 2 (metadata reason), `met_frozen true` / `met_amended_frozen false`; current: exit 2 (content-derived reason naming `0123…4567` **and** `2a675c1a…`), `met_amended true`; `violations 0` both arms; `objects_acquired {lane: [], fleet: []}` both arms |
| 4 | same command with `--keep` | 0 | grid root kept for fixture inspection (fixture inspection re-done independently in §4) |
| 5 | `TMPDIR=… python3 probe.py` (my own benign fixtures A/B/C) | 0 | A: exit 2, no document, `objects_acquired {}`; B: exit 1, `("unresolved-full-hash","0123…4567")`; C: exit 1, same defect, missing blob `b2c475fe…` not opaque |
| 6 | `TMPDIR=… python3 probeD.py` (variant D) | 0 | exit 1, `("landed-unresolved","56d7b323…")` + `("landed-omitted","18089c60…")`, hole present |
| 7 | `TMPDIR=… python3 probeE.py` (no-acquisition fingerprint) | 0 | exit 2; `.git` fingerprint identical before/after (lane 29 files, fleet 29 files; added 0 / removed 0 / changed 0) |
| 8 | read-only: `sha256sum` of auditor / runner / manifest / mutants; `git rev-parse HEAD` (prod, read-only) | 0 | pins in §1; production HEAD identical to the pinned base; production tree untouched by me |

Findings (finding/token pairs), collected:
* PG47 (grid, current arm): **no verdict document** → no defect pairs (matches `kinds: null`, `defects: null`).
* Variant A: no document (exit 2).
* Variant B: `("unresolved-full-hash", "0123456789abcdef0123456789abcdef01234567")`.
* Variant C: `("unresolved-full-hash", "0123456789abcdef0123456789abcdef01234567")`.
* Variant D: `("landed-unresolved", "56d7b323865c731da81e0225cf109d66f0480919")`, `("landed-omitted", "18089c6071793e8be726676c30371c68a837ca48")`.

Snapshot revision / hash: pinned base `2e254a1763a9c08aa07fc53081287f506c447d84`; frozen auditor
blob `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`; grid `population_sha256`
`612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`; manifest
`d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`; source
`ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`.

Observed vs inferred: every claim in §2–§4 and in the findings table is **observed** (executed
above). The statements that a *wrong* candidate could satisfy PG47 (F2), the store-wide
traversal scope (S2) and the PM10 kill attribution (A11, read from the filed build-wave
receipt, **not** re-measured here) are **inferred / read-from-record** and are labelled as
such. No claim of a source defect is made: none was found.

## 8. Files written and unverified items

Written (all absolute, all inside the designated falsify paths):
* this report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseOpaqueFake.md`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseOpaqueFake/grid-bounded-PG47.json`
* `…/out/CaseOpaqueFake/probe_opaque_family.py` (sha256 `240faa40…`), `…/probe_wrongtype_with_hole.py` (`02a3e80e…`), `…/probe_no_acquisition_fingerprint.py` (`62d0cf26…`)
* `…/out/CaseOpaqueFake/probe_variants_ABC.json`, `…/probe_variant_D.json`, `…/probe_variant_E.json`
* scratch clone, fixtures and probe roots: `/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueFake/` (repo, probe, probeD, probeE, out). Nothing outside that subtree was written; **no production source file was modified** and no expectation cell was edited.

No tool installed or updated (no pacman / uv / cargo / npm action; no system upgrade).

Unverified: the other 46 grid cells (PG46 and PG48 belong to sibling lanes; PG40 is an open row, not graded); the mutation harness at the pinned revision (the kill map in A11 was read from the build-wave receipt, measured with the build-wave runner `5e96fa60…`, not the pinned runner `b034e159…`); PM08 (static only, never executed — no-lazy-fetch removal is forbidden by the wave rules); the source-census row count (L1-owned after this stage); the fixed-candidate retest; global absence of external writes; the inherited `Git >= 2.45` prerequisite (still open at L0 — the host's git is 2.56.0 and the source uses only `--missing=print` and `--filter=blob:none`, never `--missing=print-info` / `--missing-only`, so the supplement's version constraint holds statically). No score increase, serving capability, admission, integration or shipping judgement is asserted. This review stops after the assigned bounded attack.

Report: .ufo/waves/round-24/falsify/advice/CaseOpaqueFake.md
