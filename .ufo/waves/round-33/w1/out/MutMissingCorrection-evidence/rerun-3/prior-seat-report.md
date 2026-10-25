# MutMissingCorrection — C1 missing-correction-row mutation probe

- Round 33, attempt 1, wave 1 (build + falsify); seat `MutMissingCorrection` (mutation-tester, leaf).
- Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`, pristine evaluated tip `7c35289da5f4b94e062cd900eb086919e5094003` (detached HEAD).
- Target claim: **C1 calibration** — KQ39 correction census for the round-32 C2 gate-control references. Predicate: `false_at_writing=3 valid_corrections=3 unresolved=0 met=True` at the evaluated tip.
- Frozen detector: `tools/round33-claim-audit.py`, blob `3f1cbe5893689620c85bad9316c9a729ea31bb3c`, sha256 `e98d8c0ca5e118bc7a82e6d5ce3d2197c24c46c984fbf9a8816b29a9a6df10c5` (identical in lane and all scratch clones).
- No tools installed or upgraded; no package-manager transaction was run.

## Method

Three isolated, disposable `git clone --no-hardlinks` copies of the lane were made under `/tmp/ufo-mut-missing-correction/{thin-row,empty-exit-map,missing-path}`. Each clone started at the same pristine detached `HEAD=7c35289d…`, with `SCORECARD.md` sha256 `ff84db11c91f94d88f1eaa02210f88aef90ffe906b2d65c8a2c62ae1a99ca715` (blob `f3656416eb6cb818aaf44a47f8b4e8ef84e21c33`).

Per clone, one mutation only: delete exactly one of the three `### Round 33 — correction of round-32 gate-control receipt references` table rows, commit the scratch tree, and run the frozen counter against the **mutant commit**:

```
python3 tools/round33-claim-audit.py --repo . \
  --statement-rev dc4258bdb08d658f1c5b15abc8378461659bd155 --tip <mutant commit>
```

The counter reads Git blobs only (`git show <rev>:<path>`), so the committed mutant blob — not the working tree — is what was evaluated. Afterwards each clone was restored with `git reset --hard 7c35289d…`, re-hashed, re-checked clean, and re-run at the pristine tip.

## Pristine baselines (before mutation, one per clone)

All three clones produced the identical line, `exit=0`:

```
R33_CLAIM_AUDIT statement_rev=dc4258bdb08d658f1c5b15abc8378461659bd155 tip=7c35289da5f4b94e062cd900eb086919e5094003 false_at_writing=3 valid_corrections=3 unresolved=0 legacy_mislabels_at_tip=3 met=True
```

## Mutants

| # | Mutation | Mutant commit | SCORECARD mutant blob | SCORECARD sha256 | Diff | Detector output | Exit | Expected | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | delete `thin-row` row | `408108480af93d3b4372052f82b4df8ad7172fc8` | `09d8df35245565f860aa10c074518043da135472` | `cd3b6f0e8166a358f3cc8487544e8712a89083bffda6fa4e4338da323ea4debd` | 1 deletion | `false_at_writing=3 valid_corrections=2 unresolved=1 legacy_mislabels_at_tip=3 met=False` | 1 | `unresolved=1 met=False` | **KILLED** |
| 2 | delete `empty-exit-map` row | `bc4de98e7ebcf861cf9be24d4392a815e8e80ca1` | `bb4a280c767ab4586e4526f14e26f795b58b2b3c` | `1295dc1b662aaa49eebfa651d46b1eb76b582d5a1ed26a7b44701a86843e6380` | 1 deletion | `false_at_writing=3 valid_corrections=2 unresolved=1 legacy_mislabels_at_tip=3 met=False` | 1 | `unresolved=1 met=False` | **KILLED** |
| 3 | delete `missing-path` row | `04e2b11e7632ffb2ef1e103639cd9c5e5d2043ec` | `a87127639f6e88d34bd6087794c50019b7f54e73` | `5e82a22c8a00e41cbf2cff7af65ed29e3d8931e613d7e3903af33759d6daa270` | 1 deletion | `false_at_writing=3 valid_corrections=2 unresolved=1 legacy_mislabels_at_tip=3 met=False` | 1 | `unresolved=1 met=False` | **KILLED** |

Verbatim mutant outputs (full line, `statement_rev` and `tip` elided only in the table above):

```
mutant 1 tip=408108480af93d3b4372052f82b4df8ad7172fc8
R33_CLAIM_AUDIT statement_rev=dc4258bdb08d658f1c5b15abc8378461659bd155 tip=408108480af93d3b4372052f82b4df8ad7172fc8 false_at_writing=3 valid_corrections=2 unresolved=1 legacy_mislabels_at_tip=3 met=False
exit=1

mutant 2 tip=bc4de98e7ebcf861cf9be24d4392a815e8e80ca1
R33_CLAIM_AUDIT statement_rev=dc4258bdb08d658f1c5b15abc8378461659bd155 tip=bc4de98e7ebcf861cf9be24d4392a815e8e80ca1 false_at_writing=3 valid_corrections=2 unresolved=1 legacy_mislabels_at_tip=3 met=False
exit=1

mutant 3 tip=04e2b11e7632ffb2ef1e103639cd9c5e5d2043ec
R33_CLAIM_AUDIT statement_rev=dc4258bdb08d658f1c5b15abc8378461659bd155 tip=04e2b11e7632ffb2ef1e103639cd9c5e5d2043ec false_at_writing=3 valid_corrections=2 unresolved=1 legacy_mislabels_at_tip=3 met=False
exit=1
```

Each mutant diff is exactly one line removed from the Round-33 correction table (`git show --stat`: `1 file changed, 1 deletion(-)`), at the historical line positions 1846, 1847 and 1848 respectively; `false_at_writing=3` and `legacy_mislabels_at_tip=3` are invariant, confirming the mutation touched only the correction mapping and not the frozen statement or the legacy evidence.

## Restoration evidence

Each clone was restored to the pristine commit and re-verified byte-exact; all three read:

```
restored_HEAD=7c35289da5f4b94e062cd900eb086919e5094003
restored_sha256=ff84db11c91f94d88f1eaa02210f88aef90ffe906b2d65c8a2c62ae1a99ca715
restored_blob=f3656416eb6cb818aaf44a47f8b4e8ef84e21c33
status_lines=0
R33_CLAIM_AUDIT statement_rev=dc4258bdb08d658f1c5b15abc8378461659bd155 tip=7c35289da5f4b94e062cd900eb086919e5094003 false_at_writing=3 valid_corrections=3 unresolved=0 legacy_mislabels_at_tip=3 met=True
exit=0
```

Restored `SCORECARD.md` sha256 equals the pre-mutation value in every clone. The scratch clones are disposable copies under `/tmp`; their Git history contains the three mutant commits listed above for reproduction.

## Lane integrity

- Lane `HEAD` after the probe: `7c35289da5f4b94e062cd900eb086919e5094003` (unchanged).
- Lane `SCORECARD.md` sha256 `ff84db11…`, blob `f3656416…` (unchanged).
- No add/commit/reset/checkout/jj mutation was executed in the lane; all Git writes were confined to the `/tmp` clones. The lane working tree still shows only the pre-existing sibling modification `.ufo/waves/round-33/w1/out/swarm-registry.json` (not mine) plus untracked sibling/report files under the wave output directory.

## Limits

- The detector is count-based: it reports `unresolved=1` but does not name which fault is missing. Killing all three mutants establishes that the census requires exactly one valid mapping per fault (row present, exact replacement path, exact defect line, receipt present with that line); it does not establish per-fault diagnostics.
- Untested mutations (out of assigned scope): row present but citation changed to the stale receipt, duplicated rows (also collapsed by `len(entries) != 1`), and removal of the legacy-mislabel disclosure text (not read by this counter).
- Evidence files: `.ufo/waves/round-33/w1/out/MutMissingCorrection-evidence/{pristine,mutant,restored}-{thin-row,empty-exit-map,missing-path}.out` plus `.meta` files carrying the mutant commit ids. Pristine and restored outputs are byte-identical (sha256 `1b1dc719e7fe4d63f93508a8eb1ad070da3323c39a99eb46b06c2c74f8adad97` each).
