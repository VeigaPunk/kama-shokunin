VERDICT: confirm - bounded GGUF reader, receipt reconciliation and evidence delivered.

# GgufTool final scoped findings

## Files
- `.ufo/waves/round-20/build/out/GgufTool-final/gguf-identity.py`
- `.ufo/waves/round-20/build/out/GgufTool-final/selftest.json`
- `.ufo/waves/round-20/build/out/GgufTool-final/stories260K-receipt.json`
- This report: `.ufo/waves/round-20/build/advice/GgufTool.md`

## Behavior
- Stdlib-only Python 3.14 CLI parses GGUF v2/v3 little-endian and v3 big-endian; strict UTF-8/duplicate-key/type/truncation checks; recursive array summaries; known identity keys and their actual wire types.
- Spec architecture integer keys accept UINT64 and legacy UINT32, the latter observed in the real fixture. Receipt mode binds `model_sha256_post` to the streamed file SHA, validates HTTP 200, both non-truncation flags and `body_sha256`, selects `data[].id == props.model_alias`, then compares declared context, llama embedding length, tokenizer vocabulary length and file-type presence with receipt `meta`.
- Receipt result is explicitly `receipt-self-report-not-authenticated-execution`. `props.n_ctx=256` is displayed as informational and is not compared to training context 2048; `total_slots=4` is never divided.
- Limits: file 64 GiB; SHA-256 32 GiB; decoded header+KV 64 MiB; KV 100,000; strings 1 MiB (keys 65,535 B); arrays 1,000,000 entries each / 4,000,000 aggregate / depth 32; receipt 1 MiB; body 512 KiB; JSON depth 64 / 100,000 nodes. Opens use nonblocking, close-on-exec, no-follow and require regular files. The parser never decodes tensor descriptors or payloads.

## Executed evidence
- Pinned scratch clone: `mkdir -p /tmp/kama-r20-GgufTool && git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r20-GgufTool/lane && git -C /tmp/kama-r20-GgufTool/lane checkout -q 37bd4c5bd456a2f8a54d3312c28495c321715856` — exit 0, no stdout. `python3 --version` — exit 0, stdout `Python 3.14.8`. Remaining local Python checks used `cwd=/tmp/kama-r20-GgufTool/lane`.
- Final `python3 tools/gguf-identity.py --selftest` — exit 0; stdout reproduced in `out/GgufTool-final/selftest.json`: 27/27 passed, including v2/v3 endian controls, nested arrays, metadata/hash/receipt budgets, valid/mismatched/malformed receipts, context mismatch exit 1 and missing `n_ctx_train` exit 2.
- Final `python3 tools/gguf-identity.py /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live-recovery/receipt-1.json --json` — exit 0; exact stdout in `out/GgufTool-final/stories260K-receipt.json`. File: 1,185,376 B, SHA-256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; receipt model SHA matches; body SHA `13fa21491109a1156afa59d7050635c6e57ae8db7d8fbd7be4c248acfe3f9d19`; selected alias/id `kama-r18-live`; GGUF context 2048 equals `meta.n_ctx_train=2048`; embedding 64 equals `n_embd`; vocab 512 equals `n_vocab`; `props.n_ctx=256` remains informational.
- Oracle type check: `uv run --no-project --with gguf python3 -c 'from gguf import GGUFReader; r=GGUFReader("/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf"); keys=("general.architecture","general.name","general.file_type","general.alignment","tokenizer.ggml.model","tokenizer.ggml.tokens","llama.context_length","llama.block_count","llama.embedding_length"); print({k:[t.name for t in r.fields[k].types] for k in keys if k in r.fields})'` — exit 0; stdout `{'general.architecture': ['STRING'], 'general.name': ['STRING'], 'tokenizer.ggml.model': ['STRING'], 'tokenizer.ggml.tokens': ['ARRAY', 'STRING'], 'llama.context_length': ['UINT32'], 'llama.block_count': ['UINT32'], 'llama.embedding_length': ['UINT32']}`.
- `uv run --no-project --with gguf python3 -c 'import importlib.metadata as metadata; print(metadata.version("gguf"))'` — exit 0, stdout `0.19.0`; wheel was ephemeral, no persistent install/update.
- Filesystem probes ran with `cwd=/tmp/kama-r20-GgufTool/lane`: `timeout 5 python3 tools/gguf-identity.py /tmp/kama-r20-GgufTool/model-symlink.gguf --json` — exit 3, stderr `gguf-identity: file_unavailable`; `timeout 5 python3 tools/gguf-identity.py /tmp/kama-r20-GgufTool/idle.fifo --json` — exit 3, same stderr; `python3 tools/gguf-identity.py /tmp/kama-r20-GgufTool/oversize.gguf --json` — exit 2, stderr `gguf-identity: file_byte_budget_exceeded`.
- Receipt-path probes, each with `cwd=/tmp/kama-r20-GgufTool/lane`: `timeout 5 python3 tools/gguf-identity.py /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --receipt /tmp/kama-r20-GgufTool/receipt-symlink.json --json` — exit 2; and `timeout 5 python3 tools/gguf-identity.py /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --receipt /tmp/kama-r20-GgufTool/receipt.fifo --json` — exit 2. Both stdout receipt outcomes were `{"status":"could-not-evaluate","exit_code":2,"reason":"receipt_file_unavailable"}`; neither blocked.
- No llama-server or `tools/kama-llamacpp-live.py` run.

## Source anchors
- GGUF spec `docs/gguf.md` @ `6af560d55df03ad92116e3c0a697779584477e85`: §File Structure line 148, “Models are little-endian by default”; §Specification line 218, “Arrays can be nested”; lines 448-450 specify `context_length`, `embedding_length`, and `block_count` as uint64; line 282 says v3 introduces big-endian support. The pinned real-file oracle observation above shows this older v3 fixture stores those keys as UINT32; output `key_types` preserves that fact.
- `SrcServerNctx.md:8,11` (llama.cpp pin `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`): “Training context is a separate `/v1/models` field”; `/props` does not expose `n_ctx_train`. Its receipt cross-check records props 256 and model `n_ctx_train` 2048.
- `ConnectKengaku.md:20,25-26` recommends the SHA-bound engine-agreement leg and notes receipt self-capture is not tamper-proof. `SrcCtxTrainWarning.md:27-31` distinguishes declared/training context from per-slot context and says not to infer a contradiction from `props.n_ctx` alone.
- `corpus/SOURCES.md` at round-start `37bd4c5bd456a2f8a54d3312c28495c321715856`, S039 line 51: “size 1185376, LFS sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d”; local run matches.

## Resolved first-attempt failures
- Initial `python3 tools/gguf-identity.py --selftest` — exit 1; stderr ended `ReceiptError: models_n_ctx_train_missing` because that could-not-evaluate case escaped. The wrapper now converts it to exit 2; final selftest is 27/27.
- Initial `python3 tools/gguf-identity.py /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live-recovery/receipt-1.json --json` — exit 2, stderr `gguf-identity: identity_key_type_mismatch`; the oracle type check established the fixture's legacy UINT32 keys and the parser now accepts those alongside spec UINT64.

## Risks / blockers
- The receipt has `meta.architecture` null; that optional field is explicitly outside the comparison contract. `meta.n_params` and `meta.size` are also un-compared because tensor descriptors are outside the reader scope.
- Receipt agreement is self-reported, not authenticated runtime evidence. Full-file hashing necessarily streams payload bytes but does not decode or mmap tensor data. [INFERENCE] Same-size concurrent rewrites can be detected through file timestamps/signature checks on this host, but a hostile filesystem that preserves all signature fields is outside this test.
- Blockers: none. No persistent tools installed or updated.
