# StatServerPerm — C1 matrix case design: `lstat(server_real)` PermissionError

Owned path: `.ufo/waves/round-22/build/advice/StatServerPerm.md` (this file).
Scope: design only; no code edits, no runs. Lane root
`/home/vgpnk/Projects/shokunin/kama-shokunin`. Pinned base
`master=10271460cc575fc2280aa831e442726385fc2319`.

## Case definition (the ONE case)

Inject `PermissionError(errno.EACCES, 'Permission denied')` at `os.lstat`,
armed for **the server binary entry itself** — `os.path.join(dirname(server_real), basename(server_real))` — inside a temporary install tree:
`llama-server` + ≥1 real regular lib (distinct bytes) + 1 dangling/benign soname
symlink + (optional) 1 subdirectory.

- `full = os.path.join(directory, name)` is a `str` join: call
  `install_tree(str(server))` (or compare via `os.fspath`) so the armed path
  matches a str exactly.
- Construct the error with `(errno, strerror)` so `.strerror` is populated —
  the current implementation interpolates `exc.strerror`; a bare
  `PermissionError()` would still refuse but changes the token suffix to the
  type name. Realism keeps the diagnostic pin exact.

## Expected classes (red-before / green-after)

| arm | expected outcome | evidence |
|---|---|---|
| frozen | `escaped-partial` — returns `(tree, combined)` with `combined != None` and server basename **absent** from `tree` | base `tools/kama-llamacpp-live.py` install_tree: `except OSError: continue` on the `st = os.lstat(full)` arm (git-show of pinned base: ~lines 190-193). The map is a strict subset yet the digest is well-formed: a comparable-but-incomplete identity. |
| current | `refused-setup-error` — `SetupError` propagates; `exc.code` starts `install-tree-unpinnable` | working tree `#AF80`: `raise SetupError(f'install-tree-unpinnable:lstat:{name!r}:' + (exc.strerror or type(exc).__name__)) from exc` at lines 193-195. Note `{name!r}` — the token contains the *repr* of the name; an exact pin is `install-tree-unpinnable:lstat:'llama-server':Permission denied`. |

Outcome enum recommendation for the grid: `escaped-partial` / `escaped-null` /
`refused-setup-error` / `refused-other` / `control-mismatch`. Do **not** test
violation by `combined is None` — that arm is listdir-failure, a different case.
Violation = partial `tree` + non-None `combined`. Refusal = `SetupError` from
the *same module object* that ran (the two module loads define distinct
`SetupError` classes; catch `mod.SetupError` per arm).

## Smallest injection target

`mock.patch('os.lstat', autospec/side_effect=fn)` where `fn(path, *a, **kw)`
raises only when `os.fspath(path) == server_full_str`, else calls the saved
original. Patch must wrap **only the `install_tree()` call** (not tree setup,
not `install_links`, not cleanup). `os.lstat` is global, so scope the `with:`
to the single call. Do not inject via a fake `os` module — `install_tree` binds
`os` at module import of `posix`/`nt`; a scoped patch of `os.lstat` reaches it.

Wrong-target traps: patching `os.stat`/`Path.stat`/`Path.is_file`/
`Path.read_bytes`/`producer.sha256_file`/`builtins.open` never fires the lstat
arm — on frozen the call returns full-identity and the case vacuously reads
green.

## Positive control

Same temporary tree, same module object, unpatched call:

- `(tree2, combined2)` must equal a **locally recomputed** map/digest
  (reimplement `sha256` + `f'{n} {sha}\n'` sorted-join in the grid — do not
  reuse `producer.sha256_file`, so producer regressions in hashing stay
  observable), and identical across both arms — proves successful
  regular-file map/digest preserved byte-for-byte.
- `basename(server)` ∈ `tree2`; symlink/subdir entries absent from `tree2`
  (symlink-skip semantics preserved). Include the symlink in the fixture so the
  control proves intentional-skips still skip on the *current* arm.

## Why this case discriminates

1. **Maximal semantic loss on frozen**: the dropped entry is the served binary
   itself — the artifact the identity exists to pin. A partial digest missing
   `llama-server` is the worst-comparable escape.
2. **Arm attribution is exact**: lstat precedes the `S_ISREG` check and the
   read arm; the refusal can only come from the lstat branch. Token pins
   `:lstat:` separately from `:read:`/`:listdir:` (distinct sibling cases).
3. **No host permission dependence**: pure mock, no chmod/uid games — satisfies
   "no real host permissions dependency".

## False-positive / masking risks

- **CRITICAL — e2e masking (affects CallerRepair's unpinnable-e2e.py)**:
  `install_links` (base lines ~244-261) already catches `OSError` from its own
  `os.lstat` into `problems`, and frozen `main()` turns `link_problems` into
  `SetupError('install-tree-unpinnable:...')`. So a *subprocess/e2e* run with
  lstat-permission refused is refused on **both** arms: the defect is invisible
  end-to-end for this injection. The matrix MUST call `install_tree` unit-level
  and inspect its return; an e2e-only cell for this case proves nothing.
- Corollary: token shapes differ by layer — unit `install_tree` refuses with
  `install-tree-unpinnable:lstat:'llama-server':Permission denied`, while an
  `install_links`-caught failure inside frozen main yields
  `install-tree-unpinnable:llama-server:Permission denied` (no `:lstat:`).
  Never accept the latter as evidence the install_tree fix fired.
- **Frozen must be the pinned blob**, not a copied working file: load via
  `git show 10271460cc575fc2280aa831e442726385fc2319:tools/kama-llamacpp-live.py`
  (exec/importlib into a fresh module namespace), and self-check that the
  frozen source lacks `install-tree-unpinnable` while the current contains it —
  if both sources are identical the matrix is vacuous. (Observed state: the
  lane working file is ` M` and already carries the fix; an arm that reads the
  working file twice yields false green.)
- `sorted(os.listdir)` order is irrelevant — the patch is path-keyed — but a
  patch keyed on `name` instead of the joined `full` never fires.
- `PermissionError` is an `OSError` subclass, so both arms route it through the
  `except OSError` clauses; don't arm `IOError`/`FileNotFoundError` (the latter
  is a different reviewer case — StatGone).
- `exc.code` lives on `SetupError.code` (line ~157-160); `str(exc)` also gives
  the token, but assert `code.startswith('install-tree-unpinnable')` for
  robustness against `__str__` changes.
- Keep the armed `PermissionError` instance raised fresh per call (or one
  instance is fine; `from exc` chaining doesn't mutate it) — either way the
  refusal path is deterministic because listdir always precedes lstat and the
  server name is sorted with the rest; no ordering dependence.

## Line references (as observed this wave)

- Frozen `install_tree` (git-show of pinned base): lstat arm `except OSError:
  continue` ~L190-193; read arm `continue` ~L196-199; listdir arm returns
  `(tree, None)` ~L184-187.
- Current `install_tree` `#AF80`: function L178-203; listdir→SetupError
  L184-188; **lstat→SetupError L190-195**; read→SetupError L197-200;
  combined digest L201-202.
- `install_links` OSError→problems (both versions): ~L244-261; main() glue:
  `install_links(server_real, tree)` and `link_problems`→SetupError ~L1416-1420;
  `except SetupError` → `receipt['setup_error']` ~L1603-1604 (exit 2 path).
- `SetupError`/`code`: L154-160.

## Hand-off to Matrix (install-io-grid.py)

Row contract for this case: `id: lstat-server-perm`, `inject: os.lstat`,
`armed_path: server_real`, `frozen_expect: escaped-partial`,
`current_expect: refused-setup-error` (+ optional `code_prefix:
'install-tree-unpinnable:lstat:'`), positive control row as above. Exit codes
stay per interface (0 clean / 1 violated / 2 unavailable); count
`escaped-partial` as the "incomplete identity escaping" bucket.

No installs performed (none needed; stdlib `unittest.mock` suffices).
Tooling directive: pacman untouched, per RULES.md.
