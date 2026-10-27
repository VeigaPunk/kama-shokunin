# F11C1SameNonceReplay — C1 same-nonce replay

Attacked frozen C1-r60 clause: verifier “re-derives the binary digest from frozen constants, the nonce-named model from the capture bodies, and the server log / model manifest / imported blob from the run's own work dir.” Predicate is a fresh-nonce live run independently accepted; this probe tests whether acceptance proves those artifacts came from that run.

Ran `python3 tools/kama-ollama-live.py --work /fast/scratch/hyaku/kama-r60/F11C1SameNonceReplay/run1 --nonce a05replay60 --out .../run1/receipt.json --ollama-bin ~/.local/opt/ollama-v0.40.11/bin/ollama --model-gguf ~/.cache/kama-shokunin/models/stories260K.gguf`; output verdict `MODEL_OK`, exit 0. Copied receipt and serve.log, plus the entire `models/` tree (including manifest and blob), to a distinct fresh replay directory. Called frozen `round60-c1-counter.py` `verify(receipt, replay_dir, "a05replay60")`.

Exact result: `same_nonce_full_bundle_failures=[]`; `same_nonce_full_bundle_accepted=true`. Receipt+log without model store: `same_nonce_receipt_log_only_failures=['manifest', 'blob-missing']`; `same_nonce_receipt_log_only_accepted=false`.

Finding: a byte-for-byte copied complete artifact bundle from a real run is accepted under the same nonce in a different directory; verifier validates artifact contents but not run/work-dir provenance or freshness. This does not pass the receipt+log-only variant and does not show a fabricated receipt can pass. C1 controls/predicate unchanged. Scratch removed by exit trap. No installs/updates; no lane source edited.