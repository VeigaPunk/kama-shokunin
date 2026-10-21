# S066 draft row — Linux ld.so(8) search order (scout: KamaR21.SrcLdSoNeeded-6, 2026-10-21)

Full findings: .ufo/waves/round-21/build/advice/SrcLdSoNeeded.md
Source opened this round: https://man7.org/linux/man-pages/man8/ld.so.8.html
man-pages 6.19, page 2026-08-03; raw sha256 d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83
`symlink|symbolic`: zero matches in the page (case-insensitive). Proposed status queued.

| S066 | Linux ld.so(8) search order for a soname without a slash — https://man7.org/linux/man-pages/man8/ld.so.8.html | docs | A | DT_NEEDED soname lookup mechanics behind C2 install identity: the bare soname a launcher needs is re-resolved by ordered directory search at every exec, so which file `libllama.so.0` names is live install state that a regular-file-only pin cannot see; page is silent on symlink resolution | §DESCRIPTION search-order preamble plus steps (4) and (5); man-pages 6.19, page dated 2026-08-03, tarball man-pages-6.19.tar.gz fetched 2026-09-09; raw sha256 d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83 | "If a shared object dependency does not contain a slash, then it is searched for in the following order" (19 words, §DESCRIPTION); "From the cache file /etc/ld.so.cache, which contains a compiled list of candidate shared objects previously found in the augmented library path" (21 words, step (4)); flip: superseded on a man-pages search-order change; to mined when a corpus/knowledge entry cites it for C2 | queued | 2026-10-21 | on-release | — |
