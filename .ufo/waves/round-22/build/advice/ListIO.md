# ListIO — C1 matrix case: listdir generic OSError

Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Read-only seat; no edits, no runs, no installs (stdlib-only analysis; nothing to install).

## One-line design

Inject one plain `OSError` into `os.listdir` **at the `install_tree()` unit boundary** and classify the call outcome: frozen arm must return normally (escape), current arm must raise `SetupError` (refuse). This is the ONLY observation point where the two arms diverge for a listdir failure.

## Exact source references

Frozen blob `10271460cc575fc2280aa831e442726385fc2319:tools/kama-llamacpp-live.py`:

- L184-187 `try: entries = sorted(os.listdir(directory))` / `except OSError: return tree, None` → returns `({}, None)`. `None` digest is still recorded in the receipt (`install_tree_sha256: null`) next to a comparable empty map → silent partial identity. **Escape.**
- Sibling silent sites (context, other matrix rows): lstat L191-193 `except OSError: continue`; read L197-199 `except OSError: continue`.
- Frozen `install_links` backstop: L232-234 `except OSError as exc: return links, None, [f'listdir:{exc.strerror}'], unpinned`; L259 `'{name}:not-hashed'` when `tree` given and member absent.
- Frozen producer: L1414 `tree, tree_sha = install_tree(server_real)`, L1415-1419 `install_links` + `if link_problems: raise SetupError('install-tree-unpinnable:'...)`.

Current working tree `tools/kama-llamacpp-live.py` (ApiFix applied, ` M`):

- L178-203 `install_tree`; L185-188 `except OSError as exc: raise SetupError('install-tree-unpinnable:listdir') from exc` → **refuse**, exact token `install-tree-unpinnable:listdir`.
- Siblings: lstat L191-194 `install-tree-unpinnable:lstat:{name}`; read L197-200 `install-tree-unpinnable:read:{name}`; combined digest L201-203.
- `SetupError` L154-159 (`exc.code`); `import os` L34 — no module-local `listdir` binding, so patch target is `os.listdir` itself.
- Producer call site L1414-1419 unchanged; receipt gate L1417-1419.

## Why producer-level cannot discriminate (key constraint for Matrix)

With a real install dir (regular members present), every frozen producer-level escape path is already closed by `install_links`:

1. `listdir` fails for both calls → frozen `install_links` returns `['listdir:…']` → producer refuses (same as current).
2. `listdir` fails only inside `install_tree` (first-call/stateful mock) → `tree={}` → every regular member yields `{name}:not-hashed` → producer refuses.
3. Only a directory with zero regular files escapes frozen at producer level — degenerate, not the claim.

So the discriminating cell MUST call `mod.install_tree(str(server_real))` directly on each arm, not `main()`. Sibling rows (lstat-gone, read-perm/partial) share this reasoning.

## Expected classes

| arm | injection | expected | observable |
|---|---|---|---|
| frozen (`10271460`) | `os.listdir(dir)` → `OSError` | `escape` | returns `({}, None)` — any normal return under fault counts as escape |
| current (WT) | same | `refuse` | raises `SetupError` with `exc.code == 'install-tree-unpinnable:listdir'` |

## Smallest injection target

`unittest.mock.patch('os.listdir', side_effect=fn)` where `fn` raises `OSError(errno.EIO, os.strerror(errno.EIO))` iff `os.fspath(p) == directory` else `return _real(p)` (capture `_real = os.listdir` before entering the context). One patch context per arm call — identical injection, no cross-arm mock state. `errno.EIO` keeps it a *generic* `OSError` (not `PermissionError`/`FileNotFoundError` subclasses) while still giving a real `.strerror`.

Fixture: `tempfile.TemporaryDirectory` dir containing `llama-server` (regular), `libllama.so.0.7.0` (regular), `libllama.so → libllama.so.0.7.0` (symlink). `server_real = realpath(dir/'llama-server')`; `directory = dirname(server_real)`. Symlink member proves skip semantics are unchanged (asserted via the control's arm-equal map).

## Positive digest control

Per arm, unpatched call on the same fixture must return `(map, digest)` with:

- map == `{n: sha256_file-bytes for each regular member}` (2 entries; symlink absent), and
- digest == `sha256(''.join(f'{n} {sha}\n' for n in sorted(map)).encode()).hexdigest()` (formula mirrors install-tree-grid.py L39-41), and
- frozen digest == current digest — the `back_compat_install_tree_sha256_equal` invariant proven by install-links-grid.py L266-270.

Run controls before the injected call; a control mismatch means bad arm/rev pairing → exit 2 (unavailable), not 1.

## False-positive risks

1. **Refusal token too loose**: counting any `SetupError` as refuse would pass a wrong-site raise (`:lstat:`/`:read:`). Classify refuse ONLY on `exc.code == 'install-tree-unpinnable:listdir'`; other `SetupError` codes or non-`SetupError` exceptions → violated/error.
2. **Escape check too narrow**: comparing to literal `({}, None)` misses a future `({}, 'e3b0…')` regression. Under fault, ANY normal return = escape.
3. **Unfiltered global patch**: unconditional `side_effect=OSError` can break the grid's own tempfile/teardown and the control path → rc-2 noise or misread violation. Filter on target `directory` and assert the mock actually fired (call count ≥ 1 or flag captured in `fn`).
4. **Path type/realpath mismatch**: `os.listdir` receives the `str` dir; normalize both sides with `os.path.realpath`/`os.fspath` before comparing (tempdir symlink components).
5. **Frozen rev drift**: `install-links-grid.py` pins `FROZEN_REV = 7a6bc911…` (L49) — a DIFFERENT, older blob. The new io-grid must pin `10271460cc575fc2280aa831e442726385fc2319`; the silent `except OSError: return tree, None` shape is identical in both, but only `10271460` is the round-22 base.
6. **Producer-level misattribution**: running the injection through `main()`/subprocess cannot discriminate (backstop above) — a green producer run proves nothing about `install_tree`. Unit call only.
7. **Unexpected arm class**: if frozen refuses or current escapes, that is a violated property → exit 1 (not 2); reserve 2 for `git show` failure, exec/import failure, tempdir failure, missing `SetupError`/`install_tree` attrs.
8. **`sorted()` is not the fault site**: the raise must come from `os.listdir` itself; failing inside a wrapper that `sorted` calls changes the semantics being measured.

## Conventions to reuse (Matrix)

`install-links-grid.py`: `load_source` exec-loader L61-65 (sets `module.__file__`; producer top-level is stdlib imports + `Path` constants only, safe to exec); `frozen_producer` L68-76 (`git -C LANE show REV:path`); `EvalError`→exit-2 convention L57-59, L382-395; `--arm current|frozen|both`, `--json`, `--selftest` CLI L375-395. New file name per contract: `tests/llamacpp-live/install-io-grid.py` (Matrix-owned, separate clone).

## Owned path

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/build/advice/ListIO.md` (this report)
