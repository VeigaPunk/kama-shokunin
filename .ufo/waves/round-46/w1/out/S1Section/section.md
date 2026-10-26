## Round-46 release re-verification (llama.cpp b11906, appended 2026-10-26)

Trigger: the lane pin is unchanged (`registry/engine-pins.tsv` row `llama.cpp ... b11755 S038`; 131 `bN` tags sort above it in the sample below) while the release feed moved 17 commits past the b11889 recheck. `git ls-remote --tags https://github.com/ggml-org/llama.cpp.git` at 2026-10-26T19:57Z lists line 1428 `4d71b42fd87db24b8b7c808c151b713aa4459cfd refs/tags/b11906` (copy `.ufo/waves/round-46/c1/ls-remote-llama.cpp.txt`, 8211 lines; 14 `bN` tags sort above b11889 — b11890, b11895–b11907), and `gh api repos/ggml-org/llama.cpp/releases/tags/b11906` returns `tag_name` b11906, `target_commitish` `4d71b42fd87db24b8b7c808c151b713aa4459cfd`, `published_at` 2026-10-26T19:45:36Z, `prerelease` true, `draft` false, 36 assets (JSON 69164 bytes, sha256 `b9041d4af30892fea64767acdcc3de5b9452a2d01f0b0e6fedef6c18976da6d7`, copy `.ufo/waves/round-46/c1/release-b11906.json`). Release: b11906 = `4d71b42fd87db24b8b7c808c151b713aa4459cfd`, 17 commits after b11889 = `d854d98bae598388ecea1ed84396587e5edc326d` (`git rev-list --count d854d98bae598388ecea1ed84396587e5edc326d..4d71b42fd87db24b8b7c808c151b713aa4459cfd` = 17; commit list `.ufo/waves/round-46/c1/commits-b11889-b11906.txt`, diffstat `.ufo/waves/round-46/c1/diffstat-b11889-b11906.txt`: 65 files, +4323/−2128). The release is registered as a source opened this round by a new registry row (id above S485, modelled on S482) whose cells carry `b11906` and `4d71b42fd87db24b8b7c808c151b713aa4459cfd` — the counter's new-row leg.

Population (frozen in `.ufo/waves/round-46/preregistration.json`, unchanged from round 44): the 91 registry rows of this file at base `0163fea2` that carry recheck `on-release`, status `mined` or `queued`, and a source on a `ggml-org/llama.cpp` file pinned to a commit — 89 at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (b11755) by URL, S001 at `c0fd78626405c6d9b934efef0ec7291fcc20e3d6` and S015 at `ad1b88ca0d37a2171efba1c04f1a3531c78f1b52` (master at open, commit in the anchor). The base registry yields exactly these 91 ids and no others under `tools/round46-release-recheck-audit.py`'s population rule.

Ledger: `registry/release-recheck-b11906.tsv`, header `id	path	pin_commit	release	pin_blob	release_blob	changed	pin_lines	release_lines	witness_pin	witness_new	verdict	note`, one row per population id, every field re-derived by the counter from the lane and the upstream clone. Both blobs are `git rev-parse <commit>:<path>` at the pin and at b11906 (`-` when the path is absent at the release); `pin_lines` and `release_lines` are equal-length comma lists of 1-based inclusive ranges of at most 80 lines; a range pair is text-equal when its stripped non-blank lines, joined, are equal. `holds` needs `changed` 1 and every pair text-equal; `holds-reworded` needs no `-` element and at least one unequal pair with the anchored statement still true; `drifted` covers a statement whose text moved without that claim; `removed` needs every release element `-` and the first stripped line of 8+ chars of each pin range to occur as no stripped line of the release file.

Machine-witness rule (counter docstring): every `holds-reworded`, `drifted` and `removed` row carries two verbatim excerpts, whitespace-collapsed and stripped (`ws` collapses every whitespace run to one space and strips). `witness_pin` must be at least 12 chars after collapse, occur in the collapsed text of the pin ranges, and occur nowhere in the collapsed whole release file; `witness_new` must be at least 12 chars after collapse, occur in the collapsed text of the release ranges, and occur nowhere in the collapsed whole pinned file; `removed` rows carry `witness_new` `-`. Every such row also carries a note of at least 40 chars. The witness proves only that the anchored text moved: reworded versus drifted stays the reader's call, and statement truth beyond the cited ranges is argued in the seat reports, not by the counter.

Byte-identical rows: all 91 population paths were compared with `git -C <clone> rev-parse d854d98bae598388ecea1ed84396587e5edc326d:<path>` and the same at `4d71b42fd87db24b8b7c808c151b713aa4459cfd:<path>`. 73 rows' files are byte-identical between b11889 and b11906, across 14 files. The counter re-derives every ledger row from pin-to-release bytes, so for these rows the b11906 row reproduces the b11889 row field for field — same `release_blob`, `changed`, `release_lines` and verdict — and the round-44 seat reading of the same bytes carries: no new read is taken. Six of them were `unchanged-file` at b11889 (S015, S059, S106, S128, S129, S131: the pin file equals the release file), the other 64 `holds`, and the three `holds-reworded` rows are in this set too (`tools/server/server.cpp`, whose witnesses re-derive from the identical file):

| file | rows |
|---|---|
| `tools/server/server-schema.cpp` | 36 — S140–S173, S190, S191 |
| `tools/server/server-common.cpp` | 13 — S126, S127, S137, S180–S189 |
| `tools/server/README.md` | 4 — S001, S035, S112, S134 |
| `tools/server/server.cpp` | 3 — S037, S043, S108 |
| `common/arg.cpp` | 3 — S054, S056, S110 |
| `src/llama-context.cpp` | 3 — S107, S130, S132 |
| `common/fit.cpp` | 2 — S106, S131 |
| `src/llama-kv-cache.cpp` | 2 — S113, S135 |
| `ggml/src/gguf.cpp` | 2 — S128, S129 |
| `gguf-py/gguf/gguf_reader.py` | 1 — S059 |
| `common/common.cpp` | 1 — S111 |
| `tools/quantize/README.md` | 1 — S015 |
| `tools/server/server-http.cpp` | 1 — S036 |
| `tools/server/server-queue.cpp` | 1 — S047 |

Changed files: 18 rows' files differ between b11889 and b11906. Seventeen sit on `tools/server/server-context.cpp`: the diff is 9 added and 6 removed lines, net +3 (7070 → 7073 lines), replacing b11889 lines 1020, 1024, 1708–1710 and 5130 and inserting one line at new 1015 and two at new 1401. One row (S479) sits on `tools/server/server-models.cpp`: a single replaced line at 536 (2931 lines both commits). The change is the mtmd capability refactor of `c6fb3b5b` (mtmd: add mtmd_helper_get_capabilities, #31183): `has_cap_tts`, `has_cap_chat`, `allow_image`, `allow_audio`, `allow_video` and `has_audio_stream` now read a cached `mtmd_cap` filled from `mtmd_helper_get_capabilities(model_tgt, mctx)` instead of probing `mctx` per call site, and `server-models.cpp` only renames the comment that cites the helper. No population row's cited anchor range contains a changed line, so the mechanical expectation is `holds` at shifted line numbers; one changed row's `teaches` cell names the affected capability (S125, "no multimodal projector or audio is not allowed"), so its reader must show the refusal guard still keys on that capability. Three further rows sit on byte-identical `tools/server/server.cpp` but were filed `holds-reworded` at b11889 (S037, S043, S108), so their witnesses are re-derived against the b11906 file. 21 rows are therefore read; the table below reserves one line per row and is completed from the ledger, one verdict at a time:

| id | path | b11889 verdict | why it is read | b11906 verdict | witness_pin / witness_new | note |
|---|---|---|---|---|---|---|
| `S037` | `tools/server/server.cpp` | holds-reworded | file byte-identical; reworded at b11889 | — | — | — |
| `S042` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S043` | `tools/server/server.cpp` | holds-reworded | file byte-identical; reworded at b11889 | — | — | — |
| `S060` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S108` | `tools/server/server.cpp` | holds-reworded | file byte-identical; reworded at b11889 | — | — | — |
| `S109` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S114` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S115` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S116` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S117` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S118` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S119` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S120` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S121` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S122` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S123` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S124` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S125` | `tools/server/server-context.cpp` | holds | changed file; teaches names the refactored capability | — | — | — |
| `S133` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S138` | `tools/server/server-context.cpp` | holds | changed file | — | — | — |
| `S479` | `tools/server/server-models.cpp` | holds | changed file (single comment line at 536) | — | — | — |

Flags are append-only: a row that lands `drifted` or `removed` keeps its own line in the table above, and every used-by entry the row's statement feeds gets one flag line under the paragraph that rests on it — for these rows the `corpus/knowledge/*.md` files are `llamacpp-loading-lifecycle.md` (S037, S042, S043), `endpoint-identity.md`, `served-identity-crosswalk.md` and `runtime-health-surface-matrix.md` (S037), `gguf-declared-identity.md` (S060), `context-capacity.md` (S060, S108, S109, S133) and `context-capacity-engine-sides.md` (S479); S114–S125 are used by `SKILL.md` and `registry/error-signatures-r26.json`, which the counter does not read and are flagged by hand. Flag sentence template, one line, the row id and `b11906` on that line:

```
**Round-46 flag (b11906, appended 2026-10-26):** S0NN was re-checked at llama.cpp b11906 = `4d71b42fd87db24b8b7c808c151b713aa4459cfd`; the statement this entry takes from it <now reads "…" — drifted | no longer occurs — removed>. Witness `registry/release-recheck-b11906.tsv` row S0NN (`witness_pin` against `witness_new`); see `corpus/SOURCES.md` §Round-46 release re-verification. The entry's own text is not rewritten (append-only).
```

Recheck cells stay `on-release`; no row's `status`, `recheck` or `used-by` cell changes under this section, and every edit here is an append (the five files the lane treats as append-only are audited by `tools/append-only-audit.py`, round-46 C2). Outside the population, the official b11906 Linux x64 binary was re-run on the stories260K fixture (re-fetched to `.cache/kama-shokunin/models/stories260K.gguf`, sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, the bytes S485 used) with the unchanged harness: three receipts (`.ufo/waves/round-46/c1/live/receipt-1.json`, `-2.json`, `-3.json`; `llama-server` sha256 `c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff`, asset digest `sha256:064ade62…eef3`) each pass all 11 checks — sampled instants, not a timing or quality claim, and no population row depends on them. Frontier: b11907 = `4b851fbee8867136a0c561c8a3521f2fe7d53252` is tagged at the same sample (line 1429) and is not opened here; releases after b11906 stay for the next recheck.
