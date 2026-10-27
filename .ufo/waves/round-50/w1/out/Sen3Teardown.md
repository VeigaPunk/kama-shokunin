Verdict: the built chain closes all 18 requested kill variants — every signal on the invoker, the replay, the live tool and the server during the hold, and on the invoker and the replay during the initial download, leaves no llama-server and the port refuses within 0.5 s — and leaves two measured limits, from two extra probes of where the chain is rooted: killing the process that started the *invoker* (the counter's own position) leaks the whole tree for the witness timeout (119.9–120.0 s), and a kill of the invoker within the first ~40–50 ms after the replay forks leaks an orphan replay that reaches a ready, listening server (2.46 s measured).

# Sen3Teardown — round 50 teardown kill matrix (kama lane, seat leaf)

Build under test: lane clone of `/home/vgpnk/Projects/shokunin/kama-shokunin` checked out at
`97c864bead3ee4a2f629574e77263d33834ec98a` (`git clone --shared`, clone only; the lane was not
touched). Tools under test and their digests (`tool-digests.txt`):

```
d5c58972c0fd8f818b8dd2bd81f6cbc3a87c7f23b65805a804bf09b579a5a239  tools/kama-live-replay.py
61e777b743aedb55c9532c4892d14a6cf0600f9f6f260595d635ec50ff708507  tools/kama-llamacpp-live.py
97c864bead3ee4a2f629574e77263d33834ec98a  (HEAD of the clone)
```

Every variant is a **fresh witnessed replay** of `.ufo/waves/round-48/c2/live/receipt-2.json`,
started exactly as the frozen C1 counter starts it (`round50-replay-bind-audit.py:396-404`):
`python3 -I -c INVOKER  python3 -I <tree>/tools/kama-live-replay.py --receipt R --work W --out J
--witness-dir D`, environment `PASS_ENV` + proxies, `start_new_session=True` on the invoker.
Tree under test: invoker → replay → live tool → llama-server. `t0` is the instant the signal is
sent; the clock stops when no snapshotted process (pid + `/proc/<pid>/stat` start time) is alive,
the port has no LISTEN socket and refuses `connect(2)`, and no `llama-server` whose argv names the
run's paths exists. Cap 200 s. Driver: `kill_matrix.py` (results: `summary.json`,
`results/<tag>/result.json`).

Command actually run (scratch `/fast/scratch/hyaku/kama-r50/Sen3Teardown`, now removed):

```
python3 out/Sen3Teardown/kill_matrix.py --tree $S/lane \
  --receipt $S/lane/.ufo/waves/round-48/c2/live/receipt-2.json \
  --runs $S/runs --out $S/summary.json --parallel 5
```

## Control: the frozen counter's own leg at the same commit

```
python3 tools/round50-replay-bind-audit.py --repo $S/lane --tip 97c864bead3ee4a2f629574e77263d33834ec98a \
  --scratch $S/c1b --out c1-control-receipt.json          # exit 0
bind=1 teardown=1 newrow=1 bound=3/3 met=True
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.20 s alive [] port refuses ok
detail: bind b1..b3: exe+listen+tree+env+mapped ok, child_pid joined, nonce round-tripped
```

Its leg is variant `hold-invoker-KILL`; the counter kills one pid (`os.kill(p.pid, SIGKILL)`,
`round50-replay-bind-audit.py:508`) and waits `KILL_WAIT = 30 s` (`:112`). My independent
measurement of that same variant: tree and port gone in **0.255 s**, no leftovers
(`results/hold-invoker-KILL/result.json`).

## Matrix (20 variants, one fresh replay each)

| variant | phase | target | signal | t tree gone (s) | t port free (s) | t no llama-server (s) | leftovers | within 30 s |
|---|---|---|---|---|---|---|---|---|
| `hold-invoker-INT` | hold | invoker | SIGINT | 0.477 | 0.477 | 0.229 | 0 | True |
| `hold-invoker-TERM` | hold | invoker | SIGTERM | 0.241 | 0.241 | 0.0 | 0 | True |
| `hold-invoker-KILL` | hold | invoker | SIGKILL | 0.255 | 0.255 | 0.0 | 0 | True |
| `hold-replay-INT` | hold | replay | SIGINT | 0.306 | 0.306 | 0.063 | 0 | True |
| `hold-replay-TERM` | hold | replay | SIGTERM | 0.219 | 0.219 | 0.0 | 0 | True |
| `hold-replay-KILL` | hold | replay | SIGKILL | 0.045 | 0.045 | 0.0 | 0 | True |
| `hold-live-INT` | hold | live | SIGINT | 0.046 | 0.046 | 0.0 | 0 | True |
| `hold-live-TERM` | hold | live | SIGTERM | 0.087 | 0.087 | 0.0 | 0 | True |
| `hold-live-KILL` | hold | live | SIGKILL | 0.149 | 0.149 | 0.0 | 0 | True |
| `hold-server-INT` | hold | server | SIGINT | 0.098 | 0.0 | 0.0 | 0 | True |
| `hold-server-TERM` | hold | server | SIGTERM | 0.087 | 0.043 | 0.0 | 0 | True |
| `hold-server-KILL` | hold | server | SIGKILL | 0.089 | 0.044 | 0.0 | 0 | True |
| `dl-invoker-INT` | download | invoker | SIGINT | 0.309 | 0.0 | 0.0 | 0 | True |
| `dl-invoker-TERM` | download | invoker | SIGTERM | 0.086 | 0.0 | 0.0 | 0 | True |
| `dl-invoker-KILL` | download | invoker | SIGKILL | 0.081 | 0.0 | 0.0 | 0 | True |
| `dl-replay-INT` | download | replay | SIGINT | 0.044 | 0.0 | 0.0 | 0 | True |
| `dl-replay-TERM` | download | replay | SIGTERM | 0.111 | 0.0 | 0.0 | 0 | True |
| `dl-replay-KILL` | download | replay | SIGKILL | 0.105 | 0.0 | 0.0 | 0 | True |
| `hold-parent-KILL` | hold | parent | SIGKILL | **120.007** | **120.007** | 119.923 | 0 | **False** |
| `hold-parent-TERM` | hold | parent | SIGTERM | **119.983** | **119.936** | 119.936 | 0 | **False** |

Download-phase rows: kill sent when a `*.part` file existed under `<work>/download`
(`phase_attained.part.name = llama-b11909-bin-ubuntu-x64.tar.gz.part`, 0 bytes at kill);
`live_child_present false`, `server_present false` in every one of them — so the (c) live-tool and
(d) server targets do not exist during the initial download and those four variants are
structurally absent, not untested. Every variant's result records `left_llama_servers []`; after the batches
`pgrep -af <scratch>` = 0, and the only `llama-server` left on the host belongs to another seat
(`Rev1Base`, port 45999), not to these runs.

### What closed each family (mechanism, file:line)

- **(a) invoker, all three signals** — replay's own `PR_SET_PDEATHSIG = SIGTERM` arms the
  invoker→replay edge (`tools/kama-live-replay.py:100-111`, called at `:587`); the kernel signals
  the replay regardless of the invoker's death signal, the replay dies, the live tool gets SIGTERM
  through `_child_pdeathsig` (`:314-318`, hooked at `:332`) and its `_term_handler`
  (`kama-llamacpp-live.py:1862-1866`) raises `Terminated`, so `teardown()` (`:1117`) runs:
  rerun receipts of `hold-invoker-KILL`/`-TERM` read
  `setup_error terminated:signal 15`, `teardown.returncode 0`, `port_refuses true`,
  `term_wait_ms 3`.
- **(b) replay, SIGTERM/SIGKILL** — same edge, same receipts, 0.045–0.219 s.
  **SIGINT is closed by a different path**: CPython's `subprocess.run` kills its child on *any*
  exception including `KeyboardInterrupt` (`/usr/lib/python3.14/subprocess.py:573`), so the replay
  SIGKILLs the live tool; the live tool's own `_preexec_pdeathsig` (`kama-llamacpp-live.py:661-673`)
  then SIGKILLs the server. Outcome identical (0.306 s, no leftovers) but **ungraceful**: no rerun
  receipt exists and `ready.json` is left in the witness dir (`summary-trace.json`, 5 ms trace:
  all three alive to t≈0.18 s, all gone at t≈0.23 s). The residue is harmless — the tool removes a
  previous run's `ready.json`/`release` before starting a server
  (`kama-llamacpp-live.py:59`, `:299-304`).
- **(c) live tool** — server pdeathsig SIGKILL, 0.046–0.149 s. SIGKILL of the live tool also leaves
  `ready.json`; the replay then refuses with `no-rerun-receipt:exit=-9` (exit 2), i.e. a data
  outcome, not a process leak.
- **(d) server** — port free in 0.0–0.044 s; the live tool unwinds through `verify_live` to a
  `setup-error` receipt whose `teardown.port_refuses` is still true.
- **download phase** — invoker→replay edge only; all six ≤0.309 s. A `*.part` file is left in the
  work dir (scratch only; the replay's own `fetch` unlinks it on an exception it handles, not on
  SIGKILL).

## Limits of the claim (measured)

### L1 (largest) — the chain is rooted at the invoker; the counter's own death leaks the tree

`hold-parent-KILL` / `hold-parent-TERM` insert one more level (driver → **wrapper → invoker** →
replay → live → server), the wrapper standing exactly where the counter stands
(`round50-replay-bind-audit.py:396-404` starts the invoker and waits). Killing the wrapper —
i.e. killing *the process that started the invoker*, the round-49 R2 action one level up — leaves
replay, live tool and server running for **119.9–120.0 s**, with the port **accepting for the whole
window**, and the orphaned tree then runs to completion: `results/hold-parent-KILL/out.json`
records `{"match": true, "mismatches": [], "live_exit": 0}` — a full matching replay 120 s after the
parent died. Root cause: the invoker string (`round50-replay-bind-audit.py:114-116`) arms no
parent-death signal on itself, and nothing in the lane arms one on the invoker; the built
`set_own_pdeathsig`/`preexec_fn` chain starts *at* the invoker. The bound is the live tool's
witness timeout (`kama-live-replay.py:554` default 120 s; accepted up to 3600 s, `:586`), not the
30 s contract.

So the C1 sentence "killing whatever started a replay takes replay, live tool and server down" is
true when "whatever started" is the invoker the counter starts, and false one level up. The
counter's teardown leg cannot see this: it kills only `p.pid` of the invoker after `ready.json`.

Smallest remediation (not applied — the counter is frozen): arm the signal on the invoker at the
fork the counter already does,
`subprocess.Popen(argv, …, start_new_session=True, preexec_fn=lambda: libc.prctl(1, SIGTERM, 0, 0, 0))`
in `round50-replay-bind-audit.py:404`; that makes the counter→invoker edge behave like every edge
below it. Alternative that needs no counter edit: make the lane's replay refuse to start when its
parent is not the pid the invoker passes it (`--parent-pid`), but the invoker is counter code too.

### L2 — the pdeathsig on the replay is armed ~40–50 ms after fork

`set_own_pdeathsig()` runs in `main()` *after* interpreter start-up and `argparse`
(`tools/kama-live-replay.py:587`), so a kill of the invoker before that call cannot reach the
replay, and the replay's own belt-and-braces check is blind to it: it samples `parent = os.getppid()`
*inside* the call (`:105-111`), so after reparenting `parent` is already the new parent and the
`os.getppid() != parent` test passes.

Measured with `startup_window.py` (invoker SIGKILLed N ms after the replay child is first observed
in `/proc/<invoker>/task/<invoker>/children`; survivor = any process naming the run's path 0.5 s
later). `/proc/<pid>/stat` gives the child age at kill in 10 ms clock ticks:

```
startup-sweep.json   (delay after first sight, 0.2 ms poll):
   leak  : delay 0,0,0,3,6,10,15,20,30 ms  -> measured child age 0,0,0,0,10,10,10,20,30 ms (7/7 up to 30)
   no leak: delay 45,60,100 ms             -> measured child age 50,60,100 ms
startup-bracket.json (10 ms band):
   leak  : delay 30,34,38,40 ms            -> measured child age 30,40,40,40 ms
   no leak: delay 42,44,46,50,55,60 ms     -> measured child age 40,50,50,50,50,60 ms
```

The survivor is a live replay 0.5 s after the invoker died in every leaking trial, and every
trial's leftovers were removed by the probe (`remaining_after_cleanup []`). The arm point is
between the delay-40 ms and delay-42 ms trials, i.e. ~40–50 ms of child age (the 10 ms tick makes
the age column read 40 ms for both).

Impact demonstrated by letting one orphan run (`orphan_serves.py`, `orphan_serves.json`): invoker
SIGKILLed at child age 0 ms → the orphan replay **reached `ready.json` in 2.46 s**, its server
listened (`port_accepts true`) and its chain ended outside the counter:
`server ← live ← replay(ppid 1494 = systemd user manager) ← init`. Killing that orphan replay took
the rest of the tree down in **0.02 s** with the port refusing — the chain *below* the replay is
intact; only its arming is late.

Smallest remediation: set the signal in the fork (the counter's `Popen(..., preexec_fn=…)` for the
replay, same shape as `kama-llamacpp-live.py:661-673` for the server), or have the replay take the
starter's pid and refuse unless `os.getppid()` equals it; moving `set_own_pdeathsig()` to the first
statement of `main()` narrows the window to interpreter start-up only (measured today's arm point:
between 40 and 50 ms of child age) and does not close it.

## Notes / non-findings

- These two limits are *not* counter defects: `teardown_leg` (`round50-replay-bind-audit.py:497-530`)
  waits for `ready.json` and SIGKILLs the invoker, so it exercises neither L1 nor L2, and its leg
  passes (control above). They bound the claim sentence, not the measured met=True.
- No ungraceful-kill variant produced a *process* leftover; the only residues are files in scratch
  (`ready.json` after a hard kill of replay/live, `*.part` after a download-phase kill).
- `hold-live-INT` and `hold-server-*` produce `outcome pass->setup-error` mismatches in the replay's
  own `out.json`; that is the expected consequence of interrupting the live child, not a teardown
  failure (no process, no port).
- Nothing was started outside my scratch: every llama-server ran on a loopback port the tool picked
  and was torn down; final `pgrep -c -f llama-server` = 0.

## Tooling

No installs or upgrades were needed (python3 3.14.8 stdlib + the lane's tools only; `pacman`
untouched).

## Artifacts (all under `.ufo/waves/round-50/w1/out/Sen3Teardown/`)

`summary.json` (20 variants), `summary-trace.json` (5 ms traces of the replay/live/invoker kill
variants), `results/<tag>/result.json` (+ `out.json` where one was written),
`startup-sweep.json`, `startup-bracket.json`, `orphan_serves.json`, `c1-control.out`,
`c1-control-receipt.json`, `tool-digests.txt`, `micro-subprocess-run-sigint.log`, and the three
drivers `kill_matrix.py`, `startup_window.py`, `orphan_serves.py`.
