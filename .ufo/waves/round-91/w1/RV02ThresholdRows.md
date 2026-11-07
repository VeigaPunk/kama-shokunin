# RV02ThresholdRows — C2 K2 reviewer read (round 91, kama)

## Scope
- Revision read: lane HEAD `3f317ecd211e80929c673e306e3230be287fdf20` (= M2, confirmed by `git rev-parse HEAD`).
- Rows: the 14 rows of `SKILL.md` §Serving timeout and limit thresholds (T01-T14), plus the section intro and
  `corpus/knowledge/serving-thresholds.md` statements.
- Pinned sources fetched live this seat and digest-checked against SOURCES rows S593-S595:
  - llama.cpp `common/common.h` @ b12177: `c3010a3c662a14556adb651b79bff00089564fde6b5e336959403e3db34e6073` (= S593)
  - Ollama `envconfig/config.go` @ v0.40.11: `0b0ea669b31cfe2b54313427257326a2b7a909bbc7bf8a671035efc446fb1895` (= S594)
  - vLLM `vllm/envs.py` @ v0.32.0: `e963af06cf6c775fe285147e0d811ea5b4d679e5cbd6958980ec2a0d1da70694` (= S595)
- Usage sites read: llama.cpp b12177 `common/arg.cpp`, `tools/server/server.cpp`, `server-context.cpp`,
  `server-http.cpp`, `server-models-sched.cpp`, vendored `httplib.h`; Ollama v0.40.11 tarball (`server/sched.go`,
  `server/routes.go`, `llm/llama_server.go`); vLLM v0.32.0 tarball (`v1/engine/core_client.py`,
  `entrypoints/launchers/api_server/entry.py`, `examples/.../disagg_epd_proxy.py`); pinned binary `--help`.
- No live endpoint touched (no request to 127.0.0.1:1234 or any port). No timing measured; host load at the
  reads was 1-min load average 38.21 (`uptime`, 20:28), so no timing claim is made here.
- Tooling: nothing installed or upgraded.

## Commands and outputs (exit codes)
- `git -C <lane> rev-parse HEAD` → `3f317ecd…` (exit 0)
- `curl -fsSL` of the 3 pinned files + sha256sum → the three digests above, exit 0; literal line numbers matched
  `grep -n` exit 0 (all 14 literals sit on the stated lines: 464, 632, 634, 636, 644, 669, 703; 23, 130, 150, 277,
  281; 26, 111).
- `llama-server --help` (pinned `/home/vgpnk/.local/opt/llama-b12177/llama-server`, no server start) exit 0:
  `--port PORT (default: 9931)`; `-to, --timeout N (default: 3600)`; `--sse-ping-interval N (-1 = disabled, default: 30)`;
  `-cram, --cache-ram N (default: 8192 …)`; `-np, --parallel N number of server slots (default: -1, -1 = auto)`.
- Tag bisect of `common/common.h` `port`/`timeout_read`: b11000 8080/3600; b11500 8080/3600; b11550 9931;
  b11600 9931; b11700 9931; b12000 9931/3600; b12050 9931; b12100 9931/3600 (b11650, b11950 not present, exit 22).
- Line anchors: `evidence-lines.txt` in the out dir (exit 0).

## Per-row table
| row | engine | verdict | basis (source text / path:line) |
|---|---|---|---|
| T01 | llama.cpp b12177 `port` 9931 | holds | `common.h:632`; help `--port PORT (default: 9931)`. NOTE: env `LLAMA_ARG_PORT` is a second source of the port (`llama-arg.cpp:3323`); decision says "read it from the unit argv" only. |
| T02 | llama.cpp `timeout_read` 3600 s | overreach | `common.h:634` value/unit right. `httplib.h:250-253`: server timeout is "a ceiling that reclaims a worker from a peer that has gone quiet"; applied as socket read/write timeouts (`server-http.cpp:217-218`). It bounds quiet socket time, not a slow request. Decision "keeps a slow request open up to an hour" is not established. |
| T03 | llama.cpp `sse_ping_interval` 30 s | holds | `common.h:636`; `server-context.cpp:5546-5556`: after 30 s with no result on a stream, sends `":\n\n"` (SSE comment, not data). Note for consumers: pings are comments, a data-parsing client sees nothing. |
| T04 | llama.cpp `cache_ram_mib` 8192 MiB | overreach | `common.h:644`, `server-context.cpp:1605` (8192 is the cache cap). Decision "memory growing toward 8 GiB … is the prompt cache by default, not a leak": a cap does not establish cause. Also `server-context.cpp:1592` sets cache off for decision models unless `--cache-ram` is explicit, so "by default" is false for that class. |
| T05 | llama.cpp `sleep_idle_seconds` -1 | holds | `common.h:669`; help `-1 = disabled`; `server-context.cpp:5301` (`bypass_sleep |= sleep_idle_seconds < 0`); `arg.cpp:3828` rejects 0. |
| T06 | llama.cpp `models_max` 4 | holds | `common.h:703`; help `default: %d, 0 = unlimited`; `server-models-sched.cpp:85-88` (`has_capacity`), `:91-108` (victim eviction of idle models). |
| T07 | llama.cpp `n_parallel` 1 | **misstates** | Literal `common.h:464 = 1` is right, but it is the common default. `llama-arg.cpp:1373` (inside `LLAMA_EXAMPLE_SERVER` branch): `params.n_parallel = -1; // auto by default`; `server.cpp:126-129` (instance role, `:116`): `n_parallel = 4; kv_unified = true`; pinned `--help`: `-np … (default: -1, -1 = auto)`. Decision "one sequence decodes at a time by default: concurrent completions queue" is contradicted for llama-server. |
| T08 | Ollama `defaultPort` 11434 | holds | `config.go:23`; host fallback `config.go:42` (`127.0.0.1`). NOTE: with `OLLAMA_HOST=http://…` and no port the default is 80 (`config.go:33-34`), so "any other port must cite OLLAMA_HOST" is the right rule. |
| T09 | Ollama `keepAlive` 5 min | overreach | `config.go:130` right. Expiry unloads and removes the runner (`sched.go:430-446`, `:503`) so the `/api/ps` absence holds. Two clauses are not established by S594 lines 23-281: "/api/tags still lists it" (`routes.go:2134` ListHandler; outside the cited range) and the per-request `keep_alive` override (`sched.go:555-557`) is not mentioned. |
| T10 | Ollama `loadTimeout` 5 min | overreach | `config.go:150` right. `llama_server.go:1331-1339, 1376, 1399`: a stall window measured from last load progress, refreshed on progress. Decision "a slow first answer inside that window is loading, not dead" reads a stall window as a first-answer window; elapsed time does not show loading. |
| T11 | Ollama `NumParallel` 1 | overreach | `config.go:277` right; `sched.go:540` `numParallel = max(NumParallel, 1)`. Decision "concurrent requests queue (see T12)": T12 is only the pending queue, and requests to a loaded runner bypass it (`sched.go:245`). Queueing for loaded runners is not established by T11 or T12. |
| T12 | Ollama `MaxQueue` 512 | holds | `config.go:281`; `sched.go:128` (`pendingReqCh` buffer = maxQueue), `:248-250` (full → `ErrMaxQueue`). NOTE: "512 requests wait" applies only to requests needing a load; loaded-runner requests bypass the queue (`sched.go:245`). |
| T13 | vLLM `VLLM_ENGINE_READY_TIMEOUT_S` 600 | overreach | `envs.py:26, 811-812` right. `core_client.py:738-739`: `poll(timeout=600 s)` is per wait inside `while identities:`, so the 600 s is per engine-ready message, not a total for the API server; with several engines the total can exceed 600 s. "waits up to 10 minutes for its engine cores" and "a listener not ready inside that window has failed startup" overreach. |
| T14 | vLLM `VLLM_HTTP_TIMEOUT_KEEP_ALIVE` 5 s | holds | `envs.py:111, 1142-1144` right; consumer `entrypoints/launchers/api_server/entry.py:153` (`timeout_keep_alive`). NOTE: the close behaviour lives in that consumer, outside the S595 cited lines; the reset-on-reuse claim is supported by vLLM's own `disagg_epd_proxy.py:950-955` comment (not cited in the row). |

Tally: holds 7 (T01 T03 T05 T06 T08 T12 T14); overreach 6 (T02 T04 T09 T10 T11 T13); **misstates 1 (T07)**.

## Findings
- **BLOCKER-1 (C2 K2 trips): T07 misstates llama-server's slot default.** Decision text in `SKILL.md`
  §Serving timeout and limit thresholds, row T07, and knowledge rule 4 of `corpus/knowledge/serving-thresholds.md`
  ("One parallel sequence (llama.cpp, S593 line 464 …)") state one default. The pinned binary prints
  `-np … (default: -1, -1 = auto)` and `llama-arg.cpp:1373` / `server.cpp:126-129` resolve auto to 4 slots with
  unified KV for the instance role. Proposed corrected decision: "llama-server instances default to `-np -1` = auto
  → 4 slots with unified KV (`server.cpp:126-129`); the `common.h:464` default of 1 applies to non-server examples.
  Concurrent requests beyond the slot count queue; report the latency, do not tune it." Constraint for L1: the
  counter binds the value cell to the literal on line 464 ("1"); a corrected value cell would unbind the row. Either
  keep value `1` and name it "common_params default (non-server)", or append a row for `llama-arg.cpp:1373` with its
  own SOURCES row. Either is a new revision, not an edit of the frozen predicate.
- **DEFECT-2 (prose): SKILL intro + knowledge rule 1 misstate the history of the pin.** `SKILL.md` §intro:
  "b12177 moved the default port to 9931 and the HTTP timeout to 3600 s"; knowledge rule 1: "older builds the lane
  documented used 8080 and a shorter timeout". Source: `timeout_read = 3600` already at b11000 and b11500; port
  8080 at b11500 and 9931 at b11550 (bisect above), so neither moved at b12177. Correction: "port moved from 8080 to
  9931 between b11500 and b11550; the 3600 s read timeout is unchanged from b11000 to b12177."
- **DEFECT-3 (prose): knowledge "What round 91 adds" statement on vLLM startup.** "vLLM's API server waits up to 600 s
  for its engine cores (S595 lines 26, 809-812)" repeats the T13 overreach; see T13 corrected text.
- **DEFECT-4: overreach in six rows (T02, T04, T09, T10, T11, T13).** The contract says overreach is reported with
  corrected text, not a BLOCKER. Corrected decisions:
  - T02: "The server reclaims a connection after `timeout_read` (3600 s) with no socket progress (`httplib.h:250-253`,
    `server-http.cpp:217-218`); it does not cap how long a generation runs. A probe `--timeout` (default 5 s) is the
    probe giving up, never proof the server did."
  - T04: "8192 MiB is the host-RAM prompt-cache cap (`server-context.cpp:1605`), on for non-decision models and off for
    decision models unless `--cache-ram` is set (`server-context.cpp:1592`). Resident memory approaching the cap is
    consistent with the cache; growth alone does not establish its cause. kama reports it and does not tune it."
  - T09: "Absence from `/api/ps` after idling is expected: the expiry timer unloads the runner and removes it from the
    loaded set (`sched.go:430-446`, `:503`). A per-request `keep_alive` overrides the default (`sched.go:555-557`).
    `/api/tags` lists installed models; cite `routes.go:2134` in its own row if kept."
  - T10: "A first request may wait while Ollama's load makes progress; Ollama abandons a load only after 5 min with no
    load progress (`llama_server.go:1331-1339, 1376, 1399`). A slow first answer inside that stall window is not
    abandoned by Ollama; whether it is loading must come from `/api/ps` or runner status, not from elapsed time."
  - T11: "One request per model is the default slot count (`config.go:277`, `sched.go:540`). Requests to a loaded runner
    bypass the pending queue (`sched.go:245`); this row does not establish how they serialise. Report the latency."
  - T13: "The API server waits for each engine core's ready message up to `VLLM_ENGINE_READY_TIMEOUT_S` (600 s), per wait
    (`core_client.py:738-739`); a wait that times out raises `TimeoutError` (`core_client.py:740-747`) and startup
    fails. With several engines the total can exceed 600 s."
- **NOTE-5: holds with missing qualifiers (T01, T08, T12, T14).** Add `LLAMA_ARG_PORT` (T01), the `http://` default
  of 80 (T08), the loaded-runner bypass (T12), and the consumer `entry.py:153` (T14). None changes a verdict.
- **NOTE-6: knowledge rule 5 "llama.cpp pings a stream every 30 s"** is approximately right: a ping is sent after 30 s
  without a result, not on a fixed clock (`server-context.cpp:5546-5556`). Holds.
- **NOTE-7: knowledge "Ollama abandons a load only after a 5-minute stall (S594 line 150)"** holds on the value; the
  stall semantics live in `llm/llama_server.go:1331-1339, 1376, 1399`, not cited. Add that cite.
- **Not checked:** SGLang (declared not covered); ollama `/api/tags` semantics beyond `routes.go:2134`; uvicorn's
  close timing (outside the pinned vLLM tree).

## Deliverables
- This report: `.ufo/waves/round-91/w1/RV02ThresholdRows.md` (lane) and a copy in
  `.ufo/waves/round-91/w1/out/RV02ThresholdRows/RV02ThresholdRows.md`.
- `.ufo/waves/round-91/w1/out/RV02ThresholdRows/evidence-lines.txt` (line anchors, exit 0).
- Scratch `/fast/scratch/hyaku/kama-r91/RV02ThresholdRows/` removed after copying receipts.

VERDICT: falsified — K2 trips on T07: the llama-server `n_parallel` default is auto (4 slots), not 1 (`llama-arg.cpp:1373`, `server.cpp:126-129`, pinned `--help`); 6 rows overreach and the SKILL intro misdates the pin.
