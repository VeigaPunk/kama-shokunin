# M05DropArgvBinding — Round 59 mutation probe

- **Axes:** operability; calibration (7, lowest assigned).
- **Attacked claim/clause:** C1 frozen control requiring each own `run`/mutant frame to contain its expected `--counter` and `--expect` argv. N16 is the decoy-counter-call fixture.
- **Mutation:** in an isolated scratch copy of `tools/round59-battery-outcome-check.py`, replaced the `calls_ok[label] = len(calls) == 1 and "--counter" in calls[0] and "--expect" in calls[0]` check with `calls_ok[label] = True`. No lane source or control was modified.

Scratch: `/fast/scratch/hyaku/kama-r59/M05DropArgvBinding` (`TMPDIR` explicitly set there).

## Detector evidence

Baseline exact command:

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/M05DropArgvBinding
```

Exit **0**; output included `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True` and `N16-decoy-counter-call reject exit=1`.

Mutated-checker command (same bounded C1 detector, explicit checker override):

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/M05DropArgvBinding --checker /fast/scratch/hyaku/kama-r59/M05DropArgvBinding/checker.py
```

Exit **1** (expected for this defect): `noop_rejected=15/16 ... met=False`; specifically `N16-decoy-counter-call accept exit=0`. Other 15 no-op controls remained rejected; genuine and all 3 benign cases were accepted.

Restored-checker command: same mutated-checker command above, after copying the pristine checker bytes back to `checker.py`. Exit **0**; output returned to `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True` and `N16-decoy-counter-call reject exit=1`.

## Verdict and restoration

**Killed** — removing the per-frame argv requirement makes the decoy fixture pass, violating the frozen C1 kill rule that every enumerated outcome-unbound control must be rejected. The pristine detector baseline passed, so this is not a baseline-inconclusive result.

Checker SHA-256 before mutation: `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d`. Restored checker SHA-256: `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d` (byte-identical restoration). Scratch cleanup performed before handoff; no installs.
