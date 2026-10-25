# vLLM prefix-cache reuse as a hash-keyed block lookup

source: S347 — https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html — §Automatic Prefix Caching intro and §Data Structure (block hash), Note 1 and Note 2, §Eviction (LRU), §Example — `readthedocs-version-slug` v0.9.0
verified-at: 2026-10-25
recheck: 90d — re-run `curl -fsSL 'https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html' | grep -c 'hash-based approach'` (expect ≥1; 1 on 2026-10-25)
ground: `corpus/README.md`'s coverage map at base 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea has no row naming prefix-cache reuse (`grep -c -i 'prefix-cache\|prefix cache\|radix'` = 0). The nearest row is `knowledge/context-capacity.md`, which measures llama.cpp's KV pool and per-slot ceiling, not reuse of cached blocks across requests. The README carries no frontier label "serving-stack internals (schedulers, batching, KV-cache behaviour)"; that phrasing is the round's assignment, not text already in the corpus, so this entry does not claim to close a listed gap.

## The mechanism

vLLM's design page states the choice plainly: "While there are many ways to
implement prefix caching, vLLM chooses a hash-based approach." Each kv-cache
block is hashed by the tokens it contains plus the tokens of the prefix before
it — the page lists the components as "Parent hash value", "Block tokens" and
"Extra hashes" — and reuse happens "when a new request comes in with the same
prefix as previous requests". A block's key therefore covers its whole ancestry,
and a new request can reuse cached blocks only where its prompt matches that
chain block for block.

Two constraints follow from the same page. Note 1 says "We only cache full
blocks"; the worked example shows the rule in practice — "We allocate 4 blocks.
3 of them are already full and cached. The fourth block is partially full with 3
of 4 tokens."
And the hash key is not collision-free: "Theoretically it's still possible for
the different prefix tokens to have the same hash value", and the page advises
SHA256 instead of the default builtin hash "to avoid any hash collisions in a
multi-tenant setup", adding that SHA256 "must be enabled with a command line
argument" and costs "about 100-200ns per token". Eviction is per the page's
§Eviction (LRU) heading: the head block, the least recently used one, is popped
from the free queue and its ID and hash removed.

## Why this differs from SGLang's model

The lane's SGLang rows (`knowledge/kv-cache-reclamation-models.md`) describe a
radix tree whose eviction candidates are leaves, scored by a policy with the
lowest score evicted first, and a session reference as soft protection. vLLM's
model here is a hash-keyed block pool with LRU eviction and exact-prefix,
full-block matching. The two engines share neither a matching rule nor a
reclamation rule, so a conclusion written about "prefix caching" in general is
not portable between them.

## What this entry does not establish

The page is a design document pinned at v0.9.0. The lane's other vLLM rows cite
v0.17.0 (S196), v0.25.0 (S022) and v0.32.0 (S327), and the same design page at
the v0.32.0 line changed the hashing default at v0.11 — that change, and its
effect on the SHA256 advice quoted above, is recorded in
`knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md`, not here. This
entry describes the intended mechanism at v0.9.0, not a measured cache-hit rate,
and makes no claim about any running server.
