# Scout — host runtime facts for the llama.cpp lane (C1/C2 operability + calibration)

Seat: KamaR16.ScoutHostRuntimeFacts. Read-only: nothing written except this file; no installs, no
service changes, no port bound. Measurements below are the seat's own, taken 2026-10-20 ~10:2x -03.

## Verdict

The b11755 tree is fully resolvable and its CPU dispatch **works on this host**: ggml scans all 14
bundled variants and selects `libggml-cpu-zen4.so`, and that backend executes real matmuls
(pp/tg throughput measured). No missing library, no variant-selection failure. Three
*conditional* hazards remain (foreign `LD_LIBRARY_PATH`, foreign `GGML_BACKEND_PATH`, a relocated
copy of just the binary) plus one trap already visible: `llama-server --list-devices` prints
`(none)`, so it must not be used as a CPU/backend readiness signal.

## 1. `ldd ~/.local/opt/llama-b11755/llama-server` — nothing missing

All 20 DT_NEEDED entries resolve; zero `not found` lines. Family libs come from the install tree,
the rest from `/usr/lib`:

```
libllama-server-impl.so => /home/vgpnk/.local/opt/llama-b11755/libllama-server-impl.so
libggml.so.0 => /home/vgpnk/.local/opt/llama-b11755/libggml.so.0
libggml-base.so.0 => /home/vgpnk/.local/opt/llama-b11755/libggml-base.so.0
libssl.so.3 => /usr/lib/libssl.so.3
```

`readelf -d llama-server` → `RUNPATH [$ORIGIN]` (same for `libggml-base.so.0.27.0`). Because
`RUNPATH` is `$ORIGIN`, the tree is location-independent **only** as long as the binary stays next
to its `.so` siblings. `ldd` counts on the sibling binaries `llama-cli` and `llama-bench`: 0
`not found` each.

Installed binary digests (the claimed `753bfa73…e226` is the release *asset*; the extracted
`llama-server` member legitimately differs, so this is not a contradiction [INFERENCE]):

```
b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804  llama-server
65f7908e0fa582ef863a629e3b450f48e604a57ed69fc9f62cb3c74d7afef475  libggml-cpu-zen4.so
```

`~/.local/bin/llama-server` is a symlink to the opt tree, owned `vgpnk:vgpnk`, mode 0755; the
tree's `llama-server`, `libggml-cpu-zen4.so`, `libggml.so.0.27.0` are all `-rwxr-xr-x vgpnk:vgpnk`.

## 2. `~/.local/bin/llama-server --version`

```
version: 0.7.0-dev (build 11755, commit 704366d76)
built with GNU 11.4.0 for Linux x86_64
```

Exit 0. Matches the C2 claim (build 11755 / commit 704366d76).

## 3. CPU flags relevant to ggml CPU backend selection

`/proc/cpuinfo`: `model name : AMD Ryzen 9 9950X 16-Core Processor`; `nproc` = 32.

Present (kernel spelling): `avx avx2 avx_vnni f16c fma`, `avx512f avx512dq avx512bw avx512vl
avx512cd avx512ifma avx512vbmi avx512_vbmi2 avx512_vnni avx512_bitalg avx512_vpopcntdq
avx512_bf16 avx512_vp2intersect`.

Absent: `avx512_fp16` (reported ABSENT by literal grep) and `amx_tile` (ABSENT). Those are the
features the Intel `sapphirerapids`/`icelake` variants are built around, which is consistent with
them not being chosen [INFERENCE on the exact per-variant gate; the *observation* that zen4 wins is
direct]. No `GLIBC_TUNABLES` set, so no glibc hwcaps override.

## 4. Free RAM

`free -h` at sample time: total 30Gi, used 8.1Gi, free 14Gi, buff/cache 9.8Gi, **available 22Gi**.
`/proc/meminfo`: `MemAvailable: 25330372 kB` (earlier sample; 24 GiB). Swap: 30.3 GiB
`/swap/swapfile` file, 0 B used. `ulimit -v` = unlimited; cgroup v2 `memory.max` at the session
scope = `max` (no cap), `memory.current` 7.65 GB. HugePages_Total 0, THP `[always]`, cmdline has
`zswap.enabled=1 zswap.max_pool_percent=25`.

Consequence for C2: a 1.12 MiB / 0.29 M-param F32 model plus llama-server overhead is far below
any limit; startup cannot fail on memory.

## 5. Could the bundled `libggml-cpu-*.so` variant selection fail here?

**Observed: no.** 14 variants are installed (`alderlake cannonlake cascadelake cooperlake haswell
icelake ivybridge piledriver sandybridge sapphirerapids skylakex sse42 x64 zen4`), zero GPU
backends. Running the tiny GGUF (sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`,
matches C2) produced:

```
load_backend: loaded RPC backend from /home/vgpnk/.local/opt/llama-b11755/libggml-rpc.so
load_backend: loaded CPU backend from /home/vgpnk/.local/opt/llama-b11755/libggml-cpu-zen4.so
| llama ?B (guessed) all F32 | 1.12 MiB | 0.29 M | CPU | 2 | pp4 | 37277.96 ± 0.00 |
| ...                        | ...      | ...    | CPU | 2 | tg4 | 25829.28 ± 0.00 |
```

`strace -f -e trace=openat ~/.local/bin/llama-server --list-devices` shows the loader opening
**every** `/home/vgpnk/.local/opt/llama-b11755/libggml-cpu-*.so` and then re-opening
`libggml-cpu-zen4.so` for the actual load — i.e. the scan happens through the `~/.local/bin`
symlink and still resolves to the real tree (kernel-resolved `/proc/self/exe`). Same result when
launched as `./llama-bench` from the install dir.

Zen 5 has no dedicated variant in this build; the `zen4` build is a feature-subset of Zen 5 and the
matmuls above executed without SIGILL — so "wrong variant on a newer core" is not a live risk here
[INFERENCE, backed by the pp/tg run].

### Failure modes that *could* still bite (all avoidable)

| # | Condition | Evidence | Effect | Mitigation |
|---|---|---|---|---|
| F1 | Binary copied away from its `.so` siblings (e.g. only `llama-server` into a tmpdir) | `nm -D llama-server \| grep -c ggml_backend_cpu_reg` → `0`; no `libggml-cpu` string in the executable | No CPU backend; `libggml.so` is 49.8K and carries only the loader (`ggml_backend_load_all_from_path`), so nothing computes [INFERENCE] | Always launch the installed tree (`~/.local/bin/llama-server` symlink or the absolute opt path); never copy the binary |
| F2 | A consumer exports `LD_LIBRARY_PATH` pointing at another llama.cpp | `RUNPATH [$ORIGIN]` is searched *after* `LD_LIBRARY_PATH`; currently `<unset>` | Mixed `libggml*` versions at load time [INFERENCE] | Launch with `env -u LD_LIBRARY_PATH` (and `-u GGML_BACKEND_PATH`), or assert the `load_backend: loaded CPU backend from …/libggml-cpu-zen4.so` line |
| F3 | A consumer exports `GGML_BACKEND_PATH` to a foreign dir | Verified: `GGML_BACKEND_PATH=/nonexistent/dir` logs `load_backend: failed to load /nonexistent/dir: … cannot open shared object file` yet still loads zen4, exit 0 — tolerant for a missing dir, but a *real* foreign dir with a mismatched `.so` hits `failed to initialize backend from %s: incompatible API version` (string present in `libggml-base.so.0.27.0`) | Backend init error or mixed backend | Keep `GGML_BACKEND_PATH` unset; it is currently unset |
| F4 | Using `--list-devices` as readiness/CPU proof | Output is `Available devices:` / `(none)` although CPU works | False negative if C2 gates on it | Gate on `/v1/models` (200 + `data[0].id == alias`) or the `load_backend: loaded CPU backend` stderr line, never on `--list-devices` |

Not a hazard: no `avx512_fp16`/AMX (Intel-only variants simply score out); HugePages 0 (THP
`always` covers allocations); swap present but unused.

## 6. Advice for the lane

- C2 should spawn with an explicit small thread count. 32 logical CPUs are visible while the model
  has 0.29 M params; the seat measured `-t 2` as sufficient and cheap. Default thread selection at
  32 threads only adds contention (no correctness risk).
- C2 should treat the *backend-load line* and `/v1/models` as its two positive signals; the
  `(none)` device list is not a signal.
- C2 should pin the launch to the symlink/absolute path and unset `LD_LIBRARY_PATH`/
  `GGML_BACKEND_PATH` for the child, closing F1–F3 without extra files.
- Nothing here contradicts C1: the loading-body verdict work is independent of backend selection;
  this seat found no host-level reason a lane-owned server would fail to start.

## Limits

- Read-only: no server was started, no port bound (only `llama-bench`/`llama-server --version`
  invocations plus `strace` of `--list-devices`), so no lifecycle surface was exercised here.
- Feature-gate detail per Intel variant is inferred from the kernel flag set and the observed
  winner, not from per-variant source.
- Sampling: RAM figures are point-in-time (two samples, 24 GiB then 22 GiB available).

## Installs

None. Nothing installed, upgraded, downgraded, restarted, or written outside this report.
