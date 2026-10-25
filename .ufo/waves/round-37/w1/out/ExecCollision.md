# Collision guard re-proof and real-id check

## 0–3-space ID extractor

Command logic: `^ {0,3}\|\s*(S\d+)\s*\|` over each file; `comm -12` compares the sorted unique ID sets.

```text
LANE_IDS count= 203
STAGED_IDS count= 142
COMM -12:

```

No matching staged IDs appeared in lane SOURCES.

## Indented-row guard fixture

Fixture appended to a scratch copy of the registry:

```text
  | S330 |
```

Guard invocation used the scratch repository's baseline and fixture commits:

```text
python3 tools/sources-append-only.py --repo <scratch> --from 0d741fa888b8c656a39bce7fe379a2cdbfd3a962 --to e0853ed2e5a6acf66c34f61aad05e2a7489bd0b0
exit=2
error: e0853ed2e5a6acf66c34f61aad05e2a7489bd0b0:corpus/SOURCES.md:464: row-like line outside the parsed registry table; refusing to drop it
```

The guard caught the indented row-like ID collision (failed closed; exit 2).

## E04 within-scope duplicate URL check

For each specified staged ID, extracted the URL from its `source` cell and searched the lane `corpus/SOURCES.md` for that URL. Output:

```text
S330 https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/
  lane SOURCES matches: 0
S333 https://docs.sglang.io/docs/advanced_features/radix_eviction_policy
  lane SOURCES matches: 0
S334 https://docs.sglang.io/docs/advanced_features/session_radix_cache
  lane SOURCES matches: 0
S335 https://arxiv.org/abs/2312.07104
  lane SOURCES matches: 0
S346 https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md
  lane SOURCES matches: 0
S347 https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html
  lane SOURCES matches: 0
S363 https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/
  lane SOURCES matches: 0
```

No listed staged URL matched a URL in lane SOURCES. No tools were installed or updated.
