# S3Elf — round 53, C1 offset-arithmetic source grounding

Verdict: **both candidates ADMIT** — elf(5) grounds "a mapping's file offset =
the PT_LOAD segment's page-aligned p_offset", mmap(2) grounds "bytes past the
file end read as zero"; drafted rows S510/S511 (11 cells each) staged for the
registry; claim empirically confirmed on this host; no defects found.

Seat assignment (leaf): open elf(5) and mmap(2), record URL / UTC access time /
located quote (<= 25 words) each, judge admit/reject as kama SOURCES rows for
the counter's offset arithmetic, draft the 11-cell rows.

The claim grounds the frozen counter `tools/round53-replay-code-audit.py` code
leg: for each executable /proc/<pid>/maps row of the replay's server it builds
`want = member[off:off+len] + "\0" * remainder` and compares against
`os.pread(/proc/<pid>/mem, len, lo)` (counter lines 424-431, read-only).

## 1. Sources opened

| candidate | URL | accessed (UTC) | page |
|---|---|---|---|
| elf(5) | https://man7.org/linux/man-pages/man5/elf.5.html | 2026-10-27T06:14:00Z | Linux man-pages 6.19, dated 2026-08-07 |
| mmap(2) | https://man7.org/linux/man-pages/man2/mmap.2.html | 2026-10-27T06:14:00Z | Linux man-pages 6.19, dated 2026-03-19 |

Commands (run in scratch $S=/fast/scratch/hyaku/kama-r53/S3Elf):

    $S$ date -u +%Y-%m-%dT%H:%M:%SZ && curl -sS --max-time 60 -o elf.5.html https://man7.org/linux/man-pages/man5/elf.5.html && wc -c elf.5.html
    2026-10-27T06:14:00Z
    71040 elf.5.html                      # exit 0
    $S$ curl -sS --max-time 60 -o mmap.2.html https://man7.org/linux/man-pages/man2/mmap.2.html && wc -c mmap.2.html
    48160 mmap.2.html                     # exit 0

Both pages genuine man-pages 6.19 (grep of "Linux man-pages 6.19" and content
markers: elf p_offset x5 / PT_LOAD; mmap "partial page" x2 / "zero" x6).
HTML converted to text by extracting all <pre> blocks (7 sections each);
copies staged at out/S3Elf/{elf.5.html,elf.5.txt,mmap.2.html,mmap.2.txt} with
sha256: elf.5.html da01af39…, elf.5.txt 50d09431…, mmap.2.html 86675e35…,
mmap.2.txt ccf82a34… (full digests in `sha256sum` output, report copy below).

## 2. Located quotes (<= 25 words), verified byte-exact in the text copies

- elf(5) §Program header, p_align (text copy lines 455-456; whitespace-normalized match FOUND):
  "Loadable process segments must have congruent values for p_vaddr and
  p_offset, modulo the page size." — 15 words.
  Companion (§Program header, p_offset, line 420-422): "This member holds the
  offset from the beginning of the file at which the first byte of the
  segment resides."
- mmap(2) §NOTES (text copy lines 446-448; match FOUND):
  "the remaining bytes in the partial page at the end of the mapping are
  zeroed when mapped" — 17 words.
  Companions: §DESCRIPTION (line 41-42) "offset must be a multiple of the
  page size as returned by sysconf(_SC_PAGE_SIZE)."; §NOTES (line 447)
  "A file is mapped in multiples of the page size."; POSIX paragraph
  (lines 529-530) "POSIX specifies that the system shall always zero fill any
  partial page at the end of the object".

Verification harness: python3 whitespace-normalization check over the staged
text copies; all 7 quote probes printed FOUND (probe output in transcript).

## 3. Judgment

- **elf(5): ADMIT, tier A, docs.** Scope: the file-format half of the offset
  arithmetic — p_offset locates the segment's first byte in the file and the
  p_align rule makes p_vaddr and p_offset congruent modulo the page size, so
  the maps offset column of a PT_LOAD-backed mapping is the segment's
  page-aligned file offset. Honest scoping: it is the ELF format spec, not
  /proc/<pid>/maps rendering and not kernel loader behavior; the loader step
  (page-aligned mapping) is completed by mmap(2) page alignment (S511).
  Same class/tier as round-53 rows S506-S508 (man-pages project primary
  documentation). recheck 360d; used-by corpus/lessons/round-53.md.
- **mmap(2): ADMIT, tier A, docs.** Scope: the memory half — mapping offsets
  are page-aligned and the partial final page of a file mapping is zero-filled
  at map time, so bytes past the member's end read as zero through
  /proc/<pid>/mem. Honest scoping: not behavior after the backing file is
  truncated or extended (NOTES: "The effect of changing the size of the
  underlying file ... is unspecified"). The NOTES' Linux page-cache caveat
  ("subsequent mappings may see the modified content" after a write to the
  partial page) does not weaken the row: the counter's executable mappings
  are read-only, so no writes occur; and the zero read was confirmed
  empirically on this host (§5).

No rejections. The two rows together cover the whole claim; neither alone
does, which is why the draft keeps them as two scoped rows rather than one.

## 4. Counter arithmetic being grounded (frozen files, read-only inspection)

- tools/round53-replay-code-audit.py lines 424-431:
  `off = int(f[2], 16)` (the maps offset column = page-aligned file offset),
  `want = data[off:off + (hi - lo)]`, `want += b"\0" * ((hi - lo) - len(want))`,
  `got = os.pread(mem, hi - lo, lo)`.
- Counter docstring lines 37-43 state the same contract: "the bytes the
  counter reads from /proc/<pid>/mem over that row's address range equal the
  member's bytes from the row's file offset (zero past the member's end)".

## 5. Empirical confirmation on this host (scratch only, exit 0)

1. Page-aligned offset: mmap(offset=1) failed `OSError 22 (Invalid
   argument)`; offset=0 succeeded — matches mmap(2) §DESCRIPTION.
2. Zero past EOF through /proc/<pid>/mem: mapped a 4219-byte probe file over
   2 pages (libc mmap via ctypes, PROT_READ/MAP_PRIVATE), read both pages
   with `os.pread(/proc/self/mem, 8192, base)` (the counter's exact call):
   in-file bytes matched `b"A"*4219`, remaining 3977 tail bytes all zero.
   First attempt mis-set libc.mmap restype to c_int (EINVAL/EFAULT); with
   `restype=c_void_p` the read succeeded — a probe artifact, not kernel
   behavior. (Self-inflicted pitfall recorded for honesty.)
3. PT_LOAD congruence on the real b11909 tree: parsed program headers of
   every libggml*.so* in /home/vgpnk/.local/opt/llama-b11909 — all PT_LOAD
   segments satisfy (p_vaddr - p_offset) % 4096 == 0, e.g.
   libggml-base.so.0.27.0 segments (0x0,0x0) (0x11000,0x11000)
   (0xa2000,0xa2000) (0xc6a60,0xc7a60); congruent mod pagesize: True for all.

These confirm the claim the rows ground, on the same page size (4096) and
kernel (7.2.11-arch) the counter runs on.

## 6. Draft rows

Full 11-cell markdown rows + TSV staged at
out/S3Elf/sources-rows-draft.md (S510 elf(5), S511 mmap(2), next ids after
S509; opened 2026-10-27; recheck 360d; used-by corpus/lessons/round-53.md).
Anchor cells reference the canonical copies `.ufo/waves/round-53/c1/elf.5.txt`
and `mmap.2.txt` per the S506-S509 convention; seat-staged page copies with
sha256 are in out/S3Elf/ for the L1 to place.

## 7. Defects

None. The frozen counter implements exactly what the two sources ground; the
row drafts introduce no new convention (mirroring S506-S509 cell style).

## Paths written

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/S3Elf.md (this report)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/S3Elf/sources-rows-draft.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/S3Elf/elf.5.html
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/S3Elf/elf.5.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/S3Elf/mmap.2.html
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/S3Elf/mmap.2.txt
