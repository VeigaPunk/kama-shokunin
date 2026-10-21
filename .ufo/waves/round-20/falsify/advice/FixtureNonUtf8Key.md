VERDICT: confirm - exit, named reason, and pinned fixture digest match the expected entry.

## Evidence
- Ran the assigned `/usr/bin/python3 .../tools/gguf-identity.py .../fixtures/non-utf8-key.gguf --json` command. Exit: `2`; stdout: empty; stderr: `gguf-identity: invalid_utf8`.
- `tests/gguf-identity/expected.json:366-372` expects exit `2`, reason `invalid_utf8`, SHA-256 `ff6c67089a63180feb7fcf6ecc41bf75b1303ec4348a4521f7e02ef821dc4761`, and size 43 bytes. The observed SHA-256 and size match; `SHA256SUMS:19` independently pins the same digest.
- The fixture bytes show key `test.\xff` (invalid UTF-8). `tools/gguf-identity.py:158-160` strictly decodes UTF-8 and maps `UnicodeDecodeError` to `invalid_utf8`; `:964-966` prints the reason and returns the error's exit code.
- The expected entry has no `metadata` field. This parse failure exits before a successful result is returned, so no metadata is emitted; no metadata content is expected by this fixture entry.

## Findings
None for the assigned parser fixture: the declared exit, named reason, and digest/size match.

## Residual risk
`--json` failure output is not JSON: this run produced no stdout and the reason on stderr. The manifest specifies the failure exit/reason but no structured error object; whether callers require JSON-encoded errors is not established by this fixture. This test establishes parser behavior only, not serving, loading, authentication, or model quality.

## Verification gaps
The `xd://lsp` device is unavailable (the read returned “No such tool”; mounted devices were `ast_edit` and `debug`), so LSP status/references/definition/diagnostics could not be checked. No semantic caller claim is made.