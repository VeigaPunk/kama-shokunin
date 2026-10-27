# R57Item37CounterSelftestMutation — case 58

Axes: calibration + operability. No installs; no lane-source or shared-file edits.

## Probe

Target copied to isolated scratch: `tools/capability-repertoire-audit.py`; bounded detector: `TMPDIR=/fast/scratch/hyaku/kama-r57/R57Item37CounterSelftestMutation/tmp python3 <copy> --selftest`. Expected on pristine: `CAP_SELFTEST pass=2 fail=0`, exit 0.

Mutant: in both selftest arms, replace `rc, out, err = evaluate(repo, None)` with canned literals, leaving the fixture writes and assertions unchanged:

- Arm 1 literal: `1, {"missing": 1, "met": False, "unsubstantiated": 0}, ""`
- Arm 2 literal: `1, {"missing": 0, "met": True, "unsubstantiated": 1}, ""`

Thus the selftest instrument never invokes `evaluate` and does not read the target fixture. This is one defect class (literalized instrument) applied to the two arm call sites.

## Fixtures / outputs

Fixture names from source and observed execution: temp directory prefix `cap-selftest-`; actual pristine observed directory `/fast/scratch/hyaku/kama-r57/R57Item37CounterSelftestMutation/tmp/cap-selftest-yz6l7w4x`; fixture repo `r`; `SCORECARD.md`, `tools/a.py`, and `tools/b.py`. Arm labels: `arm 1: a demonstrated capability the canonical table does not carry`; `arm 2: a name-only canonical row is unsubstantiated`. The observer wrapped calls through to originals on pristine: `EVALUATE_CALLS=2`, both with repo `<fixture-dir>/r`, rev `None`. Mutant observation: fixture directory `/fast/scratch/hyaku/kama-r57/R57Item37CounterSelftestMutation/tmp/cap-selftest-_p3fivuz`, `EVALUATE_CALLS=0`.

Actual bounded detector outputs/exits:

- Pristine: `CAP_SELFTEST pass=2 fail=0`; `exit=0`.
- Mutated: `CAP_SELFTEST pass=2 fail=0`; `exit=0`.
- Restored: `CAP_SELFTEST pass=2 fail=0`; `exit=0`.

The literalized mutant therefore survives; detector does not catch that the instrument never reads/evaluates either target fixture. This is a selftest coverage finding, not a change to the contract. The frozen no-op control independently prints `mismatches=0 maxN=46 met=True` and exits 0 (`controls/c1-noop.py`, `controls/noop-c1.out`); this probe specifically measures the selftest's fixture-to-instrument binding.

## Hashes / restoration

SHA-256 before: lane source and pristine scratch copy both `8f9c60baca48c2661ba893ae776edaeaec43a9431d8b3a40337e5ec8dc25d00e`.

Mutated scratch `counter-mutant.py`: `0fc1fcd253f9a7c8bc15fe1d089c32fd8fa2457a44ae1d0c8d499ea0e8692241`.

Restored scratch mutant path, pristine copy, and lane source all hash to `8f9c60baca48c2661ba893ae776edaeaec43a9431d8b3a40337e5ec8dc25d00e`; `diff -q counter-pristine.py counter-mutant.py` exit 0. The lane source remained byte-identical throughout. The restored detector output matches pristine.
