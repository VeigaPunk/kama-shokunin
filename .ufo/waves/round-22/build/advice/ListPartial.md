# ListPartial — `os.listdir` partial-return semantics (round 22, C1)

Seat: KamaR22.ListPartial (read-only reviewer). Owned path: this file only. No installs,
no verification runs. Question assigned: *can `os.listdir` return a partial list on
failure, versus iterator semantics?* Answer below, then bounded coverage.

## Verdict: atomic at call granularity — a "partial listdir" is a FALSE case

`os.listdir` **never returns a partial list**. It either returns a complete `list` of
names or raises; there is no Python-observable state in which it yields some entries and
then fails. Evidence from CPython tag `v3.14.8` (host interpreter is Python 3.14.8,
observed), `Modules/posixmodule.c`, `_posix_listdir` (fetched to `/tmp/posixmodule.c`,
lines cited):

- `readdir` returns NULL with `errno != 0` → `path_error(path)` then `Py_CLEAR(list)`
  and `goto exit` — the partially built list is **destroyed**, never returned
  (lines 4637–4644).
- Name decode failure (`PyUnicode_DecodeFSDefaultAndSize` → NULL) → `Py_CLEAR(list)`
  (lines 4654–4656). `PyList_Append` failure → `Py_DECREF` + `Py_CLEAR(list)`
  (lines 4658–4661). Same discard-on-any-error pattern.
- `opendir` failure → `path_error(path)`, `list = NULL` (lines 4617–4627). Nothing is
  returned on any failure arm; the function only returns the list when the readdir loop
  exits on `errno == 0` (line 4638–4639).

The only documented non-determinism is *concurrent mutation*: the 3.14 docs say that for
a file added/removed during the call, "whether a name for that file be included is
unspecified" (sibling SrcScandir located this quote). That is a snapshot-tightness
property of a *successful* call, not a failure mode — C1's lstat/read refusal rows cover
its downstream symptom (a listed name that no longer stats).

**Consequence:** any matrix row or claim of the form "`listdir` returns fewer entries
than exist" is invented. Do not add it. A mock that returns a truncated list models a
*smaller directory*, which is indistinguishable from an honest listing and must produce
the honest smaller map/digest — that is the positive-control shape, not a fault.

## Where partial-iteration-then-raise IS real (and why it doesn't apply)

`os.scandir` and `pathlib.Path.iterdir` (3.13+: `os.scandir` underneath) yield lazily.
`ScandirIterator_iternext` (same file, ~line 16467): on a mid-iteration `readdir` errno
it calls `path_error` and returns NULL — **entries yielded by earlier `iternext` calls
stay yielded**. A consumer that catches the exception mid-comprehension can hold a
partial result. This is the genuine "iteration semantics" hazard — for code that
consumes `scandir` incrementally. The producer does not:

- `install_tree`/`install_links` use `os.listdir` (lines 186/233 working copy), not
  scandir; SrcScandir's advice to reject a scandir rewrite stands — it would import the
  very partial-yield semantics this claim excludes, plus `DirEntry.is_file()`'s
  `FileNotFoundError`→`False` swallow.
- The producer's sole `iterdir` use (selfcheck, ~line 1287, `list(Path(directory).iterdir())`)
  is whole-or-nothing for the consumer: `list()` either completes or raises, discarding
  partial state. No row needed.

## Bounded coverage — what the listdir fault rows legitimately are

Real listdir-side faults are exactly the OSError surface of `opendir`/`readdir`, all
raised by the single call:

- `ENOENT` → `FileNotFoundError` (parent or dir vanished; also reachable when
  `install_tree` runs without `install_links`' prior checks),
- `EACCES`/`EPERM` → `PermissionError`,
- `ENOTDIR` → `NotADirectoryError` (parent replaced by a regular file between
  `realpath`/`isfile` and `listdir` — the race sibling StatGone covers at member level),
- unmapped errnos (`EMFILE`, `EIO`, `ESTALE`) → plain `OSError`.

Current `install-io-grid.py` `ERRORS` + FAULTS already covers permission/missing/io at
the `listdir` stage. **Optional** completion: add `NotADirectoryError` as a fourth named
subclass (it is the only `opendir`-reachable errno-name in the OSError table the grid
doesn't exercise); not required, since `except OSError` catches it either way.
`InterruptedError`: PEP 475/signal machinery means EINTR rarely surfaces; if it did it
is still `OSError` → refused. No dedicated row (agrees with SrcExceptions).

Non-`OSError` raises (`TypeError`, `ValueError`, `MemoryError`, `KeyboardInterrupt`)
must **propagate**, not refuse — grid already pins `value-error`/`keyboard-interrupt`
propagation controls. `sorted()` on the returned list can't fail on real input (all-str
or all-bytes; a mixed-type result would require a mock violating the API).

## Accuracy notes for the claim and the two arms

1. **The base listdir escape is `({}, None)`, not a partial digest.** At frozen
   `1027146`, `install_tree` returns `({}, None)` on listdir `OSError`; the
   *comparable-partial-digest* shape (smaller map + valid-looking digest) is produced by
   the lstat/read `continue` sites, not by listdir. Keep claim language precise.
2. **Producer-level silence for a listdir fault is narrow.** `install_links` runs its
   own `listdir` and flags `not-hashed`/`unreadable`/lstat problems against the passed
   `tree`; the caller refuses on any problem. A base listdir failure stays silent at
   producer level only if `install_links`' own enumeration succeeds **and** sees no
   regular member it can check — e.g. a directory containing only valid in-dir symlinks
   and unpinned subdirs, or a transient one-call failure masked by the second call
   succeeding while no regular members exist. The grid measures function-level escape
   (`status: 'returned'` with `tree == {}`/`digest is None` on a fault row), which is
   the right red-before signal regardless.
3. **Time-of-writing observation (may already be resolved):** lane working copy
   `install_tree` raises `SetupError('install-tree-unpinnable:listdir')` /
   `...:lstat:{name}` / `...:read:{name}` (no trailing detail), while
   `install-io-grid.py` line ~152 expects `reason.startswith(expected_reason + ':')`,
   i.e. `install-tree-unpinnable:listdir:` with a detail colon. If that pair is current
   for both files, listdir/lstat/read fault rows fail green on format alone. Flagging
   for Matrix/ApiFix/L1 alignment only — I don't own either file.
4. **Fault count note:** `observe()` counts exactly one `fault` per row; `install_tree`
   calls `listdir` once, so raising-on-every-call is fine here. A "fails on the second
   call" shape is a producer-level transient scenario — legitimate for `unpinnable-e2e`
   (CallerRepair's lane), not for this function-level grid.

## Owned paths

- `.ufo/waves/round-22/build/advice/ListPartial.md` (this file — sole owned artifact).

## Residual unknowns

- I verified POSIX `_posix_listdir` only; Windows `_listdir_windows_no_opendir` shows
  the same discard-on-error shape in adjacent code but was not audited line-by-line —
  the lane is Linux-only, so out of scope.
- Whether libc `readdir` itself can return an errno mid-stream on the host's filesystems
  (ext4/btrfs) is kernel territory; unnecessary — the refusal row covers any errno.
