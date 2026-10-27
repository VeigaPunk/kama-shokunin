# R14CandidateScope — round-59 scope falsification

**Axes:** operability, calibration (assigned calibration floor 7). **Attacked claim/clause:** any interpretation of frozen C1's simulated round-56 battery outcome binding as evidence of local-serving operability, or as a measurement of serving behavior rather than lane-tool bookkeeping.

## Finding

The frozen C1 criterion is explicitly a checker property: per-leg binding of each named run's `--expect` to observed `ld_audit` and exit, 3/3 coverage, rejection of enumerated controls, and zero evaluation errors. The checker runs the committed battery under a harness; it does not start or contact a local model server. In `round59-battery-outcome-check.py`, `result_for()` infers synthetic `detected`/`missed` from a counter source's `BAD_ENV` declaration (lines 30–34), and `fake_run()` fabricates the returned `ld_audit` field and exit from the supplied `--expect` (lines 59–76). The parent then checks observed call frames and returns (lines 172–202). This can test checker/battery wiring against that synthetic model, not whether an actual serving process starts, binds a loopback port, responds to health/readiness probes, serves the configured model identity, or detects endpoint drift.

This scope boundary matches PROVINCE: kama owns local serving discovery and read-only inspection, served-model reconciliation, and `/health`, `/props`, `/slots` probe conventions (PROVINCE lines 3–15); it explicitly distinguishes pin correctness from serving liveness and records the concrete registered ports as `DEAD`/connection-refused, with restoration operator-owned (lines 19–31). The round-56 battery is specifically an `LD_AUDIT` replay-code audit harness, not a local server test (`tools/round56-env-leg-battery.py` lines 1–4, 10–18, 37–61). C1 therefore improves operability/calibration of the lane's *test harness assertion wiring* only; broadening it to a claim about local-serving operability would be a category error. Conversely, this scope challenge does not falsify the frozen, narrower C1 predicate.

C2 is also a separate lane calibration-row/repository-evidence reconciliation predicate, not a serving-runtime measurement (freeze lines 11–15); neither counter can establish a live runtime outcome. The freeze explicitly says no score increases or capability acquisition are claimed and bars claiming external S517/S518 discernment progress (lines 17 and assignment context). I make no such progress claim.

## Verdict

- **Frozen C1 as lane-tool outcome-binding:** this review found no scope basis to reject that narrow interpretation; measured counter receipts are not independently rerun here and are not treated as passed by this report.
- **Local-serving operability from C1 synthetic outcomes:** unsupported / must not be claimed. The harness fabricates outcomes and executes no serving endpoint.
- **Province-specific serving operability:** not assessed by this item; existing PROVINCE observations are bounded historical evidence, not a fresh live check.
- **Calibration implication:** keep claim language bounded to checker evidence and the frozen fields. Do not transfer a synthetic `ld_audit` receipt into a claim of service health, loaded-model identity, or endpoint reconciliation.

## Evidence and commands

Read-only file inspection: `PROVINCE.md` lines 3–15, 19–31; `.ufo/waves/round-59/controls/freeze.txt` lines 4–17; `tools/round56-env-leg-battery.py` lines 1–4, 10–18, 37–61; `tools/round59-battery-outcome-check.py` lines 30–34, 59–76, 172–202. No command executing a serving runtime or counter was run; there is no such pass to report. No tools installed or updated. No source edits or commits.