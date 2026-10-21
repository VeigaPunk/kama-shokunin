VERDICT: partial - the seven verdicts and the 6/1 and 4/3 totals in `.ufo/waves/round-18/residual/assignments.json` match the committed advice; the file is a retrospective roster first committed at 7229fa9, with no dispatch, spawn, or role evidence, so the "Dispatch record" label in round-18.md:389-394 is wrong.

Scope: leaf seat `CloseKama18.AssignmentsLabel-2`. Lane `kama-shokunin` at 37bd4c5 was read only (git read commands, `_grep`, `_read`). No lane file, index, or git state was changed. Drafted sidecar: `.ufo/waves/round-20/build/out/AssignmentsLabel/assignments.PROVENANCE.md` (for the L1 to place at `.ufo/waves/round-18/residual/` in the lane; not placed by me). No installs. No scratch directory created.

## Commands and results (all run in the lane; exit shown)

1. `git log --format='%h %ad %s' -- .ufo/waves/round-18/residual/assignments.json` → exit 0; one commit: `7229fa9 Wed Oct 21 02:55:06 2026 -0300`.
2. `git show --stat 7229fa9` → exit 0; `residual/assignments.json | 48 ++`, same commit adds `corpus/lessons/round-19.md`.
3. `git status --short -- .ufo/waves/round-18/residual/` → exit 0, empty; `git diff --stat HEAD -- …/residual/` → exit 0, empty.
4. `sha256sum` of `git show 7229fa9:…assignments.json`, working file, and `git show 37bd4c5:…` → all `8d3a9aee251e700319f93210de7bdd945730fdb3d83fc17e5f109451ef389226`, exit 0.
5. `git log -- .ufo/waves/round-18/residual/advice/` → exit 0; only `888cd38 Wed Oct 21 01:58:02 2026 -0300`.
6. `git ls-tree -r --name-only 1b85a24 -- …/residual/` → exit 0; advice files only. `git ls-tree --name-only 888cd38 -- …/residual/advice` → exit 0; `assignments.json` absent.
7. Line-1 `VERDICT:` of the 7 advice files (`grep -n -m3 -iE verdict`, exit 0): Privacy confirm, Health confirm, ImplPin confirm, CounterC2 confirm, CounterC1 partial, Claims partial, Corpus partial. File's seats and totals (6 reviewer, 1 critic, 4 confirm, 3 partial) match, checked by hand [INFERENCE: no script run].
8. `git blame -s -L 311,320 corpus/lessons/round-18.md` → exit 0, all `0c75c61`; text matches the file's `call` field. `git blame -s -L 387,396` → exit 0, all `7229fa9`; the "Dispatch record (defect 4)" wording.
9. `git log --all --oneline -- '*residual/assignments.json'` → exit 0; `7229fa9`, `ab95aef`, `e7ba3ce`. `git cat-file -p` of `ab95aef` and `e7ba3ce` → exit 0; both tree `2fd9fbe`, both change-id `qnvsluswkvwlnulutplrtzlyrmxuqrut`, parent `8bf99ca`. `git branch -a --contains ab95aef` / `e7ba3ce` → empty (not on any branch). `git reflog --all | grep` → exit 0; only `7229fa9` entries.
10. `git merge-base --is-ancestor 7229fa9 37bd4c5` → exit 0 (yes). `git rev-parse --short 7229fa9^` → `8bf99ca`.
11. `_grep` for `ResidPrivacy` over the lane and fleet `.ufo` (gitignore off) → hits only in the residual files, round-19 advice, lesson files, and `.ufo/reports/round-18/kama.md:54-55` (narrative "one ordinary `task` call"). No spawn, dispatch, or taskCall record found.
12. `git rev-parse --short HEAD` → `37bd4c5`; `git status --short` → `?? .ufo/waves/round-20/` only (the L1's own wave dir).
13. `mkdir -p .ufo/waves/round-20/build/out/AssignmentsLabel` → exit 0.

Tool installs/updates: none.

## Findings

- F1 (verified). Introduced at 7229fa9, one commit after the round-18 residual advice (888cd38) and after the round-18 measured pass (1b85a24). It is a post-hoc record. Blob unchanged since; mtime 03:12:31 is not provenance.
- F2 (verified). Verdicts and totals agree with committed advice line 1.
- F3 (verified). The `call` field is copied from round-18.md:311-319, which was committed before the file existed. No dispatch record exists in the repo or in the fleet `.ufo` search.
- F4 (unsourced). Roles: no committed artifact states a role; "critic" for ResidClaims is [INFERENCE] from its name only.
- F5 (defect in an earlier label). `corpus/lessons/round-18.md:389-394` says "Dispatch record (defect 4)". That is wrong and should be corrected by appending a correction (not by rewriting). `corpus/lessons/round-19-verifier-spotcheck.md:51,197` already labels it retrospective; `round-19/build/advice/R18Defects.md:14` says roster only. The round-19 corrections in `round-19.md:8-10` also rely on it as a carrier of the correction.
- F6 (observation). `ab95aef` and `e7ba3ce` are jj same-change-id siblings of `7229fa9` (same tree, unreachable from any branch). Not a provenance problem for the blob, but the commit history of this file is not linear and should be noted if the L1 cites the commit.

## Provenance note (drafted)

`.ufo/waves/round-20/build/out/AssignmentsLabel/assignments.PROVENANCE.md` (3104 bytes). It says: retrospective, written in round 19, not the original dispatch; sha256; first commit 7229fa9; absent at 888cd38/1b85a24; what the file records; what it does not establish (single call, roles, completeness); the superseded "Dispatch record" label.

## Lesson sentence (drafted)

A record written after the fact is a retrospective roster, not dispatch evidence: it must carry a provenance label naming its committing revision and what it cannot prove, and any dispatch claim requires committed spawn evidence.

## Routed to L1

- Place the sidecar at `.ufo/waves/round-18/residual/assignments.PROVENANCE.md` (lane write; not done here).
- Append (do not rewrite) a correction to `corpus/lessons/round-18.md` erratum lines 389-394 replacing "Dispatch record" with "retrospective roster (see the sidecar)"; the lesson is append-only per round-19's rule.
- Add the lesson sentence in the round-20 lesson.
