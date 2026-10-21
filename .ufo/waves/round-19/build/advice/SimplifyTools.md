VERDICT: confirm — three round-19 tools simplified in scratch; both selftests exit 0.

## Axes
- **Maintainability** (LOC, duplicate branches)
- **Operability** (selftest green, CLI/json contracts unchanged)
- **Calibration** (pass/fail boundaries on registry rows, receipt pins, grid argv)

## Tools (new/changed)
| Tool | Role |
|------|------|
| `tools/citation-provenance.py` | C1 citation checker (`??` in lane) |
| `tests/llamacpp-live/check-receipt.py` | C2 sixth pin `--expect-install-tree-sha256` |
| `tests/llamacpp-live/install-tree-grid.py` | C2 install-tree swap grid (`??`) |

## Applied (scratch only: `/tmp/kama-r19-SimplifyTools`)
1. **citation-provenance.py** — merge duplicate `mismatch` branches; tighten selftest `run()` assertion; drop unused return.
2. **install-tree-grid.py** — delete `pins()` helper (inlined argv); fold member fallback into one expression.
3. **check-receipt.py** — tree pin: only emit “no digest” when `tree_sha is None` (invalid hex already via `check_digest`); pin mismatch only when `is_hex64(tree_sha)`.

## Not deleted (evidence)
- **`tree_sha()` / `install_tree_sha()` duplicate** across grid and gate: intentional producer mirrors; shared import would couple grid to gate module (LSP/grep: no shared module; grid takes `--gate PATH`).

## Selftests (executed)
```text
cd /tmp/kama-r19-SimplifyTools
python3 tools/citation-provenance.py --selftest          # exit 0
python3 tests/llamacpp-live/check-receipt.py --selftest  # exit 0
```

## Artifacts
- Diffs: `/tmp/kama-r19-SimplifyTools/out/{citation-provenance,install-tree-grid,check-receipt}.diff`
- Receipt: `/tmp/kama-r19-SimplifyTools/out/selftest-receipt.txt`

## Installs
None.
