# SOURCES — where kama learns

Contract: `SOURCES-CONTRACT-v1` (kaika, 2026-10-19, frozen). Claim admission stays
in `QUALITY.md`; this file records where claims come from, how far to trust each
source for which scope, and when to look again. Tiers are scoped to `scope`, never
global. Every row was opened in round 10 (2026-10-19); the round lesson
`lessons/round-10.md` §Gate carries each row's URL, access date and quote.

## Registry

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S325 | vLLM V1 Guide — https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/ | docs | A | vLLM V1 scheduling and batching model as the project documents it; not a runtime observation | §Scheduler — "V1's unified scheduler treats both prompt and output tokens the same way"; §Chunked Prefill — "Chunked prefill is enabled by default whenever possible"; docs page version v0.19.1 | one token budget spans prompt and output tokens; chunked prefill is on by default; FCFS or priority scheduling via `--scheduling-policy` | mined | 2026-10-23 | 90d — re-run `curl -fsSL 'https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/' \| grep -c 'unified scheduler'` (expect ≥1) (ran 2026-10-23) | corpus/knowledge/kv-cache-reclamation-models.md |
