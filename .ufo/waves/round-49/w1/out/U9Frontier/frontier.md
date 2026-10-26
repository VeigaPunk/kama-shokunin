# U9Frontier - round 49 carried frontier: what a next round must read

Sampled 2026-10-26T23:11-23:40Z. Upstream `ggml-org/llama.cpp` newest tag is **b11912** = `961c376a2daa42220ec09663b9bde32c5fba1f70` (`git ls-remote --tags`); b11911 does not exist as a tag. Evidence files sit beside this file (`rng.out`, `tree-ids.out`, `tokenize-handler.out`, `asset-retention.out`, `s013-revisions.out`, `imp-*.mdx`).
Method: `git clone --bare --filter=blob:none` of upstream into scratch (removed), read-only git, `gh api` one request per object, `curl`. No lane file touched, no llama-server started, no tool installed.

## 0. Verdict table

| item | next round reads | can anything the C1 witness checks change? |
|---|---|---|
| b11906 ledger population (91 rows) at b11909+ | 2 files, 5 rows (S107 S130 S132 S113 S135); 14 of 16 ledger paths are blob-identical b11906=b11909=b11912. Expected verdict for all 5: holds, text-equal, renumbered (table in section 1). | No. |
| S013 re-pin | One Ollama commit (`98acec40`) and the consumer table row at `corpus/knowledge/gguf-runtime-compatibility-boundary.md:22`. Stronger than round 46 said: the cited revision does not just 404, its mdx teaches the opposite (section 2). | Not applicable (no llama.cpp). |
| ten off-population llama.cpp rows | 10 rows still outside; 4 more per-release rows (S486-S489) joined them; S494 joined the population (92 by the round-46 rule). Reads in section 3. | No row's teach changes; S477's number does (135 vs 115). |

## 1. b11906 ledger population re-verification (U2Server carry)

Reproduction of U2Server's claim, with my own blobs/line maps, not its text:

- `registry/release-recheck-b11906.tsv`: 91 rows, 16 distinct paths. Every `release_blob` equals `git rev-parse b11906:<path>`. (`tree-ids.out`)
- b11906 -> b11909 -> b11912: blob-identical for 14 paths (`common/arg.cpp`, `common/common.cpp`, `common/fit.cpp`, `ggml/src/gguf.cpp`, `gguf-py/gguf/gguf_reader.py`, `tools/quantize/README.md`, `tools/server/{README.md,server-common.cpp,server-context.cpp,server-http.cpp,server-models.cpp,server-queue.cpp,server-schema.cpp,server.cpp}`). Whole trees `tools/server` = `bb7cdb4c71c9`, `common` = `3b01489f2240`, `include` = `b48f64b4ca00`, `ggml/include` = `47e687a1f220` are identical at b11906, b11909 and b11912 (`tree-ids.out`).
- The two changed paths changed in b11907/b11908 only (commits `4b851fbee`, `a4699400e`; U2Server `map.md` section 1). b11909 -> b11912 (`63b4b303b` opencl, `4244ad7ac` CI, `961c376a2` laguna) touches 4 files: `.github/workflows/behavior-check.yml`, `ggml/src/ggml-opencl/ggml-opencl.cpp`, `src/llama-arch.cpp` (+1), `src/llama-graph.cpp` (1 line, adds `LLM_ARCH_LAGUNA`). Neither `src/llama-context.cpp` nor `src/llama-kv-cache.cpp` has a different blob at b11912 than at b11909 (`git rev-parse` in `tree-ids.out`). So the same 5-row set is the whole reading set at b11912 too.

Independent text check (`rng.py`, `difflib` line map b11906 -> b11909 over the registry's own pinned ranges; `rng.out`): every old line in every cited range is matched equal (no unmatched line) except the kv-cache signature/ctor span 65-98, where old lines 67 and 82 differ (signature `const llama_hparams &` -> `bool no_alloc` + re-indented `const char * name_tag`) and one line is inserted (`ctxs_bufs(no_alloc),`). Cited statements all sit on equal lines.

| row | file | b11906 ranges (ledger `release_lines`) | b11909 = b11912 ranges | read |
|---|---|---|---|---|
| S107, S132 | src/llama-context.cpp | 225, 387-403, 419-427, 4132-4136 | 225, 387-403, 419-427, **4133-4137** | text equal; +1 after new line 492 (`/*.no_alloc =*/ model.no_alloc()`). Dependencies 192, 342, 370 equal and unshifted. |
| S130 | src/llama-context.cpp | 2642 (deps 192, 342, 618) | **2643** (192, 342, **619**) | `GGML_ASSERT(n_outputs >= 1)` line text equal |
| S113 | src/llama-kv-cache.cpp | 65-98, 142-145, 233-244, 301-304, 1222-1234 | **65-100, 144-147, 235-246, 289-292, 1197-1209** | cited n_stream line 84 -> 85, kv_size override 92-97 -> 94-99, size log (`LLAMA_LOG_INFO("%s: size = %7.2f MiB (%6u cells, %3d layers, %2u/%u seqs)...`) at 289-292 identical; the 301-304 block moved up 12 lines because the per-buffer alloc/clear loop shrank. 65-98 is the only range with changed lines (signature) -> verdict `holds` (or `holds-reworded` if the seat grades signature drift). |
| S135 | src/llama-kv-cache.cpp | 142-145, 233-234, 301-304 | **144-147, 235-236, 289-292** | text equal |

Behaviour of the moved code (what is not a text range): the old loop did `ggml_backend_alloc_ctx_tensors_from_buft` then `ggml_backend_buffer_clear(buf, 0)`; the new `llama_memory_bufs::emplace` (`src/llama-memory.cpp:89-98` at b11909) calls `alloc_buf` then `ggml_backend_buffer_clear(buf.get(), 0)` with the same comment ("avoid NaNs in the padding"). The `no_alloc=true` branch is the former dummy-buffer code verbatim. Normal-load behaviour is unchanged. `src/llama-memory.cpp/.h` and `src/llama-moe-cache.cpp` are new in the diff and cited by no ledger row; a next round that wants the "moved, not changed" claim as a row would have to add them.

What the next round must do (not done here: the round-46 counter is frozen at b11906):
1. Read the five rows' ranges at the new release (file `src/llama-context.cpp` blob `455f5198e...` at b11909 vs `d5a66a499` at b11906; `src/llama-kv-cache.cpp` `61b5cb370` vs `4ab280a61`) and write release-recheck rows with the renumbered ranges above. Everything else carries by blob identity, which a one-line `git rev-parse` per path proves.
2. Make the release identity a measurement, not a constant (K1Pop F1, still open; `tools/round46-release-recheck-audit.py:102-103`): `git rev-parse b11912^{commit}` = `961c376a...` today.
3. The population is 92, not 91, by the round-46 rule: S494 (`raw.githubusercontent.com/ggml-org/llama.cpp/caa8191d.../tools/server/README.md`, `mined`, `on-release`, 11 cells) is now selected (computed from `corpus/SOURCES.md` at lane HEAD 122c4ee9 with the rule in `tools/round46-release-recheck-audit.py:25-31`: 92 selected, the frozen 91 all still selected, new: S494). Its README blob `8e27e37b8d4a` is identical at b11909 and b11912; I verified the lane's copy `.ufo/waves/round-49/c1/server-README-caa8191d.md` is byte-equal to `git show b11909:tools/server/README.md` (whole file and lines 686-735).

Can anything the witness checks change? No source-level change in the three releases touches a witness-checked surface:
- `POST /tokenize` handler (`tools/server/server-context.cpp:6252-6290` at b11909; `post_detokenize` 6293-) is text-identical at b11755, b11909 and b11912 (`tokenize-handler.out`: `755==909`, `909==912`). `tokenize_mixed`/`tokens_to_str` live in `tools/server/server-common.cpp` (blob identical b11906..b11912); `common_token_to_piece` in `common/common.cpp` (identical); `src/llama-vocab.cpp`, `src/llama-vocab.h`, `src/unicode*.cpp` identical (`tree-ids.out`). The README `/tokenize` and `/detokenize` span, S494's quote, is unchanged.
- `-m` parsing: `common/arg.cpp` identical. `/proc/<pid>/exe`, LISTEN inode: no upstream dependency.
- What does change per release is the binary: b11912's asset `llama-b11912-bin-ubuntu-x64.tar.gz` digest `sha256:344ea88c...` differs from b11909's `bf94332a...`; the counter's frozen `llama-server` sha `35ac50fb...` is b11909-only. Moving the witness to a later release needs a new frozen digest and a new set of receipts; the receipts' recorded digests do not carry.
- Retention (not a source change): all five Linux assets still answer HTTP 200 today after redirects: b11755, b11889, b11906, b11909, b11912 (`asset-retention.out`), and the HF model URL at the frozen revision answers 200. Every release in the last 8 is `prerelease: true`; b11909's and b11889's records say `immutable: false` (`gh api repos/ggml-org/llama.cpp/releases/tags/b11889`; S488 text). Nothing upstream promises retention of prerelease assets, so a replay can fail with a download error, not a verdict, at any later time; that is unchanged from the round-48 carry.

## 2. S013 re-pin (Ollama importing a model)

Row: `corpus/SOURCES.md:25`: source `https://docs.ollama.com/import`, anchor "page undated, live text mirrors ollama/ollama docs/import.md commit 6d02a43a75cd3364b3c230e9070f1413e60f0d02 (2025-10-28)", teaches "GGUF import consumes a prepared file and does not quantize it; shards need original filenames plus a wildcard". Consumer: `corpus/knowledge/gguf-runtime-compatibility-boundary.md:22` repeats "`docs/import.md` at commit `6d02a43a` (2025-10-28)" and the quote "Ollama does not quantize GGUF models during import"; `:4` makes it `on-release` with the S013 import paragraph as a recheck item.

Measured today (`gh api`, `curl`; `s013-revisions.out`, the three `imp-*.mdx` copies):
- Live page https://docs.ollama.com/import (HTTP 200) still contains "Ollama does not quantize GGUF models during import" and "keep the original split filenames and use a wildcard that matches every shard". So the teach holds on the page.
- `docs/import.mdx` blob at `main` (`6c15b26ba0d0`, 2026-10-26T23:10Z) = `8a8778ceba25e492b49eb1b276e788f1c2082462` = blob at `98acec40ae2b3ed361fc5117e5b2ae81a4bf5c18` (2026-09-15, "create: add server-side MLX imports and drop GGUF conversion (#14969)"). No commit touched the file after 2026-09-16 (`commits?path=docs/import.mdx&since=...` length 0).
- **New (round 46 only reported the 404):** at the cited `6d02a43a` the file is `docs/import.mdx` (176 lines; `docs/import.md` is 404 at that commit) and it teaches the opposite of the row: lines 111-128 "## Quantizing a Model ... Ollama can quantize FP16 and FP32 based models ... `ollama create --quantize q4_K_M mymodel`"; there is no "does not quantize GGUF models during import" and no "wildcard" anywhere in that revision (`grep -c`: 0). The same holds at `948f69330acf` (2026-08-11, "does not quantize" count 0; "Quantizing a Model" section still at line 111) and at `fc5f9bb4481a`. The first revision that carries the row's text is `98acec40` (lines 35 and 43). So the anchor cell's "mirrors 6d02a43a (2025-10-28)" is wrong in kind, not only in path: a reader who follows it finds a page that says Ollama quantizes, and the date of the teach is 2026-09-15, not 2025-10-28.
- Both the S013 row and `gguf-runtime-compatibility-boundary.md:22` carry the wrong revision and date; the table row's "Import only" claim is correct on the live page.

What a next round must do: change the anchor cell of S013 to `https://github.com/ollama/ollama/blob/98acec40ae2b3ed361fc5117e5b2ae81a4bf5c18/docs/import.mdx` (blob `8a8778ce...`, lines 35 and 43, equal to `main` today), set the date to 2026-09-15, and fix `gguf-runtime-compatibility-boundary.md:22` to the same commit. Because S013's source is an `https://docs.ollama.com/...` page, the round-46 population rule does not select it; a pin to a github.com `blob/<40hex>/` of `ollama/ollama` is still outside a `ggml-org/llama.cpp` rule, so its trigger stays "ollama/ollama commits to `docs/import.mdx` after 98acec40" (a dated `gh api commits?path=docs/import.mdx&since=2026-09-16` check, one request), not a llama.cpp release. Nothing the C1 witness checks depends on S013.

## 3. The ten off-population llama.cpp rows (round-46 K1Pop), recomputed at lane HEAD

Recomputed from `corpus/SOURCES.md` at 122c4ee9 with the round-46 rule (11 cells, `on-release`, `mined|queued`, `ggml-org/llama.cpp` blob/tree/raw URL): 92 selected (frozen 91 plus S494), and these llama.cpp-naming rows stay outside it:

| row | line | form | what b11909/b11912 does to it | a next round reads |
|---|---|---|---|---|
| S026 | 38 | PR #18001 `/v1/metrics`, rejected | `git grep -c v1/metrics b11912` exits 1 (no hit in the tree); flip condition still unmet | same grep at the newest tag; PR state once (`gh api repos/ggml-org/llama.cpp/pulls/18001`) |
| S028 | 40 | issue #4746, rejected, 90d | history row; `/health` exists (`server-context.cpp:5618` `res->ok({{"status", "ok"}})` at b11912) | nothing |
| S038 | 50 | release b11755 tag + asset record | `rev-parse b11755^{commit}` = `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` today; asset still 200 | tag ref, asset digest (`asset-retention.out`) |
| S477 | 230 | tag inventory, 30d (due 2026-11-24) | row says 115 above b11755; `git ls-remote --tags` today: highest `b11912`, **135** bN tags above b11755 (20 above b11887). Row was 115 at 2026-10-25T20:03Z, 130-131 at b11906 (K1Pop), 135 now: it moves every few hours | in no population and not due; the K1Pop F2 fix (put it in the next population, supersession line in `corpus/knowledge/engine-pin-watch.md`) is still open |
| S482 | 235 | release b11889 record | `gh api .../releases/tags/b11889`: `target_commitish` d854d98bae598388ecea1ed84396587e5edc326d, prerelease true, published 2026-10-25T23:44:54Z, `immutable` false - all as recorded | release record |
| S484 | 237 | b11889 asset digest | asset still HTTP 200 | digest from the API |
| S485 | 238 | b11889 live receipts | by reading: `tools/server` tree identical b11906..b11912; by execution: b11906 (S487) and b11909 (S489) receipts exist, none at b11912 | execute a b11912 live receipt, or state behavioural freshness trails |
| S041, S046, S055 | 53, 58, 67 | b11755 receipts, `every round` | carried by S485/S487/S489; statements still true at b11912 by reading: `/metrics` error text with `Start it with `--metrics`` at `server-context.cpp:5625`, `owned_by` "llamacpp" at 5503, health body at 5618 | nothing new |

New since round 46 and equally outside the rule: S486 (b11906 binary), S487 (b11906 receipts), S488 (b11909 binary), S489 (b11909 receipts) - `on-release`, `mined`, source cell is a release-asset URL or own-work receipt. S486/S488 asset digests (`064ade62...`, `bf94332a...`) equal what the API reports today. The family grows two rows per released-and-replayed build and no population ever reopens it: 14 now. Round 49's S494/S495 add one in-rule row and one man7 row.

Remaining unknown I did not execute: nothing in this seat ran a b11912 server, so "statements hold at b11912" is by source reading plus tree identity (inference), not an observed lifecycle.

## 4. A witness edge I checked and closed

The counter compares each returned `/tokenize` piece with `vocab[id].replace("\u2581", " ")` (`tools/round49-replay-witness-audit.py:280-281`) and has no `<0xNN>` byte-token case, while the server returns `common_token_to_piece(...)` (`server-context.cpp:6265`), which decodes a SentencePiece byte token to the raw byte. So a nonce character that fell to byte fallback would make the counter reject a correct server. Checked against the frozen model (downloaded from the frozen HF URL, sha256 `270cba1b...bd256d` matches; GGUF KV parse, 512 tokens, model `llama`, 256 `<0x..>` byte tokens present): every character of the nonce alphabet (`kama witness` with U+2581 for the space, plus `0-9a-f`) is itself a vocab token, so SPM never needs a byte token for any nonce the counter can draw. No defect for this model; it would become one with a different model or a nonce containing a non-ASCII or uncommon character. Parse script was inline (not kept); the model file was removed with scratch.
