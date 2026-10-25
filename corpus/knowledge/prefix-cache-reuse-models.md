# vLLM prefix-cache reuse as a hash-keyed block lookup

source: S347 — https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html — H1 preamble (hashing paragraph), Note 1, Note 2, §Eviction (LRU) — docs page version v0.9.0, reopened 2026-10-25
verified-at: 2026-10-25
recheck: 90d — re-run `curl -fsSL 'https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html' | grep -c 'hash-based approach'` (expect ≥1)
ground: the lane held SGLang's reclamation model from primary sources but had no vLLM-side source for how a cached prefix is found; this entry is that vLLM design-side ground.

### The mechanism

vLLM's design page states the choice plainly: "While there are many ways to implement
prefix caching, vLLM chooses a hash-based approach." Each kv-cache block is hashed by
the tokens it contains *plus* the tokens of the prefix before it *plus* extra hashes
the page lists (LoRA IDs, multi-modality input hashes, cache salts), so a block's key
covers its whole ancestry and its tenant context rather than only its own text. A new
request can therefore reuse cached blocks only when its prompt matches the cached
prefix exactly, block by block, under the same additional hashes.

Two constraints follow directly from the same page. Only full blocks are cached ("We
only cache full blocks"), so a partially-filled trailing block is recomputed. And the
hash key is not collision-free: "The above hash key structure is not 100% collision
free. Theoretically it's still possible for the different prefix tokens to have the
same hash value", and the page advises SHA256 instead of the default builtin hash in
a multi-tenant setup, where a collision would serve one tenant's cached KV to another.

### Why this differs from SGLang's model

The wave-1 SGLang rows describe a radix tree whose leaves are scored and evicted
lowest-first, with a session reference as soft protection. vLLM's model is a
hash-keyed block pool with LRU eviction and exact-prefix matching. Reuse is therefore
block-aligned in vLLM, while SGLang's radix tree (S335) shares prefixes at node
boundaries; the granularity is page-size dependent in current SGLang, so no fixed
comparison of "boundary" shapes is portable without pinning both engines' parameters.
A conclusion written about "prefix caching" in general is therefore not portable
between the two engines.

### What this entry does not establish

The page is a design document at v0.9.0, roughly one release line behind the versions
the lane's other vLLM rows cite (v0.17.0, v0.19.1, v0.32.0). It describes the intended
mechanism, not a measured cache-hit rate, and it makes no claim about any running
server.
