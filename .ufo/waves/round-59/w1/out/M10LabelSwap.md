# M10LabelSwap — Round 59 falsification

- **Axes:** operability, calibration (assigned calibration floor 7; this probe makes no score/admission claim).
- **Attacked claim/clause:** frozen C1-r59 outcome binding; checker must associate each named run's own expected result with its own observed field/value and exit, and require the exact run-label roster.
- **Mutation:** in scratch-only `tools/round59-battery-outcome-check.py`, changed the `sys.setprofile` call-event label collection from the function's first local argument (`frame.f_locals.get(frame.f_code.co_varnames[0])`) to the `--expect` value recovered from recorded argv (`argv[argv.index("--expect") + 1]`). The mutant-assert label remained unchanged. This substitutes argv/expected-value label for the function label.
- **Detector:** same frozen C1 counter and tip for every run: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work "$TMPDIR/<stage>-work" --checker "$TMPDIR/checker-<stage>.py"`, with `TMPDIR=/fast/scratch/hyaku/kama-r59/M10LabelSwap`.

## Receipts

Pristine run: exit **0**; `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`. Each benign was accepted and all 16 no-op controls rejected (exit 1 each).

Mutant run: exit **1**; `genuine=0/1 benign=0/3 noop_rejected=16/16 errors=0 met=False`. Genuine and B1/B2/B3 all rejected (exit 1); all 16 no-op controls rejected (exit 1). The label substitution prevents intended run frames from being correctly matched to their roster entries.

Restored run: exit **0**; same summary and all per-fixture outcomes as pristine: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`.

## Verdict and restoration evidence

**KILLED.** Detector passes pristine baseline, rejects the label-swap mutant, and passes after restoration; therefore baseline did not fail and this is an observed mutation kill. Scratch hashes: pristine checker `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d`; mutated checker `2a018a8e06c4f352506682f615b5ab4669f015ffc8a89de0ae590e37d1c810f0`; restored checker `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d`, matching pristine and lane source. Temporary scratch was removed before reporting. No installs; no lane source/counter/fixture edits.