VERDICT: confirm - red-before reproduced: gate crashes count as rejected; the crash mutant survives the frozen grid.

Axes: calibration (C1, errors versus verdicts) and operability (bounded, isolated replay); no round-score judgment.
Frozen revision: `37bd4c5bd456a2f8a54d3312c28495c321715856`.
Evidence directory: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/MutGridRedBefore/`.
Retained: `run-detector.py`, `gate-pristine.py`, `gate-mutated.py`, and `pristine.json`, `mutated.json`, `restored.json`; each phase JSON records exact argv/cwd, exit, stdout/stderr, and input hashes before/after.
Executed isolation command (exit 0; stdout was the frozen revision): `git clone -q --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r20-MutGridRedBefore/lane && git -C /tmp/kama-r20-MutGridRedBefore/lane checkout -q 37bd4c5bd456a2f8a54d3312c28495c321715856 && git -C /tmp/kama-r20-MutGridRedBefore/lane rev-parse HEAD`.

## One mutation and the same detector
The stub recognizes the baseline by the supplied install-tree pin, printing `VALID receipt` / exit 0; changed receipts normally print `INVALID install-tree pin mismatch` / exit 1. This is a controlled fake, not receipt authentication.
Only scratch `gate-stub.py:11` changed: `print("INVALID install-tree pin mismatch")` → `raise RuntimeError("injected gate crash")`; it was then restored exactly.
Expected detector [INFERENCE]: the pinned grid should classify the three crashed calls as `error`, count zero rejections, and return a nonzero could-not-evaluate result—not a successful kill count.
Each subprocess was bounded to 30 seconds; the grid and direct member probe ran concurrently. All completed without timeout and were reaped.
Executed commands (each runner exit 0; child outcomes below):
```
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/MutGridRedBefore/run-detector.py pristine
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/MutGridRedBefore/run-detector.py mutated
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/MutGridRedBefore/run-detector.py restored
```
All three invoke the frozen `tests/llamacpp-live/install-tree-grid.py --gate /tmp/kama-r20-MutGridRedBefore/gate-stub.py --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live-recovery/receipt-1.json` with all six recorded receipt pins (including `--tree-sha`) and `--json`; full, unelided argv is in each phase JSON.
| Phase | Grid exit | Baseline | Rejected | Every member's gate exit / stdout | Direct gate exit / stderr |
|---|---:|---|---:|---|---|
| Pristine | 0 | VALID | 3/3 | 1 / `INVALID install-tree pin mismatch` | 1 / empty |
| Mutated | 0 | VALID | 3/3 | 1 / empty | 1 / traceback ending `RuntimeError: injected gate crash` |
| Restored | 0 | VALID | 3/3 | 1 / `INVALID install-tree pin mismatch` | 1 / empty |
Actual mutated JSON rows: `libggml-base.so.0.27.0`, `libllama-common.so.0.7.0`, `libllama.so.0.7.0` each have `gate_exit: 1`, `status: "rejected"`, `stdout: ""`. Grid stderr was empty in every phase.
Mutation verdict: **SURVIVED**, not killed or inconclusive: pristine and restored detector runs passed, and the crashed subject still produced grid exit 0. This is advisory red-before evidence, not an official measurement of a fixed grid.
Cause at frozen revision: `install-tree-grid.py:110` starts `status = ("rejected" if code == 1 else`; `:49-53` discards captured stderr. The real gate's `check-receipt.py:2233-2236` emits stdout starting `INVALID ` before returning 1.

## Six mutants a fixed grid must kill
The following are proposed, **unexecuted [INFERENCE]** fixed-grid mutations; no kill result is claimed for them.
| Mutant | Discriminating injected subject | Required detector observation |
|---|---|---|
| 1. Restore return-code-only rejection (`code == 1`) | Uncaught crash or silent exit 1; no stdout verdict | `error`, rejected 0, run nonzero |
| 2. Accept `INVALID ` from stderr/merged streams | Exit 1; stdout empty; stderr `INVALID tree mismatch` | `error`, not rejected; run nonzero |
| 3. Replace prefix match with substring search | Exit 1; stdout `diagnostic: INVALID tree mismatch` | `error`, not rejected; run nonzero |
| 4. Drop the exit-1 requirement | Exit 2; stdout `INVALID tree mismatch` | `error`, not rejected; run nonzero |
| 5. Drop the verdict delimiter (`startswith("INVALID")`) | Exit 1; stdout `INVALIDATED tree mismatch` | `error`, not rejected; run nonzero |
| 6. Treat error rows as successful coverage in final aggregation | One genuine rejection plus an error row | Preserve error row and reject count 1; run nonzero |

## Hashes and restoration
Gate stub SHA-256 pristine/restored: `06e99c836e39cfc45b82f69edc8bca84ce6dcc87674dfe2bf66b6bfb6730e0dd`; mutated: `11594dcf9bf3c070d118a302fd95172e460d1a6a92667b6f2b6ffd65a9b5ceb6`.
Frozen grid SHA-256 before/after all phases: `6f51803c47db597e2f6778b492bfaba14735a23c599bc972f8d33ab477a68f05`.
Input receipt SHA-256 before/after all phases: `89728a0248f208ada93ae9b2ce08a5da5e65bcd30259c43b8329d3e6d3bca863`; identical to its frozen-clone committed copy.
Restoration `cmp -s /tmp/kama-r20-MutGridRedBefore/gate-stub.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/MutGridRedBefore/gate-pristine.py` exited 0; the accompanying SHA-256 capture matched the hashes above and printed `restored_bytes_equal=1`.
Cleanup executed: `rm -rf /tmp/kama-r20-MutGridRedBefore && test ! -e /tmp/kama-r20-MutGridRedBefore && printf 'scratch_removed=1\nexit=0\n'` → exit 0, stdout `scratch_removed=1` then `exit=0`.
No lane source, index, or history edits; only assigned evidence/report writes. No servers or live harness started. No installs/updates; `/usr/bin/python3 --version` exited 0 with `Python 3.14.8`.
