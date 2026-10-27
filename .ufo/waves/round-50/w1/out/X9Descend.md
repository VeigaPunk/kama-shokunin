# X9Descend — descendant-walk edges (round 50, kama, C1 operability)

**Verdict: operability holds on the measured tree — the frozen C1 descendant walk (`descendants()` 3-level BFS,
`replay_pid()` singleton rule, `descends_from()` ppid chain) is correct for the lane's fixed invoker and the real
replay tree, and the teardown snapshot includes the live tool (grandchild) and the llama-server (great-grandchild)
while excluding the counter and its own unrelated children; 20/20 adversarial shapes matched prediction, and the six
shapes that break its assumptions are limits — fail-closed for invoker-child multiplicity, depth, and a *detached
server*, but open-side (a survivor while the check reports `ok`) for a detached *extra* descendant or one forked
after the snapshot — all reachable only by changing the lane tools, never by the tree the tools build at 97c864be.**

## 1. Baseline: the frozen counter, instrumented copy, at the build tip

The counter was imported from a byte-identical scratch copy (the lane file was never imported, so no
`__pycache__` was written into the lane) and every `descendants()` / `replay_pid()` / `start_replay()` call was
recorded by wrappers that call the originals and return their values unchanged:

```
$ sha256sum $S/counter_copy.py                                  # $S=/fast/scratch/hyaku/kama-r50/X9Descend
ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89   # == tools/round50-replay-bind-audit.py
$ git clone --shared .../kama-shokunin $S/lane
$ TMPDIR=$S python3 $S/probe_instrumented.py $S $S/lane 97c864bead3ee4a2f629574e77263d33834ec98a   # exit 0
tip=97c864bead3ee4a2f629574e77263d33834ec98a
bind=1 teardown=1 newrow=1 bound=3/3 met=True
detail: bind b1: pid 3943953 port 38381 exe+listen+tree+env+mapped ok, child_pid joined, ...
detail: bind b2: pid 3962042 port 35315 ... ok
detail: bind b3: pid 3979108 port 45673 ... ok
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
```

16.1 s wall, one live clone, four real replays (three bind + one kill); the b11909 binary and the 75 MB server
archive were fetched by the replay into its own scratch tree, per leg. Evidence: `c1-instrumented.out`,
`snapshots.json`.

## 2. What the walk actually sees (real tree, recorded, not inferred)

`tools/round50-replay-bind-audit.py:279` (`descendants`) enumerates `/proc` once, builds `ppid → children`, and
walks the graph from the root; `:418` (`replay_pid`) keeps the direct children of the invoker and returns the
singleton; `:297` (`descends_from`) walks `pid → ppid` upward, ≤ 64 hops.

Seven non-empty snapshots were taken by the counter itself (§1 run). Every recorded process closes to its root:

| leg | root (invoker) | replay (1 hop) | live tool (2 hops, grandchild) | llama-server (3 hops) |
|---|---|---|---|---|
| b1 | 3928687 | 3928778 | 3942157 | 3943953 |
| b2 | 3948805 | 3948850 | 3960410 | 3962042 |
| b3 | 3966595 | 3966653 | 3977560 | 3979108 |
| **kill (teardown)** | 3983346 | 3983408 | **3995604** | **3997385** |

- `replay_pid`: for each bind leg the invoker had exactly one direct child, and `replay_pid` returned it
  (`3928778`, `3948850`, `3966653`); the recorded `replay_pid` result equals the replay pid in 3/3 legs.
- Teardown snapshot (`:505`) contains exactly the three live processes; the announced `ready.json` pid is the
  server (`:507` guard), and it is in the snapshot in all legs. The teardown check (`:512-520`) then settled in
  0.10 s (cap `KILL_WAIT = 30`, `:112`).
- **Excluded, as required:** the counter process itself (3902767) appears in no snapshot, and the decoy child the
  probe hung off the counter side (3902976, a `sleep 600`, alive for the whole run) appears in none — the root is
  the invoker, never the counter, and `descendants()` never includes its own root. The second `descendants()` call
  each leg makes (inside `reap`, after the replay exited) returned 0 processes, which is the premise reap relies on.
- Each bind leg's first snapshot is taken *before* `replay_pid`, so the grandchild/great-grandchild were already
  present when the singleton rule ran — i.e. the singleton rule is insensitive to the replay's own children, as
  documented.

## 3. Adversarial matrix (synthetic trees, same functions, real pdeathsig cascade)

`synth_probe.py` runs under the same invoker shape (`INVOKER` from `:116`) with stand-ins that keep the real
process geometry (replay → tool with `PR_SET_PDEATHSIG` SIGTERM → server with SIGKILL-on-parent-death) and the
same teardown expressions as `:452` and `:507/:520`. 20/20 predictions matched; results in `synth-results.json`.

| # | shape | counter behaviour | direction |
|---|---|---|---|
| A | clean 3-level tree | snapshot = {replay, tool, server}; `replay_pid` = replay; `descends_from(server, invoker)` true; SIGKILL invoker empties snapshot in 0.05 s; probe/counter-side pids absent | pass |
| B | **extra background child of the invoker** (second direct child) | `replay_pid` → `None`; `:452` emits `server pid N does not descend from the replay process None`; bind leg false | **false negative** |
| C | **ppid gap** — descendant `setsid`+double-forks, intermediate exits (orphan reparents to the namespace init, here `systemd` pid 1494) | absent from `descendants()`; `descends_from` false; teardown `alive` empty and would report `ok` while the escaped descendant still runs | **false positive** (survivor) |
| D | **child created after the snapshot** | late child has ppid = replay, absent from the snapshot; snapshot processes all die (0.05 s), late child survives — check reports `ok` | **false positive** (survivor) |
| E | zombie child beside one live child | zombie not counted (`descendants` skips `Z`/`X`), `pid_alive` false, `replay_pid` still the live child | pass (intended) |
| E2 | *only* a zombie direct child | `replay_pid` → `None` | false negative (unreachable: the fixed invoker reaps via `subprocess.call`) |
| F | 70-hop spine | `descendants()` finds all 71 pids; `descends_from(leaf, invoker)` **false** (64-hop cap) | inconsistency at depth > 64 |

The same noisy-invoker shape was also run **against a real replay** (`noisy_real.py`, exit 0, `noisy-real.json`):
invoker 229733 with direct children `[229837 sleep, 229842 python3 … kama-live-replay.py]`; snapshot
`[229837, 229842, 246648, 248888]` with parents `tool→replay→invoker` and `server(248888)→tool(246648)`;
`replay_pid` → `null`; `descends_from(server, 229842)` → **true**; replay exit 0, `match true`. So the failure in
B is attribution only — the tree is sound and the server genuinely descends from the replay.

## 4. Shapes that break the assumptions (limits, with file:line)

1. **Invoker child multiplicity** — `replay_pid` (`:418-421`, docstring "The replay process: the invoker's only
   child") requires exactly one live direct child. One extra background child of the invoker makes it `None` and
   the bind tree check (`:452`) a false negative (B, and real replay above). The counter *documents* its invoker as
   `python3 -I -c … which only starts the replay and waits` (`:27`), and `start_replay` (`:396-406`) is the only
   producer of invokers, so this is a limit, not a live hole. It fails closed (bind = 0), which is the safe side.
2. **Reparenting gap** — `descends_from` (`:297-307`) needs an unbroken live `ppid` chain. A descendant that
   detaches (`setsid` + intermediate exit, double-fork, any wrapper that exits) is neither in the teardown snapshot
   (`:505`) nor found by `descends_from`; the teardown `ok` (`:520`) and the survivor reap (`reap`, `:425-435`,
   called from the `finally` at `:490` and `:525`) are both blind to it (C). Server-side, the same gap yields a false
   negative: `:452` fires and, for teardown, `:507` fails the leg closed — so a daemonising server cannot pass.
3. **Post-snapshot child** — the snapshot is a single `/proc` pass (`:279-296`); a descendant forked after it is
   unchecked and, if its own parent dies without pdeathsig, survives both the check and reap (D). The real replay
   closes this window for its own tree: the live tool is forked before `ready.json` and the server before it
   (`kama-live-replay.py:332`, `kama-llamacpp-live.py:1892`), and both carry parent-death signals
   (`kama-live-replay.py:314-319`, `kama-llamacpp-live.py:668`).
4. **Depth cap** — `descends_from` stops after 64 hops (`:299`, `while pid > 1 and seen < 64`), while
   `descendants()` has no cap; above depth 64 the two disagree (F). Measured depth is 3, so unreachable here, but
   any wrapper chain inserted between invoker and replay (`sh -c`, `env`, a supervisor) eats hops.
5. **Zombies** — `descendants` skips `Z`/`X` and `pid_alive` treats them as gone (`:244-249`, `:286-289`); an
   only-zombie child collapses `replay_pid` to `None` (E2), which the fixed invoker (which reaps) cannot produce.
6. **PID namespaces** — `descendants()` is a scan of the counter's own `/proc`; a descendant in another PID
   namespace (or a `/proc` entry unreadable to the counter) is invisible. [INFERENCE] — not exercised here, no
   unprivileged namespace available.

**Reachability of the limits at this tip:** the lane tools never detach and never wrap: the replay starts the live
tool with `subprocess.run` + `preexec_fn` pdeathsig (`kama-live-replay.py:332-339`) and the tool starts the server
with `subprocess.Popen` (`kama-llamacpp-live.py:1892`); no `setsid`, no double-fork, no shell wrapper in either
(`grep -n "setsid\|daemon\|preexec_fn"` over both returns only the pdeathsig preexec). The measured trees were
exactly 3 levels with 7/7 ancestry closure, so limits 1–5 do not bear on the round-50 claim; they bound what a
future change to the tools may silently invalidate.

## 5. Proposed hardening (not applied; counters are frozen)

- `:418-421` — prefer the direct child whose `cmdline` names the replay path, falling back to the singleton rule:
  ```python
  def replay_pid(p):
      """The replay process: the invoker's only child (preferring an argv naming the replay)."""
      kids = [pid for pid, _s in descendants(p.pid).items()
              if (stat_fields(pid) or (None, None))[1] == p.pid]
      named = [k for k in kids if any(x.endswith("kama-live-replay.py") for x in argv_of(k))]
      return (named or kids)[0] if len(named or kids) == 1 else None
  ```
  (`argv_of(pid)` = `/proc/<pid>/cmdline` split on NUL, illustrative.)
- Invoker (`:114-116`, used at `:396-406`) — set `PR_SET_CHILD_SUBREAPER` in the invoker so a detached descendant
  reparents to the invoker instead of the namespace init; the existing snapshot at `:505` and reap at `:425` then
  cover limits 2 and 3 without changing any check expression.

Both are proposals only; no lane file was modified (`tools/round50-replay-bind-audit.py` sha256 still
`ff6ac2ac…`, `tools/kama-live-replay.py` `d5c58972…`, `tools/kama-llamacpp-live.py` `61e777b7…`).

## 6. Hygiene

- One live `git clone --shared` at `$S/lane`; read-only use of the lane (the counter copy was taken with `cp`,
  the lane tools were never imported, so the lane's `tools/__pycache__` was not touched by this seat).
- No pacman, no installs, no service starts beyond the counter's own loopback llama-server legs (all torn down by
  the counter; `pgrep -f llama-server` afterwards shows only other seats' trees, none under `kama-r50/X9Descend`).
- `$S` removed before finishing; every cited receipt is copied into this directory.

Evidence files (this directory): `c1-instrumented.out`, `snapshots.json`, `synth-results.json`,
`noisy-real.json`, and the probes `probe_instrumented.py`, `synth_probe.py`, `noisy_real.py`, `shim.py`,
`spawn_child.py`, `deep.py`. All probes take `$S` as `argv[1]` and expect a byte-identical copy of the frozen
counter at `$S/counter_copy.py` (`cp .../tools/round50-replay-bind-audit.py $S/counter_copy.py`); `$S` is removed
after the run.
