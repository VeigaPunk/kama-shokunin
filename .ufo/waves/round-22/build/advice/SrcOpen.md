# SrcOpen — Python 3.14 `open()` failure raises OSError (round 22, C1)

Seat: KamaR22.SrcOpen (scout, read-only). Owned path: `.ufo/waves/round-22/build/advice/SrcOpen.md` (this file only). No edits to `corpus/SOURCES.md`; no verification runs; no installs.

## Verdict
ACCEPT — tier A, status `mined` proposed. ID reserved for L1 (next free = S075; L1 allocates).

## Source (observed)
- URL: https://docs.python.org/3.14/library/functions.html#open
- Version: page title "Python 3.14.8 documentation"; footer "Last updated on Oct 21, 2026 (10:01 UTC)". Fetched 2026-10-21 with `curl` (318871 bytes).
- Section: Built-in Functions → `open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)`, first paragraph.
- Located quote (12 words): "Open file and return a corresponding file object. If the file cannot be opened, an OSError is raised."
- Corroborating quote, same entry, "Changed in version 3.3" note (13 words): "IOError used to be raised, it is now an alias of OSError."

## Why it matters to C1 (observed in frozen blob 10271460, `tools/kama-llamacpp-live.py`)
- `sha256_file` (line 171) calls `open(path, 'rb')` (line 173). Its failure is the documented `OSError`.
- `install_tree` (line 178) catches that failure at lines 196–199 (`except OSError: continue`), which drops the member and still returns a combined digest over the rest. The `listdir` failure returns `(tree, None)` (lines 184–187), and an `lstat` failure skips the entry (lines 190–193).
- What the source licenses: an unopenable member surfaces as `OSError`, so the code can see and refuse the failure. Silently skipping it is a choice the code makes, not something Python forces. The source does not say how to handle it; that belongs to C1.

## Proposed row (L1 assigns ID)
| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S0xx (L1) | Python built-in `open()` (Python 3.14) — https://docs.python.org/3.14/library/functions.html#open | docs | A | failure signalling of `open()` itself in the host's Python 3.14.8 harness; not errors from later `read()` calls, not `os.listdir`/`os.lstat` | §Built-in Functions `open()` ¶1 and its "Changed in version 3.3" note; page titled Python 3.14.8 documentation, updated 2026-10-21; opened 2026-10-21 | "If the file cannot be opened, an OSError is raised." So `sha256_file`'s member-open failure is an observable exception, and `install_tree`'s `except OSError: continue` is what turns it into a silent partial digest; flip: the versioned docs change the exception class. | mined | 2026-10-21 | on-release | corpus/lessons/round-22.md (L1 to confirm target) |

## Redundancy check against current `corpus/SOURCES.md` (master 10271460, rows S001–S074)
- No row cites `functions.html` or `open()`. The existing Python rows are S044/S064 (subprocess returncode), S051 (exception hierarchy), and S061/S065 (sys.exit).
- S051 covers which exceptions escape `except Exception`. It does not cover the fact that `open` raises `OSError`, so the two are complementary.
- S069 (Go dirhash `os.Open` per file) is a design from another ecosystem and does not overlap.

## Scope limits and unresolved gaps
- This row covers only the failure of `open()`. `OSError` from `fh.read()` partway through the hash loop (the IsADirectory, EIO or vanished-file races in `sha256_file`) is not stated on this page. The likely anchor is `io` (`RawIOBase.read` / `FileIO`), and that is for a sibling seat (ReadIO/ReadIsDir) if C1 rests on it [INFERENCE].
- `os.listdir` and `os.lstat` raising `OSError` comes from the `os` module docs, not this page. They are separate rows if needed (siblings SrcScandir/SrcExceptions).
- The same page notes PEP 475: an EINTR is retried rather than raised. That is irrelevant to C1 but explains why the fault matrix should inject `OSError` subclasses such as `PermissionError`, `FileNotFoundError` and `IsADirectoryError`, not `InterruptedError` [INFERENCE].
- The version is pinned to the 3.14 path. S044 records that `/3/` serves 3.15, so do not cite the unversioned URL.

## Tooling
No installs or updates.
