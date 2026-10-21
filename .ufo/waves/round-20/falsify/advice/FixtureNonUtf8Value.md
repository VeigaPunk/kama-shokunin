VERDICT: confirm - non-utf8-value.gguf produces exactly exit 2, named reason `invalid_utf8` on stderr, no stdout metadata; hash/size match expected.json and SHA256SUMS; fixture provably exercises the string-value decode path and the tool is offline parser-only.

# Observed run (pinned command, measured at HEAD 846e366dc9dbac58463494a7e05ad060ae3ed3b0; `git status --porcelain` clean for tools/gguf-identity.py and tests/gguf-identity/)
- Command: `/usr/bin/python3 tools/gguf-identity.py tests/gguf-identity/fixtures/non-utf8-value.gguf --json` from kama-shokunin root.
- Exit: 2. stdout: 0 bytes (od-verified empty). stderr: exactly `gguf-identity: invalid_utf8\n` (28 bytes, od-verified).
- Without `--json`: byte-identical stdout and stderr, same exit 2 (cmp clean) — the flag does not alter the error contract.

# Comparison against tests/gguf-identity/expected.json (entry lines 374-383)
- expected_exit: 2 (expected.json:376) vs observed 2 — MATCH.
- expected_reason: "invalid_utf8" (expected.json:378) vs stderr reason `invalid_utf8` — MATCH.
- basis "GGUF string payloads are UTF-8: gguf.md:231-237" (expected.json:375) — parser raises on UnicodeDecodeError at tools/gguf-identity.py:157-160; consistent.
- sha256 expected 66f173acbefd382ca9557bcfb88266fd3d54e39864ecde598bfe4cd424b5688a (expected.json:381) — MATCH observed sha256sum.
- size_bytes: 58 (expected.json:382) — MATCH observed 58B.

# Comparison against tests/gguf-identity/SHA256SUMS
- Line 20: `66f173acbefd382ca9557bcfb88266fd3d54e39864ecde598bfe4cd424b5688a  fixtures/non-utf8-value.gguf` — identical to measured hash.
- `sha256sum -c SHA256SUMS` from tests/gguf-identity/: `fixtures/non-utf8-value.gguf: OK` (also non-utf8-key OK; no FAILED lines).

# Metadata semantics
- Error path emits no JSON metadata by design: main() returns at tools/gguf-identity.py:964-966 before the metadata print at :982-990. expected.json declares no metadata payload for this entry — absence is the contract, and observed absence matches.

# Value-path attribution (fixture is not a key-fixture reroute)
- Hexdump: key_len=0x0d at 0x18, key bytes 0x20..0x2c are ASCII `test.bad_utf8`, value type 0x08 (STRING) at 0x2d, value length 1, sole payload byte 0xff at 0x39 (file ends at 58B). The key decodes cleanly; the UnicodeDecodeError can only fire on the value decode (tools/gguf-identity.py:159-160). The ASCII/key-restriction check raising `invalid_key` (:161-162) is downstream and untouched.
- expected.json deliberately gives non-utf8-key and non-utf8-value the same reason `invalid_utf8` but distinct bases (:367-368 vs :375); that conflation is in the contract, not an artifact. Distinct hashes (SHA256SUMS:19-20) and sizes (43B vs 58B) rule out same-file reuse.

# C2 boundary (parser behavior only)
- No socket/urllib/requests/http/subprocess matches in tools/gguf-identity.py; the reader consumes file bytes only. No serving, weight-loading, authentication or model-quality behavior is exercised by this fixture — claim boundary holds.
- Exit-code provenance: GGUFError defaults exit_code=2 (tools/gguf-identity.py:74); bad_magic alone overrides to 1 (:235); file_unavailable is 3 (:968-969) — matches expected.json exit_codes table.

# Residual risk / verification gaps
- Evidence measured at HEAD 846e366d; C1's frozen tree is 0957ce61. No tree pin exists for this C2 item, so no mismatch is claimable here, but if C2 is later frozen to 0957ce61 the run should be repeated on that checkout. [OBSERVED, not a defect]
- Only the single invalid byte 0xff was tested; multi-byte truncated-sequence and overlong-encoding variants would hit the same raise site — inference from code path, not separately executed.
- Scratch /tmp/kama-r20-FNV removed before return; no production files touched.
