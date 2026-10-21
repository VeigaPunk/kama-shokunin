# SrcExceptions — round 22 source scout: Python 3.14 OSError subclasses and errno boundaries

Seat: KamaR22.SrcExceptions (read-only scout). Owned path: this file only. No edits to
`corpus/SOURCES.md`, no clone, no verification runs, no installs.

## Verdict

**Accept as a new tier-A row, scoped narrowly. ID is reserved for L1 (proposed next: S075).**
The source is strong: official, versioned, first-party CPython documentation, and the host
interpreter matches the documented version. It does not duplicate S051. S051 cites the same page
but is scoped to "which built-in exceptions escape `except Exception`", anchored on §Exception
hierarchy, KeyboardInterrupt, SystemExit, GeneratorExit and BaseExceptionGroup. It says nothing
about OSError construction, errno mapping or the OS-exception subclasses. Widening S051's scope
would merge two unrelated claims into one row, so I recommend a separate row.

## Source as opened

- URL requested: https://docs.python.org/3.14/library/exceptions.html#OSError
- Observed on 2026-10-21 13:01 UTC: `HTTP/2 301`, with `location: https://docs.python.org/3.14/builtins/exceptions.html`.
  The target answers `HTTP/2 200`, `last-modified: Wed, 21 Oct 2026 10:03:02 GMT`, `etag: "6ad88dd6-232ca"`.
  This is the same redirect S051 already records.
- Version: the page navigation reads "3.14.8 Documentation", and the footer reads "Last updated on Oct 21, 2026 (10:01 UTC)".
  The host interpreter is `3.14.8 (main, Oct 2 2026, 10:23:31) [GCC 16.2.1 20260810]`.
- Fetched body: 144074 bytes, sha256 `183e57b3c36a33ad2fecd7d7143f09de490d1dec4803f5d0f322f2f197de2872`.
  The temporary copy was at `/tmp/srcexc-exceptions.html` and is not a lane artifact.
- Page anchors present: `id="OSError"` and `id="os-exceptions"`.
- Access date: 2026-10-21.

### Located quotes (each 25 words or fewer)

1. §Concrete exceptions → `exception OSError`, constructor paragraph (24 words):
   "The constructor often actually returns a subclass of OSError, as described in OS exceptions below. The particular subclass depends on the final errno value."
2. Same paragraph, next sentence, which sets the boundary for mocks:
   "This behaviour only occurs when constructing OSError directly or via an alias, and is not inherited when subclassing."
3. §OS exceptions, intro (17 words):
   "The following exceptions are subclasses of OSError, they get raised depending on the system error code."

The supporting mappings in §OS exceptions are:
- `FileNotFoundError` corresponds to `ENOENT`.
- `PermissionError` corresponds to `EACCES`, `EPERM` and `ENOTCAPABLE`.
- `NotADirectoryError` corresponds to `ENOTDIR`.
- `IsADirectoryError` corresponds to `EISDIR`.
- `InterruptedError` corresponds to `EINTR`. Since 3.5, PEP 475 retries interrupted system calls instead of raising.
- `OSError.errno` is "A numeric error code from the C variable errno".
- The attributes `strerror`, `filename` and `filename2` "default to None if not specified".

## Proposed row (L1 allocates the ID; do not paste the placeholder ID)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S0?? (L1: next is S075) | Python 3.14 OSError and OS exceptions — https://docs.python.org/3.14/builtins/exceptions.html#OSError (the requested `/3.14/library/exceptions.html#OSError` answers 301 to it) | docs | A | how an OSError raised by `os.listdir`/`os.lstat`/`open`/`read` in the host's Python 3.14 harness maps errno to a subclass, and that one `except OSError` covers all of them; not Windows `winerror`, not non-OSError faults | §`exception OSError` constructor paragraph and attribute list; §OS exceptions (`#os-exceptions`); page "Built-in Exceptions — Python 3.14.8 documentation", last updated 2026-10-21 10:01 UTC; opened 2026-10-21 | "The particular subclass depends on the final errno value." Mapped errnos become FileNotFoundError, PermissionError and similar; unmapped ones such as EIO stay plain OSError. A handler that catches only named subclasses misses those, so install identity must refuse on any OSError. | queued; set to mined once L1 cites it from the round-22 lesson or the install-io grid | 2026-10-21 | on-release | (L1 fills in: e.g. corpus/lessons/round-22.md, tests/llamacpp-live/install-io-grid.py) |

Flip condition: if the 3.14 docs drop or change the constructor-returns-subclass paragraph or the
§OS exceptions errno table, or if the harness interpreter moves off 3.14, re-open this row and
downgrade it. Status stays `queued`, not `mined`, until some lane artifact actually cites it.

## Why it matters for C1 (install_tree must fail closed)

What I observed in the frozen code: `git show 10271460…:tools/kama-llamacpp-live.py`, lines 178–202.
`install_tree` wraps each of its three operations in a bare `except OSError`:

| Operation | Frozen behavior on OSError |
|---|---|
| `os.listdir` (line 185) | Returns `{}, None` |
| `os.lstat` (line 191) | Skips the member with `continue` |
| `sha256_file` (line 197) | Skips the member with `continue` |

After any skip, the combined digest is still computed over the members that remain. That is
exactly the silent, comparable partial digest the C1 claim targets.

What the source plus a host probe establish (an interpreter probe on 3.14.8, not a test run):
- Constructing `OSError(errno.X, msg, path)` produced these types:
  - `ENOENT` became `FileNotFoundError`.
  - `EACCES` and `EPERM` became `PermissionError`.
  - `ENOTDIR` became `NotADirectoryError`.
  - `EISDIR` became `IsADirectoryError`.
  - `EINTR` became `InterruptedError`.
  - `EIO`, `ELOOP`, `ENAMETOOLONG`, `EMFILE`, `ESTALE` and `EXDEV` all stayed plain `OSError`.
  - Every one of them satisfied `isinstance(e, OSError)`.
- A user subclass `class S(OSError)` constructed with `ENOENT` stayed `S`. This matches quote 2.
- `OSError('boom')` has `errno is None` and `strerror is None`.

Implications for the seats (advice only, not edits):

1. **ApiFix.** The refusal must trigger on *any* `OSError`, as the current `except OSError` sites already do.
   Do not narrow the catch to `(FileNotFoundError, PermissionError)`: unmapped errnos such as EIO would
   then escape as raw tracebacks instead of `SetupError('install-tree-unpinnable')`. Only `OSError`
   should be caught. Widening to `Exception` would turn programming errors into "unpinnable" reports.
2. **Matrix (install-io grid).** Include at least one unmapped errno per site (`EIO` is enough)
   alongside `ENOENT` and `EACCES`. Otherwise a mutant that narrows the catch to named subclasses survives.
   Inject the fault with `OSError(errno.EIO, os.strerror(errno.EIO), path)` so that errno mapping actually
   runs. A custom `OSError` subclass would not be remapped (quote 2).
3. **Mistake to watch for when preserving reason detail.** `OSError('msg')` and a bare `OSError()` carry
   `strerror=None`. The frozen `install_links` (line 234) builds its detail with `f'listdir:{exc.strerror}'`,
   which renders as `listdir:None` under such an injection.
   - Any reason detail should come from `exc.errno`/`errno.errorcode` or the subclass name, with a fallback, rather than assuming `strerror` is set.
   - Fixtures should use the three-argument form.
4. **Vanished member.** An entry removed between `listdir` and `lstat` raises `FileNotFoundError` (`ENOENT`).
   - Under the C1 claim this must refuse rather than be skipped, because the snapshot is no longer a consistent identity.
   - [INFERENCE] Treating ENOENT as "simply absent" would reopen the partial-digest hole through a race.
   - ApiFix and Matrix should make this an explicit matrix row (lstat ENOENT and open ENOENT) with an expected refusal.
5. **EINTR.** Since 3.5, CPython retries interrupted system calls (PEP 475, per the §InterruptedError note), so
   `InterruptedError` should not reach `install_tree` in practice. A mock that raises it is still an `OSError`
   and must refuse. It is not a separate row the matrix needs to cover.

## Out of scope / remaining unknowns

- Windows `winerror` semantics. The host is Linux only.
- Non-OSError faults. For example, `UnicodeEncodeError` on undecodable names belongs to the UnicodeNames seat;
  `ValueError` from embedded NUL is not an `OSError` and is not covered by this row.
- This source documents the errno-to-subclass mapping. It does not document *which* errnos `listdir`, `lstat`,
  `open` or `read` can produce on Linux; that is libc/kernel man-page territory (e.g. readdir(3), lstat(2)) and
  was not opened here.
- No LSP was used. This is a docs row plus a `git show` of the frozen blob; the line numbers are from that blob.

## Tooling

No installs or updates. Tools used: `curl`, `python3` 3.14.8 (host), `git show` (read-only), `sha256sum`.
