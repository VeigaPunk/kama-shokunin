VERDICT: partial - S055/Gate drift is real and commit-attributable (ambiguity at 1c325b2; in-place overwrite at 1b85a24; producer/tool drift at 101f399 and 0c75c61). Round-19 has since corrected its own mis-bound gate token (introduced 7229fa9, fixed at f1790e2 and 028235e), but the checker still exits 0 on the mis-bound registry, and SOURCES:217 still does not qualify `runs/run.py` or the tool pin.

Scope: read-only git-history reconstruction. Final pin: HEAD = origin/master = 8d9191f. The lane moved about ten times during this session; commits after 8d9191f were not analysed. Evidence and every command with its exit: `/tmp/kama-r19-RevDriftHistory/out/timeline.md`, `out/RECEIPT.md`, `out/head-pin-final.txt`, `out/artifact-blob-table.tsv`. Lane reads used `git --no-optional-locks -C /home/vgpnk/Projects/shokunin/kama-shokunin`. The only lane write is this report.

## Which commit introduced what

| ambiguity | introduced by | evidence |
|---|---|---|
| A. Anchor "commands/exits … runs/commands.json at measured c6dc46f" names the measured base, but the artifacts first exist at 1c325b2 | `1c325b2` (SOURCES.md:67; lesson:53 Gate row; LOG.md:1098) | `cat-file -e c6dc46f:…/runs` rc=128; jj keep-ref dd56eb8 (parent c6dc46f) has the same tree as 1c325b2 (`diff --quiet` rc=0) |
| B. Cited paths are mutable names (`runs/commands.json`, `runs/live-gate-N.stdout`) | designed in `1c325b2`; realised by `1b85a24` | commands.json b8dadf30 (was ce7dc79c); live-gate-1 now `VALID …/live-recovery/receipt-1.json` (was `…/live/receipt-1.json`); `live/receipt-{1,2,3}.json` byte-identical since 1c325b2 |
| C. Producer, tool and gate identity drift | `101f399` (tool dc036d7d→ec7a7567; check-receipt c5715641→e69f91b3); `0c75c61` (run.py writes `live-recovery/`, run.py:54; 5th pin `--expect-server-impl-sha256`; tool→83eac5c0) | full digest of the tool at c6dc46f and 1c325b2 equals the S055 quote; it does not at 101f399 or 0c75c61 |
| D. Overclaim "so S055's citation resolves to the bytes it describes" (lesson:385) | `1b85a24` | true for `live/` only; the same commit overwrote the other cited paths |
| E. Mis-bound token: lesson:418-419 called `cite(eb78788…, live-gate-1.stdout, sha256=b2043ba8…)` the recovery output | `7229fa9` (round-19) | eb78788's blob is the checkpoint output (`VALID …/live/receipt-1.json`); the recovery output is sha 1cb5a41b…, first committed at 1b85a24. eb78788 is the recovery run's `measured_commit`, the same measured-vs-artifact conflation as A |

The round-start tip per context is 1b85a24, so B and D were inherited. E is round-19's.

## Status at 8d9191f
- Committed values at 8d9191f, each with the commit that last changed it: `runs/commands.json` b8dadf30… (1b85a24); `runs/live-gate-1.stdout` 1cb5a41b… (1b85a24); `runs/run.py` 5add39f79923… (7229fa9); `tools/kama-llamacpp-live.py` 83eac5c04893… (0c75c61); `tests/llamacpp-live/check-receipt.py` a0dc1d07220f… (f1790e2); `corpus/SOURCES.md` 8b6b1c7d3645… (f1790e2); `live/receipt-1.json` e616f67e… (1c325b2); `live-recovery/receipt-1.json` 89728a0248f2… (1b85a24).
- E corrected: lesson:418-421 now cites the checkpoint (1c325b2, b2043ba8…) and the recovery (1b85a24, 1cb5a41b…) as separate tokens. The registry adds `gate-live-checkpoint` (rev 1c325b2) beside `gate-live-1` (rev 1b85a24). The HEAD checker exits 0, 4/4 verified.
- The checker does not detect the E class. The HEAD checker, run on the mis-bound 7229fa9 registry, still exits 0 (3/3 verified). Its doc binding and `origin/master` ancestry gate test neither the digest's first-appearance commit nor the sentence (checker blob 5c887572b37a, unchanged from 30ed378 through 8d9191f).
- SOURCES:217 still qualifies only `runs/commands.json` and `runs/live-gate-*.stdout`. It does not qualify `runs/run.py` (writes `live-recovery/` since 0c75c61) or the S055 tool pin dc036d7d (`tools/` is 83eac5c0 since 0c75c61).

## Recommendations (append-only; not applied)
1. Append the producer and tool-pin qualification to the S055 erratum at SOURCES:217.
2. Add a first-appearance rule to the checker or to review: the cited revision should be the first commit at which that digest appears at that path. [INFERENCE: not implemented or run.]
3. Keep writing new measured outputs to revision-named paths. Do not overwrite `runs/commands.json` or `runs/live-gate-*.stdout` in place.

## Limits
- Master first-parent ancestry c6dc46f..8d9191f is 16 commits. jj keep-refs dd56eb8 (tree identical to 1c325b2) and 7855353 (not an ancestor of HEAD) are non-master.
- The live/ overwrite-then-restore cited in LOG.md:1106 happened only in the worktree. Git shows no net change.
- No official measurement, gate or counter was run. Checker runs are read-only probes on historical bytes staged under /tmp.
