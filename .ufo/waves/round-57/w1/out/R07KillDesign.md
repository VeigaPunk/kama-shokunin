# R07KillDesign — case 15 self-description counter mutation

Scope: isolated copies of `tools/round42-selfdesc-reconcile.py` and its imported `tools/round41-scorecard-reconcile.py`; no source-tree files changed. Lane checkout root was verified read-only as `/home/vgpnk/Projects/shokunin/kama-shokunin`. Detector held constant across runs: `TMPDIR=/fast/scratch/hyaku/kama-r57/R07KillDesign/tmp python3 /fast/scratch/hyaku/kama-r57/R07KillDesign/round42-selfdesc-reconcile.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip b89bdab2cc114735ec5d331c6c610134258f7864`.

## Frozen basis and baseline

The freeze amendment assigns the self-description counter to C2/calibration and specifies the stale run-count mismatch: expected 42, actual committed verifier spotcheck count 43; require `mismatches=0`. Frozen `base-c1.out` is a receipt record containing command/exit trailers, so it is not byte-identical to raw stdout; the raw three-line detector stdout exactly matches its recorded `tip`, summary, and detail. Baseline actual output is in `R07KillDesign/pristine.out`; exit 1 (`pristine.exit`). It reports `r41=1 ... mismatches=1 maxN=56 met=False`, with detail that the run produced no line equal to 42.

## Mutations and observed detector response

1. **maxN target mutation** — in scratch only, changed `maxn = max(rounds)` to `maxn = 46`. Actual output: `r41=1 banner=1 planned=1 ... mismatches=3 maxN=46 met=False`, exit 1. Exact output: `R07KillDesign/mutant-maxn.out`; exit: `mutant-maxn.exit`. The altered target is observable in output and adds banner/planned failures, but the met verdict remains false, as it was on pristine. **Killed by output comparison; not distinguished by the binary pass/fail verdict from the already-failing baseline.**

2. **canonical-row reading bypass** — in scratch only, replaced `cn, crows = canon(sc)` with `cn, crows = -1, []`. Actual output: `r41=1 retired=1 caps=1 ... mismatches=3 maxN=56 met=False`, exit 1. Exact output: `R07KillDesign/mutant-canon-bypass.out`; exit: `mutant-canon-bypass.exit`. `canon()` no longer reads the canonical rows; the mismatch counter visibly detects the missing derived capabilities, but the overall met verdict remains false as on pristine. **Killed by output comparison; not distinguished by the binary pass/fail verdict from the already-failing baseline.**

3. **Current no-op-control acceptance check** — frozen `noop-c1.out` records `mismatches=0 maxN=46 met=True`, exit 0, from `c1-noop.py`; `noop-c2.out` records `canonical_table_reads=0`, `self_description_reads=0`, the same passing summary, exit 0. Therefore these existing controls do not enforce actual canonical-row reads: a no-op is already recorded as green. This is an observed frozen-control result, not a newly mutated counter run. It is the coverage gap relevant to C2’s execution/content-binding requirement.

## Restoration

After each mutation, the changed line was restored. Final detector output equals pristine byte-for-byte (`cmp` exit 0); restored detector exit 1. `round42-selfdesc-reconcile.py` hash before/after: `9736923ec3086c6e56512cd67fa7c00a22cbb8ac63022bef45a676f2200f9ef0`. Imported `round41-scorecard-reconcile.py` hash before/after: `eff934a27b3e7525226c78e376ce774f3ab0b225ab98427b19201e5312176cd6`. Hash receipts: `R07KillDesign/pristine-hashes.txt` and `R07KillDesign/restored-hashes.txt`. Scratch artifacts were copied into the wave directory before cleanup.

No tools installed or updated.

Report: .ufo/waves/round-57/w1/out/R07KillDesign.md