# AMENDMENT to `prefix-cache-reuse-models.md` — the hash default changed at v0.11

> This is an addition to `corpus/knowledge/prefix-cache-reuse-models.md`, landing
> in the same round. It does not replace it; it corrects one statement that file
> makes from a superseded page. The `2026-10-23` in this file's name is the
> amendment's filing date; every source below was re-opened for this lane on
> 2026-10-25.

source: S363 — https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/ — §Automatic Prefix Caching intro, Note 1 and Note 2 — `readthedocs-version-slug` v0.32.0
verified-at: 2026-10-25
recheck: 90d — re-run `curl -fsSL 'https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/' | grep -c 'sha256'` (expect ≥1; 3 on 2026-10-25)
ground: `corpus/README.md`'s coverage map at base 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea has no row naming a hashing algorithm or a prefix-cache default; its vLLM rows are health, identity and metrics surfaces. The gap this file fills is local to the corpus, not a README label: the sibling entry quotes the v0.9.0 advice as current for its page, and that advice is not current at v0.11 and later.

## The correction

The v0.9.0 design page says: "The above hash key structure is not 100%
collision free. Theoretically it's still possible for the different prefix
tokens to have the same hash value. To avoid any hash collisions in a
multi-tenant setup, we advise to use SHA256 as hash function instead of the
default builtin hash. SHA256 is supported since vLLM v0.8.3 and must be enabled
with a command line argument." That wording is quoted in
`knowledge/prefix-cache-reuse-models.md`.

The current documentation line says: "In previous versions, the hash key was not
guaranteed to be collision-free. As of v0.11, the default hashing algorithm is
sha256, which addresses collision risks." The algorithm is also selectable:
"For vllm serve , you can control the hashing algorithm via --prefix-caching-hash-algo". The same list adds a caveat on the default:
sha256 "Uses Python's pickle for serialization. Hashes may not be reproducible
across different Python or vLLM versions", and `sha256_cbor` is the entry
"recommended for deterministic caching across environments".

The advice became the default. A reader of the sibling entry would conclude that
a multi-tenant deployment must actively switch to SHA256 to avoid cross-tenant
collision; at v0.11 and later the default is already `sha256`.

## What the amendment does not establish

The mechanism itself is unchanged: vLLM still "chooses a hash-based approach",
still hashes each kv-cache block by its own tokens plus the prefix before it, and
still caches only full blocks (Note 1 on the current page repeats it). Only the
default algorithm and the status of the caveat moved. The page states the
boundary as "As of v0.11"; it does not state what governs deployments older than
v0.11, and this entry draws no conclusion about them. The page says sha256
"addresses collision risks", not that it removes them, and it lists other
algorithms (`sha256_cbor`, `xxhash`) whose properties this entry does not
assess.
