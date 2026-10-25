# FetchS334 — SGLang Session-Aware Radix Cache page

Seat: `L1Kama37.ValuableMite` (round 37, w1). One read-only GET of the item URL; no other URL
fetched; no row appended; no corpus/knowledge/SOURCES/SCORECARD/LOG/lesson file touched.

## Fetch receipt (single GET)

| field | value |
|---|---|
| URL | `https://docs.sglang.io/docs/advanced_features/session_radix_cache` |
| effective URL | same (curl `%{url_effective}` identical; no redirect followed) |
| HTTP status | `200` |
| bytes downloaded | `277182` |
| on-disk size | `277182` bytes (`wc -c`; full body, no truncation) |
| saved bytes | `.ufo/waves/round-37/w1/out/FetchS334/sglang-session-radix-cache.html` (477 lines) |
| sha256 of saved bytes | `69d21ab9a22a1ffdb114cf9a4ef7e53b539ce6d8670b0eeef659b03ecd828258` |
| `<title>` | `Session-Aware Radix Cache` |

Content-Type was not captured: the single authorized GET wrote only the body (`curl -sS -o`), and
a header probe would be a second request. The body is HTML (documents `<meta charset>`, `<h1>`,
Mintlify markup). Retrieved 2026-10-25.

## Located statement — section

Page structure from the saved bytes: eyebrow `Advanced Features` + `<h1 id="page-title">` =
`Session-Aware Radix Cache` (line 446), then the lead paragraph, then the target sentence as its
own paragraph on **line 447**, then `<h2 id="enable-the-cache">` on line 448. The page has only
three H2s (`enable-the-cache`, `pass-and-close-the-session`, `eviction-behavior`, per both the
rendered headings and the in-page TOC) and no H3.

Section: **the page lead / overview paragraph directly under the H1, with no subsection
heading** — i.e. before `Enable the cache`. The TOC has no entry for it, so it cannot be cited
by anchor; cite it as “lead paragraph under `#page-title`, immediately before `#enable-the-cache`”.

Rendered markup at line 447:

```html
<span data-as="p">Session references are soft protection, not memory pins. Referenced KV can still be evicted when reclaiming unreferenced KV is insufficient.</span>
```

## Verbatim quote (20 words)

> Session references are soft protection, not memory pins. Referenced KV can still be evicted when reclaiming unreferenced KV is insufficient.

Preceded in the same lead block (line 446) by: “Session-aware radix caching improves cache hits
for long-lived, multi-turn workloads under memory pressure. It registers reusable KV to a session
and evicts unreferenced KV before KV still referenced by an active session.”

## Does the page say referenced KV can still be evicted?

**Yes — explicitly.** The quoted sentence states it affirmatively (“Referenced KV can still be
evicted when reclaiming unreferenced KV is insufficient”). Two further places in the served
bytes corroborate, without adding a second quote:

- `#eviction-behavior` table, Full attention row: eviction order is “Unreferenced nodes first,
  then referenced nodes with fewer session references, then the configured policy such as LRU”.
- Same table, SWA row: “Two LRU passes: unreferenced nodes first, then referenced nodes if more
  space is required”. Mamba row is the same two-pass shape.
- `#eviction-behavior` lead (line 472): “Device and host eviction use the same session
  preference.”
- `#pass-and-close-the-session` tail (line 470): “Closing removes the session’s references but does
  not immediately free its KV. The KV remains reusable and returns to the normal eviction order.”

Net: session references are a priority hint (referenced KV is evicted later, and by count of
references), not a pin. This is a session-lifetime/priority statement, not a guarantee that a
registered prefix survives memory pressure.

## Facts vs inference

- Observed: status, byte count, on-disk size, sha256, line numbers, heading ids/levels, TOC
  entries, quoted spans above — all read from the saved bytes.
- Inferred: none required. “Section = lead paragraph” is by document position (verified: line 447
  is bracketed by the H1 lead text at 446 and `<h2 id="enable-the-cache">` at 448); the TOC
  absence of an anchor for the lead is itself observed.
- Unresolved / not pursued (out of item scope): the served page does not name which SGLang
  version introduced `--enable-session-radix-cache`; no version string appears in the saved
  bytes' title or lead.

## Bounds compliance

One read-only GET of the exact item URL. Writes confined to this report and the seat scratch dir
`.ufo/waves/round-37/w1/out/FetchS334/`. No row appended; no git/jj mutation; no pacman; no tool
installs needed this seat.
