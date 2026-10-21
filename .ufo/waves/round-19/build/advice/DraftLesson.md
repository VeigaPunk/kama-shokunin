VERDICT: partial - C1 counts reproduce; the C2 sentence inverts the grid polarity and the S057 quotes are miscounted or not verbatim; corrected drafts are in /tmp/kama-r19-DraftLesson/out.

Scope: DraftLesson, draft sections for corpus/lessons/round-19.md (Declared claims, Gate, Mistakes candidates, Measurement plan). Work in /tmp/kama-r19-DraftLesson (copy of lane tip 1b85a24 plus round-19 tree). Lane not modified. Full receipts (commands, exits, artifacts): /tmp/kama-r19-DraftLesson/out/receipts.md. Corrected sections: /tmp/kama-r19-DraftLesson/out/round-19-sections.md.

Findings (each with an executed command and observed exit):
1. C1 count reproduces: `python3 tools/citation-provenance.py` -> `required=3 found=3 verified=3 missing=0 mismatch=0`, exit 0. With HEAD docs (`git archive HEAD`) -> `missing=3`, exit 1. `--selftest` -> exit 0.
2. All three C1 tokens sit in corpus/lessons/round-18.md. `grep -c 'cite('` gives SOURCES.md 0 and SCORECARD.md 0 tokens (one prose line). The SOURCES/SCORECARD corrections are not machine-bound.
3. The checker has no document precedence: `check()` accepts a token from any default doc. A duplicated token in a non-authoritative doc passes. Not covered by the 5 selftest cases.
4. C2 polarity error in the draft: "consistent swaps ... are accepted 0/3 before the pin and rejected 3/3 with it" inverts the meaning. Observed (advisory, receipts 1-3, pins from each receipt): no pin -> `rejected=0/3 tree_pin=off`, exit 1; with pin -> `rejected=3/3 tree_pin=on`, exit 0. Correct sentence: before the pin the consistent swaps are accepted 3/3; with the pin they are rejected 3/3.
5. Tree pin is self-referential: run.py takes the pin from the producer's own install_tree() of the same server; the dry run took it from the receipt's recorded install_tree_sha256. Record it as an observed value, not a constant.
6. Negative pin (64 zeros) -> `check-receipt.py` exit 1. Pinned gate on receipt-1 -> exit 0, VALID.
7. S057 (man7 ld.so(8), page Linux man-pages 6.19, 2026-08-03; opened 2026-10-21; sha256 d9b7737e...379f83): the registry's "11 words" quote is 10 words; the "14 words" $ORIGIN quote is a composite with an ellipsis, not verbatim. Verbatim replacements: "are searched only to find those objects required by DT_NEEDED" (10); "do not apply to those objects' children" (7); "This expands to the directory containing the program or shared object." (11); the sibling-library example sentence (20 words).
8. S057 is not in registry/required-citations.json, and round-19.md is not in the checker's default docs, despite the S057 used-by cell.
9. The draft's Gate row "A tree digest authenticates execution" is not in the page; it is an [INFERENCE] and must be marked so. The row "Lawful interception / name-service query" is a stray carry-over and should be deleted.

Advisory measurement vs official: the grid and gate runs above are subprocess validators in my copy, not the official harness (which needs a clean commit). No listener was opened. The C2 "baseline VALID" claim is observed only in this dry run.

Tooling: no installs or updates were made. Standard tools only (curl, python3, git, sha256sum).

Action for the main agent after the wave: correct the C2 polarity and the S057 counts in round-19.md and SOURCES.md before the official run; add the duplicate-token precedence selftest and confirm it fails first; then run the official measurements listed in round-19-sections.md §Measurement plan.
