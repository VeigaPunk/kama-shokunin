VERDICT: confirm - The C2 grid is path-independent for the copied and symlinked tree; an added directory is rejected.

Attack: C2 install-tree path independence and fail-closed handling of an unpinnable tree.
Axes: operability (8) and calibration (7).

## Findings
- Checked lane commit `a6617149722c73d90e142fbdc8154d6967055f7e` in a private scratch clone. `cp -a /home/vgpnk/.local/opt/llama-b11755 /tmp/kama-r21-C2GridPathIndependence/tree` created the test copy; a symlink path pointed to that copy. Scratch setup and copy command exited 0.
- Ran `python3 /tmp/kama-r21-C2GridPathIndependence/lane/tests/llamacpp-live/install-links-grid.py --tree /tmp/kama-r21-C2GridPathIndependence/tree --arm current --json`: exit 0.
- Ran the same grid with `--tree /tmp/kama-r21-C2GridPathIndependence/tree-via-symlink`: exit 0. The grid normalizes the symlink path to `/tmp/kama-r21-C2GridPathIndependence/tree`.
- A JSON comparison of the baseline `c2-grid-current.stdout`, copied-tree run, and symlink-path run exited 0: every JSON field except the expected `tree` path was equal. Thus both runs match the baseline on the full grid document, including summary and digests.
- Matching identity digests: `install_tree_sha256=6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c`; `install_links_sha256=5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060`. Source digests also match baseline: gate `6b8764374f1cc1059ba7520f7e7a68f37acc6a31b3e72220f4b42826e72d4a61`; producer `e4cc6d8885c7755717157fd23bfce3be39288990a9cf5985cb1c56a4b11cf68f`.
- Matching summary: `pass`, `real_tree_gate_clean=true`, no wrong cells; link 13/13 changed, subdir 1/1, regular 3/3, type 1/1, null 0/1.
- Added an empty regular file and a subdirectory only to the scratch copy. The fixture-creation command and type-recording command exited 0; the saved `mutation-fixtures.txt` confirms a regular file and directory.
- A producer-function probe exited 0: the regular file was inventoried, while `install_links()` reported exactly `['c2-grid-extra-subdir:not-regular-or-symlink']`. The grid on the mutated copy exited 2 with `could-not-evaluate: EvalError: ... real tree is not pinnable: ['c2-grid-extra-subdir:not-regular-or-symlink']`.
- The producer source at lines 1375–1379 explicitly raises `SetupError('install-tree-unpinnable:...')` on a nonempty `link_problems` list. The live producer entrypoint and llama-server were not run; the grid and import-only producer probe exercised the safe preflight behavior.

## Retained evidence
Under `.ufo/waves/round-21/falsify/out/C2GridPathIndependence/`: `copied-tree.stdout`, `copied-tree.stderr`, `copied-tree.exit`; `symlink-path.stdout`, `symlink-path.stderr`, `symlink-path.exit`; `identity-comparison.txt`; `mutation-fixtures.txt`; `mutated-producer-probe.stdout`, `mutated-producer-probe.stderr`, `mutated-producer-probe.exit`; `mutated-tree.stdout`, `mutated-tree.stderr`, `mutated-tree.exit`. Exit records contain 0 for both clean grids and the probe, and 2 for the mutated grid.

No lane files were changed. No tools were installed. No remaining blocker; direct live-producer execution was intentionally omitted under the no-live-run boundary.