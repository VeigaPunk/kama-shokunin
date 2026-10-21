VERDICT: confirm - 23 fixture outcomes pass; snapshot drift is reported as CNE2 with stable finding IDs.

# GgufFixtures scoped findings

## Delivered
- `.ufo/waves/round-20/build/out/GgufFixtures/tests/gguf-identity/make_fixtures.py`
- `.ufo/waves/round-20/build/out/GgufFixtures/tests/gguf-identity/expected.json`
- `.ufo/waves/round-20/build/out/GgufFixtures/tests/gguf-identity/SHA256SUMS`
- `.ufo/waves/round-20/build/out/GgufFixtures/tests/gguf-identity/fixtures/` (23 files)
- `.ufo/waves/round-20/build/out/GgufFixtures-final/measure-final.py`
- `.ufo/waves/round-20/build/out/GgufFixtures-final/measure-reference.json` (unchanged; SHA-256 `fb367e9e2c91eaadf4fb48bddb7a984a2c0c0feda41a45a00d75bbed182c5bc6`)
- `.ufo/waves/round-20/build/out/GgufFixtures-final/measure-final-transcript.json`
- `.ufo/waves/round-20/build/out/GgufFixtures-final/measure-final-selftest.json`

The stdlib generator encodes GGUF fields directly from the pinned spec; all files are below 4 KiB. The runner checks an external reference digest before using its pinned fixture/oracle/receipt-evidence hashes. Changed reference, expected manifest, fixture, oracle or receipt-evidence snapshots yield `snapshot_tampered`/exit 2; unavailable evidence also exits 2. Behavioral mismatches retain exit 1. The production parser's actual SHA-256 is recorded but is not a pass criterion.

The final runner locates the lane by finding `tools/gguf-identity.py` plus `registry` in an ancestor, and reads `measure-reference.json` beside itself, so defaults work from either `build/out/GgufFixtures-final/` or `.ufo/waves/round-20/c2/`. `--json` is accepted; `--fixtures-only` avoids model, oracle and receipt inputs. Full model/receipt mode remains implemented but was not run in this bounded correction.

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
- Fixture copy into `.ufo/waves/round-20/build/out/GgufFixtures/tests/gguf-identity/` — exit 0, no stdout. L1 copied the set into `tests/gguf-identity/`; the final runner validated its manifest and every file digest.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only 37bd4c5bd456a2f8a54d3312c28495c321715856 -- tools/gguf-identity.py` — exit 0, empty stdout; frozen state is `capability_absent`, not a fabricated parser failure.
- `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measure-final.py --selftest --json --timeout 5 --transcript /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measure-final-selftest.json` — exit 0; seven controls passed. Deleted fixture → `unavailable:fixture:v3-minimal`/CNE2; changed fixture, relabelled manifest, altered oracle, altered receipt evidence, and co-drifted reference → their stable `snapshot_tampered:*` IDs/CNE2; normal behavior mismatch remains exit 1.
- `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measure-final.py --fixtures-only --json --timeout 5 --transcript /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measure-final-transcript.json` — exit 0; 23/23 fixture rows passed, zero mismatches/unavailable; integrated parser hash `195f71e7bfc4c1bc0da00acc6a348a6d2e0dbfa341cb1811ec4880231ccbf03f`. Model/oracle/receipt reads were false in this fixture-only transcript.
- `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measure-final.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measure-reference.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measure-final-transcript.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufFixtures-final/measure-final-selftest.json /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gguf-identity.py` — exit 0; hashes respectively `a67e42b99d66fce34d89445aba7f07d829635458a991bfef01276f6d5baa9117`, `fb367e9e2c91eaadf4fb48bddb7a984a2c0c0feda41a45a00d75bbed182c5bc6`, `97ded07dc53a1905efcb6a8975ce05c8195de113873d30a9bbd2f65a339832c3`, `88e3b81951902d6cb0f78b21bea3fecc48a22276bf55f548495ab0d36fd0397f`, `195f71e7bfc4c1bc0da00acc6a348a6d2e0dbfa341cb1811ec4880231ccbf03f`.
- No tool was installed or updated. No live server, build, lint, or full C2 survivors ran. L1 integrated production code; this seat changed only its assigned output artifacts and advisory report.

## Risks / blockers
- L1 reports that the `gguf` 0.19.0 wheel and a same-version pinned-source snapshot differ; the independent reference stays pinned to the wheel hash, not a claim of source equivalence.
- The final correction intentionally did not rerun model/receipt mode; no post-correction model/receipt result is claimed.
- Blockers: none.
