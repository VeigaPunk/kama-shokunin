# ScribeSrcMergeBase — scoped findings

- Opened and saved `https://git-scm.com/docs/git-merge-base` to `.ufo/waves/round-29/w1/out/ScribeSrcMergeBase/page.html`; SHA-256 `0dc2f88a4935851e824b3d35c8236d7d4ad4603554b2ff24cc25ec83962868f3`.
- The `--is-ancestor` section documents exit 0 when the first commit is an ancestor of the second, 1 when it is not, and another nonzero code for errors. The installed Git 2.56.0 manual contains the same text; online page says last updated in Git 2.43.0.
- C1's helper rejects equal commits before using `git merge-base --is-ancestor`, so strictness is the counter's guard, not wording attributed to the Git manual.
- Proposed row S175 and its Gate quote are in `.ufo/waves/round-29/w1/out/ScribeSrcMergeBase/row.md` and `quote.txt`; detailed commands, outcome, provenance and limits are in `REPORT.md`.
- UTC sample was `2026-10-23T12:03:03Z`, collected concurrently with `curl`; subsecond HTTP transaction time was not recorded. No lane source file was edited and no counter/test was run.
