# CtlTypeGuess — type rule, no check

## Policy and expected detector

Axes: calibration discrimination, input isolation, exact-byte restoration.

The single mutation appends one correction section to the sandbox SCORECARD.md, containing all 35 P/Q statements extracted from the two base documents: 10 P rows with `p:absent` and 25 Q rows with `q:no-artifact`. Statement ids use the frozen extractor's filename, class, ten-character line hash, repeated-line suffix, and class-local match index. No holding/failing decision selects the rows.

Expected detector: the unchanged frozen counter should reject guessed observations and corrections naming holding statements, yielding `met: false`. The counter was run once each on pristine, mutated, and restored committed bytes, using the same repository, `--tip ctl`, a 300-second timeout, and a 1,048,575-byte per-file write limit. Only the receipt destination differs between phases. Every run exited 0.

## Inputs read and not read

Before fixing the policy, the agent read the assigned context and item, Godspeed skill, operator rules, the preregistration, the counter docstring/constants, function-location search results, and extraction code. The preregistration itself exposes aggregate baseline counts; those counts were not used by the builder. The builder read only `SCORECARD.md` and `SHONEN.md` from base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` through `git show`. It independently implemented only the P/Q extraction rules and common line-id calculation. Hash-only reads confirmed the pristine checkout's two documents exactly matched these base inputs.

Input-boundary caveat: source-navigation tools automatically displayed the `check()` declaration, its opening setup/class-dispatch/blob-lookup lines (232–235), and a closing `raise RuntimeError(cls)` footer. This incidental preview was not requested as check logic and was not used to choose rows or observations; it is disclosed rather than claiming those lines were unseen. The remaining check implementation was not opened.

No receipt was opened or consumed to construct the policy. The policy was saved before the first detector invocation. The builder did not run blame, inspect writing-revision blobs, read other document revisions, inspect evidence artifacts, or obtain any per-statement check result. The frozen scorer necessarily reads history internally when executed; its outputs were not fed back into the policy. After scoring and restoration, the reporter opened a summary projection of the mutant receipt, including its false-correction records. No further mutation was made.

## Actual outputs

Pristine:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
exit=0
```

Mutated:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 24 unresolved 24 met False tip 3802e4faac93
exit=0
```

Restored:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip f94d8e712d08
exit=0
```

Mutant receipt `met`: **false**. The 24 false-correction records each report `not-a-mismatch`.

Control verdict: **rejected**. The type rule guessed all 11 real mismatches but also asserted failures for 24 holding statements. This policy **skips the claimed work**: it does not check each false base statement at its writing revision and record the check's observed value; instead it blindly assigns class-wide failure strings.

Strict mutation-test verdict: **inconclusive**, not killed or survived, because the pristine target was already `met False`. Rejection of this control is observed directly, but a pristine-pass-to-mutant-fail claim is not supported.

## Exact-byte restoration evidence

Sandbox: `/fast/scratch/hyaku/kama-r29/ctl/CtlTypeGuess/repo`.

- Pristine commit: `827d136546b85059a984b34970f5b493d9a71290`.
- Mutation commit: `3802e4faac931fec1f79d2438a6ec1d95e3547e5`.
- Restoration commit, current sandbox `ctl`: `f94d8e712d08eda41765da5ff4a9e75148eff9c6`.
- Restoration executed in a `finally` block before the restored detector invocation. The mutant remains available as the restoration commit's parent; the saved diff describes that mutant, not the final restored tree.

| File | Pristine SHA-256 | Mutated SHA-256 | Restored SHA-256 |
| --- | --- | --- | --- |
| SCORECARD.md | `7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db` | `ae1f934ad6726847323c5e037e78245626781777dc17783fef7765115f2918d5` | `7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db` |
| SHONEN.md | `1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5` | `1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5` | `1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5` |
| Frozen lane counter | `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` | `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` | `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` |

The measured before/restored hashes match exactly. The frozen counter hash was additionally checked immediately before each detector run. Only the sandbox SCORECARD.md was mutated; no tracked lane or fleet files were edited, and all git writes used the isolated clone with Git directory/worktree/index environment variables unset. No server or additional agent runtime was started. No tools were installed or updated.

## Output files

All outputs are under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlTypeGuess/`:

- `REPORT.md`: this report.
- `policy.json`: row set and allowed-input hashes, fixed before any detector run.
- `change.diff`: mutation against the frozen commit, 2,337 bytes.
- `receipt.json`, `counter.out`: actual mutant receipt and output.
- `pristine-receipt.json`, `pristine-counter.out`: pristine run.
- `restored-receipt.json`, `restored-counter.out`: restored run.
- `evidence.json`: exact commands, exit codes, outputs, commit ids, and phase hashes.
