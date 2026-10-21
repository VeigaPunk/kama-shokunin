VERDICT: confirm - KILLED: removing the nested-array guard makes the fixed over-depth fixture succeed and the parser selftest fail; pristine and restored controls pass.

Scope/axes: regression sensitivity, causal isolation, exact restoration; one private scratch mutant only. No lane, committed-evidence, registry, or production writes; no installs, services, model loads, delegated probes, or Git/JJ operations.
Mutant: copied /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gguf-identity.py into /tmp/kama-r20-MutGgufArrayDepth/gguf-identity.py, then deleted only original lines 172-173 (`if depth >= MAX_ARRAY_DEPTH:` and its `raise GGUFError("array_nesting_too_deep")`). Constant 32, recursion, fixture bytes, and assertions were unchanged.
Contract: /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gguf-identity.py:39,165-174; its existing array_depth_limit assertion is at :802-806 and failure exit at :914-922.
Fixture oracle: /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/expected.json:404-412 specifies exit 2 / array_nesting_too_deep for array-nesting-exceeds-limit.gguf.
Expected detector: pristine/restored selftest exit 0 and over-depth CLI exit 2 with the exact reason; removing the guard should cause selftest exit 1 and over-depth CLI exit 0. Valid nested-array positive control should remain exit 0.

Exact commands (all three run unchanged on pristine, mutated, and restored scratch bytes; cwd /home/vgpnk/Projects/shokunin/kama-shokunin):
D1: timeout 10s python3 -B /tmp/kama-r20-MutGgufArrayDepth/gguf-identity.py --selftest
D2: timeout 10s python3 -B /tmp/kama-r20-MutGgufArrayDepth/gguf-identity.py /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/fixtures/array-nesting-exceeds-limit.gguf --json
D3: timeout 10s python3 -B /tmp/kama-r20-MutGgufArrayDepth/gguf-identity.py /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/fixtures/v3-nested-array.gguf --json
Each invocation was additionally bounded by subprocess.run(timeout=12), with stdout/stderr captured; none timed out.

Observed outputs (JSON below reserialized compactly; selftest lists only diagnostic/count fields, not its unchanged 30-name cases list):
Pristine D1: exit=0; stderr=''; stdout fields={"case_count":30,"failed":[],"passed":30,"status":"passed"}.
Pristine D2: exit=2; stdout=''; stderr='gguf-identity: array_nesting_too_deep\n'.
Pristine D3: exit=0; stderr=''; stdout JSON is the positive-control JSON below.
Mutated D1: exit=1; stderr=''; stdout fields={"case_count":30,"failed":[{"case":"array_depth_limit","expected":"array_nesting_too_deep","observed":"success"}],"passed":29,"status":"failed"}.
Mutated D2: exit=0; stderr=''; stdout JSON={"arrays":{"test.deep":{"length":1,"type":"ARRAY"}},"endianness":"little","key_types":{},"keys":{"general.alignment":null,"general.architecture":null,"general.file_type":null,"general.name":null,"tokenizer.ggml.model":null},"kv_count":1,"metadata_bytes":538,"path":"/home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/fixtures/array-nesting-exceeds-limit.gguf","sha256":"201606a9107a21a94fd015c3e2a41bf851e711572177b8667bfa61563a91e052","size":538,"tensor_count":0,"version":3}.
Mutated D3: exit=0; stderr=''; stdout exactly unchanged from pristine.
Restored D1: exit=0; stderr=''; stdout fields={"case_count":30,"failed":[],"passed":30,"status":"passed"}.
Restored D2: exit=2; stdout=''; stderr='gguf-identity: array_nesting_too_deep\n'.
Restored D3: exit=0; stderr=''; stdout exactly unchanged from pristine.
Positive-control stdout JSON={"arrays":{"test.empty":{"length":0,"type":"INT32"},"test.nested":{"length":2,"type":"ARRAY"},"test.strings":{"length":3,"type":"STRING"}},"endianness":"little","key_types":{},"keys":{"general.alignment":null,"general.architecture":null,"general.file_type":null,"general.name":null,"tokenizer.ggml.model":null},"kv_count":3,"metadata_bytes":206,"path":"/home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/fixtures/v3-nested-array.gguf","sha256":"51c6aa6c677575a0ca734498875f5d0ebbe1c05c56d1d58063d7c57e90412729","size":206,"tensor_count":0,"version":3}.
Captured result comparison: restored_output_exactly_matches_pristine=True for all three commands, including exits and complete stdout/stderr; positive_control_output_unchanged=True across all phases.

SHA-256/restoration evidence (sha256sum exit=0):
Source, pristine scratch and backup before mutation: 195f71e7bfc4c1bc0da00acc6a348a6d2e0dbfa341cb1811ec4880231ccbf03f.
Mutated scratch: db3aa6add51c5b3bda5448d022f5c70116bc26ca23faab62f54f1be33b684a4a.
Restored scratch, retained pristine backup and source after restoration: 195f71e7bfc4c1bc0da00acc6a348a6d2e0dbfa341cb1811ec4880231ccbf03f.
Over-depth fixture before/after: 201606a9107a21a94fd015c3e2a41bf851e711572177b8667bfa61563a91e052.
Positive-control fixture before/after: 51c6aa6c677575a0ca734498875f5d0ebbe1c05c56d1d58063d7c57e90412729.
Restoration command: cp --preserve=mode,timestamps -- /tmp/kama-r20-MutGgufArrayDepth/gguf-identity.pristine.py /tmp/kama-r20-MutGgufArrayDepth/gguf-identity.py
Byte comparison: cmp -- /tmp/kama-r20-MutGgufArrayDepth/gguf-identity.pristine.py /tmp/kama-r20-MutGgufArrayDepth/gguf-identity.py ; exit=0, no output, before restored detector runs.
Cleanup command: rm -r -- /tmp/kama-r20-MutGgufArrayDepth && test ! -e /tmp/kama-r20-MutGgufArrayDepth && printf 'scratch_removed=true\ncleanup_exit=0\n'
Cleanup exit=0; stdout='scratch_removed=true\ncleanup_exit=0\n'; scratch removed before return.
Conclusion: KILLED, not an inconclusive baseline failure or crash-as-rejection: the unchanged parser regression names only array_depth_limit as failed with observed success, while the fixed fixture actually changes exit 2 to exit 0. This establishes sensitivity to this single missing guard, not exhaustive depth or parser coverage.
