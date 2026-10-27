# M07AlwaysAccept — round 59 mutation probe

Axes: operability (C1) and calibration (C2). This is a falsification probe, not a score/judgment or external discernment claim. No tools were installed.

## C1: always-accept checker mutant

**Attacked claim/clause:** frozen C1-r59 outcome-binding checker must accept genuine + 3/3 benign cases and reject all 16 enumerated no-op controls, with zero errors. Mutant: change the checker’s final decision from `return 0 if met else 1` to unconditional `return 0` (always accept). Only the isolated scratch copy was changed.

**Bounded detector:**
`TMPDIR=/fast/scratch/hyaku/kama-r59/M07AlwaysAccept/tmp python3 tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/M07AlwaysAccept`

- Pristine run, exit 0: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`.
- Mutant run used the same command plus `--checker /fast/scratch/hyaku/kama-r59/M07AlwaysAccept/checker.py`; exit 1: `genuine=1/1 benign=3/3 noop_rejected=0/16 errors=0 met=False`. All 16 no-op legs were accepted (each `accept exit=0`).
- Restored run used the same command plus the same `--checker` path; exit 0: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`.
- Verdict: **killed** — counter detects the always-accept defect. Checker SHA-256 before mutation: `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d`; mutant: `1afd93943681afc33cef3a3a87ed64f99faf0cb20ed336177c058d9f91314903`; restored: `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d` (byte-identical to pristine).

## C2 bounded control run

Command:
`TMPDIR=/fast/scratch/hyaku/kama-r59/M07AlwaysAccept/tmp python3 tools/round59-c2-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 --fleet-ref HEAD`

Output, exit 0: `tip=2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 fleet=0f99f606120d0c884656c6e7a290f0e8f33c2181 maxN=57 manifest=rejected-honest-stop`; `rows=44 mismatches=0 met=True` (all eight mismatch fields are 0). This is the genuine C2 control, not a C2 mutation probe. The resolved fleet HEAD observed by this invocation is `0f99f606120d0c884656c6e7a290f0e8f33c2181`, differing from the task’s stated `3f3dd97345ef1aedfdaec818c9e58675d4f41e3f`; report the actual resolution, do not claim the task-stated ref was exercised. No external S517/S518 discernment progress is claimed.

One initial C2 invocation from the fleet-root cwd failed before running the detector (`python3: can't open file '/home/vgpnk/Projects/shokunin/tools/round59-c2-counter.py'`, exit 2); rerunning from the lane cwd above succeeded. No source, commit, push, or fleet/lane tracked-file changes were made. Scratch was removed after evidence capture.