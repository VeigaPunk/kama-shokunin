# F01C1FalseGreenRepro — C1 H1

Reproduced the W1 H1 false-green using a patched copy only under `/fast/scratch/hyaku/kama-r60/F01C1FalseGreenRepro` (scratch removed after preserving evidence). The copy inserted a synchronization gate after the `ps-after` capture and `ps-lists-loaded` check, immediately before `run_evidence(..., 'after')`; no lane source changed.

Command: `TMPDIR=/fast/scratch/hyaku/kama-r60/F01C1FalseGreenRepro/tmp python3 /fast/scratch/hyaku/kama-r60/F01C1FalseGreenRepro/run.py` (runner launched patched tool with nonce `f01h1sigterm01`, Ollama v0.40.11, fixture `stories260K.gguf`). At the gate the runner sent `SIGTERM` to the exact recorded Ollama child PID `3219514`, then released replay. Tool output: exit `0`, verdict `MODEL_OK`; `evidence-after-load` passed, teardown `{returncode: 0, sigkill_needed: false, port_closed: true}`.

Imported `verify()` from `tools/round60-c1-counter.py` and checked the resulting receipt against its own run directory and nonce: `verifier_bad=[]`, `verifier_accepted=true`. This is an end-to-end false green: a live Ollama child was externally terminated before evidence replay completed, but both tool and independent verifier accepted the receipt. Mechanism matches frozen H1: replay grades captured files and teardown does not establish that the tool caused termination.

Evidence: `repro/receipt.json`, `repro/serve.log`, `repro/signal.txt`. Disk guard status was checked before the run; scratch removed. No installs/updates; no lane edits.