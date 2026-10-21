VERDICT: confirm - the pre-pin grid (gate 1b85a24, no tree pin) rejects 0/3 consistent swaps (exit 1); with the pin on the committed round-19 gate (7229fa9) it rejects 3/3 (exit 0), identically on live-recovery receipts 1-3. Outside the claim: SONAME-symlink retargets leave the pinned digest unchanged (R2).

# GateTreeBaseline: install-tree grid before/after (round 19, C2)

## Scope and provenance
- The lane HEAD is now `7229fa9` (round-19 commit), not `1b85a24`: the lane committed after my copy was taken. `1b85a24` is an ancestor (`git merge-base --is-ancestor`, exit 0).
- I re-measured on the committed bytes, read with `git show` (gate blob `fe53e789…`, sha256 `10912f24…`; grid sha256 `49a42f81…`). The copy-time working-tree snapshot (gate `afc9e79b…`, grid `467d44d8…`) gives the same cells.
- Work copy: `/tmp/kama-r19-GateTreeBaseline` (`cp -a` of the lane at `8bf99ca`). The lane was only read; this report is the only lane write.
- Evidence: `out/head-7229fa9/` (primary: `receipt.json`, `COMMANDS.txt`, `SUMMARY.txt`, `matrix/`, `census/`, `snap/`). The copy-time run is in the `out/` root.

## Before / after (receipt-1; receipts 2 and 3 print identical lines)

| cell | gate | tree pin | exit | grid output |
|---|---|---|---|---|
| Before | 1b85a24 blob, sha256 `1dfcf23e…ad99` | off | **1** | `baseline=VALID members=3 rejected=0/3 tree_pin=off` |
| After | 7229fa9 blob, sha256 `10912f24…92dd` | on | **0** | `baseline=VALID members=3 rejected=3/3 tree_pin=on` |

Commands (run in `/tmp/kama-r19-GateTreeBaseline`; pins are receipt-1's recorded values; absolute-path forms are in `out/head-7229fa9/COMMANDS.txt`):
```
/usr/bin/python3 out/head-7229fa9/snap/install-tree-grid.7229fa9.py --gate out/gates/check-receipt.1b85a24.py --receipt .ufo/waves/round-18/live-recovery/receipt-1.json --model-sha 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --server-sha b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --impl-sha e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed --probe-sha 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --tool-sha 83eac5c0489377a88c8ecead89af4ca5f057bd0463d8bf8a79467eb6c5de88c4
/usr/bin/python3 out/head-7229fa9/snap/install-tree-grid.7229fa9.py --gate out/head-7229fa9/snap/check-receipt.7229fa9.py --receipt .ufo/waves/round-18/live-recovery/receipt-1.json --model-sha 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --server-sha b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --impl-sha e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed --probe-sha 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --tool-sha 83eac5c0489377a88c8ecead89af4ca5f057bd0463d8bf8a79467eb6c5de88c4 --tree-sha 6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c
```
- Controls from the same runner: 7229fa9 gate without the pin, exit 1, `rejected=0/3`; 1b85a24 gate with the pin, exit 2, `baseline=INVALID … rejected=3/3` (see R1).
- Direct gate checks on receipt-1: 1b85a24 + pins exit 0 (VALID); 7229fa9 + pins exit 0; 7229fa9 + pins + tree pin exit 0; 7229fa9 + pins + tree pin `0`×64 exit 1 (`server.install_tree_sha256 6c216313… != expected 0000…`); 1b85a24 + tree pin exit 2 (`unrecognized arguments: --expect-install-tree-sha256`).
- Runner `/usr/bin/python3 out/run_head.py` exit 0; the two passes are identical after masking grid tempdir names (`determinism identical=True`); `all_as_expected=True`.

## Attribution
- After: each of the 3 mutants exits 1 with one problem, `server.install_tree_sha256 <recomputed> != expected 6c216313…`. Before: each of the 3 mutants is `VALID` (exit 0).
- Gate delta 1b85a24 → 7229fa9 (`git diff --numstat`, exit 0): 33 insertions, 3 deletions. These are usage text, the `expect_tree` parameter, the tree-pin check in `validate`, the expect-loop entry, the argparse flag, and selftest cases (two new mutations, selftest-only). On every measured no-pin case (grid cells A and C; direct checks G1 and G2) the two gates give identical verdicts.
- Pin value: the live producer `install_tree()` on `/home/vgpnk/.local/opt/llama-b11755` gives `6c216313…` (51 members, none differing from receipt-1; `out/producer-install-tree.json`). This is the same value `run.py` passes (HEAD lines 58-61).
- The lane's `run.py` (HEAD lines 67-68) already expects exit 1 for the no-pin run and 0 for the pin run. The measurements match.

## Supplementary census (all 51 members of receipt-1; `out/head-7229fa9/census/SUMMARY.txt`; `/usr/bin/python3 out/census.py` exit 0)
- 1b85a24, no pin: exit 1, `rejected=2/51`, 49 accepted. The two rejections come from pre-existing checks: `llama-server` (`install_tree['llama-server'] != server.sha256`) and `libllama-server-impl.so` (`server_impl_sha256 != install_tree[...]`).
- 7229fa9 + pin: exit 0, `rejected=51/51`. 49 are rejected solely by the pin, with one problem each. The two above also fail the pin, with two problems each.
- So the pin adds exactly the 49 members that the five existing pins leave unbound. All three default grid members are among them. The pre-round gate's own comment (`check-receipt.1b85a24.py:393-395`) says the same.

## Residuals
- **R1 (low, harness).** The grid marks any nonzero gate exit as `rejected` (`install-tree-grid.py:103`), so a usage error counts. Cell D prints `baseline=INVALID … rejected=3/3`; the exit 2 is the only guard. Suggested (unexecuted): count only exit 1 as rejected, and print counts only for a VALID baseline.
- **R2 (medium; outside C2's claim; not measured by the grid).** `install_tree()` keeps regular files only (`lstat` + `S_ISREG`, `tools/kama-llamacpp-live.py:178-199`). The install has 10 symlinks, including SONAME links `libllama.so.0`, `libggml.so.0` and `libggml-base.so.0` (`find -maxdepth 1 -type l`, exit 0). llama-server and the three default libraries have RUNPATH `$ORIGIN` (`readelf -d`, exit 0), and libllama-common NEEDs `libllama.so.0`, `libggml.so.0` and `libggml-base.so.0`.
  - Probe `/usr/bin/python3 out/probes/symlink_probe.py` (exit 0): on a private copy of the install, retargeting `libllama.so.0` from `libllama.so.0.7.0` to `libllama-common.so.0.7.0` leaves the digest at `6c216313…`. That equals the receipt pin, and the tree dict is equal. The bytes the link resolves to change (`983e1a2a…` → `3270bc66…`). A synthetic control shows that a regular-member swap does change the digest.
  - Whether ld.so then loads the retargeted bytes is [INFERENCE]: the loader was not run.
  - Suggested (unexecuted): fold each SONAME link's resolved target into the pinned digest, and add a symlink-retarget mutant to the grid.
- **R3 (lane docs).** A case-insensitive grep for `soname|retarget`, and for symlink near tree/pin, across `corpus/`, the round-18/19 waves, `tools/` and `tests/`, found no discussion of SONAME-link retargeting. The only "symlink" hits concern other links: `ResidImplPin.md:31`, `ConnectTsukuroi.md:74`, `ScoutLlamaNewerTags.md:19`.

## Not exercised / limits
- The lane's new grid `--selftest` mode and the gate's selftest were not run (outside this assignment).
- No server was started, and there was no network access or persistent process.

## Records
- Installs or updates: none. Tools used: `/usr/bin/python3` 3.14.8, git, readelf, cp, sha256sum, grep.
