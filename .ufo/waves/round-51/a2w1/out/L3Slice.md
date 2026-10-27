Verdict: all 27 scoped ledger classes are mechanically correct; no still-valid content loss warrants literal restoration, but the audited in-place corrections conflict with the files' declared A-corr append-correction practice.

Evidence:
- Read `tools/round51-append-audit-v6-check.py:1-22` and `tools/append-only-audit.py:1-28`: the frozen class is `revert` only for subjects starting `Revert "`, otherwise `in-place-edit` when the deleted line's -U0 hunk adds lines, else `removal`; the key hashes line bytes with one trailing CR removed.
- Read `registry/append-only-contract.tsv:3,9`: SCORECARD declares A-corr, with dated round sections append-only and only its five named re-derived sections region-exempt; the errata TSV declares itself an append-only corrections ledger.
- Read `corpus/QUALITY.md:143` (KQ26): corrections to filed records are appended with superseded text/revision named.
- Data review used read-only `git show --format= --no-ext-diff -U0 <commit> -- <file>` for every exact-file ledger row, locating its deleted line by SHA-256 after trailing-CR removal; each of 27 rows matched exactly one deleted line. Every matching deletion had added lines in its hunk and every deleting subject was not `Revert "…"`; all ledger classes therefore match the mechanical rule.
- Checked each line key against `<tip>:<file>` at `138af25b963450b6520794995605fa7dbbcd87e0`; no original line key remained anywhere in that same file. The diff replacements, however, supplied corrected errata, qualified/revised narratives, repaired pointers, restructured headings, or actual measured results. No case demonstrated that valid substantive content was lost and should now be restored verbatim.
- The three report-landing errata rows at commit `1471344b4c8b` were replaced with revised diagnostics in the same-file diff, and the SCORECARD rows likewise show in-place replacement/updates. Since both contracts require append/correction treatment, the process should have appended named corrections rather than rewriting these graded rows. The table records per-row decisions and categories.

Full per-row table: `.ufo/waves/round-51/a2w1/out/L3Slice/table.md`.

Verification gaps: no campaign counter run was required for this slice audit; no runtime/service was started.