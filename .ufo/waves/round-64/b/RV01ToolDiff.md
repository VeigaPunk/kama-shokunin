# RV01ToolDiff — review of tools/kama-completion-live.py (v3, round 64)

Seat: RV01ToolDiff (reviewer, leaf, no subagents). Axis: operability. Milestone: review tool v3.
Tree reviewed: f6a4ea9a8b5a876d685b08e7e582ec0723412a4a (scratch clone `--shared`, rev-parse verified).
Diff under review: 0c1eff3c..f6a4ea9a for tools/kama-completion-live.py (+57/-2) plus the whole tool
(673 lines) and its dependency tools/kama-llamacpp-live.py primitives (`_listen_inodes`,
`_proc_listener_inode`, `_tcp6_is_loopback`, `port_owned_by`, `prepare_witness_dir`, `hold_for_witness`,
`pick_port`, `refused_ports`).

Advisory finding list only. No verdict on the frozen claims, no edits to lane source, no commit.
Evidence (receipts, drivers, matrix output) is under `.ufo/waves/round-64/b/out/RV01ToolDiff/`.

## 0. Requested live runs (bare x5, hold x5)

| run | mode | verdict | rc | holders | notes |
|---|---|---|---|---|---|
| bare1..5 | bare | REQUEST_OK x5 | 0 x5 | 1 each (child, exe sha = pin `b6a31a8e…`) | no failed evaluated check |
| hold1..5 | hold (driver releases after ready.json) | REQUEST_OK x5 | 0 x5 | 1 each | hold.json removed after each run |

REQUEST_OK failures: **0 of 10**. Nothing in the requested runs flaked.
The defects below were found by targeted runs (section 2), not by the 10 nominal runs, which is the
point: the nominal path is green while the holders and hold-window claims are unproven.

Tool/versions used: python 3.14.8 (host), llama-server `/home/vgpnk/.local/bin/llama-server` →
`llama-b11755` (sha256 b6a31a8e…, matches DEFAULT_SERVER_SHA). `sudo -n` (passwordless, pre-installed)
was used once for a privileged `pidfd_getfd` demo (section 2, D1). Nothing installed or upgraded;
no pacman transaction; no changes under ~/.local/bin.

## 1. Findings (ranked)

### H1 — holders scan is blind to processes it cannot read; the receipt does not say so (high)
`_proc_holders` (tool lines 190-223): `os.listdir(f'/proc/{pid}/fd')` raises PermissionError for any
pid of another uid (non-root reviewer), and line 203-205 `continue`s silently. The pid is neither
recorded nor counted, so `listener_holders_pinned` (`len(holders)==1`) can pass with an unread second
holder. `kama-llamacpp-live._listen_inodes` plus a same-uid scan cannot prove "every holder".
Observed (D1, section 2): a root process duplicated the child's run-port listener fd during the hold
window; the same-uid scan returns only the child; the receipt is REQUEST_OK with one holder.
This is the exact property the frozen C1 sentence names ("every holder of the run-port listener is
the hold pid"). The tool is not in a position to prove it unprivileged; the receipt must at least
record the unreadable pid count (and the counter must say so). Note the counter's `holder_pids`
(tools/round64-c1-counter.py ~line 264-272) has the same skip for non-own-uid pids (it fails closed
only for own-uid unreadable tables). That bears on the frozen predicate; the L1 decides.
Fix shape: record `unreadable_pids` (pid + stat uid) in `listener_holders`; state the boundary in the
docstring; the counter scans as root or records the boundary explicitly. Do not make "any unreadable
pid" fail, because every host has root daemons and the check would then always fail.

### H2 — holders check is placed before the hold window and never re-taken (high, placement)
Tool order: holders scan line 521 → hold.json written line 533-546 with `'holders': holders`
(pre-window snapshot) → `hold_for_witness` line 547 (window) → teardown 572+. Nothing re-scans the
listener after release or before SIGTERM. A holder that attaches during the window is invisible to
the tool's own check. Observed (D1): the root holder attached after ready.json (i.e. after the
pre-window scan) and was present for the whole window; receipt `listener_holders` lists only the
child; `checks.listener_holders_pinned` passed; verdict REQUEST_OK; the root process released its
dup before `release` was written (so teardown was clean, which is why the receipt is green).
Fix shape: re-run `_proc_holders` after `hold_for_witness` returns and before teardown; record it as
`listener_holders_after_hold`; require equality with the pre-window set; keep hold.json's
`holders` labelled as the pre-window snapshot.

### M1 — receipt `hold` is overwritten, dropping the witness record (medium)
Line 554 `receipt['hold'] = w` (schema, dir, port, pid, released, waited_ms, orphaned) is replaced at
teardown line 615 `receipt['hold'] = {'dir': args.hold_dir, 'released': released}`. Observed
(`receipts/hold1.json`): `receipt.hold = {'dir': '…/hold1', 'released': True}`. `waited_ms` and
`orphaned` (the parent-death signal the witness primitive exists to record) never reach the receipt.
Also `dir` is `args.hold_dir` unnormalised, while the witness record uses abspath.
Fix: write the teardown fields under a separate key (e.g. `hold_teardown`) or merge.

### M2 — hold.json survives every failure path; stale file names a dead pid with a fresh `at` (medium)
hold.json is unlinked only when `hold_for_witness` returns normally (lines 549-552). The except
branch (559-568) does not unlink it, a SIGKILL of the tool does not run finally, and
`prepare_witness_dir` (kama-llamacpp-live.py 290-325) clears ready.json, release and tmp names but
NOT hold.json. Observed (`receipts/stale*.json`, dir `hold_stale`):
```
tool killed rc=137
child gone (pdeathsig)
dir after SIGKILL:
hold.json
ready.json
hold.json pid 531086 at 2026-10-29T00:14:40.636Z
== setup-error run into same hold dir
rc=2
dir after SETUP_ERROR run:
hold.json
ready.json
SETUP_ERROR
```
So a later receipt-less SETUP_ERROR leaves a hold.json whose pid is dead and whose `at` is fresh. A
freshness rule keyed on `at` alone would accept it. Fix: unlink hold.json in `prepare_witness_dir`
(or before the server starts), and the counter must check pid liveness against ready.json, not `at`.

### M3 — SETUP_ERROR path escapes as an uncaught exception: traceback, rc=1, no receipt (medium)
`try:` starts at line 321. Everything before it can raise without a receipt: `sha256_file` lines
278-279, `_live.refused_ports()` 293, `_live.pick_port()` 294 (SetupError), `os.makedirs(hold)` 309
(OSError), `_live.prepare_witness_dir` is inside a try (312, ok). `main()` (line 662) has no handler.
Observed:
- A1 `--port 45987` (my own listener, in use): `kama_llamacpp_live.SetupError: port-in-use:45987`, rc=1, no JSON.
- A3 `--port 70000`: `kama_llamacpp_live.SetupError: explicit-port-out-of-range`, rc=1, no JSON.
- C1 `--hold-dir <regular file>`: `FileExistsError: … notadir`, rc=1, no JSON.
- C2 unreadable `--model`: `PermissionError: … unreadable.gguf`, rc=1, no JSON.
(C3 `--work` under a regular file is caught: `SETUP_ERROR NotADirectoryError`, rc=2.)
rc=1 is the documented "evaluated check failed" code, so an unhandled setup fault is indistinguishable
from a FAIL by exit code, and the run leaves no receipt. Fix: move the input block into the try, or
wrap `run()` in `main()` so any SetupError/OSError emits `SETUP_ERROR` and rc=2.

### M4 — exit-code and verdict contract disagrees with the docstring; SETUP_ERROR without reason (medium, schema text)
- Docstring (lines 42-45): rc 1 = "at least one evaluated check failed"; rc 2 = setup error. Observed (B,
  `--server-sha256 00`): `SETUP_ERROR {'model_digest': (True, True), 'server_digest': (False, True)}`,
  **rc=2** with an evaluated failing check. Lines 288-291 set SETUP_ERROR after check(); the
  contract as written is wrong in this path.
- Same receipt has `verdict: SETUP_ERROR` and **no `setup_error` key** (verified). The reason lives only
  in `checks.server_digest.reason`. Lines 282-291 need a setup_error string.
- Docstring names only REQUEST_OK; FAIL, NOT_EVALUATED and SETUP_ERROR are undocumented verdicts.
- SETUP message text (lines 346-348): `server not ready within {ready_timeout}s` is printed when the
  child exited at once (`last=None/child-exited`). Observed A2: `server not ready within 60.0s` on a
  run that ended within a second (bind to port 80 denied, non-root). Wrong text on the failing path.

### M5 — wildcard and non-loopback listeners are invisible; the comment says the opposite (medium)
`_listen_inodes` (kama-llamacpp-live.py 619-638) excludes 0.0.0.0, :: and LAN addresses. Its docstring
says "Wildcard addresses are deliberately not counted — fail-closed"; excluding them is fail-OPEN.
Address matrix (`receipts/listen_matrix.out`, same run):
```
       127.0.0.1: _listen_inodes=['1861344056'] _proc_holders=[1487298] port_closed_by_tool=False
       127.0.0.2: _listen_inodes=['1861336049'] _proc_holders=[1487298] port_closed_by_tool=False
             ::1: _listen_inodes=['1861339615'] _proc_holders=[1487298] port_closed_by_tool=False
::ffff:127.0.0.1: _listen_inodes=['1861339669'] _proc_holders=[1487298] port_closed_by_tool=False
         0.0.0.0: _listen_inodes=[] _proc_holders=[] port_closed_by_tool=True
              ::: _listen_inodes=[] _proc_holders=[] port_closed_by_tool=True
   192.168.0.253: _listen_inodes=[] _proc_holders=[] port_closed_by_tool=True
```
IPv6 loopback and IPv4-mapped loopback are counted correctly (`_tcp6_is_loopback`). Wildcard/LAN are not.
Consequence: `teardown_port_closed` (tool line 604-609) passes while a 0.0.0.0 or :: listener from a
forger that binds after child exit survives. The counter's `listeners()` counts any address, so the
counter would catch this; the tool's own receipt would not. Also `port_owned_by` returns None (not
False) for wildcard-only listeners, which the first-answer gate treats as "not owned", so the
message is misleading. Fix: count wildcard addresses (0.0.0.0, ::, and any non-loopback bind on the
port) as listeners for the holders and teardown checks, and correct the comment. The module docstring
line 24-26 ("every process that holds a LISTEN socket on the run port") is wrong until this is done.

### L1 — schema/doc and dead-code text (low)
- Module docstring line 20-21 "writes nothing outside the receipt and the hold dir": false, server.log
  is written under --work (line 327).
- Docstring "captures ... completion2 ... for every POST": completion2 exists only when the completion
  envelope passed (line 491 inside `if ok_env`).
- `# HOLDERS-RETURN` marker (line 223): no reader in tools/ or .ufo/waves/round-64 (grep). Remove or document.
- `finally: pass` (569-570): no-op. `log_f` is not closed on the early SETUP returns (338-350) or on the
  except path (559-568); only the teardown path closes it (611-613).
- Teardown (572-630) is outside the try: a second `proc.wait(timeout=10)` TimeoutExpired (line 591)
  propagates as a traceback with no receipt.
- `hold.json` is written with `open(…,'w')`, not tmp+replace as ready.json is. Ordering protects a
  reader that waits for ready.json; a reader that polls hold.json alone can see a partial file.

### L2 — `_proc_holders` race windows (low; [INFERENCE] from code, not observed)
- Holder exits between the fd match (209-211) and the exe readlink/hash (217-218): `exe` and
  `exe_sha256` become None and the holder is recorded with null identity, so the check FAILs. That is
  fail-closed but produces a spurious FAIL, not a pass.
- Pid reuse between the fd match and the exe read: the recorded exe/digest can belong to a different
  process than the one holding the fd. Fix: read /proc/<pid>/stat starttime before and after, or hold
  a pidfd.
- Zombies: a zombie has no fd table and no exe, so it is not a holder. No defect there.

## 2. Targeted demonstrations (what was actually run)

D1 — root holder during the hold window (`demo_rootholder.sh`, `root_holder.py`, sudo pidfd_getfd, syscall 438)
```
tool=911424 child=912132 port=39733
listener inode=1858593458 child fd=3
root holder pid=915324 ; me=915324 dup_fd=4 target=912132:3
-- root's fd table (root view):
lrwx------ 1 root root 64 Oct 28 21:15 4 -> socket:[1858593458]
-- same-uid view of root's fd table:
ls: cannot open directory '/proc/915324/fd': Permission denied
-- same-uid _proc_holders during hold:
  holders = [{'pid': 912132, 'exe': '/home/vgpnk/.local/opt/llama-b11755/llama-server', ...}]
root holder before release: me=915324 dup_fd=4 target=912132:3 released
tool rc=0
receipt verdict= REQUEST_OK  listener_holders= [(912132, '/home/vgpnk/.local/opt/llama-b11755/llama-server')]
receipt hold= {'dir': '…/hold_root', 'released': True}
```
The root process held the same listener inode (`socket:[1858593458]`) for the whole window; the receipt is green.

D2 — stale hold.json (section M2), D3 — SETUP escapes (A1, A3, C1, C2; section M3), D4 — rc/setup_error
(section M4), D5 — listener address matrix (section M5). Raw output is in receipts/.

## 3. What is correct (checked, no finding)
- The 10 nominal runs (section 0) are clean: REQUEST_OK, one holder, exe pinned.
- IPv6 loopback and IPv4-mapped loopback are counted by `_listen_inodes`; 127.0.0.2 is counted.
- `port_owned_by` treats an unreadable own-process fd table as unknown and the first-answer gate
  fails closed (SETUP).
- PDEATHSIG + hold-end on parent death: the SIGKILL demo showed the child gone after the tool died.
- `prepare_witness_dir` removes ready.json and release before the server starts (no stale release).

## 4. Residual risk and verification gaps
- Not checked: pid reuse and exit races (L2) are from code reading only.
- Not checked: whether the holders check passes with a root holder present at the pre-window scan (the
  demo attaches it after ready.json). The EACCES skip is shown directly by calling `_proc_holders`.
- Not checked: any counter control. The counter is not this seat's item; H1 and M5 bear on its frozen
  sentence and are passed to the L1 as facts, not verdicts.
- Not run: the forged-tool replays (controls/forge-*.patch); the L1 or counter seats own them.
- Host caveat: another seat's MT04ArgvSpoof tool process was running on the host during my runs; I did
  not touch it (`pgrep` shows it under its own scratch path). My root holder and listeners all exited.

## 5. Tally

bare 5/5 REQUEST_OK, hold 5/5 REQUEST_OK (0 failures); findings H1 H2 (high), M1-M5 (medium), L1 L2 (low); D1 reproduced H1+H2 (root holder, REQUEST_OK); L2 from code reading only.
