source: S593 (llama.cpp `common/common.h` @ tag `b12177`, `common_params` lines 464-705), S594 (Ollama `envconfig/config.go` @ tag `v0.40.11`, lines 23-281), S595 (vLLM `vllm/envs.py` @ tag `v0.32.0`, lines 26, 111, 809-813, 1142-1145); cross-read, not cited as rows: llama.cpp `common/arg.cpp` @ `b12177` lines 3318-3323 (`--port` help prints `params.port`), 3560-3564 (`--timeout` sets read and write), 3664-3666 (`--models-max`, `0 = unlimited`). Prior art held before round 91: `corpus/knowledge/endpoint-identity.md` (readiness signals and probe thresholds of the probe itself), `corpus/knowledge/router-mode-readiness.md` (router `status` vocabulary, S581).
verified-at: 2026-11-06 — every row of `SKILL.md` §Serving timeout and limit thresholds bound by `python3 tools/round91-threshold-rows.py` (live fetch, sha256 equal to the SOURCES row, literal on the stated line); receipt `.ufo/waves/round-91/measured/c2.out`.
recheck: on-release — on any bump of the llama.cpp, Ollama or vLLM pin, re-open the three files at the new tag, add rows for the new pin (append-only) and re-run the counter; a moved default is a new row, never an edit of an old one.

# Serving timeout and limit thresholds of the pinned engines

## What was already held (not new in round 91)

The lane's decision tables grade an endpoint by what it answers (`/v1/models`, `/health`, router `status`),
and the probe bounds its own waiting (`--timeout`, `--connect-timeout`, the 4 MiB answer cap of round 90).
What the lane did not hold is the other side's clock: how long each engine keeps a request, a model or a
connection by default, and at which port it listens when nobody configured one. Without that, a slow first
answer, a model missing from Ollama's `/api/ps`, a reset keep-alive connection or a `DEAD` on 8080 could only
be read as faults.

## What round 91 adds

Fourteen default thresholds, each read on its line at the pinned tag (table and probe decisions in
`SKILL.md` §Serving timeout and limit thresholds). The reading rules:

1. **A default is a property of the pin.** llama.cpp b12177 listens on 9931 when `--port` is absent and keeps
   an HTTP request open 3600 s (S593 lines 632, 634); older builds the lane documented used 8080 and a shorter
   timeout. The counter binds a value to one tag; a pin bump needs new rows.
2. **Absence after idling is not absence.** Ollama unloads an idle model after 5 minutes (S594 line 130,
   doc comment line 128 "Default is 5 minutes."), so `/api/ps` loses it while `/api/tags` keeps it; a
   llama.cpp router holds at most 4 loaded models (S593 line 703), so `unloaded` entries are normal there.
3. **A wait inside the engine's window is loading.** Ollama abandons a load only after a 5-minute stall
   (S594 line 150); vLLM's API server waits up to 600 s for its engine cores (S595 lines 26, 809-812). Inside
   those windows the honest verdict is loading, outside them failed startup.
4. **Queueing is reported, never tuned.** One parallel sequence (llama.cpp, S593 line 464; Ollama, S594 line
   277) and a 512-request Ollama queue (line 281) explain latency and overflow under load; scheduling is
   out of province (`PROVINCE.md`).
5. **Connection lifetime is the server's.** vLLM closes an idle keep-alive connection after 5 s (S595 line
   111, comment line 1142); llama.cpp pings a stream every 30 s (S593 line 636). A reset after idle reuse is
   not a server fault; a stream silent far beyond 30 s is.

## Limits

The values are defaults read from source at one tag each; a unit's argv or environment overrides them, and
kama does not read service units (operator-owned). No row was measured on a live server this round. SGLang
is not covered: its `server_args.py` at v0.5.22 moved its defaults into `sglang/srt/arg_groups/` (opened, not
mined this round; see the round-91 lesson Gate).

## Round 91 correction (2026-11-06) — wave-1 non-author read

Rules 1, 3 and 4 above overreach or misstate; the body is kept (append-only), read it through this section.
Evidence: `.ufo/waves/round-91/w1/RV02ThresholdRows.md` (per-row table, tag bisect) and
`.ufo/waves/round-91/w1/SC01SourceReopen.md`; the L1 re-ran the pinned binary's `--help`
(`-np, --parallel N number of server slots (default: -1, -1 = auto)`).

- **Rule 4, llama.cpp half, is wrong.** `S593 line 464` is the `common_params` default; `llama-server`
  overrides it to auto (`common/arg.cpp:1373`), which resolves to 4 slots with unified KV
  (`tools/server/server.cpp:126-129`). A default llama-server b12177 decodes up to 4 sequences at once. The
  Ollama half (one request per model, S594 line 277) stands, but requests to a loaded runner bypass the
  512-request queue (`server/sched.go:245`), so the queue explains overflow only for requests waiting on a load.
- **Rule 1 history is wrong.** The port moved 8080 → 9931 between b11500 and b11550; `timeout_read = 3600`
  is unchanged from b11000 to b12177. `timeout_read` bounds a quiet socket, not a request's run time.
- **Rule 3 overreaches.** Ollama's 5 minutes are a stall window from the last load progress
  (`llm/llama_server.go:1331-1339`); vLLM's 600 s apply per engine-ready wait (`v1/engine/core_client.py:738-739`),
  so total startup can exceed 600 s. Elapsed time alone does not prove loading.
- Lesson: a struct default is not the runtime default until the binary's own argument parser or `--help`
  agrees (QUALITY KQ146, `corpus/lessons/round-91.md` M1).
