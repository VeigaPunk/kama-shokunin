VERDICT: partial - Existing selftest + population killed 5/10 mutants; five survivors expose coverage gaps, each killed by an executed CLI case.

Axes: calibration 7 (C1 detector coverage); operability 8 (exit-code contract). No official scoring or integration performed.
Revision: `a29bb84abbb8b4d328f5970a89e448330a3a42ac`; isolated clone only; one behavior-bearing mutation at a time.
Writes: scratch source and this out directory only; no lane source/index, fleet, installed serving tree, service, or model changes.
Routing: binding out-only deliverable scope takes precedence over requested `build/advice/AuditErrataMutants.md`; L1 may relocate this report.

## Executed detectors
S: `python3 /tmp/kama-r21-AuditErrataMutants-6/lane/tools/report-landing-audit.py --selftest`.
P: `python3 /tmp/kama-r21-AuditErrataMutants-6/lane/tools/report-landing-audit.py --lane-repo /tmp/kama-r21-AuditErrataMutants-6/lane --fleet-repo /home/vgpnk/Projects/shokunin --branch HEAD --json` (committed default ledger, rounds 10–20).
F: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/build/out/AuditErrataMutants/detect_errata.py --script /tmp/kama-r21-AuditErrataMutants-6/lane/tools/report-landing-audit.py --scratch /tmp/kama-r21-AuditErrataMutants-6`.
Each fixed-byte phase ran S/P/F concurrently; mutation phases never overlapped. All commands completed within their bounds.
Pristine: S exit 0, stdout `selftest cases=15 failed=0`; P exit 0, 11 reports, 9 defects, 9 corrected, 0 uncorrected/unmatched/invalid, status clean.
Pristine F: exit 0, JSON `case_count=12, failed_count=0`; checks exact matching, unmatched rows, nonexistent/blob corrections, malformed fields/round/kind, and CLI exits 0/1/2.
After EACH mutation: exact restoration, then S/P/F all exit 0 with the same pristine outcomes. Previous restored runs also supply the next mutant's pristine baseline.

## Mutants and observed output
| ID / original line | Small defect | S exit / failed cases | P exit | S+P verdict | Expected killing detector |
|---|---|---|---|---|---|
| M01 / 170 | Drop round equality | 0 / 0 | 0 | survived | F `round-must-equal` |
| M02 / 171 | Drop kind equality | 0 / 0 | 0 | survived | F `kind-must-equal` |
| M03 / 172 | Replace token equality with prefix match | 0 / 0 | 0 | survived | F `token-must-equal-not-prefix` |
| M04 / 175 | Return no unmatched rows | 1 / 1 | 0 | killed | S `unmatched-errata-fails` |
| M05 / 178 | Invert RESOLVABLE membership | 1 / 1 | 0 | killed | S `invalid-correction-fails` |
| M06 / 179 | Accept any Git object, not only commits | 0 / 0 | 0 | survived | F `blob-is-not-correction-commit` |
| M07 / 159 | Skip malformed rows instead of error | 1 / 1 | 0 | killed | S `malformed-errata-is-error` |
| M08 / 225 | Clean maps to 1 instead of 0 | 1 / 2 | 1 | killed | S `errata-clean`; P clean exit |
| M09 / 226 | Failed maps to 0 instead of 1 | 1 / 4 | 0 | killed | S `raw-fails` |
| M10 / 398 | Could-not-evaluate maps to 1 instead of 2 | 0 / 0 | 0 | survived | F malformed/missing-report CLI exits |
S stdout ends `selftest cases=15 failed=N`, with N shown above; each failed case emits `FAIL <name>`.
M08 also failed `uncommitted-draft-requires-all`; M09 also failed `unmatched-errata-fails`, `invalid-correction-fails`, `missing-section-fails`.
P counts stayed 9 defects/9 corrected/0 uncorrected/unmatched/invalid for every mutant; only M08 changed status to failed and exit to 1.
F exited 1 for every mutant (10/10 killed by the expanded detector); no inconclusive probes. Full stdout/stderr and failed-case arrays are retained.

## Executed killing cases for all five survivors
Common fixture: two real round-1 commits, report with both in Landed changes and a nonexistent 40-hex token of forty `f` characters in Work performed; valid correction is a real commit.
M01: ledger round 2, matching kind/token. Pristine/restored CLI exit 1, uncorrected=1/unmatched=1; mutant exit 0, both 0, status clean.
M02: ledger kind `landed-omitted`, round 1 and same full token. Pristine/restored exit 1, uncorrected=1/unmatched=1; mutant exit 0, both 0, status clean.
M03: ledger token `fffffff`, otherwise exact. Pristine/restored exit 1, uncorrected=1/unmatched=1; mutant exit 0, both 0, status clean.
M06: exact row whose correction is the fixture's existing `HEAD:f` blob. Pristine/restored exit 1, invalid=1; mutant exit 0, invalid=0, status clean.
M10: four-field ledger row `1\tunresolved-full-hash\tx\ty`. Pristine/restored exit 2; mutant exit 1; both stderr `could-not-evaluate: errata <temporary-path>:1: malformed row`. Missing-report CLI case also killed it.
These are coverage findings, not observed defects in the restored implementation and not permission to change its contract.

## Restoration, evidence, cleanup
Source SHA-256 before AND after every probe: `a60acc3a2444eddb34122d84f8d88cd0bcc5c6b103c90f2ca2e9ef330c28df9d`; byte-for-byte equality checked after every restoration.
Committed ledger SHA-256 before/after: `baaf4bdaf30c1ce0a08434017cc279b34aa6745450cedabb9e0c3fe144fce53d`.
`M01.json`–`M10.json` contain exact diffs, full mutated/before/restored hashes, and actual argv/exit/stdout/stderr for pristine, mutated, restored phases; `summary.json` indexes all results and phase hashes.
`pristine.json` retains initial outputs; `detect_errata.py` is the bounded runnable CLI oracle; 63 top-level detector commands were observed.
`rm -r -- /tmp/kama-r21-AuditErrataMutants-6`: exit 0, empty stdout/stderr; `test ! -e /tmp/kama-r21-AuditErrataMutants-6`: exit 0, empty stdout/stderr. Recorded in `cleanup.json`.
All subprocesses were finite, waited for, and exited; scratch and generated fixture repositories were removed. No persistent process was started.
Tool installs/updates: none. Preinstalled `python3 --version`: exit 0, `Python 3.14.8`; `git --version`: exit 0, `git version 2.56.0`.
