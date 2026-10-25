
# AMENDMENT (2026-10-23) to prefix-cache-reuse-models.md — the hash default changed at v0.11

> This is an addition to `corpus/knowledge/prefix-cache-reuse-models.md`, staged by
> round 2. It does not replace it; it corrects one statement that file makes from a
> superseded page.

source: S363 — https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/ — §Automatic Prefix Caching → Note 2 — docs page version v0.32.0
verified-at: 2026-10-23
recheck: 90d — re-run `curl -fsSL 'https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/' \| grep -c 'sha256'` (expect ≥1) (ran 2026-10-23)
ground: frontier item "serving-stack internals (schedulers, batching, KV-cache behaviour)" — the round-2 entry described a collision caveat that the current documentation line no longer states as an obligation.

### The correction

Round 2's entry was written from the v0.9.0 design page, which says: "Note 2: The
above hash key structure is not 100% collision free. Theoretically it's still possible
for the different prefix tokens to have the same hash value. To avoid any hash
collisions in a multi-tenant setup, we advise to use SHA256 as hash function instead
of the default builtin hash. SHA256 is supported since vLLM v0.8.3".

The current documentation line says: "Note 2 In previous versions, the hash key was
not guaranteed to be collision-free. **As of v0.11, the default hashing algorithm is
sha256**, which addresses collision risks." The algorithm is also selectable with
`--prefix-caching-hash-algo`.

The advice became the default. A reader of the round-2 entry would conclude that a
multi-tenant deployment must actively switch to SHA256 to avoid cross-tenant
collision; on v0.11 and later it does not have to.

### What the amendment does not establish

The mechanism itself is unchanged: vLLM still "chooses a hash-based approach", still
hashes each kv-cache block by its own tokens plus the preceding prefix, and still
caches only full blocks. Only the default algorithm and the status of the caveat
moved. The version boundary is stated by the page as v0.11, so any deployment older
than that is still governed by the v0.9.0 wording.
