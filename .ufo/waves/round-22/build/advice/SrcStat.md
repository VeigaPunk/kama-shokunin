VERDICT: confirm, narrowly scoped — Python 3.14.8 `stat` docs ground the S_ISREG/S_ISLNK type split that C1's "preserve regular-file map and symlink semantics" control rests on; they say nothing about error handling, so they carry no part of C1's fail-closed claim. Proposed status `queued` (flip rule below); L1 allocates the ID (next free S075).

# SrcStat — round 22 source re-open (KamaR22 leaf, read-only)

## Source opened, 2026-10-21
- URL: https://docs.python.org/3.14/library/stat.html (cite `/3.14/`; `rel="canonical"` points at `/3/library/stat.html`, which serves 3.15 per S044/S051 notes).
- Fetched twice: Cursor WebFetch (rendered markdown) and `curl -fsSL` raw HTML. Exit 0; 67792 bytes; sha256 `9a9c4fe8f7635943dc1be7c47c76f33ec7e5e397e559e28422af0d8ef1a80a5d`; `<title>` "stat — Interpreting stat() results — Python 3.14.8 documentation"; footer "Last updated on Oct 21, 2026 (10:01 UTC)".
- The bytes match round 21's fetch exactly (`.ufo/waves/round-21/build/advice/SrcPythonReadlink.md` line 7: same sha256 and size), so the page has not changed since round 21.

## Located quotes (each an exact substring of the raw HTML, count 1)
- Q1 §file-type test functions, `#stat.S_ISREG` (10 words): "Return non-zero if the mode is from a regular file."
- Q2 same section, `#stat.S_ISLNK` (10 words): "Return non-zero if the mode is from a symbolic link."
- Q3 `#stat.S_IFMT` (18 words): "Return the portion of the file's mode that describes the file type (used by the S_IS*() functions above)." (Raw-match key `that describes the file type (used by the`; the apostrophe is a typographic one in the HTML.)
- Q4 paragraph after `S_IFMT` (≤25 words, raw-match key `wish to avoid the overhead of the`): "useful when you are doing multiple tests of the same file and wish to avoid the overhead of the stat() system call for each test"
- E1 `walktree` example (rendered fetch only; syntax highlighting splits it, so it is not a raw exact substring): `mode = os.lstat(pathname).st_mode` then `if S_ISDIR … elif S_ISREG(mode): callback … else: print('Skipping %s' …)`. The example has no `try`/`except`.

## What the page supports, and what it does not
- Supports: S_ISREG and S_ISLNK test one file-type field (Q3), extracted from a mode value. A mode can be "from a regular file" or "from a symbolic link", not both [INFERENCE from Q3's single type field; the page never says "mutually exclusive"].
- Supports: the predicates read a mode value that was already captured (Q4). The S_ISREG verdict describes the `lstat` snapshot, not the file at `open` time.
- Does NOT support: that `os.lstat` reports the link itself rather than its target. That is `os.lstat` in `library/os.html` ("Similar to stat(), but does not follow symbolic links.", quoted by round-21 SrcPythonReadlink Q2). I did not re-open os.html this round, so do not cite this row for it.
- Does NOT support any C1 statement about errors. The page is silent on `OSError`, partial results and refusal. The fail-closed property must rest on the lane fault-injection matrix (`tests/llamacpp-live/install-io-grid.py`, owned by Matrix), not on this row.

## Mapping to the frozen producer (lane checkout `tools/kama-llamacpp-live.py`, base 10271460)
- `install_tree` L184–199: `os.listdir` → `os.lstat(full)` (L191) → `if not stat.S_ISREG(st.st_mode): continue` (L194) → `sha256_file`. Every `except OSError` branch returns `tree, None` (L186) or `continue`s (L192, L198). That silent skip is the C1 defect.
- Docstring L179–181, "Symlinks are skipped as members (they are not regular files)": true per Q1–Q3 only together with lstat's no-follow behavior (os.html, not this page).
- `install_links` L245–254: `S_ISLNK` → readlink; `S_ISDIR` → unpinned; `not S_ISREG` → problem. Both functions take one lstat mode per entry and branch on these predicates.

## Mistake mining (findings for ApiFix / Matrix / L1)
1. The skips have two different causes, and the fix must keep them apart. `if not S_ISREG: continue` (L194) is the intended type skip: symlinks, directories, FIFOs and devices stay out of `tree`, and `install_links` stays the policy owner for them. Only the three `except OSError` exits (L185–186, L190–192, L196–198) should become `SetupError('install-tree-unpinnable')`. Turning the S_ISREG skip into a refusal would break "preserve existing symlink semantics". For example, it would refuse the real b11755 tree, which has 10 soname symlinks per round-21 SrcPythonReadlink L41.
2. The frozen code's `try/except OSError: continue` around `lstat` is weaker than the docs' own E1 pattern. E1 has no handler, so an lstat failure propagates. The frozen producer turned that propagation into a silent drop [INFERENCE: E1 is illustrative example code, not a stated contract; use it as corroboration only].
3. Time-of-check/time-of-use (TOCTOU) gap, outside C1 [INFERENCE]: Q4 makes S_ISREG a verdict on a snapshot. Between `lstat` (L191) and `sha256_file` (`open`, which follows links), an entry swapped for a symlink would be hashed by target content under a "regular" name. The fault-injection matrix should not claim race coverage. Flag it to CritRace; it is not a C1 obligation.
4. The page's advice to "use the `os.path.is*()` functions" for type tests would be the wrong choice here. `os.path.isfile` follows links (round-21 RevengeInstallTreeIntent L12), so it would admit symlinks as members and change the regular-file map. Keep `lstat` + `S_ISREG` exactly as it is.
5. Matrix symlink and non-regular controls: a symlink to a member and a FIFO must stay absent from `tree` on both the frozen and current arms, with the digest unchanged versus the same tree without them. This is the positive control the row would back.

## Redundancy check against current rows
- `corpus/SOURCES.md` registry (S001–S074): no row cites `library/stat.html`, `S_ISREG` or `S_ISLNK`. The only Python rows are S044/S064 (subprocess), S051 (exceptions) and S061/S065 (sys.exit), all on different scopes.
- Prior exclusion: the round-21 search log (`corpus/SOURCES.md` L105) says the "Python os/stat" source was excluded because no C1/C2 statement rested on it. Round 22 changes that premise for one statement only: C1's acceptance requires the successful map/digest and the symlink semantics to stay unchanged. That is a mechanism premise, and this page is its type half. If L1 judges the matrix controls self-evident without a citation, the round-21 exclusion still stands; record it as excluded again in the round-22 search log rather than as a row.

## Draft row (contract v1, 11 cells; NOT written to SOURCES; ID reserved for L1)
| S0?? (L1: next S075) | Python 3.14 `stat` — Interpreting stat() results — https://docs.python.org/3.14/library/stat.html | docs | A | file-type predicates over one `st_mode` value (`S_ISREG` vs `S_ISLNK`, via `S_IFMT`) on Python 3.14.8; not lstat's no-follow behavior (os.html), not error handling, not race-free classification | §file-type test functions `#stat.S_ISREG`, `#stat.S_ISLNK`; `#stat.S_IFMT`; page titled Python 3.14.8 documentation, footer "Last updated on Oct 21, 2026 (10:01 UTC)"; HTML sha256 9a9c4fe8f7635943dc1be7c47c76f33ec7e5e397e559e28422af0d8ef1a80a5d; opened 2026-10-21 | `S_ISREG` and `S_ISLNK` test the single file-type field of a captured mode, so an lstat-classified symlink is never a regular member; refusing on I/O errors must leave this type skip unchanged. | queued | 2026-10-21 | on-release | — |

- Tier A: official CPython documentation, versioned to the host interpreter (3.14.8), scoped to type predicates only.
- Status `queued`. Flip to `mined` only when a round-22 lesson or knowledge path that exists at census time lists the row in used-by for the symlink/non-regular preservation control. Flip to `rejected` (excluded in the search log) if L1 decides no C1 sentence cites type classification.
- Pairing: if L1 needs the full "symlinks are skipped" chain, it also needs an `os.lstat` row anchored at `library/os.html#os.lstat`, re-opened this round. Round-21 SrcPythonReadlink Q2 has the quote, but that page was not re-opened here.
- Recheck flip: the 3.14 page changes the S_IS* wording, or the producer stops classifying with `lstat` (for example, moves to `os.scandir` `DirEntry.is_file(follow_symlinks=False)`; see seat SrcScandir).

## Search-log line for L1
Identified 1, screened 1 (re-open of the round-21-excluded stat.html; byte-identical). Proposed 1 queued row. Stop: the page carries only the type half; errors and refusal rest on the lane matrix.

## Hygiene
- Installs or updates: none. Tools used: Cursor WebFetch, `/usr/bin/curl` (stdout only, nothing written), `sha256sum`, `rg`.
- Edits: only this report. SOURCES, production code and the lane checkout were not touched. No verification runs; no processes left running.
- Owned path: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/build/advice/SrcStat.md`.
