# Contingent row draft — S510 (only if the integrator wants a teaches-level row)

STATUS: CONTINGENT. Seat S4Ldso's recommendation is REUSE of S079 (see
`reuse-note-S079-ld-library-path.md` in this directory). This draft exists only so
the L1 can act in one step if a frozen leg or QUALITY row will cite the sentence by
row ID. If used, it must be appended to `corpus/SOURCES.md` (never inserted; the
append-only guard `tools/sources-append-only.py` enforces this) and it will draw a
W04 duplicate-URL warning of the same accepted class as S057/S067/S079.

Contract shape: eleven columns per `SOURCES-CONTRACT-v1` (verified against the
header at `corpus/SOURCES.md:11` and the frozen guard, round-19
`.ufo/waves/round-19/build/advice/DraftS057.md:24`).

```
| S510 | Linux ld.so(8), LD_LIBRARY_PATH precedence — https://man7.org/linux/man-pages/man8/ld.so.8.html | docs | A | step-order position of LD_LIBRARY_PATH among the slash-less DT_NEEDED search steps; not secure-execution semantics, not LD_PRELOAD | §DESCRIPTION search-order step (2), between step (1) DT_RPATH and steps (4)-(5) ld.so.cache and /lib,/usr/lib defaults; man-pages 6.19, page dated 2026-08-03; re-opened 2026-10-27 (copy .ufo/waves/round-53/w1/out/S4Ldso/ld.so.8.txt, sha256 d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83, byte-identical to the round-19 fetch) | "Using the environment variable LD_LIBRARY_PATH, unless the executable is being run in secure-execution mode (see below), in which case this variable is ignored." (23 words) — step (2) precedes step (4) /etc/ld.so.cache and step (5) /lib,/usr/lib, so a directory named by LD_LIBRARY_PATH is searched before the cache and defaults; complements S079 (same page, steps 1-5) | mined | 2026-10-27 | on-release | corpus/lessons/round-53.md |
```

If unused, delete this file at integration; it is a draft, not a landed row.
