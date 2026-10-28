# L01HostLife — live-tool robustness under concurrent contention (operability)

Wave: round-62 / w1. Lane: kama-shokunin. Seat scope: run the C2-bound live tool
`tools/kama-llamacpp-live.py` twice concurrently in separate scratch dirs, confirm both
pick distinct free unregistered ports and both exit 0, and report the receipts' port lines.
Advisory leaf: findings only, no verdict on C1/C2, no commit, no edit outside this file and
`w1/out/L01HostLife/`.

## Pinned inputs (read from bytes, not assumed)

- Lane tip at run time: `git rev-parse HEAD` = `65d7cad0fce90e34de37527cde22e97b63b118bf`
  (= `master`; matches the C1 measured tip in the spec; frozen base is
  `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3`).
- `tools/kama-llamacpp-live.py` sha256 = `98d2e6bb48a90e60797df0d2bee895eac4a6cdd9859af2dc47b64bdb4a36fbe9`
- `tools/kama-probe.sh` sha256 recorded by every receipt = `4393ab819d6a741646237ef0268cc0836988a9711bab6b06c46cbfea382964f4`
- Model: `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`, size 1185376,
  sha256 = `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`
  (equals the `--model-sha256` in the `live-llamacpp-lifecycle` row of
  `registry/capability-claims-r62.tsv`; receipts report `model_sha256_post` unchanged).
- Server: `llama-server` resolved to `/home/vgpnk/.local/opt/llama-b11755/llama-server`
  (pinned b11755 install).
- Registered consumer ports (`registry/endpoint-consumers.tsv`): 8080 and 34113. Every
  receipt records `port_refusal_set = [8080, 34113]`; none of the four ports below is in it.

Both invocations use the frozen row's exact run shape:
`python3 <lane>/tools/kama-llamacpp-live.py --model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --model-sha256 270cba1...`
plus per-run `TMPDIR` and `--out` into the run's own scratch dir. No `--port` was passed
(port selection is the tool's own `bind(127.0.0.1:0)` path under contention).

## Pass 1 — two plain runs launched in the same instant

Launched as two background subshells in one shell, each with its own scratch dir
(`a/`, `b/`) and its own `TMPDIR`; `wait` on both.

| run | started_utc | ended_utc | port line | outcome | exit |
|---|---|---|---|---|---|
| a | 2026-10-28T12:28:56.771Z | 2026-10-28T12:28:56.951Z | `"port": 40201` | `pass` | 0 |
| b | 2026-10-28T12:28:56.774Z | 2026-10-28T12:28:56.953Z | `"port": 34175` | `pass` | 0 |

Port lines verbatim (receipt, line 486 in both files, plus the argv the child was exec'd with
and the server's own log line captured by teardown):

```
a: "port": 40201                                  argv[--port] = 40201
   0.00.009.239 I srv  llama_server: listening on http://127.0.0.1:40201
b: "port": 34175                                  argv[--port] = 34175
   0.00.009.233 I srv  llama_server: listening on http://127.0.0.1:34175
```

- Ports distinct: **yes** (40201 ≠ 34175); both free at pick time and both outside
  `[8080, 34113]`, i.e. unregistered.
- Overlap: the two lifecycles started 3 ms apart and each ran ~180 ms, so the two
  servers' listen windows overlapped; child pids 989473 / 989487 (distinct).
- Each receipt: `schema kama-llamacpp-live/v4`, `outcome pass`, `port_listener_ownership
  "child"` (proof the listening socket fd belongs to the spawned child, not a foreign
  listener), teardown `returncode 0`, `port_refuses true`, checks
  **11/11 passed** — `health_ready`, `models_alias_id`, `models_owned_by_llamacpp`,
  `metrics_not_enabled`, `props_alias`, `probe_model_ok`, `probe_mismatch`,
  `teardown_graceful`, `teardown_port_closed`, `loading_envelope_graded`, `model_unchanged`.
- stderr empty, stdout empty (receipt went to `--out`).
- Post-run: 40201 and 34175 both `ECONNREFUSED`; no child of mine survives.

## Pass 2 — same tool, both servers held up simultaneously (harder contention proof)

To remove the "did they really coexist?" doubt from a 180 ms lifecycle, the same two
concurrent runs were repeated with the tool's own `--witness-dir` hold (still no `--port`,
still loopback, unregistered). While both held, both ports were queried from outside:

```
readyA {"schema": "kama-live-witness/v1", "port": 44863, "pid": 1070657, "written_utc": "2026-10-28T12:29:26.056Z"}
readyB {"schema": "kama-live-witness/v1", "port": 39299, "pid": 1070658, "written_utc": "2026-10-28T12:29:26.057Z"}
ports distinct: True 44863 39299      pids distinct: True 1070657 1070658
A /health      (200, '{"status":"ok"}')
B /health      (200, '{"status":"ok"}')
A /v1/models   (200, "id":"kama-live-probe","owned_by":"llamacpp", n_ctx 256, n_vocab 512)
B /v1/models   (200, "id":"kama-live-probe","owned_by":"llamacpp", n_ctx 256, n_vocab 512)
A ss -ltnp: LISTEN 127.0.0.1:44863  users:(("llama-server",pid=1070657,fd=3))
B ss -ltnp: LISTEN 127.0.0.1:39299  users:(("llama-server",pid=1070658,fd=3))
```

Both servers were serving at the same instant on distinct ports, each socket owned by its
own child pid. Release touched in both witness dirs → both harnesses tore down:

| run | started_utc | ended_utc | port line | witness waited_ms | checks | exit |
|---|---|---|---|---|---|---|
| c | 2026-10-28T12:29:25.888Z | 2026-10-28T12:29:38.293Z | `"port": 44863` | 12230, released=true, orphaned=false | 11/11 | 0 |
| d | 2026-10-28T12:29:25.890Z | 2026-10-28T12:29:38.296Z | `"port": 39299` | 12233, released=true, orphaned=false | 11/11 | 0 |

Teardown for both: `returncode 0`, `port_refuses true`, `alive_at_teardown_start true`;
server log line `listening on http://127.0.0.1:44863` / `:39299`. Post-run: 44863 and 39299
both `ECONNREFUSED`; `pgrep -af 'llama-server.*(--port (40201|34175|44863|39299))'` finds
nothing.

## Findings (operability)

1. **Contention-safe at the observed width.** Four concurrent-path port picks across two
   passes produced four distinct ports, all free, all outside the refusal set, with no
   retry/`no-free-unregistered-port` and no `port-in-use`; every run exited 0 with 11/11
   checks true. The kernel's `bind(:0)` allocation did not hand the same port to two
   simultaneous picks.
2. **The documented release/rebind race did not fire, and its failure mode is fail-closed
   by design.** `port_pick_note` still reads "port released after bind(:0) and re-bound by
   the server; a sub-second collision race is possible". If a collision ever occurred the
   tool's own `port_listener_ownership` gate would report `foreign`/`unproven` rather than
   grade a foreign listener's answers — but that gate is only exercised here through the
   `child` outcome, so this run is positive evidence of no collision, not proof the race is
   impossible. [INFERENCE: residual risk bounded to that sub-second window.]
3. **No interference with the live fleet surface.** Registered consumer ports 8080/34113
   were in the refusal set on every run and never appeared as picked ports; no registered
   consumer port was contacted (all HTTP contacts went to the four picked ports above).
4. **Hold mode is a usable contention probe.** With `--witness-dir`, two runs coexist for
   >12 s each, serving `/health` 200 and `/v1/models` on the served alias while both
   listeners are up; release is prompt (waited_ms ≈ 12.2 s measured from the moment the
   release file was touched plus poll granularity) and teardown leaves both ports closed.
   Nothing in the hold path changed the receipt schema (`kama-llamacpp-live/v4`, witness
   block `kama-live-witness/v1`).

No blocker. No tool installs or upgrades were needed or attempted (pacman paused host-wide;
nothing required it). No git/jj mutation was run; only read-only `git rev-parse`.

## Durable evidence (this directory's `out/L01HostLife/`)

- `pass1-a-receipt.json` sha256 `215eee416bfa1fb4021a2f311032df8566ad3882016fc8c823bcae430918d71e`
- `pass1-b-receipt.json` sha256 `568fcfb6e2dbdc8cff02fcb11fb9ec8d15f7b8bcff775e01655d92c4b1309721`
- `pass2-c-hold-receipt.json` sha256 `429589aaa5a42f0618305512fe480115b687fea15a2149bee6d3ffe1bd3702dd`
- `pass2-d-hold-receipt.json` sha256 `6ecea5bc0be16d3c8b7a9550158c95ad3bac680d2436050f3375d980a24bad31`
- `pass1-a-exit` / `pass1-b-exit` / `pass2-c-exit` / `pass2-d-exit` — all `0` (sha256
  `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` = "0\n")
- Server logs are not retained separately: the tool unlinks its temp log at teardown; the
  kept log lines live in each receipt's `teardown.log_lines` (quoted above).

Tally: 2/2 concurrent plain runs exit 0 on distinct unregistered ports (40201, 34175); 2/2 concurrent hold runs exit 0 on distinct unregistered ports (44863, 39299); checks 11/11 each; registered-port contacts 0; leftover listeners 0.
