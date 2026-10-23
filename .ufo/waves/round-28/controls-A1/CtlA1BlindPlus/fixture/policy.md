# CtlA1BlindPlus policy (fixed before the single scoring run)

Control: one source-blind guess per field for the A1 counter
(sha256 a38faefeeb48be9fd3590b5077030ed6b7cef08dcaf1ca0540b464bd222749a5,
lane commit 75b78bb4900aae1edcdb6b229bb8c572c20fcbce).

## Information sources actually used

1. Public server README at the pinned commit 704366d
   (/fast/scratch/hyaku/kama-r28/llama.cpp/tools/server/README.md): the /completion
   option table, the documented defaults, the /props `default_generation_settings.params`
   example and the /slots `params` example. These name the keys that exist in
   `generation_settings` and give each field's default.
2. Declaration names and line numbers only from the pinned
   `.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp` snapshot:
   a strict extractor prints `line<TAB>first-string-literal` for every line
   containing `new field_`; no other text of that file was read, printed or used.
3. General programming knowledge: C-style JSON conversion (truncation toward zero,
   unsigned wrap), clamp-to-bound conventions for probabilities and enums,
   list wrapping for string-or-array parameters, and hard-bound rejection messages.
4. The wave dispatch record controls/HOLDS.md (not a receipt.json): its published
   margin (strongest A0 shortcut 14 of 38) told me the A0 shortcut sat on generic
   conversions, which A1 clause (e) now refuses. No receipt.json was opened.

Not used: any file under .ufo/waves/round-28/w1/, any controls/*/receipt.json,
any before/*.json, any live llama-server run, any semantics of server-schema.cpp.

## Shape of the attack

The A1 counter refuses, for `effective` rows, the sent value (identity), the
field's value when omitted (server default) and every generic conversion of the
sent value (float32 rounding, saturation, truncation, wrap, truthiness). So a
blind row can only count when the server stores a *semantic* function of the
sent value. Two such functions are reachable from the README alone:

- clamp to a declared bound (probability 0..1, enum 0..2, sentinel -1, floor 0),
- wrap a scalar into a one-element list for array-typed options,
- reject with the field's hard bounds, which then must be guessed exactly.

The policy therefore uses, per field, the only class that can win for that field:

| class | sent | declared outcome | why this can be non-generic |
|---|---|---|---|
| probability clamp | 2.5 | effective 1.0 | int(2.5)=2, so a clamp to 1.0 is not truncation |
| low clamp to 0 | -1.5 | effective 0.0 | int(-1.5)=-1, wrap not 0 |
| enum clamp | 5 | effective 2 | 2 is not bool/float32/truncation/wrap of 5 |
| sentinel clamp | -5 | effective -1 or 0 | -1/0 are not conversions of -5 |
| list wrap | string | effective [string] | a list is never a conversion of a number; string sent disables number generics |
| case normalise | "AUTO" | effective "auto" | exact string inequality |
| hard reject | out of range | 400 with guessed bounds | clause (e) does not apply to reject rows |

Fields whose default *is* the clamp target are not winnable by clamping
(clause e refuses the default), so they were given the reject guess instead:
min_keep 0, n_indent 0, n_probs 0, t_max_prompt_ms 0, t_max_predict_ms 0,
reasoning_budget_tokens 0, n_cmpl 1, sse_ping_interval -1, seed 4294967295.

Fields with no constructible non-generic outcome under A1 (booleans, opaque
objects, nested `speculative.*` names whose flat JSON key the request cannot
address, grammar/logit_bias payloads, stream options) are omitted: every blind
guess for them lands on identity, default or truthiness.

Bounds guesses are the canonical pairs a blind writer would pick:
0..2147483647 and -1..2147483647 for int32 counts, 0..4294967295 for the uint32
seed, 1..2147483647 for a completion count, and 0..FLT_MAX / -1..FLT_MAX for
float fields whose documented default equals the zero floor (the counter's
1e-6 relative tolerance absorbs printf rounding of 3.4028234663852886e38).

## Fixed table (38 rows, one per field)

| # | field | sent | outcome |
|---|---|---|---|
| 1 | top_p | 2.5 | effective top_p = 1.0 |
| 2 | min_p | 2.5 | effective min_p = 1.0 |
| 3 | xtc_probability | 2.5 | effective xtc_probability = 1.0 |
| 4 | typical_p | -1.5 | effective typical_p = 0.0 |
| 5 | temperature | -1.5 | effective temperature = 0.0 |
| 6 | dynatemp_exponent | -1.5 | effective dynatemp_exponent = 0.0 |
| 7 | mirostat_tau | -1.5 | effective mirostat_tau = 0.0 |
| 8 | mirostat_eta | -1.5 | effective mirostat_eta = 0.0 |
| 9 | repeat_penalty | -1.5 | effective repeat_penalty = 0.0 |
| 10 | dry_base | -1.5 | effective dry_base = 1.0 |
| 11 | adaptive_target | 2.5 | effective adaptive_target = 1.0 |
| 12 | adaptive_decay | 2.5 | effective adaptive_decay = 1.0 |
| 13 | mirostat | 5 | effective mirostat = 2 |
| 14 | top_k | -5 | effective top_k = 0 |
| 15 | n_keep | -5 | effective n_keep = -1 |
| 16 | n_discard | -5 | effective n_discard = -1 |
| 17 | n_predict | -5 | effective n_predict = -1 |
| 18 | repeat_last_n | -5 | effective repeat_last_n = -1 |
| 19 | dry_allowed_length | -5 | effective dry_allowed_length = 0 |
| 20 | dry_penalty_last_n | -5 | effective dry_penalty_last_n = -1 |
| 21 | min_keep | -5 | reject 400, bounds 0 to 2147483647 |
| 22 | n_indent | -5 | reject 400, bounds 0 to 2147483647 |
| 23 | n_probs | -5 | reject 400, bounds 0 to 2147483647 |
| 24 | t_max_prompt_ms | -5 | reject 400, bounds 0 to 2147483647 |
| 25 | t_max_predict_ms | -5 | reject 400, bounds 0 to 2147483647 |
| 26 | reasoning_budget_tokens | -5 | reject 400, bounds 0 to 2147483647 |
| 27 | seed | 4294967296 | reject 400, bounds 0 to 4294967295 |
| 28 | n_cmpl | 0 | reject 400, bounds 1 to 2147483647 |
| 29 | sse_ping_interval | -5 | reject 400, bounds -1 to 2147483647 |
| 30 | stop | "zqx" | effective stop = ["zqx"] |
| 31 | dry_sequence_breakers | "zqx" | effective dry_sequence_breakers = ["zqx"] |
| 32 | samplers | "top_k" | effective samplers = ["top_k"] |
| 33 | reasoning_format | "AUTO" | effective reasoning_format = "auto" |
| 34 | dynatemp_range | -1.5 | reject 400, bounds 0.0 to 3.4028234663852886e+38 |
| 35 | frequency_penalty | -1.5 | reject 400, bounds 0.0 to 3.4028234663852886e+38 |
| 36 | presence_penalty | -1.5 | reject 400, bounds 0.0 to 3.4028234663852886e+38 |
| 37 | dry_multiplier | -1.5 | reject 400, bounds 0.0 to 3.4028234663852886e+38 |
| 38 | top_n_sigma | -5.0 | reject 400, bounds -1.0 to 3.4028234663852886e+38 |

## Freeze

This table is the policy. It was written before the counter ran and was not
changed after the run. No second, feedback-driven attempt was made; the scored
run is the only run used for the verdict. Rows are ordered so that the cheap
sampler rows go first and the row that can force a long generation (n_predict)
and the type-sensitive rows come later; order is not a feedback loop.
