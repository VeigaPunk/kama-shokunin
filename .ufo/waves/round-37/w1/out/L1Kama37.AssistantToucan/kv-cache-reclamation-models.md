# What vLLM and SGLang document about KV-cache reclamation, and why the two models are not interchangeable

source: S330 — https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/ — §Feature Support (the state-legend note), §Chunked Prefill and §Prompt Logprobs with Prefix Caching — `readthedocs-version-slug` v0.19.1
source: S333 — https://docs.sglang.io/docs/advanced_features/radix_eviction_policy — §How eviction picks a victim and §Available policies — page metadata `originalFileLocation` docs/advanced_features/radix_eviction_policy.mdx, `lastModified` 2026-10-24T12:16:03.909Z; no commit pin on the rendered page
source: S334 — https://docs.sglang.io/docs/advanced_features/session_radix_cache — page lead paragraph (before §Enable the cache) and §Eviction behavior — page metadata `originalFileLocation` docs/advanced_features/session_radix_cache.mdx, `lastModified` 2026-10-24T12:16:03.909Z; no commit pin on the rendered page
source: S335 — https://arxiv.org/abs/2312.07104 and https://arxiv.org/html/2312.07104v1 — §5.1 RadixAttention — arXiv:2312.07104v1
source: S346 — https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md — §6.4.1 source-location table lines 330–331 and §6.4.2 RadixAttention — commit 35b83cee12ae26f10b58d4163298352384503907
verified-at: 2026-10-25
recheck: 90d — re-run one GET per row: (a) `curl -fsSL 'https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/' | grep -c 'unified scheduler'` (expect ≥1; 1 on 2026-10-25); (b) `curl -fsSL 'https://docs.sglang.io/docs/advanced_features/radix_eviction_policy' | grep -c 'lowest score is evicted first'` (expect ≥1; 2 on 2026-10-25); (c) `curl -fsSL 'https://docs.sglang.io/docs/advanced_features/session_radix_cache' | grep -c 'soft protection, not memory pins'` (expect ≥1; 2 on 2026-10-25); (d) `curl -fsSL 'https://arxiv.org/html/2312.07104v1' | grep -c 'reference counter is zero'` (expect ≥1; 1 on 2026-10-25); (e) `curl -fsSL 'https://raw.githubusercontent.com/AaronYang238/llm/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md' | grep -c 'radix_cache.py'` (expect ≥1; 3 on 2026-10-25)
ground: `corpus/README.md`'s coverage map at base 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea has no row naming KV-cache eviction, reclamation or a radix cache (`grep -c -i 'radix\|prefix-cache\|prefix cache\|reclamation\|eviction'` = 0). The nearest row is `knowledge/context-capacity.md`, which covers llama.cpp's KV **pool** and per-slot ceiling on the lane fixture, not eviction candidates or a scoring policy. The README carries no frontier label "serving-stack internals (schedulers, batching, KV-cache behaviour)"; that phrasing is the round's assignment, not text already in the corpus, so this entry does not claim to close a listed gap.

## Two models, and what each source actually documents

- **vLLM (S330).** The V1 guide's note says "vLLM V1's unified scheduler treats
  both prompt and output tokens the same way by using a simple dictionary
  (e.g., `{request_id: num_tokens}`) to dynamically allocate a fixed token
  budget per request, enabling features like chunked prefills, prefix caching,
  and speculative decoding". It also says "Chunked prefill is enabled by
  default whenever possible, unlike in V0 where it was conditionally enabled
  based on model characteristics", and that the V1 scheduler "supports multiple
  scheduling policies, including First-Come, First-Served (FCFS) and
  priority-based scheduling (where requests are processed based on assigned
  priority, with FCFS as a tie-breaker), configurable via the
  `--scheduling-policy` argument". One consequence for a served request is on
  the same page: "While V1 supports passing prompt logprobs with prefix caching
  enabled, it no longer caches the logprobs. For a request requiring prompt
  logprobs, the engine will ignore the prefix cache and recompute the prefill of
  full prompt to generate the logprobs." Beyond that cache-bypass note, the page
  documents admission and allocation: it names no eviction candidate, no score
  and no victim, so **this entry asserts no vLLM eviction model**; the other
  consequence drawn from it is that admission is driven by a per-request token
  budget.
- **SGLang (S333, S335).** Eviction "only ever considers evictable leaves:
  nodes whose KV is present, unlocked (no in-flight request holds them), and not
  shadowed by a child that still holds KV"; "the root is never evictable"; "the
  policy scores each candidate and the lowest score is evicted first"; and a
  policy "only scores. It does not decide how much to free, and it cannot pin
  KV in memory — a node protected by the policy is still evicted if reclaiming
  everything else is not enough". The policies page adds "All of them fall back
  to least-recently-used order within a tie", with `lru` as the default. The
  paper states the protectiveness rule directly: in continuous batching "we
  cannot evict nodes that are being used by the currently running batch", so
  each node keeps a reference counter and "a node is evictable if its reference
  counter is zero" (S335 §5.1).

## The rule that is easy to get wrong

A **session reference is not a memory pin**. The session-aware page says so
explicitly: "Session references are soft protection, not memory pins.
Referenced KV can still be evicted when reclaiming unreferenced KV is
insufficient." The page's §Eviction behavior makes the order concrete: for the
full-attention component the order is "Unreferenced nodes first, then referenced
nodes with fewer session references, then the configured policy such as LRU".
The lead paragraph also says the `session_id` "labels cache references only; it
does not append or reconstruct conversation context, so each request must still
contain the intended prompt" — the example passes
`"text": "FULL_PROMPT_FOR_THIS_TURN"` on every turn.

## Why the two are not one model

SGLang's reclamation is defined over a tree: candidates are leaves, a policy
scores them, the lowest score goes first. The vLLM page cited here defines a
single token-budget dictionary and documents no reclamation rule at all. A
statement about "KV-cache eviction" written from the SGLang pages therefore does
not carry to this vLLM source, and the vLLM scheduling sentence does not
describe SGLang's tree.

## The Chinese-language source map (secondary)

The Chinese write-up in S346 is useful as a *map*, not as an authority: its
§6.4.1 table names the concrete implementation files (`mem_cache/radix_cache.py`
→ `RadixCache`, `managers/schedule_policy.py` → `SchedulePolicy`) and its
comparison row contrasts vLLM's 链式(扁平) hash prefix cache with SGLang's
基数树 prefix cache and LPM scheduling. It is tier B because a community file
map cannot outrank the upstream project on behaviour.

## What this entry does not establish

No eviction, prefill or latency behaviour was observed on this host. A
documentation-level model of reclamation does not license a prediction about any
particular request's latency. The S333 and S334 pages carry a `lastModified`
timestamp but no commit pin, so their statements are dated by that timestamp and
`verified-at`, and the recheck commands are the only drift guard. The Chinese
file map may drift from the upstream source at any release.
