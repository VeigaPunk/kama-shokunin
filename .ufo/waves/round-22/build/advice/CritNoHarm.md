# CritNoHarm — round 22 C1, dimension: no harm to existing successful results

Seat: KamaR22.CritNoHarm (critic, read-only). No verification runs. No installs.
Base: master = 10271460cc575fc2280aa831e442726385fc2319 (producer blob sha256
`cec67949…`, identical to round-21 measured commit 7054dba1; `git diff 7054dba1 master
-- tools/kama-llamacpp-live.py tests/llamacpp-live/` is empty).

## Axes
Primary axis 7 (operability). This dimension asks one thing: does every existing
successful map/digest result, receipt result, grid result and `setup_error` stay
byte-for-byte the same? The baseline is the 33 declared exits in
`.ufo/waves/round-21/recipe-final.json`, measured at `runs/7054dba1`.

## Evidence read
- `tools/kama-llamacpp-live.py:171-262` (`sha256_file`, `install_tree`, `install_links`),
  `:1117-1198` (`_install_identity_selftest`), `:1413-1419` (main: `install_tree`, then
  `install_links(server_real, tree)`, then `SetupError('install-tree-unpinnable:'+…)`),
  `:1602` (the `SetupError` handler).
- `tests/llamacpp-live/install-links-grid.py:169-183,203-271,301-364,383`
  and `tests/llamacpp-live/unpinnable-e2e.py:70-107`.
- `tests/llamacpp-live/check-receipt.py:165-175,307-318,407-421` and
  `tests/llamacpp-live/install-tree-grid.py`. Both are receipt-only; neither calls `install_tree`.
- `corpus/lessons/round-21.md` C2 and `corpus/QUALITY.md` KQ29.
- Round-21 final measurement `runs/7054dba1`:
  - `c2-grid-current`: real_identity `install_tree_sha256 6c216313a88d71b1…`,
    `install_links_sha256 5cb9f4865c8e1315…`, link 13/13, subdir 3/3, regular 3/3, type 1/1, null 0/1;
    row `regular-unreadable = {changed:true, refused:true, gate_chain_problems:{}}`.
  - `c2-unpinnable-e2e`: the `setup_error` strings are
    `install-tree-unpinnable:glibc-hwcaps:loader-searched-subdirectory` (×2) and
    `install-tree-unpinnable:libggml.so:link-not-to-member;libggml.so.0:link-not-to-member`.

## Finding 0 (contract breach, blocking measurement): the lane checkout is mutated
At 13:01–13:02Z, `git status` in the lane root shows:
`M tools/kama-llamacpp-live.py`, `M tests/llamacpp-live/install-links-grid.py`,
`?? tests/llamacpp-live/install-io-grid.py`. Only `build/sandboxes/Matrix` exists.

- The working-tree producer is now sha256 `b140044c…`; the frozen blob is `cec67949…`.
- Any seat or recipe that reads the "frozen" producer from the working tree now reads post-fix code.
  That makes the red-before measurement false.
- The round-21 `run.py` pattern refuses an unclean tree (`run.py:27`).

Impacted axes: provenance and operability.

Rejection condition: L1 measures with a dirty lane, or any frozen arm loads the producer from a path
instead of `git show 10271460…:tools/kama-llamacpp-live.py`.

Minimum remedy: the author moves the edits into its own sandbox and L1 integrates from there.
Every frozen arm loads by `git show <rev>:path`. I did not revert anything; ApiFix and Recipe have been notified.

## Review of the draft currently in the lane (taken as ApiFix/CallerRepair's proposal)

### Preserved (no counterexample found)
- **Success-path map and digest.** On a readable tree, `install_tree` takes the same
  `sorted(os.listdir)`, `lstat` and `S_ISREG` path and builds the same `'{n} {sha}\n'` lines. Only the
  three `except` arms changed, so a readable tree yields the same digest as before
  (`6c216313…`, 51 members).
- **Symlink semantics.** Symlinks and directories still `continue` before any read.
- **Receipt-only consumers.** `check-receipt.py`, `install-tree-grid.py` and the three legacy receipts
  recompute from stored receipts, so their declared exits 0/0/0 and 1/1/1 (`--require-install-links`) do not depend on `install_tree`.
- **`unpinnable-e2e` rows.** None of the three mutations makes `install_tree` raise. A `glibc-hwcaps`
  directory, a symlink and a dangling link all pass `lstat` and are not regular. So the `install_links`
  path still produces the three `setup_error` strings above unchanged.
- **Grid `regular-unreadable` row.** The draft `identity()` returns `problems=[exc.code]`, giving
  `refused:true`, `changed:true` (because `install_tree_sha256` is None, it differs from the real tree's) and
  `gate_chain_problems:{}` (empty link map). That equals the 7054dba1 row. In the grid selftest,
  `regular[-1]` is `llama-server`, so `controls-both-arms` (regular changed == 3) still holds.

### H1: an unrepaired `install-links-grid.py` flips three declared exits
With the producer fix and without the `identity()` repair, the current arm raises `SetupError` out of
`identity()` at cell `regular-unreadable` (`chmod 0` on `regular[-1]`). The handler at `main:383`
maps that to exit 2. The declared results change:
- `c2-grid-selftest`: 0 → 2
- `c2-grid-current`: 0 → 2
- `c2-grid-both`: 1 → 2

The frozen arm loads `FROZEN_REV 7a6bc911` via `git show` and is unaffected.

Rejection condition: any of the round-21 declared exits for `c2-grid-*` differs, or the
`regular-unreadable` current row is not `{changed:true, refused:true, gate_chain_problems:{}}`.

Remedy: land the `identity()` `SetupError` catch atomically with the producer change. Re-raise for
the frozen arm, which is the draft's choice. The catch must be `module.SetupError` only, never a bare `Exception`.

### H2: the pristine scan in `unpinnable-e2e.py` has no `SetupError` arm
`unpinnable-e2e.py:73` calls `producer.install_tree` outside any `SetupError` handler. `:106` catches only
`OSError`, `RuntimeError`, `ValueError` and `TimeoutExpired`. If the pristine copy ever has a member that
cannot be read:
- before the fix, the scan recorded `pristine copy has problems [...]`, printed its JSON rows and exited 1;
- after the fix, it dies with an uncaught traceback, prints no rows, and exits 1 by Python's default.

The exit code is unchanged, but the evidence rows are lost. An exit 1 from a crash now looks the same as
the declared verdict "1 = a case was not refused".

This file is not yet edited in the lane. Rejection condition: a pristine-scan `SetupError` produces anything other
than a `pristine-scan` row whose problems contain the code, followed by exit 1.

Remedy (CallerRepair): catch `producer.SetupError` around lines 73-75 and record `[exc.code]` as problems.

### H3: `setup_error` detail grammar silently changes for the unreadable-member path
In main, `install_tree` now raises before `install_links`. For an install with an unreadable member:
- before: `install-tree-unpinnable:<name>:unreadable`, with up to 8 `;`-joined problems from every entry;
- after: `install-tree-unpinnable:read:<name>`, first failure only.

Diagnostics regress in two ways:
- Co-occurring `install_links` problems are no longer reported. A `glibc-hwcaps` entry plus an
  unreadable lib now reports only the lib.
- The draft drops `exc.strerror`, so `EACCES` and a vanished member (`ENOENT`) produce the same token.

The `install-tree-unpinnable:` prefix (colon included) is kept, which is what `unpinnable-e2e.py:92`
requires. No consumer pins the full string (search of `tests/`, `tools/`, `SKILL.md` and
`corpus/knowledge/llamacpp-loading-lifecycle.md:344`). This is a tradeoff to declare, not a verdict harm.

Rejection condition: a bare `install-tree-unpinnable` token without the trailing colon, or any
`setup_error` row in the round-21 e2e output changes.

Remedy: keep the `<name>:<strerror>` grammar, e.g. `install-tree-unpinnable:<name>:<exc.strerror>` and
`install-tree-unpinnable:listdir:<strerror>`, so it matches `install_links` (`f'{name}:{exc.strerror}'`).
Use `{name!r}` when the name contains a control character. Also state in the lesson that aggregation is now first-failure.

### H4: deleting the `install_links` `not-hashed` branch as "now dead" would be harm
After the fix, main only reaches the `tree is not None and name not in tree` branch (`:258`) when a
regular member appears between the two `listdir` calls (a race between them). It is the only refusal
for that race, and `_install_identity_selftest:1188-1190` pins it.

Rejection condition: the branch, or the selftest pin, is removed in this round.

Remedy: keep it, and reword the docstring (`:224-225`) to name the race. The same rewording applies to the
round-21 lesson/KQ29 text "regular members install_tree failed to hash".

### H5: success-digest regression vectors to reject on sight
- `os.scandir` with `DirEntry.is_file()` follows symlinks by default, so soname links would become
  members and `6c216313…` would move.
- `os.stat` in place of `os.lstat` causes the same failure.
- Raising on directories or symlinks inside `install_tree` would refuse `openvino-licensing/`.
  That breaks the `subdir-other-recorded` cell, which expects not refused.
- Returning `({}, None)` or a partial map on error instead of raising would reproduce the original defect.

Rejection condition: for every readable tree in the matrix, current `(map, digest)` differs from
`git show 10271460:tools/kama-llamacpp-live.py`'s `install_tree`. Also reject if `back_compat_install_tree_sha256_equal`
is not true in `c2-grid-both`.

### Pre-existing, not introduced (do not attribute to C1)
- When run as root, `chmod 0` does not block reads. `regular-unreadable` then reads as "same" in both arms
  and the grid exits 1. Matrix must mock this, never depend on host permissions.
- Undecodable (surrogate-escaped) names make `''.join(...).encode()` raise `UnicodeEncodeError`.
  The frozen code has the same behaviour.

## Falsifiable rejection condition (single, for the judge)
Reject C1 on the no-harm dimension if, at the integrated commit, measured on a clean lane, either of these holds:
- One of the 33 round-21 recipe-final declared exits changes (excluding entries whose command
  intentionally targets the new fault matrix).
- One of these values changes:
  - `install_tree_sha256 6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c`
  - `install_links_sha256 5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060`
  - the grid per-class counts (link 13/13, subdir 3/3, regular 3/3, type 1/1, null 0/1)
  - the `regular-unreadable` row
  - the three e2e `setup_error` strings.

## Minimum remedy set (not an implementation)
1. Move the edits out of the lane checkout into sandboxes. L1 integrates from there, and every
   frozen arm uses `git show`.
2. Land the producer change and the `identity()` catch in `install-links-grid.py` atomically.
3. Add the `SetupError` arm to the pristine scan in `unpinnable-e2e.py`.
4. Use `<name>:<strerror>` detail and keep the colon prefix.
5. Keep the `not-hashed` branch and reword its docstring.

## Addendum, 13:04Z: the lane is still being mutated, and the notices were not delivered
The messages to `KamaR22.ApiFix` and `KamaR22.Recipe` were not processed: both wake turns failed
with `turn_rate_limit_exceeded`. L1 must act on Finding 0 directly.

The lane now also has these changes:
- `M tests/llamacpp-live/check-receipt.py`: comment only. `allow_none=True` is kept, so legacy
  receipts with a null tree digest still validate, and the legacy exits are preserved.
- `M tests/llamacpp-live/unpinnable-e2e.py`
- `M corpus/SOURCES.md` (+17 lines). Its append-only status is not checked here; the
  `nh-sources-append-only` pin applies.

H2 update: the e2e edit wraps the pristine scan and converts `SetupError` into `RuntimeError`, which
exits 2 (could-not-evaluate). There is no traceback, and declared `c2-unpinnable-e2e` 0 is unaffected.
That is acceptable. One residual: a pristine `install_links` problem still exits 1, while a pristine
`install_tree` failure exits 2. Declare that split; it is not a harm.

H3 update (new determinism harm): the draft detail is now `…:read:<name>:{exc}`. `str(OSError)` is
`[Errno 13] Permission denied: '/abs/path/…'`, so `setup_error` embeds the absolute path. For the e2e
and grid copies that path is a random temporary directory, so the same failure yields different
receipt bytes on every run. The errno text also adds `:` and spaces into a `:`-delimited token.

Rejection condition: two runs on the same fault in different temporary directories produce different
`setup_error` strings.

Remedy: use `exc.strerror` (or `errno.errorcode[exc.errno]`) and `{name!r}`, never `{exc}`.

## Addendum, 13:14Z: ApiFix proposes a bare `SetupError.code`
ApiFix reports that it now edits only `sandboxes/ApiFix`, and that the dirty lane edits are not
its own; their author is unknown. L1 has to decide whether to discard them.

ApiFix proposes `code == 'install-tree-unpinnable'` (bare, for Matrix's oracle), with the detail
only in the rendered message. That is harm (H6):
- **The detail never reaches the receipt.** Main records only `receipt['setup_error'] = exc.code`
  (`10271460:1602-1603`), so the member name and error text are lost.
- **One refusal class gets two spellings.** `install_links` refusals stay
  `install-tree-unpinnable:<problems>` (the round-21 e2e strings, which must not change), while
  `install_tree` refusals become bare. `unpinnable-e2e.py:92` matches
  `startswith('install-tree-unpinnable:')`, so it would read a bare `install_tree` refusal as not refused.

Rejection condition: the receipt's `setup_error` for an `install_tree` I/O refusal is the bare token,
or it carries no member and operation context.

Remedy: use `code = f'install-tree-unpinnable:{op}:{name!r}:{exc.strerror}'` and keep the
`SetupError(code)` signature. Matrix's oracle should accept the bare token or the colon prefix.
ApiFix and Matrix have both been told.

## Addendum, 13:15Z: H6 is resolved by ApiFix's `SetupError(code, detail=None)`
ApiFix's revised design:
- `.code` stays bare (`install-tree-unpinnable`), so Matrix's exact-equality oracle passes.
- `str(exc)` renders as `code + ':' + detail`.
- Main's handler writes `code:detail` only when a detail is present.

The only producer reader of `SetupError.code` is `main:1603`; line 504 is an unrelated
`HTTPError.code`. That makes the receipt handler the single choke point. I approve the design on the
no-harm dimension, subject to these conditions:

1. With `detail=None`, the receipt `setup_error` is byte-identical to today for every existing raise
   site, including `install-tree-unpinnable:<problems>` from the `install_links` path. The round-21
   e2e strings must not change.
2. The detail is deterministic: `op:{name!r}:{exc.strerror}`, or `listdir:<strerror>`. Never `{exc}`,
   and never an absolute path.
3. The positional `SetupError(code)` signature is kept.
4. Test-side readers that want the detail use `str(exc)`, not `.code`. The `identity()` catch in
   `install-links-grid.py` is fine because only `refused` is emitted. The pristine-scan message in
   `unpinnable-e2e.py` should use `str(exc)`.
5. The report declares that `.code` is bare for `install_tree` raises but carries a colon suffix for
   `install_links` raises. The receipt string is uniform either way.

Rejection condition: one of the round-21 `setup_error` strings changes, or an `install_tree` I/O
refusal receipt lacks the `install-tree-unpinnable:<op>:` prefix.

## Owned paths
- Written: `.ufo/waves/round-22/build/advice/CritNoHarm.md` (this file only).
- Messages sent: `agent://KamaR22.ApiFix` and `agent://KamaR22.Recipe` (lane-dirty notice).
- Installs: none.
