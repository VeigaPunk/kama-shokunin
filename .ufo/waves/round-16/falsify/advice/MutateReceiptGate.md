VERDICT: partial — check-receipt.py mutation sensitivity: four assigned weakenings killed; trusting passed for probe claims survives.

## Scope and axes

Attacked only the receipt gate and its built-in detector. Axes: detector sensitivity, positive-receipt compatibility, and byte-exact isolation/restoration. No score, integration, or shipping decision is made here.

- Gate: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py`.
- Input receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/live/receipt.json`.
- Isolated scratch: `/tmp/kama-r16-MutateReceiptGate` (removed after restoration and all runs).
- Five independent gate copies, one logical defect per copy. No source gate, live receipt, producer, probe, fleet state, or sibling lane was edited. No server was started, network endpoint probed, other runtime invoked, or subagent dispatched.

## Exact detector invocation and bounds

For each absolute subject path below, these two argv vectors were executed on pristine, mutated, and restored bytes, in that order:

```python
["python3", SUBJECT, "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/live/receipt.json"]
["python3", SUBJECT, "--selftest"]
```

Each call used `subprocess.run(..., capture_output=True, text=True, timeout=30)`, with cwd and TMPDIR `/tmp/kama-r16-MutateReceiptGate`, PYTHONDONTWRITEBYTECODE=1, and the otherwise inherited environment. Independent calls ran with at most five workers. No timeout occurred. This is 30 top-level detector invocations; the three supplementary witness invocations below are separate.

| Subject (absolute path) | Mutation | Receipt exit pristine / mutant / restored | Selftest exit pristine / mutant / restored | Verdict |
|---|---|---|---|---|
| `/tmp/kama-r16-MutateReceiptGate/M1-skip-model-unchanged.py` | Skip model_unchanged derivation | 0 / 0 / 0 | 0 / 1 / 0 | **KILLED** |
| `/tmp/kama-r16-MutateReceiptGate/M2-accept-metrics-200.py` | Accept metrics status 200 as well as 501 | 0 / 0 / 0 | 0 / 1 / 0 | **KILLED** |
| `/tmp/kama-r16-MutateReceiptGate/M3-skip-refusal-membership.py` | Skip chosen-port membership in port_refusal_set | 0 / 0 / 0 | 0 / 1 / 0 | **KILLED** |
| `/tmp/kama-r16-MutateReceiptGate/M4-trust-probe-passed.py` | Trust passed=true for both probe claim derivations | 0 / 0 / 0 | 0 / 0 / 0 | **SURVIVED** |
| `/tmp/kama-r16-MutateReceiptGate/M5-accept-any-env-key.py` | Accept any recorded child_env_keys | 0 / 0 / 0 | 0 / 1 / 0 | **KILLED** |

All ten pristine detector calls passed; therefore none of the four kills relies on a failing baseline. All ten restored detector calls passed. Receipt-only validation accepted all five mutants: this positive input by itself does not distinguish the weakenings.

Exact common receipt stdout (all 15 receipt runs), with empty stderr:

```text
VALID /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/live/receipt.json
```

Exact common passing selftest stdout (all five pristine, M4 mutated, all five restored), with empty stderr:

```text
selftest: 16 mutations + unreadable case all rejected; valid receipt accepted
```

## Mutation definitions and expected detectors

The line numbers below refer to the pinned original gate. M4 changes two guards implementing one logical defect: trust a successful claimed probe check instead of re-deriving that claim. Its earlier structural/internal-consistency checks intentionally remain in place.

```diff
# M1, line 680
-    if "model_unchanged" in by_id:
+    if False and "model_unchanged" in by_id:

# M2, line 582
-        elif metrics_status != 501:
+        elif metrics_status not in (200, 501):

# M3, line 218 (hard pins and refusal-list shape validation remain)
-        if port in refusal:
+        if False and port in refusal:

# M4, original lines 607 and 630
-    if "probe_model_ok" in by_id:
+    if "probe_model_ok" in by_id and \
+            by_id["probe_model_ok"].get("passed") is not True:
-    if "probe_mismatch" in by_id:
+    if "probe_mismatch" in by_id and \
+            by_id["probe_mismatch"].get("passed") is not True:

# M5, line 301 (ignore the recorded field entirely)
-    env_keys = receipt.get("child_env_keys")
+    env_keys = []
```

Expected sensitivity: each listed selftest case should make the weakened gate return 0 for a bad receipt, causing the outer selftest to fail (exit 1). Actual outer output follows; M4 is the exception.

### M1: Skip model_unchanged derivation

Command: `python3 /tmp/kama-r16-MutateReceiptGate/M1-skip-model-unchanged.py --selftest` → exit **1**. Expected detector case(s): `model-changed-post-digest`.

```text
SELFTEST FAIL model-changed-post-digest: exit 0, want 1; stdout='VALID /tmp/kama-r16-MutateReceiptGate/check-receipt-1fx91dfx/case-7-model-changed-post-digest.json'
```

### M2: Accept metrics status 200 as well as 501

Command: `python3 /tmp/kama-r16-MutateReceiptGate/M2-accept-metrics-200.py --selftest` → exit **1**. Expected detector case(s): `metrics-200-not-501`.

```text
SELFTEST FAIL metrics-200-not-501: exit 0, want 1; stdout='VALID /tmp/kama-r16-MutateReceiptGate/check-receipt-kv229bdr/case-11-metrics-200-not-501.json'
```

### M3: Skip chosen-port membership in port_refusal_set

Command: `python3 /tmp/kama-r16-MutateReceiptGate/M3-skip-refusal-membership.py --selftest` → exit **1**. Expected detector case(s): `port-inside-refusal-set`.

```text
SELFTEST FAIL port-inside-refusal-set: exit 0, want 1; stdout='VALID /tmp/kama-r16-MutateReceiptGate/check-receipt-hueyf6wf/case-5-port-inside-refusal-set.json'
```

### M4: Trust passed=true for both probe claim derivations

Command: `python3 /tmp/kama-r16-MutateReceiptGate/M4-trust-probe-passed.py --selftest` → exit **0**. Expected detector case(s): `passed-flipped-against-stored-probe / model-ok-claimed-exit-2`.

```text
selftest: 16 mutations + unreadable case all rejected; valid receipt accepted
```

### M5: Accept any recorded child_env_keys

Command: `python3 /tmp/kama-r16-MutateReceiptGate/M5-accept-any-env-key.py --selftest` → exit **1**. Expected detector case(s): `env-key-off-allowlist`.

```text
SELFTEST FAIL env-key-off-allowlist: exit 0, want 1; stdout='VALID /tmp/kama-r16-MutateReceiptGate/check-receipt-91tew35o/case-15-env-key-off-allowlist.json'
```

## Survivor: non-equivalence witness

M4 survives the two assigned detectors, but it is not behaviorally equivalent to the pristine gate. A supplementary receipt was generated from the assigned live receipt with exactly these field updates to the record whose expect is `kama-not-this-model`; all claimed checks, including passed=true and their original observed fields, were left unchanged:

```python
mismatch["exit"] = 0
mismatch["result"]["summary"].update(exit=0, model_ok=1, drift=0)
mismatch["result"]["rows"][0].update(
    verdict="MODEL_OK", reason="matched", drift=False)
```

It was serialized with `json.dumps(witness, indent=2, sort_keys=True) + "\n"` to `/tmp/kama-r16-MutateReceiptGate/witness-coherent-wrong-mismatch.json`; SHA-256 `4c03bbb475bc9c720b514dccac60785ef4114d2e4a80175ba13dff90188867de`.

Exact supplementary commands and outputs (same 30-second bound, empty stderr in all three):

- **pristine control**, `python3 /tmp/kama-r16-MutateReceiptGate/pristine.py /tmp/kama-r16-MutateReceiptGate/witness-coherent-wrong-mismatch.json` → exit **1**.

```text
INVALID /tmp/kama-r16-MutateReceiptGate/witness-coherent-wrong-mismatch.json: 3 problem(s)
  - probe_mismatch: stored verdict 'MODEL_OK' != MODEL_MISMATCH
  - probe_mismatch: stored reason 'matched' != served-id-mismatch
  - probe_mismatch: recorded exit 0 != 2
```

- **M4 mutated**, `python3 /tmp/kama-r16-MutateReceiptGate/M4-trust-probe-passed.py /tmp/kama-r16-MutateReceiptGate/witness-coherent-wrong-mismatch.json` → exit **0**.

```text
VALID /tmp/kama-r16-MutateReceiptGate/witness-coherent-wrong-mismatch.json
```

- **M4 restored**, `python3 /tmp/kama-r16-MutateReceiptGate/M4-trust-probe-passed.py /tmp/kama-r16-MutateReceiptGate/witness-coherent-wrong-mismatch.json` → exit **1**.

```text
INVALID /tmp/kama-r16-MutateReceiptGate/witness-coherent-wrong-mismatch.json: 3 problem(s)
  - probe_mismatch: stored verdict 'MODEL_OK' != MODEL_MISMATCH
  - probe_mismatch: stored reason 'matched' != served-id-mismatch
  - probe_mismatch: recorded exit 0 != 2
```

The witness is therefore rejected before mutation, accepted by M4, and rejected after restoration. M4 remains a **survivor of the prescribed receipt + selftest detector**, not a killed mutant merely because this additional witness distinguishes it.

[INFERENCE] The built-in probe cases are masked by other assertions: `passed-flipped-against-stored-probe` changes the mismatch row to MODEL_OK without changing its exit 2, so the earlier MODEL_OK/exit consistency guard (original gate lines 451–456) can reject it even when the claim-specific derivation guards (607–652) are disabled. A coherent wrong-verdict/exit/drift tuple is the missing discrimination demonstrated above. This is a detector-coverage finding, not evidence that the unmodified gate accepts the witness; it rejected it with three named problems.

## Hashes and restoration evidence

Common before and restored SHA-256 for every subject, pristine control, and lane gate: **`954340c51ab0c35a9aaf01537e805cfe604fca7e082c04f59e78e3c1d79a47ba`**.

| Subject | Mutated SHA-256 | Restored SHA-256 |
|---|---|---|
| `/tmp/kama-r16-MutateReceiptGate/M1-skip-model-unchanged.py` | `ebf5600b2785af5537f5c297e74aa31fa2c27b62078967be8b4e442180cd8101` | `954340c51ab0c35a9aaf01537e805cfe604fca7e082c04f59e78e3c1d79a47ba` |
| `/tmp/kama-r16-MutateReceiptGate/M2-accept-metrics-200.py` | `9c923279487db871a1d19a9728c39a9dbede134383d3cff1227ce230c4a7bbb4` | `954340c51ab0c35a9aaf01537e805cfe604fca7e082c04f59e78e3c1d79a47ba` |
| `/tmp/kama-r16-MutateReceiptGate/M3-skip-refusal-membership.py` | `8a16bb2e414ff739b5402960305fa42c4fc66614ee09ec3af34144037f28b968` | `954340c51ab0c35a9aaf01537e805cfe604fca7e082c04f59e78e3c1d79a47ba` |
| `/tmp/kama-r16-MutateReceiptGate/M4-trust-probe-passed.py` | `b3b11ba991cbfc83c8ae1937e1cec60fe2aace64e97ea9883b24aa4f362bdac3` | `954340c51ab0c35a9aaf01537e805cfe604fca7e082c04f59e78e3c1d79a47ba` |
| `/tmp/kama-r16-MutateReceiptGate/M5-accept-any-env-key.py` | `f5274d95872e158da2d62a09416f0ffc355a5995a97d6da0918c936ac038d58e` | `954340c51ab0c35a9aaf01537e805cfe604fca7e082c04f59e78e3c1d79a47ba` |

`sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/live/receipt.json /tmp/kama-r16-MutateReceiptGate/*.py` ran before mutation (exit 0); `sha256sum /tmp/kama-r16-MutateReceiptGate/*.py` recorded the mutant hashes (exit 0).

For every subject in the table, the following restore and byte-comparison commands ran, chained with `&&`; all five cp operations and all five cmp operations succeeded (overall shell exit 0, cmp stdout empty):

```text
cp -- /tmp/kama-r16-MutateReceiptGate/pristine.py SUBJECT
cmp -- /tmp/kama-r16-MutateReceiptGate/pristine.py SUBJECT
```

The same successful shell then ran:

```text
sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/live/receipt.json /tmp/kama-r16-MutateReceiptGate/*.py /tmp/kama-r16-MutateReceiptGate/witness-coherent-wrong-mismatch.json
```

It printed the common restored digest above for all six scratch gate files and the lane gate. The receipt digest remained **`6fb32c05f68d9291563a5e404a963e0b2b7e4ab88e18aa4fabd1dee847255eeb`**, identical to its pre-run digest. The restored detector results and restored witness rejection are recorded above.

One preliminary tool-based restoration attempt failed (Eval exit 1): a raw read was truncated, and the write guard refused incomplete replacement with `RuntimeError: Refusing to overwrite ... with an incomplete read projection`. No successful overwrite was reported; all five mutant anchors were re-read before the successful cp restoration. The raw-read limitation was reported through the tool issue route. No detector result or hash above comes from that failed attempt.

Cleanup command (after exact-byte restoration and reruns):

```text
rm -rf -- /tmp/kama-r16-MutateReceiptGate && test ! -e /tmp/kama-r16-MutateReceiptGate && printf 'scratch_removed=yes\n'
```

Exit **0**, stdout **`scratch_removed=yes`**. Scratch JSON logs, witness, and copies were deliberately removed; this report retains the commands, exact relevant outputs, mutation definitions, and hashes needed to reproduce the finding.

## Limitations and installs

- Exactly five assigned logical gate mutations were tested; these results are not a claim about all possible validator defects.
- M3 covers chosen-port membership in the receipt refusal set, not removal of hard-pin membership requirements. M4 skips only the two claim-specific derivation blocks, not all probe consistency validation. M5 accepts arbitrary recorded child_env_keys by ignoring that field completely, not merely relaxing its allowlist.
- The supplementary witness tests a coherent incorrect mismatch verdict; it does not change the contract or modify the shipped detector. L1 owns any integration and final measurements.
- No live lifecycle, server, or probe matrix was run. No invocation of the L1 receipt-rewriting measurement script occurred.
- Installs/updates: **none**.
