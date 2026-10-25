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
