# OracleMissingErrata — missing committed lane errata blob: independent expected outcome

Round 24, leaf lane (oracle). Scope: the errata ledger read
(`registry/report-landing-errata.tsv` at the lane branch tip) and the
corrected/uncorrected verdict it determines.

**Verdict: the oracle is pinned, satisfiable, and discriminating against
ten mutants. One cross-lane boundary is reported in §5; it is not mine to
settle.**

The pinned oracle is `expected.json` (15 arms) in this lane's out
directory. It was derived from the round-24 preregistration, the **live**
`oracle-amendment-1.json`, and the base auditor's source, **before any
candidate implementation existed** — no candidate file was present in the
lane at any point in this lane's work. The only auditors measured are the
r23 base extracted from the base commit, and a scratch reference repair
written afterwards solely to prove satisfiability.

Artifacts (all under `.ufo/waves/round-24/build/out/OracleMissingErrata/`):

| file | role |
|---|---|
| `expected.json` | the pinned oracle: 15 arms, expected exit/verdict/counts per arm |
| `build_fixture.py` | the bounded offline fixture recipe; builds all 15 arms |
| `grade_oracle.py` | runs an auditor against the oracle; per-arm met/not-met |
| `mutation_check.py` | 10 mutants; proves the oracle discriminates each failure mode |
| `reference-repaired-audit.py` | scratch proof of satisfiability (**not** the candidate) |

---

## 1. Axes

1. **Correctness of the expected outcome.** A committed ledger whose blob is
   unavailable locally must be `could-not-evaluate` (exit 2), never an
   absent-ledger fallback that emits a verdict.
2. **No-harm.** The corrected/uncorrected counts on the plain and
   metadata-marked arms must not move.
3. **Fixture safety.** Offline, synthetic, no network transport, no program
   execution, no fixture mutation across runs.
4. **Discrimination.** The oracle must reject every failure mode it is
   meant to reject, and must not over-constrain a second acceptable
   implementation.
5. **Handoff usability.** L1 must be able to run this against a candidate
   without reading this report.

---

## 2. The distinction the oracle pins

The r23 base refuses any promisor-marked repository outright
(`tools/report-landing-audit.py:455-465`, `check_history_repo`: the promisor
pack check at `:457`, the `extensions.partialclone` / `remote.*.promisor`
config check at `:462-465`). That is the harm the round repairs: a
*complete* local clone that merely carries promisor metadata is refused
with exit 2 although its evidence is all present.

The repair must separate four states that the base conflates or refuses
alike:

| state | required outcome |
|---|---|
| ledger committed, blob present locally | ordinary verdict |
| ledger committed, blob **not** available locally | **exit 2** — required evidence unavailable |
| ledger path never committed | exit 2 — no ledger in this repository |
| ledger committed and available, but the repository carries promisor metadata or a promisor pack | ordinary verdict, identical to the plain twin |

The middle state is the one at risk of being laundered. A candidate that
treats an unreadable ledger as "zero ledger rows" does not crash and does
not refuse: it produces a *verdict*. In the arms where the report cites
every required commit (E10, E12), that verdict is **exit 0 clean** — a
clean verdict derived from evidence the auditor never read. The oracle pins
exit 2 for those arms, and the mutant check confirms the oracle rejects
exactly that fallback.

Two further distinctions are pinned, because both are one-directional
mistakes:

- **Metadata vs. content (E7, E11, E14, E15 vs. E10).** Promisor metadata
  and a promisor pack are declarations that an object *may* live at the
  origin; they are not evidence that any object is missing here. A marked
  repository whose content is complete must yield the same substantive
  verdict as its plain twin. A marked repository whose ledger blob is
  missing must not. Both arms exist with identical substantive history, so
  the pair cannot be satisfied by any single blanket rule. E15 is the
  sharpest: a `blob:none` clone whose ledger blob was copied back — every
  object the audit reads is present, yet the repository still carries a
  promisor pack. Refusing it would be a blanket precondition.
- **Marked vs. unmarked twins (E8 vs. E9).** The same ledger row — naming a
  correction commit — must give the same verdict whether or not the
  repository is promisor-marked. E8's origin genuinely holds the named
  commit (measured: a fetch-enabled read restores it), so a candidate that
  treats promisor-marked repositories differently changes the verdict on
  metadata alone. The tripwire separately proves the auditor did not fetch
  it.

### 2.1 Alignment with the live amendment

The amendment (`.ufo/waves/round-24/oracle-amendment-1.json`, "live (L1
decision)") **withdrew** the original preregistration's
`expected_after[3]` ("a missing citation in any promisor-backed repository
is unknown, not proved absent: exit2"). Its `prospective_expected[0]` says
promisor metadata alone never changes local-object resolution or a
clean/failed verdict, including locally unresolved citations and authorized
errata matching.

This oracle was written against the original preregistration and has been
**re-pinned to the amendment**, which changes two of my arms:

- **E8** was pinned exit 2 (unknown-citation reading) and is now pinned
  **exit 1 with the E9 counts** — the marked and unmarked twins must agree.
- **E14** was added after the amendment: it is the PG29/PG30 shape (an
  errata-corrected missing SHA in a marked lane) and is pinned exit 0
  clean, matching the sibling 44-case snapshot's amended expectation.

**E13/E14 exist because the amendment's `prospective_expected[0]` names
"authorized errata matching" explicitly, and the withdrawn reading would
abort before the errata could correct anything.** These two arms are the
historical round-20 workflow (the spliced SHA corrected by a committed
ledger row) and are the workflow the round must not break.

---

## 3. Measured results

Base auditor = `tools/report-landing-audit.py` at the base commit
`0df800e896f6bce285a81e794ad4ae1d1e6c3a71`, sha256
`da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`
(confirmed byte-identical at the current HEAD `aacbd52`).

### 3.1 Base against the oracle — 10/15, failing exactly the five harm arms

```
E1  ledger-present-complete                   exit 0 clean   def 1 corr 1 uncorr 0 rows 1
E2  ledger-committed-blob-missing-promisor    exit 2  partial clone (remote.origin.promisor)
E3  ledger-committed-blob-missing-blobless    exit 2  partial clone (promisor pack)
E4  ledger-absent-from-tree                   exit 2  path 'registry/report-landing-errata.tsv' does not exist
E5  ledger-committed-blob-missing-no-promisor exit 2  bad object
E6  ledger-present-row-mismatch               exit 1 failed  def 1 corr 0 uncorr 1 rows 1 unm 1 inv 1
E7  promisor-marked-complete                  exit 2  partial clone (extensions.partialclone)   <-- FAIL
E8  promisor-marked-ledger-correction-missing exit 2  partial clone (extensions.partialclone)   <-- FAIL
E9  ledger-correction-missing-no-promisor     exit 1 failed  def 2 corr 1 uncorr 1 rows 1 inv 1
E10 promisor-marked-ledger-missing-no-defects exit 2  partial clone (extensions.partialclone)
E11 promisor-marked-ledger-present-no-defects exit 2  partial clone (extensions.partialclone)   <-- FAIL
E12 ledger-missing-no-defects-no-promisor     exit 2  bad object
E13 errata-corrected-missing-sha-plain        exit 0 clean   def 1 corr 1 uncorr 0 rows 1
E14 errata-corrected-missing-sha-promisor     exit 2  partial clone (extensions.partialclone)   <-- FAIL
E15 blobless-lane-ledger-hydrated             exit 2  partial clone (promisor pack)             <-- FAIL
```

The five failures are the r23 harm stated as measurable rows: every arm
whose only distinguishing feature is promisor metadata or a promisor pack
on a content-complete repository. With the metadata stripped from a copy of
each fixture, the same fixtures give **E7 exit 0 clean (defects 1,
corrected 1)**, **E11 exit 0 clean (defects 0, errata_rows 1)**, **E14 exit
0 clean (defects 1, corrected 1)** and **E8 exit 1 failed (the E9 counts)**
— the substantive expectations the candidate must reproduce.

The base's own `load_errata` path was probed directly (scratch
`probe_base_paths.py`, with the blanket refusal bypassed) to record the two
error classes the candidate must keep apart:

- E2/E3/E5 — the read fails on the **object**: `fatal: bad object <oid>:
  registry/report-landing-errata.tsv`.
- E4 — the read fails on the **path**: `fatal: path
  'registry/report-landing-errata.tsv' does not exist`.

### 3.2 Satisfiability — a reference repair passes 15/15

`reference-repaired-audit.py` (scratch; **not** the candidate) makes three
changes to the base: promisor metadata and a promisor pack are no longer
refusals; the ledger read distinguishes path-absent from blob-unavailable
and refuses the latter with a content-derived reason; and nothing else
changes. Result: **15/15 arms met, 0 violations**, and the retained r23
grid's controls and contracts are unaffected (§5).

The oracle does not over-constrain: an earlier variant that changed only
the ledger path and left the general citation rule alone also passed every
arm at the time it was written. Both implementations are acceptable; the
oracle constrains the outcome, not the mechanism.

### 3.3 Mutation check — 10 mutants, all rejected

`mutation_check.py` (exit 0). Every mutant is rejected, each by a
different subset of arms:

| mutant | rejected by |
|---|---|
| M1 empty-ledger fallback (base) | E4 E5 E7 E8 E11 E12 E14 E15 |
| M2 empty-ledger fallback, narrow form (base) | E4 E5 E7 E8 E11 E12 E14 E15 |
| M3 absent-path fallback (base) | E4 E7 E8 E11 E14 E15 |
| M4 fetch-enabled read (base) | E7 E8 E11 E14 E15 |
| M5 fetch-enabled read (repaired) | E2 E3 E8 |
| M6 promisor-pack refusal reinstated (repaired) | E15 |
| M7 empty-ledger fallback (repaired) | E2 E3 E5 E10 E12 |
| M8 promisor-metadata refusal reinstated (repaired) | E7 E8 E11 E14 E15 |
| M9 withdrawn citation-exit2 rule reinstated (repaired) | E1 E6 E7 E8 E9 E11 E13 E14 E15 |
| M10 withdrawn rule + empty-ledger fallback (repaired) | E1 E6 E7 E8 E9 E11 E13 E14 E15 |

There are now **no tolerated variants**: every mutant is a behaviour the
oracle must forbid.

M5 is the most instructive mutant: with `--no-lazy-fetch` removed from the
repaired auditor, E2 **silently fetches** the missing blob from the local
origin and returns **exit 0** — a clean verdict on evidence it never read.
The grader catches this by re-probing object availability after every run
(`fetched: ['errata_blob']`), independently of the exit code.

---

## 4. Harness defects found and fixed (fixture-safety axis)

Two defects were found in this lane's own harness while measuring, and both
are recorded because they would have produced false confidence:

1. **The premise probe destroyed the premise.** A plain
   `git cat-file -e <blob>` against a promisor-backed repository *fetches*
   the blob. The first probe of E2/E3 restored the objects it was supposed
   to prove absent. Fixed: every availability probe now uses
   `git --no-lazy-fetch cat-file -e`, and the fetch-enabled comparison runs
   on a throwaway copy.
2. **The grader mutated shared fixtures.** An auditor that lazy-fetches
   restores the object inside the fixture repository, so the *next* arm and
   the *next* mutant run saw a different fixture. This produced a false
   "MISS" for one mutant before it was found. Fixed: `grade_oracle.py` now
   copies each arm into its own temporary directory and evaluates the
   tripwire against that copy.

A third defect was in the mutation set itself: one mutant was initially a
no-op edit (identical to the base) and was reported as "rejected" while
changing nothing. It was rewritten to remove `--no-lazy-fetch` from
`GIT_ISOLATION`, which is what it was meant to test. Two further mutants
became no-ops after the reference repair changed shape (the promisor-pack
refusal was removed from it); both were repointed at live anchors, and the
check that a mutant must actually change the source is now enforced in
`mutation_check.py`.

---

## 5. Cross-lane boundary (reported, not settled)

The retained r23 grid (`tests/report-audit/repo-state-grid.py`) was run
against three auditors. Base: **faults 26/26, contracts 4/4, controls
13/13, violations 0**. The reference repair differs on two rows:

| row | base | reference repair | channel |
|---|---|---|---|
| F06-lazy-fetch-command (fault) | exit 2, reason `partial clone`, met | **exit 1**, kinds `['landed-unresolved','unresolved-full-hash']`, NOT-MET | cited-blob / unknown-citation |
| F23-promisor-pack-without-config (contract) | exit 2, reason `promisor pack`, met | **exit 1**, kinds `['unresolved-full-hash']`, NOT-MET | cited-blob / missing-object |
| O01-alternates-foreign-object (open) | exit 0, NOT-MET | exit 0, NOT-MET | ungraded |
| O02-gitfile-redirect (open) | exit 0, NOT-MET | exit 0, NOT-MET | ungraded |
| T01-blobless-partial-clone (tradeoff) | exit 2, NOT-MET | exit 2, NOT-MET | ungraded |

Read carefully: **both rows are outside my lane's channel.** F06 and F23
concern a *cited blob* that is missing and a fabricated citation — the
"missing cited object" and "unknown citation" channels, which the
sibling 44-case snapshot (PG13/PG14, PG22/PG23/PG24, PG33/PG34, PG41/PG42)
and `oracle-supplement-2.json` own. My lane owns the *errata ledger read*.

The snapshot's `reason_forbidden` lists `partial clone (` and
`promisor pack` for the amended promisor rows, and the supplement states
that a *missing cited blob known to name unavailable referenced local
content* must be exit 2 with a content-derived reason. My reference repair
implements the ledger channel only; it does not implement the bounded
missing-object traversal that the supplement describes for the citation
channel. That is why F06 and F23 land differently under it — the repair is
incomplete in a channel it does not own, not wrong in mine.

**Consequence for L1:** a candidate that implements only the ledger channel
will still show F06 and F23 differently, and must not be judged on those
rows by this lane's oracle. The rows that belong to the citation channel
must be settled by its owner, and the F06 refusal-reason string in the
grid's `REASONS` map will need a documented policy-row update if the
refusal reason changes from `partial clone` to a content-derived reason.

Everything else in the retained grid is unaffected: 25/26 faults, 3/4
contracts, 13/13 controls, 0 tracebacks, 0 executed commands, 0 timeouts.

---

## 6. Residual risk and verification gaps

- **The candidate has not been seen.** This lane produced an oracle, not a
  verdict on a candidate. Everything above is measured against the base and
  against a scratch reference repair.
- **`expected.json` is a policy artifact.** If L1 reads the ledger
  differently — for example treating a ledger path absent from the tree as
  "no ledger" — the E4 and E12 rows change. The r23 base treats a missing
  ledger path as exit 2 and this oracle preserves that as no-harm; a
  deliberate change would need documenting as a policy-row change.
- **E3's blobless construction is the least robust arm.** It copies every
  blob except the ledger back from the source, which depends on the
  `rev-list --objects` listing. The premise checks assert the ledger is
  the only unavailable object; if the listing changes shape the arm
  degrades to a generic blobless clone. The E2 arm (a deleted loose object
  in a full clone) is the simpler statement of the same case, and E5/E12
  are its non-promisor twins.
- **E8 rests on a policy reading.** Under the withdrawn
  `expected_after[3]`, E8 would be exit 2; under the live amendment it is
  exit 1. It is pinned to the amendment because that is the live L1
  decision and because `prospective_expected[0]` requires marked and
  unmarked twins to agree. If L1 reinstates the withdrawn rule, E8 must be
  re-pinned, not silently.
- **The citation channel was not verified against a candidate.** Not my
  lane; see §5.
- **Unrun.** No candidate was run. No full-suite check was run. The
  retained r23 grid was run against the base and against the scratch
  reference repair only, and the base's own selftest was run once
  (`--selftest`: 50 cases, 0 failed).

---

## 7. How to run this against a candidate

```sh
cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/OracleMissingErrata
python3 build_fixture.py /tmp/errata-fixtures          # offline, synthetic
python3 grade_oracle.py \
    --auditor /path/to/candidate/tools/report-landing-audit.py \
    --fixtures /tmp/errata-fixtures \
    --expected expected.json
# exit 0 = every arm met its pinned expectation; exit 1 = at least one did not
```

`grade_oracle.py` copies each arm before running it, so it is safe to point
at a candidate that fetches. The mutation check re-runs the same grader
against ten mutants:

```sh
python3 mutation_check.py --base <base-audit.py> --repaired reference-repaired-audit.py \
    --fixtures /tmp/errata-fixtures --expected expected.json --grader ./grade_oracle.py
```

## 8. Commands and files

- Fixture builder: `.ufo/waves/round-24/build/out/OracleMissingErrata/build_fixture.py`
  (scratch copy: `/fast/scratch/hyaku/kama-r24/OracleMissingErrata/build_fixture.py`)
- Oracle: `.ufo/waves/round-24/build/out/OracleMissingErrata/expected.json`
- Grader: `.ufo/waves/round-24/build/out/OracleMissingErrata/grade_oracle.py`
- Mutants: `.ufo/waves/round-24/build/out/OracleMissingErrata/mutation_check.py`
- Reference repair (proof of satisfiability, not the candidate):
  `.ufo/waves/round-24/build/out/OracleMissingErrata/reference-repaired-audit.py`
- Base auditor under test: `git cat-file blob
  0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py`
  (sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`)
- Base ledger-read source: `tools/report-landing-audit.py:374-385`
  (`load_errata`), `:438-471` (`check_history_repo`), `:387-410`
  (`apply_errata`), `:139-174` (`lookup`)
- Live authority read: `.ufo/waves/round-24/preregistration.json`,
  `.ufo/waves/round-24/oracle-amendment-1.json`,
  `.ufo/waves/round-24/oracle-supplement-2.json`,
  `.ufo/waves/round-24/oracle-snapshot-before-inspection.json` (44 cases,
  PG29/PG30 are the errata-corrected-missing-SHA pair this lane reproduces)
- Retained grid: `tests/report-audit/repo-state-grid.py` (base 26/26 faults,
  4/4 contracts, 13/13 controls, 0 violations; the reference repair differs
  on F06 and F23 only — see §5)
- Scratch workspace: `/fast/scratch/hyaku/kama-r24/OracleMissingErrata/`

No tool was installed or updated for this lane; no host service, operator
config, fleet, sibling repository or lane Git index was touched; no
commits or pushes were made.
