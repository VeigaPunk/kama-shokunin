VERDICT: confirm - delivered 26 named mutant designs with discriminating fixtures and oracles; none executed

Axes: operability (assigned 8): bounded, actionable detector design; calibration (assigned 7): distinguish expected outcomes from observed verdicts. No axis score or capability measurement claimed.

Deliverable: `.ufo/waves/round-20/build/out/MutGgufPlan/mutants.json` (40,995 bytes reported by write tool).

Scope/result:
- GGUF-M01–M16: magic/version, high-word uint64 counts, scalar endianness/width, duplicates, truncated reads, unknown types, UTF-8, architecture namespace, array counts/bounds/string traversal, KV alignment and explicit alignment metadata.
- GGUF-M17–M26: alias versus digest, pre versus post hash, whole-file hashing, slot multiply/divide, requested versus observed context, equality boundary, warning versus failure, unavailable evidence and boolean numeric coercion.
- Every entry names one behavior-bearing mutation, a concrete fixture recipe, independent authority/oracle, and assertions that must distinguish pristine from mutated behavior.
- [INFERENCE] Expected kills and fixture/oracle results are designs only. All current mutant verdicts are `not-run`; actual pristine/mutated/restored outputs and mutation hashes are null.
- No subject bytes were mutated, so exact-byte restoration is not applicable. Reference-source hashes are provenance only, not fabricated restoration evidence.

Detector requirements:
- Freeze fixtures and independent expectations before mutation; use the identical bounded detector on pristine, mutated and exactly restored bytes. Baseline/restoration failure is inconclusive.
- A crash, signal, timeout, silent nonzero, early-abort selftest, target literal, or missing selected-case outcome is not a kill. Require the identified subject result and the full expected result fields.
- Slot arithmetic, equality, endianness, array-length and warning mutants require semantic assertions: successful exit agreement alone does not detect them.
- [INFERENCE] M03 is a header-only uint64 wire witness, not a valid enormous complete model; M04 checks declared lane count limits without invoking a potentially unbounded official reader.
- Positive complete synthetic fixtures should freeze official `gguf.GGUFReader` projections independently of the subject's own fixture helpers. New-fixture official-reader results were not executed here.

Evidence read:
- Delivered parser and reconciliation helper were inspected read-only; exact paths/hashes are in JSON `reference_targets`. The helper was separate at inspection, so integrated `--receipt` behavior is not asserted.
- Existing peer artifact `out/GgufOracle/stories260K.oracle.json`, L2–L15 and L29–L43, records gguf 0.19.0 provenance and real-model identity. This seat read it, not reran the oracle.
- Pinned [GGUF specification](https://github.com/ggml-org/ggml/blob/da8e2a54b919557b816b1c2beb432ccb766f7ce0/docs/gguf.md), [official reader source](https://github.com/ggml-org/llama.cpp/blob/8baabd53b77d1c48c6ef8d3b620436292f3f6231/gguf-py/gguf/gguf_reader.py), and [per-slot context source](https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp) were opened; exact verbatim quotes, locations and revisions are in JSON `authorities`.

Executed provenance commands:
- JSON `commands_executed_here` records the exact five invocations, actual stdout and exit 0 for each: frozen-commit resolution; receipt SHA-256; two upstream HEAD resolutions; hashes of the two delivered source references.
- Frozen commit resolved to `37bd4c5bd456a2f8a54d3312c28495c321715856`; receipt hash was `89728a0248f208ada93ae9b2ce08a5da5e65bcd30259c43b8329d3e6d3bca863`.
- Parser reference hash: `fe3c81a567108dd7d6b8d543a1d624aa3d38ab2ab92640d6e89d59bb193c1a61`; reconciliation reference hash: `9d4696078413d055b813d47018255de5c0213fe0eb7ecc554d8b9185a7700328`.
- `mkdir -p /tmp/kama-r20-MutGgufPlan` and `rmdir /tmp/kama-r20-MutGgufPlan` each exited 0 with empty stdout; the empty isolated design scratch is removed.

Safety/limits: no lane source/VCS edits, subagent dispatch, detector/selftest execution, model download, oracle invocation, server launch or persistent process. No tools installed or updated by this seat. No build/test/lint or mutation measurements claimed. GitHub API reads returned HTTP 403; upstream revisions were instead resolved with the successful recorded `git ls-remote` calls. Report only is at the explicitly requested advice path; design data is confined to this seat's out directory.
