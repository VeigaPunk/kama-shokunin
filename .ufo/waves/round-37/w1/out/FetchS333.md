# FetchS333 — SGLang radix eviction policy page

## Fetch receipt (one read-only GET)
- URL: https://docs.sglang.io/docs/advanced_features/radix_eviction_policy
- Method: single `curl -sS` GET (one URL, no retries, no other URLs)
- HTTP status: **200**
- Bytes downloaded: **296606** (`%{size_download}`); on-disk size 296606
- Content-Type: `text/html; charset=utf-8`; `server: Vercel`; `date: Sun, 25 Oct 2026 07:56:20 GMT`
- Saved bytes: `.ufo/waves/round-37/w1/out/FetchS333/page.html` (+ `headers.txt`)
- sha256 of saved bytes: `0cf0de212514080ce4ce9cf6c1261c8399e00bfe61e54dc3d230a7752073825f`
- `<title>`: `Radix Cache Eviction Policies - SGLang Documentation`

## Anchor
Page H1 `Radix Cache Eviction Policies`; section H2 **`How eviction picks a victim`**
(id `how-eviction-picks-a-victim`), saved-file lines 447–450. The phrase occurs twice in the
bytes — once in the rendered article (`page.html:449`) and once in the embedded RSC payload
(offset 263695, same sentences) — so it is **one** logical statement, not two.

Rendered section text (saved-file lines 448–450):

> Eviction only ever considers **evictable leaves**: nodes whose KV is present, unlocked (no in-flight request holds them), and not shadowed by a child that still holds KV. The root is never evictable.
>
> The policy scores each candidate and the **lowest score is evicted first**. Once a leaf is evicted, its parent may become a leaf and re-enter the candidate set, so eviction walks a branch from its tip toward the root.
>
> A policy only scores. It does not decide how much to free, and it cannot pin KV in memory — a node protected by the policy is still evicted if reclaiming everything else is not enough.

## Verbatim quotes (section: `How eviction picks a victim`)

Quote A — 12 words:
> The policy scores each candidate and the lowest score is evicted first.

Quote B — 21 words (the candidate conditions; the full sentence is 27 words, over the cap,
so the sentence's clause is quoted — verbatim contiguous substring of line 448):
> nodes whose KV is present, unlocked (no in-flight request holds them), and not shadowed by a child that still holds KV

Quote C — 5 words (same line, the root exclusion):
> The root is never evictable.

HTML markup of the quoted clause: `Eviction only ever considers <strong>evictable leaves</strong>: nodes whose KV is present, unlocked (no in-flight request holds them), and not shadowed by a child that still holds KV.` — the `<strong>` sits before the quoted clause, so Quote B is uninterrupted rendered text.

## Candidate conditions, as stated
A node is an *evictable leaf* (the only thing eviction considers) iff all of:
1. its KV is present,
2. it is unlocked — no in-flight request holds it,
3. it is not shadowed by a child that still holds KV.

Plus: the root is never evictable. Ordering: lowest score first; evicting a leaf can make
its parent a leaf and re-enter the candidate set, so eviction walks a branch tip→root. A policy
only scores: it neither sets how much to free nor pins KV against reclamation.

## Version pin
**No version pin on the page.** Evidence:
- Zero occurrences of the substring `versions` anywhere in the served bytes, and zero `v0.x`-style release tokens; `navMaps.firstHrefInVersion` is `{}` (empty), i.e. no versioned nav exists for this doc.
- No version selector/badge element and no "since vX" prose in the article.
- The only identifiers are build-time/deployment ones, not content versions: `x-served-version: dpl_849ArpqvBiCczQiT1Y1stNGpbqHT`, `x-mintlify-client-version: 0.0.3965`, `x-mint-proxy-version: 1.0.0-prod`.
- Page-level freshness metadata exists but is not a version pin: `"lastModified":"2026-10-24T12:16:03.909Z"`, `"originalFileLocation":"docs/advanced_features/radix_eviction_policy.mdx"`.

Caveat for any citation built on this page: because nothing pins a release, a later
`kama` re-read can legitimately differ; the sha256 above is the byte identity to cite.

## Scope note
No row appended anywhere (`corpus/lessons/round-37.md`, knowledge files, `corpus/SOURCES.md`
all untouched); no lane file other than this report and the two scratch files in
`.ufo/waves/round-37/w1/out/FetchS333/` written. Only one HTTP GET was issued.
