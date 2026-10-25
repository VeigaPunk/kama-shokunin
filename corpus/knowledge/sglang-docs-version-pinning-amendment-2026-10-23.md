# AMENDMENT (2026-10-25) to sglang-docs-version-pinning.md — the release pin is also the newest release tag

> This is an addition to `corpus/knowledge/sglang-docs-version-pinning.md`. It does not
> replace it; it closes the one question that file left open — whether `v0.5.22` is the
> newest release of `sgl-project/sglang` or a release behind one.

source: S352 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/advanced_features/radix_eviction_policy.mdx — §How eviction picks a victim, line 13 — source file at release tag v0.5.22 (6243 bytes, sha256 4ba2e6210d27ed1de045ae5b6aad9e475f9a7debdd64671178c04193c560876b), refetched 2026-10-25
source: S353 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/advanced_features/session_radix_cache.mdx — lead paragraph, line 9 "Session references are soft protection, not memory pins." — source file at release tag v0.5.22 (2820 bytes, sha256 0b50a3e5b8b5e97d3ce035801d18183ce1fa06dba9f6644f9c0f75bc0bf748cd), refetched 2026-10-25
source: S472 — `git ls-remote --tags https://github.com/sgl-project/sglang.git` — own-work tag inventory, run 2026-10-25T09:12:47Z with git 2.56.0, exit 0, 190 ref lines (166 tag names), output sha256 5585f602f71c4d4fa5a20125b2b8e4a1132a2d41abf511d7ef09c43a91d950f2; `refs/tags/v0.5.22` = tag object 35ce313293052f8362e0829e7512bc9bc3d336c9 peeling to commit baa9befa381511cd4d56f83980951e5a45fffc6d (evidence `.ufo/waves/round-38/assimilation/exec-tag-inventory/ls-remote-tags.txt`)
verified-at: 2026-10-25
recheck: 90d — re-run `git ls-remote --tags https://github.com/sgl-project/sglang.git | grep -oE 'refs/tags/v[0-9][^^]*$' | sed 's#refs/tags/##' | sort -V | tail -1` (expect `v0.5.22`; any later name reopens this entry) and `git ls-remote --tags https://github.com/sgl-project/sglang.git | grep -c 'refs/tags/v0.5.22$'` (expect 1) (ran 2026-10-25)
ground: the amended entry pinned both SGLang documentation files to release tag `v0.5.22` but could not show that it was the newest release, because the tag inventory could not be listed.

### The addition

The amended entry established that both SGLang documentation files are contained
unchanged in release tag `v0.5.22`, and recorded that the tag inventory itself could
not be listed. The git protocol answers that question directly, without the GitHub
REST API: `git ls-remote --tags` on the repository lists every tag ref the server
advertises. The twenty highest version tags, newest first by version sort, are:

`v0.5.22, v0.5.21, v0.5.20, v0.5.19, v0.5.18, v0.5.17, v0.5.16, v0.5.15.post1,
v0.5.15, v0.5.14, v0.5.13.post1, v0.5.13, v0.5.12.post1, v0.5.12, v0.5.11,
v0.5.10rc0, v0.5.10.post1, v0.5.10, v0.5.9, v0.5.8.post1`.

**`v0.5.22` is the newest release tag.** No `v0.5.23` or `v0.5.24` ref exists in the
inventory, so the HTTP 404s the amended entry recorded for those tags were the correct
answer, not a transient failure.

### The refused anchor

A REST-API reading of the same inventory —
`https://api.github.com/repos/sgl-project/sglang/tags?per_page=20` — was proposed as
this amendment's source (staged S360). It is refused. On this host on 2026-10-25 the
endpoint answered HTTP 403 "API rate limit exceeded" (`x-ratelimit-limit: 60`,
`x-ratelimit-remaining: 0`) on two independent requests, so its recheck cannot be run
where the lane runs it. The own-work row S472 supersedes it: the same question,
answered by a command that needs no token and no API quota, with its exit status and
output digest recorded.

Flip condition: S360 becomes admissible as a corroborating anchor if an unauthenticated
request to that endpoint from this host returns HTTP 200 with a `tags` array whose
newest version name agrees with the S472 recheck. S472 stays the primary anchor either
way.

### What the amendment changes

The amended entry could say the release pin was *valid* but not whether it was
*latest*. It is both. The pin is therefore anchored to the current release of the
SGLang documentation rather than to an older one, and the recheck now has a definite
expected value: the newest version tag should remain `v0.5.22` until a later release
appears, at which point the two pinned files are re-probed and a further correction
entry is opened.

This also strengthens the two source rows that cite SGLang at that tag: the tag is not
merely *a* release but the newest one.

### What this amendment does not establish

The tag inventory says which tags exist, not that the pinned files were unchanged
inside them; that is verified separately by the byte-for-byte comparison and the
live-page wording check recorded in the amended entry. A tag ref is also not a GitHub
Release object: the inventory shows `v0.5.22` is the highest version tag, not that a
release page was published for it. "Newest" here means the highest version under
`sort -V`, a sort order that ranks `v0.5.10rc0` above `v0.5.10`.

## Correction — round 40

The S472 output SHA-256 in the provenance row above is superseded: 5585f602f71c4d4fa5a20125b2b8e4a1132a2d41abf511d7ef09c43a91d950f2 does not hash the committed ls-remote output. Its correct digest is 5585f6027df2dbc4dbafd4979b61c218ffd94e8af99936733218e0ae989e50f2 (S474), independently reproduced by the current run in `.ufo/waves/round-40/c1/ls-remote-rerun.txt`. The old provenance line is retained as historical text; S474 carries the corrected evidence citation.
