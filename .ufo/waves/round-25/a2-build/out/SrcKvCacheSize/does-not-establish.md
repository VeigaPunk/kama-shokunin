# What src/llama-kv-cache.cpp @ 704366d76 does NOT establish

1. How `kv_size` is computed from `n_ctx` and `n_seq_max`. This file receives `kv_size` as a constructor parameter (lines 73-74) and never uses `n_ctx` for sizing (the only `n_ctx` reference is rope-yarn, line 1952). Padding, capping, `--fit` and per-slot split sizing live in other files (call site), out of this row's scope.
2. That `n_seq_max` equals the server's parallel slot count (`-np`) or any particular value; `n_seq_max` is caller-supplied (line 74).
3. The server startup line `load_model: initializing, n_slots = ..., n_ctx_slot = ...`. This file logs `llama_kv_cache: size = ...` (lines 301-304) with no `n_ctx_slot` wording; the server line is emitted elsewhere.
4. Runtime slot behavior: how many tokens a slot actually serves, sequence-to-stream mapping at request time, eviction/head reuse under load. The constructor only sizes the data structures (lines 142-155, 233-244).
5. What `/props`, `/slots` and `/v1/models` report. Those are server surfaces (adjacent row S060 covers `server-context.cpp`); this file is not an HTTP surface.
6. Actual memory footprint on the fixture: `size_k_bytes`/`size_v_bytes` feed the log, but real buffer sizes depend on backend allocation (buffer size logged separately, line 291) and on the passed `offload` flag (lines 216-221).
7. That the b11755 binary in fact executes this code path identically. A source file alone cannot prove runtime behavior; live observation belongs to the C2 server-run receipt.
