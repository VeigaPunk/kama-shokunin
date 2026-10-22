# Draft SOURCES registry row — llama.cpp src/llama-kv-cache.cpp @ 704366d76

Status: queued (until the L1 cites it). Id left as `S1xx` per assignment.
Exact 11-column format of `corpus/SOURCES.md` (header line 11):

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S1xx | llama.cpp src/llama-kv-cache.cpp — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp | code | A | llama.cpp KV cache construction at commit 704366d76 (release b11755): stream count, per-stream cell count, tensor shape and the `llama_kv_cache: size` log line; not how kv_size derives from n_ctx (call-site logic, other files) | constructor lines 65-98 (shared-source override 92-97), 135 (stream assert), 142-145 (per-stream cells), 233-244 (tensor dims/views); log line 301-304; get_size/get_n_stream 1221-1233; raw file sha256 d0739eaf00d8457f4109a616e0beb1cf07ea074c9b460d92a7b6d48c4519d294 | `n_stream = unified ? 1 : n_seq_max` (line 84); every stream holds `kv_size` cells (144); K/V tensors are (embd, kv_size, n_stream), so total cells = kv_size × n_stream per layer (233-234); the size log prints kv_size as "cells" and n_seq_max/n_stream as "%2u/%u seqs" (301-304); a shared source cache overrides kv_size to match (93-97) | queued | 2026-10-22 | on-release | — |
