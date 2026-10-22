# DocExpectationBinding — round-24 falsification

**Target.** The 47-cell expectation manifest
`tests/report-audit/promisor-grid-expectations.json` against the frozen 44-case
oracle snapshot + the 3-cell independent supplement: are the expectation
fields unchanged, which corrections are runner/fixture-only, and are the strong
`names_any_of` refusal pins preserved?

**Verdict: HOLDS on the core binding; PARTIAL on two binding gaps and one
receipt defect.** No expectation field of the 44 frozen cells was changed and
no fit-to-candidate was found; the strong OID refusal pin is intact in the
pinned runner. Three residual defects are reported below (F1, F2, F3 — F3 is a
documentation/byte-count defect in the build-lane receipt) plus two residual
risks (F4, F5). No production file was edited; every measurement was made in a
private scratch clone.

---

## 1. Snapshot under test

| artifact | path | sha256 | bytes |
|---|---|---|---|
| pinned commit | `2e254a1763a9c08aa07fc53081287f506c447d84` (production HEAD, worktree clean for all six files below) | — | — |
| manifest (47 cells) | `tests/report-audit/promisor-grid-expectations.json` | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | 45580 |
| runner | `tests/report-audit/promisor-grid.py` | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | 46583 |
| candidate auditor | `tools/report-landing-audit.py` | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | — |
| frozen oracle (44) | `.ufo/waves/round-24/oracle-snapshot-before-inspection.json` | `1f5a469989b24b6b321b6b9a39533dad00f7e4daba80dca5f1321e888b142b0e` | 40110 |
| oracle supplement (3) | `.ufo/waves/round-24/oracle-supplement-2.json` | `4600a8c3951d26b68ee2562d5967cecfe9b00d66443ac10e6d371956e5d34368` | 2337 |
| oracle amendment | `.ufo/waves/round-24/oracle-amendment-1.json` | `930b087a218f880a55c4507b7f11309eae130e2b5dd2111e27d5653b39c8f82f` | 2337 |
| preregistration | `.ufo/waves/round-24/preregistration.json` | `6dde0d72343c9b8e64ec6e3ae4c9b382dfa3daaf9d0f6afd3f274cfac30e844c` | — |
| frozen auditor (r23) | `0df800e:tools/report-landing-audit.py` | `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` | — |

All four oracle files are **byte-identical between the pinned commit and the
production worktree** (`git cat-file blob 2e254a1:<path> | sha256sum` ==
`sha256sum <production path>` for all four): no post-freeze drift of the
oracle. The manifest's own `derived_from.frozen_auditor_sha256`
(`da5041a8…`) matches the real r23 blob, verified independently — the one
digest pin the manifest carries is true.

Scratch clone (read-only against production): `/fast/scratch/hyaku/kama-r24/falsify/DocExpectationBinding/repo`,
`git clone --no-hardlinks` + `git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84`.
`TMPDIR` for every subprocess = `/fast/scratch/hyaku/kama-r24/falsify/DocExpectationBinding`.

---

## 2. Exact commands, exits, findings

| # | command (cwd = scratch repo unless stated) | exit | finding |
|---|---|---|---|
| 1 | `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin repo && cd repo && git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84` | 0 | `HEAD=2e254a1…`, worktree clean |
| 2 | `sha256sum tests/report-audit/promisor-grid-expectations.json tests/report-audit/promisor-grid.py tests/report-audit/promisor-mutants.py tools/report-landing-audit.py` | 0 | manifest `d86b7bea…`, runner `b034e159…`, mutant probe `6e0b9d62…`, auditor `ea51bc35…` — all four match the pins named in the lane contract |
| 3 | `git cat-file blob 0df800e:tools/report-landing-audit.py \| sha256sum` | 0 | `da5041a8…` == manifest `derived_from.frozen_auditor_sha256` |
| 4 | python3 deep-compare of `manifest["cases"]` (47) vs `snapshot["cases"]` (44) by id and by field | 0 | **0 field differences** across all 44 shared ids; `calibration` equal; `open_rows` equal; `views`/`amendment` equal; manifest-only ids = exactly `PG46/PG47/PG48`; case **order** identical for the 44 |
| 5 | python3 compare of the 3 supplement rows (`expected_exit` 2 / 2 / 0) vs manifest `amended` views of PG46/PG47/PG48 | 0 | exact match: PG46 exit 2 `reason_class=unavailable`, PG47 exit 2 `unavailable`, PG48 exit 0 `kinds=[] defects=[]` |
| 6 | python3 cross-check of `amendment.amended_rows` (8 keys) vs the per-case `amended` keys | 0 | consistent; PG37 `null` ⇒ no `amended` key ⇒ live view = `original` (as the snapshot's `views` text requires); PG40 open row and PG46–48 carry their own `amended` keys as expected |
| 7 | `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/DocExpectationBinding python3 tests/report-audit/promisor-grid.py --arm both --case PG46-opaque-tree-hides-cited-blob --case PG47-opaque-tree-with-unresolved-fabricated-token --case PG48-opaque-unused-tree-no-unresolved-token --json --out <scratch>/out` | **0** | 3/3 graded rows met in **both** arms; `violations=0/0`; `expectations_sha256=d86b7bea…`; `population_sha256=612b0a74…`; `population_size=47`; `objects_acquired {"lane":[],"fleet":[]}` in every row (no lazy fetch, no acquisition) |
| 8 | same run, current arm stderr tails | — | PG46: `could-not-evaluate: round 1: unknown: unavailable required object: 2f62e7ff9e9e4c2e972dab0989d414e027012348 could be hidden behind the missing tree or commit 2a675c1af91c97c51f5101d6cff10bb797458ab6 …`; PG47: same shape naming `0123456789abcdef0123456789abcdef01234567` + tree `2a675c1a…`; PG48: exit 0, empty stderr, `defects=[]` |
| 9 | same run, **frozen** arm (r23 base blob) on PG46/47/48 | — | all three exit 2 with `partial clone (remote.origin.promisor)` ⇒ the manifest's *unbacked* "frozen" view for the three supplement rows (exit 2, `reason_class=metadata`) is **true**, measured, not assumed |
| 10 | `diff -u .ufo/waves/round-24/build/out/GridOracle/promisor-grid.py tests/report-audit/promisor-grid.py` | 1 (diff) | 46 changed lines; the delta is exactly: drop module-level `import re`, drop the per-fixture `paths` key, drop `PATH_EXPR` + `names_unavailable()`, revert `check_exit2_form`/`grade()`/`run_case` to the OID-only pin, plus two comment rewordings. **No path-based acceptance remains.** |
| 11 | python3 population-digest recomputation from the oracle files alone | 0 | digest over the 44 frozen rows computed from `oracle-snapshot-before-inspection.json` **alone** = `94eda3acb2d28a59eb40b518c898eb01e13073081b9206803dfbbcf5ba1d3d34`; the same digest computed from the manifest's 44 rows is identical ⇒ the binding is independently reproducible; the runner's 47-row digest is `612b0a74…` |
| 12 | `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD; git status --porcelain -- <the six files>` | 0 | production HEAD is still `2e254a1…`; all six files clean in the worktree |
| 13 | grep for `PATH_EXPR\|names_unavailable\|"paths"` in the pinned runner | 1 (no match) | the declined path-expression relaxation is absent; `import re` at line 277 is the local import inside `re_fullmatch_remote`, unrelated |
| 14 | grep `expectations_sha256\|population_sha256` in the pinned runner | 0 | the run summary records the manifest digest (line 955) and the population digest (line 958) |

Evidence file: `.ufo/waves/round-24/falsify/out/DocExpectationBinding/grid-3case-supplement.json`
(sha256 `ca258165e1a51ae1a17c4c79a6b109388f11cb01474715e963d2b3548ad30b5d`) and
`.ufo/waves/round-24/falsify/out/DocExpectationBinding/grid-3case-population.json`
(the 47-row table + digests written by the same run).

---

## 3. Findings

### F1 — MEDIUM — the manifest↔oracle binding is *not* machine-checked anywhere in the repo

`derived_from` pins exactly one digest, `frozen_auditor_sha256`; it pins **no**
digest for the three oracle files that define the expectations
(`oracle-snapshot-before-inspection.json` `1f5a4699…`,
`oracle-supplement-2.json` `4600a8c3…`,
`oracle-amendment-1.json` `930b087a…`) nor for `preregistration.json`.
The only automated check in the runner that looks like a population pin is
tautological:

* `tests/report-audit/promisor-grid.py:874` `population(table)` — hashes
  `[case, kind, builder, frozen, original, amended, twin]`;
* `tests/report-audit/promisor-grid.py:898`
  `cases.append(("population-stable", population(table) == population(table)))`
  — compares the value with itself, so it can never fail.

The byte-identity assertion that does exist lived only in a build-lane scratch
script that is not in the repository
(`.ufo/waves/round-24/build/advice/GridOracle.md:184-185`: "the 44 registered
cells are asserted byte-identical to the L1's snapshot by
`GridOracle-scratch/add_supplement.py`").

**Consequence (observed):** today the binding *is* true — I proved it by
recomputing the 44-row population digest from the oracle snapshot alone
(`94eda3ac…`, command #11) and by the 0-field-difference deep compare
(command #4) — but nothing in the committed tooling would detect a later
divergence between `tests/report-audit/promisor-grid-expectations.json` and
`.ufo/waves/round-24/oracle-snapshot-before-inspection.json`.

**Minimal correction (additive; touches no expectation field):** in
`derived_from`, add `oracle_snapshot_sha256`, `oracle_supplement_sha256`,
`oracle_amendment_sha256`, `preregistration_sha256`; and add one selftest row
`manifest-matches-frozen-oracle` that compares the manifest's shared 44 rows
byte-wise with the committed `.ufo/waves/round-24/oracle-snapshot-before-inspection.json`
(a repo file already tracked at the pinned commit) and asserts
`population(44) == 94eda3acb2d28a59eb40b518c898eb01e13073081b9206803dfbbcf5ba1d3d34`.
If the `derived_from` addition is judged too invasive for a frozen artifact, the
equivalent minimal move is to publish `94eda3ac…` in the receipt next to
`612b0a74…`, so that a third party can recompute the binding without the
manifest.

### F2 — MEDIUM — the population digest does not cover the strong refusal pins

`population()` (`promisor-grid.py:874`) hashes only
`case, kind, builder, frozen, original, amended, twin`. The fields that carry
the strong refusal pins — `names_any_of` and `reason_forbidden` — are **not**
covered (measured: the fields outside the digest are `names_any_of`,
`reason_forbidden`, `notes`, `policy_ref`, `not_graded_because`).

**Consequence (observed):** the digest that is quoted in every receipt and run
summary (`612b0a74…`) does not change if the strong OID pins are edited; only
the whole-file `expectations_sha256` (`d86b7bea…`, runner line 955) covers
them, and that value lives outside the manifest. This matters because the
round-24 lesson's own headline claim is that the strong `names_any_of` pins
were *not* relaxed.

**Minimal correction:** add a second, explicitly named digest in the run
summary, e.g. `refusal_pin_sha256 = sha256(json.dumps([[c["case"],
c.get("names_any_of"), c.get("reason_forbidden")] for c in table["cases"]],
sort_keys=True))`, and pin it in the receipt. Do **not** silently widen
`population()`: that would change `612b0a74…`, which is quoted in
`GridOracle.md:20` and `RECEIPT.md` — any change must be appended with a named
rationale, per that receipt's own freeze rule.

### F3 — LOW (documentation/byte-count defect) — GridOracle's receipt table is stale and its byte count is wrong

`.ufo/waves/round-24/build/out/GridOracle/RECEIPT.md`:

* line 11 still lists the runner as `d6aa4e74…`, 46189 B, "**final, frozen**
  pending fresh falsification", although the same receipt's later entries
  (line 96: `5e96fa60…`; line 140: the integrated `b034e159…`) supersede it,
  and the file actually filed in `build/out/GridOracle/promisor-grid.py` is
  `5e96fa60…` (sha256 verified) at **47480 B**;
* line 96 states the new runner `5e96fa60…` as "(46189 B → the corrected
  size)" — 46189 B is the *previous* runner's size; the corrected artifact is
  47480 B (measured). The manifest's stated 45580 B is correct.

**Minimal correction (build-lane file, L1 owns integration):** append a row to
the "Artifact states" table marking `d6aa4e74…` as superseded by
`5e96fa60…` (47480 B) and note the integrated production runner `b034e159…`
(46583 B); correct the byte count in entry 2. Append-only, never rewrite the
filed entries.

### F4 — LOW (residual, pre-existing, do not "fix") — five exit-2 cells accept a bare path as the "names the unavailable object" alternative

`names_any_of` for PG13/PG14 (`"$sources_blob"`, `"corpus/SOURCES.md"`,
manifest lines 466-468 / 490-492), PG17/PG18 (`"$report_blob"`,
`".ufo/reports/round-1/kama.md"`, lines 568-570 / 592-594) and PG43
(`"$report_blob"`, `".ufo/reports/round-1/kama.md"`, lines 1319-1321) lists a
**path** as an accepted alternative to the object id. The runner accepts
either (`promisor-grid.py:774-775`: `if not any(n and n in err for n in names)`).

This is **pre-existing frozen-oracle content** (byte-identical to the snapshot,
command #4), not a round-24 relaxation, and the *runner-side* path-expression
loosening (`5e96fa60…`, `PATH_EXPR`/`names_unavailable`) that would have
extended the same idea to the tree cells was **correctly declined** — the
pinned runner has no such code (command #13) and the refusal for the tree cells
must name the real OID (measured: PG46's stderr names
`2f62e7ff…`/`2a675c1a…`). Reported for completeness only: **do not** change
those five `names_any_of` lists — that would edit frozen expectation fields.

### F5 — LOW (coverage gap) — the supplement's "complete twin" premise is prose-only; no cell exercises it

`oracle-supplement-2.json` row 1 says "Complete twin resolves the blob" and row
3 says "the correct clean twin verdict". The manifest registers PG46/PG47/PG48
with `"twin": null`, and the runner has **no** builder for a complete version of
the opaque fixture (builders: `c_opaque_tree_hides_cited_blob`,
`c_opaque_tree_fabricated_token`, `c_opaque_unused_tree_clean` only), so the
runner's twin-document comparison (runner lines ~1000-1018) never touches the
three supplement cells. The supplement's twin premise is therefore asserted in
prose and never executed.

**Minimal correction:** do **not** add cells to the frozen 47 (that would move
`population_size` and the 47-row digest). The honest minimal move is to say so
in the manifest note for PG46/PG48 (e.g. "no complete-twin cell is registered;
the twin claim is unexercised") or to register the twin cells in a *declared
later* round with its own oracle. The PG48 note as written ("the correct clean
twin verdict") reads as if a twin were compared; the `twin: null` field is
honest, the prose is not.

---

## 4. Claims that HOLD (with evidence)

1. **The 44 frozen expectation fields are unchanged.** 0 field differences
   across all 44 shared ids, identical order, identical `calibration`,
   `open_rows`, `views`, `amendment` blocks; the manifest's 3 extra ids are
   exactly the 3 supplement cells (commands #4, #6).
2. **The 3 supplement rows match their oracle.** `expected_exit` 2 / 2 / 0 and
   "content-derived could-not-evaluate; no JSON verdict" are carried as
   `amended = {exit 2, reason_class "unavailable"}` / `{exit 2, …}` /
   `{exit 0, kinds [], defects []}` with `reason_forbidden = ["partial clone (",
   "promisor pack"]` (command #5).
3. **The withdrawn original view was not relabelled as passed.** The original
   view (e.g. PG22 exit 2 `unknown-citation`) is retained verbatim in the
   manifest, and the runner scores it separately (`met_original`,
   `promisor-grid.py:838-839`), reporting it under
   `withdrawn_original_failures` and never in `met`/`violations`
   (`promisor-grid.py:1020-1031`). No "passed" label is attached to the
   withdrawn reading anywhere in the manifest.
4. **Strong refusal pins are preserved in the pinned runner.** The only
   acceptance rule for the exit-2 form is "stderr contains one of the resolved
   ids" (`promisor-grid.py:774-775`); the declined path-expression relaxation is
   absent (command #13, diff #10); the measured PG46/PG47 refusals name the
   real 40-hex ids (command #8).
5. **Runner/fixture-only corrections are exactly those disclosed.** The pinned
   runner differs from the build lane's filed copy (`5e96fa60…`) by 46 lines,
   all of it the removal of the path-based loosening plus two comments; the
   PG46 fixture repair (`drop=("opaque_tree","hidden_blob")` + the premise
   assertion that the cited hidden blob is absent from both repositories) is
   present in the pinned runner and matches the supplement's own fixture text
   ("the cited blob d/f is absent but its OID is hidden behind that missing
   subtree"), i.e. the fixture was brought to the oracle, not the oracle to
   the candidate. The manifest bytes are untouched by all of it.
6. **No expected-outcome fit.** The frozen 44 rows are byte-identical to a file
   committed at `f66b226` (15:04:12), the supplement at `aacbd52` (15:12:55) —
   both **before** the candidate commit `ed1cc3a` (15:14:18). For the 3
   supplement rows the *expected* values come from the pre-candidate
   supplement file, and the only manifest-authored fields for them
   (`builder`, `frozen`, `original`, `names_any_of`) are either structural
   (builder names) or verified against the r23 base (the `frozen` view:
   measured exit 2 + `partial clone` reason for all three, command #9) or
   derived from the supplement's rule (a missing tree may conceal an
   unresolved token's dependency names ⇒ name the object or the missing tree).
   The candidate happens to meet them (command #7), but the expectations were
   not authored from its output.
7. **Measured non-acquisition.** `objects_acquired {"lane": [], "fleet": []}`
   in every measured row of both arms — the no-lazy-fetch / no-transport
   isolation holds in the cells I ran.

---

## 5. Observed vs inferred

* **Observed (measured here):** all hashes above; the 0-field-difference deep
  compare; the digest `94eda3ac…`; the 3-case grid run (exit 0, 3/3 met in
  both arms, frozen arm's exit-2 metadata refusal for PG46–48); the runner diff
  (46 lines, path-loosening removed); the receipt byte-count/staleness defect;
  the absence of `PATH_EXPR`/`names_unavailable`/`"paths"` in the pinned runner.
* **Inferred (read from source, not executed):** that `population()` cannot
  detect a change to `names_any_of` (by construction of the hashed row
  tuple — verified by re-computing the digest with and without those fields);
  that the 3 supplement rows' `original`/`frozen` views are honoured by the
  runner's `live = expect.get("amended", expect["original"])` selection
  (source read, and confirmed for the amended view by the run).
* **Not verified (out of my assignment / not run):** the other 44 cells'
  runtime behaviour (no full suite was run, per the lane contract); the
  auditor's internals beyond the three measured rows; the mutation probe
  (`promisor-mutants.py`, `6e0b9d62…`) — I confirmed statically that it
  re-runs the grid (so it inherits this manifest) and holds no second copy of
  the expectations, but I did not execute it and did not run PM08; the blobless
  cells (PG05/PG06/PG28/PG43) — note the hazard relayed by
  `KamaR23-2.CaseFleetBlobless` that a stray probe without `--no-lazy-fetch`
  can materialise a missing blob in a blobless fixture; I ran no blobless cell.

---

## 6. Files written by this lane

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/DocExpectationBinding.md` (this report)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/DocExpectationBinding/grid-3case-supplement.json` (the 3-case both-arms run, sha256 `ca258165…`)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/DocExpectationBinding/grid-3case-population.json` (the 47-row table + `population_sha256` + `expectations_sha256` written by the same run)

Heavy scratch/temp only under `/fast/scratch/hyaku/kama-r24/falsify/DocExpectationBinding`.
No production source file, no `production/.jj/index`, no fleet, no sibling, no
operator config, no routing, no service and no real object store was touched;
no tool was installed or updated (no install was needed), so there is no
install/version/channel record to report. No network, no transport, no
execution payload, no PM08, no broad `pkill`.

**Report:** `.ufo/waves/round-24/falsify/advice/DocExpectationBinding.md`
