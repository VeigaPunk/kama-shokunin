# ExecDeterminism — C1 signature stability falsifier

Verdict: STABLE — all four confirmed C1 triggers produced the same signature literal
and the same status on all 6 runs each (3x `-t 1`, 3x default threads); no variation
was observed, so the hypothesis "for the fixture, each confirmed trigger yields the
same signature on every run regardless of thread count" was NOT falsified.

Seat: KamaR26.ExecDeterminism (leaf executor). Port block 47690-47693 (free at start,
`ss -ltn` showed nothing bound; re-checked before each launch via TCP connect test).
One child at a time; every launch wrapped in `timeout 45`; every child killed and its
port confirmed closed before the next launch (`port_closed: true` on all 24 rows).
No servers of mine remain (`pgrep -af llama-server` after the run shows only other
seats' processes on ports 47604/47612/47618/47624/47646, all outside my block).
No tools installed this wave.

Fixture used (byte-identical pins): `~/.local/bin/llama-server` sha256
b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 (build 11755, commit
704366d); model `~/.cache/kama-shokunin/models/stories260K.gguf` sha256
270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d. Thread counts
confirmed in logs: `-t 1` -> `n_threads = 1`; default -> `n_threads = 16`.

## Result table (trigger x run -> status, literal present)

HTTP triggers: status = HTTP status of the registered request; literal located in the
response body. Startup triggers: status = exit code; literal located in the combined
stdout+stderr log. All 24 rows: literal present on every run.

| Trigger | Run | `-t 1` status | `-t 1` literal | default status | default literal |
|---|---|---|---|---|---|
| GET /metrics (no `--metrics`) | 1 | 501 | yes | 501 | yes |
| GET /metrics (no `--metrics`) | 2 | 501 | yes | 501 | yes |
| GET /metrics (no `--metrics`) | 3 | 501 | yes | 501 | yes |
| `--no-slots` GET /slots | 1 | 501 | yes | 501 | yes |
| `--no-slots` GET /slots | 2 | 501 | yes | 501 | yes |
| `--no-slots` GET /slots | 3 | 501 | yes | 501 | yes |
| missing model `-m /nonexistent/kama-r26/missing.gguf` | 1 | exit 1 | yes | exit 1 | yes |
| missing model | 2 | exit 1 | yes | exit 1 | yes |
| missing model | 3 | exit 1 | yes | exit 1 | yes |
| unknown flag `--kama-r26-bogus` | 1 | exit 1 | yes | exit 1 | yes |
| unknown flag | 2 | exit 1 | yes | exit 1 | yes |
| unknown flag | 3 | exit 1 | yes | exit 1 | yes |

Summary: for every trigger and every run, status identical and the chosen literal
present. `litter... literal` is `true` on all 24 rows (results.json).

## Literals and verbatim source lines (pinned snapshot, read this round)

- `This server does not support metrics endpoint` — server-context.cpp:5304,
  `res->error(format_error_response("This server does not support metrics endpoint. Start it with `--metrics`", ERROR_TYPE_NOT_SUPPORTED));`
- `This server does not support slots endpoint` — server-context.cpp:5366,
  `res->error(format_error_response("This server does not support slots endpoint. Start it with `--slots`", ERROR_TYPE_NOT_SUPPORTED));`
- `failed to load model '` — common.cpp:1423, `COM_ERR("failed to load model '%s'\n", params.model.path.c_str());`
- `error: invalid argument: ` — arg.cpp:830,
  `throw std::invalid_argument(string_format("error: invalid argument: %s", arg.c_str()));`

All four literals: absent from the counter's healthy-baseline surface (the same server
with the same model answered /health, /v1/models, /props, /slots, /completion,
/v1/chat/completions, /tokenize with 200s — see counter lines 84-93), and absent from
`llama-server --help` (exit 0, 60469 bytes) and `--version` (exit 0, 90 bytes):
`grep -c -F` returned 0 for every literal in both outputs, `grep_exit=1` (no match).

## Representative raw logs (all 24 under out/ExecDeterminism/logs/)

- `metrics_off_t1_1.log` / `metrics_off_def_3.log`: still n_threads = 1 / 16; the GET
  /metrics response body each time:
  `{"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}}`
- `slots_off_t1_2.log` / `slots_off_def_2.log`: GET /slots body each time:
  `{"error":{"code":501,"message":"This server does not support slots endpoint. Start it with `--slots`","type":"not_supported_error"}}`
- `missing_model_t1_3.log` / `missing_model_def_1.log`: exit 1, log ends
  `E srv llama_server: exiting due to model loading error` and contains
  `E srv load_model: failed to load model, '/nonexistent/kama-r26/missing.gguf'`
- `unknown_flag_t1_1.log` / `unknown_flag_def_3.log`: entire log is exactly
  `error: invalid argument: --kama-r26-bogus` (42 bytes), exit 1.

## Notes for the L1

- The HTTP triggers' `exit` codes are all 1, but that is OUR teardown SIGTERM (the
  logs show `Received second interrupt, terminating immediately.` after the response
  was captured); the meaningful stable status for the http channel is HTTP 501. Do
  not read these exit codes as a trigger property.
- Startup triggers exited non-zero within 30 s on every run (well within, ~0.03 s
  for unknown flag, ~0.03 s for missing model after load attempt).
- `--no-slots` is a valid flag in this build (arg.cpp:3648 `{"--no-slots"}`).
- No variation in signature text was observed across thread counts; per the acceptance
  criterion the hypothesis survives this falsifier.

Files written (all paths relative to /home/vgpnk/Projects/shokunin/kama-shokunin):
- `.ufo/waves/round-26/w1-build/advice/ExecDeterminism.md` (this report)
- `.ufo/waves/round-26/w1-build/out/ExecDeterminism/results.json` (24 rows, machine-readable)
- `.ufo/waves/round-26/w1-build/out/ExecDeterminism/logs/*.log` (24 raw logs)
Driver kept in scratch: `/fast/scratch/hyaku/kama-r26/ExecDeterminism/run.py`
(re-runnable; contains the full argv for every run).
