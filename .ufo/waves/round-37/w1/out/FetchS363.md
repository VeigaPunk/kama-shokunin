# FetchS363 — vLLM 0.32.0 prefix caching design page

## Fetch receipt (one read-only GET)
- URL: https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/
- Method: single `curl -sS` GET (no headers, no retries, no other URLs)
- HTTP status: **200**
- Bytes downloaded: **215347**
- Content-Type: `text/html; charset=utf-8`
- Saved bytes: `.ufo/waves/round-37/w1/out/FetchS363/page.html`
- sha256 of saved bytes: `e41f1046f6df35179a5b00a7face1f94c4fc86b0805a8689c0091f6d37864f72`
- `<title>`: `Automatic Prefix Caching - vLLM`

## Anchor
Page H1 `Automatic Prefix Caching` (id `automatic-prefix-caching`), in the hash-key bullet list
(`Parent hash value` / `Block tokens` / `Extra hashes`), admonition titled `Note 2` at saved-file
lines 14035–14039.

## Verbatim quote (13 words)
> As of v0.11, the default hashing algorithm is `sha256`, which addresses collision risks.

(HTML: `As of v0.11, the default hashing algorithm is <code>sha256</code>, which addresses collision risks.`)

## `--prefix-caching-hash-algo` flag
Present. Same Note 2 block, immediately after the quoted sentence, at saved-file lines 14036–14039:

> For `vllm serve`, you can control the hashing algorithm via `--prefix-caching-hash-algo`:

Flag value list as served: `sha256` (default), `sha256_cbor`, `xxhash`, `xxhash_cbor`.

## Scope note
No row appended anywhere; no lane file other than this report touched. Staged package and
`considerthese/` untouched.
