# S347 fetch receipt — vLLM v0.9.0 Automatic Prefix Caching

Seat: `L1Kama37.FamousTarsier` (round 37, w1).
Mode: read-only GET of the single URL in the item; nothing else fetched. No row appended anywhere.

## Fetch

| field | value |
|---|---|
| URL | `https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html` |
| effective URL | `https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html` (no redirect) |
| HTTP status | `200` |
| bytes downloaded | `59059` |
| on-disk size | `59059` bytes (full body, no truncation) |
| content-type | `text/html; charset=utf-8` |
| sha256 | `4e8ce91df7f3706981efb081c35b56b455560ee3eef0884b7f2adf8012def82f` |
| saved bytes | `.ufo/waves/round-37/w1/out/FamousTarsier/prefix_caching_v0.9.0.html` (1691 lines) |

Retrieved 2026-10-25. Rendered docs page; the quoted text is present in the served HTML itself
(`<p>`, `<blockquote>`, `<h3>` elements), so no JS execution or second request was needed.

## Located items

### 1. "hash-based approach" — anchor `#automatic-prefix-caching`

Line 1444, paragraph directly under `<h1 id="automatic-prefix-caching">` (page has no subheading
between the H1 and this paragraph; line 1443 is the preceding "prefix caching is almost a free
lunch" paragraph). Verbatim, 17 words:

> vLLM chooses a hash-based approach. Specifically, we hash each kv-cache block by the tokens in the block

### 2. Note 2 — collision-free caveat + SHA256 advice — anchor `#automatic-prefix-caching` (blockquote, lines 1457–1461)

Note 2 begins at line 1459; the SHA256 support/perf sentence continues at line 1460.
Verbatim with one elision (`...` dropping "Theoretically it's still possible for the different
prefix tokens to have the same hash value."), 22 words:

> not 100% collision free ... in a multi-tenant setup, we advise to use SHA256 as hash function instead of the default builtin hash

Verification note: the first fragment and the second fragment both match the page's tag-stripped
rendered text; the second fragment spans a `<strong>` element boundary within line 1459 (`<strong>`
opens before "in a multi-tenant setup" and closes after "SHA256"), so a raw-byte substring match
fails on markup only, not on wording. Exact sentence in rendered order is: "To avoid any hash
collisions in a multi-tenant setup, we advise to use SHA256 as hash function instead of the
default builtin hash."

Supporting clause in the same Note 2 paragraph, stated separately rather than quoted beyond the
25-word budget: SHA256 is "supported since vLLM v0.8.3", must be enabled with a command line
argument, and costs "about 100-200ns per token (~6ms for 50k tokens of context)". The
preceding bullet (line 1454) gives the mild mitigation: including exact block tokens "to reduce
potential hash value collision".

### 3. Eviction (LRU) — anchor `#eviction-lru`

Heading at line 1603: `<h3 id="eviction-lru">Eviction (LRU)</h3>`. Lead paragraph at line 1604,
verbatim, 20 words:

> When the head block (least recently used block) of the free queue is cached, we have to evict the block

Directly following ordered list (lines 1606–1608), summarized (not quoted): pop the block from the
head of the free queue, remove the block ID from the Cache Block, remove the block hash.

## Facts vs inference

- Observed: status, byte count, content-type, sha256, line numbers, anchors, quoted spans above —
  all read from the saved bytes.
- Inferred: none required for the three items. Anchor attribution for item 1 is by document
  position (no intermediate heading element), verified by reading lines 1430–1465 raw.
- Unresolved: the served page does not state the CLI flag name for enabling SHA256; not pursued,
  out of item scope.

## Bounds compliance

One read-only GET of the named URL only; write confined to this report and the seat scratch dir
`.ufo/waves/round-37/w1/out/FamousTarsier/`. No corpus/knowledge/SOURCES/SCORECARD/LOG/lessons
edits, no row appended, no git/jj mutation, no pacman, no installs needed this seat.
