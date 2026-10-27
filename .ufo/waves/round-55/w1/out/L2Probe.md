# L2Probe — round-55 bounded /proc/<pid>/maps pathname inventory vs KERNEL_MAPS

**Verdict: KERNEL_MAPS in tools/round54-replay-code-audit.py:144 is exhaustive for every row the server produced in the round-55 build receipts — the only bracketed executable rows on this host are `[vdso]` (r-xp) and `[vsyscall]` (--xp), both covered; the build measured `anon=0` (no anonymous executable rows); one frozen cosmetic dead string (`"[vvar_boot"`, missing `]`) is harmless. No defect affecting C1.**

## Question

Is the kernel-map list exhaustive for rows the server produced in the build receipts?

## Counter code under test (frozen)

`tools/round54-replay-code-audit.py:144`:

```python
KERNEL_MAPS = ("[vdso]", "[vsyscall]", "[vvar]", "[vvar_vclock]", "[vvar_boot", "[uprobes]")
```

 consulted at lines 502-505 only for rows whose perms contain `x` (filter at line 498):

```python
if len(f) < 6 or not f[5].startswith("/"):
    name = f[5].split("(", 1)[0].strip() if len(f) >= 6 else ""
    if name in KERNEL_MAPS:
        continue
    probs.append(f"code: anonymous executable mapping {f[0]} {f[1]} (name {name or '(none)'!r})")
```

Executable rows with a `/`-leading pathname go to: memfd branch (`/memfd:` admitted by (dev,ino) match to the sealed image, else flagged), tree branch (byte-compared against the archive), host branch (root-owned, inode-matched, basename in frozen `HOST_LIBS`, else flagged). Everything is fail-closed.

## Build-receipt rows the server actually produced

Source: `.ufo/waves/round-55/measured/c1-build.out` (tip 9c60eae6, met=True exit 0), detail lines for b1/b2/b3, all three replays identical:

- `8 archive files (16 executable ranges) byte-equal in /proc/<pid>/mem` — plain paths under the unpacked tree.
- `13 root-owned host files` — plain paths, basenames in `HOST_LIBS` (frozen set at lines 138-142, 13 names).
- `sealed b*: running image '/memfd:llama-server (deleted)' 00:01:... seals 15` — the memfd branch.
- `anon=0` — zero anonymous executable rows across all three replays.
- `twopass b*: both observation passes byte-identical over 16 range reads` — 16 = the archive executable ranges only.
- Kernel pseudo-rows present in every process on this host (empirically verified below): `[vdso]` r-xp, `[vsyscall]` --xp — both executable, both in KERNEL_MAPS; `[vvar]`, `[vvar_vclock]` r--p — non-executable, removed by the `x` filter before KERNEL_MAPS is consulted.

So the set of non-plain-path executable rows the server produced = {`[vdso]`, `[vsyscall]`, `/memfd:llama-server (deleted)`}. KERNEL_MAPS covers the first two; the memfd branch covers the third. **Exhaustive: yes.**

## Empirical inventory (this host, kernel 7.2.11-arch1-1)

Probe design: `setsid sleep 300` + `python3 -c "...time.sleep(300)"` children, plus an enriched self-probe producing exotic forms (memfd, unlinked-file mapping, named anon VMA via `prctl(PR_SET_VMA_ANON_NAME)`, executable anonymous page, thread) and an ia32 compat binary. Full raw outputs in `.ufo/waves/round-55/w1/out/L2Probe/`.

| # | pathname field form | example observed | executable? | counter handling |
|---|---|---|---|---|
| 1 | plain path | `/usr/lib/libc.so.6` | yes | tree branch / host branch |
| 2 | `path + ' (deleted)'` (unlinked, still mapped) | `.../todelete.bin (deleted)` | possible | host branch → basename ∉ HOST_LIBS → flagged (fail-closed) |
| 3 | `/memfd:<name> (deleted)` | `/memfd:l2probe-memfd (deleted)` | yes (server image) | memfd branch by (dev,ino) |
| 4 | `/dev/zero (deleted)` (MAP_SHARED anon) | observed | not exec | host branch → flagged if exec (fail-closed) |
| 5 | `/SYSV00000000 (deleted)` (SysV shm) | observed | not exec | host branch → flagged if exec (fail-closed) |
| 6 | `[vdso]` | `r-xp` | yes | KERNEL_MAPS hit |
| 7 | `[vsyscall]` | `--xp` on this host | yes (x bit) | KERNEL_MAPS hit |
| 8 | `[vvar]` | `r--p` | no | x-filter; also in KERNEL_MAPS |
| 9 | `[vvar_vclock]` | `r--p` | no | x-filter; also in KERNEL_MAPS |
| 10 | `[heap]` | `rw-p` | no | x-filter |
| 11 | `[stack]` | `rw-p` | no | x-filter |
| 12 | `[stack:<tid>]` | per-thread views only | no | not visible in leader maps; x-filter anyway |
| 13 | `[anon:<name>]` (prctl, kernel ≥ 6.2) | `[anon:l2probe_named_anon]` | not observed; exec → flagged | intended K1Cheat flag |
| 14 | no pathname field (row ends `00:00 0 ` + trailing space) | heaps; `rwxp` shellcode page | yes (rwxp observed) | flagged as anonymous executable mapping (intended) |
| 15 | `[uprobes]` | not produced (needs armed uprobe events) | n/a | in KERNEL_MAPS defensively |
| 16 | `[vvar_boot]` | not produced on this host | no (r--p) | see F1 |

Evidence commands (all run in scratch `/fast/scratch/hyaku/kama-r55/w1/L2Probe`, copies in the out dir):

- `python3 maps_inventory.py 2525744 sleep 2482387 python` → `inventory-basic.txt`. Both processes: bracketed rows = `[heap],[vvar],[vvar_vclock],[vdso],[stack],[vsyscall]`; kernel-map hits exactly the 4 rows `[vvar],[vvar_vclock],[vdso],[vsyscall]`; zero executable rows outside plain paths + `[vdso],[vsyscall]`.
- `python3 maps_enriched.py` → `inventory-enriched.txt`. Produces `(deleted)` rows for both the unlinked file and the memfd; `[anon:l2probe_named_anon]` after prctl rc=0; two `rwxp` anonymous executable pages flagged `kernel-map-hit=False`; `[vdso],[vsyscall]` the only KERNEL_MAPS hits among executable rows.
- Thread probe (main+thread) → `inventory-thread-shmem.txt`. No `[stack:<tid>]` in the leader's maps view; MAP_SHARED anon shows as `/dev/zero (deleted)`; SysV shm as `/SYSV00000000 (deleted)`.
- ia32 compat binary (`gcc -m32`, `vsyscall32=1`) → `inventory-ia32-maps.txt`. Kernel names are identical to x86_64 (`[vdso]`, `[vvar]`, `[vvar_vclock]`) — **no `[vdso32]`** — and `[vsyscall]` is absent for ia32. KERNEL_MAPS needs no compat entries on this host.
- Trailing-space quirk: `awk '$0 ~ /00:00 0 ?$/' /proc/self/maps | od -c` shows rows with no pathname end `... 0   0  : 0 0   0  \n` — i.e. a trailing space. `row.split(None, 5)` yields 5 fields, so the counter's `len(f) < 6` branch is taken — handled.

## Findings

- **F1 (frozen cosmetic; no C1 impact).** `tools/round54-replay-code-audit.py:144` — `KERNEL_MAPS` contains the prefix string `"[vvar_boot"` (no closing bracket). The kernel's actual special-mapping name is `"[vvar_boot]"` (non-executable r--p), which can therefore never match this entry. Harmless twice over: the row never carries `x` so line 498 filters it before line 503, and even a hypothetical executable row would be flagged "anonymous executable mapping" — the fail-closed direction. Not fixable in place (counter is frozen, sha256 c81fe971… pinned in the preregistration); candidate correction for a future freeze round: replace `"[vvar_boot"` with `"[vvar_boot]"`. No proposed diff is applied; the observation is the deliverable.
- **F2 (harmless over-approximation).** `[vvar]`, `[vvar_vclock]` are in KERNEL_MAPS but are always skipped by the executable-row filter first; `[uprobes]` is never produced by the server (kernel has 9 uprobes symbols; nothing arms probe events). Belts-and-suspenders, no behavior change.
- **F3 (correctly absent from KERNEL_MAPS).** `[heap]`, `[stack]`, `[stack:<tid>]`, `[anon:<name>]`, `[anon_shmem:<name>]` are not kernel-provided code. Any executable instance is exactly the anonymous-code shape (K1Cheat shellcode) the counter is designed to flag at lines 502-505. An attacker naming an executable anon page would still be caught. Fail-closed by construction.

## Conclusion

For the rows the server produced in the round-55 build receipts, the kernel-map list is exhaustive: `{[vdso], [vsyscall]}` are the only bracketed executable rows any process on this host (x86_64 or ia32) emits, both are covered, the sealed memfd goes through its own (dev,ino) branch, and the measured `anon=0` confirms no anonymous executable rows were produced. Residual coverage gaps that remain are all non-executable forms filtered before the check, plus one dead prefix string (`"[vvar_boot"`) that can never match anything. No defect; C1's maps audit is sound for this claim.

## Evidence index (this directory)

- `inventory-basic.txt` — sleep + python children, full classification
- `inventory-enriched.txt` — memfd / (deleted) file / named anon / rwxp anon page / thread
- `inventory-thread-shmem.txt` — thread stacks, `/dev/zero (deleted)`, `/SYSV...` SysV form
- `inventory-ia32-maps.txt` — ia32 compat process maps (no `[vdso32]`, no `[vsyscall]`)
- `inventory-summary.json` — machine-readable forms table + findings

No tools installed; no lane files edited; all probe processes torn down (`pgrep -af llama-server` not applicable — none started; sleep/python/m32 probe pids killed and re-checked).
