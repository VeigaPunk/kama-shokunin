# Proposed SOURCES row (candidate S058; L1 assigns the registry ID)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S058 | llama.cpp gguf-py reader and metadata constants @ 704366d76 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/gguf-py/gguf/gguf_reader.py | code | A | llama.cpp's Python gguf-py header/metadata reader at this commit; not the C++ model loader or a later PyPI wheel | `gguf_reader.py`:41, 116-165, 206-213, 234-272; `constants.py`:10-12, 22-27, 48, 108-114, 6295-6308; SHA-256 reader `d0ea743200e19d7ef0a4c969edcc4a6dba8e3656a790b217e3bdc7b31170718e`, constants `b84596cf8bc54b329dadeb74b7fc741cd4f7528ef8b30c4ec85aadf875ff7c63` | The Python reader checks literal `GGUF` magic, marks byte order swapped when the host-order version's low 16 bits are zero, and accepts versions 2 and 3 only; `GGUFValueType` codes 0–12 are UINT8, INT8, UINT16, INT16, UINT32, INT32, FLOAT32, BOOL, STRING, ARRAY, UINT64, INT64, FLOAT64; identity-key constants are `general.architecture`, `general.file_type`, and `{arch}.context_length`. | queued | 2026-10-21 | on-release | — |

## Located quote (20 words total)

- `gguf_reader.py:41`: “READER_SUPPORTED_VERSIONS = [2, GGUF_VERSION]” (4 words).
- `gguf_reader.py:149-150`: “that means it's (probably) a GGUF file created for the opposite byte order” (13 words).
- `constants.py:24, 27, 110`: “general.architecture”; “general.file_type”; “{arch}.context_length” (3 words).

Source quote word count excludes locations and parenthetical counts. The pinned `GGUF_VERSION` is 3 (`constants.py:11`).