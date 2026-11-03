# kama: from iteration scheduling to phase-specific service objectives

Date: 2026-11-03 · Batch 5

**Unassimilated post-hyaku reading proposal; assimilation awaits the user’s explicit instruction.** No deployment, endpoint probe, workload, installation or training was performed. Historical performance claims are not extrapolated to the present host.

## Orca → DistServe → contemporary vLLM guidance

**Timeline and reading.** Yu et al.'s [Orca](https://www.usenix.org/conference/osdi22/presentation/yu), OSDI July 2022, schedules at generation-iteration granularity and selectively batches Transformer operations. The important transition is letting the serving batch evolve during generation rather than waiting for whole requests. Read the scheduling and selective-batching design, keeping its evaluation hardware and model separate from local serving facts.

Zhong et al.'s [DistServe](https://arxiv.org/abs/2401.09670v3) first appeared 2024-01-18; selected v3 is 2024-06-06, associated with OSDI 2024. Read sections 2–4 and the evaluation setup. It separates prefill and decode placement to optimize requests meeting both first-token and per-output-token latency objectives. KV transfer, network bandwidth and phase-specific resource allocation become explicit costs. Its measured gains concern particular workloads and SLOs, not every deployment's raw throughput.

**Current practice bridge.** The [vLLM disaggregated-prefill document](https://github.com/vllm-project/vllm/blob/a900ac810ecaedc0c2c5e9a8887e353cf1a5c350/docs/features/disagg_prefill.md) was read at [commit a900ac8](https://github.com/vllm-project/vllm/commit/a900ac810ecaedc0c2c5e9a8887e353cf1a5c350), dated 2026-11-03T14:57:17Z. It marks the feature experimental, describes independent TTFT/ITL tuning and explicitly warns against expecting throughput improvement. It also identifies chunked prefill as another way to control tail ITL. This implementation guidance is not a controlled replication of DistServe.

**What changed and stayed.** The optimization target expanded from keeping execution productive to satisfying separate latency constraints. Batching and memory/resource accounting still matter. Phase separation complements scheduling; it does not erase it. Older colocated serving remains a sensible baseline when interconnect capacity, available GPUs or operational simplicity constrain deployment. That is a bounded engineering inference to test, not an asserted winner for this host.

**Original future question.** After hyaku, under which fictional workload/SLO combinations would extra phase isolation be worth transfer and coordination costs? Draft a comparison ledger holding model, precision, hardware budget and offered arrivals fixed while separately recording raw tokens/second, TTFT/ITL distributions and joint SLO attainment. Include a low-load case where extra machinery has no demonstrated benefit.

**Rights and novelty.** Orca reuse rights beyond reading were not established. DistServe's selected arXiv record is CC-BY-SA-4.0. vLLM's pinned [LICENSE](https://github.com/vllm-project/vllm/blob/a900ac810ecaedc0c2c5e9a8887e353cf1a5c350/LICENSE) is Apache-2.0; connectors have separate dependencies. No source or assets are copied. Orca, DistServe and this transition were absent from the supplied registry and four prior batches; vLLM as a publisher is not claimed novel.
