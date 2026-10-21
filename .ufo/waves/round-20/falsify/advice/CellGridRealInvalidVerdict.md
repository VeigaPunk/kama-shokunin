VERDICT: partial - the stored row confirms the requested classes and both executions; source behavior at the recorded command path avoids exit-only verdicts, but its exact execution-time bytes are not pinned.

## Evidence
- Stored cell: `.ufo/waves/round-20/build/out/CensusHarness/error-injection-cells.json:8` (array index 6) selects `grid-real-invalid-verdict`, mode `invalid`, expects frozen/current `rejected`, `known_red=false`.
- Exact result: `.ufo/waves/round-20/runs/0957ce61/error-pair.stdout`, `$.results[6]` (lines 78–88): `frozen_class=rejected`, `current_class=rejected`, both expected classes are `rejected`, `frozen_witness_match=true`, `frozen_ran=true`, `current_ran=true`. Header lines 1–10 says `arm=both` and `unrun=[]`. No discrepancy in this row.
- Per-arm outputs corroborate: `error-frozen.stdout:79–80` records the frozen row/class; `error-current.stdout:79–81` records the current row/class.
- The recorded invocation is `tools/error-verdict-census.py --json` (`commands.json:129–146`); it completed with the expected exit and empty stderr hash.
- The command target’s current `classify_grid` (`tools/error-verdict-census.py:164–179`) parses the instrument JSON, obtains `rows[0].status`, and returns that status only when the process exit matches the status-specific expected exit (`rejected` → 0). It cannot classify `rejected` from an exit code alone.
- The instrument also requires a real gate verdict: `install-tree-grid.py:87–92` recognizes `INVALID` only when exit is 1 and stdout starts `INVALID `; `:152–167` maps that verdict to row status `rejected` and emits JSON. The stored fixture’s `invalid` mode prints `INVALID synthetic mutant...` and exits 1 (`error-injection-fixtures/grid-gate.py:23–25`).

## Residual risk / verification gap
- `commands.json` records the producer path and output hashes, not the producer source hash. The generated `build/out/CensusHarness/error-verdict-census.py` copy differs from `tools/error-verdict-census.py` (SHA-256 `20ae502a…` vs `f83f8a70…`); I used the recorded command target’s source for the semantic check, not the generated copy. Therefore the exact producer bytes at execution time are not independently bound by this run metadata.
- No LSP device/status API was available in this seat; semantic checks used direct reads of the relevant function bodies. The whole matrix was not rerun.