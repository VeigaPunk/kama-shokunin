# K08DoNothing — Round 56 base-control replay

**Axes:** operability (C1), calibration (C2).

Both frozen base-control targets were independently replayed at preregistered BASE `e10b6d39af450e8d652be9ac2986768b531fe13f`. Both reached their preregistered red-control outcomes; neither was green at BASE.

## C1 — operability

Extracted `tools/round54-replay-code-audit.py` from BASE into seat scratch and ran:

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round56-env-leg-test.py --counter /fast/scratch/hyaku/kama-r56/K08DoNothing/base-counter.py --expect missed
```

Observed output:

```text
ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol: la_version; ignored.
ld_audit=missed pid=1997396 problems=[]
c1_exit=0
```

The expected base-counter miss was observed with exit 0. This validates the C1 BASE control, not the full battery or the round-56 positive/mutant cases.

## C2 — calibration

Ran the frozen checker against the preregistered BASE tip:

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round56-prereg-check.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e10b6d39af450e8d652be9ac2986768b531fe13f
```

Observed output:

```text
tip=e10b6d39af450e8d652be9ac2986768b531fe13f
present=0 roster_match=0 kills=0 controls=0 met=False
c2_exit=1
```

The expected absent-files/red gate result was observed with exit 1. Thus BASE does not satisfy the roster target (`met=False`), as preregistered.

**Assessment:** No defect found in either base control. Each reaches its specified negative-control outcome at BASE. C1 shows the base counter misses `LD_AUDIT`; C2 shows the round-56 checker inputs are absent at BASE. No tool installations. Scratch was removed after replay.
