# X3Teardown — round 53, lane kama (w1): teardown and fd hygiene at build c22602bd

**Verdict: PASS — SIGKILL of the `subprocess.call` invoker took the whole four-process chain down in 20 ms (bound: 30 s), the server's fd table held 4 fds with no inherited memfd, and TCP 127.0.0.1:44231 refused (ECONNREFUSED) at the same 20 ms sample. No defect found in the assigned scope.**

## Setup (fresh clone at the build commit)

The lane working tree is at `bc8e6e7f1c53ea6f557001cea1e4d1e8b586c18e` (post-build integration), so the
tool source used is a shared clone pinned to the build, per the shared-resource directive:

```console
$ S=/fast/scratch/hyaku/kama-r53/X3Teardown; export TMPDIR="$S"
$ git clone --shared -q /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
$ git -C "$S/lane" checkout -q --detach c22602bd8d83ab26349d1087e916ca537ee4f9d1
$ git -C "$S/lane" rev-parse --show-toplevel
/fast/scratch/hyaku/kama-r53/X3Teardown/lane
$ git -C "$S/lane" rev-parse HEAD
c22602bd8d83ab26349d1087e916ca537ee4f9d1
$ git -C "$S/lane" rev-parse HEAD:tools/kama-live-replay.py
eb5933321eb14afab8afb07a1a888a85608cdbea
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse c22602bd8d83ab26349d1087e916ca537ee4f9d1:tools/kama-live-replay.py
eb5933321eb14afab8afb07a1a888a85608cdbea
$ git -C "$S/lane" status --porcelain     # empty, rc 0
```

The clone's `tools/kama-live-replay.py` and `tools/kama-llamacpp-live.py` are the build-commit blobs
(sha256 `6c0bfbdf…e98102` / `82b253e5…b349d`, clone HEAD == `c22602bd`). For the record: the lane's
**working tree** no longer matches the build for these two tools — `git -C <lane> status --porcelain
-- tools/` reports ` M tools/kama-live-replay.py` and ` M tools/kama-llamacpp-live.py` (+70/−20,
post-build wave edits naming V1Review/V3Review); they are not in `bc8e6e7`. Those edits were not
touched or read as evidence; every `:line` below is the blob at `c22602bd` in the clone.

Harness (written in my scratch/out, not a counter; no tracer was used anywhere): `drive.py` launched
the exact invoker shape from the seat spec and measured the kill. Full script: `out/X3Teardown/drive.py`;
full measurement JSON: `out/X3Teardown/result.json`.

```console
$ cd "$S" && TMPDIR="$S" /usr/bin/python3 drive.py
```

Invoker argv (verbatim, `result.json:invoker_argv`):

```console
/usr/bin/python3 -c 'import subprocess,sys;sys.exit(subprocess.call(sys.argv[1:]))'
  /usr/bin/python3 $S/lane/tools/kama-live-replay.py
  --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-1.json
  --work $S/w --out $S/r.json --witness-dir $S/wd
```

`ready.json` appeared 2.811 s after the invoker launched (downloads + extraction + server start + checks):

```json
// out/X3Teardown/ready.json  (out/X3Teardown/result.json:ready)
{"schema": "kama-live-witness/v1", "port": 44231, "pid": 2748746,
 "written_utc": "2026-10-27T06:15:45.256Z"}
```

Process chain at snapshot (`result.json:ps_tree`; all four states `S`):

| role | pid | ppid | session | note |
|---|---|---|---|---|
| invoker | 2747659 | 2747656 | 2747656 | `python3 -c subprocess.call` wrapper |
| replay | 2747660 | 2747659 | 2747656 | `kama-live-replay.py` |
| live | 2748471 | 2747660 | 2747656 | `python3 -I kama-llamacpp-live.py` |
| server | 2748746 | 2748471 | 2748746 | own session (`Ssl`), `start_new_session=True` (`kama-llamacpp-live.py:2182`) |

The listener belonged to the server pid and its fd 3 (`result.json:ss_listen`, rc 0):

```console
State  Recv-Q Send-Q Local Address:Port  Peer Address:Port Process
LISTEN 0      512        127.0.0.1:44231      0.0.0.0:*   users:(("4",pid=2748746,fd=3))
```

`ss -tnp sport = :44231` at snapshot: header only, no established connection (rc 0).

## Required observation 1 — `ls -l /proc/2748746/fd`

`ls -l /proc/2748746/fd` rc 0, 4 descriptors (`out/X3Teardown/fd-ls.txt`):

```console
total 0
lrwx------ 1 vgpnk vgpnk 64 Oct 27 03:15 0 -> /dev/null
lrwx------ 1 vgpnk vgpnk 64 Oct 27 03:15 1 -> /fast/scratch/hyaku/kama-r53/X3Teardown/w/tmp/kama-llamacpp-live-j_ihm6d6.log
lrwx------ 1 vgpnk vgpnk 64 Oct 27 03:15 2 -> /fast/scratch/hyaku/kama-r53/X3Teardown/w/tmp/kama-llamacpp-live-j_ihm6d6.log
lrwx------ 1 vgpnk vgpnk 64 Oct 27 03:15 3 -> socket:[1049425768]
```

- `0` is `/dev/null` (stdin `DEVNULL`), `1`/`2` are the live tool's captured log, `3` is the listening
  socket — the same socket `ss` attributes to pid 2748746/fd 3.
- No `/memfd:` link, no replay-owned descriptor, no library fd: the sealed server memfd handed to the
  live tool (`kama-live-replay.py:482-486`) is **not** inherited by the server (`Popen` `close_fds`
  default; the image is reached at exec time through `executable=/proc/<live-pid>/fd/<n>`,
  `kama-llamacpp-live.py:2186-2190`).
- `/proc/2748746/status`: `Name: 4`, `Pid/Tgid: 2748746`, `PPid: 2748471`, `Uid: 1000 1000 1000 1000`,
  `Seccomp: 0`.

## Required observation 2 — `/proc/2748746/maps` executable rows

Full maps: `out/X3Teardown/maps.txt`; rows with `x` in perms: `out/X3Teardown/maps-exec.txt` (24 rows,
including `[vdso]`/`[vsyscall]`); pathname rows: `out/X3Teardown/maps-exec-file.txt` (22 rows). First
and last rows as captured:

```text
556275475000-556275476000 r-xp 00001000 00:01 184983                     /memfd:llama-server (deleted)
7fab2ec07000-7fab2ed2c000 r-xp 00015000 103:05 814057842                 .../w/server/llama-b11909/libggml-cpu-zen4.so
...
7fab321ae000-7fab321db000 r-xp 00001000 00:1e 13506894                  /usr/lib/ld-linux-x86-64.so.2
ffffffffff600000-ffffffffff601000 --xp 00000000 00:00 0                  [vsyscall]
```

Unique executable file mappings (22 = 1 memfd image + 8 archive libs + 13 host libs):

- `/memfd:llama-server (deleted)` dev `00:01` inode `184983` (the sealed image; no path exists).
- Under `w/server/llama-b11909/`, uid 1000, dev `103:05`: `libllama-server-impl.so`,
  `libggml-base.so.0.27.0`, `libggml.so.0.27.0`, `libggml-cpu-zen4.so`, `libggml-rpc.so`,
  `libllama.so.0.7.0`, `libllama-common.so.0.7.0`, `libmtmd.so.0.7.0` — the four families C1 requires
  (`libllama-server-impl.so`, `libggml-base.so*`, `libggml.so*`, `libggml-cpu-*.so`) are all present.
- Under `/usr/lib/`, uid **0** for all 13: `ld-linux-x86-64.so.2`, `libc.so.6`, `libm.so.6`,
  `libstdc++.so.6.0.36`, `libgcc_s.so.1`, `libgomp.so.1.0.0`, `libz.so.1.3.2`,
  `libzstd.so.1.5.7`, `libssl.so.3`, `libcrypto.so.3`, `libbrotlienc.so.1.2.0`,
  `libbrotlidec.so.1.2.0`, `libbrotlicommon.so.1.2.0`.

This is the same 8-archive-library / 13-root-owned-host-file shape the L1 recorded at the build
(`.ufo/waves/round-53/measured/c1-build.out`), re-observed independently here (uid read via `os.stat`
on each path; the memfd row has no path, which is why the build's `code_mappings()` drops `/memfd:`
rows from the receipt — `kama-llamacpp-live.py:774-834`, filter at `:792-793`).

## Kill and teardown window

```console
$ kill -KILL 2747659      # the invoker; verified as the wrapper by /proc/2747659/cmdline first
```

Timeline from `result.json:timeline` (monotonic ms since the kill; full sample list in the JSON):

| t (ms) | invoker | replay | live | server | connect_ex(127.0.0.1:44231) |
|---|---|---|---|---|---|
| 0 | R | S | S | S | 0 (connected) |
| 20 | Z | gone | gone | gone | **111 (ECONNREFUSED)** |

- `first_all_gone_ms = 20`, `first_port_refused_ms = 20`; final sample at `+21 ms`:
  states `{invoker: gone, replay: gone, live: gone, server: gone}`, `connect_ex = 111`,
  `final_states_all_gone = true`, `final_port_refused = true`, `within_30s = true`.
- `invoker_exit = -9` (SIGKILL, reaped by the harness; it was `Z` for the 20 ms sample).
- The mechanism is the recorded chain: invoker dies → replay's own `PR_SET_PDEATHSIG(SIGTERM)`
  (set at `kama-live-replay.py:864`, definition `:134-143`) → live child's `preexec`
  `PR_SET_PDEATHSIG(SIGTERM)` (`kama-live-replay.py:461-466`, called at `:484`) → server's
  `PR_SET_PDEATHSIG(SIGKILL)` (`kama-llamacpp-live.py:669`, `preexec_fn` at `:2183`). The server's
  own session (`start_new_session=True`, `:2182`) does not survive the signal.
- Post-mortem: `ps -p 2747659,2747660,2748471,2748746` → header only; `pgrep -af
  'X3Teardown/(lane|w)'` → none; witness dir after teardown `[]` (live tool's `finally` removed
  `ready.json`, `kama-llamacpp-live.py:365-372`); no leftover temp log in `w/tmp` (unlinked at
  `kama-llamacpp-live.py:1334`); `r.json` absent — the replay was killed before its comparison, which
  is expected for a teardown probe, not a replay-match claim.
- Exit codes: driver `0`; invoker `-9`; `ls` `0`; `ss` `0`.

## Observations / residual risks (not claim failures)

1. **Server `comm` is the memfd descriptor number, not `llama-server`.** `/proc/<pid>/status` shows
   `Name: 4` and `ss -ltnp` prints `users:(("4",pid=…,fd=3))`. Cause: the round-52 memfd exec passes
   `executable=/proc/<live-pid>/fd/<n>` (`kama-llamacpp-live.py:2186-2190`), and the kernel derives
   `comm` from the exec path's basename. Operability note only: [INFERENCE from `Name: 4`:] comm-based
   lookups (`pgrep llama-server`, `ps -C llama-server`) would not find the running server; the cmdline
   (`pgrep -f llama-server`), `ss` pid and the receipt's `child_pid` do. C1 is unaffected (it reads
   `/proc/<pid>/maps`, `kama-llamacpp-live.py:774-834`),
   and the claims do not name `comm`. No fix proposed against the build — changing `comm` would need a
   server-side `PR_SET_NAME`, outside the ratified shape.
2. **The witness handshake is single-run safe** as documented: `ready.json` is announced only for a
   live child (`kama-llamacpp-live.py:341-352`) and removed when the hold ends; the directory was empty
   after the kill. No stale pid/release remained.
3. Not measured here (outside this seat): the replay's post-kill receipt/comparison
   (`--out r.json` never written by design), and the C1/C2 counter verdicts.
4. No tool installs or upgrades were needed; nothing was run under a tracer.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X3Teardown.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X3Teardown/drive.py` (harness)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X3Teardown/result.json` (pids, states, timeline, ss, ps, status, leftovers)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X3Teardown/fd-ls.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X3Teardown/maps.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X3Teardown/maps-exec.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X3Teardown/maps-exec-file.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X3Teardown/ready.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X3Teardown/ready.json.copy`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X3Teardown/receipt-1.json` (input receipt copy)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X3Teardown/invoker.log` (empty; all output went to the live receipt path)
