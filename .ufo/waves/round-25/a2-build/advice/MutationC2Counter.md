FALSE COUNTS FOUND: mismatched KV log values count; 27 of 29 counter mutants were killed, two survived, and every mutated copy was restored exactly.

## Scope and observed execution

Axes: false acceptance, invalid-receipt rejection, mutation sensitivity, exact restoration, and fixture isolation.

Only synthetic receipts were used. No llama-server child, consumer probe, other model runtime, Git operation, production edit, or tool installation was performed. These are counter tests, not live capacity evidence. The uniform numeric values in the positive synthetic fixture are deliberately not assertions about any registered configuration.

Command, run from the lane:

```text
python3 .ufo/waves/round-25/a2-build/out/MutationC2Counter/probe.py
```

Exit 0, stdout:

```json
{
  "receipts": 45,
  "mutants": 29,
  "verdicts": {
    "killed": 27,
    "survived": 2,
    "inconclusive": 0
  },
  "source_sha256": "e8553c5b44a1b052eab06c9e5e40d03e42e21b399709fc5114ed679a0d920f6c",
  "restorations_exact": true
}
```

The detector is the real counter run as `python3 <counter-copy> <receipt.json>`, with a five-second timeout per invocation. Four independent worker threads execute copies; no copy is shared between mutants. Each mutant gets exactly the same two receipts on pristine, mutated, and restored bytes: `valid_all_14` and its named challenge receipt. The positive control stayed `registered 14 observed 14 bound True missing []`, exit 0, in all three phases for all mutants. The baseline challenge outputs and restored challenge outputs matched exactly and all exited 0. A killed mutant is an observed output/exit-code difference, not necessarily a changed observed count.

Full raw stdout, stderr, exit codes, mutation substitutions, and all hashes: `.ufo/waves/round-25/a2-build/out/MutationC2Counter/results.json`. No baseline failure was treated as a kill.

## Named false counts and limitations

1. **`kv_pool_suffix_collision.json`: definite false count.** K1 declares `kv_pool_n_ctx: 2048`; its only log is `llama_context: n_ctx = 12048`. The unmodified counter prints `registered 14 observed 14 bound True missing []`, exit 0. Amendment 2 requires the integer to match the log value; 2048 does not equal 12048. The counter at `.ufo/waves/round-25/count-c2.py:55-56` checks a string suffix, not an integer token.
2. **`kv_pool_non_numeric_log.json`: definite false count.** The only K1 log is `llama_context: n_ctx = nonsense2048`; the same full 14/True output occurs, exit 0. It contains no integer-valued `n_ctx` assignment equal to 2048, but passes the suffix test.
3. **`wrong_server_build_prefix_collision.json`: semantic binding weakness.** `server_version: "build 117550"` prints `registered 14 observed 14 bound True missing []`, exit 0. Source line 95 uses substring membership. This follows amendment 2's literal wording, “contains `build 11755`”, but does not identify build 11755 uniquely. It is a false fixture binding, not an observed-count change. Ordinary `build 11754` correctly produces `bound False`.
4. **`failed_start_truthy_complete_fields.json`: status flags are ignored.** All cells have `observed: "false"` and `started: "false"`, but retain complete synthetic evidence fields. Output is 14/True. With only those truthy flags and no evidence fields, the output is 0/True. Source lines 43-70 and 91 do not consult these flags. The strict registered structural predicate does not explicitly require an `observed` or `started` boolean; therefore this is a status/provenance limitation, not independently a violation of an explicit boolean-flag requirement. Strings in actual integer evidence fields are rejected.
5. **`float_prompt_tokens.json` and `float_n_predict.json`: equality, not integer type.** Values `1000.0` and `600.0` count, respectively. Source lines 67-68 compare numeric equality. Booleans are rejected for these two values because they do not equal 1000 or 600; integer HTTP status explicitly rejects booleans. Amendment 2 expressly types HTTP status; whether the two token fields must also have integer JSON types is not explicit. No stronger contract is silently imposed here.

Duplicate IDs exclude the duplicated registered cell entirely. Extra unknown cells do not increase the numerator. Wrong build/SHA deliberately leave observed=14 but print bound=False: this is the documented separate binding result, not a false observed count (counter lines 8-9, 93-98). A caller must require both the target observed count and bound=True; exit 0 alone is not admission.

## Synthetic receipts → unmodified counter output

Every receipt below is under `.ufo/waves/round-25/a2-build/out/MutationC2Counter/receipts/`; append `.json` to the first column. Every invocation exited **0**, with empty stderr. Challenge fixtures differ from `valid_all_14` only as encoded in `probe.py`; most alter K1, while request fixtures alter L1.

| Receipt | Exact stdout, without trailing newline |
|---|---|
| valid_all_14 | `registered 14 observed 14 bound True missing []` |
| failed_start_truthy_observed_only | `registered 14 observed 0 bound True missing ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'X1', 'X2', 'X3', 'L1', 'L2', 'L3']` |
| failed_start_truthy_complete_fields | `registered 14 observed 14 bound True missing []` |
| truthy_string_props_n_ctx | `registered 14 observed 13 bound True missing ['K1']` |
| missing_props_n_ctx | `registered 14 observed 13 bound True missing ['K1']` |
| boolean_props_n_ctx | `registered 14 observed 13 bound True missing ['K1']` |
| truthy_string_total_slots | `registered 14 observed 13 bound True missing ['K1']` |
| missing_total_slots | `registered 14 observed 13 bound True missing ['K1']` |
| boolean_total_slots | `registered 14 observed 13 bound True missing ['K1']` |
| truthy_string_models_n_ctx_train | `registered 14 observed 13 bound True missing ['K1']` |
| missing_models_n_ctx_train | `registered 14 observed 13 bound True missing ['K1']` |
| boolean_models_n_ctx_train | `registered 14 observed 13 bound True missing ['K1']` |
| truthy_string_kv_pool_n_ctx | `registered 14 observed 13 bound True missing ['K1']` |
| missing_kv_pool_n_ctx | `registered 14 observed 13 bound True missing ['K1']` |
| boolean_kv_pool_n_ctx | `registered 14 observed 13 bound True missing ['K1']` |
| boolean_slots_element | `registered 14 observed 13 bound True missing ['K1']` |
| string_slots_element | `registered 14 observed 13 bound True missing ['K1']` |
| empty_slots | `registered 14 observed 13 bound True missing ['K1']` |
| wrong_args | `registered 14 observed 13 bound True missing ['K1']` |
| duplicate_K1 | `registered 14 observed 13 bound True missing ['K1']` |
| extra_cell | `registered 14 observed 14 bound True missing []` |
| wrong_server_build | `registered 14 observed 14 bound False missing []` |
| wrong_server_build_prefix_collision | `registered 14 observed 14 bound True missing []` |
| missing_server_version | `registered 14 observed 14 bound False missing []` |
| wrong_model_sha | `registered 14 observed 14 bound False missing []` |
| kv_pool_no_matching_log | `registered 14 observed 13 bound True missing ['K1']` |
| kv_pool_suffix_collision | `registered 14 observed 14 bound True missing []` |
| kv_pool_non_numeric_log | `registered 14 observed 14 bound True missing []` |
| kv_pool_unrelated_suffix | `registered 14 observed 13 bound True missing ['K1']` |
| empty_logs | `registered 14 observed 13 bound True missing ['K1']` |
| empty_log_element | `registered 14 observed 13 bound True missing ['K1']` |
| nonstring_log_element | `registered 14 observed 13 bound True missing ['K1']` |
| mapping_logs | `registered 14 observed 13 bound True missing ['K1']` |
| one_load_request | `registered 14 observed 13 bound True missing ['L1']` |
| mapping_requests | `registered 14 observed 13 bound True missing ['L1']` |
| wrong_request_mode | `registered 14 observed 13 bound True missing ['L1']` |
| request_not_dict | `registered 14 observed 13 bound True missing ['L1']` |
| boolean_http_status | `registered 14 observed 13 bound True missing ['L1']` |
| string_http_status | `registered 14 observed 13 bound True missing ['L1']` |
| wrong_prompt_tokens | `registered 14 observed 13 bound True missing ['L1']` |
| wrong_n_predict | `registered 14 observed 13 bound True missing ['L1']` |
| boolean_prompt_tokens | `registered 14 observed 13 bound True missing ['L1']` |
| boolean_n_predict | `registered 14 observed 13 bound True missing ['L1']` |
| float_prompt_tokens | `registered 14 observed 14 bound True missing []` |
| float_n_predict | `registered 14 observed 14 bound True missing []` |

## Counter mutants → expected detector and observed result

Each mutant removes or weakens one guard in its own isolated copy. Exact old/new strings are in `results.json` and `probe.py`. A positive-control failure or nonzero baseline would be inconclusive; none occurred. The expected detector is a difference from the challenge receipt's baseline output in the preceding table. `FULL` below means the exact stdout `registered 14 observed 14 bound True missing []`, exit 0. Error rows had empty stdout, exit 1; their full tracebacks are preserved in `results.json`.

| Mutant / removed check | Challenge receipt | Mutated result | Verdict |
|---|---|---|---|
| M01_boolean_ints / exclude bool from int | boolean_props_n_ctx | FULL | killed: count |
| M02_integer_type / require int | truthy_string_props_n_ctx | FULL | killed: count |
| M03_props_type | truthy_string_props_n_ctx | FULL | killed: count |
| M04_slot_count_type | truthy_string_total_slots | FULL | killed: count |
| M05_training_type | truthy_string_models_n_ctx_train | FULL | killed: count |
| M06_pool_type | truthy_string_kv_pool_n_ctx | FULL | killed: count |
| M07_slots_guard | empty_slots | FULL | killed: count |
| M08_slots_nonempty | empty_slots | FULL | killed: count |
| M09_slots_elements | boolean_slots_element | FULL | killed: count |
| M10_log_list | mapping_logs | FULL | killed: count |
| M11_log_elements | empty_log_element | FULL | killed: count |
| M12_pool_log_match | kv_pool_no_matching_log | FULL | killed: count |
| M13_pool_log_label | kv_pool_unrelated_suffix | FULL | killed: count |
| M14_pool_log_value | kv_pool_no_matching_log | FULL | killed: count |
| M15_load_evidence | one_load_request | FULL | killed: count |
| M16_request_mode | wrong_request_mode | FULL | killed: count |
| M17_request_cardinality | one_load_request | FULL | killed: count |
| M18_status_type | boolean_http_status | FULL | killed: count |
| M19_prompt_count | wrong_prompt_tokens | FULL | killed: count |
| M20_prediction_count | wrong_n_predict | FULL | killed: count |
| M21_duplicates | duplicate_K1 | `registered 14 observed 15 bound True missing []`, exit 0 | killed: count |
| M22_registered_id | extra_cell | `KeyError: 'EXTRA'`, exit 1 | killed: exception, not a count change |
| M23_registered_args | wrong_args | FULL | killed: count |
| M24_build_binding | wrong_server_build | FULL | killed: binding only |
| M25_model_binding | wrong_model_sha | FULL | killed: binding only |
| M26_version_type | missing_server_version | `TypeError: argument of type 'NoneType' is not a container or iterable`, exit 1 | killed: exception, not a count change |
| M27_log_nonempty | empty_logs | `registered 14 observed 13 bound True missing ['K1']`, exit 0 | survived |
| M28_slots_list | string_slots_element | `registered 14 observed 13 bound True missing ['K1']`, exit 0 | survived |
| M29_request_dict | request_not_dict | `AttributeError: 'NoneType' object has no attribute 'get'`, exit 1 | killed: exception, not a count change |

Totals: **22 changed counts, two changed binding, three raised exceptions, two survived.** It would be false to assert that every removed check changed the count.

The two surviving mutants are bounded coverage findings, not permission to alter the contract. [INFERENCE] M27's nonempty-log guard is overlapped by the later `any(...)` match, which rejects an empty list. M28's selected malformed-element receipt is still a list, so it exercises the integer-element requirement but does not distinguish the explicit list-type guard. This probe establishes no general equivalence for M28 and does not claim every malformed JSON shape is covered.

## Restoration and written files

Source before and after, every mutable copy before mutation, and every mutable copy after restoration all had exactly:

```text
e8553c5b44a1b052eab06c9e5e40d03e42e21b399709fc5114ed679a0d920f6c
```

All 29 **mutated** hashes differ from that value and are individually recorded with before/restored hashes under `mutants[]` in `results.json`. Mutation writes are enclosed by `finally: path.write_bytes(ORIGINAL)`; restored detectors were actually run, not inferred from the hashes. The lane source was never written. Only Python's existing standard library was needed; no install/update to record.

Files written, all paths relative to the lane unless explicitly absolute:

- This report: `.ufo/waves/round-25/a2-build/advice/MutationC2Counter.md`.
- `.ufo/waves/round-25/a2-build/out/MutationC2Counter/probe.py`.
- `.ufo/waves/round-25/a2-build/out/MutationC2Counter/results.json`.
- `.ufo/waves/round-25/a2-build/out/MutationC2Counter/count-c2-pristine.py`.
- All 45 receipt filenames are individually named in the first table, under the `receipts/` directory stated there.
- All 29 restored counter-copy filenames are individually named in the mutant table: under `.ufo/waves/round-25/a2-build/out/MutationC2Counter/mutants/`, append `.py` to the mutant identifier before ` /`.
- A setup-only copy at `/fast/scratch/hyaku/kama-r25a2/MutationC2Counter/count-c2-pristine.py` was written, hashed equal to the source, then deleted. Its empty setup directories were removed with `rmdir`, exit 0. No retained artifact is outside the requested output tree and report.

No production repair or integration was performed. No external implementation source was relied on: all findings concern the local registered counter and preregistration bytes opened this round.

Report: .ufo/waves/round-25/a2-build/advice/MutationC2Counter.md
