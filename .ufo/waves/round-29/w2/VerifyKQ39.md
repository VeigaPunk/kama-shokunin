# VerifyKQ39 — w2 verification (round 29 attempt 2)

Seat: `kama-r29-w2-VerifyKQ39-3` (reviewer, leaf). Claim served: round-28 spot-check
routed repairs (not claims) — verification of the attempt-1 narrative.
Full report: `.ufo/waves/round-29/w2/out/kama-r29-w2-VerifyKQ39-3/report.md`.

## Verdict: all four sub-checks PASS

1. **KQ39 writing-revision rule matches count-c1.py.** KQ39 (`corpus/QUALITY.md:289`)
   judges each statement at writing revision W identified by `git blame --line-porcelain`;
   false at W = calibration mismatch. The counter docstring (`count-c1.py:8-14`) states W
   is the blame-named commit and "A statement HOLDS iff its check passes against the lane
   tree and history at W"; `extract()`/`blame()` (`:128-137,173,228`) and `check()`
   (`:232-265`, all lookups at W: blob, strict_ancestor, ctime, `git grep` at W) implement
   exactly that.

2. **Drift assignment matches.** KQ39: true at W but false later = drift → freshness, not
   calibration. The counter puts into `mism` only statements whose W-evaluation fails
   (`:304-308`); statements holding at W never enter `mism`, and correction rows on them
   are refused as `not-a-mismatch` false corrections (`:314-321`). Drift is excluded from
   calibration by construction. (No explicit freshness ledger; "assigned to freshness" is a
   disposition the counter satisfies operationally — framing note only.)

3. **Correction-row shape matches.** KQ39: appended row preserving the original statement,
   carrying the counter's observed value; missing/duplicate/wrong-value/false correction =
   mismatch. Docstring and code: rows under `## Round 29 — self-assessment corrections`,
   first cell `SA29:<sid>`, last cell exact observed string; append-only = tip starts with
   base bytes; false classes duplicate / not-a-mismatch / wrong-observed, each counted as
   unresolved (`:268-279,309-327`).

4. **CtlBaseTree receipt exercises the drift clause.** Receipt
   (`.ufo/waves/round-29/controls/CtlBaseTree/receipt.json`) has exactly 4 false
   corrections, all `why: not-a-mismatch`: `H:cda32b698f:0`, `N:cda32b698f:0`,
   `H:f4c42debcc:0`, `N:54da210e98:0`. Independently verified:

   - Each holds at W (W = `ea72c3eae4ec` / `83bee7faf5a7`): `tools/kama-probe.sh` md5
     `1f81e859c2d7f43f87d1f7e01327b2cf` + 1092 unterminated lines; `tools/test-snapshot.sh`
     md5 `860f26ac05938cdfc1a8816eff1570b4`; `SKILL.md` 323 unterminated lines (with
     `git show`).
   - Each fails at base `2aa46e24`: md5 `e8bfdcac…` / `3116d459…`, newlines 1138 / 1230.
   - Both W commits are strict ancestors of base (`git merge-base --is-ancestor`), so base
     is later → exactly "true at W, false later" = KQ39 drift.
   - The frozen counter refuses the policy's rows as `not-a-mismatch` false corrections,
     each → unresolved (9 total), `met False`: exercises KQ39's reject clauses "A
     statement is checked only at base … rather than W" and "later drift is called a
     writing-time error".
   - Receipt reproduced exactly: froze counter sha256 `fe11d599…7383` re-run against the
     intact policy clone `/fast/scratch/hyaku/kama-r29/ctl/CtlBaseTree/repo` at
     `93efe2d45da5` → identical receipt field-for-field; appended line:
     `statements 69 mismatched_at_base 11 append_only True valid_corrections 6 false_corrections 4 unresolved 9 met False tip 93efe2d45da5` (exit 0).

## Observations

- The round-28 spotcheck has no literal "calibration-at-writing" heading; anchors are the
  calibration verdict (`round-28-verifier-spotcheck.md:163`, ResSelfAssessment 3/46) and
  routed defect 9 (`:246-247`, SHONEN box 2), answered by C1/KQ39 + repair 9.
- KQ39 "false correction counts as a mismatch" vs counter counting them as `unresolved`:
  functionally identical for the target; documented in docstring.
- Control commit `93efe2d45da5` lives only in the scratch clone (lane object store lacks
  it); receipt reproduced from that clone.

Tooling: no installs. Verification gaps: sibling-covered items (data-tip append-only,
RefPaste, row checks) not re-verified here.
