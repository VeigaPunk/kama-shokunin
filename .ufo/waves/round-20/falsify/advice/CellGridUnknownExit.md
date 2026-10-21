VERDICT: confirm - the stored grid-unknown-exit result matches its pinned expectations.

- **Stored cell:** `.ufo/waves/round-20/build/out/CensusHarness/error-injection-cells.json:6` pins `mode=unknown`, `expected_frozen_class=accepted`, `expected_current_class=error`, and `known_red=true`.
- **Exact paired row:** `.ufo/waves/round-20/runs/0957ce61/error-pair.stdout:57-65` records `frozen_class=accepted`, `current_class=error`, matching expected classes, `frozen_witness_match=true`, `frozen_ran=true`, and `current_ran=true`. Summary lines 2-10 report `arm=both` and `unrun=[]`.
- **Not exit-alone:** `.ufo/waves/round-20/build/out/CensusHarness/error-verdict-census.py:164-179` classifies from parsed stdout JSON and its row `status`; `rc` is not used to choose the class. The instrument’s unknown-exit fixture is `SystemExit(7)` (`tests/llamacpp-live/install-tree-grid.py:266-270`), and `gate_verdict` requires a matching recognized exit and verdict prefix, otherwise returning `ERROR` (`:81-93`).
- **Discrepancy:** none against the stored cell or paired row. The matrix was not rerun.

**Residual risk / verification gap:** The stored paired row contains classifications and run flags, not the raw per-arm process output. LSP was unavailable (`read xd://lsp` returned “No such tool”; mounted devices were `ast_edit` and `debug`); source behavior was checked directly, not through LSP.