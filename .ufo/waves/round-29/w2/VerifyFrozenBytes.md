# VerifyFrozenBytes — C1 frozen-artifact integrity (kama lane, round 29 w2)

**Seat:** kama-r29-w2-VerifyFrozenBytes · **Date:** 2026-10-23
**Repo:** /home/vgpnk/Projects/shokunin/kama-shokunin (branch master)

## Verdict

**VERIFIED.** The frozen C1 artifacts are byte-identical at the freeze commit (827d136546b85059a984b34970f5b493d9a71290), the controls commit (35b90184f638ab6a4149092b93143c7a2b873787), and the data commit (513eba3ba51a142c9936553e3a85918345eb5c4c == current HEAD). No tampering after the data commit: the working tree contains no uncommitted changes to any of the three paths.

## Evidence — `count-c1.py` sha256 (`git show <rev>:.ufo/waves/round-29/count-c1.py | sha256sum`)

| Commit | sha256 |
|---|---|
| 827d136546b85059a984b34970f5b493d9a71290 | fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383 |
| 35b90184f638ab6a4149092b93143c7a2b873787 | fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383 |
| 513eba3ba51a142c9936553e3a85918345eb5c4c | fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383 |

All three match the claimed frozen sha256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`.

## Evidence — blob identity (`git rev-parse <rev>:<path>`)

| Path | 827d1365 | 35b90184 | 513eba3b | Identical? |
|---|---|---|---|---|
| `.ufo/waves/round-29/count-c1.py` | `4adc6dfebd37b31de8fbf0e4362449728f4ca94d` | `4adc6dfebd37b31de8fbf0e4362449728f4ca94d` | `4adc6dfebd37b31de8fbf0e4362449728f4ca94d` | yes |
| `.ufo/waves/round-29/preregistration.json` | `5e4b49a7ba5c99577f55514e474efd3d7a5d0037` | `5e4b49a7ba5c99577f55514e474efd3d7a5d0037` | `5e4b49a7ba5c99577f55514e474efd3d7a5d0037` | yes |
| `.ufo/waves/round-29/before/c1-base.out` | `e6cdec616c8867057af0996f8a78141c70a7de84` | `e6cdec616c8867057af0996f8a78141c70a7de84` | `e6cdec616c8867057af0996f8a78141c70a7de84` | yes |

Equal git blob ids prove byte-identical content across all three commits.

## Evidence — chain integrity and worktree state

- `git merge-base --is-ancestor`: linear chain `827d1365` → `35b90184` → `513eba3b` (`35b9018` parent = `827d1365`; `513eba3b` parent = `35b90184`; `827d1365` parent = `2aa46e24`, the stated base). Committed history is a straight line; no rewrite or interposition possible between the sampled revisions.
- `git rev-parse HEAD` = `513eba3ba51a142c9936553e3a85918345eb5c4c` — HEAD is the data commit itself.
- `git status --porcelain` on the three frozen paths: **empty** (no uncommitted modification).
- Worktree `git hash-object`: `count-c1.py` = `4adc6dfe…` , `preregistration.json` = `5e4b49a7…`, `before/c1-base.out` = `e6cdec61…` — all equal the committed blobs; worktree `sha256sum` of the counter = `fe11d599…`.
- Pin cross-check: `preregistration.json` line 17 contains `"counter_sha256": "fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383"`, matching the observed bytes at every revision.

## Residual observations (not defects of the frozen bytes)

- Freeze-commit timestamp claim is slightly off: `git log -1 --format=%cI 827d1365` reports committer time `2026-10-23T07:55:43-03:00` (= **10:55:43Z**), author time `06:55:34-03:00` (09:55:34Z). Goal text states freeze at **10:55:45Z**. 2-second drift; likely a hand-transcribed timestamp. Does not affect hash identity, but any receipt quoting 10:55:45Z should be corrected to 10:55:43Z.
- Scope note: this check covers the three named files only. Other round-29 artifacts under `.ufo/waves/round-29/` (e.g., untracked `final/`, `mined/`, `w1/`, `w2/` directories observed in the worktree) are outside this item's mandate.

## Commands run

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse <each rev>^{commit} HEAD
git -C … show <rev>:.ufo/waves/round-29/count-c1.py | sha256sum        (×3)
git -C … rev-parse <rev>:<path>                                       (3 paths × 3 revs)
git -C … log -1 --format='%H %cI parents=%P' <each rev>
git -C … merge-base --is-ancestor <a> <b>                             (both pairs)
git -C … status --porcelain -- <3 frozen paths>
git -C … hash-object <3 frozen paths>
git -C … show 513eba3b:.ufo/waves/round-29/preregistration.json | grep fe11d599
```

All read-only; no lane index/worktree mutation. No tools installed (pacman untouched).
