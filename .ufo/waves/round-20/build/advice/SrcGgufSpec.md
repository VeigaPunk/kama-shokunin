VERDICT: confirm - pinned GGUF v3 specification supplies the requested identity layout

Axes: operability (offline GGUF identity inputs); calibration (source pin and evidence traceability).

Source: ggml-org/ggml `docs/gguf.md`, pinned raw URL:
https://raw.githubusercontent.com/ggml-org/ggml/da8e2a54b919557b816b1c2beb432ccb766f7ce0/docs/gguf.md
SHA-256: `1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020`.

Executed retrieval evidence (all paths below are scratch files; source inspection used the pinned file):
- `git ls-remote https://github.com/ggml-org/ggml refs/heads/master` — exit 0; returned `da8e2a54b919557b816b1c2beb432ccb766f7ce0`.
- `curl -fsSL https://raw.githubusercontent.com/ggml-org/ggml/HEAD/docs/gguf.md -o ...` — exit 0; `wc -lc` — exit 0, 828 lines / 43,175 bytes.
- `curl -fsSL https://raw.githubusercontent.com/ggml-org/ggml/da8e2a54b919557b816b1c2beb432ccb766f7ce0/docs/gguf.md -o ...` — exit 0; `sha256sum` — exit 0, hash above; `wc -lc` — exit 0, 828 / 43,175.
- `cmp -s` of the HEAD and pinned files — exit 0 (byte-identical).
- The GitHub commits API attempt returned HTTP 403 / curl exit 22; it was not used as source evidence or for the pin.

Observed format facts (all line numbers refer to the pinned `docs/gguf.md`):
- Header, §§File Structure lines 277–298: magic is literal bytes `47 47 55 46` (ASCII `GGUF`); `version` is `uint32`; `tensor_count` and `metadata_kv_count` are each `uint64` (lines 279–296).
- The header says version `3` is required for the version described here (line 285). Version History lines 770–780 records v3 adds big-endian support, v2 changes most countable values from `uint32` to `uint64`, and v1 is the initial version. The document does not claim a general reader-acceptance matrix for v1/v2; treat v3 as the only version specified by this header, not as proof that every implementation rejects or accepts earlier versions.
- Strings: `uint64 len` counts bytes, followed by UTF-8 non-null-terminated bytes (lines 231–236). Metadata keys must be valid ASCII, hierarchical lower_snake_case segments separated by `.`, and at most 65,535 bytes (lines 262–268).
- Full `gguf_metadata_value_type : uint32_t` enum (§File Structure lines 198–229): `UINT8=0`, `INT8=1`, `UINT16=2`, `INT16=3`, `UINT32=4`, `INT32=5`, `FLOAT32=6`, `BOOL=7`, `STRING=8`, `ARRAY=9`, `UINT64=10`, `INT64=11`, `FLOAT64=12`.
- Array layout (§File Structure lines 219–222, 252–259): element type (`gguf_metadata_value_type`), `uint64` element count, then values; length counts elements, not bytes; nested arrays are allowed.
- Endianness, §File Structure line 151 and Version History lines 770–772: little-endian by default; big-endian files encode all values, including metadata and tensors, big-endian. The spec says it provides no way to determine big-endian at the time written and says to assume little-endian absent other information.
- `general.alignment` is `uint32`, must be a multiple of 8, and defaults to 32 when omitted (§General line 384; alignment purpose lines 147–149).
- `general.architecture: string` is under General / Required, describes the architecture and is lowercase ASCII using `[a-z0-9]+` (lines 369–383). `[llm]` is a placeholder for a concrete architecture, not a literal key; `[llm].context_length: uint64` is `n_ctx`, the trained context length in tokens (lines 447–451). The spec cautions these LLM keys are not required for every architecture (line 449).

Two located quotes (each <25 words):
1. §File Structure line 279: “Must be `GGUF` at the byte level: `0x47` `0x47` `0x55` `0x46`.”
2. §General line 384: “Some writers may not write the alignment. If the alignment is **not** specified, assume it is `32`.”

Draft SOURCES.md row (registry currently ends at S057; S058 is proposed, not written to the lane):
`| S058 | GGUF file format — https://raw.githubusercontent.com/ggml-org/ggml/da8e2a54b919557b816b1c2beb432ccb766f7ce0/docs/gguf.md | spec | A | GGUF v3 header, metadata serialization, byte order, alignment, and standardized architecture/context metadata at this commit | §§File Structure, General, LLM, Version History; lines 147–451, 764–780 @ ggml-org/ggml da8e2a54b919557b816b1c2beb432ccb766f7ce0; raw SHA-256 1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020 | Defines header widths, type IDs and encodings, endian default, alignment default, and declared architecture/context metadata for offline GGUF identity parsing. | mined | 2026-10-21 | on-release | tools/gguf-identity.py |`

No tools installed or updated. No lane files were modified.