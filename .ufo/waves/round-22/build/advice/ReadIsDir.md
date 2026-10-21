# ReadIsDir — the ONE discriminating C1 case: member `sha256_file` IsADirectoryError

Lane root: `/home/vgpnk/Projects/shokunin/kama-shokunin` (base `master=10271460cc575fc2280aa831e442726385fc2319`).
Advice only; no code edits, no runs. Owned path: this file.

## ⚠ Lane integrity flag (for L1/Main, not actionable by me)

`tools/kama-llamacpp-live.py` in the **lane checkout** was mutated mid-wave
(mtime 2026-10-21 10:05:45 -0300, uncommitted `git diff HEAD`): `install_tree`
was rewritten fail-closed in place (listdir→`install-tree-unpinnable:listdir:…`,
lstat→`…:lstat:{name!r}:…`, read→`…:read:{name!r}:…`). That violates
"never mutate lane checkout; every code writer gets its own sandbox clone" and
poisons any grid that loads "current" from the lane file. install-io-grid.py
MUST load the current arm from an explicit producer path (ApiFix's sandbox
clone), e.g. `--producer <path>` defaulting to a supplied sandbox path — never
implicitly from `LANE/tools/…`.

## Frozen semantics (base blob 10271460, `tools/kama-llamacpp-live.py`)

- L171-176 `sha256_file(path)`: `open(path,'rb')` at L173 → IsADirectoryError is an `OSError`.
- L185-187 `os.listdir` fails → `return tree, None` (`({}, None)` — the *only* null-digest escape; not comparable).
- L191-193 `os.lstat` fails → `continue` (silent member skip).
- L194 `stat.S_ISREG` gate: a real directory can never reach `sha256_file` —
  IsADirectoryError there is only reachable via a **lstat→open rename race**
  (regular file swapped for a directory) or by injection. This is exactly why
  the case needs `unittest.mock`, and why it is non-redundant with every
  permission-based case (PermissionError is realizable without mocks; EISDIR is not).
- L196-199 `sha256_file` fails → `except OSError: continue` — **the silent
  member-read skip**. Map stays self-consistent.
- L200-201 `combined = sha256(''.join(f'{n} {tree[n]}\n' for n in sorted(tree)))`
  — a partial map still yields a valid, comparable 64-hex `install_tree_sha256`.
  This digest-comparability is the C1 defect: the receipt pins a *smaller*
  identity with a perfectly good-looking digest.
- Consumer net (why you MUST isolate): producer L1413-1419 calls
  `install_tree` then `install_links(server_real, tree)`; base install_links
  L258-259 turns a missing member into `{name}:not-hashed` → producer
  `SetupError('install-tree-unpinnable:…')`. So an **end-to-end** run already
  fails closed even with the frozen `install_tree` — e2e green tells you
  nothing about the install_tree defect. `unpinnable-e2e.py` can never
  exercise this arm. Call `mod.install_tree(...)` directly (precedent:
  `unpinnable-e2e.py` L74, `install-links-grid.py` L179).
- Producer catch L1602-1603: `SetupError` → `receipt['setup_error']=exc.code`,
  exit 2. A `SetupError` raised *inside* install_tree is already caught.

## The case

- **Population** (temp dir, no permission tricks, contract-clean):
  `llama-server` (regular), `libllama.so.0.7.0` (regular),
  `libmtmd.so.0.4.0` (**victim**, regular), plus symlink
  `libllama.so -> libllama.so.0.7.0` and subdir `licensing/` for the control.
  Victim is a sort-middle name (sorted order puts two members before it and
  `llama-server` after) so the frozen map provably skips one member while
  still hashing members after it — a genuine partial, not a truncation.
  `server_real = <dir>/llama-server`; it is hashed as a member like the rest.
- **Smallest injection target**: `unittest.mock.patch.object(mod, 'sha256_file', wrapper)`
  — one module-global attribute (install_tree calls the module global, so the
  patch lands regardless of `mod.__name__`). `wrapper(path)`: on first call
  whose `os.path.basename(path) == VICTIM`, set `fired=True` and raise
  `IsADirectoryError(errno.EISDIR, os.strerror(errno.EISDIR), str(path))`;
  otherwise delegate to the real `mod.sha256_file`. All three args so
  `exc.strerror == 'Is a directory'` deterministically (see risk d).
- **Expected outcomes** (exit 0 = every row as expected; 1 = any `escaped-*`
  on green arm or contract-miss; 2 = load failure / armed-not-fired / internal):
  - `frozen` → `escaped-partial`: returns `(tree, sha)`; `VICTIM not in tree`;
    `len(tree) == 3`; `sha` is non-None 64-hex AND `sha ==` independent
    recomputation `sha256(''.join(f'{n} {tree[n]}\n'…))` — asserting
    self-consistency proves a *comparable* partial digest escaped, not a
    sentinel. `--arm frozen` must exit 1 (red before).
  - `current` → `refused-contract`: `mod.SetupError` raised, no return value,
    `exc.code` == `'install-tree-unpinnable'` or starts
    `'install-tree-unpinnable:'` (the live worktree shape is
    `install-tree-unpinnable:read:'libmtmd.so.0.4.0':Is a directory`). Green.
  - `escaped-null` = returned `({}, None)` or `sha is None` — distinct class,
    also a violation, do not fold into `refused`.
  - `refused-untyped` = non-`SetupError` raise (e.g. raw OSError escaping).
    Process-level still fail-closed but producer L1602 only maps `SetupError`
    into the receipt — report separately, not green for the token contract.
- **Positive control** (same population, zero injection): both arms return
  identical `(tree, sha)`; `tree` == `sha256` of each of the 4 regular files;
  symlink and subdir absent from the map; `sha` equals independent
  recomputation. Guards ApiFix regressions: wrongly-injected members,
  digest-formula drift, symlink/subdir semantics.
- **`--selftest`**: stub module where `sha256_file` raises for victim → assert
  classes `escaped-partial` (frozen stub) / `refused-contract` (current stub);
  stub where the fault never fires → exit 2 path.

## False-positive / false-negative risks

- **a) Masked by install_links** (top risk): arming the producer e2e makes the
  frozen arm green via `not-hashed` — destroys the red-before signal. Call
  `install_tree` in isolation. `install-links-grid.py` arms (link/subdir/
  regular/type/null) are a different claim; do not reuse its verdict logic.
- **b) Armed-but-never-fired → false green**: ApiFix may legitimately inline
  hashing (`open`+`hashlib` inside install_tree); then the `sha256_file`
  patch never fires and a fixed tree returns — looking exactly like a pass.
  Record `fired` + `mock.call_count == 1`; not-fired → exit 2
  (`armed_not_fired: true`), never a verdict. Fallback if ApiFix inlines:
  patch `os.lstat` to return an `os.stat_result` with `S_ISREG` mode for a
  real subdirectory named VICTIM — real `open()` then raises a genuine
  IsADirectoryError inside whatever hashing code exists (survives inlining,
  needs only a stat_result tuple + real mkdir).
- **c) Over-firing**: matching on full path only breaks under path
  normalization; matching on `basename == VICTIM` and firing once keeps the
  escape *partial* — raising for every member yields `({}, sha256(''))`, a
  different (empty-comparable) escape class.
- **d) Nondeterministic code text**: `IsADirectoryError()` without args leaves
  `exc.strerror = None`; the live impl's fallback uses `type(exc).__name__`.
  Always construct with `(errno.EISDIR, os.strerror(errno.EISDIR), path)`.
- **e) Counting `({}, None)` as refused**: it is `escaped-null`, a failure
  class (silent empty identity is arguably worse — downstream could compare a
  digest of nothing only if it recombines; `sha=None` is non-comparable but
  still silently incomplete). Keep classes separate so the JSON shows *which*
  escape died.
- **f) Frozen pin drift**: `install-links-grid.py` L49 pins
  `FROZEN_REV="7a6bc911…"` (round-21). Round-22 frozen MUST be
  `10271460cc575fc2280aa831e442726385fc2319` — pin the full hex, not HEAD.
- **g) `sys.exc_info` leakage**: classify on `type(exc)`/`exc.code`, not on
  message substrings other than the `install-tree-unpinnable` token prefix.
- **h) Control contamination**: run the positive control in the same tempdir
  *before* arming (or a second identical tempdir) so mock state never leaks
  into the control digest.

## Reuse

Loader/exec pattern: `install-links-grid.py` L61-85 (`load_source`,
`frozen_producer` via `git show <rev>:tools/kama-llamacpp-live.py`,
`current_producer` — repoint at `--producer`); docstring exit-code convention
L29-31 (0 clean / 1 violated / 2 could-not-evaluate). Independent digest
recompute: `install-tree-grid.py` L39-41 `tree_sha()`. CLI shape per
assignment: `--arm frozen|current|both`, `--json`, `--selftest`.

Suggested JSON row:

```json
{"case":"member-read-eisdir","victim":"libmtmd.so.0.4.0",
 "frozen":{"outcome":"escaped-partial","fired":true,
           "tree_missing":["libmtmd.so.0.4.0"],
           "sha_self_consistent":true},
 "current":{"outcome":"refused-contract","fired":true,
            "setup_error":"install-tree-unpinnable:read:'libmtmd.so.0.4.0':Is a directory"},
 "control":{"identical":true,"members":4,"symlink_skipped":true,"subdir_skipped":true}}
```

## Tooling

No installs this wave (pacman transactions paused host-wide; none needed —
stdlib only: `unittest.mock`, `errno`, `tempfile`, `hashlib`, `json`).
