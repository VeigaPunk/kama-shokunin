# X1Kill — killing a witnessed replay: leftovers, and what pdeathsig actually covers

**Verdict: FALSIFIED for kills aimed at the replay.** SIGTERM *or* SIGKILL of a witnessed
`tools/kama-live-replay.py` leaves the llama-server running and its port LISTENing for
**120.16 s** (the witness timeout), not ≤ 15 s. The hypothesis holds only when the kill lands on
the live tool: SIGKILL there drops the server in **0.25 s**. `pdeathsig` covers **one hop only**
(live tool → llama-server); nothing covers replay → live tool, so the chain is broken above the
last link.

Measured against the build blobs extracted from **74558c71** (`kama-live-replay.py` sha256
`636074f9628f8c6106a0b5508dd7a15e8d677ea89cfbe0cd2a665f85ddd1e01a`, `kama-llamacpp-live.py`
sha256 `72e76079995c5ba8269bbaa31e30b8c15c5e503de2a58e603b78561424bffd4c`). The same scenarios were
also run on the lane working tree, which other seats were editing throughout this wave; at the
time of runs A–E its bounded witness path was still identical to the build. That changed at
~20:38Z and the change alters the answer for kills aimed at the replay — see *Lane state* below.
The worktree is a moving target; the fixed point is the build blobs.

## What was run

Seat command, per scenario, with a fresh `--work` and `--witness-dir` (scratch
`/fast/scratch/hyaku/kama-r49/X1Kill`):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py \
  --receipt .../.ufo/waves/round-48/c2/live/receipt-1.json \
  --work $S/w-<tag> --out $S/j-<tag>.json --witness-dir $S/wd-<tag>
```

The replay was started in its own session (`start_new_session=True`, so cleanup could `killpg`
without touching the harness), then polled for `$S/wd-<tag>/ready.json` (ready in **2.4–2.9 s**
each run, four runs), and after `ready.json` appeared the signal was sent and the tree observed
every 250 ms for **15 s**: `alive(/proc/<pid>)` (Z counted dead), a real connect to
`127.0.0.1:<port>`, and `ss -ltnp 'sport = :<port>'` at t=0 and at the end of the window.
`/proc/<server>/exe` hashed `35ac50fb2cfd9c4f…d7ff0` (frozen b11909 server) in every run;
`ready.json` schema/port/pid were correct in every run.

Drivers kept in `out/X1Kill/`: `drive.py` (A/B/C), `driveD.py`, `driveE.py`, `driveFG.py`,
`driveH.py`, `driveI2.py`, `counter_shape.py`, `driveBuild.py`. Raw per-scenario records:
`out/X1Kill/result-*.json`, compact roll-up `out/X1Kill/SUMMARY.json`.

## Evidence

| # | tree | signal sent to | exit | server + listener at 15 s | gone at |
|---|------|----------------|------|---------------------------|---------|
| **B1** | build 74558c71 | replay pid 2422232, **SIGTERM** | replay −15 | **yes, `LISTEN 127.0.0.1:45725 users:(("llama-server",pid=2426019,fd=3))`** | never in 15 s |
| **B2** | build 74558c71 | live tool pid 2460730, **SIGKILL** | replay 2 (`no-rerun-receipt:exit=-9`) | no | server 0.25 s, port 0.25 s |
| A | worktree | replay, SIGTERM | replay −15 | yes, `LISTEN …:42139 …pid=297160` | never in 15 s |
| B | worktree | replay, SIGKILL | replay −9 | yes, `LISTEN …:36487 …pid=297162` | never in 15 s |
| C | worktree | live tool, SIGKILL | replay 2 | no | 0.2 s |
| D | worktree | replay, SIGTERM, **no release written** | replay −15 | yes | **120.16 s** (see below) |
| E | worktree | live tool, **SIGTERM** (cooperative) | replay 1, `live_exit 2` | no | 0.2 s |
| I2 | worktree + counter-shape parent | the parent (≡ the C1 counter), SIGTERM | — | **yes: replay 1715818 + live 1724006 + server 1725243 all alive, `LISTEN …:38507`** | never in 15 s |

B1/B2 (`out/X1Kill/result-B1.json`, `result-B2.json`) are the authoritative pair on the build:

* B1 `at_15s`: `server True, listening True, replay_exit -15`; the orphaned live tool's ppid had
  been rewritten from 2422232 to **1494** (`live_ppid 1494`) — the live tool does not notice.
* B2 `gone_after_s {server 0.25, port_closed 0.25, live 0.25}` and `replay_exit 2`, i.e. the
  kernel's `PR_SET_PDEATHSIG` on the server kills it when its own parent (the live tool) dies.

**D bounds the leftover**: with no `release` file, the orphan held the server for exactly
**120.16 s**, then tore it down itself — its rerun receipt records
`witness {released: false, waited_ms: 120004}`, `teardown {returncode 0, sigterm_sent true,
sigkill_sent false, port_refuses true}`, `outcome pass`. So the leftover is not permanent; it is
the witness timeout (`--witness-timeout`, default 120 s; exposed at
`tools/kama-live-replay.py:453`).

**E is the clean stop path**: SIGTERM to the *live tool* makes it run its ordinary teardown —
server gone in 0.2 s, `port_refuses` true, replay exits 1 with `live_exit 2` (the rerun receipt
carries `setup_error terminated:…`, no `witness` block).

**I2 shows the leak propagates one level up.** A parent process that spawns the replay exactly
the way the frozen counter does (`tools/round49-replay-witness-audit.py:297-298`:
`subprocess.Popen(...)` with no `start_new_session`, no `preexec_fn`, stdout/stderr to a log)
was SIGTERMed mid-witness; 15 s later the replay, the live tool and the server were all alive
with the port bound. Stopping it needed two signals: `SIGTERM` replay (dies in 1 s, live tool
survives), then `SIGTERM` live tool (server torn down cleanly). A `kill` of the replay alone is
the natural operator move and does nothing to the server.

## Lane state during this seat (worktree, 2026-10-26T23:27–23:41Z)

The worktree moved under this seat while it measured. Digests at the time of the last two runs:
`kama-live-replay.py` sha256 `d086d22dfa0c879221fe2790c6b1ecc865032d80b71ebd9592e564cb544ef79d`,
`kama-llamacpp-live.py` sha256 `9743406fd120977c77dffbc16dfbc6cec2b043fb64bae8c1b7565563c0b1ee00`.
Peer changes that landed during the wave: `prepare_witness_dir()` (X1Offline), a per-run
`ready.json.tmp.<pid>`, a child-alive check before announce (V1Live F2), the archive
`os.open`/`fstat` hardening (V1Live F1), a `--witness-dir` selftest case (X1Selftest) — and, at
~20:38Z, the hold-loop parent check below. Re-measured at that state (`driveW.py`,
`result-W1.json`, `result-W2.json`):

| # | signal | at 15 s | result |
|---|--------|---------|--------|
| **W1** | SIGTERM the replay | server gone **0.25 s**, port closed 0.25 s, `witness {orphaned true, released false, waited_ms 100}`, no `ready.json` and no `release` left in the dir | hypothesis **holds**: the replay-kill half of the defect is now fixed in the worktree |
| **W2** | SIGTERM a counter-shape parent (spawn shape copied from `round49-replay-witness-audit.py:297-298`) | replay 2857582 alive, live 2859904 alive, server 2897103 alive, `LISTEN 127.0.0.1:41555 users:(("llama-server",pid=2897103,fd=3))`, counter dead | **still leaks**: a parent's death is invisible to the hold's own parent check, and the replay does not die with the counter |

The worktree `hold_for_witness()` now reads `parent = os.getppid()`, ends the loop when reparented,
unlinks `ready.json` in a `finally` and reports `orphaned` — the comment credits this seat. The
worktree `kama-live-replay.py` still differs from the build only by a witness selftest case: no
`start_new_session`, no `preexec_fn`, no signal handling, so the replay hop remains open and W2 is
closed only by proposal 1. With the hold fix in place, cleaning W2 now needs two signals instead
of three: `SIGTERM` the replay → the live tool aborts its hold → server down within ~1 s.

## Defect

**`tools/kama-live-replay.py:280-281` (build 74558c71)** — the live child is started with

```python
p = subprocess.run(argv, capture_output=True, text=True, env=env,
                   timeout=timeout + (witness_timeout if witness_dir is not None else 0))
```

no `start_new_session`, no `preexec_fn` pdeathsig, and the module imports none of `signal`
(imports at 55-65). The tool therefore has no way to take the process that owns the announced
server down with it: a SIGTERM/SIGKILL of the replay leaves the live tool waiting on
`<witness-dir>/release` (up to 120 s) and the server holding the port.

**`tools/kama-llamacpp-live.py:280-300` (hold loop, `while … :295-296`)** — the hold loop watches
`release`, the timeout and the child; it never watches its own parent. The only parent-awareness
in the file is child-side: `_preexec_pdeathsig` (588-601, `prctl` at 595), `_FORKED_PPID`
(1743, 596), and the spawn flags at 1748-1749. `receipt['pdeathsig']` (1760) is recorded
`prctl_ok 'unknown'` — honest, but it documents only the live→server hop.

So `pdeathsig` does **not** cover the chain: replay → live tool is unprotected, live tool →
llama-server is protected (proved by B2/C).

Showing command (read-only toward the lane; re-extracts the build blobs with `git show` and
asserts their sha256, then runs both scenarios, ~45 s):

```
python3 .ufo/waves/round-49/w1/out/X1Kill/driveBuild.py
# B1: SIGTERM replay -> server + listener alive at 15 s   (reproduced twice: pids 2422232, 2628071)
# B2: SIGKILL live   -> server + port gone at 0.25 s      (reproduced twice: pids 2460730, 2654274)
```

Corollary, not a false pass: the frozen counter spawns the replay with the same unprotected shape
(`round49-replay-witness-audit.py:297-298`), so a counter killed mid-witness leaks the same tree
(I2). On its own timeout it kills only the replay (`:315-318 p.kill()`), after which its
"server still alive or port still accepting" check fires and the leg *fails* — the instrument
reports the leak rather than hiding it, so C1's `met` predicate is not cheated by this defect.

## Proposed fix (verified, not applied to the lane)

1. `out/X1Kill/proposed-replay-spawn.diff` — `tools/kama-live-replay.py` against the build blob:
   `import signal`, a `StopRequested` exception, an `_pdeathsig()` preexec, and
   `Popen(..., start_new_session=True, preexec_fn=_pdeathsig)` + `communicate()` with
   `killpg(SIGKILL)` on timeout and `killpg(SIGTERM)` → grace → `killpg(SIGKILL)` on any stop;
   a stop is recorded as `refused: terminated:signal N`, exit 2.
2. `out/X1Kill/proposed-live-witness-orphan.diff` — `tools/kama-llamacpp-live.py` against the
   build blob: `hold_for_witness()` records `os.getppid()` and leaves the loop as soon as it is
   reparented, adding `orphaned` to the witness block. Defence in depth for any future caller
   that gets the spawn wrong.

Verification (each a real replay of receipt-1; `$S/prop/` and `$S/fake-lane/` are the patched
copies, the patched live tool staged with `tools/kama-probe.sh` + `registry/` so it resolves its
lane-relative paths):

| run | combination | result |
|-----|-------------|--------|
| F | patched replay + SIGTERM | server 0.2 s, port 0.2 s, `refused terminated:signal 15`, exit 2 |
| G | patched replay + SIGKILL | server 0.2 s, port 0.2 s, replay −9 |
| H1 | patched live, normal `release` | exit 0, `match true`, `witness {released true, orphaned false, waited_ms 100}` — no regression |
| H2 | **build** replay + patched live + SIGTERM to replay | server 0.2 s, port 0.2 s, `witness {orphaned true, released false, waited_ms 100}` — patch 2 alone also satisfies the hypothesis |

## Operability notes

* A killed witness run binds a loopback port for up to `--witness-timeout` (120 s default) and
  then self-cleans; the correct teardown target today is the **live child** (SIGTERM, 0.2 s) or
  writing `<witness-dir>/release`, *not* the replay.
* `ready.json` outlives a killed replay, which is what lets an outside observer still find the
  held server — useful, but it also means "replay gone" does not imply "server gone".
* No new tool was installed; system `python3` (3.14), `ss`, `sha256sum` only. No pacman, no git
  mutation, no lane write outside `out/` (`git -C kama-shokunin status --porcelain` shows only
  other seats' in-flight files, e.g. `tools/kama-llamacpp-live.py` from V1Live; untouched by me).
* Leftovers: none of mine. A `/proc` scan for cmdlines containing `kama-r49/X1Kill` returns 0
  after cleanup; every server I started was killed and its port verified closed. `pgrep -f
  llama-server` shows only peers' processes (`.../kama-r49/M1Ctr/...`, `.../S1Gate/...`).

## Files written

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Kill.md`
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Kill/`
(`SUMMARY.json`, `result-A…E.json`, `result-B1.json`, `result-B2.json`, `result-F…H2.json`,
`result-I2.json`, `drive*.py`, `counter_shape.py`, `replay-*.log`,
`proposed-replay-spawn.diff`, `proposed-live-witness-orphan.diff`)
