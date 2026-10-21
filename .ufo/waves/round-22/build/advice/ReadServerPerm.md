# ReadServerPerm — discriminating C1 case: server `sha256_file` PermissionError

Seat: KamaR22.ReadServerPerm (read-only advice). Owned path: this file only.
No code edits, no runs, no installs. Line refs cite frozen blob
`10271460cc575fc2280aa831e442726385fc2319:tools/kama-llamacpp-live.py`
(sha256 `cec67949…c980e023`, verified) unless marked `[wt]` = dirty lane working tree.

## The ONE case

**`read-llama-server-permission`** — the `llama-server` member lstats fine
(`S_ISREG`) but its `sha256_file` read raises `PermissionError`. This is the
member-read failure leg at the *server* member, distinct from the library-member
variant (ReadLibPerm) and from the listdir/lstat legs (sibling seats).

Present in the Matrix draft population already as
`('read-llama-server-permission', 'read', 'llama-server', 'permission')` —
`install-io-grid.py` FAULTS, lane copy line 32–34 (read leg, member
`llama-server`, error `permission`).

Why the server member is the uniquely discriminating pick, not merely a variant:

1. **Identity incoherence.** Frozen producer computes `server.sha256` at
   producer-level `sha256_file(server_real)` (frozen 1413) *before*
   `install_tree` (frozen 1414). If the member read then fails, frozen
   `install_tree` returns a map **missing the binary it is supposed to pin**
   while `server.sha256` still records it — an internally incoherent identity.
   The library variant cannot produce this shape.
2. **Internal fault, not refusal, at e2e.** If the mock fails `sha256_file` for
   the server path *before* `install_tree` (i.e. at producer 1413), the raw
   `PermissionError` is **not** a `SetupError`: it lands in
   `except BaseException → _record_internal` (frozen 1606–1607). Both arms then
   show `internal:PermissionError` — *non-discriminating* (see FP risk 1).
3. **Double-hashing is real.** `llama-server` is hashed twice per producer run
   (1413 and inside `install_tree`); the member-read fault is the only site
   where the second hash can fail after the first succeeded — a TOCTOU-shaped
   window no other member has.
4. **Real-chmod e2e is impossible for this member.** `chmod 0` on the copied
   `llama-server` trips `server-not-executable` (frozen 1398–1399, since mode 0
   fails `os.access(X_OK)` depending on euid) *before* identity work — this case
   cannot be exercised by `unpinnable-e2e.py` at all. Mock-only.

### Fixture (temporary tree)

Minimum viable: `{llama-server, lib.so}` (Matrix draft BODY, line 41). Sorted
enumeration puts `lib.so` first, so a fault on `llama-server` yields the
nonempty partial `{lib.so: sha}`.

Sharper: Matrix's own earlier population `{llama-server, libllama.so.0.7.0}` —
`llama-server` sorts **last**, so the frozen partial contains every library.
Either way the escaped identity is non-trivially comparable.

## Smallest injection target

`patch.object(mod, 'sha256_file', guarded)` with a path-filtered dispatcher:

```python
def hashed(path):
    if os.fspath(path) == os.fspath(folder / 'llama-server'):
        calls['fault'] += 1
        raise injected            # PermissionError
    return original_hash(path)
```

This is exactly what the draft does (`hashed()`, install-io-grid.py 82–86,
installed at 118). Why this layer:

- `sha256_file` is the claim's named boundary; frozen swallows at
  `tree[name] = sha256_file(full)` 197 → `except OSError: continue` 198–199;
  [wt] converts at 199–202 (`raise SetupError('install-tree-unpinnable:read:'
  '{name!r}:…')`).
- `builtins.open` is one layer deeper than the claim and hits unrelated opens;
  `os.listdir`/`os.lstat` are sibling legs; `hashlib.sha256` is the wrong type.
- Path-keyed (not call-count): an unfiltered blanket mock would fire at
  producer `sha256_file(server_real)` 1413 in any in-process producer row —
  wrong site. Filtering makes the same mock safe for both unit and future
  producer rows.
- `PermissionError ⊂ OSError` lands on both arms' `except OSError`
  (frozen 198 / [wt] 201).
- Recommend `PermissionError(13, 'Permission denied', str(path))` over bare
  `PermissionError('injected fixture failure')` (draft line 67): sets
  `.errno`/`.strerror`, so impls that format `exc.strerror` — the [wt] code
  does `(exc.strerror or type(exc).__name__)` at 188–189/195–196/202–203 —
  behave exactly as under a real EPERM instead of falling to the class-name
  fallback. Cost: nothing.

## Expected classes

| arm | observable | verdict |
|---|---|---|
| `frozen` | `install_tree` **returns** `(partial_tree, hex_sha)`, `llama-server` absent, `digest == tree_sha(partial)` (recomputed via `expected_tree`) | **violation → exit 1 (red)** |
| `current` | `install_tree` **raises** `SetupError` with agreed token `install-tree-unpinnable` for this read failure | refusal → green |
| `current` | non-`SetupError` raise (raw `PermissionError`) | **violation** — producer catches only `SetupError` → `setup_error` (frozen 1602–1603); anything else is `internal:` |
| either | `fault != 1` | `RuntimeError('fault_not_reached')` → exit 2 (harness, never a verdict) |

Draft classification already implements this: `expected_reason` prefix + status
`refused` (lines 144–152); frozen gets identical expectations so its silent
return counts as a violation.

### Strengthened oracle for the red row (recommendation)

The draft records `result['tree']/['digest']` but only checks
`status=='refused'`. For the frozen arm's escape row additionally assert:

- `result['status'] == 'returned'` **and**
- `result['digest'] == expected_tree({k: v for k, v in BODY.items()
  if k != 'llama-server'})[1]` **and**
- `result['tree'] ==` that partial map.

This proves the escape is a *well-formed comparable* digest over the complete
surviving subset, not just a non-None value. In the Matrix sandbox population
(`MEMBER_BYTES`, `install-io-grid.py` 29–41), `llama-server` sorts after all
three libraries, so the failed server member leaves a 3-member partial map.
In the lane draft's smaller `{llama-server, lib.so}` population, the result is
the 1-member `{lib.so: sha}` partial map. Pin the exact map and recomputed
digest for whichever population is selected.

## False-positive risks

1. **PRODUCER/E2E MASKING — dominant.** Measuring producer exit/`setup_error`
   cannot discriminate this case:
   - If the mock fires at producer 1413 → `internal:PermissionError` on *both*
     arms (frozen 1606–1607) — frozen looks "safe" for the wrong reason.
   - If the mock fires only inside `install_tree` → frozen still refuses via
     `install_links`'s `not-hashed` (frozen 258–259) → `link_problems` →
     `SetupError('install-tree-unpinnable:…')` (frozen 1417–1419). Green-looking
     on frozen while the defect shipped.
   **Only the `install_tree` return/raise discriminates.** `unpinnable-e2e.py`
   and receipt checks are structurally blind to this case.
2. **REASON OVER-PINNING — live bug in lane draft.** It expects
   `'install-tree-unpinnable:read:llama-server:'` (install-io-grid.py 145–146),
   while dirty [wt] producer emits
   `install-tree-unpinnable:read:'llama-server':…` (`{name!r}`, [wt] 201–203).
   The exact string check false-fails the current arm. The shared contract
   specifies `SetupError('install-tree-unpinnable')`, so the grid need not
   require a site/member suffix. Worktree detail is a separate API choice;
   accept it only if ApiFix/L1 deliberately retains it as stable contract.
   Match the agreed token, never uncontracted quoting. The [wt] code mutated
   during review (non-`!r` → `!r`), further demonstrating this is unstable.
3. **Host-permission injection is invalid for this member.** Real `chmod(0)`
   on `llama-server` either fails `X_OK` early (1398–1399) or reads anyway
   under root/`CAP_DAC_OVERRIDE`; frozen selftest already guards its own
   chmod-0 assertion behind `if not os.access(lib, os.R_OK)` (frozen 1192–1195).
   Mock only — draft complies.
4. **Fault-not-firing silence.** Without `result['fault'] == 1` (draft 142–143)
   a path-key mismatch would classify 'returned' clean rows identically to a
   passing control — the guard converts this to exit 2. Keep it.
5. **Coincidental OSError.** The draft counts any caught `PermissionError` as
   the injected one for fault rows via `same_exception` only on the 'raised'
   path; a refusal that never saw the injected object is still blocked by
   `fault==1`. Residual: an impl swallowing-then-raising its own `SetupError`
   for an unrelated member would still pass — acceptable; the population pins
   the fixture as tiny.
6. **`os.fspath` equality** (draft 70/77/83/111) assumes `install_tree`'s
   `os.path.join(dirname(server_real), name)` (frozen 189–190) is string-equal
   to `folder/member`. True for real tmpdirs; breaks if `tempfile` ever yields
   a symlinked base or `install_tree` gains `realpath`. Low; acceptable.
7. **`except (InjectedInterrupt, Exception)`** (draft 125) won't catch
   `SystemExit`/`GeneratorExit` escapes — they propagate as harness errors →
   exit 2, not a silent green. Fine.

## Source line references

Frozen blob (`git show 1027146:…`, sha `cec67949…c980e023`):

- `SetupError` class: 154–159 (`.code` at 159).
- `sha256_file`: 171–176; real fault site `open(path,'rb')` 173.
- `install_tree`: 178–202; `dirname` 183; **defect pair** `tree[name] =
  sha256_file(full)` 197 / `except OSError: continue` 198–199.
- `install_links` backstops that mask e2e: `unreadable` 256–257,
  `not-hashed` 258–259.
- Producer: `sha256_file(server_real)` 1413; `install_tree` 1414;
  `install_links(server_real, tree)` 1415–1416; `link_problems → SetupError`
  1417–1419; receipt `install_tree`/`install_tree_sha256` 1431–1432.
- Catch layer: `except SetupError → receipt['setup_error']` 1602–1603;
  `except BaseException → _record_internal` 1606–1607.
- Host-dependent precedent: `os.chmod(lib, 0)` 1192, `os.access` guard 1194.
- Gate prerequisite `server-not-executable` (blocks chmod-e2e): 1398–1399.

[wt] working tree (dirty vs HEAD, provenance unknown, mutated during review):
`install_tree` fail-closed at 178–206; `:listdir:` raise 187–189;
`:lstat:{name!r}:` 194–196; `tree[name] = sha256_file(full)` 199–200;
`:read:{name!r}:` raise 201–203; combined digest 204–205.

Grid: `tests/llamacpp-live/install-io-grid.py` (untracked lane draft, sha256
`792debbd…1ae9f14`; sandbox Matrix copy differs — `d6da60f8…4f99e5c4`, both
carry the `read-llama-server-permission` row and the same over-pinning issue).

## Owned paths

- Report (append-only): `.ufo/waves/round-22/build/advice/ReadServerPerm.md`
- No production/test ownership; advice for Matrix
  (`tests/llamacpp-live/install-io-grid.py`) and L1's integration verdict.

## Verification gaps

- No runs this wave (contract). Classes derived from frozen/current source
  diff, not execution.
- Lane `tools/kama-llamacpp-live.py` is dirty vs HEAD and changed between two
  reads during this review — [wt] refs may drift; re-pin reason-format
  expectations against the *integrated* ApiFix artifact, and have `--arm
  current` load the ApiFix sandbox clone path, not the lane checkout.
- Lane `install-io-grid.py` (untracked) vs Matrix sandbox copy diverge; L1
  must pick one — the lane copy is newer (selftest + propagation rows) but both
  share the over-pinning bug in FP-2.
