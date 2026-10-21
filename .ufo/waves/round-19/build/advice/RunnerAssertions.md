VERDICT: confirm - run.py now refuses a receipt whose install-tree fields are missing, empty, not 64 chars, or differ from the measured digest; the diff applies to lane HEAD 7229fa9; the lane gate still accepts an empty install_tree (finding 1).

# RunnerAssertions: receipt install-tree assertions in round-18 run.py

Axes: operability (stop on a receipt/tree mismatch after its gate record is kept) and calibration (valid-path verdict unchanged; an empty-tree receipt that the run layer passed is now refused).

## Change
- New `tree_problem(path,want)` in `.ufo/waves/round-18/runs/run.py` (lines 19-31 of the rebased file). It requires the receipt to exist, `server.install_tree` to be a non-empty dict, `server.install_tree_sha256` to be a 64-char string, and that string to equal the measured `tree_sha`.
- Loop (lines 79-81): after each `live-gate-i` run, `_problem=tree_problem(receipt,tree_sha)`, and `raise SystemExit` on a problem.
- The existing computed-side guard (lane lines 59-60: member count and 64-char length on `_tree`/`_tree_sha`) is unchanged.
- Deliverable: `/tmp/kama-r19-RunnerAssertions/out/run.py.lane-rebased.diff` (sha256 `702ab7f9…`). It applies to HEAD's `run.py` (`5add39f7…`) with a one-line offset on both hunks. Full file: `out/run.py.rebased` (`a1220461…`). Frozen-base diff: `out/run.py.assertions.diff` (`e344f03f…`, against `3d9a5dbc…`).

## Evidence
- `out/verify.sh` writes `out/receipt.txt`: 20 steps. Sixteen exit 0. Four exit 1 by design, and each is a `diff` reporting differing files. No step runs `run.py`.
- Lane, read-only: `git rev-parse HEAD` → `7229fa95…`. `git show HEAD:…/run.py | sha256sum` → `5add39f7…`, identical to the working tree. `HEAD:…/check-receipt.py` → `10912f24…`. `cmp` of lane `run.py` and gate against the snapshots exits 0 after the run.
- Real receipt `live-recovery/receipt-1.json`: 51-member `install_tree`, stored digest `6c216313…`, equal to a read-only recomputation of the producer's `install_tree()` on the same server directory.
- Harness `out/harness/check_tree_assertions.py` extracts the loop with ast and stubs `run()`, so nothing launches and nothing is written to the lane. It then runs the lane gate read-only on each receipt. Both modes report `all_ok=true` (exit 0).

| scenario | patched loop | calls | lane gate exit |
|---|---|---|---|
| valid (real receipt) | pass | 6 | 0 VALID |
| digest mismatch (`ffff…`) | SystemExit: != measured digest | 2 | 1 INVALID |
| digest null / short | SystemExit: not 64-char | 2 | 1 |
| tree `{}`, digest kept | SystemExit: no members | 2 | **0 VALID** |
| tree or server absent | SystemExit: no members | 2 | 1 |
| member altered, digest kept | pass | 6 | 1 INVALID (recompute) |
| receipt not written | SystemExit | 2 | none |
| malformed JSON | JSONDecodeError | 2 | 2 |

Under the pre-patch loop (lane HEAD bytes), all ten scenarios pass the loop, and only the gate rejects the mismatches. The empty-tree receipt gets gate exit 0. [INFERENCE] The run would record that gate call as expected (`run()` line 28 sets `as_expected`; the final exit is line 96 in lane HEAD), so the official run would not flag it.

## Findings and risks
1. **Gate hole, not patched (gate is outside this seat's file scope).** `check-receipt.py:357-360` accepts `install_tree: {}`. The basename check (`:369`, `:372`) and the recomputation (`:380`) are guarded by `tree and`. A receipt with an empty tree and the pinned digest is VALID (observed, lane gate `10912f24…`). Suggested owner fix: reject an empty dict at `:357-360` and add a selftest mutant. [INFERENCE] Untested.
2. The run-layer assertion compares stored fields only. It does not recompute from members; the gate does (the member-altered row). The assertion is necessary, not sufficient.
3. Fail-fast: a mismatch stops the loop after that receipt's gate record. The grid, pin-negative, legacy, and clone steps are then skipped. The run already fails on that path. If full evidence on failure is wanted, record it as a check instead.
4. Dirty guard: `run.py` lines 10-13 exempt `runs/` files except `run.py`. The patched file must be committed before the official run, or the script refuses with exit 2. Code-read, not executed.
5. A malformed receipt raises a JSONDecodeError traceback after the gate's exit-2 record. It still fails closed but is not formatted.
6. Sibling cross-reference, not verified by me: `C2MemberAbsent.md` Finding 1 reports that default members are silently dropped in `install-tree-grid.py`, and that run.py's `tree-grid-pin` then passes with reduced coverage.

## Not done
- `run.py` was not executed. It hardcodes the lane as `L`, would launch llama-server, and writes lane `runs/` and `live-recovery/`. Official gates and grids belong to L1.
- No installs or updates. Tools used: python3 3.14.8, `/usr/bin/patch`, `diff`, `cmp`, `sha256sum`, and read-only git (`rev-parse`, `show`). No subagents, servers, or background jobs. The only lane write is this report.
