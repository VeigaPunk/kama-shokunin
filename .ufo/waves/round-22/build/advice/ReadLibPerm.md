# ReadLibPerm — discriminating C1 case: library `sha256_file` PermissionError

Scope: design only, no code edits, no runs. All line numbers cite frozen blob
`10271460cc575fc2280aa831e442726385fc2319:tools/kama-llamacpp-live.py` unless marked
[wt] = current lane working tree (dirty, uncommitted — see Verification gaps).

## The ONE case

**`member-read-permission:libllama.so.0.7.0`** — a regular library member lstats
fine but its `sha256_file` read raises `PermissionError`. This exercises the
member-read failure leg (the `open()` inside `sha256_file`), distinct from
listdir/lstat legs owned by sibling reviewers.

### Fixture (temporary tree)

| name | kind | role |
|---|---|---|
| `llama-server` | regular file | `server_real` arg; also a hashed member |
| `libggml-base.so.0.27.0` | regular file | surviving member (non-trivial partial) |
| `libllama.so.0.7.0` | regular file | **fault target** |
| `libllama.so` | symlink → `libllama.so.0.7.0` | symlink-semantics sentinel |

Two surviving regular members are deliberate: a single-member partial (`{}` or
1-entry map) is still comparable, but a 2-of-3 partial makes "comparable partial
digest" vivid — the resulting `tree_sha` equals what a genuinely smaller release
directory would produce (silent downgrade, not detectable downstream).

### Smallest injection target

`unittest.mock.patch.object(mod, 'sha256_file', side_effect=guarded)` where
`mod` is the per-arm module object and:

```python
real = mod.sha256_file
def guarded(path, *a, **k):
    if os.path.basename(path) == 'libllama.so.0.7.0':
        raise PermissionError(13, 'Permission denied', path)
    return real(path, *a, **k)
```

Why this layer and not others:

- `sha256_file` is the exact member-read boundary named by the claim; frozen
  swallows it at line 197→199 (`except OSError: continue`), [wt] converts it at
  199→200 (`raise SetupError('install-tree-unpinnable:read:{name}')`).
- `builtins.open`/`io.open` is overbroad — injects into harness/module internals
  (`install_links`'s `os.readlink` is fine but tempfile/traceback/import paths
  are not) and misrepresents the fault site (claim says sha256_file).
- `os.lstat`/`os.listdir` target the sibling failure legs, not member-read.
- `hashlib.sha256` is the wrong error type/location entirely.
- Key on `basename`, not `==` full path: `install_tree` builds `full` via
  `os.path.join(os.path.dirname(server_real), name)` (frozen 189–190) — basename
  is collision-free inside one tmpdir and immune to path-construction drift.
- `PermissionError` ⊂ `OSError`, so it lands precisely on both arms'
  `except OSError` (frozen 198 / [wt] 199).

### Loading discipline

`importlib.util.spec_from_file_location` per arm → distinct module objects;
module is import-safe (stdlib-only imports, `__main__` guard at tail).
**Bind the patch to each arm's own `mod`** — `install_tree` resolves
`sha256_file` through its module globals at call time (frozen 197).

## Expected classes

| arm | expected | verdict |
|---|---|---|
| `frozen` | returns `(partial_tree, hex_sha)` — target absent, `sha` non-None well-formed, `partial_tree == {llama-server: h0, libggml-base.so.0.27.0: hA}` | **violation → exit 1** (red) |
| `current` | raises `SetupError` with `exc.code == 'install-tree-unpinnable:read:libllama.so.0.7.0'` (prefix `install-tree-unpinnable` per ApiFix contract) | refusal → green |
| `current` any **non-`SetupError`** exception | producer maps only `SetupError` → `receipt['setup_error']` (frozen 1602–1603); a raw `PermissionError` escapes that channel | **violation → exit 1** |

Positive control (unarmed or never-firing mock, e.g. key `no-such-member`):
`install_tree` returns all 3 regular members (symlink excluded) and
`sha == tree_sha(map)` recomputed independently via the formula already in
`install-tree-grid.py:39-41`. **Identical expected digest on both arms** —
pins population, expected outcomes, digests; proves the frozen red is property,
not harness noise.

Precision control: fault keyed to symlink name `libllama.so` → both arms skip
at the `S_ISREG` gate (frozen 195 / [wt] 195) before hashing → clean on both.
Preserves claim's "existing symlink semantics" and proves member-read targeting.

## False-positive risks (must design around)

1. **E2E masking — the dominant risk.** Measuring producer receipt/exit instead
   of the `install_tree` return makes frozen *appear* to refuse:
   `install_links(server_real, tree)` flags the missing member as
   `libllama.so.0.7.0:not-hashed` (frozen 258–259) → `link_problems` non-empty →
   `SetupError('install-tree-unpinnable:…')` (frozen 1417–1419). The frozen
   defect is only observable at unit level. **Assert on `install_tree`'s
   return/raise directly; e2e rows cannot discriminate this case.**
2. **Real `chmod(0)` injection is host-dependent** — root/`CAP_DAC_OVERRIDE`
   reads anyway. The frozen selftest already concedes this: it asserts the
   unreadable-member path only under `if not os.access(lib, os.R_OK)`
   (frozen 1191–1194, `os.chmod(lib, 0)` at 1192). Spec forbids host-permission
   dependence → mock only.
3. **Double masking with real chmod**: under real unreadability frozen
   `install_links` flags `:unreadable` (frozen 256–257) before `:not-hashed` —
   another layer that would hide unit-level partial escape at e2e.
4. **Non-SetupError refusal on current arm** — if ApiFix leaks `PermissionError`
   instead of `SetupError`, the producer's `except SetupError` (frozen 1602)
   won't catch it. Count any non-`SetupError` raise as violated; do not accept
   "it raised something" as fail-closed.
5. **Module-identity slip** — patching `sys.modules` or a shared alias misses;
   each arm's module object needs its own `patch.object`.
6. **Digest-inequality detection** — detect violation by *member missing from
   returned map with non-None combined digest*, not `partial_sha != full_sha`.
   The claim is "comparable partial digest": `tree_sha(partial)` is exactly the
   digest of a smaller legitimate install set — that equality is the proof of
   comparability, so assert it rather than mere inequality.
7. **`server_real` placement** — fixture's `llama-server` must live in the same
   tmpdir; `install_tree` enumerates `dirname(server_real)` (frozen 184). Do not
   point `server_real` outside the fixture tree.

## Source line references (frozen blob)

- `sha256_file` 171–176; real fault site `open(path,'rb')` 173.
- `install_tree` 178–203; defect pair: `tree[name] = sha256_file(full)` 197 /
  `except OSError: continue` 198–199. (`listdir` swallow 185–187, `lstat`
  swallow 190–194 — sibling legs.)
- `S_ISREG` skip (symlink/dir policy) 195–196.
- `install_links` backstops: `:unreadable` 256–257, `:not-hashed` 258–259.
- Producer: `install_tree` call 1414; `install_links(server_real, tree)`
  1415–1416; `link_problems` → `SetupError('install-tree-unpinnable:…')`
  1417–1419; receipt fields `'install_tree'` 1431 / `'install_tree_sha256'`
  1432; `except SetupError` → `receipt['setup_error'] = exc.code` 1602–1603.
- Frozen selftest host-dependent precedent: `os.chmod(lib, 0)` 1192, guarded
  `os.access` assertion 1194.
- [wt] fail-closed reference: `raise SetupError('install-tree-unpinnable:'
  'read:{name}')` at working-tree 199–200 (`:listdir` 187–188, `:lstat:{name}`
  193–194).

## Owned paths

- Report (this file, append-only):
  `.ufo/waves/round-22/build/advice/ReadLibPerm.md`
- No production/test file ownership — design advice for `Matrix`
  (`tests/llamacpp-live/install-io-grid.py`) only.

## Verification gaps

- Lane working tree `tools/kama-llamacpp-live.py` is **dirty vs HEAD 1027146**
  (uncommitted fail-closed patch, provenance unknown). Matrix's `--arm current`
  MUST load ApiFix's sandbox clone at
  `.ufo/waves/round-22/build/sandboxes/<ApiFix-seat>/tools/kama-llamacpp-live.py`,
  never the lane checkout or a HEAD extract — the dirty file may not equal the
  integrated patch.
- `--arm frozen` must load a `git show 1027146:tools/kama-llamacpp-live.py`
  extract, not HEAD-of-clone if ApiFix's clone carries uncommitted edits —
  clone-then-extract-blob is safest.
- `exc.code` exact suffix (`:read:libllama.so.0.7.0`) is ApiFix's design point;
  Matrix should accept prefix `install-tree-unpinnable` and record the full code
  rather than over-pinning the suffix.
- No runs performed this wave (per contract); classes are derived from the
  frozen/current source diff, not execution.
