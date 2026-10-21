# OrderControl — enumeration-order independence, successful digest

Seat: `KamaR22.OrderControl` (reviewer). Read-only; no code edits, no runs.
Owned output: this file only. Reviewed targets: `tools/kama-llamacpp-live.py`
(frozen `10271460cc575fc2280aa831e442726385fc2319`, blob sha256
`cec679495591cf2410334dfe08c648e310f23825181dcbae7d13b911c980e023` — verified
against `git show`; matches `install-io-grid.py:24`) and
`tests/llamacpp-live/install-io-grid.py` (untracked, in-flight).

## The ONE case

**No-fault permutation control**: inject a deterministic non-sorted enumeration
order into the single `os.listdir` call, on the standard 2-member fixture, and
assert `install_tree` returns the complete map and the content-oracle digest.
This is already implemented as control `reversed-order`:
`install-io-grid.py:40` (CONTROLS), `:74` (`list(reversed(result)) if reverse`),
`:177` (`reverse=name == 'reversed-order'`), `:184-188` (verdict).

## Expected class per arm — GREEN-GREEN, pin this explicitly

- **frozen**: `complete-map-and-digest`. Frozen `install_tree` normalizes
  enumeration twice — intake `sorted(os.listdir(directory))` (blob line 185)
  and digest `sorted(tree)` (blob line 200-201). Order is already a non-input;
  a red frozen row here means harness breakage (e.g. leaked patch), not a real
  defect.
- **current**: `complete-map-and-digest`, same oracle. Working-tree sort points
  are `tools/kama-llamacpp-live.py:186` and `:204-205`.
- This row does **not** carry red-before/green-after semantics — it is a
  positive-control regression guard proving the C1 rewrite preserves digest as
  a pure function of directory content. Say so in the population pin so a
  frozen-green is never reclassified as a matrix failure.

## Smallest injection target

One seam: `module.os.listdir` wrapper (`install-io-grid.py:69-74`, patched at
`:116`). One producer call site is on the success path (frozen :185 / current
:186). lstat/sha256_file/open must stay unpatched for this row; `stage=None`
keeps `calls['fault']==0`, which the verdict already asserts (`:188`).

## Positive control

- `expected_tree` (`install-io-grid.py:55-58`) is an **independent oracle**
  recomputing sorted `'name sha\n'` digest from fixture bytes — digest equality
  is to a pinned value, not merely cross-arm equality; correctly prevents two
  identically-broken arms from passing. Same encoding as
  `check-receipt.py:165-177` recompute — oracle parity confirmed.
- Sibling `'regular'` control (same BODY, `reverse=False`) is the within-fixture
  baseline; the pair proves digest = f(content), not f(order).

## Findings

### 1. HIGH — `reversed(raw_listdir)` can equal `sorted(raw)`: vacuous control
`install-io-grid.py:74` reverses whatever order the real `readdir` returns.
BODY `{'llama-server','lib.so'}` is written in insertion order (grid `:163-164`,
`dict(BODY)` preserves); on tmpfs (`tempfile` default on this host) readdir
commonly yields creation order `['llama-server','lib.so']`, and reversed that is
`['lib.so','llama-server']` — **exactly the sorted order the producer computes
anyway**. With n=2 there are only two raw orders; one yields a vacuous row.
Effect is never a false red — it is a silent *false green*: the row reports
`passed` while having exercised nothing order-distinct, so an order-dependence
regression would slip through undetected on precisely the most common CI
filesystem. Fix: return `sorted(result, reverse=True)` — guaranteed ≠ sorted
for n≥2 distinct names — and self-check `injected != sorted(injected)` so the
row fails loudly instead of passing vacuously. Keep n≥2.

### 2. HIGH (cross-cut, not this row) — reason-shape mismatch poisons 15/18 fault rows
Current producer emits `install-tree-unpinnable:lstat:'lib.so':…` with
`{name!r}` quoting (`tools/kama-llamacpp-live.py:195`, `:202`), while the grid
builds bare `stage:member` (`install-io-grid.py:149-150`) and checks
`startswith(expected_reason + ':')` (`:152`). `'lib.so'` ≠ `lib.so` at the
first char after `lstat:` → all member-named rows (stat 6, read 8, late-read 1)
report violation on the correct refusal. Align quoting on one side before the
matrix is run. Listdir rows are unaffected (no member component).

### 3. LOW — permutation applies to every `listdir`, not just the fixture
The fault branches are path-filtered (`install-io-grid.py:70`, `:77`, `:83`,
`:111` `os.fspath(path) == os.fspath(folder...)`) but the reversal at `:74`
rewrites every `os.listdir` result while the patch lives; `os` is a shared
global module (`patch.object(module.os, ...)`, `:116`). Within this synchronous
evaluate() only `install_tree`'s single call is affected, so impact is latent —
apply the same folder filter to the reversal for hygiene and to keep the row
faithful if observe() ever runs arms/consumers concurrently.

### 4. LOW — `paired_problems` is dead code
`install-io-grid.py:129` `return result` precedes the `install_links` pairing
block at `:130-133`; unreachable. If pairing was intended to strengthen order
controls (assert `paired_problems` order-invariant), it currently never runs.

### 5. INFO — dict-equality assertion surface is sufficient, do not over-assert
`tree ==` (`install-io-grid.py:187`) is order-insensitive, and no observable
downstream channel consumes insertion order: digest re-sorts
(producer `:204-205`), receipt JSON is `sort_keys=True` (`:1308-1312`),
`links_digest` canonicalizes (`:212-214`), `install_links` uses `tree` for
membership only (`:262` `name not in tree`). Asserting insertion order would
reject legal implementations; current surface is exactly right.

### 6. INFO — optional second-order discriminator, if Matrix wants one more row
Faults are correctly name-targeted (`:77`, `:83`), keeping fault rows
order-deterministic. A *positional* fault × `reverse` pair would additionally
prove frozen's silent-partial digest is enumeration-unstable (two different
comparable partial digests for one "kth member fails" fault) while current's
refusal is order-invariant — red-before/green-after on the order axis itself.
Strict reading of the assigned case ("successful digest") keeps the plain
permutation control; list this only as an available strengthening, not required.

## Residual risk / verification gaps

- Finding 1 leaves the order row provably vacuous-or-not at readdir's whim until
  the permutation is pinned; that is the single change that makes this case a
  true discriminator.
- No runs performed (wave rule). Proposed check for L1: after fixes,
  `install-io-grid.py --arm both --json` must show `reversed-order` green on
  both arms with identical digest to `expected_tree`, and frozen fault rows all
  `returned` with partial digests (completeness violation evidence).
- Working tree is dirty (ApiFix/CallerRepair/Matrix edits in flight, per
  `git status`); line numbers cited are working-tree unless tagged "blob".

## Tooling

No installs or updates made. pacman paused per contract; nothing needed.
