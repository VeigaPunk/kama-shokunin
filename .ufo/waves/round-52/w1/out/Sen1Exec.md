# Sen1Exec — round 52, lane kama: security review of exec-from-fd (build 5dacf2c)

**Verdict:** no exploitable exposure in the exec-from-fd mechanism — (1) the `/proc/<pid>/fd/N` reachability is same-uid only and strictly *less* than what the round-51 path gave the same attacker, (2) the memfd is **not** inherited by the server, (3) `LD_LIBRARY_PATH` points at a tree whose 28 shared objects collide with no host soname (the path-loaded-libraries limit is confirmed, not widened), and (4) a host with `vm.memfd_noexec >= 1` **fails closed but opaquely** (`launch-failed:PermissionError`, empty stderr) — one low-severity operability defect with a tested 3-hunk patch. A sibling's uncommitted worktree hunk (seat `S4NoExec`, mtime 02:16:17) already covers the replay half of (4); the live tool's half is unaddressed.

## State reviewed

| item | value |
|---|---|
| lane | `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only; HEAD `34d82600`, worktree dirty — see §5) |
| build under review | `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` |
| `tools/kama-live-replay.py` @build | sha256 `9c11b2fbc77bd73e628b9870736f804c6b6be897ec59ca45ac16a81edafe7233` |
| `tools/kama-llamacpp-live.py` @build | sha256 `424b7808b3f897dd148f7a190dffb72159f9d0fa3ad75d9bfebad8be3bdad50a` |
| counters (frozen) | C1 `053ff502…121f5`, C2 `29dfd886…853ea` — both match `preregistration.json` `counter_sha256` (verified with `sha256sum`) |
| host | Linux 7.2.11-arch1-1, `vm.memfd_noexec=0`, `kernel.yama.ptrace_scope=1`, `/proc` mounted without `hidepid` |
| instrument | my own `git clone --shared` at the build commit in `/fast/scratch/hyaku/kama-r52/Sen1Exec/lane`; every run below used that clone or the host install `/home/vgpnk/.local/opt/llama-b11909/` (sha256 `35ac50fb…ff0`, the receipts' frozen server) |

Reproduction drivers are in `out/Sen1Exec/` (`witness_probe.py`, `probe_seals.py`, `noexec_probe.py`) with the JSON each produced. No counter was edited; both were hashed, not re-run (the L1's battery at the build is `measured/c1-build.out` `met=True`, `measured/c2-build.out` `met=True`).

## 1. `/proc/<live pid>/fd/N` — is a same-uid open a new exposure?

**No. It is a strict reduction.**

Evidence (`out/Sen1Exec/witness-evidence.json`): the live tool ran the build's own `--server-fd` path (sealed memfd, `--witness-dir`, witnessed while serving `{"status":"ok"}`, HTTP 200 on port 34041). From a *separate* process of the same uid:

```
live_fd_table      = {"0":"/dev/null","1":…log,"2":…log,"3":"/memfd:llama-server (deleted)"}
O_RDONLY  on /proc/<live>/fd/3  -> ok, seals 15, nlink 0, sha256 35ac50fb…ff0   (readable)
O_WRONLY  on /proc/<live>/fd/3  -> ETXTBSY (26) "Text file busy"                (image executing)
O_RDWR    on /proc/<live>/fd/3  -> ETXTBSY (26)
```

The executing image being write-opened is refused by `deny_write_access()` (ETXTBSY). With the image *not* executing — the window between `sealed_member()` (replay `:247`) and the child's `execve` — the write-open **succeeds** and every mutation still fails on the seals (`out/Sen1Exec/seals-and-third-party.json`, a sealed memfd of the same bytes, second process):

```
open_O_WRONLY ok; write -> EPERM(1); pwrite -> EPERM(1); ftruncate ↓/↑ -> EPERM(1);
mmap(PROT_WRITE) -> EACCES(13); F_ADD_SEALS(32) -> EPERM(1); content sha256 unchanged
```

Boundary: `/proc/pid/fd` dereference is gated by a `PTRACE_MODE_READ_FSCREDS` check (`proc_pid_fd(5)`), i.e. same uid (or `CAP_SYS_PTRACE`) — not another user. Compare the state this replaced: at base `9ff76b1` the same-uid process could open `/…/work-b1/server/llama-b11909/llama-server` **and rewrite or rename over it** (`controls/base.c1.out`: `running image link '…/llama-b11909/llama-server'`, `link count 1`). Today it can read the image from `/proc` and cannot alter it; another uid can no longer read it at a 0755 path at all.

Residual, noted not filed: a same-uid writer-open held *before* the exec makes `execve` fail with `ETXTBSY(26)` (measured: `third_party_write_open ok`, then `exec -> 26:Text file busy`). That is a denial strictly weaker than the `SIGKILL` the same uid may already send, and it does not survive as a defect.

Hygiene notes, no impact: the fd number is in the tool's own cmdline (`--server-fd 3`), which only helps an entity that can already scan `/proc/<pid>/fd`; the memfd name `llama-server` is debugging-only (`memfd_create(2)`: "serves only for debugging purposes"); the image is mode `0777` like every memfd (no setuid bit, same uid, no privilege change).

## 2. Is the memfd leaked into the server?

**No.** While the witnessed server was up and answering:

```
server_fd_table = {"0":"/dev/null","1":"/tmp/kama-llamacpp-live-nb61lgtl.log",
                   "2": same log, "3":"socket:[1001624175]"}      (no /memfd: entry)
server_exe      = "/memfd:llama-server (deleted)"  nlink 0  dev 00:01 inode 157486
maps            = 5 /memfd: segments (r--p, r-xp, r--p, r--p, rw-p) — W^X, private data only
```

Mechanism: the executable path `/proc/<live pid>/fd/N` (live tool `:1995-1996`) resolves in the **parent's** fd table; the `Popen` (live tool `:1985-1999`) passes no `pass_fds`, so CPython's `close_fds=True` closes the live tool's copy in the child. The log fd is unlinked at teardown (`teardown(proc, port, log_path)` → `os.unlink`); `ls /tmp/kama-llamacpp-live-*.log` is empty after each run.

Observation (optional, not a defect): neither layer records the child's fd table — the counter's `observe()` (`round52-replay-memfd-audit.py:328-358`) reads exe/listen/environ/maps only — so a future inheritance regression would be invisible to the claim's instruments. Current state verified clean by hand.

## 3. `LD_LIBRARY_PATH` = extracted tree — can a name collision pull an unexpected library?

**Not against the host, no; the path-loaded-library limit is real but confined to the same uid.**

The extracted tree at the build (receipt `server.install_tree`, 51 members = 28 `.so` + 22 executables + LICENSE; full list in `out/Sen1Exec/receipt-ok-live.json`; the archive-extracted tree is byte-identical to it — all 51 `install_tree` digests and `install_links_sha256` equal between the witnessed host-install run and the replay's own extracted tree): 28 `*.so` members — `libggml-base.so.0.27.0`, 14 × `libggml-cpu-*.so` (alderlake…zen4), `libggml-rpc.so`, `libggml.so.0.27.0`, `libllama.so.0.7.0`, `libllama-common.so.0.7.0`, 8 × `libllama-*-impl.so`, `libmtmd.so.0.7.0` — plus soname symlinks recorded by `install_links()` (live tool `:423`) and 22 executables.

What the witnessed server actually mapped:

```
tree : libggml-cpu-zen4.so, libggml-rpc.so, libggml-base.so.0.27.0, libggml.so.0.27.0,
       libllama.so.0.7.0, libllama-common.so.0.7.0, libllama-server-impl.so, libmtmd.so.0.7.0
system: ld-linux-x86-64.so.2, libc.so.6, libstdc++.so.6.0.36, libgcc_s.so.1, libm.so.6,
       libz.so.1.3.2, libzstd.so.1.5.7, libssl.so.3, libcrypto.so.3, libgomp.so.1.0.0,
       libbrotli*.so.1.2.0, /etc/ld.so.cache
```

* No tree member carries a system soname: `ldconfig -p | grep -iE 'libggml|libllama|libmtmd'` → none, so `LD_LIBRARY_PATH` precedence cannot displace libc/libstdc++/libz/libssl; every llama/ggml name is versioned (`libggml.so.0.27.0`…).
* The variable is set **only** in the child env (live tool `:1957`, `child_env = {k: os.environ[k] for k in CHILD_ENV_KEYS}` at `:1950`); the tool itself never takes `LD_LIBRARY_PATH`. `CHILD_ENV_KEYS = (PATH, HOME, LANG, LC_ALL, TMPDIR)` excludes `LD_PRELOAD`.
* `cwd = dirname(--server)` (`:1997`) is what lets ggml's bare-name `dlopen` find its CPU backend; together with the variable the search path is *tree + default*, exactly the coverage `$ORIGIN` gave before the memfd removed the exe's directory. No new directory is added.
* Residual (preregistered limit, "libraries still load from the extracted tree by path"): the tree is `drwxr-xr-x vgpnk:vgpnk` and writable by its owner, so a same-uid process can plant e.g. `libggml-base.so.0.27.0` after extraction and before load; the sealed memfd does not cover the libraries, and the archive digest (`acquire()`, replay `:203-211`) is checked before extraction only.

Free detection that is recorded but not used: the receipt carries `server.install_tree` (51 sha256) and `server.install_links_sha256`, yet the replay's `compare()` (`kama-live-replay.py:303-336`) checks only schema, outcome, `server.sha256`, `model.sha256`, checks and `projection()` (`:273-301`: props, slots, health, models, metrics, loading, teardown, ownership). A planted library therefore produces **no** replay mismatch. Smallest improvement (recommendation, not a defect — the limit is preregistered): add `install_tree` / `install_links_sha256` to `compare()` so the limit becomes observed.

## 4. `vm.memfd_noexec` at 1 or 2 — does the tool fail closed with a clear reason?

**Fails closed: yes. Clear reason at the build: no.** Defect F1 below.

Kernel contract (`mm/memfd.c`, `check_sysctl_memfd_noexec`, fetched from codebrowser.dev for `linux/mm/memfd.c:345-366`):

```
if (!(*flags & (MFD_EXEC | MFD_NOEXEC_SEAL))) {
        if (sysctl >= MEMFD_NOEXEC_SCOPE_NOEXEC_SEAL)      *flags |= MFD_NOEXEC_SEAL;
        else                                               *flags |= MFD_EXEC;
}
if (!(*flags & MFD_NOEXEC_SEAL) && sysctl >= MEMFD_NOEXEC_SCOPE_NOEXEC_ENFORCED) return -EACCES;
```

`MFD_NOEXEC_SEAL = 0x0008` and `MFD_EXEC = 0x0010` (`include/uapi/linux/memfd.h:8-14`); `F_SEAL_EXEC (32)` "the execute mode bits … cannot be modified … permanently not executable", and it implies GROW/SHRINK/WRITE/FUTURE_WRITE (`F_ADD_SEALS(2const)`). The build's `sealed_member()` passes neither flag (replay `:237`), so at sysctl 1 or 2 the kernel implies `MFD_NOEXEC_SEAL` and the image can never be executed.

Measured, same bytes, one process (`out/Sen1Exec/seals-and-third-party.json`):

```
flags CLOEXEC|ALLOW_SEALING          -> mode 0777, F_GET_SEALS 15, execv /proc/self/fd/N -> ok, exit 0
flags CLOEXEC|ALLOW_SEALING|NOEXEC   -> mode 0666, F_GET_SEALS 47, execv -> 13:Permission denied
```

End to end through the build's own tools (ablation: my clone's `sealed_member` adds `0x0008`, `out/Sen1Exec/ablation-mfd-noexec-seal.diff`; replay of `.ufo/waves/round-48/c2/live/receipt-1.json`, `--work` fresh, output `out/Sen1Exec/replay-noexec-ablation.json`):

```
replay: live_exit=2, match=False, mismatches=22 (incl. "live-exit:2", "server-exe:absent")
own_server = {"memfd":true,"seals":47,…}                      <- the replay already knew: 47 = 15|32
rerun receipt: outcome=setup-error  setup_error='launch-failed:PermissionError'
               server.fd = {seals:47, nlink:0, sha256:35ac50…}  <- sealed_fd() ACCEPTED it
live tool stderr = "" (empty), stdout = ""
```

Three separate acceptance points let the non-executable image through:

* replay `:249-250` — `if seals & SEALS_ALL != SEALS_ALL: raise memfd-not-sealed` accepts 47 (no `F_SEAL_EXEC` test);
* live `sealed_fd()` `:786-812`, gate at `:796` — same 15-bit predicate, then size and digest;
* live `:2001-2002` — the only place the exec refusal surfaces: `SetupError(f'launch-failed:{type(exc).__name__}')`, which drops `errno`, `strerror` **and** the memfd, where kernel `execve` returned `EACCES`.

The replay's operator output names none of it: `server-exe:absent` + `live-exit:2` (replay `:439`), and the reason is only in the nested receipt. A counter run on such a host would report `bind=0 sealed=0 met=False` (`sealed_exe` `:361-392` never sees a live child) — fail-closed, silently.

Two consequences worth recording: on a sysctl-1/2 host the round-52 capability cannot be met by an unprivileged user at all unless `MFD_EXEC` is requested (honoured at 1, `EACCES` at 2), and the check that would have caught it (`F_SEAL_EXEC` present after sealing) is free — it is already in `F_GET_SEALS`.

### F1 — low, operability/diagnosis: a non-executable memfd passes every app-level check and dies at `execve` with an opaque reason

* files: `tools/kama-live-replay.py:237,249-250`; `tools/kama-llamacpp-live.py:786-812` (gate `:796`), `:2000-2002`
* show it: `out/Sen1Exec/live-noexec-memfd.json` (build's live tool, noexec memfd: `exit 2`, `stderr ""`, `receipt server.fd.seals 47`, `receipt_errors null`) and `out/Sen1Exec/replay-noexec-ablation.json`
* proposed fix, unified diff, applies to `5dacf2c` (dry-run `patch -p1 --dry-run` OK): **`out/Sen1Exec/memfd-noexec-clear-reason.diff`** — (a) replay `sealed_member`: after sealing, `if seals & F_SEAL_EXEC: raise Refused(f"memfd-noexec:vm.memfd_noexec={memfd_noexec()}:seals={seals}")`; (b) live `sealed_fd`: same test → `SetupError('server-fd-not-executable:F_SEAL_EXEC:memfd_noexec=…')`; (c) live `Popen` except: keep `errno`/`strerror`.
* measured effect of the patch (applied to a scratch clone, never to the lane):
  * noexec memfd → `exit 2`, `setup_error='server-fd-not-executable:F_SEAL_EXEC:memfd_noexec=0'`, `server.fd` absent (`out/Sen1Exec/live-noexec-memfd.json` pre-patch; receipt field quoted from the patched run)
  * replay + ablation → `exit 2`, `refused='memfd-noexec:vm.memfd_noexec=0:seals=47'`, `mismatches=0`, no server started (`out/Sen1Exec/replay-noexec-patched.json`)
  * normal path unchanged → `live_exit 0`, health `[200, {"status":"ok"}]`, `server_exe /memfd:…`, `server_fd_table` without the memfd, receipt `seals 15` (`out/Sen1Exec/witness-patched-live-in-clone.json`)

## 5. Concurrent lane delta (coordination, not a finding against the build)

While this review ran, the lane's **worktree** (not the build commit) gained an uncommitted hunk in `sealed_member` — `git -C <lane> diff HEAD -- tools/kama-live-replay.py`, mtime 02:16:17, comment credits seat `S4NoExec`:

```
-        fd = os.memfd_create(os.path.basename(member), os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
+        flags = os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING
+        try:
+            fd = os.memfd_create(os.path.basename(member), flags | getattr(os, "MFD_EXEC", 0x0010))
+        except OSError as exc:
+            if exc.errno != errno.EINVAL: raise Refused(f"memfd-create-failed:{exc.strerror}") from None
+            fd = os.memfd_create(os.path.basename(member), flags)
```

Assessment of that hunk against §4: at sysctl 1 the explicit `MFD_EXEC` suppresses the implication and the exec works (kernel branch quoted above); at sysctl 2 `memfd_create` returns `EACCES` → `Refused('memfd-create-failed:Permission denied')`, fail-closed with a reason (better than `launch-failed:PermissionError`, though still not naming `vm.memfd_noexec`); pre-6.3 kernels take the `EINVAL` fallback. It does **not** cover the live tool, and it leaves the F_SEAL_EXEC blind spot on any path where `MFD_EXEC` is dropped or refused-and-retried (e.g. a seccomp filter that returns `EINVAL`); the post-seal `F_SEAL_EXEC` check in my diff is orthogonal to that hunk and catches every cause. Integration choice is the L1's.

## Findings

| id | sev | what | evidence |
|---|---|---|---|
| F1 | low | non-executable (`F_SEAL_EXEC`) memfd accepted by `sealed_member`/`sealed_fd`; dies at `execve` with `launch-failed:PermissionError`, empty stderr, replay shows only `live-exit:2` | `live-noexec-memfd.json`, `replay-noexec-ablation.json`, diff + patched receipts |
| F2 | info | same-uid writer-open on the sealed image before exec ⇒ `execve` `ETXTBSY`; DoS weaker than the `SIGKILL` the same uid may already send | `seals-and-third-party.json`, inline probe in §1 |
| F3 | info | `install_tree`/`install_links_sha256` recorded but not compared by replay `compare()`, so a planted tree library yields no mismatch (preregistered limit) | replay `:273-336`; receipt `server.install_tree` |
| F4 | info | no layer records the server's fd table, so memfd inheritance into the child would be unobserved (clean today) | `witness-evidence.json` server_fd_table vs counter `observe()` |

Nothing was found that makes the round-52 C1 claim false at the build; F1 is a diagnosis/operability gap on hosts the claim does not cover, and it lands as a clear reason plus a pre-exec refusal with the patch.

## Files written

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Sen1Exec.md` (this report)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Sen1Exec/` — `witness_probe.py`, `probe_seals.py`, `noexec_probe.py`, `witness-evidence.json`, `witness-patched-live-in-clone.json`, `seals-and-third-party.json`, `live-noexec-memfd.json`, `receipt-ok-live.json`, `rerun-receipt-noexec.json` (unpatched live receipt: `setup_error='launch-failed:PermissionError'`, `server.fd.seals 47`), `receipt-noexec-patched.json`, `replay-noexec-ablation.json`, `replay-noexec-patched.json`, `ablation-mfd-noexec-seal.diff`, `memfd-noexec-clear-reason.diff` (sha256 `e4597ce7…5d8a15`)
