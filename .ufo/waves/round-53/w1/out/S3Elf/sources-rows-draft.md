# S3Elf — draft SOURCES rows for the C1 offset-arithmetic claim

Claim being sourced (seat assignment): **a mapping's file offset = the PT_LOAD
segment's page-aligned p_offset; bytes past the file end read as zero.**
This is the arithmetic in `tools/round53-replay-code-audit.py` code leg
(`want = data[off:off + (hi - lo)]; want += b"\0" * ((hi - lo) - len(want))`
vs `os.pread(mem, hi - lo, lo)` over each executable /proc/<pid>/maps row,
lines 424-431 of the frozen counter).

## Admission judgments

| candidate | judgment | why |
|---|---|---|
| elf(5) https://man7.org/linux/man-pages/man5/elf.5.html | **ADMIT** (tier A, docs) | p_offset ("the offset from the beginning of the file at which the first byte of the segment resides") plus the p_align rule ("Loadable process segments must have congruent values for p_vaddr and p_offset, modulo the page size") ground why the maps offset column of a PT_LOAD-backed mapping is that segment's page-aligned file offset. Scoped honestly: ELF format spec, not /proc/<pid>/maps rendering and not kernel loader behavior; the loader step is completed by mmap(2) page alignment (S511) and the congruence. |
| mmap(2) https://man7.org/linux/man-pages/man2/mmap.2.html | **ADMIT** (tier A, docs) | §DESCRIPTION grounds page-aligned mapping offsets ("offset must be a multiple of the page size"); §NOTES grounds zero past the file end ("the remaining bytes in the partial page at the end of the mapping are zeroed when mapped"). Scoped honestly: not behavior after truncate/extend of the backing file. The NOTES' Linux caveat (writes to a partial page persist in page cache and "subsequent mappings may see the modified content") does not weaken the row: the counter's executable mappings are read-only, so no writes occur, and the zero read was confirmed on this host (report §5). |

Both are man-pages-project primary documentation of kernel ABI behavior, the
same class and tier as the round-53 rows S506-S508; opened 2026-10-27, recheck
360d, used-by corpus/lessons/round-53.md.

## Located quotes (each <= 25 words), URLs, access times

- elf(5), accessed 2026-10-27T06:14:00Z:
  "Loadable process segments must have congruent values for p_vaddr and
  p_offset, modulo the page size." (15 words; §Program header, p_align;
  also p_offset: "This member holds the offset from the beginning of the
  file at which the first byte of the segment resides.")
- mmap(2), accessed 2026-10-27T06:14:00Z:
  "the remaining bytes in the partial page at the end of the mapping are
  zeroed when mapped" (17 words; §NOTES; also §DESCRIPTION: "offset must be
  a multiple of the page size as returned by sysconf(_SC_PAGE_SIZE).")

## Draft 11-cell registry rows (markdown, ready to append after S509)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S510 | Linux elf(5) — https://man7.org/linux/man-pages/man5/elf.5.html | docs | A | the file-format half of the counter's offset arithmetic: why the /proc/<pid>/maps offset column for a PT_LOAD-backed executable mapping is that segment's page-aligned file offset (p_offset locates the segment's first byte in the file; p_align makes p_vaddr and p_offset congruent modulo the page size); ELF format spec, not /proc/<pid>/maps rendering and not kernel loader behavior | §Program header, p_offset and p_align member descriptions; man-pages 6.19, page dated 2026-08-07 (text copy `.ufo/waves/round-53/c1/elf.5.txt`) | "Loadable process segments must have congruent values for p_vaddr and p_offset, modulo the page size." — with p_offset "the offset from the beginning of the file at which the first byte of the segment resides", the maps offset column is the PT_LOAD segment's page-aligned p_offset, so the counter can slice its own archive member at that offset | mined | 2026-10-27 | 360d | corpus/lessons/round-53.md |
| S511 | Linux mmap(2) — https://man7.org/linux/man-pages/man2/mmap.2.html | docs | A | the memory half of the counter's offset arithmetic: why a file mapping's offset is page-aligned and why the bytes the counter reads from /proc/<pid>/mem past the end of an executable member's bytes are zero — a file is mapped in whole pages, the partial final page is zero-filled at map time, and mmap offsets must be page multiples; not behavior after the backing file is truncated or extended | §DESCRIPTION ("offset must be a multiple of the page size") and §NOTES ("A file is mapped in multiples of the page size..."; POSIX zero-fill paragraph); man-pages 6.19, page dated 2026-03-19 (text copy `.ufo/waves/round-53/c1/mmap.2.txt`) | "the remaining bytes in the partial page at the end of the mapping are zeroed when mapped" — so the zero padding the counter appends to the member bytes past the member's end is exactly what /proc/<pid>/mem returns for the mapping's tail | mined | 2026-10-27 | 360d | corpus/lessons/round-53.md |

## Same rows as TSV (one line per row, for mechanical append)

```tsv
S510	Linux elf(5) — https://man7.org/linux/man-pages/man5/elf.5.html	docs	A	the file-format half of the counter's offset arithmetic: why the /proc/<pid>/maps offset column for a PT_LOAD-backed executable mapping is that segment's page-aligned file offset (p_offset locates the segment's first byte in the file; p_align makes p_vaddr and p_offset congruent modulo the page size); ELF format spec, not /proc/<pid>/maps rendering and not kernel loader behavior	§Program header, p_offset and p_align member descriptions; man-pages 6.19, page dated 2026-08-07 (text copy `.ufo/waves/round-53/c1/elf.5.txt`)	"Loadable process segments must have congruent values for p_vaddr and p_offset, modulo the page size." — with p_offset "the offset from the beginning of the file at which the first byte of the segment resides", the maps offset column is the PT_LOAD segment's page-aligned p_offset, so the counter can slice its own archive member at that offset	mined	2026-10-27	360d	corpus/lessons/round-53.md
S511	Linux mmap(2) — https://man7.org/linux/man-pages/man2/mmap.2.html	docs	A	the memory half of the counter's offset arithmetic: why a file mapping's offset is page-aligned and why the bytes the counter reads from /proc/<pid>/mem past the end of an executable member's bytes are zero — a file is mapped in whole pages, the partial final page is zero-filled at map time, and mmap offsets must be page multiples; not behavior after the backing file is truncated or extended	§DESCRIPTION ("offset must be a multiple of the page size") and §NOTES ("A file is mapped in multiples of the page size..."; POSIX zero-fill paragraph); man-pages 6.19, page dated 2026-03-19 (text copy `.ufo/waves/round-53/c1/mmap.2.txt`)	"the remaining bytes in the partial page at the end of the mapping are zeroed when mapped" — so the zero padding the counter appends to the member bytes past the member's end is exactly what /proc/<pid>/mem returns for the mapping's tail	mined	2026-10-27	360d	corpus/lessons/round-53.md
```

Note for the integrator: the anchor cells reference the canonical text-copy
locations `.ufo/waves/round-53/c1/elf.5.txt` and `mmap.2.txt` (matching the
S506-S509 convention). Seat-staged copies of both pages (html + extracted
text, with sha256) are in this directory for the L1 to place there.
