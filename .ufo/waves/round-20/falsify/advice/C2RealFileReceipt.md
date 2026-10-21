VERDICT: confirm - current GGUF file identity and declared metadata agree with the captured receipt; the receipt remains self-report, not authentication.

- `sha256sum /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` returned `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`. It exactly equals receipt `model.sha256` and `model_sha256_post`; receipt path/fields are `.ufo/waves/round-18/live-recovery/receipt-1.json:262-267`.
- `file` identifies GGUF v3, 48 tensors, 19 metadata entries; `stat` reports physical size 1,185,376 bytes.
- A read-only inline GGUF header/tensor-descriptor parse found `general.architecture=llama`, `llama.context_length=2048`, `llama.embedding_length=64`, and 512 tokenizer tokens. The 48 tensor descriptors total 292,800 elements and all use type code 0 (F32).
- These values agree with the receipt's captured `/v1/models` metadata (`n_vocab=512`, `n_ctx_train=2048`, `n_embd=64`, `n_params=292800`, `ftype="(guessed) all F32"`), at `receipt-1.json:43` (full captured body). `meta.size=1171200` equals 292,800 × 4; it is not the physical file length.
- Runtime `n_ctx=256` in that capture is consistent with receipt `ctx:256` (`receipt-1.json:237`) and argv `-c 256` (`receipt-1.json:13-14`). This is the configured runtime context, distinct from the GGUF training context 2048, not a metadata mismatch.
- No server was started.

Residual risk / verification gap: the independent digest establishes that the current file has the digest the receipt reports. The receipt itself is unsigned self-report; this does not authenticate the receipt, prove which bytes were loaded at the earlier run, measure loaded weights, or establish model quality.