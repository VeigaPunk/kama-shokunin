# KamaExecMetrics — source fragment (round 10, 2026-10-19)

Fragment for `corpus/SOURCES.md`. Every row below was re-opened by this seat on
2026-10-19; quotes are verbatim from the opened page. S001's row is owned by
KamaExecHealth — this seat contributes only the metrics-section quote.
`used-by` values name the entry written this round; L1 integrates rows.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S003 | vLLM Production Metrics — https://docs.vllm.ai/en/stable/usage/metrics/ | docs | A | vLLM metric names, request phases and histogram-cardinality design | §General Metrics and §Custom Histogram Buckets — stable docs page dated 2026-10-17 | Exact vllm: metric names for queue, running, KV-cache, TTFT, TPOT, e2e latency and tokens, plus the custom-bucket cardinality warning. | mined | 2026-10-19 | on-release | corpus/knowledge/serving-metrics-crosswalk.md |
| S007 | SGLang Production Metrics — https://docs.sglang.io/docs/references/production_metrics | docs | A | SGLang exporter enablement and metric definitions | §Language model metrics, §Request-level time per output token and §Setup Guide — docs page opened 2026-10-19 (no version stamp on page) | --enable-metrics flag, sglang: metric names, streaming vs non-streaming TTFT boundary and request-level TPOT semantics. | mined | 2026-10-19 | on-release | corpus/knowledge/serving-metrics-crosswalk.md |
| S018 | Prometheus Metric and label naming — https://prometheus.io/docs/practices/naming/ | docs | A | Prometheus naming, unit suffix and label-cardinality guidance | §Metric names, §Labels and §Base Units — practices page opened 2026-10-19 (no version stamp on page) | Base-unit and suffix naming rules plus the high-cardinality label caution that bounds any kama-authored metric or panel. | mined | 2026-10-19 | 90d | corpus/knowledge/serving-metrics-crosswalk.md |
| S019 | OpenTelemetry GenAI metric conventions — https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-metrics.md | spec | A | Development-stage OTel model-server metric names and boundaries | §Generative AI model server metrics — main branch commit 547934a, page status Development | gen_ai.server.* names for request duration, TTFT and time-per-output-token as a naming crosswalk target, not a stable contract. | mined | 2026-10-19 | on-release | corpus/knowledge/serving-metrics-crosswalk.md |

## Gates

### quote-for-S001 (row owned by KamaExecHealth; metrics-section contribution only)

- URL: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- accessed: 2026-10-19
- quote: "This endpoint is only accessible if `--metrics` is set."
- location: §GET `/metrics`: Prometheus compatible metrics exporter (raw README line 1131 on master @ 4c3c581)
- revision: master branch commit 4c3c5810f87efe177949f1b85ae509d38a2a311f (`git ls-remote` on 2026-10-19)

### S003

- URL: https://docs.vllm.ai/en/stable/usage/metrics/
- accessed: 2026-10-19
- quote: "Every bucket boundary creates one extra time series per metric and per label combination"
- location: §Custom Histogram Buckets, paragraph "Bucket cardinality"
- revision: stable docs page footer "October 17, 2026"

### S007

- URL: https://docs.sglang.io/docs/references/production_metrics
- accessed: 2026-10-19
- quote: "For streaming requests it ends when the first output arrives after detokenization, which may contain no printable text."
- location: §Language model metrics, `sglang:time_to_first_token_seconds` definition paragraph
- revision: docs page opened 2026-10-19; page carries no version stamp

### S018

- URL: https://prometheus.io/docs/practices/naming/
- accessed: 2026-10-19
- quote: "Do not use labels to store dimensions with high cardinality (many different label values)"
- location: §Labels, CAUTION block
- revision: practices page opened 2026-10-19; page carries no version stamp

### S019

- URL: https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-metrics.md
- accessed: 2026-10-19
- quote: "Time per output token generated after the first token for successful responses."
- location: §Generative AI model server metrics, `gen_ai.server.time_per_output_token` table row
- revision: main branch commit 547934afa90a34298441caf80c43b27255c3a292 (`git ls-remote` on 2026-10-19); page banner reads "**Status**: [Development]"

## Leads (unopened)

None — every assigned row (S003, S007, S018, S019) plus the S001 metrics
section was opened in this session.
