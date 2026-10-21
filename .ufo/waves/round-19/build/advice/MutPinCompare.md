VERDICT: confirm - assigned substring-comparison mutant SURVIVED both existing detectors; exact scratch bytes restored. No acceptance bypass demonstrated.

Axes: operability + calibration. This is a scoped mutation result, not an axis score or round-admission judgment.

## Mutant and detector

Only `/tmp/kama-r19-MutPinCompare/tests/llamacpp-live/check-receipt.py:388` changed: `elif tree_sha != expect_tree:` → `elif expect_tree not in tree_sha:`. Expected detectors: the gate's existing `--selftest` and the pinned `install-tree-grid.py` three-member replay. A stored v3 receipt was replayed with its recorded pins; no live serving measurement was performed.

Executed commands, cwd `/tmp/kama-r19-MutPinCompare`:

| Exact command | Exit | Receipt |
|---|---:|---|
| `python3 /tmp/kama-r19-MutPinCompare/out/probe.py pristine` | 0 | `/tmp/kama-r19-MutPinCompare/out/pristine.json` |
| `python3 /tmp/kama-r19-MutPinCompare/out/probe.py mutated` | 0 | `/tmp/kama-r19-MutPinCompare/out/mutated.json` |
| `python3 /tmp/kama-r19-MutPinCompare/out/probe.py restored` | 0 | `/tmp/kama-r19-MutPinCompare/out/restored.json` |

The same bounded child commands ran in all three phases, concurrently within each phase, with 60-second per-command limits. Exact expanded argv, exit, stdout, stderr, fixture digest and gate digest are in each receipt. All child stderr was empty; no timeout occurred.

- Selftest, every phase, exit **0**: `selftest: 6 VALID and 1 NOT-EVALUATED receipts accepted; 74 mutations + unreadable case rejected`.
- Pinned grid, every phase, exit **0**: `baseline=VALID members=3 rejected=3/3 tree_pin=on`; libggml-base, libllama-common and libllama swaps all rejected.
- Full-pin positive control, every phase, exit **0**: `VALID /tmp/kama-r19-MutPinCompare/out/receipt.json`.
- Separate prefix witness (`6c216313a88d71b1`), pristine/mutated/restored: exits **1/1/1**, `INVALID` with **2/1/2** problems. The mutant drops the comparison diagnostic, but the independent `not 64 lowercase hex chars` rejection remains.

Coverage finding: these existing detectors do not distinguish strict comparison from this substring mutant. [INFERENCE] Because receipt and expected pin each have independent 64-character lowercase-hex guards (`is_hex64`, lines 195–197; expected-pin validation, lines 445–451), substring matching is verdict-equivalent to equality for well-formed CLI pins. Do not promote this survivor into a claimed tree-pin bypass.

## Restoration and artifacts

Gate SHA-256:
- Pristine/restored: `afc9e79b2b2966b71981d3b1d19ec072b829bbb68e46168e1b8769613be56291`.
- Mutated: `db52fe42af476d4299fb023c0e8b1eca6371adac62c513a824a31f6122184733`.

`cmp /tmp/kama-r19-MutPinCompare/out/check-receipt.pristine.py /tmp/kama-r19-MutPinCompare/tests/llamacpp-live/check-receipt.py` exited **0**, stdout/stderr empty. `sha256sum /tmp/kama-r19-MutPinCompare/out/check-receipt.pristine.py /tmp/kama-r19-MutPinCompare/tests/llamacpp-live/check-receipt.py` exited **0**, printing the pristine/restored digest above for both files.

Consolidated receipt: `/tmp/kama-r19-MutPinCompare/out/receipt-probe.json`; exact mutant: `/tmp/kama-r19-MutPinCompare/out/mutation.patch`; executable replay: `/tmp/kama-r19-MutPinCompare/out/probe.py`. The gate was the only mutated scratch source. Lane source and git/jj state untouched; this requested advice report is the only lane write. No tools installed/updated; no server launched.
