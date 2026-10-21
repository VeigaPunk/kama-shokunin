# ListMissing — discriminating C1 case: `listdir` FileNotFoundError

Read-only reviewer. Owned path: this report only
(`.ufo/waves/round-22/build/advice/ListMissing.md`). Lane root:
`/home/vgpnk/Projects/shokunin/kama-shokunin`. No code edits, no runs.

## Source evidence (verified at both revisions)

Frozen `10271460cc575fc2280aa831e442726385fc2319` (`git show` blob),
`tools/kama-llamacpp-live.py`:

- L178 `def install_tree(server_real)`
- L185 `entries = sorted(os.listdir(directory))`
- L186 `except OSError:` → L187 `return tree, None` — **the injected fault
  lands here; returns `({}, None)`, a value not a refusal**
- L192 `except OSError:` → `continue` (silent lstat skip)
- L198 `except OSError:` → `continue` (silent read skip → comparable
  partial digest, the core C1 gap)
- L200–202 `combined = hashlib.sha256('name sha\n' lines)`;
  `return tree, combined`
- Consumers in frozen blob: selftest L1135/L1157; producer L1414
  `tree, tree_sha = install_tree(server_real)`; receipt records
  `install_tree_sha256` at L1432; `except SetupError` →
  `receipt['setup_error']` at L1602.

Current worktree (already carries the ApiFix-shaped change; uncommitted
`M tools/kama-llamacpp-live.py`):

- L185–188 `try: entries = sorted(os.listdir(directory)) / except OSError
  as exc: raise SetupError('install-tree-unpinnable:listdir') from exc`
- L191–194 lstat → `SetupError(f'install-tree-unpinnable:lstat:{name}')`
- L197–200 read → `SetupError(f'install-tree-unpinnable:read:{name}')`
- Producer L1415–1420: `install_tree` → `install_links` →
  `if link_problems: raise SetupError('install-tree-unpinnable:' …)`;
  catch L1603–1604 `except SetupError as exc:
  receipt['setup_error'] = exc.code` → outcome `setup-error`, exit 2
  (L1785). Symlink semantics unchanged (L195 `S_ISREG` skip identical).

Round-21 `FROZEN_REV 7a6bc911…` has the *identical* silent-skip body, so
the discriminating contrast holds under either pin — but Matrix MUST pin
`FROZEN_REV = "10271460cc575fc2280aa831e442726385fc2319"` (declared base),
not reuse the round-21 constant in `tests/llamacpp-live/install-links-grid.py`
L49.

## The ONE case: `listdir-missing` (FNFE on directory enumeration)

**Why this cell discriminates.** Enumeration is the gatekeeper: both
revisions execute `sorted(os.listdir(directory))` at the same source line
(frozen L185 / current L186) — one injection coordinate exercises both
blobs. Frozen swallows the `OSError` and returns `({}, None)`; current
raises `SetupError('install-tree-unpinnable:listdir')`. `FileNotFoundError`
(errno ENOENT, `os.strerror` = "No such file or directory") is the natural
instance: the install directory vanishing between the producer's
`os.path.isfile(server_real)` check and enumeration. It is disjoint from
the permission lane (EACCES → ListPermission) and from member-level lanes
(lstat ENOENT → StatGone; read → ReadGone).

**Why a unit-level cell and not e2e.** Producer-level, a persistent
listdir failure is *already* refused in frozen code: `install_links`
(frozen L232–234) independently calls `listdir` and returns a `problems`
entry → `SetupError` at frozen L1417. The frozen escape is real only at
the function contract (`({}, None)` propagates into
`receipt.server.install_tree{,_sha256}` where `None` reads as "unpinned",
not "refused") and for direct/selftest callers. So the grid cell must call
`install_tree` directly and classify the *return-versus-raise* — do not
route this cell through the producer.

## Injection (smallest precise target)

```python
target_dir = os.path.dirname(server)          # str; listdir sees dirname(server_real)
real_listdir = os.listdir
def fake_listdir(path):
    if os.path.realpath(path) == os.path.realpath(target_dir):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
    return real_listdir(path)
with unittest.mock.patch.object(mod.os, 'listdir', fake_listdir):
    result = call_install_tree(mod, server)   # capture return OR exception
```

- Patch the module's `os` attribute (`mock.patch.object(mod.os, 'listdir',
  …)`), not a name inside `install_tree` — the module does `import os`
  (L34), so `mod.os` *is* `os`; the wrapper's arg match keeps the fault
  precise to the one directory and delegates everything else.
- Match on `realpath(arg) == realpath(target_dir)` to stay correct under
  symlinked tmpdir components (`/tmp` may be a link).
- Both revisions pass `directory` (str) to `listdir`; pass `server` as a
  `str` path so `os.path.dirname` yields str and the match is literal.

## Fixture + positive control (same temp tree)

Temp dir members: `llama-server` (`b'server-stub\n'`),
`libllama.so.0.7.0` (`b'lib-0.7.0\n'`), `libllama.so.0.7.1`
(`b'lib-0.7.1\n'`), plus symlink `libllama.so.0 -> libllama.so.0.7.0`
(the round's preserved symlink semantics).

Control row (unpatched, both arms):
- `tree == {name: hashlib.sha256(body).hexdigest() for name, body in
  members.items()}` — exact membership {3 regular files}, symlink absent
  (proves intentional-skip preserved, not a new failure).
- `combined == hashlib.sha256(''.join(f'{n} {tree[n]}\n' for n in
  sorted(tree)).encode()).hexdigest()` — recompute via the documented
  formula (same independent code path as `tree_sha()` in
  `install-tree-grid.py` L39–41); assert `combined is not None` and
  `len(combined) == 64`.

Fault row (patched), per arm:

| arm | pinned `expected` | discriminating signal |
|---|---|---|
| frozen | `escaped` | returns `({}, None)`; `tree_sha is None` recorded |
| current | `refused` | `SetupError` raised; `exc.code ==
  'install-tree-unpinnable:listdir'`; `isinstance(exc.__cause__,
  FileNotFoundError)` and `exc.__cause__.errno == errno.ENOENT` (chains
  the injected fault — proves the refusal is this injection, not drift) |

`escaped` = function returned a value (incomplete identity escaping);
`refused` = `SetupError`; any other exception class = `error`
(could-not-evaluate, never conflate with escape).

## Exit semantics (recommended to Matrix)

Contract: `0 clean, 1 violated property, 2 unavailable`. Literal reading:
exit **1 iff any armed row escaped** (the C1 property is "no incomplete
identity escapes"); exit **2** on load failure, fixture failure, or an
unexpected exception class; else 0. Consequence: `--arm frozen` → 1,
`--arm current` → 0, `--arm both` → 1; the red-before/green-after
contrast lives in per-row `expected`/`observed` in `--json`, not in one
ambiguous exit code. (`--selftest` asserts the same contrast in-process.)
Alternative — exit 0 when `observed == expected` per arm — hides the
frozen violation behind a pass; AVOID.

## Conventions to reuse (from `install-links-grid.py`, same dir)

- `LANE = Path(__file__).resolve().parents[2]`, `PRODUCER =
  "tools/kama-llamacpp-live.py"` (L46–47)
- `load_source(name, source, path)` exec-based loader, no `__pycache__`
  (L61–65); distinct module names `frozen_producer`/`current_producer` —
  top-level is import-safe (constants only; `SCRIPT` resolves via
  `__file__`).
- `frozen_producer()`: `git -C LANE show <REV>:tools/…` → `EvalError` on
  nonzero (L68–76); `current_producer()` reads `LANE/PRODUCER` (L79–85).
- `EvalError` → exit 2 for could-not-evaluate (L57–58); `--arm
  current|frozen|both`, `--json`, `--selftest` already the established
  CLI shape.

## False-positive risks

1. **Patch leakage / cross-arm contamination**: `mod.os is os` — always
   restore via context manager before the next arm's call; never hold two
   patches.
2. **Arg-match miss**: `listdir` receives `dirname(server_real)`, not
   `server_real`; matching on the file path would inject nothing and fake
   a "refused"/"clean" result. Match the directory (realpath-compared).
3. **Wrong errno**: `FileNotFoundError()` with no args has `errno=None`;
   pin `errno=ENOENT` and assert `__cause__.errno == ENOENT`, else a
   bare-OSError raise could mask errno-specific handling.
4. **Weak positive control**: asserting only "no exception" would pass if
   `install_tree` silently dropped members. Pin exact member set, per-file
   digests, combined digest, and symlink absence.
5. **Classification conflation**: a `SetupError` whose `__cause__` is not
   the injected `FileNotFoundError` is NOT this cell's refusal — classify
   `error`, not `refused`.
6. **Frozen-baseline misread**: a frozen refusal (arm frozen → refused)
   means the wrong blob loaded → exit 2, never count as pass.
7. **Import side effects**: exec the blob under a private module name;
   `module.__file__` must be set (loader does this) since `SCRIPT` resolves
   at import — cosmetic only, `install_tree` never touches it.
8. **`PermissionError` bleed**: keep this cell strictly ENOENT; an
   `os.chmod(dir, 0)` injection belongs to ListPermission's lane and would
   be host-permission-dependent (contract forbids).
9. **Real-deletion variant**: `shutil.rmtree(dir)` before the call also
   yields ENOENT — valid fallback that needs no mock, but mutates the
   fixture (control must run first or use a second tree) and conflates
   with producer-level TOCTOU. Mock injection is primary; if used, note it
   exercises identical semantics.
10. **Stale frozen pin**: reusing round-21 `FROZEN_REV 7a6bc911…` produces
    the same behavior but the wrong pinned base — cite risk only, update
    to `10271460…`.

## Coordination notes for peers

- **Matrix** (`tests/llamacpp-live/install-io-grid.py`, its clone): the
  `current` arm in a fresh `--shared` clone sees **frozen** behavior —
  the fix lives only in ApiFix's sandbox/uncommitted lane worktree. Grid
  selftest will honestly report `current=escaped` until integration;
  document this so the red result is not misread as a defect.
- **CallerRepair** (`install-links-grid.py`, `unpinnable-e2e.py`): e2e
  expectations unchanged by this cell — producer already refused
  persistent listdir failure via `install_links` problems (frozen
  L232–234 + L1417); the e2e `install-tree-unpinnable:` prefix assertions
  remain correct. Frozen install_links listdir branch stays a
  `problems` entry (`listdir:{strerror}`), not a raise — do not expect
  `SetupError` from `install_links` itself.
- **Producer selftest gap**: `_install_identity_selftest`
  (current L1119–1199) exercises `install_links` problems but **no**
  `install_tree` failure path — the io-grid is the only red/green
  evidence for enumeration failure. No selftest edit needed; the grid
  carries the claim.

## Residual risk

- `install_tree` returning `({}, None)` under frozen is *distinguished*
  from a genuine empty directory only by `tree_sha is None`; the grid
  records `tree_sha is None` explicitly so the receipt-level ambiguity
  (None = unpinned vs refused) is documented, not silently equated.
- Case covers directory-gone only; lstat-mid-listing ENOENT (member
  deleted between listdir and lstat) is StatGone's lane — do not
  duplicate it here.

## Verification gaps (none run — build wave)

- No execution performed; all behavior claims are source-derived at the
  two cited revisions (frozen blob via `git show`, current via worktree
  read at lines cited).
- Exact `SetupError` message text (`'install-tree-unpinnable:listdir'`)
  verified at current L188; if ApiFix's final clone differs in suffix
  detail, the `exc.code.startswith('install-tree-unpinnable')` plus
  `__cause__` assertions still discriminate — recommend Matrix pin exact
  code but tolerate suffix drift via the cause check.
