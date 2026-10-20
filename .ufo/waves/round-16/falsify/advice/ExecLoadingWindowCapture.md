VERDICT: confirm — the live 503 "Loading model" window is real and easily capturable; the new MODEL_LOADING verdict fires on genuine llama-server traffic while the frozen probe misclassifies the same bytes as FOREIGN_SERVICE.

# Seat: ExecLoadingWindowCapture (round-16 FALSIFY)

Attacked item: the C1/C2 loading-window premise — that the pinned llama-server
b11755 actually emits the documented 503 loading envelope on GET /v1/models,
and that the new `MODEL_LOADING` verdict separates from the frozen probe's
`FOREIGN_SERVICE` on real (not stub-fixture) bytes.

## Commands run and exit codes

1. `python3 /tmp/kama-r16-ExecLoadingWindowCapture/capture503.py` — exit 0.
   Harness mirrors `tools/kama-llamacpp-live.py` launch discipline: absolute
   server path `/home/vgpnk/.local/opt/llama-b11755/llama-server`, pinned model
   `~/.cache/kama-shokunin/models/stories260K.gguf` (sha256 pre-verified
   `270cba1b…256d`, else abort), `--host 127.0.0.1`, `-c 256 -t 1
   --no-webui --offline`, free non-registered port (bind:0 probe, refusing
   8080/34113 and every registry port token), env allowlist
   {PATH,HOME,LANG,LC_ALL,TMPDIR}, `start_new_session`, killpg teardown.
   Unlike the lane harness it polls ONLY `/v1/models` on a keep-alive
   connection from the first accepted socket.

2. `python3 /tmp/kama-r16-ExecLoadingWindowCapture/replay_stub.py` — exit 0.
   Served the verbatim captured bytes (status 503 + captured headers + body)
   on every path of a loopback stub, then ran
   `bash <probe> check --port P --expect kama-stories260k --json --timeout 2
   --connect-timeout 1` for current and frozen probes.

3. `python3 /tmp/kama-r16-ExecLoadingWindowCapture/probe_race.py` — exit 0.
   Spawned the real probe immediately after each `Popen` of llama-server,
   alternating current/frozen, 10 launches.

## Evidence

### Capture rate: 10/10 tries produced live 503s on /v1/models

```
try 0: port=54917 connect_ms=6.56  n=37 503s=36   try 5: n=45 503s=44
try 1: port=36041 connect_ms=6.50  n=49 503s=48   try 6: n=43 503s=42
try 2: port=45799 connect_ms=6.66  n=50 503s=49   try 7: n=44 503s=43
try 3: port=58959 connect_ms=6.44  n=49 503s=48   try 8: n=41 503s=40
try 4: port=42979 connect_ms=6.75  n=51 503s=50   try 9: n=52 503s=51
```
Total: 453 live 503 responses across 10 launches; all ten runs ended
`ready-200` (final 200 on /v1/models ~12ms after first socket accept).

### Verbatim captured response (try-0 first hit, t_ms 6.56)

Status `503`. Headers:
`Server: llama.cpp`, `Access-Control-Allow-Origin: ""`,
`Content-Type: application/json; charset=utf-8`, `Connection: close`,
`Content-Length: 75`.
Body (verbatim, single distinct sha256
`baa09177700f64520a799fd2628bb3663c1486b25e17e4a507f2e6c81bef957c` across
ALL 453 captured 503s in ALL 10 tries):

```
{"error":{"message":"Loading model","type":"unavailable_error","code":503}}
```

This is byte-identical to the documented envelope
(`tools/kama-probe.sh:33`, `kama-llamacpp-live.py` `loading_envelope_exact`)
and to the stub-matrix fixtures — real traffic matches the pinned claim.

### Stub replay of the exact captured body — both probes

- current `tools/kama-probe.sh`: exit **2**, verdict **MODEL_LOADING**,
  reason **llamacpp-loading**.
- frozen `.ufo/waves/round-16/frozen/kama-probe-before.sh`: exit **2**,
  verdict **FOREIGN_SERVICE**, reason **non-2xx-non-model-http**.

Separability is confirmed on genuinely captured bytes, not just authored
fixtures: the frozen probe misclassifies the real llama.cpp loading envelope
as a foreign service — exactly the drift the C1 calibration fixes.

### Live probe race (end-to-end, no stub)

10 fresh launches, probe spawned in the same instant as `Popen`:

```
try 0 current  DEAD            connection-refused     wall=25.3ms
try 1 frozen   DEAD            connection-refused     wall=23.9ms
try 2 current  MODEL_LOADING   llamacpp-loading       wall=39.9ms
try 3 frozen   FOREIGN_SERVICE non-2xx-non-model-http wall=42.3ms
try 4 current  MODEL_LOADING   llamacpp-loading       wall=40.2ms
try 5 frozen   DEAD            connection-refused     wall=24.2ms
try 6 current  DEAD            connection-refused     wall=24.1ms
try 7 frozen   DEAD            connection-refused     wall=23.0ms
try 8 current  MODEL_LOADING   llamacpp-loading       wall=38.4ms
try 9 frozen   FOREIGN_SERVICE non-2xx-non-model-http wall=44.3ms
```

Current probe: 3/5 MODEL_LOADING live, 2/5 DEAD (probe's curl fired before
the listener existed — a pre-listen race, not a misclassification). Frozen:
2/5 FOREIGN_SERVICE on live loading traffic, 3/5 DEAD. The new verdict is
observable on the real server within one bash-curl spawn latency (~25-40ms)
when it lands inside the window.

### Teardown verified

All 20 launched servers exited rc 0 via SIGTERM process-group kill; final
`pgrep -x llama-server` empty (exit 1) and `ss -ltn` shows none of my ten
ports listening. (During the run one foreign `llama-server` PID 39645 from
sibling seat `KamaR16.ScoutPromiseInventoryLive` was observed and left
untouched; it is also gone now.)

## Observation relevant to L1's receipt

`.ufo/waves/round-16/live/receipt.json` records `loading_observed: false`
with transitions refused@1ms → `/health` 200@22ms. My capture shows the
/v1/models 503 window is ~5-6ms wide (first 503 ≈6.5ms after first accepted
socket, 200 ≈12ms). The lane harness alternates `/health` + `/v1/models` on
fresh connections with `POLL_INTERVAL=0.02` — it plausibly sampled past the
window [INFERENCE: the exact reason its alternation missed is not directly
proven; what IS proven is the window exists and is narrower than its
sampling cadence]. The receipt's `loading_observed:false` is a
sampling-rate artifact, not evidence against the envelope — the claimed
behavior is confirmed live.

## Limitations

- Single small model (260K params, warm page cache after try 0): larger
  models will widen the window; this does not falsify anything.
- The pre-listen DEAD race means a one-shot `check` cannot deterministically
  catch MODEL_LOADING; it is a timing property of the loading window, not a
  probe defect — and it affects both probes equally.
- Stub replay dropped `Connection`/`Content-Length` (stub recomputed them);
  all other headers served verbatim. Probe verdicts depend only on
  status/body/content-type/server string, which were exact.
- `check.py --probe` cannot run an ad-hoc test row (matrix is loaded only
  from its own directory), so the replay used a hand-rolled stub; verdict
  semantics identical to `run_probe` inside check.py.

## Installs

None. Stock python3 + bash + ss only; pacman pause honored, no packages
touched.
