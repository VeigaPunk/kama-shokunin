# CaseMissingLaneTree — offline oracle case: promisor-marked lane, reachable tree unavailable, commits present → exit 2 (could-not-evaluate)

Seat: CaseMissingLaneTree (leaf, no dispatch). Base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
Preregistration: `.ufo/waves/round-24/preregistration.json` (C1 calibration 7→7, "distinguish promisor
metadata from unavailable evidence"). No production file was written; no suite was run.

## Verdict

The case is **specified, constructed and measured**, and it is **satisfiable and discriminating**:

* expected outcome for the case: **exit 2, could-not-evaluate** — never exit 0 (clean), never exit 1 (failed);
* the base (r23) reaches exit 2 for the **wrong reason** (promisor metadata), so the case is *not* passed by the
  r23 blanket refusal;
* a tolerant repair that treats an unreadable lane tip tree as "no registry" produces a **false clean**
  (exit 0, measured) — the case catches it;
* a scratch reference repair that replaces the metadata refusal with a read-only availability check produces
  **exit 2 with an evidence-based reason** (measured) — the case is satisfiable.

Artifacts: `.ufo/waves/round-24/build/out/CaseMissingLaneTree/` (builder, grid fragment, machine-readable
oracle spec, four measurement runs, scratch-escape proof, probes).

## Axes (godspeed)

1. *Outcome correctness* — unavailable required object ⇒ exit 2, never a verdict.
2. *Diagnostic honesty* — the refusal reason must be the missing evidence, not the promisor metadata.
3. *Repair discrimination* — the case must separate "metadata refusal removed" from "availability actually checked".
4. *No-harm* — the paired complete promisor lane must keep a real verdict (exit 0); no transport, no program,
   no fetch, no timeout.
5. *Reproducibility* — deterministic fixture (identical object ids in four independent builds), no fixture
   outside the lane scratch.

## The fixture (recipe, offline, deterministic)

`lane` and `fleet` are fresh `git init -b master` repositories under a scratch root:

| step | command | result (deterministic) |
|---|---|---|
| lane commit 1 | `git commit -m "round-1: work"` (author `kama-shokunin`, author time 1000) | `db796f8b820bf3825c58832419138cdba23206a7` |
| lane commit 2 (tip) | `git commit -m "round-1: more"` (author `kama-shokunin`, author time 1500) | `29e8ea69cc44bbb72af22255c5231a7d13b577e0` |
| fleet report | `.ufo/reports/round-1/kama.md`, `## Landed changes` cites **both** lane commits by full 40-hex, fleet author time 2000 | cutoff 2000, both lane commits "required" |
| **the missing object** | `os.unlink(.git/objects/7f/51e981…)` — the **tip commit's tree** | tree `7f51e981fce6ef87a85eca1addefa308391aaa74` absent |
| promisor metadata | `extensions.partialClone=origin`, `remote.origin.promisor=true`, `remote.origin.url=<scratch>/absent-promisor.git` (**path does not exist**) | metadata only, no pack, no `core.sshCommand` |

Every commit object of the lane stays present locally (`git cat-file -t` → `commit` for both), so the citation
resolves and no verdict may be derived from the missing tree.

Implementation: `out/CaseMissingLaneTree/case_missing_lane_tree.py` (builder + premise checks + a `--measure`
runner), paste-in grid fragment in `out/CaseMissingLaneTree/grid-fragment.py`
(`f_missing_lane_tree`, row `("F20-promisor-missing-lane-tree", "contract", …, 2, None)`).

## Expected exits / findings (written before any candidate exists)

Machine-readable: `out/CaseMissingLaneTree/case_missing_lane_tree.json` → `expected`.

| assertion | value |
|---|---|
| exit code | **2** |
| defect kinds / verdict | none (`kinds: null`, `verdict: null`; stdout carries no verdict document) |
| stderr must contain | `could-not-evaluate:` and evidence language (`missing` / `not a tree object` / `unable to read` / `unavailable` / `not available` / `no such`) |
| stderr must **not** contain | `partial clone (promisor pack)`, `partial clone (extensions.partialclone`, `partial clone (remote.` — the r23 metadata refusal phrases |
| no traceback, no timeout, no command executed | true |
| lane object store unchanged after the run | true (nothing fetched) |
| the tip tree still unavailable after the run | true (no lazy fetch) |

Paired controls (same builder, one variable changed): `control-promisor-complete` → exit 0, `kinds: []`;
`control-plain-missing-tree` → exit 2; `control-plain-complete` → exit 0, `kinds: []`.

## Measured evidence (base + three scratch reference variants)

Command: `python3 out/CaseMissingLaneTree/case_missing_lane_tree.py --measure --arm <auditor> --out <json> --scratch <root>`
(invocation of the auditor: `--lane-repo <lane> --fleet-repo <fleet> --rounds 1 --no-errata --json`).

| auditor | case (promisor + missing tree) | control: promisor + complete | control: plain + missing tree | control: plain + complete |
|---|---|---|---|---|
| base r23 `0df800e` (blob sha256 `da5041a8…`) | **exit 2**, `could-not-evaluate: …/lane: partial clone (extensions.partialclone)` | exit 2, same metadata reason | exit 2, `git ls-tree … rc=128 fatal: not a tree object` | exit 0, `kinds: []`, clean |
| scratch reference repair (metadata refusal → availability check) | **exit 2**, `…: object 7f51e981fce6ef87a85eca1addefa308391aaa74 reachable from refs/heads/master is not available locally; missing evidence, not absence` | **exit 0 clean** | exit 2, same availability reason | exit 0 clean |
| scratch reference repair, no availability check (strict read kept) | **exit 2**, `… rc=128 fatal: not a tree object` | exit 0 clean | exit 2 | exit 0 clean |
| scratch reference repair, tolerant read (unreadable tip tree ⇒ "no registry") | **exit 0, clean** ← *false clean, caught by the case* | exit 0 clean | exit 0 clean ← false clean | exit 0 clean |

All four runs: `object_store_unchanged=true`, `tree_still_missing=true` (case rows), no traceback, no timeout.
The scratch reference auditors live in `/fast/scratch/hyaku/kama-r24/CaseMissingLaneTree/` only
(`ref-audit.py`, `ref-audit-noavail.py`, `ref-audit-tolerant.py`; sha256 in the oracle spec). **They are not a
candidate, they are not in the repository, and L1 must not integrate them.**

## Why the missing tree is *required* evidence (not an arbitrary object)

* `tools/report-landing-audit.py:258-268` — `load_source_urls()` reads the **lane tip tree**
  (`git ls-tree <branch> -- corpus/SOURCES.md`). The presence of the committed registry decides how 40-hex
  tokens in the report are classified (`classify_full_hashes`, `:283-300`): with the registry the token is
  exempt, without it the same token is an `unresolved-full-hash` defect. The tip tree is therefore
  verdict-determining evidence, and with it unavailable the verdict is undecidable.
* Measured consequence: with the tip tree absent, `git ls-tree` fails (`rc=128 fatal: not a tree object`) and
  the audit can only answer by refusing. A repair that reads it "tolerantly" (treating the failure as
  "no registry") produced the false clean measured above.
* The commits are present, so the *citation* is not in question: this case isolates object availability from
  citation resolution (the latter is the sibling case `CaseUnreachableCitation` / `CaseUnknownCitation`).

## Implementation recommendation (advisory, not a candidate)

Replace the metadata refusal (`tools/report-landing-audit.py:457` promisor pack, `:462-465`
`extensions.partialclone` / `remote.*.promisor`) with an **evidence-availability** rule. Measured read-only
primitives on the case fixture (all offline, all with `--no-lazy-fetch --no-replace-objects`):

| primitive | output on the case fixture | on the complete promisor control |
|---|---|---|
| `git rev-list --objects --missing=print <ref>` | `?7f51e981fce6ef87a85eca1addefa308391aaa74` | no `?` line (0 of 6 objects) |
| `git fsck --connectivity-only --no-dangling` | `missing tree 7f51e981…` (rc 10) | — |
| `git cat-file --batch-check` (tree id) | `<tree> missing` | — |
| `git log --format=%H master` | rc 0, both commits listed (commit objects present) | — |

`rev-list --objects --missing=print` is the cheapest: one read-only call, no fetch, no network, and it does
not fire on a content-complete promisor clone. Whatever the repair chooses, the *outcome* asserted by this
case is the contract; naming the unavailable object id in the diagnostic is recommended (soft), not required.

## No-harm, no transport, no execution

* The promisor remote URL points at a **non-existent local path**; there is no `core.sshCommand` and no
  marker script — nothing can be executed, nothing can be fetched, and any transport attempt would surface as
  a fetch error in stderr (it did not: no run produced one).
* All 16 audited runs left the lane object store byte-identical and the tree still unavailable.
* No fixture escaped the lane scratch: `out/CaseMissingLaneTree/scratch-proof.txt` (fixtures only under
  `/fast/scratch/hyaku/kama-r24/CaseMissingLaneTree/`, no `/tmp/missing-lane-tree-*`, no `gitfile`/`alternates`
  redirect, no untracked path outside `.ufo/waves/round-24/`). The only tracked modification in the working
  tree is `LOG.md`, written by the CritEvidence/ScribeLog lane during the wave — not by this lane, which
  produced no production edit.

## Boundaries and non-claims

* Not a duplicate of the sibling r24 cases: `CaseMissingFleetTree` (missing **fleet** ancestor tree),
  `CaseMissingLaneBlob` (missing lane **SOURCES blob**, tree present), `OracleMissingSourceTree`
  (SOURCES evidence unavailable), `CaseUnknownCitation` / `CaseUnreachableCitation` (missing **citation**).
  Mine is the missing **lane tip tree** with all commit objects present.
* Not claimed: that the r24 repair is implemented (it does not exist yet); that `tests/report-audit/promisor-grid.py`
  exists (it does not); that every required-object boundary is settled — **the definition of "required object"
  is L1's decision**, this case only pins the lane tip tree, which the current implementation genuinely reads.
* The scratch reference repairs were written by me solely to prove the oracle is satisfiable and to measure the
  discriminating power; they are not evidence about L1's implementation.

## Verification gaps (unrun ⇒ unverified)

* No r24 candidate was run: there is none yet. The oracle spec was written before any candidate existed.
* No suite was run: not `tests/report-audit/repo-state-grid.py`, not `--selftest`, not the r24 grid
  (`promisor-grid.py` does not exist at base).
* The "not a tree object" reason of the strict-read repair depends on git 2.56.0's wording; the case pins
  evidence *language* patterns, not git's exact sentence, and the base's own wording is matched only by the
  forbidden metadata phrases.
* Whether L1's repair performs an availability check or relies on strict reads is unknown; both are measured
  here and both satisfy the case.

## Files (all under `.ufo/waves/round-24/build/out/CaseMissingLaneTree/`)

| file | sha256 (head) | content |
|---|---|---|
| `case_missing_lane_tree.py` | `ec0c32d5a3e8d86a…` | builder + premise checks + `--measure` runner |
| `grid-fragment.py` | `586e827205de8013…` | paste-in case for `tests/report-audit/promisor-grid.py` |
| `case_missing_lane_tree.json` | — | machine-readable oracle: expectations, premises, controls, measured arms, hashes |
| `measure-base.json` | — | base r23 arm (4 variants) |
| `measure-ref-repair.json` | — | scratch reference repair with availability check (4 variants) |
| `measure-ref-no-availability.json` | — | scratch reference repair without availability check (4 variants) |
| `measure-ref-tolerant-read.json` | — | scratch tolerant repair — the false-clean arm (4 variants) |
| `scratch-proof.txt` | — | no-fixture-escape proof |
| `probe_tree.py`, `probe_detect.py`, `ref_repair.py`, `assemble_oracle.py` | — | probes and the oracle assembler |

Environment: git 2.56.0, Python 3.14.8, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, no inherited
`GIT_*`. **No installs, no pacman transactions, no host service or config mutations, no model overrides.**
