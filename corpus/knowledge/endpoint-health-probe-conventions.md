# A 503 can be an admission rejection

source: S327 — https://docs.vllm.ai/en/v0.32.0/configuration/engine_args/ — `--max-num-queued-reqs` — opened 2026-10-24
verified-at: 2026-10-24
recheck: 90d

The lane already grades one 503: llama.cpp's loading envelope (`Loading model` /
`unavailable_error` / integer code 503) is `MODEL_LOADING`, not a dead endpoint
(KQ19). That grading does not cover a different 503. vLLM's engine-args page
for v0.32.0 says that when `--max-num-queued-reqs` is reached, new requests are
rejected with HTTP 503 so the client can retry on another instance. The same
page says `--max-num-queued-tokens` also rejects with HTTP 503. Those are
admission valves in the API server process, not a statement that the process
is down.

A probe that maps every 503 to dead will call a saturated vLLM server dead.
That is a different condition from llama.cpp's loading 503, and it is not a
readiness proof. This entry does not claim a vLLM process is running on this
host, and it does not sample any registered consumer.

What this entry does not establish: Docker `HEALTHCHECK`, Compose
`service_healthy`, llm-d route maps, and Prometheus `probe_success` were not
re-opened into this file. A cloud platform's configurable health route
(`serving_container_health_route`) is remote endpoint health and stays outside
this entry.

## Correction — round 44 (2026-10-26): the API server's 503 is not the only vLLM 503 that is not a death verdict

The round-43 entry `corpus/knowledge/runtime-health-surface-processes.md` adds
a third vLLM 503, in a second process. Both sentences below are quoted as they
stood and then read as corrected; this entry's own S327 ground (the v0.32.0
admission limits) is unchanged.

Superseded — the sentence at lines 12-14 (inside the enumerated 9-14):

> Those are admission valves in the API server process, not a statement that the process is down.

Read it as: "Those are admission valves in the API server process, not a
statement that the process is down, and they are not the whole vLLM 503 space:
from v0.31.0 the `vllm preload` weight-cache supervisor answers its own
`/health` with 503 until every expected target and draft rank reports, which
is a third condition — not ready — on a route in a second process (S480, S481;
the two-outcome handler at `preload.py:75`, recorded at
`runtime-health-surface-processes.md:41`)."

Superseded — the sentence at line 16 (the enumerated range 16-17 is that
sentence plus the start of the next, which stands):

> A probe that maps every 503 to dead will call a saturated vLLM server dead.

Read it as: "A probe that maps every 503 to dead will call a saturated vLLM
inference server dead, and will call a weight-cache supervisor whose ranks are
still loading dead — the same status code on a different process's `/health`.
Which vLLM process answered therefore belongs in the probe's rule, not only
which status came back: the supervisor's route is opt-in
(`--weight-cache-health-port`, default `None`, 'disabled by default' — the
`preload.py:134-137` read recorded at
`runtime-health-surface-processes.md:41`), so a probe pointed at the inference
server never sees it and
a probe pointed at it reads a 200 as 'every daemon rank is up', not as 'the
engine is alive' (S480, S481)."

The sentence that follows at lines 17-18 — "That is a different condition from
llama.cpp's loading 503, and it is not a readiness proof." — stands as
written: the admission 503 is still a different condition from the loading
one, and still not a readiness proof.

Recheck: this entry's `recheck:` is 90d (line 5) and so are S480's and S481's;
no cadence change follows from this correction.

**Round-45 citation correction (appended 2026-10-26; round-44 closure D3).** The round-44 process qualifications above cite "(S480, S481)" for which process answers the second vLLM `/health` (lines 42 and 61). S480's own `teaches` cell disclaims the process question (release notes list what shipped, not where the route lives) and S481 is a tier-C pull request. The row that carries the process fact is **S483** (`vllm/entrypoints/cli/preload.py` at v0.31.0: `_build_health_app` line 70, `@app.get("/health", include_in_schema=False)` line 73, `return Response(status_code=200 if state.is_ready else 503)` line 75). Read those citations as S483 for the process statement; S480 and S481 stay as the release-scope and change-history pointers. The earlier lines are not rewritten.
