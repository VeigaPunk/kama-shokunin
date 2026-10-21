# GGUF declared identity: what a header states, and what it does not prove
source: S0xx-gguf-spec https://github.com/ggml-org/ggml/blob/6af560d55df03ad92116e3c0a697779584477e85/docs/gguf.md §File Structure, §Standardized key-value pairs; S0xx-llamacpp-gguf https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp; S0xx-llamacpp-model …/src/llama-model.cpp; S0xx-llamacpp-ctx …/src/llama-context.cpp; S0xx-llamacpp-arch …/src/llama-arch.cpp; S037 and S042 …/tools/server/server.cpp and server-context.cpp (same pin); S054 …/common/arg.cpp; S0xx-ollama-gguf https://github.com/ollama/ollama/blob/370c9b6739e38df6542ca906b1848434e71ab551/fs/gguf/gguf.go
verified-at: 2026-10-21 — spec and llama.cpp sources opened at the pins above (sha256 in §Evidence); `stories260K.gguf` header read offline; no server launched; no `~/.ollama` store on this host.
recheck: on-release — re-open gguf.cpp header checks, llama-model.cpp context_length read and server-context.cpp `n_ctx_slot`/`get_res_props` when either pin moves.

## Claim

A GGUF header *declares* identity: architecture, name, trained context length, block count, embedding length, tokenizer model. The writer chose those strings and numbers. A header read proves what the file says, not which weights were loaded, that they load, or that they answer well.

## Header layout

- Bytes 0–3: magic `GGUF`; then `uint32` version (current spec: 3); `uint64` tensor_count; `uint64` metadata_kv_count; typed key-value pairs; tensor infos; data padded to `general.alignment` (spec §File Structure, lines 278–290, 147).
- Little-endian by default; big-endian files exist; the spec admits no in-file way to tell (spec line 151).
- llama.cpp `gguf.cpp` rejects: wrong magic (lines 477–484), version 0 (495), version 1 (512), version above 3 (515–517), tensor count out of range (527), duplicate key (575).
- `general.alignment` must be `uint32` (624–628) and a power of two (632–635); absent means 32 (`GGUF_DEFAULT_ALIGNMENT`, `gguf.h` line 46).
- Ollama `fs/gguf/gguf.go` accepts `GGUF` (little-endian) and `FUGG` (big-endian) at lines 81–83 and version ≥1 at line 93. It accepts version 1; llama.cpp does not.

## Keys that declare identity

| key | read at | role |
|---|---|---|
| `general.architecture` | loader `llama-model-loader.cpp:577` (not required); unknown name → `LLM_ARCH_UNKNOWN` (`llama-arch.cpp:1196`) | picks the `<arch>.` prefix for every other key |
| `general.name` | `llama-model.cpp:1374` (optional) | free-text label; spec line 388 says only "should be unique within the community" |
| `<arch>.context_length` | `llama-model.cpp:1382`, required (`llama-model-loader.h:207` default `required = true`) | declared trained context, `n_ctx_train` |
| `<arch>.block_count`, `<arch>.embedding_length` | `llama-model.cpp:1394`, `:1383` | layer count, embedding width |
| `tokenizer.ggml.model` | `llama-arch.cpp:414` | tokenizer family |
| `general.file_type`, `general.quantization_version`, `general.alignment` | spec lines 384, 383, 407 (optional) | quantization hints; `file_type` is not a quality claim |

Omitted keys mean "unknown", and readers "either default or error" (spec line 361). Community keys must be namespaced (spec line 363).

## A header read is not a load, nor a quality claim

- The reader in `gguf.cpp` validates structure and bounds. It never decodes tensors or checks weights.
- A load is a separate act: `llama-model.cpp` reads hyperparameters at line 1382 and continues; the remaining load checks were not traced. Only a live `/health` 200 with a model id (S042, S046) shows that a server took the file.
- No header key carries a benchmark, eval score, or training-data claim. Spec line 17 says the file contains "all the information needed to load a model"; that is a design goal, not a verification.

## Declared train context vs served per-slot `n_ctx`

- Declared: `<arch>.context_length` → `n_ctx_train` (`llama-model.cpp:1382`).
- Served: `/props` `default_generation_settings.n_ctx` = `meta.slot_n_ctx` (`server-context.cpp:5234–5236`); `/v1/models` `meta.n_ctx` (5186) and `meta.n_ctx_train` (5187).
- `n_ctx_slot()` = min(`n_ctx_seq`, `kv_unified_per_slot` if >0, `n_ctx_train`) (`server-context.cpp:4655–4663`). A slot never exceeds the train context.
- `n_ctx` 0 means "use the train context" (`llama-context.cpp:219`; `-c` help "0 = loaded from model", S054 `arg.cpp:1642–1643`).
- With `kv_unified`, `n_ctx_seq = n_ctx`; otherwise `n_ctx / n_seq_max`, padded to 256 (`llama-context.cpp:379–383`).
- Auto slots (`-np -1`; `arg.cpp:2548–2549`, default at `arg.cpp:1406`) set `n_parallel = 4` and `kv_unified = true` (`server.cpp:169–172`).
- Live receipt (own-work): `.ufo/waves/round-18/live-recovery/receipt-1.json` ran `-c 256` with no slot flag; `/props` returned `n_ctx` 256 and `total_slots` 4; the header declares 2048. So served per-slot 256 is the whole pool, not 256/4. [INFERENCE: the unified pool is shared across slots; the code fixes sizes, not occupancy.]
- Reconcile the two fields separately. Equal values are not expected, and a mismatch is not automatically a defect.

## Ollama blobs are GGUF

- Store: `$OLLAMA_MODELS`, else `~/.ollama/models` (`envconfig/config.go:114, 123`). Blob path `models/blobs/<digest>` (`manifest/paths.go:409`); name `sha256-<64 hex>` (`manifest/manifest.go:23`).
- Import reads the blob with `gguf.ReadFileMetadata(blobPath, 1)` (`server/create.go:1093`) and tags the layer `application/vnd.ollama.image.model` (`create.go:1102`).
- Create-time quantization of GGUF is refused, text: "quantize GGUF models with llama.cpp tools before importing" (`create.go:741–744`), consistent with S013.
- The blob is content-addressed: its bytes hash to the digest (`manifest/manifest.go:1394`). That the import copies bytes unchanged is [INFERENCE]; not traced.
- No Ollama store exists on this host (`ls -ld ~/.ollama` exit 2), so no Ollama blob was read.

## Limits

- Self-declared: the header struct has magic, version, and two counts, and nothing else (spec lines 278–290). No signature, checksum or hash appears in the spec's prose (sweep in §Evidence). `gguf.cpp` and `gguf.go` do no integrity check.
- No authentication: `general.name`, `general.architecture` and `context_length` are free text or integers any writer can set. Only the file's sha256 binds bytes, and it says nothing about who wrote them.
- Filenames are not identity (S0xx-gguf-spec naming section: "not intended to be perfectly parsable in the field").
- Served identity needs a dated live sample (S001, S042); this entry never supplies one.

## Evidence

- `sha256sum` of the pinned files: `docs/gguf.md` 1dead27b…; `ggml/src/gguf.cpp` 7505d6a4…; `ggml/include/gguf.h` e56714aa…; `src/llama-model.cpp` 4a209cc6…; `src/llama-context.cpp` 2a25e556…; `src/llama-arch.cpp` 1170b4b3…; `tools/server/server.cpp` 21439622…; `tools/server/server-context.cpp` dd1de0f2…; `common/arg.cpp` bf4c58c1….
- Header dump: `python3 hdr.py stories260K.gguf` → magic GGUF, version 3, tensor_count 48, kv_count 19, `general.architecture=llama`, `general.name=llama`, `llama.context_length=2048`, `llama.block_count=5`, `llama.embedding_length=64`, `tokenizer.ggml.model=llama`, no `general.alignment`, no `general.file_type` (exit 0; saved as `header-dump.txt`).
- Oracle cross-check: `uv run --with gguf==0.19.0 python …` returns the same values (exit 0).
- Negative sweep: `grep -n -i -w -E "signature|checksum|hash|authentication|verify|trust" gguf.md` matches only C comments about signed integers (lines 201–225); `gguf.cpp` and `gguf.go` exit 1 for `checksum|sha256|signature|verify|hash`.
