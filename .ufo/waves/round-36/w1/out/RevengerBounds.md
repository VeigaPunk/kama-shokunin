# RevengerBounds — round-36 w1 write boundary

## Reconstructed contract

Confirm this seat did not read a secret file, did not edit MISSION.md, did not run an endpoint-admin command, and did not mutate jj or the Git index. List the commands this seat ran. Say whether the seven r35 leftovers are still uncommitted. One allowed write: this report. Stop after that surface. Judged on adjacency.

The seven leftovers are the R35-KEEP paths in tools/round36-statement-audit.py, the same seven the round-35 spot-check classified and left unswept:

1. `.ufo/waves/round-35/w1/out/ConnSibling/seat.log` — seat-log flush
2. `.ufo/waves/round-35/w1/out/ExecDisposition/seat.log` — seat-log flush
3. `.ufo/waves/round-35/w1/out/ScoutCoverageAbsence/seat.log` — seat-log flush
4. `.ufo/waves/round-35/w1/out/ExecDisposition.md` — report overwrite
5. `.ufo/waves/round-35/assimilation/validate/` — mixed mirror
6. `.ufo/waves/round-35/w1/out/ScribeGate/fetch/docker-dockerfile.html` — helper-skipped HTML
7. `.ufo/waves/round-35/w1/out/ScribeGate/fetch/dockerfile.html` — helper-skipped HTML

## Boundary confirmation

| check | result |
| --- | --- |
| Secret file read | No. No `.env`, credential store, private key, or fetched HTML was opened. |
| MISSION.md edited | No. Absent from the lane tree and from HEAD. Fleet copy was not opened and was not written. |
| Endpoint-admin command | No. No systemctl, service restore, admin API, ssh, pacman, or package install. |
| jj mutated | No. `.jj` is present. This seat ran no jj command. |
| Git index mutated | No. No add, commit, stash, checkout, switch, reset, pull, push, or update-index. `git diff --cached --quiet` exit 0. No `.git/index.lock`. |

## Seven r35 leftovers

Still uncommitted: yes. Observed at lane HEAD `9014843cb7de8fbe87a97954c13832b67d55f046`. None of the seven are in that commit. None are staged. Index matches HEAD for the four tracked paths; worktree differs. The three others are untracked.

```
 M .ufo/waves/round-35/w1/out/ConnSibling/seat.log
 M .ufo/waves/round-35/w1/out/ExecDisposition.md
 M .ufo/waves/round-35/w1/out/ExecDisposition/seat.log
 M .ufo/waves/round-35/w1/out/ScoutCoverageAbsence/seat.log
?? .ufo/waves/round-35/assimilation/validate/
?? .ufo/waves/round-35/w1/out/ScribeGate/fetch/docker-dockerfile.html
?? .ufo/waves/round-35/w1/out/ScribeGate/fetch/dockerfile.html
```

` M` is unstaged. `??` is untracked. `git diff --numstat HEAD` on the four tracked paths: ConnSibling/seat.log 142/1, ExecDisposition.md 84/1953, ExecDisposition/seat.log 2011/1, ScoutCoverageAbsence/seat.log 144/1. Those counts match the round-35 spot-check. Both HTML files are 1066624 bytes and are absent from `git ls-tree HEAD`. `git status --porcelain -uall` under `assimilation/validate/` is 95 paths, equal to the spot-check's 11 symlinks plus 84 regular files. This seat did not reclassify symlink versus regular file, and did not re-hash the HTML.

The only commit after frozen tip `e5a8ececf3d60fd53b36bb74299693a29e8f74b6` is `9014843` (`round-36: freeze predicates, failing controls, and wave spec`, author kama-shokunin). `git merge-base --is-ancestor` of the frozen tip exited 0. `git show --name-only` of that commit lists round-36 freeze files and the two counters. The keep-path filter of that commit printed no names.

Full `git status --porcelain` at the snapshot was 42 lines. The other 35 are untracked round-36 seat directories, `dispatch-manifest.json`, and reports already written by other seats (`ExecC1.md`, `ExecC2.md`, `ExecCensus.md`). Those are not the r35 leftovers. This seat did not stage or commit them. Writing this report adds one further untracked path. That write is the assigned report, not a commit of the leftovers.

## Commands this seat ran

Shell, all from `/home/vgpnk/Projects/shokunin/kama-shokunin`. Invocations 1–5 are read-only. Invocations 6 and 7 write only this report. Invocation 7 is the last shell command. No jj. No git index write.

1. `git rev-parse HEAD`; `git diff --cached --name-only`; `git diff --cached --quiet`; `git status --porcelain` on the seven keep paths, on `.ufo/waves/round-35`, and a line count of the full porcelain; `git status --porcelain` on `MISSION.md`, `corpus/SOURCES.md`, `SCORECARD.md`, `LOG.md`, `considerthese`; `git ls-files` and `git diff --cached --name-only` on the keep paths; `[ -d .jj ]`; `stat -c '%s %n'` on the two HTML files; `[ -d .ufo/waves/round-35/assimilation/validate ]`.

2. `git rev-parse HEAD`; `git merge-base --is-ancestor e5a8ececf3d60fd53b36bb74299693a29e8f74b6 HEAD`; `git log --oneline e5a8ececf3d60fd53b36bb74299693a29e8f74b6..HEAD`; `git diff --name-only` on the four tracked leftovers; `git ls-tree -r --name-only HEAD` on the two HTML paths and `assimilation/validate`; `git status --porcelain=v1 -uall` under `assimilation/validate` (first 20 lines and a count).

3. `git show --name-only` of `9014843cb7de8fbe87a97954c13832b67d55f046`; the same show limited to the seven keep paths; `git diff --numstat HEAD` on the four tracked leftovers; `git status --porcelain=v1 --untracked-files=all` on the two HTML files; `git rev-parse HEAD:MISSION.md` (exit 128, path absent). `git hash-object MISSION.md` did not run; the `&&` stopped at that failure.

4. Existence test for lane `MISSION.md` (absent); `git status --porcelain --ignored` on `MISSION.md`, `corpus/SOURCES.md`, `SCORECARD.md`, `LOG.md`; `git ls-files '*MISSION.md'`; index-lock test; `git diff --cached --quiet` (exit 0).

5. `git status --porcelain`; `stat -c '%s %y'` on `/home/vgpnk/Projects/shokunin/MISSION.md` (metadata only, contents not read); `ls -1 MISSION.md` in the lane (absent).

6. A `printf` redirect that created this report, and no other path. A non-shell read of this report followed, to check the redirect. That read is not a secret-file open.

7. This `python3` rewrite of this report only, recording invocations 6 and 7. No other path. Last shell command.

Non-shell reads, contents only, no secret stores: `RevengerBounds/prompt.txt`, `w1/spec.json`, `w1/plan.json`, `ReviewLeftovers/prompt.txt`, `.ufo/waves/round-36/preregistration.json`, `tools/round36-statement-audit.py`, `.ufo/waves/round-35/w1/out/RevengerScope.md`, `corpus/lessons/round-35-verifier-spotcheck.md` lines 1–50, `RevengerBounds/seat.log`. Grep and Glob were used to locate those paths. A content search of `LOG.md` and of `ExecDisposition.md` returned no non-sensitive matches; those files were not opened.

## Evidence chain

1. Contract paths come from `KEEP_PATHS` in `tools/round36-statement-audit.py` and from the classified list in `corpus/lessons/round-35-verifier-spotcheck.md` lines 29–39. Prefer the porcelain over the names: the same seven paths are the only round-35 porcelain lines.
2. Uncommitted means not in HEAD and not only sitting clean in the index. `git ls-files` tracks the four modified paths and not the HTML or validate tree. `git ls-tree HEAD` has neither HTML path nor any `assimilation/validate` path. Cached diff is empty. Worktree diff is nonempty for the four tracked paths.
3. The freeze commit does not absorb them. Its name list has no keep path.
4. Boundary commands are the seven shell invocations above. The sixth and seventh write only this report. None is `git add`, `commit`, `stash`, `checkout`, `switch`, `reset`, `pull`, `push`, `update-index`, or any `jj` subcommand. None is systemctl or an admin endpoint call.
5. Lane `MISSION.md` is absent, so it cannot have been edited here. Fleet `MISSION.md` metadata: 5040 bytes, mtime 2026-10-19 21:10:11 -0300. Contents not read.

## Divergences

- Frozen tip in the wave brief is `e5a8ececf3d60fd53b36bb74299693a29e8f74b6`. HEAD is one commit later. That commit is not this seat, and it does not commit the leftovers. Predicates were not retargeted.
- Porcelain is not seven lines. The extra lines are live round-36 seat output. They do not change the leftover verdict.
- `.jj` exists. This seat did not read the operation log and did not run jj, so "jj not mutated by this seat" is an invocation fact, not a jj-status snapshot. Inference: another process could still touch jj; this seat did not.
- HTML byte-identity with the spot-check sha256 was not re-derived. Size, path, and untracked state match. The hash itself is prior record.

## Confidence

High that this seat did not read a secret, edit MISSION.md, run endpoint-admin, or mutate jj or the Git index. High that the seven r35 leftovers were still uncommitted at the status snapshot: flags, numstat, sizes, and commit name-list agree. Low that a later seat will leave them uncommitted; this report does not commit them and does not delete them.

