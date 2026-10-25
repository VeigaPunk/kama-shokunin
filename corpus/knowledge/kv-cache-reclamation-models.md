# How vLLM and SGLang reclaim KV cache, and why the two models are not interchangeable

source: S330 — https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/ — §Feature Support (admonition note); §Differences from V0 → Chunked Prefill — docs page version v0.19.1, reopened 2026-10-25
source: S333 — https://docs.sglang.io/docs/advanced_features/radix_eviction_policy — §How eviction picks a victim — reopened 2026-10-25
source: S334 — https://docs.sglang.io/docs/advanced_features/session_radix_cache — lead paragraph under the page title (no heading) — reopened 2026-10-25
source: S335 — https://arxiv.org/abs/2312.07104 — §5.1 RadixAttention — arXiv:2312.07104 (abs) and arXiv:2312.07104v1 (HTML full text), reopened 2026-10-25
source: S346 — https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md — §6.4 SGLang 深读 — commit 35b83cee12ae26f10b58d4163298352384503907, reopened 2026-10-25
verified-at: 2026-10-25
recheck: 90d — re-run the row recheck commands for S330, S333, S334, S335 and S346 (curl -fsSL the URL, grep the quoted anchor, expect ≥1)
ground: the lane's coverage map held engine surfaces (metrics, health routes, served-model identity) but no documented account of *why* a served request is re-prefilled or evicted; these entries close that gap for the endpoint-health question (what a served endpoint answers, and at what cost).

### Two reclamation models, not one

- **vLLM.** The V1 scheduler "treats both prompt and output tokens the same way",
  allocating a fixed token budget per request from one dictionary; "chunked
  prefill is enabled by default whenever possible, unlike in V0". Scheduling
  policy is FCFS or priority, with FCFS as the tie-breaker, configurable via
  `--scheduling-policy`. The design page (S347) describes the cache as a
  hash-keyed block pool with LRU eviction; reclamation on the engine side is
  therefore block-pool and admission-shaped, not tree-shaped — an inference
  from the two pages, not a quoted sentence.
- **SGLang.** The KV cache is a radix tree. Eviction "only ever considers
  evictable leaves": nodes whose KV is present, unlocked (no in-flight request
  holds them), and not shadowed by a child that still holds KV, and "the policy
  scores each candidate and the lowest score is evicted first". The paper states
  the protectiveness rule directly: in continuous batching a node used by the
  running batch cannot be evicted, so "a node is evictable if its reference
  counter is zero", with LRU eviction recursively removing leaf nodes and a
  cache-aware scheduling policy sorting the queue by matched prefix length.

### The rule that is easy to get wrong

A **session reference is not a memory pin**. SGLang's session-aware radix cache
says so explicitly: "session references are soft protection, not memory pins",
and referenced KV "can still be evicted when reclaiming unreferenced KV is
insufficient". The `session_id` labels cache references only; "it does not
append or reconstruct conversation context", so each request must still carry
its full intended prompt.

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
