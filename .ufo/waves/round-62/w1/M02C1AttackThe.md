# M02C1AttackThe — C1 fake-family probe

Axis: operability. Counter/functions were taken from `master` at `65d7cad0fce90e34de37527cde22e97b63b118bf`; live receipt from `/fast/scratch/hyaku/kama-r62/measure/c1b/receipt.json`. Reproduced `grade()`/`score()` without running a second runtime. The receipt nonce was installed as the scoring nonce. The fake witnesses included live-shaped values derived from the receipt; canned completion body was independently serialized and capture SHA updated to model a synthetic server's recorded body.

- Existing `envelope` fake (`chat.completion`, empty text): **REJECTED**; score `{"alltrue":false,"inconsistent":["completion_envelope","completion_finish_reason","completion_model_id","completion_fingerprint","completion_usage","completion_timings","completion_deterministic"],"live":true,"met":false,"verdict_ok":true}`.
- Existing `fingerprint` fake (`system_fingerprint=b1-x`): **REJECTED**; score `{"alltrue":false,"inconsistent":["completion_fingerprint","completion_deterministic"],"live":true,"met":false,"verdict_ok":true}`.
- Third fake with full copied valid completion envelope and recomputed capture hash, but witness PID changed to `child_pid + 1000`: **REJECTED**; score `{"alltrue":true,"inconsistent":[],"live":false,"met":false,"verdict_ok":true}`. This tests witness binding directly; the receipt's otherwise-valid capture does not salvage mismatched witness identity.

No accepted forgery; no C1 falsification found in this probe. Detector output reports the existing fake family as two of two rejected (the same `score()` met-false result for each). No tools installed/updated. Scratch probe source and receipt were removed after the output was recorded; no lane source was changed.
