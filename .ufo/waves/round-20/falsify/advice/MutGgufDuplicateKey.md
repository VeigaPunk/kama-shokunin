VERDICT: confirm - Removing duplicate-key rejection loses the expected malformed-input result; the assigned duplicate-key detector kills this mutant.

Scope: advisory mutation probe only; no C1/C2 admission or broader coverage judgment.
Source: /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gguf-identity.py:254-259.
Contract: /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/expected.json:354-362 requires exit 2 / duplicate_key; lines 9-22 require v3-minimal decoding at exit 0.
Fixture construction: /home/vgpnk/Projects/shokunin/kama-shokunin/tests/gguf-identity/make_fixtures.py:426-437 repeats test.duplicate with UINT8 values 1 and 2.
Mutant: delete only original lines 256-257 (`if key in seen:` and `raise GGUFError("duplicate_key")`) from /tmp/kama-r20-MutGgufDuplicateKey/gguf-identity.py; retain seen.add and all other behavior.
All scripts/fixtures were private copies; production source, committed evidence and registry were not edited.

Exact duplicate command, identical for pristine/mutated/restored:
`timeout 10s python3 -B /tmp/kama-r20-MutGgufDuplicateKey/gguf-identity.py /tmp/kama-r20-MutGgufDuplicateKey/duplicate-key.gguf --json`
Exact positive-control command, identical for all three stages:
`timeout 10s python3 -B /tmp/kama-r20-MutGgufDuplicateKey/gguf-identity.py /tmp/kama-r20-MutGgufDuplicateKey/v3-minimal.gguf --json`
Both commands ran from /home/vgpnk/Projects/shokunin/kama-shokunin, additionally bounded by subprocess.run(timeout=12).
Same in-memory probe(stage) checked duplicate exit=2, stdout empty, stderr exactly `gguf-identity: duplicate_key\n`; positive control required exit=0, stderr empty, JSON version=3, kv_count=0, tensor_count=0, and the pinned control SHA-256.

Observed actual CLI outputs/exits:
- Pristine duplicate: exit 2; stdout=""; stderr="gguf-identity: duplicate_key\n". Positive control: exit 0; stderr="".
- Mutated duplicate: exit 0; stderr=""; stdout is the decoded JSON below, not a malformed-input result. Positive control: exit 0; stderr="".
- Restored duplicate: exit 2; stdout=""; stderr="gguf-identity: duplicate_key\n". Positive control: exit 0; stderr="".
Mutated duplicate stdout (complete JSON, whitespace normalized):
`{"arrays":{},"endianness":"little","key_types":{},"keys":{"general.alignment":null,"general.architecture":null,"general.file_type":null,"general.name":null,"tokenizer.ggml.model":null},"kv_count":2,"metadata_bytes":78,"path":"/tmp/kama-r20-MutGgufDuplicateKey/duplicate-key.gguf","sha256":"4606213b88ea773f25d6b53c9d7144cf41c32bd08226ef5822fdb2b0f7cd21ef","size":78,"tensor_count":0,"version":3}`
Positive-control stdout for every stage (complete JSON, whitespace normalized):
`{"arrays":{},"endianness":"little","key_types":{},"keys":{"general.alignment":null,"general.architecture":null,"general.file_type":null,"general.name":null,"tokenizer.ggml.model":null},"kv_count":0,"metadata_bytes":24,"path":"/tmp/kama-r20-MutGgufDuplicateKey/v3-minimal.gguf","sha256":"a4e5e156ddec27e286f75328784d7106b60a4eb1d246e950a001a3f944fbda99","size":24,"tensor_count":0,"version":3}`
Logical detector results (not subprocess exit codes): pristine=0/pass, mutated=1/mismatch, restored=0/pass. Verdict: KILLED, not inconclusive; baseline and restoration both passed, and the positive control passed throughout.

SHA-256 evidence:
- Original source / pristine scratch / backup / restored scratch / source after: 195f71e7bfc4c1bc0da00acc6a348a6d2e0dbfa341cb1811ec4880231ccbf03f.
- Mutated scratch: 05c6b2b17845819d3c6302ab9ce78cafda6e547debbcaaa536a2c4478fd4f0f0.
- Duplicate fixture source and scratch: 4606213b88ea773f25d6b53c9d7144cf41c32bd08226ef5822fdb2b0f7cd21ef.
- Positive fixture source and scratch: a4e5e156ddec27e286f75328784d7106b60a4eb1d246e950a001a3f944fbda99.
Restoration: reinserted the exact two removed lines before running the restored probe; byte comparisons reported scratch_bytes_equal_original=true and source_bytes_equal_original=true. Final fixture source/scratch hash comparisons also returned true.
Cleanup: `rm -r -- /tmp/kama-r20-MutGgufDuplicateKey && test ! -e /tmp/kama-r20-MutGgufDuplicateKey` exited 0 with no output; scratch is removed.
No installs, services, model loads, Git/JJ operations, production edits or additional probes were performed.
Report: .ufo/waves/round-20/falsify/advice/MutGgufDuplicateKey.md
