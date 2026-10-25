# Pinning SGLang documentation that carries no version marker

source: S352 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/advanced_features/radix_eviction_policy.mdx — §How eviction picks a victim (line 13) — source file at release tag v0.5.22 of sgl-project/sglang (6243 bytes, sha256 4ba2e6210d27ed1de045ae5b6aad9e475f9a7debdd64671178c04193c560876b)
source: S353 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/advanced_features/session_radix_cache.mdx — lead paragraph (line 9) — source file at release tag v0.5.22 of sgl-project/sglang (2820 bytes, sha256 0b50a3e5b8b5e97d3ce035801d18183ce1fa06dba9f6644f9c0f75bc0bf748cd)
verified-at: 2026-10-25
recheck: 90d — run `for f in radix_eviction_policy session_radix_cache; do curl -fsSL https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/advanced_features/$f.mdx | sha256sum; done; git ls-remote --tags https://github.com/sgl-project/sglang.git "refs/tags/v0.5.22^{}" | cut -f1; curl -fsSL https://docs.sglang.io/docs/advanced_features/radix_eviction_policy | grep -c "lowest score is evicted first"; curl -fsSL https://docs.sglang.io/docs/advanced_features/session_radix_cache | grep -c "Session references are soft protection, not memory pins"` (expect sha256 `4ba2e6210d27ed1de045ae5b6aad9e475f9a7debdd64671178c04193c560876b` and `0b50a3e5b8b5e97d3ce035801d18183ce1fa06dba9f6644f9c0f75bc0bf748cd`, peeled commit `baa9befa381511cd4d56f83980951e5a45fffc6d`, and both live-page greps = 2)
ground: the round-37 coverage-map row for `knowledge/kv-cache-reclamation-models.md` rests its SGLang eviction and session-reference claims on S333 and S334, which cite the published `docs.sglang.io` pages with no revision, so the map recorded what those pages say but not which version of them was read; this entry supplies that version anchor and adds no new serving behaviour.

### The problem

`docs.sglang.io` publishes these pages with no version indicator in the URL or the
body. A row that cites the published URL therefore points at content that can change
under the reader, and the recheck can only compare wording, not identity.

### The available pin

The repository keeps the page source under `docs/docs/advanced_features/`. Both files
are contained unchanged in release tag `v0.5.22` of `sgl-project/sglang`, which is a
stable, immutable identifier:

| document | branch-commit pin | release pin | size at both | live page |
|---|---|---|---|---|
| `radix_eviction_policy.mdx` | commit `77091cea…` | tag `v0.5.22` | 6243 bytes | same wording |
| `session_radix_cache.mdx` | commit `d34f7b23…` | tag `v0.5.22` | 2820 bytes | same wording |

Tag `v0.5.22` is also the release the lane already holds a row for, so the new pin
introduces no new upstream coordinate to track. Tags `v0.5.23` and `v0.5.24` were
probed for both paths and return HTTP 404, so `v0.5.22` is the reachable release
containing these files.

### What this entry does not establish

The two files are identical at the branch commits and at tag `v0.5.22`, which shows
the tag is a valid anchor for what was read — it does not show that the published
pages will never change again. A later recheck should re-run the comparison and, if the
live page has moved, open a further correction entry rather than editing this one.

The "immutable" property of the tag is a release convention, not something Git
enforces: a tag can be deleted and re-created. On 2026-10-25 `git ls-remote --tags`
resolved `v0.5.22` to commit `baa9befa381511cd4d56f83980951e5a45fffc6d`. The recheck
compares that peeled commit and the SHA-256 of both files, so it detects a moved tag
and any change to the pinned content, including a change that keeps the byte size.

The live-page half of the recheck searches each page for one anchor sentence. A match
shows that sentence is still published; it does not show that the rest of the page
has the same wording, and tables and code blocks are not compared at all. This entry
does not say which release is the newest; that is the companion amendment's claim.
