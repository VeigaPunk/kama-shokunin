VERDICT: confirm - the stored expectation and paired result agree; both arms ran, and this fixture’s structured unreadable count is required alongside exit status for classification.

## Evidence
- Stored cell: `.ufo/waves/round-20/build/out/CensusHarness/error-injection-cells.json:11` pins `citation-document-unreadable`, mode `document-unreadable`, expected frozen/current `error`, and `known_red: false`.
- Exact paired row: `.ufo/waves/round-20/runs/0957ce61/error-pair.stdout:111-121` reports frozen/current `error`, matching expected classes, `frozen_witness_match: true`, and `frozen_ran: true` / `current_ran: true`. No discrepancy with the pinned cell.
- Arm-specific rows corroborate execution: `error-frozen.stdout:111-121` has frozen `error` and `frozen_ran: true`; `error-current.stdout:111-121` has current `error` and `current_ran: true`.
- Not exit-alone for this fixture: `tools/error-verdict-census.py:258-284` sets `--docs` to missing `absent.md` for this mode and invokes the instrument with `--json`. Its `classify_citation` at `:184-201` parses the JSON counts and returns `error` for the unreadable case only when `docs_unreadable` is nonzero and `rc == 2`. `tools/citation-provenance.py:53-68,115-124,333-347` records unreadable documents in that JSON count and returns 2 when the count is nonzero. Thus the structured unreadable observation, not exit status alone, is necessary for this fixture’s classification.
- `commands.json:129-141` records the `error-pair` invocation of `tools/error-verdict-census.py --json` and its expected driver exit 0.
- The recorded command omits `--cells` (`commands.json:129-134`). The invoked tool’s default selection at `tools/error-verdict-census.py:377-383` falls back to `registry/error-injection-cells.json` because `tools/error-injection-cells.json` is absent; the effective registry row at `registry/error-injection-cells.json:11` matches the assigned build snapshot row 11.

## Residual risk / verification gap
- The saved paired row contains classes and run flags, not each child’s raw JSON/return code; I did not rerun the matrix, so I could not independently reparse those per-arm child outputs.
- LSP unavailable: `read xd://lsp` returned “No such tool” (mounted devices: `ast_edit`, `debug`). The behavior check above is based on direct source excerpts, not grep as semantic proof.