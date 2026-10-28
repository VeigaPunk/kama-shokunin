# C1 constant-drift mutation probe — M17C1ConstDrift

Base/tip: `65d7cad0fce90e34de37527cde22e97b63b118bf` (master and HEAD at probe start). Axis: operability. Detector: counter `grade()` + `score()` on the genuine live receipt, with the synthetic witness populated consistently from that receipt. Baseline counter was run fully, including its live leg and 16 controls.

Baseline actual output:

```text
tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True
```

Baseline genuine receipt SHA-256: `719e923f4b4cd2be63d3180c977ef260632383f173c9c41bd628e656e2bf5ad3`. Pristine counter SHA-256 before/after all probes: `a3498308938ed4715cfdf1ce5c9a2e4ddf9cb5f9befbba29857980721fe8c415`.

## Drift each frozen constant

Each row loads a scratch-only copy with that one constant drifted, then grades/scores the same genuine receipt. `ACCEPTED` means `score.met=True`.

| Constant drift | Genuine receipt result | Effect |
|---|---|---|
| `MODEL_SHA` → 64 zeroes | REJECTED (`model_digest` false; `met=False`) | Load-bearing: model digest is recomputed against the pinned value. |
| `SERVER_SHA` → 64 zeroes | REJECTED (`server_digest` false and live witness false; `met=False`) | Load-bearing in both receipt grade and live witness binding. |
| `ALIAS` → `other-alias` | REJECTED (`models_alias_id`, `props_alias`, `completion_model_id` false) | Load-bearing across captured model surfaces. |
| `FP_RE` → `^NEVER_MATCH$` | REJECTED (`completion_fingerprint` false; `met=False`) | Load-bearing: fingerprint is checked in receipt grading and witness. |
| `SCHEMA` → `forged/schema` | ACCEPTED (`met=True`, alltrue/verdict/live true, no inconsistencies) | Not load-bearing in grading/scoring of the receipt. The schema constant is not enforced by these functions. |

The four rejecting drift results come from the direct Python `grade`/`score` methods, not a rerun of the full CLI for each drift. The baseline detector itself ran successfully as shown above.

## Empty-ALIAS forged receipt

Mutant: `ALIAS = ''`. Built a receipt whose model surfaces all named `another-alias`, updated their captured-body hashes, recomputed stored checks, and gave `score()` a live witness naming `another-alias`. Result: **REJECTED** (`met=False`, live false; `models_alias_id`, `props_alias`, and `completion_model_id` false). So the weakened empty alias does not accept this internally consistent different-alias receipt; equality checks still require the empty string. No successful bypass shown.

Per-variant scratch counter SHA-256 (scratch-only files): `MODEL_SHA` `75e448fee2d752d5a2f67ddaf13fb2ef14e9d10e5abe0b844a26694869853017`; `SERVER_SHA` `56cc5327070ca4dd66ff56da652508eccdfe61aa85c69bb72215e12a635ae515`; `ALIAS` `21d9fd936430272ae94de3822a1cd59093b5cb32fceb976904673286ebc32798`; `FP_RE` `a6aaa006f25cd18cd6f645ceadb80e7423404acf2ad80a31eba979244f478e16`; `SCHEMA` `8d49363e07335de2d16efa03eca52be848205250fa764758a63cf4ce41c899c9`.

No tools installed or updated. Scratch `/fast/scratch/hyaku/kama-r62/w/M17C1ConstDrift` removed after preserving this report; pristine source remained byte-identical at its recorded hash. No lane source mutation was made. Counter/tally: `tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True`
