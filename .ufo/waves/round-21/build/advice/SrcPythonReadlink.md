VERDICT: confirm - Python 3.14.8 os/stat docs (opened 2026-10-21) ground each semantic install_links() relies on; draft row S066 is queued and census-clean in a scratch copy.

# SrcPythonReadlink — round 21 draft row S066 (KamaR21 leaf)

## Sources opened, 2026-10-21
- https://docs.python.org/3.14/library/os.html — `curl -fsSL` exit 0; 739130 bytes; sha256 a88a57fd6da9cbe9c95954b693d65cb7a14bbbab455477fab8c1cd65ad4eda11; title "os — Miscellaneous operating system interfaces — Python 3.14.8 documentation"; footer "Last updated on Oct 21, 2026 (10:01 UTC)".
- https://docs.python.org/3.14/library/stat.html — exit 0; 67792 bytes; sha256 9a9c4fe8f7635943dc1be7c47c76f33ec7e5e397e559e28422af0d8ef1a80a5d; same title line and footer.
- Both pages carry `<link rel="canonical">` to the unversioned `/3/` URL, which serves 3.15 (per S044/S051 notes); the row cites the `/3.14/` URL.
- Host `python3 --version`: Python 3.14.8, exit 0.

## Verbatim quotes (raw HTML, exact-substring check; word counts)
- Q1 os.listdir, §Files and Directories, #os.listdir (24): "The list is in arbitrary order, and does not include the special entries '.' and '..' even if they are present in the directory."
- Q2 os.lstat, §Files and Directories, #os.lstat (9): "Similar to stat(), but does not follow symbolic links."
- Q3 os.stat, §Files and Directories, #os.stat (16): "This function normally follows symlinks; to stat a symlink add the argument follow_symlinks=False, or use lstat()."
- Q4 os.readlink, §Files and Directories, #os.readlink (10): "The result may be either an absolute or relative pathname"
- Q5 stat.S_ISLNK, stat §Interpreting stat() results, #stat.S_ISLNK (10): "Return non-zero if the mode is from a symbolic link."
- Q6 os.readlink, same entry (6): "the call may raise a UnicodeDecodeError"
- Q7 os.listdir, same entry (10): "whether a name for that file be included is unspecified"
- Q8 os module introduction, Note block (21): "All functions in this module raise OSError (or subclasses thereof) in the case of invalid or inaccessible file names and paths"

## Draft row S066 (contract v1, 11 cells; NOT written to corpus/SOURCES.md; insert after line 77)
| S066 | Python 3.14 `os` module — Miscellaneous operating system interfaces — https://docs.python.org/3.14/library/os.html | docs | A | link identity and listdir name order for kama's install-link digest; not llama.cpp's link layout, Windows reparse points or loader link resolution | §Files and Directories: `os.listdir` (#os.listdir), `os.lstat` (#os.lstat), `os.stat` (#os.stat), `os.readlink` (#os.readlink); stat module §Interpreting stat() results, `stat.S_ISLNK` (https://docs.python.org/3.14/library/stat.html, #stat.S_ISLNK); both titled Python 3.14.8 documentation, footer "Last updated on Oct 21, 2026 (10:01 UTC)"; fetched HTML sha256 a88a57fd6da9cbe9c95954b693d65cb7a14bbbab455477fab8c1cd65ad4eda11 (os), 9a9c4fe8f7635943dc1be7c47c76f33ec7e5e397e559e28422af0d8ef1a80a5d (stat) | Why a link-identity digest sorts `os.listdir` names and reads each entry with `os.lstat` plus `stat.S_ISLNK`: `os.stat` follows symlinks by default and listdir order is arbitrary; `os.readlink` returns the target path, which may be relative. | queued | 2026-10-21 | on-release | — |

Copy: out/SrcPythonReadlink/draft-row-S066.md.

## Census (contract commands; every command exit 0)
- Baseline, lane a29bb84 SOURCES.md: rows 65; malformed 0; A=62 C=3; mined=52 queued=6 rejected=7; no duplicate ids; max id S065. Matches the frontier census.
- No prior row: grep for readlink|listdir|S_ISLNK|library/os.html|library/stat.html gives 0 matches (grep exit 1). S066 unused (grep exit 1).
- Candidate, row inserted after line 77 in a scratch copy: rows 66; malformed 0; A=63 C=3; mined=52 queued=7 rejected=7; no duplicates; no enum or tier-inflation violations; S066 has 13 fields; mined used-by paths missing 0. Saved: out/SrcPythonReadlink/census-candidate.txt.
- First draft lacked the trailing `|`; the census caught it (malformed=1, S066 NF=12). Corrected before the recorded run.

## Mapping to install_links() at a29bb84 (tools/kama-llamacpp-live.py)
- L214 `sorted(os.listdir(directory))` ← Q1, Q7: order unspecified, so sorting is required for a deterministic digest.
- L220 `stat.S_ISLNK(os.lstat(full).st_mode)` ← Q2, Q5; Q3 says stat would follow the link.
- L221 `os.readlink(full)` ← Q4. tests/llamacpp-live/check-receipt.py L181-198 accepts only same-directory basenames, consistent with a relative-text reading.
- L224-225 digest over sorted `name -> text` lines.

## Observations (scratch; host Python 3.14.8, linux posix)
- `python3 probe_links.py`, exit 0 (out/SrcPythonReadlink/probe_links.out.txt): listdir not sorted; readlink returns relative text unchanged; absolute link returns an absolute path; lstat S_ISLNK True; stat follows (S_ISREG True); readlink on a regular file gives EINVAL (22).
- Soname retarget in a temp dir: links digest changed True; regular-only digest changed False (the R19 gap in microcosm).
- Read-only listing of ~/.local/opt/llama-b11755 (no writes): 61 entries, listdir not sorted, 10 symlinks, all relative same-directory targets, two-hop chains (libllama.so -> libllama.so.0 -> libllama.so.0.7.0).

## Scope against C1 / C2
- C1 (report landing audit): this source does not bear on it.
- C2 (symlink-aware identity): supports the mechanism only (Q1–Q5). The full claim rests on the lane grid and receipts, not on this row.
- [INFERENCE] The docs do not say readlink text is byte-verbatim; that property belongs to POSIX readlink(2), which I did not open. Do not cite S066 for it.
- Gap for L1/critic, not a row claim: install_links() L222-223 and install_tree() L190-199 `except OSError: continue` silently drop entries. Q7 makes a name removed mid-scan unspecified, so a drop is indistinguishable from absence: fail-open. Severity low for a static tree [INFERENCE].
- Q6: readlink "may raise a UnicodeDecodeError" (a ValueError, not OSError), which would escape install_links()'s `except OSError`. Probably unreachable on POSIX with the default surrogateescape handler and an ASCII tree [INFERENCE].

## Proposed status
- `queued`, used-by `—`, recheck `on-release`, opened 2026-10-21. Flip to `mined` only when a lesson or knowledge path that exists at census time lists S066 in used-by.
- The round Gate needs URL, access date 2026-10-21, and Q1 with §Files and Directories / #os.listdir.

## Hygiene
- Installs or updates: none. Tools: curl (/usr/bin/curl), git (clone; read-only commands), python3 3.14.8 (host).
- Lane: no edits. One read-only `git status --porcelain -- corpus/SOURCES.md` ran in the lane checkout; it may refresh the index stat cache, with no content change. Disclosed.
- Scratch /tmp/kama-r21-SrcPythonReadlink deleted at the end. No processes started.
- Deliverables: out/SrcPythonReadlink/{probe_links.py, probe_links.out.txt, draft-row-S066.md, census-candidate.txt}.
