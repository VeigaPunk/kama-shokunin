VERDICT: confirm - S038/S039 at 37bd4c5 match host bytes, the round-18 live receipt and today's upstream records (16/16 local checks, exit 0)

# FreshnessS039 — S038/S039 freshness spot (not a claim)
Seat CloseKama18.FreshnessS039-2 (reviewer, leaf). Rows read with `git -C <lane> show 37bd4c5bd456a2f8a54d3312c28495c321715856:corpus/SOURCES.md` (S038 line 50, S039 line 51). `git rev-parse HEAD` = 37bd4c5…; lane untouched (`git status --short` shows only the pre-existing `?? .ufo/waves/round-20/`).

## Host bytes vs row cells
| row | row cell | command (exit) | observed | result |
|---|---|---|---|---|
| S039 | size 1185376, LFS sha256 270cba1b…d256d | `sha256sum /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` (0); `stat -c %s` | 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d, 1185376 B | match |
| S038 | `llama-b11755-bin-ubuntu-x64.tar.gz` size 22240468, sha256:753bfa73…e226 | archive present at `/home/vgpnk/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz`; `sha256sum` (0) | 753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226, 22240468 B | match |

## Binding chain — `out/FreshnessS039/freshness_check.py` (stdlib, read-only)
`python3 out/FreshnessS039/freshness_check.py --out out/FreshnessS039/freshness-result.json` → exit 0, 16/16 `match`:
- archive bytes == S038 asset name, size and digest (3 checks).
- archive's 61 members (51 regular, 10 symlinks) == `/home/vgpnk/.local/opt/llama-b11755` exactly: no extra or missing entry, every regular-file sha256 and symlink target equal (3).
- installed tree under the `tools/kama-llamacpp-live.py:178-202` rule (regular files, sorted `name sha` lines): 51 members, digest 6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c == archive-derived digest == receipt `server.install_tree` (all 51) == receipt `install_tree_sha256`; receipt `server.sha256` b6a31a8e… == installed `llama-server`; `server_impl_sha256` e404b91a… == installed `libllama-server-impl.so` (5).
- model bytes == S039 size/sha256 == receipt `model.path`, `model.sha256` and `model_sha256_post` (5).
Receipt: `.ufo/waves/round-18/live-recovery/receipt-1.json` (sha256 89728a02…a863; committed in 1b85a24; `git diff --quiet 37bd4c5 -- <receipt>` exit 0); argv[0] and `server.realpath` = `/home/vgpnk/.local/opt/llama-b11755/llama-server`.
Fail-capability controls (`out/FreshnessS039/controls.txt`): 1 flipped model byte → 4 mismatches, exit 1; absent archive → `error archive read`, exit 2, no mismatch claimed; zeroed `model_sha256_post` → 1 mismatch, exit 1; rev 96bbd742 (no SOURCES.md, git exit 128) → 2 parse errors, exit 2.

## Upstream recheck (S039 recheck `every round`; S038 `on-release`)
- `gh api repos/ggml-org/llama.cpp/releases/tags/b11755` (0, 07:24:34Z): target_commitish 704366d7…, prerelease true, immutable false, published_at 2026-10-20T11:18:44Z; asset size 22240468, digest sha256:753bfa73…e226, state uploaded, updated_at 2026-10-20T11:21:11Z. `gh api repos/ggml-org/llama.cpp/git/ref/tags/b11755` (0): commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad. All S038 anchor cells unchanged; the API's explicit `"immutable": false` supports the row's "the release is mutable".
- `curl -sSI` on `huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf` and on `…/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/…` (both 0): 302, x-repo-commit 499bc882…, x-linked-size 1185376, x-linked-etag "270cba1b…d256d". paths-info (0): lfs.oid 270cba1b…, size 1185376, lastCommit 96f460f9c1e2… "gguf : bump training context from 256 to 2048" (2025-10-28T08:55:08Z). revision/main (0): sha 499bc882…, lastModified 2025-10-28T10:43:38Z, cardData null, so "no license declared" still holds. All S039 anchor cells unchanged.
- Projections saved: `out/FreshnessS039/upstream-gh-b11755.json`, `upstream-hf-stories260K.json` (raw-response sha256 inside).

## C2 real-file population scope
- Name glob `/home/vgpnk/**/*.gguf` (hidden on, gitignore off) → 1 file, the S039 model. This is not a magic scan: extensionless GGUF blobs elsewhere are not excluded [INFERENCE]; the magic census belongs to GgufHostCensus.
- statx birth times: model 2026-10-20 10:17:53 -0300, archive 10:17:47, install dir 10:17:52, all before round start (37bd4c5 committed 2026-10-21T04:05:09-03:00). Install-dir ctime 10:17:53.108 is unchanged since extraction, so no entry was added or removed afterwards [INFERENCE from ctime semantics].
- `llama-connect` (9729072 B, mtime 2026-09-02) predates the other files but is listed in the archive (`tar -tvzf` exit 0), so the tree holds no foreign file.

## Heads-up for C2 (observed, outside the row check)
1. The receipt's `.captures.props.fields` stores the flattened literal key `"default_generation_settings.n_ctx": 256`, so the nested jq path `.captures.props.fields.default_generation_settings.n_ctx` returns null (observed). A tool reading the nested path sees "absent", which must count as could-not-evaluate, never as a verdict.
2. gguf-py 0.19.0 (the oracle; `uv run --offline --no-project --with gguf`, exit 0) reads llama.context_length 2048, block_count 5, embedding_length 64, general.architecture llama, general.name llama, tokenizer.ggml.model llama; general.file_type ABSENT, general.alignment ABSENT; 22 KV fields, 48 tensors. The served n_ctx 256 comes from receipt argv `-c 256`, so declared 2048 vs served 256 is an explicit launch override, consistent with the HF commit title.
3. The real file lacks general.file_type and general.alignment: `tools/gguf-identity.py` must report those keys absent, not fail.

## Residual risk / gaps
- Host archive == GitHub-recorded digest shows the local file equals the published asset record at fetch time. It does not show GitHub serves those bytes today: no re-download, by the large-download bound.
- Each upstream record was fetched once (07:24Z), so a later edit to the mutable pre-release is not covered.
- No round-start host snapshot exists; "readable at round start" rests on birth and ctime timestamps.

Tooling: nothing installed or upgraded. Used existing uv 0.13.0, gh (authenticated), python3 3.14.8, and gguf 0.19.0 + numpy 2.5.4 from the uv cache (`--offline`).
Files (new, under `.ufo/waves/round-20/build/out/FreshnessS039/`): freshness_check.py (sha256 204dd6d4…c2a7), freshness-result.json, controls.txt, upstream-gh-b11755.json, upstream-hf-stories260K.json. Scratch `/tmp/kama-r20-FreshnessS039` deleted.
