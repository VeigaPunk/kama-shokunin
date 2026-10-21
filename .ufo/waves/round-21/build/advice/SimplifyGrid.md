VERDICT: confirm - behaviour-preserving simplification; patch delivered

## Gods speed axes
- **operability**: fewer producer entrypoints (`load_producer` vs `load_source`+`frozen_producer`+`current_producer`); clearer mirror check and summary loops.
- **calibration**: `--selftest` and `--arm both --json` (tree stripped) byte-identical before/after.
- **maintainability**: −2 lines (332→330); no new dependencies.
- **complexity**: walrus in summary only; gate loop unchanged (inline beats extract on line count).

## Change (base `a29bb84abbb8b4d328f5970a89e448330a3a42ac`)
1. Rename `load_source` → `_exec_module`; merge frozen/current into `load_producer(rev=None)`.
2. Mirror identity: `all()` + `next()` instead of nested loop.
3. Summary `by_class`: dict comprehension with walrus.
4. Selftest: drop single-item `for label, path in (...)` wrapper.

Preserved: `gate_module`, `build_cells`, `identities`, `render`, JSON shape, exit codes.

## Evidence (scratch clone; lane tree untouched)
| Command | Exit |
|---------|------|
| `git clone … && checkout a29bb84…` | 0 |
| `python3 …/install-links-grid.py --selftest` (before) | 0 |
| `python3 …/install-links-grid.py --selftest` (after) | 0 |
| `python3 … --arm both --json \| … strip tree` (before) | pipe 0; grid 1 |
| same (after) | pipe 0; grid 1 |
| `git -C lane diff --quiet tests/llamacpp-live/install-links-grid.py` | lane clean |
| `git diff --stat` on patch | 30 insertions, 32 deletions |

`selftest.diff` and `both-json.diff` under out dir: **empty** (identical).

## Deliverables
- Patch: `.ufo/waves/round-21/build/out/SimplifyGrid/install-links-grid.patch`
- Baselines/after copies + empty diffs in same dir.

## Tooling
No installs (stdlib + host `~/.local/opt/llama-b11755` read-only).

Report: `.ufo/waves/round-21/build/advice/SimplifyGrid.md`
