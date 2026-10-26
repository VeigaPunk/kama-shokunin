# Registry row draft — llama.cpp release b11906 (sourced claim / C1 newrow leg)

Id: `S486` is a proposal (highest id in `corpus/SOURCES.md` at base
0163fea2dab3f282ebd70c71da9ab5de4cedf733 and at my read of the working tree is
`S485`; `S486` is absent at base). The L1 assigns the final id, per seat S1Row's
brief. **The id must be three digits** (`| S###`): the frozen counter
`tools/round46-release-recheck-audit.py` parses ids with `^\| S\d{3}` and its
`newrow` leg needs a row whose id is absent at base, so a literal `S4NN` would
score `newrow=0`. The line below is the whole row, one line, 11 cells in the
`## Registry` header order (id | source | kind | tier | scope | anchor | teaches
| status | opened | recheck | used-by).

## Proposed line

| S486 | llama.cpp release b11906 — https://github.com/ggml-org/llama.cpp/releases/tag/b11906 (asset record: https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11906, captured byte-exact as `.ufo/waves/round-46/c1/release-b11906.json`, 69164 bytes, sha256 b9041d4af30892fea64767acdcc3de5b9452a2d01f0b0e6fedef6c18976da6d7) | docs | A | identity of the llama.cpp b11906 tag, its commit 4d71b42fd87db24b8b7c808c151b713aa4459cfd and the official Linux x64 CPU asset the round-46 population is re-verified against; not runtime behaviour | Quote, byte offset 1521 of the captured JSON (`/target_commitish`): `"target_commitish":"4d71b42fd87db24b8b7c808c151b713aa4459cfd","name":"b11906","draft":false,"immutable":false,"prerelease":true`. That commit is the `refs/tags/b11906` ref (`git ls-remote --tags` 2026-10-26T19:57:59Z) and the object the b11889..b11906 diff is taken from. Published 2026-10-26T19:45:36Z, created 2026-10-26T14:18:45Z, updated 2026-10-26T19:49:05Z, Pre-release. Asset `llama-b11906-bin-ubuntu-x64.tar.gz` size 22478121, digest sha256:064ade6220799fd9e7b1804b574f5f92c38dde358cc987c6b8283cfaeb1eeef3. 17 commits and 65 files between b11889 d854d98bae598388ecea1ed84396587e5edc326d and b11906; b11907 (4b851fbee) was already tagged at 2026-10-26T19:57:59Z and its release object still returned HTTP 404 at 2026-10-26T19:58:14Z | Every holds, holds-reworded, drifted and removed verdict in registry/release-recheck-b11906.tsv is anchored to this tag-to-commit pair, this file path set and this GitHub-computed asset digest; the release object is mutable (`prerelease` true, `immutable` false, `updated_at` five minutes after `published_at`) and the tag already had a successor, so the ledger cites the commit and the digest, never the tag alone | mined | 2026-10-26 | on-release | registry/release-recheck-b11906.tsv |

## Cell-by-cell intent

1. `S486` — proposed id, L1 assigns (see above).
2. source — the release page plus its asset record API URL, with the local
   byte-exact capture named so a reader can re-derive every number below.
3. kind `docs`; 4. tier `A` — matches the precedent row S038 (b11755 release
   identity), which is the same claim shape one release cycle back.
5. scope — release identity only: tag, commit, Linux x64 CPU asset. Runtime
   behaviour is out of scope here (S041/S046/S055 own live receipts).
6. anchor — a single verbatim, unique, offset-located quote from the release
   JSON; the tag ref the commit is read from; the timestamps; the asset
   `size`/`digest`; the b11889..b11906 extent; and the successor-tag caveat.
7. teaches — what the ledger actually relies on, plus the mutability warning
   that makes the digest (not the tag) the identity.
8. status `mined`; 9. opened `2026-10-26`; 10. recheck `on-release` (a release
   tag is a release event, like S038 and every other `on-release` row);
11. used-by — the C1 ledger this row is the anchor for.

## Checks I ran on this text

- quoted fragment is verbatim and unique in the captured JSON:
  `raw.find(q)` = 1521, `raw.count(q)` = 1;
  quoted material = 1 whitespace-separated token, far under 25 words.
- the row contains both `b11906` and
  `4d71b42fd87db24b8b7c808c151b713aa4459cfd` (the counter's `newrow` test).
- cell count = 11 when split on `|`; single physical line; every number in it
  re-derived from `release-b11906.json`, `ls-remote-llama.cpp.txt`,
  `commits-b11889-b11906.txt` and `diffstat-b11889-b11906.txt`.
