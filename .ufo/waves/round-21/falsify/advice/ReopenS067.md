VERDICT: partial - S067 URL, version, quote, status and used-by verify; teaches overstates (cache step dropped, "live state, not a launcher property" off-page), the anchor omits the step that grounds its own example, and the scope lacks glibc.

Attacked: row S067 (corpus/SOURCES.md:79) as committed at b76727f3 (blob sha256 cc623740..., identical to the worktree); round-21 Gate quote (corpus/lessons/round-21.md:43); used-by consumers (corpus/knowledge/llamacpp-loading-lifecycle.md:330 and :336). Scout ReopenS067, access date 2026-10-21. Lane not modified; scratch clone removed.

Re-opened source: https://man7.org/linux/man-pages/man8/ld.so.8.html. HTTP 200, no redirect, 41,398 B, sha256 d9b7737e...f83; response Date 21 Oct 2026 11:19:23 GMT; Last-Modified 08 Oct 2026 17:39:35 GMT. Raw copy and headers: .ufo/waves/round-21/falsify/out/ReopenS067/.
Footline line 715: "Linux man-pages 6.19 2026-08-03 ld.so(8)". Colophon lines 705-708: tarball man-pages-6.19.tar.gz, fetched 2026-09-09. HTML rendering created 2026-09-09 (line 756). Line numbers below refer to the saved HTML.

| Field | Verdict | Evidence |
|---|---|---|
| URL | agree | fetch above; no redirect in the header dump |
| title | agree (cosmetic) | row title is a paraphrase; page title per reader metadata is "ld.so(8) - Linux manual page" |
| kind docs, tier A | agree, caveat | man-pages project documentation (colophon 699-715); the page documents glibc's loader. [INFERENCE] a reviewer could ask for glibc source for a glibc-specific order |
| scope | partial | "silent on symlink resolution" agrees: case-insensitive grep for readlink, realpath, canonical, dereferenc, symbolic, symlink, sym link gives No matches; "soname" appears only at line 528 (LD_PROFILE). "complements S057's RUNPATH step" agrees (step (3), lines 113-116, is S057's anchor). Missing qualifier: the page is glibc's loader (lines 89-90 "for glibc2", line 185 "since glibc 2.33", line 603 /etc/ld.so.cache) |
| anchor | partial | section §DESCRIPTION = lines 80-183; quote at 102-103; steps (4) at 121-127 and (5) at 129-132 exist. The teaches example resolves at step (3), which this anchor omits (see teaches) |
| revision / version | agree | man-pages 6.19 and page date 2026-08-03 match line 715. Served Last-Modified (2026-10-08) and rendering date (2026-09-09) are not recorded (minor) |
| opened | agree | response Date header 2026-10-21; lesson Gate and build advice both say 2026-10-21 |
| teaches | disagree | (a) "re-resolved by directory search": steps (1)-(3) and (5) search directories; step (4) (lines 121-123) reads "a compiled list of candidate shared objects previously found", i.e. a cache. The build advice says "directory/cache search" (SrcLdSoNeeded.md line 30) and "ordered directory search" (line 25); the row has neither word. (b) "at every exec": not stated; lines 81-83 "find and load the shared objects ... and then run it" support it [INFERENCE]. (c) "live state, not a launcher property": not on the page. The first half follows from search at exec time [INFERENCE]; the second half is the lane's framing. (d) Example is accurate for this build: libllama-server-impl.so has DT_NEEDED libllama.so.0 and RUNPATH $ORIGIN (readelf -d, exit 0), so with LD_LIBRARY_PATH unset (harness env HOME, LANG, PATH only; knowledge line 115) it resolves at step (3). libllama.so.0 is a symlink to libllama.so.0.7.0 (test -L and readlink, exit 0) |
| lesson Gate quote | agree | verbatim across the page's own pre-block line wrap (lines 102-103); located in §DESCRIPTION (80-183); 19 words, within 25. It grounds only the lookup-order preamble. Contract rule 1 requires the quote to ground teaches; teaches (b) and (c) have no quote |
| status "mined" | agree | census at b76727f3, cwd = clone, all exit 0: rows 74; malformed 0; tier A70 B1 C3; status mined60 queued7 rejected7; duplicate ids none; enum violations none; used-by paths missing none; S067 row NF=13 |
| used-by | agree | grep corpus/ at b76727f3 finds exactly: knowledge/llamacpp-loading-lifecycle.md lines 330 and 336; lessons/round-21.md line 43 |
| recheck on-release | agree | allowed cadence |
| append-only | agree | git diff --unified=0 7a6bc911 b76727f3 -- corpus/SOURCES.md, exit 0: "11 insertions(+), 0 deletions(-)" (rows S066-S074 plus one search-log bullet). No existing row changed |
| negative-claim sweep (contract rule 5) | disagree | search-log bullet SOURCES.md:105 gives counts and a stop rationale but no sweep for "silent on symlink resolution". The only sweep is in advice SrcLdSoNeeded.md ("No matches found") |

Proposed corrections for the L1 (not applied):
- teaches: "A slash-less DT_NEEDED name is resolved at program load by the page's fixed order (steps 1-5); step (4) reads the ldconfig cache rather than walking directories; the page is silent on symlinks."
- scope: prefix "glibc ld.so:".
- anchor: "§DESCRIPTION preamble (quote at lines 102-103) and steps (1)-(5)". S057 remains the step-(3) anchor for the llama example.
- search log: add the sweep (page, date, command, zero matches).

Adjacent, not S067's row: knowledge line 336 repeats "by directory search at every exec (S067)". Line 330 cites S067 with neither URL nor anchor, against the contract's knowledge rule. Its hwcaps claim (lines 343-348) is supported by page NOTES lines 666-680 and step (4) lines 125-127, which S067's anchor does not cite. SOURCES.md line 6 says every row was opened in round 10, which is stale for later rows.

Commands and exits:
- curl -sS -L -D ld.so.headers -o ld.so.8.html https://man7.org/linux/man-pages/man8/ld.so.8.html: exit 0; sha256sum d9b7737e...f83; wc -c 41398
- git clone -q <lane> <scratch>/lane && git checkout -q b76727f31e522763ce24e43d6ec86d21b507a11f: exit 0; rev-parse HEAD = b76727f3...
- sha256sum clone vs worktree (SOURCES.md, lessons/round-21.md, knowledge/llamacpp-loading-lifecycle.md): exit 0; each pair identical
- contract census, 7 commands, cwd = clone: each exit 0; values as in the status row
- git diff --unified=0 7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d b76727f31e522763ce24e43d6ec86d21b507a11f -- corpus/SOURCES.md: exit 0
- grep tool on the saved HTML and on corpus/: results as cited (tool output, no shell exit)
- readelf -d llama-server; readelf -d libllama-server-impl.so: exit 0 and exit 0
- test -L and readlink on libllama.so.0 and libggml.so.0 in ~/.local/opt/llama-b11755: exit 0 each
- cp to out dir, sha256sum, rm -rf scratch: exit 0

Tooling: no installs or upgrades. Used existing /usr/bin/curl, /usr/bin/readelf (binutils), git, awk, sha256sum. No llama-server launched; no model fetched.
