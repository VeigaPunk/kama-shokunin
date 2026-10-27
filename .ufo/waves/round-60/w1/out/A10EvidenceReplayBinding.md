# A10 — evidence replay binding falsification

Axis: operability. The patched-copy attack succeeded: the live lifecycle accepted hard-coded replay findings without invoking `kama-ollama-evidence.py`, and the frozen verifier accepted the resulting receipt.

## Method and evidence

Copied the three specified files (`kama-ollama-live.py`, `kama-ollama-evidence.py`, `ollama-live-pin.tsv`) into a scratch tree, preserving `REPO` resolution. Patched only `run_evidence()` in the copied live tool: it still writes the supplied tags/ps bytes to the expected work-dir files, but instead of subprocess-running the classifier it returns `available_not_loaded, 1` for `before` and `loaded_same_digest, 0` for `after`. Ran that copy against the installed pinned Ollama and fixture using nonce `a10replay60`.

Exact observed outputs:

```text
tool_exit=0
verdict=MODEL_OK
nonce=a10replay60
evidence-before=[{'detail': 'kama-ollama-evidence over tags+ps before any generation: available_not_loaded exit 1', 'evaluated': True, 'id': 'evidence-before-load', 'passed': True}]
evidence-after=[{'detail': 'kama-ollama-evidence over tags+ps after generation: loaded_same_digest exit 0', 'evaluated': True, 'id': 'evidence-after-load', 'passed': True}]
verify_failures=[]
verify_accepted=True
```

The receipt and captured stdout are in `w1/out/A10EvidenceReplayBinding/` (`replay-stub-receipt.json`, `replay-stub-run.stdout`, and `replay-stub-verify.stdout`). The receipt includes the normal live captures and its capture SHA-256 values; verifier result above is from importing the frozen `tools/round60-c1-counter.py` and calling `verify(receipt, run_dir, nonce)` directly. The committed lane source was not modified. Scratch was removed after copying the evidence. Disk guard status was checked before the run; it reported `/fast/scratch/hyaku` 590.2G free.

## Clause result

`verify()` fails to reject the forged replay. It requires `evidence-before-load` and `evidence-after-load` to have `passed is True` and `evaluated is True` (`REQUIRED` loop), verifies SHA-256 over the receipt's capture bodies, then parses tags/ps to check model identity and digest consistency. It never invokes or independently re-derives `kama-ollama-evidence.py`'s classifications, and does not bind the written `evidence-{before,after}-{tags,ps}.json` files to the captures. Consequently the forged findings and detail text satisfy the evidence check flags while the genuine HTTP captures, checksums, server log, manifest, and imported-blob checks remain valid. No verifier clause rejected this receipt.

A counter clause closing this specific gap must independently run the pinned evidence classifier over the receipt's `captures.tags.body` paired with `captures.ps-before.body` and `captures.ps-after.body`, and require both its finding IDs and exit codes to equal the expected before/after results (and/or bind the replay input files byte-for-byte to those receipt captures). Merely checking the evidence check booleans, recorded text, or capture digests does not establish replay execution.
