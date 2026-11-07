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

## Round 92 revision (2026-11-06) — the defaults re-declared under KQ146

source: S596 (llama.cpp `common/arg.cpp` @ tag `b12177`, per-example defaults line 1373), S597 (llama.cpp
`tools/server/server.cpp` @ tag `b12177`, `server_prepare_params` lines 115-131); S593, S594, S595 re-opened this round
(sha256 equal to their rows).
verified-at: round 92 — `python3 tools/round92-server-defaults.py --repo . --rev <rev> --binary <llama-server b12177>`
(receipts under `.ufo/waves/round-92/measured/`).

`SKILL.md` §Serving defaults (round 92 revision) supersedes the round-91 table row for row (R01–R15 name the
T01–T14 they replace). The reading rules, revised:

1. **The binary decides.** A default is the value the program kama probes uses. For llama-server that is the
   `common_params` struct default only where the server's parser keeps it; the counter compares each option row with
   the pinned binary's `--help` (H1), which prints the post-parser default. `n_parallel` is the case: struct 1
   (`common.h:464`), parser -1 = auto (S596 line 1373), startup 4 slots with unified KV outside the router role
   (S597 lines 126-130). A derived value no option prints (the 4) binds only to the server entry point (H2).
2. **The run-time reader, not the declaration.** vLLM's `envs.py` declares `VLLM_ENGINE_READY_TIMEOUT_S: int = 600`
   under `TYPE_CHECKING` (line 26) for type checkers; the value the server uses comes from the
   `environment_variables` lambda (line 812, `os.environ.get(…, "600")`, served by the module `__getattr__`). The
   two agree at this pin, but only the lambda is the default; the counter cannot tell them apart (pre-freeze control
   V7), so this rule is a reviewer read.
3. **A default says what the server may do, not what happened.** Every decision cell is phrased as what kama may
   and may not infer: a probe timeout is the probe's, a missing `/api/ps` entry is consistent with keep-alive, a slow
   first answer is never graded from elapsed time against a stall window, and how queued requests are served is not
   read from a parallelism default.

Limits: llama.cpp rows are bound to b12177 and its Linux x64 binary only; Ollama and vLLM rows have no installed
binary to compare, so they rest on the line alone (KQ146's `--help` half does not apply). Pin bumps need new rows.

## Round 92 correction (2026-11-06) — every setter, not only the default

source: S596 (`common/arg.cpp` @ `b12177` lines 4613-4764), S598 (`tools/server/server-http.cpp` @ `b12177` lines 93-125),
S599 (`tools/server/server-models.cpp` @ `b12177` line 1218).

Rule 1 above is necessary, not sufficient: the value can be the binary's default while a decision about what the binary
*does* still fails. llama-server b12177 has eleven preset options that set `params.port` and/or `params.n_parallel`
(`--embd-gemma-default`: port 8011, 32 slots), an AIP mode that replaces the port (`AIP_HTTP_PORT`, default 8080) and
router children that listen on a free port. A decision that states the default's effect names or excludes each setter
(QUALITY KQ149; lesson `corpus/lessons/round-92.md` M4; wave-1 SC01).
