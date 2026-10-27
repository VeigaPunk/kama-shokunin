# F11C1SameNonceReplay
- Reproduced fresh run (`a05replay60`): `MODEL_OK`, exit 0.
- Same nonce, fresh directory, copied receipt+log+models/: verifier `[]` (accepted).
- Receipt+log only: `['manifest', 'blob-missing']` (rejected).
- Finding: acceptance authenticates copied artifact contents, not their run/directory provenance; full replay remains possible under C1's “from the run's own work dir” clause.
- No predicate changes or lane edits; scratch removed. No installs.