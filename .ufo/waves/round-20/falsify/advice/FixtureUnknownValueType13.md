VERDICT: confirm - type 13 is rejected with the expected named parser error and the fixture checksum matches.

## Findings
- None. The pinned fixture behavior matches the expected result.

## Evidence
- Executed exactly: `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gguf-identity.py /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/fixtures/unknown-value-type-13.gguf --json`.
  Exit status: `2`; stdout empty; stderr: `gguf-identity: unknown_value_type`.
- `tests/gguf-identity/expected.json:317-324` identifies the metadata `value_type` as the first unassigned enum value `13`, expects exit `2` and reason `unknown_value_type`, and records size `48` and SHA-256 `c3b413ffe6dacf6126ae03f740614d5db2e84ff6a0694514afff822b49ae422a`. This error fixture has no decoded `metadata` field in the expected row.
- `tests/gguf-identity/SHA256SUMS:15` has the same digest. `sha256sum -c SHA256SUMS` reported `fixtures/unknown-value-type-13.gguf: OK`.
- `od -An -v -tx1 tests/gguf-identity/fixtures/unknown-value-type-13.gguf` shows the 48-byte fixture ending in key `test.unknown` followed by `0d 00 00 00` (value type 13). `tools/gguf-identity.py:50-55` defines only codes 0-12; lines 165-167 raise `unknown_value_type` for any other code.
- `tools/gguf-identity.py:961-966` catches this parser error, writes the named reason to stderr, and returns its exit code before the JSON-output path at lines 982-984. Thus empty stdout/no metadata payload is consistent with this invalid-type fixture, not a metadata mismatch.

## Residual risk
- This confirms only parser behavior for this fixture. It establishes nothing about serving, model loading, loaded-weight authentication, or model quality.

## Verification gaps
- No LSP device was available (`read xd://lsp` returned “No such tool”; mounted devices were `ast_edit` and `debug`), so LSP references/definition/diagnostics were unavailable. Source locations above were checked by direct reads; grep was used only as a fallback to locate symbols.
