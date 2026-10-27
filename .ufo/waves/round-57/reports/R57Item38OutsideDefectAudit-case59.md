# R57Item38OutsideDefectAudit — distinct case 59: independent test of the assigned case

Assigned case (spec item `round57/OutsideDefectAudit/38`): re-evaluate round-56 non-author routed defects against the tree and report exact scope. This file is the independent evidence run; the scope analysis is in `OutsideDefectAudit/38/evidence.md` (Report trailer there). Axes: operability + calibration; no shared writes.

## Independence statement

- The result does not depend on the round-56 receipt `.ufo/waves/round-56/measured/c2-noop-control.out`. That receipt was read only as corroboration after my fixtures ran; the fixtures are reconstructed from committed blobs and committed in scratch repos.
- The frozen counter is identified by digest, not by trusting a file name: `git show b89bdab2:tools/round56-prereg-check.py | sha256sum` = `c7b0d787...f1489853`, equal to `.ufo/waves/round-56/preregistration.json` `claims.C2.counter_sha256`.
- Scratch root: `/fast/scratch/hyaku/kama-r57/R57Item38OutsideDefectAudit/` (created explicitly, not `/tmp`). Fixture repos: `/fast/scratch/hyaku/kama-r57/R57Item38OutsideDefectAudit/fix-noop`, `.../fix-unreachable`; `git rev-parse --show-toplevel` printed each fixture dir before the fixture commit (guard in the fixture driver, `receipts/fixtures.sh`).
- No repository writes outside that scratch tree, `OutsideDefectAudit/38/`, and this case file (`reports/R57Item38OutsideDefectAudit-case59.md`); no commits, no installs.

## Method

1. Extract bytes: old checker `b89bdab2:tools/round56-prereg-check.py`; new checker `HEAD:tools/round56-prereg-check.py`; battery `b89bdab2:tools/round56-env-leg-battery.py`; prereg `b89bdab2:.ufo/waves/round-56/preregistration.json`.
2. Build fixture A ("literal-roster no-op"): the committed battery truncated at `def main():` with `def main(): return 0` appended — the exact preregistered `ROSTER` literal, zero `run(...)`/`assert_mutant_breaks_detection(...)` calls.
3. Build fixture B ("unreachable-call no-op"): same body plus `if False:` guarded `run("base-old-counter"|"round56-counter"|"m-drop-ldaudit", ...)` calls; `main()` still returns 0 and executes nothing.
4. Commit each fixture with `git init` in its own dir after asserting the toplevel, then run both checkers with `--repo <fixture> --tip <fixture commit>`.
5. Re-derive the D1/D3/D4 tree facts with direct reads and three append-only-audit runs; re-derive the round-57 lesson's defect coverage with greps.

Fixture commits: no-op `68287493ea642504e86ee5908103b49945663669`; unreachable `addf0626a31bd6d4d5be2155c5f38e01d4c64720`.

## Results (exact output, captured in `receipts/precheck.txt`)

```
== old checker (b89bdab2) vs literal-roster no-op
tip=68287493ea642504e86ee5908103b49945663669
present=1 roster_match=1 kills=1 controls=2 met=True
exit=0

== new checker (HEAD) vs literal-roster no-op
tip=68287493ea642504e86ee5908103b49945663669
present=1 roster_match=1 kills=1 controls=2 met=False
exit=1

== new checker (HEAD) vs unreachable-call fixture
tip=addf0626a31bd6d4d5be2155c5f38e01d4c64720
present=1 roster_match=1 kills=1 controls=2 met=True
exit=0

== new checker (HEAD) vs genuine lane battery at HEAD
tip=8640e34cad02adcd247ba0862da63f6fb2aab0df
present=1 roster_match=1 kills=1 controls=2 met=True
exit=0

== old checker (b89bdab2) vs genuine lane battery at b89bdab2
tip=b89bdab2cc114735ec5d331c6c610134258f7864
present=1 roster_match=1 kills=1 controls=2 met=True
exit=0
```

Reading: the routed defect's literal no-op is killed by the current counter; the expanded no-op (same labels, dead calls) survives; the genuine battery stays accepted on both checker versions.

D1/D3/D4 and lesson coverage, re-derived (`receipts/checks.txt`):

```
MISSION.md:29  axes: "operability + freshness (local model serving/endpoints)"
shokunin.conf:52  kama|kama-shokunin|operability + calibration (local model serving and endpoint health)
SCORECARD.md:6  **Current authority (round 57):** ... MISSION.md:29 still says operability + freshness, an open L0 question since round 35
grep -c SHONEN tools/round42-selfdesc-reconcile.py  -> 0 (exit 1)
grep -c S513 corpus/QUALITY.md                      -> 0 (exit 1)
grep -c S513 corpus/lessons/round-57.md             -> 0 (exit 1)
corpus/SOURCES.md:266  S513 ... REJECTED: ... overlaps the dedicated rtld-audit(7) source S512 ...
corpus/lessons/round-57.md rows: calibration-staleness (24), no-op-counter (25)
append-only-audit at 7b74e2f2: exit 1, unrestored=2, bad_declarations=4
append-only-audit at 16efcf5e: exit 1, unrestored=6 (2 inherited + 4 in-flight), bad_declarations=4
append-only-audit at 77e7f5ee: exit 1, unrestored=6, bad_declarations=4
bad declared_at: SCORECARD.md/corpus/QUALITY.md/corpus/README.md -> corpus/README.md:761; corpus/lessons/*.md -> corpus/README.md:1239
```

## Case verdict

The assigned case reproduces: 0 of the 4 routed defects are fully addressed at checks-time tree `77e7f5ee`; D2 is partially addressed (literal no-op only) and its SCORECARD/SHONEN test is absent; D1, D3 and D4 are unchanged; the round-57 lesson carries only the D2 no-op row. Full scope, divergences (claim-label ordering, `maxN`/`46`, syntactic binding, orphaned canonical fixtures) and confidence are in `OutsideDefectAudit/38/evidence.md`.

## Limits

- HEAD moved during the runs; fixture outcomes are pinned to the commits printed above, and the audit JSON receipts carry their own `to`.
- Fixture A/B are reconstructions of the round-56 no-op shape, not the original round-56 fixture bytes (that scratch path is not in the tree); the original receipt is cited only as corroboration.
- No mutation of lane files, no scoring, no admission decision.

Report: .ufo/waves/round-57/reports/R57Item38OutsideDefectAudit-case59.md
