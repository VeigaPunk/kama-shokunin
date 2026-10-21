VERDICT: confirm - frozen reproduces six named red outcomes; the fixture-only current arm classifies all 15 cells as expected.

## Axes and boundary
- Calibration 7: bounded evidence for “errors are not verdicts”; no score increase or exhaustive-population claim.
- Operability 8 unchanged. No model, endpoint, server, or persistent process was used.
- This is the finite named regression set only, not a census of every lane counter/error path.

## Deliverables
- `build/out/CensusHarness/error-verdict-census.py` — stdlib-only, fixed grid/citation/survivor adapters; `--arm frozen|current|both`; pins the 15-cell manifest and frozen instrument digests.
- `build/out/CensusHarness/error-injection-cells.json` — exact IDs, modes, expected frozen/current classes, and known-red vector; digest `ff3b7da9c060a7f12a7ca081c79db06899a4f5c9418d26ffe4a88bc6c607f469`.
- `build/out/CensusHarness/error-injection-fixtures/` — deterministic gate, immediate timeout shim, and isolated survivor-arm fixture; fixture digests are in `build/out/CensusHarness/pins.txt`.
- `build/out/CensusHarness/selftest.txt`, `frozen-red.txt`, `current-clean.txt`, `pair.json`, `pins.txt`, and `commands.txt` retain test output, per-cell results, digests, and exact command/exit receipts.

## Fixture-only measurements
The paired run (`pair.json`) observed 15/15 cells run, frozen misclassified 6, current misclassified 0, frozen witness mismatches 0, red-vector mismatches 0; frozen/current error counts were 3/8. The six frozen red rows were the grid traceback, silent exit 1, signal, unknown exit, post-`INVALID` traceback, and survivor early-abort cells. Current early-abort is `could-not-evaluate`; the completed target-failure control remains `killed`.

`--arm frozen` returned **1** with `frozen_misclassified=6`, as required for the pinned red arm. `--arm current` returned **0** with `current_misclassified=0`. Default paired `--json` returned **0** with the exact frozen vector and clean current arm. The positive controls include a clean grid baseline, a genuine `INVALID` rejection, a valid citation, a real missing-token failure, and a complete survivor target failure. The nonexistent citation revision remains `failed`, not `error`; missing Git and unreadable documentation are `error` controls. The malformed `[1]` registry crash is intentionally omitted and is not covered by this finite denominator.

## Commands and exits
- `commands.txt` records exact executed command lines and exits: checkout 0, selftest 0, frozen arm 1, current arm 0, paired JSON 0, help 0, digest pipelines 0, scratch cleanup 0.
- No tools installed or updated. No production lane source, index, or Git state was edited; only assigned output/report files were written. LSP is not exposed by the mounted tool inventory.

## Frozen source anchors
At `37bd4c5bd456a2f8a54d3312c28495c321715856`:
- `tests/llamacpp-live/install-tree-grid.py:110-111`: `status = ("rejected" if code == 1 else "error" if code in (2, 3) else "accepted")`.
- `tests/llamacpp-live/check-receipt.py:2233-2236`: `print(f"INVALID {args.receipt}: {len(problems)} problem(s)")`.
- `tools/citation-provenance.py:238-241`: unreadable docs return 2; nonzero missing/mismatch/off-ref counts return 1.
- `.ufo/waves/round-18/c2/survivors.py:931-956`: “Only a named selftest assertion is a kill; exit 2 is inconclusive.” The frozen arm counts a target `FAIL` line without completion evidence; paired run output records early abort as `could-not-evaluate` and a complete target failure as `killed`.
