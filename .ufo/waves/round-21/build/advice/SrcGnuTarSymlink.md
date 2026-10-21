VERDICT: partial - GNU tar 1.35 manual (read from its signed release tarball) confirms link-text-by-default versus `-c -h`: narrow prior art for C2's link-text record; no C1 bearing; supports no digest or loader claim
# SrcGnuTarSymlink - GNU tar symlink archiving (round 21, build wave)
Lane kama-shokunin at draft a29bb84 (not modified). Access date 2026-10-21. Scout KamaR21.SrcGnuTarSymlink-6.

## Source
- Canonical node `https://www.gnu.org/software/tar/manual/html_node/dereference.html`: NOT reached. `curl` exit 28 (25 s); `read` of www.gnu.org pages "Method: failed ... timed out".
- Opened: `https://ftp.gnu.org/gnu/tar/tar-1.35.tar.xz`, HTTP 200, 2,317,208 bytes, sha256 4d62ff37342ec7aed748535323930c7cf94acf71c3591882b26a7ea50f3edc16. Member `tar-1.35/doc/tar.texi` (13,430 lines), sha256 221e9ac4f5b9e0465b5766308cbd948c4cb370cfe85d58072476f47c18ce843b. `doc/version.texi`: `@set VERSION 1.35`, `@set UPDATED 10 July 2023`.
- Signature: `gpg --verify` against `https://ftp.gnu.org/gnu/gnu-keyring.gpg` (sha256 0fe55175b96a8ea1c4b670cc3fe11d56b341e4eff81b161ea49958ae550be6ca): "Good signature from Sergey Poznyakoff <gray@gnu.org>", key 325F650C4C2B6AD58807327A3602B07F55D0C732, made 18 Jul 2023, "not certified with a trusted signature". Exit 0, run twice.
- Local `tar --version`: "tar (GNU tar) 1.35". No existing GNU tar row: corpus grep for `software/tar|GNU tar|tar.texi|dereference` matched only S033 (`dereferenced`, a different source).

## Quotes (verbatim; texinfo markup removed; node `dereference`, "Symbolic Links", under "Making tar Archives More Portable")
- Q1, 20 words, texi 10353-10354: "Normally, when tar archives a symbolic link, it writes a block to the archive naming the target of the link."
- Q2, 15 words, texi 10354-10355: "In that way, the tar archive is a faithful record of the file system contents."
- Q3, 13 words, texi 10357-10359: "tar archives the files symbolic links point to, instead of the links themselves."
- Companion, not drafted (one row requested), node `hard links`, texi 10406-10408, 20 words: "tar stored it only once, under the name jeden, and stored file one as a hard link to this file."
- Every fragment checked with `grep -n -F` on the extracted texi: exit 0 each.

## Observations (own-work; `build/out/SrcGnuTarSymlink/tar-link-experiment.sh`, log `.log`, exit 0)
Tree: regular `llama/libggml.so.0.0.0`, identical-bytes `libggml.so.0.0.1`, link `libggml.so.0` -> A: `.0.0.0`, B: `.0.0.1`. Archives built with `--mtime=@0 --owner=0 --group=0 --numeric-owner --sort=name`.
- O1 `-c`: archives differ (default-A 78843fc7..., default-B fc4a3a0d...). Only the link text changed: `-> libggml.so.0.0.0` vs `-> libggml.so.0.0.1`.
- O2 `-c -h`: archives differ (deref-A baed3e72..., deref-B e9a83b9f...) though every followed file has identical bytes. `tar -tvf` moves the hard-link record (A: `libggml.so.0.0.0 link to llama/libggml.so.0`; B: `libggml.so.0.0.1 link to llama/libggml.so.0`), per the companion passage.
- O3 read-only: `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` (22,240,468 bytes) lists 10 symlink members. Their name -> link-text set equals the 10 top-level symlinks of `~/.local/opt/llama-b11755` (`diff` exit 0). The installed tree has 51 regular files at top level. `install_tree` pins regular files only (`corpus/lessons/round-19.md:53-57`).

## C1 / C2
- C1 (report landing audit): none.
- C2 (symlink-aware install identity): supports, narrowly. Q1/Q2 make the link text the default faithful record of a symlink, and O1 is exactly the change the default archive records. That matches `install_links` (readlink text) as a datum separate from `install_tree` (regular bytes). [INFERENCE: the split mirrors the default archive; it is not evidence the lane's code is correct.]
- Not supported by this source: chain-to-pinned-member checks, loops, dangling or shadowing rules, loader resolution (S057), digest authentication, representativeness of the 13 grid cells.
- Boundary from O2: a `tar -h`-style identity changes with aliasing alone, so it must not serve as install identity without addressing that.

## Draft row (exact line in `build/out/SrcGnuTarSymlink/row-S066.txt`)
```
| S066 | GNU tar 1.35 manual, §Symbolic Links — https://www.gnu.org/software/tar/manual/html_node/dereference.html (canonical page not fetched: www.gnu.org timed out 2026-10-21; opened as doc/tar.texi in https://ftp.gnu.org/gnu/tar/tar-1.35.tar.xz) | docs | A | GNU tar 1.35 archive member written for a symbolic link: link text by default, linked-to files under `-c -h`; not digest, identity or loader semantics | §Symbolic Links (texi node `dereference`, lines 10347-10359; parent §Making tar Archives More Portable); `@set VERSION 1.35`, `UPDATED 10 July 2023` (doc/version.texi); tarball sha256 4d62ff37342ec7aed748535323930c7cf94acf71c3591882b26a7ea50f3edc16, doc/tar.texi sha256 221e9ac4f5b9e0465b5766308cbd948c4cb370cfe85d58072476f47c18ce843b; signature good (Sergey Poznyakoff, key 325F650C4C2B6AD58807327A3602B07F55D0C732, signed 2023-07-18; not WoT-certified) | GNU tar's default archive names a symlink's target instead of copying the target's files, which the manual says keeps the archive a faithful record; only `-c -h` archives the linked-to files. | queued | 2026-10-21 | on-release | — |
```
- Id S066 = next unused at a29bb84 (highest S065). Sibling scouts drafting rows this round may claim S066 too; the L1 must assign ids serially at integration.
- Status `queued`. `mined` needs a used-by path that exists (census missing check); nothing cites this row yet. Flip: a knowledge entry or the round-21 lesson cites it, the used-by cell names that path, and status becomes `mined`.
- Gate lines if admitted: URL https://ftp.gnu.org/gnu/tar/tar-1.35.tar.xz (member doc/tar.texi; canonical HTML not reached), access 2026-10-21, quote Q1, §Symbolic Links, texi 10353-10354.

## Validation (scratch copy of the lane registry, final tag 8CA4; lane untouched)
- Census per CORPUS.md commands, run from scratch lane root: rows 66 (was 65); malformed 0; tiers A=63 C=3; status mined=52 queued=7 rejected=7; duplicate ids none; enum/inflation none; mined used-by missing none.
- `scripts/sources-census.sh validate --file <copy> --today 2026-10-21`: "file ok", exit 0. Only pre-existing W04 warnings (S031, S043, S056, S060, S064, S065); none on S066.
- Caught and fixed: first draft lacked the closing `|` (NF=12). Re-run clean.

## Limits
- Quotes come from the release texi; the HTML rendering was not compared (unreachable). The `dereference.html` filename is [INFERENCE] from `@node dereference`.
- Signature checked against GNU's keyring only; the key is not web-of-trust certified.
- O1-O3 cover one synthetic tree on tar 1.35 and one read-only archive/tree pair. No claim about other tar versions.
- That the retained tarball is the archive the installed tree came from is [INFERENCE]; not verified here.

## Tooling record
- Installs or updates: none. Present tools used: curl 8.23.0, gpg 2.4.9 (/usr/bin/gpg), tar 1.35, find, diff, sort, awk, grep, sed (read-only pipelines only).
- Persistent processes started: none. Scratch `/tmp/kama-r21-SrcGnuTarSymlink` removed at finish.

## Files
- `.ufo/waves/round-21/build/advice/SrcGnuTarSymlink.md` (this report)
- `.ufo/waves/round-21/build/out/SrcGnuTarSymlink/`: `tar-link-experiment.sh`, `tar-link-experiment.log`, `row-S066.txt`, `provenance-sha256.txt`, `gpg-verify.txt`
