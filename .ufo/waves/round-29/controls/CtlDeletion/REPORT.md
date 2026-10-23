# CtlDeletion — one deletion-policy probe

Axes: calibration sensitivity, sandbox isolation/exact-byte restoration, bounded reproducible evidence.

## Policy and expected detector

In the isolated clone `/fast/scratch/hyaku/kama-r29/ctl/CtlDeletion/repo`, delete every distinct line identified by `mismatches[].file/line` in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/before/c1-base.json`. The 11 mismatches occupy 10 SCORECARD.md lines: 20, 192, 211, 740, 823, 824, 833, 834, 1349, 1375. Line 20 carries two mismatches. No SHONEN.md lines were listed, so that file was unchanged. No heading or correction rows were appended; no other source bytes were edited.

Expected frozen detector: refuse deletion. Removing SCORECARD.md base bytes violates append-only, so `append_only` should change from True to False and all 69 base statements become unresolved; `met` remains False. The frozen counter itself was never modified.

## Actual outputs

Same command for each phase, changing only the receipt output filename:

`/usr/bin/timeout 300 /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py --repo /fast/scratch/hyaku/kama-r29/ctl/CtlDeletion/repo --tip ctl --out <absolute phase receipt path in this output directory>`

Git environment overrides were unset. Detector subprocess writes were capped with RLIMIT_FSIZE=1048575. All three runs exited 0; none timed out.

Pristine:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
exit=0
```

Mutated, committed policy:

```text
statements 69 mismatched_at_base 11 append_only False valid_corrections 0 false_corrections 0 unresolved 69 met False tip 1c2a351f8519
exit=0
```

Restored exact bytes, committed restored tree:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip f9d5889b621d
exit=0
```

`met = false` for the deletion policy. Verdict: **inconclusive as a C1-target mutation kill**, because the pristine baseline already has `met=False`; it is not counted as a killed mutant from an already-failing target. Separately, the mutation-specific append-only detector rejected the deletion as expected: True → False → True, with unresolved 11 → 69 → 11. This control did not survive as a claim-meeting policy.

## Claimed work skipped

Yes. C1.claimed_work requires appending one correctly valued correction row for each false base statement under the frozen heading, preserving the original self-assessment. This policy deletes the original false lines and appends zero rows. Reading the base receipt to locate lines does not perform the required correction work.

## Exactly what was read

- Full control CONTEXT.md and items/CtlDeletion.md; `/home/vgpnk/.omp/agent/RULES.md`; the Godspeed skill.
- Full preregistration.json, including the complete C1.predicate and C1.claimed_work; frozen count-c1.py docstring and its displayed leading source (requested lines 1–90, with the read tool's automatic surrounding/declaration context). No other counter implementation sections were manually opened.
- Base receipt projection `{base,tip,met,mismatched_at_base,unresolved,mismatches}`: all 11 mismatch records, including their line numbers, ids, tokens, observed values and writing revisions. Holding-statement records were not opened.
- Clone SCORECARD.md deletion neighborhoods using selectors 17–23, 189–195, 208–214, 737–743, 820–826, 830–836, 1346–1352, 1372–1378, plus automatic read context. Recovery reopened the mutated insertion anchors (18–20, 189–192, 207–209, 735–737, 817–819, 825–827, 1339–1341, 1364–1366), plus automatic context. Edit-tool echoes displayed the changed/restored neighborhoods.
- Selected summary fields from all three produced receipts. Directory listings of the isolated scratch parent, clone root and clone .git metadata. The root listing was inspected for a possible failed-command core artifact; none was listed.
- sha256sum read the complete bytes of SCORECARD.md and SHONEN.md for each phase, and the frozen lane counter before and after. Git clone/checkout copied the repository; Git plumbing read the frozen root tree and the edited SCORECARD.md blob. The unmodified counter performed its own committed-object/history checks in the clone.

No SHONEN.md content was manually opened. No separate artifact/source/history adjudication was done to invent or repair observations; selection relied entirely on the frozen base receipt. No sibling source, live model server, external service, alternate object store, replacement ref, judging, integration, or other mutation policy was used.

## Commit procedure and restoration

The prescribed `git commit -qam` attempt hit SIGXFSZ (exit -25): the clone's pre-existing index is 1,925,930 bytes, larger than the 1,048,575-byte subprocess file cap. The partial index.lock was exactly 1,048,575 bytes. Only that probe-created lock was removed. See `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlDeletion/setup.out` for the actual failure output.

To preserve the write cap without changing the policy, sandbox-only `git hash-object -w`, `git mktree`, `git commit-tree` and `git update-ref` committed the edited blob, replacing only the SCORECARD.md root-tree entry. The mutant is commit `1c2a351f851905f6a33a4446725f417036aba699`, preserved at `refs/heads/ctl-deletion-mutant`. The saved policy diff is 6,216 bytes.

The edit tool restored the exact captured deleted lines. The final working-tree SCORECARD.md SHA-256 equals its pristine hash, and SHONEN.md remained byte-identical throughout. A restored-tree commit, `f9d5889b621d7f88aae2708c8b72867bbe1991dc`, uses the pristine tree and is now `refs/heads/ctl`. This let the restored run use the identical `--tip ctl` detector command. Full before/mutated/restored hashes are in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlDeletion/hashes.json`.

SCORECARD.md pristine/restored: `7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db`; mutated: `91b5a9638613f6c13175e1d1700e73a1aaf64ac83019e907a56906235080e999`.

SHONEN.md all phases: `1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5`.

Counter before/after: `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` (matches the frozen expected digest).

No lane/fleet Git or jj writes occurred. Outputs are confined to this assigned control directory; clone changes are confined to the assigned scratch clone. No tools were installed or updated. Only the assigned bounded detector was run; no builds, linters, formatters, or additional tests were invoked.

## Files

All output files are under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlDeletion/`: REPORT.md, change.diff, receipt.json, counter.out, pristine-receipt.json, pristine-counter.out, restored-receipt.json, restored-counter.out, hashes.json, setup.out.
