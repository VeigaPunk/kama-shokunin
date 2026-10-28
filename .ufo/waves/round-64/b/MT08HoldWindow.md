# MT08HoldWindow - round 64, wave b, C1 (operability): counter-owned hold window

Seat: MT08HoldWindow (leaf, no subagents). Axis: operability. Milestone: falsify C1 binding.
Tip under test: f6a4ea9a8b5a876d685b08e7e582ec0723412a4a (freeze base 0c1eff3c...).
Counter scored unmodified at its committed tip: `tools/round64-c1-counter.py --repo <clone> --tip <rev> --work <scratch>`.
Scratch clone: /fast/scratch/hyaku/kama-r64/b/MT08HoldWindow/clone (detached at the tip; each mutant committed on top of it).
Evidence: `.ufo/waves/round-64/b/out/MT08HoldWindow/` (receipts/<mutant>/out.txt+err.txt, patch-<mutant>.diff, helper.py, spy.py, helper.log).

## Result in one table

| id | forged tool (committed in clone) | counter output (met=) | verdict | decided by (procfs observation or its absence) |
|---|---|---|---|---|
| base | none (tip) | met=True, 76/76, live_ok=1 | reference | - |
| a | never writes hold.json; ready.json only (hold.json write cut) | live_ok=0, met=False | KILLED | absence of hold.json: no binding snapshot is ever taken |
| b | hold dir replaced by a symlink to a tool-prepared dir; honest child | met=True | SURVIVED - equivalent, not a forgery | none of the verdict inputs depend on the hold dir's identity |
| c | release ignored: child serves 90 s after the counter's release | live_ok=0, met=False, `live: ["teardown_observed"]` | KILLED | pid_gone(child)=False and a LISTEN socket on the run port at the 30 s teardown deadline |
| d | child not tied to the tool (no pdeathsig); receipt claims clean teardown and exits with child alive | live_ok=0, met=False, `live: ["teardown_observed"]` | KILLED | same two observations; the receipt's own teardown claim is ignored |
| e | hold.json names a pinned server started before the run (pid/port of a leftover) | live_ok=0, met=False, `live: ["bind_ancestry","bind_claim","hold_fresh","live_pid","live_port","teardown_observed"]` | KILLED | ppid chain of the holder lacks the tool pid; holder start ticks predate the tool; leftover still listening after release |
| f | pidfd_getfd the child's listener, hand it to a pre-existing non-dumpable helper over SCM_RIGHTS, SIGSTOP child; helper answers probes; unconditional | live_ok=1/1 (live binding ACCEPTS), but overall met=False from forge-family collateral | live SURVIVED; overall met=False for a non-binding reason | the helper is invisible to the counter's holder enumeration (see section 2) |
| f2 | f with the hook gated to the counter's `live` run only (so the patch-derived controls stay honest) | **met=True** | **SURVIVED - forgery accepted by the committed counter** | same; the helper is recorded as `unreadable_old`, which is never graded |
| f3 | control: the same helper spawned by the tool during the run | live_ok=0, met=False, `live: ["bind_holders"]` | KILLED | `unreadable_own=[1332143]` (the spawned helper): start ticks >= tool ticks |

Assignment items (a)-(e) are all KILLED or equivalent. The valuable finding is f2 (section 2).

## 1. Per-item outputs (pasted one-liners)

base (tip f6a4ea9, 9 s):
```
tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True
```

**(a) never writes hold.json, ready.json only - KILLED.** Commit 3e2d4f53 (two lines cut at kama-completion-live.py:545-546).
```
tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=['bind', ...] eval_selftest=0/3 errors=1 met=False families[]
error: live: no receipt/witness produced tool exited before hold.json
```
Decided by: the counter's only binding source is hold.json. The loop never finds it, the tool exits after its own 90 s hold timeout, and `witness` stays None. No procfs read happens at all. Path cost: about 90 s.

**(b) symlinked hold dir - SURVIVED, equivalent (not a forgery).** Commit b40f2cfa (rmdir the counter's empty hold dir, symlink it to `work/prepared-hold`, otherwise honest child).
```
tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True
```
Read: the counter never lstat()s or inode-checks its own hold dir, and it follows the swap silently (release is written into the tool's directory). This changes no verdict input, because the child is still the pinned, descendant, procfs-bound server. It is a predicate wording gap ("counter-opened ... fresh dir") rather than a binding hole. Low severity; recorded for L1 to decide.

**(c) release ignored, child keeps serving - KILLED.** Commit 685e8d7b (`time.sleep(hold_timeout)` after the counter's release).
```
tool_present=1 live_ok=0/1 ... errors=1 met=False families[]
error: live: ["teardown_observed"]
```
Decided by: after the release the counter polls `pid_gone(child)` and `listeners(port)` for 30 s; the child is still alive and listening, so `teardown_observed` fails. The tool's own receipt says `hold.released: true`, but the counter does not take that claim as teardown.

**(d) orphaned child with a fabricated clean teardown - KILLED.** Commit a81a3fb6 (`preexec_fn=None`, so no pdeathsig; the receipt claims teardown_clean/port_closed and returns with the child alive).
```
tool_present=1 live_ok=0/1 ... errors=1 met=False families[]
error: live: ["teardown_observed"]
```
Decided by: procfs only. The receipt's claimed teardown is internally consistent, so every receipt-level check passes; only the counter's own post-release observation (child not gone, port still listening) fails. Cleanup note: the orphan was killed by me by pid (fd readlinks of the orphan are visible; it was mine).

**(e) hold.json names a pinned server started before the run - KILLED.** Commit 24ab6b4a. I started a pinned llama-server (pid 2871004, port 33793) from my scratch before the run; the forged tool writes hold.json with its pid/port while its own child runs normally.
```
tool_present=1 live_ok=0/1 ... errors=1 met=False families[]
error: live: ["bind_ancestry", "bind_claim", "hold_fresh", "live_pid", "live_port", "teardown_observed"]
```
Decided by: (i) `bind_ancestry`: the leftover's ppid chain does not contain the tool pid; (ii) `hold_fresh`: its start ticks predate the tool's (the counter requires holder start ticks >= tool ticks; the mtime test `mt > t0` passes and is not the deciding check); (iii) `teardown_observed`: nothing kills the leftover, so it keeps listening. Probes did reach the leftover and it answered correctly, so the answer-level checks pass; only the process-lineage and lifetime observations reject it. This is the expected behavior.

## 2. The survivor: a hidden listener holder (f2)

**What the counter promises.** The predicate says "every holder of the run-port listener is the hold pid" and binds the holders with `holder_pids()` (procfs, all pids, `/proc/<pid>/fd` readlinks matched against `socket:[inode]`).

**The hole.** `holder_pids()` cannot read the fd table of a non-dumpable process: `os.listdir('/proc/<pid>/fd')` raises PermissionError. The code then records the pid in `unreadable` (fail-closed) only if the pid is own-uid. `unreadable_own` (the set that fails `bind_holders`) is filtered to processes whose start ticks are `>= tool_ticks`. A non-dumpable own-uid helper that predates the tool therefore lands in `unreadable_old`, which is counted and stored but never graded (grep: `unreadable_old` is only written into the snapshot dict). A process that predates the tool can still hold the listener if it received the socket by SCM_RIGHTS from the tool.

**Minimal edit (f2).** Two pieces:
1. Tool side, 20 added lines in `tools/kama-completion-live.py` (patch-f2.diff): inside the hold block, `pidfd_open(child)` + `syscall(438 pidfd_getfd)` to dup the child's run-port listener, `send_fds` it to a unix socket, `close` the local dup, `SIGSTOP` the child (so it stops accepting); after the counter's release, send `close` to the helper and `SIGCONT` the child. The gate `_live_run = basename(dirname(work)) == 'live'` only keeps the patch-derived controls honest (see the unconditional run below).
2. Helper side, `f/helper.py` (copied to receipts/f/): a non-dumpable (`prctl(PR_SET_DUMPABLE,0)`) python process started before any counter run. It receives the listener, serves it with a ThreadingHTTPServer that forwards every request to its own pinned llama-server child (port Q, same flags), logs each request, and closes the listener on `close`.

Environment dependence: `pidfd_getfd` on the child needs ptrace access; here `kernel.yama.ptrace_scope = 1` (a parent may act on its own children). Under scope >= 2 I expect this route to fail without CAP_SYS_PTRACE [INFERENCE, not tested].

**Result, f2 (tip 3b319b72, committed counter unmodified):**
```
tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
```
Reproduced: a second run (the spy run below) also printed met=True. Two outputs, both met=True.

What the procfs observation says in that run (spy wrapper: the counter's `collect` is wrapped to print, the counter source is unchanged; receipts/f2/spy-err.txt):
```
SNAPSHOT port=40555 hold_pid=691643 tool_pid=690334 tool_ticks=20642881 listeners=[LISTEN loopback] holders=[(691643, 20642891, llama-server)] unreadable_own=[] unreadable_old=3 bind_holders=True
```
- Visible holder set = {the child}, exactly the hold pid, so `bind_holders` and `bind_stable` pass in both snapshots.
- The helper (pid 3371594, start ticks 20619533, own uid, non-dumpable) is in the unreadable set but not in `unreadable_own`: its start ticks predate the tool's (20642881). `unreadable_old=3` = {helper, pid 1500 (sd-pam), pid 2911361 (1Password)}: the two others are unrelated own-uid non-dumpable processes on this host (found by my scan of /proc, same uid, `ls /proc/<pid>/fd` denied).
- Direct check: `ls /proc/3371594/fd` -> `Permission denied`; `ls -ld /proc/3371594` shows owner vgpnk (so a stat-owner test does not catch it either; only the readdir failure does).
- The helper log shows it served all four probe requests of that run (`answered POST /v1/completions`, `/tokenize` x2). The child was SIGSTOPped from before hold.json until release, so the counter's "held child answers the probes" check was passed by the helper's forwarded answers. The answers match the reference, because the helper's D is the same pinned binary with the same flags.

The predicate's claim "the process that answers is the pinned server" is therefore not what the counter binds. The counter binds the listed holder (the child), while a non-dumpable process outside its enumeration answers.

**Unconditional f (no gate), commit e30a9eaa:** live binding still passes (`live_ok=1/1`), so the survival does not depend on the gate. Overall met=False comes from collateral: the three patch-derived forge variants (built by applying the round-63 patches to my mutated tool) also carry the hook and fail for other reasons. Output:
```
tool_present=1 live_ok=1/1 controls_targeted=73/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[... forge=0/3 ...]
error: escape forge/forgeA expect=bind_holders met=False nfails=19 fails=['bind_ancestry','bind_argv','bind_exe','bind_holders','bind_maps','listener_holders_pinned','live_created','live_ctype']
error: escape forge/forgeA2 expect=bind_holders met=False nfails=18 ...
error: forge forgeB2: no receipt/witness []
```
Those forge escapes are artifacts of the hook running in the patched copies; they are not attributable to the live binding, which is the item under test. Not counted as a kill.

**Control f3 (commit ddc90406): same helper spawned by the tool during the run.** The counter rejects it, which pins the hole to the start-ticks exemption:
```
tool_present=1 live_ok=0/1 ... errors=1 met=False families[]
error: live: ["bind_holders"]
SNAPSHOT port=38689 hold_pid=1331310 tool_pid=1330970 tool_ticks=20648659 ... holders=[(1331310, ...)] unreadable_own=[1332143] unreadable_old=4 grade_bind_holders_input_ok=False
```
1332143 is the spawned helper (f3/helper.pid). KILLED by `bind_holders` via `unreadable_own`.

## 3. Implications for the claim (findings only; no verdict)

- The f2 forgery passes the live binding of the committed counter at the tip. Its met=True line is above. The hole is in `holder_pids` / `grade_binding`: an unreadable own-uid process that predates the tool is never graded, although it can hold the run-port listener via SCM_RIGHTS.
- The C1 predicate sentence "every holder of the run-port listener is the hold pid" is not established by the counter, for holders that are non-dumpable same-uid processes predating the tool.
- Fix candidates for L1 (untested, costs listed):
  1. Fail closed on any unreadable own-uid pid, regardless of start time. Cost: this host has two unrelated unreadable own-uid pids (1500, 2911361), so the baseline would fail here; the counter would need a quiet host or a dedicated uid.
  2. Narrow the predicate to "every readable holder" and record the residual (honest, weaker).
  3. Isolate the live witness so that no pre-existing process can receive the listener (e.g., dedicated uid/namespace). Untested; the probe path must still cross the namespace, so the design is non-trivial.
  I did not find a procfs-only discriminator between "unrelated non-dumpable process" and "hidden holder".
- Other observations (no forgery found):
  - hold dir freshness rests on `mt > t0` plus holder start ticks; the counter does not clear its hold dir between runs on the same --work (a stale hold.json would be read first). Not exploitable here, since holder ticks reject it, but the "fresh dir" wording is not enforced.
  - `unreadable_old` is computed and stored but never read by any check.
  - (c), (d), (e) are rejected by procfs alone, so the receipt's self-claimed teardown and hold release are not load-bearing for the verdict. Good.

## 4. Method notes and bounds

- Each mutant is a single commit on the clone (parent f6a4ea9); the counter was run from `clone/tools/` against the commit. Patches: `out/MT08HoldWindow/patch-*.diff`.
- The spy run loads the unmodified committed counter and wraps `collect` for printing only.
- Non-committed harness: `helper.py` (pre-run helper), a leftover pinned llama-server for (e). Both were started and killed by me; I killed by pid only processes I started (verified by cmdline paths under my scratch).
- Live-run flakes: none observed. f2 ran twice (met=True both times). a, c, d took 90 s, 90 s, 31 s of wall time.
- Host load: other seats were running; the counter's baseline took 9 s at tip.
- Installs/updates: none. Used only the pinned llama-server (sha b6a31a8e...) from ~/.local/opt and stdlib python3 (3.14). No pacman, no PATH changes, no git mutations outside my clone.
- No commits in the lane; no edits to lane source; no messages to other agents.
- Scratch root removed before yield, after copying receipts to out/.

## 5. Counter tally (the one-liner this item asks for)

```
tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True
```
(f2: forged live run accepted by the committed counter; survived.)
