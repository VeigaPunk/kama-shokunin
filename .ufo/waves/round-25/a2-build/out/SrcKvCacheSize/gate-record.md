# Gate record — llama.cpp src/llama-kv-cache.cpp @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad

- URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp
- Raw: https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp
- Access date: 2026-10-22
- Fetch command: `curl -sS -o /fast/scratch/hyaku/kama-r25a2/SrcKvCacheSize/llama-kv-cache.cpp <raw URL>` — exit 0.
- Size: 98638 bytes; 2962 lines.
- sha256 (content): `d0739eaf00d8457f4109a616e0beb1cf07ea074c9b460d92a7b6d48c4519d294`
- Git blob SHA-1: `b7dfadef4638f6221608f48aff0a1f83df281063` — matches `https://api.github.com/repos/ggml-org/llama.cpp/contents/src/llama-kv-cache.cpp?ref=704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (name llama-kv-cache.cpp, size 98638). Byte-identical to the pinned commit.

## Located quote (at most 25 words)

`llama-kv-cache.cpp:301-304` (format string of the constructor log line):

> "size = %7.2f MiB (%6u cells, %3d layers, %2u/%u seqs), K (%s): %7.2f MiB, V (%s): %7.2f MiB" (18 words)

Arguments at 302-304: cells = `kv_size`, then layers, then `n_seq_max`/`n_stream`.
