VERDICT: partial - S055/Gate drift is real and commit-attributable (ambiguity at 1c325b2; in-place overwrite at 1b85a24; producer/tool drift at 101f399 and 0c75c61), but round-19 erratum 7229fa9 adds a mis-revisioned gate token (lesson:418-419 and registry `gate-live-1`) that tools/citation-provenance.py passes (exit 0).

Scope: read-only git-history reconstruction. Lane HEAD observed 7229fa9 (2026-10-21 03:34:47 -03, parent 8bf99ca). Evidence and every command with its exit: `/tmp/kama-r19-RevDriftHistory/out/timeline.md`, `out/RECEIPT.md`, `out/artifact-blob-table.tsv`. Lane reads used `git --no-optional-locks -C /home/vgpnk/Projects/shokunin/kama-shokunin`; nothing else was written to the lane.

## Which commit introduced what

| ambiguity | introduced by | evidence |
|---|---|---|
| A. Anchor "commands/exits … runs/commands.json at measured c6dc46f" names the measured base, but the artifacts first exist at 1c325b2 | `1c325b2` (SOURCES.md:67; lesson:53 Gate row; LOG.md:1098) | `cat-file -e c6dc46f:…/runs` rc=128; tree of jj keep-ref dd56eb8 (parent c6dc46f) equals tree of 1c325b2 (`diff --quiet` rc=0) |
| B. Cited paths are mutable names; the gate row cites `runs/live-gate-1.stdout` | designed in `1c325b2`; realised by `1b85a24` | `runs/commands.json` b8dadf30 (was ce7dc79c); `runs/live-gate-1.stdout` now `VALID …/live-recovery/receipt-1.json` (was `…/live/receipt-1.json`); `live/receipt-{1,2,3}.json` byte-identical since 1c325b2 |
| C. Producer, tool and gate identity drift | `101f399` (tool dc036d7d→ec7a7567; check-receipt c5715641→e69f91b3); `0c75c61` (run.py writes `live-recovery/` at run.py:54; 5th pin `--expect-server-impl-sha256`; tool→83eac5c0) | full-digest check: S055's quoted tool digest matches the blob at c6dc46f and 1c325b2 only |
| D. Overclaim "so S055's citation resolves to the bytes it describes" (lesson:385) | `1b85a24` | true for `live/` only; the same commit overwrote the other cited paths |
| E. New mis-bound token: lesson:418-419 says the recovery gate output is `cite(eb78788…, runs/live-gate-1.stdout, sha256=b2043ba8…)` | `7229fa9` (round-19) | eb78788's blob is the checkpoint output (`VALID …/live/receipt-1.json`, sha b2043ba8…); recovery output is sha 1cb5a41b…, first committed at 1b85a24. eb78788 is the recovery run's `measured_commit`, the same measured-vs-artifact conflation as A |

Round-start tip per context is 1b85a24, so B and D were inherited. E is round-19's.

## Checker behaviour (exit codes)
- `tools/citation-provenance.py` @7229fa9 on its registry and the 7229fa9 docs: exit 0, verified 3/3. It passes E.
- Corrected tokens (`cite(1c325b2…, live-gate-1.stdout, b2043ba8…)` and `cite(1b85a24…, live-gate-1.stdout, 1cb5a41b…)`): exit 0, 4/4.
- Negative control (recovery digest bound to eb78788): exit 1, mismatch 1.
- Reading: `check()` (lines 69-103) compares digest at `rev:path` only, so it cannot see what the sentence claims [code reading, confirmed by the probes].

## Gaps in the 7229fa9 correction
- SOURCES.md:217 qualifies `runs/commands.json` and `runs/live-gate-*.stdout`, but not `runs/run.py` (writes `live-recovery/` since 0c75c61) or the S055 tool pin dc036d7d (now 83eac5c0 at `tools/`).

## Live hazard (observed, uncommitted)
- Worktree `.ufo/waves/round-18/runs/commands.json` is modified: measured_commit 7229fa9, 11 commands (HEAD: 32), sha256 50e7096238c70718. If committed, the S055 anchor and lesson:53 drift again by the mechanism of 1b85a24.

## Recommendations (append-only; not applied)
1. Replace the E token in lesson:418-419 and in registry row `gate-live-1` with two tokens: `cite(1c325b2e58fcfdc6761f645b44cedfb1d65243e6, .ufo/waves/round-18/runs/live-gate-1.stdout, sha256=b2043ba8a7b20b707367f03c13d25333ed045c4ec303b2ff3cc0df0dc5395c15)` (checkpoint) and `cite(1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e, …live-gate-1.stdout, sha256=1cb5a41bbfeb8f0f9306d9bf86df83d33cf9bc3aa46887c574e1dd07875574c7)` (recovery). Probe verified 4/4.
2. Add an appended S055 correction for `runs/run.py` (live-recovery output since 0c75c61) and the tool pin (`1c325b2:tools/kama-llamacpp-live.py`, dc036d7d…).
3. Stop overwriting `runs/commands.json` and `runs/live-gate-*.stdout` in place. Write new outputs under revision-named paths and cite them as `rev:path` plus sha256.
4. [INFERENCE, not run] Make the checker require that a token's revision is the first commit where that digest appears at that path, or split `measured_at` from `committed_at`.

## Limits
- Attribution uses master first-parent ancestry. jj keep-refs `dd56eb8` (tree identical to 1c325b2) and `7855353` (not an ancestor of HEAD) are non-master.
- The live/ overwrite-then-restore cited in LOG.md:1106 happened only in the worktree. Git shows no net change.
- No official measurement, gate or counter was run. The checker runs are read-only probes on historical bytes in /tmp.
