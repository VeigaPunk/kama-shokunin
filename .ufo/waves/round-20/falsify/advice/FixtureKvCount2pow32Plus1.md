VERDICT: confirm - observed exit 2, named reason kv_count_too_large, and header metadata all match expected.json and SHA256SUMS exactly; no defect found in scope.

# Command under test (exact, per lane)
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gguf-identity.py /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/fixtures/kv-count-2pow32-plus1.gguf --json

# Observed (pinned run)
- exit=2; stdout empty (0 bytes); stderr exactly `gguf-identity: kv_count_too_large` (captured via separate stdout/stderr redirects under scratch /tmp/kama-r20-kvc32, removed after).

# Contract comparison — all match
- tests/gguf-identity/expected.json:343-350, id kv-count-2pow32-plus1: expected_exit=2, expected_reason="kv_count_too_large" -> both exact.
- expected.json:348-350: kv_count=4294967297, sha256=40d8775ea8dfc7f0d8a8905116dae41dd73367f0b151b0450a334ffa9e777fa0, size_bytes=24.
- tests/gguf-identity/SHA256SUMS:17 lists that digest for fixtures/kv-count-2pow32-plus1.gguf; sha256sum of the fixture reproduces it byte-exact; stat size=24.
- Fixture bytes (xxd, 24-byte header-only file): magic "GGUF", version=3 LE, tensor_count=0, kv_count=0x0000000100000001=4294967297=2^32+1 -> matches expected.json description "v3 metadata_kv_count is 4294967297; there are no following KV records."

# Mechanism verified in tools/gguf-identity.py
- :247 kv_count = reader.u64("kv_count"); u64 is an unsigned "Q" unpack (:148-149) — no u32 wraparound, 2^32+1 preserved (does not silently become 1).
- :248-249 `if kv_count > max_kv: raise GGUFError("kv_count_too_large")` with default DEFAULT_MAX_KV=100_000; the check precedes the per-record loop (:258+), so no iteration/allocation toward 2^32+1 records — fail-closed and bounded.
- GGUFError defaults to exit_code=2 -> observed exit matches expected_exit.
- main():964-966: GGUFError path prints plain `gguf-identity: <reason>` to stderr and returns the code; --json output is emitted only on the success path (:982-983). expected.json's contract (exit_codes map: 2 = "malformed or unsupported (named reason)") requires exit + named reason, not JSON formatting on the error path, so empty stdout with --json is contract-conformant, not a defect.
- Acceptance cannot be forced via CLI: --max-kv is clamped by nonnegative_limited(value, MAX_KV_LIMIT=100_000) (:940-941), so no invocation can raise the limit to admit kv_count=2^32+1.

# Attack angles exercised
- u32 wraparound to kv_count=1 (would produce a different reason such as truncated): refuted by the u64 read and the observed named reason.
- unbounded record loop / resource exhaustion on 2^32+1: refuted by check ordering (:248 before the read loop).
- verdict/reason mismatch or silent success: refuted; reason byte-exact, exit 2.
- C2 scope boundary respected: run performed declared-metadata parsing only; no serving, weight loading, authentication, or model-quality output.

# Residual notes
- The fixture is not limit-discriminating: any kv_count > 100_000 yields the same reason (kv-count-2pow40 behaves identically). Its regression value is the u64-vs-u32 wraparound probe, which passes.
- Selftest covers the same named reason only via a lowered max_kv=1 (:779-780); this fixture exercises the default-limit path — complementary coverage, both route to :248-249.
- [INFERENCE/unavailable] Pinned tree 0957ce619789d13bb5779606078fa1498114d2c7 not independently re-verified: Git/JJ operations are out of lane bounds; all cited evidence is from the live working-tree files as read.
- No mutation outside scratch /tmp/kama-r20-kvc32 (removed); no installs performed.
