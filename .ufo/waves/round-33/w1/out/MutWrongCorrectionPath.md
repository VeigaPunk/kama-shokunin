# MutWrongCorrectionPath — C1 counter mutation probe

Assignment: mutation-test C1 (`tools/round33-claim-audit.py`, the KQ39
correction census) with (A) one canonical receipt path replaced by its
mislabeled legacy path and (B) one fault row duplicated. Expected: the counter
refuses each case, exits non-zero, and reports its exact count.

Execution was confined to two disposable Git clones of the lane at
`7c35289da5f4b94e062cd900eb086919e5094003` (`/tmp/mut-wcp-a`, `/tmp/mut-wcp-b`).
The lane worktree, index, and jj state were not modified; the lane was read
only via `git clone`/`git show`.

## Detector and pristine baseline

Command (same in lane and clones):

```
python3 tools/round33-claim-audit.py --repo . \
  --statement-rev dc4258bdb08d658f1c5b15abc8378461659bd155 \
  --tip 7c35289da5f4b94e062cd900eb086919e5094003
```

Pristine output, lane and both clones, exit `0`:

```
R33_CLAIM_AUDIT statement_rev=dc4258bdb08d658f1c5b15abc8378461659bd155 tip=7c35289da5f4b94e062cd900eb086919e5094003 false_at_writing=3 valid_corrections=3 unresolved=0 legacy_mislabels_at_tip=3 met=True
```

`SCORECARD.md` pristine sha256 (identical lane and both clones):
`ff84db11c91f94d88f1eaa02210f88aef90ffe906b2d65c8a2c62ae1a99ca715`
(blob `f3656416eb6cb818aaf44a47f8b4e8ef84e21c33`).

## Mutant A — canonical path replaced by mislabeled legacy path

Change: in the round-33 correction table, row `thin-row`, the canonical receipt
`.ufo/waves/round-32/c2/controls/thin-v2.out` was replaced by the stale legacy
file `.ufo/waves/round-32/c2/controls/thin-row-v2.out` (that legacy file exists
and contains base-tree output, so the failure is semantic, not missing-blob).

Mutant commit (scratch A only): `68e1894a4cd08bc8f6782ddc9e16c02698e15cbc`,
blob `47a207c9723ed9691d42de0fb85c9546fe4e6793`. Diff:

```diff
-| thin-row | `.ufo/waves/round-32/c2/controls/thin-v2.out` | `defective .ufo/waves/round-29/count-c1.py: thin-row` |
+| thin-row | `.ufo/waves/round-32/c2/controls/thin-row-v2.out` | `defective .ufo/waves/round-29/count-c1.py: thin-row` |
```

Counter at the mutant tip, exit `1`:

```
R33_CLAIM_AUDIT statement_rev=dc4258bdb08d658f1c5b15abc8378461659bd155 tip=68e1894a4cd08bc8f6782ddc9e16c02698e15cbc false_at_writing=3 valid_corrections=2 unresolved=1 legacy_mislabels_at_tip=3 met=False
```

Expected: `cited_path == correct_path` fails for `thin-row` → that fault cannot
be counted; with the other two rows valid the exact expected count is
`valid_corrections=2 unresolved=1 met=False` and a refusal exit.

Verdict: **killed** — the counter refused (exit 1) and reported exactly
`valid_corrections=2 unresolved=1`.

## Mutant B — duplicated fault row

Change: the `thin-row` correction row was duplicated verbatim (one row inserted
after the original).

Mutant commit (scratch B only): `0b03437f9af1643c84bb5efa231ca443ba204e8e`,
blob `73c175e5b2da38a7dcefdefde0c22be8c81ccab5`. Diff:

```diff
 | thin-row | `.ufo/waves/round-32/c2/controls/thin-v2.out` | `defective .ufo/waves/round-29/count-c1.py: thin-row` |
+| thin-row | `.ufo/waves/round-32/c2/controls/thin-v2.out` | `defective .ufo/waves/round-29/count-c1.py: thin-row` |
```

Counter at the mutant tip, exit `1`:

```
R33_CLAIM_AUDIT statement_rev=dc4258bdb08d658f1c5b15abc8378461659bd155 tip=0b03437f9af1643c84bb5efa231ca443ba204e8e false_at_writing=3 valid_corrections=2 unresolved=1 legacy_mislabels_at_tip=3 met=False
```

Expected: `len(entries) != 1` for `thin-row` → that fault is skipped; exact
expected count is `valid_corrections=2 unresolved=1 met=False` and a refusal
exit.

Verdict: **killed** — the counter refused (exit 1) and reported exactly
`valid_corrections=2 unresolved=1`.

## Restoration evidence

Each scratch worktree restored from the pristine commit:

```
git -C /tmp/mut-wcp-a checkout 7c35289da5f4b94e062cd900eb086919e5094003 -- SCORECARD.md
git -C /tmp/mut-wcp-b checkout 7c35289da5f4b94e062cd900eb086919e5094003 -- SCORECARD.md
```

Post-restore sha256 in both scratch trees:
`ff84db11c91f94d88f1eaa02210f88aef90ffe906b2d65c8a2c62ae1a99ca715` — byte-equal
to pristine and to the lane file. Post-restore baseline in both trees, exit `0`:

```
R33_CLAIM_AUDIT statement_rev=dc4258bdb08d658f1c5b15abc8378461659bd155 tip=7c35289da5f4b94e062cd900eb086919e5094003 false_at_writing=3 valid_corrections=3 unresolved=0 legacy_mislabels_at_tip=3 met=True
```

Lane afterward: `SCORECARD.md` sha256 still
`ff84db11c91f94d88f1eaa02210f88aef90ffe906b2d65c8a2c62ae1a99ca715`; lane
`git status` shows only the pre-existing wave-output artifacts owned by other
seats (`swarm-registry.json`, sibling report/evidence files). The mutant
commits exist only inside the `/tmp` scratch clones.

## Summary

| Case | Mutation | Expected refusal | Observed | Exit | Verdict |
|---|---|---|---|---|---|
| A | `thin-v2.out` → stale `thin-row-v2.out` in the `thin-row` row | `valid_corrections=2 unresolved=1 met=False` | exactly that | 1 | killed |
| B | `thin-row` correction row duplicated | `valid_corrections=2 unresolved=1 met=False` | exactly that | 1 | killed |

`false_at_writing=3` (statement-rev side) and `legacy_mislabels_at_tip=3` (the
three stale `*-v2.out` files still in the tree) stayed constant in both mutants,
so the reported deltas are attributable to the correction-row checks alone. No
surviving mutant and no counter/contract change; both probes target only the
report-side correction table. Raw diffs, counter outputs, and hashes are in
`MutWrongCorrectionPath-evidence/`.

No tool installs or upgrades were performed. No service, endpoint, model, or
cross-lane claim is made.
