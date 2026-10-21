VERDICT: partial - correction 0957ce61 is the right single referent for report line 7; row 3's evidence misstates the splice (15+25 hex, not 16+24) and row 5 misstates where 0957ce61 is cited

Scope: read-only. Lane not modified; no installs; no official measurement; no persistent process. Evidence: `out/ErrataR20Splice/splice_check.py` (rc0, 26 PASS / 0 FAIL, saved in `splice_check.stdout`) and `out/ErrataR20Splice/commands-run.txt` (every command with rc).

## 1. Splice: which real commits
- T = 0957ce619789d13d894ef21bc863486bcb35b56c (report :7) is an object in neither repo (`cat-file` rc128 in both).
- Prefix/suffix scan of all 197 lane and 1022 fleet commit objects: exactly one pair with >=8 matched chars.
  - A = 0957ce619789d13bb5779606078fa1498114d2c7: prefix match 15. Lane commit 05:23:44 -0300, "round-20: pin independent capability measurement...".
  - B = 33a6777866d0f63d894ef21bc863486bcb35b56c: suffix match 26. Lane commit 04:05:09 -0300, "round-20: named error regression guards...". A's parent is B.
- T = A[0:15] + B[15:] exactly: "0957ce619789d13" + "d894ef21bc863486bcb35b56c". Index 15 is `d` in T and B, `b` in A. A split at 14 also fits (all three have `3` there); 15 is the maximal A-prefix.
- Row 3's stated composition, "first 16 hex of 0957ce61 + last 24 of 33a67778", gives 0957ce619789d13b894ef21bc863486bcb35b56c, which is not T. The evidence is off by one at the junction.
- Hamming distances: T-A 25, T-B 14. This follows from the split alone, so it is not evidence of intent.

## 2. What report line 7 describes
It is a Work-performed bullet. The round-20 author reused, without re-running, "the committed R20 implementation/frozen population and original measurement at <T>". Wave 1's 72 seats and the original evidence are said to sit under `build/` and `runs/0957ce61/`. The bullet cites LOG.md:1204-1227 and SCORECARD.md:865-930, and those assign the two roles to two different commits (hashes shortened here):
- LOG.md:1204-1206 (lane HEAD): "Work/frozen population landed 33a67778; counting tools/recipe completed at measured 0957ce61." LOG.md:1207-1208 runs the official recipe with `--out .../runs/0957ce61`.
- SCORECARD.md:891-892: "Work/frozen-population commit 33a67778; measured tree 0957ce61."
- `runs/0957ce61/commands.json`: `"measured_commit": "0957ce619789d13bb5779606078fa1498114d2c7"`.

## 3. Right referent: 0957ce61 (33a67778 fits only one clause)
A single commit must hold every referent of the sentence:
- 33a67778 is the parent of 0957ce61. `CensusHarness/` and `tools/` are identical between the two (`git diff --quiet` rc0), so 0957ce61 contains the implementation and frozen population.
- The measurement and accounting exist only from 0957ce61 on: `recipe.json`, `c1/`, `c2/`, `build/completion-summary.json` (spawned 72, 70 completed, 2 dead) and `build/verdict-count.json`. 33a67778's round-20 tree has none of them.
- 0957ce61 precedes the corrected rerun 9add96e4 (ancestor rc0). "Original" therefore means 0957ce61, not the table's "Measured commit" 9add96e4.
- Report :10 is accurate: `SKILL.md:652-656` at 0957ce61 contain the routed rows.
- The non-author closure 221707d2 (MANIFEST.json:10112, defect D1) also names 0957ce61 as the correct commit.
- 33a67778 alone leaves "original measurement" and the 72-seat accounting unpinned. [INFERENCE on author intent; the facts above are observed.]

## 4. Earliest occurrence (origin)
- Fleet: 04eb5d2d9b4712c5266bdc36fbb16c2fefd7b392 (07:13:14 -0300, kama-shokunin, "round-20: kama report"). Blob 54b1aff4 is `.ufo/reports/round-20/kama.md`, and this is the file's only commit (+67 lines). The 8996-object scan finds T in 5 blobs; the other four are MANIFEST.json versions from 221707d2 (07:16:43, protocol-shokunin closure) onward.
- Lane: 00aa1486a0dee3375d6e974adc45ee501d7ab4d7 (empty subject, parent 7a6bc911, 07:24:53; kept only by `refs/jj/keep/`) and a29bb84 (master; identical tree). Blob 19fef3a9 is `registry/report-landing-errata.tsv`. The 3582-object scan finds no earlier lane object holding T.
- Origin: T has been in the round-20 report text since its first commit, 04eb5d2d. The lane ledger copied it about 12 minutes later. Fleet never amended the report. How the two hashes were joined is not recoverable from git. [INFERENCE: composed by hand from two hashes both present in LOG.md of that round.]

## 5. Other defects in the same ledger (not the token)
- Row 3 evidence: "first 16 hex" should read 15 and "last 24" should read 25.
- Row 5 evidence says 0957ce61 is cited in "Work performed line 10 and the measurement table". The measurement table (report :23-26) contains no 0957ce61 hex; only line 10 does. The same error appears in `.ufo/waves/round-21/build/advice/LessonDraftC1.md:26`. Classification is unaffected: landed-omitted depends only on the Landed section (`tools/report-landing-audit.py:119-137`); `cited_elsewhere` is annotation.
- Row 4 "33a67778 absent from the whole report" is true: no "33a6777" substring in the report.
- The ledger is append-only. Any wording fix should be an appended note, not an edit of row 3 (L1 decision). Per `apply_errata` (`tools/report-landing-audit.py:166-181`), a second row with the same round, kind and token would match the same defect and not be reported unmatched. [INFERENCE from code; not executed, since the audit is an official path.]

## 6. Recommendation to L1
Keep the correction 0957ce61. Record the evidence corrections as an appended note: the row-3 composition is first 15 hex of 0957ce61 plus last 25 hex of 33a67778, and row 5 should cite report line 10 only (line 7 carries the splice, not 0957ce61).
