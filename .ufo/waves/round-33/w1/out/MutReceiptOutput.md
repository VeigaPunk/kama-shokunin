# MutReceiptOutput — C2 output-to-exit correspondence (round 33, w1)

Role: mutation-tester (leaf; no subagent dispatch).
Target invariant: claim C2, that a replay receipt is counted **complete** only when its
captured defect output and its numeric `EXIT_CODE` agree with the pinned gate replay.
Detector: the claim's own counting command,

```
python3 tools/round33-gate-receipts.py audit --repo . --tip <full commit> \
  --source-rev 967d88528c1d83535563f971863f7855f76b4849 \
  --receipt-dir .ufo/waves/round-33/c2/final
```

The audit reads receipts with `git show <tip>:<path>`, so mutant bytes must be committed at
the audited tip. To avoid touching lane bytes, the probe ran in a disposable clone:

```
SCRATCH=/tmp/r33-mut-receipt-output.MjCsqz
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin $SCRATCH
# lane read-only; all commits below exist only in $SCRATCH
```

Mutated case: `empty-exit-map` (`.ufo/waves/round-33/c2/final/controls/empty-exit-map-r33.out`),
chosen because it is a control whose named defect line is exactly one whole stdout line.
`empty-exit-map` is expected to exit 1 and to print
`defective .ufo/waves/round-33/count-fixture.py: empty-exit-map`.

## Baseline — pristine bytes (conclusive baseline)

| run | tip | detector output | exit |
|---|---|---|---|
| lane (read-only, claimed counting command) | `7c35289da5f4b94e062cd900eb086919e5094003` | `R33_GATE_RECEIPT_AUDIT source_rev=967d88528c1d83535563f971863f7855f76b4849 tip=7c35289da5f4b94e062cd900eb086919e5094003 complete=4/4 missing=0 invalid=0 met=True` | 0 |
| scratch clone, pristine | `7c35289da5f4b94e062cd900eb086919e5094003` | identical (complete=4/4 missing=0 invalid=0 met=True) | 0 |

Pristine receipt hashes (lane `HEAD` blob == worktree == clone):

```
d2f8f48d31470bc6ce0b86f82be432f2203a7a8006750331a93f3c0b4838ac0b  gate-tip-r33.out
fc4c4490efd50a38d0e40d6c8e826341e787017df94387142daaf9e1a42682cd  controls/thin-row-r33.out
ccfb4bb49ad069d1cb5a7ae133d32a318b9c0c7359b4a95457a7f7e6ecfbe553  controls/empty-exit-map-r33.out
23b48c21f093bdefc8a72b3eca507cca167885b0659b9e9fb6dd17ff705fb1ea  controls/missing-path-r33.out
```

Baseline passes, so both mutants below are conclusive, not baseline failures.

## Mutant A — defect line removed, `EXIT_CODE=1` kept

Commit (scratch only): `15e3ffe1207b2fc2982254aec989fe24ac612a2a`.

Exact byte change vs pristine (one deleted line, nothing else; `EXIT_CODE=1` untouched):

```diff
@@ -9,7 +9,6 @@ GATE_SHA256=e07cf8d753560cd34b5945c89f4dc3f19122ca87d19f8e85844e3b1ae4e0506b
 EXIT_CODE=1
 STDOUT_BEGIN
-defective .ufo/waves/round-33/count-fixture.py: empty-exit-map
 registered 1 unregistered 0 defective 1
```

Receipt hash: `ccfb4bb49ad069d1cb5a7ae133d32a318b9c0c7359b4a95457a7f7e6ecfbe553`
→ `4abc754da176e5a9eb6630c80efda6a9ad4bbc3dd51b948915be85c5584bfec7`.

Expected detector: receipt must **not** count complete (either as invalid or missing), overall
`met=False`, exit 1.

Actual detector output:

```
R33_GATE_RECEIPT_AUDIT source_rev=967d88528c1d83535563f971863f7855f76b4849 tip=15e3ffe1207b2fc2982254aec989fe24ac612a2a complete=3/4 missing=0 invalid=1 met=False
EXIT=1
```

Predicate isolation (`output_ok` called directly on the mutant text with the pinned case
expectations): `parse_receipt` succeeds (not a malformed-receipt rejection),
`defect_line_present=False`, `stdout_exact=False`, `output_ok=False`.

**Verdict: KILLED** — not counted complete (complete=3/4, invalid=1, met=False, exit 1).

## Mutant B — defect line kept, `EXIT_CODE=0`

Commit (scratch only): `d81c3d272a75292e38e6fefb97ad0f0f73d782a1`.

Exact byte change vs pristine (one line substitution; defect line present):

```diff
@@ -7,7 +7,7 @@ EVALUATED_REV=58f49f42348c74af41a31dc06697f4edf4292c8d
 RUNNER_SHA256=309543621a90f3c50bf130e06bc4e26a95e40202d84e81f769fca826a9e1dc04
-EXIT_CODE=1
+EXIT_CODE=0
 STDOUT_BEGIN
 defective .ufo/waves/round-33/count-fixture.py: empty-exit-map
```

Receipt hash: `ccfb4bb49ad069d1cb5a7ae133d32a318b9c0c7359b4a95457a7f7e6ecfbe553`
→ `72dd647aa73209f68ac8fd32db5a17bb5f0f1239abb5dfb99b79b3221233384a`.

Expected detector: receipt must **not** count complete; overall `met=False`, exit 1.

Actual detector output:

```
R33_GATE_RECEIPT_AUDIT source_rev=967d88528c1d83535563f971863f7855f76b4849 tip=d81c3d272a75292e38e6fefb97ad0f0f73d782a1 complete=3/4 missing=0 invalid=1 met=False
EXIT=1
```

Predicate isolation: `parse_receipt` succeeds; `defect_line_present=True`;
`stdout_exact=True`; `output_ok=False`. Because the defect line and the whole stdout are
byte-exact, the only failing correspondence is `EXIT_CODE` (`0` vs the replayed `1`) — the
output−exit disagreement is caught on its own, not merely as a byte diff against the oracle.
The audit also compares `EXIT_CODE` among its `stable_fields`, so two independent predicates
reject this direction.

**Verdict: KILLED** — not counted complete (complete=3/4, invalid=1, met=False, exit 1).

## Restoration

Restore commit (scratch only): `c722942e7da089ff6586377674bb2c120869ce3c`
(`git checkout 7c35289da5f4b94e062cd900eb086919e5094003 -- <receipt>`, then commit).

```
git diff --stat 7c35289da5f4b94e062cd900eb086919e5094003 c722942e7da089ff6586377674bb2c120869ce3c
# (empty output; exit 0)

sha256sum controls/empty-exit-map-r33.out
ccfb4bb49ad069d1cb5a7ae133d32a318b9c0c7359b4a95457a7f7e6ecfbe553   # == pristine

python3 tools/round33-gate-receipts.py audit --repo . --tip c722942e7da089ff6586377674bb2c120869ce3c \
  --source-rev 967d88528c1d83535563f971863f7855f76b4849 --receipt-dir .ufo/waves/round-33/c2/final
R33_GATE_RECEIPT_AUDIT source_rev=967d88528c1d83535563f971863f7855f76b4849 tip=c722942e7da089ff6586377674bb2c120869ce3c complete=4/4 missing=0 invalid=0 met=True
EXIT=0
```

All four receipts in the restore commit hash identically to the pristine `7c35289` blobs
(listed under Baseline). The disposable clone is clean (`git status --porcelain` empty).

Lane integrity after the probe: lane `HEAD` still `7c35289da5f4b94e062cd900eb086919e5094003`;
the four `c2/final` blob hashes at lane `HEAD` equal the pristine hashes above; the only lane
worktree changes are peer-owned files (`swarm-registry.json` modified, peer evidence dirs
untracked). No lane Git index, jj state, branch or remote was touched; no lane commit/add/
checkout was run. Sibling scratch dirs (e.g. `/tmp/c2mut`) were not read into or modified.

## Summary

| probe | mutant bytes | expected | actual | verdict |
|---|---|---|---|---|
| baseline | pristine | complete=4/4, met=True, exit 0 | complete=4/4, met=True, exit 0 | pass (control) |
| A | defect line deleted, `EXIT_CODE=1` | not complete, met=False, exit 1 | complete=3/4, invalid=1, met=False, exit 1 | **KILLED** |
| B | defect line kept, `EXIT_CODE=0` | not complete, met=False, exit 1 | complete=3/4, invalid=1, met=False, exit 1 | **KILLED** |
| restore | pristine bytes | complete=4/4, met=True, exit 0 | complete=4/4, met=True, exit 0 | pass |

No surviving mutant in the assigned probe: C2's audit enforces both directions of the
output-to-exit correspondence for the `empty-exit-map` control. This is a test of the
counter's rejection behavior, not new evidence that the frozen claim is true; the
counter's acceptance side was observed only on the pristine control set.

## Scope notes

- The audit's input is the committed blob at `--tip`; uncommitted receipt edits are invisible
  to it. The mutants therefore live as commits in the disposable clone, which is outside the
  lane. This is a scope property of the counter (the claim's counting command names a commit),
  not a defect verdict.
- `output_ok` returns the truthy `COMMAND_ARGV_JSON` string rather than boolean `True` on
  success. Boolean use is unaffected (pristine baseline and restored audits pass); recorded as an
  observation only.
- v2 gate fixtures audited here are synthetic control inputs; nothing about live serving,
  model quality, endpoint readiness, or registered-consumer health is claimed.
- Filed report bytes were not read as mutable input and were not modified.

## Tooling record

No tool installed or upgraded during this seat (nothing needed; `git 2.56.0`,
`python3 3.14.8` already present). Pacman was not invoked.
