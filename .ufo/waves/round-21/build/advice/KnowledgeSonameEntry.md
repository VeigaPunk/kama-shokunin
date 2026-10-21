VERDICT: confirm - the install-tree pin entry is `corpus/knowledge/llamacpp-loading-lifecycle.md`; the symlink rule is confirmed by a retarget experiment and the gate selftest; an appended section draft is delivered, with S0xx placeholders.

# Scope
- Entry located by `grep -rln -i 'install_tree\|install-tree' corpus/` (exit 0). The existing entry `llamacpp-loading-lifecycle.md` already covers the install-tree pin. Its round-19 note (lines 315-322) says soname symlinks sit outside the pin. A new entry would duplicate it, so no new file was written.
- Draft delivered as text: `.ufo/waves/round-21/build/out/KnowledgeSonameEntry/draft-append-llamacpp-loading-lifecycle.md`. Append it after line 322 of the entry. Its `source:`/`verified-at:`/`recheck:` lines start at column 0, so the freshness sweep can read them.
- Lane not modified. Only new files were written, under `build/out/KnowledgeSonameEntry/` and this report.

# Commands and exits
- `git rev-parse --short HEAD` → `a29bb84` (lane tip; the round-21 commit is the one under review).
- `grep -rln -i 'install_tree\|install-tree' corpus/` → exit 0; hits include `corpus/knowledge/llamacpp-loading-lifecycle.md`.
- `grep -n 'install_tree\|install_links' tools tests` → exit 0; producer `tools/kama-llamacpp-live.py:178,205`; gate `tests/llamacpp-live/check-receipt.py:165-197,441-478`.
- `python3 tests/llamacpp-live/check-receipt.py --selftest` → exit 0; stdout `selftest: 9 VALID and 1 NOT-EVALUATED receipts accepted; 90 mutations + unreadable case rejected`.
- Retarget experiment (scratch `/tmp/kama-r21-KnowledgeSonameEntry`, producer functions loaded via importlib from the lane file, exit 0): before `install_tree_sha256` 91498d10…1823f, `install_links` `{'libllama.so.0': 'libllama.so.0.1'}`; after retarget to `libllama.so.0.2`, tree digest identical (`True`), link digest changed (`True`). Tree members were the regular files only.
- `zcat /usr/share/man/man2/readlink.2.gz | sed -n 49,54p` → exit 0; DESCRIPTION text quoted in draft (≤25 words).
- `zcat /usr/share/man/man7/symlink.7.gz | sed -n 326,336p` → exit 0; relative-path note quoted in draft (24 words).
- `pacman -Q man-pages` → `man-pages 6.19-1`, exit 0 (query only; no pacman transaction).
- `ls tests/llamacpp-live/install-links-grid.py` → exists (13,834 bytes, exit 0). Grid NOT run (out of scope for drafting; L1 runs official measurements).

# Installs or updates
None. No tool was installed or upgraded.

# Source rows for L1 (S0xx placeholders, not assigned)
- readlink(2) §DESCRIPTION, Linux man-pages 6.19-1, opened 2026-10-21, local man page. Quote: "places the contents of the symbolic link path in the buffer buf" (12 words).
- symlink(7) §Symbolic links relative-path note, man-pages 6.19-1, opened 2026-10-21, local man page. Quote: "may very well cause it to stop working" (9 words).
L1 decides whether local man pages count as the source tier for `SOURCES.md`.

# Findings for L1
1. The round-19 note (entry lines 315-322) is historical on symlink scope. L1 may mark it superseded. I did not edit it, because the entry is append-only in spirit and the draft says so.
2. The rule holds: the retarget changes only the link digest. This is own-work evidence of the mechanism, not a claim about a live service.
3. Boundaries stated in the draft: not execution authentication; link text is not resolution; loader search is outside the record [INFERENCE]; system NEEDED libraries stay unpinned.
4. Missing piece: none inside scope. The grid's frozen-arm numbers in the round-21 lane report were not re-run here.

# Draft text location
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/build/out/KnowledgeSonameEntry/draft-append-llamacpp-loading-lifecycle.md`

# Scratch
`/tmp/kama-r21-KnowledgeSonameEntry` removed (`ls` after `rm -rf` → exit 2, absent).
