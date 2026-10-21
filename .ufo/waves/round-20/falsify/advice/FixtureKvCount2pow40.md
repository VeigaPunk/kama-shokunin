VERDICT: partial - The fixture's exit, reason, and encoded metadata match; expected.json misstates the tool's default KV limit.

## Findings (by severity)

- Low — `tests/gguf-identity/expected.json:327,420` says the tool's default `--max-kv` is 1,000,000. The implementation sets both `MAX_KV_LIMIT` and `DEFAULT_MAX_KV` to 100,000 (`tools/gguf-identity.py:32-34`). Thus the fixture's basis and global `tool_default_max_kv` metadata are inaccurate. This particular case still rejects as expected because its count (2^40) exceeds either limit; the mismatch does not explain or invalidate this observed rejection.

## Fixture result

- Ran the assigned command with `/usr/bin/python3`: exit 2; stdout empty; stderr exactly `gguf-identity: kv_count_too_large\n`. The parser checks `kv_count > max_kv` and raises that named reason (`tools/gguf-identity.py:246-249`); `main` reports parser errors on stderr and returns the error code (`tools/gguf-identity.py:961-966`).
- `expected.json:330-331` expects exit 2 and reason `kv_count_too_large`: both match.
- Actual fixture is 24 bytes and SHA-256 is `c7956947aa09e2c2f3304ffd7eba18b54520446b4baf93667af75ef3aaef690b`; this matches `expected.json:335-336` and `SHA256SUMS:16`.
- The 24-byte header decodes as GGUF v3, little-endian, tensor_count 0, kv_count 1099511627776 (2^40); those fields match `expected.json:328-338`. The `--json` run emits no JSON for this rejected file; the header metadata comparison is against the fixture bytes and pinned manifest, not runtime JSON output.

## Residual risk and verification gaps

- Confirms only parser behavior for this fixture. It establishes nothing about serving, loading, authentication, or model quality.
- No other fixtures or runtime paths were tested. No tools installed.