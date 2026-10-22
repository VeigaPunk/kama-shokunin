# ReopenS113: per-check verdicts for SOURCES row S113

Inputs: corpus/SOURCES.md:125 (S113 row), corpus/lessons/round-25.md:29 (Gate line) and :13-18 (Gate paragraph), corpus/knowledge/context-capacity.md (entry), committed tip fa3b62ae6475d111eb466d79af616aeebb08bbb9. Fetch on 2026-10-22 of the pinned file. Command output and exit codes are in fetch-and-hash.txt. Receipt output is in receipt-cross-check.txt.

| # | Check | Evidence | Verdict |
|---|---|---|---|
| C1 | Anchor sha256 equals the fresh fetch | SOURCES.md:125 anchor value d0739eaf00d8457f4109a616e0beb1cf07ea074c9b460d92a7b6d48c4519d294; sha256sum of the fetch gives the same; python equality EXACT (fetch-and-hash.txt step 2) | holds |
| C2 | Fetched bytes equal the pinned commit's file | git hash-object b7dfadef4638f6221608f48aff0a1f83df281063 (exit 0); GitHub contents API for ref 704366d76 gives the same sha, size 98638 (exit 0) | holds |
| C3 | "release b11755" is commit 704366d76 | GitHub tag API refs/tags/b11755 gives object 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, type commit (exit 0) | holds |
| C4 | Cite line 84 (stream count) | llama-kv-cache.cpp:84 `n_seq_max(n_seq_max), n_stream(unified ? 1 : n_seq_max), ...` | holds (the teaches cell writes the initializer with "=", F3) |
| C5 | Cite line 135 (stream assert) | :135 `GGML_ASSERT(n_stream == 1 \|\| n_stream == n_seq_max);` | holds |
| C6 | Cite 142-145 (per-stream cells) | :142 `v_cells.resize(n_stream);`; :143 loop over s < n_stream; :144 `v_cells[s].resize(kv_size);`; :145 closes loop | holds |
| C7 | Cite 233-244 (tensor dims, views) | :233 `ggml_new_tensor_3d(ctx, type_k, n_embd_k_gqa, kv_size, n_stream)`; :234 same shape for V; :243-244 per-stream view calls (loop :242-245) | holds |
| C8 | Cite 92-97 and 93-97 (shared override) | :92 `if (other) {`; :93 `size_other = other->get_size()`; :94 `if (kv_size != size_other)`; :95 LOG_WARN "overridden"; :96 `kv_size = size_other;` | holds (source only, see gaps) |
| C9 | Cite "constructor lines 65-98" | :65 constructor header; first column-0 `}` after :65 is :389 (python); next function starts :391 | label imprecise (F2) |
| C10 | Cite 301-304 (size log) | :301 format string `%s: size = ... (%6u cells, %3d layers, %2u/%u seqs), K (%s) ... V (%s) ...`; :302-304 arguments kv_size, layers, n_seq_max, n_stream | holds |
| C11 | Cite 1221-1233 (get_size, get_n_stream) | :1221-1225 get_size returns v_cells[seq_to_stream[0]].size(); :1231-1233 get_n_stream returns n_stream | holds |
| C12 | Gate quote exact, ≤25 words, right line | round-25.md:29 quote is a verbatim substring of llama-kv-cache.cpp:301 (python True); 18 words; range "lines 301-304" correct | holds |
| C13 | Gate URL equals row URL | round-25.md:29 and SOURCES.md:125 both give https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp (python: identical) | holds |
| C14 | Teaches (a): n_stream = unified ? 1 : n_seq_max, line 84 | :84 | holds |
| C15 | Teaches (b): every stream holds kv_size cells, line 144 | :143-145 | holds |
| C16 | Teaches (c): K/V tensors (embd, kv_size, n_stream), total = kv_size x n_stream "per layer", lines 233-234 | :233-234 hold for each layer that reaches the allocation. Layers skipped before it: :166-169 (no KV), :171-174 (filtered), :176-191 (shared layers are pushed and continue, so they get no tensor). Reused layers at :252-273 get no tensor | over-general (F1) |
| C17 | Teaches (d): log prints kv_size as "cells" and n_seq_max/n_stream as "%2u/%u seqs", lines 301-304 | :301-304 | holds |
| C18 | Teaches (e): shared source cache overrides kv_size, lines 93-97 | :92-97 | holds (source only) |
| C19 | Product rule on live data (committed receipt) | 14 cells, every size line: stream rule holds, pool = kv_size x n_stream (receipt-cross-check.txt); receipt:35 (1.25 MiB, 4/1 seqs, K 0.62) and receipt:820 (5.00 MiB, 4/4 seqs, K 2.50) | holds (dated sample, not re-run) |
| C20 | Entry uses S113 for what the row teaches | context-capacity.md:65-67 "one stream per sequence when split and one when unified; its size log prints cells per stream (S113, llama-kv-cache.cpp 84, 144, 301-304)" | holds |
| C21 | Entry header lists S113 correctly | context-capacity.md:1 `source: ... S113 (src/llama-kv-cache.cpp) ...` | holds |
| C22 | Entry does not take the n_ctx to kv_size derivation from S113 | Derivation is carried by S107 (context-capacity.md:52-54) and S106/S111 (:71-74); S113 scope excludes it (SOURCES.md:125 scope cell) | holds |
| C23 | Machine binding of S113 | count-c2.py:137-141 binds build and model sha only; tools/kama-context-capacity.py has no stream or kv_size logic (log filter regex :92-96; "stream" at :447 is the request field) | S113 not machine-bound; no defect |
| C24 | Census | validate exit 0, "kama ok" (census-validate.tsv); 29 W04 lines, none for S113; overdue: "cadence S113 recheck=on-release" | holds |
| C25 | Row shape and enums | 11 inner cells, no stray pipe; kind `code` (contract .ufo/waves/kaika/SOURCES-CONTRACT-v1.md:24-25); tier A (source code, :26-30); status mined with used-by present; opened ISO date; recheck symbolic (:38-39) | holds |
| C26 | used-by path exists at the committed tip | context-capacity.md: committed sha = working sha (committed-vs-working.txt) | holds |
| C27 | Status history | draft-row.md status queued; committed row status mined; row first appears in fa3b62a (git log -S) as a new row; rule 2 (contract :49-51) governs in-place changes | holds [INFERENCE on the reading of rule 2] |
| C28 | Committed S113 bytes equal working bytes | SOURCES.md:125 and round-25.md:29 identical in committed and working copies | holds |
| C29 | Gate paragraph claim: sha in anchor cell; seat report exists | a2-build/advice/SrcKvCacheSize.md committed at fa3b62ae (cat-file exit 0); it records d0739eaf... (grep count 1) | holds |
| C30 | Teaches grounding by the Gate quote | contract :34-35 ("one grounded learner benefit"); :45-48 (one ≤25-word quote grounding teaches); Gate quotes line 301 only; teaches carries five claims | residual, corpus-wide (F4) |
