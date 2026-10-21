VERDICT: partial - 12/18 mutants survive selftest; 8/18 survive both bounded detectors.
# AuditRegexMutants — scoped mutation findings
Axes: calibration 7 (primary: honest detector coverage); operability 8 (guardrail: reproducible, isolated probes). No scoring/admission judgment.
Lane revision: `a29bb84abbb8b4d328f5970a89e448330a3a42ac`; frozen fleet revision: `7fd7c785a918131a8eb11793bca7857201e9867f`.
Only disposable scratch source was mutated; source changes were never integrated into the lane. Every mutant changes one behavior-bearing line.
Evidence: [evidence.json](evidence.json) contains exact argv, exits, complete stdout/stderr, patches, input digests, and every full before/mutated/restored SHA-256.
## Detectors and baseline
`python3 -B /tmp/kama-r21-AuditRegexMutants/lane/tools/report-landing-audit.py --selftest` → exit 0, `selftest cases=15 failed=0`.
`python3 -B /tmp/kama-r21-AuditRegexMutants/lane/tools/report-landing-audit.py --no-errata --lane-repo /tmp/kama-r21-AuditRegexMutants/lane --fleet-repo /tmp/kama-r21-AuditRegexMutants/fleet --branch a29bb84abbb8b4d328f5970a89e448330a3a42ac` → exit 1, 11 reports / 9 defects (1 unresolved full hash + 8 omitted commits).
S = selftest; P = differential population detector comparing the exact evaluated result to that frozen expected `(exit 1, nine known defects)` reference. Raw population exit 1 is expected, not itself a kill; exit-code-only population checking detects none here.
K = killed, S = survived. All evaluations completed; none inconclusive. Selftest and read-only population/witness commands ran concurrently within each phase; mutants never overlapped.
The table gives observed `exit/failed-cases` for selftest and `exit/defects` for population. Minimal witnesses are independently executed, not merely proposed.
## One-mutant-at-a-time matrix
| ID | Mutation | S exit/fail | P exit/defects | S/P verdict | Minimal witness expectation |
|---|---|---:|---:|---|---|
| M01 | FULL width {40} -> {39,40} | 0/0 | 1/9 | S/S | `FULL(H39) == []` |
| M02 | FULL width {40} -> {39} | 1/4 | 1/8 | K/K | `FULL(H40) == [H40]` |
| M03 | FULL remove left alphanumeric boundary | 0/0 | 1/16 | S/K | `FULL("g" + H40) == []` |
| M04 | FULL remove right alphanumeric boundary | 0/0 | 1/16 | S/K | `FULL(H40 + "g") == []` |
| M05 | ABBREV minimum 7 -> 8 | 0/0 | 1/13 | S/K | `ABBREV(H7) == [H7]` |
| M06 | ABBREV minimum 7 -> 6 | 0/0 | 1/9 | S/S | `ABBREV(H6) == []` |
| M07 | ABBREV maximum 40 -> 39 | 1/2 | 1/29 | K/K | `ABBREV(H40) == [H40]` |
| M08 | ABBREV remove left alphanumeric boundary | 0/0 | 1/10 | S/K | `ABBREV("g" + H7) == []` |
| M09 | ABBREV remove right alphanumeric boundary | 0/0 | 1/9 | S/S | `ABBREV(H7 + "g") == []` |
| M10 | Landed-section body lazy .*? -> greedy .* | 1/4 | 1/21 | K/K | `L("## Landed changes\nx\n## End\ny\n") == "x\n"` |
| M11 | Landed-section heading remove start-of-line anchor | 0/0 | 1/9 | S/S | `L("prefix ## Landed changes\nx\n") is None` |
| M12 | Landed-section heading remove allowed trailing text | 0/0 | 1/9 | S/S | `L("## Landed changes (commits)\nx\n") == "x\n"` |
| M13 | Round subject remove colon after round number | 1/4 | 1/9 | K/S | `round-10: other round excluded from round 1` |
| M14 | Round subject remove checkpoint alternative | 1/6 | 1/8 | K/K | `checkpoint(r1) included` |
| M15 | Round subject require space after colon | 0/0 | 1/9 | S/S | `round-1:work included (no space)` |
| M16 | Checkpoint subject require colon after closing parenthesis | 0/0 | 1/9 | S/S | `checkpoint(r1) included (no colon)` |
| M17 | Author filter remove exact lane identity test | 1/4 | 1/9 | K/S | `round-1: foreign author / someone excluded` |
| M18 | Author filter exact equality -> startswith lane identity | 0/0 | 1/9 | S/S | `round-1: author collision / kama-shokunin-extra excluded` |
Here `Hn = "f" * n`; FULL/ABBREV denote `.findall`, and L denotes `landed_section`. Round/author witnesses each use one real temp Git commit and `round_commits(..., rnd=1)`; author defaults to `kama-shokunin` except where shown.
## Coverage finding and minimal additions
Existing selftest kills M02/M07/M10/M13/M14/M17 (6/18). Population output comparison additionally catches M03/M04/M05/M08; it is not a substitute for their missing selftest assertions.
M01/M06/M09/M11/M12/M15/M16/M18 survive both; these are demonstrated coverage gaps, not permission to alter the contract. M12 preserves existing heading-suffix behavior rather than asserting a new report policy.
[witness_cases.py](witness_cases.py) implements the table’s minimal assertions. All 18 witnesses ran pristine → mutated → restored with exits 0 → 1 → 0, including every selftest survivor.
The existing `--selftest` was not extended or represented as extended; the supplemental witness executable is an advisory integration artifact only.
## Restoration, cleanup and boundaries
Initial and final source SHA-256: `a60acc3a2444eddb34122d84f8d88cd0bcc5c6b103c90f2ca2e9ef330c28df9d`; `sha256sum /tmp/kama-r21-AuditRegexMutants/lane/tools/report-landing-audit.py` exited 0 with that digest both times.
All 18 restoration phases compared byte-for-byte to the initial source, replayed selftest (exit 0 / 15 cases) and population (exit 1 / exact original nine-defect output), and passed their minimal witness (exit 0). Full mutant hashes are in `mutants.Mxx.source_sha256_before` and restoration hashes in `mutants.Mxx.restored_sha256` of evidence.json.
`rm -rf -- /tmp/kama-r21-AuditRegexMutants` → exit 0, empty stdout/stderr; subsequent existence check was false. All started commands exited; no server, model or persistent service was launched.
`python3 --version` → exit 0, `Python 3.14.8`. No tools installed or updated.
Delivery location follows the binding out-only write scope; the requested advice-directory path was not written. This report, evidence JSON and witness script are the only lane-side deliverables, all newly created under this seat’s out directory.
