# ExecReceiptMutants — round-33 C2 receipt-auditor mutation exercise

Seat: ExecReceiptMutants (leaf executor, header lane: kama / round 33 / attempt 1 / wave 1).
Target: exercise `tools/round33-gate-receipts.py audit` with controlled missing-field and
changed-output inputs against a temporary isolated copy of the four committed C2 receipts.

**Result: all three specified mutations are detected as invalid, `met=False`, CLI exit 1.**
Clean baseline is 4/4 `met=True`, exit 0. No lane file, lane receipt byte, Git index or jj
state was modified by this seat.

## 1. Method and environment

- Lane repo: `/home/vgpnk/Projects/shokunin/kama-shokunin`, HEAD `7c35289da5f4b94e062cd900eb086919e5094003`
  (unchanged before and after this run).
- Isolated copy: `git clone --quiet --no-hardlinks file:///home/vgpnk/Projects/shokunin/kama-shokunin /tmp/r33-receipt-mutants/repo`
  → clone HEAD `7c35289da5f4b94e062cd900eb086919e5094003`. All mutations were committed only in
  this clone (fixed identity `r33-mutant-lab <r33-mutant-lab@shokunin.local>`, `commit.gpgsign=false`).
  The clone is outside the lane and disposable.
- Receipt set under audit: `.ufo/waves/round-33/c2/final/gate-tip-r33.out` plus
  `controls/{thin-row,empty-exit-map,missing-path}-r33.out`.
- Every run used the auditor's own CLI, from the clone root:

```
python3 tools/round33-gate-receipts.py audit --repo . \
  --tip <TIP> \
  --source-rev 967d88528c1d83535563f971863f7855f76b4849 \
  --receipt-dir .ufo/waves/round-33/c2/final
```

- Environment: Python 3.14.8, git 2.56.0. No tool installed or upgraded; no pacman transaction
  was attempted (host-wide pause respected).

The auditor reads receipts with `git show <tip>:<path>` (`receipt_blob`), so each mutation had
to land as a commit in the clone; working-tree-only edits are not audited. Each mutation run
started from a `git reset --hard 7c35289…` pristine base.

## 2. Mutation runs — CLI output verbatim

| Run | Mutation | Tip (clone) | CLI output | Exit |
|---|---|---|---|---|
| M0 | none (clean baseline) | `7c35289da5f4b94e062cd900eb086919e5094003` | `R33_GATE_RECEIPT_AUDIT source_rev=967d88528c1d83535563f971863f7855f76b4849 tip=7c35289da5f4b94e062cd900eb086919e5094003 complete=4/4 missing=0 invalid=0 met=True` | 0 |
| M1 | remove `EXIT_CODE` header from all four receipts | `1c6687fc88685247b20c5ace99c2ffc0a8897efb` | `R33_GATE_RECEIPT_AUDIT source_rev=967d88528c1d83535563f971863f7855f76b4849 tip=1c6687fc88685247b20c5ace99c2ffc0a8897efb complete=0/4 missing=0 invalid=4 met=False` | 1 |
| M2 | remove `EVALUATED_REV` header from all four receipts | `9ae0a703b0357466a52ee4fb602dcc3f8b2a3656` | `R33_GATE_RECEIPT_AUDIT source_rev=967d88528c1d83535563f971863f7855f76b4849 tip=9ae0a703b0357466a52ee4fb602dcc3f8b2a3656 complete=0/4 missing=0 invalid=4 met=False` | 1 |
| M3 | change one expected defect line in `thin-row` receipt | `21c9f9936896f733ab47ea6b7f2acd5d1d738ad9` | `R33_GATE_RECEIPT_AUDIT source_rev=967d88528c1d83535563f971863f7855f76b4849 tip=21c9f9936896f733ab47ea6b7f2acd5d1d738ad9 complete=3/4 missing=0 invalid=1 met=False` | 1 |
| M4 | remove `EXIT_CODE` from `gate-tip` only | `b44cac16389fcdddd1860dd0fa8851d8924048df` | `R33_GATE_RECEIPT_AUDIT source_rev=967d88528c1d83535563f971863f7855f76b4849 tip=b44cac16389fcdddd1860dd0fa8851d8924048df complete=3/4 missing=0 invalid=1 met=False` | 1 |
| M5 | remove `EVALUATED_REV` from `gate-tip` only | `b64ea047b6801b264df9046788f3fbbe0d17486e` | `R33_GATE_RECEIPT_AUDIT source_rev=967d88528c1d83535563f971863f7855f76b4849 tip=b64ea047b6801b264df9046788f3fbbe0d17486e complete=3/4 missing=0 invalid=1 met=False` | 1 |

M1 and M2 apply the field removal to the whole receipt set (the "remove field" mutation applied
once per run); M4/M5 repeat each removal on a single receipt to show the counter attributes the
defect to exactly the mutated receipt instead of failing the set. M3 mutates a single receipt by
construction.

## 3. Exact mutated bytes

`git show --format= --unified=0` in the clone:

M1 (`1c6687f`) — four deletions only:
```
-EXIT_CODE=1
-EXIT_CODE=1
-EXIT_CODE=1
-EXIT_CODE=0
```
M2 (`9ae0a70`) — four deletions only:
```
-EVALUATED_REV=58f49f42348c74af41a31dc06697f4edf4292c8d
-EVALUATED_REV=a1ff870829fb2980f9716359e115095441eb7297
-EVALUATED_REV=77ff9c056e32f5c5b41abd3c0d2e83a59c2e6a83
-EVALUATED_REV=967d88528c1d83535563f971863f7855f76b4849
```
M3 (`21c9f99`) — one line replaced in `controls/thin-row-r33.out`:
```
-defective .ufo/waves/round-33/count-fixture.py: thin-row
+defective .ufo/waves/round-33/count-fixture.py: thin-row-alias
```
M4 (`b44cac1`) — one deletion in `gate-tip-r33.out`: `-EXIT_CODE=0`.
M5 (`b64ea04`) — one deletion in `gate-tip-r33.out`: `-EVALUATED_REV=967d88528c1d83535563f971863f7855f76b4849`.

Receipt SHA-256 at the pristine tip (`7c35289…`), equal in lane worktree and committed blob:
`gate-tip-r33.out d2f8f48d…`, `thin-row-r33.out fc4c4490…`,
`empty-exit-map-r33.out ccfb4bb4…`, `missing-path-r33.out 23b48c21…`
(full digests: `d2f8f48d31470bc6ce0b86f82be432f2203a7a8006750331a93f3c0b4838ac0b`,
`fc4c4490efd50a38d0e40d6c8e826341e787017df94387142daaf9e1a42682cd`,
`ccfb4bb49ad069d1cb5a7ae133d32a318b9c0c7359b4a95457a7f7e6ecfbe553`,
`23b48c21f093bdefc8a72b3eca507cca167885b0659b9e9fb6dd17ff705fb1ea`).

## 4. Per-receipt attribution

The CLI prints only aggregate counts (`complete/missing/invalid`), so each tip was additionally
evaluated case-by-case using the auditor module's own `parse_receipt`, `output_ok`,
`known_runner_hashes` and the same stable-field comparison as `audit`. One shared gate replay
oracle (`expected_receipts`) was computed per run; verdicts:

| Tip | gate-tip | thin-row | empty-exit-map | missing-path |
|---|---|---|---|---|
| M0 `7c35289` | valid | valid | valid | valid |
| M1 `1c6687f` | INVALID | INVALID | INVALID | INVALID |
| M2 `9ae0a70` | INVALID | INVALID | INVALID | INVALID |
| M3 `21c9f99` | valid | INVALID | valid | valid |
| M4 `b44cac1` | INVALID | valid | valid | valid |
| M5 `b64ea04` | INVALID | valid | valid | valid |

Attribution matches the mutated-file sets from `git show --stat`: M3 touched only
`controls/thin-row-r33.out`; M4/M5 touched only `gate-tip-r33.out`. Every mutation produced
`invalid` (never `missing`); the missing-receipt branch was not exercised.

## 5. Findings

1. **Missing `EXIT_CODE` is rejected.** Both the stable-field equality check and
   `output_ok`'s `headers.get("EXIT_CODE") == str(expected_exit)` fail. Observed: 0/4 complete,
   4/4 invalid, exit 1 (set-level); 1/4 invalid with the other three complete (single receipt).
2. **Missing `EVALUATED_REV` is rejected.** The stable-field comparison and the `COMMAND_ARGV_JSON`
   evaluated-revision consistency check both fail. Observed: 0/4 complete, 4/4 invalid, exit 1;
   1/4 invalid single-receipt.
3. **A changed expected defect line is rejected even when every header field is intact.**
   Changing only `thin-row` → `thin-row-alias` in the stdout block of one receipt yields
   3/4 complete, 1/4 invalid, `met=False`, exit 1. `stdout == expected_stdout` plus
   `expected_line in stdout.splitlines()` catch it.
4. **Baseline control holds in an isolated clone.** The four committed receipts audit 4/4
   `met=True` in both the lane repo (read-only run) and the isolated clone, so the mutation
   results are not an artifact of the copy.
5. **Observed lineage behavior (not a defect introduced here).** The committed receipts carry
   `RUNNER_SHA256=309543621a90f3c50bf130e06bc4e26a95e40202d84e81f769fca826a9e1dc04`
   (the runner blob committed at `f2c0fc1`), while the executing runner
   `tools/round33-gate-receipts.py` hashes to
   `196d9766cadc286fde6e6eeda92e0984153d91576b9333eb6a3ec20ef8cdfb00` (at `36c5cc2`/HEAD).
   `known_runner_hashes(repo, tip)` accepts any runner blob reachable from tip history, and the
   receipts still audit 4/4. Runner identity is therefore pinned to a history window, not
   byte-equality with the tip's runner.
6. **`COMMAND_ARGV_JSON` is structurally validated, not compared.** The clone baseline passes
   while the receipts' argv references `/home/vgpnk/Projects/shokunin/kama-shokunin` and the
   vanished capture directory `/tmp/kama-r33-gate-vjibi9wa/...`; `output_ok` requires only a
   six-element argv with an absolute repo path and `argv[5] == EVALUATED_REV`.
7. **Audit scope is committed blobs.** Receipt edits that are not committed at `--tip` are
   invisible to the audit; this mutation test required a clone-local commit per run.

## 6. Files changed

- This report only: `.ufo/waves/round-33/w1/out/ExecReceiptMutants.md`.
- Lane repo HEAD `7c35289…` unchanged; the four C2 receipt files are byte-identical to their
  `HEAD` blobs; `git status --porcelain` shows only sibling-authored wave artifacts and the
  pre-existing `swarm-registry.json` modification, none written by this seat.
- No commits, no jj commands, no writes outside the lane report path; the mutation clone lives
  at `/tmp/r33-receipt-mutants/repo` and can be deleted.

## 7. Limits, risks, blockers

- Claims only auditor sensitivity to the three supplied mutation classes. No claim about C1,
  the full C2 counter, service restoration, endpoint readiness, model quality, or live serving;
  the v2 controls are synthetic fixture inputs.
- The CLI reports aggregates only; without the per-case evaluation in §4, an `invalid=1` result
  would not name the defective receipt. For any C2 evidence that must attribute a defect,
  either use one mutated receipt per run (M3–M5 pattern) or re-evaluate per case.
- Only exit 1 (invalid) and exit 0 (met) were exercised; the `ReceiptError`/exit-2 branch was
  not triggered. `missing` was never nonzero.
- Mutation testing ran against clone commits whose parent is `7c35289…`; results do not
  establish behavior for other tips, other receipt directories, or a runner differing from
  `196d9766…`.
- No blockers.
