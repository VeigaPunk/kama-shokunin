VERDICT: partial - ld.so(8) (man-pages 6.19) reachable; distinct search-order/cache quotes support C2's soname-lookup premise; the page never mentions symlinks, so the "found file can be a symlink" half is not supported by this source.

Axes: operability 8, calibration 7 (assigned). This seat = calibration-facing source scout; no code touched, no lane mutation.

# Executed commands (all run this session)
1. `curl -sS -L -o /tmp/kama-r21-SrcLdSoNeeded/ld.so.8.html https://man7.org/linux/man-pages/man8/ld.so.8.html; echo curl_exit=$?; wc -c ...` → curl_exit=0, 41398 bytes.
2. `sha256sum` on that file → d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83
3. grep (case-insensitive) `symlink|symbolic` over the fetched page → "No matches found".
4. grep `S06[0-9]|man7\.org/linux/man-pages/man8` over corpus/SOURCES.md → rows end at S065 (line 77); S057 (line 69) is the only man7 man-pages row; S066 unused. Source is NOT already a row under a new id, and my anchors are distinct from S057's (see below).
5. `curl ... ldconfig.8.html` → curl_exit=0, 11926 bytes, sha256 6a81540a534692ed7cb6d5434275e08b3ade388311bdb88f1e4e506be2bfde38 (lead only, see §Symlink half).
No tool installs or upgrades performed (tooling directive: nothing needed beyond curl/grep already present).

# Source facts (ld.so(8), man7.org)
- URL: https://man7.org/linux/man-pages/man8/ld.so.8.html — accessed 2026-10-21.
- Revision: footline "Linux man-pages 6.19  2026-08-03  ld.so(8)"; colophon: page "obtained from the tarball man-pages-6.19.tar.gz" fetched 2026-09-09.
- Observed text (§DESCRIPTION, search-order paragraph): "When resolving shared object dependencies, the dynamic linker first inspects each dependency string to see if it contains a slash" ... "(1) DT_RPATH ... (2) LD_LIBRARY_PATH ... (3) DT_RUNPATH ... (4) /etc/ld.so.cache ... (5) In the default path /lib, and then /usr/lib".

# Symlink half: NOT in this source
Case-insensitive grep for `symlink|symbolic` over the whole page returns zero matches. ld.so(8) describes where a slash-less dependency name is searched but never states that the found candidate may be a symlink; open(2)/readlink resolution semantics are out of its scope. No quote for that half is invented.

# Where the symlink half actually lives (lead, opened 2026-10-21, not drafted — one-row cap)
ldconfig(8) same tarball (sha256 above): §DESCRIPTION "ldconfig creates the necessary links and cache to the most recent shared libraries" (13 words) and §DESCRIPTION "ldconfig expects a certain pattern to how the symbolic links are set up, like this example, where the middle file (libfoo.so.1 here) is the SONAME for the library" (verbatim; location: §DESCRIPTION, symlink-pattern example intro). This is the candidate source if the L1 wants a row pinning soname-symlink semantics. Left unrowed; L1 decides.

# Draft row (contract v1, 11 cells; proposes S066; final id/order is the L1's)
| S066 | Linux ld.so(8) search order for a soname without a slash — https://man7.org/linux/man-pages/man8/ld.so.8.html | docs | A | DT_NEEDED soname lookup mechanics behind C2 install identity: the bare soname a launcher needs is re-resolved by ordered directory search at every exec, so which file `libllama.so.0` names is live install state that a regular-file-only pin cannot see; page is silent on symlink resolution | §DESCRIPTION search-order preamble plus steps (4) and (5); man-pages 6.19, page dated 2026-08-03, tarball man-pages-6.19.tar.gz fetched 2026-09-09; raw sha256 d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83 | "If a shared object dependency does not contain a slash, then it is searched for in the following order" (19 words, §DESCRIPTION); "From the cache file /etc/ld.so.cache, which contains a compiled list of candidate shared objects previously found in the augmented library path" (21 words, step (4)); flip: superseded on a man-pages search-order change; to mined when a corpus/knowledge entry cites it for C2 | queued | 2026-10-21 | on-release | — |

Word counts: 19 (preamble) and 21 (step 4), each <=25, quoted verbatim from the rendered page text; locations given per quote. Distinct from S057, which anchors step (3) DT_RUNPATH scope + $ORIGIN tokens; this row anchors the no-slash preamble, the cache step (4) and default-path step (5).

# Claim mapping
- C2 (symlink-aware install identity): SUPPORTED on the soname-lookup premise only — runtime resolution of the bare DT_NEEDED name is a live directory/cache search, so a retargeted soname link changes what the loader names without touching any pinned regular file. The symlink-resolution mechanism itself is NOT supported by this source (grep evidence above); ldconfig(8) lead covers it.
- C1 (report landing audit): unaffected; no support or refutation.

# Proposed status and reason
- queued: opened this round with located quotes, but nothing in corpus/knowledge cites it yet.
- Flip to mined when a corpus/knowledge entry (e.g. the round-21 soname entry) cites it for C2. Flip to rejected if the L1 judges S057's scope ("grounds an install-tree identity pin") already subsumes it — then the ldconfig(8) lead becomes the better C2 row instead.
