# Scratch normalization of staged row S327

Not an append to corpus/SOURCES.md. The data row is the fleet-schema row.

## Registry

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S327 | vLLM Engine Arguments — https://docs.vllm.ai/en/v0.32.0/configuration/engine_args/ | docs | A | vLLM admission-control valves and the HTTP status they produce; not a health verdict | §EngineArgs → SchedulerConfig → `--max-num-queued-reqs` — "When the limit is reached, new requests are rejected with HTTP 503 so the client can retry on another instance."; docs page version v0.32.0 | a 503 can be a deliberate admission rejection (request backlog or prefill-token backlog), enforced in the API server process across DP ranks | mined | 2026-10-23 | 90d | corpus/knowledge/endpoint-health-probe-conventions.md |
