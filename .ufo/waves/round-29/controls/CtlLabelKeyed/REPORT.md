# CtlLabelKeyed — label-keyed echo control

## Policy and expected detector

Axes: policy fidelity; counter discrimination; exact-byte restoration; bounded isolation.

Only the base SCORECARD.md/SHONEN.md text selected the policy's values. Reimplemented the frozen extractor (same regular expressions, measured-cell selection, line sha256 first 10 hex, duplicate suffixes, class-local indices), omitting blame and every check. Appended the frozen heading to sandbox SCORECARD.md and exactly 69 rows: first cell SA29:<sid>, last cell the statement's original extractor token, unmodified. Counts: C=27, H=2, N=2, P=10, Q=25, T=3. The table adds 4875 bytes; SHONEN.md is unchanged. Committed policy at `9c3dd9133e2c15898a2b807fbcc3f307cf871175` on `ctl` before running any counter.

Expected detector: frozen counter refuses the echo policy (`met False`), because an echoed claim is not a check's observed value and rows also name holding statements. The pristine evaluation was expected to run successfully and retain the preregistered 11 unresolved statements. Same lane counter, same sandbox, same 300-second bound and file-size cap were used for pristine, mutated and restored committed bytes; only tip/output names changed.

## Actual outputs

Pristine (`ctl-pristine`, exit 0):

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
```

Mutated (`ctl`, exit 0):

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 69 unresolved 80 met False tip 9c3dd9133e2c
```

Restored (`ctl-restored`, exit 0):

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip b2d8fe19ef88
```

`met = False`. The control was refused: 0 valid corrections, 69 false corrections, 80 unresolved. **Mutation-kill verdict: INCONCLUSIVE**, not killed: pristine also fails the `met` predicate, so this is not a passing-baseline mutation kill. Restored output returns to the pristine counts (tip necessarily differs). No stderr in any run.

## Read scope and isolation limitation

Read the assigned item, full controls context, preregistration, godspeed skill and operator rules. Read counter docstring/imports/constants at lines 1-58; extraction constants 58-66 and 69-74; helpers/extractor 140-230. A definition-location grep also displayed its automatic adjacent context for constants and function/class declarations (git environment prologue, Repo initializer, nlines, blame prologue, helpers/extractor, corrections prologue and argument-parser prologue).

**Incidental prohibited source exposure:** that grep automatically included check() lines 232-235: signature, initial tuple assignment, P/H/N branch and blob-read assignment. This is disclosed as an information-isolation limitation; no further check body, check return/observed-value logic or failure branches were inspected, copied or used. The policy still derives every sid and value exclusively from the base documents. No pre-existing receipt was opened; the counter was not run until the policy was constructed and committed. Do not treat this as an entirely zero-exposure blind control.

The generator opened only the two base blobs, via `git show 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d:<file>`. Blob-id metadata proved frozen and base document bytes identical before the base-text insertion anchor was read. It opened no writing-revision or non-document blob and ran no blame/check. Full checker history/object reads happened only in the required post-commit scoring. New receipts were written by the detector, not used to select or amend rows. No sibling outputs or source were opened.

This policy **skips C1.claimed_work**: it neither identifies the false statements by their writing-revision checks nor records those checks' observed values. It emits one row for every statement instead. No contract, counter, claim, reference policy or lane tracked file was changed.

## Restoration and hashes

SCORECARD.md sha256:
- Before: `7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db`
- Mutated: `7d03904480dc3ff8ab47f0f6415612a3ba384d093a1551f6357828b9ca326628`
- Restored: `7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db`

SHONEN.md before/mutated/restored: `1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5`.

Lane counter before/after: `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` (matches freeze).

Exact original SCORECARD.md bytes were restored from the captured base blob (104553 bytes, same blob as frozen), then committed at `b2d8fe19ef88023661f6fc6510fa52800f3c3a84` on `ctl-restored`; sha256sum confirmed exact restoration of both affected document inputs. The mutant remains reachable on `ctl` for the recorded diff. The restored committed bytes were scored with the same bounded detector. Restoration was performed before reporting results. No serving runtime started, no additional mutation attempted, no integration or shipping performed.

All sandbox git commands had GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE unset and ran under timeout; commands used absolute repository paths. Counter children had RLIMIT_FSIZE=1048575, and saved logs/diff/manifests/report were size-checked below 1 MiB. No installs or updates.

## Files

All report artifacts are under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlLabelKeyed/`: REPORT.md, change.diff, receipt.json, counter.out, pristine.json, pristine.out, restored.json, restored.out, policy-inputs.json, hashes.json, execution.json. Sandbox: `/fast/scratch/hyaku/kama-r29/ctl/CtlLabelKeyed/repo`; currently restored branch `ctl-restored`, policy branch `ctl` retained.
