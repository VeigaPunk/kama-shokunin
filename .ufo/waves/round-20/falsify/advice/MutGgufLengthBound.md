VERDICT: confirm - The length-bound mutant loses the pinned string_too_large result and is killed by the named-reason detector; malformed-file exit 2 remains.

Scope: one mutation in /tmp/kama-r20-MutGgufLengthBound/gguf-identity.py; production source and fixtures were read-only. No installs, services, Git operations, delegated probes or other mutations.
Axes: bounded behavioral sensitivity, passing positive control, exact restoration, scratch isolation.

Mutant:
- Source: /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gguf-identity.py:151-156.
- Scratch line 153 changed from `limit = min(self.max_str, MAX_KEY_BYTES) if key else self.max_str` to `limit = min(self.max_str, MAX_KEY_BYTES) if key else (1 << 64) - 1`.
- This raises the value-string cap from the default 1,048,576 bytes to UINT64_MAX, leaving the key cap and all other checks unchanged.
- /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/make_fixtures.py:378-389 declares UINT64_MAX for the assigned malformed fixture.

Expected detector:
- /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/expected.json:309-314 pins exit 2 and reason string_too_large.
- The same in-memory subprocess detector ran on pristine, mutated and restored bytes, with a 5-second command deadline and 1-second kill grace (outer subprocess timeout 8 seconds).
- Negative assertion: exit 2, empty stdout, stderr exactly `gguf-identity: string_too_large\n`.
- Positive assertion: exit 0, empty stderr, JSON version=3, tensor_count=0, kv_count=0, size=24 and the pinned SHA-256 below.

Exact commands (each executed in all three stages):
`/usr/bin/timeout --kill-after=1s 5s /usr/bin/python3 /tmp/kama-r20-MutGgufLengthBound/gguf-identity.py /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/fixtures/string-length-exceeds-file.gguf --json`
`/usr/bin/timeout --kill-after=1s 5s /usr/bin/python3 /tmp/kama-r20-MutGgufLengthBound/gguf-identity.py /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/fixtures/v3-minimal.gguf --json`

Observed outputs:
- Pristine negative: exit 2; stdout=""; stderr="gguf-identity: string_too_large\n"; detector PASS.
- Mutated negative: exit 2; stdout=""; stderr="gguf-identity: truncated_string_value\n"; detector FAIL.
- Restored negative: exit 2; stdout=""; stderr="gguf-identity: string_too_large\n"; detector PASS.
- Positive control: exits [0,0,0], stderr ["","",""]; stdout byte-identical across all stages.
- Positive stdout (compact JSON rendering): {"arrays":{},"endianness":"little","key_types":{},"keys":{"general.alignment":null,"general.architecture":null,"general.file_type":null,"general.name":null,"tokenizer.ggml.model":null},"kv_count":0,"metadata_bytes":24,"path":"/home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/fixtures/v3-minimal.gguf","sha256":"a4e5e156ddec27e286f75328784d7106b60a4eb1d246e950a001a3f944fbda99","size":24,"tensor_count":0,"version":3}
- MUTANT VERDICT: KILLED by the exact named-reason assertion, with a passing baseline and restored replay. No timeout or crash occurred.
- Limitation: generic malformed-file rejection was NOT lost. /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gguf-identity.py:111-118 still rejects the out-of-file read. An exit-only assertion would not distinguish these observed results; acceptance of this malformed fixture is not demonstrated.

SHA-256 and restoration evidence:
- Before: source, scratch and saved pristine copy all 195f71e7bfc4c1bc0da00acc6a348a6d2e0dbfa341cb1811ec4880231ccbf03f.
- Mutated scratch: 1817cfe8db5b2f201016eaf684b4ca0ff80381024557bcc8210e8e158d2c51be.
- Restore command (in finally): `/usr/bin/cp -- /tmp/kama-r20-MutGgufLengthBound/gguf-identity.py.pristine /tmp/kama-r20-MutGgufLengthBound/gguf-identity.py`; exit 0.
- After restore: source, scratch and saved pristine copy all 195f71e7bfc4c1bc0da00acc6a348a6d2e0dbfa341cb1811ec4880231ccbf03f.
- `cmp -- /tmp/kama-r20-MutGgufLengthBound/gguf-identity.py.pristine /tmp/kama-r20-MutGgufLengthBound/gguf-identity.py` exited 0 before cleanup.
- Actual fixture hashes: string-length-exceeds-file.gguf=e932e98a3558d63c804ab0f243f90dbec87546f93a15fee6a8fa0255f678c808; v3-minimal.gguf=a4e5e156ddec27e286f75328784d7106b60a4eb1d246e950a001a3f944fbda99.
- `rm -r -- /tmp/kama-r20-MutGgufLengthBound && test ! -e /tmp/kama-r20-MutGgufLengthBound` exited 0; scratch removal verified before report creation.
