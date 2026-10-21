VERDICT: confirm - the driver exercises five isolated citation-checker mutants and records which survive `--selftest`.

Axes: mutation sensitivity (killed vs. surviving defects) and reproducible evidence (isolated variants plus a retained JSON receipt).

Artifacts in `/tmp/kama-r19-MutationChecker/out/`:
- `mutation-driver.py` creates independent source copies, applies one exact replacement per mutant, runs each copy with `--selftest`, and writes the receipt.
- `mutation-receipt.json` retains the source digest, each exact selftest argv/cwd/exit/stdout/stderr, mutant digest, and outcome.

Executed commands and observed results:
- `cp -a /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r19-MutationChecker` — exit 0; stdout empty.
- From `/tmp/kama-r19-MutationChecker`: `python3 /tmp/kama-r19-MutationChecker/out/mutation-driver.py >/dev/null; rc=$?; printf 'driver_exit=%s\n' "$rc"; exit "$rc"` — exit 0; stdout `driver_exit=0`. The retained receipt records baseline `--selftest` exit 0, stdout `selftest: ok (5 cases)`, stderr empty.

Mutation results from the receipt:

| Mutant | Result | Selftest evidence |
|---|---|---|
| `token-min-revision-1` — lower TOKEN revision bound 7 → 1 | **survived** | exit 0, `selftest: ok (5 cases)` |
| `token-max-revision-39` — upper bound 40 → 39 | killed | exit 1; case 0 reports `found: 0`, `missing: 1` |
| `sha-comparison-disabled` — replace `observed != want` with `False` | **survived** | exit 0, `selftest: ok (5 cases)` |
| `sha-comparison-inverted` — replace `observed != want` with `observed == want` | killed | exit 1; case 0 reports `verified: 0`, `mismatch: 1` |
| `default-doc-list-empty` — replace `DEFAULT_DOCS` with an empty tuple | **survived** | exit 0, `selftest: ok (5 cases)` |

Survivors: `token-min-revision-1`, `sha-comparison-disabled`, `default-doc-list-empty`. The observed gaps are limited to this selftest: it has no short-revision rejection case; its wrong-digest fixture misses the registry token rather than exercising an existing blob with a matching token and wrong registry digest; and it invokes `check(..., [doc])` directly, bypassing the CLI default-document list. The two killed mutants confirm the suite rejects a 40-character revision pattern that stops matching and rejects an inverted digest comparison.

No tools were installed. No implementation files in the lane were changed; the only lane write is this assigned advice report. No blockers.