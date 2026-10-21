# StatLibPerm — discriminating C1 matrix case: `os.lstat` PermissionError on a library member

Seat: KamaR22.StatLibPerm (reviewer, read-only). Owned path: this file only.
Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`. No code edits, no runs, no installs.

Working-tree note: `tools/kama-llamacpp-live.py` and `tests/llamacpp-live/install-io-grid.py`
changed mid-review (uncommitted fail-closed draft + newer L1 grid). Line refs below cite the
frozen blob `10271460` (stable, via `git show`) and the current working tree as of this
writing; suffix format drifted twice, so oracle wording is stated as semantics, not literals.

## The ONE case

**`stat-lib.so-permission`**: `os.lstat(<dir>/lib.so)` raises `PermissionError` exactly
once, inside `install_tree` — a *regular file, non-server* member.

Lane grid row: `tests/llamacpp-live/install-io-grid.py:29-31` builds `('stat-lib.so-permission',
'lstat', 'lib.so', 'permission')` from `ERRORS['permission']=PermissionError` (:25).
Older sandbox copy (`.ufo/waves/round-22/build/sandboxes/Matrix/...`) names the same row
`lstat:library:permission` — same cell, two generations; treat the lane file as canonical.

Why this member and not the server (`stat-llama-server-permission`): the server has an
independent pin — receipt `server.sha256` from `sha256_file(server_real)` (frozen :1413)
is separately re-derived, and the gate requires `install_tree[basename]` to equal it
(check-receipt.py ~:249). A dropped server is partially masked by downstream evidence; a
dropped library exists *only* in the tree. The library case is the cleanest demonstration
that the partial digest is *indistinguishable* from a complete one.

Why `lstat` and not `listdir`: frozen `listdir` failure returns `({}, None)` (frozen
:186-187) — a null digest, trivially incomparable. Only `lstat`/`read` cells produce the
contract phrase "**comparable partial digest**": non-null, self-consistent, sorts into any
digest comparison as a valid-looking identity. `PermissionError` (not `FileNotFoundError`)
models the steady-state EACCES case (e.g. directory mode 0400: listdir succeeds on the read
bit, lstat/open fail on the missing search bit) rather than a vanish race.

## Expected classes

- **Frozen (red-before)**: `os.lstat` OSError → `continue` (frozen :192-193). Returns
  `({'llama-server': <sha>}, <digest>)` — map missing `lib.so`, digest **non-null and
  self-consistent** = `sha256("llama-server <sha>\n")`. With this report's fixture
  (`b"server\x00"`-style bodies): for `llama-server: ba28c4bd…f31`, partial digest =
  `48bb849fadd4a44da75548e83d2bbf0bd1a533800b17357f6bcb4db76bb5f716` (recomputed now).
  The grid counts any `status='returned'` fault row as a violation — correct; I recommend
  additionally pinning the *expected* escape tuple so a frozen return of wrong kind (e.g.
  `(tree, None)` here, or missing the wrong member) is a distinct finding, not the same red.
- **Current (green-after)**: `except OSError as exc: raise SetupError(...) from exc`
  (working tree :194-196). Refusal class = `SetupError` whose `.code` starts
  `install-tree-unpinnable:lstat:` and names the member (`{name!r}` → `'lib.so'`), with
  `__cause__` the injected instance. `except SetupError → exit 2` in `main` (:1606 area).
- **Escape-class boundary**: e2e this fault does *not* discriminate — frozen `main` still
  refuses via the `install_links(server_real, tree)` backstop (`{name}:not-hashed`, frozen
  :258 → raise at :1417-1419; and a persistent lstat fault also lands as
  `f'{name}:{exc.strerror}'` problems at :260-261). **The producer-boundary (`install_tree`
  return/raise) is the only surface where frozen red and current green differ** — which is
  precisely C1's claim. The lane grid already records this honestly: `paired_problems`
  (install-io-grid.py:130-132) runs `install_links` *after* the ExitStack unwinds, so it
  observes the unpatched `lib.so:not-hashed` backstop separately from the unit escape.

## Smallest injection target

`patch.object(module.os, 'lstat', new=stated)` where `stated` raises the pre-built
`PermissionError` iff `os.fspath(path) == os.fspath(folder/'lib.so')`, else delegates to the
captured real `os.lstat` — as implemented at install-io-grid.py:76-80, 117.

- Producer lookup is `os.lstat(full)` — a call-time attribute on the shared `os` module
  (frozen :191; current :193). `patch.object(module.os, 'lstat')` is the correct site;
  `patch.object(module, 'lstat', create=True)` would never fire (no `module.lstat` lookup).
- One-shot counting wrapper (`calls['fault']`, :64/78) + `result['fault'] != 1 →
  RuntimeError('fault_not_reached')` (:143) is mandatory: if ApiFix migrates to
  `os.scandir`/`DirEntry`, the patch silently never fires → exit 2, never false-green.
  Mistake to mine: `DirEntry.stat()` defaults `follow_symlinks=True` — a scandir rewrite
  would also break intentional symlink skip; the `control-symlink`/`control-directory`
  rows (CONTROLS :39-40) catch that regression for free.
- Scope: `with ExitStack` (:115-119) patches four sites but the predicates gate on
  `stage`, so only the lstat wrapper fires; `install_links` in `paired_problems` runs
  unpatched (:130-132). Keep the patch inside the `with`; never across fixture
  setup/teardown (`shutil.rmtree`/`tempfile` call `os.lstat` themselves).
- Exception shape: `PermissionError('injected fixture failure')` (:67). Single-arg →
  `exc.strerror is None` → current code `(exc.strerror or type(exc).__name__)` yields
  `…:lstat:'lib.so':PermissionError` — deterministic, path-free. `PermissionError` is an
  `OSError` subclass, so frozen's `except OSError` swallows it; a non-OSError would escape
  frozen raw and be misclassified as refusal — keep injection in the OSError family.

## Positive control

`control-regular` (CONTROLS :39): unpatched `install_tree` on the same fixture must return
`expected_tree(BODY)` — exact map and digest — on **both** arms, `fault == 0`. Companion
`control-symlink`/`control-directory`/`control-fifo` pin the preserved skip semantics
(intentional nonregular omissions are not refusals). These are what make the fault cell
*discriminating* rather than just red.

## False-positive risks (ranked)

1. **Oracle suffix drift.** Producer code format changed twice this wave
   (`…:lstat:{name}` → `…:lstat:{name}:{exc}` → `…:lstat:{name!r}:{exc.strerror or type}`).
   The lane grid's `startswith(expected_reason + ':')` (:149-152) must not tighten to exact
   equality, and must tolerate the repr quoting. Contract's literal `SetupError(
   'install-tree-unpinnable')` is satisfied by the suffixed subtype; an exact-match oracle
   would report a correct producer as a violation.
2. **Chaining assumption.** `cause_is_fault` (:125) requires `raise … from exc`. If ApiFix
   drops `from`, a correct refusal scores `passed=False` — arguably intentional (provenance
   requirement), but should be a named expectation, not an accident.
3. **Patch-site confusion.** `patch.object(module.os, 'lstat')` patches the process-global
   `os` for the `with` window — any concurrent in-process use sees the fault. The
   path-exact predicate confines it; a name-substring predicate (`'lib' in path`) would
   also hit `libllama.so.0` symlinks' stat calls and miscount `calls['fault']`.
4. **Mock-not-firing green** (covered above): guaranteed exit 2 via `fault_not_reached`;
   never allow `calls['fault']==0` to reach the refused/escaped classifier.
5. **Member choice.** Failing `lstat` on a symlink or on `llama-server` is weaker: symlink
   lstat failure frozen-skips an entry that would be skipped anyway (no identity change →
   non-discriminating); server-victim is masked by the independent `server.sha256` pin.
6. **Frozen-arm oracle symmetry.** The same `evaluate` runs both arms; frozen "red" must be
   asserted as *escape of the right shape* (partial map + consistent non-null digest),
   not merely `not passed`. A frozen `({}, None)` return would also be `passed=False` but
   is a different defect class.
7. **Tuple shape.** `tree, digest = module.install_tree(...)` (:121): a 3-tuple return or
   raising non-SetupError → 'raised'/ValueError → violation, not silent pass. Fine, but
   label the distinction in row output.

## Residual risk / gaps for L1

- Unit-boundary discrimination only; frozen e2e refuses through `install_links` for both
  persistent and transient faults. If C1 wants e2e red evidence, it must come from a fault
  `install_links` cannot see (none in this fault family) — accept unit-level as canonical.
- The two `install-io-grid.py` generations (lane vs `sandboxes/Matrix`) diverge: lane copy
  has richer rows (`late-read`, `PROPAGATION`, subtype oracle + selftest fixtures
  `stat-refusal-deleted` etc.) — confirm L1 integrates the lane copy and drops the sandbox one.
- `_install_identity_selftest` (producer :1122+) still asserts only `install_links`
  problems, not `install_tree` refusal — ApiFix gap, flagged by PermRoot.

## Proposed checks (not run this wave)

- `python3 tests/llamacpp-live/install-io-grid.py --arm both --json` → frozen exit 1 with
  `stat-lib.so-permission` returned-escape; current exit 0 all fault rows refused.
- `python3 tests/llamacpp-live/install-io-grid.py --selftest` → 0 (`stat-refusal-deleted`
  fixture proves the lstat arm of the oracle).
- Repeat under `sudo -n` to prove euid-independence (all faults are mock-injected).
