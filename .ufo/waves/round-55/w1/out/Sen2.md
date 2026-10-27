# Sen2 — C1 counter /proc access review (round 55)

**Verdict: no write primitive, no ptrace attach, no cross-uid/cross-process write; the descendant gate covers every per-pid read of the announced server; ROW_CAP bounds every `/proc/<pid>/mem` read. One medium verdict-integrity defect: on a host with Yama `ptrace_scope > 1` the counter cannot read its own descendants but still exits 1 with `met=False` (a falsification) instead of `could-not-evaluate` (exit 2), and the preregistered kill rule reads that exit as claim falsification. Current host is `ptrace_scope = 1`, so the frozen measurements are unaffected.**

Reviewed artifact: `tools/round54-replay-code-audit.py` at `9c60eae6f7ed84f7da93d219a406aadc30958c6c`, sha256 `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` — equal to `claims.C1.counter_sha256` in `.ufo/waves/round-55/preregistration.json`.

```
$ git -C <clone> rev-parse HEAD
9c60eae6f7ed84f7da93d219a406aadc30958c6c
$ sha256sum tools/round54-replay-code-audit.py
c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af  tools/round54-replay-code-audit.py
```

All paths below are relative to that file unless stated otherwise.

## 1. Every /proc path the counter opens

Enumerated by `grep -n '/proc' tools/round54-replay-code-audit.py` (comments filtered) and `grep -n 'os\.open'`:

| Path | Line(s) | Operation | Which pid | `descends_from` gate |
|---|---|---|---|---|
| `/proc/net/tcp`, `/proc/net/tcp6` | 253–255 | `open()` text, full read | n/a (host-wide socket table) | n/a — no pid |
| `/proc` | 335 | `os.listdir` | n/a | n/a |
| `/proc/<pid>/stat` | 290 (via `stat_fields`, 287) | `open()` text read | **every numeric pid on the host** (tree build, line 335) plus snapshot/replay/announced pids (657, 663, 695, 697, 808, 839) | host-wide scan is ungated by construction; specific pids are the invoker's snapshot descendants or the replay |
| `/proc/<pid>/fd`, `/proc/<pid>/fd/<n>` | 275, 277 | `listdir` + `readlink` | announced server pid | **yes** (697) |
| `/proc/<pid>/environ` | 326 (`environ_keys`) | `open(..., "rb")`, full read | announced pid (435) **and its direct parent** (407–411) | **yes** for the announced pid; the parent is by definition on the same chain (see §2) |
| `/proc/<pid>/maps` | 366 (`mapped_model`), 481 (`code_observe`, twice) | `open()` text, full read | announced pid | **yes** |
| `/proc/<pid>/mem` | 487 | `os.open(..., os.O_RDONLY)` + `os.pread` (533) | announced pid | **yes** |
| `/proc/<pid>/exe` | 398 (`sha_file`), 583 `readlink`, 584 `os.open(..., os.O_RDONLY)`, 589 `fstat`, 591 `fcntl(F_GET_SEALS)`, 596–598 full hash | open/read/link | announced pid | **yes** |

No other `/proc` node is touched: no `/proc/<pid>/status|cmdline|task|root|cwd|syscall|stack|pagemap`, no `/proc/sys/*` (the Yama defect in §5), no `/proc/kcore`.

## 2. The descendant gate

Single check, `bind_one` lines 694–703:

```
pid, port = ready["pid"], ready["port"]      # 696: announced by the replay, untrusted
snap = descendants(p.pid)                    # 695
rp = replay_pid(p)                           # 657: the invoker's only child
if rp is None or not descends_from(pid, rp): # 697
    probs.append("server pid ... does not descend ... no /proc read made")  # 701-702
else:
    env_leg(pid); observe(pid,...); sealed_exe(pid); code_observe(pid,...) x2   # 704-717
```

`descends_from` (350–359) walks `ppid` via `/proc/<pid>/stat` at most 64 steps, returns False on any stat failure and at pid ≤ 1. `replay_pid` returns None unless the invoker has exactly one child, so ambiguity fails closed. All five per-pid readers (`environ`, `exe`, `maps`, `mem`, `fd`) are inside the `else`, so *every* read of the announced pid is gated; the receipt path for a named non-descendant is "no /proc read made" with `bind=False`.

The one ungated per-pid read family is the `/proc/<pid>/stat` host-wide scan in `descendants()` (335–348) — required to build the tree, reads only state/ppid/starttime, no gate possible and none needed. `teardown_leg` (834+) reads no `/proc/<pid>/{environ,exe,maps,mem}` of the announced pid; it only tests membership in the snapshot (841–842).

Residual (low): the gate is evaluated once and the announced pid's `starttime` (captured in `snap`) is never re-checked before the reads, so a pid-reuse race inside the gate→read window could read a foreign same-uid process (read-only). Any such read is compared against the frozen digests and cannot produce `met=True`; under `ptrace_scope 1` the kernel also refuses non-descendant `mem`.

## 3. ROW_CAP

`ROW_CAP = 64 << 20` (line 145) = 67,108,864 bytes, applied at 524 only to rows whose pathname is under the replay's unpacked tree:

```
length = hi - lo
if length > ROW_CAP:  probs.append(... "not read"); continue   # 524-526
if off + length > len(data):  probs.append(... past the member); continue  # 528-531
got = os.pread(mem, length, lo)                                  # 533
```

So every `/proc/<pid>/mem` read is bounded twice: by ROW_CAP and by the archive member's own length (a row that overruns the member is a problem, not a short read). Non-tree rows (host files, memfds, anonymous pages) are never read from `mem`. There is exactly one `os.pread` site (533). No zero-padding path exists (overrun is a problem, line 528).

Unbounded `/proc` reads outside ROW_CAP (low, DoS-only, fail-closed): `maps` (366, 481) and `exe` (398, 584/596) are read in full with no size cap; a hostile descendant could inflate either and slow the counter. It cannot yield `met=True`.

## 4. Write-access audit — clean

- Only two `os.open` calls in the file: 487 (`/proc/<pid>/mem`) and 584 (`/proc/<pid>/exe`), both `os.O_RDONLY` (numerically 0). `grep -nE 'O_CREAT|O_WRONLY|O_RDWR|O_APPEND|O_TRUNC'` → no matches.
- No `ptrace(2)` attach and no `process_vm_readv/writev`: `grep -nE 'ctypes|ptrace|vm_readv|vm_writev'` → only docstring/comment lines 100–101, 699.
- `fcntl` is used only with `F_GET_SEALS` (591), a read-only query.
- `os.access(path, os.W_OK)` (558, 561) is a *check* on a mapped host library, not a write.
- Writes exist only under `--scratch`: the planted `sitecustomize.py` + marker (625–628, under `$S/canary-*`), the replay log (638, `$S`), the release marker (720–721, `$S/wd-*`), the downloaded model/archive (905, 918, `$S`), the receipt (964) and `rmtree(S)` (968).
- Process control, not procfs writes: `os.kill(..., SIGKILL)` (666, 843) and `os.killpg` (671) target the invoker's snapshot descendants / the session group created by `start_new_session=True` (641).

## 5. Yama ptrace_scope — current value and the scope-2 path

```
$ cat /proc/sys/kernel/yama/ptrace_scope
1
$ sysctl kernel.yama.ptrace_scope
kernel.yama.ptrace_scope = 1
```

Current host is **1** (restricted): a process may ptrace its own descendants, so the counter's reads of the replay's descendants are permitted, and the frozen receipts prove they happened (below). The counter never reads this sysctl; its docstring states the requirement only (`tools/round54-replay-code-audit.py:100-101`: "ptrace read access to its own descendants (Yama ptrace_scope 0 or 1)").

Under `ptrace_scope = 2` (admin-only; only `CAP_SYS_PTRACE`), `/proc/<pid>/{environ,maps,mem,exe,fd}` of a same-uid non-root process are denied even when it is a descendant (`PTRACE_MODE_ATTACH/READ_FSCREDS` checks; `stat` still works, so the gate at 697 still passes). The counter then appends, for each replay:

- `env: environ of pid N unreadable` (435) and the observe-side environ problems (407–411) → `envnames=False`, `bind=False`;
- `sealed: /proc/<pid>/exe unopenable: Permission denied` (586), plus `exe sha256 None ...` (399) → `sealed=False`;
- `code: maps unreadable: Permission denied` (484) or `/proc/<pid>/mem unopenable` (489) → `code=False`, and `hostlibs=False`, `twopass=False` via `cobs is None` (823–830);
- `met = bool(... all legs ...)` (954) → `False` → `return 0 if met else 1` (966) = **exit 1**, with no `could-not-evaluate` line. Exit 2 is reachable only from the git branch (894–895).

The denial path itself was exercised directly against the frozen module (read-only calls; the module was loaded from the clone after the sha256 check above). Output in `probe-denial.json`, script in `probe.py`:

```
$ python3 probe.py ; echo exit=$?
{ "sealed_exe(1)":  {"ret": "None", "probs": ["sealed: /proc/1/exe unopenable: Permission denied"]},
  "env_leg(1)":     {"ret": "None", "probs": ["env: environ of pid 1 unreadable"]},
  "code_observe(1,None)": {"ret": "None", "probs": ["code: maps unreadable: Permission denied"]} , ...}
exit=0
```

The probe's `EACCES` comes from the uid check on pid 1, not from Yama (writing `/proc/sys` is out of bounds for this seat), but it lands on exactly the three branches a scope-2 denial takes; no branch can turn a denial into a pass — every read failure appends a problem and every leg consumes it.

### Defect D1 (medium, verdict integrity)

`tools/round54-replay-code-audit.py:966` (with 954 and 894–895): an environment that denies the ptrace-mode reads is scored as a falsifying measurement (`met=False`, exit 1) rather than "could not evaluate" (exit 2). Per `preregistration.json` `claims.C1.kill_rule`, "the claim is falsified if ... the build measurement prints met=False", so re-running the frozen measurement on a `ptrace_scope=2` host (or any LSM/hidepid policy denying those nodes to the counter's own descendants) would declare C1 falsified with zero evidence of falsification. It is not a security escalation and cannot pass a cheat (fail-closed), but it corrupts the verdict taxonomy the kill rule relies on.

Smallest remediation (full text in `proposed-fix.diff`, `git apply --check` exit 0): refuse to measure when the scope is not 0/1, before any work is done.

```diff
--- a/tools/round54-replay-code-audit.py
+++ b/tools/round54-replay-code-audit.py
@@ -880,6 +880,15 @@
     a = ap.parse_args(argv)
+    try:
+        with open("/proc/sys/kernel/yama/ptrace_scope") as fh:
+            scope = int(fh.read().strip())
+    except (OSError, ValueError):
+        scope = 0
+    if scope > 1:
+        print(f"could-not-evaluate: Yama ptrace_scope {scope} (need 0 or 1); the counter "
+              "cannot read its descendants' environ/exe/maps/mem")
+        return 2
     if a.out:
```

For the frozen artifact this is a finding only; the counter, preregistration and receipts are not edited. Residual after the fix: an LSM/hidepid denial that is not Yama still yields exit 1; the robust completion is to classify `EACCES`/`EPERM` on `environ|exe|maps|mem` as could-not-evaluate instead of a problem, which needs a leg-level signal (larger than the smallest fix).

## 6. Evidence that the reviewed code actually ran under scope 1

`c1-build.out` (copied here from `.ufo/waves/round-55/measured/`) is the freeze measurement at tip `9c60eae6…`, `met=True`, and its detail lines can only be produced if the gated reads succeeded for all three replays: `coderuns=3/3` (mem reads), `envnames=3/3` (environ reads), `sealedruns=3/3` (exe opens + `F_GET_SEALS`), e.g. `code b1: 8 archive files (16 executable ranges) byte-equal in /proc/<pid>/mem to the counter's own archive, 13 root-owned host files`. `base.c1.out` is the red control (`newrow=0`, `met=False`, exit 1 per the preregistration) and shows the same `/proc` legs green at the base tip, i.e. the base control fails for its intended reason, not for an access denial. No leftover `llama-server` process: `pgrep -af llama-server` → no match (exit 1). This seat started none.

## 7. Files written

- `.ufo/waves/round-55/w1/out/Sen2.md` (this report)
- `.ufo/waves/round-55/w1/out/Sen2/proposed-fix.diff` (sha256 `a14747c0…`)
- `.ufo/waves/round-55/w1/out/Sen2/probe.py`, `probe-denial.json`
- `.ufo/waves/round-55/w1/out/Sen2/c1-build.out` (sha256 `4f8f277b…`), `base.c1.out` (sha256 `3d6736a3…`)

No tool installs. Scratch `/fast/scratch/hyaku/kama-r55/w1/Sen2` removed after the report.
