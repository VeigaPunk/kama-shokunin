# U9Frontier — carried llama.cpp / Ollama frontier at 2026-10-26T22:38Z (round 48, w1)

**Verdict: nothing on the carried frontier can change what the v5 receipts check. Upstream `tools/`, `common/` and `include/` are byte-identical from b11906 through the newest tag b11912, so every HTTP-facing statement and the `/props` fields behind the receipts read the same source at b11912 as at b11909; the only src/ change that touches the stories260K load path (b11907/b11908, in the b11909 build) is already exercised by the three v5 receipts. Three items need action in a later round, and one correction to a round-47 finding: the S013 re-pin cannot be an in-place edit (SOURCES.md is append-only per `registry/append-only-contract.tsv` row `corpus/SOURCES.md A-row`); the b11906 ledger's five src/ rows hold at b11912 by exact-block match; the off-population llama.cpp rows are now 14, not 10; and the v5 receipts have no registry row yet.**

Method: bare blobless clone of `https://github.com/ggml-org/llama.cpp.git` (scratch, removed), read-only git; `gh api` for releases and the Ollama repo (one request per object); `curl -I` for Hugging Face. Counters and receipts were not re-run (no live server started by this seat). Transcripts and scripts: `evidence.txt`, `ranges.out`, `sweep.out`, `ranges.py`, `sweep.py` in this directory (the scripts read a scratch clone and a scratch copy of `SOURCES.md@380bcdff` that were deleted at the end; re-create `up/` with the clone command above to re-run).

## 0. Where upstream is now

`git ls-remote --tags` / local clone, 2026-10-26 ~22:38Z:

| tag | commit | note |
|---|---|---|
| b11906 | 4d71b42fd87d | S486/S487 subject |
| b11907 | 4b851fbee886 | no_alloc: model output structs (#31142) |
| b11908 | a4699400e3cc | `no_alloc` out of `llama_hparams` (#31141), 30 files |
| b11909 | caa8191df159 | hexagon (#31169); **v5 receipt subject** (S488/S489, asset digest `bf94332a…`, `gh api releases/tags/b11909` digest identical) |
| b11910 | 63b4b303bd87 | opencl KV set_tensor (#30471) |
| b11911 | — | **no tag**; `releases/tags/b11911` is 404 (a number gap, like the 16 gaps above b11755, so "tags above the pin" ≠ numeric difference) |
| b11912 | 961c376a2daa | moe amax rescaling for laguna (#31147); release published 2026-10-26T22:30:51Z, asset `llama-b11912-bin-ubuntu-x64.tar.gz` digest `sha256:344ea88c09666c1fb3eb5f7a649ada48ff753daaa660c7d7bc0b614cda49a078` (22476351 bytes) |

`git diff --stat b11909 b11912` = 4 files, 72+/3-: `.github/workflows/behavior-check.yml` (new), `ggml/src/ggml-opencl/ggml-opencl.cpp`, `src/llama-arch.cpp` (+1, `case LLM_ARCH_LAGUNA`), `src/llama-graph.cpp` (1 line, `|| arch == LLM_ARCH_LAGUNA` in `build_moe_ffn`). `git diff --stat b11906 b11909 -- tools common include` and `git diff --stat b11909 b11912 -- tools common include ggml/include` are both empty (`evidence.txt`). Blobs at b11909 = b11912: `src/llama-context.cpp` 455f5198, `src/llama-kv-cache.cpp` 61b5cb37, `tools/server/server-context.cpp` 9043fa2c, `server-http.cpp` cf147c7e, `server.cpp` b6ebf752. The lane pin is still `registry/engine-pins.tsv:4` `llama.cpp … b11755`.

Moving target warning: b11912 appeared ~1.5 h before this sample; a next round should name the release it re-verifies by a frozen 40-hex commit, not "newest".

## 1. b11906 ledger population (91 rows) re-verified at b11909+

Round-47 seat U2Server (`.ufo/waves/round-47/w1/out/U2Server.md`, `…/U2Server/map.md` §4) derived from hunk offsets that 5 of 91 rows (S107, S113, S130, S132, S135) cite changed files. I redid it independently and one step further (target b11912, exact-block search instead of hunk arithmetic): for each `release_lines` range of `registry/release-recheck-b11906.tsv` (columns 9) I took the b11906 text of the range and searched `src/llama-context.cpp` / `src/llama-kv-cache.cpp` at b11912 for the same contiguous lines (`ranges.py` → `ranges.out`):

| row | file | b11906 range → exact-match line at b11912 |
|---|---|---|
| S107, S132 | src/llama-context.cpp | 225→225, 387-403→387, 419-427→419, 4132-4136→**4133** |
| S130 | src/llama-context.cpp | 2642→**2643** |
| S113 | src/llama-kv-cache.cpp | 142-145→144, 233-244→235, 301-304→289, 1222-1234→1197; **65-98 has no exact match** |
| S135 | src/llama-kv-cache.cpp | 142-145→144, 233-234→235, 301-304→289 |

S113 65-98: `git diff -U0 b11906 b11912 -- src/llama-kv-cache.cpp` shows only the constructor signature (`bool no_alloc` inserted at line 67, a realigned parameter line 68, `name_tag` re-indented at 83) and `ctxs_bufs(no_alloc)` inserted at 86. The statements S113 teaches inside that span match exactly at shifted lines: `n_stream(unified ? 1 : n_seq_max)` 84→85, shared-source `if (other)` block 92-97→94-99, `GGML_ASSERT(n_stream == 1 || n_stream == n_seq_max)` 135→137, ctor body 68-81→69 and 87-91→89. The remaining diff (`ggml_backend_alloc_ctx_tensors_from_buft` + `ggml_backend_buffer_clear` + the `no_alloc` dummy buffer moved into `ctxs_bufs.emplace`, `memory_breakdown()` → `ctxs_bufs.memory_breakdown()`) is outside every cited range; S113's cited log line (`llama_kv_cache: size`, 301-304) is text-equal at 289-292.

So: U2Server's verdict stands and extends to b11912 — all five rows are `holds` with renumbering (S113 is `holds-reworded` only if the reader counts the signature hunk inside 65-98). The other 86 rows cite files whose b11906 blob equals the b11909/b11912 blob (`tools/server/*`, `common/arg.cpp`, `common/common.cpp`, `common/fit.cpp`, `ggml/src/gguf.cpp`, `gguf-py/gguf/gguf_reader.py`, `tools/quantize/README.md`; the tools/ and common/ trees are identical, `evidence.txt`), so a freshness round carries them by blob identity.

**What a next round must read.** Only these, at the commit it freezes (b11912 `961c376a2daa42220ec09663b9bde32c5fba1f70` or later):
- `src/llama-context.cpp` and `src/llama-kv-cache.cpp` — compare against the b11906 ledger ranges above (`git rev-parse <tag>:<path>` first; if the blob is still 455f5198/61b5cb37 the five rows carry unchanged). Reference commits: `a4699400e` (#31141 no_alloc move) and `4b851fbee` (#31142 output structs).
- Not needed: tools/, common/, include/ (empty diff). Re-read them only if a *new* tag's `git diff --stat b11912 <new> -- tools common include` is non-empty.
- A ledger-guard for the next counter (K1Pop F1, still open): `git rev-parse b119xx^{commit}` from the clone must equal the frozen commit; I confirmed b11909→`caa8191df159f764fb0160e3d2fc6be008948aee` and b11912→`961c376a2daa42220ec09663b9bde32c5fba1f70` today.

**Could it change anything the v5 receipts check? No at source level; yes only if the next release touches the five server files or `common/arg.cpp`.** Receipt-1 (`.ufo/waves/round-48/c2/live/receipt-1.json`, schema `kama-llamacpp-live/v5`, 11/11 checks) checks: `/health` 200 `{"status":"ok"}`, `/v1/models` id = `--alias` and `owned_by` `"llamacpp"`, `/metrics` 501 without `--metrics`, `/props` fields (`build_info` `b11909-caa8191df`, `default_generation_settings.n_ctx` 256, `is_sleeping`, `model_alias`, `total_slots` 4), slots count 4, the loading 503 envelope, SIGTERM teardown, listener ownership, model digest unchanged, and the provenance block (asset URL/digest/member, model URL/commit/digest). The argv (`-c 256 -t 1 --no-webui --offline`) comes from `common/arg.cpp` (identical). At b11912 the statement sites are unchanged, all from `git show b11912:…`: `server-context.cpp` `{"owned_by","llamacpp"}` 5503, `get_health` 5609-5619 (`res->ok({{"status","ok"}})` 5618), `/metrics` `ERROR_TYPE_NOT_SUPPORTED` "Start it with `--metrics`" 5625; `server-http.cpp` `middleware_server_state` 308-330 (`res.status = 503` 315, "Loading model" 319); `server.cpp` `server_install_signal_handlers` 318-325 (`sigaction(SIGTERM…)` 325), `shutdown_handler` 645-648, `start_loop()` 671. What changes per release is only `build_info` (`bNNNNN-<9 hex>`): a replay of the b11909 receipts uses the b11909 archive pinned in them, so it keeps reading `b11909-caa8191df`; a b11912 receipt would legitimately differ there (and in the asset digest), which the v5 `--compare` projection should treat as a version change, not a regression.

The only src/ edits that sit on the stories260K load path (llama arch → `llama_kv_cache`, so `llama_memory_bufs::emplace`) are b11907/b11908, both inside the b11909 binary the receipts ran, and all three receipts passed 11/11 — measured, not inferred. b11910-b11912 add nothing on that path: the opencl change is not in the ubuntu-x64 CPU asset, the two laguna lines are gated on `arch == LLM_ARCH_LAGUNA`, and the workflow file is CI only. [INFERENCE: a b11912 live run would be 11/11; not executed.]

Round-47 U2Server finding 3b (receipt `documented_by` URLs pinned to `704366d…` with L5288-5299, L314-325, L529-534) — **refinement, not a defect in the URLs**: I read the cited spans at `704366d` (b11755): `server-context.cpp` 5288-5299 is `get_health` verbatim, `server-http.cpp` 314-325 is the 503 block verbatim, `server.cpp` 519-534 is the old in-`main` shutdown/sigaction block. They are correct permalinks for **b11755**; they are not wrong, they document the old build while the receipts' subject is b11909 (the v5 tool still builds them from `LLAMA_COMMIT` at `tools/kama-llamacpp-live.py:79-80`). The b11909/b11912 equivalents are `server-context.cpp` 5609-5619, `server-http.cpp` 315-326 (block text equal, +1), `server.cpp` 318-325 + 645-648 + 671 (the refactor f3269ef96 moved the SIGTERM install into a helper). Proposed fix for the next tool version (tool and counters are frozen this round): add a `documented_at` second permalink at the receipt's own build commit (`/blob/<server commit>/…`) beside the existing pin, and set it from `--server-archive` metadata; no behaviour change to the 11 checks.

## 2. S013 re-pin

Row: `corpus/SOURCES.md:25` (S013, "Ollama Importing a Model — https://docs.ollama.com/import", tier A, `mined`, `on-release`) cites "live text mirrors ollama/ollama docs/import.md commit 6d02a43a75cd3364b3c230e9070f1413e60f0d02 (2025-10-28)" and teaches "GGUF import consumes a prepared file and does not quantize it; shards need original filenames plus a wildcard". Round-46 seat U9Floating proposed `98acec40ae2b3ed361fc5117e5b2ae81a4bf5c18` (recorded as `registry/hexrun-ledger.tsv:83`), but no row was re-pinned: `SOURCES.md:25` still names 6d02a43a at `380bcdff`.

Re-derived today (`gh api` raw contents of `docs/import.mdx` at each revision, `evidence.txt`):

| revision | date | "does not quantize" | `--quantize` flag text | "wildcard" |
|---|---|---|---|---|
| 6d02a43a (cited) | 2025-10-28 | 0 | 2 | 0 |
| 3d99d977, fc5f9bb4, 948f6933 | 2025-10-28 … 2026-08-11 | 0 | 2 | 0 |
| **98acec40** | 2026-09-15 ("create: add server-side MLX imports and drop GGUF conversion (#14969)") | **1** (line 35) | 0 | **1** (line 43) |

- `gh api 'repos/ollama/ollama/commits?path=docs/import.mdx'`: 98acec40 is still the newest commit touching the file; blob of `docs/import.mdx` at `main` (`66ab8482e080`, 2026-10-26T04:25:58Z) = blob at 98acec40 = `8a8778ceba25` (2869 bytes). The cited 6d02a43a version teaches the opposite ("Ollama can quantize FP16 and FP32 based models … `-q/--quantize`"), and `docs/import.md` is 404 there (file is `.mdx`), as `hexrun-ledger.tsv:16` already notes.
- Live page `https://docs.ollama.com/import` (HTTP 200) and `https://docs.ollama.com/import.md` (200) contain "Ollama does not quantize GGUF models during import … llama.cpp's `llama-quantize`" (md line 37) and the wildcard sentence (md line 45); the `.md` body differs from the 98acec40 `.mdx` only in Mintlify rendering (title line, `*` vs `-` bullets, ` theme={"system"}` on code fences); the two quoted sentences are identical.
- Latest Ollama release `v0.40.11` (2026-10-24T00:30:13Z); the doc did not change at any release since 2026-09-15.

**The re-pin cannot be done the way the row's own cell suggests.** `registry/append-only-contract.tsv` declares `corpus/SOURCES.md  A-row  SKILL.md:578  *  registry rows appended; only status, recheck and used-by change in place`, and `tools/sources-append-only.py` (docstring lines 1-20: the compared set is the seven immutable cells {source, kind, tier, scope, anchor, teaches, opened}) exits 1 on a changed anchor cell. Rewriting S013's anchor cell (the `6d02a43a` text) is therefore an append-only violation by that guard; `tools/append-only-audit.py` v3 would not flag it by itself (its events need >= 20 deleted lines, default threshold), so the C1 counter is silent and the row-level guard is the one that matters. The established pattern is the one round 48 itself used for the model URL (S490 "stays as filed" → S492 the pinned replacement): **append a new row** (next free id after S493, i.e. S494 at this sample) citing `https://github.com/ollama/ollama/blob/98acec40ae2b3ed361fc5117e5b2ae81a4bf5c18/docs/import.mdx` §Importing a GGUF model (lines 33-46; "does not quantize" 35, wildcard 43), with S013's `status` left to the row-edit rules the sources-append-only tool allows (status / recheck / used-by only). Consumers to move to the new id: `corpus/knowledge/gguf-runtime-compatibility-boundary.md` lines 2, 22 and 63 (the `6d02a43a` text lives at line 22; knowledge docs are editable, `SOURCES.md` is not), `corpus/SOURCES.md:255` and `:282` mention S013 only by id. Also worth appending a one-line correction note beside the round-46 "Round-46 release re-verification" section (`SOURCES.md:593` names "S013 citation defect" without a fix).

What a next round must read: `docs/import.mdx` at the then-newest `git log -1 -- docs/import.mdx` commit on `ollama/ollama` (one `gh api` call; unchanged today), the live page text for the two quoted sentences, and `corpus/knowledge/gguf-runtime-compatibility-boundary.md` lines 2/22/63. Nothing S013 teaches is read by any v5 receipt; no llama.cpp or Ollama endpoint is involved.

## 3. The off-population llama.cpp rows

The rule (`tools/round46-release-recheck-audit.py:25-31`) still selects exactly 91 rows at `380bcdff` (population computed from the counter's own `population()` on `corpus/SOURCES.md@380bcdff` equals the base-`0163fea2` set: `in pop at 380 not at base: []`, `in base not 380: []`, `sweep.out`). Off-population rows that cite llama.cpp are **14 at `380bcdff`**, not 10: K1Pop's ten (S026, S028, S038, S041, S046, S055, S477, S482, S484, S485) plus S486, S487 (b11906 asset + receipts, round 46) and S488, S489 (b11909 asset + v4 receipts, round 47). All are `on-release` or `every round` or `30d` rows that no recheck population re-opens. Row by row, with what to read at b11912:

| row (SOURCES.md line) | teaches | status at b11909/b11912 | read next |
|---|---|---|---|
| S026 (38), PR #18001 `/v1/metrics`, rejected | no `/v1/metrics` in a released source | holds: `git -C up grep -q 'v1/metrics' b11912` exit 1, no hit in the tree | same grep at the frozen commit; flip condition unchanged |
| S028 (40), issue #4746, tier C rejected | historical healthcheck request | holds (history); route exists at `server-context.cpp:5609` b11912 | nothing |
| S038 (50), b11755 release + asset | tag→commit `704366d76f8748…`, asset digest | immutable; `b11755^{commit}` still `704366d76f87…` | `git rev-parse b11755^{commit}` |
| S477 (230), tag inventory | "115 tags above b11755 at b11887" | **moves**: tag counts above b11755 are 115 (b11887), 117 (b11889), 121 (b11897), 123 (b11899), 130 (b11906), 133 (b11909), **135 (b11912)** (`git tag -l 'b[0-9]*'`, gaps counted); 16 number gaps incl. b11911 | `git tag -l 'b[0-9]*'` at the frozen clone; not due until 30d (2026-11-24) but `engine-pin-watch.md:51-54` still prints 115/"behind"/"has not been checked" |
| S482 (235) b11889 release record, S484 (237) b11889 asset | per-release immutable facts | hold | `gh api releases/tags/b11889` once, only if a row edits them |
| S485 (238) b11889 receipts, S487 (240) b11906 receipts | v3 receipts at older builds | outside the v5 claim; the same 11 statements read identically at b11909 (server-* blobs equal b11906..b11912) | no new read; the v5 receipts supersede them as the behavioural evidence at b11909 |
| S486 (239) b11906 asset | identity of the b11906 binary | holds (asset digest `064ade62…`, tag `4d71b42f…`) | nothing |
| S488 (241) b11909 asset, S489 (242) b11909 v4 receipts | identity of b11909 binary; v4 receipts | hold: `releases/tags/b11909` digest `sha256:bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b`, target `caa8191df159f764fb0160e3d2fc6be008948aee` | nothing |
| S041, S046, S055 (53, 58, 67), b11755 receipts, `every round` | b11755 lifecycle | carried by S485/S487/S489 and the v5 receipts | nothing |

Findings:
1. **The v5 receipts have no registry row.** `grep -n "round-48/c2/live" corpus/SOURCES.md` at `380bcdff` returns nothing; S489 describes the v4 receipts (`round-47/c2/live`, schema v4) and S492/S493 only cover the model pin and the hf-hub doc. The b11909 binary has an S-row (S488) and the v4 receipts one (S489), but the round-48 evidence that the C2 claim is about (schema v5, `--server-archive`, three receipts, `provenance.model.commit`, `provenance.verified`) is not citable by a source id. Proposed: one own-work row S494-class beside S489 (`kama live llama.cpp lifecycle receipts at b11909, schema v5 …`), `tier A`, `recheck on-release`, naming `.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json` and `install.txt`; subject to the integrator, as it edits the registry.
2. **The v0.x semver stream is already recorded** (`corpus/README.md:747-751`: `releases/latest` = v0.7.0 = the b11669 commit, every `bN` release a prerelease); I re-confirmed it (`gh api releases/latest`: `v0.7.0`, 2026-10-15T17:13:19Z, `prerelease:false`, single asset `nightly-tag.txt` = `b11669`; `git describe --match 'v0.*' b11909` = `v0.7.0-240-gcaa8191df`). Not re-reported as a finding; it is the reason the next round must key on `bN` tags and not on `releases/latest`.

## 4. What the receipts still depend on outside llama.cpp (immutability check)

- Model: `https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf` still answers 302 with `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81`, `x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"`, `x-linked-size: 1185376`; the `resolve/main` URL returns the same commit and digest, i.e. the pinned revision is still the repo head (last commit 2025-10-28, "stories15M : revert training context to 128"). The repo is named `models-moved` and `GET /api/models/ggml-org/models-moved` reports `gated:false disabled:false private:false`; a future rename or deletion of that repo is the one external risk to the v5 replay; a next round should re-run the pinned `curl -sSI` and `/api/models/…/commits/main` check (one HF request each) and, if the repo moves, find the successor by sha256 `270cba1b…`, which survives any URL change.
- Asset: `https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz` digest in the release JSON equals `install.txt` and the receipts' `provenance.server.asset_sha256` (`bf94332a…`). GitHub keeps old bN release assets for as long as the release exists; a next round should re-read `releases/tags/b11909` `.assets[].digest` rather than trust this note.

## 5. Order of work for the next round (cheapest first)

1. Freeze the release by 40-hex commit (candidate b11912 `961c376a2daa…`, or the then-newest), guard it with `rev-parse <tag>^{commit}`.
2. `git diff --stat b11912 <new> -- tools common include ggml/include`: empty ⇒ every one of the 86 tools/common rows and every receipt statement carries; non-empty ⇒ read only the changed files among the 16 ledger paths (`registry/release-recheck-b11906.tsv` column 2) and, if any of `tools/server/server-{context,http,common,queue,schema,models}.cpp`, `tools/server/server.cpp` or `common/arg.cpp` changed, re-run the three-receipt live test against that release's asset (`--server-archive`) before saying anything about it.
3. Re-read the five src rows only if the `src/llama-context.cpp` or `src/llama-kv-cache.cpp` blob differs from 455f5198 / 61b5cb37.
4. S013: append the S494-class row on 98acec40 and move the knowledge doc; recheck `git log -1 -- docs/import.mdx` is still 98acec40.
5. S477 / `engine-pin-watch.md` §Result: re-derive the tag count, append a dated supersession line (K1Pop F2, still open).
6. Register the v5 receipts as a source row.

## 6. Housekeeping

Tools installed: none. Scratch `/fast/scratch/hyaku/kama-r48/U9Frontier` removed (a blobless clone of llama.cpp, one SOURCES copy, Ollama `import.mdx` revisions). No lane file, fleet file, counter, preregistration or control was edited; no service started; no live server run; `gh api` used sparingly: Ollama commits-by-path, contents at 6 refs, main commit, latest release; llama.cpp releases/latest, releases list, releases/tags b11906/b11909/b11911/b11912.
