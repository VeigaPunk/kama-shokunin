# X2Rerun — second independent C1 measurement (round 53, lane kama)

**Verdict: C1 reproduces — two back-to-back runs of the frozen counter at `c22602bd8d83ab26349d1087e916ca537ee4f9d1`, on one clone, both print the identical verdict line `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True` (exit 0), each with 8 archive libraries / 8 executable ranges / 13 root-owned host files per receipt, and the same CPU backend `libggml-cpu-zen4.so` every time (deterministic: `ggml_backend_score` of the archive's own variant binaries scores zen4 1984, the maximum, on this CPU).**

Independent of the L1: own `git clone --shared`, own scratch, own archive/model downloads. Both runs agree with the L1 build receipt line-for-line once volatile ids are masked (0 mismatches).

## Environment

- Host: `AMD Ryzen 9 9950X 16-Core Processor`, 32 threads, 1 socket, 1 NUMA node; kernel `7.2.11-arch1-1`.
- Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r53/X2Rerun/lane` (read-only use; `git -C … rev-parse --show-toplevel` = that clone; `git status --porcelain` empty; `cat-file -t c22602bd…` = `commit`). Clone HEAD was `bc8e6e7f…`; the counter measures `--tip` via `git archive`, so the checkout state is irrelevant.
- Counter integrity: `sha256sum tools/round53-replay-code-audit.py` = `1a7a144204ba8b7ea9791706ab5fc90f1dab55db12a824a1af5ae89a81b75d8f`, equal to `preregistration.json` C1 `counter_sha256`. Counter, preregistration and controls untouched.
- Frozen inputs the counter itself re-checks: `detail: counter archive: its own download, frozen digest` (archive sha256 `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b`, verified again by my own download) and `detail: counter vocabulary: 512 tokens from its own download`.
- No tool installs/upgrades, no pacman, no services started beyond the counter's own loopback replays; `pgrep -af llama-server` before run 2 and after run 2 showed no leftover server.

## Commands, exits, wall time

Scratch `S=/fast/scratch/hyaku/kama-r53/X2Rerun`, `TMPDIR=$S`, sequential on the same clone:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-replay-code-audit.py \
  --repo "$S/lane" --tip c22602bd8d83ab26349d1087e916ca537ee4f9d1 --scratch "$S/run1"
python3 … --scratch "$S/run2"
```

| run | exit | wall (outer, incl. archive+model download) | scratch |
|---|---|---|---|
| 1 | 0 | 19.144 s | `$S/run1` |
| 2 | 0 | 18.498 s | `$S/run2` |

Wall time is well inside the counter's own budget (`READY_WAIT` 600 s, `EXIT_WAIT` 180 s) and the counter removed each scratch subtree on exit. Receipts: `c1-run1.out`, `c1-run2.out` (stdout captured verbatim; both `.err` files 0 bytes).

## Verdict line: identical across runs

Run 1 / run 2, byte-equal:

```
bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True
```

Both runs produce 15 lines (1 `tip=`, 1 verdict, 13 `detail:`). Programmatic comparison (`agreement.txt`, `agreement.json`):

- `verdict_identical: True`
- `code_rows_identical: True` (all three `code bN` rows, member lists included)
- `tail_identical: True` (both `counter …` lines, `teardown`, `newrow`)
- `detail_sets_equal_modulo_numbers: True`

Only the expected volatile fields differ: pid, port, tree inode, witness nonce, memfd `dev:inode` (run 1 b1 `pid 2581575 port 35677`, run 2 b1 `pid 2595462 port 45057`; nonces `kama witness dedbdf11…` vs `0be2f3f7…`). Teardown is `0.10 s` in both.

Cross-check against the L1 build receipt (different clone, different scratch, different session): `measured/c1-build.out`, core lines only, masking `pid`, `port`, `inode`, `nonce`, `dev:inode`, teardown seconds → **0 mismatches for run 1 and 0 for run 2** (`build-receipt-compare.txt`).

## Per-receipt archive libraries and executable range counts

Identical in both runs, for each of b1, b2, b3:

| receipt | archive files | executable ranges | root-owned host files | member list |
|---|---|---|---|---|
| b1 | 8 | 8 | 13 | `libggml-base.so.0.27.0`, `libggml-cpu-zen4.so`, `libggml-rpc.so`, `libggml.so.0.27.0`, `libllama-common.so.0.7.0`, `libllama-server-impl.so`, `libllama.so.0.7.0`, `libmtmd.so.0.7.0` |
| b2 | 8 | 8 | 13 | same 8 |
| b3 | 8 | 8 | 13 | same 8 |

`8 ranges` for `8 files` means each archive library contributes exactly one executable mapping (no library mapped twice, no variant library missing); all four `REQUIRED` patterns are satisfied by `libllama-server-impl.so`, `libggml-base.so.0.27.0`, `libggml.so.0.27.0`, `libggml-cpu-zen4.so`. My own archive download confirms each of these names is a single regular member at `llama-b11909/…` with these digests (from `archive-members.json`): base `16527517…`, zen4 `2f473ffc…`, rpc `4b6be3e1…`, ggml `8643a58b…`, llama-common `29feaa27…`, llama-server-impl `b8f0f203…`, llama `9705244b…`, mtmd `48d84bf9…`.

## Is the CPU backend the same each time, and why

**Same:** all six held servers (3 receipts × 2 runs) map `libggml-cpu-zen4.so`, and no other `libggml-cpu-*` variant appears in any `code_mappings`/`own_code` list.

**Why (mechanism read from b11909, not guessed):** the loader picks the CPU plugin by score, not by name order — `ggml/src/ggml-backend-reg.cpp` at tag b11909: `ggml_backend_load_best(name, silent, dir)` (line 480) dlopens every `libggml-<name>-*.so` in the directory, calls the plugin's exported `ggml_backend_score` (lines 523–525), keeps the strictly highest `s > best_score` with `best_score` starting at 0 (504, 529–531), and only loads a backend if `best_score != 0` (548, 564); `ggml_backend_load_all` invokes it with the name `"cpu"` (592). The archive ships 14 candidates (`libggml-cpu-{alderlake,cannonlake,cascadelake,cooperlake,haswell,icelake,ivybridge,piledriver,sandybridge,sapphirerapids,skylakex,sse42,x64,zen4}.so`), so the choice is a pure function of CPU feature detection — no randomness, no load/frequency/affinity sampling, hence stable across runs.

**Feature input on this host** (`/proc/cpuinfo`, `cpu-flags-subset.txt`): `avx avx2 avx512_bf16 avx512_bitalg avx512bw avx512cd avx512dq avx512f avx512ifma avx512_vbmi2 avx512vbmi avx512_vnni avx512_vp2intersect avx512_vpopcntdq avx512vl avx_vnni f16c fma vaes vpclmulqdq`; **AMX absent** (`grep -c '^amx'` on the flags line = 0).

**Scores measured on this host** (`cpu-backend-score-probe.py`, ctypes `CDLL(RTLD_LOCAL)` + `ggml_backend_score()` per library, output `cpu-backend-scores.json`):

```
zen4 1984 | cooperlake 1728 | icelake 1472 | cascadelake 1216 | cannonlake 448 |
skylakex 192 | alderlake 128 | haswell 64 | piledriver 24 | ivybridge 23 |
sandybridge 21 | sse42 5 | x64 1 | sapphirerapids 0
```

So `zen4` wins by 256 over the runner-up, and `sapphirerapids` (the only AMX-specific variant) scores 0 — it is not merely losing, it declines because AMX is absent. The probe loaded the host install copies; `sha256(libggml-cpu-zen4.so)` on the host is `2f473ffc7d445ef35ccc80d193513259e878c15fa967b4d3c7953f79c5ca25a9`, byte-identical to the archive member, so the winning score is computed from exactly the bytes the counter verified in `/proc/<pid>/mem`. For the non-winning variants I did not hash host copy vs archive member individually — that equality rests on the round-52 J5HostMemfd install-equals-archive result [INFERENCE]; it does not affect which backend wins.

## Limits of this measurement (no defect claimed in the frozen counter)

- Two runs on one host are agreement, not a determinism proof against changed host state: a different CPU mask/CPU model would legitimately change the backend. Nothing in these two runs perturbed features between them (same kernel, no hotplug, no `taskset`/feature masking).
- The counter reads executable mappings once per server; a library rewritten after that read is unobserved (preregistered C1 limit).
- Host libraries are only classed root-owned + not-writable by the counter; their bytes are not compared (preregistered limit) — hence `13 root-owned host files` is a count, and the detail line does not name them.
- Both runs needed network to github.com/huggingface.co and both got the frozen digests; an offline host would fail at download, not at a leg.

## Files written (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X2Rerun.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X2Rerun/c1-run1.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X2Rerun/c1-run1.err`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X2Rerun/c1-run2.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X2Rerun/c1-run2.err`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X2Rerun/agreement.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X2Rerun/agreement.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X2Rerun/build-receipt-compare.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X2Rerun/archive-members.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X2Rerun/cpu-backend-scores.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X2Rerun/cpu-flags-subset.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X2Rerun/cpu-backend-score-probe.py`
