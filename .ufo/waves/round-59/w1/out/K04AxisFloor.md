# K04AxisFloor — round 59 claim falsification

Axes: **operability** and **calibration**. Frozen calibration floor is **7**, below operability 8 and the saturation line 8; the frozen claim explicitly says **nudge inactive**. This is a re-derivation of assigned axes/floor, not evidence of score improvement or discernment progress.

## C2 — calibration 7, closure pointer/count derivation

Attacked frozen claim/clause: C2 in `.ufo/waves/round-59/controls/freeze.txt` lines 11–15, especially the requirements that each SCORECARD calibration-row field be derived from committed lane bytes and named fleet ref, and that genuine-tip output bind exact lane tip/resolved fleet revision. The C2 predicate checks the row, typed count/pinned revision absence, pointer round/verdict, `including` round, and command presence (`tools/round59-c2-counter.py`, lines 49–71).

Committed evidence supplied by the assignment and controls:

- Exact command: `python3 tools/round59-c2-counter.py --repo <lane> --tip 2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 --fleet-ref HEAD`.
- Recorded current-HEAD result: `tip=2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 fleet=3f3dd97345ef1aedfdaec818c9e58675d4f41e3f maxN=57 manifest=rejected-honest-stop`; `rows=44 mismatches=0 met=True`; all eight mismatch counters are 0. Recorded exit: `controls/c2-after-current-head.exit` = `0`.
- Earlier recorded run at the then-named fleet ref: same lane tip, `fleet=58cffd1f42723048bcfe48eb0bc2f346caa9b77f`, `maxN=57`, verdict `rejected-honest-stop`, `rows=44 mismatches=0 met=True`; `controls/c2-after.exit` is present in the checkout but its contents were not read for this review.
- Base control: freeze base lane `8f7f58cd161f2b7dfa1709450c3ae79599c12833`, fleet base `c071f0dea9d00d944690534ff8461653eb94df66`; recorded `rows=44 mismatches=3 met=False`, with `typed_count=1 pinned_fleet_revision=1 count_command=1` and other five counters 0 (`controls/c2-base.out`). Its exit file was not read here, so no exit claim.

**Assessment:** C2's observed counter result is positive for its stated measured predicate at the supplied tip/current HEAD: output binds the exact lane tip and resolved current fleet revision, derives max spotcheck round 57 and `rejected-honest-stop`, reports zero mismatches, and base fails. It does **not** establish the frozen full calibration claim: freeze line 13 additionally requires pre-data controls changing each individual field while preserving real S517 and S518 outside admit/reject records. The task context explicitly says external S517/S518 spot-check is not recorded; do not claim discernment progress. Therefore C2 work has calibration floor 7, but this evidence is not grounds to raise it or to say the complete frozen C2 predicate is established. Current fleet evidence has no kama r58 closure row and latest committed kama closure is r57; matching maxN=57 is internally consistent, not a substitute for missing external S517/S518 records.

## Nudge

The exact assigned axes and current scores are present in SCORECARD `## Axes` (operability 8, calibration 7); its Saturation section states saturation line 8 and assigned axes operability + calibration, with calibration 7 below line and nudge inactive. The round-59 frozen clause likewise states these values. Thus **nudge inactive** follows from the lowest assigned score 7 < 8, independently of whether the C2 counter's met output is treated as sufficient for the whole frozen claim.

## Scope / verification

Read-only review. Read `/home/vgpnk/.omp/agent/RULES.md`, freeze, C2 counter source, SCORECARD, `controls/c2-after-current-head.out`, `.exit`, `controls/c2-after.out`, `controls/c2-base.out`, and wave spec. Also observed lane HEAD `4a541190b6d494a4e99116249632e99aab80adcc` and fleet HEAD `0f99f606120d0c884656c6e7a290f0e8f33c2181`; these differ from the assignment's stated measurement environment, so the recorded counter output's fleet revision is used as the measured run evidence, not represented as a fresh run. No counter command was run, no tests/builds were run, no installation occurred. No S517/S518 outside review was run or claimed.
