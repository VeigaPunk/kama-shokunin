VERDICT: confirm - pinned command exits 0 (stdout-only JSON, stderr 0 bytes) and every shared field matches expected.json's v3-nested-array entry and SHA256SUMS; reason "decoded" holds via the documented exit→reason map, since the tool never prints a literal reason string on success.

# Observed run (exact pinned command)
- `/usr/bin/python3 tools/gguf-identity.py tests/gguf-identity/fixtures/v3-nested-array.gguf --json`: EXIT=0; stdout 727 bytes of JSON; stderr 0 bytes.
- `grep -c decoded` on stdout = 0. Success emits no reason field: result dict is built at `tools/gguf-identity.py:288-296` (keys/arrays/key_types/endianness/...) and printed at `:982-984`; named reasons are only printed on `GGUFError` at `:964-966`. The observed reason is therefore "decoded" by mapping exit 0 through `tests/gguf-identity/expected.json:3` (`"0": "decoded"`) and the entry's `expected_reason` at `expected.json:121`; non-JSON mode prints only "GGUF v3 (little endian)" (`:985`).

# Contract comparison vs expected.json entry (:116-146)
- expected_exit 0 (:120) vs observed 0 — MATCH.
- expected_reason "decoded" (:121) vs exit-0 map — MATCH (see caveat above).
- endianness little (:119), kv_count 3 (:124), size 206 (:143), tensor_count 0 (:144), version 3 (:145), sha256 51c6aa6c...12729 (:142) — all MATCH the observed JSON.
- metadata (:125-141) vs observed `arrays` block: test.empty {array,int32,0}↔{type INT32,length 0}; test.nested {array,array,2}↔{ARRAY,2}; test.strings {array,string,3}↔{STRING,3}. Key set and lengths identical; only naming convention differs (uppercase element type in `arrays` vs lowercase type/element_type pairs; `TYPE_NAMES` at `tools/gguf-identity.py:51-54`). No contradiction.
- Observed extra fields (keys: 5 identity keys all null — fixture declares none; key_types {}; metadata_bytes 206; path) are tool diagnostics absent from the entry schema; they contradict nothing.

# Independent byte parse (stdlib struct, in-memory, no writes)
- magic GGUF, version 3, tensor_count 0, kv_count 3; records: test.nested ARRAY-of-ARRAY len 2 {ARRAY-of-UINT8 len 3 [1,2,255]; ARRAY-of-STRING len 2 ["a","β"]}; test.strings ARRAY-of-STRING len 3 ["", "hello", "λ"]; test.empty ARRAY-of-INT32 len 0. Exactly 206/206 bytes consumed, 0 trailing.
- Matches entry description "nested uint8/string vectors, an empty int32 array and UTF-8 strings" (:118) and basis "length counts elements" (:117). Outermost-only summaries in both contract and tool; inner element types are not part of either, so no gap.

# Integrity chain
- `sha256sum` of the fixture = 51c6aa6c...12729 = `tests/gguf-identity/SHA256SUMS:4` = entry (:142); `stat` size 206 = (:143).
- `sha256sum tests/gguf-identity/expected.json` = 1ffe884a523fb85866ac43775fee0a5be1f69398c09a3dae8b8832f39c9f7f9f, equal to the pin recorded at final measurement (`.ufo/waves/round-20/build/out/GgufFixtures-final/measure-final-transcript.json:366-369`), so I compared against the same bytes that were frozen.
- Frozen harness record for this fixture (same transcript :91-125): actual_exit 0, actual_reason "decoded", status "pass", parsed block identical to my run on every recorded field (that capture projects a subset — it omits metadata_bytes/path).
- `.ufo/waves/round-20/c2/measure-reference.json:14` pins the same id/size/sha/expected_exit/expected_reason.

# Findings by severity
- None blocking for this item. Two L1-actionable notes, neither affecting this fixture's verdict:
  1. (low, docs) expected.json `limits.tool_default_max_kv` = 1000000 (:420) vs implementation 100000 (`tools/gguf-identity.py:32-34`) — already reported by the kv-count-2pow40 seat; kv_count 3 here is far under both.
  2. (low, contract wording) "named reason" is observable for success only via the exit_codes map, not tool output; if L1 wants a literal success reason, the tool would need to emit it. Current entry/exit agreement is exact, so no calibration impact.
- lsp checks unavailable: `xd://lsp` → "No such tool; mounted: ast_edit, debug". Comparison evidence is runtime + text, per fallback; no LSP-backed reference/definition/diagnostics claims are made.

# Scope
- Fixture + offline declared-metadata reader only: tensor payloads are never decoded (`tools/gguf-identity.py:9-10`); no serving, loaded-weight authentication, or model-quality claim is made or supported here.

# Residual risk / verification gaps
- I did not re-derive the other 22 fixtures; this verdict covers v3-nested-array only.
- The 727-byte stdout was parsed visually against the entry; a scripted deep-equality on the shared fields would be the mechanical form of the same comparison I performed field-by-field.
