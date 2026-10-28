# CR04OwnershipScope - round 64 wave b, C1 scope and "What met=True does not show"

Seat: CR04OwnershipScope (leaf, advisory; no subagents, no commits, no lane edits).
Axis: operability. Tip under test: `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a` (freeze commit).
Counter scored unmodified: `tools/round64-c1-counter.py` at f6a4 (scratch clone, `cmp`-identical to the lane file).
Host: Linux 7.2.11-arch1-1, Python 3.14.8, `/proc/sys/kernel/yama/ptrace_scope` = 1.
Pinned server: `/home/vgpnk/.local/opt/llama-b11755/llama-server` (sha256 `b6a31a8e…`, same bytes as `~/.local/bin/llama-server`).
Tools installed or upgraded: none. Pacman untouched.

## 1. Decision

**Narrower.** The r64 sentence ("the process that answers is the pinned llama-server") and the counter establish
something weaker. At two counter snapshots that bracket the probe requests, the only *visible* same-uid holder of the
run-port listener is a process whose on-disk executable hashes to the pinned digest, and the two probe answers equal a
reference server's answers. They do not establish any of the three conjuncts the item names:

| Conjunct | What the counter actually grades | Gap |
|---|---|---|
| holds the listener | holder set at two instants: raw_a before probes (`round64-c1-counter.py:898`), raw_b after (`:901`); only raw_a is graded (`:717-720`), raw_b only compared (`:721-722`) | a holder present only between the two snapshots is never seen (S1, S2) |
| answers correctly | probe answers equal a reference server's answers (`:697-698`, `:806-840`) | no observation of which process accepted or answered a probe (S1) |
| pinned | exe digest of the live inode at snapshot (`:344`, `:417-419`), self-reported argv (`:421-433`), env denylist (`:434-437`), path-hashed maps (`:439-463`) | not memory-level; argv and env are self-reported (S5-S8) |
| no socket handed to another process | not checked | only the holder set at two instants (S1, S2) |

So the sentence should be narrowed (section 5). A process that "holds AND answers AND is pinned with a socket handed to
no other process" is **not** what met=True shows.

## 2. Frozen counter at the tip (measured)

`python3 tools/round64-c1-counter.py --repo <clone> --tip f6a4ea9a8b5a876d685b08e7e582ec0723412a4a --work <scratch>`,
exit 0 (`out/CR04OwnershipScope/main.out`):

```
tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
```

## 3. Survivors and unmodelled vectors (evidence)

Scratch fixtures are in `out/CR04OwnershipScope/` (`expA.py`, `expB.py`, `expC.py`, `expE2.py`, `forged_e.py`,
`driveE.py`, `c1.py` = copy of the counter, `experiments.txt` = all outputs).

**S1 - composed forger: window takeover, hold pid stopped, tool answers; counter's own scorer says met=True.**
`driveE.py` scores a genuine tip-tool run and a forged run through the counter's `witness_run` and `score_run`
(`:856-939`, `:1525-1534`), the same path `main()` uses for its live leg.

```
GENUINE met=True fails=[] teardown={'gone': True, 'port_closed': True}
FORGED met=True fails=[]
FORGED probe_text=['. Every', 's. She likes']
FORGED hold_pid=2923002 receipt_child=2923002 teardown={'gone': True, 'port_closed': True}
```
Final forger variant: `FORGED met=True fails=[]` in 4 of 4 consecutive runs (`forged-log-run{1,2,3}.txt`, `driveE` output above).
Mechanism, each step demonstrated in the forger log (`forged-log-driveE.txt`):
1. The forger starts a genuine llama-server on run port P (the hold pid) and a second genuine one on P2; health checked.
2. It takes a pidfd on the hold pid (`pidfd_open`, the forger is its ancestor) and SIGSTOPs the hold pid, so it never accepts.
3. It writes `hold.json` naming the hold pid; the counter's raw_a (`:898`) sees only the hold pid.
4. Probes queue on the listener (`/proc/net/tcp` rx_queue = 1 in the log); the probe comes after raw_a, so the window is open after the snapshot.
5. It `pidfd_getfd`s the listener into itself, answers the four probe requests (two probes x completion+tokenize) by forwarding to P2, and closes its copy before the fourth answer leaves.
6. It SIGCONTs the hold pid; raw_b (`:901`) sees only the hold pid; the counter releases and observes teardown.
Observed: hold pid in state `T` at window close (`forged-log-driveE.txt`); the hold pid's server log shows no processed task
(`hold-pid-server.log`); P2 processed two (`second-genuine-server.log`); the four requests were served by the forger's pid.
Prerequisites on this host: `pidfd_getfd` from an ancestor is permitted (`ptrace_scope=1`, demonstrated in expC).
Limits, stated plainly: the forger carries a genuine receipt template copied from an earlier genuine run (`genuine-receipt-template.json`);
the composed run is not the lane tip tool, so `main()` was not run on it (forge patches need the tip tool text, so
`main()` would fail its family table for an unrelated reason); the 76 controls were not evaluated on it.
Disclosure: two earlier forger variants (no settle time after SIGCONT) printed `bind_stable` (raw_b had no listener row).
I did not isolate that; it fails closed and does not bear on the bypass. The final variant is the one reported.

**S2 - transient holder, mechanism only (expC).** The tool, an ancestor of the hold pid, takes the listener with `pidfd_getfd`,
the counter's mid-window snapshot shows it, and the bracketing snapshots do not:

```
raw_a (before window): holders=[child]
pidfd_getfd ok: local fd=5
raw_mid (inside window): holders=[tool, child]
tool got: ping ; client got: answered-by-tool
raw_b (after window): holders=[child]
bind_holders on raw_a: True  raw_b: True  raw_a==raw_b holder sig: True
```

**S3 - pre-tool non-dumpable holder is recorded but not graded (expB).** `holder_pids` skips a holder whose fd table it cannot read
and records it in `unreadable_own` only if it started after the tool (`:270-276`, `:382-384`); `collect` also records
`unreadable_old` (`:385`), which no check reads (grep: `:385` is its only occurrence). Output:

```
(i) holders= [hold pid]   B(nondump, pre-tool) holds the same listener
    unreadable_own= []  unreadable_old= 3
    grade_binding bind_holders= True   (requires holders=={hold pid} and not unreadable_own; :412-416)
```

**S4 - dumpability, post-tool (fails closed).** With `PR_SET_DUMPABLE=0` on an extra listener holder (expA), `holder_pids`
omits it from the holder set (`holder_pids=[hold]`, `B_visible=False`) and lists it as an unreadable own-uid pid
(`unreadable_own=[..., B]`). `collect` keeps such a pid in `unreadable_own` when it started after the tool (`:382-384`), and
`bind_holders` then fails (`:415`). This closes the post-tool case only; S3 is the pre-tool case.

**S5 - argv is self-reported (expE2).** A process launched with `--port 1 --model /tmp/decoy.gguf` rewrites its argv area through
`/proc/self/mem` and `/proc/<pid>/cmdline` then reads as the pinned command line:

```
cmdline after self-rewrite: ['/home/vgpnk/.local/opt/llama-b11755/llama-server', '--port', '51333', '--model', '/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf', '--alias', 'kama-completion-probe']
```
`bind_argv` reads `cmdline` (`:348-350`, `:421-433`); the only independent anchor is the exe digest.

**S6 - environment is a denylist on the exec-time block.** `/proc/<pid>/environ` is read once (`:353-359`); `bind_env` rejects only
`LD_*` and `GLIBC_TUNABLES` (`:434-437`). The pinned library reads `LLAMA_ARG_PORT`, `LLAMA_ARG_HOST`, `LLAMA_ARG_MODEL`
(strings of `libllama-common.so.0.7.0`), so any other `LLAMA_ARG_*` key passes; argv takes precedence on flags it sets, so the effect
is limited to flags not on argv [INFERENCE on the effect; the key-passing is read from the code].

**S7 - mapped files are hashed by path, anonymous and system mappings are unhashed.** `read_maps` hashes the path at snapshot time
(`:330-334`), not the mapped inode via `/proc/<pid>/map_files`; a rename-over shows `(deleted)` and fails (`:328`, `:445-446`).
`maps_ok` skips anonymous mappings (`:449-450`) and any file under `/usr/lib/`, `/usr/lib64/`, `/lib/`, `/lib64/` (`:140`, `:451-452`). A path-vs-inode
swap inside one read is not exercised [INFERENCE, not run].

**S8 - same-uid ptrace and in-memory code.** The exe digest reads the on-disk file (`:344`); no memory of the running text is hashed,
and the counter never reads `/proc/<pid>/status` (no `TracerPid` read in the file). pidfd/ptrace by an ancestor succeeded under
`ptrace_scope=1` (expC), so a patched in-memory server is not excluded by any check [INFERENCE: patching not run].

**S9 - hold.json freshness is a lower bound.** `hold_fresh` needs `mtime > t0` only (`:470-471`); a tool may set any future mtime.
The stale-hold controls are rejected by holder start times (`:472-473`), not by freshness.

**S10 - other-uid holders are skipped silently** (`:270-276`: a PermissionError on another uid's fd table is not recorded).
Requires another uid's cooperation; not run [INFERENCE, low].

## 4. The controls do not reach these vectors

- The 20 `bind` controls (`:1363-1413`) edit one stored genuine snapshot: an extra holder that is always present (`:1374-1377`),
  argv flags (`:1382-1388`), `LD_PRELOAD`/`GLIBC_TUNABLES` keys (`:1389-1393`), maps (`:1396-1403`). None adds a holder present only
  between `raw_a` and `raw_b`, none adds a non-dumpable or pre-tool holder, none rewrites argv to a pinned-looking value, none adds
  an `LLAMA_ARG_*` key or an anonymous/system mapping.
- The live forgeries (`:1033-1135`: detach, proxy, canned, stalehold x2, preload, pathcopy) and the round-63 patches (`forge` x3,
  `:1163-1184`) keep the forged holder visible at the snapshots. Canned and proxy fail on holder identity because the tool, not the hold pid,
  holds the listener; the composed forger in S1 is not among the declared families.
- Net: met=True is a statement about holders that are visible and persistent across both snapshots, plus answer agreement.

## 5. Draft `What met=True does not show` (round 64) - for the SCORECARD

- The counter samples holders at two instants, before and after the probes (`tools/round64-c1-counter.py:898-902`, graded at `:717-722`), so a same-uid process that holds the run-port listener only in between is never seen: a forger that `pidfd_getfd`s the listener, SIGSTOPs the pinned hold pid, and answers both probes itself meets the counter's own live scorer (`:1525-1534`) in 4 of 4 runs (`.ufo/waves/round-64/b/out/CR04OwnershipScope/`).
- Nothing observes which process accepts a probe connection, so the probe answers are compared only with a reference server's answers (`:697-698`, `:806-840`), and a forwarder in front of a second pinned server passes, with the hold pid logging no processed task.
- The "pinned" check is a digest of the on-disk executable (`:344`, `:417-419`), not of the code the process runs, and the counter never reads `TracerPid` from `/proc/<pid>/status`, so in-memory patching by a same-uid ptracer is not graded (`ptrace_scope=1` permits it for an ancestor on this host).
- A non-dumpable same-uid holder that started before the tool is counted in `unreadable_old` (`:385`) and never graded, so `bind_holders` (`:412-416`) passes with it present (expB).
- The argv leg reads `/proc/<pid>/cmdline` (`:348-350`), which the process rewrites itself through `/proc/self/mem`, so `bind_argv` (`:421-433`) adds nothing beyond the exe digest (expE2).
- The environment leg is a two-prefix denylist on the exec-time block (`:353-359`, `:434-437`), not the "initial environment ... pinned set" the predicate names, so an initial `LLAMA_ARG_*` key passes.
- Mapped files are hashed by path at snapshot time (`:330-334`), not by inode, and anonymous mappings and anything under `/usr/lib/`, `/usr/lib64/`, `/lib/` or `/lib64/` are accepted unhashed (`:140`, `:447-452`).
- `hold.json` freshness is a lower bound only (`:470-471`), so a tool may set any future mtime.
- The 76 controls do not reach these vectors: the 20 `bind` controls edit one stored snapshot (`:1363-1413`) and the live forgeries keep the forged holder visible for the whole hold window (`:1033-1135`).
- The receipt-level checks re-derive from captured bytes the tool supplies (`:489-490`), so a tool may carry bytes from an earlier genuine run, and only the live leg (`:677-734`) ties the answers to this run.

What it does show (for balance): at the two snapshots, the run-port listener is loopback and held only by the counter's hold pid,
whose on-disk executable is the pinned digest (`:410-419`); the two probes agree with a reference pinned server (`:697-698`);
and teardown (holder gone, port closed) is observed by the counter after its own release (`:915-928`).

## 6. Proposed predicate sentence (narrower; NOT applied - needs a numbered amendment before wave f)

> C1-r64 (narrowed): at the tip, the byte-pinned tool runs one counter-opened hold-mode lifecycle on the pinned fixture;
> at two counter snapshots bracketing two probe requests, the only visible same-uid holder of the run-port listener is a
> process whose on-disk executable hashes to the pinned llama-server digest, with pinned-set argv and a no-LD denylist
> environment, and the two probe answers equal a reference pinned server's answers. It does not show that this process
> accepted or answered the probes, that no socket was handed to another process between the snapshots, or that the
> executable's memory is unmodified.

The same wording belongs in `freeze.txt` (C1 predicate) and the docstring (`round64-c1-counter.py:6-25`). Both are frozen; the
change is the L1's to make by amendment. I did not edit either.

## 7. Closure candidates for the L1 (not built here, not tested)

- Owner of the accepted socket: during a keep-alive probe, the server-side ESTABLISHED row on the run port (`/proc/net/tcp` state `01`) maps to an inode; `holder_pids` of that inode must equal `{hold pid}`. S1 would fail (the forger owns the accepted socket). Untested.
- Grade `unreadable_old` like `unreadable_own`, and reject any non-dumpable holder regardless of start time (S3).
- Read `TracerPid` of the hold pid and of the tool; require 0 (S8).
- Hash the mapped inode via `/proc/<pid>/map_files/<range>`; flag anonymous executable mappings (S7).
- Replace the environment denylist with an allowlist, or reject `LLAMA_ARG_*` (S6).
- Require `hold.json` mtime at or before the counter's read time (S9).

## 8. Receipts and cleanup

Copied to `.ufo/waves/round-64/b/out/CR04OwnershipScope/`: `experiments.txt`, `main.out`, `main.err`, the scripts, `forged-binding.json`,
`forged-log-driveE.txt`, `forged-log-run{1,2,3}.txt`, `hold-pid-server.log`, `second-genuine-server.log`, `genuine-receipt-template.json`.
Scratch root `/fast/scratch/hyaku/kama-r64/b/CR04OwnershipScope/` removed before yield. One leftover fixture process of mine
(a stopped `expC` child, pid 1400114, cwd in my scratch) was killed; no other process was touched.

Counter output, one line, at f6a4 (frozen counter, exit 0):
`tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True`
Composed forger (scored by the same `score_run`): `FORGED met=True fails=[]`.
