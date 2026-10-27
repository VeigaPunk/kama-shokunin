# KQ98 control receipt index — round-58 seat W03QualityCriterion

Probe: `flip-topic-overlap-check.py`, sha256 `d693ee3a54da994b810150cd28085d1e5561cbcbf868665332d053044289bb6a`, run under CPython 3.14.8, stdout only.

Inputs are scratch dumps of committed bytes (digests in `inputs.sha256`):
`SOURCES.md@dcd69473` `2363f5d4…`; `ld.so.8.html@dcd69473` `d9b7737e…`; `rtld-audit.7.html@dcd69473` `a95aa3fb…`.
Fixtures: `make-fixtures.py <SOURCES dump> <rtld-audit dump> <outdir>`; regenerated files were byte-identical (`cmp`) in all five cases.

Needle map (the round's recorded mapping, not the tool's): `{"secure-execution":["secure-execution"],"dynamic string tokens":["dynamic string token"],"loader namespace semantics":["linker namespace","loader namespace"]}`; unlocated control: `{"IFUNC resolver ordering":["IFUNC"]}`. Flip topics end at the first `;` and at `,`/` or `.

| run | input | verdict | exit |
|---|---|---|---|
| `base.out` | frozen S513 row, real copies, `--overlap-row S512` | `topics=3 supported=0 delta=3 unlocated=0 path=none met=False`, reason `blanket-overlap-rejection` | 1 |
| `control-repaired.out` | row + `claim-scoped` + `flip-delta:` listing all 3 | `path=claim-scoped met=True`, reason `delta-recorded` | 0 |
| `control-blanket.out` | row + `claim-scoped`, no `flip-delta:` | `path=none met=False`, reason `delta-not-recorded` | 1 |
| `control-partial.out` | `flip-delta:` lists 2 of 3 topics | `path=none met=False`, reason `delta-not-recorded` | 1 |
| `control-unlocated.out` | flip = `IFUNC resolver ordering`, absent from both copies | `unlocated=1 path=none met=False`, reason `unlocated:IFUNC resolver ordering` | 1 |
| `control-covered.out` | frozen row, overlap copy synthetically carries the 3 topics | `supported=1 delta=0 path=redundancy met=True` | 0 |

Per-topic hits on the frozen row (`base.out`): `secure-execution` 12 lines in `ld.so.8` (110, 246, 248, 261, 323, 349, 389, 408, 458, 468, 533, 540), 0 in `rtld-audit.7`; `dynamic string token` 5 (134, 180, 328, 358, 404), 0; `linker namespace` 1 (382), 0.

`controls.exit` holds the six exit codes; every `.out` carries the full JSON plus the one-line summary.
