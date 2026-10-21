VERDICT: partial - exit 2 confirmed on all 14 corrupted-pin baselines; "does not count mutants" refuted: the grid still runs 3 mutant gates and prints `rejected=3/3` at lane HEAD 7229fa95.

## Scope and state
- Corrupted each non-tree pin (model, server, impl, probe, tool) on the CLI and in a copy of `.ufo/waves/round-18/live-recovery/receipt-1.json`, with the tree pin on and off, plus a malformed-pin case and a `--json` case: 14 invalid-baseline variants.
- Scratch: `/tmp/kama-r19-C2BaselineInvalid`. Lane HEAD moved to `7229fa95` (03:34:47, "round-19: citation provenance, install-tree pin...") after my first copy. I re-synced the grid and gate to the HEAD blobs and reran everything; pre-HEAD results are kept in `out/snapshot-a/` and agree.
- Only this report was written into the lane.

## Measured (receipt `out/receipt.json`; logs `out/head-runs/`, `out/patched-head-runs/`)
- All 14 invalid variants: exit 2. Each makes 4 gate calls (baseline + 3 mutants) and prints `baseline=INVALID members=3 rejected=3/3`. The real gate invoked directly, with no wrapper, gives the same result (`out/head-direct-gate/`).
- Tree pin on: the mutants also fail the tree pin, so the tally is partly real, but it comes from a baseline that failed. Tree pin off: rejections come only from the corrupted non-tree check (`model.sha256 != expected`), so `rejected=3/3` is an artifact of the corrupted pin. [pre-HEAD logs, `out/snapshot-a/`; `validate()` is unchanged at HEAD]
- Valid controls match SCORECARD: no pin gives `baseline=VALID members=3 rejected=0/3` with exit 1; with the pin, `rejected=3/3` with exit 0.
- Bad input: a missing file, non-JSON, and a missing `server` key each raise an uncaught traceback, exit 1. The docstring says 2, and exit 1 means "a mutant survived". A missing `install_tree` exits 2 with zero gate calls, the correct early exit.
- The lane's HEAD `--selftest` passes (exit 0), but asserts `rejected=1` for the invalid bad-receipt case (`install-tree-grid.py:183`), so the lane's own test encodes the defect.

## Defects (HEAD line numbers)
- `:75-76`: receipt parse sits outside any try, so bad input exits 1.
- `:91`: the mutant loop runs regardless of baseline; the invalid check comes only at `:118-119`, after all mutant gate calls.
- `:183`: the selftest expects mutant counting on an invalid baseline.

## Proposed fix (verified in scratch, not applied to the lane)
`out/install-tree-grid.proposed-head.diff` (3 hunks, sha `dac97ea8...`; patched grid sha `17163fa8...`):
1. Run mutants only when the baseline is VALID. Invalid runs then print `members=0 rejected=0/0`, make 1 gate call, and exit 2.
2. Wrap the receipt load in try/except, exiting 2 with a message.
3. Change the selftest bad-receipt expectation to status `None` and `rejected` 0. This is required with (1): the old expectation is unmet by the fixed grid (checked).
Post-fix results: 14/14 exit 2 with 1 gate call; bad input exits 2; the missing-`install_tree` case is unchanged; valid controls are unchanged (exit 1 at `0/3`, exit 0 at `3/3`); `--selftest` exits 0.

## Repro (HEAD bytes, real gate; expect exit 2 and `baseline=INVALID members=3 rejected=3/3 tree_pin=on`)
```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/install-tree-grid.py \
  --gate /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py \
  --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live-recovery/receipt-1.json \
  --model-sha 0000000000000000000000000000000000000000000000000000000000000000 \
  --server-sha b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 \
  --impl-sha e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed \
  --probe-sha 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 \
  --tool-sha 83eac5c0489377a88c8ecead89af4ca5f057bd0463d8bf8a79467eb6c5de88c4 \
  --tree-sha 6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c
```

## Gaps and [INFERENCE]
- Not run: `run.py`, the live server, `check-receipt.py --selftest`, and any official measurement.
- Changing the grid changes its digest (`49a42f81...` to `17163fa8...`). A lane grep for `49a42f81`, `467d44d8`, and `17163fa8` across tests/, tools/, .ufo/waves/round-18, registry, SCORECARD.md, and LOG.md found no hits [executed], so no pin needs refreshing [INFERENCE].
- The patch changes stdout only for invalid baselines.
- Installs or updates: none. Used `/usr/bin/python3` 3.14.8.
