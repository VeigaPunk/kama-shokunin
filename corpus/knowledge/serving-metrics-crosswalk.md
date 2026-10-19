# Serving metrics crosswalk — llama.cpp, vLLM, SGLang exporters vs OTel GenAI
source: S001 https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md §GET `/metrics` + §Available metrics; S003 https://docs.vllm.ai/en/stable/usage/metrics/ §General Metrics + §Custom Histogram Buckets; S007 https://docs.sglang.io/docs/references/production_metrics §Language model metrics + §Request-level time per output token; S018 https://prometheus.io/docs/practices/naming/ §Metric names + §Labels; S019 https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-metrics.md §Generative AI model server metrics
verified-at: 2026-10-19 — vendor/spec docs opened; no local runtime contacted
recheck: on-release — S001 §GET `/metrics`; S003 §General Metrics and §Custom Histogram Buckets; S007 §Language model metrics and §Request-level TPOT; S019 status banner and metric names

## Claim

`/metrics` enablement, metric names, and measurement boundaries (TTFT, per-token latency, queue/running, cache use, end-to-end latency, token throughput) differ per engine, so a cross-engine comparison must cite each engine's flag + metric name + documented definition; metrics never establish served-model identity or pin correctness.

## Crosswalk

| Operational question | llama.cpp | vLLM | SGLang | OTel GenAI name |
|---|---|---|---|---|
| Exporter enablement | `/metrics` only when `--metrics` is set [S001] | `/metrics` on the OpenAI-compatible API server [S003] | `--enable-metrics` at launch [S007] | instrumentation convention, no server flag [S019] |
| Queue pressure | `llamacpp:requests_deferred` [S001] | `vllm:num_requests_waiting` [S003] | `sglang:num_queue_reqs` [S007] | not documented in opened page |
| Running requests | `llamacpp:requests_processing` [S001] | `vllm:num_requests_running` [S003] | `sglang:num_running_reqs` [S007] | not documented in opened page |
| Cache usage | `llamacpp:n_tokens_max` (context high watermark, not live KV use) [S001] | `vllm:kv_cache_usage_perc` [S003] | `sglang:num_used_tokens`; `sglang:token_usage`; `sglang:cache_hit_rate` [S007] | not documented in opened page |
| TTFT | not documented in opened page | `vllm:time_to_first_token_seconds` [S003] | `sglang:time_to_first_token_seconds` [S007] | `gen_ai.server.time_to_first_token` [S019] |
| Per-token latency | not documented in opened page | `vllm:inter_token_latency_seconds`; `vllm:request_time_per_output_token_seconds` [S003] | `sglang:inter_token_latency_seconds`; `sglang:request_time_per_output_token_seconds` [S007] | `gen_ai.server.time_per_output_token` [S019] |
| End-to-end latency | `llamacpp:prompt_seconds_total`; `llamacpp:tokens_predicted_seconds_total` (cumulative process time, not per-request latency) [S001] | `vllm:e2e_request_latency_seconds` [S003] | `sglang:e2e_request_latency_seconds` [S007] | `gen_ai.server.request.duration` [S019] |
| Token throughput | `llamacpp:prompt_tokens_seconds`; `llamacpp:predicted_tokens_seconds` gauges + `llamacpp:prompt_tokens_total`; `llamacpp:tokens_predicted_total` counters [S001] | `vllm:prompt_tokens`; `vllm:generation_tokens` counters [S003] | `sglang:prompt_tokens_total`; `sglang:generation_tokens_total` counters; `sglang:gen_throughput` gauge [S007] | not documented in opened page (token counters sit in the client-side section) |

Measurement-boundary notes:

- TTFT boundary differs: SGLang ends streaming TTFT "when the first output arrives after detokenization" but non-streaming at first scheduler token [S007]; OTel defines "Time to generate first token for successful responses" [S019]; S003's table gives no boundary split.
- TPOT is not one thing: `sglang:request_time_per_output_token_seconds` excludes the first token and weights each finished request equally, unlike token-weighted `sglang:inter_token_latency_seconds` [S007]; vLLM also documents both families [S003].
- Enablement is opt-in on two of three engines: llama.cpp requires `--metrics` [S001], SGLang requires `--enable-metrics` [S007]; vLLM documents `/metrics` as a served route [S003].
- Cardinality caution: vLLM `--custom-histogram-buckets` adds one series per boundary per metric per label combination [S003]; SGLang's TPOT histogram splits by `is_streaming` and reuses `--bucket-inter-token-latency` [S007]; Prometheus warns against high-cardinality label values [S018].
- Naming style differs on purpose: engines ship `vllm:`/`sglang:`/`llamacpp:` prefixes with `_seconds`/`_total` suffixes per Prometheus practice [S018]; OTel `gen_ai.server.*` names omit unit/type, which S018 explicitly contrasts with Prometheus naming.

## What this does not establish

- No local endpoint was scraped and no runtime here is shown to expose these names; docs and fixtures are not runtime integration (KQ4).
- Metrics say nothing about which model is served or whether a configured pin is correct; identity stays on `/v1/models` per `SKILL.md` §Served-id normalization and `knowledge/served-model-identity.md`.
- This entry covers local engine exporters — a different topic from `knowledge/free-tier-provider-limits.md`, which is provider load-test dispatch telemetry.
- S019 self-marks `Status: Development`; its names are a crosswalk target, not a stable contract.

## kama use

- On a registered endpoint proven llama.cpp with `--metrics` enabled, `llamacpp:` names may be cited in a dated census; without the flag the `/metrics` surface does not exist [S001].
- Any future cross-engine panel keys on the operational question, not a guessed name: record flag + metric name + definition per engine before comparing.
- Metrics stay out of the identity-verdict path; this entry authorizes no new probing.
- kama-authored recording rules (none exist today) follow S018 base units and low-cardinality labels.

## QUALITY clearance

- KQ1: no present endpoint claim; every statement is engine + documented section + opened date, never a live verdict.
- KQ2: pin provenance and effective-runtime selection untouched; metrics enter neither.
- KQ3: anchors name section plus revision/date; OTel Development status recorded verbatim.
- KQ4: docs-scoped crosswalk; no scrape, fixture, or monitoring claim is made.
- KQ5: no service started, no endpoint contacted, no credentials or prompt content as telemetry.
- KQ6: every engine statement names engine + documented revision (commit, release or dated page) + section and cites an opened `SOURCES.md` row (tier A for its scope; no C-tier row supports this entry); never asserted as local runtime fact.
- KQ7–KQ10: not a correction entry (KQ7); no privilege-bounded verdict (KQ8); no negative claim — absences are stated as 'not documented in the opened page', not as non-existence (KQ9); no census or probe run by the entry's author (KQ10).

## Cited sources

- S001 — llama.cpp server README, §GET `/metrics` + §Available metrics table, master @ `4c3c581` (opened 2026-10-19)
- S003 — vLLM Production Metrics, §General Metrics + §Custom Histogram Buckets, stable docs page dated Oct 17 2026
- S007 — SGLang Production Metrics, §Language model metrics + §Request-level time per output token + §Setup Guide (opened 2026-10-19)
- S018 — Prometheus Metric and label naming, §Metric names + §Labels + §Base Units (opened 2026-10-19)
- S019 — OTel semantic-conventions-genai `gen-ai-metrics.md`, §Generative AI model server metrics, `Status: Development`, main @ `547934a` (opened 2026-10-19)
