# M03DropCallCount — round 59 C1 mutation

Claim/clause attacked: the frozen C1 outcome-binding checker requires each named leg to have exactly one `subprocess.run` call containing `--counter` and `--expect` (checker `calls_ok`, lines 190–191); all fixture expectations remain frozen.

Mutation: changed only the call-count predicate from `len(calls) == 1` to `bool(calls)`, retaining argument checks against the first call. The checker is the measured-tip blob of `tools/round59-battery-outcome-check.py` at `aca8d0067ea25627c5015c2193c843965148bc8e`. Original SHA-256 `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d`; mutant SHA-256 `15040f9a1d22a9a8dee181d593883a9c3bebee0bc7345630e70af673782a7d49`.

Detector: `python3 tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work <isolated scratch>`; for mutant and restored runs, additionally `--checker /fast/scratch/hyaku/kama-r59/M03DropCallCount/checker.py`. `TMPDIR` was explicitly set to the seat scratch. All three runs completed with no evaluation errors.

Pristine: exit 0; `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`. Fixtures: genuine and B1/B2/B3 accepted (exit 0); N01–N16 all rejected (exit 1).

Mutant: exit 1; `genuine=1/1 benign=3/3 noop_rejected=15/16 errors=0 met=False`. N01–N15 rejected (exit 1), but `N16-decoy-counter-call` accepted (exit 0); genuine and B1/B2/B3 accepted (exit 0). This is the specific expected detector failure: it detects the dropped exact-one-call condition because the decoy-counter negative control is accepted. Verdict: **killed**.

Restored-byte control: exit 0; `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; all fixtures returned to the pristine verdicts. Restored SHA-256 `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d`, exactly matching the before-mutation hash.

No installs. No lane source, fleet, or sibling files were modified. Isolated scratch was removed after recording results.