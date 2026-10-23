# ExecMetricsOff — round-26 wave-1 build findings

**Verdict: one confirmed candidate signature (metrics endpoint queried on a server started without `--metrics`); reproduced live twice on the lane fixture; counts 1/1 in the frozen counter scratch check.**

## Fault and live reproduction (2 runs)

Launch: `timeout 120 ~/.local/bin/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 47600 -t 2` (port 47601 for run 2; `-t 2`, logs under `/fast/scratch/hyaku/kama-r26/ExecMetricsOff/`). Waited for `/health` 200 (1 s), then `GET /metrics`.

Run 1 (port 47600) and run 2 (port 47601) both returned the identical error:

```
HTTP/1.1 501 Not Implemented
Server: llama.cpp
Content-Type: application/json; charset=utf-8
Content-Length: 136

{"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}}
```

`curl` exit 0 both times. The server log (launch1.log/launch2.log) contains no error line for this path (the handler returns `res->error(...)` early; the 501 body is the channel). A `POST /metrics` variant returns 404 `File Not Found` (route registered GET-only at `server.cpp:280`).

## Signature

`This server does not support metrics endpoint. Start it with `--metrics`` (72-byte signature; HTTP body Content-Length 136) — verbatim in `server-context.cpp:5304`:

```cpp
res->error(format_error_response("This server does not support metrics endpoint. Start it with `--metrics`", ERROR_TYPE_NOT_SUPPORTED));
```

- Source file: `server-context.cpp` (basename in `.ufo/waves/round-26/sources/llama.cpp-704366d/`), sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` = pinned value.

- Fresh fetch opened 2026-10-23: `https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5304`. Located quote (line 5304, 11 words): “This server does not support metrics endpoint. Start it with `--metrics`”.
- Fetched raw bytes and committed snapshot compare equal (`cmp` exit 0); both sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`.
- Error type `ERROR_TYPE_NOT_SUPPORTED` → code 501 at `server-common.cpp:115-118`.
- Clause (f) checks: signature absent (0 hits) from the healthy baseline run (7 baseline requests on port 47602 + `baseline.log`), absent from `llama-server --help` (the help text says only `--metrics ... (default: disabled)`) and from `--version`; also absent whitespace-squashed.
- Clause (b) check: `git -C <lane> grep -F -q -e '<sig>' 1560e4d8 -- SKILL.md corpus` exited 1 (absent at base).

## Registry entry

`candidates.json` (`.ufo/waves/round-26/w1-build/out/ExecMetricsOff/candidates.json`): one entry, id `TBD`, channel `http`, model `fixture`, `args` [], `occupy_port` false, request `GET /metrics`, source row `TBD`, file `server-context.cpp`. The L1 must assign the final id and S### row (scratch check used `EMO1` / `S901`).

## Frozen counter scratch check

Extract of frozen tip `a23c0e042114016a909eb15173aa6df74b5b7eb0` at `/fast/scratch/hyaku/kama-r26/ExecMetricsOff/counter-check/` (via `git archive` from the lane repo), with placeholder SKILL.md section `## Round-26 live error signatures`, SOURCES row `S901` (names `server-context.cpp` and commit `704366d`), and registry row `EMO1`.

Command (under `flock /fast/scratch/hyaku/kama-r26/counter.lock`):
```
timeout 900 python3 .ufo/waves/round-26/count-c1.py --json --out receipt.json
```
Exit 0. Output: `registered 1 counted 1 target 12 met False not-counted []`. All 12 checks true for the entry (`a_skill_row`, `b_long`, `b_new_at_base`, `c_source_row`, `d_source_pinned`, `d_in_source`, `e_error_shown` (501), `e_signature_seen`, `e_not_echoed`, `f_absent_from_baseline`, `g_distinct`, `id_unique`). Receipt saved to `out/ExecMetricsOff/counter-receipt.json`; combined counter stdout plus summary saved to `counter-output.txt`.

## Files written (all under lane `.ufo/waves/round-26/w1-build/out/ExecMetricsOff/`)

- `candidates.json`
- `RUNS.txt`
- `run1-metrics.txt`, `run2-metrics.txt`, `run2-post-metrics.txt` (raw response bodies with status)
- `launch1.log`, `launch2.log` (server logs)
- `baseline.log`, `baseline-responses.txt` (healthy baseline)
- `counter-receipt.json` (scratch counter receipt)
- `counter-output.txt` (scratch counter stdout plus summary)

## Risks / notes

- Cross-row risk: clause (g) rejects a row if an earlier counted signature appears in its channel text. This specific body contains `This server does not support `, so any earlier counted generic-prefix signature can block this row; the scratch check had no earlier counted row. The L1 must account for this when ordering/integrating family entries.
- The 72-byte signature itself is verbatim in source and response; it does not avoid clause-(g)'s channel-text overlap with a generic family-prefix signature.
- `--metrics` handler captured at `server-context.cpp:5301-5306`; `ERROR_TYPE_NOT_SUPPORTED` maps to code 501 at `server-common.cpp:115-118`. The source confirms this path; the live 501 response was observed directly.
- No llama-server processes of mine remain (`pgrep -af 'llama-server.*4760[0-3]'` → rc 1); ports 47600-47603 closed and verified with `ss -ltn`.
