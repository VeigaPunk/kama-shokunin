VERDICT: confirm - Scoped INVALID-then-traceback control remains error; the intentional precedence mutant was killed.

## Scope and source evidence
- Only a private copy under `/tmp/kama-r20-MutGridInvalidTraceback` was mutated; no lane source, registry, or committed evidence was modified.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/install-tree-grid.py:82-88` checks traceback before accepting exit-1 stdout beginning `INVALID `.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/error-injection-fixtures/grid-gate.py:23-28` provides the genuine INVALID positive control and INVALID-then-RuntimeError control.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/error-injection-cells.json:8-9` expects these cells to be `rejected` and `error`, respectively.
- Grid arguments and minimal receipt match `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/error-verdict-census.py:220-239`; receipt was `{"server":{"install_tree":{"libllama.so.0.7.0":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}}}`.

## Mutant and expected detector
Replace only the scratch grid's traceback condition at original lines 82-83 with:
```python
    if (not (code == 1 and out.startswith("INVALID "))
            and ("Traceback (most recent call last):" in out
                 or "Traceback (most recent call last):" in err)):
```
This lets an INVALID prefix bypass traceback detection and reach the existing INVALID verdict branch.
The same custom scoped detector ran pristine, mutated, and restored bytes; it was not the full census or grid selftest.
Each child used `subprocess.run(..., timeout=10, check=False)` and all generated temporary files stayed under the private scratch directory.
Detector predicate: exactly one row; baseline `VALID`; gate_exit=1; target `(grid exit,status,rejected,errors)=(2,error,0,1)` plus traceback reason/signature; positive control `(0,rejected,1,0)`. Any mismatch makes detector exit 1.
Exact detector command, with cwd `/tmp/kama-r20-MutGridInvalidTraceback`, unchanged for all three stages:
`env PYTHONDONTWRITEBYTECODE=1 python3 /tmp/kama-r20-MutGridInvalidTraceback/detector.py`
Exact target child command:
`env PATH=/bin:/usr/bin LC_ALL=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/kama-r20-MutGridInvalidTraceback/tmp CENSUS_GATE_MODE=invalid-then-traceback /usr/bin/python3 /tmp/kama-r20-MutGridInvalidTraceback/install-tree-grid.py --gate /tmp/kama-r20-MutGridInvalidTraceback/grid-gate.py --receipt /tmp/kama-r20-MutGridInvalidTraceback/receipt.json --model-sha model --server-sha server --impl-sha impl --probe-sha probe --tool-sha tool --members libllama.so.0.7.0 --json`
Exact positive-control child command:
`env PATH=/bin:/usr/bin LC_ALL=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/kama-r20-MutGridInvalidTraceback/tmp CENSUS_GATE_MODE=invalid /usr/bin/python3 /tmp/kama-r20-MutGridInvalidTraceback/install-tree-grid.py --gate /tmp/kama-r20-MutGridInvalidTraceback/grid-gate.py --receipt /tmp/kama-r20-MutGridInvalidTraceback/receipt.json --model-sha model --server-sha server --impl-sha impl --probe-sha probe --tool-sha tool --members libllama.so.0.7.0 --json`

## Observed output and exits
All six grid runs reported baseline `VALID`, members=1 and gate_exit=1. These are scoped JSON output fields, not full-document equality claims.
| Bytes | Target grid exit/status/rejected/errors | Genuine INVALID positive control | Detector output/exit |
|---|---|---|---|
| Pristine | 2 / error / 0 / 1 | 0 / rejected / 1 / 0; PASS | DETECTOR=PASS / 0 |
| Mutated | 0 / rejected / 1 / 0; FAIL | 0 / rejected / 1 / 0; PASS | DETECTOR=FAIL / 1 |
| Restored | 2 / error / 0 / 1 | 0 / rejected / 1 / 0; PASS | DETECTOR=PASS / 0 |
Every row stdout was `INVALID synthetic mutant: 1 problem(s)`.
Pristine/restored target row error was `traceback in gate output (exit 1)`; grid stderr was `install-tree-grid: 1 member gate run(s) gave no verdict\n`.
Mutated target had no row error field and empty grid stderr despite retaining the traceback below. Positive controls had empty row stderr and grid stderr in all stages.
All target rows retained this exact gate-stderr string (the grid's own 200-character excerpt):
`Traceback (most recent call last):\n  File "/tmp/kama-r20-MutGridInvalidTraceback/grid-gate.py", line 28, in <module>\n    raise RuntimeError("injected failure after INVALID")\nRuntimeError: injected fai`
Mutation verdict: **killed**. Both healthy stages passed; only the deliberately misclassified target failed, while genuine rejection remained functional.

## Hashes, restoration, and cleanup
- SHA-256 pristine scratch, pristine backup, lane source before/after, and restored scratch: `d9689c0718a6001f808c00c7b5318327e0757713033e9df04994687a422650c5`.
- SHA-256 mutated scratch: `e4a932bb6f71535f4bbe95c3d401ae82b142f2afb12a2725d2fc54b1e84b5e3b`.
- SHA-256 unchanged detector before/after: `714a41d114fa389e2184f211be3b1a54e927a3dbb3dce623bacf80cfb41c3e16`.
- SHA-256 original/copied pinned gate: `0e65e584fe9d7bda52af233c7fd189555d4314b1b7ae6267b12cbf1e2d3bbb5f`.
- Restoration command: `cp /tmp/kama-r20-MutGridInvalidTraceback/install-tree-grid.pristine.py /tmp/kama-r20-MutGridInvalidTraceback/install-tree-grid.py`; subsequent `cmp` exited 0, restored detector exited 0, and hashes matched exactly.
- Cleanup command: `rm -rf -- /tmp/kama-r20-MutGridInvalidTraceback && test ! -e /tmp/kama-r20-MutGridInvalidTraceback && printf 'scratch_removed=yes\n'`; exit 0, output `scratch_removed=yes`.
- No installs, Git/JJ operations, services, model loads, delegated probes, or production changes. Result applies only to this assigned precedence mutation.
