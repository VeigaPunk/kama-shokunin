# L1Probe — round 55 wave 1 bounded probe (LD_AUDIT honoring + LD_PRELOAD_32 absence)

Verdict: **glibc 2.44 honors LD_AUDIT only for an audit-capable DSO (one exporting `la_version`); the audit DSO is mapped into a trivial child and externally visible in /proc/<pid>/maps while SIGSTOP-held — and the battery's m-ldaudit-foreign vector-analysis is grounded, because an ordinary foreign host lib (/usr/lib/libexpat.so.1, zero `la_version` exports) is refused ("undefined symbol: la_version; ignored") and never mapped. LD_PRELOAD_32 is unconditionally inert on this host (glibc never implemented it; token absent from both ld.so binaries), even for a 32-bit child.**

No defects found in the frozen artifacts this probe touches. Full transcript with every command/output/exit code: `.ufo/waves/round-55/w1/out/L1Probe/probe-transcript.txt`.

## What was run and seen

All artifacts built in scratch `/fast/scratch/hyaku/kama-r55/w1/L1Probe` with the host GCC 16.2.1 (host x86_64, glibc 2.44):

- `audit.c` → `libaudit.so` / `libaudit32.so` — audit-capable DSO exporting `la_version` (echoes the version back; a 0 return would disable auditing) and `la_preinit` (syscall-only; dumps `/proc/self/maps` lines containing "libaudit" to fd 2). Sources in out dir.
- `child.c` — exact trivial `int main(void){return 0;}`. `child_slow.c` — identical plus `usleep(600000)` so the parent can freeze it inside its lifetime.
- `parent.c` — fork+exec harness: sets one env var, SIGSTOPs the child 200 ms after fork, dumps `/proc/<pid>/maps`, SIGCONTs, waits; prints `SUMMARY maps_lines=N audit_so_mapped=M child_exit=C`.
- `marker.c` — 64/32-bit marker DSO with a constructor print.

### Q1: does glibc honor LD_AUDIT for an audit-capable DSO? — YES, and it is mapped

RUN 1 (`LD_AUDIT=$S/libaudit.so $S/child`, exact trivial child): `[audit] la_version called` and `la_preinit` both fired; the in-child `/proc/self/maps` dump shows `libaudit.so` mapped with 5 VMAs (`r--p/r-xp/r--p/r--p/rw-p`); child exit 0. (The harness's external read printed `maps_lines=0` only because the exact trivial child exits in microseconds, before the 200 ms SIGSTOP; the in-child dump is the authoritative mapping evidence.)

RUN 2 (same, against `child_slow`, external read while SIGSTOP-held): full 36-line maps dump including the 5 `libaudit.so` VMAs; `SUMMARY maps_lines=36 audit_so_mapped=1 child_exit=0`. The audit DSO is externally observable in the held child's maps.

### Q2: battery vector m-ldaudit-foreign — grounded (the vector is void for non-audit foreign libs)

The battery driver (`.ufo/waves/round-55/c1/battery/run-battery.py:55-61`) records `LD_AUDIT=/usr/lib/libexpat.so.1` as a "vector" (expected `met=True`) on the theory that glibc won't map a non-audit foreign lib. Verified:

- `nm -D /usr/lib/libexpat.so.1 | grep -c la_version` → **0** (not audit-capable).
- RUN 3: stderr `ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol: la_version; ignored.`; 25-line maps dump contains no foreign lib; `audit_so_mapped=0 child_exit=0`.

So the LD_AUDIT route cannot plant a root-owned foreign DSO: only a purpose-built, `la_version`-exporting DSO is ever mapped (RUN 2). Complements: nonexistent audit path → loud refusal, exit 0, nothing mapped (A); audit-capable 32-bit DSO honored symmetrically by the 32-bit ld.so (B); wrong-ELF-class audit DSO refused (C).

### Q3: LD_PRELOAD_32 on this host — absent, unconditionally

- RUN 4: `LD_PRELOAD_32=$S/libaudit.so` vs 64-bit child_slow → `audit_so_mapped=0`, exit 0 (no load, no ctor).
- RUN 5: `LD_PRELOAD_32=/nonexistent.so` vs 64-bit child → exit 0, no error, nothing loaded.
- RUN 6 (positive-control attempt): `LD_PRELOAD_32=$S/marker32.so` vs a real 32-bit child (`cc -m32`, ELFCLASS32, runs under `/lib/ld-linux.so.2`) → **marker NOT loaded** (no ctor output; `LD_DEBUG=libs,files` shows no preload processing). Plain `LD_PRELOAD` with the same 32-bit object loads fine (`[marker] ctor ran`). glibc 2.44 does not honor `LD_PRELOAD_32` even for a 32-bit process.
- Root cause: `strings /usr/lib/ld-linux-x86-64.so.2` and `strings /usr/lib32/ld-linux.so.2` contain **no `LD_PRELOAD_32` token** (recognized tokens are `LD_AUDIT`, `LD_BIND_NOT`, `LD_BIND_NOW`, `LD_DEBUG`, `LD_DEBUG_OUTPUT`, `LD_DYNAMIC_WEAK`, `LD_LIBRARY_PATH`, `LD_ORIGIN_PATH`, `LD_PRELOAD`, `LD_PROFILE`, `LD_PROFILE_OUTPUT`, `LD_SHOW_AUXV`, `LD_VERBOSE`, `LD_WARN`; plus `LD_PREFER_MAP_32BIT_EXEC` on the 64-bit loader). `LD_PRELOAD_32`/`_64` are Solaris `ld.so.1` variables; upstream glibc `process_envvars()` never adopted them (2011 libc-alpha proposal declined).
- Host-class note: the seat brief calls this a "64-bit-only host"; observed it is not — `/usr/lib32` and `/lib/ld-linux.so.2` exist, IA32 emulation works (the 32-bit child executed). The distinction is moot for the counter: the spawned server binary (`llama-b11909`, confirmed via `file` on the running copy) is `ELF 64-bit LSB pie executable, x86-64`, so `LD_PRELOAD_32` would be a no-op for it even on a Solaris-style loader, and here it is a no-op for every process.
- Control (RUN 7): plain `LD_PRELOAD=marker64.so` vs 64-bit child → ctor ran, exit 0 — the envnames leg's LD_PRELOAD concern remains live; only the `_32` variant and the foreign-LD_AUDIT vector are void.
- RUN 8: wrong-class `LD_PRELOAD` (64-bit object into 32-bit child) → refused with a stderr line, exit 0.

## Seat-specific notes

- `pgrep -af llama-server` at the end shows 4 processes, all under other seats' scratch trees (`J5EnvNames`, `X9Separation`); L1Probe started none and tore nothing down.
- No lane/fleet/shokuknow writes; no fixtures needed beyond scratch; counters/preregistration untouched (read-only inspection of `run-battery.py` lines 30-123 for mutant context).
- Receipt cited (`.ufo/waves/round-55/c1/battery/m-ldaudit-foreign.out`) copied to the out dir as `receipt-m-ldaudit-foreign.out`.

## Files written (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/L1Probe.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/L1Probe/probe-transcript.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/L1Probe/receipt-m-ldaudit-foreign.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/L1Probe/{audit.c,child.c,child_slow.c,parent.c,marker.c}`
