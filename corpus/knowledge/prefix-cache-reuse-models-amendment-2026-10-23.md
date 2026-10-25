# AMENDMENT (2026-10-25) to prefix-cache-reuse-models.md — the hash default changed at v0.11

> This is an addition to `corpus/knowledge/prefix-cache-reuse-models.md`, admitted by
> round 37. It does not replace it; it corrects one statement that file makes from a
> superseded page.

source: S363 — https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/ — H1 preamble, Note 2, --prefix-caching-hash-algo list — docs page version v0.32.0, reopened 2026-10-25
verified-at: 2026-10-25
recheck: 90d — re-run `curl -fsSL 'https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/' | grep -c 'default hashing algorithm is sha256'` (expect ≥1)
ground: the round-37 entry described a collision caveat from the v0.9.0 page; the current documentation line changed the default and the status of that caveat.

### The correction

The v0.9.0 design page says: "Note 2: The above hash key structure is not 100%
collision free. Theoretically it's still possible for the different prefix tokens to
have the same hash value. To avoid any hash collisions in a multi-tenant setup, we
advise to use SHA256 as hash function instead of the default builtin hash. SHA256 is
supported since vLLM v0.8.3".

The current documentation line says: "Note 2 In previous versions, the hash key was
not guaranteed to be collision-free. As of v0.11, the default hashing algorithm is
sha256, which addresses collision risks." The algorithm is also selectable with
`--prefix-caching-hash-algo` (sha256 default, sha256_cbor recommended for
deterministic caching, plus xxhash and xxhash_cbor variants, for which the collision
caution still applies).

The advice became the default. The v0.9.0 page advised SHA256 for multi-tenant
setups; on v0.11 and later the default is sha256, so that active switch is no
longer required unless a non-sha256 algorithm is selected.

### What the amendment does not establish

The mechanism itself is unchanged: vLLM still "chooses a hash-based approach", still
hashes each kv-cache block by its own tokens plus the preceding prefix plus extra
hashes, and still caches only full blocks. What moved is the default algorithm, the
status of the builtin-hash caveat (historical for the default, live for the xxhash
variants), and a new reproducibility caveat on the default: sha256 uses Python's
pickle for serialization, so hashes may not be reproducible across different Python
or vLLM versions. The version boundary is stated by the page as v0.11, so any
deployment older than that is still governed by the v0.9.0 wording.
