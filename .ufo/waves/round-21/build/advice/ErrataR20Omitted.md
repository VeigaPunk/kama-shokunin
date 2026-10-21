VERDICT: partial - all four rows are genuine round-20 landed-omitted defects; evidence text misstates the report in row 4 ("absent from the whole report") and row 5 ("measurement table", "only").

Scope: ledger rows 4-7 (round 20, landed-omitted) against draft a29bb84 (parent 7a6bc911) and `.ufo/reports/round-20/kama.md` (11800 bytes; byte-identical to its only fleet commit 04eb5d2, the sole `A` commit for the path). Ledger blob identical to the draft blob.

## 1. Commit facts: all PASS (git show / cat-file -t / merge-base --is-ancestor, exit 0)
| row | commit | author / committer | committer ct | subject (exact match to evidence) | ancestor of 7a6bc91 / a29bb84 |
|---|---|---|---|---|---|
| 4 | 33a6777866d0f63d894ef21bc863486bcb35b56c | kama-shokunin / kama-shokunin | 1792569678 | round-20: named error regression guards, offline GGUF identity, routed corrections and build evidence | yes / yes |
| 5 | 0957ce619789d13bb5779606078fa1498114d2c7 | kama-shokunin / kama-shokunin | 1792571024 | round-20: pin independent capability measurement, official recipe and complete build accounting | yes / yes |
| 6 | 92b146253fd3a8c4bfade94c909dc63b13d6f4a8 | kama-shokunin / kama-shokunin | 1792573685 | round-20: record measurements and validate falsify wave | yes / yes |
| 7 | 846e366dc9dbac58463494a7e05ad060ae3ed3b0 | kama-shokunin / kama-shokunin | 1792574702 | round-20: record falsify wave assignments | yes / yes |

- Cutoff: 04eb5d2 "round-20: kama report" (kama-shokunin), ct 1792577594 (`git log --diff-filter=A --format=%H %ct`, exit 0). Each row commit precedes it by 2892-7916 s.
- Completeness: of 82 lane commits reachable from a29bb84, 9 are kama-shokunin `round-20:` (or `checkpoint(r20)`): the five Landed commits (7a6bc911, 3ec5ea68, 9add96e4, 04de7a87, c7311039) and exactly rows 4-7. No further omission.

## 2. Absent from `## Landed changes`: PASS
The section's bullets (lines 15-19) cite only c7311039, 04de7a87, 9add96e4, 3ec5ea68, 7a6bc911. No >=7-hex prefix of any row commit occurs in the section.

## 3. Evidence text vs report
- Row 4, "absent from the whole report": OVERSTATED. No full hash or >=7-hex prefix exists. But line 7 (Work performed) contains `0957ce619789d13d894ef21bc863486bcb35b56c`, whose last 24 hex are 33a6777's tail (`894ef21bc863486bcb35b56c`), and its wording "committed R20 implementation/frozen population" is row 3's referent for 33a6777. Longest shared substring with the report: 26 hex. Accurate wording: "not cited by hash or >=7-hex prefix; only line 7's corrupted splice token shares its tail".
- Row 5, "cited only in Work performed line 10 and the measurement table": FALSE in two parts. Line 10 (full hash) is correct. Line 7 also names the "original measurement" by a corrupted token starting `0957ce619789d13d`, so line 10 is not the only citation. The measurement table (`## Before → after measurements`, lines 21-29) does not contain 0957ce61; its Measured-commit cells are all 9add96e4. "Not in Landed changes": correct.
- Rows 6 and 7, "absent from the whole report": TRUE. No shared substring of >=6 hex with the report; case-insensitive grep for `92b14` and `846e36` has no hit.

## 4. Audit tool cross-check
Scratch copy at a29bb84; `--fleet-repo /home/vgpnk/Projects/shokunin` passed explicitly because the scratch path has no fleet parent (default is `here.parent`).
- `tools/report-landing-audit.py --fleet-repo ... --rounds 20 --no-errata`: exit 1. Round 20 = 1 unresolved-full-hash (line-7 splice) + 4 landed-omitted, exactly rows 4-7. `cited_elsewhere`: 0957ce61 true (line 10); 33a6777, 92b1462, 846e366 false.
- Same with errata: exit 1, solely because errata rows for r10/r18 are unmatched under the restricted range; the five r20 defects are corrected_by lines 3-7.
- Full range `--no-errata`: exit 1, 9 defects (matches the ledger's "raw 9"). Full range with errata: exit 0, status clean, corrected 9, uncorrected 0, errata_unmatched 0, errata_invalid 0.
- The tool matches errata on (round, kind, token) only (`apply_errata`, lines 166-181). Evidence wording cannot change the audit outcome or C1's counts.

## 5. Re-runnable check
`python3 .ufo/waves/round-21/build/out/ErrataR20Omitted/verify-landed-omitted.py` (read-only, real lane and fleet): exit 1. All 40 commit-level checks PASS (4 rows x 10). Evidence checks: row 6 and row 7 PASS; row 4 FAIL (26-hex shared substring); row 5 FAIL (measurement table does not cite 0957ce61).

## 6. Out of scope, noticed while checking line 7 (row 3)
Row 3 says line 7 "splices the first 16 hex of 0957ce61 ... with the last 24 hex of 33a67778". Byte check: the token equals `0957ce61[:14] + 33a6777[14:]` (26-hex tail); its 16-hex head `0957ce619789d13d` differs from 0957ce61's own `0957ce619789d13b` at index 15. Row 3's correction `0957ce619789d13bb5779606078fa1498114d2c7` is still the right full hash. Not checked: SCORECARD.md:891.

## 7. Limits and records
- Not run: `--selftest` (C1's own check); no other rounds' content verified.
- "Predates" uses committer time, as the tool does; author times also precede the cutoff.
- Ledger is append-only. If the L1 wants evidence corrected, record the correction in the round-21 LOG/report rather than rewriting rows [INFERENCE on policy; the audit outcome does not depend on it].
- Installs/updates: none. Lane, fleet and sibling lanes not modified (lane cloned read-only; git calls under --no-optional-locks; the scratch clone was removed, rm exit 0).
- Files: this report; `out/ErrataR20Omitted/verify-landed-omitted.py` (new).
