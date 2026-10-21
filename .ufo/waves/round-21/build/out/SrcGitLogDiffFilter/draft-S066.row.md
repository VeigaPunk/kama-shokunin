# S066 draft — git-log `--diff-filter=A` and `%ct` (kama, contract v1)

Insert after the S065 row in `corpus/SOURCES.md` (`## Registry`). Verified on a scratch copy at a29bb84: frozen census rc 0 (rows 66, every check empty); `tools/sources-append-only.py --from a29bb84 --to HEAD` rc 0 ("added S066 (allowed)").

| S066 | git-log manual (Git 2.56.0) — https://git-scm.com/docs/git-log | docs | A | committer timestamp and added-path selection that a git-log report-cutoff reads; not commit rewriting and not any audit's correctness | §PRETTY FORMATS, placeholder `%ct` ("committer date, UNIX timestamp"); §DIFF FORMATTING, `--diff-filter` ("Select only files that are Added (A), Copied (C), Deleted (D), Modified (M), Renamed (R)"); page "last updated in 2.56.0"; local `man git-log` (Git 2.56.0) carries the same wording; opened 2026-10-21 | `git log --diff-filter=A --format=%ct -- <path>` prints the committer date of each commit that adds the path, newest first by default; `%ct` is committer time, not author time (`%at`). | queued | 2026-10-21 | on-release | — |

## Gate (round lesson, contract rule 1)

- URL https://git-scm.com/docs/git-log; accessed 2026-10-21; revision: manual "git-log last updated in 2.56.0" (2.56.0 dated 2026-09-28); local `man git-log` = Git 2.56.0 (footer 2026-09-27); `git --version` = 2.56.0.
- Quote 1 (4 words), §PRETTY FORMATS, placeholder `%ct`: "committer date, UNIX timestamp"
- Quote 2 (15 words), §DIFF FORMATTING, `--diff-filter`: "Select only files that are Added (A), Copied (C), Deleted (D), Modified (M), Renamed (R)"
- Quote 3 (10 words), §OPTIONS, Commit Ordering: "By default, the commits are shown in reverse chronological order."

## Status and claims

- Proposed status: queued (no lesson or knowledge path cites S066; used-by —). Flip: mined when the round lesson or a knowledge entry lists S066 in used-by.
- C1: supports the mechanics (what `--diff-filter=A` selects, what `%ct` prints). Does not establish `%ct` as a stable landing time; see the report, sections 4–5.
- C2: no statement in this source; no effect.
