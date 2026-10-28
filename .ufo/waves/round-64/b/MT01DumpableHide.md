# MT01DumpableHide — C1 falsification: non-dumpable listener holders (round 64, wave b)

Seat: MT01DumpableHide (leaf, advisory). Claim C1 (operability, `live-completion-request-plane`).
Tip under test: f6a4ea9a8b5a876d685b08e7e582ec0723412a4a (freeze commit). Frozen counter sha256
b69c4b075f36b12fe275869da056fe6debe49db45bdf68c53d0eb4e8cbb12c84 (lane file == git blob at f6a4; verified).
Forged tools live only in my scratch clone (commits 6bd373d1, 808a1d43, 4769155d; lane untouched, no commit here).
Evidence: `.ufo/waves/round-64/b/out/MT01DumpableHide/` (runs/, code/, patches/).

## Verdict

- **The counter does NOT bind the answering process against an own-uid non-dumpable helper that the tool did
  not start.** A forged tool that hands the run-port listener (SCM_RIGHTS) to a pre-existing non-dumpable
  process, while the pinned real child stays the only *visible* holder, is accepted: `met=True`, 76/76, both
  with a full-answering helper (O3) and with a silent helper (O4).
- **The counter DOES reject a tool-started non-dumpable child** (T1 holds a dup of the real listener; T2 binds a
  fake listener). The decisive field is `unreadable_own`.
- **Decisive field for the survivors:** `unreadable_own` is `[]` because the gate is
  `start_ticks_of(p) >= tool_ticks`, so the old helper is excluded; the helper appears only in `unreadable_old`
  (a count), and `grade_binding` never reads `unreadable_old`. `holders` lists only the real child, which
  equals `hold_pid`, so `bind_holders` passes.
- **Stronger, procfs-free observation found:** K5 (below) stops the held pid, probes the port, and requires
  silence. It kills O3 (the helper answers while the real pid is stopped) and leaves the honest tool at 76/76.
  O4 survives K5 because its hidden holder never accepts; no procfs-only fix I tried closes that case without
  breaking the honest host.

## Genuine control (frozen counter, freeze tip)

    tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[...]   (exit 0)

Forged tool with its mode file absent (commit 6bd373d1) also gives `met=True` 76/76, so the forgery hook is inert
when unused.

## Mutant results (frozen counter, fresh --work per mode; run-final.sh)

| mutant | construction | verdict | decisive field |
|---|---|---|---|
| T1 | tool-started child: `prctl(PR_SET_DUMPABLE,0)`, holds a `pidfd_getfd` dup of the real listener; real child SIGSTOPped | **KILLED** | `unreadable_own=[4193624]` (own-uid, fd table EACCES, started after tool) -> `bind_holders` false; only failing check |
| T2 | real child killed; tool-started non-dumpable child binds the run port (fake listener) | **KILLED** | `holders=[]` and `unreadable_own=[hold_pid]`; 9 checks fail |
| O3 | pre-started non-dumpable helper (not tool's child) gets the dup via SCM_RIGHTS, serves and forwards to a real backend; real child SIGSTOPped | **SURVIVED** | `holders=[real child]`, `unreadable_own=[]`, `unreadable_old=4` (helper counted, never graded) |
| O4 | pre-started non-dumpable helper holds the dup and never accepts; real child answers normally | **SURVIVED** | same as O3; the helper never receives a request |

Counter one-liners (verbatim, families dict abbreviated where marked):

    T1  (final): tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 ... eval_selftest=0/3 errors=1 met=False families[]
        error: live: ["bind_holders"]
    O3  (final): tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    O4  (final): tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[...all 76/76 exact...]
    T2  (run-modes): tool_present=1 live_ok=0/1 ... errors=1 met=False families[]
        error: live: ["bind_ancestry","bind_argv","bind_claim","bind_env","bind_exe","bind_holders","bind_maps","hold_fresh","live_pid"]

Repeat / flake data for O3 (same forged commit, same counter; all outputs kept in runs/):

    O3 run #1 (before one-shot fix, bg job): live_ok=1/1 controls_targeted=72/76 ... forge=0/3 ... relabel=0/1 ... met=False
    O3 run #2 (driver, reused --work): live_ok=1/1 controls_targeted=69/76 ... met=False (7 fake controls: "tool exited before hold.json")
    O3 run #3 (fresh --work, O3b):    live_ok=1/1 controls_targeted=76/76 of 76 ... met=True
    O3 final (fresh --work):          met=True (above)

Both met=False O3 runs are harness artifacts, not counter behaviour (see "Harness artifacts"). The live binding
passed in all four O3 runs (`live_ok=1/1`), so the survival does not depend on the controls.

## The forgeries (clone commits; tool diff vs f6a4 in patches/forged-tool-hook.patch)

Common: the tip tool is unchanged except a gated hook after `listener_holders_pinned`. Mode comes from a
one-shot file in the scratch forge dir, so only the live run is forged and the counter's control runs are genuine.
The hook:

1. `_forge_dup_listener(pid, port)`: finds the socket inode from `_live._listen_inodes` in `/proc/<real>/fd`, then
   `pidfd_open` + `syscall(438 /* pidfd_getfd */)` (Yama ptrace_scope=1; the tool is the parent, so allowed).
2. Hands the dup to a non-dumpable helper over a unix socket (`socket.send_fds`). `helper.py` calls
   `prctl(PR_SET_DUMPABLE, 0)` then serves `FD <qport>` (forwards to a backend), `HOLD` (keeps the fd, never
   accepts), `DROP` (closes the listener).
3. T1/O3: `os.kill(real, SIGSTOP)` so the visible holder never accepts. The backend (second pinned llama-server,
   child of the tool, not on the run port) answers the forwarded probes. Cleanup sends SIGCONT, DROP and kills
   the backend.
4. Helper placement: T1 = `subprocess.Popen` by the tool (descendant). O3/O4 = started by the attacker before the
   counter (not a descendant; start_ticks < tool_ticks).

Minimal edit for O4 (smallest survivor; no SIGSTOP, no backend, no forwarder): after `holders = _proc_holders(port)`,
add a dup via pidfd_getfd, one `send_fds(b'HOLD', [fd])` to a pre-started helper that does `prctl(4,0)` and keeps
the fd, then `os.close(fd)`. About 15 added lines in the tool plus a ~20-line helper. The real child keeps answering
(`served-final-O4.log` absent: the helper served 0 requests).

Served evidence: `served-final-O3.log` = 4 requests (2 completions + 2 tokenize, the counter's probes), all
served by the helper pid. `served-final-T1.log` = 4 requests, all by the tool-started helper. The real child
served none of the probes in either case.

## Snapshot fields and what decides each mutant

Counter code (frozen, lines in `tools/round64-c1-counter.py` at f6a4): `holder_pids` skips a pid silently unless
`listdir(/proc/<pid>/fd)` raised PermissionError and `os.stat('/proc/<pid>').st_uid == me`; `collect` splits such pids
into `unreadable_own` (start_ticks >= tool_ticks) and `unreadable_old` (all); `grade_binding` reads `unreadable_own`
(in `bind_holders`) and never reads `unreadable_old`.

Direct probe (on a real helper pid, genuine counter's own `holder_pids`): old helper ∈ `unreadable` (`unreadable_old`
counts it); `start_ticks` < stand-in tool ticks; ∉ `unreadable_own`. So the helper is seen and then discarded
by the start-time gate.

## Procfs facts measured (this kernel, uid 1000, Python 3.14)

- prctl(PR_SET_DUMPABLE,0) child: `listdir(/proc/<pid>/fd)` = EACCES; `st_uid` stays 1000; `status` Uid = 1000
  (3 probes, incl. after 2 s). So the current `st_uid == me` proxy does catch prctl-hidden children.
- Execute-only ELF copy of python3 (chmod 0111): fd table EACCES, `st_uid` stays 1000.
- Host process `fusermount3` (setuid exec): `st_uid` = 0 while `status` Uid = 1000. So `st_uid` is not a reliable
  non-dumpable test; the correct proxy is `status` Uid plus the EACCES listing. A setuid-exec'd own-uid holder
  would evade the current gate; I did not build a forgery for that.
- Kernel threads, root daemons, `systemd`: fd tables unreadable with uid 0 (expected).

## Counter-side fixes tried (mutants of the counter; not committed to the lane)

K1 — status-Uid owner check and no start-time gate (`unreadable_own = all own-uid unreadable`):
- Honest tool REJECTED: `live: ["bind_holders"]`, `unreadable_own=[1500,1881,2857332,2911361]` (sd-pam, fusermount3,
  a `sudo -n /usr/bin/python3 .../MT07RefAgree/.../rootforge.py` process of another seat, 1Password-BrowserSupport).
  `met=False`. T1/O3/O4 also fail, but only through this host-wide set.
- Verdict: invalid fix (false negative on the genuine tool). The start-time gate is what keeps pre-existing host
  processes out of the verdict [INFERENCE from this host's process list]; it cannot be dropped as-is on a host with
  long-lived own-uid non-dumpable processes.

K5 — behavioural check added to `witness_run`: after the probes, SIGSTOP the claimed hold pid, probe `/health` with a
3 s timeout, record the status, SIGCONT. `score()` fails `bind_answers_while_held_stopped` when a status came back.
- NONE (honest): `met=True` 76/76 (`out-k5-NONE.txt`); all 76 controls still rejected.
- T1: `live: ["bind_answers_while_held_stopped","bind_holders"]` -> KILLED.
- O3: `live: ["bind_answers_while_held_stopped"]` -> KILLED (the one check; helper answered while real pid was held).
- O4: `met=True` 76/76 -> SURVIVED (silent hidden holder; the answer binding is intact, only the "every holder"
  clause of the predicate is unmet). Not decidable from unprivileged procfs (see below).
- Guard needed before adoption: the probe SIGSTOPs a pid the tool *claims* in hold.json. Gate that on
  `hold_pid` being a visible holder with the pinned exe (`bind_holders`/`bind_exe` precondition) so the counter never
  signals an arbitrary process. My mutant does not have the guard (not exercised by these forgeries).
- Cost: +3 s per live run. Changing the frozen instrument needs a numbered AMENDMENT (freeze.txt) before wave f.

## What procfs cannot see (for the L1)

A non-dumpable own-uid process that predates the run and holds an fd for the listener is invisible to every
readable procfs field except a count. `/proc/net/tcp` has no holder column, fd tables are unreadable without
ptrace rights (`pidfd_getfd`/`kcmp`/`/proc/<pid>/fd` all need ptrace access and fail for non-dumpable targets),
and `sock_diag` does not expose holders. So "every holder is the hold pid" is unverifiable by an unprivileged
counter for pre-existing non-dumpable helpers. Options: (a) run the counter with CAP_SYS_PTRACE/root so fd tables
are readable (then `holder_pids` is complete); (b) amend the predicate to "every visible holder" and add a
behavioural check (K5); (c) both.
[INFERENCE] A previous forged-tool run that left a double-forked non-dumpable helper would look exactly like O3 to
this counter. I did not test persistence.
[INFERENCE, untested] A holder can flip dumpable between `listdir` (readable) and `readlink(fd/N)` (EACCES),
so `holder_pids` drops it silently (no unreadable record). Narrow race; not built.

## Harness artifacts and reproducibility (reported, not hidden)

1. O3 run #1: my mode file was still set during the counter's control runs, so the replayed forge-A/B and relabel
   tools ran my hook and crashed (`forge=0/3`, `relabel=0/1`). Fixed by making the mode file one-shot.
2. O3 run #2: `--work work-O3` was reused from run #1, so the fake tools' hold dirs still held `release` files; those
   fakes were released before the counter could poll, producing 7 "tool exited before hold.json" failures
   (`met=False`, `live_ok=1/1`). Finding for the L1: the C1 counter does not refuse a reused `--work` (the C2 counter
   does), and this causes a false negative. Fresh-dir re-run O3b: `met=True` 76/76.
3. My ad hoc procfs probe used `$!` after `setsid`, which pointed at a process that had already exited, so that
   probe read the wrong PID (fixed by pgrep). The driver's logged helper PIDs did match the served logs (4125 for O3,
   4193624 for T1), so the driver's kill and served-count evidence refer to the right processes. My leftover
   helpers from the ad hoc probes were stopped by pgrep under my scratch path only.
4. `wrap.py` prints the graded raw snapshot (`SNAP` lines in `err-*.txt`); it only reads procfs and calls the
   counter's own functions.

## Host notes

- No installs or upgrades. Stdlib Python 3.14, util-linux `setsid`, `pgrep`, the pinned llama-server (`~/.local/opt/llama-b11755`,
  sha b6a31a8e...), and the cached stories260K model were already present. No pacman.
- Other seats' processes seen on the host (not touched): a `sudo -n` rootforge.py for MT07; several llama-servers on
  ports 45669, 1234 and 37323 (not mine). Their presence affects the K1 false negative only.
- Killed only processes whose cmdline pointed into my scratch path (leftover helpers from my own runs).

## Checks the main agent should run (not run by me)

- Reproduce with the frozen counter on the freeze tip with the forged commit: the O3/O4 commands are in
  `code/run-final.sh` (needs the clone at 4769155d, the pinned server, and the forge dir); no need to rerun for
  the verdict.
- Decide on the counter fix: K5 with the hold-pid guard is the candidate; K1 is rejected on the honest run.

## Files

- runs/: every counter output and err (SNAP) log for T1, T2, O3 (x3), O4, K1, K5 and the genuine finals; served-*.log
  and state-*.log (served request counts per helper pid; state read immediately after SIGSTOP is only indicative).
- code/: helper.py (forgery helper, prctl(4,0), SCM_RIGHTS), wrap.py (snapshot wrapper), run-*.sh (drivers),
  owner_flip.py / unreadable_scan.py / dump_probe.py / xonly-probe.py (procfs probes), genuine-counter.py (frozen copy, sha in sha256.txt).
- patches/: forged-tool-hook.patch (tip -> 4769155d), k5-counter-mutant.patch (K5 against the frozen counter),
  clone-commits.txt. K1 is not saved as a patch; the edit is described above (two lines: status-Uid in holder_pids,
  `unreadable_own = sorted(unreadable)`).

Scratch root /fast/scratch/hyaku/kama-r64/b/MT01DumpableHide removed after copying the receipts above.

    O3 (final, frozen counter, fresh --work): tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True
