VERDICT: partial - row drafted from executed exits at 37bd4c5; grid exit 0 can hide gate crashes (red cell confirmed), so the verdict map is conditional until fixed.

# RegGridRow — `tests/llamacpp-live/install-tree-grid.py` (CloseKama18 RegGridRow-2)

Pin `37bd4c5bd456a2f8a54d3312c28495c321715856`; scratch clone checkout exit 0; lane untouched. Host python3 3.14.8. No tools installed or upgraded; no server, network or model download.

## Classification: measurement, not gate [INFERENCE: judgment]
Verdict is a kill count over mutants of `check-receipt.py`. Exit 1 = "a mutant survived" (`:129`), a finding about the gate; no receipt is accepted by its exit. Same shape as the round-16/17 C1 counting rows.

## Exit map (`:127-129`, `:110-111`)
- 0: baseline VALID and every row `rejected`.
- 1: a row `accepted`/`absent`/`error`; no-pin mode exits 1 whenever a mutant survives.
- 2: baseline not VALID (gate exit 3 included, printed as INVALID), receipt unreadable, or no `install_tree`.
- Mutant status: gate exit 1 -> `rejected`; 2/3 -> `error`; else `accepted`.
- Uncaught Python exception exits 1 (same code as "survivor").

## Executed evidence (outputs in `.ufo/waves/round-20/build/out/RegGridRow-2/`)
| Command | Exit | Observed |
|---|---|---|
| `install-tree-grid.py --selftest` (x2) | 0, 0 | `selftest: baseline, member rejection, absent member and bad receipt passed` |
| real grid, no pin | 1 | `baseline=VALID members=3 rejected=0/3 tree_pin=off` |
| real grid + `--tree-sha 6c2163…785a2c` | 0 | `baseline=VALID members=3 rejected=3/3 tree_pin=on` |
| same with `--json` | 0 | schema `kama-install-tree-grid/v1`; gate stdout `INVALID … install_tree_sha256 … != expected` |
| `--tree-sha` = 64 zeros | 2 | `baseline=INVALID members=0 rejected=0/0` |
| `--receipt /nonexistent.json` | 2 | `cannot read …` |
| real gate, pins + `--require-schema v3` on receipt-1 | 0 | `VALID …receipt-1.json` |
| `--members libllama.so.0.7.0` + pin | 0 | `VALID 1 1 ['rejected']` |

Fake-gate probes (grid with pin; stubs in `out/RegGridRow-2/fake-gates-src/`, ephemeral):
| Gate behaviour | Grid exit | Rows |
|---|---|---|
| real `check-receipt.py` (control) | 0 | rejected 2/2 |
| uncaught exception, exit 1, empty stdout | **0** | **rejected 2/2**, stdout `''` |
| silent `sys.exit(1)` | **0** | **rejected 2/2** |
| NOT-EVALUATED exit 3 / exit 2 | 1 | error 0/2 |
| real INVALID text, exit 1 | 0 | rejected 2/2 |
| baseline gate exit 3 / crash | 2 | `baseline=INVALID` |

Malformed receipts: `{}` -> exit 1 `KeyError: 'server'`; `[]` -> exit 1 `TypeError` (`crash-*.stderr`).

## Pinned values (sha256 at 37bd4c5)
- `install-tree-grid.py` = `6f51803c47db597e2f6778b492bfaba14735a23c599bc972f8d33ab477a68f05` (blob `5ebd958293f18eae04ed47e4080a4e242893c688`)
- `check-receipt.py` = `a0dc1d07220ff804e375d5947ed8119a3ae697da5dbd0cc83006b2abe39043a6`
- round-18 `receipt-1.json` = `89728a0248f208ada93ae9b2ce08a5da5e65bcd30259c43b8329d3e6d3bca863`; recorded `server.install_tree_sha256` = `6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c`
- Pins: model `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; server `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`; impl `e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed`; probe `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`; tool `83eac5c0489377a88c8ecead89af4ca5f057bd0463d8bf8a79467eb6c5de88c4`.
- Default members (`:29-30`): `libggml-base.so.0.27.0`, `libllama-common.so.0.7.0`, `libllama.so.0.7.0`.

## Row text (draft for `SKILL.md`, owner kama; L1 merges)

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Install-tree swap grid (receipt-gate mutant kill count) | measurement: `python3 tests/llamacpp-live/install-tree-grid.py --gate tests/llamacpp-live/check-receipt.py --receipt .ufo/waves/round-18/live-recovery/receipt-1.json --model-sha 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --server-sha b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --impl-sha e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed --probe-sha 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --tool-sha 83eac5c0489377a88c8ecead89af4ca5f057bd0463d8bf8a79467eb6c5de88c4 [--tree-sha 6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c] [--members NAME ...] [--json]`; 0 baseline VALID and every member rejected (pin mode); 1 a member survived, absent or errored (no-pin mode always 1 at 37bd4c5: rejected 0/3); 2 baseline not VALID (gate exit 3 printed as INVALID), receipt unreadable or no install_tree. Caveat: a crashed mutant gate (exit 1, no INVALID stdout) is counted `rejected`, so 0 does not yet prove each kill is a gate INVALID verdict (C1 red cell, `:110`). | `python3 tests/llamacpp-live/install-tree-grid.py --selftest`: exit 0, 3 cases (VALID + pinned member rejection, absent member, bad receipt); prints `selftest: baseline, member rejection, absent member and bad receipt passed`. Does not exercise crash, NOT-EVALUATED or silent mutants. | receipt-1 sha `89728a02…bca863`; install-tree sha `6c216313…785a2c`; grid sha `6f51803c…f05`; gate sha `a0dc1d07…043a6` (full `a0dc1d07220ff804e375d5947ed8119a3ae697da5dbd0cc83006b2abe39043a6`) | stdout only; temp dir `install-tree-grid-*` created and removed; selftest uses its own temp dir; no fleet, lane or server writes | kama |

Round-18 argv (`runs/run.py:66`, want=1; `:68`, want=0): no-pin form, then the same plus `--tree-sha 6c216313…785a2c`.

## Discrepancies (route to L1; not fixed here)
1. Docstring (`:17-18`) says without `--tree-sha` the caller reads the count; code returns 1 on any survivor (`:129`).
2. C1 red cell confirmed: gate exit 1 with no INVALID stdout counts as `rejected` (`:110`); the real verdict is `INVALID ` + exit 1 (`check-receipt.py:2233-2236`).
3. Baseline gate exit 3 is printed as `baseline=INVALID` (`:92`).
4. Uncaught exceptions exit 1 (`:76-129`), colliding with "survivor".
5. Gate stderr is discarded (`:50-53`).
6. Selftest covers 3 cases (`:188-192`) and none of the crash/NOT-EVALUATED/silent paths.

## Hygiene
Scratch `/tmp/kama-r20-RegGridRow-2` removed (rm exit 0; post-check 0 matches). New files only under `out/RegGridRow-2/` and this report. Report: .ufo/waves/round-20/build/advice/RegGridRow.md
