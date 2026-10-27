# Item 1 — id collision check (kama, round 50, seat X1Assimilation, 2026-10-26)

Recipe (fleet `scripts/hyaku/lane-addendum.md` lines 388-394), run with
`A=.ufo/waves/round-50/X1Assimilation`, `LC_ALL=C`:

    grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' <lane>/corpus/SOURCES.md \
      | grep -oE 'S[0-9]+' | sort > "$A/reg-ids"
    grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' /home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md \
      | grep -oE 'S[0-9]+' | sort > "$A/staged-ids"
    comm -12 "$A/reg-ids" "$A/staged-ids" > "$A/collisions"

Measurement (lane read at its working tree, 2026-10-26):

    reg-ids     239   (unique; no in-file duplicate)
    staged-ids  142   (unique; S330..S471)
    collisions    9   NON-EMPTY

    S330 S333 S334 S335 S346 S347 S352 S353 S363

## Every collision is a row the lane already holds under that same id

For each of the 9: the lane registry row exists, is `mined`, and carries the
same document URL as the staged row. The staged copies also fail the census
shape: each splits into 12 cells, because the staged `recheck` cell carries an
escaped pipe from its `curl … \| grep -c …` re-verify command (census E01).

| id | lane row (corpus/SOURCES.md) | lane status | document | staged cells |
|---|---|---|---|---|
| S330 | line 216 | mined | https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/ | 12 |
| S333 | line 217 | mined | https://docs.sglang.io/docs/advanced_features/radix_eviction_policy | 12 |
| S334 | line 218 | mined | https://docs.sglang.io/docs/advanced_features/session_radix_cache | 12 |
| S335 | line 219 | mined | https://arxiv.org/abs/2312.07104 | 12 |
| S346 | line 220 | mined | https://github.com/AaronYang238/llm/blob/35b83cee…/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md | 12 |
| S347 | line 221 | mined | https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html | 12 |
| S352 | line 223 | mined | https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/advanced_features/radix_eviction_policy.mdx | 12 |
| S353 | line 224 | mined | https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/advanced_features/session_radix_cache.mdx | 12 |
| S363 | line 222 | mined | https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/ | 12 |

The lane rows are the adopted, re-anchored versions. Example S330:

    lane   §Feature Support (admonition note) — "vLLM V1's unified scheduler treats both prompt and output tokens the same way …"
    staged §Scheduler — "V1's unified scheduler treats both prompt and output tokens the same way"

Round-37's lesson (`corpus/lessons/round-37.md` lines 59-70) records adopting
S330, S333, S334, S335, S346, S347 and S363 from this same package by "the
staged ids carried by the same documents"; S352/S353 were adopted later. So the
collision set is exactly the adoption history, and the staged package was never
pruned after the adoptions.

## Action

Adopt nothing for these 9 ids: they are already-adopted documents, so the id
follows the document and no renumber is required (lane-addendum line 399 — an
id shifted by arithmetic breaks the next citation). A later merge must drop the
9 rows from the staged set, not renumber them.

## Second collision surface the id check cannot see

142 staged rows; 34 carry no URL (own-work evidence artifacts). Of the 108 that
do, 33 cite a document the lane already holds: the 9 above **plus 24 already
adopted under a different lane id**:

    S331->S196  S332->S327  S340->S205  S341->S206  S344->S209  S358->S223
    S364->S329  S365->S329  S371->S328  S377->S329  S378->S478  S394->S479
    S396->S329  S420->S004  S421->S029  S430->S480  S431->S481  S440->S004
    S441->S481  S454->S004  S460->S016  S462->S004  S463->S481  S471->S016

Four of those (S331, S340, S341, S344) also repeat the lane row's `scope` cell
verbatim, which the census grades E04 (`duplicate url … within scope`) unless
`teaches` carries a `supersedes S…`. Measured below in item 4.
