VERDICT: partial — C2's fail-capability holds, but `loading_envelope_graded` false-failed on a healthy b11755 server under host load (1/60 loaded runs); `teardown_graceful` 0/60.

# LiveUnderLoad — C2 false-failure attack under host load

Seat: KamaR17.LiveUnderLoad (falsify wave, round 17). Target: C2's
false-failure risk, not its fail-capability. Lane root
`/home/vgpnk/Projects/shokunin/kama-shokunin`, attacked at lane commit
`54a29268e2083caa2b1e0d54ee1e7d90961302f3` (lane `git rev-parse HEAD` =
that commit; only untracked `.ufo/waves/round-17/falsify/` present). All
runs were done in a `/tmp` clone of that commit; the lane tool is
byte-identical (`sha256 0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`)
and the probe is byte-identical (`36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`).

## What was attacked

Real `tools/kama-llamacpp-live.py` (b11755 llama-server, real
`stories260K.gguf`) run 60 times while the 32-vCPU host was saturated by
`stress-ng --cpu N` (preinstalled 0.22.01) at 3x, 12x, 32x (three arms)
and 64x the CPU count. One idle baseline and five idle
`--threads 32 --ctx 8` runs were used as controls. The counted question:
does `teardown_graceful` or `loading_envelope_graded` fail on the healthy
real server?

## Measured result

60 loaded runs, 11 checks each, harness exit and gate exit recorded per
run. All nine other checks are 60/60; the two named checks:

| arm | stressors (x vCPU) | runs | 1-min loadavg at arm start | `loading_envelope_graded` fails | `teardown_graceful` fails |
|---|---|---|---|---|---|
| cpu96 | 96 (3x) | 10 | 1.96 | 0 | 0 |
| cpu384 | 384 (12x) | 10 | 22.15 | 0 | 0 |
| cpu1024 | 1024 (32x) | 10 | 174.87 | 0 | 0 |
| cpu2048 | 2048 (64x) | 10 | 309.95 | 0 | 0 |
| cpu1024b | 1024 (32x) | 10 | 537.20 (residual) | **1** (`cpu1024b-1`) | 0 |
| cpu1024c | 1024 (32x) | 10 | 308.90 | 0 | 0 |

- `teardown_graceful`: **60/60 pass**, `term_wait_ms` 4 / 152 / 368
  (min/median/max), `sigkill_sent` false in every run; the 10.0 s
  `TERM_GRACE` (`tools/kama-llamacpp-live.py:73`) was never approached.
- `loading_envelope_graded`: **59/60 pass**. Passing runs captured 1-243
  total 503 responses; 23 of the 59 passing runs captured exactly one. The
  failure captured **zero**.
- Harness exit: 59 x 0, 1 x 1. Gate exit: 59 x 0 `VALID`, 1 x 1
  `INVALID`.
- Idle controls: baseline 11/11 `VALID`; five `--threads 32 --ctx 8`
  runs 11/11 with loading windows 79-927 ms, all observed. The C2
  claim's idle measurements are not disturbed by this attack.

## The false failure (exact evidence)

Run `cpu1024b-1` (scratch receipt, regenerable): real server sha256
`b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`
(b11755, `/home/vgpnk/.local/opt/llama-b11755/llama-server`), tool
`0efd1723…`, probe `36b64978…`, model `270cba1b…`, alias
`kama-live-probe`, ctx 256, threads 1, port 41519, child pid 3543432,
`started_utc 2026-10-20T18:48:44.092Z`, `ended_utc
2026-10-20T18:48:51.136Z`. `setup_error` null, `internal_fault` null,
`port_listener_ownership` `child`.

Ten of eleven checks passed, including `health_ready` (200,
`{"status":"ok"}`), both `models_*` checks, `metrics_not_enabled` (501),
`props_alias`, both probes (`MODEL_OK`/`matched`, `MODEL_MISMATCH`/
`served-id-mismatch`), `teardown_graceful`
(`{"alive_at_teardown_start": true, "sigterm_sent": true,
"sigkill_sent": false, "returncode": 0, "term_wait_ms": 92}`),
`teardown_port_closed`, and `model_unchanged`. Only
`loading_envelope_graded` failed: `loading_observed` false,
`loading_503` null, `loading_503_bodies` `[]`,
`loading_envelope_exact` null.

Its `transitions` (verbatim values):

```
models /v1/models  status=None error=ConnectionRefusedError  t_ms=27  repeats=56
models /v1/models  status=200  error=None                    t_ms=71  (678-byte body)
health /health     status=200  error=None                    t_ms=255 (15-byte body)
```

The server's own kept log lines (server-relative ms):

```
0.00.014.006 I srv    load_model: loading model '...stories260K.gguf'
0.00.026.192 I srv  llama_server: model loaded
0.00.029.029 I srv  llama_server: listening on http://127.0.0.1:41519
```

The server clocks are child-relative (its process start precedes the
readiness loop's `t0`), so only the harness clock orders the probe
attempts: no request was made between its last refused connect (t=27 ms)
and its next request (t=71 ms), and that next request was the first
success, at 200. The loading transition completed inside a 44 ms
observation hole; nothing was stored, and the check graded the absence
as a server failure.

Gate output for that receipt (exit 1):

```
INVALID .../cpu1024b-1.json: 3 problem(s)
  - check 'loading_envelope_graded': passed is false
  - loading_envelope_graded: no loading_503 body stored, nothing graded
  - loading_envelope_graded: loading_503_bodies missing or empty in a v2 receipt
```

## Why this is a C2 defect

The producer fails closed on an observation the harness itself can lose:

- `tools/kama-llamacpp-live.py:589` leaves the `/v1/models` phase on the
  first non-503 response; `:554` stores a body only for an observed 503;
  `:1153` sets `loading_observed` from `loading_503 is not None`.
- The check at `tools/kama-llamacpp-live.py:1345-1358` requires
  `loading_observed is True` **and** every stored body exact.
- Its `documented_by` text (`:136-143`) states the intent: "no 503
  observed -> fail with {\"loading_observed\": false} (a real b11755 run
  shows dozens)".
- The gate re-derives the same claim and additionally refuses an empty
  body list (`tests/llamacpp-live/check-receipt.py:908-935`), and turns
  any failed check into a validation problem
  (`tests/llamacpp-live/check-receipt.py:649-650`), so a healthy run
  yields harness exit 1 and gate `INVALID`.

The transition is genuinely sub-millisecond sometimes: passing runs
`cpu1024b-9` and `cpu96-7` captured 19/20 and 7/8 503 responses and the
200 in the **same millisecond**, i.e. the whole window can be shorter
than the 1 ms reporting granularity. Whether the 44 ms hole was the
parent being descheduled or one request being answered only after
readiness, the harness observed no 503 and reported a server defect
although every other server-observable behaviour was correct.
[INFERENCE] the server did serve 503s in this run (the same startup path
served them in 59/59 other runs); the receipt proves the observation
gap, not a server violation.

The failure is a scheduling race, not a monotone function of load: 1/30
runs at 32x, 0/10 at 64x, 0/30 at 3x-12x. 1/60 loaded runs is the
measured rate; the assignment's criterion ("a false failure on a healthy
server is a C2 defect") is met.

## Advice (advisory; L1 decides)

1. Do not count a zero-observation run as a server failure. When
   `loading_observed` is false but the first successful response was 200
   and the rest of the lifecycle is clean, report could-not-evaluate
   (the lane's exit-4 convention) rather than exit 1 / `INVALID`.
2. If a hard verdict is required, retry the lifecycle once or twice on
   that condition before failing. The fake controls cannot lose this
   race: every serving fake answers >=3 loading 503s
   (`tests/llamacpp-live/controls.py:48-49`, `LOADING =
   {'/v1/models': 3, '/health': 1}`), and K2's bad envelope still
   produces 503s, so a retry/could-not-evaluate rule does not weaken K0
   or K2. There is currently no control for a server that never serves a
   503, so fail-closed on absence buys no tested detection.
3. Keep the all-bodies envelope grade unchanged when any 503 is
   observed; this defect is only the zero-observation branch.
4. This does not refute C2's fail-capability: the frozen/current controls
   counts, the three idle 11/11 receipts, and the gate's v1/v2
   re-derivation are untouched; my idle control also gave 11/11 `VALID`.

## Commands run (exit codes in the text)

```
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.LiveUnderLoad-clone
git -C /tmp/KamaR17.LiveUnderLoad-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3   # exit 0
setsid stress-ng --cpu <96|384|1024|2048> --timeout 600s --metrics-brief &                     # each arm
PYTHONDONTWRITEBYTECODE=1 python3 tools/kama-llamacpp-live.py \
  --model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf \
  --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
  --out <receipt>                                  # 59 x exit 0, 1 x exit 1 (cpu1024b-1)
PYTHONDONTWRITEBYTECODE=1 python3 tests/llamacpp-live/check-receipt.py <receipt>
                                                   # 59 x exit 0 VALID, 1 x exit 1 INVALID
```

Arms: `run10.sh 10 96 cpu96`, `10 384 cpu384`, `10 1024 cpu1024`,
`10 2048 cpu2048`, `10 1024 cpu1024b`, `10 1024 cpu1024c` (runner exit 0
each; per-run exits as above). Baseline and the five `--threads 32
--ctx 8` runs used the same command without load, all exit 0, 11/11.

## Limitations

- CPU-only load (no memory pressure, I/O or network stress); the false
  failure is measured for scheduler contention only.
- One hit in 60; the rate estimate has a wide confidence interval, and
  no deterministic reproducer exists (the race depends on per-run
  scheduling).
- `loadavg` figures are host 1-minute averages, not per-run instantaneous
  load; other fleet seats were also running, so the exact stressor
  contribution is not isolable, though stress-ng was the dominant load
  (post-arm 1-min averages reached 939-2036).
- The receipt cannot distinguish "parent descheduled" from "one request
  answered after readiness"; both produce the same zero-observation
  outcome and the same false failure.

## Tooling, privacy, cleanup

- No installs or upgrades. `stress-ng` 0.22.01 and Python 3.14.8 were
  already present; no pacman transaction was run.
- Ports 8080, 34113 and registry consumer ports were never contacted or
  bound; every run used a fresh loopback port chosen by the tool
  (reported ports 34k-45k).
- No lane file other than this Report was written; all measurement ran
  in the `/tmp` clone. After the runs: no `stress-ng`, no `llama-server`
  alive, every receipt child pid dead, no receipt port listening. The
  `/tmp/KamaR17.LiveUnderLoad-*` scratch (clone, runner, receipts) was
  removed after this Report was written.
