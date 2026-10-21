# C2GridReview evidence (FALSIFY, round 21)

Target: `tests/llamacpp-live/install-links-grid.py` @ `a6617149722c73d90e142fbdc8154d6967055f7e`.
All grid runs used a scratch clone at a6617149 (`LANE` = clone), never the live lane.
Measured reference: `.ufo/waves/round-21/runs/b76727f3/c2-grid-*.stdout` (commands.json exits: selftest 0, current 0, frozen 1, both 1).

## 1. Reproduction of requested runs (cwd = scratch clone at a6617149)

| command | exit | comparison |
|---|---|---|
| `python3 tests/llamacpp-live/install-links-grid.py --selftest` | 0 | stdout identical to `c2-grid-selftest.stdout` (diff exit 0); 13 ok, `selftest cases=13 failed=0` |
| `--arm current` (text) | 0 | `summary arm=current link=13/13 subdir=1/1 regular=3/3 type=1/1 null=0/1 wrong=0 real_tree_gate_clean=True status=pass` |
| `--arm current --json` | 0 | identical to `c2-grid-current.stdout` (diff exit 0) |
| `--arm frozen` (text) | 1 | `summary arm=frozen link=0/13 subdir=0/1 regular=3/3 type=1/1 null=0/1 wrong=14 status=fail` |
| `--arm frozen --json` | 1 | identical to `c2-grid-frozen.stdout` (diff exit 0) |
| `--arm both --json` | 1 | identical to `c2-grid-both.stdout` (diff exit 0); `back_compat_install_tree_sha256_equal=True` |

Text render parity: `render(json)` equals the text file for both arms after restoring CLASSES key order (JSON `sort_keys` reorders `by_class`; cosmetic only).
Files: `selftest.stdout`, `arm-current.{txt,json}`, `arm-frozen.{txt,json}`, `arm-both.json`, `*.stderr` (all 0 bytes).

## 2. Structural facts
- `NEEDED_SONAMES` = (libggml-base.so.0, libggml.so.0, libllama-common.so.0, libllama.so.0, libmtmd.so.0).
- `readelf -d -W llama-server` (rc 0): NEEDED = libllama-server-impl.so, libstdc++.so.6, libgcc_s.so.1, libc.so.6 (none of the five).
- `readelf -d -W libllama-server-impl.so` (rc 0): NEEDED includes exactly the five soname names plus libssl.so.3, libcrypto.so.3, libstdc++.so.6, libm.so.6, libgcc_s.so.1, libc.so.6, ld-linux-x86-64.so.2.
- Python scan of 49 ELF files in tree: in-tree symlink names NEEDED by any ELF = exactly the five; dev links (libggml-base.so, libggml.so, libllama-common.so, libllama.so, libmtmd.so) NEEDED by none.
- In-tree symlinks: 10 (5 soname + 5 dev), all same-directory basenames. Regular files: 51; `regular[-1]` = `llama-tts` (unreadable victim). Cells: 19.
- `ld.so --list-diagnostics` (rc 0): `dl_hwcaps_subdirs="x86-64-v4:x86-64-v3:x86-64-v2"`, `dl_hwcaps_subdirs_active=0x7`. `ldd --version`: GNU libc 2.44.
- `stat` real tree: mtime/ctime 2026-10-20 (pre-session); grid never wrote to it.

## 3. Boundary matrix (scratch trees, `out/C2GridReview/boundary-matrix.json`, `--arm current` unless noted)

| case | exit | observed |
|---|---|---|
| no dev links (5 removed) | 0 | `link=12/12 ... wrong=0 status=pass` (dev cell silently dropped) |
| glibc-hwcaps/ dir in tree | 2 | `real tree is not pinnable: ['glibc-hwcaps:not-regular-or-symlink']` |
| libmtmd.so.0 link missing | 2 | `missing soname link(s): libmtmd.so.0` |
| libggml.so.0 dangling (-> .so.9) | 1 | `real_tree_gate_clean=False status=pass` |
| unreadable member libllama-common.so.0.7.0 (current) | 2 | `not pinnable: ['libllama-common.so.0.7.0:unreadable']` |
| unreadable member (frozen) | 2 | PermissionError at mirror copy |
| FIFO member | 2 | `not pinnable: ['kama-fifo:not-regular-or-symlink']` |
| llama-server removed | 2 | `llama-server missing` |
| --tree nonexistent | 2 | `llama-server missing` |
| --tree is a regular file | 2 | `LICENSE/llama-server missing` (message does not say "not a directory") |
| --tree = symlink to real tree | 0 | JSON identical to measured current (realpath handling OK) |
| non-git lane, `--arm frozen` | 2 | `git show ...: fatal: not a git repository` |
| non-git lane, `--arm current` | 0 | summary pass (current arm needs no git) |

## 4. Root (`sudo -n`, uid 0; passwordless sudo confirmed rc 0)
- Probe: mode-0 file, `os.access(R_OK)` = True, open+read = True.
- `sudo -n env PYTHONDONTWRITEBYTECODE=1 python3 install-links-grid.py --arm current --tree ~/.local/opt/llama-b11755` -> rc 1; `regular-unreadable ... current=same`; `summary ... regular=2/3 wrong=1 ... status=fail` (`root-arm-current.txt`).
- Same with `--selftest` -> rc 1: FAIL current-catches-all-via-symlinked-tree, FAIL controls-both-arms, FAIL current-only-exit-0 (`root-selftest.txt`).
- Producer `_install_identity_selftest()` imported as root (unmodified lane) -> returns OK; as root on mutant M1 -> returns OK (vacuous).

## 5. Injected hash-time read error (`sha256_file` raises EIO for libggml.so.0.27.0)
- a6617149 producer: install_tree members = [libllama.so.0.7.0, llama-server]; install_links problems = []; links = {libllama.so.0: libllama.so.0.7.0} -> no refusal.
- Worktree snapshot producer: problems = ['libggml.so.0.27.0:not-hashed'] -> refusal.

## 6. Mutants (scratch clones; patches in this dir)
- M1 (a6617149 producer: remove `elif not os.access(...)` unreadable branch, lines 241-242): `producer --identity selftest` non-root rc 1 (AssertionError 'unreadable member not a problem'); root rc 0. `grid --selftest` rc 0 (13/13). `grid --arm current` rc 0; `regular-unreadable` changed, `refused`=False (`m1-*.txt/json`).
- M6 (remove `elif not S_ISREG` non-regular branch, lines 239-240): producer selftest rc 1 (AssertionError 'subdirectory not reported as a problem'); `grid --selftest` rc 1 (3 FAIL); `grid --arm current` rc 1 (`subdir=0/1 wrong=1`) (`m6-*.txt`).
- M1 on worktree snapshot (`wtm1`): `grid --arm current` rc 0; `regular-unreadable ... changed+refused` (via not-hashed); `grid --selftest` rc 0; producer identity selftest non-root rc 1 (`wtm1-*.txt`).

## 7. hwcaps premise (ld.so --list, rc 0 both)
- without subdir: `libllama.so.0 => /tmp/kama-r21-C2GridReview/hw0/libllama.so.0`
- with glibc-hwcaps/x86-64-v3/libllama.so.0: `libllama.so.0 => .../hw1/glibc-hwcaps/x86-64-v3/libllama.so.0` (subdir copy loaded)

## 8. Source-level checks (read-only greps / reads)
- `install-tree-unpinnable` referenced in lane only at producer main (`kama-llamacpp-live.py` 1377-1379) and docs; no test references it.
- frozen (7a6bc911) vs current (a6617149): `sha256_file` and `install_tree` source identical (True/True).
- Measured `current_sources_sha256`: producer e4cc6d88..., gate 6b876437... = a6617149 blobs.

## 9. Live lane state (read-only; `git --no-optional-locks`)
- HEAD = a6617149 (rc 0). `status --porcelain`: M SCORECARD.md, corpus/SOURCES.md, tests/llamacpp-live/check-receipt.py, tests/llamacpp-live/install-links-grid.py, tools/kama-llamacpp-live.py, tools/report-landing-audit.py; untracked .ufo/waves/round-21/{build/completion-summary.json, build/verdict-count.json, falsify/, wave-accounting.py}.
- Worktree vs a6617149 sha: grid ae248248 vs 4f091523 (differs); producer cec67949 vs e4cc6d88 (differs); gate 63b6884c (first read) -> 0ba37be3 (snapshot): gate moved during the review.
- `git diff --name-only b76727f3 a6617149`: 86 files, all under `.ufo/waves/round-21/runs/b76727f3/` (no code change in that step).
- Disclosure: one `git status --short` ran without `--no-optional-locks` (may refresh the index stat cache; no content change).
- Worktree delta vs a6617149 saved as `worktree-vs-a6617149.diff`; snapshot outputs `wt-snapshot-*.txt` (grid selftest rc 0 13/13; `--arm current` rc 0; `--arm frozen` rc 1).

## 10. Tools
No installs or upgrades. Used existing: GNU readelf 2.47, ld.so/ldd (glibc 2.44), python3 3.14.8, git 2.56.0, sudo -n. No servers or daemons started; producer `main` not executed.
