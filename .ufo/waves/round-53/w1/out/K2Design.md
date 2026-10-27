# K2Design — round 53, C1 design critique (operability)

Verdict: C1's executable-range comparison is sound for what it claims and reproduces at the
build commit (met=True; 8 archive executable ranges byte-equal in /proc/<pid>/mem, 13 host
libraries root-owned), but the held-replay measurement shows it compares only 21 of 188
/proc/<pid>/maps rows — the largest remaining gap is the relocated data/RELRO segments of the
archive libraries (38 rows, measured legitimately differing from archive bytes, so the fix
must be relocation-aware), followed by silently-skipped anonymous executable rows (measured
zero today) and class-only host libraries (trust boundary by design); the proposed round-54
claim shape closes the first two and pins the third.

## Evidence

### 1. Frozen counter run at the build commit (reproduction)

Command (run against my own shared clone of the lane at the build commit):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-replay-code-audit.py \
  --repo /fast/scratch/hyaku/kama-r53/K2Design/lane \
  --tip c22602bd8d83ab26349d1087e916ca537ee4f9d1 \
  --scratch /fast/scratch/hyaku/kama-r53/K2Design
```

Exit code 0. Receipt (copy: out/K2Design/c1-k2design.out):

```
tip=c22602bd8d83ab26349d1087e916ca537ee4f9d1
bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True
detail: code b1: 8 archive files (8 executable ranges) byte-equal in /proc/<pid>/mem to the
counter's own archive, 13 root-owned host files; recorded in code_mappings and own_code:
['libggml-base.so.0.27.0', 'libggml-cpu-zen4.so', 'libggml-rpc.so', 'libggml.so.0.27.0',
'libllama-common.so.0.7.0', 'libllama-server-impl.so', 'libllama.so.0.7.0', 'libmtmd.so.0.7.0']
```

This matches the L1's build receipt `.ufo/waves/round-53/measured/c1-build.out` exactly.

### 2. Held-replay maps measurement

I held a witnessed replay of receipt-1 (`kama-live-replay.py --witness-dir`, server held at
pid 2827397, then a second hold at pid 3122061; both released and drained, no leftovers) and
classified every row of /proc/<pid>/maps by permission and backing. Analyzer and raw maps:
out/K2Design/maps-analysis.txt, maps-held-188rows.txt, maps-summary.json.

First hold (188 rows) — rows by permission and by backing:

```
r--p 69   rw-p 63   ---p 31   r-xp 23   r--s 1   --xp 1
host-file 67   anonymous 64   archive-tree 46   memfd 5
kernel: heap/vvar/vvar_vclock/vdso/stack/vsyscall 1 each
```

Which rows the counter compares — `code_observe()` filter at
tools/round53-replay-code-audit.py:413 (`"x" in perms and pathname starts with "/" and not
/memfd:`): **21 of 188 rows (11 %)**, identical in both holds:

- 8 archive-tree r-xp rows (one per library: libllama-server-impl.so, libllama.so.0.7.0,
  libllama-common.so.0.7.0, libmtmd.so.0.7.0, libggml.so.0.27.0, libggml-base.so.0.27.0,
  libggml-cpu-zen4.so, libggml-rpc.so);
- 13 host-file r-xp rows (ld-linux, libc, libm, libz, libzstd, libgcc_s, libgomp, libstdc++,
  libssl, libcrypto, libbrotlienc, libbrotlidec, libbrotlicommon).

Skipped: 167 rows — 164 without `x` (archive-tree 38 of them: 24 r--p + 8 rw-p + 6 ---p), 2
anonymous kernel rows ([vdso] r-xp, [vsyscall] --xp), 1 memfd r-xp row (the sealed image,
covered by the sealed leg's whole-image hash at tools/round53-replay-code-audit.py:462).
rwxp rows anywhere: **0**.

### 3. Relocation is real and blocks a naive extension

Measured on the held server by a process in its ancestry (Yama ptrace_scope 1, S507) — every
maps row of `llama-b11909/libggml.so.0.27.0` read from /proc/<pid>/mem and compared with the
archive member bytes at the row's file offset (evidence: out/K2Design/relocation-libggml.txt):

```
r--p 0x000000  8192   True   0     None   header/rodata
r-xp 0x002000  24576  True   0     None   executable row  <- the only row C1 compares
r--p 0x008000  4096   True   0     None   rodata
---p 0x009000  4096   True   0     None   guard
r--p 0x009000  4096   False  69    3497   RELRO (relocated)
rw-p 0x00a000  4096   False  476   8      .data (relocated/written)
```

The executable row is byte-equal to the archive member (the claim holds); the RELRO and .data
rows legitimately differ. Any round-54 data-segment check must apply the member's own dynamic
relocations at the observed load base and compare only non-relocated bytes.

## What the executable-range comparison proves

- Server memory, not the filesystem, is the observation: each archive library's x range is
  read from /proc/<pid>/mem and compared with the counter's own pinned download of the
  archive at the maps row's file offset (code_observe, tools/round53-replay-code-audit.py:
  393-459). A library swapped after the record-time member check — the round-52 closure R2
  scenario — is caught, because memory holds the actually-mapped inode's pages.
- The receipt cannot lie about which files ran: the launcher's `code_mappings`
  (tools/kama-llamacpp-live.py:774) opens each mapped path with O_NOFOLLOW and hashes only
  while fstat() shows the mapped dev+inode (`(deleted)` never opened); the replay's
  `verify_code` (tools/kama-live-replay.py:305) hashes the named members from the archive
  stream; the counter re-derives both and cross-checks them against its own observation.
- The anonymous memfd image is covered by the sealed leg (whole-image sha256 + seals).
- The model mapping is covered by the round-50 bind leg: path-bound, the file at the mapped
  dev+inode hashed to the frozen digest (measured: one r--s row, tools/…-audit.py:307-339).

## What it leaves (measured)

1. **Data/RELRO segments of the archive libraries — largest gap.** 38 archive-tree rows
   (24 r--p, 8 rw-p, 6 ---p) are never compared; §3 shows two of them legitimately differ from
   the archive at 69 and 476 bytes. The replay is the server's parent and can ptrace it (Yama
   scope 1, S507), so a modified replay could patch relocated data in memory after the counter's
   one read and pass every leg. This is capability, not just hygiene: .data/RELRO carry global
   state that steers execution.
2. **Anonymous executable memory is silently skipped.** The filter keeps only absolute-pathname
   rows (tools/round53-replay-code-audit.py:413). Measured today: 0 anonymous x rows, 0 rwxp
   rows (only kernel [vdso]/[vsyscall]); but nothing *fails* if a replay injected an anonymous
   executable mapping — it would be skipped like the vdso.
3. **Host libraries are classed, not compared.** The 13 host rows are accepted on uid 0 +
   inode equality + not-writable (tools/round53-replay-code-audit.py:430-444); their bytes are
   never checked against anything. This is the claim's stated trust boundary, but it means the
   lane trusts the host's whole userspace stack by class.
4. **The download itself.** Both sides pin sha256 of their own downloads (counter:
   ARCHIVE_SHA/MODEL_SHA; replay: receipt provenance), so byte equality pins *content* to the
   frozen digests. Not proven is *provenance* — that the bytes came from the pinned URL rather
   than the byte-identical host install. This is the preregistration's own declared limit
   (round-52 J5HostMemfd); out of scope for the claim as written.
5. One-shot read TOCTOU (preregistration limit): the counter reads once while the server is
   held; a patch after the read is unobserved.

## Proposed round-54 claim shape (closes the largest gap)

Predicate sketch (same style as the round-53 predicate):

> a replay of each committed v5 b11909 receipt holds a server every one of whose mappings is
> either (a) an archive member whose bytes the counter reads from /proc/<pid>/mem — executable
> ranges compared whole, data ranges compared at every non-relocated offset after the counter
> applies the member's own dynamic relocations at the observed load base — (b) the model
> mapping, whose in-memory bytes equal the frozen model bytes (GGUF is data: no relocation),
> (c) a root-owned host library whose sha256, recorded at the lane's record time against the
> mapped inode, the counter reproduces from that inode, or (d) unmapped: the server maps no
> anonymous executable page and no rwxp page; and the counter reads every compared range
> twice around the bind observation and requires both reads equal.

Mechanism notes: a minimal ELF relocation applier for .rela.dyn (x86-64 RELATIVE/GLOB_DAT/
JUMP_SLOT/JUMP_TABLE/IRELATIVE) in the frozen counter — no new dependency; the model leg is
relocation-free and cheap; the no-anonymous-executable and no-rwxp assertions are pure maps
filters on rows already being read; the double read closes the one-shot TOCTOU; host-library
digest pinning needs one new receipt field at record time.

Ranking: gap 1 (data/RELRO) is the largest measured, unclosed surface and needs the relocation
machinery; gap 2 (anonymous exec) is the largest potential hole but measured zero and closes
with a fail-closed assertion — the claim shape covers both, and pins gap 3 at the record-time
boundary.

## Artifacts written

- .ufo/waves/round-53/w1/out/K2Design.md (this report)
- .ufo/waves/round-53/w1/out/K2Design/c1-k2design.out — my counter receipt at the build commit
- .ufo/waves/round-53/w1/out/K2Design/maps-held-188rows.txt — raw /proc/<pid>/maps of the held server
- .ufo/waves/round-53/w1/out/K2Design/maps-analysis.txt — full classification of the second hold (204 rows; compared set identical)
- .ufo/waves/round-53/w1/out/K2Design/maps-summary.json — machine-readable summary of the second hold
- .ufo/waves/round-53/w1/out/K2Design/relocation-libggml.txt — per-row memory-vs-archive comparison for libggml.so.0.27.0
- .ufo/waves/round-53/w1/out/K2Design/replay-own-code.json — the held replay's own_code result (verified, 8 members)

Scratch (/fast/scratch/hyaku/kama-r53/K2Design) removed after writing; no llama-server
processes left running (checked with pgrep before finishing). No lane or fleet files were
modified; no tools installed.
