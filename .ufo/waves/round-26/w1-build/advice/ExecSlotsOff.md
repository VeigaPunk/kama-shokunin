# ExecSlotsOff — C1 wave-1 falsifier advice

Verdict: one confirmed C1 signature (slots endpoint disabled via `--no-slots`, GET /slots -> 501); frozen counter on a scratch extract prints `registered 1 counted 1` with all checks a-g true.

## Claim served
C1 (data: candidate signature rows). Fault family: slots endpoint queried on a server started with `--no-slots` (GET /slots).

## Port block
47604-47607 (checked free with `ss -ltn` before each launch; confirmed closed after each run). Only 127.0.0.1. `-t 2` passed, `timeout 90` wrapper, one server at a time. No server left running at the end (`pgrep -af llama-server` shows no process of mine; my leftover pid 3492896 on 47606 was killed and port confirmed closed).

## Fixture
- Server: `~/.local/bin/llama-server` — `version: 0.7.0-dev (build 11755, commit 704366d76)`.
- Model: `~/.cache/kama-shokunin/models/stories260K.gguf`, sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (matches count-c1.py MODEL_SHA256).

## Reproduction (twice)
Run on 47604 and 47605: launch with `-m <fixture> --host 127.0.0.1 --port <P> --no-slots -t 2`, wait for /health, then `curl -s -w '\nHTTP_STATUS=%{http_code}\n' http://127.0.0.1:<P>/slots`.

Both runs, identical output:
```
{"error":{"code":501,"message":"This server does not support slots endpoint. Start it with `--slots`","type":"not_supported_error"}}
HTTP_STATUS=501
```
curl exit 0 in both. Server killed after each run; ports 47604/47605 confirmed closed.

Raw outputs saved under out/ExecSlotsOff/: `slots_body_47604.txt`, `slots_body_47605.txt` (bodies with HTTP_STATUS), `run_47604.log`, `run_47605.log` (server logs), `healthy_slots.txt` + `baseline_healthy.log` (healthy baseline, HTTP 200).

## Chosen signature
```
This server does not support slots endpoint. Start it with `--slots`
```
- Length: 66 bytes (>= 20).
- Verbatim in pinned source: `server-context.cpp:5366` (inside `format_error_response`):
  `5366:            res->error(format_error_response("This server does not support slots endpoint. Start it with `--slots`", ERROR_TYPE_NOT_SUPPORTED));`
  Source file served from the lane-committed pinned snapshot `.ufo/waves/round-26/sources/llama.cpp-704366d/server-context.cpp` (pinned commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad; sha256 pinned in count-c1.py SOURCE_SHA256 as `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4`). Located quote at line 5366, 24 words. Access date 2026-10-23.
- Absent at base 1560e4d8: `git -C kama-shokunin grep -F -q -e 'This server does not support slots endpoint. Start it with `--slots`' 1560e4d8 -- SKILL.md corpus` -> exit 1 (absent).
- Absent from healthy baseline: healthy `GET /slots` returns 200 with slot JSON (no message); `grep -c -F 'does not support slots endpoint' out/ExecSlotsOff/baseline_healthy.log` -> 0; also absent from the healthy response body.
- Not echoed from request: request is GET /slots with empty body.
- Not in `--help`/`--version` output (help text for the flag says "expose slots monitoring endpoint (default: enabled)").

## Trigger (registry entry)
```
channel: http, args: ["--no-slots"], model: fixture, occupy_port: false,
request: {method: GET, path: /slots, headers: {}, body: ""},
source: {row: <S### assigned by L1>, file: "server-context.cpp"}
```
`--no-slots` is not in the counter's FORBIDDEN_ARGS. The handler gate is at `server-context.cpp:5365-5367` (`if (!params.endpoint_slots) { ... }`), flag set by `arg.cpp:3646-3653` (`--no-slots`).

## Frozen-counter check (scratch extract only)
Scratch extract at `/fast/scratch/hyaku/kama-r26/ExecSlotsOff/extract` created via
`git -C kama-shokunin archive a23c0e042114016a909eb15173aa6df74b5b7eb0 | tar -x -C <extract>`;
sources copied in; scratch-only placeholder rows added (SKILL.md section heading `## Round-26 live error signatures` + row `| KamaR26-SlotsOff | <signature> | S901 | ...`, corpus/SOURCES.md row `| S901 | server-context.cpp | 704366d | ...`, registry `registry/error-signatures-r26.json` with id KamaR26-SlotsOff and source.row S901). Neither the SKILL row, the SOURCES row nor the registry exist in the lane; they are scratch-only.

Run (host-wide flock, inside the scratch extract):
```
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 \
  python3 <extract>/.ufo/waves/round-26/count-c1.py --lane <extract> \
  --out /fast/scratch/hyaku/kama-r26/ExecSlotsOff/counter-receipt.json
```
Output: `registered 1 counted 1 target 12 met False not-counted []` (exit 0).
Receipt: checks a-g all true; observed status 501; channel_sha256 `9c08c13405b685a8cc7a7f105ed0710a0ace945566df1940aa7c1ac057561b23`; excerpt is the JSON body with the message. Receipt copied to out/ExecSlotsOff/counter-receipt-scratch.json.

## Files written
- `.ufo/waves/round-26/w1-build/out/ExecSlotsOff/candidates.json` (1 entry, id/source.row "TBD" pending L1 assignment)
- `.ufo/waves/round-26/w1-build/out/ExecSlotsOff/RUNS.txt`
- `.ufo/waves/round-26/w1-build/out/ExecSlotsOff/slots_body_47604.txt`, `slots_body_47605.txt`, `healthy_slots.txt`, `run_47604.log`, `run_47605.log`, `baseline_healthy.log`, `counter-receipt-scratch.json`
- This advice report.

## Risks / notes
- Clause (g) collision risk: the message shares the prefix `This server does not support ` with sibling fault families (metrics /embeddings /reranking /props etc. — all `server-context.cpp` `format_error_response` messages). If a sibling publishes a signature that is a prefix or superstring of this one (e.g. `This server does not support ` or the full family prefix), clause (g) may invalidate this row. This seat recommends the full message `This server does not support slots endpoint. Start it with \`--slots\`` as the registered signature: it is the smallest verbatim chunk that uniquely identifies the slots family (the tail `slots endpoint. Start it with \`--slots\`` is not shared by any sibling family), and it is the full format-string constant at server-context.cpp:5366.
- The dominant message in the counter's own baseline is a 200 JSON; the healthy log lacks the message — f passes.
- No tooling installed this round (nothing needed; no pacman, uv, pip or binary changes). No credentials read. No jj commands run. Nothing written outside the lane out-dir, the advice report, and the /fast scratch area.
