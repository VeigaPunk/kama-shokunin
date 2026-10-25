# FetchS330 — vLLM v1 guide (`/usage/v1_guide/`, v0.19.1)

Seat: `L1Kama37.StripedMink` (round 37, w1). One read-only GET of the item URL; no other URL
fetched; no row appended; no corpus/knowledge/SOURCES/SCORECARD/LOG/lesson file touched; no
git/jj mutation; no pacman.

## Fetch receipt (single GET)

`curl -sSL -o v1_guide.html -w '%{http_code} %{url_effective} %{size_download} %{content_type} %{num_redirects}'`

| field | value |
|---|---|
| URL | `https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/` |
| effective URL | `https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/` (identical; `%{num_redirects}` = `0`, no redirect followed) |
| HTTP status | `200` |
| bytes downloaded | `435441` (`%{size_download}`) |
| on-disk size | `435441` bytes, `435329` decoded UTF-8 chars (full body, no truncation) |
| Content-Type | `text/html; charset=utf-8` |
| sha256 of saved bytes | `d0d8ecfef51ea729f37a653963a53903c259e3a241884e4d88e54a8954b85ad5` |
| `<title>` | `vLLM V1 - vLLM` |
| generator | `mkdocs-1.6.1, mkdocs-material-9.7.6` |
| saved bytes | `.ufo/waves/round-37/w1/out/StripedMink/v1_guide.html` (13 lines; the doc body is minified onto line 11, so byte/char offsets below are the precise locators) |

Retrieved 2026-10-25. No `http-equiv=refresh` in the bytes, so nothing client-side redirects it.

## Located statement A — "treats both prompt and output tokens the same way"

The exact string occurs **twice** in the saved bytes (once per section), always as a
`<div class="admonition note">` whose title is `Note`, with identical full text:

> vLLM V1’s unified scheduler treats both prompt and output tokens the same way by using a simple
> dictionary (e.g., `{request_id: num_tokens}`) to dynamically allocate a fixed token budget per
> request, enabling features like chunked prefills, prefix caching, and speculative decoding
> without a strict separation between prefill and decode phases.

(apostrophe is U+2019, `V1’s`)

**Occurrence A1** — char offset 420276 (line 11, col 418149).

- Section: `<h1 id=vllm-v1>vLLM V1</h1>` → `<h2 id=feature-support>Feature Support</h2>`.
- Position: the note closes the **Feature Support section intro**, immediately after the
  🟢 Functional / 🟡 In Progress / 🔴 Removed legend list and immediately before
  `<h3 id=hardware>Hardware</h3>`. No subheading of its own — cite as “Note admonition at the end
  of `#feature-support` intro, before `#hardware`”.

**Occurrence A2** — char offset 428549.

- Section: `<h1 id=vllm-v1>` → `<h2 id=feature-support>` → `<h3 id=features>Features</h3>`.
- Position: the same note immediately follows the Feature/Status table (last rows
  `GPU <> CPU KV Cache Swapping` 🔴 Removed, `Request-level Structured Output Backend`
  🔴 Removed) and immediately precedes `<h4 id=removed-features>Removed Features</h4>`. Cite as
  “Note admonition at the end of `#features`, before `#removed-features`”.

**Verbatim quote, ≤25 words (this clause is 18 words):**

> vLLM V1’s unified scheduler treats both prompt and output tokens the same way by using a simple dictionary

## Located statement B — "enabled by default whenever possible"

Exactly **one** occurrence, char offset 417926 (line 11, col 415799).

- Section: `<h1 id=vllm-v1>vLLM V1</h1>` → `<h2 id=differences-from-v0>Differences from V0</h2>`
  → `<h3 id=chunked-prefill>Chunked Prefill</h3>`, first (and only) paragraph of that H3.

**Verbatim quote, ≤25 words (20 words, the whole sentence):**

> Chunked prefill is enabled by default whenever possible, unlike in V0 where it was conditionally enabled based on model characteristics.

## Does the page carry a version marker?

**Yes, but only machine-readable in `<head>`; the rendered body carries no visible version text.**

- Line 1: `<link href=https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/ rel=canonical>` (offset 167).
- Line 11 head tail: `<meta name="readthedocs-version-slug" content="v0.19.1" />`,
  `<meta name="readthedocs-project-slug" content="vllm" />`,
  `<meta name="readthedocs-resolver-filename" content="/usage/v1_guide/" />`,
  `<meta name="readthedocs-http-status" content="200" />`.
- `<title>` is `vLLM V1 - vLLM` — no version string.
- The `<body>` contains **zero** occurrences of `0.19`; there is no `md-version` / `rst-versions`
  element in the served HTML. The version selector is injected at runtime by
  `<script async src="/_/static/javascript/readthedocs-addons.js">`, so a text-only reader of
  these bytes sees the version only via the canonical URL and the `readthedocs-version-slug` meta.

## Neighbouring observed facts (context for the C2 prefix-cache candidates)

Read from the same bytes, no second fetch:

- `#features` status table rows: `Prefix Caching 🟢 Functional`, `Chunked Prefill 🟢 Functional`,
  `FP8 KV Cache 🟢 Functional`, `Prompt Logprobs with Prefix Caching 🟢 Functional`.
- `#prompt-logprobs-with-prefix-caching` (h4): “While V1 supports passing prompt logprobs with
  prefix caching enabled, it no longer caches the logprobs. For a request requiring prompt
  logprobs, the engine will ignore the prefix cache and recompute the prefill of full prompt to
  generate the logprobs.”
- `#kv-cache-features` (h5, under `#removed-features`), list item, raw markup
  `<strong>GPU &lt;&gt; CPU KV Cache Swapping</strong>`: “with the new simplified core architecture,
  vLLM V1 no longer requires KV cache swapping to handle request preemptions.”
- **Negative fact:** the whole document contains exactly one `enabled by default` claim — the
  chunked-prefill one. The page never says prefix caching is on by default; it labels it only
  🟢 Functional. Any candidate entry must therefore not attribute a default-on prefix-cache claim
  to this page.

## Facts vs inference

- Observed: status 200, effective URL, redirect count 0, `%{size_download}`, on-disk byte count,
  sha256, Content-Type, `<title>`, generator, both occurrence offsets and counts, heading
  ids/levels/offsets, the version-marker tags, the body-level absence of `0.19`, the single
  `enabled by default` occurrence, and all quoted spans — read directly from the saved bytes.
- Inferred (marked, not load-bearing): A2's placement “end of `#features`” follows from offset
  428549 lying between the h3 `Features` and h4 `Removed Features` headings — verified by
  heading offsets, not by rendering.
- Unresolved / not pursued (out of item scope): whether the live site still serves this build
  (single GET only, no re-fetch); the page body itself states no release date or changelog for
  v0.19.1 beyond the head metadata.

## Bounds compliance

One read-only GET of the exact item URL. Writes confined to this report and the seat scratch dir
`.ufo/waves/round-37/w1/out/StripedMink/`. No row appended anywhere; no edits outside the named
report path. No tools needed installing this seat.
