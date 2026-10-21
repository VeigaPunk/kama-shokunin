VERDICT: confirm - Version-1 fixture fails closed with the expected named reason and pinned digest.

- Exact command: `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gguf-identity.py /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/fixtures/version-1.gguf --json` returned exit 2; stdout was empty; stderr was `gguf-identity: unsupported_version`.
- `tests/gguf-identity/expected.json:277-286` specifies `expected_exit: 2`, `expected_reason: "unsupported_version"`, version 1, little-endian, zero counts, and size 16. It has no `metadata` object, matching the absence of decoded metadata on this rejection.
- `tests/gguf-identity/SHA256SUMS:11` pins `3d4d198e376009ce341ce70a37f8861a5692bb7190e6e922afcdf0c681f56933` for `fixtures/version-1.gguf`; `sha256sum -c SHA256SUMS` reported that fixture `OK`.
- Source behavior is consistent: `tools/gguf-identity.py:244` raises `unsupported_version`; `:964-966` emits the named error on stderr and returns its exit code before the JSON-output branch at `:982-983`.

This fixture establishes parser rejection behavior only; it provides no evidence of serving, model loading, loaded-weight authentication, or model quality.