ATTACK routed-defect-5/raw-hash-binding: holds

# Scope and axes

- Axes: raw-byte/digest binding; cell-to-file identity; behavioral sensitivity and exact restoration.
- Measured commit: `f4066979096e3452ae731c0e09e50155c6d8258a`, extracted with `git archive`, not the moving worktree.
- Target: `.ufo/waves/round-25/count-c2.py`, specifically `raw_bound` at lines 84-114 and its use in `bound` at lines 185-189.
- Rebuilt exactly the five inputs from `.ufo/waves/round-26/w1-build/advice/MutationC2Receipts.md` and its `out/MutationC2Receipts/mutations.json`. Their mutated hashes below match the wave-1 receipt mutants.
- Scratch root: `/fast/scratch/hyaku/kama-r26w2/MutC2Binding/`. Its root is the pristine-input case; five independent child extracts are `raw-bytes/`, `raw-sha/`, `raw-deleted/`, `raw-empty/`, and `raw-cross-cell/`.
- Result is limited to the assigned six-input suite and three binding-code mutants. No C1 signature, upstream-source, live-server or wider claim judgment was attempted. No production repair was made.

# Detector and landed results

Expected behavior: the pristine receipt retains `observed 14 bound True`; every assigned inconsistent raw-evidence input changes binding to `False`. Exit 0 is not acceptance by itself: the counter documents parsed-receipt exit 0 at lines 31-33 and returns it at line 193.

The identical bounded detector ran from each case's extracted root in every phase:

```sh
timeout --kill-after=2s 20s prlimit --as=268435456 --cpu=10 --nproc=8 --nofile=64 -- python3 .ufo/waves/round-25/count-c2.py
```

At most four independent case detectors ran concurrently. Each had a 256 MiB address-space limit, 10 CPU seconds, 20 wall seconds, process limit 8 and descriptor limit 64. All six pristine baseline runs succeeded before any mutation.

Here `R` means `.ufo/waves/round-25/final/context-capacity-receipt.json`; `H` means `.ufo/waves/round-25/final/raw/K1.health.body`. Locations refer to pristine bytes.

| Receipt mutant | Exact change | Landed counter stdout | Exit | Verdict |
|---|---|---|---:|---|
| pristine | None | `registered 14 observed 14 bound True missing []` | 0 | Baseline passes |
| raw-bytes | `H:1`: `{"status":"ok"}` → `{"status":"no"}`; receipt unchanged | `registered 14 observed 14 bound False missing []` | 0 | Killed |
| raw-sha | `R:71`: K1 `raw_health` first hex digit `a` → `b`; raw file unchanged | `registered 14 observed 14 bound False missing []` | 0 | Killed |
| raw-deleted | Delete H; retain the receipt digest | `registered 14 observed 14 bound False missing []` | 0 | Killed |
| raw-empty | `R:70-76`: replace K1 `raw` object with `[]` | `registered 14 observed 14 bound False missing []` | 0 | Killed |
| raw-cross-cell | `R:72-75`: copy K2's complete raw digest object (`R:167-173`) onto K1; health digest already identical; preserve all ids, measurements, args, argv and logs | `registered 14 observed 14 bound False missing []` | 0 | Killed |

Actual evidence: `out/MutC2Binding/baseline.json` and `landed.json`, relative to `.ufo/waves/round-26/w2-falsify/`. All stdout strings have one terminating newline; all stderr strings are empty. The five failures are binding rejections, not parse errors or lost observed cells.

# Binding-code mutant kill table

Each code mutant changed only one line in each isolated counter, with the six receipt/raw input states held fixed. Between mutants the counter bytes were restored and the same six-input detector suite was rerun. A code mutant is **killed** when a previously rejected invalid receipt becomes accepted; unchanged rejection means that individual receipt does not kill that code mutant. All code-mutant pristine-receipt runs remained accepted, so these are behavioral kills rather than crashes.

| Code mutant | Single change in count-c2.py | Receipt mutants that kill it | Verdict | Smallest correction to injected defect |
|---|---|---|---|---|
| M1: code-no-raw-bound | Line 189: remove `and raw_bound(cells)` from `bound`, leaving its closing parenthesis | raw-bytes, raw-sha, raw-deleted, raw-empty, raw-cross-cell | Killed | Restore the `and raw_bound(cells)` conjunct |
| M2: code-any-hash | Line 110: replace the own-file digest comparison with `if not val:`; any nonempty hash string is accepted for a schema-known raw key, while raw-shape/string and unknown-key checks remain | raw-bytes, raw-sha, raw-deleted, raw-cross-cell | Killed | Restore `if val != files.get(f"{c.get('id')}.{suffix}"):` |
| M3: code-no-cell-match | Line 110: replace the own-file digest comparison with `if val not in by_hash:`; match any raw file instead of this cell's prescribed file | raw-bytes, raw-deleted, raw-cross-cell | Killed | Restore the same own-file digest comparison |

Exact stdout key: **T** = `registered 14 observed 14 bound True missing []`; **F** = `registered 14 observed 14 bound False missing []`. Every entry below includes its actual exit code. **K** denotes a code-mutant kill by that input.

| Input | Landed | M1 | M2 | M3 |
|---|---|---|---|---|
| pristine | T / 0 | T / 0 | T / 0 | T / 0 |
| raw-bytes | F / 0 | **K: T / 0** | **K: T / 0** | **K: T / 0** |
| raw-sha | F / 0 | **K: T / 0** | **K: T / 0** | F / 0 |
| raw-deleted | F / 0 | **K: T / 0** | **K: T / 0** | **K: T / 0** |
| raw-empty | F / 0 | **K: T / 0** | F / 0 | F / 0 |
| raw-cross-cell | F / 0 | **K: T / 0** | **K: T / 0** | **K: T / 0** |

The M3 result on raw-bytes/raw-deleted is explained by the recorded pristine manifests: K2's health body has the same SHA256 as K1's. A directory-wide hash-membership test can therefore accept the missing or changed K1 file using another cell's health file. The arbitrary changed digest in raw-sha matches no file and still fails M3. The empty list still fails M2/M3 at lines 103-104.

No assigned receipt mutant survived the landed counter; no injected binding-code mutant survived the complete suite. No landed correction is indicated by this scoped probe. It does not assert coverage beyond the requested mutants.

# Before, mutated and restored hashes

SHA256 aliases, all measured from the archive extracts:

- **C0** (landed counter): `2f952dca58a4ff2efe55cbb9f2afcae1b8ae4efd41a3ee8461522699d77d760b`
- **R0** (pristine receipt): `78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c`
- **H0** (pristine health body): `a29ee2b15c494311c52521766e44af56a3ad2248e7a8ab465e5206463c13d288`

| Mutant | File | Before | Mutated SHA256 / state | Restored |
|---|---|---|---|---|
| raw-bytes | H | H0 | `4687dfd44b632f14cc079b5d1a007d9ea15e5aa7a11abf8177f6413f5da03ae4` | H0 |
| raw-sha | R | R0 | `a68b96085b26053e9e597a3e42af9a9876dbb5a9efe7f08f0bb9b8a7e7e96a58` | R0 |
| raw-deleted | H | H0 | Absent | H0 |
| raw-empty | R | R0 | `f8a9bf4a3cb48ced33a297a8cce0666fc012498dedb832f59c02358990e17c47` | R0 |
| raw-cross-cell | R | R0 | `509fdc0fb19c8e62cf4a7f696e974a79aee92846667cfe8423205107fb14b95d` | R0 |
| M1 | Counter | C0 | `c82509d45a2c99f017f7a97faac03cd4c599fd1598cca78c58be1aceb3ae1a40` | C0 |
| M2 | Counter | C0 | `75c28c40a3bdef48bd0a594c699d0f6312bf6f779d1b25e565dceed8e6b815fe` | C0 |
| M3 | Counter | C0 | `b5309147ffdf240e48da1872934bf9e56bacd54673050b254bedf348611c3e09` | C0 |

Each of the three code restorations exactly recovered the full landed six-input state, including the deliberately invalid receipt/raw inputs. After the final receipt/raw restoration, **all 76 counter/final files in each of the six extracts matched its pristine manifest**, with no added, missing or changed files. All six restored detectors printed `registered 14 observed 14 bound True missing []`, exit 0. The deleted health body was restored as its exact 15 original bytes, without a newline.

Across the nine phases there were **54 actual detector executions**, all exit 0 with empty stderr. No detector altered any input bytes, no baseline failed, and no result is inconclusive. `summary.json` records the kill sets and exact restoration comparisons; every phase JSON retains full SHA256 manifests, commands, cwd, stdout, stderr and exit codes.

# Reproduction and retained evidence

Initial extraction (exit 0, empty output):

```sh
mkdir -p /fast/scratch/hyaku/kama-r26w2/MutC2Binding /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/MutC2Binding && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive --format=tar f4066979096e3452ae731c0e09e50155c6d8258a .ufo/waves/round-25/count-c2.py .ufo/waves/round-25/final | tar -x -C /fast/scratch/hyaku/kama-r26w2/MutC2Binding
```

Five child extracts were independently unpacked from a captured `git archive` of those same paths, with those three Git environment variables unset. Archive SHA256: `314571e4d8877b1472defaddff00fc5ef4b198b64f422e3cadc41ab3d78c5986`; archive command exit 0, stderr empty. Exact provisioning details are in `setup.json` and `written-files.json`.

The suite invocation was:

```sh
timeout --kill-after=5s 90s python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/MutC2Binding/probe.py --stage landed
```

The same command ran once for each literal stage value, in this order: `baseline`, `landed`, `code-no-raw-bound`, `code-no-raw-bound-restored`, `code-any-hash`, `code-any-hash-restored`, `code-no-cell-match`, `code-no-cell-match-restored`, `restored`. Every suite invocation exited 0. `written-files.json` records every fully expanded suite command and its exit code. `probe.py` only records detector results and hashes; mutations/restorations were explicit scratch-file edits, not hidden harness transformations.

Process check: `pgrep -af '[l]lama-server'` exited **1**, stdout/stderr empty. This seat had no port block and started no server, model runtime, detached process, nested agent, installation, Git-index operation, jj command, commit or push. All detector/archive subprocesses completed. Lane production files and sibling sources were not edited. Tool installs or updates: **none**.

Files written in the lane (all paths relative to the lane):

1. `.ufo/waves/round-26/w2-falsify/advice/MutC2Binding.md` — this report.
2. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/probe.py`
3. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/setup.json`
4. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/mutations.json`
5. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/baseline.json`
6. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/landed.json`
7. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/code-no-raw-bound.json`
8. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/code-no-raw-bound-restored.json`
9. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/code-any-hash.json`
10. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/code-any-hash-restored.json`
11. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/code-no-cell-match.json`
12. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/code-no-cell-match-restored.json`
13. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/restored.json`
14. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/summary.json`
15. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/process-check.json`
16. `.ufo/waves/round-26/w2-falsify/out/MutC2Binding/written-files.json`

Every one of the **456 extracted scratch files** is named by absolute path in `written-files.json`; the only edited/deleted scratch paths were each extract's counter and the five receipt/raw mutation targets above, now exactly restored.

Report: .ufo/waves/round-26/w2-falsify/advice/MutC2Binding.md
