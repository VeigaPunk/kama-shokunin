VERDICT: confirm - 23 fixtures and pinned measurement pass against the integrated parser, oracle, and receipt.

# GgufFixtures scoped findings

## Delivered
- `.ufo/waves/round-20/build/out/GgufFixtures/tests/gguf-identity/make_fixtures.py`
- `.ufo/waves/round-20/build/out/GgufFixtures/tests/gguf-identity/expected.json`
- `.ufo/waves/round-20/build/out/GgufFixtures/tests/gguf-identity/SHA256SUMS`
- `.ufo/waves/round-20/build/out/GgufFixtures/tests/gguf-identity/fixtures/` (23 files)
- `.ufo/waves/round-20/build/out/GgufFixtures-final/measure.py`
- `.ufo/waves/round-20/build/out/GgufFixtures-final/measure-reference.json`
- `.ufo/waves/round-20/build/out/GgufFixtures-final/measurement-transcript.json`

The stdlib generator encodes fields directly from the pinned GGUF spec; all 23 files are below 4 KiB. The independent reference pins the full fixture manifest, expected-file and fixture SHA-256 values, oracle JSON/wheel identities and projections, production-tool SHA-256, and the prior parser receipt result. The measurement reports all fixture rows, per-field mismatches, the frozen-before capability state, exact model/oracle identity comparison, and the production tool's `receipt` object. Its exits are 0 pass, 1 mismatch, 2 unavailable; reason aliases preserve exact expected exit codes.

The final receipt reports `engine-agreement`: GGUF `llama.context_length` 2048 equals receipt `meta.n_ctx_train` 2048; `props_n_ctx=256` remains informational-only; `total_slots=4` with no slot division. The receipt identifies its scope as self-report, not authenticated execution.

## Specification evidence

Pinned source: `ggml-org/ggml` `docs/gguf.md`, revision `da8e2a54b919557b816b1c2beb432ccb766f7ce0`, SHA-256 `1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020`.

- `docs/gguf.md@da8e2a54b919557b816b1c2beb432ccb766f7ce0, §File Structure:278-283`: “Must be `GGUF` at the byte level: `0x47` `0x47` `0x55` `0x46`.”
- `... , §File Structure:151`: “Models are little-endian by default. They can also come in big-endian for use with big-endian computers; in this case, all values (including metadata values and tensors) will also be big-endian.”
- `... , §File Structure:198-228` defines scalar value-type codes 0-8 and 10-12 and ARRAY=9; `... , §File Structure:219-222`: “Arrays can be nested, and the length of the array is the number of elements in the array, not the number of bytes.”
- `... , §File Structure:294-298` defines uint64 tensor/KV counts; `... , §Version History:770-776` says v3 adds big-endian and v2 changed most countable values to uint64.

The duplicate-key, resource-bound and named-error expectations are tool-contract checks rather than claims that the format specification explicitly forbids duplicate keys or fixes resource ceilings.

## Executed evidence
- `git ls-remote https://github.com/ggml-org/ggml refs/heads/master` — exit 0; stdout `da8e2a54b919557b816b1c2beb432ccb766f7ce0 refs/heads/master`.
- `curl -sSfL -o /tmp/kama-r20-GgufFixtures/spec/gguf.md https://raw.githubusercontent.com/ggml-org/ggml/da8e2a54b919557b816b1c2beb432ccb766f7ce0/docs/gguf.md && sha256sum /tmp/kama-r20-GgufFixtures/spec/gguf.md && wc -lc /tmp/kama-r20-GgufFixtures/spec/gguf.md` — exit 0; SHA-256 `1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020`; 828 lines, 43,175 bytes.
- `python3 /tmp/kama-r20-GgufFixtures/lane/tests/gguf-identity/make_fixtures.py` — exit 0; generated 23 fixtures and printed each size/hash/exit/reason.
- `mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures/tests/gguf-identity && cp -a /tmp/kama-r20-GgufFixtures/lane/tests/gguf-identity/make_fixtures.py /tmp/kama-r20-GgufFixtures/lane/tests/gguf-identity/expected.json /tmp/kama-r20-GgufFixtures/lane/tests/gguf-identity/SHA256SUMS /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures/tests/gguf-identity/ && cp -a /tmp/kama-r20-GgufFixtures/lane/tests/gguf-identity/fixtures /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures/tests/gguf-identity/` — exit 0; no stdout. L1 later copied the fixture set into `tests/gguf-identity/`; the final measurement validated its manifest and file hashes.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only 37bd4c5bd456a2f8a54d3312c28495c321715856 -- tools/gguf-identity.py` — exit 0, empty stdout: frozen state is `capability_absent`, not a fabricated parser failure.
- `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gguf-identity.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufTool-final/stories260K-receipt.json /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/expected.json` — exit 0; digests respectively `3b7eb757d942ea6c541fad12f9974c103dce62f7057ef3f6fd31e2e601cb921a`, `61529605c2519728ca085ec3c9d6e851b3cb875010220a1e2f37e6e01b3098a7`, `1ffe884a523fb85866ac43775fee0a5be1f69398c09a3dae8b8832f39c9f7f9f`.
- `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measure.py --tool /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gguf-identity.py --oracle /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufOracle/stories260K.oracle.json --expected /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/expected.json --model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live-recovery/receipt-1.json --receipt-evidence /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufTool-final/stories260K-receipt.json --repo /home/vgpnk/Projects/shokunin/kama-shokunin --reference /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measure-reference.json --timeout 5 --transcript /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measurement-transcript.json` — exit 0; stdout JSON: 23/23 fixtures pass, zero mismatches/unavailable; real model v3, 48 tensors, 19 KV, expected SHA-256; receipt status `engine-agreement`.
- `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measure.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measure-reference.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measurement-transcript.json` — exit 0; hashes respectively `6a3fba1a049b2be3521ba4337cd4c8c0d7909aad5da2e5148dbec5c6cd15bc67`, `fb367e9e2c91eaadf4fb48bddb7a984a2c0c0feda41a45a00d75bbed182c5bc6`, `c872c8ba0a6ecb6f398f18bc5d68e9818ebed488333e8522217b46319f564f80`.
- One earlier draft harness invocation exited 2 with a `TypeError` in its oracle-validator return path before any parser call; that harness defect was corrected before the successful run above.
- No tool was installed or updated. No live server, build, lint, full C2 survivors, or selftest was run by this seat. The L1 integrated the production reader and copied fixtures; this seat wrote only the assigned output artifacts and this advisory report.

## Risks / blockers
- The independent oracle is the pinned `gguf` 0.19.0 wheel; the L1 reports a same-version pinned-source divergence acknowledged by `SrcGgufPyReader`. Expected values are tied to the wheel hash, not a claim of source equivalence.
- Blockers: none.
