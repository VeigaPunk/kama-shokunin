# GridOracle — integration receipt (append-only)

Lane: GridOracle (oracle lane, round 24). One integration owner: the L1
(`KamaR23-2`). This lane writes **no** production file; everything below is a
candidate artifact under `build/out/GridOracle/` plus this receipt.

## Artifact states

| artifact | sha256 | bytes | state |
|---|---|---|---|
| `promisor-grid.py` (runner) | `d6aa4e74aa1f7dd56167dc8d7e2907642764ea67c8eaf0e419a684f338debdca` | 46189 | **final, frozen** pending fresh falsification |
| `promisor-grid-expectations.json` (manifest) | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | 45580 | **unchanged** since the L1's 44-case snapshot (`1f5a4699…`, byte-identical for those 44 cells) plus the 3 disclosed supplement cells |
| `promisor-grid.patch` | — | — | both new files against the base tree |
| `promisor-grid.cross-repo-fix.patch` | — | — | the exact `cca76aa3` → `d6aa4e74` delta (see below) |
| `population.json` | population sha256 `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` | — | the case table + digest (manifest unchanged, so the digest stands) |
| `candidate.json` | — | — | the last both-arms run; **pre-dates Correction 1/2/3** (it lacks `objects_acquired`, `raw_defects` and the frozen-amended score). The L1's integrated run regenerates it. |

## Why the runner hash changed after the L1's integration

The L1 integrated the runner at `cca76aa3b79fc6864a5ba7b963694bee55e5ec38df85c680b8c3a0cc513dbdc6`
(the Correction-2 state: isolated availability probes, the before/after
object-acquisition pin, the errata ledger enabled per cell, the grade
clarification that pins *uncorrected* defects and reports the raw set, the
failure lists computed after the twin comparison, the unknown-`--case`
rejection, and the frozen arm scored against the amended view). The out
artifact then moved to `d6aa4e74…` because of **one** further change, made
after the MutationOracle sensitivity pass reported a coverage gap.

**Rationale (source, not oracle-fit).** MutationOracle-2 measured that mutant
`PM05-ignore-second-repo` (a lookup that consults only the first audited
repository) **survived** the 47 cells, and that no cell exercised
cross-repository resolution. The cause was in the grid's fixture, not in the
candidate: `build()` accepted a `cross_repo=True` option and never read it
(the only occurrences of the name were the two call sites), so PG26/PG27 were
built exactly like PG07/PG08 — a citation that lives in the lane — and could
not separate "resolved in the second audited repository" from "resolved in the
first". The preregistration's `expected_after[3]` exception clause ("unless
resolved locally by another audited repository") and the L1's crosswalk both
name that semantic, and it had no fixture.

**The change (two hunks, 14 added lines, 0 removed, fixture only).**

1. `build()`: with `cross_repo`, the report's `## Landed changes` section also
   cites the **fleet's own commit** (`fleet: init`), which exists only in the
   fleet. The lane does not hold it, so the citation can only be resolved by
   consulting the second audited repository.
2. `build()`: the premise is asserted before the auditor runs — the token must
   be absent from the lane and present in the fleet, otherwise the cell is a
   harness could-not-evaluate (exit 2) — and is recorded as
   `premise.cross_repo_token`.

**Proof that this is the whole delta.** Reverting exactly those two hunks
reproduces the L1's integrated file byte for byte: the reconstruction hashes to
`cca76aa3b79fc6864a5ba7b963694bee55e5ec38df85c680b8c3a0cc513dbdc6`. The
delta is therefore exactly `promisor-grid.cross-repo-fix.patch`.

**No expectation changed.** The manifest is untouched (`d86b7bea…`); PG26 and
PG27 keep their registered expectations (exit 0, kinds []). Only the fixture
behind them changed.

**Evidence (bounded, no full suite, no candidate sweep).**

| measurement | result |
|---|---|
| `--selftest` | 11/11 ok |
| frozen arm, PG27 | exit 0, kinds [], defects [] (met) |
| frozen arm, PG26 | exit 2 = the r23 metadata refusal = its frozen expectation (met) |
| candidate build `AuditRepair/report-landing-audit.py` sha256 `b5a5ce8c…`, PG26 + PG27 | both exit 0, kinds [], `objects_acquired {"lane": [], "fleet": []}` (met) |
| mutant PM05-ignore-second-repo | now killable from either side: the marked and the plain twin both flip to NOT-MET (the lookup finds the cited token missing and exits 1 instead of 0) |

The candidate file probed (`b5a5ce8c…`) is not the hash MutationOracle quoted
(`47370897…`): the L1 was still editing the candidate between the two runs.
That is a chronology note, not a disagreement.

## Freeze

The runner (`d6aa4e74…`) and the manifest (`d86b7bea…`) are **frozen** as the
lane's final artifact from now on. No further edit will be made without a
disclosed rationale, a named source and an appended receipt entry here and in
`build/advice/GridOracle.md`; a fresh falsification round may require a
correction, which will be appended, never silently applied. The L1 remains the
single integration owner and this lane writes no production file.

**Receipt:** `.ufo/waves/round-24/build/out/GridOracle/RECEIPT.md`

---

## Receipt entry 2 — Correction 4 (L1 source diagnosis of the PG46 exit 0)

**Manifest: UNCHANGED**, sha256
`d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`, 45580 B —
the same bytes the L1 integrated. No expectation, no exit, no kinds, no
defects and no `names_any_of` field was touched.

**Runner: new sha256
`5e96fa6084049550081a63ae532f6152bb56df03a7cf4c3d93364e1c1db02223`** (46189 B
→ the corrected size), replacing the frozen `d6aa4e74…`. Two changes, both
outside the expectations:

1. **PG46 fixture (L1's source diagnosis).** `c_opaque_tree_hides_cited_blob`
   dropped only `opaque_tree`; the cited blob under the missing subtree stayed
   in the store, so the auditor could resolve the token and the cell answered
   exit 0. The cell now drops `("opaque_tree", "hidden_blob")`, the drop map
   carries `hidden_blob -> lane`, and the builder asserts — with lazy fetching
   disabled — that the cited hidden blob is absent from both audited
   repositories, else harness exit 2. This makes the fixture match the
   manifest's already-written PG46 note ("the cited blob d/f is absent but its
   OID is hidden behind that missing subtree"). PG47 and PG48 unchanged.
2. **The exit-2 "names the unavailable content" rule, implemented in the
   runner instead of the frozen manifest.** The L1's rule allows naming the
   unavailable object id **or the required path whose object is unavailable**.
   The manifest listed only the tree object id for the four tree cells, so a
   refusal naming the unread content as `<commit>:corpus/SOURCES.md` /
   `HEAD:.ufo/reports/round-1/kama.md` (a 40-hex id *and* the required path)
   was rejected. The runner now also accepts a `<oid>:<path>` / `HEAD:<path>`
   expression whose path is one of the fixture's declared paths (recorded per
   fixture as `paths`).

**Bounded verification (no full suite, per the L1).** `--selftest` 11/11;
frozen arm: PG15, PG16, PG19, PG20, PG46, PG47 all exit 2 and met; candidate
build `b5a5ce8c…`: the same six cells exit 2 and met — **PG46 now answers exit
2 instead of exit 0**. The five cells MutationOracle reported as unmet by the
pristine candidate were four over-strict pins and one defective fixture, both
on this lane's side; **no candidate gap remains in that set**.

**Freeze.** The runner (`5e96fa60…`) and the manifest (`d86b7bea…`, unchanged)
are the lane's final artifacts. Any further change must be appended here and
in `build/advice/GridOracle.md` with a named rationale and a source.

---

## Receipt entry 3 — the L1's integrated pair, verified

The L1 integrated the grid by surgical composition: the strong `d6aa4e74…`
grader plus the **fixture-only** Correction 4 (the path-based grader loosening
of `5e96fa60…` was declined). Production state observed read-only:

| artifact | sha256 | note |
|---|---|---|
| `tests/report-audit/promisor-grid.py` (integrated) | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | the L1's composition; behaviourally equivalent to my composed `bd2bfaad3c2962744715bec2815bffd7c7ffd875172f959f89daa51947f7a732` |
| `tests/report-audit/promisor-grid-expectations.json` (integrated) | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | **unchanged** since the 44-case snapshot |
| `tools/report-landing-audit.py` candidate build | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | names the actual required tree OID |

Bounded verification of the **integrated** pair (six cells only, no full suite,
read-only against production): PG15, PG16, PG19, PG20, PG46, PG47 all exit 2
and met, 0 violations. The five cells that the pristine candidate left unmet
are met with the strong grader, i.e. with no relaxation of any expectation.

**Filed state unchanged.** The out directory keeps the `5e96fa60…` runner and
this receipt; the path-based loosening is recorded as a **proposal that was not
adopted**. The lane's expectation authority is the manifest
`d86b7bea…` (47 cells; 44 byte-identical to the L1's snapshot plus 3 disclosed
supplement cells).

**Freeze.** No further change from this lane. Any later correction must be
appended here and in `build/advice/GridOracle.md` with a named rationale and a
source.
