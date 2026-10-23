# CtlAllFalse — one assigned mutation probe

## Axes
Calibration (the frozen C1 claim); policy independence from measured observations; isolation, exact restoration and bounded evidence.

## Mutant and expected detector
At frozen commit `827d136546b85059a984b34970f5b493d9a71290`, append only to the clone's SCORECARD.md: the frozen heading `## Round 29 — self-assessment corrections`, then exactly 69 unique correction rows, one for every extracted statement. Map classes unconditionally: P → `p:absent`, H → `h:absent`, N → `n:absent`, C → `c:unresolved`, T → `t:future`, Q → `q:no-artifact`.

Expected detector: the unchanged frozen counter refuses the blanket policy (`met False`, positive unresolved), because corrections of holding statements are false corrections. No detector code, predicate, extraction rule or target was changed.

Policy commit: `3fe6136627df3aa66e0753376526a240f031e545`, retained at `refs/heads/ctl-mutant` in `/fast/scratch/hyaku/kama-r29/ctl/CtlAllFalse/repo`. Its tree is `1218b6b7084d8b82d9643c3e90332d7b3fe51c6e`. The only policy change is the appended SCORECARD.md section, saved in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlAllFalse/change.diff` (4,381 bytes).

## Exactly what the policy read
- Binding CONTEXT.md and CtlAllFalse.md, the preregistration, Godspeed skill and operator RULES.md.
- Frozen counter docstring and selected environment/repository helpers, correction parser and main/receipt handling; identifier locations found with a textual search.
- The pristine clone's SCORECARD.md append boundary/tail and git root-tree metadata needed to preserve every other entry.
- One frozen-counter `--list` run at the freeze commit, writing `/fast/scratch/hyaku/kama-r29/ctl/CtlAllFalse/all-statements.json`. The only statement fields projected/read for policy construction were `all_statements[].sid` and `all_statements[].class` (all 69). The mapping above did not depend on any measured result.
- After the policy was fixed and scored: the mutant receipt's aggregate counts, class counts, tip, counter hash and false-correction reason counts, solely for this report; and the appended byte range, solely to remove it for restoration.

Not read/used by the policy: `all_statements[].holds`, `all_statements[].observed`, per-statement mismatches/observations, source blobs at writing revisions, blame histories, or the base receipt's mismatch records. The frozen detector itself performs its prescribed repository/history checks; that is measurement infrastructure, not policy selection logic. No reference-policy rows were used.

Skips C1.claimed_work: **yes**. It neither identifies false statements nor records their measured observations; it blanket-labels every statement false. The 11 valid corrections coincide with class guesses, while the other 58 correct statements receive false correction rows.

## Actual bounded detector outputs
Every detector used `/usr/bin/timeout 300 /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py --repo /fast/scratch/hyaku/kama-r29/ctl/CtlAllFalse/repo --tip ctl --out <fresh path>`; pristine additionally used `--list` exactly once. GIT_DIR, GIT_WORK_TREE and GIT_INDEX_FILE were unset. Child file writes were capped at 1,048,575 bytes. All three returned exit 0.

Pristine (receipt with list kept in the assigned scratch directory):
```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
exit=0
```

Mutant (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlAllFalse/receipt.json`):
```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 58 unresolved 58 met False tip 3fe6136627df
exit=0
```

Restored (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlAllFalse/restored-receipt.json`):
```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 63329ad1c797
exit=0
```

Mutant receipt: 69 correction rows; 11 valid; 58 false, all reason `not-a-mismatch`; unresolved 58; **met = false**.

Control outcome: **refused**. Mutation kill verdict: **inconclusive, not killed**: the pristine claim predicate was already false (`unresolved 11`, `met False`), so this is not evidence of a passing-baseline-to-failing-mutant transition. The direct control refusal above is nevertheless the observed counter result. No contract change or additional probe was made.

## Exact restoration and hashes
Removed exactly the appended lines, including their leading blank line. Restored committed tree `efe74520595f60b69e33b79b378348fe69a31043` is the frozen tree, with restoration commit `63329ad1c797840a3eb7bfe77700462a912978e9` now at `refs/heads/ctl`. The mutant remains reachable through `ctl-mutant`. The detector was rerun after restoration and returned the pristine counts. Hash equality was checked before that rerun.

| File | Pristine SHA-256 | Mutant SHA-256 | Restored SHA-256 |
|---|---|---|---|
| SCORECARD.md | `7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db` | `7d19c12f482f6e2f8bc985fa28bd76b4178077283e6d746e1ed0230b8d77f63a` | `7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db` |
| SHONEN.md | `1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5` | `1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5` | `1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5` |
| Frozen lane counter | `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` | `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` | `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` |

## Bounded-commit deviation and failure evidence
The prescribed `git commit -qam` was attempted under the same <1 MiB file-write cap. It failed before scoring:
```text
timeout: the monitored command dumped core
exit=-25
```
The clone's pre-existing index was 1,925,930 bytes; the failed index.lock reached the 1,048,575-byte cap. That lock was removed from this clone. The parent explicitly approved bounded git plumbing instead. `hash-object`, `ls-tree`, `mktree`, `commit-tree` and `update-ref` committed the exact one-file policy without rewriting the large index; the same bounded plumbing recorded the restored original tree. These commands touched only this assigned clone, with required Git environment variables unset and each command under timeout. Full failure and successful-commit evidence are preserved in `commit-attempt.out`, `commit.out` and `restore.out` below this report's directory.

All report/receipt/log/diff artifacts are below `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlAllFalse`; the single `--list` receipt is at the item-mandated scratch path above. No tracked lane or fleet file was edited; no sibling clone was touched. No llama-server, tests, builds, alternate detector/runtime, subagents or tool installs/updates were invoked.

## Files
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlAllFalse/receipt.json`, `counter.out`, `change.diff`, `REPORT.md`, `pristine-counter.out`, `restored-receipt.json`, `restored-counter.out`, `pristine.sha256`, `mutated.sha256`, `restored.sha256`, `commit-attempt.out`, `commit.out`, `restore.out`.
