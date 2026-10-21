VERDICT: partial - S055/Gate drift is real and commit-attributable (ambiguity at 1c325b2; in-place overwrite at 1b85a24; producer/tool drift at 101f399 and 0c75c61). Round-19's own mis-bound gate token (introduced 7229fa9) was corrected by hand at f1790e2, but the checker still exits 0 on the mis-bound registry (5b108c1, f1790e2), and SOURCES:217 still does not qualify `runs/run.py` or the tool pin.

Scope: read-only git-history reconstruction. Final pin: HEAD = origin/master = f1790e2 (2026-10-21 03:42:45 -03). Evidence and every command with its exit: `/tmp/kama-r19-RevDriftHistory/out/timeline.md`, `out/RECEIPT.md`, `out/head-pin-final.txt`, `out/artifact-blob-table.tsv`. Lane reads used `git --no-optional-locks -C /home/vgpnk/Projects/shokunin/kama-shokunin`; nothing else was written to the lane.

## Which commit introduced what

| ambiguity | introduced by | evidence |
|---|---|---|
| A. Anchor "commands/exits … runs/commands.json at measured c6dc46f" names the measured base, but the artifacts first exist at 1c325b2 | `1c325b2` (SOURCES.md:67; lesson:53 Gate row; LOG.md:1098) | `cat-file -e c6dc46f:…/runs` rc=128; tree of jj keep-ref dd56eb8 (parent c6dc46f) equals tree of 1c325b2 (`diff --quiet` rc=0) |
| B. Cited paths are mutable names (`runs/commands.json`, `runs/live-gate-N.stdout`) | designed in `1c325b2`; realised by `1b85a24` | commands.json b8dadf30 (was ce7dc79c); live-gate-1 now `VALID …/live-recovery/receipt-1.json` (was `…/live/receipt-1.json`). `live/receipt-{1,2,3}.json` byte-identical since 1c325b2 |
| C. Producer, tool and gate identity drift | `101f399` (tool dc036d7d→ec7a7567; check-receipt c5715641→e69f91b3); `0c75c61` (run.py writes `live-recovery/`, run.py:54; 5th pin `--expect-server-impl-sha256`; tool→83eac5c0) | the full digest of the tool at c6dc46f and 1c325b2 equals the S055 quote; at 101f399 and 0c75c61 it does not |
| D. Overclaim "so S055's citation resolves to the bytes it describes" (lesson:385) | `1b85a24` | true for `live/` only; the same commit overwrote the other cited paths |
| E. Mis-bound token: lesson:418-419 called `cite(eb78788…, live-gate-1.stdout, sha256=b2043ba8…)` the recovery output | `7229fa9` (round-19) | eb78788's blob is the checkpoint output (`VALID …/live/receipt-1.json`); the recovery output is sha 1cb5a41b…, first committed at 1b85a24. eb78788 is the recovery run's `measured_commit`, the same measured-vs-artifact conflation as A |

Round-start tip per context is 1b85a24, so B and D were inherited. E is round-19's.

## Status of E at HEAD f1790e2
- Corrected by hand in `f1790e2`: lesson:418-419 now cites `1b85a24`/`1cb5a41b…`, and registry `gate-live-1` is re-pinned to 1b85a24 with a `doc` field.
- The checker does not catch the class. `tools/citation-provenance.py` at 5b108c1 and at f1790e2 each exit 0 (verified 3/3) on the mis-bound 7229fa9 registry. The new doc binding and `origin/master` ancestry gate do not test whether the digest belongs to the commit that carries it.
- The 7229fa9 checker also exits 0 on the mis-bound registry. Its negative control, the recovery digest bound to eb78788, exits 1, so it is fail-capable on digests.

## Gaps still open at f1790e2
1. The checker cannot see sentence-to-token semantics. E was fixed by hand and could recur.
2. SOURCES.md:217 qualifies `runs/commands.json` and `runs/live-gate-*.stdout`, but not `runs/run.py` (writes `live-recovery/` since 0c75c61; run.py:63 at HEAD) or the S055 tool pin dc036d7d (`tools/` is 83eac5c0 since 0c75c61).
3. The in-place overwrite pattern remains available. A future measured run writing `runs/commands.json` or `runs/live-gate-*.stdout` at the same paths would recreate B and D. Worktree `runs/commands.json` was briefly rewritten during the session (measured 7229fa9, 11 commands) and was back to HEAD bytes (b8dadf30…, measured eb78788, 32 commands) at the final check.

## Recommendations (append-only; not applied)
1. Keep the corrected tokens and give the checker a rule that a token's revision must be the first commit where that digest appears at that path. Token pairs for the record: `cite(1c325b2e58fcfdc6761f645b44cedfb1d65243e6, .ufo/waves/round-18/runs/live-gate-1.stdout, sha256=b2043ba8a7b20b707367f03c13d25333ed045c4ec303b2ff3cc0df0dc5395c15)` and `cite(1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e, .ufo/waves/round-18/runs/live-gate-1.stdout, sha256=1cb5a41bbfeb8f0f9306d9bf86df83d33cf9bc3aa46887c574e1dd07875574c7)`. Probe: exit 0, 4/4 (corrected set, 7229fa9-era probe).
2. Add an appended S055 correction for `runs/run.py` (live-recovery output since 0c75c61) and for the tool pin (`1c325b2:tools/kama-llamacpp-live.py`, dc036d7d…).
3. Write new measured outputs under revision-named paths (for example `runs/<measured-rev>/…`) and cite them as `rev:path` plus sha256. Stop overwriting `runs/commands.json` and `runs/live-gate-*.stdout` in place.
4. [INFERENCE, not run] A first-appearance check would catch E: `git log --diff-filter=A -- <path>` or `git log -S <digest-producing content>` returning a rev later than the token's rev. Not implemented or run.

## Limits
- Attribution uses master first-parent ancestry (10 commits from c6dc46f to HEAD). jj keep-refs `dd56eb8` (tree identical to 1c325b2) and `7855353` (not an ancestor of HEAD) are non-master.
- The live/ overwrite-then-restore cited in LOG.md:1106 happened only in the worktree. Git shows no net change.
- No official measurement, gate or counter was run. The checker runs are read-only probes on historical bytes staged under /tmp.
