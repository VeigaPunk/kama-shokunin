VERDICT: confirm — the frozen v2 tool falsely exits 1 on real b11755 zero-503 runs: 15/60 under pinned 32× CPU oversubscription.

# ProbeZeroLoading — before-evidence for R4

Axes: operability and calibration.

## Setup and frozen identity

Ran the requested frozen `/v1/models` loading-window experiment, then bounded supplementary arms to produce and instrument the rare zero-observation state. The lane tip was `e75cf680b53484a61709ee1b2787d8dbc6419f74`. I cloned it to `/tmp/kama-r18-ProbeZeroLoading`, created `seat/ProbeZeroLoading` there, and ran lifecycle tests only in that clone. `cmp` confirmed the clone tool, probe and receipt gate equal the frozen copies; the tool SHA-256 was `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`, probe `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`, gate `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5`. The actual server resolved to `/home/vgpnk/.local/opt/llama-b11755/llama-server`, SHA-256 `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`; the model SHA-256 matched the requested `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.

Host: 32 CPUs (`nproc`), Python 3.14.8, `stress-ng` 0.22.01 (already installed). No tools were installed or updated. The frozen tool's `--help` succeeded (exit 0); it reports schema `kama-llamacpp-live/v2` and the specified `--server`, `--model`, `--model-sha256`, `--out` options.

## Requested 20 idle + 20 loaded runs

All lifecycle command invocations used this exact command shape from cwd `/tmp/kama-r18-ProbeZeroLoading` (the `{label}` substitution is shown in the tables):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/kama-llamacpp-live.py \
  --server /home/vgpnk/.local/bin/llama-server \
  --model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf \
  --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
  --out /tmp/kama-r18-ProbeZeroLoading-runs/{label}.json
```

The command's stdout and stderr were empty for every run because `--out` wrote the receipt. The exit code is listed for every run. Each receipt was gated with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/llamacpp-live/check-receipt.py \
  /tmp/kama-r18-ProbeZeroLoading-runs/{label}.json
```

For the requested arms, every gate invocation exited 0, wrote exactly `VALID /tmp/kama-r18-ProbeZeroLoading-runs/{label}.json` to stdout, and wrote nothing to stderr.

### Idle arm: 20/20, no stressor

Window 2026-10-20 21:03:29.307Z–21:03:34.063Z; load average at start/end `2.15 3.71 10.22` / `2.38 3.73 10.19`.

`refused` is the number of `/v1/models` requests returning `ConnectionRefusedError` (collapsed transition's `repeats + 1`); `t` columns are receipt transition `t_ms`; `503` is the response count summed from `loading_503_bodies`; exits are `tool/gate`.

| Run | refused | last refused t | first 503 t | 503 count | last 503 t | first models 200 t | tool/gate |
|---|---:|---:|---:|---:|---:|---:|---:|
| idle-01 | 213 | 7 | 7 | 45 | 12 | 12 | 0/0 |
| idle-02 | 108 | 6 | 7 | 48 | 11 | 11 | 0/0 |
| idle-03 | 207 | 6 | 7 | 45 | 12 | 12 | 0/0 |
| idle-04 | 201 | 6 | 6 | 44 | 11 | 12 | 0/0 |
| idle-05 | 218 | 6 | 7 | 46 | 12 | 12 | 0/0 |
| idle-06 | 210 | 6 | 7 | 45 | 11 | 12 | 0/0 |
| idle-07 | 218 | 6 | 7 | 48 | 12 | 12 | 0/0 |
| idle-08 | 211 | 6 | 7 | 41 | 11 | 12 | 0/0 |
| idle-09 | 216 | 6 | 7 | 46 | 12 | 12 | 0/0 |
| idle-10 | 216 | 6 | 7 | 45 | 12 | 12 | 0/0 |
| idle-11 | 205 | 6 | 7 | 45 | 12 | 12 | 0/0 |
| idle-12 | 226 | 6 | 7 | 30 | 12 | 12 | 0/0 |
| idle-13 | 218 | 6 | 7 | 42 | 12 | 12 | 0/0 |
| idle-14 | 203 | 6 | 7 | 45 | 12 | 12 | 0/0 |
| idle-15 | 193 | 6 | 7 | 34 | 12 | 12 | 0/0 |
| idle-16 | 216 | 6 | 7 | 45 | 12 | 12 | 0/0 |
| idle-17 | 213 | 6 | 7 | 27 | 11 | 11 | 0/0 |
| idle-18 | 232 | 7 | 7 | 29 | 12 | 13 | 0/0 |
| idle-19 | 223 | 6 | 7 | 45 | 12 | 12 | 0/0 |
| idle-20 | 211 | 6 | 7 | 31 | 11 | 12 | 0/0 |

503-count sequence: `45, 48, 45, 44, 46, 45, 48, 41, 46, 45, 45, 30, 42, 45, 34, 45, 27, 29, 45, 31`. Min/median/max/mean `27/45/48/41.30`. Zero: **0/20**. All 20 tool receipts had all 11 checks true and tool/gate exit 0.

### CPU-load arm: 20/20, `stress-ng --cpu 32`

Command: `stress-ng --cpu 32 --timeout 600s --metrics-brief` (one server at a time; stressor in its own process group). Stress started `2026-10-20T21:08:19.924Z`, runs began `21:08:24.924Z`, assigned 20 ended `21:08:38.111Z`, stress stopped `21:09:36.398Z`; stress-ng exit 0, 32 workers, no remaining process-group members. Load average at ramp / assigned-run end: `7.35 4.34 8.60` / `14.06 5.98 9.07`.

| Run | refused | last refused t | first 503 t | 503 count | last 503 t | first models 200 t | tool/gate |
|---|---:|---:|---:|---:|---:|---:|---:|
| load-01 | 213 | 17 | 19 | 5 | 27 | 29 | 0/0 |
| load-02 | 121 | 12 | 15 | 17 | 29 | 30 | 0/0 |
| load-03 | 213 | 17 | 19 | 21 | 30 | 31 | 0/0 |
| load-04 | 215 | 19 | 21 | 16 | 32 | 34 | 0/0 |
| load-05 | 203 | 16 | 23 | 16 | 35 | 35 | 0/0 |
| load-06 | 311 | 15 | 21 | 20 | 33 | 33 | 0/0 |
| load-07 | 128 | 15 | 17 | 29 | 31 | 31 | 0/0 |
| load-08 | 172 | 18 | 21 | 16 | 36 | 37 | 0/0 |
| load-09 | 375 | 17 | 20 | 5 | 29 | 31 | 0/0 |
| load-10 | 203 | 18 | 20 | 8 | 34 | 34 | 0/0 |
| load-11 | 186 | 17 | 22 | 20 | 34 | 37 | 0/0 |
| load-12 | 211 | 15 | 23 | 19 | 35 | 35 | 0/0 |
| load-13 | 190 | 16 | 21 | 6 | 31 | 31 | 0/0 |
| load-14 | 237 | 18 | 21 | 16 | 32 | 33 | 0/0 |
| load-15 | 182 | 17 | 21 | 10 | 31 | 31 | 0/0 |
| load-16 | 191 | 18 | 20 | 28 | 35 | 35 | 0/0 |
| load-17 | 183 | 16 | 20 | 14 | 31 | 33 | 0/0 |
| load-18 | 189 | 15 | 19 | 19 | 31 | 31 | 0/0 |
| load-19 | 192 | 15 | 20 | 14 | 32 | 35 | 0/0 |
| load-20 | 199 | 16 | 20 | 14 | 33 | 33 | 0/0 |

503-count sequence: `5, 17, 21, 16, 16, 20, 29, 16, 5, 8, 20, 19, 6, 16, 10, 28, 14, 19, 14, 14`. Min/median/max/mean `5/16/29/15.65`. Zero: **0/20**. All 20 tool receipts had all 11 checks true and tool/gate exit 0. The requested 1×-CPU-count stress arm did not reproduce zero observations.

## Poll interval and first-poll latency

The frozen transitions are coalesced: repeated identical rows increment `repeats` and overwrite `t_ms` with the last response time. Therefore a receipt's first `status=None` row `t_ms` is the *last* refused-poll time, not the first-poll latency; the table above preserves that distinction. `loading_503.t_ms` is the first observed 503; the coalesced `/v1/models` 503 transition `t_ms` is the last one. The transitions alone do not retain per-request timestamps.

Receipt-derived timing for the 20 idle runs: refused requests `108–232` (median `213`) collapsed into the first row at `6–7ms`; first 503 was at `6–7ms`, the last 503 row at `11–12ms`, first 200 at `11–13ms`. The observed 503 window was `4–5ms`; across runs, `(last 503 t - first 503 t)/(503 count - 1)` gives a rough interval of `0.085–0.179ms` (median `0.114ms`). For loaded runs: refused requests `121–375` (median `195.5`) ended at `12–19ms`; first 503 `15–23ms`, last 503 `27–36ms`, first 200 `29–37ms`; observed window `8–15ms`; rough 503 interval `0.50–2.25ms` (median `0.823ms`). These are receipt-granularity estimates, not per-request intervals.

To resolve first-poll latency and cadence, a scratch-only wrapper around the unchanged frozen tool logged monotonic start/end around each `_KeepAlive.get` and the readiness-loop start (two added monotonic calls per poll). Five idle and five 32-worker-load instrumented runs were supplementary, not included in the requested 20+20:

- Instrumented idle: first poll began `0.014–0.017ms` after readiness-loop t0 (median `0.015ms`), first refused GET completed `0.907–1.048ms` (median `0.971ms`). Median per-run interval between refused poll starts was `0.0222–0.0227ms`. First successful response was 503, starting `5.622–5.986ms` and completing `6.336–6.694ms`. There were `5–13` 503s in these five runs.
- Instrumented 32-worker load: first poll began `0.019–0.024ms`, completed `1.351–1.516ms`; refused poll-start intervals had per-run medians `0.0364–0.0376ms`. First successful response was 503, starting `14.696–20.221ms`, completing `16.604–21.028ms`. Largest consecutive poll-start gap was `6.215–10.774ms`; first-503-to-next-poll delay was `5.738–8.818ms`. There were `6–13` 503s in these five runs.

## Zero-503 reproductions: higher, localized oversubscription

Because the requested `stress-ng --cpu 32` arm produced no zero run, I performed a separate, clearly distinguished scheduler-contention arm. The live-tool parent and its child server were both affined to CPUs `28-31`; `stress-ng` ran 128 CPU workers on the same four CPUs (`taskset -c 28-31 stress-ng --cpu 128 --timeout 1500s --metrics-brief`). It was one server at a time; stress and server were stopped/reaped before finishing. Stress window 1: `21:11:50.236Z–21:19:56.424Z`, 60 ordinary invocations; 129 process-group members observed including stress-ng parent, all had affinity `28-31`, stress exit 0, no group leftovers. Load average at ramp / run end was `15.67` / `144.94` (1-minute average; other host work contributes). This is not the requested 1× load arm and should not be pooled with it.

503-count distribution across those 60 real-server runs: `0:15, 1:27, 2:13, 3:3, 4:1, 5:1`. Thus **15/60 (25%)** had zero `/v1/models` 503s. Exits were `45× tool 0 / gate 0`, `15× tool 1 / gate 1`. Every zero run had `setup_error=null`, `internal_fault=null`, listener ownership `child`, healthy `/v1/models` 200 and `/health` 200, and exactly one failed check (`loading_envelope_graded`) among 11; all other ten checks, including graceful teardown and closed port, passed. Every corresponding gate invocation reported INVALID with exit 1. The exact zero-run transition receipts:

| Run | refused row (`t_ms`, polls) | models 200 `t_ms` | health 200 `t_ms` | Port |
|---|---:|---:|---:|---:|
| pin-08 | 194, 319 | 318 | 356 | 37109 |
| pin-33 | 229, 296 | 391 | 435 | 45837 |
| pin-35 | 249, 258 | 337 | 391 | 44727 |
| pin-36 | 215, 269 | 386 | 436 | 34759 |
| pin-44 | 207, 251 | 354 | 418 | 33119 |
| pin-47 | 177, 270 | 302 | 321 | 35859 |
| pin-49 | 168, 281 | 279 | 284 | 33765 |
| pin-50 | 204, 269 | 323 | 339 | 34905 |
| pin-51 | 160, 253 | 274 | 301 | 32913 |
| pin-52 | 176, 271 | 312 | 346 | 34349 |
| pin-53 | 251, 257 | 350 | 385 | 40641 |
| pin-54 | 247, 267 | 340 | 393 | 44513 |
| pin-57 | 243, 274 | 389 | 443 | 43817 |
| pin-59 | 221, 289 | 323 | 356 | 33291 |
| pin-60 | 289, 275 | 382 | 401 | 46315 |

For every row above, `loading_503=null`, `loading_503_bodies=[]`, `loading_observed=false`, and the `loading_envelope_graded` observation was `all_exact:null`, `exact:null`, `total_503_responses:0`. Example raw command (same frozen lifecycle command template, `--out /tmp/kama-r18-ProbeZeroLoading-runs/pin-08.json`, prefixed by `taskset -c 28-31`): tool stdout empty, stderr empty, exit 1. Gate command: `PYTHONDONTWRITEBYTECODE=1 python3 tests/llamacpp-live/check-receipt.py /tmp/kama-r18-ProbeZeroLoading-runs/pin-08.json`; exact stdout:

```text
INVALID /tmp/kama-r18-ProbeZeroLoading-runs/pin-08.json: 3 problem(s)
  - check 'loading_envelope_graded': passed is false
  - loading_envelope_graded: no loading_503 body stored, nothing graded
  - loading_envelope_graded: loading_503_bodies missing or empty in a v2 receipt
```

Gate stderr empty, exit 1. The other 14 zero-run receipts had the same three gate findings and exit 1, with their respective receipt paths. All 60 tool runs had empty stdout/stderr (`--out`); the exit distribution above is the per-run raw exit record.

A further 50 instrumented pinned runs used the same 4-CPU/128-worker arrangement (window `21:22:08.811Z–21:27:51.811Z`, stress exit 0, no process-group leftovers). They produced 9 additional zero-503 runs: `pini-01`, `pini-07`, `pini-08`, `pini-09`, `pini-15`, `pini-36`, `pini-43`, `pini-44`, `pini-49`; all tool/gate exit `1/1`, all with loading-envelope as sole failed check. Per-poll instrumentation showed the first successful GET was 200, not 503. For each zero run below, fields are last refused response end / first 200 GET start / first 200 GET end (ms from readiness-loop t0): `pini-01 168.147/221.982/311.337`; `pini-07 176.263/176.265/290.508`; `pini-08 178.865/178.867/272.643`; `pini-09 129.830/153.992/196.253`; `pini-15 182.235/204.973/269.948`; `pini-36 177.103/177.105/334.824`; `pini-43 206.646/206.648/373.080`; `pini-44 176.896/208.918/329.884`; `pini-49 192.641/192.643/360.401`. Tool/gate exits across the 50 were `41×0/0`, `9×1/1`. First poll began `0.019–0.032ms`; it completed `1.042–1.396ms`. The per-run medians for refused poll-start cadence were `0.0235–0.0265ms`; maximum gap between poll starts across runs ranged `44.286–168.808ms` (median of per-run maxima `105.939ms`). The requests that returned the first 200 in the zero runs lasted `42.261–167.758ms`; this is observed timing, not proof of the server-side instant the readiness flag flipped.

## Additional sample and interpretation

To check that zero observations were not merely one accidental run, I also did 80 more idle runs and 80 more runs under the 32-worker stressor, plus five instrumented runs in each condition. Idle extension: 0/80 zeros, counts min/median/max/mean `5/19.5/39/19.49`, all tool/gate `0/0`. Loaded extension: 0/80 zeros, counts `1/12/32/12.35`, all tool/gate `0/0`. The five instrumented idle and five instrumented loaded runs also had no zero. Together, the requested arms plus their extensions gave 0/100 idle and 0/100 at 1× CPU-count load; this does not disprove the R4 failure because the separately stressed real runs reproduce it directly. The pinned experiment has sample/time-dependent scheduler conditions and is not a universal zero rate.

Observed cause boundary: the v2 receipt faithfully records that it saw no 503, then reports a failed loading-envelope check and exits 1; the gate rejects the same unobserved condition. The real single-model server's underlying ready-state transition is not timestamped by the receipt, so these observations establish the false-failure classification for a healthy lifecycle, not the exact scheduling mechanism that caused each 503 to be missed.

## Limitations, cleanup, installs

- One host, one b11755 server build, one warm-cache 1.17 MB fixture model. Idle/1× stress and 4-CPU pinned 32× stress are different regimes; do not compare 503 counts across them as if only one variable changed. Other host activity and load average varied.
- Back-to-back invocations accumulate TIME_WAIT sockets. A direct D1 `port_owned_by` timing was about `1.3ms` at 1,472 `/proc/net/tcp` rows plus 152 `/proc/net/tcp6` rows; the table reached 3,696 IPv4 rows plus 137 IPv6 rows during an earlier run, but scan time was not measured at that high-water count. This occurs after a transition row is appended and before the first 503 body is saved, so it cannot erase that already-recorded first 503, but it consumes remaining observation-window cadence. Treat per-run 503 counts as sensitive to host TCP table size. (Source-line check: frozen tool `:546-572`, transition row appended at `:545` before the ownership scan/body capture.)
- `stress-ng --cpu 32` was used for the assigned loaded arm; the separate reproduction used 128 workers pinned to 4 CPUs. No hard confidence interval is claimed for the 15/60 rate; runs are sequential, not independent of host state.
- The scratch clone, receipts, timing wrapper and stress logs under `/tmp/kama-r18-ProbeZeroLoading*` were removed. Every recorded receipt had its child dead and port not listening after teardown. Final process check: no `llama-server` process and no `stress-ng` process.
- Final `ss -ltnp` check (remaining listeners are unrelated host services; no experiment listener):

```text
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      4096       127.0.0.1:631        0.0.0.0:*   
LISTEN 0      4096      127.0.0.54:53         0.0.0.0:*   
LISTEN 0      512        127.0.0.1:36381      0.0.0.0:*    users:(("omp",pid=3092,fd=98))
LISTEN 0      4096       127.0.0.1:40443      0.0.0.0:*   
LISTEN 0      10         127.0.0.1:39017      0.0.0.0:*    users:(("chromium",pid=2082972,fd=77))
LISTEN 0      4096      172.17.0.1:53         0.0.0.0:*   
LISTEN 0      5          127.0.0.1:8796       0.0.0.0:*    users:(("python3",pid=1511,fd=3))
LISTEN 0      5          127.0.0.1:8795       0.0.0.0:*    users:(("python3",pid=1512,fd=3))
LISTEN 0      512        127.0.0.1:8793       0.0.0.0:*    users:(("python3",pid=1516,fd=3))
LISTEN 0      512        127.0.0.1:8791       0.0.0.0:*    users:(("python3",pid=1515,fd=3))
LISTEN 0      5          127.0.0.1:8790       0.0.0.0:*    users:(("python3",pid=1517,fd=3))
LISTEN 0      5          127.0.0.1:8789       0.0.0.0:*    users:(("python3",pid=1513,fd=3))
LISTEN 0      5          127.0.0.1:8788       0.0.0.0:*    users:(("python",pid=1518,fd=3))
LISTEN 0      256        127.0.0.1:8787      0.0.0.0:*    users:(("python3",pid=1514,fd=3))
LISTEN 0      4096   127.0.0.53%lo:53         0.0.0.0:*   
LISTEN 0      4096         0.0.0.0:5355       0.0.0.0:*   
LISTEN 0      4096           [::1]:631           [::]:*   
LISTEN 0      4096            [::]:5355          [::]:*   
```
