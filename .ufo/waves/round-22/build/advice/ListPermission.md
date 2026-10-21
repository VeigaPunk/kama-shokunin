# ListPermission — the one discriminating C1 case: `listdir PermissionError` (round 22, C1)

Seat: KamaR22.ListPermission (read-only scout). Owned path: this file only
(`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/build/advice/ListPermission.md`).
No code edits, no verification runs, no installs. Line numbers are from the frozen blob
(sha256-verified) and the in-flight worktree, both cited below; the worktree was observed
changing under ApiFix twice during this read, so function-name anchors outrank line numbers.

## The case (canonical cell)

- **Fixture**: fresh `TemporaryDirectory` dir `D` containing `llama-server` + `lib.so`
  regular members (`tests/llamacpp-live/install-io-grid.py` `BODY`, :41). At least one
  regular member is required — see "empty-dir trap" under FP risks.
- **Fault**: `os.listdir(D)` raises `PermissionError` exactly once, only for path `D`.
- **Unit under test**: `module.install_tree(str(D / 'llama-server'))` — unit scope, not the
  producer. Reason below.
- **Frozen expected class** = escape, specifically *null-identity* (not a comparable partial
  digest): returns `({}, None)` — `except OSError: return tree, None` at frozen
  `tools/kama-llamacpp-live.py:186-187`. `tree == {}` despite the directory holding real
  members; `digest is None`. Every member's pin is dropped silently.
- **Current expected class** = refusal: `SetupError` (the producer's own class, caught as
  `module.SetupError`, not generic `Exception`) whose `.code` **starts with**
  `install-tree-unpinnable`. Observed ApiFix code at worktree :188 raises
  `'install-tree-unpinnable:listdir:' + (exc.strerror or type(exc).__name__)` — the
  contract pins only the `install-tree-unpinnable` prefix; assert the prefix, record the
  stage token `listdir` separately (see FP-4).
- **Positive control**: same `D`, no fault → both arms return the identical
  `({name: sha256(member-bytes)}, sha256(''.join(f'{n} {h}\n' ...)))` tuple (frozen digest
  formula at :200-201, reproduced by `expected_tree` in the grid, :55-58). A second control
  dir with one symlink + one subdir must yield the same digest as the regular-only dir —
  this is what catches an ApiFix that "fixes" C1 by refusing on symlinks/nonregular entries
  (`S_ISREG` skip at :195 preserved, semantics owned by `install_links`).

## Why unit scope is mandatory — producer scope cannot discriminate this fault

Frozen producer path (`git show 1027146…:tools/kama-llamacpp-live.py`, sha256
`cec679495591cf2410334dfe08c648e310f23825181dcbae7d13b911c980e023` — matches Matrix's
`FROZEN_SHA` pin at `install-io-grid.py:24`):

1. `install_tree(server_real)` at producer :1414 — listdir fault → returns `({}, None)`.
2. `install_links(server_real, tree)` at :1415 — then does its **own**
   `os.listdir(directory)` (frozen :232-234):
   - **Unguarded injection** (`os.listdir` fails for everyone): `install_links` hits its own
     except → `problems = ['listdir:' + exc.strerror]` → frozen producer raises
     `SetupError('install-tree-unpinnable:listdir:…')` at :1417-1419 — **byte-identical
     class to current**. No discrimination.
   - **Path-guarded injection that fails only install_tree's call** (call-count or
     first-call guard): `install_links`'s listdir succeeds, iterates the real regular
     members, finds them `not in tree` → `'{name}:not-hashed'` (frozen :259-260) →
     `SetupError('install-tree-unpinnable:llama-server:not-hashed;…')` — still a refusal.
3. The **only** producer-level escape corner: a directory whose every member is
   non-regular (symlinks/subdirs only) — `not-hashed` never fires because no regular member
   is seen. That is a vacuous identity, not the "comparable partial digest" C1 names, and
   an unrealistic install tree. [INFERENCE] Not worth a cell.
4. Same conclusion at member level: frozen lstat/read `continue` drops a member →
   `install_links` sees it, `os.access(R_OK)` passes (frozen :257-260) → `not-hashed` →
   refusal. The cross-check backstops the producer path for **every** injected OSError at
   the consumer boundary — which is precisely why the discriminating oracle for C1 is the
   `install_tree` unit, and why Matrix's `paired_problems` field (:130-132, calling
   `install_links` *after* patch teardown) is the right way to report that backstop
   without letting it mask the unit escape. CallE2E F2 already established the e2e script
   gives no red/green signal for C1; this note pins the mechanism for the listdir cell.

## Smallest sufficient injection target

`patch.object(module.os, 'listdir', listing)` — `module.os` is the shared `os` module
object (both producer copies do `import os`), so this is process-wide in effect, but safe
because **all three** of these hold (Matrix draft `observe()`, :61-133, implements each):

1. **Path guard**: wrapper raises only when `os.fspath(path) == os.fspath(folder)` and
   delegates to the captured real `os.listdir` otherwise (:69-74).
2. **Lifetime**: patch lives only inside `with ExitStack` around the single
   `install_tree` call (:115-121); `install_links` runs after stack exit (:130-132), so it
   never sees the fault.
3. **Reach proof**: `calls['fault']` must equal exactly 1 (:146 `fault_not_reached` →
   exit 2). This is what keeps the cell honest if ApiFix ever switches to
   `os.scandir`/`Path.iterdir`: the guard misses, the cell reports could-not-evaluate,
   never a silent pass (SrcScandir F2/SrcMock mistake-1).

`PermissionError` is the right exception: a mapped `OSError` subclass that frozen's
`except OSError` (:186) swallows. Inject the 3-arg form
`PermissionError(errno.EACCES, os.strerror(errno.EACCES), str(D))` — a bare
`PermissionError('injected fixture failure')` leaves `strerror=None`, which only survives
because ApiFix currently falls back to `type(exc).__name__`; the 3-arg form is what a real
`EACCES` looks like and keeps the cell meaningful if reason text is ever graded
(SrcExceptions mistake-3). Draft currently injects the bare form (:67) — cosmetic delta,
not a defect.

## Expected-class table (what "escape vs refusal" means here)

| Arm | listdir PermissionError | Counter bucket |
|---|---|---|
| frozen | returns `({}, None)` | escape — *null-identity* (`digest is None`) |
| current | `SetupError` code `install-tree-unpinnable[:…]` | refusal |

Two distinct escape kinds exist across the C1 matrix and must not be conflated:
`null_results` (listdir cell: `({}, None)`) vs `partial_digests` (lstat/read cells:
`({subset}, <valid-looking sha>)`). The draft counts them separately (:194-197) — correct;
a "comparable partial digest" claim would be *under*-stated if a listdir escape were
counted as a digest.

## False-positive risks (all observed, with refs)

- **FP-1 Producer-scope injection (dominant).** Any cell that injects through the producer
  or through `install_links`'s scan sees refusal on **both** arms (frozen :232-234,
  :259-260 → :1417-1419). A "green" producer-level row proves nothing about C1.
- **FP-2 Unguarded global patch.** `patch('os.listdir', side_effect=…)` without the path
  guard also breaks `install_links` (:232), `/proc/{pid}/fd` scans (:444) and harness
  `shutil`/`tempfile` internals [INFERENCE: rmtree uses scandir, not listdir — the guard
  makes this moot]. Draft guards correctly.
- **FP-3 `chmod 0o000` real-permission fault.** Euid-dependent (root bypasses
  `open`/`listdir` checks): the "no real host permissions" contract forces mock injection.
  SourceReject and CallE2E F4 cover this; applies identically to the listdir cell — a
  chmod-0 dir also fails `install_links`'s own listdir, so even when it fires it is the
  FP-1 non-discriminating shape.
- **FP-4 Token over-pinning.** Draft `expected_reason` (:149-152) requires
  `install-tree-unpinnable:<stage>:` **with a trailing detail**. The assignment contract
  names `SetupError('install-tree-unpinnable')`; a bare
  `raise SetupError('install-tree-unpinnable') from exc` (or `from None`) would be
  contract-conforming yet red. [INFERENCE] Deliberate strictness forcing ApiFix's detail
  suffix is defensible — but the refusal predicate should floor at
  `code.startswith('install-tree-unpinnable')`, with stage attribution and
  `cause_is_fault` (:125, `exc.__cause__ is injected`) as separate, recorded assertions.
  Note `from None`/bare-`raise`-inside-except would fail `cause_is_fault` while still
  refusing — a known-strict, not a bug.
- **FP-5 Empty-dir ambiguity.** `({}, None)` is only provably an escape because the fixture
  has members; the 'empty' control (:39, expects `({}, sha256(b''))`) is what makes
  `digest is None` unambiguous. Do not drop that control — it is the load-bearing
  negative for this cell.
- **FP-6 `fault != 1` strictness vs retries.** An implementation that retries `listdir`
  once and completes would produce a *complete* identity yet fail the cell
  (fault==1 + status returned → not refused → violation). Contract requires refusal on
  enumeration failure; flag as known-strict, not a defect.
- **FP-7 Path equality.** Guard compares `os.fspath` strings; if a future implementation
  `realpath`s the directory before `listdir` and `$TMPDIR` traverses a symlink, the guard
  misses → `fault_not_reached` → exit 2. Safe direction (never a false pass); hardening
  option is comparing `os.path.realpath` of both sides.
- **FP-8 Frozen-arm loading.** Must be `git show FROZEN:tools/kama-llamacpp-live.py` —
  *not* `HEAD` (worktree is dirty under ApiFix; observed `M tools/kama-llamacpp-live.py`
  mid-wave). Draft pins `FROZEN` (:23) **and** verifies `FROZEN_SHA` (:24, :209-210 →
  exit 2 on mismatch). Verified independently: blob sha256 = `cec67949…e023`. Correct.
- **FP-9 Module identity.** Frozen and current are distinct `types.ModuleType` objects
  (:48-52); `patch.object(module, 'sha256_file')` applies per-arm, but
  `patch.object(module.os, …)` is global — safe only because of FP-2's guard+lifetime.

## Alignment with observed Matrix draft (`tests/llamacpp-live/install-io-grid.py`, untracked, in-flight)

The `list-permission` cell already exists as specified: `FAULTS` entry
`('list-permission', 'listdir', None, 'permission')` (:28), injected through `listing()`
(:69-74) inside the scoped `ExitStack` (:115-121), graded refused-only-with-cause
(:149-155), and selftest fixture `list-refusal-deleted` (:244) reproduces the frozen shape
expecting exit 1. Remaining deltas worth a Matrix report line: (a) FP-4 refusal predicate
floor; (b) 3-arg `PermissionError` realism; (c) optional `list-enotdir`
(`NotADirectoryError`, `dirname` not a directory — a fourth listdir-class fault in the
`ERRORS` table sense, since `ENOTDIR` maps to its own subclass).

## Exact source references

Frozen `10271460cc575fc2280aa831e442726385fc2319` (= `master` = `HEAD` at write time),
`tools/kama-llamacpp-live.py` — `install_tree` :178-202 (listdir try/except :184-187,
lstat skip :190-193, `S_ISREG` skip :194-195, read skip :196-199, combined digest
:200-201); `install_links` :213-263 (own listdir problems :231-234, `not-hashed` :259-260);
producer call :1414-1419; `except SetupError → receipt['setup_error']` :1602-1603.
Current worktree (ApiFix, volatile): `install_tree` :178-203 with raises at :188-189
(listdir), :194-196 (lstat), :200-202 (read) — re-read before citing numbers downstream.

## Owned paths

- Written: this file only.
- Read: `tools/kama-llamacpp-live.py` (worktree + frozen blob), `tests/llamacpp-live/
  install-io-grid.py`, `install-links-grid.py`, `install-tree-grid.py`, `controls.py`,
  `unpinnable-e2e.py`, sibling advice `SrcMock`/`SrcOsLstat`/`SrcScandir`/`SrcExceptions`/
  `SourceReject`/`CallE2E`.

## Tooling

None installed or updated.
