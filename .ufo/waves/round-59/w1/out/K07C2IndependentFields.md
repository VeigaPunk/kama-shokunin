# K07C2IndependentFields — C2 clause falsification

Axes: operability; calibration (assigned lowest at 7). Frozen C2 contract: `controls/freeze.txt` lines 12–15. No source edits or installs.

## Attempt and outcome

Inspected measured C2 checker `tools/round59-c2-counter.py` at the specified measured tip. It computes mismatch flags for typed count, pinned fleet hash, missing pointer, pointer round, pointer verdict, including round, and command (lines 60–71). The required independent mutation battery was **not completed**; no field-level rejection is claimed.

Commands/results:

- `python3` fixture driver using `git archive` then `tarfile.extractall`: **exit 1**, `tarfile.AbsoluteLinkError`: archived lane contains `.ufo/waves/round-36/w3/out/MutRowPipe/probe/.ufo`, a link to an absolute path.
- Retried with isolated `git worktree` fixtures; first driver stopped at `FileExistsError` because the failed run had left scratch mutation directories.
- Retried cleanup/fixture driver through bash; command rejected before execution: `error: pi-natives:command: syntax error at line 1 col 301`.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin worktree list --porcelain` showed only the lane worktree; no fixture worktrees were created. Removed `/fast/scratch/hyaku/kama-r59/K07C2IndependentFields` before reporting.

Thus there are no actual checker invocation outputs or exits for the seven mutations. Unrun is not passed. The checker source's separate regex flags suggest distinct field coverage, but this is not behavioral evidence. Scope remains C2 field isolation; operability and calibration evidence are both incomplete. Smallest safe next action: rerun a corrected scratch-only driver (e.g. proper shell quoting and fresh per-mutation directories), each fixture committed only after `git rev-parse --show-toplevel` equals its fixture directory, invoking the frozen checker against the frozen fleet HEAD; record all seven exact outputs/exits.