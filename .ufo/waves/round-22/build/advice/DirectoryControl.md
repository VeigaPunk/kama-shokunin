# DirectoryControl — discriminating control case: intentionally skipped non-hwcaps subdirectory

Scope: design the ONE positive-control case for the C1 fail-closed matrix
(`install-tree-unpinnable`). Producer: `tools/kama-llamacpp-live.py`; new grid:
`tests/llamacpp-live/install-io-grid.py` (Matrix's seat). Advice only; no
edits/runs. Lane root: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Round-22 frozen base: `10271460cc575fc2280aa831e442726385fc2319`
(NOT `install-links-grid.py:49`'s older `7a6bc911…` — the io-grid must pin the
round-22 master or its "frozen" arm won't show silent-skip behavior).

## Case: `subdir-member-skipped` (positive control, expect `complete` on BOTH arms)

Fixture (pure filesystem — no `unittest.mock`, no permission changes):

```
<tmp>/
  llama-server                 regular file
  libllama.so.0.7.0            regular file
  libllama.so.0.7.1            regular file
  openvino-licensing/          real directory (never 'glibc-hwcaps')
    LICENSE.txt                regular file INSIDE the dir (kills recursion false-negative)
```

Call `mod.install_tree(str(tmp/'llama-server'))` on each arm.

Expected, both arms: returns `(tree, combined)` where
`tree == {'llama-server': sha('server-stub…'),
          'libllama.so.0.7.0': sha(…), 'libllama.so.0.7.1': sha(…)}`
and `combined == sha256(''.join(f'{n} {tree[n]}\n' for n in sorted(tree)).encode()).hexdigest()`.
No exception. `openvino-licensing` and `openvino-licensing/LICENSE.txt` absent
from map keys.

## Why this case (source anchors)

- `install_tree` skips non-regular entries BY TYPE, not by name:
  current (AF80) L194-195 `except … : raise …:lstat` then
  `if not stat.S_ISREG(st.st_mode): continue`; frozen L191-195 same `continue`
  on the same `lstat` result. A directory is S_ISDIR → skipped, digest never
  touched by directory NAME — so `glibc-hwcaps` vs `openvino-licensing` is
  IDENTICAL for install_tree; the hwcaps name check lives only in
  `install_links` L242-243.
- The skip is not "silent" at the consumer: `install_links` records real dirs
  by name in `unpinned` (L253-254) and refuses `glibc-hwcaps` (L242-243);
  precedent `os.mkdir(os.path.join(directory,'openvino-licensing'))` in the
  selftest L1184-1187 asserts `problems==[] and unpinned==['openvino-licensing']`.
- It is the discriminating control: a sloppy fail-closed patch that raises on
  ANY non-regular entry (instead of only on OSError) turns this cell `refused`
  on the current arm while the lstat/listdir/read fault cells also refuse —
  i.e. it detects over-broad refusal that a fault-only matrix cannot see.
  A recursion regression surfaces as extra map keys (populated dir is required
  for this; an empty dir cannot detect it).

## False-positive / vacuous-pass risks (must pin exactly)

1. `install_tree` pins `os.path.dirname(server_real)` (L183 current / L183
   frozen). Passing the DIRECTORY as `server_real` maps the PARENT. Pass a
   member path (`tmp/'llama-server'`), ideally `os.path.realpath`'d to match
   producer usage at L1414-1415.
2. Frozen returns `(tree, None)` on listdir failure, not an exception —
   per-outcome classifier must handle BOTH `(tree, sha)` success and
   `SetupError` (current refusal); frozen's `(tree, None)` is the
   `partial-escape` shape for fault cells, `complete` for this one.
   `partial` is legal frozen output ONLY with `combined=None` for listdir;
   lstat/read skips in frozen still return `combined` = digest of the shrunken
   map — that is exactly the "comparable partial digest" C1 attacks, so
   classify by (raised? sha is None? keys == expected?) not by shape.
3. Compute expected digests with a GRID-SIDE `sha256` (precedent
   `install-tree-grid.py:39-41`), never the module's own `sha256_file`
   (L171-176) — using it couples expectation to the code under test.
4. Don't chmod the subdir or make `lstat` fail on it — that re-enters the
   lstat-failure cell territory and needs host perms; the contract forbids
   host-permission dependence. Plain `mkdir` + `write_bytes` suffices;
   `lstat` on an entry only needs +x on the parent.
5. Real directory, NOT a symlink-to-dir (S_ISLNK branch is `install_links`'s
   link policy, different cell). Name must never be `glibc-hwcaps`
   (L242-243 refuses by name on the links side; keeping the case
   install_tree-only avoids conflating producers).
6. Control-char name risk is links-side only (L237-240); keep fixture names
   plain ASCII anyway so the cell cannot cross-contaminate if Matrix later
   extends it to install_links.
7. Assert the exact `(tree, combined)` tuple, not just "no exception": a
   patch that hashes the dir or returns a null/empty digest must fail.
   Arm-vs-arm equality alone is a false-negative for a shared bug — pin
   literals (digests of fixed fixture bytes) or grid-side recomputation.
8. Expected frozen class = `complete`, same tuple — do NOT label frozen
   `partial-escape` here or the control misfires. This cell's job is to hold
   "directory skip is preserved" while sibling fault cells hold "failure
   refuses": together they pin skip≠error.

## Matrix wiring notes (Matrix seat)

- Load arms the way `install-links-grid.py:61-85` does
  (`git show 10271460…:tools/kama-llamacpp-live.py` → `load_source`; current =
  lane file). Catch `mod.SetupError` → `refused`; `(tree, None)` or
  `(tree≠expected, sha)` → `partial-escape`; exact tuple → `complete`; any
  other exception → eval-error (exit 2), never a verdict.
- This cell contributes zero to `escaped`/`refused` counters; it is the
  guard proving the patch did not swallow the intentional dir skip.
  `install_links`-side `unpinned`/`glibc-hwcaps` coverage already lives in
  `install-links-grid.py` cells `subdir-hwcaps-shadow`,
  `subdir-hwcaps-symlink`, `subdir-other-recorded` (L161-165) and the
  selftest L1169-1187 — do not duplicate; CallerRepair owns that file.
- Consumer contract anchor for why refusal is correct upstream:
  `main` L1414-1420 — `install_tree` raising `SetupError` now short-circuits
  before `install_links`, and its `link_problems → SetupError
  'install-tree-unpinnable:…'` mapping already defines the receipt channel
  (exit 2, `setup_error` token; `unpinnable-e2e.py` asserts the same shape).

## Owned paths

- Report: `.ufo/waves/round-22/build/advice/DirectoryControl.md` (this file).
- No source edits; design delivered to `KamaR22.Matrix` for
  `tests/llamacpp-live/install-io-grid.py` in its own sandbox clone.

## Tooling

No installs this wave (pacman transactions paused host-wide; nothing needed).

## Update — Matrix negotiation (same wave)

Matrix renamed its combined `control:ignored-symlink-directory` cell to
`subdir-member-skipped` with the populated `openvino-licensing/LICENSE.txt`
fixture and exact-tuple assertions on both arms — adopted. Open point flagged
to Matrix: it plans to also retain a regular-file symlink inside that same
cell. Detection power for C1 is unaffected either way, but if that row is the
only install_tree-level link-skip assertion, a link-only regression would
misattribute to dir-skip. Recommended resolution: keep the cell dir-only and
add a separate `symlink-member-skipped` row (selftest-style tree of regulars +
soname links), or record per-entry diffs so a red cell stays attributable.
Resolution: Matrix split the cell three ways — `control:complete-map-digest`
(baseline exact tuple), `control:subdir-member-skipped` (dir-only, plain real
`openvino-licensing/` + LICENSE.txt, no symlink), and a symlink-only row. All
three assert exact `(tree, combined)` recomputed grid-side on both arms.
Directory-control design fully landed as intended.
