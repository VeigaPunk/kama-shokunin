# E12KillSwitch — pdeathsig teardown proved by SIGKILLing the tool inside its hold window (w1)

Seat: advisory leaf (kama, axes operability + calibration). Item: run
`tools/kama-completion-live.py --hold-dir …`, then SIGKILL **the tool** (the parent, never
the child) while the hold window is open, and confirm from kernel state that the
`llama-server` child dies (pdeathsig) and that its port frees. This is a measured
teardown receipt, **not** a verdict on C1 or C2, and it changed no lane file.

## Environment / pinning

| fact | value |
|---|---|
| lane tip (`git rev-parse master`) | `65d7cad0fce90e34de37527cde22e97b63b118bf` |
| `tools/kama-completion-live.py` | sha256 `71ac4f2c45570a79cb1e80db91e85268609f28bf4dd421d628ffb9d10243771f`; `git cat-file -p master:…` identical; `git status --porcelain` clean |
| `tools/kama-llamacpp-live.py` (dependency) | sha256 `98d2e6bb48a90e60797df0d2bee895eac4a6cdd9859af2dc47b64bdb4a36fbe9`; identical at `master`; clean |
| model fixture | `~/.cache/kama-shokunin/models/stories260K.gguf`, 1 185 376 B, sha256 `270cba1b…bd256d` (= the tool's `DEFAULT_MODEL_SHA`) |
| server binary | `/home/vgpnk/.local/opt/llama-b11755/llama-server`, 17 864 B, sha256 `b6a31a8e…c804` (= the tool's `DEFAULT_SERVER_SHA`) |
| kernel / runtime | `Linux 7.2.11-arch1-1`; Python 3.14.8; git 2.56.0; `ss` iproute2-7.2.0; 32 CPUs |
| scratch | `/fast/scratch/hyaku/kama-r62/w/E12KillSwitch/` — created with `mkdir -p`, passed explicitly to every command (`--hold-dir`, `--work`); never an inherited `TMPDIR`, never `/tmp` |

Working tree carries two pre-existing modifications from other seats (`M corpus/SOURCES.md`,
`M tools/round62-c1-counter.py`). Neither is in the measured path: the two tools above are
byte-identical on disk and at `master`, and the model/server digests are re-derived by the
tool on every run. No pacman transaction was attempted (host-wide pause); no uv/npx/binary
install was needed — stock `python3 3.14.8`, `ss`, and the lane tools ran everything.

## Method (what was made observable)

Driver `out/E12KillSwitch/driver.py` (stdlib only, imports the lane tool's own primitives
`_listen_inodes` / `port_owned_by` / `http_get`):

1. Spawn `tools/kama-completion-live.py --work <fresh> --hold-dir <fresh> --hold-timeout 180
   --out <receipt.json> --nonce e12-killswitch-r62` with `start_new_session=True`, so the
   tool — and only the tool — is signallable by pid.
2. Accept `ready.json` **only** when it is fresh (mtime ≥ spawn) *and* the announced pid's
   `/proc/<pid>/stat` `ppid` equals the tool pid; then require
   `port_owned_by(child, port)` — the hold window is provably open.
3. Snapshot: `/proc/<pid>/stat` (state, ppid, pgrp, sid, field 52 `exit_code`), a `/proc`
   descendant BFS, child `exe`/`cmdline`, listener inodes, `ss -ltnp sport = :<port>`, a
   `bind(127.0.0.1:<port>)` probe (must fail pre-kill), a scan of
   `registry/endpoint-consumers.tsv` for the port, and (runs 9–10) one outside
   `GET /health` + `GET /v1/models`.
4. `os.kill(tool_pid, SIGKILL)`. **No signal is ever sent to the child.**
5. Poll `/proc/<child>/stat` every 0.5 ms for the first non-alive sample (state `Z`/`X`/gone)
   and read `exit_code`; poll listener inodes to emptiness; then re-probe `bind`, TCP
   connect, `ss`, and the hold dir.

Every run used a **fresh** hold dir (`hold-<label>-<driverpid>`) — see the invalidated run
below for why that is not incidental.

## Observed process tree (run9, verbatim)

```
pid=1208120 ppid=1208117 pgrp=1208120 sid=1208120 state=S comm=python3      <- the tool
pid=1208123 ppid=1208120 pgrp=1208120 sid=1208120 state=S comm=llama-server <- its only child
child_exe     = /home/vgpnk/.local/opt/llama-b11755/llama-server
child_cmdline = …/llama-server --model …/stories260K.gguf --alias kama-completion-probe
                --port 34203 --host 127.0.0.1 -c 512 -t 1
child_descendants = []
hold dir listing  = ['hold.json', 'ready.json']      (hold window open; the tool is in the loop)
GET /health       -> 200 {"status":"ok"}             (answering at kill time, not merely bound)
GET /v1/models    -> 200, data[].id = "kama-completion-probe"
ss -ltnp "sport = :34203"
  LISTEN 0  512  127.0.0.1:34203  0.0.0.0:*  users:(("llama-server",pid=1208123,fd=3))
listen_inodes = ['1434161059'] ; port_owned_by_child = True
bind(127.0.0.1:34203) = [False, 'OSError:Address already in use']   -> the port really is taken
registry/endpoint-consumers.tsv tokens for 34203 = []              -> not a registered consumer port
```

The tree is exactly two processes: the tool (session leader, because the driver isolates it)
and one `llama-server` child whose only parent is the tool. The server has no descendants,
so `PR_SET_PDEATHSIG` (which the tool requests in the child via `preexec_fn` before `exec`,
and which `fork(2)` would clear for any grandchild) is the only guard that must hold.

## After the SIGKILL

```
kill = {"signal": "SIGKILL", "sent_to": 1208120, "sent_to_child": false,
        "tool_returncode": -9, "tool_reaped_ms": 1}
child first non-alive sample (+1 ms):
  pid=1208123 ppid=1494 pgrp=1208120 sid=1208120 state=Z  exit_code=9  exit_signal=9  comm=llama-server
port gone at +3 ms:
  listen_inodes = [] ; ss -ltnp "sport = :34203" -> header only
  bind(127.0.0.1:34203) = [True, None] ; tcp connect -> ConnectionRefusedError: Connection refused
child_stat after = null (reaped) ; child_descendants = []
hold dir still ['hold.json', 'ready.json']  (a SIGKILLed run never reaches its unlink)
tool receipt written: NO ; tool stdout bytes: 0
```

Three independent readings agree: the child is gone (`exit_code` 9 = killed by SIGKILL,
`ppid` already reparented to systemd 1494, `Z` = dead), the port has no listener and is
immediately bindable/refusing, and **no tool code ran after the signal** — `SIGKILL` cannot
be caught, the tool left no receipt and no stdout byte, so the child's death cannot be the
tool's own teardown path. It is kernel-delivered pdeathsig.

## Cross-run tally (9 fully-bound receipts)

```
run    tool_pid  child_pid  port   pre: listen/owned/bind-blocked  exit_sig  death_ms  port_ms  post: listen/bind/connect
run1   926532    926665     34541  True/True/True        -         1         4        False/True/refused
run2   1052611   1052752    42851  True/True/True        -         1         3        False/True/refused
run3   1055087   1055294    34793  True/True/True        -         1         4        False/True/refused
run4   1057595   1057756    41469  True/True/True        -         1         3        False/True/refused
run5   1157473   1157477    32967  True/True/True        9         1         3        False/True/refused
run6   1157535   1157541    43849  True/True/True        9         2         4        False/True/refused
run7   1157869   1157937    40363  True/True/True        9         1         3        False/True/refused
run9   1208120   1208123    34203  True/True/True        9         1         3        False/True/refused  (+ /health 200 pre-kill)
run10  1212170   1212237    44795  True/True/True        9         1         3        False/True/refused  (+ /health 200 pre-kill)
```

`exit_sig` is `/proc/<pid>/stat` field 52 (`exit_code & 0x7f`); it is `9` wherever the
zombie was still resident when sampled (5/9). In runs 1–4 systemd reaped the zombie inside
the 0.5 ms poll gap, so only state `Z` (or absence) plus the port release was recorded —
the latency figure is unaffected. Every run's child is still absent and every run port still
bindable as of the final check (`receipts-tally.txt`), i.e. nothing was stranded across
eleven spawns.

## Mechanism control — the observation is sensitive (3 cases, no server, no port)

`out/E12KillSwitch/pdeathsig-control.json`: a scratch harness forks `sleep 300` and the
conductor SIGKILLs the harness.

| case | where `prctl(PR_SET_PDEATHSIG, SIGKILL)` is requested | child after harness SIGKILL |
|---|---|---|
| positive | in the child, before `exec` (the lane tool's `preexec_fn` pattern) | **dead at +1 ms** |
| negative | not requested | alive after 500 ms (survivor killed by the conductor, which spawned it) |
| parent_side | in the parent, before `fork(2)` — the naive placement | alive after 500 ms |

So the live-run observation is attributable to pdeathsig and not to "the environment reaps
children": the same harness, same signal, differing only in where the prctl lands, splits
1 dead / 2 alive. The `parent_side` case also documents the trap — `fork(2)` clears the
setting, so a prctl in the parent is a silent no-op, which is exactly why the tool's
child-side `preexec_fn` placement (and its post-prctl `getppid` check) is the load-bearing
line.

## Invalidated run and the witness-freshness hazard it exposes

Attempt 1 of run `run8` produced no receipt: the driver crashed serializing `bytes`
(`TypeError: Object of type bytes is not JSON serializable`) **after** the kill, so the
observation happened but left no file; that child (1175024 @ 44711) is gone and its port is
bindable. Attempt 2 then re-used the same `--hold-dir`, and its receipt
(`teardown-receipt-run8-INVALID-stale-ready.json`) bound the **previous attempt's**
`ready.json`:

```
ready read: {"pid": 1175024, "port": 44711, "schema": "kama-live-witness/v1",
             "written_utc": "2026-10-28T12:30:54.561Z"}   tool actually spawned: pid=1178573
```

That is the documented stale-witness hazard in the observer's direction: an observer that
starts polling at spawn time can read a leftover `ready.json` before the tool's own
`prepare_witness_dir` runs (the window is ≥ 5 ms — the driver's first poll; the tool removes
leftovers at its own start, so the window closes then). Consequences, precisely:

- It is **fail-closed for a consumer**: the stale document names a dead pid and a closed
  port, so an outside prober fails rather than passing. The real child of attempt 2
  (1178574 @ 45639, from `hold.json`) also died and freed its port.
- It is **not self-detecting**: `ready.json` carries `schema`/`port`/`pid`/`written_utc` and
  `hold.json` adds alias + both digests, but **neither carries the caller's `--nonce` or any
  run id**, so freshness must be bound out-of-band (mtime ≥ the observer's own spawn time,
  and `announced pid`'s `ppid == expected parent`). With that binding adopted, runs 9 and 10
  rejected no announcement (`rejected_announcements = []`) and bound only their own child.
  Recorded as an observation for the L1 to route; not a verdict on C1's counter, which
  re-derives its receipt from captured bytes.

Two driver defects were found and fixed by the controls themselves (kept as calibration
evidence, not hidden): the pdeathsig control initially issued the prctl in the parent and
returned a **false negative** (positive child survived), and the receipt serializer rejected
`bytes` bodies. Both are now covered by the positive/negative/parent-side triple above.

## Adjacent observation (not mine to remedy, not touched)

`pgrep -a llama-server` at the start and end of this work shows six servers this seat never
spawned and never signalled: one is another seat's live hold (`pid 1030667`, `ppid 1030490`
alive, port 35075), and **five are stranded** — `ppid 1494` (systemd), ages 6 280–23 973 s,
argv `/home/vgpnk/.local/opt/ollama-v0.40.11/lib/ollama/llama-server … --port 42317 / 37539 /
42665 / 38791 / 37323`, all loaded from round-61 scratch trees (`kama-r61/*/run-pd/…`) and
all still LISTENing. They are the same class the control's negative case reproduces: a
server whose spawner never requested a parent-death signal outlives its parent indefinitely.
Reported for routing; not killed here (not spawned by this seat).

## Limits

- One host, one kernel (`7.2.11-arch1-1`), one fixture pair (model + server digest pinned);
  the failure mode is Linux-specific `PR_SET_PDEATHSIG` semantics.
- The kill lands **inside the hold window** (after `/health` readiness and the first-answer
  ownership gate), not during model load and not mid-completion. The same kernel rule should
  hold there, but this seat did not measure it.
- pdeathsig is proved as a consequence, not read as an attribute: `/proc` exposes no
  "this pid holds a parent-death signal" field. The attribution chain is tool code path
  (`preexec_fn` → prctl in the child before `exec`) + `exit_code 9` with the tool never
  signalling the child + the three-case control.
- The tool's own receipt is deliberately absent in every run here (SIGKILL means no
  receipt), so the request-plane grading of C1 is unaffected and not exercised.

## Receipts (durable)

Under `.ufo/waves/round-62/w1/out/E12KillSwitch/`:

- `teardown-receipt-run1.json`, `-run2 … -run7`, `-run9`, `-run10` — 9 fully-bound per-run
  receipts (process tree, `/proc` stats, listener inodes, `ss`, bind probes, kill record,
  death sample, port release, hold listing)
- `teardown-receipt-run8-INVALID-stale-ready.json` — the invalidated stale-`ready.json`
  binding, kept verbatim
- `pdeathsig-control.json` — the 3-case mechanism control
- `receipts-tally.txt` — the cross-run table + post-hoc "child gone / port bindable" check
- `process-tree-run9.txt` — the run9 tree, `/health` + `/v1/models` bodies and both `ss`
  snapshots, verbatim
- `driver.py`, `control_pdeathsig.py` — the exact drivers that produced the above
- `hold-run1/`, `hold-run8/`, `hold-run9/`, `hold-run10/` — `hold.json` + `ready.json` as the
  killed runs left them (a SIGKILLed tool never reaches its `unlink`). `hold-run8/hold.json`
  is attempt 2's (`45639`/`1178574`); the stale `44711`/`1175024` document the driver had
  read was removed by the tool's own `prepare_witness_dir` at attempt 2's start, which is
  precisely the race described above.

Scratch `/fast/scratch/hyaku/kama-r62/w/E12KillSwitch/` was `rm -rf`'d after copying. The
lane checkout was read-only for this seat; the only lane files written are this report and
the receipts directory above. No git/jj mutation, no commit, no push.

## Tally

```
kills=11 (tool SIGKILLed inside its hold window; child never signalled)
child_died=11/11  child_death_ms=1-2  exit_signal=SIGKILL(9) sampled 5/11 (/proc field 52)
port_freed=11/11  port_release_ms=2-4  post: listen_inodes=[] bind=ok connect=refused
receipts=9 valid + 1 invalid (stale ready.json) + 1 receipt-less (driver serialization)
mechanism_control: positive=dead@1ms  negative=alive  parent-side-prctl=alive  (control is sensitive)
pre-kill the server was answering: /health 200, /v1/models data[].id=kama-completion-probe (runs 9,10)
run ports vs registry/endpoint-consumers.tsv: 0 tokens in 9/9 checks (unregistered loopback only)
stale-witness window observed >=5ms; ready.json/hold.json carry no nonce -> freshness must be bound by the observer
adjacent (untouched): 5 stranded ollama llama-server listeners from r61 scratch (ppid 1494), 1 sibling live hold @35075
```

Report: .ufo/waves/round-62/w1/E12KillSwitch.md
