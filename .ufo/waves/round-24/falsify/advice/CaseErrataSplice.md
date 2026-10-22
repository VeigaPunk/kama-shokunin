# CaseErrataSplice — r24 FRESH falsification of fixture family ErrataSplice

**Verdict: HOLDS (no source defect found; two fixture-fidelity limitations recorded separately).**
The amended (live) expectation is met for both cells of the family at the pinned
commit; the originally registered (withdrawn) expectation for PG30 is **still NOT met**
and is reported as withdrawn, never relabelled passed. No source bug was found in
this family, so no correction is proposed.

- Lane: leaf member, no subagent dispatch. No production file was edited.
- Pinned revision under test: `2e254a1763a9c08aa07fc53081287f506c447d84`
  (scratch clone `/fast/scratch/hyaku/kama-r24/falsify/CaseErrataSplice/repo`,
  `git clone --no-hardlinks`, detached checkout; clone worktree clean, `git status
  --porcelain` empty).
- Production repo `production/` lane `/.jj/index`, fleet, siblings, routing, services
  and object stores were **not** touched. The only production-side write is this
  report and the artifacts under `.ufo/waves/round-24/falsify/out/CaseErrataSplice/`.
- No tool was installed or updated in this lane (nothing to install; the task needed
  only the pinned repo's own python3 + git). No pacman transaction was attempted.

---

## 1. Assigned measurement (exact command, exit, artifact)

```
cd /fast/scratch/hyaku/kama-r24/falsify/CaseErrataSplice/repo
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseErrataSplice/tmp \
  python3 tests/report-audit/promisor-grid.py --arm both \
    --case PG29-errata-corrected-missing-sha-plain \
    --case PG30-errata-corrected-missing-sha-promisor --json
```
exit **0**; stdout 9937 bytes of JSON (saved: `out/CaseErrataSplice/grid-erratasplice.json`);
stderr **empty** (0 bytes, `out/CaseErrataSplice/grid-erratasplice.stderr`).

Digest identity of the pinned toolchain (matches the task's pinned digests exactly):
- runner `tests/report-audit/promisor-grid.py` → `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` (`b034e159…` ✔)
- manifest `tests/report-audit/promisor-grid-expectations.json` → `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (`d86b7bea…` ✔), and the run reports the same `expectations_sha256`
- source tool `tools/report-landing-audit.py` → `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` (`ea51bc35…` ✔)
- mutation probe `tests/report-audit/promisor-mutants.py` → `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` (`6e0b9d62…` ✔)
- frozen arm blob = `git cat-file blob 0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py`
  → sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`, identical to
  `derived_from.frozen_auditor_sha256` in the manifest ✔
- `population_size: 47`, `population_sha256: 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`;
  the graded table is PG01–PG39, PG41–PG45 (44 original cells) **+** the 3 independent opaque
  cells PG46 `opaque-tree-hides-cited-blob`, PG47 `opaque-tree-with-unresolved-fabricated-token`,
  PG48 `opaque-unused-tree-no-unresolved-token` (oracle-supplement-2) = the fixed 47. PG40 is
  carried as an ungraded `open_rows` entry, not as a graded cell.

## 2. Builders / premises read before measurement

`tests/report-audit/promisor-grid.py`:
- `build()` (l.320 ff.) — one lane + one fleet repo per case; `errata=True` splices
  `spliced = real_lane_commit[:15] + HIST_TAIL` (`HIST_TAIL = "d894ef21bc863486bcb35b56c"`,
  l.53) into the report's *Notes*, and commits the correcting row
  `1\tunresolved-full-hash\t<spliced>\t<lane_commit>\tev` to
  `registry/report-landing-errata.tsv` in the lane.
- `c_errata_corrected_missing_sha_plain` (l.588) = `build(root, tmp, errata=True)` (no mark).
- `c_errata_corrected_missing_sha_promisor` (l.592) = `build(root, tmp, lane_mark="config", errata=True)`
  → `mark_config()` sets `remote.origin.promisor=true`, `extensions.partialclone=origin`,
  `remote.origin.url=<absent path>` in the **lane** only; the fleet is plain in both cells.
- Hard premise in `build()` (l.440 ff.): the spliced token must be 40 hex and must **not**
  exist in either audited repository, or the build raises `Premise` (exit 2).

Fixed-expectation source: `tests/report-audit/promisor-grid-expectations.json`.
- `views`: `frozen` = r23 base behaviour (history, never a target); `original` = the initial
  registration from `preregistration.json expected_after[3]` (withdrawn prospectively for the
  rows the amendment changes); `amended` = the live graded view
  (`oracle-amendment-1.json prospective_expected[0]` and `[3]`).
- `amendment.amended_rows["PG30-errata-corrected-missing-sha-promisor"]` =
  `{exit: 0, kinds: [], reason_class: null, defects: []}` (live). PG29 is unchanged
  (`original == frozen == amended == exit 0, kinds [], defects []`).
- `amendment.amended_rows` holds 8 keys, one of which is `null` (PG37 = "no change").
- `calibration[0]` names PG30 in its changed-row list and states explicitly: "Both readings
  are carried side by side. The original view is reported as withdrawn for these rows and is
  never counted as achieved; the amended view is the graded one."

## 3. Independent re-derivation (not trusting the grid's own grading)

`out/CaseErrataSplice/verify-independent.py` (source) + `verify-independent.json` (data).
It rebuilds both fixtures with the pinned builders, then checks the premises with **plain
git plumbing** (`git --no-lazy-fetch --no-replace-objects …`), runs the pinned auditor by
hand, and compares object inventories before/after.

### 3.1 Actual missing / present objects

| probe | PG29 (plain) | PG30 (promisor) |
|---|---|---|
| `rev-list --objects --missing=print` over `refs/heads/master` (lane) | `[]` | `[]` |
| same over `--all` refs (lane) | `[]` | `[]` |
| same over `HEAD` (fleet) | `[]` | `[]` |
| same over `--all` refs (fleet) | `[]` | `[]` |
| objects held (lane / fleet) | 9 / 9 | 9 / 9 |
| spliced token `58866b563cd900dd894ef21bc863486bcb35b56c` in lane / fleet | **absent / absent** | **absent / absent** |
| real lane commit `58866b563cd900df310588effe79028efc104c33` in lane | present | present |
| `f` blob in lane | present | present |
| fleet report blob in fleet | present | present |
| `FAKE` `0123…4567` in lane / fleet | absent / absent | absent / absent |
| lane promisor config | none | `remote.origin.promisor=true`, `extensions.partialclone=origin` |
| fleet promisor config | none | none |

**Both cells are content-complete: not one object is missing anywhere in either
repository, over any ref.** Therefore *neither* cell is on the "unavailable required
object" path at all, and the clean verdict is a genuine local verdict, not a
degenerate "nothing to check". The spliced token is a **proved absence** (absent from
both stores, and no store references it), which is precisely the case the historical
errata workflow exists for.

### 3.2 The splice is the exact historical shape (checked against the real ledger)

Production `registry/report-landing-errata.tsv` (read-only) contains, for round 20:
`20 unresolved-full-hash 0957ce619789d13d894ef21bc863486bcb35b56c 0957ce619789d13bb5779606078fa1498114d2c7 <evidence>`.
Verified arithmetically: `token[:15] == correction[:15] == "0957ce619789d13"` and
`token[15:] == "d894ef21bc863486bcb35b56c" == tail25("33a6777866d0f63d894ef21bc863486bcb35b56c")`
(the work/frozen-population commit named in the ledger evidence), and the correction
object is present in the repository (`git cat-file -t` → `commit`).
The fixture reproduces this construction exactly: `spliced == lane_commit[:15] + HIST_TAIL`
(True), 40 hex, and the fixture's own ledger row read back out of the lane object store is
`1\tunresolved-full-hash\t58866b563cd900dd894ef21bc863486bcb35b56c\t58866b563cd900df310588effe79028efc104c33\tev`.

### 3.3 Exact finding / token pairs

Current arm, both cells, identical:

| cell | exit | stderr | raw defect (kind, token) | corrected_by | uncorrected | summary.status |
|---|---|---|---|---|---|---|
| PG29 | 0 | empty | `("unresolved-full-hash", "58866b563cd900dd894ef21bc863486bcb35b56c")` | `[1]` (errata line 1) | `[]` | `clean` |
| PG30 | 0 | empty | `("unresolved-full-hash", "58866b563cd900dd894ef21bc863486bcb35b56c")` | `[1]` (errata line 1) | `[]` | `clean` |

`summary` (both cells, byte-identical): `errata_rows 1, errata_unmatched 0, errata_invalid 0,
corrected 1, defects 1, uncorrected 0, required_commits 1, post_report_commits 0,
by_kind {unresolved-full-hash: 1, everything else 0}, rounds [1], status clean`.
The one defect is *kept visible* in the document (raw defect list) and merely marked
corrected — the corrected defect is not erased, and the amended expectation
(`kinds: []`, `defects: []`) is the **uncorrected** view, which the auditor matches
(`observed_defects()` splits corrected/uncorrected). ✓

### 3.4 Content-derived reason IDs

Neither cell refuses, so no exit-2 reason ID exists to assert: the amended expectation for
both cells is `exit 0`. The applicable reason constraint is therefore `reason_forbidden:
["partial clone (", "promisor pack"]`, and the current arm's stderr is **empty** for both
cells → the r23 metadata refusal does not appear. The only refusal in the whole run is in
the **frozen** arm (PG30): `could-not-evaluate: <lane>: partial clone (remote.origin.promisor)`
— i.e. the historical r23 blanket metadata refusal, exactly as the frozen column records
(`exit 2, reason_class metadata`). No content-derived reason is asserted for a cell that
does not refuse; asserting one would be fabricating a check.

### 3.5 No objects acquired

Object inventories (`git --no-lazy-fetch cat-file --batch-all-objects --batch-check=%(objectname)`)
taken immediately before and after each auditor run:

| cell | lane acquired | fleet acquired | lane lost | fleet lost | refs after | FETCH_HEAD / .promisor / shallow / alternates |
|---|---|---|---|---|---|---|
| PG29 | `[]` | `[]` | `[]` | `[]` | `refs/heads/master` | none |
| PG30 | `[]` | `[]` | `[]` | `[]` | `refs/heads/master` | none |

The grid's own per-row `objects_acquired` agrees (`{"lane": [], "fleet": []}` for all four
rows). No transport residue, no new refs, no pack or loose object appeared. Consistent with
`GIT_ISOLATION` in `tools/report-landing-audit.py` l.136-139 (`--no-replace-objects`,
`--no-lazy-fetch`, `log.follow=false`, `log.showSignature=false`, `log.mailmap=false`),
which covers every git call the auditor makes — including the errata read
`git(lane_repo, "show", f"{tip}:{ERRATA}")` (l.539), i.e. the errata ledger is read from the
**object store at the branch tip**, not from a working-tree copy.

### 3.6 Actual twin document comparison

`normalise_document()` (path-substituted) equality: **PG29 document == PG30 document** →
`twins {PG30…: true}` and `twin_equal: true` in both directions, in the current arm.
The comparison is substantive, not vacuous: the full verdict JSON is compared
(`results[0].defects`, `summary.by_kind`, `summary.corrected/uncorrected`,
`cutoff 2000`, `required 1`, `round_commits 1`, `post_report []`, `source_url_hashes []`,
`errata_invalid []`, `errata_unmatched []`). The only difference between the two fixtures
is the promisor mark on the lane, and the mark leaves **no trace** in the verdict document.
(Note: the document contains only the *fleet* report path, so the lane-path substitution in
`normalise_document()` is inert for this pair; the equality still compares all substantive
fields.)

### 3.7 Counterfactual: the errata ledger is load-bearing (not a vacuous clean)

Same two fixtures, same pinned auditor, `--no-errata` added (a supported CLI flag; nothing
edited, no expectation cell touched) — `out/CaseErrataSplice/counterfactual-no-errata.json`:

| cell | exit | pairs | status |
|---|---|---|---|
| PG29 | 1 | `("unresolved-full-hash", "58866b563cd900dd894ef21bc863486bcb35b56c")`, `corrected_by: []` | `failed`, uncorrected 1 |
| PG30 | 1 | same | `failed`, uncorrected 1 |

So: the auditor really does detect the spliced citation as an unresolved full hash in both
the plain and the promisor-marked lane, and the clean verdict comes from the authorized
errata row being applied — it is not obtained by ignoring unresolved tokens in a
promisor-backed store. The promisor mark changes nothing about detection or matching.

## 4. Amended-target comparison (frozen history met is **not** improvement)

The task's rule: "Frozen history met is not improvement; compare amended target columns."
Per cell, against the **amended** columns (`exit 0, kinds [], defects []`):

| cell | arm | exit | met_frozen | met_amended | met_original | amended columns |
|---|---|---|---|---|---|---|
| PG29 (control) | frozen | 0 | true | true (frozen baseline) | n/a | met at base |
| PG29 (control) | current | 0 | n/a | **true** | true | met, unchanged |
| PG30 (policy) | frozen | 2 (`partial clone (remote.origin.promisor)`) | true | **false** | n/a | **unmet at base** |
| PG30 (policy) | current | 0 | n/a | **true** | **false** | **met** |

- Frozen arm summary: `amended_view_met 1 / amended_view_total 2`,
  `amended_view_unmet: ["PG30-errata-corrected-missing-sha-promisor"]` → the base refused
  the original required workflow on exactly this cell.
- Current arm: `violations: 0`, `violating_cases: []`, both rows `met_amended: true`.
  **The improvement of this family is therefore exactly one amended cell (PG30), and
  PG29 is a no-harm control** (met at base, still met). No cell regressed.
- Read the counters carefully: `arms.current.amended_view_met: 0` is **not** a current-arm
  score — that counter is computed over the *frozen* arm only (it is the historical
  baseline the repair is measured against). The current arm's own score is
  `violations: 0` plus per-row `met_amended: true` for both rows.
- `withdrawn_original_failures: ["PG30-errata-corrected-missing-sha-promisor"]` — the
  originally registered expectation (`exit 2`, `reason_class "unknown-citation"`) is **still
  NOT met** by the candidate and is carried as withdrawn. It is **not** relabelled passed
  anywhere in the manifest, the grid output, or this report. PG29's original view
  (`exit 0`) is met and needs no withdrawal.

## 5. Fixture flaws (separate from source flaws)

**No source flaw was found in this family.** The two items below are fixture-fidelity
limitations of the *fixture*, not defects in `tools/report-landing-audit.py`. They do not
weaken the graded cell (the cell is about citation → authorized-errata matching), but they
bound how far the cell's "exact historical shape" claim may be read.

**F1 — the errata-ledger commit in the fixture is not a required-commit candidate.**
The fixture commits the ledger with author `fixture` and subject `errata`
(`promisor-grid.py` l.395-396), so it is excluded from the required-commit set twice over:
`round_commits()` (`tools/report-landing-audit.py` l.287-313) requires
`author == "kama-shokunin"` **and** subject `^(?:round-N:|checkpoint\(rN\))`.
In the real repository the ledger was committed by `kama-shokunin` with subjects
`round-21: report landing audit with errata ledger; …` and `round-21: integrate
build-wave findings into report audit …` — i.e. a real lane's ledger commit **is** a
required commit whenever its round equals the audited round, and must then be cited in
`## Landed changes` or it is a `landed-omitted` defect.
*Consequence:* the fixture never exercises "the errata-ledger commit is itself a required
lane commit" (the real-world round-21 shape), because it hides that commit behind a
non-matching author and subject. It also means the fixture's `required: 1` / `round_commits: 1`
counts do not reflect a lane that carries a round-1 ledger commit.
*Minimal correction (fixture only, not source):* author the ledger commit
`kama-shokunin` with subject `round-1: errata ledger` **and** cite it in the report's
`## Landed changes`, so the ledger commit is both a required commit and a cited one; the
graded cell (splice → errata match → clean) is unchanged. Not applied here: changing a
fixture to fit the candidate is explicitly out of bounds for this lane, and this lane may
not edit the pinned grid.

**F2 — the ledger's `evidence` field is a 2-character placeholder.**
The fixture writes `ev` as the fifth field (`promisor-grid.py` l.394), whereas the real
row carries a full sentence. `parse_errata()` (l.515-527) requires five tab-separated
fields and does not validate the evidence text, so the cell passes; but the fixture does
not exercise a realistic ledger payload. No behavioural consequence: the auditor never
reads the evidence field. Cosmetic only.

*Fidelity claim that IS exact:* the **citation splice** is reproduced exactly — head-15 of
the real commit + the last 25 hex of `33a6777866d0f63d894ef21bc863486bcb35b56c`, verified
against the production ledger row 20 (§3.2). Only the *ledger commit's* metadata (F1) and
the evidence text (F2) are simplified.

## 6. Residual risk / verification gaps

1. **`reason_forbidden` is inert for the graded view of this family.** `check_exit2_form()`
   runs only when the exit is 2; both cells exit 0, so the "no `partial clone (` / no
   `promisor pack`" clause is not exercised by the current arm here. It is exercised only
   by the frozen arm, where the reason *is* the metadata refusal. A grader reading
   "PG30 met" as "the metadata refusal was forbidden" would be over-reading; the actual
   evidence is "PG30 exits 0 with a clean verdict document and an empty stderr".
2. **The amended rows are exercised only through the grid's own `grade()`**, which compares
   the *uncorrected* defect set against `kinds: []` / `defects: []`. My independent run
   confirms the same thing from the raw JSON (`uncorrected: 0`, `corrected: 1`, one raw
   defect kept visible with `corrected_by: [1]`). A grader wanting the *raw* defect set to
   be non-empty must read `raw_defects`, not `defects`.
3. **Not covered by this lane** (out of my bounded family, no claim made either way):
   the exit-2 content-derived reason for an actually-unavailable required object, the
   opaque-tree diagnosis, the token-scoped unknown-citation rule, mutation sensitivity,
   and the `--no-errata` / `--errata FILE` ledger-source boundary. `load_errata()`
   (l.530-540) reads the ledger from `git show <tip>:registry/report-landing-errata.tsv`
   with `--no-lazy-fetch`; if that blob were genuinely absent in a promisor-marked lane,
   the resulting `EvalError` is **not** wrapped by `required_read()` and would surface as
   a raw `git show … rc=128 …` reason that names the *path* rather than an object id.
   I did not exercise that path (both my cells are content-complete), so I report it as an
   unverified residual, not as a finding; the errata-boundary question belongs to the
   `CodeErrataBoundary` peer.
4. **The fixture's fleet is plain in both cells.** PG30 therefore varies exactly one
   dimension (the lane's promisor mark), which is what the twin comparison needs; it does
   not test a promisor-marked fleet carrying the report (that is PG02/PG04/PG17/PG19's
   territory).

## 7. Files written

Production side (append-only, absolute):
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseErrataSplice.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseErrataSplice/grid-erratasplice.json` (assigned measurement output)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseErrataSplice/grid-erratasplice.stderr` (empty)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseErrataSplice/verify-independent.json` (independent re-derivation data)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseErrataSplice/verify-independent.py` (independent re-derivation script)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseErrataSplice/counterfactual-no-errata.json` (+ `.stderr`)

Scratch (heavy, disposable): `/fast/scratch/hyaku/kama-r24/falsify/CaseErrataSplice/`
(clone `repo/`, `verify.py`, `verify.json`, `grid-erratasplice.*`, `verify-root/`, `verify-root2/`, `cf-root/`, `tmp/`).
`TMPDIR` was set to `/fast/scratch/hyaku/kama-r24/falsify/CaseErrataSplice/tmp` for every
subprocess; the grid's own root is under `/fast/scratch/hyaku/kama-r24` (`SCRATCH`).

No expectation cell, fixture builder, manifest, or source file was modified anywhere.

## 8. Appendendum — lazy-fetch hazard closure for this family (peer `CaseFleetBlobless`)

Peer `KamaR23-2.CaseFleetBlobless` reported a fixture hazard on the PG43
fleet-unhydrated-blobless lane: a `blobless_clone()` keeps `remote.origin.url` pointing
at a **reachable** `file://` origin, so any probe *without* `--no-lazy-fetch` lazy-fetches
and materialises the missing blobs, silently evaporating the premise and letting the
auditor return a false clean exit 0.

**This hazard does not apply to PG29/PG30, and I verified the closure rather than
assuming it:**
- PG29/PG30 use no `blobless_clone()` at all: both lanes are plain `git init` repos
  (`promisor-grid.py` l.320-321) that are only *marked* by `mark_config()`.
- `mark_config()` (l.252-256) sets `remote.origin.url` to
  `<tmp>/absent-remote.git`, i.e. a **non-existent local path** — there is no reachable
  origin to fetch from. Verified in the rebuilt fixtures: the configured URL is
  `/fast/scratch/…/verify-root/PG30/absent-remote.git` and `os.path.exists()` is **False**;
  PG29's lane has no `remote.origin.*` key at all.
- Every probe I ran against either fixture used `git --no-lazy-fetch --no-replace-objects`
  (`plain_git()` in `verify-independent.py`), so no probe could have materialised an
  object even if a reachable origin had existed.
- Post-run residue check over both fixtures: **no** `FETCH_HEAD`, **no** `*.pack`,
  **no** `*.promisor` marker, no `shallow`, no `alternates`; object inventory unchanged
  (0 acquired, 0 lost) and `refs/heads/master` the only ref before and after.
- The lane/fleet are content-complete by construction (§3.1: zero missing objects over
  every ref), so there is nothing for a lazy fetch to materialise in the first place.

No correction to the grid is proposed for this family. The PG43 hazard itself is
`CaseFleetBlobless`'s to carry; I only record that it is out of reach for ErrataSplice.
