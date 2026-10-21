VERDICT: confirm - the pinned clean-baseline cell and stored frozen/current row agree; both arms ran and the verdict is output-derived, not exit-only.

## Findings
- No discrepancy found for `grid-clean-baseline`.

## Evidence
- Cell manifest `.ufo/waves/round-20/build/out/CensusHarness/error-injection-cells.json:7` pins mode `accept`, expected frozen/current classes `accepted`, and `known_red: false`.
- Exact stored row `.ufo/waves/round-20/runs/0957ce61/error-pair.stdout:68-77` records both classes as `accepted`, both expected classes as `accepted`, `frozen_witness_match: true`, and `frozen_ran: true` / `current_ran: true`. Header lines 2-11 show `arm: both` and `unrun: []`.
- `tools/error-verdict-census.py:164-181` parses the child stdout as JSON, requires a `VALID` baseline and a single row, extracts that row's `status`, and only then checks the corresponding exit code. `tests/llamacpp-live/install-tree-grid.py:180-185` returns exit 1 when a mutant is accepted/survives, consistent with the census's accepted→1 cross-check; exit alone does not yield this verdict.
- `tools/error-verdict-census.py:318-341` invokes frozen and current arms separately and stores their run flags; `:75-91` marks failed launches/timeouts false and returns true after child completion.
- SHA-256 check of `error-pair.stdout` produced `924d52bc8e194e5b40e63f80dc854b0c1c6ff918d93c843a267aa2a1e30db425`, matching the `error-pair` `stdout_sha256` recorded in `runs/0957ce61/commands.json`.

## Residual risk and verification gaps
- This confirms the named stored cell only; it is not an exhaustive error census. The whole matrix was not rerun, as instructed.
- No LSP device was exposed in this seat, so LSP status/references/diagnostics were unavailable; the relevant producer logic was inspected directly.