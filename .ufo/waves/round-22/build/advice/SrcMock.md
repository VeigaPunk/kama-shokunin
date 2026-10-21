# SrcMock — round 22 source scout: unittest.mock "Where to patch"

Seat: KamaR22.SrcMock (scout, read-only). Owned path: this file only.
No SOURCES edit, no verification runs, no installs.

## Source opened (this round)

- URL: https://docs.python.org/3.14/library/unittest.mock.html#where-to-patch
- Version: page title "unittest.mock — mock object library — Python 3.14.8 documentation"; opened 2026-10-21.
- Section: §The patchers › §Where to patch, ¶2 (anchor `#where-to-patch`).
- Quote (22 words): "The basic principle is that you patch where an object is looked up, which is not necessarily the same place as where it is defined."
- Companion sentence, same page, §patch() ¶3: "the target must be importable from the environment you are calling `patch()` from."
- Implementation cross-check (installed `/usr/lib/python3.14/unittest/mock.py`, `python3 --version` 3.14.8, matches the docs version):
  - lines 1684–1690 `_get_target`: string targets resolve via `pkgutil.resolve_name` (an import).
  - lines 1476–1477: a builtin name on a `ModuleType` target sets `create = True` automatically.

## Redundancy check

`corpus/SOURCES.md` has no `unittest`/`mock` row. The highest ID is S074, and S075–S079 appear nowhere in `corpus/`. The Python rows S061, S064 and S065 cover `sys.exit` and `subprocess`, so this source does not overlap them.

## Proposed row (ID reserved for L1; next free = S075)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S0__ (L1: S075) | Python unittest.mock, Where to patch — https://docs.python.org/3.14/library/unittest.mock.html#where-to-patch | docs | A | name-lookup target of `patch()`/`patch.object()` in Python 3.14.8; it does not cover whether an injected exception is faithful to real kernel errno behaviour | §The patchers › §Where to patch ¶2; §patch() ¶3 "importable" sentence; Python 3.14.8 documentation opened 2026-10-21; installed mock.py 3.14.8 lines 1476–1477, 1684–1690 | A fault patched where the code under test does not look the name up has no effect, and the arm then looks green while doing nothing. The matrix must patch at the producer's lookup site and prove the fault was reached. | mined if install-io-grid.py adopts the lookup-site and reach-proof rules below; otherwise queued | 2026-10-21 | on-release | tests/llamacpp-live/install-io-grid.py (proposed), round-22 lesson if written |

Tier A rationale: the source is the official, versioned stdlib documentation, and the installed implementation agrees with it on the two mechanics the matrix depends on.

Flip conditions:
- The claim stops resting on this row if the matrix injects faults by a non-`mock` method, such as real chmod or a fake filesystem.
- The row needs re-reading if a later Python release changes `_get_target` or builtin auto-create.

Not rejected: the source is strong. Its only limit is the scope above (mocked `OSError` ≠ real I/O failure).

## Lookup sites in the producer (observed, `tools/kama-llamacpp-live.py` @ lane checkout)

| Fault | Producer lookup | Correct scoped patch | Wrong / over-broad patch |
|---|---|---|---|
| listdir | `import os` (l.34); `os.listdir(directory)` l.185, call-time attribute on the shared `os` module | `patch.object(mod.os, 'listdir', side_effect=wrapper)`, where `wrapper` raises only for the exact tree directory and otherwise delegates to the captured real `os.listdir` | Unconditional `patch('os.listdir', side_effect=OSError)`: process-wide; also hits `install_links` l.232, `/proc/{pid}/fd` l.440 and harness tempfile cleanup [INFERENCE] |
| lstat | `os.lstat(full)` l.191; `install_links` also l.245 | Path-keyed wrapper on `mod.os.lstat` for one member path | Unconditional lstat patch: `install_links` and `os.path.realpath`/`isfile` [INFERENCE] fail together, which blurs which consumer refused |
| member read | `sha256_file(full)` l.197, a module global looked up in `mod.__dict__` | `patch.object(mod, 'sha256_file', side_effect=wrapper)` per arm; or `patch.object(mod, 'open', ...)` (auto-`create` applies because `mod` is a `ModuleType`) for a mid-read `fh.read` failure | `patch('builtins.open')` (breaks the harness); patching one arm's module (frozen and current are distinct module objects, each with its own globals) |

Load mechanism (observed):
- `install-links-grid.py` l.61–65 and `unpinnable-e2e.py` l.58 build `types.ModuleType` and `exec` the source into it.
- `controls.py` l.444–446 uses `module_from_spec` + `exec_module`.
- None of them registers the module in `sys.modules`.
- Consequence: a string target such as `patch('kama_live_under_test.sha256_file')` goes through `pkgutil.resolve_name`, which imports by name. It would fail or bind a different module. Use `patch.object(<module object>, ...)` only.

## Mistake-mining for Matrix / MatrixMutation / ApiFix

1. **Vacuous green.** If ApiFix moves enumeration to `os.scandir` or `Path.iterdir`, a `listdir` patch never fires and the current arm "refuses nothing" for an untested reason. Each cell MUST assert the injected mock was called with the target path (`call_count > 0`, or `assert_any_call(path)`). Otherwise the cell reports exit 2 (unavailable), never 0 or 1.
2. **Red-before must use exceptions the frozen code swallows.**
   - Frozen `install_tree` catches only `OSError` (l.186, 192, 198).
   - Inject `OSError` subclasses: `PermissionError`, `FileNotFoundError`, `OSError(errno.EIO, ...)`.
   - A `ValueError` or `RuntimeError` would escape the frozen arm and could be miscounted as refusal.
   - Count as refusal only `SetupError` with `'install-tree-unpinnable'`. Count as escape a returned `(tree, digest)` with a missing member, or `digest is None` from the listdir path (l.187).
3. **Frozen listdir failure returns `({}, None)`, not a digest.** "Comparable partial digest" escapes only through the lstat and read cells. Under the C1 wording ("exception is not empty map or null digest"), the listdir cell still violates, but by a null identity rather than a partial one. The matrix should label the two escape kinds separately.
4. **Positive control.** With no patch active, the exact regular-file map and combined digest (l.200–201) must equal the pinned values in both arms. Symlinks and non-regular entries stay excluded (l.194). This catches an ApiFix that refuses on symlinks.
5. **Patch lifetime.** Use `with patch.object(...)` per cell, or `addCleanup(p.stop)`. `start()` without `stop()` leaks the fault into later cells (docs §patch methods: start and stop, Caution).

## Remaining unknowns

- Whether `tempfile`/`shutil.rmtree` in 3.14.8 call `os.listdir` or `os.lstat` during harness cleanup [INFERENCE: `rmtree` uses `os.scandir`/`os.lstat`]. The path-keyed wrapper makes this moot.
- ApiFix's final enumeration primitive. If it changes, the lookup-site table must follow it, and rule 1 enforces that.

## Tooling

No installs or updates.
