# MutC2Junk

Seat: MutC2Junk. Axis: coverage. One mutation probe. Tool not edited. Lane Git index not touched. No subagent.

Axes: coverage (a junk mention must not satisfy C2), calibration (do not treat a selftest pass as `met True`), restoration (lane bytes unchanged).

C2 target line, not changed: `named 1 file_exists 1 cited_row 1 met True`.

Neither assigned command meets that line. The counter is not wrong.

## Assigned commands

### Selftest

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --selftest
```

```
SELFTEST base_met=False junk_met=False pass=1
base named 0 file_exists 0 cited_row 0 met False
```

exit 0

Exit 0 is the selftest pass bit (`pass=1`), not C2 met. `junk_met=False`. `base_met=False`. Same two lines as `.ufo/waves/round-35/controls/c2-selftest.out`.

### Base tip

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 719655f12517a9ce6b1a5ca44316897fed8420b0
```

```
named 0 file_exists 0 cited_row 0 met False
```

exit 1

Same line as `.ufo/waves/round-35/controls/c2-base.out`. This command reads `git show` at the pinned tip, not the worktree.

## Mutant

Claim challenged: a junk coverage mention must not meet C2.

Isolated scratch only: `.ufo/waves/round-35/w1/out/MutC2Junk/scratch-repo/`. Not the lane corpus.

Pristine scratch README is `719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/README.md` plus an empty `## Coverage map — round 35 addition` block closed by `## Frontier disposition — round 35 probe`. That heading is absent from the base blob, so the assigned selftest's appended see-line never reaches the window (`if HEADING not in readme: return 0`). The scratch makes the window load-bearing.

Other conjuncts held on purpose, so a counted name would have been enough to meet C2: scratch `corpus/knowledge/endpoint-health-probe-conventions.md` is the one line `Local probe convention cites S001.`; scratch `corpus/SOURCES.md` is the base blob and contains `| S001 |`.

Smallest mutation: append one line after the closer, outside the round-35 body:

```
see knowledge/endpoint-health-probe-conventions.md outside the block
```

That is the selftest's junk string. It is not inside the heading body (`split` on the closer excludes it).

## Expected detector

Same command on pristine, mutated, and restored scratch bytes:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-35/w1/out/MutC2Junk/scratch-repo
```

Expected if the invariant holds: `named 0 file_exists 1 cited_row 1 met False`, exit 1. A pristine `met True` would have been inconclusive, not a kill. A mutated `met True` would have been a surviving mutant and a wrong counter. Contract not changed either way.

## Output

Pristine:

```
named 0 file_exists 1 cited_row 1 met False
```

exit 1

Mutated:

```
named 0 file_exists 1 cited_row 1 met False
```

exit 1

Restored:

```
named 0 file_exists 1 cited_row 1 met False
```

exit 1

## Verdict

Killed. The junk mention did not meet C2. `named` stayed 0 while `file_exists` and `cited_row` stayed 1. Not a surviving mutant. Not permission to change the contract. The counter is not wrong.

## Restoration evidence

Scratch README sha256:

- pristine `73c3d4b0c77591aeff76efee575a4b733d5b5711ea1ff9712d96b81ad4864637` (35888 bytes)
- mutated `b362054404ddae55051a066e9c2e07405a42462610489baffb62e3e380130dbb` (35957 bytes)
- restored `73c3d4b0c77591aeff76efee575a4b733d5b5711ea1ff9712d96b81ad4864637` (match; entry path count 0)

Scratch sources unchanged `d88e497c5c10ffacb7caed0c137a9bf4c6b1bbc0e7520749bdae9f9dfa855603`. Scratch entry unchanged `530bd163bc6c39b787dad67c51679813e3bf7a60a32937657ada1479a199701d`.

Lane sha256 before and after the probe, identical:

- `tools/round35-coverage-audit.py` `ff5318494c01cd545455d386f65b9dcfdd64d361d4e94e98454081a7cb55d013`
- `corpus/README.md` `d8c2bc05dc764f8146a48bf1819cd2b6cb05311fd8b1bcce743254474d699add`
- `corpus/SOURCES.md` `57352f20b1de70c01405adea6f77bf165006e6cdafda459f4dd985f87f679a46`
- `corpus/knowledge/endpoint-health-probe-conventions.md` `492c39315316291b23b4b0c025111103c7783bc7a9935fa238659be7c5f9b39f` (already present; not read; not written)

No lane source was mutated. Scratch left restored under the seat directory.
