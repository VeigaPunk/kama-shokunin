VERDICT: confirm - v2-valid fixture run matches expected.json on exit, reason-mapping, and all metadata; fixture hash matches SHA256SUMS; tool scope is parser-only for this run.

# Command under test
`/usr/bin/python3 tools/gguf-identity.py tests/gguf-identity/fixtures/v2-valid.gguf --json`

# Observed (exact)
- Exit: 0; stderr: 0 bytes (captured separately). stdout: JSON only.
- JSON: version=2, endianness=little, kv_count=3, tensor_count=0, size=151,
  metadata_bytes=151, sha256=083128b301233cb7544cbe9c645b445d4da6b201966c2f54d4b834468dd6ceb1,
  key_types {general.architecture: STRING, general.name: STRING, llama.context_length: UINT64},
  keys {general.architecture: llama, general.name: fixture-v2, llama.context_length: 4096,
  plus general.alignment/general.file_type/llama.block_count/llama.embedding_length/
  tokenizer.ggml.model: null}, arrays={}, path=<fixture abs path>.

# Comparison vs tests/gguf-identity/expected.json:28-51
- expected_exit 0 = observed 0. OK.
- expected_reason "decoded": tool emits no reason token on success (JSON has no "reason"
  key; stderr empty). Named reason is derivable only via expected.json:2-7 exit_codes
  map ("0": "decoded"). Mapping holds for exit 0; observable surface is exit+empty stderr.
- kv_count 3=3, tensor_count 0=0, version 2=2, size_bytes 151=151, sha256 identical,
  endianness little=little. metadata: string/llama, string/fixture-v2, uint64/4096 all
  match observed key_types+keys (case differs STRING vs "string"; representational only).

# Fixture integrity vs tests/gguf-identity/SHA256SUMS:2
- `sha256sum -c SHA256SUMS` in tests/gguf-identity: all 23 fixtures OK, CHECK_EXIT=0;
  v2-valid line hash equals observed JSON sha256. Fixture file is 151 bytes on disk.

# Independent byte-level cross-check (xxd of fixture)
- 4747 5546 "GGUF", version 2 (LE uint32), then uint64 tensor_count=0 and kv_count=3
  (v2 uses uint64 counts). Records: "general.architecture" type 8 (string) len 5 "llama";
  "general.name" type 8 len 10 "fixture-v2"; "llama.context_length" type 10 (uint64)
  value 0x1000=4096. No tensor data; whole 151 bytes is header+metadata, consistent with
  metadata_bytes=151=size. Observed JSON is a faithful decode of the actual bytes.

# Scope claim (parser behavior only)
- tools/gguf-identity.py:14-25 imports stdlib only (argparse/hashlib/io/json/math/os/re/
  stat/struct/sys); no socket/urllib/requests/subprocess. Receipt mode (--receipt,
  gguf-identity.py:944,970-976) loads an existing captured receipt file via load_receipt();
  no serving, no loaded-weight access, no auth or model-quality evaluation anywhere in the
  invoked path. Claim "declared metadata reader + comparison with an existing captured
  receipt" is consistent with the source.

# Caveats (observations, not defects)
- Success path yields no emitted named reason; error paths print `gguf-identity: <reason>`
  to stderr (gguf-identity.py:964-966). For v2-valid the reason comparison rests on the
  exit_codes map in expected.json, not a tool-emitted token.
- Tool JSON is a superset of expected.json's projection (path, metadata_bytes, key_types,
  arrays, null placeholders for known-but-absent keys). Null placeholders conflate
  "known key absent" with value null; expected.json lists only present keys, so no
  contradiction, but downstream consumers must not read nulls as file content.
- expected.json does not pin metadata_bytes, key_types casing, or endianness-of-JSON
  formatting; extras are unconstrained by the contract (summary != full-document equality).

# Evidence trail (relative to kama-shokunin)
- tools/gguf-identity.py:950-989 (main/JSON print), :14-25 (imports), :964-966 (stderr reason)
- tests/gguf-identity/expected.json:28-51 (v2-valid entry), :2-7 (exit_codes)
- tests/gguf-identity/SHA256SUMS:2 (v2-valid hash); sha256sum -c all-OK
- Fixture hexdump cross-check performed in-session; scratch file /tmp/kama-r20-fixturev2valid.err removed.
