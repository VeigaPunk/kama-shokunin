# CaseMissingAncestor — offline oracle case: a required lane ancestor commit that is not available in a promisor-backed lane ⇒ exit 2 (could-not-evaluate), never a truncated-history verdict

Lane: reviewer (leaf, no dispatch). Base observed: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
(ancestor of lane tip; the auditor blob is byte-identical at `0df800e` and at the preregistration
commit `d1b9d95`, sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`).
Preregistration: `.ufo/waves/round-24/preregistration.json` (C1 calibration 7→7, "distinguish promisor
metadata from unavailable evidence"). Scratch clone: `/fast/scratch/hyaku/kama-r24/CaseMissingAncestor`
(`git clone --no-hardlinks`). git 2.56.0, Python 3.14.8. **No production file was written; no suite was run.**

## Verdict

The case is **specified, constructed and measured**, and it is **satisfiable and discriminating**:

* expected outcome: **exit 2, could-not-evaluate** for the unavailable required ancestor — never exit 0
  (clean), never exit 1 (failed), never a "landed-omitted" guess;
* the r23 base reaches exit 2 for the **wrong reason** (promisor *metadata*), so the case is **not**
  passed by the r23 blanket refusal — the fault row now pins an *evidence-based* refusal;
* the pre-r23 auditor (`4fe9339f`, sha256 `09ecd63b…`) satisfies **all three arms** — the expectations
  are satisfiable by the tool's own history, not only by a scratch simulation;
* a tolerant repair that enumerates the lane history without failing on the gap produces a **false clean**
  (exit 0, measured) — the case catches it.

Artifacts: `.ufo/waves/round-24/build/out/CaseMissingAncestor/` (case builder + runner, paste-in grid
fragment, four measurement runs, one harness run, scratch-escape proof).

## Axes (godspeed)

1. *Outcome correctness* — an unavailable required object ⇒ exit 2, never a verdict.
2. *Diagnostic honesty* — the refusal reason must be the missing evidence, not the promisor metadata.
3. *Repair discrimination* — the case must separate "the metadata refusal was removed" from "the evidence
   was actually checked", and must catch a truncated-history reading.
4. *No-harm* — the paired complete promisor lane must keep a real verdict (exit 1, `landed-omitted`), and
   the full clone must reach exactly the same findings.
5. *Reproducibility* — deterministic fixture (identical object ids in every independent build), no fixture
   outside the lane scratch, no transport, no program, no fetch.

## The fixture (recipe, offline, deterministic)

One lane history, one fleet report, one local bare origin. Nothing else.

| object | how it is built | value (deterministic) |
|---|---|---|
| L0 `round-1: base` | `git commit -m "round-1: base"`, author `kama-shokunin`, author time 900 | `f2a3f555fec1893ef9fcc26a1ae3b8fe834f660d` |
| L1 `round-1: work` | same, author time 1000 | `adf2a3a5f286862c96099b7cd59457c6cd88621c` |
| L2 `round-1: measure` | same, author time 1100 | `e51bbdbc7eb8ba2e2fbba826088b87ba77c44fe1` |
| L3 `round-1: late` | same, author time 2100 (post-report) | `ad057c4cf6f92d0190911731fbfa51d0ff5e8453` |
| fleet report | `.ufo/reports/round-1/kama.md`, `## Landed changes` cites **L0 and L2** by full 40-hex, fleet author time 2000 | cutoff 2000; L1 is the **genuine omission** |
| origin | `git clone --bare --no-hardlinks src origin.git`, `uploadpack.allowFilter=true` | local path, the only "remote" |

The lane is a **clone of that origin**; the three arms differ in one variable — is L1 available locally?

| arm | lane | L1 | promisor metadata |
|---|---|---|---|
| CA-1a | `clone --filter=blob:none --no-local --no-checkout file://origin` (a *real* blobless partial clone: `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`, `extensions.partialClone=origin`, `core.repositoryformatversion=1`, one `*.promisor` pack) | present | real |
| CA-1b | the same partial clone, its pack rebuilt without L1 | **absent** (the origin still holds it, so a lazy fetch would restore it and be visible) | real |
| CA-1c | `clone --no-local --no-checkout file://origin` (full clone, no promisor metadata) | present | none |

Rebuilding the pack without L1 uses an **explicit object list** (`pack-objects --stdout` fed with the
commit, tree and blob ids of L0/L2/L3): a rev-list exclusion (`^L1`) would also drop L0, because L0 is an
ancestor of L1 — an earlier draft of this fixture did exactly that and silently turned the case into a
*missing-citation* case. The `.promisor` marker is kept, so CA-1b stays a promisor-backed repository.

Implementation: `out/CaseMissingAncestor/case-missing-ancestor.py` (builder + premise checks + runner).
Paste-in grid fragment: `out/CaseMissingAncestor/grid-fragment.py` (`c_ca1_promisor_complete`,
`f_ca1_missing_required_ancestor`, `c_ca1_full_clone`, the three `CA1_CASES` rows, one `CA1_REASONS`
entry, and the four assertions the grid protocol cannot express).

## Expected exits / findings (written before any candidate exists)

| arm | kind | exit | findings | stderr | post-conditions |
|---|---|---|---|---|---|
| CA-1a | control | **1** | `["landed-omitted"]`, token = L1's sha; `required_commits=3`, `post_report_commits=1` | — | L1 still present; object store unchanged |
| CA-1b | fault | **2** | **none** — no verdict document on stdout, no `landed-omitted` / `landed-unresolved` / `unresolved-full-hash` / `landed-section-missing` | `could-not-evaluate:` + evidence language (`missing` / `not available` / `unable to read` / `could not read` / `failed to traverse` / `incomplete` / `truncat` …) and **not** the r23 metadata phrases (`partial clone (promisor pack)`, `partial clone (extensions.partialclone`, `partial clone (remote.`) | L1 still absent; object store byte-identical; lane and fleet `HEAD` unchanged; no traceback; no timeout |
| CA-1c | control | **1** | identical to CA-1a (kinds, tokens, counts) | — | L1 still present |

Recommended (soft, not graded): the CA-1b diagnostic should name the unavailable object
`adf2a3a5f286862c96099b7cd59457c6cd88621c`.

Why this is *required* evidence and not an arbitrary object: the lane's round-1 commit set **is** the
required-candidate set. `round_commits()` (`tools/report-landing-audit.py:189-213`) walks
`git log -z --format=%H%x00%an%x00%at%x00%s <branch>` and keeps every commit whose author is
`kama-shokunin` and whose subject matches `^(?:round-1:|checkpoint\(r1\))`; `audit_round()`
(`:302-357`) turns the pre-cutoff part of that set into the `required` set and reports a `landed-omitted`
defect for every required commit the report does not cite. If L1 cannot be read, that set cannot be
established: the auditor cannot know whether L1 landed, and the report's silence about L1 is **unknown,
not absence**.

## Measured evidence

Auditor invocation (identical for every arm): `--lane-repo <lane> --fleet-repo <fleet> --rounds 1
--no-errata --json`, in a subprocess with `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, no
inherited `GIT_*`.

| auditor | CA-1a (promisor, complete) | CA-1b (required ancestor absent) | CA-1c (full clone) |
|---|---|---|---|
| **base r23** `0df800e` (blob sha256 `da5041a8…`) | **exit 2** `could-not-evaluate: …/lane: partial clone (promisor pack)` → **NOT MET** | **exit 2** `…: partial clone (promisor pack)` → **NOT MET** (right code, metadata reason) | exit 1, `["landed-omitted"]` → met |
| **pre-r23 auditor** `4fe9339f` (blob sha256 `09ecd63b…`) | exit 1, `["landed-omitted"]` → met | exit 2 `… rc=128 error: Could not read adf2a3a5… / fatal: Failed to traverse parents of commit e51bbdbc…` → met | exit 1, `["landed-omitted"]` → met |
| **scratch simulation "repaired"** (base minus the two promisor-metadata refusals; sha256 `90169c7f…`) | exit 1, `["landed-omitted"]` → met | exit 2, evidence reason → met | exit 1, `["landed-omitted"]` → met |
| **scratch simulation "tolerant"** (`rev-list --missing=print` + `git show -s`; sha256 `32850894…`) | exit 1 → met | exit 2 → met (git itself refuses to parse a commit whose parent is missing) | exit 1 → met |
| **scratch simulation "nowalk"** (`rev-list --missing=print` + `git log --no-walk`; sha256 `2e20c920…`) | exit 1 → met | **exit 0, clean — FALSE CLEAN → NOT MET** | exit 1 → met |

The three scratch simulations exist only to measure satisfiability and discriminating power; they are **not
a candidate**, they are not in the repository, and L1 must not integrate them. They are rebuilt
deterministically by `out/CaseMissingAncestor/make-simulations.py` from the base blob.

Grid-harness run (the fragment pasted into the existing `tests/report-audit/repo-state-grid.py`, only the
three CA-1 rows selected, `--arm both`): `out/CaseMissingAncestor/results-grid-harness-ca1.json` —
frozen (`4fe9339f`) 3/3 met, current (`0df800e`) 2/3 met with CA-1a `exit=2, partial clone (promisor
pack)`. The fragment is paste-ready: it uses only the helpers that harness already provides
(`g`, `init`, `commit`, `report`, `publish`, `require`, `env`).

## What the case forces on the repair (measured git behaviour, git 2.56.0)

* A **strict** history read fails loudly: `git --no-lazy-fetch log -z --format=… <branch>` → **rc=128**,
  `error: Could not read <L1>` + `fatal: Failed to traverse parents of commit <L2>`. That is the exit-2 path
  the pre-r23 auditor already takes.
* A **tolerant** read truncates silently: `git rev-list --missing=print <branch>` → rc=0 and the visible
  history stops at the gap (`L3`, `L2`, `?L1`); `L0` and `L1` are *not* listed. Combined with
  `git log --no-walk` per listed commit, the auditor sees 2 of 4 commits, the required set becomes
  `{L2}`, the report cites L0 and L2, nothing is missing and nothing is omitted ⇒ **exit 0, clean**
  (measured). This is the "truncated history" verdict the case exists to forbid.
* `git show -s <L2>` is *not* a tolerant reader (rc=128, `unable to parse commit <L1>`): git refuses to
  render a commit whose parent object is missing. Only readers that take the commit bytes without the
  parent (`cat-file --batch`, `log --no-walk`) can produce the truncated view — which is why the case must
  be measured, not argued.
* The lazy-fetch channel is the **object lookup**, not the traversal: `git cat-file -e <L1>` without
  `--no-lazy-fetch` fetched L1 back from the local origin and wrote two new packs into the clone
  (measured). With `--no-lazy-fetch` the same query answers `missing` and nothing is fetched. CA-1b's
  post-condition (object store byte-identical, L1 still absent) detects that regression if the repair ever
  reaches L1 through a lookup.
* CA-1b also carries a **store-positive / closure-negative citation**: the report cites L0, which the
  closure cannot reach once L1 is missing, while `cat-file --batch-check <L0>` still resolves it. A repair
  that decides citations from the closure instead of the object store would emit a false
  `unresolved-full-hash` for L0 — forbidden by this arm ("no verdict on stdout"). The complement of this
  witness — a citation that is present locally but outside the pinned root, on a *complete* promisor lane,
  where the expected outcome is a substantive verdict — belongs to the sibling case `CaseUnknownCitation`.

## No-harm, no transport, no execution

* The only remote is a **bare repository on the same filesystem**, reached through git's local path
  transport (`file://`); there is no network, no `core.sshCommand`, no `uploadpack` hook, no marker
  script, no payload, and nothing to execute.
* Every arm: no traceback, no timeout, `HEAD` of lane and fleet unchanged, lane object store byte-identical
  before and after the run, and (CA-1b) L1 still absent afterwards.
* The auditor itself is run with a scrubbed environment (`GIT_CONFIG_GLOBAL=/dev/null`,
  `GIT_CONFIG_NOSYSTEM=1`, no inherited `GIT_*`), like the existing grid harness.

## Containment (no fixture escaped the scratch)

`out/CaseMissingAncestor/scratch-proof.txt` (regenerated from live commands): all fixture repositories live
under `/fast/scratch/hyaku/kama-r24/CaseMissingAncestor/`; the case runner deletes them by default
(`--keep` preserves them); no `/tmp` fixture of this lane remains (the temporary directories of two crashed
harness runs were removed by this lane); the real lane repository contains no `origin.git`, no `*.promisor`,
no probe directory and no new object/refs; the only paths this lane wrote into the repository are
`.ufo/waves/round-24/build/advice/CaseMissingAncestor.md` and
`.ufo/waves/round-24/build/out/CaseMissingAncestor/`. (`corpus/QUALITY.md`, `corpus/SOURCES.md` and
`corpus/lessons/round-24.md` in the working tree are **other lanes'** edits — not mine.)

## Boundaries and non-claims

* Not a duplicate of the sibling r24 cases: `CaseMissingLaneTree` (missing lane **tip tree**),
  `CaseMissingLaneBlob` (missing lane **SOURCES blob**), `CaseMissingFleetTree` (missing fleet ancestor
  **tree**), `CaseMissingFleetReport` (missing fleet report), `CaseUnknownCitation` /
  `CaseUnreachableCitation` (missing **citation**), `CaseCompleteLane` / `CaseHydratedLane` (complete and
  hydrated promisor clones). Mine is the missing **lane ancestor commit** — the case where the *history
  itself* stops at the gap.
* Not claimed: that the r24 repair exists (it does not); that `tests/report-audit/promisor-grid.py`
  exists (it does not at base — the fragment is written for it); that "required object" is settled for
  every boundary (that is L1's decision — this case pins the lane ancestor commit only).
* The scratch simulations were written solely to prove the oracle is satisfiable and to measure its
  discriminating power; they say nothing about L1's implementation.
* The fleet repository in this fixture is an ordinary repository. A promisor-marked **fleet** is a sibling
  case (`CaseCompleteFleet`, `CaseHydratedFleet`); not covered here.

## Verification gaps (unrun ⇒ unverified)

* No r24 candidate was run: there is none yet. The expectations were written before any candidate existed.
* No suite was run: not `tests/report-audit/repo-state-grid.py` in full (only the three CA-1 rows through
  a patched copy), not `--selftest`, not the r24 grid (`promisor-grid.py` does not exist at base).
* The fault row's *reason* check accepts a set of evidence wordings; a repair whose diagnostic uses
  wording outside that set would need the list extended. The r24 grid's `REASONS` map holds a single
  substring, so it cannot express "evidence-based, not metadata-based" — the same limitation the sibling
  `CaseMissingFleetTree` reports; an any-of mechanism is needed there for both rows.
* Whether L1's repair relies on the strict read or adds an explicit availability check is unknown; both
  paths are measured here and both satisfy the case.
* The `trace2.eventTarget` / `trace2.normalTarget` config keys produced **no** trace file on git 2.56.0
  (measured), and the auditor scrubs `GIT_TRACE2_EVENT` from the environment, so attempt-level fetch
  detection is not available to this case; it rests on the object-store delta instead.

## Files (all under `.ufo/waves/round-24/build/out/CaseMissingAncestor/`)

| file | sha256 (head) | content |
|---|---|---|
| `case-missing-ancestor.py` | `3612bff4…` | builder + premise checks + runner (`--auditor`, `--keep`, `--json`) |
| `grid-fragment.py` | `270a1aa8…` | paste-in case for `tests/report-audit/promisor-grid.py` |
| `make-simulations.py` | `9f151fa9…` | rebuilds the three scratch simulations from the base blob |
| `grid-harness-with-ca1.py` | `f457d316…` | the existing harness with the fragment pasted in (the fragment is proved paste-ready) |
| `results-base-r23.json` | `46b3cc21…` | base r23 arm (3 arms) |
| `results-sim-repaired.json` | `87d69d03…` | scratch "metadata refusals removed" arm |
| `results-sim-tolerant.json` | `c6abb4a8…` | scratch "tolerant reader" arm |
| `results-sim-nowalk.json` | `771ee7cf…` | scratch "truncated history" arm — the false clean |
| `results-grid-harness-ca1.json` | `574508d9…` | the three rows through the existing grid harness, both arms |
| `scratch-proof.txt` | `57976194…` | no-fixture-escape proof |
| `probe-git-missing-commit.py` | `098fede8…` | the raw git behaviour probe behind the expected exits (`log` rc=128, `rev-list --missing=print`, lazy fetch restoring the object) |
| `probe-promisor-clone-pack.py` | `851a7628…` | the probe that built the real partial clone and rebuilt its pack without the required ancestor |

Environment: git 2.56.0, Python 3.14.8, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, no inherited
`GIT_*`. **No installs, no pacman transactions, no host service or config mutations, no model overrides, no
secrets, no production edit.**
