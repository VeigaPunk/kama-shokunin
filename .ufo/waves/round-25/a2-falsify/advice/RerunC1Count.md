# RerunC1Count: C1 claim value (wave 2, falsify)

Verdict: holds. The registered C1 counting command gives the claimed values at efe58e96 (registered 27, stale 2) and at 1fc41e34 (registered 28, stale 0), exit 0 at all three revisions. One residual risk concerns kill power, not the count (R1).

## What I ran
- Command: the `C1.command` string in preregistration.json, run with `bash -c` from the clone root. Saved verbatim as out/RerunC1Count/c1-command.txt.
- Environment: `PYTHONDONTWRITEBYTECODE=1` was added, so no bytecode was written. The command text is unchanged.
- Clone: `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r25a2w2/RerunC1Count/clone` (exit 0). Each revision was checked out there with `git checkout --detach`. `git status --porcelain` was empty before and after every run.
- Byte check: for each revision, the two files in the clone have the same sha256 as `git show <rev>:<path>` in the lane (six of six pairs identical).
- Host tools: Python 3.14.8 and git 2.56.0, both already present. Nothing was installed or upgraded.
- Not done: no llama-server, no port, no subagent, no mutant grid run by me, no lane write outside the out directory and this report, no git write in the lane.

## Outputs and exit codes

| Revision | Exit | stdout (verbatim) | stderr | Claimed value | Match |
|---|---|---|---|---|---|
| efe58e96e6cfbef88a0fba9d64505e18b7ad7356 | 0 | `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']` | empty | same | yes |
| 1fc41e346853afd98cbd7010af5db4e54dc877f7 | 0 | `registered 28 stale 0 []` | empty | same | yes |
| fa3b62ae6475d111eb466d79af616aeebb08bbb9 | 0 | `registered 28 stale 0 []` | empty | none stated for this revision | n/a |

Per-mutant counts (diag command, supporting only, exit 0 each):
- efe58e96: 27 ids. The M11 literal occurs 0 times, the M17 literal 2 times, and the other 25 once.
- 1fc41e34 and fa3b62ae: 28 ids. Each literal occurs exactly once and ids are unique. M33-ref-shadow-bare-objects is the new id.

Artifacts: out/RerunC1Count/c1-<rev>.stdout.txt, .stderr.txt, .exitcode.txt, .diag-per-mutant.txt.

## Differences from claimed values
None. The counts and exit codes match at both claimed revisions.

## What changed between the revisions (the two files only)
- 147f5bdd..efe58e96: no change (git diff empty). The preregistration's before value "at 147f5bdd" is therefore the same bytes. I did not run the command at 147f5bdd.
- efe58e96..1fc41e34: isolation-mutants.py +30 -3. The three removed lines are the old M11 literal, the old M17 comment, and the old M17 literal. No id line is removed. M33 is added. The auditor tools/report-landing-audit.py is unchanged (sha256 b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f at all three revisions).
- 1fc41e34..fa3b62ae: isolation-mutants.py +7 (docstring lines 33-39 at the tip). The 28 mutant entries are unchanged.

## The lane tip has moved past fa3b62ae
In the lane, master (and HEAD) = 46be41cf674301953837c8863cd2026e8a21fcb0, committed 2026-10-22 06:57:14 -03:00. fa3b62ae is an ancestor. 46be41cf adds four files: .ufo/waves/round-25/a2-falsify/advice/swarm-registry.json, .ufo/waves/round-25/a2-falsify/dispatch.json, .ufo/waves/round-25/a2-falsify/spec.json, and .ufo/waves/round-25/report-draft.md (971 insertions). Neither C1 file changed (empty diff for both paths between fa3b62ae and 46be41cf), so the count at master equals the count at fa3b62ae by identical bytes. I did not run the command at 46be41cf.

## Non-narrowing checks (element identity)
- M17 (kept): tip tools/report-landing-audit.py:275-277 is the lookup() guard `if not peel and not parts[0].startswith(token):` followed by its raise. The round-23 auditor (commit e876b95, extracted to scratch) has the same guard and the same single raise at lines 170-172, and that is the only "names a ref" raise in that file. Same element.
- M11 (kept): tip :681-683 is the fleet listing call `ls-tree ... ".ufo/reports", errors="surrogateescape"`. Round-23 :429-430 is the same call. Same element.
- M33 (new, second call site): tip :212-214, the bare_objects() raise with no peel guard. The id first appears in commit 1fc41e34 (git log -S), so there is no id reuse.
- No id is retired in round 25. The removed lines in efe58e96..1fc41e34 are anchor and comment lines only.

## Residual risk R1 (kill power, not the count)
- Committed full run at fa3b62ae, final/c1/c1-tip-mutants.json (read from the clone): pristine "passed"; 28 mutants; 26 killed; surviving ["M17-ref-shadow", "M20-log-sha-shape"]; a retired list of four ids.
- The lane's docstring (isolation-mutants.py:33-36) says M17 was killed at round 23 by grid row F13. Since round 24 that row runs through bare_objects() (M33), so M17 survives. Lines 37-39 say M17 "may be unkillable", labelled by the lane as [INFERENCE from source and a probe]. I did not re-run the grid or test reachability; that question belongs to the sibling seat KamaR25a2.MutationM17Reachability.
- Effect: the count checks that each literal occurs once. It does not check that the mutant ever fires. The C1 claim does not claim kill parity (its not_claimed list includes full isolation), so the claim value is not falsified. But "repaired instrument" overstates the state: at the tip one of the 28 registered mutants (M17) survives, and M20 also survives. M20 was not evaluated.

## R2 (scope of the count)
- The command runs no mutant and does not check that a literal sits in live code rather than in a comment. It imports only standard-library modules and resolves the auditor from its own location (isolation-mutants.py:55-56), so its output depends only on the two files above.

## Not evaluated
- Axis fit (SCORECARD round-25 section): outside this attack.
- Whether F13 killed M17 at round 23: needs the grid run.
- The command at 147f5bdd and at 46be41cf: not run (identical bytes).

## Files written
- .ufo/waves/round-25/a2-falsify/out/RerunC1Count/: c1-command.txt; c1-efe58e96.{stdout.txt, stderr.txt, exitcode.txt, diag-per-mutant.txt}; c1-1fc41e34.{same four}; c1-fa3b62ae.{same four}; diff-147f5bdd-efe58e96.patch.txt (empty); diff-efe58e96-1fc41e34.patch.txt; diff-1fc41e34-fa3b62ae.patch.txt; run-log.txt.
- .ufo/waves/round-25/a2-falsify/advice/RerunC1Count.md (this report).
- Outside the lane (scratch): /fast/scratch/hyaku/kama-r25a2w2/RerunC1Count/clone (the clone); /fast/scratch/hyaku/kama-r25a2w2/RerunC1Count/e876b95-report-landing-audit.py (git show of the round-23 auditor).

Tool records: none installed or upgraded. git 2.56.0 and Python 3.14.8 were already on the host.
