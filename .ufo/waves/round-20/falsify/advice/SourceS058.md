VERDICT: confirm - row S058 accurately binds GGUF v3 specification da8e2a54 without exceeding declared-metadata scope

## Source verification and anchor check
- Path: `corpus/SOURCES.md:70` (row S058).
- URL: `https://raw.githubusercontent.com/ggml-org/ggml/da8e2a54b919557b816b1c2beb432ccb766f7ce0/docs/gguf.md`.
- Opened date: 2026-10-21; revision: `da8e2a54b919557b816b1c2beb432ccb766f7ce0`.
- Raw SHA-256: `1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020` (828 lines, 43,175 bytes).
- Anchors checked against raw revision:
  - Line 279: `    // Must be `GGUF` at the byte level: `0x47` `0x47` `0x55` `0x46`.`
  - Lines 198–298: `gguf_metadata_value_type` enum (198–229), `gguf_string_t` (231–237), `gguf_metadata_value_t` (239–260), `gguf_metadata_kv_t` (262–275), `gguf_header_t` (277–298).
  - General lines 369–384 (`general.architecture`, `quantization_version`, `alignment`).
  - LLM lines 447–451 (`[llm].context_length` / `n_ctx`).
  - Version History lines 770–780 (v3 big-endian, v2 uint64 counts, v1 initial).

## Located excerpt (lines 277–285)
```c
struct gguf_header_t {
    // Magic number to announce that this is a GGUF file.
    // Must be `GGUF` at the byte level: `0x47` `0x47` `0x55` `0x46`.
    // Your executor might do little-endian byte order, so it might be
    // check for 0x46554747 and letting the endianness cancel out.
    // Consider being *very* explicit about the byte order here.
    uint32_t magic;
    // The version of the format implemented.
    // Must be `3` for version described in this spec, which introduces big-endian support.
```

## Row properties and declared-metadata scope
- Kind: `spec` | Tier: `A` (canonical format specification) | Status: `mined`.
- Quote/Meaning: Sourced quote from line 279 matches `corpus/lessons/round-20.md:51`. "Teaches" column correctly bounds offline identity inspection without claiming execution authentication.
- Scope: "GGUF v3 header and metadata serialization; format declarations, not loader acceptance or model quality".
  - Confirmed: Header declarations do not imply loader acceptance, runtime execution, weight validity, or inference quality.
- Used-by: `corpus/knowledge/gguf-declared-identity.md` (lines 1, 11) and `corpus/lessons/round-20.md` (lines 21, 51, 63). Active citations confirmed.

## Lane province boundary scan
- `kengaku` (eval/quality): S058 specifies architecture and context metadata (`[llm].context_length`). `PROVINCE.md:40-43, 98-106` and `corpus/knowledge/cross-lane-scope.md:27, 32` acknowledge technique overlap but strictly refuse quality/eval claims. Kama uses S058 only for offline header decoding and receipt reconciliation (`tools/gguf-identity.py`), not benchmark scoring or evaluation.
- `kumitate` (routing/gateway): Kama verifies local model artifacts without absorbing model routing or dispatch orchestration.
- `kagi` (credentials/auth): Kama reads only explicitly provided file paths without searching config trees or reading secrets.
