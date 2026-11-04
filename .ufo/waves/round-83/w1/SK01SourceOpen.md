# SK01 — six sources opened, anchor extracts built (round 83 w1)

Seat `SK01SourceOpen`, leaf scout: read-only over the network plus writes inside this seat dir. Access date 2026-11-04.

- Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` — **read-only**: no production file written, no `git add`/commit/checkout, no mutating `jj`, no sibling repo read, fleet root untouched.
- Revision provenance (read-only): dispatch base `30d8eac394a8714fad3dc792b74a45a25b4366a2`, sealed C2 `b1ba614b51255a3dcfe3e0946f32f8e31bd65c09`, lane tip `git -C <lane> rev-parse master` → `eae884adc80a6a2de2ce93fccd89b913020eb574`. No graded claim depends on the tip.
- Scratch `S=/fast/scratch/hyaku/kama-r83/SK01SourceOpen` held every fetch plus the two builder scripts; deleted before yield, receipts copied into this seat dir first.
- No tool installed or upgraded (nothing needed): no pacman, no `uv tool`, no PATH write.

## 1. Fetch receipts — each row is a fetch this seat performed

Command shape, one per URL: `curl -sS -L --max-time 120 -o <S>/<id>.body -w '%{http_code} %{size_download}' <url>` → exit 0 for all six.

| id | ref | HTTP | bytes | sha256 of body | lines | anchor line | quote line |
|---|---|---|---|---|---|---|---|
| S566 | b12110 | 200 | 136429 | `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137` | 2620 | 480 | 482 |
| S567 | v0.5.23 | 200 | 18295 | `3ed171186990d6a67a1d950f1d491fe83986cf539bf24d1e65b95481e7d87a3c` | 471 | 108 | 111 |
| S568 | v0.5.22 | 200 | 17359 | `209087c3d30dc25cbcdb3b8a31b0453089d83e0fdfa39d317ab54646787e11eb` | 467 | 108 | 109 |
| S569 | v0.33.0 | 200 | 13916 | `67ee4e2b7bc23d40e9b366e4a9053ae4ecd0925ddef51f412ac5c16b9dc83a61` | 236 | 3 | 3 |
| S570 | v0.32.0 | 200 | 13916 | `67ee4e2b7bc23d40e9b366e4a9053ae4ecd0925ddef51f412ac5c16b9dc83a61` | 236 | 3 | 3 |
| S571 | live (docs 2.56.0) | 200 | 82763 | `cc28e3b8008d1d3023159409728f6a64fb18510de212818fa7b3c654f230e187` | 2847 | 2146 / 2579 | 2146 / 2579 |

Quotes, verbatim and ≤ 25 words (counts 11 / 18 / 8 / 16 / 16 / 17 + 19):

- S566: ``This endpoint is public (no API key check). `/v1/health` also works.``
- S567: ``- `/ready`: Returns 200 when the server accepts new requests; 503 while starting, paused, unhealthy, or shutting down.``
- S568: ``- `/health`: Check the health of the server.``
- S569 / S570: `Prefix caching kv-cache blocks is a popular optimization in LLM inference to avoid redundant prompt computations.`
- S571: `Annotates each line in the given file with information from the revision which last modified the line.`
- S571 (porcelain): `option can be used to output full commit information for each line, allowing simpler (but less efficient) usage like`

Every quote was machine-checked twice — it occurs on its declared source line (`quote_occurs_at_line`) and inside the committed extract (`quote_occurs_in_extract`); both true for all seven rows.

## 2. Anchor extracts — `anchors/`, ready for the C3 register

Header grammar, line 1 of every file: `# url=<url> sha256=<64-hex of the body bytes after this line> ref=<ref> lines=<a>-<b>`

| file | ref | source lines | body lines | header digest |
|---|---|---|---|---|
| `anchors/S566.md` | b12110 | 480-492 | 13 | `b9a260db8f67baf6bd3a430abef508e06d973e5318811b0db1bb4408cfdedc83` |
| `anchors/S567.md` | v0.5.23 | 108-126 | 19 | `c8bd5bfd08d2d65e53af242ebb4ea783930c86f88ac697076c370fd21ba6a4cf` |
| `anchors/S568.md` | v0.5.22 | 108-124 | 17 | `10e5aee63d80f368137ace47183048e52f55c78ba1ce45b528110f0ddc89613e` |
| `anchors/S569.md` | v0.33.0 | 1-5 | 5 | `d1498873b49ae26d70b3b0b07c77df1f958685e325cfaf51335eb41b866c4ad1` |
| `anchors/S570.md` | v0.32.0 | 1-5 | 5 | `d1498873b49ae26d70b3b0b07c77df1f958685e325cfaf51335eb41b866c4ad1` |
| `anchors/S571.md` | live | 2143-2147 | 5 | `ecde75b71debe1a33c21df9d38906464d7f0f488669dd7498a4add504277239e` |
| `anchors/S571.line-porcelain.md` | live | 2573-2580 | 8 | `59ac405de24b34ae22c2523d83ad0ac8f47d8ea9362b937fb3211aa167bbe67b` |

Digest convention honoured literally: the header `sha256` is the sha256 of the extract's own bytes after line 1. `check-extracts.py` (two lines, globbing `anchors/S*.md`) recomputes and compares → `OK` ×7, exit 0. A third check compared each extract body with its source line range byte for byte: all seven identical (435 / 776 / 396 / 745 / 745 / 296 / 699 B).

The six extracts the C3 register reads are `S566.md`-`S571.md`. `S571.line-porcelain.md` is supplementary: S571 names two anchors (the blamed-commit definition and `--line-porcelain`), so the second anchor is digest-verified rather than only quoted. `S571`'s header uses `ref=live` because `https://git-scm.com/docs/git-blame` carries no ref segment (the page serves the current manual, 2.56.0 in its version list); the dispatch pins no ref for S571.

## 3. Identity

- **S566 (b12110) vs S563's b12103 read** (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SK01PinRecon/artifacts/llama-b12103-README.md`): `cmp -s` → exit 0, **byte-identical, 0 differing bytes** — 136429 B both, sha256 `eafc1b53…a137` both, 2620 lines. The newest llama.cpp tag carries the same README bytes as the tag S563 recorded, so the `/health` anchor state did not move across b12103 → b12110.
- **S569 (v0.33.0) vs S570 (v0.32.0)**: `cmp -s` → exit 0, **byte-identical, 0 differing bytes** — 13916 B both, sha256 `67ee4e2b…3a61` both. The pinned side and the newest side carry the same sentence, so C3 relation 5's `holds` follows from the bytes alone.
- Extras, same method: S567 and S568 are `cmp`-identical to `sglang-v0.5.23-native_api.mdx` and `sglang-v0.5.22-native_api.mdx`, and S569 is identical to `vllm-v0.32.0-prefix_caching.md` — these six bodies are the same bytes the lane already cites.
- S567 vs S568 differ by **+936 B** (18295 vs 17359): v0.5.23 adds exactly two rows under `## Health Check` (`/ready` at 111, `/ping` at 112); the rest of the section is byte-identical.

## 4. Findings

1. **S566 heading form (matters for a byte-exact recheck quote).** The literal string `### GET /health` does **not** occur in the b12110 README: source line 480 is ``### GET `/health`: Returns health check result`` — the path is backticked and the line carries a trailing description. The unbackticked path appears only at source line 2560, as ``- `GET /health` `` in the endpoint index. A recheck row quoting `### GET /health` verbatim reads absent, i.e. falsely `drifted`; quote the backticked heading or the sentence at 482.
2. **S568 has no `/ready` and no `/ping`** anywhere in the file (checked file-wide, not just the section); S567 adds both. That is the whole SGLang delta between the pinned and newest refs.
3. **S571 `--line-porcelain` is present** — OPTIONS synopsis 2289, prose 2579. The blamed-commit definition is DESCRIPTION 2146-2147, broken after `which`, so a byte-exact quote must cross the newline or take the line-2147 fragment; `sources.json` records `quote_match: line-span-normalized` for that row.
4. S569's anchor is the page's first descriptive sentence, naming both what is stored (kv-cache blocks) and what it buys (no redundant prompt computation) — usable as the register's pinned-side quote unedited.

## 5. C3 hints (first-hand only)

Relation 1 (`llama.cpp b11755`), 4 (`sglang v0.5.22`), 5 (`vllm v0.32.0`): the pin-side sentence occurs verbatim in the newest-side extract at source lines 482 / 109 / 3 → `holds`. Relation 2 (`39febd2a`, source row S555) is **not** checked here — that document was not fetched by this seat and S566 does not stand in for it. Relation 3 (`llama.cpp b7200`) remains `ungraded`, as the plan expects.

## 6. Limits

- S571's `ref` is `live`, not a tag: the URL offers no ref, so provenance is the access date plus the page's own version list; a ref-pinned URL would need a fresh extract.
- No relation-register row was written (that is the register seat's file); `registry/pin-recheck-rows.tsv` still did not exist at this seat's end.
- All six bodies arrived as HTTP 200 without redirect.
