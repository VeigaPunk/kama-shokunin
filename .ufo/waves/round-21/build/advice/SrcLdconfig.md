VERDICT: partial - ldconfig(8) (man-pages 6.19) grounds C2's soname-chain premise and refutes nothing; it never names DT_SONAME, so the link-name tie rests on the gABI and GNU ld texts plus a readelf observation, not on this row.

Scope: one draft row (S066, `queued`) for kama. No lane file touched. C1: no bearing. Access date 2026-10-21 (`date -u +%F`, exit 0). Tools installed or updated: none. Scratch `/tmp/kama-r21-SrcLdconfig` removed (`rm -rf`, exit 0).

## Source and revision
- URL https://man7.org/linux/man-pages/man8/ldconfig.8.html, fetched 2026-10-21 (`curl -sS -D ... -o ...`, exit 0). Raw HTML 11926 B, sha256 6a81540a534692ed7cb6d5434275e08b3ade388311bdb88f1e4e506be2bfde38 (`sha256sum`, exit 0). Last-Modified Thu, 08 Oct 2026 17:39:35 GMT. Footer "Linux man-pages 6.19 2026-08-03".
- Current: kernel.org mirror index (`read`) lists man-pages-6.19.tar.xz (25-Aug-2026) as newest. Tarball fetched (`curl`, exit 0); sha256 88a7c42ad2e03d8b96dc72d95e451f2d875ff0f43103a8eb8ac8242133bdcb05 (`sha256sum`, exit 0) equals its line in sha256sums.asc. PGP signature NOT verified [INFERENCE: no key check run].
- Tarball `.TH` footer reads "Linux man-pages (unreleased)". Installed `/usr/share/man/man8/ldconfig.8.gz` (`pacman -Qo`: man-pages 6.19-1, exit 0) differs from the tarball only on that line (`zcat | diff -`, exit 1). Body identical.
- Unreachable: git.kernel.org `plain/man8/ldconfig.8` returned HTTP 404 (wrong path; the tarball holds `man/man8/`). Not needed.

## Quotes (verbatim, ≤25 words; found in man7 HTML and upstream troff)
- Q1 §DESCRIPTION ¶1 (13 w): "ldconfig creates the necessary links and cache to the most recent shared libraries"
- Q2 §DESCRIPTION ¶2 (19 w): "checks the header and filenames of the libraries it encounters when determining which versions should have their links updated."
- Q3 §DESCRIPTION ¶3 (12 w): "where the middle file (libfoo.so.1 here) is the SONAME for the library"; example block `libfoo.so -> libfoo.so.1 -> libfoo.so.1.12`.
- Q4 §DESCRIPTION ¶3 (13 w): "Failure to follow this pattern may result in compatibility issues after an upgrade."
- Negative: `_grep` for `DT_|ELF` in man7 HTML and `DT_` in upstream troff: no matches. The page never names the DT_SONAME tag.

## How DT_SONAME relates to the link name
- ldconfig(8): the middle link "is the SONAME" (Q3). Q2's "header" is the nearest wording; no ELF or DT_ term.
- gABI ch5 (https://refspecs.linuxfoundation.org/elf/gabi4+/ch5.dynamic.html; undated page; opened, NOT drafted): §Dynamic Section, DT_SONAME "giving the name of the shared object"; §Shared Object Dependencies "Names in the dependency list are copies either of the DT_SONAME strings or the path names" (16 w).
- GNU ld 2.47 manual (https://sourceware.org/binutils/docs/ld/Options.html, §-soname=name): "set the internal DT_SONAME field to the specified name" (9 w).
- Observed, read-only (`readelf -d`, exit 0): libllama.so.0.7.0 has SONAME [libllama.so.0] and NEEDED [libggml.so.0], [libggml-base.so.0]; libggml.so.0.27.0 has SONAME [libggml.so.0].
- [INFERENCE] Composed chain: `-soname` sets DT_SONAME, consumers copy it into DT_NEEDED, the loader searches that name (S057), and ldconfig names the link after SONAME. The tree shows exactly that.

## Observed tree and lane (read-only)
- `find <llama tree> -maxdepth 1 -type l` (exit 0): 10 links in five 3-level chains (`libllama.so -> libllama.so.0 -> libllama.so.0.7.0`; same shape for ggml, ggml-base, llama-common, mtmd). This is the Q3 shape.
- Lane at a29bb84 (scratch clone, `git rev-parse`, exit 0): `_grep ldconfig` matches only .ufo advice notes (round-16 SentinelInstallChain.md:49, round-19 LdsoRunpath.md:19, both `ldconfig -p` observations). No tools/ or tests/ match, so the lane never runs ldconfig. The links' origin is [INFERENCE: release archive; asset not downloaded, 22 MB].

## C1 / C2 mapping
- C2 supported: soname links are managed chains ending at a real file (Q3 + tree); retargeting the SONAME link changes what loads (Q3 + NEEDED observation); a changed layout is an upgrade hazard (Q4).
- C2 NOT supported by this source: "no '/' targets" (the example uses bare names, consistent but not mandated); "no link shadowing a member"; any digest rule.
- C1: no bearing. Refutation found: none.

## Draft row (contract v1; copy at out/SrcLdconfig/S066-draft-row.md)
```
| S066 | Linux ldconfig(8) — https://man7.org/linux/man-pages/man8/ldconfig.8.html | docs | A | ldconfig's documented soname link layout and which link it calls the SONAME; not ldconfig's implementation, not the DT_SONAME tag | §DESCRIPTION paragraphs 2 and 3 (SONAME chain example and the sentence after it); man-pages 6.19, page dated 2026-08-03 (man7 footer "Linux man-pages 6.19"; tarball .TH footer "(unreleased)"; installed man-pages 6.19-1 identical to the tarball except that footer); tarball man-pages-6.19.tar.xz sha256 88a7c42ad2e03d8b96dc72d95e451f2d875ff0f43103a8eb8ac8242133bdcb05; man7 HTML sha256 6a81540a534692ed7cb6d5434275e08b3ade388311bdb88f1e4e506be2bfde38, fetched 2026-10-21 | Names the middle link of a soname chain (libfoo.so -> libfoo.so.1 -> libfoo.so.1.12) as the library's SONAME and warns that failing to follow that pattern may cause compatibility issues after an upgrade; the page never names DT_SONAME, so this row does not tie that tag to the link name. | queued | 2026-10-21 | on-release | — |
```
- Format: awk on the row (NF==13 and the contract enums): rows=1, no violations, exit 0. This is not the registry census; the L1 runs that.
- Id collision: S066 is also proposed by SrcLdSoNeeded (ld.so(8), tier A) and SrcTldpSoname (TLDP HOWTO §3.1.1, tier B). The L1 assigns final ids in write order after S065; the row body does not depend on the number. I sent no peer messages.
- Status `queued`: no path cites the row yet, and `mined` needs at least one existing used-by path. Flip to `mined` when a knowledge entry cites it; the natural site is corpus/knowledge/llamacpp-loading-lifecycle.md lines 318–322 (soname-symlink pin scope). Flip to `rejected` only if a later release drops the chain paragraph.
- Tier A is scoped to the layout claim: the maintainers' official man page, with S057 as precedent. It does not cover implementation or DT_SONAME.
- Recheck `on-release`, matching man-pages release cadence.

## Gate items for the L1 round lesson
URL https://man7.org/linux/man-pages/man8/ldconfig.8.html; access date 2026-10-21; Q1–Q4 with the locations above; revision man-pages 6.19, with the `.TH` caveat.

## Limits
- Documentation only: glibc elf/ldconfig.c not read; no ldconfig executed on any tree.
- The DT_SONAME tie rests on sources I opened but did not draft (one-row cap) and on one host's readelf output.
- Tarball PGP signature not verified.
