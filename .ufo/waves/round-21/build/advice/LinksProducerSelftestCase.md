VERDICT: confirm - `--selftest` never runs install_tree/install_links (0 calls, rc 0 at a29bb84); the patch adds a stub-install case that pins the link map/digest and retarget invariance, passes on the patched producer and fails 9/9 seeded defects.

# LinksProducerSelftestCase (round 21, BUILD): producer selftest coverage

Base a29bb84abbb8b4d328f5970a89e448330a3a42ac. Work in scratch clone `/tmp/kama-r21-LinksProducerSelftestCase` (removed at end). Lane not written; the only lane write is this report at the path the assignment names. No tool installed or upgraded. No labrat spawned (leaf seat).

## 1. Finding: the producer selftest never reaches install_tree/install_links
- `git show a29bb84:tools/kama-llamacpp-live.py | grep -n 'install_'` (exit 0): hits only at 178, 205, 207 (docstring), 1229-1230 (receipt init), 1293-1294 and 1306-1309 (`main()`). `_selftest()` spans 1082-1180 and contains none.
- Instrumented run: `probe_calls.py` on a29bb84 printed `probe: selftest_rc=0 install_tree_calls=0 install_links_calls=0` (exit 0). Plain `--selftest` printed `selftest: ok; closed tcp6 listeners ::1:41869, ::ffff:127.0.0.1:34305`, exit 0.
- Existing exercisers sit outside `--selftest`: `tests/llamacpp-live/install-links-grid.py` `identities()` (lines 150-156) loads the producer and calls both functions; `check-receipt.py` selftest feeds synthetic `SELFTEST_LINKS` (line 1644), not producer code. The live `main()` path was not run.

## 2. Patch
- `out/LinksProducerSelftestCase/links-producer-selftest.patch` (3296 B): `git diff` vs a29bb84, only `tools/kama-llamacpp-live.py`; `git diff --numstat` = `45 1`.
- Adds `_install_identity_selftest()` (patched lines 1082-1122), called from `_selftest()` at line 1222. `_selftest` docstring extended. install_tree/install_links bodies untouched.
- Stub install: `llama-server` plus regular libs `libllama.so.0.7.0` and `libllama.so.0.7.1`. The second lib is the retarget target, so the retarget is a real soname bump onto a pinned regular member. Chain `libllama.so -> libllama.so.0 -> libllama.so.0.7.0` mirrors the real tree: read-only `readlink` on `~/.local/opt/llama-b11755` gave exactly that (exit 0 each).
- Asserts: (a) install_tree == the three regular members' sha256 plus the `name sha\n` digest, symlinks absent; (b) install_links == `{libllama.so: libllama.so.0, libllama.so.0: libllama.so.0.7.0}` and digest == sha256 of the pinned bytes `name -> text\n` lines; (c) retarget `libllama.so.0` -> `libllama.so.0.7.1` records the new text, changes install_links_sha256, and leaves install_tree and install_tree_sha256 unchanged.
- Companion scripts in the same out dir: `probe_calls.py PRODUCER` (counts calls, runs `--selftest`) and `mutants_probe.py PRODUCER` (control plus 9 seeded defects).

## 3. Executed checks (exit as observed)
| command | exit | observed |
|---|---|---|
| `python3 tools/kama-llamacpp-live.py --selftest` (scratch, a29bb84) | 0 | ok line above |
| `probe_calls.py` (a29bb84) | 0 | calls 0 / 0 |
| `--selftest` on patched fresh clone, then 5 repeats | 0 each (6 runs) | `selftest: ok; ...` |
| `probe_calls.py` (patched) | 0 | `install_tree_calls=2 install_links_calls=2` |
| `mutants_probe.py` (patched, scratch and clone) | 0, 0 | control PASS; 9/9 substitutes FAIL with expected text |
| `git apply --check`, then `git apply` on fresh a29bb84 clone | 0, 0 | `1 file changed, 45 insertions(+), 1 deletion(-)` |
| `git apply --check -R`; `git diff --check` (clone) | 0, 0 | reverse-applies; no whitespace errors |
| `cmp` clone file vs scratch lane file | 0 | identical |
| helper raises, then `main(['--selftest'])` | rc 1 | stderr `kama-llamacpp-live selftest: AssertionError` |
| `git status --porcelain` (clone) | 0 | only ` M tools/kama-llamacpp-live.py` |

Seeded defects (each FAILs at the assertion named):
- tree-follows-symlinks: install_tree members mismatch
- tree-digest-without-newline: install_tree_sha256 digest mismatch
- tree-moves-on-retarget: retarget moved install_tree identity
- links-empty: install_links map mismatch
- links-resolved-target: install_links map mismatch (absolute realpaths)
- digest-names-only, digest-without-arrow: install_links_sha256 digest mismatch
- links-stale-pair: retarget not recorded by install_links
- links-stale-digest: retarget left install_links_sha256 unchanged

## 4. Caveats for L1
- Coupling: the helper pins the `name -> text\n` digest format, identical to `check-receipt.py` `install_links_sha()` (lines 173-178). Any producer encoding change must change those literals in the same commit.
- Uncovered: the `except OSError` branches (`({}, None)`) in install_tree/install_links are not asserted. They are outside the requested assertions.
- Doc: the SKILL.md "Ownership parser" row (line 611) scopes `--selftest` to tcp6. Update it after integration. QUALITY.md:102-103 (quoted in ConnectMori.md, not re-read here) requires a registry-row sweep when a selftest changes.
- Tool bytes: any edit to `tools/kama-llamacpp-live.py` changes `tool.sha256` on later receipts. The matches I read in tests/llamacpp-live, registry and SKILL.md show `--expect-tool-sha256` placeholders only. Output was truncated, so no committed tool digest is claimed [INFERENCE].
- Not run: live llama-server or `kama-llamacpp-live.py` launch (forbidden); `install-links-grid.py` (not needed to decide this claim); gate selftests; linters (edit wave in flight).
- Linux-only, like the tool (symlinks, procfs).
- Cleanup: scratch removed; `pgrep` found no process from this seat; no selftest temp dirs left behind.
