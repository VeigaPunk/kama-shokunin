VERDICT: killed — both assigned inline-`EXIT_CODE` mutants (removed, value falsified) are rejected by the same C2 audit CLI; pristine and restored bytes met 4/4.

# MutReceiptExit — inline EXIT_CODE mutation probe (C2)

## Axes and scope

- Calibration: sensitivity of the C2 receipt auditor to (A) a receipt with the inline `EXIT_CODE` header line removed and (B) a receipt whose `EXIT_CODE` value is falsified (`0` → `1`), with every other byte unchanged.
- Isolation / no harm: all mutation happened in a disposable `git clone` under `/tmp`; the lane repository, its HEAD, its index and its jj state were never written. The mutated file was restored to the exact pristine bytes in the scratch clone.
- Attacked claim: C2 operability — "complete replay receipts for the clean gate-tip and three named v2 controls: 0/4→4/4 receipts with pinned source/evaluated revisions and inline exit codes."
- Result is limited to these two mutants: **2 killed, 0 survived, 0 inconclusive**. This is not a whole-C2 admission judgment, not live serving evidence, and says nothing about header fields other than `EXIT_CODE`.

## Detector

The assigned counting command, run verbatim against the scratch clone (only `--repo` and `--tip` differ from the lane invocation):

```text
python3 tools/round33-gate-receipts.py audit --repo /tmp/r33-mut-receipt-exit/repo \
  --tip <tip> --source-rev 967d88528c1d83535563f971863f7855f76b4849 \
  --receipt-dir .ufo/waves/round-33/c2/final
```

The `EXIT_CODE` header is load-bearing in two independent predicates of `tools/round33-gate-receipts.py` (pristine source, sha256 `309543621a90f3c50bf130e06bc4e26a95e40202d84e81f769fca826a9e1dc04`):

- `output_ok()` line 325: `and headers.get("EXIT_CODE") == str(expected_exit)`.
- `audit()` lines 441–447: `stable_fields` includes `"EXIT_CODE"` and every stable header must equal the freshly replayed expected receipt.

The capture path writes the line at source line 217 (`f"EXIT_CODE={exit_code}"`). The audit reads committed receipt blobs (`git show <tip>:<path>`), so a mutant must be committed in the scratch clone to be visible.

## Method and scratch target

1. `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/r33-mut-receipt-exit/repo` at lane HEAD `7c35289da5f4b94e062cd900eb086919e5094003`; `--source-rev` commit `967d88528c1d83535563f971863f7855f76b4849` is present as an ancestor, and runner history (needed by `known_runner_hashes`) is intact.
2. Scratch receipt `gate-tip-r33.out` initially hashed `d2f8f48d31470bc6ce0b86f82be432f2203a7a8006750331a93f3c0b4838ac0b`, identical to the lane blob at HEAD.
3. Baseline audit in the lane and in the scratch clone both returned `complete=4/4 missing=0 invalid=0 met=True`, exit 0.
4. Mutant A: branch `mut-exit-missing` from the pristine tip; deleted the single line `EXIT_CODE=0`; committed `654e5e76cf05d54d1ba7813d7b1a72cc85c3cad1` ("mutant A: remove EXIT_CODE header from gate-tip receipt").
5. Mutant B: branch `mut-exit-value` from the pristine tip (independent of A); replaced `EXIT_CODE=0` with `EXIT_CODE=1`; committed `948d6f51f003438d8f15a194e81f0dce46af4cae` ("mutant B: falsify EXIT_CODE value 0->1 in gate-tip receipt").
6. Restored: `git checkout 7c35289...` in the scratch clone; receipt hash returned to `d2f8f4...`; audit re-run.

Both mutations were applied with the surgical edit tool (single-line replacement/deletion); no `sed`/`perl`/scripted rewriting was used. The two mutant branches leave the three control receipts byte-identical, so the audit's per-case counters isolate the mutation to `gate-tip`.

## Results

| State | Scratch commit | Receipt sha256 | Audit output | Exit | Verdict |
|---|---|---|---:|---:|---|
| lane pristine | `7c35289` (lane HEAD) | `d2f8f48d…38ac0b` | `complete=4/4 missing=0 invalid=0 met=True` | 0 | baseline passes |
| scratch pristine | `7c35289` | `d2f8f48d…38ac0b` | `complete=4/4 missing=0 invalid=0 met=True` | 0 | baseline passes |
| **A: EXIT_CODE removed** | `654e5e7` | `41681d1f…ec8a10` | `complete=3/4 missing=0 invalid=1 met=False` | 1 | **killed** |
| **B: EXIT_CODE 0→1** | `948d6f5` | `6842affb…95dd6e` | `complete=3/4 missing=0 invalid=1 met=False` | 1 | **killed** |
| restored | `7c35289` | `d2f8f48d…38ac0b` | `complete=4/4 missing=0 invalid=0 met=True` | 0 | restored |

Full audit lines (verbatim):

```text
R33_GATE_RECEIPT_AUDIT source_rev=967d88528c1d83535563f971863f7855f76b4849 tip=654e5e76cf05d54d1ba7813d7b1a72cc85c3cad1 complete=3/4 missing=0 invalid=1 met=False
R33_GATE_RECEIPT_AUDIT source_rev=967d88528c1d83535563f971863f7855f76b4849 tip=948d6f51f003438d8f15a194e81f0dce46af4cae complete=3/4 missing=0 invalid=1 met=False
```

Both mutants are counted as **invalid**, not **missing**: `parse_receipt()` accepts the receipt in both states (`parse_ok=True`), and rejection happens on the header/value comparison. Neither mutant touched `RUNNER_SHA256` or the runner path, and `RUNNER_SHA256` remained `309543621a90f3c50bf130e06bc4e26a95e40202d84e81f769fca826a9e1dc04` (in `known_runner_hashes`), so the kill is not a runner-identity artifact.

### Supplementary attribution (same module predicates, not a substitute detector)

A probe importing `tools/round33-gate-receipts.py` and calling its own `parse_receipt`, `expected_receipts` and `output_ok` on the three committed blobs produced:

```text
pristine        parse_ok=True stable_field_mismatches={}                  output_ok=<truthy argv list>
mutant-A-removed parse_ok=True stable_field_mismatches={'EXIT_CODE': (None, '0')} output_ok=False
mutant-B-value   parse_ok=True stable_field_mismatches={'EXIT_CODE': ('1', '0')}  output_ok=False
```

Only `EXIT_CODE` differs from the replayed expected receipt in each mutant, and `output_ok()` returns `False` for both.

## Mutant detail

Mutant A (one line deleted):

```diff
--- a/.ufo/waves/round-33/c2/final/gate-tip-r33.out
+++ b/.ufo/waves/round-33/c2/final/gate-tip-r33.out
@@ -7,7 +7,6 @@
 RUNNER_SHA256=309543621a90f3c50bf130e06bc4e26a95e40202d84e81f769fca826a9e1dc04
-EXIT_CODE=0
 STDOUT_BEGIN
```

Mutant B (value only):

```diff
--- a/.ufo/waves/round-33/c2/final/gate-tip-r33.out
+++ b/.ufo/waves/round-33/c2/final/gate-tip-r33.out
@@ -7,7 +7,7 @@
-EXIT_CODE=0
+EXIT_CODE=1
 STDOUT_BEGIN
```

## Hashes and exact restoration

| Subject | Before | Mutated | After restoration |
|---|---|---|---|
| `gate-tip-r33.out` (scratch) | `d2f8f48d31470bc6ce0b86f82be432f2203a7a8006750331a93f3c0b4838ac0b` | A: `41681d1fee10a6578a6348c10d3d9fd8aeeeb2caef07a69a1e3b9cfcbeec8a10` | `d2f8f48d31470bc6ce0b86f82be432f2203a7a8006750331a93f3c0b4838ac0b` |
| `gate-tip-r33.out` (scratch) | same | B: `6842affb1109c5940ae7e1de58476e7a0412809728e40ef1430ea7f36795dd6e` | same |

Restoration was byte-exact in the scratch clone; the restored state was re-audited and returned `met=True`.

## Lane untouched (post-probe evidence)

- Lane HEAD remains `7c35289da5f4b94e062cd900eb086919e5094003`; no commit, ref, index or jj write was made.
- Lane receipt hashes after the probe are unchanged:
  - `gate-tip-r33.out` `d2f8f48d…38ac0b`
  - `controls/empty-exit-map-r33.out` `ccfb4bb4…fbe553`
  - `controls/missing-path-r33.out` `23b48c21…5fb1ea`
  - `controls/thin-row-r33.out` `fc4c4490…2682cd`
- `git diff --stat -- .ufo/waves/round-33/c2/final` is empty.
- Lane `git status --short` shows only peer-owned artifacts (`swarm-registry.json` modification and sibling evidence dirs) plus this report's own files; nothing under `tools/` or the C2 receipt tree changed.

## Evidence files

All under `.ufo/waves/round-33/w1/out/MutReceiptExit-evidence/`:

- `lane-pristine-audit.out` — baseline audit against the lane repo.
- `baseline-scratch.out` — baseline audit against the scratch clone.
- `mutant-A-removed-exit-code.out`, `mutant-B-falsified-exit-value.out` — detector outputs with exit codes.
- `restored-pristine.out` — restored-state audit.
- `mutant-A.diff`, `mutant-B.diff` — exact committed diffs.
- `pristine-receipt.out`, `mutant-A-receipt.out`, `mutant-B-receipt.out` — full receipt bytes per state.
- `attribution-probe.txt` — supplementary predicate attribution.
- `hashes.txt` — commit ids, receipt sha256 by state, lane receipt hashes, lane HEAD.

The scratch clone is retained at `/tmp/r33-mut-receipt-exit/repo` (branches `mut-exit-missing`, `mut-exit-value`; checked out detached at the pristine tip). It is a non-durable path; the diffs, hashes and detector outputs above are the durable record.

## Boundaries and limitations

- The C2 fixtures are synthetic control inputs; no live endpoint, model quality, service restoration or registered-consumer health is claimed.
- Only the `gate-tip` receipt was mutated. The three control receipts were left pristine, so the audit's `complete=3/4` shows the failure is attributed to that one case; this does not test control-receipt `EXIT_CODE` handling separately.
- [INFERENCE] Because `EXIT_CODE` is checked in both `output_ok()` and the `stable_fields` comparison, the detector rejects either mutation even if one predicate were removed; this probe does not test that redundancy.
- A surviving mutant would have been a coverage finding, not a contract change; none survived here.

## Installs

None. No package transaction, tool install or upgrade was performed; no pacman command was run.
