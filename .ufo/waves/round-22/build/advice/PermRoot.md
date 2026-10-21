# PermRoot — root/nonroot-independent permission faults for install_tree (round 22, C1)

Seat: KamaR22.PermRoot (read-only advice). Owned path: this file only.
No verification runs; no installs; no host permission changes.

## Verdict

Use deterministic `unittest.mock` fault injection at the exact call sites
`install_tree` uses (`os.listdir`, `os.lstat`, the module-global
`sha256_file`, optionally a module-scoped `open`). An unprivileged child
process is **not needed** and is rejected (see "Rejected alternative").
Every `chmod 0`-based fault in the lane is root-sensitive today.

## Observed facts

- Host session: uid 1000, `CapEff`/`CapPrm` = 0, `/proc/self/uid_map`
  `0 0 4294967295` (initial user namespace). `master` = `HEAD` =
  `10271460cc575fc2280aa831e442726385fc2319`.
- The lane working tree is **not** clean against base. It already contains an
  uncommitted fail-closed `install_tree` in `tools/kama-llamacpp-live.py`
  (raises `SetupError('install-tree-unpinnable:listdir')`,
  `...:lstat:<name>`, `...:read:<name>`, `from exc`), and an
  `identity()` change in `tests/llamacpp-live/install-links-grid.py` that
  maps current-arm `SetupError` to `problems=[exc.code]` with null digests.
  I did not write these; treat them as the user's/L1's state.
- Base `install_tree` (`tools/kama-llamacpp-live.py:178-202` at base):
  listdir failure returns `({}, None)`; lstat and `sha256_file` `OSError`
  are `continue` (partial map + comparable digest).
- `sha256_file` is resolved via module globals and uses builtin `open`
  (`:171-176`). Frozen and current producers are loaded with `exec` into
  separate `types.ModuleType` objects (`install-links-grid.py:61-85`), so
  each arm has its own `sha256_file` global, but both share the one
  process-wide `os` module.

## Root-sensitive sites (exact)

1. `tests/llamacpp-live/install-links-grid.py:169-170`, cell
   `regular-unreadable` (`os.chmod(d / regular[-1], 0)`).
   As root (CAP_DAC_OVERRIDE), the read still succeeds and mode bits are
   not part of any digest, so both arms report `changed=False` while
   `expect_change=True`. That puts the cell in `wrong`, and `run` exits 1.
   The selftest check `controls-both-arms` (`:340-342`, which expects
   `regular` changed == 3) also FAILs, because the count becomes 2. As
   nonroot, the base frozen arm drops the member (changed), and the lane's
   current arm refuses (changed+refused). The cell's red/green therefore
   depends on euid. Owner: CallerRepair.
2. `tools/kama-llamacpp-live.py:1191-1198`, `_install_identity_selftest`.
   The `if not os.access(lib, os.R_OK) and ...` guard makes the
   `:unreadable` assertion **vacuous** under root: it is skipped silently,
   not failed. The lane draft adds no selftest of the new `install_tree`
   refusal. Owner: ApiFix.
3. `tests/llamacpp-live/unpinnable-e2e.py` has no permission dependence
   today. Do not add a chmod-based case there.
4. Real-kernel listdir/lstat EACCES needs a non-searchable or non-readable
   directory. Root bypasses both, so every permission-based fault for all
   three failure points is root-vacuous. The only alternative that does not
   depend on permissions is an ENOENT race (a member vanishes between
   `listdir` and `lstat`/`open`), and that is not deterministic without a
   mock either.

## Proposed deterministic mock (draft for Matrix / CallerRepair / ApiFix)

```python
import errno, os
from unittest import mock

def _selective(real, victim, err):
    def fake(path, *a, **k):
        if os.fspath(path) == victim:
            fake.fired += 1
            raise OSError(err, os.strerror(err), victim)
        return real(path, *a, **k)
    fake.fired = 0
    return fake

def run_fault(module, server, kind, victim_name, err=errno.EACCES):
    d = os.path.dirname(server)
    if kind == 'listdir':
        fake = _selective(os.listdir, d, err)
        ctx = mock.patch('os.listdir', fake)          # shared os module
    elif kind == 'lstat':
        fake = _selective(os.lstat, os.path.join(d, victim_name), err)
        ctx = mock.patch('os.lstat', fake)
    elif kind == 'read':
        fake = _selective(module.sha256_file, os.path.join(d, victim_name), err)
        ctx = mock.patch.object(module, 'sha256_file', fake)  # per arm
    with ctx:                                          # scope: one call only
        try:
            out = ('returned', module.install_tree(server))
        except module.SetupError as exc:
            out = ('refused', exc.code)
    if fake.fired == 0:
        raise EvalError(f'{kind} fault did not fire')  # exit 2, never green
    return out
```

Constraints the mock must keep:

- **Exact-path selectivity, tight scope.** `os.lstat`/`os.listdir` are
  process-global, and `tempfile`, `shutil.rmtree` and `os.path.realpath`
  call them too. Patch only around the single `install_tree` call. Never
  hold the patch across fixture setup or `TemporaryDirectory` cleanup.
- **Fired guard is mandatory.** If ApiFix moves to `os.scandir` or
  `DirEntry.stat()`, a listdir or lstat patch would silently not fire and
  the cell would look green. Zero fires must count as unavailable (exit 2).
- **Patch `sha256_file` per module object**, once for the frozen blob and
  once for the current module. Patching `os` reaches both arms; patching
  one module's global does not.
- Optional mid-stream read fault, which exercises the real chunk loop:
  `mock.patch.object(module, 'open', create=True, new=fake_open)`. Here
  `fake_open` wraps the real file and raises `OSError(EIO)` on the 2nd
  `read()` call, which is the EOF read, so it works for any member size.
  The patch is module-scoped because global lookup finds the module
  attribute before `builtins.open`.
- Errno matrix: `EACCES` (permission), `ENOENT` (vanish race), `EIO`
  (media). All three are host-independent.
- Expected outcomes. Frozen: listdir gives `({}, None)`, which counts as
  escape (null digest, not a refusal). lstat and read give the tree minus
  the victim, with a digest equal to the sha256 over the remaining sorted
  `name sha\n` lines; pin it from fixed fixture bytes. Current: refused with
  a code starting `install-tree-unpinnable:`. Positive control (no fault):
  the frozen and current tuples are identical and equal to a pinned map and
  digest.

### Site-specific recommendations

- **CallerRepair, `install-links-grid.py`.** Turn `regular-unreadable`
  into a fault cell: no chmod. Run `identity()` for that cell under
  `run_fault`-style `sha256_file` patching, applied per arm module, with the
  victim `regular[-1]`. Then the frozen arm is changed (member dropped), the
  current arm is changed+refused, and `controls-both-arms` == 3 under any
  euid. The cleanup loop `:239-243` (`chmod 0o755`) appears to exist only
  for the chmod-0 cell [INFERENCE]. Once no chmod-0 remains, delete it.
- **ApiFix, producer selftest.** Replace the `os.access` guard at
  `:1191-1198` with a deterministic case. Use
  `mock.patch('os.access', side_effect=lambda p, m, real=os.access: False if p == lib else real(p, m))`
  so that `install_links(server)[2] == ['libllama.so.0.7.0:unreadable']`
  holds as root too. Add one refusal assertion per `install_tree` failure
  point via `mock.patch.dict(globals(), {'sha256_file': failing})` and
  selective `os.listdir`/`os.lstat`. Inside the producer, `__name__` is
  `'__main__'` when run as a script, so patch `globals()` rather than a
  module path string.
- **unpinnable-e2e.py.** Do not add a permission case. In-process grids
  already cover refusal. A subprocess cannot inherit a mock without a
  bespoke loader shim.

## Rejected alternative: unprivileged child

- As root, it needs `setuid` to drop to nobody plus `chown` of the temp
  tree. `TemporaryDirectory` is mode 0700 and owned by root, so the child
  fails at traversal: the wrong fault, at listdir instead of the victim.
- As nonroot, a process cannot drop privileges, so it would need a second
  code path, which is not deterministic.
- `unshare -r` maps the caller to uid 0 with CAP_DAC_OVERRIDE over files
  it owns, so the bypass persists.
- ACLs and `chattr` need privilege or host filesystem features.

Conclusion: the child process adds root-only machinery and still cannot
produce per-member read faults. Use the mock only.

## Remaining unknowns

- Whether L1 accepts the lane's uncommitted draft as ApiFix's result, or
  whether it is stray. The source of those edits was not determined.
- What the final `SetupError` code granularity will be (`:listdir`,
  `:lstat:<name>`, `:read:<name>` in the lane draft). Grids should assert
  the prefix `install-tree-unpinnable:` plus the fault kind, not full
  strings with errno text.

## Proposed checks (for L1, after integration)

- `python3 tests/llamacpp-live/install-io-grid.py --selftest`, then
  `--arm both --json`. Expect frozen=1 (escape) and current=0, run once as
  uid 1000 and once under `sudo -n` [no host perms changed].
- `python3 tests/llamacpp-live/install-links-grid.py --selftest`, as both
  nonroot and root. `controls-both-arms` must pass under both.
- `python3 tools/kama-llamacpp-live.py --selftest` (or the producer's
  selftest entry), as both nonroot and root.

Installs: none.
