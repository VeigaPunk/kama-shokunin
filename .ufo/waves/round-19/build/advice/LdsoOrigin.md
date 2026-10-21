VERDICT: partial - the $ORIGIN sentence is verbatim on the opened page; with a loader fixture it licenses same-directory sibling lookup for a binary's direct DT_NEEDED entries only, below LD_LIBRARY_PATH. The lane's ellipsis quote and "14 words" are not verbatim, and "launcher bytes do not identify" and "not authentication" are [INFERENCE], not S057.

Scope: LdsoOrigin, round 19. Lane not modified; work in /tmp/kama-r19-LdsoOrigin (receipts in its out/: receipt.txt from repro.py, install_tree_probe.txt, gate-quote.md). Installs or updates: none.

## Page evidence (ld.so(8), opened 2026-10-21)
- Fetch: `curl -sS -o ld.so.8.html https://man7.org/linux/man-pages/man8/ld.so.8.html` exit 0; 41398 B; sha256 d9b7737e…379f83 (same as DraftS057's receipt). Man-pages 6.19, dated 2026-08-03.
- $ORIGIN definition, verbatim (1 hit, 15 words; receipt G1), under DESCRIPTION > bold run-in "Dynamic string tokens":
  "$ORIGIN (or equivalently ${ORIGIN}) This expands to the directory containing the program or shared object."
- Tokens are expanded inside DT_RUNPATH values (S1, 1 hit): "inside the values of the dynamic section tags DT_NEEDED, DT_RPATH, DT_RUNPATH, DT_AUDIT, and DT_DEPAUDIT of ELF binaries"
- Search order: step (2) "Using the environment variable LD_LIBRARY_PATH, unless the executable is being run in secure-execution mode" precedes step (3) DT_RUNPATH (S2, S3).
- Step (3) scope (S4): "do not apply to those objects' children, which must themselves have their own DT_RUNPATH entries."
- Stated purpose (S5): "can instead be unpacked into any directory and still find their own shared objects." The page's example is `$ORIGIN/../lib` (S6). Same-directory `$ORIGIN` follows from the definition [INFERENCE]; fixture A confirms it.
- Zero hits: digest, authentic, checksum, sha256, signature, integrity, trust, launcher, identity, symbolic link, symlink. The only "verify" is `--verify` (S7): "Verify that program is dynamically linked and this dynamic linker can handle it." That is a linkage check, not content authentication.

## Lane text defects (not edited; for the lane owner)
- round-19.md:27 and SOURCES.md:69 quote 2 use "$ORIGIN ... expands to ..." and claim "14 words". That form has 0 contiguous hits (receipt X1). Excluding the ellipsis it is 11 words; no reading gives 14. Replace with the verbatim 15-word quote below.
- Quote 1 ("are searched only to find those objects required by DT_NEEDED") is 10 words (receipt X2), not 11 as round-19.md:28 and SOURCES.md:69 say.
- round-19.md:27 "a launcher's bytes do not identify the libraries it loads" and row 29 "same page: ... identity is not authentication" are not on the page. Mark them [INFERENCE] or drop the "same page" citation.

## Second S057 Gate quote (verbatim, 15 words, ≤25)
> "$ORIGIN (or equivalently ${ORIGIN}) This expands to the directory containing the program or shared object."
Section: DESCRIPTION > Dynamic string tokens. Full text in out/gate-quote.md.

## One-line admission scope
Identity boundary, not authentication: DT_RUNPATH `$ORIGIN` sets the search directory for a binary's direct DT_NEEDED entries (after LD_LIBRARY_PATH, not their children); S057 says nothing about whether the bytes found are authentic.

## Does it license a launcher sibling from its own directory?
Yes, as documented loader mechanism for the launcher's direct DT_NEEDED entry. No for children, for precedence over LD_LIBRARY_PATH, or for trust in the bytes found. "License" as a normative reading is [INFERENCE]; the page describes behavior.

## Loader fixture (glibc 2.44, /lib64/ld-linux-x86-64.so.2, out/fixture; receipt.txt; 9/9 PASS)
| case | command | exit | observed |
|---|---|---|---|
| A | `ld.so --list tree/app` (launcher RUNPATH, sibling RUNPATH) | 0 | libsib.so and libchild.so resolve in tree/ |
| B | `ld.so --list tree/app2` (sibling has no RUNPATH) | 127 | libchild.so not found: launcher RUNPATH does not reach children (S4) |
| C | `ld.so --list bin/app` (symlink into tree) | 0 | resolves in the real directory |
| D | `LD_LIBRARY_PATH=envlib ld.so --list tree/app` | 0 | envlib/libsib.so wins over RUNPATH (S2) |
| E / F | exec tree/app / exec tree/app2 | 0 / 127 | matches A / B |
| H / I | exec bin/app / exec tree/app, LD_DEBUG=libs | 0 / 0 | trace tries tree/libsib.so; never bin/ |
| G | with tree/glibc-hwcaps/x86-64-v2/libsib.so present, `ld.so --list tree/app` | 0 | hwcaps copy shadows the top-level sibling (S8 "preferred") |

Symlink resolution to the real directory (C, H) is observed here, not stated by S057 (zero hits for "symbolic link").

## Pin coverage (C2 side; executed)
- `install_tree()` (tools/kama-llamacpp-live.py:178-202, extracted by AST and run unmodified; out/install_tree_probe.py, exit 0; 4/4 PASS): it digests top-level regular files only. A subdirectory shadow (S) and a symlink retargeted outside the tree (L) leave the combined digest unchanged; a regular-file rewrite (R) changes it.
- Host tree today (read-only `find`, exit 0): 0 subdirectories; 10 symlinks, all resolving inside the tree. The gap is latent, not active.
- Implication: the admission scope above is correct. Any C2 wording that the pin identifies "the libraries loaded" must add that the pin covers top-level regular files only.

## Install record
None. No tools installed or updated. gcc, readelf, and ld.so were already present.

## Not checked
- Other glibc versions (only 2.44 here). Whether registry/required-citations.json cites S057 by the same id (not inspected).
