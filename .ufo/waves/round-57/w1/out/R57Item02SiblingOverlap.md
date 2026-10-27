# R57Item02SiblingOverlap — cross-claim and sibling-overlap scan (C1 stale count, C2 canonical-row binding)

Seat: `R57Item02SiblingOverlap` (connector, leaf; no subagent dispatch). Read-only on the lane. Writes: this file, the case-23 file `.ufo/waves/round-57/reports/R57Item02SiblingOverlap-case23.md`, and receipts under `.ufo/waves/round-57/w1/out/R57Item02SiblingOverlap/`. Scratch: `/fast/scratch/hyaku/kama-r57/R57Item02SiblingOverlap/`. No commits, jj/git mutations in the lane, no shared-file edits, no installs (RULES read; pacman untouched; none needed).

Report path: the spec text I was given names a "Report trailer path" but does not state the literal path. I used the round-56 convention `.ufo/waves/round-57/w1/out/<seat>.md`. Planner: confirm or correct.

Tips: frozen base `b89bdab2`; lane HEAD at seat run `7b74e2f2` (all numbers below are at that tip unless stated). Lane moved to `8a7f1976` during the run; the counter and round-56 checker bytes did not change between those tips.

## Verdict

The overlap is material. Five things block C1 and C2 from being measured as independent claims:

1. **The claim labels exist in three versions.** The wave spec context and `controls/freeze.txt` (commit `89dc4f52`) say C1 = calibration stale canonical capability-row count / `maxN`, and C2 = operability canonical-row execution binding. `controls/freeze-amendment.txt` (commit `7c873d7b`, "supersedes the earlier round-57 freeze's claim ordering only") says C1 = operability round-56 prereg-checker no-op control, and C2 = calibration round-42 stale verifier-spotcheck count. The landed record (`LOG.md` at `7b74e2f2`, `corpus/lessons/round-57.md`, and the SCORECARD round-57 section at `8a7f1976`) follows the amendment. The dispatch spec was not updated, so seats disagree about what C1 and C2 are.
2. **C1's stale count is already repaired at tip, and its "maxN 56 vs 46" part is not a failure input.** The frozen base reproduces `mismatches=1` from one calibration fact. At `7b74e2f2` the same counter reports `mismatches=0 met=True`. `maxN` is never compared with 46: it is derived from the `## Round N` headings and enters `met` only through the banner and Planned consistency checks, which pass at 56.
3. **C2 has no distinct frozen predicate.** `controls/base-c2-frozen.out` is the same round-42 counter output as `base-c1.out`, differing only by one extra line (`base_c1_exit=1`). Its no-op control, `noop-c2.out`, is a fixed-print stub, not a canonical-row check.
4. **Canonical rows are not execution- or content-bound by any counter.** The 11 round-49 rows have zero run facts and zero SHA-256 digests; their evidence pointers are checked only for `tools/`/`registry/` tokens being present in `PROVINCE.md`. A dead evidence pointer and a mis-bound row both pass (case-23 file).
5. **Shared surfaces and a changed frozen instrument.** Both claims write to `tools/round42-selfdesc-reconcile.py` (`canon()`, `maxN`, `caps`, and the imported round-41 run machinery) and to `SCORECARD.md` (calibration row at line 18, round-49 table at lines 2844–2860). Separately, `7b74e2f2` edited `tools/round56-prereg-check.py`; the round-56 preregistration still records its frozen SHA-256 as `c7b0d787…` (`.ufo/waves/round-56/preregistration.json:22`), while HEAD's file is `dee6f922…`.

## Evidence

Commands run from the lane with `TMPDIR` set to scratch. Counters write nothing to the repo without `--out`. Exit codes are shown.

**E1 — frozen base vs HEAD for the round-42 counter**

```
$ python3 tools/round42-selfdesc-reconcile.py --repo <lane> --tip b89bdab2cc114735ec5d331c6c610134258f7864
tip=b89bdab2cc114735ec5d331c6c610134258f7864
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
exit=1

$ python3 tools/round42-selfdesc-reconcile.py --repo <lane> --tip 7b74e2f2515a6f598918488fa5144658ff29925f
tip=7b74e2f2515a6f598918488fa5144658ff29925f
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=56 met=True
exit=0
```

Spotcheck blobs: `git ls-tree -r --name-only <tip> corpus/lessons | grep -c 'verifier-spotcheck.md$'` gives 43 at `b89bdab2` and at `7b74e2f2`. The calibration row (SCORECARD line 18) reads `→ \`42\`` at `b89bdab2` and `→ \`43\`` at `7b74e2f2`; `7b74e2f2` is the only commit that changed it (`git log -- SCORECARD.md`).

**E2 — the frozen C1 and C2 base receipts are the same counter output**

```
$ diff controls/base-c1.out controls/base-c2-frozen.out
4d3
< base_c1_exit=1
exit=1
```

`controls/noop-c2.out` is `control=no-op instrument / canonical_table_reads=0 / self_description_reads=0 / summary=mismatches=0 maxN=46 met=True / exit=0`. That summary line is hard-coded in `controls/c1-noop.py` (`print("mismatches=0 maxN=46 met=True")`), so neither no-op control reads the canonical table.

**E3 — canonical rows (round-49 table, SCORECARD lines 2844–2860; 11 rows)**

Scripted over the evidence column at `7b74e2f2`: run facts 0 per row, sha256 0 per row. The 20 backticked `tools/`, `registry/`, `corpus/`, `.ufo/`, `scripts/` paths in evidence cells all exist at tip (`git cat-file -e` passed for all 20). The `## Capabilities` mirror has 11 rows with names equal to the canonical table. The Retired section states `11 capabilities`, which the counter checks.

**E4 — the round-42 counter does not read canonical evidence beyond names, PROVINCE tokens, and maxN**

From `tools/round42-selfdesc-reconcile.py`: `canon()` (highest `canonical list as of round N` heading; names and first-working rounds), `caps` (head names equal canonical names), `province` (`tools/`/`registry/` tokens in canonical evidence must appear in `PROVINCE.md`), `receipts` (only sections whose headings name rounds 40 and 41), `rel` (Axes rows only). No canonical row's command is executed. The `run_fact`/`RUN_RE` runner in `tools/round41-scorecard-reconcile.py` is applied only to `## Axes` rows.

**E5 — fixtures (case-23 file has the full table)**

| variant | edit | exit | met |
|---|---|---|---|
| base `7b74e2f2` | none | 0 | True |
| v1 (round-49 heading only) | orphans the 11 rows | 0 | True |
| v1c (round-49 block, 17 lines) | whole block deleted | 0 | True |
| v2-deadpointer | evidence pointer → non-existent path | 0 | True |
| v3-wrongbind | evidence pointer → existing unrelated `tools/pin-watch.py` | 0 | True |

**E6 — round-56 checker: frozen hash drifted in-round, verdict unchanged at both tips**

```
$ git show b89bdab2:tools/round56-prereg-check.py | sha256sum   → c7b0d787f348691b…  (matches .ufo/waves/round-56/preregistration.json:22)
$ git show 7b74e2f2:tools/round56-prereg-check.py | sha256sum   → dee6f922d0d93b10…
$ python3 tools/round56-prereg-check.py --repo <lane> --tip b89bdab2…  → present=1 roster_match=1 kills=1 controls=2 met=True  exit=0
$ python3 tools/round56-prereg-check.py --repo <lane> --tip 7b74e2f2…  → present=1 roster_match=1 kills=1 controls=2 met=True  exit=0
```

I did not run the no-op fixture against the new checker; the SCORECARD round-57 section reports that it now returns `met=False`, which I have not verified.

**E7 — seat overlap and peer outputs (read-only)**

- `X01SiblingOverlap`, `R57Item02SiblingOverlap` and `R57Item22SiblingOverlap` have identical scope text ("Cross-claim/sibling overlap scan of C1 stale count and C2 row-content execution target"). I checked 02 against 22 for equality of the prompt before the `Distinct case` clause: equal.
- `out/R57Item09ClaimFalsifier.md` already records the claim-ordering conflict, reported and not resolved.
- `out/R57Item04CanonicalBinding.md` (`case25`) builds its own canonical-row audit prototype (`canon-row-audit.py`). It overlaps this seat's C2 target and should be compared with the counter, not with my fixtures.
- Commit `7b74e2f2` (author `kama-shokunin`, 15:06:45, inside the wave window) touched `LOG.md`, `SCORECARD.md`, `corpus/lessons/round-57.md` and `tools/round56-prereg-check.py`. The spec tells seats not to commit. I cannot attribute authorship from the commit record and have not tried.

## Risks and limits

- Any fix to `canon()`, `maxN` or the `caps`/`province` legs changes C1's and C2's receipts together. Both claims need separate counters (or serialized edits) before either is admitted.
- A canonical-row binding should not reuse `tools/round42-selfdesc-reconcile.py` alone: E3 and the fixtures show the existing counter is blind to omission, dead pointers and rebinding.
- The round-56 checker's frozen hash no longer matches its preregistration. Either the preregistration is re-anchored with a dated amendment, or the change is treated as a new instrument and not as the frozen one.
- The "expected 46" value is the round-46 measured receipt (`maxN=46` in the SCORECARD round-46 results). It is stale history, not a computed expectation.

## Recommendations to the planner (routing only, no decision made)

1. Name one claim ordering in the spec and in `freeze.txt`, or record both in the wave's claim table with their dates; the landed LOG/lesson/SCORECARD currently follow the amendment.
2. If the canonical-row claim stays, freeze it as a separate predicate with its own base receipt. The current `base-c2-frozen.out` duplicates C1 and is not evidence for C2.
3. Serialize writes to `tools/round42-selfdesc-reconcile.py` and to the round-49 table in `SCORECARD.md` across the two claims.
4. Route the round-56 checker hash mismatch to the claim owner (seat R01ClaimFalsifier and the round-56 preregistration).

## Checks for the main agent (not run by this seat)

- `python3 tools/round42-selfdesc-reconcile.py --repo <lane> --tip 7b74e2f2515a6f598918488fa5144658ff29925f` (expect `met=True`, exit 0 at that tip).
- `python3 tools/round56-prereg-check.py --repo <lane> --tip 7b74e2f2515a6f598918488fa5144658ff29925f` (expect `met=True`, exit 0).
- Re-run the case-23 fixtures only if the canonical block changes again.

## Receipts

`.ufo/waves/round-57/w1/out/R57Item02SiblingOverlap/`: `base.round42.{out,err}`, `v1-omit49.round42.{out,err}`, `v1c-omit49-block.round42.{out,err}`, `v2-badpath.round42.{out,err}`, `v2-deadpointer.round42.{out,err}`, `v3-wrongbind.round42.{out,err}`, `prereg-{b89bdab2,7b74e2f2}.{out,err}`, `fixtures.tsv`.
