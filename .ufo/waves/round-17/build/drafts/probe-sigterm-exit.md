# Probe: llama-server b11755 signal-exit behaviour (ProbeSigtermExit-2, 2026-10-20)

Empirical advice for the C2 `teardown_graceful` predicate (expected `returncode 0`).
Subject: `~/.local/bin/llama-server` → `~/.local/opt/llama-b11755/llama-server`
(`version: 0.7.0-dev (build 11755, commit 704366d76)`, GNU 11.4.0, Linux x86_64).
Fixture: `~/.cache/kama-shokunin/models/stories260K.gguf` (1,185,376 bytes,
sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d).
Argv per run: `-m stories260K.gguf --alias kama-probe-x --host 127.0.0.1
--port <free ephemeral> -c 256 -t 1`, `start_new_session=True` only in case (e).
Ports: a fresh `socket.bind(("127.0.0.1", 0))` port per run (observed e.g.
37187, 60097, 60417, 48561, 41461); nothing from
`registry/endpoint-consumers.tsv` was bound. Harness: `python3` 3.14.8,
`Popen.send_signal`/`os.killpg`, `proc.wait(timeout=15)`. 5 runs per case,
sequential, one server at a time. Post-run cleanup verified:
`ss -ltnp | grep -i llama` empty, `pgrep -af llama-server` empty.

## Results — every run (returncode, ms from signal to exit, ms until trigger condition)

| case | trigger | signal | runs | returncode | exit_ms (all runs) | trigger_ms (all runs) |
|------|---------|--------|------|------------|--------------------|------------------------|
| a | `/health` 200 `{"status":"ok"}` | SIGTERM → pid | 5 | **0 ×5** | 3.1, 3.1, 3.2, 3.1, 3.1 | 50–54 |
| b | `/health` 200 ok | SIGINT → pid | 5 | **0 ×5** | 3.1, 3.1, 3.1, 3.1, 3.2 | 50–51 |
| c | port accepts TCP (pre-health) | SIGTERM → pid | 5 | **0 ×5** | 1.1, 1.1, 1.1, 1.1, 1.1 | 20–20 |
| d | `/health` 200 ok | SIGTERM ×2, 10 ms apart | 5 | **0 ×5** | 10.1, 10.1, 10.1, 10.1, 10.1 | 50–51 |
| e | `/health` 200 ok, new session | SIGTERM → pgid | 5 | **0 ×5** | 3.1, 3.1, 3.1, 3.1, 3.1 | 50–51 |

25/25 runs: `returncode == 0`. Zero timeouts, zero SIGKILLs needed, zero
nonzero exits. No run reported a returncode other than 0.

## stderr — the only shutdown line (identical in all 25 runs)

```
0.00.0NN.NNN I srv    operator(): operator(): cleaning up before exit...
```

Exactly one shutdown-related line per run; no "terminate", "signal",
"interrupt", "exiting" or "stopped" text. Log timestamps confirm the
ordering: `listening on http://127.0.0.1:<port>` at ~9 ms after spawn,
`cleaning up before exit...` at ~48–51 ms.

## Case (c) caveat — "SIGTERM during loading" could not be staged

With the 1.2 MB fixture the server self-reports `model loaded` at ~9 ms and
opens the listen socket at ~20 ms; `/health` is already 200 `{"status":"ok"}`
at first poll (~50 ms). The socket never accepts while the model is still
loading, so "send SIGTERM as soon as the port accepts" measures
**SIGTERM after listen, before first /health OK** — i.e. ready-but-young, not
loading-state. A true loading-state SIGTERM needs an artificial delay:
bigger model, `SIGSTOP`/throttle, or a fake server. [INFERENCE]

## Advice for `teardown_graceful` (receipt `kama-llamacpp-live/v2`)

1. `returncode == 0` is the correct expected value on b11755: it holds for
   SIGTERM-ready, SIGINT, double-SIGTERM (10 ms gap), and group-SIGTERM.
   A `teardown_graceful` check graded as `sigterm_sent && !sigkill_sent &&
   returncode == 0` matches observed behaviour exactly.
2. rc 0 alone **cannot** distinguish harness-initiated SIGTERM from a
   spontaneous clean exit or from SIGINT — all three produce rc 0 and the
   same stderr line. The receipt MUST carry the harness's own record of
   which signals it sent (`sigterm_sent`, `sigkill_sent`); the exit
   observation alone is not evidence of the cause. (This is the round-16
   ReviewLiveHarnessCode defect.)
3. Exit latency: max observed 10.1 ms (double-signal case). A
   `term_wait_ms` bound of ~1 s (or any bound ≥ ~100 ms) will never flake on
   this model/hardware while still catching a hang; the round-16 receipt's
   `term_wait_ms 3` is reproduced (3.1 ms).
4. A second SIGTERM during shutdown is absorbed harmlessly (rc 0, ~10 ms) —
   the predicate does not need to special-case repeat signals, but
   `sigkill_sent` MUST remain the fail signal (SIGKILL exit = `returncode -9`
   per `subprocess` docs).
5. stderr marker, if a check wants one: the stable literal is
   `operator(): operator(): cleaning up before exit...` (tag `srv`,
   severity `I`). It is emitted on every graceful exit observed. Absence of
   this line with rc 0 would indicate exit before the server loop installed
   its handlers [INFERENCE — no such run was produced].

## Limitations

- One model (1.2 MB, sub-100 ms startup), one host, -c 256 -t 1. Larger
  models with slow loads could exercise code paths (slot init, prompt
  processing in flight) that change exit latency. [INFERENCE]
- Loading-state signal path unmeasured (see case c caveat).
- Only graceful-signal space probed; no SIGKILL-after-SIGTERM-escalation
  run (not in the assigned matrix).
- `exit_ms` measured by harness wall clock around `proc.wait`; ±0.1 ms noise.

## Provenance

Raw results: `/tmp/kama-sigterm-exit/results.json` (deleted with scratch dir
before finish). Probe script `/tmp/kama-sigterm-exit/probe.py` (same).
25 spawns of the operator-installed binary; no installs, no registry ports,
no lane files mutated.
