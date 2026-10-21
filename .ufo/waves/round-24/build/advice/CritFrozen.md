# CritFrozen: frozen comparison fairness, round 24

Seat: KamaR23-2.CritFrozen-2 (critic, leaf). Base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`, git 2.56.0.
Review time 2026-10-21T17:58:15Z. At that time `build/out/` had no `AuditRepair` or `GridOracle`
directory, so expected outcomes could still be frozen before any candidate existed.

## Verdict

**The comparison is fixable, but it is not fair yet. Six defects must be fixed before L1 grades the candidate.**
The r23 harm got through because the harmed row was ungraded and the grid reported zero violations.
The r24 plan, as specified, leaves four ways for that to happen again:

1. An ungraded or under-pinned row can hide an over-refusal.
2. The new grid has only the r23 auditor as its frozen arm, and r23 already refuses every promisor row. So it cannot show that the candidate restores the r22 verdicts.
3. One required-evidence policy row is still undecided. Whatever the candidate does on it would become the expected answer by default.
4. The closure's own real-lane control cannot be fully restored under preregistration line 10. That gap must be declared now, not discovered after the run.

Impacted axes: operability (over-refusal must count as a failure) and calibration (claims must match what the grid can actually show). The quality trend follows from those two.

## Findings

### F1. The r23 harm was hidden in an ungraded row, and the retained grid would hide it again

- `tests/report-audit/repo-state-grid.py:10-13`: `tradeoff` and `open` rows are "reported, never graded".
- `tests/report-audit/repo-state-grid.py:689`: `T01-blobless-partial-clone` is a `tradeoff` row.
- `tests/report-audit/repo-state-grid.py:797-812`: violations are counted only over fault, control and contract rows.
- `tests/report-audit/isolation-mutants.py:97-99`: mutants are killed only by those same three kinds.
- Filed evidence `.ufo/waves/round-23/final/grid-both.json`: the r23 current arm on T01 gave exit 2, "partial clone (promisor pack)", met false. The r22 frozen arm gave exit 0, met true. Yet current `violations: 0`.
- `MANIFEST.json` `rounds[428].verification.harm_ruling` says exactly this: "this row is explicitly ungraded as tradeoff, so grid green does not establish no harm."
- **Counterexample.** An r24 candidate that still refuses T01 passes the retained grid with exit 0.
- **Smallest correction.** Make T01 a `control` row expecting exit 0 with no defect kinds. Add a fixture premise to `t_blobless` at `repo-state-grid.py:596-602`, which currently has no `require()`: a paired `.promisor`/`.pack` exists, and `rev-list --objects --missing=print` under `--no-lazy-fetch` reports zero missing objects. Without that premise the row can pass trivially on a git that doesn't honor the filter.

### F2. Two exit-2 rows accept any refusal reason

- `REASONS` at `repo-state-grid.py:694-708` has no pin for `F28-shallow-fleet` (line 676) or `F29-broken-branch-same-named-tag` (line 677). Both expect exit 2.
- `met` at `:750-753` only checks a reason when one is pinned.
- **Counterexample.** A candidate that refuses for a generic "missing required object" reason, or any other reason, still meets F28 and F29.
- **Smallest correction.** Pin F28 to `shallow repository` and F29 to `dereferences to tree type`. The latter matches git's own message in the filed r23 stderr tail.

### F3. The new grid's frozen arm (r23) cannot show that r22 verdicts are restored

- The r24 measurement in `preregistration.json:16` is `promisor-grid.py --arm both`, with frozen set to `0df800e`.
- The r23 auditor refuses every promisor-marked repository at `tools/report-landing-audit.py:450-465`.
- So on every expected-exit-2 row (missing tree, blob, ancestor or report, and unknown citation), the r23 arm already matches the exit code. Those rows show no gain for the candidate over r23.
- On complete rows, r23 always fails. Beating r23 there proves only that the candidate doesn't refuse; it doesn't prove the verdicts are the ones r22 gave.
- **Bounded measurement.** I ran `out/CritFrozen/premise.py` (sha256 `e102d0ac…`). Output is in `premise.json` (sha256 `038daf88…`). It used three fixtures, only the two frozen auditor blobs, and no candidate. All fixtures were under `/fast/scratch/hyaku/kama-r24/CritFrozen`, which has 0 entries left.

| fixture | missing objects | r22 on promisor clone | r23 on promisor clone | both on the full lane |
|---|---|---|---|---|
| T01 replica, complete | 0 | exit 0 | exit 2 "promisor pack" | exit 0 |
| blob:none clone, one historical blob missing and not cited | 1 | exit 0 | exit 2 | exit 0 |
| F23 replica, cited blob missing and config removed | 1 | exit 1 `unresolved-full-hash` (false defect) | exit 2 | exit 0 |

- **Smallest correction.** Add a third reference arm, `historical` (the r22 auditor `4fe9339`), to `promisor-grid.py`.
  - Run it only on rows whose premise proves zero missing required objects and every citation found locally. That keeps r22, which lacks `--no-lazy-fetch`, off every row where it could fetch.
  - On those rows, require the candidate's (exit, defect kinds, tokens) to equal r22's and the literal expected values.
  - Report gains in three disjoint buckets:
    - **recovered**: r23 exit 2, candidate and r22 both correct;
    - **safety retained**: r23 exit 2, candidate exit 2, r22 wrong;
    - **reason-only**: same exit, different message. This bucket is never counted as a gain; the closure already ruled that "wording-dependent rows are not independent isolation wins".
- Keep `repo-state-grid.py:32` frozen at r22. Retargeting it to r23 would rewrite the historical baseline, and it would turn the documented "frozen red by design" (lines 17-18) green without any evidence.

### F4. One required-evidence policy row is undecided, so the candidate would define its own expected outcome

- `preregistration.json:9` says an unavailable **required** object gives exit 2. Line 12 says completeness and availability of **required** evidence decide the outcome.
- The `AuditRepair` brief in `spec.json` asks for `rev-list --objects --missing=print` "on pinned lane/fleet commit roots". On the lane, that walks every historical blob.
- What the auditor actually reads:
  - **Lane:** commits only (`:192`, a log with no pathspec), the tip `corpus/SOURCES.md` tree and blob (`:260`, `:268`), and the errata blob (`:383`).
  - **Fleet:** commits and `.ufo/reports/round-N` trees across history (`:216`, `--diff-filter=A`), the HEAD report blob (`:310`) and the HEAD `.ufo/reports` subtree (`:429`).
  - **Citations:** looked up in both repositories (`:139-174`).
- **Counterexample, measured.** In the middle fixture above, a missing historical lane blob that nothing reads takes r22 to exit 0 and r23 to exit 2. A candidate that checks the full lane object closure also gives exit 2. That is an over-refusal under lines 9 and 12, and it keeps r23's harm for any real multi-commit blob:none lane.
- **Smallest correction.** Before `AuditRepair` lands, freeze row `C16-blobless-history-blob-missing` expecting exit 0 with no defect kinds. Its premise is exactly one missing object: uncited and never read. The full recipe is in `out/CritFrozen/expected-row-changes.json`; `OracleMissingNonrequired` may hold the same case.
- If L1 instead wants "full object closure required", that is new hardening the contract doesn't allow. It would have to be preregistered as a declared trade, and per the r23 closure it would still count as harm.

### F5. The closure's real-lane control can't be fully restored under preregistration line 10; declare that now

- The harm ruling's second control: a `--filter=blob:none` clone of the real lane (complete, because the server ignored the filter), rounds 10-22. There r22 gave rc0 with the same JSON as the full lane, and r23 gave rc2.
- `.ufo/waves/round-23/final/audit-historical-ledger.stdout`: round 20 has `unresolved-full-hash` token `0957ce619789d13d894ef21bc863486bcb35b56c`, corrected by `registry/report-landing-errata.tsv:3`.
- I ran `git --no-lazy-fetch cat-file -t` for that token in `kama-shokunin` and in the fleet root. Both fail ("could not get object info"). Neither repository is promisor: there is no matching config and no `.promisor` file.
- **[INFERENCE]** On the promisor-marked lane clone, a candidate that follows preregistration line 10 must give exit 2 for round 20 and for any range containing it. Rounds 10-19, 21 and 22 must give rc0, byte-equal to the full-lane run.
- r22's rc0 there was not built from local evidence alone: r22 lacks `--no-lazy-fetch`, so a missing-token lookup could lazily fetch from the `file://` origin.
- **Smallest correction.**
  - Add this control to the r24 measurement, split into those two expectations.
  - Record the round-20 exit 2 as a preregistered policy row: neither restored nor a regression.
  - Phrase the claim as "restored rounds 10-19, 21, 22; round 20 could-not-evaluate, as preregistered", not "harm repaired".

### F6. Retained rows change meaning; each must be listed, and none counted as a gain

| row | r23 expectation | r24 expectation | class |
|---|---|---|---|
| T01 (`:689`) | tradeoff, exit 0 | control, exit 0 | harm made graded (see F1) |
| F23 (`:670`, reason `:704`) | exit 2 "promisor pack" | exit 2, new unknown-citation reason | reason-only |
| F06 (`:651`, reason `:697`) | exit 2 "partial clone" | exit 2, new reason; the marker must stay absent | reason-only |
| F27 (`:674-675`) | exit 1, landed-unresolved and unresolved-full-hash | exit 2, unknown citation | policy flip: a new refusal |

- **F27 is contested.** `ScribeFrontier/promisor-policy-matrix.md:23` says to keep F27 at exit 1. But `preregistration.json:10` and `AuditRepair`'s "including partialclonefilter" make exit 2 the rule.
  - The fixture's own premise (`repo-state-grid.py:494-496`) proves git tried a lazy fetch.
  - `SrcPromisorCode` cites `promisor-remote.c:148-163`: a filter-only remote registers as a promisor.
  - So the absence really is uncertain, and exit 2 is justified. L1 must still choose before the candidate exists, and must not count the flip as a gain over either frozen arm (both give exit 1).
- **Mutant sensitivity drops.** Mutants M14 (`isolation-mutants.py:46-47`), M22 (`:62-63`), M27 (`:75`) and M29 (`:78-79`) match refusal strings that the repair deletes. With those strings gone, `:119-122` exits 2 (pattern matched 0 times).
  - Worse, the controls that killed M27 and M29 (C09 at `:679`, C10 at `:680`) have no unknown citation. After the repair they cannot kill a boolean-ignoring or pairing-ignoring detector.
  - **Smallest correction.** Add `C14-promisor-false-fabricated` and `C15-orphan-marker-fabricated`. Each is the existing control plus a FAKE full hash outside the Landed section, expecting exit 1 with `unresolved-full-hash`. A detector that treats `promisor=false` or an orphan marker as a promisor gives exit 2 there, which is an over-refusal.
  - Replace the four mutants with named successors. Report per-mutant results rather than comparing against r23's "30/31 killed".
- **Population hash.** Publish the old hash `f29fab8d…364a` and the new one, with a per-row diff ledger. Leave the r23 filed `grid-both.json` unchanged (append only).

## Scoring constraints for the promisor grid (for `GridOracle`)

- A row is met only when all of these hold:
  - the exit code equals the literal expected value;
  - the defect kinds equal the literal expected kinds;
  - the pinned reason substring is present;
  - there is no marker, timeout or traceback.
- Exit 2 on an expected-0/1 row is a failure.
- Do not check a promisor/full pair only against each other through the candidate; a candidate that refuses both would pass. Check each against literal values (`preregistration.json:15`).
- Keep separate counters for over-refusals (expected 0/1, got 2), false verdicts (expected 2, got 0/1) and fetches. A fetch is any change in the fixture's `objects/` listing across the audit; this catches a lazy fetch that succeeded. The gate requires all three to be zero.
- Auditor exit 2 is a row result. Grid exit 2 is reserved for fixture-premise failure, as in `repo-state-grid.py:750-753` and `:814-816`. Otherwise `isolation-mutants.py:93-94` treats a blanket-refusal mutant as could-not-evaluate and never kills it.
- Freeze evidence: before `AuditRepair` writes its candidate, append the expected-table sha256 and a UTC timestamp to `GridOracle.md`. L1 then checks that the candidate's mtime is later.

## Artifacts

- `.ufo/waves/round-24/build/out/CritFrozen/premise.py`, `premise.json`, `premise.stderr` (empty)
- `.ufo/waves/round-24/build/out/CritFrozen/expected-row-changes.json`: the frozen row-change ledger and new-row recipes

## Commands and limits

- I ran: `premise.py` (rc 0, under 1 s, 3 fixtures, frozen r22 and r23 auditor blobs only); read-only `git cat-file` and `git config` on the real lane and fleet; JSON reads of the filed r23 `final/*` files and `MANIFEST.json rounds[428]`.
- Not run: the candidate (none existed), the full grid, the mutants, selftests and the real-lane promisor clone. F5's per-round outcomes are an inference.
- Fixtures used only `file://` clones inside scratch, with the origin URL repointed to an absent path afterwards. There was no network, no transport beyond fixture construction, and no payload execution.
- Tool installs or updates: none.

## Addendum 2026-10-21T18:00Z: frozen auditor pins (cross-check of OracleLocalBlobType)

I checked the pin that `OracleLocalBlobType` sent and it matches. Both auditor blobs used in `premise.py` are listed below:

| arm | revision | `tools/report-landing-audit.py` git blob | sha256 |
|---|---|---|---|
| r23 frozen (new grid) | `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` | `cf706c52233139920da60f8b55d06f031286c4f9` | `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` |
| r22 historical (retained grid) | `4fe9339f8fc3a4a4a479d9c938a850da12f1124d` | `fcc255ce5115a749dfbd09cf992ba9851a2dc90a` | `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f` |

- The lane working-tree file is byte-identical to the r23 blob.
- Both sha256 values equal `auditor_sha256` in the filed `round-23/final/grid-both.json`.
- Their report adds a new measured fact: a citation of a blob that is present locally gets exit 2 from r23 in a promisor repo and exit 0 in the same content without promisor metadata. That is one more over-refusal on r23's side of the "recovered" bucket in F3. It is not evidence of a gain on any expected-exit-2 row.
- `promisor-grid.py` should record both pins in its JSON output, so a later reader can check which auditor each arm ran.
