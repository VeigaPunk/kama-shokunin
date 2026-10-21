VERDICT: confirm - the duplicate-key fixture matches its pinned fail-closed parser exit, reason, and bytes.

## Scope
This confirms this fixture's parser behavior only. It makes no claim about serving, model loading, loaded-weight authentication, or model quality.

## Findings by severity
- None. The observed parser result and fixture digest match the pinned expectations.

## Evidence
- Ran the assigned absolute-path command with `--json`: `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gguf-identity.py /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/fixtures/duplicate-key.gguf --json`.
- Observed exit `2`; stdout was empty; stderr was exactly `gguf-identity: duplicate_key\n`.
- `tests/gguf-identity/expected.json:357-362` gives `expected_exit: 2`, `expected_reason: duplicate_key`, describes two records with the same key, and pins SHA-256 `4606213b88ea773f25d6b53c9d7144cf41c32bd08226ef5822fdb2b0f7cd21ef` and size 78 bytes. The rejected-fixture entry has no `metadata` field.
- Actual `sha256sum` and `stat` returned that same digest and 78 bytes; `tests/gguf-identity/SHA256SUMS:18` lists the same digest for `fixtures/duplicate-key.gguf`.
- Parser source checks for an already-seen key and raises `duplicate_key` (`tools/gguf-identity.py:254-258`). The CLI emits that named reason and returns its exit code on `GGUFError` before the success JSON serialization path (`tools/gguf-identity.py:961-966,982-984`). Thus this rejection returns no metadata object, consistent with the expected entry containing none.

## Residual risk and verification gaps
- The `--json` invocation's parse-error path is plain stderr, not a JSON error envelope; the pinned expected record specifies exit/reason and no error-envelope or metadata schema for this rejection.
- LSP status was unavailable: attempting `read xd://lsp` returned “No such tool” (only `ast_edit` and `debug` were mounted). No LSP references/definition/diagnostics check was possible; direct execution and fixture-byte checks establish only this scoped parser outcome.
