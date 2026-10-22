# DocScorecardAuthority — checks transcript

Base: 2e254a1763a9c08aa07fc53081287f506c447d84 (detached scratch clone, --no-hardlinks)
Scratch: /fast/scratch/hyaku/kama-r24/falsify/DocScorecardAuthority
All commands read-only; no grid/mutant/selftest/parity execution; no network.

## 1. base
2e254a1763a9c08aa07fc53081287f506c447d84
(status output above: empty means clean)

## 2. digests
ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220  tools/report-landing-audit.py
b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa  tests/report-audit/promisor-grid.py
d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1  tests/report-audit/promisor-grid-expectations.json
6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2  tests/report-audit/promisor-mutants.py
1f5a469989b24b6b321b6b9a39533dad00f7e4daba80dca5f1321e888b142b0e  .ufo/waves/round-24/oracle-snapshot-before-inspection.json

## 3. SCORECARD r24 diff (0df800e..2e254a1)
 SCORECARD.md | 25 +++++++++++++++++++++++++
 1 file changed, 25 insertions(+)

## 4. parity artifact (bytes / lines) and content
144 .ufo/waves/round-23/final/nh-history-parity.stdout
10-21 current 0 frozen 0 same
10-21 --no-errata current 1 frozen 1 same
10-22 current 0 frozen 0 same
10-22 --no-errata current 1 frozen 1 same

## 5. recipe nh-history-parity ranges
RECIPE> for r in ('10-21','10-22'):

## 6. r23 grid / mutants / selftest summary
ARM current {'commands_executed': 0, 'contracts': 4, 'contracts_met': 4, 'controls': 13, 'controls_met': 13, 'faults': 26, 'faults_met': 26, 'timeouts': 0, 'tracebacks': 0, 'violations': 0}
ARM frozen {'commands_executed': 3, 'contracts': 4, 'contracts_met': 1, 'controls': 13, 'controls_met': 13, 'faults': 26, 'faults_met': 0, 'timeouts': 2, 'tracebacks': 9, 'violations': 29}
auditor_sha256 {'current': 'da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1', 'frozen': '09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f'}
frozen_revision 4fe9339f8fc3a4a4a479d9c938a850da12f1124d
population_sha256 f29fab8d9af1d02de7f6fa4c7b39b2307113d3716fd4b11cffdd0cd65d55364a
mutants 31 killed 30 surviving ['M20-log-sha-shape'] pristine passed
selftest cases=50 failed=0
rc=0

## 7. manifest vs frozen snapshot (44 unchanged + 3 added)
snapshot_cases 44 current_cases 47
added ['PG46-opaque-tree-hides-cited-blob', 'PG47-opaque-tree-with-unresolved-fabricated-token', 'PG48-opaque-unused-tree-no-unresolved-token']
changed_fields 0 []

## 8. grid summary field semantics (source lines 1028-1044)
                            if r.get("twin_equal") is False]
            withdrawn = [r["case"] for r in rows
                         if r["arm"] == "current" and r["met_original"] is False]
            baseline = [r for r in graded
                        if r["arm"] == "frozen" and r["met_amended_frozen"]]
            doc["arms"][arm] = {
                "rows": rows,
                "graded": len(graded),
                "violations": len(live_fail) + len(frozen_fail),
                "violating_cases": [r["case"] for r in live_fail + frozen_fail],
                "amended_view_met": len(baseline),
                "amended_view_total": len(graded),
                "amended_view_unmet": sorted(
                    r["case"] for r in graded
                    if r["arm"] == "frozen" and not r["met_amended_frozen"]),
                "withdrawn_original_failures": withdrawn,
                "twin_pairs_in_manifest": len(twin_links),
preliminary current arm: {'graded': 5, 'violations': 0, 'violating_cases': [], 'amended_view_met': 0, 'amended_view_total': 5, 'amended_view_unmet': [], 'withdrawn_original_failures': [], 'twin_pairs_in_manifest': 2, 'twin_compared': 0, 'twin_pairs_compared': [], 'twin_mismatch': [], 'tracebacks': 0, 'timeouts': 0, 'harness_leaks': 0}
expectations_sha256 d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1 population_size 47 auditor_sha256 {'current': 'e9790358546a974e3832c7146b822ec27ce5b6f7289b2091978344b0c4a39424'}

## 9. original view wording (never achieved)
views.original: the initial registration, derived from preregistration.json expected_after[3]. Withdrawn prospectively for the rows the amendment changes; reported separately and never counted as achieved.
amendment.original_view_verdict: The initial unknown-citation=>exit2 requirement conflicts with the original supported local-object workflow and is withdrawn prospectively, not counted as achieved.
  original  the initial registration derived from preregistration.json
            expected_after[3].  Reported; withdrawn for the rows the L1
            amendment changes; never counted as achieved.
  amended   the live policy: .ufo/waves/round-24/oracle-amendment-1.json.
            This is the graded view.

## 10. SCORECARD key lines (1167, 1200-1202, 1207-1213)
| Existing selftest / historical ledger, no harm | 50/50 → 50/50; rounds 10–22 ledger and `--no-errata` byte-identical to frozen (exit 0 / exit 1, 9 raw defects all corrected) | `python3 tools/report-landing-audit.py --selftest`; recipe line `nh-history-parity` | `.ufo/waves/round-23/final/` |
The initial registration's blanket unknown-citation expectation is
withdrawn/not-achieved, not retroactively passed. Its original view stays
in `.ufo/waves/round-24/preregistration.json` and
Integration is pinned at `ed1cc3a342bd801fe2d0f54f7ba2eb4ca42d5f05`;
the comparable quantitative record is the amended47-cell target, not the
frozen-history reproduction column. Final measurements are separate
committed-tree evidence after fresh falsification; this declaration does
not claim that those runs have occurred. No numeric promotion or new
capability. The Git>=2.45 prerequisite remains an unresolved R23-H2
operator decision, not older-Git restoration.

## 11. same parity over-statement in build advice (ConnNoHarm.md 253-255)
* **R6 — historical parity.** The r23 historical-ledger parity
  (`.ufo/waves/round-23/final/nh-history-parity.stdout`) covers rounds 10–22
  and is unaffected by the promisor policy; the r24 candidate must not change

## 12. no r24 final measurement dir yet
ls: cannot access '.ufo/waves/round-24/final': No such file or directory

## 13. source rows / lesson pointers
105
53:| stale-premise: confusing T01 with F23 | T01 clones with checkout (hydrates its single blob); F23 uses --no-checkout and asserts a real reachable blob is absent | independent outside T01 measurement; base fixture source:195–213,596–602 | retain distinct complete/incomplete oracles; never repin T01 to a refused ungraded trade by assuming all blobless clones are incomplete |
850:| Promisor local-evidence grid | gate: `python3 tests/report-audit/promisor-grid.py --arm frozen\|current\|both [--json]` | 0 selected arm observations meet their declared column; 1 mismatch/twin 
153:GIT_TIMEOUT = 20
