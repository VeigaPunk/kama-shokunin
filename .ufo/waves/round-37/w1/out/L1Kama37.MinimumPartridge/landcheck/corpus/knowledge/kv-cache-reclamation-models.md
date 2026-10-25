
# How vLLM and SGLang reclaim KV cache, and why the two models are not interchangeable

source: S330 — https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/ — §Scheduler and §Chunked Prefill — page version v0.19.1
source: S333 — https://docs.sglang.io/docs/advanced_features/radix_eviction_policy — §Eviction candidates — source docs/docs/advanced_features/radix_eviction_policy.mdx @ sgl-project/sglang 77091cea68d0701d6cc71edfb45f2815c4f8d791 (2026-09-29)
source: S334 — https://docs.sglang.io/docs/advanced_features/session_radix_cache — §Session references — source docs/docs/advanced_features/session_radix_cache.mdx @ sgl-project/sglang d34f7b2326a10cb5f3ba8ec95efb31c761237750 (2026-09-22)
source: S335 — https://arxiv.org/abs/2312.07104 — §RadixAttention — arXiv:2312.07104 and arXiv:2312.07104v1
source: S346 — https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md — §6.4 RadixAttention — commit 35b83cee12ae26f10b58d4163298352384503907 (2026-06-16)
verified-at: 2026-10-23
recheck: 90d — re-run the row recheck commands for S330, S333, S334, S335 and S346 in SOURCES-PROPOSED.md (ran 2026-10-23)
ground: frontier item "serving-stack internals (schedulers, batching, KV-cache behaviour)" — the lane held engine *surfaces* (metrics, health routes) but no documented account of *why* a served request is slow, rejected, or re-prefilled.

### Two reclamation models, not one

- **vLLM.** The V1 scheduler "treats both prompt and output tokens the same way",
  allocating a fixed token budget per request from one dictionary, which is what
  makes chunked prefill possible; chunked prefill is on by default. Scheduling
  policy is FCFS or priority, with FCFS as the tie-breaker. Reclamation is
  therefore block-pool and admission-shaped, not tree-shaped.
- **SGLang.** The KV cache is a radix tree. Only *evictable leaves* are
  candidates — present, unlocked, and not shadowed by a child still holding KV —
  and "the policy scores each candidate and the lowest score is evicted first",
  with LRU as the tie-break. The paper states the protectiveness rule directly:
  in continuous batching a node used by the running batch cannot be evicted, so
  "a node is evictable if its reference counter is zero".

### The rule that is easy to get wrong

A **session reference is not a memory pin**. SGLang's session-aware radix cache
says so explicitly: "session references are soft protection, not memory pins", and
referenced KV can still be evicted when reclaiming unreferenced KV is insufficient.
The `session_id` labels cache references only; it neither appends nor reconstructs
conversation context, so every request must still carry its full intended prompt.

### The Chinese-language source map (secondary)

The Chinese write-up in S346 is useful as a *map*, not as an authority: it names
the concrete implementation files (`mem_cache/radix_cache.py` → `RadixCache`,
`managers/schedule_policy.py` → `SchedulePolicy`) and contrasts vLLM's flat
hash-chain prefix cache with SGLang's radix tree and LPM scheduling. It is tier B
because a community file map cannot outrank the upstream project on behaviour.

### What this entry does not establish

No eviction, prefill or latency behaviour was observed on this host. A
documentation-level model of reclamation does not license a prediction about any
particular request's latency, and the Chinese file map may drift from the upstream
source at any release.
