# CritExpected — round 24 critic: self-referential expected outcomes

Verdict: **fixable defects, plus one tradeoff the judge has to rule on.** The
preregistration never defines "required" or "complete" evidence, and two of its
bullets contradict each other. Because of that gap, the oracle drafts are
filling in expected outcomes from the *planned implementation* (or from the
same auditor run against a twin), not from the claim itself. Two of the planned
outcomes also contradict each other. The round-24 frozen comparator (r23 base)
refuses every promisor repository. It therefore cannot reveal a candidate that
regresses verdicts r22 got right. Those are exactly the verdicts the round-23
closure used to rule harm.

Scope: static reading plus one bounded offline premise probe in my own scratch.
No candidate auditor was run, no grid, no full suite. Every transport was
blocked with `protocol.allow=never`. Evidence:
`.ufo/waves/round-24/build/out/CritExpected/` (`premise.py`, `premise.json`,
`premise-v2.json`, `freeze-witness.txt`). git 2.56.0.

## Axes
A1 calibration (verdict = ground truth) · A2 operability (no correct verdict
lost versus r22/full clone) · A3 oracle independence (expected outcomes fixed
from construction, before the candidate) · A4 policy/regression separability ·
A5 provenance.

## Findings

### F1. "Required" is undefined, so planned behaviour is setting the expected outcomes (A1, A2, A3)
- `preregistration.json:7`/`:9`/`:12` speak of "complete" clones and
  "unavailable required" objects without defining either.
- The oracle drafts encode two incompatible definitions:
  - **Whole reachable closure from the pinned roots.** CaseHydratedLane
    `out/CaseHydratedLane/hydrated_lane_case.py:332-335` expects
    `unhydrated/clean` and `partial/clean` to be exit 2. That lane is a
    blob:none clone made with `--no-checkout` (`:158-165`). Its only missing
    objects are blobs `f`/`g` (`:120-129`), and the auditor never reads them.
    CaseMarkerLane `grid_fragment.py:28-37` calls F23's missing blob `f` "a
    required object".
  - **Only the objects the audit reads.** The in-progress candidate
    `/fast/scratch/hyaku/kama-r24/AuditRepair/tools/report-landing-audit.py:572-580`
    collects missing closure objects but never refuses on them. Required reads
    fail through `--no-lazy-fetch`.
- **Counterexample (measured, `premise-v2.json`, fixture
  `unhydrated_two_files`, the CaseHydratedLane shape).** The closure is
  missing 2 objects. Every object the audit reads is present (0 missing).
  - r22 frozen `4fe9339f` on the marked lane: exit 0, `[]`. It is identical to
    the full clone and the lane's object count is unchanged, so no fetch
    happened.
  - r23 base: exit 2, "partial clone (promisor pack)".
  - The same pattern holds for `two_commit_blobless_clean` (r22 0 = full
    clone 0), `two_commit_blobless_omission` (r22 1 `landed-omitted` = full
    clone) and `f23_no_blob_citation` (r22 0 = full clone).
- If the closure definition is adopted, these rows go from a correct r22
  verdict to exit 2. That is the same harm class the round-23 closure ruled on
  (MANIFEST `rounds[428].verification.harm_ruling`: "the old verdict is
  correct … loses previously runnable correct cases").
- **The r23 T01 row cannot discriminate.** The `t01_as_r23` probe shows a
  one-commit lane whose checkout hydrates the only blob, so the closure is
  complete. Under both definitions T01 gives exit 0. One matching row is
  standing in for every variant.
- **Smallest correction.** Append a preregistration amendment, before any
  candidate measurement, that defines the required set R as the objects the
  audit reads:
  - lane commits reachable from the pinned tip;
  - lane tip trees and blobs on the paths `corpus/SOURCES.md` and
    `registry/report-landing-errata.tsv`;
  - fleet commits reachable from HEAD, with their root and path trees along
    `.ufo/reports/round-N/kama.md`;
  - the fleet HEAD report blob;
  - the `.ufo/reports` trees listed by `ls-tree -r HEAD`.

  Re-derive the CaseHydratedLane `unhydrated`/`partial` rows as 0/1. Keep exit 2
  for rows that remove an object in R (CaseMissingLaneBlob,
  CaseMissingFleetReport, CaseMissingFleetTree, CaseMissingAncestor, and
  CaseMissingLaneTree only if the removed tree is on the tip path). If L1
  instead keeps the closure definition, every row above has to be declared a
  trade, and the no-trade rule likely rejects it.

### F2. The preregistration contradicts itself on promisor citations (A1, A4)
- `:7`: with valid cited commits, findings must be "exact same … as otherwise
  identical full clones".
- `:10`: any missing citation in a promisor-backed repository gives exit 2.
- `:12`: metadata alone does not establish incompleteness.
- **Shape where they collide.** The Landed commits are valid and a fabricated
  40-hex appears in `## Notes`. Measured `f27_filter_only` (filter-only
  config, closure complete): full clone exit 1 `unresolved-full-hash`; r22 and
  r23 marked lane also exit 1. Bullet `:7` requires 1; bullet `:10` requires 2.
- **The drafts split on it.**
  - CaseUnknownCitation `out/CaseUnknownCitation/expected.json` (A-main,
    required exit 2) follows `:10`.
  - The in-progress candidate (`:107-112`: `absence_is_proof = not
    self.missing`; refusals at `:374`/`:393`/`:461`) returns exit 1 whenever
    the closure is complete. That follows `:7` and `:12`, and violates `:10`.
- **Risk.** AuditRepair was told to "coordinate interface immediately with
  GridOracle". If the grid adopts the candidate's rule, preregistered bullet
  `:10` is silently replaced by implementation behaviour.
- **Note on the candidate's rule.** Tying "absence unknowable" to "closure
  incomplete" is a non-sequitur. An unreferenced cited object can sit on the
  remote whether or not the local closure is complete.
- **Smallest correction.** Amend `:7` to "every cited token (Landed and
  full-hash) resolves locally", so `:10` governs unresolved tokens. Freeze
  CaseUnknownCitation A-main = 2 and B-control = 0 as written, and treat any
  later realignment as a contract change.

### F3. Policy-row changes in the retained r23 grid (A4). Declare these, don't absorb them
r22 = `4fe9339f`, r23 = `0df800e8` (from `.ufo/waves/round-23/final/grid-both.json`
and the probe).

| Row (`tests/report-audit/repo-state-grid.py`) | r22 | r23 | r24 per prereg | Class |
|---|---|---|---|---|
| F06 lazy-fetch (`:651`, reason `:697` "partial clone") | 1 + program executed | 2 | 2; reason becomes unknown citation | reason-pin change |
| F23 promisor pack, no config (`:670`, reason `:704` "promisor pack") | 1 | 2 | 2; reason is unknown citation (under R) or missing closure object (closure definition) | reason-pin change; reason depends on F1 |
| F27 filter-only (`:674-675`, graded fault, want 1) | 1 + executed | 1 | **2** (`:10`; the fabricated token is truly absent) | **policy exit change 1→2 on a graded row** |
| T01 blobless (`:689`, "tradeoff", ungraded) | 0 | 2 (hidden, ungraded) | 0, graded | repair; does not discriminate (F1) |
| C03 fabricated full hash, non-promisor | 1 | 1 | 1 | invariant: the unknown-citation rule must not leak |
| C09 promisor=false, C10 orphan marker, C05 shared clone | 0 | 0 | 0 | invariant |

- **F27 is a regression by the closure's own standard.** The fixture
  constructs a fabricated hash, so exit 1 is ground truth. If `:10` stands,
  F27 has to ship as a declared trade with its rationale (git treats
  `partialclonefilter` as a promisor remote; SrcPromisorCode), and the judge
  rules on it. It must not ship as a silent expectation edit.
- **Reason-pin self-reference.** The old pins "partial clone" and "promisor
  pack" are substrings of the r23 blanket messages. A candidate that words its
  new refusal "…partial clone…" keeps F06 green without proving anything.
- **Correction.**
  - Replace the pins with semantic tokens frozen by the oracle (for example
    `absence is not provable` or `unavailable object <oid>`).
  - Add negative pins: stderr must not match
    `partial clone \((promisor pack|extensions\.partialclone|remote\..*\.promisor)\)`.
  - Record the old and new `population_sha256` (r23 value
    `f29fab8d9af1d02de7f6fa4c7b39b2307113d3716fd4b11cffdd0cd65d55364a`).

### F4. Twin-equality and kinds-only grading are self-referential (A3)
- **Twin treated as authoritative.** `out/CaseMarkerLane/grid_fragment.py:14-18,96`
  says "The twin comparison is the authoritative check … same binary, same
  run". `out/CaseCompleteLane/run-oracle-case.py:30-31` points both arms at the
  live `tools/report-landing-audit.py`, so after integration the reference arm
  *is* the candidate (`agree` at `:168-172`). A candidate that is wrong the
  same way on both arms passes: it refuses both, misses the omission on both,
  or uses a last-touch cutoff.
- **Kinds-only grading.** `repo-state-grid.py:740-753` compares the set of
  defect kinds only, yet the preregistration oracle (`:15`) promises "finding
  IDs". If the reused `run_case` flags the wrong commit as `landed-omitted`,
  the row still passes. CaseHydratedLane and CaseMarkerLane pin kinds only.
  CaseCompleteFleet pins `(kind, sha)` correctly.
- **Correction.**
  - Constructed `(exit, [(kind, token)])` values are authoritative.
  - Twin equality is a secondary check, and its reference arm is the frozen
    blob read through `git cat-file`, never the live path.
  - Extend the r24 `run_case` to compare `(kind, token)` pairs.
  - Change CaseCompleteFleet's `EXPECTED_SOURCE` (`:90-93`) to cite the
    construction, keeping the base auditor only as corroboration (A5).

### F5. The frozen comparator hides regressions against r22 (A2, A4)
- `preregistration.json:16` uses frozen = r23 base. On every promisor row r23
  gives exit 2, so "candidate 2, frozen 2" reads as unchanged even when r22's
  verdict was correct (every F1 counterexample).
- Rows where r23 gives exit 2 for the wrong reason and the candidate gives
  exit 2 for the right reason (C-full, F06, F23) are not improvements.
- **Correction.**
  - Add a third, read-only r22 comparator (`4fe9339f`) for promisor rows, with
    transports blocked. Count every r22-correct → r24-exit-2 row as harm.
  - Count improvements only on rows whose expected exit is 0 or 1.

### F6. Freeze ordering cannot be shown (A3, A5)
- The preregistration was committed in `d1b9d95` at 14:53:46 -0300.
- The candidate already carries +187/−45 in scratch (last write 15:00:06).
- `tests/report-audit/promisor-grid.py` does not exist yet, in either the lane
  or GridOracle's scratch.
- File mtimes only show the last edit. I recorded a content-hash witness of
  every case draft and of the candidate as observed (`freeze-witness.txt`, 72
  lines). Any later change to an expectation table needs a written
  justification that does not cite candidate output.
- **Side note (not an issue).** `:13`'s r23 corrections (69 lane reports, not
  68; 40 of 56 FIFO identities) are already appended at `LOG.md:1418-1420` in
  `d1b9d95`. The falsify `advice/*.md` count is 69 tracked files. Re-appending
  them would create a duplicate authority; reference the existing entry
  instead.

### F7. Residual scope gap (A2), unverified
The closure routed H2 (the git ≥ 2.45 floor) separately. The preregistration
claims "operability harm repair" but never mentions H2, and `--no-lazy-fetch`
keeps the floor in place. Either scope the claim to H1 or record H2 as an
operator-approved prerequisite.

## Policy changes vs regressions (summary)
- **Policy (declare and get a judge ruling):** F27 1→2. The C03 shape under
  any promisor config goes 1→2. The F06 and F23 reason pins change.
- **Regression if the closure definition is adopted:** the unhydrated,
  checkout-only and no-blob-citation blob:none rows go from r22's correct 0/1
  to 2.
- **Repairs:** complete config-only, marker-only, filter-only and hydrated
  rows go from r23's 2 to 0/1. They count only with `(kind, token)` pins.

## Addendum: OracleLocalBlobType (IRC, 18:02Z)
- **The expectation is accepted, and it comes from construction.** The report
  cites a full hash of a locally present blob outside `## Landed changes`. The
  non-Landed lookup has no peel, so the token resolves and the result is exit 0
  with no findings, matching the full-clone twin. This holds in every promisor
  variant. r23 gives exit 2 in all variants except filter-only.
- **Their probe is corroboration only.** It is the r23 auditor with the two
  refusal lines deleted, which is exactly the naive repair. So this row cannot
  kill the blanket-removal mutant. Grade it only in the same arm as rows that
  do discriminate: CaseHydratedLane `unhydrated` (with expectations re-derived
  per F1), CaseUnknownCitation A-main, and F23.
- **Pins:** use `(kind, token)` plus the summary object, not kinds alone.

## Addendum 2: oracle-amendment-1 (18:05Z)
- **What the amendment is.** `.ufo/waves/round-24/oracle-amendment-1.json`
  (sha256 `930b087a…`, committed `123640b` at 15:04:12 -0300) withdraws
  `expected_after[3]` (preregistration line 10) prospectively, marked "not
  counted as achieved". The original `preregistration.json` hash is unchanged
  (`6dde0d72…`).
- **It resolves F2** in favour of lines 7 and 12. The authority it cites is
  independent of the candidate: Main's real-lane closure control includes an
  errata-corrected, locally missing hash that the old rule would abort on.
- **It resolves F1** in favour of the set of objects the audit reads (bullets 2
  and 5).
- **Independence check.** AuditRepair's candidate followed the amendment, not
  the other way round:
  - At about 15:00, per `freeze-witness.txt`, the draft read "absence unknown
    if any reachable object is missing".
  - At 15:05, after the amendment, `AuditRepair/tools/report-landing-audit.py:527-539`
    refuses only a cited token that is in the rev-list missing set (amendment
    bullet 3).
  - I found no evidence that the expectation was derived from the candidate.
- **Updated policy rows.** Declare these; don't absorb them silently.

  | Row | r22 | r23 | r24 (amended) | Class |
  |---|---|---|---|---|
  | F06 lazy-fetch (graded fault) | 1 + program executed | 2 | **1** (`landed-unresolved` + `unresolved-full-hash`), executed = 0 | policy exit 2→1; the isolation half stays graded |
  | F27 filter-only | 1 + executed | 1 | 1 | no change (my earlier F27 trade concern is withdrawn) |
  | F23 promisor pack | 1 | 2 | 2; the cited blob is in the missing set; reason re-pinned | reason-pin change |
  | CaseUnknownCitation A-main and C-full | – | – | **1** (superseded from 2) | mark superseded in its `expected.json`; don't edit in place |
  | CaseHydratedLane `unhydrated`/`partial` | 0 | 2 | 0/1 (bullet 5) | re-derive |
  | Non-promisor repo with a hole whose missing object is cited | 1 | 1 | **2** (the candidate computes the missing set for every store) | new non-promisor policy row; declare it |
- **Discriminators needed.**
  - P07 (OracleLocalBlobType): the cited blob is the hole. It kills the naive
    repair.
  - P08 (proposed): an unrelated hole plus a fabricated token outside the
    missing set, expected exit 1. It kills the "any hole means unknown" rule.
  - P07 alone cannot separate the amendment rule from the over-broad one.

## Addendum 3: P06/P07 reconciliation (parent request, 18:10Z)
Full table: `out/CritExpected/p06-p07-reconciliation.json`. No candidate was
consulted.

- **Exact pins** (`--no-errata`, compared as exact `(kind, token)` lists):

  | Row | Exit | Defects / pin |
  |---|---|---|
  | P06 | 1 | `[(unresolved-full-hash, 0123456789abcdef0123456789abcdef01234567)]` |
  | P07 | 2 | no JSON verdict; stderr names `de1d85fdd17416717224bf9faa67ca1009cc9df1`; stderr must not match the r23 metadata-refusal regex |
  | WrongType (present blob B in Landed) | 1 | `[(landed-unresolved, B)]` only |
  | P08 (unrelated hole + fabricated token) | 1 | `[(unresolved-full-hash, T)]` |

- **OracleLocalBlobType §13 agrees** with these pins.
- **GridOracle's** `promisor-grid-expectations.json` (15:02:29) predates the
  amendment and still grades the withdrawn rule:
  - PG23 and PG24: exit 2 should become exit 1 with pairs.
  - PG22: exit 2 holds only in the P07 shape; otherwise exit 1.
  - PG28: exit 2 holds only if an object the audit reads is missing.
  - PG15 and PG16: the removed tree must be on the tip path.
  - It pins kinds only, and its reason classes are substring bags that do not
    exclude the metadata refusals.
  - It has no P07, P08 or WrongType rows.
  - Sent to GridOracle. The original rows must be kept as withdrawn/not-met,
    not overwritten.
- **Retained r23 grid pairs:**
  - F06: 2 → 1, `[(landed-unresolved, abcdef…abcd), (unresolved-full-hash, abcdef…abcd)]`.
  - F27: 1, with the same pairs.
  - F23: 2, and stderr must name the cited blob oid.
  - The "executed = 0" requirement stays graded.

## Addendum 4: finalized row set (18:08Z)
Checked against `out/OracleLocalBlobType/rows-p08-p09-results.json` and
`out/CaseWrongTypeCitation/expected.json`. Sent to OracleLocalBlobType,
CaseWrongTypeCitation and GridOracle. Pins: `--no-errata`, exit plus an exact
`(kind, token)` list; exit-2 rows name the oid and must not match the
"partial clone (…)" refusal regex.

| Row | Store | Exit | Exact pin | Class |
|---|---|---|---|---|
| P01–P03, P05 | promisor, cited blob present | 0 | `[]`, summary equal to the full-clone twin | repair (construction) |
| P04 | filter-only, cited blob present | 0 | `[]`, summary equal to twin | no-harm |
| P06 | promisor, complete, fabricated token | 1 | `[(unresolved-full-hash, 0123456789abcdef0123456789abcdef01234567)]` | repair (construction) |
| P07 | promisor, cited token is the hole `de1d85fd…` | 2 | stderr names the oid | discriminator (kills the naive repair) |
| P08 | promisor, unrelated hole, fabricated token | 1 | same as P06 | discriminator (kills "any hole means unknown") |
| P08b | non-promisor, same shape as P08 | 1 | same as P06 | uniformity |
| P09 | non-promisor, cited token is the hole | 2 | stderr names the oid | **declared non-promisor policy row** (r22 gives 1); unverified until a candidate run |
| C-WT1 (4 arms) | present blob cited in Landed | 1 | `[(landed-unresolved, 6e98d181389d343031fd578c6a775ce0889a8b0d)]` | invariant |
| P10 (suggested) | C-WT1 plus an unrelated hole | 1 | same as C-WT1 | discriminator on the peel path |

## Addendum 5: pin precisions (18:10Z)
- **OracleLocalBlobType §15** adopted the exit-2 form for P07, P09 and F23:
  - stderr starts with `could-not-evaluate:`;
  - stdout is not a JSON verdict;
  - stderr names the oid;
  - stderr must not match the metadata-refusal regex.

  On that fixture, the base's stderr fails both the "names the oid" and the
  "must not match" pins, so the pins separate base from repair.
- **F06/F27 token literal:** `abcdefabcdefabcdefabcdefabcdefabcdefabcd`
  (`repo-state-grid.py:275`, `:487`).
- **F23 oid:** pin the value the builder returns (`rev-parse lc:f`), not a
  literal.
- **PG15/PG16** remain unmeasured by both lanes.

## Addendum 6: P10 measured (18:12Z)
- **P10 (promisor) and P10b (plain store): exit 1**, exactly
  `[(landed-unresolved, 4c226b603e6a26a14212b131fcac232ca7318852)]`.
  - The lane's missing set is only `f40b7a32…`, so T is not in it.
  - P10b base and the refusal-removed probe both give that pair; P10 base gives
    exit 2 (the blanket refusal).
  - Source: `out/OracleLocalBlobType/rows-p10-results.json`.
- **Rationale correction sent:** the full-hash scan includes Landed tokens
  (`tools/report-landing-audit.py:285` with no SOURCES, `:293` with SOURCES),
  so T goes through both lookups. The no-peel lookup resolves T, so the
  discriminating weight is on the peel path.
- **Keep the two T values apart:** P10's T (`4c226b60…`) is not C-WT1's
  (`6e98d181…`).

## Addendum 7: builder-relative pins (18:14Z)
- **OracleLocalBlobType §17 adopts builder-returned tokens and oids** for F23,
  P07, P09, P10 and P10b. The literal values are snapshots of byte-fixed
  content.
- **PG15/PG16** remain unverified in both reports.
- **Correction sent:** Landed tokens are always in the no-peel full-hash scan.
  This holds with or without SOURCES (`tools/report-landing-audit.py:285` and
  `:293`), so an absent Landed 40-hex token gives both `landed-unresolved` and
  `unresolved-full-hash` in every fixture.

## Unverified
- Candidate behaviour (not run). The F2 claim about it comes from reading the
  scratch source.
- Whether `git log` and `diff-tree` fail rather than skip on missing trees or
  ancestors in promisor repositories (CritCompleteness owns this).
- No tools installed. Scratch `/fast/scratch/hyaku/kama-r24/CritExpected` was
  left empty (the probe used a temporary directory).
