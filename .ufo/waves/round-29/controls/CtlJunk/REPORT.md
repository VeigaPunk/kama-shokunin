# CtlJunk — completed mutation probe

## Axes and policy

Axes: policy fidelity, counter rejection discrimination, byte-exact restoration.

Mutant: append only the frozen heading `## Round 29 — self-assessment corrections`, the exact table header `| id | statement | observed |`, a separator, and 11 junk rows to the sandbox SCORECARD.md. Each first cell is `SA29:SCORECARD.md:P:<10 random hex>:0`; the statement cell is `junk`; each last cell is an independently generated 24-character random hex string. Randomness came from Python `secrets.token_hex`. No statement ids or observed values were taken from an assessment receipt.

Sandbox: `/fast/scratch/hyaku/kama-r29/ctl/CtlJunk/repo`.
Frozen parent: `827d136546b85059a984b34970f5b493d9a71290`.
Scored policy: ref `ctl`, commit `394e898d132c49796c91d6320d92c6f8bdd4c0f0`.
Only SCORECARD.md was changed by the policy. The committed diff is 1,298 bytes.

## Reads and blindness

Before committing the policy, read the binding CONTEXT.md, CtlJunk.md, Godspeed skill, operator RULES.md, and preregistration.json, including its embedded baseline-count summary. Read the frozen counter docstring and the surrounding imports/constants/Git helper declarations returned by the requested lines 1–110 (including tool-added closing context). Read the sandbox SCORECARD.md append location: the displayed final lines 1429–1441 and enclosing headings. SHA-256 commands read the pristine SCORECARD.md and SHONEN.md bytes and the frozen counter bytes for digests only; SHONEN.md text was not inspected.

Did not open the base receipt `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/before/c1-base.json`, read a base mismatch list, inspect writing-revision evidence to choose corrections, use `--list`, or run the counter before the junk rows were committed and scored. Git clone/checkout necessarily read repository objects, but no observed mismatch values were extracted for the policy.

After scoring, read only the three detector outputs and filtered summaries of this probe's newly generated receipts, a sandbox `.git` directory listing and branch-state output for restoration recovery, and the restored SCORECARD.md tail. The unchanged counter itself read committed objects during its three executions. No base receipt was read at any point.

## Expected detector

Use the same frozen lane counter, each execution bounded by `timeout 300`, against the isolated sandbox. Expected healthy pristine/restored result: 69 statements, 11 base mismatches, append-only true, zero valid or false corrections, unresolved 11, met false. Expected junk result: zero valid corrections, 11 false corrections, unresolved 22, met false. An execution failure or unexpected pristine result would make the probe inconclusive rather than a killed mutant.

Execution order was mutated → pristine → restored: the item expressly prohibited a counter run before scoring the committed junk policy. Pristine evaluation used the frozen commit's committed bytes; restored evaluation used a ref to that same frozen tree after working-tree restoration. Only the tip/output arguments varied; the executable, repository and 300-second bound were unchanged.

Frozen counter SHA-256 before and after:
`fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`.

## Actual outputs

Mutated (`ctl`), exit 0:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 11 unresolved 22 met False tip 394e898d132c
```

Pristine (`827d136546b85059a984b34970f5b493d9a71290`), exit 0:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
```

Restored (`ctl-restored`), exit 0:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
```

The mutated receipt records all 11 rows as `not-a-mismatch`; `met` is JSON `false`.

Verdict: **killed / junk control rejected**. The pristine detector completed normally and matched the preregistered unchanged-tree expectation; its `met=false` is not an execution failure. The junk rows added 11 false corrections and resolved none of the 11 existing mismatches. The policy **skips C1.claimed_work**: it does not name the actual false base statements or record their observed values.

## Exact restoration and recovery

SCORECARD.md SHA-256:

- Before: `7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db`
- Mutated: `3863a86c2d39f6f7912b519f05c1f44226ed9e17b0dd3d35982dbd5ebc3a304c`
- Restored: `7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db`

SHONEN.md before/restored SHA-256:
`1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5`.

Restoration was placed in a `finally` block. The initial sandbox checkout restored the tracked file bytes but then hit the imposed 1,048,575-byte file-size cap while rewriting the clone's existing 1.8 MB Git index: exit -25, `timeout: the monitored command dumped core`. This was a restoration-command failure, not a detector failure. The byte hashes above were observed after that partial checkout. Removed only its newly created sandbox `.git/index.lock`, disabled further core dumps, and created `ctl-restored` at the frozen commit using a ref-only operation that does not rewrite the index. The restored detector then completed successfully, as shown above.

The scored `ctl` branch and its existing index remain at the mutant; HEAD remains `ctl`. The working-tree SCORECARD.md is byte-for-byte pristine, intentionally different from scored HEAD. `ctl-restored` names the pristine committed tree used for the restored detector. No claim is made that the sandbox has a clean Git working-tree status. The lane's tracked files and counter were not edited.

## Files and tooling

All report artifacts are under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlJunk/`:

- `REPORT.md`
- `receipt.json`, `counter.out`
- `pristine.receipt.json`, `pristine.out`
- `restored.receipt.json`, `restored.out`
- `change.diff`
- `evidence.json` (commands, time bounds, outputs and hashes)
- `restoration.out` (failed checkout and recovery evidence)

Artifact writes were bounded below 1 MiB; counter receipts were subject to the same OS file-size limit. All external commands were timeout-bounded. No tools were installed or updated, no server or other agent runtime was started, and no additional mutation was attempted.
