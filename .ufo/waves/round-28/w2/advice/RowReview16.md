# RowReview16 — C1 falsify: F28-31 (logit_bias, S170) and F28-32 (ignore_eos, S171)

Verdict: **holds** for both rows. No wrong/overstated/harmful statement found; no corrected meaning sentence is needed.

## Live re-measure (port 48316, pinned server b11755, stories260K.gguf)

Counter's exact request: `POST /completion` body `{"prompt": "Once upon a time", "n_predict": 1}` updated with the row's `set`.

| Row | request `set` | status | generation_settings result | response sha256 |
|---|---|---|---|---|
| base (field omitted) | — | 200 | logit_bias `[]`, ignore_eos `false` | b1f9f6e165d3a3e987bcd2a26ae1d448abb579d1e6525b5e741e1f7daacdf67d |
| F28-31 | `{"logit_bias": {"12": 5}}` | 200 | logit_bias `[{"bias": 5.0, "token": 12}]` | 18940bf92be1b8c717b1b905482647eb4870c74cfd6b7f1aa5eeaa19d1087e74 |
| F28-32 | `{"ignore_eos": true}` | 200 | ignore_eos `true`, logit_bias `[{"bias": null, "token": 2}]` | b3e8d6a2d1765a0ed490ec442319404c6346e7d06c6a8cbbb2d933aca3af251f |

Both matches the registered `outcome` values and the L1 receipt `effective` values (F28-31: `[{"bias":5.0,"token":12}]`; F28-32: `[{"bias":null,"token":2}]`). (Response body sha256 differs run-to-run due to random sampling/timings; the contract is status+effective and it matches.)

## Source verdict (pinned snapshot server-schema.cpp @704366d, sha256 1f9d7b73…4050)

- F28-31 / S170 / L382: `add((new field_json("logit_bias"))` declares the field; handler L384-421. Object branch L407-420: `strtol` key, in-vocab filter L414 `if (tok >= 0 && tok < n_vocab)` — this exactly explains the observed outcome (kept token 12, bias 5.0). Probes on the live server confirm the filter: `{"999999":5}` and `{"-5":5}` → logit_bias `[]`; string key `{"cat":5}` → tokenized (tokens 280/294 both bias 5.0). Source fully explains the observation.
- F28-32 / S171 / L423: `add((new field_bool("ignore_eos", params.sampling.ignore_eos))` declares the field; handler L425-433 sets `ignore_eos` and appends `ctx.logit_bias_eog` to logit_bias. EOG population: common/common.cpp:1347 (704366d) pushes `{i, -INFINITY}` for every EOG token; this model has exactly one EOG token (id 2), so the appended entry is `{2, -INFINITY}`, serialized as `{"bias": null, "token": 2}` (JSON non-finite float → null; [INFERENCE], code level: -INFINITY, JSON level: null). Source fully explains the observed outcome.

## Prose verdict (SKILL.md meaning cells)

- F28-31: "Sending logit_bias as a JSON object returns 200 but generation_settings.logit_bias is normalized to an array of {"bias", "token"} objects, keeping only tokens in [0, n_vocab), so a client must read back the array form and may not assume an out-of-vocabulary token was applied." — all statements true and supported by live measurement + source; scoped to this build/model (table contract). No correction needed.
- F28-32: "Setting ignore_eos true returns 200 with generation_settings.ignore_eos true and, because the handler appends the precomputed EOG biases, injects token 2 into generation_settings.logit_bias with a null (minus-infinity) bias that the client never sent." — all statements true and supported (ignore_eos true verified live; token-2 injection verified live; handler append verified in source). "token 2" is fixture-specific (single EOG token of stories260K) and correct here. No correction needed.

## SOURCES / Gate verdict

- URLs: raw fetch of `tools/server/server-schema.cpp@704366d76` sha256 = `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` = pinned snapshot; byte-identical to the lane snapshot (`diff -q` clean). Fragments #L382 / #L423 point at the declaring lines.
- Gate quotes (round-28.md): S170 quote (lines 382-383 whitespace-joined, 25 words) and S171 quote (lines 423-424, 10 words) both occur verbatim in the whitespace-normalised snapshot (programmatic check passed).
- SOURCES.md S170/S171 rows: name `server-schema.cpp`, cited line (382/423), commit 704366d, handler lines 414/429 (both within the handler ranges), raw sha256 1f9d7b73… — all consistent.

## Counted verdict (final/c1-e49b4cf7-receipt.json)

Both F28-31 and F28-32 are in `counted_ids` (26/34) with `why: []`; the verdict is right: live status 200, effective matches the row value, differs from the field-omitted base (`[]`), differs from the request value, and is not a generic conversion under A1 (bool/dict request values have no conversions).

## Residual risk / verification gaps

1. `bias: null` ⇔ -INFINITY is inferred (common.cpp pushes -INFINITY; JSON shows null); not directly visible in the schema snapshot.
2. "token 2 = the only EOG token" is fixture-specific; verified live (exactly one appended entry) and consistent with the model's EOS=2.
3. Response body sha256 instability is expected (timings/content) and not a contract violation.
4. Full-counter run not performed (leaf seat; item does not authorize it) — per-row equivalence established by same-request re-measurement and source verification.
