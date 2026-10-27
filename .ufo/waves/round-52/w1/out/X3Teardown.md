# X3Teardown — round 52, lane kama: teardown with a memfd server

**Verdict: PASS (operability).** With the server exec'd from the replay's sealed memfd, SIGKILL of the invoker removed the whole tree — invoker, replay, live tool and `llama-server` — by `0.139 s` after the kill (the invoker itself gone at `0.001 s`), the server having exited `rc=0` on SIGTERM in `3 ms` with its port refusing; the memfd (`dev 00:01, ino 173384, nlink 0, seals 15`) was held **only** by the replay (fd 4) and the live tool (fd 4), **not** by the server, whose only non-std fd is its own listening socket. No defect found; one scoping caveat for the uid-global grep is recorded below.

## Inputs

- Lane commit 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 (round-52 build), cloned `--shared` into scratch and checked out detached; `git -C <clone> rev-parse HEAD` = `5dacf2c7…`.
- Tools at that commit are byte-identical to the lane working copy:
  `9c11b2fb…` tools/kama-live-replay.py, `424b7808…` tools/kama-llamacpp-live.py.
- Receipt `.ufo/waves/round-48/c2/live/receipt-1.json` (v5, b11909, server sha256 `35ac50fb…`, model `270cba1b…`).
- Run: `--work <S>/w2 --out <S>/r2.json --witness-dir <S>/wd2 --witness-timeout 300`, started in the background under the prescribed invoker:

```
python3 -c 'import subprocess,sys;sys.exit(subprocess.call(sys.argv[1:]))' \
  python3 <clone>/tools/kama-live-replay.py \
  --receipt …/.ufo/waves/round-48/c2/live/receipt-1.json \
  --work <S>/w2 --out <S>/r2.json --witness-dir <S>/wd2 --witness-timeout 300
```

Driver: `teardown_driver2.py` (copied into the out dir; strict tree walk, no cmdline guessing). Everything below is reproduced verbatim in `evidence2.json` / `driver2.out`.

## Process tree at the hold (parentage verified, not inferred)

`wd2/ready.json` = `{"schema":"kama-live-witness/v1","port":36337,"pid":752996,"written_utc":"2026-10-27T05:11:41.631Z"}`

```
    PID    PPID    PGID     SID STAT
 744013  742890  742890  742890 S     python3 -c '…subprocess.call…' … kama-live-replay.py …
 744142  744013  742890  742890 S     python3 <clone>/tools/kama-live-replay.py --receipt …receipt-1.json …
 751730  744142  742890  742890 S     python3 -I <clone>/tools/kama-llamacpp-live.py --server <S>/w2/server/llama-b11909/llama-server …
 752996  751730  752996  752996 Ssl   <S>/w2/server/llama-b11909/llama-server -m … -c 256 -t 1 --no-webui --offline
```

`ps` confirms invoker→replay→live→server; the server is in its own session (`start_new_session=True`, tools/kama-llamacpp-live.py:1989), so the replays' process group kill cannot be what reaps it — the teardown is the live tool's SIGTERM handler plus the server's own parent-death signal.

## FDs and the running image (the two posed questions)

```
$ ls -l /proc/752996/exe /proc/752996/fd
lrwxrwxrwx … /proc/752996/exe -> /memfd:llama-server (deleted)

/proc/752996/fd:
0 -> /dev/null
1 -> <S>/w2/tmp/kama-llamacpp-live-z_ab2fx7.log
2 -> <S>/w2/tmp/kama-llamacpp-live-z_ab2fx7.log
3 -> socket:[997821959]
```

- **memfd held by replay and live only: yes.** Global fd scan while up returned exactly two holders, both of this run:
  `744142:4 -> /memfd:llama-server (deleted)` (replay) and `751730:4 -> /memfd:llama-server (deleted)` (live), both `dev 00:01, ino 173384, nlink 0` — one file, the same descriptor inherited through `pass_fds` (tools/kama-live-replay.py:400-403; `sealed_member` at :222).
- **Does the server inherit any extra fd? No.** Its fd list is `0` (`/dev/null`, Popen stdin), `1`/`2` (the per-run log file the live tool opens for it), and `3` — its **own** listening socket: `socket:[997821959]` resolves in `/proc/net/tcp` to `0100007F:8DF1 … state 0A`, i.e. `127.0.0.1:36337` LISTEN (the announced port). The live tool's fd table at the same instant is `0,1(pipe),2(pipe),4(memfd)` — no socket to inherit. This is `execve("/proc/<live pid>/fd/4")` with `close_fds` semantics of `Popen` (tools/kama-llamacpp-live.py:1995-1997), so the image has no path and no fd.
- **The image is the memfd, sealed, with the frozen bytes.** Opening `/proc/752996/exe` (the counter's own procedure): `path=/memfd:llama-server (deleted)`, `dev 00:01`, `ino 173384`, `nlink 0`, `size 17864`, `F_GET_SEALS = 15`; `/proc/752996/maps` has 5 `memfd:llama-server` segments, all inode `173384`. The extracted member is also `17864` bytes, `nlink 1`, sha256 `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` = the receipt's server.

## Kill and teardown

```
[SIGKILL invoker 744013]
gone_at = {invoker 0.001 s, replay 0.139 s, live 0.139 s, server 0.139 s}; all_gone_within_30s = true
port_after_probe = refused            (Python connect to 127.0.0.1:36337)
memfd holders after (scoped): none of this run (only other seats' replay/live, labelled scope=other)
witness dir after: []                 (ready.json removed by the live tool; no release created)
w2/r2.json: absent (replay was killed)   w2/rerun-receipt.json: written by the live tool
```

The orphaned live tool's own record of the teardown (copied as `rerun-receipt.json`):

```
outcome            setup-error            setup_error "terminated:signal 15"
teardown           alive_at_teardown_start true, sigterm_sent true, sigkill_sent false,
                   term_wait_ms 3, returncode 0, port_refuses true,
                   log: model loaded; "listening on http://127.0.0.1:36337"
checks             teardown_graceful True, teardown_port_closed True (evaluated)
server_exe         opened true, /memfd:llama-server (deleted), inode 173384, nlink 0, seals 15,
                   sha256 35ac50fb…, size 17864
server.fd          dev 00:01, inode 173384, nlink 0, seals 15, sha256 35ac50fb…
model_mapping      mapped true, sha256 270cba1b… (the download, dev 103:05)
witness            null (the hold was cut by the run's SIGTERM chain, not by `release`)
```

Chain: invoker SIGKILL → the replay's `PR_SET_PDEATHSIG` (tools/kama-live-replay.py:123) delivers SIGTERM to the replay → the live child's own `PDEATHSIG` (tools/kama-llamacpp-live.py:662) delivers SIGTERM to it, raising `Terminated` out of the witness hold (tools/kama-llamacpp-live.py:327-378) → `teardown()` (tools/kama-llamacpp-live.py:1201-1235) `killpg(SIGTERM)`s the server, which exits `rc=0` in 3 ms with no SIGKILL needed → port proves closed.

This is exactly the counter's teardown leg (tools/round52-replay-memfd-audit.py:533-566, `KILL_WAIT = 30` at :97): invoker SIGKILLed during the hold, every snapshotted descendant gone, port refusing, all inside 30 s. Measured: 0.139 s.

## Post-run cross-checks (final scan, `post_scan.txt`)

- `ss -ltn` for 36337 and the earlier run's 34281: `no listener`.
- `/proc/744013`, `744142`, `751730`, `752996`: all absent (no zombies).
- No fd anywhere holds inode `173384`; no `/proc/*/maps` in any process maps `173384`; `pgrep -af X3Teardown` → none.
- `pgrep -x llama-server` → rc=1 (none of mine; the only remaining uid-wide `memfd:llama` fd is another seat's).

## Notes and risks (no defect in the lane tools)

1. **The seat-level `ls -l /proc/*/fd | grep memfd:llama` check is uid-global, not run-scoped.** While my server was up the scan showed exactly my two holders, but at `t+0.37 s` after the kill the same grep returned 2 lines belonging to another seat's replay/live (J5HostMemfd; later R1Old, M2Replay, Sen2Scratch, L1 held theirs). Any reader of that check must attribute by `/proc/<pid>/cmdline` or by the memfd inode: my memfd `173384` was referenced by no fd and mapped by no process. The counter itself is not exposed to this (it snapshots its own descendants), so this is a reporting caveat only.
2. **Killed-replay path shape.** When the replay dies during the hold, the live tool still writes `--out` with `outcome=setup-error`, `witness=null`, and complete teardown evidence; `r2.json` is absent, so a C1 audit of that run would refuse at `no-rerun-receipt` rather than compare a half-run. Consistent, no action.
3. **`fd 3` on the server is its listening socket**, not an inherited descriptor — recorded here so the "extra fd" question is not re-opened from the bare fd count.
4. No tools installed or upgraded; no pacman; no lane mutation (read-only git on the lane, mutation only on the disposable `--shared` clone); one live clone, removed with the rest of `/fast/scratch/hyaku/kama-r52/X3Teardown` after the artifacts were copied (verified absent; `pgrep -x llama-server` rc=1).

## Artifacts

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X3Teardown/`

```
driver2.out          2a5c1836fbc55aa7fa9ef0246d8dff70e4b4c2b7ad5172bf62c5ef0bf5fe208a
evidence2.json       068e987a99a506e9c31987594f1277b001193bd76e99ffd64cd890c4b2187261
post_scan.txt        da06d3f91b666f86f289eace294f8c6da86f83092522197f60b0df210b23d7b7
rerun-receipt.json   59d636dd26c092016623ce9d991014b67b9a6cc0e1334731d96d8b42e63da135
teardown_driver2.py  b18054c6c62925f65181a4f7746ba28bdb6662202b86334439542dc77d099440
```
