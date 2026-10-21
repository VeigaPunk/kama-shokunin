# EmptyControl — C1 matrix case: empty-directory successful digest

Scope: design ONE discriminating case for `tests/llamacpp-live/install-io-grid.py`
(Matrix-owned). Advice only; no code edits, no verification runs. Lane root:
`/home/vgpnk/Projects/shokunin/kama-shokunin`.

## The case: `empty-dir` — zero-fault positive control and collision anchor

### Setup (no mocks, no host-permission dependency)
- `tempfile.TemporaryDirectory()` → genuinely empty dir `D`.
- `server = os.path.join(D, 'llama-server')` — path constructed, file **NOT**
  created (creating it would add a member and defeat the point).
- Call `module.install_tree(server)`. `install_tree` only uses
  `os.path.dirname(server_real)`, so a nonexistent `server_real` is in-contract
  at function level and keeps `D` at zero members.

### Expected outcome — BOTH arms
| arm | result class | expected value |
|---|---|---|
| frozen (`1027146`) | `legit-success` | `({}, e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855)` |
| current (working tree) | `legit-success` | identical tuple, returned normally |

Pin the digest as a **literal constant** (`sha256(b'')`). Never derive it via
the module's own join-formula or a second `install_tree` call — oracle-echo
hides regressions. Do not confuse with `install_links` empty digest
`44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a`
(`sha256('{}')`); different constant, different function.

## Why this is THE discriminating case

Frozen `install_tree` produces `(tree, combined)` where `combined` is sha256
over `''.join(f'{n} {tree[n]}\n' ...)`. For an empty map that join is `b''`,
so the digest is `e3b0c442...b855` — a perfectly normal, comparable digest.

The same `({}, e3b0...)` tuple is emitted by frozen when **every** member
faults: all-`lstat`-fail, or all-`sha256_file`-fail after successful lstats.
Byte-identical output, opposite legitimacy. The digest value itself cannot
discriminate; only the cell's injected fault count can. The `empty-dir` cell
is therefore the reference that names the shared constant and the guard
against the over-refusal fix:

- `faults == 0` → digest required on **both** arms. If a "fixed" producer
  raises on a genuine empty map (e.g., treats `e3b0...`/`{}` as suspicious,
  or refuses whenever `tree` is empty), this cell goes red — a real
  regression the fault cells alone cannot see.
- `faults > 0` → digest-returned is a violation on frozen, refusal required
  on current. `empty-dir` supplies the exact expected digest those fault
  cells must be compared against to prove frozen emitted a *comparable
  partial identity*, not a distinct sentinel.

Note the third class: frozen `listdir`-fail returns `({}, None)` — digest
`None`, *not* `e3b0...`. Three distinct frozen outcomes must stay distinct
in the grid's classifier: `legit-success` (`e3b0`), `null-escape` (`None`),
`digest-escape` (real digest under faults>0).

## Smallest injection targets (for the paired fault cells this case anchors)

For `empty-dir` itself: **zero injection** — that is its value.

For the colliding all-fail cells, narrowest scope first:
1. `mock.patch.object(module, 'sha256_file', side_effect=OSError(...))` —
   module attribute only, zero global mutation; covers the read path.
2. For `os.listdir`/`os.lstat`: `mock.patch.object(module, 'os', ...)`
   with `types.SimpleNamespace(path=os.path, listdir=..., lstat=...)` —
   `install_tree` needs only `os.path.dirname`, `os.path.join`, `os.listdir`,
   `os.lstat`. This avoids mutating global `os.*` entirely; a
   `mock.patch('os.lstat')` would leak process-wide for the patch duration.
3. If global patching is used anyway: context-manager scope only, and the
   grid's `--selftest` should assert `module.os is os` and `os.lstat`/`os.listdir`
   identity restored after each cell.

## Refusal detection

Classify current-arm refusal as `module.SetupError` whose
`str(exc).startswith('install-tree-unpinnable')` (contract-pinned token).
Do **not** assert exact message suffix — the working tree has already shown
two variants (`{exc}` vs `exc.strerror or type(exc).__name__` detail) within
one observation window. A raw `OSError`/`Exception` surfacing is a different
class (unwrapped fault), never count it as `refused`.

## False-positive risks

1. **Passing `D` instead of `D/llama-server`**: `install_tree` takes
   `dirname(server_real)` — passing the directory itself silently enumerates
   `$TMPDIR`, producing a non-empty map of unrelated files. The cell would
   "succeed" on both arms while exercising nothing. Always pass a file path
   inside `D`. Similarly, a bare basename (`'llama-server'`) gives
   `dirname == ''` → `os.listdir('')` raises → looks like a listdir failure.
2. **Uniform `refused` expectation**: if the matrix schema forces every
   current-arm cell to `refused`, `empty-dir` either goes falsely red on a
   correct fix or is dropped — losing the over-refusal guard. Expected
   classes are per-cell per-arm.
3. **`None`-vs-`e3b0` conflation**: an "escaped" detector keyed on
   `tree_sha is not None` misses the listdir-fail `({}, None)` outcome; one
   keyed on `tree == {}` conflates all three. Detect on (faults_injected,
   digest_is_None, digest_value, exception_type).
4. **Shared temp dir**: real members created for fault cells leaking into a
   reused `D` make the empty map non-empty. Fresh `TemporaryDirectory` per
   cell, or fresh subdirectory.
5. **Mock leakage into the control**: any leaked `os.listdir`/`os.lstat`
   mock fabricates entries or faults in `empty-dir`. The SimpleNamespace
   approach eliminates this class; run `empty-dir` first in `--selftest` as
   the canary for leaked state.
6. **Stale "current" snapshot**: the working-tree producer is being actively
   edited this wave (two `install_tree` variants observed within one
   investigation). `--arm current` must load the file per run; never cache a
   snapshot as "current".
7. **Expecting the digest via recompute**: see literal-pinning above.

## Exact source references

Frozen blob `10271460cc575fc2280aa831e442726385fc2319`,
`tools/kama-llamacpp-live.py` (also current `HEAD`, verified via `git show`):
- `sha256_file`: lines 171–176 (the read-fault injection point).
- `install_tree`: lines 178–202.
  - listdir silent escape: 184–187 (`except OSError: return tree, None`)
  - lstat silent skip: 190–193 (`except OSError: continue`)
  - read silent skip: 196–199 (`except OSError: continue`)
  - combined digest / empty-map `e3b0` origin: 200–201; return: 202.
- `SetupError`: 154–160.
- `install_links` independent re-enumeration + `not-hashed` backstop:
  231–262 (esp. 258–259); consumer gate raising
  `SetupError('install-tree-unpinnable:…')` on `link_problems`: main() lines
  1414–1420; receipt fields written only after the gate: 1431–1433.

Current working tree (modified vs HEAD; `install_tree` now lines 178–206,
file 1794 lines): `SetupError('install-tree-unpinnable:listdir|lstat|read:…')`
raises at 188–189, 195–196, 202–203; success tuple at 204–206; nonregular
skip (`stat.S_ISREG`) preserved at 197–198. Consumer shifted ≈+4 lines
(≈1418–1424). The lane checkout was observed dirty and mid-edit — treat as
volatile; the frozen blob above is the stable reference.

## Nuance for the claim record

In production `main()`, the pre-fix `install_links(server_real, tree)` gate
already caught most overlapping failure modes (`not-hashed`, per-member
OSError → problems → `SetupError` at 1418–1420) before the receipt fields at
1431–1433 were written. The frozen hole is at **function contract level**:
`install_tree` alone returns a comparable partial digest with no error
signal — relevant to any direct consumer and to gate-ordering drift. The
matrix discriminates at function level, which is where the C1 claim is
scoped; do not claim the e2e path had zero backstop pre-fix.

## Owned / advised paths

- Owned (this report only): `.ufo/waves/round-22/build/advice/EmptyControl.md`
- Advised consumer: `tests/llamacpp-live/install-io-grid.py` (Matrix's clone)
- Observed, not edited: `tools/kama-llamacpp-live.py` (ApiFix's clone is the
  integration source; lane working tree is dirty — flag to L1 that
  `git status` shows ` M tools/kama-llamacpp-live.py` at lane root).

No tools installed this wave. No verification runs performed (per wave rules).
