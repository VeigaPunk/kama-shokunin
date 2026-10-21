VERDICT: partial - Git docs and runs confirm the --diff-filter=A and %ct mechanics C1 uses; amend and rebase rewrite committer time, so the cutoff is unstable (both error directions reproduced), though no r10-r20 pre/post split flips today

# SrcGitLogDiffFilter (round 21, kama): S066 draft and C1 cutoff basis
Scope: one contract-v1 row drafted; lane, fleet, sibling lanes and MANIFEST untouched; scratch `/tmp/kama-r21-SrcGitLogDiffFilter` deleted. Outputs: `out/SrcGitLogDiffFilter/` (draft-S066.row.md, evidence.txt, experiments.py, rerun-output.txt). Tools: none installed or upgraded (git 2.56.0-1 is current; `pacman -Q git` query only, rc 0; python3 stdlib).

## 1. Source: https://git-scm.com/docs/git-log, accessed 2026-10-21 (reachable)
- Revision: manual "last updated in 2.56.0" (dated 2026-09-28); local `man git-log` = Git 2.56.0. Web and local wording match for each quote. Tier A: official manual, scoped to git-log output fields.
- Q1 §PRETTY FORMATS, `%ct` (4 words): "committer date, UNIX timestamp"
- Q2 §DIFF FORMATTING, `--diff-filter` (15 words): "Select only files that are Added (A), Copied (C), Deleted (D), Modified (M), Renamed (R)"
- Q3 §OPTIONS, Commit Ordering (10 words): "By default, the commits are shown in reverse chronological order."

## 2. Draft row (one row; census-checked on a scratch copy)
```
| S066 | git-log manual (Git 2.56.0) — https://git-scm.com/docs/git-log | docs | A | committer timestamp and added-path selection that a git-log report-cutoff reads; not commit rewriting and not any audit's correctness | §PRETTY FORMATS, placeholder `%ct` ("committer date, UNIX timestamp"); §DIFF FORMATTING, `--diff-filter` ("Select only files that are Added (A), Copied (C), Deleted (D), Modified (M), Renamed (R)"); page "last updated in 2.56.0"; local `man git-log` (Git 2.56.0) carries the same wording; opened 2026-10-21 | `git log --diff-filter=A --format=%ct -- <path>` prints the committer date of each commit that adds the path, newest first by default; `%ct` is committer time, not author time (`%at`). | queued | 2026-10-21 | on-release | — |
```
- Proposed status queued (no lesson or knowledge path cites it; used-by —). Flip: mined once the round lesson lists S066 in used-by.
- C1: supports the mechanics; does not establish `%ct` as a stable landing time (sections 4-5). C2: no statement; no effect.
- Rewrite-rule sources (section 4) are not rows here; they need their own rows if the L1 cites them.

## 3. Mechanics (executed; git 2.56.0 scratch repos; all rc 0)
- E4 delete then re-add: default order lists the re-add first and the add last; the audit's `split()[-1]` returns the first add (ct 1000000100). E5: re-add with an earlier committer time leaves the order and the pick unchanged (linear history).
- E3: `--all`, `--date-order`, `--topo-order` all list the commit with the later committer time first: order follows committer time. Local manual: `--date-order` = "commit timestamp order".
- [INFERENCE] merged concurrent adds: whether `split()[-1]` is the ancestry-first add is not verified.

## 4. Does committer time change on rebase/amend? Yes, by default (executed)
- amend, no date env (E1b, E6b): `%ct` = amend time, `%at` kept; report-commit cutoff 1000000100 -> 1792579747.
- amend `--reset-author` (E1c): `%at` renewed too (git-commit: "This also renews the author timestamp.").
- replaying rebase (E2b): `%ct` = replay time, `%at` kept; cutoff 1000000200 -> 1792579747. No-op rebase ("Current branch feat is up to date.", E2c): commit unchanged.
- `--committer-date-is-author-date` (E2e): `%ct` = `%at`. Manual: "Instead of using the current time as the committer date, use the author date of the commit being rebased as the committer date."
- git-commit documents no committer-date option (`--date`: "Override the author date used in the commit."); only `GIT_COMMITTER_DATE` pins it (E1d; git(1): "The date used for the committer identity when creating commit or tag objects, or when writing reflogs.").

## 5. Effect on C1 (real `audit_round` from lane tools/report-landing-audit.py at a29bb84; executed)
- S1: uncited lane commit b, cutoff 1200: before, landed-omitted b; after a plain amend, `%ct` 1792579989 > cutoff, defects []: false negative.
- S2: commit c at 1250 (correctly post-report): before, no defects; after amending the fleet report commit, cutoff = 1792579989 and c is flagged landed-omitted: false positive.
- Live history: 14 of 60 kama round/checkpoint commits have `%at` != `%ct` (e.g. 7a6bc911f: 1792577448 vs 1792577449); none has ct < at (0 of 82).
- Straddles r10-r20: 0 in both directions, so `%at` and `%ct` give the same pre/post split today. Fleet add commits r10-r20: `%at` == `%ct` for all 11 [INFERENCE: not rewritten].
- Advice (L1 decision, not implemented): record a stable landing fact (e.g. cite the lane tip SHA in the report) or gate out post-landing rewrites. `%at` survived every plain rewrite here, but a caller can set it.

## 6. Validation (scratch copy; commands and exits in evidence.txt section 0)
- Frozen census (CORPUS.md awk checks) at a29bb84: rows 65, A 62, C 3, mined 52, queued 6, rejected 7; every check output empty; rc 0 (matches census-before).
- With S066 appended: rows 66, A 63, C 3, queued 7; every check output empty; rc 0. `git-scm.com/docs/git-log` was absent from the base file; S066 is the next unused id.
- `tools/sources-append-only.py --from a29bb84 --to HEAD`: rc 0, "added S066 (allowed)". `python3 experiments.py`: rc 0 (rerun-output.txt).

## 7. Not tested
- Merges, cherry-pick, filter-repo, `--author-date-order` (manual only). The 8 raw landed-omitted defects were not recomputed.
