VERDICT: does-not-meet
counted 0 registered 52 exit 0
A0 counted 20 registered 52 exit 0
counter sha256 (A1) a38faefeeb48be9fd3590b5077030ed6b7cef08dcaf1ca0540b464bd222749a5
counter sha256 (A0) e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c
target 18 / lane commit 75b78bb4900aae1edcdb6b229bb8c572c20fcbce

# CtlA1Conversion — one generic conversion per typed request field

## What was tested

The shortcut that amendment A1 exists to stop: with no per-field knowledge, send one
type-level extreme to every request field and predict the conversion the declared C++
type applies. 52 registry rows, one per field declared by `new field_num` or
`new field_bool` in the sha256-pinned 704366d `server-schema.cpp` snapshot, excluding
`n_cache_reuse` and `xtc_threshold` as assigned:

- 18 `float` fields: send `1e+39`, predict `3.4028234663852886e+38` (float32 saturation);
- 20 `int32` fields and 1 `int64` field: send `2.5`, predict `2` (truncation toward zero);
- `seed` (`uint32_t` per the declaration comment): send `4294967296`, predict `0` (uint32 wrap);
- 12 `bool` fields: send `1`, predict `true`.

Only declaration names, declaring lines and declared parameter types entered the fixture;
no bound, default, handler or observed outcome was encoded. The response key was guessed
as the field name for every row (for the nested `include_usage` this is the flat key).

## Exact commands

cwd `/fast/scratch/hyaku/kama-r28/ctlA1/CtlA1Conversion`:

```
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin tree
git -C tree checkout -q 75b78bb4900aae1edcdb6b229bb8c572c20fcbce
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show d8bf1804:.ufo/waves/round-28/count-c1.py > /tmp/a0-counter-kama-r28.py
cp /tmp/a0-counter-kama-r28.py tree/.ufo/waves/round-28/count-c1-A0.py
/usr/bin/python3 build_fixture.py
timeout 900 /usr/bin/python3 tree/.ufo/waves/round-28/count-c1.py --lane tree --repo tree --out receipt.json
timeout 900 /usr/bin/python3 tree/.ufo/waves/round-28/count-c1-A0.py --lane tree --repo tree --out receipt-A0.json
```

Counter integrity before scoring: `sha256sum tree/.ufo/waves/round-28/count-c1.py` =
a38faefeeb48be9fd3590b5077030ed6b7cef08dcaf1ca0540b464bd222749a5;
`sha256sum tree/.ufo/waves/round-28/count-c1-A0.py` =
e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c (the A0 counter as
published at d8bf1804, unmodified, copied under a different name; it reads the same
`registry/request-field-outcomes-r28.json`). A1 was scored first, A0 second, one counter at
a time; no llama-server was started by hand and `ss -ltnp` showed ports 47600-47619 free
after both runs.

## Result

- A1 counter (unchanged): **counted 0 / 52**, target 18 not met, exit 0.
- A0 counter (same fixture, published predicate): **counted 20 / 52**, target 18 **met**, exit 0.

The shortcut therefore does exactly what amendment A1 was written to prevent: under A0 it
would have met the target with no field knowledge at all (20 >= 18). Under A1 every row
that reproduced its predicted conversion was refused by clause (e).

## Clause accounting

Clauses (a), (b) and (c): 0 refusals. A dry run of the counter's own `static_checks` over all
52 rows before scoring returned no failures (`skill rows 52`, table cell, declaring line,
new S9### source row, no duplicate line or field); the scored receipts agree.

Clause (d) refused 31 rows in both runs (A1 not-counted 52 = 31 d + 21 e; A0
not-counted 32 = 31 d + 1 `e:default`). Subgroups, all `d:not-shown`:

- 11 (F28-00, F28-01, F28-02, F28-04, F28-05, F28-06, F28-40, F28-41, F28-48, F28-49, F28-51) — bool field sent numeric `1`; HTTP 400. [INFERENCE] the boolean getter
  rejects a JSON number (type error), so no `true` is ever stored.
- 1 (F28-03) — `include_usage` is declared only as a subfield of `stream_options`;
  the flat key is ignored and the response has no such key.
- 4 (F28-16, F28-17, F28-19, F28-35) — float field sent `1e+39` but soft-limited below FLT_MAX; the stored
  value is `1.0`, not the predicted float maximum.
- 2 (F28-21, F28-29) — float field stored infinity (no upper limit, or a handler that keeps
  the value); infinity serialises as JSON null, so the predicted FLT_MAX is not shown.
- 1 (F28-36) — `adaptive_decay` has hard limits; `1e+39` became infinity and was
  rejected with HTTP 400.
- 5 (F28-07, F28-09, F28-12, F28-14, F28-50) — declaration accepted the truncated value but the field has no key in
  `generation_settings` (`sse_ping_interval`, `n_indent`, `n_cmpl`, `t_max_predict_ms`,
  `reasoning_budget_tokens`).
- 7 (F28-13, F28-42, F28-43, F28-44, F28-45, F28-46, F28-47) — declaration present in the snapshot text but not live in the compiled
  schema (commented-out `t_max_prompt_ms`; the `#if 0` speculative fields); the unknown key
  is ignored.

Clause (e) refused 21 rows under A1: 21 (F28-08, F28-10, F28-11, F28-15, F28-18, F28-20, F28-22, F28-23, F28-24, F28-25, F28-26, F28-27, F28-28, F28-30, F28-31, F28-32, F28-33, F28-34, F28-37, F28-38, F28-39). Every one of those rows reached its
predicted stored value exactly - 21 of the 21 are
`e:generic-conversion`; `F28-30` (`dry_allowed_length`, stored 2) is additionally `e:default`
because its omitted default is also 2. Under A0 the same 21 rows split 20 counted + 1
refused by `e:default`, which is the whole difference between the two scores.

## Per-row evidence

`live` is the A1 receipt's observation; the A0 receipt observed the same status/effective on
every row (both receipts in this directory). Predicted value is the row's outcome cell.

| id | field | type | sent | predicted | live | A1 clause | A0 clause |
|---|---|---|---|---|---|---|---|
| F28-00 | `verbose` | bool | 1 | true | 400 | d:not-shown | d:not-shown |
| F28-01 | `timings_per_token` | bool | 1 | true | 400 | d:not-shown | d:not-shown |
| F28-02 | `stream` | bool | 1 | true | 400 | d:not-shown | d:not-shown |
| F28-03 | `include_usage` | bool | 1 | true | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-04 | `cache_prompt` | bool | 1 | true | 400 | d:not-shown | d:not-shown |
| F28-05 | `return_tokens` | bool | 1 | true | 400 | d:not-shown | d:not-shown |
| F28-06 | `return_progress` | bool | 1 | true | 400 | d:not-shown | d:not-shown |
| F28-07 | `sse_ping_interval` | int32 | 2.5 | 2 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-08 | `n_predict` | int32 | 2.5 | 2 | 200, effective 2 | e:generic-conversion | COUNTED |
| F28-09 | `n_indent` | int32 | 2.5 | 2 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-10 | `n_keep` | int32 | 2.5 | 2 | 200, effective 2 | e:generic-conversion | COUNTED |
| F28-11 | `n_discard` | int32 | 2.5 | 2 | 200, effective 2 | e:generic-conversion | COUNTED |
| F28-12 | `n_cmpl` | int32 | 2.5 | 2 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-13 | `t_max_prompt_ms` | int32 | 2.5 | 2 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-14 | `t_max_predict_ms` | int64 | 2.5 | 2 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-15 | `top_k` | int32 | 2.5 | 2 | 200, effective 2 | e:generic-conversion | COUNTED |
| F28-16 | `top_p` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 1.0 | d:not-shown | d:not-shown |
| F28-17 | `min_p` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 1.0 | d:not-shown | d:not-shown |
| F28-18 | `top_n_sigma` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 3.4028234663852886e+38 | e:generic-conversion | COUNTED |
| F28-19 | `xtc_probability` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 1.0 | d:not-shown | d:not-shown |
| F28-20 | `typical_p` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 3.4028234663852886e+38 | e:generic-conversion | COUNTED |
| F28-21 | `temperature` | float | 1e+39 | 3.4028234663852886e+38 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-22 | `dynatemp_range` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 3.4028234663852886e+38 | e:generic-conversion | COUNTED |
| F28-23 | `dynatemp_exponent` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 3.4028234663852886e+38 | e:generic-conversion | COUNTED |
| F28-24 | `repeat_last_n` | int32 | 2.5 | 2 | 200, effective 2 | e:generic-conversion | COUNTED |
| F28-25 | `repeat_penalty` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 3.4028234663852886e+38 | e:generic-conversion | COUNTED |
| F28-26 | `frequency_penalty` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 3.4028234663852886e+38 | e:generic-conversion | COUNTED |
| F28-27 | `presence_penalty` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 3.4028234663852886e+38 | e:generic-conversion | COUNTED |
| F28-28 | `dry_multiplier` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 3.4028234663852886e+38 | e:generic-conversion | COUNTED |
| F28-29 | `dry_base` | float | 1e+39 | 3.4028234663852886e+38 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-30 | `dry_allowed_length` | int32 | 2.5 | 2 | 200, effective 2 | e:generic-conversion + e:default | e:default |
| F28-31 | `dry_penalty_last_n` | int32 | 2.5 | 2 | 200, effective 2 | e:generic-conversion | COUNTED |
| F28-32 | `mirostat` | int32 | 2.5 | 2 | 200, effective 2 | e:generic-conversion | COUNTED |
| F28-33 | `mirostat_tau` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 3.4028234663852886e+38 | e:generic-conversion | COUNTED |
| F28-34 | `mirostat_eta` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 3.4028234663852886e+38 | e:generic-conversion | COUNTED |
| F28-35 | `adaptive_target` | float | 1e+39 | 3.4028234663852886e+38 | 200, effective 1.0 | d:not-shown | d:not-shown |
| F28-36 | `adaptive_decay` | float | 1e+39 | 3.4028234663852886e+38 | 400 | d:not-shown | d:not-shown |
| F28-37 | `seed` | uint32 | 4294967296 | 0 | 200, effective 0 | e:generic-conversion | COUNTED |
| F28-38 | `n_probs` | int32 | 2.5 | 2 | 200, effective 2 | e:generic-conversion | COUNTED |
| F28-39 | `min_keep` | int32 | 2.5 | 2 | 200, effective 2 | e:generic-conversion | COUNTED |
| F28-40 | `backend_sampling` | bool | 1 | true | 400 | d:not-shown | d:not-shown |
| F28-41 | `post_sampling_probs` | bool | 1 | true | 400 | d:not-shown | d:not-shown |
| F28-42 | `speculative.n_max` | int32 | 2.5 | 2 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-43 | `speculative.n_min` | int32 | 2.5 | 2 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-44 | `speculative.p_min` | float | 1e+39 | 3.4028234663852886e+38 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-45 | `speculative.ngram_size_n` | int32 | 2.5 | 2 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-46 | `speculative.ngram_size_m` | int32 | 2.5 | 2 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-47 | `speculative.ngram_min_hits` | int32 | 2.5 | 2 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-48 | `grammar_lazy` | bool | 1 | true | 400 | d:not-shown | d:not-shown |
| F28-49 | `reasoning_control` | bool | 1 | true | 400 | d:not-shown | d:not-shown |
| F28-50 | `reasoning_budget_tokens` | int32 | 2.5 | 2 | 200, no key/value (null) | d:not-shown | d:not-shown |
| F28-51 | `ignore_eos` | bool | 1 | true | 400 | d:not-shown | d:not-shown |

## Boundaries

- The fixture uses one probe per field, so no field is probed twice (the duplicate rule
  voids all rows of a repeated field).
- Excluded fields: the registry omits `n_cache_reuse` and `xtc_threshold`; the counter does
  not enforce the exclusion list, the fixture does.
- Nothing was installed or updated for this control; no tool versions changed.
- The 31 (d) rows are misses of the shortcut, not evidence against A1's completeness: the
  class this control exercises is exactly the numeric conversion family that (e) enumerates,
  and it was refused at 21/21 live matches.
