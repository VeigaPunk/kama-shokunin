# KnowGguf — GGUF declared-identity knowledge draft (round 20, BUILD)

VERDICT: confirm - draft `corpus/knowledge/gguf-declared-identity.md` (68 lines) is grounded in the opened spec and llama.cpp/Ollama sources at pinned commits; a header is a declaration, not a load, quality, or authenticated identity.

## Deliverable
- `.ufo/waves/round-20/build/out/KnowGguf/gguf-declared-identity.md` — 68 lines (`wc -l`, exit 0). Opens with `source:` / `verified-at:` / `recheck:`; external sources cite `S0xx-*` placeholders for the L1 to number. Not written into the lane (`corpus/knowledge/` untouched).
- `out/KnowGguf/hdr.py` — stdlib header dumper (scratch-quality, read-only); `out/KnowGguf/header-dump.txt` — its output on the real model (re-run diff: exit 0).

## Pins opened (`curl` to raw.githubusercontent.com, all exit 0 unless noted)
- ggml `docs/gguf.md` @ 6af560d55df03ad92116e3c0a697779584477e85 — sha256 1dead27b…
- llama.cpp @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad (b11755): `ggml/src/gguf.cpp` 7505d6a4…, `ggml/include/gguf.h` e56714aa…, `src/llama-model.cpp` 4a209cc6…, `src/llama-context.cpp` 2a25e556…, `src/llama-arch.cpp` 1170b4b3…, `src/llama-model-loader.h`/`.cpp`, `tools/server/server.cpp` 21439622… (matches S037), `tools/server/server-context.cpp` dd1de0f2… (matches S042), `common/arg.cpp` bf4c58c1… (matches S054).
- Ollama @ 370c9b6739e38df6542ca906b1848434e71ab551 via `git clone --filter=blob:none` + `git show` (exit 0). `fs/ggml/gguf.go` does not exist at this commit (curl 404, exit 22); the reader is `fs/gguf/gguf.go` (e943750b…). Also `manifest/paths.go`, `manifest/manifest.go`, `server/create.go`, `envconfig/config.go`.

## Checks run
- `python3 hdr.py stories260K.gguf` → exit 0: magic GGUF, version 3, tensor_count 48, kv_count 19, `general.architecture=llama`, `general.name=llama`, `llama.context_length=2048`, `llama.block_count=5`, `llama.embedding_length=64`; no `general.alignment`, no `general.file_type`. File sha256 270cba1b… matches S039.
- `uv run --with gguf==0.19.0 python …` (PyPI gguf 0.19.0, ephemeral env, exit 0) → same architecture, name, context_length, block_count, embedding_length, tokenizer model; 22 fields = 19 kv + 3 pseudo-fields. Oracle agrees.
- `python3 -` reading `.ufo/waves/round-18/live-recovery/receipt-1.json` (exit 0): argv `-m stories260K.gguf --alias kama-r18-live … -c 256` with no `-np`/slot flag; `captures.props.fields.default_generation_settings.n_ctx = 256`, `total_slots = 4`; `model_sha256_post = 270cba1b…`.
- Negative sweeps (`grep`, exit 1 = no match): `gguf.cpp` and `gguf.go` for `checksum|sha256|signature|verify|hash` → none. `gguf.md` word-boundary `signature|checksum|hash|authentication|verify|trust` → only C-comment "signed integer" lines 201–225.
- `ls -ld ~/.ollama` → exit 2 (no Ollama store on host; no blob read).
- Not run: no llama-server launch, no live endpoint, no model download, no Ollama command.

## Findings for the L1
- Served per-slot `n_ctx` is not `train/slots`. Under auto slots, llama.cpp sets `kv_unified = true` (`server.cpp:169–172`), so `n_ctx_seq = n_ctx` (`llama-context.cpp:379–380`). The receipt's `-c 256` gives 256 per slot, while the header declares 2048. [INFERENCE: pool sharing across slots is inferred from the code's sizing, not observed occupancy.]
- `general.architecture` is read non-required (`llama-model-loader.cpp:577`); `<arch>.context_length` is required (`llama-model.cpp:1382`, default `required = true`, `llama-model-loader.h:207`). A missing architecture resolves to `LLM_ARCH_UNKNOWN` (`llama-arch.cpp:1196`) — the load path after that was not traced.
- Version split: llama.cpp rejects version 1 (`gguf.cpp:512`); Ollama accepts it (`gguf.go:93`). Ollama also accepts big-endian `FUGG` (`gguf.go:83`).
- Ollama blobs: `models/blobs/sha256-<hex>` (`manifest/paths.go:409`, `manifest/manifest.go:23`); GGUF import tags `application/vnd.ollama.image.model` after `ReadFileMetadata` (`create.go:1093, 1102`); create-time GGUF quantization refused (`create.go:741–744`). Byte-identity of an import with its source file is [INFERENCE].

## Limits / not done
- The entry is a knowledge draft; it does not add any SOURCES.md row (L1 numbers `S0xx`) and does not claim any served-identity result.
- `CORPUS.md` read (fleet root `/home/vgpnk/Projects/shokunin/CORPUS.md`); its rules followed: provenance trio first, count with command, quote with location, no credential material.
- Tools: `uv run --with gguf==0.19.0` (ephemeral, via official PyPI, uv 0.13.0) — no persistent install. Scratch `/tmp/kama-r20-KnowGguf` removed.
- Commands the main agent may re-run: `sha256sum` of the pinned files; `python3 out/KnowGguf/hdr.py <model>` and diff with `header-dump.txt`.
