VERDICT: confirm - LDP Program Library HOWTO §3.1.1 (version 1.20, 2003) states that a soname is a symbolic link to the real name; draft row S066 is queued tier B, supports the C2 premise only, and has no C1 bearing.

# SrcTldpSoname: Program Library HOWTO §3.1.1 (opened 2026-10-21)

## Source and revision (executed)
- URL: https://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html#AEN49, section 3.1.1 "Shared Library Names" (`<A NAME="AEN49">`, raw line 119). `curl` → `http=200 bytes=28706`; a rerun is byte-identical (`cmp` exit 0).
- Revision: HOWTO "version 1.20, 11 April 2003" (index raw line 36, `CLASS="PUBDATE"`); HTTP `last-modified: Fri, 11 Apr 2003 23:07:25 GMT`. The page's `meta GENERATOR` names the DocBook stylesheet 1.7, not the HOWTO revision.
- Access date: 2026-10-21 (HTTP `date: Wed, 21 Oct 2026 10:46:31 GMT`).
- sha256: shared-libraries.html `61c31cade7efaab4b8101c5e4ac67eb8203df3aa621abf87e37e681817ac38f6`; index.html `9f798583410099a7589ec0bc88b569503e24b1304e84c17bb1867568f0200575`.

## Verbatim quotes (substring match on whitespace-normalised raw bytes: all FOUND)
- Q1, §3.1.1, raw 130-131, 18 words: on a working system a fully-qualified soname is simply a symbolic link to the shared library's ``real name''
- Q2, §3.1.1, raw 174-175, 16 words: installers must specifically modify symbolic links to update what the linker will use for a library
- Q3, §3.1.1, raw 156-157, 16 words: ldconfig examines the existing files and creates the sonames as symbolic links to the real names
- Q4, §3.5 "Installing and Using a Shared Library" (`AEN115`), raw 638-639, 20 words: you'll need to set up the necessary symbolic links, in particular a link from a soname to the real name
- Q5, §3.1.1 (linker name), raw 161-162, 19 words: the linker name is simply created as a symbolic link to the ``latest'' soname or the latest real name

## Draft row (contract v1)
S066 is the next unused id at census-before (65 rows, last S065). The L1 renumbers if another round-21 row lands first.

| S066 | Program Library HOWTO, §3.1.1 Shared Library Names — https://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html#AEN49 | docs | B | soname, real-name and linker-name roles of Linux shared-library filenames on a working system; not loader search order (S057) and not any distribution's current layout | §3.1.1 Shared Library Names (`#AEN49`), HOWTO version 1.20, 11 April 2003 (index PUBDATE; HTTP Last-Modified Fri, 11 Apr 2003 23:07:25 GMT); raw `shared-libraries.html` sha256 61c31cade7efaab4b8101c5e4ac67eb8203df3aa621abf87e37e681817ac38f6 fetched 2026-10-21 | On a working system the soname is a symbolic link to the real name that ldconfig creates, and installers change what the linker uses by modifying symbolic links. | queued | 2026-10-21 | 180d | — |

## Tier and status
- Tier B: strong secondary (an expert HOWTO by David A. Wheeler). It is not A, because it is neither official glibc/ld.so documentation nor a maintainer statement. Scope is naming roles only; loader search order stays with S057 (A).
- Status queued: opened and quoted, but no knowledge entry or lesson cites it (`used-by —`). The contract requires a citing path for `mined`.
- Flip to mined: the L1 adds a citing knowledge path. The natural candidate is `corpus/knowledge/llamacpp-loading-lifecycle.md` lines 315-322 (round-19 sixth-pin note), which states the soname-symlink premise with no source.
- Flip to rejected: only if the L1 judges the premise covered by the A-tier ldconfig(8) page (companion below). A rejection would need `REJECTED: <reason>; flip: <what changes it>`.
- Recheck 180d: the content has been static since 2003, so the cadence checks URL liveness and revision drift. [INFERENCE] S021's URL rot shows why liveness matters.

## C1 / C2 mapping
- C2 premise supported: Q1 (a soname entry is a symlink to the real name), Q3 (ldconfig creates it), Q2 (installers change the linker's target by editing symlinks). This underlies the R19 TreeCap debt: `install_tree()` skips links, so a soname retarget is invisible to it.
- Host check (read-only `find -maxdepth 2 -type l`, exit 0): `~/.local/opt/llama-b11755` holds 10 symlinks, five soname links (e.g. `libllama.so.0 -> libllama.so.0.7.0`) and five linker-name links (e.g. `libllama.so -> libllama.so.0`). Both classes exist, as Q1-Q5 describe.
- [INFERENCE] Q5 gives linker-name links a different creator (installers, not ldconfig). `install_links()` should therefore enumerate all symlinks rather than only `*.so.N`. I did not check the lane code for this.
- Not supported by this source: the `install_links()` implementation, the gate, and the grid results. The page says nothing about digests.
- C1 (report landing audit): no bearing.

## Companion lead (not drafted; one-row bound)
- ldconfig(8), man-pages 6.19 (footer `Linux man-pages 6.19 2026-08-03`), §DESCRIPTION, https://man7.org/linux/man-pages/man8/ldconfig.8.html; raw Last-Modified Thu, 08 Oct 2026 17:39:35 GMT; sha256 `6a81540a534692ed7cb6d5434275e08b3ade388311bdb88f1e4e506be2bfde38` (tags stripped for matching).
- Q7: "ldconfig expects a certain pattern to how the symbolic links are set up" (13 words). Q8: "where the middle file (libfoo.so.1 here) is the SONAME for the library" (12 words).
- This is a tier A candidate for the link-chain pattern. The L1 decides whether to draft it.

## Census on candidate (copy of corpus/SOURCES.md with the row inserted after line 77; lane untouched)
- Rows: 66 (lane baseline 65). Malformed (NF!=13): 0. Tier histogram: A=62 B=1 C=3. Status histogram: mined=52 queued=7 rejected=7.
- Duplicate ids: none. Enum and tier-inflation violations: none. Missing mined used-by paths: none (cwd = lane root).
- All census commands exited 0 (eight invocations, including the lane baseline row count). They are the contract's census block, pointed at the candidate.

## Coordination, tools, cleanup
- Messaged KamaR21.KnowledgeSonameEntry-6 (delivered) to avoid an S066 collision.
- Tools installed or updated: none. Used `/usr/bin/curl`, `sha256sum` and `find` as found.
- Out dir `build/out/SrcTldpSoname/`: shared-libraries.html (28706 B), index.html (4374 B), ldconfig.8.html (11926 B), S066-registry.diff (848 B, sha256 `7eac818f85bcbf9f0ac49484372eae53a68fbd30ff2b396e3655331fb1db5f38`).
- Scratch `/tmp/kama-r21-SrcTldpSoname` removed after this report was written.
- Lane: no edits and no git commands run in the lane.
