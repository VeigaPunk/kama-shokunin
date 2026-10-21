# SrcScandir — Python 3.14 `os.scandir` / `os.DirEntry` source (round 22, C1)

Seat: KamaR22.SrcScandir (read-only scout). Owned path: this file only. No SOURCES edit, no
verification runs, no installs.

## Source opened

- URL: https://docs.python.org/3.14/library/os.html#os.scandir (sections also at
  `#os.DirEntry`, `#os.DirEntry.is_dir`, `#os.DirEntry.is_file`, `#os.DirEntry.stat`)
- Version: page titled "os — Miscellaneous operating system interfaces — Python 3.14.8
  documentation"; host interpreter `python3 --version` = Python 3.14.8 (observed).
- Accessed: 2026-10-21.
- Located quotes (each ≤25 words, verbatim from the fetched page):
  - §`class os.DirEntry` ¶4 (primary): "Because the os.DirEntry methods can make operating system
    calls, they may also raise OSError." (14 words)
  - §`class os.DirEntry` ¶2: "When a stat() or lstat() system call is made, the os.DirEntry
    object will cache the result." (16 words)
  - §`DirEntry.is_dir()` last ¶ (also referenced by `is_file()`: "Caching, system calls made, and
    exceptions raised are as per is_dir()"): "This method can raise OSError, such as
    PermissionError, but FileNotFoundError is caught and not raised." (16 words)
  - Module-level Note under §os: "All functions in this module raise OSError (or subclasses
    thereof) in the case of invalid or inaccessible file names and paths" (21 words)
  - §`os.listdir`: "If a file is removed from or added to the directory during the call of this
    function, whether a name for that file be included is unspecified." (27 words, so it is
    over the limit as a single quote. Cite only the first clause, "whether a name for that file
    be included is unspecified", if it is used.)

## Observed code facts

- Base `master` = `10271460cc575fc2280aa831e442726385fc2319` (observed).
- `tools/kama-llamacpp-live.py` `install_tree` (lines 178–202 at master) uses `os.listdir` and
  `os.lstat`, and hashes through `sha256_file` (`open()`). It has three silent-skip sites:
  `except OSError: return tree, None` on listdir, `continue` on lstat, and `continue` on
  `sha256_file`. A successful run returns a `(map, combined)` tuple. A failed listdir returns
  `({}, None)`. A member that fails lstat or reading is dropped without any signal, and the
  digest is still produced.
- `install_links` (lines 213–263) enumerates the same directory with `os.listdir` and
  `os.lstat`. It records the failures it sees as `problems`. When the caller passes the `tree`
  map, it flags a regular member the map lacks as `not-hashed`.

## Findings

1. **The docs support the fail-closed fix with the existing calls; no rewrite is needed.** The
   module note says every `os` function raises `OSError` or a subclass for inaccessible paths.
   So catching `except OSError` around `listdir` and `lstat` and then raising
   `SetupError('install-tree-unpinnable')` covers the whole documented failure surface of those
   two calls. `open()` and `read` failures inside `sha256_file` are also `OSError`, and S051
   already covers that hierarchy, so this page adds nothing there. Confidence: high (docs).
2. **Reject a scandir rewrite.** It harms other axes and improves none:
   - **It would silently reintroduce the bug.** `DirEntry.is_file()` and `is_dir()` catch
     `FileNotFoundError` and return `False`, per the third quote. If a member vanishes between
     enumeration and the type check, an `entry.is_file()` filter treats it as "not regular" and
     skips it with no signal. That is the incomplete-identity failure C1 removes, now hidden
     inside the standard library. The current `os.lstat` raises `FileNotFoundError`, which the
     fix can turn into a refusal. Confidence: high (docs).
   - **It gives no syscall saving on Unix.** The §`os.scandir` text says
     "os.DirEntry.stat() always requires a system call on Unix". A rewrite that keeps
     `entry.stat(follow_symlinks=False)` makes the same lstat-class call as today. Confidence:
     high (docs).
   - **Its results go stale.** The §`DirEntry` text says the cached result is reused and that
     "os.DirEntry instances are not intended to be stored in long-lived data structures". A
     cached type answer adds a second staleness window that the pinning gate would then have
     to reason about. Confidence: high (docs).
   - **It splits the error surface.** Per §`scandir.close()`, errors can also arise "during
     iterating", so failures would surface mid-loop as well as at the call. The `sorted()`
     ordering would still force the whole listing into memory, so there is no streaming
     benefit. Confidence: medium (docs, plus inference about the sort).
   - **It would make the fault-injection grid incomparable** [INFERENCE]. Matrix and
     CallerRepair inject failures at `os.listdir`, `os.lstat` and `sha256_file` against the
     frozen blob. A scandir-based current arm would need different patch points, so the
     frozen-before and current-after rows would no longer exercise the same faults.
     `install_links` would also stop enumerating the same way as `install_tree`, and the
     `not-hashed` cross-check depends on the two agreeing on membership.
3. **Race caveat for the matrix (StatGone and ReadGone).** `os.listdir` leaves unspecified
   whether a name removed or added during the call is included. A listdir-then-lstat
   `FileNotFoundError` is therefore a real, documented state, not a contrived one, and C1
   requires it to end in refusal rather than `continue`. The same applies to `sha256_file`
   hitting `FileNotFoundError` after lstat succeeded. Confidence: high (docs); its applicability
   to the grid rows is inference.
4. **Symlink semantics are unaffected.** `os.lstat` "does not follow symbolic links", and the
   `S_ISREG` filter skips symlinks and other non-regular entries as intentional skips, not
   errors. Keeping `listdir` plus `lstat` preserves this exactly. Confidence: high.

## Proposed SOURCES row (the ID is reserved for L1; the next free ID observed is S075)

No current row cites `os.html`, `scandir`, `DirEntry`, `listdir` or `lstat` (grep over
`corpus/SOURCES.md`: no matches). The nearest rows are S051 (exception hierarchy), S044 and
S064 (subprocess), and S061 and S065 (sys.exit). None of them overlaps this scope.

```
| S0?? (L1 allocates; next S075) | Python `os.scandir` / `os.DirEntry` (Python 3.14) — https://docs.python.org/3.14/library/os.html#os.DirEntry | docs | A | `os` OSError surface for listdir/lstat and DirEntry cache/FileNotFoundError-swallow semantics in the host's Python 3.14.8; not Windows, not non-CPython | §class os.DirEntry ¶2 and ¶4; §DirEntry.is_dir last ¶; §os.scandir ¶2; module Note under §os; page titled Python 3.14.8 documentation (host 3.14.8); opened 2026-10-21 | "Because the os.DirEntry methods can make operating system calls, they may also raise OSError." `is_file()`/`is_dir()` swallow FileNotFoundError, so a scandir filter would silently drop a vanished member; keep listdir+lstat and refuse on OSError. flip: versioned docs change DirEntry caching/exception wording, or host leaves 3.14. | mined | 2026-10-21 | on-release | (L1: round-22 lesson / C1 knowledge note) |
```

- Tier: A, scoped to the official CPython documentation for the host's own minor version.
- Status: `mined`, provided L1 cites the row from the round-22 lesson or the C1 note. If no
  consumer cites it, file it as `queued` instead.
- I am not proposing a rejection. The source is primary, versioned and matches the host
  interpreter.

## Remaining unknowns

- I did not check whether the CPython `Modules/posixmodule.c` implementation at 3.14.8 matches
  the documented `FileNotFoundError` swallow. Opening the source at tag `v3.14.8` would raise
  the evidence from documentation to code.
- I did not check whether ApiFix's draft uses any `os.scandir` or `DirEntry` call. I saw no
  clone of it and did not message the seat.
