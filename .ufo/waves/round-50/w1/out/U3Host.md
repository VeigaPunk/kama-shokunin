# U3Host — host-safety walk of the round-50 teardown chain

VERDICT: the chain holds exactly where the counter tests it — killing the replay's parent (my shell, same position as the counter's invoker) took replay, live tool and server down and closed the port at the first 25 ms poll, far inside the 30 s bound, and SIGTERM to the replay tears the server down gracefully through the live tool's handler — but one unprotected link remains above it: the counter's invoker itself has no pdeathsig, so killing the counter (the invoker's parent) leaves invoker + replay + live + server up for the FULL witness timeout (observed 15.0 s at --witness-timeout 15; the counter uses the 120 s default), after which the orphaned replay completes normally and writes a matched receipt with witness.released=false and orphaned=false. Claim C1 teardown is met for what it measures; the docstring's "killing whatever started it takes replay, live tool and server down" (round50-replay-bind-audit.py:7, replay docstring:50-51) is overstated for the counter-death case.

Tools run: lane clone at HEAD 3b79ead; `kama-live-replay.py` / `kama-llamacpp-live.py` verified byte-identical to the frozen build commit 97c864bead3ee4a2f629574e77263d33834ec98a (git show + diff, zero differences). Receipt: `.ufo/waves/round-48/c2/live/receipt-1.json` (schema kama-llamacpp-live/v5). Harness: `teardown_walk.py`, `leg_d.py` (copied into this directory).

## Chain as built (file:line)

- replay arms its own pdeathsig SIGTERM: `set_own_pdeathsig()` tools/kama-live-replay.py:100-109, called at :587 before `replay()`.
- replay spawns live isolated `python -I`, allow-list env, preexec pdeathsig SIGTERM: kama-live-replay.py:309-332.
- live installs SIGINT/SIGTERM/SIGHUP → `Terminated`: kama-llamacpp-live.py:1862-1866; `finally:` teardown SIGTERMs the server process group, SIGKILL after 10 s grace, proves the port: :1117-1150.
- server spawned with `start_new_session` + preexec pdeathsig SIGKILL: kama-llamacpp-live.py:661-672, :1882-1896 (belt under the handler).
- live's witness hold also polls its own parent: `os.getppid() == parent` kama-llamacpp-live.py:342,359, `orphaned` recorded at :363.

## Leg A — SIGKILL the shell that started the replay (replay's parent)

`bash -c 'python3 -I <clone>/tools/kama-live-replay.py --receipt <clone>/.ufo/waves/round-48/c2/live/receipt-1.json --work work-A --out A.json --witness-dir wd-A & wait'`, `start_new_session`, env = PATH/HOME/LANG/TMPDIR only; shell = replay's direct parent — the same slot the counter's `python3 -I -c` invoker occupies (round50-replay-bind-audit.py:402-404).

- ready.json at 2.4 s: port 33021, server pid 978537. Tree: bash 954022 → replay 954028 → live 975622 → llama-server 978537 (ppids verified via /proc stat).
- `kill -9 954022` (shell rc -9). Result: replay, live AND server all gone and port 33021 refusing at the first 25 ms poll; `all_dead_within_30s: true`.
- What the rerun receipt shows (rerun-receipt-A.json): `setup_error: "terminated:signal 15"`, `outcome: "setup-error"`, `teardown: {sigterm_sent: true, sigkill_sent: false, returncode: 0, alive_at_teardown_start: true, port_refuses: true, term_wait_ms: 3}`, `child_pid: 978537` — live caught the pdeathsig SIGTERM, SIGTERMed the server group, server exited 0 in 3 ms, and live wrote its receipt before exiting. `witness` is null (Terminated was raised inside hold_for_witness before it returned; ready.json removed by its finally — wd-A left empty). Replay wrote no out.json — expected: it died mid-`subprocess.run`.
- No survivor, no zombie; kill order at 25 ms granularity indistinguishable.

Does the counter's invoker shape avoid survival? YES for the link it guards: the invoker IS the replay's parent, so its death fires the same pdeathsig leg A exercised — the counter's teardown_leg (SIGKILL invoker, :509) is exactly this measurement, and the round-49 hole (parent death never noticed) is closed by arming pdeathsig on the replay itself rather than only on the server.

## Leg B — SIGTERM the replay mid-hold

Same launch; `kill -TERM 981769` (replay). Replay has no SIGTERM handler → dies instantly. Kernel then delivers SIGTERM to live (its pdeathsig). Result: all three gone, port 32789 refusing at first 25 ms poll. rerun-receipt-B.json identical in shape to A: `terminated:signal 15`, graceful teardown (sigterm_sent, no sigkill, rc 0, 3 ms), witness null, ready.json removed. The shell's `wait` returned 0 — bash `wait` with no arguments always exits 0 (verified with a toy `sleep 30 & wait`; not tool behavior). No replay out.json.

## Leg C — the frontier gap: SIGKILL the counter-stand-in (invoker's parent)

Chain bash → `python3 -I -c` invoker (exact counter INVOKER source, round50-replay-bind-audit.py:114-115) → replay → live → server. Killed the TOP bash at t=0.

- Survivors at 0.5 s, 2 s, 5 s: invoker, replay, live AND server ALL alive; port 39203 still accepting. The invoker has no pdeathsig (it is plain `subprocess.call`), so the counter's death is invisible to the whole chain — this is R2's complaint shape one link up.
- Then `kill -9` on the orphaned invoker (t=5.01 s): all four gone and port refusing at the first 25 ms poll — leg A's mechanism again, proving the fix works per-link.

## Leg D — how bad is the gap? (counter-stand-in killed, no rescue, --witness-timeout 15)

- Nothing died for the full 15 s witness window; at 15.02 s invoker, replay, live and server exited together and the port refused.
- The orphaned replay then COMPLETED: replay-out-D.json `match: true`, `live_exit: 0`; rerun-receipt-D.json `outcome: "pass"`, `setup_error: null`, `witness: {released: false, waited_ms: 15036, orphaned: false}`. `orphaned` only tracks live's DIRECT parent (replay, still alive) — a grandparent kill is invisible to it.
- So a dead counter leaves: llama-server listening on loopback and a ~76 MB work tree for up to `--witness-timeout` (120 s default in the counter; bounded also by live's `--witness-timeout` arg), then honest self-clean — no infinite leak, no false receipt, but "whatever started it" is not taken down promptly.

### Finding (report only — counter/tools frozen)

`round50-replay-bind-audit.py:114-115` INVOKER is the one link in counter → invoker → replay → live → server that arms no parent-death signal. Proposed fix (either):
1. Give the invoker its own pdeathsig, e.g. prepend to INVOKER: `import ctypes, os, signal, subprocess, sys` + `ctypes.CDLL(None).prctl(1, int(signal.SIGKILL), 0, 0, 0)` (PR_SET_PDEATHSIG) — then a counter death kills the invoker, which kills the replay via leg-A's path. Keeps the counter's teardown leg unchanged.
2. Or have the replay watchdog `os.getppid()` against the ppid captured at `set_own_pdeathsig` and abort when it changes (covers any launcher, not just the counter).

## Reproducibility / hygiene

- Harness and all outputs copied here: `teardown_walk.py`, `leg_d.py`, `results.json`, `legD.json`, `rerun-receipt-{A,B,C,D}.json`, `replay-out-D.json`.
- Every leg's witness dir was left empty (ready.json removed; verified `wd_entries: []`); no llama-server or replay process of mine survived (`pgrep -f` clean). Scratch `/fast/scratch/hyaku/kama-r50/U3Host` removed after copying.

Report: .ufo/waves/round-50/w1/out/U3Host.md
