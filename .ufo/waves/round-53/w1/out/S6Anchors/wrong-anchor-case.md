Case S6-1 (the sample's single wrong anchor)

Citing sentence (SCORECARD.md:707 at lane commit c22602bd8d83ab26349d1087e916ca537ee4f9d1):
  "**C1 calibration (lowest axis):** `SKILL.md:533` claimed check.py "grades
   verdict, reason, exit and drift" and maps harness errors to exit 2; ..."

Last (re)write of the sentence: 82b5e9d33a19 (2026-10-26, "round-45: restore
SCORECARD/LOG/QUALITY/README bodies truncated by the previous commit ... and
re-append round-45 text"). `git show 82b5e9d33a:SKILL.md` line 533 is the
instrument-registry table HEADER:
  533: | Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
The claimed content ("0 all rows pass, 1 a row failed, 2 harness/schema error;
grades verdict, reason, exit and drift") is the "Probe verdict stub matrix"
row at line 535 of that commit (and of c22602bd).

History: correct when first authored — at 54a29268e2 (round-17) SKILL.md:533
was the check.py row. SKILL.md then gained two lines above the table
(53ac-era edit), so by 0718b6ab (parent of the restore) line 533 was already
the header; the round-45 restore re-appended the sentence with the stale
anchor 533 instead of re-anchoring to 535.

Right line today (c22602bd): SKILL.md:535.
Proposed fix: proposed-fix-SCORECARD-707.diff (SCORECARD.md:707 `SKILL.md:533`
-> `SKILL.md:535`).

Note: SCORECARD.md's own append-only contract (registry/append-only-contract.tsv,
SCORECARD.md exempt= region) may require this as an appended correction row
rather than an in-place edit; that routing is the L1's call. The anchor defect
itself is what is reported here.
