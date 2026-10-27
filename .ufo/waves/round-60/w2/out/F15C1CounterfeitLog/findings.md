# F15C1CounterfeitLog — C1 counterfeit-log attack

Axis: operability. Frozen predicate unchanged: C1-r60 requires fresh-nonce live run acceptance plus rejection of the seven specified controls, errors=0. W1's `MT01CounterClauseDrops` report records a genuine live baseline and demonstrates 30/31 isolated verifier-clause mutants survive; its `evidence/receipt-nonce-c180a667979787dd95.json` and `serve.log` are real captured artifacts.

## Offline verifier result

Built an offline bundle under `/fast/scratch/hyaku/kama-r60/F15C1CounterfeitLog/offline` using the W1 captured receipt and serve.log, the pinned fixture copied to the frozen-hash blob path, and a manually synthesized matching model manifest. Copied `tools/round60-c1-counter.py` into that bundle. No Ollama server was started for this check. Invoked the verifier function directly:

```sh
python3 - "$SCR/offline" <<'PY'
# Load receipt; synthesize manifest referencing FROZEN_MODEL_SHA;
# copy pinned stories260K.gguf to models/blobs/sha256-FROZEN_MODEL_SHA;
# import copied counter.py and print(repr(verify(receipt, run_dir, receipt['nonce'])))
PY
```

Exact output: `failures= []` (exit 0). Thus `verify()` accepts a copied capture/receipt plus fabricated run-dir structure offline; serve.log is copied rather than synthesized in this run. The acceptance proves consistency with the verifier's local predicates, not that an Ollama lifecycle occurred. In particular, code at `tools/round60-c1-counter.py:108-129` checks only a matching log substring, manifest-layer text, and the blob's pinned SHA; it does not cryptographically bind these files to a server process or prove they were produced during the run. A digest-valid fixture blob is reusable data, and the manifest is plain text.

## Scope / interpretation

This does **not** establish that the full counter can report `met=True` without a live run: its `main()` always calls `run_tool()` at lines 170-175 before computing `live_ok`, and subsequently runs fake-binary controls (lines 179-193). I did not bypass that behavior or claim the frozen C1 predicate is falsified. I established only that the independent per-receipt verifier is replayable offline and accepts the genuine copied W1 evidence when paired with a synthetic manifest and copied genuine blob. W1's already-documented 30 surviving clause-drop mutants reinforce that its 7 controls do not independently exercise many checks; see W1 `MT01CounterClauseDrops.md:53-81`. No lane source modified, no live server started, no tools installed/updated.
