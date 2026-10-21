VERDICT: partial - 31/32 selftest cases mutation-confirmed; `uncommitted-draft-uses-now` is vacuous as named (its "now" fallback is completely unpinned), plus 3 low-severity coverage gaps; C1's 32/32 selftest claim and the detector claim itself stand.

Attack target: the 32 `--selftest` cases of `tools/report-landing-audit.py` at `a6617149722c73d90e142fbdc8154d6967055f7e` — does each assertion test what its name claims? Method: 44 surgical production-code mutations (scratch clone `/tmp/kama-r21-C1SelftestReview/lane`, mutants under `/tmp/.../mut`, never the lane checkout); each mutant ran `--selftest`; a case is "killed" when a baseline-ok case stops passing. Harness + full matrix: `.ufo/waves/round-21/falsify/out/C1SelftestReview/mutation-harness.py` and `mutation-results.json`.

Executed baseline: `python3 tools/report-landing-audit.py --selftest` in the clone at a6617149 -> 32/32 ok, exit 0, 0.172s. Matrix rerun exit 0, 1.4s. No tools installed (system python3 only).

Findings by severity

F1 MEDIUM — `uncommitted-draft-uses-now` is vacuous as to "uses-now" (case 25 of 32).
- M32 replaces the fallback `cutoff = int(time.time())` with `cutoff = 0`: 32/32 ok, exit 0.
- M33 deletes the fallback entirely (`pass`, cutoff stays None): 32/32 ok, exit 0.
- Root cause: the case audits round 2 via `--report 2=...`, and the fixture has ZERO round-2 lane round-commits, so no commit time is ever compared against the cutoff; the assertion (`rc == 0 and not report_committed`) cannot observe the cutoff value.
- What the case does pin: an uncommitted draft with an override does not raise, and `report_committed` is False. The name's "uses now" is untested; a regression to `cutoff = 0` would classify every commit of an uncommitted-draft round as post_report (required=0, omissions silently accepted) and still pass 32/32.
- Production code at a6617149 is correct (`int(time.time())`); this is a test defect, no measurement impact (official runs never used the uncommitted path).
- Repair: run the uncommitted-draft case on a round that has lane round-commits and assert a pre-"now" commit is `required`/not in `post_report` (proves cutoff ~= now, not 0/None).

F2 LOW — `inherited-GIT_DIR-untouched` (case 32) is a tripwire that cannot fire independently.
- M43 makes `git_env` keep `GIT_DIR`: exit 2, zero cases run, crash during fixture build: `could-not-evaluate: git add f in /tmp/report-landing-selftest-*/lane: rc=128 fatal: this operation must be run in a work tree`.
- So GIT_DIR stripping is load-bearing, but the leak always crashes the fixture build (first `_commit` fails) before any case prints; the final decoy-objects assertion is never the failure mode. [INFERENCE from that crash + code reading: with GIT_DIR leaked, the suite can never reach the final check with all other cases passing.]
- Harmless belt-and-braces; the case name implies its assertion is the guard, which it is not.

F3 LOW — suite coverage gaps (no case asserts these behaviors).
- Leading hex boundary `(?<![0-9A-Za-z])` of BOTH regexes is never exercised: M16 (ABBREV lookbehind dropped) and M48 (FULL lookbehind dropped) both pass 32/32. No fixture token has alnum glued before a hex run, so prose-glued citations (e.g. `xdeadbe1`) are behaviorally unpinned.
- `malformed-errata-is-error` pins only 1 of parse_errata's 3 rules: M28 (kind-enum check dropped) kills it, but M29 (field-count + round-digit checks dropped) passes 32/32.
- Result fields `cited_elsewhere` and `cutoff` (audit_round, lines 200/205) are never referenced by any selftest assertion.

F4 INFO — no action needed (verified non-defects).
- Singly-redundant guards, contract still pinned by multi-site kills: reversed-range (M36/M37 survive, M38 pair kills), irregular-report (M40/M35 survive, M44 pair kills), missing-report (M34/M35 survive, M47 pair kills), unusable-git (M41 single and M45 double survive, M49 triple kills). Genuine defense in depth.
- `empty-report-path-is-error` has real teeth: M39 (drop `not value` guard) kills it — empty string falls through the falsy `if path` in audit_round and silently audits the committed round-1 report (exit 1 verdict instead of exit 2).
- M09: the `^` in the round-subject pattern is a dead anchor (no-op) because `pat.match()` already left-anchors; prefix-ignoring (`xround-1:`) is enforced by match-vs-search semantics (M46 combo kills the author-exact case).

Per-case result (all 32; kill = executed mutation evidence)
1 raw-fails M01 | 2 mashup-detected M02 | 3 checkpoint-without-colon-omission-detected M03 | 4 bad-abbrev-detected M04 | 5 exact-defect-set M05 (+M02-04 collateral) | 6 subject-without-space-required M06 | 7 author-exact-other-round-and-prefix-ignored M07 (author) + M10 (other-round) + M46 (prefix), each aspect separately killed | 8 author-time-cutoff-survives-rebase M11 (%at->%ct) | 9 post-report-excluded M12 | 10 token-bounds M13/M14/M15, but see F3 leading-boundary gap | 11 heading-anchor M17 | 12 hex-words-not-citations M18 | 13 errata-clean M19 | 14 unmatched-errata-fails M23 | 15 unselected-round-row-ignored M24 | 16 round-must-equal M20 | 17 kind-must-equal M21 | 18 token-must-equal M22 | 19 invalid-correction-fails M25 | 20 blob-is-not-a-correction M26 (dedicated, zero collateral) | 21 omitted-correction-must-be-the-commit M27 (dedicated, zero collateral) | 22 malformed-errata-is-error M28 (partial, see F3) | 23 draft-uses-fleet-cutoff M30 | 24 missing-section-fails M31 | 25 uncommitted-draft-uses-now NO KILL (F1) | 26 missing-report-is-error M47 | 27 reversed-range-is-error M38 | 28 empty-report-path-is-error M39 | 29 irregular-report-is-error M44 | 30 unusable-git-is-error M49 | 31 open-range-finds-reports M42 | 32 inherited-GIT_DIR-untouched M43 crash-only (F2).

Residual risk
- C1's official measurement (9 defects at b76727f3) does not depend on any finding here; `exact-defect-set`, the 0-FP/FN control, is mutation-confirmed.
- If the now-fallback regressed (F1), only future uncommitted-draft audits (`--report` for rounds with no fleet report) would misclassify required commits; current committed-report audits are unaffected.

Verification gaps
- F2's "assertion cannot fire independently" is inference from the M43 crash plus code reading, not a proof by exhaustive leak simulation.
- The 44 mutations are targeted, not exhaustive (no equivalent-semantics sweep, no regex-fuzz); a case could still miss defects its claimed mutations don't model.
- Tooling record: no installs/updates performed (system python3 used; channel n/a). Scratch `/tmp/kama-r21-C1SelftestReview` deleted after this report; no lane tracked file touched; no background processes left.
