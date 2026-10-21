VERDICT: partial - the measured claim reproduces at lane HEAD 7229fa9 (pinned 3/3 rejected, pre-pin 0/3, baseline VALID on receipts 1-3), but the "install-tree identity" boundary is narrower than stated: symlinks are unhashed although the loader follows them, so a consistent attacker can redirect a SONAME link without changing `install_tree_sha256`.

# C2ConsistentSwap - round-19 reproduction

## State
- Copy: `/tmp/kama-r19-C2ConsistentSwap` (`cp -a` of the lane at 8bf99ca, exit 0). Lane HEAD moved to 7229fa9 (committed 03:34:47) during the run and changed `check-receipt.py`, `install-tree-grid.py`, `runs/run.py`. I refreshed those three from 7229fa9 via `git show` (sha256 10912f24…, 49a42f81…, 5add39f7…, matching HEAD) and re-ran everything at HEAD. The checks shared with the earlier 8bf99ca run (predates the sweep; kept in `out/snapshot-8bf99ca/`) give identical results.
- Unchanged across both commits: `receipt-1.json` 89728a02…, `tools/kama-llamacpp-live.py` 83eac5c0…, `tools/kama-probe.sh` 36b64978…. On disk: `llama-server` b6a31a8e…, `libllama-server-impl.so` e404b91a…, `stories260K.gguf` 270cba…. All equal the receipt and `run.py` pins.
- Producer `install_tree()` on disk: 51 regular members, digest 6c216313… = receipt `install_tree_sha256` = `run.py` pin.
- No servers started. No lane writes except this file. No installs (used `/usr/bin/readelf`).

## Reproduced (official `install-tree-grid.py`, copy at HEAD)
| receipt | run | baseline | members rejected | exit |
|---|---|---|---|---|
| 1 | `--tree-sha 6c216313…` | VALID | 3/3 | 0 |
| 1 | no pin | VALID | 0/3 | 1 |
| 2 | pin / no pin | VALID | 3/3 / 0/3 | 0 / 1 |
| 3 | pin / no pin | VALID | 3/3 / 0/3 | 0 / 1 |

Each pinned rejection has exactly one problem: `server.install_tree_sha256 <mutant> != expected 6c216313…` (`check-receipt.py:384-389`). Unpinned mutants are accepted. Extra members via `--members` (`libggml-cpu-x64.so`, `libmtmd.so.0.7.0`, `llama-cli`, `libllama-server-impl.so`): pinned 4/4 rejected, exit 0.

Controls (all executed):
- Direct gate, six pins plus `--require-schema v3`, receipt 1: `VALID`, exit 0. Zero pin `0`×64: `INVALID`, exit 1.
- Naive swap (member changed, digest not recomputed): unpinned 3/3 rejected by the recomputation check, exit 1. The pin adds value only for consistent swaps.
- Full-tree sweep, all 51 members, consistent swap. Pinned: 51/51 rejected, exit 1. Unpinned: 49 accepted; 2 rejected, `llama-server` (`install_tree['llama-server'] != server.sha256`) and `libllama-server-impl.so` (`server_impl_sha256 != install_tree[...]`). Round-18 digest fields rewritten consistently are rejected unpinned by `--expect-server-sha256` / `--expect-server-impl-sha256`, exit 1.
- Self-pin: receipt with `libggml-base` consistently swapped, pin = its own digest: `VALID`, exit 0.
- Selftests at 7229fa9: `check-receipt.py --selftest` exit 0 (76 mutations); `install-tree-grid.py --selftest` exit 0.
- Grid with missing gate: `baseline=INVALID members=3 rejected=3/3 tree_pin=on`, exit 2.

## Findings
1. **HIGH (claim scope): symlinks sit outside the digest, but the loader follows them.** `install_tree()` skips non-regular files (`tools/kama-llamacpp-live.py:179-181,194-195`). The install dir has 10 symlinks, including the SONAME links the loader resolves: `libllama.so.0`, `libggml.so.0`, `libggml-base.so.0`, `libllama-common.so.0`, `libmtmd.so.0`. `readelf -d` shows `RUNPATH [$ORIGIN]` on `llama-server`, `libllama-server-impl.so`, `libllama.so.0.7.0`, `libllama-common.so.0.7.0`, `libggml-base.so.0.27.0`. Demonstrated on a copy (`out/tree-symlink-demo`):
  - Re-point `libllama.so.0` to sibling `libllama-common.so.0.7.0`: tree dict and digest unchanged (6c216313…). Baseline `llama-server --version` exits 0. Redirected run exits 127 with `undefined symbol: llama_max_devices`. `nm -D` shows `libllama.so.0.7.0` defines that symbol and `libllama-common.so.0.7.0` does not (only these two were checked), so the loader consumed the redirect.
   - Re-point `libllama.so.0` to an absolute path outside the pinned dir (same bytes, `out/tree-symlink-demo/external/`): realpath is outside the pin, digest unchanged.
   A consistent attacker with install-dir write access can redirect a SONAME to a file outside the pin without changing any hashed byte. Adding a new regular file is still caught. Exploiting this with a *compatible* library is [INFERENCE]: not demonstrated, and symbol compatibility across the 51 members was not enumerated. Fix direction: hash symlink name→target (plus target digest or an external marker), and add a re-point mutant to the grid.
2. **MEDIUM (provenance): the pin is self-referential.** `run.py:58-61` takes `tree_sha` from `_tool_mod.install_tree()` on disk at driver start, the same disk observation the producer makes. The pin catches change between driver start and the gate. A tree swapped before driver start would yield a matching pin [INFERENCE on the live path; the gate-level self-pin control is VALID]. Wording should say "in-run consistency", not "pinned identity".
3. **LOW (calibration): the grid counts any nonzero exit as rejected.** `install-tree-grid.py:103` uses `"rejected" if code != 0`. A missing gate prints `rejected=3/3` with `baseline=INVALID` (exit 2). `run.py`'s want-codes still catch it, but the headline alone is not evidence.
4. **LOW (process): no official tree-grid artifacts in the lane.** At HEAD 7229fa9, `.ufo/waves/round-18/runs/` has no `tree-grid-no-pin`, `tree-grid-pin`, or `tree-pin-negative` files, and `commands.json` (`measured_commit` 7229fa9) has no tree records. The 0/3 and 3/3 numbers above are advisory reproduction, not measurement. L1 must run the official driver to retain them.
5. **INFO (boundary): system NEEDED libs sit outside the pin.** `libc.so.6`, `libstdc++.so.6`, `libgcc_s.so.1`, `libm.so.6`, `libssl.so.3`, `libcrypto.so.3`, `libgomp.so.1` are absent from the install dir and resolve via `/usr/lib` (LD_DEBUG). The claim should say "install-dir RUNPATH set".
6. **NIT:** grid `--json` rows embed the gate's temp path, so JSON is not byte-stable (identical after tempdir normalization). Text mode, which `run.py` uses, is stable. The grid's gate call omits `--require-schema v3`, which `run.py`'s live gate uses.

## Not verified
- Live producer (would start an ephemeral llama-server): not run. Official measurement is L1's.
- Consistent swaps used synthetic digest `'a'*64`. The gate never opens the tree; it reads only the receipt dict (grep-checked). Real-bytes swaps were not run separately.

## Commands (cwd `/tmp/kama-r19-C2ConsistentSwap`; exits observed)
- `cp -a /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r19-C2ConsistentSwap` → 0
- `git -C <lane> show 7229fa9:<path>` (refresh of 3 files) → 0; sha256 matches HEAD
- `python3 out/reproduce.py` → 0 (135 runs, all as expected; core checks true). Argv and exits in `out/commands.txt`.
- `python3 tests/llamacpp-live/install-tree-grid.py --gate <copy>/tests/llamacpp-live/check-receipt.py --receipt out/receipt-1.json --model-sha 270cba… --server-sha b6a31a8e… --impl-sha e404b91a… --probe-sha 36b64978… --tool-sha 83eac5c0… [--tree-sha 6c216313…]` → 0 with pin; 1 without
- `python3 tests/llamacpp-live/install-tree-grid.py --selftest` → 0
- `python3 tests/llamacpp-live/check-receipt.py --selftest` → 0
- `readelf -d` on five binaries → 0
- Baseline `llama-server --version` → 0; re-pointed copy → 127 (`out/tree-symlink-demo/ld-debug-final.{log,exit}`)
- Missing-gate grid → 2

Receipts: `out/reproduce-summary.json`, `out/runs/*.{stdout,stderr,exit}`, `out/mutants/`, `out/snapshot-8bf99ca/`, `out/run2-head-basic-runs/`.

## Recommendations (advice only)
- Do not describe the pin as covering "install-tree identity" until symlinks are hashed or refused.
- Anchor the expected digest outside driver-time disk state (a reviewed pin file or an upstream manifest).
- Count only exit 1 with an `INVALID` verdict as rejected.
- Run the official grid and retain artifacts at the measured commit before C2 is scored.
