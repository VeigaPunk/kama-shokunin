# StatGone — C1 discriminating case design: lstat member vanished (FileNotFoundError)

Scope: design only, no edits/runs. Owned path: this file. Lane root `/home/vgpnk/Projects/shokunin/kama-shokunin`; frozen blob `10271460cc575fc2280aa831e442726385fc2319`.

## The case

`lstat:vanished:missing` — a member name appears in `os.listdir(directory)` output but is gone by `os.lstat` time (TOCTOU between frozen line 185 and line 191). This is the only lstat-class fault whose frozen-arm escape is *unmaskable* by `install_links` (see FP-3).

### Expected class

- **Frozen (red): `escaped`, and the returned tuple equals the healthy control bit-for-bit.** Frozen `install_tree` (blob lines 190–193) does `except OSError: continue`; FileNotFoundError is an OSError subclass, the phantom is skipped, and the function returns `(EXPECTED_TREE, EXPECTED_TREE_SHA256)` — a *comparable* digest: identical to the digest the complete fixture produces, so a consumer pins a silently smaller identity that still matches itself on re-run. This is the exact axis7 harm.
- **Current (green): `refused`** — `SetupError` whose code carries `install-tree-unpinnable`, `__cause__` a genuine FileNotFoundError (errno ENOENT, `.filename` set by the kernel). Working-tree code raises at line 194 (`install-tree-unpinnable:lstat:{name}:{exc}`).

## Smallest injection target (ranked)

1. **Patch `module.os.listdir` only** — for the exact fixture-directory argument, return `original(path) + [PHANTOM]`; delegate all other paths. The phantom is never created on disk; the producer's own `sorted()` (frozen 185 / current 186) places it deterministically, and the *real* `os.lstat` raises a genuine ENOENT. One mock, one call site, kernel-produced errno, no permissions, no threads. This is strictly smaller and more faithful than mocking `lstat`, and it exercises both fault seams at once (listdir lies about existence; lstat exposes absence).
2. Patch `module.os.lstat` to raise `FileNotFoundError(ENOENT,…)` on an existing member — what Matrix sandbox rows 44/47 already do. Same function-level verdict, but fabricates the exception and is producer-level *masked* (FP-3); keep those rows for error-class coverage, do not let them substitute for the vanished row.
3. Rejected: real background-unlink race — nondeterministic activation, cannot meet the `injection["calls"] == 1` activation gate (sandbox line 180).

Phantom name: ASCII, absent from `MEMBER_BYTES` and control extras (`libllama.so.0`, `plugins/`), e.g. `'a0-vanished.so'` sorting first — also proves frozen continues hashing members *after* the skipped fault (skip-and-continue, not abort). Assert `not os.path.lexists(phantom_path)` in fixture setup.

## Positive control

Existing `control:complete-map-digest` (sandbox grid line 59) on the same fixture suffices and doubles as the comparability oracle: assert on the frozen arm that the vanished case's `result ==` that control's `(EXPECTED_TREE, EXPECTED_TREE_SHA256)` (pinned lines 29–37). Recommend recording `digest_matches_control: true` in the row so "comparable partial digest" is evidenced, not implied.

## False-positive risks

- **FP-1 (classification, highest):** sandbox `_observe` (line 130) requires `exc.code == "install-tree-unpinnable"` *exactly*; the current working-tree producer emits suffixed codes (`…:lstat:name:exc`, line 194). Every green-arm fault row then classifies `error`, not `refused` → `property_pass` False for the wrong reason (false red on green; cannot false-pass). Fix one side: producer emits the bare token per the shared interface, or grid classifies `code == token or code.startswith(token + ':')` (prefix-with-boundary preserves reason detail per the "subtype" discussion clause). Meanwhile the lane-root draft expects `repr(member)` (`install-tree-unpinnable:lstat:'lib.so':`, lane line 149–150) which the producer's raw `{name}` also fails — the two io-grid drafts disagree with each other; only one may integrate.
- **FP-2 (activation bookkeeping):** the vanished case injects at listdir but the ENOENT is raised by the kernel, not by `inject()` — adapt the `raised` counter (count listdir diversions == 1) or the activation gate at sandbox line 180 spuriously marks the row `injection-not-reached` → `error`. On the green arm optionally assert `exc.__cause__` is FileNotFoundError for cause-faithfulness (lane-draft's `cause_is_fault` idea, line 125).
- **FP-3 (end-to-end masking — why phantom, not lstat-mock):** a persistent lstat failure is caught by `install_links` even in the frozen producer: its own listdir (frozen 232) still yields the member, `os.lstat` fails → `{name}:No such file or directory` problem (frozen 260–261), or if lstat succeeds there but the member is absent from the map, `…:not-hashed` (frozen 258–259); producer then raises `SetupError('install-tree-unpinnable:…')` at frozen 1417–1419. So mock-lstat rows discriminate only at function level; the vanished member (absent from `install_links`' enumeration) is the sole lstat fault that escapes the frozen *pipeline* — the receipt-level discriminator.
- **FP-4 (os-module sharing):** `module.os` *is* the global `os` — the listdir patch must be path-guarded to the fixture dir string (`os.fspath(path) == str(directory)`) and confined to the `install_tree` call window, as existing rows already do (sandbox 152–157, 177–178); both armed modules share `os`, so arms must stay sequential (they are).
- **FP-5 (fixture hygiene):** phantom must never be created, must not equal the `server` arg basename, contain no `/` or control chars (those route to different problems, frozen 237–239), and must stay out of `EXPECTED_TREE`/digest pins. `os.listdir` injection affects only this directory — `install_links`' real enumeration never sees the phantom, which is exactly the vanish semantics.
- **FP-6 (wrong-fix detection):** a "fix" that skips only FileNotFoundError (`except FileNotFoundError: continue` before the OSError clause) fails this row on the green arm as `escaped` — the case discriminates partial fixes, not just frozen-vs-fixed.
- **FP-7 (sentinel vs partial):** don't conflate escapes. Frozen listdir failure returns `({}, None)` (frozen 186–187) — a *null* digest, not comparable; the lstat-vanished case returns a *full-shape comparable* tuple. Keep `null_results`/`partial_digests` accounting distinct (lane-draft lines 194–197 already separates them; sandbox uses `returned_identity` which counts both — acceptable since both are `escaped`, but the vanished row's `digest_matches_control` flag is what makes the axis7 claim).

## Source line references

Frozen blob `1027146:tools/kama-llamacpp-live.py`: install_tree 178–202; listdir fail→`({}, None)` 184–187; **member lstat `except OSError: continue` 190–193 (the fault line)**; read skip 196–199; combined digest 200–202. install_links 213–262 (own listdir 231–234, lstat 245, not-hashed 258–259, OSError→problem 260–261). Consumer 1414–1419 (tree 1414, links 1415–1416, SetupError 1417–1419). SetupError class 154–157+; receipt `setup_error` mapping 1603–1604.

Current working tree (dirty, may shift): install_tree 178–203; raises at 188 (listdir), **194 (lstat)**, 200 (read); docstring 179–182 states the fail-closed contract.

Authoritative grid draft (Matrix sandbox, 307 lines — supersedes the stale 263-line lane-root copy): `FAULT_CASES` 40–57 (lstat-missing rows 44, 47; no vanished row yet), `_make_fixture` 104–112, `_expected_exception` 115–122 (ENOENT at 118–119), `_observe`+token check 125–133, injector 136–198 (lstat branch 158–166), activation gate 180–186, controls 201–214, summary/`property_pass`/`baseline_red` 221–235.

## Integration notes

- Lane checkout is dirty (producer + `install-links-grid.py` + `unpinnable-e2e.py` modified, `install-io-grid.py` untracked) — edits appear to have landed in the lane root, not only in `sandboxes/ApiFix` (which does not exist under `build/sandboxes/`; only `sandboxes/Matrix` present). L1 should re-check clone discipline; my line refs for "current" are WT-relative and will drift.
- Recommended matrix row: `("lstat:vanished:missing", "vanished", "a0-vanished.so", FileNotFoundError)` with operation `"vanished"` implemented as the listdir-append patch; add as a 17th row rather than replacing rows 44/47 (they pin permission/EIO lstat coverage).
