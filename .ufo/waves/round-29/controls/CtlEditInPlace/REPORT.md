# CtlEditInPlace — one policy probe

Axes: detector fidelity, isolation, exact reversibility, evidence completeness.

## Mutant and expected detector

Policy: rewrite the 11 mismatching statements from the frozen base receipt in place, with no correction heading or correction rows. Only 10 existing SCORECARD.md lines changed (line 20 carries two mismatches); SHONEN.md stayed unchanged. Seven unsupported quoted-output spans were replaced by explicit notices that the quoted output was not preserved in committed evidence. Two short pointers were qualified to their existing lane paths: corpus/lessons/round-17-verifier-spotcheck.md:217–221 and .ufo/waves/round-26/count-c1.py:384. The other two absent pointers were rewritten to acknowledge the absence of the lane-local MISSION.md and report artifact at writing.

This deliberately skips C1.claimed_work: it does not append one SA29 row per false base statement under the frozen correction heading. It changes history-bearing assessment lines instead.

Expected detector: the unchanged frozen counter must reject the policy, because SCORECARD.md no longer starts with the base bytes. Its documented append-only rule then makes all 69 base statements unresolved, independently of whether the rewritten statements are true now.

Clone: /fast/scratch/hyaku/kama-r29/ctl/CtlEditInPlace/repo
Pristine/restored commit: 827d136546b85059a984b34970f5b493d9a71290
Mutant commit, retained as refs/heads/ctl: a528237e8f174baaf09af0c9938952fef60b30e8
Final HEAD: refs/heads/restored, pointing to the pristine commit. Exact original worktree bytes were restored; the mutant remains available as a committed object/ref, not as active source bytes.

## Actual bounded detector outputs

All three runs used /usr/bin/python3 and the same lane counter, with --repo pointing at this clone, under timeout 300. The pristine and mutated runs used --tip ctl at their respective commits; the restored run used --tip restored. No other behavioral detector was run.

Pristine:

    statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
    exit=0

Mutated:

    statements 69 mismatched_at_base 11 append_only False valid_corrections 0 false_corrections 0 unresolved 69 met False tip a528237e8f17
    exit=0

Restored:

    statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
    exit=0

met: false. Control outcome: rejected, matching the expected append-only rejection. Mutation kill verdict: INCONCLUSIVE, not a killed mutant, because the pristine target was already unmet (unresolved 11, met False). All detector invocations evaluated successfully; exit 0 is not a target pass.

## Reads and omissions

Read the complete binding CONTEXT.md, CtlEditInPlace item, preregistration.json (including the full predicate), godspeed skill, operator RULES.md, and eval-helper documentation. Read the frozen counter's docstring/constants/repository access and main correction/receipt/output sections; the counter was never edited. Read the base receipt's keys and all 11 mismatch records, not its complete all_statements array.

In the clone, read the relevant SCORECARD.md line ranges and tail, and captured the complete original SCORECARD.md and SHONEN.md text solely for byte-exact restoration and hashing. Read corpus/lessons/round-17-verifier-spotcheck.md:217–221 with the reader's surrounding context, and .ufo/waves/round-26/count-c1.py:380–388 with context, to choose the two qualified pointers. Listed the clone root, corpus/lessons, round-26 wave paths, and scratch .git metadata; read the root tree through git ls-tree for the index-free commit. An attempted directory read of the original round-25 report location returned not found.

Did not independently open every statement's writing-revision blob or validate the historical quoted measurement outputs, did not run the cited historical tools, and did not append the claimed correction rows. The frozen detector itself performed its normal committed-object/history reads on all three runs. No sibling source, fleet/lane tracked file, counter, or live server was modified or started; no git/jj write targeted the lane or fleet repository.

## Hashes and restoration

SHA-256 of SCORECARD.md:

- Pristine: 7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db
- Mutated: 22ea96577afed9c160c228c0ba7d037d65a13ffe7122270e13f0ebaf5f4d2984
- Restored: 7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db

SHONEN.md SHA-256 in every phase: 1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5.

Counter SHA-256 before and after: fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383, matching the frozen digest. Restoration was in a finally block and was checked by exact source hashes; the restored detector result matches the pristine result.

## Bounded-write recovery and artifacts

The clone inherited a 1,925,930-byte git index. The first ordinary commit attempt hit the 1,048,575-byte per-file RLIMIT_FSIZE (exit -25); an attempted version-4 index compaction also hit that bound. Those setup failures were not detector runs. Original worktree bytes were restored after the first failure; only the two self-created stale index.lock files were removed. To avoid rewriting the oversized index, the identical policy was committed using git hash-object, mktree, commit-tree and update-ref, preserving every other root-tree entry. This is a disclosed procedural deviation from commit -qam, not a policy change. Subsequent commands disabled core dumps as well. Commands were timeout-bounded; report/counter artifact writes are under 1 MiB. No tool was installed or updated.

Artifacts in this report's directory: receipt.json, counter.out, change.diff, pristine.receipt.json, pristine.counter.out, restored.receipt.json, restored.counter.out, restoration.json, setup-recovery.json, REPORT.md. restoration.json records phase outputs, commit identities and hashes; setup-recovery.json records the bounded-index failure and recovery.
