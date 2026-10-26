# SOURCES anchor draft — pinned stories260K.gguf revision (round 47, X2Revision)

## One-line anchor (the `anchor` cell)

`resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf` answers 302 with `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81` and `x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"` (`x-linked-size: 1185376`), and the downloaded bytes are sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` and `cmp`-identical to `resolve/main` and to `resolve/96f460f9c1e2ca43d0adc1c682b832525a2c0ea3` on 2026-10-26; the blob (git `941cd12cc9e7e7b83944e83ab5887cbed28d2f0f`) was written by `96f460f9`, whose parent `22027b1a` served `68c694e7584c358446e8ec05c4648c72382aa3457b56443e35a6fecf55b429d2`, and `688f41dd` before it served `047bf46455a544931cff6fef14d7910154c56afbc23ab1c5e56a72e69912c04b` — the same path moved through three byte strings, 2025-09-26 to 2025-10-28.

## Copy-ready table row (id provisional: next free after S487)

| S488 | Hugging Face ggml-org/models-moved — tinyllamas/stories260K.gguf at revision 499bc8821c6b12b4e53c5bffcb21ec206f212d81 — https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf | dataset | A | file identity of the CI fixture weights kama serves in its live harness, addressed by an immutable revision instead of the moving `main` ref; identity only, not model quality or behaviour | resolve/<commit> answers 302 with x-repo-commit 499bc8821c6b12b4e53c5bffcb21ec206f212d81, x-linked-etag "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d", x-linked-size 1185376; bytes sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d and cmp-identical to resolve/main on 2026-10-26; blob git 941cd12cc9e7e7b83944e83ab5887cbed28d2f0f written by 96f460f9 (parent 22027b1a = 68c694e7…, 688f41dd = 047bf464…) | Names the pin by revision; a replay that records this URL re-acquires the same bytes without depending on `main`, while rule R417-2-d still refuses other bytes (measured: shifted revision, exit 2) | mined | 2026-10-26 | every round | corpus/knowledge/llamacpp-loading-lifecycle.md |

## Relationship to the existing S039 row (SOURCES.md:51)

S039 already records the same identity — repo commit `499bc8…`, file commit `96f460f9…`,
size 1185376, LFS sha256 `270cba1b…` — and even says "the same path held three different
byte strings on 2025-10-28, so the digest, not the path, identifies it". The pinned row above
adds only the *actionable* part: the URL form that makes the identity reachable without the
moving ref. If the lane prefers to keep one row per source, append to S039's `anchor` cell
instead of adding S488:

`; deliverable URL: https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf (302, x-repo-commit 499bc8…, x-linked-etag "270cba1b…", 1185376 bytes, cmp-identical to resolve/main 2026-10-26)`
