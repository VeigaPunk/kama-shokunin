# SrcOsLstat — Python 3.14 `os.lstat` symlink and failure semantics (round 22, C1)

Seat: KamaR22.SrcOsLstat (scout, read-only). Owned path: this file only. No SOURCES edit, no probes, no installs.

## Source opened

- URL: https://docs.python.org/3.14/library/os.html#os.lstat
- Version: page title "os — Miscellaneous operating system interfaces — Python 3.14.8 documentation"; footer "Last updated on Oct 21, 2026 (10:01 UTC)". HTTP 200, `last-modified: Wed, 21 Oct 2026 10:03:02 GMT`, etag `"6ad88dd6-b473a"`.
- Accessed: 2026-10-21 (13:00 UTC). Fetched HTML sha256 `a88a57fd6da9cbe9c95954b693d65cb7a14bbbab455477fab8c1cd65ad4eda11` (739130 bytes). This is byte-identical to round-21 SrcPythonReadlink's fetch.

## Located quotes (checked against the tag-stripped HTML)

- Q1. Section `#files-and-directories`, entry `#os.lstat`, ¶1 (21 words): "Perform the equivalent of an lstat() system call on the given path. Similar to stat(), but does not follow symbolic links."
- Q2. Section `#module-os` (module introduction), the Note block (21 words): "All functions in this module raise OSError (or subclasses thereof) in the case of invalid or inaccessible file names and paths"

The `#os.lstat` entry says nothing about failures. Failure semantics come only from the module-level Note (Q2) on the same page. Other `#os.lstat` facts: it is an alias for `stat()` on platforms without symlinks, it equals `os.stat(path, dir_fd=dir_fd, follow_symlinks=False)` since 3.3, and it accepts `dir_fd`.

## Findings

Observed facts from the frozen base `10271460cc57` `tools/kama-llamacpp-live.py`:

- `install_tree` L190–193: `st = os.lstat(full)` followed by `except OSError: continue`. Per Q2, an `OSError` here means the path was invalid or inaccessible. The function then drops the member and still returns a comparable `combined` digest, so the partial identity looks just like a smaller complete one. This is the C1 defect at the lstat site.
- L194: `if not stat.S_ISREG(st.st_mode): continue`. Per Q1, lstat describes the link itself and not its target. A symlink, including a dangling one, therefore yields a successful non-regular result and is skipped on purpose. That skip is the existing symlink semantics and must stay unchanged; `install_links` (L213+) remains the policy for links.
- Q2's "or subclasses thereof" means the frozen `except OSError` also catches `PermissionError`, `FileNotFoundError` and `NotADirectoryError`. A fault-injection matrix should therefore raise at least `PermissionError(13)` and `FileNotFoundError(2)` from `os.lstat`, plus a base `OSError(EIO)`.
- `install_links` L245 also calls `os.lstat`, but it already records `unpinned`/errors there (L260). It is not the silent path.

Inferences (not stated on the page):

- [INFERENCE] Under POSIX `lstat(2)`, a dangling symlink returns `S_IFLNK` without error. The fail-closed fix must therefore not treat a dangling link as an lstat failure. Q1 supports this only indirectly ("does not follow"), so a matrix row "dangling symlink → digest unchanged, no refusal" is the right positive control.
- [INFERENCE] `FileNotFoundError` from lstat after `listdir` is the race where an entry disappears mid-scan. Its listdir half belongs to SrcOsList. The page does not call such an entry absent, so refusing (`SetupError('install-tree-unpinnable')`) is the consistent choice, and silently skipping is not.
- [INFERENCE] `dir_fd` (Q1 entry) could pin lstat to the opened directory and narrow rename races. This is optional hardening and outside C1's claim. Do not add it.

## Redundancy check (corpus/SOURCES.md at lane HEAD, rows through S074)

- No current row cites `library/os.html`. Closest rows: S051 (built-in exception hierarchy: `OSError` is an `Exception`, which matters for the producer's `SetupError` catch), S044/S064 (subprocess) and S061/S065 (sys.exit). None of these covers lstat or the module's OSError convention.
- Round 21 drafted an os-module row (SrcPythonReadlink, draft "S066") and excluded it: "implementation detail or prior art no C1/C2 statement rests on" (SOURCES log, line 105). Round-22 C1 does rest on Q2, so the exclusion reason no longer holds. Coordinate with SrcOsList, SrcScandir and SrcStat so that L1 allocates one `os.html` row with combined anchors rather than one row per function.

## Proposed row (L1 allocates the id; next free is S075)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S0__ (L1) | Python 3.14 `os` — `os.lstat` and module OSError note — https://docs.python.org/3.14/library/os.html#os.lstat | docs | A | Python 3.14 lstat no-follow semantics and OSError signalling for kama's install-tree identity; not POSIX lstat(2) errno lists, not Windows reparse points | §Files and Directories `#os.lstat` ¶1; §module intro Note (`#module-os`); Python 3.14.8 documentation, footer Last updated Oct 21, 2026 (10:01 UTC); HTML sha256 a88a57fd…eda11; opened 2026-10-21 | lstat reports the link itself, so a symlink is a successful non-regular entry; an OSError means the member was inaccessible, so skipping it yields a partial identity. | mined | 2026-10-21 | on-release | corpus/lessons/round-22.md (+ the knowledge file L1 updates) |

Tier and status rationale: this is the official, version-pinned CPython documentation for the exact interpreter the harness runs (3.14.8), so tier A within the stated scope. Status is `mined` because C1's refusal rule depends on Q2. Not rejected.

Flip conditions:
- If L1 merges this into one `os.html` row with SrcOsList and SrcStat, keep Q1 and Q2 as that row's lstat and failure anchors.
- If a later Python version drops or rewords the module Note, the failure half needs `lstat(2)` (man7) ERRORS as its tier-A anchor.
- If C1's claim narrows to listdir or read failures only, this row should be `queued`, not `mined`.

## Proposed matrix rows (for Matrix; no runs performed)

- lstat raises `PermissionError`, `FileNotFoundError` or `OSError(EIO)` on one member. Frozen arm: partial digest escapes. Current arm: `SetupError('install-tree-unpinnable')`.
- Dangling symlink and valid symlink in the tree (lstat succeeds, `S_ISLNK`). Both arms return the same digest as the tree without the link.
- Regular-files-only tree, no faults. Both arms return the same `(tree, combined)` as the frozen pin.

## Tooling

None installed or updated. `curl` and `python3` were already present.
