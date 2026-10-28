> **L1 preface, not part of the appended text.** `corpus/knowledge/completion-request-plane.md` already carries an *uncommitted* section on this topic (`## Round-63 strict response grading, schema `kama-completion-live/v2` (S527, S528)`). Replace that section with the block below; do not append a second copy. Placeholder map: `SNEW-task` = the `server-task.cpp` row (S527 in the working-tree SOURCES draft), `SNEW-common` = the `server-common.cpp` row (S528). The L1 assigns the final ids.

---

## Round-63 strict response grading (v2)

verified-at: 2026-10-28 at tip 03a6a1d850902a66a13dfad33f89cf3a8b759a09 — one live run of that tip's `tools/kama-completion-live.py` on the pinned fixture, no hold window (`REQUEST_OK`, 22 evaluated checks passed, nonce `wr02-r63-kn-1`; receipt `.ufo/waves/round-63/w1/out/WR02KnowledgeDraft/live-tip-receipt.json`). Failure counts come from the round-63 receipt tree. recheck: on any change to `tools/kama-completion-live.py` or to the `llama-server` / model pin.

Round 62 graded the envelope, `finish_reason`, model id, fingerprint, usage, timings, determinism and the bad-request answer. Round 63 adds six check names (`completion_headers`, `completion_untruncated`, `completion_choice_shape`, `completion_id_created`, `completion_prompt_tokens`, `completion_request_bound`) and strengthens `completion_usage` (positive counts, `cached_tokens` bound) and `completion_timings` (`cache_n` / `prompt_n` bounds). `completion_finish_reason` is unchanged. Every check from `completion_headers` through `completion_deterministic` runs only when `completion_envelope` passed (`if ok_env:` in the tool), so an envelope failure reports one check and leaves the rest unevaluated.

Ground per row: **source** = pinned llama.cpp b11755 bytes (`SNEW-task`: `server-task.cpp`, sha256 4c3f413b…; `SNEW-common`: `server-common.cpp`, sha256 b4f4aae7…; kept under `.ufo/waves/round-63/source/`); **observed** = live receipt only; **own** = the tool's own bound, not a server property. Named failure examples are fixture runs (canned, mutated or hostile-argument), not defects of b11755.

Located quotes (each re-read at the cited lines; whitespace normalised):

- **Q1** `SNEW-task` 359–362: `{"completion_tokens", n_decoded},` `{"prompt_tokens", n_prompt_tokens},` `{"total_tokens", n_decoded + n_prompt_tokens},` `{"cached_tokens", n_prompt_tokens_cache}`
- **Q2** `SNEW-task` 367–369: `std::time_t t = std::time(0);` / `json logprobs = json(nullptr); // OAI default to null` / `if (!stream && probs_output.size() > 0) {`
- **Q3** `SNEW-task` 374–375: `json finish_reason = "length";` / `if (stop == STOP_TYPE_WORD || stop == STOP_TYPE_EOS) {`
- **Q4** `SNEW-task` 382, 387, 390, 392: `{"index", index},` `{"created", t},` `{"object", "text_completion"},` `{"id", oaicompat_cmpl_id}`
- **Q5** `SNEW-task` 399–400: `if (stats.is_set()) {` / `res["timings"] = stats.to_json();`
- **Q6** `SNEW-common` 141, 143, 148, 149: `{"cache_n", n_prompt_cached},` `{"prompt_n", n_prompt_processed},` `{"predicted_n", n_gen},` `{"predicted_ms", t_gen_ms()},`
- **Q7** `SNEW-common` 95–97 and 128–132: `case ERROR_TYPE_INVALID_REQUEST:` / `type_str = "invalid_request_error";` / `code = 400;` / `return json { {"code", code}, {"message", message}, {"type", type_str}, };`
- **Q8** `SNEW-common` 181–182: `std::string gen_chatcmplid() {` / `return "chatcmpl-" + random_string();` (the generator; the completion route's id assignment is not in the retained bytes)

| Check | Asserts | Ground | Failure signature |
|---|---|---|---|
| `completion_envelope` | HTTP 200; `object` is `text_completion`; `choices[0].text` is a string | source: `object` literal (Q4, 390) and the one-element `choices` array (`SNEW-task` 379–386); HTTP status observed | any status other than 200, another `object`, or no `choices[0].text` string. 8 receipts, e.g. RV01 `trunc_cl` (body cut at 120 of 900 bytes, unparseable); every later body check is then not evaluated |
| `completion_headers` | `Content-Type` media type is `application/json` (parameters ignored) | observation-only: the HTTP layer is not retained; live `application/json; charset=utf-8` | a `text/plain` or other type, or no header. 0 failures in 133 evaluations |
| `completion_untruncated` | body read whole (cap 65,536 bytes, own); when `Content-Length` is sent it equals the captured byte count | own; framing is not in the retained source | body at the cap with a larger `Content-Length`: RV01 `pad` (65,536 captured, `Content-Length` 70,448). A short body with a larger length fails `completion_envelope` first (`trunc_cl`), so this check is not evaluated there |
| `completion_choice_shape` | exactly one choice; `index` integer 0 (not bool); `logprobs` null; `text` non-empty | source: one-element array (`SNEW-task` 379–386); `logprobs` null unless a non-stream request produced probabilities (Q2, 368–369). `index` 0 and non-empty text are observation-only (`index` is set outside the retained files; text is model-dependent). Live: index 0, `logprobs` null, text `' ground. She liked'` | two choices, `index` 1 or a bool, non-null `logprobs`, or empty text. 4 receipts, e.g. MT03 I1 |
| `completion_finish_reason` | `choices[0].finish_reason` is `length` or `stop` | source: Q3 (374–375); the emitter produces only these two. Unchanged from round 62 | any other string. 0 failures in 133; live `length` at `n_predict` 8 |
| `completion_model_id` | `model` equals `--alias`, never the file path | observation-only: `oaicompat_model` is emitted at `SNEW-task` 388 but assigned outside the retained bytes | `model` empty or the file path. 1 receipt: EX05 `c_y5_alias_empty`, which also fails `models_alias_id` and `props_alias` |
| `completion_fingerprint` | `system_fingerprint` matches `^b\d+-[0-9a-f]{9,40}$` | source: emitted from `llama_build_info()` (`SNEW-task` 389); the pattern is own; live `b11755-704366d76` | a non-matching string. **Open defect:** `$` accepts one trailing newline, so `b11755-704366d76\n` passes (RV01 `fp_newline`, `REQUEST_OK`). Needs `fullmatch` or `\Z`. 0 failures in 133 |
| `completion_id_created` | `id` is a non-empty string; `created` is an integer above 10^9 | source: `created` = `std::time(0)` (Q2, 367); `id` = `oaicompat_cmpl_id` (Q4, 392); the generator (Q8) yields `chatcmpl-` plus 32 characters. The 10^9 floor is own | empty or non-string `id`, bool or non-integer `created`, or `created` ≤ 10^9. 0 failures in 133; live id 41 characters, `created` 1793227992 |
| `completion_usage` | three integer counts; `completion_tokens` and `prompt_tokens` ≥ 1; `total = completion + prompt`; `prompt_tokens_details.cached_tokens` integer in [0, prompt_tokens] | source: Q1 (359–362); the sum holds by construction (361); the ≥ 1 floor and the cached bound are own. A missing or empty `usage` fails normally. A truthy non-object `usage` does not fail: `u.get` raises and the verdict is `SETUP_ERROR` (`AttributeError: 'str' object has no attribute 'get'`, RV01 `usage_str`). 0 FAIL in 132 evaluations |
| `completion_timings` | `timings` present; `predicted_n` equals `usage.completion_tokens`; `cache_n` and `prompt_n` non-negative integers; `predicted_ms` finite and non-negative | source: field names (Q6, `SNEW-common` 141–149); presence only when `stats.is_set()` (Q5). The equality with usage and the value bounds are observed/own: the retained bytes do not link `n_gen` to `n_decoded` | missing `timings` or field, a negative, bool or non-finite number, or `predicted_n` ≠ `completion_tokens`. 8 fixture receipts (MT05 V1–V8) |
| `completion_prompt_tokens` | `usage.prompt_tokens` equals the length of the server's `/tokenize` answer (`add_special` true) for the prompt | observation-only: live `/tokenize` returned 8 ids for `The cat sat on the` (first id BOS 1) and `prompt_tokens` was 8. The special-token rule is not in retained source; holds for this tokenizer only | a count that differs from `/tokenize`: RV01 `tokenize_mismatch`; 4 receipts in all |
| `completion_request_bound` | the captured request bytes hash to `request_sha256` and carry the prompt the tool sent | own: the tool sends and hashes the bytes itself | an altered prompt in the bytes or a mismatched hash: 3 receipts, e.g. MT07 M3 |
| `completion_deterministic` | at temperature 0, a byte-identical second request returns the same `choices[0].text`; skipped (reported `None`, not passed) at other temperatures | observation-only: determinism at a fixed seed is not in retained source; live: passed | a different second text: 3 receipts, e.g. MT03 I3 |
| `bad_request_graded` | a request without `prompt` answers 400 or 500 with an object under `error` | source: inner object `{code, message, type}` (Q7, 128–132) and `invalid_request_error` → 400 (Q7, 95–97). The `error` wrapper is added by a caller not in the retained bytes: observed. Message text not graded | status outside {400, 500}, or no `error` object. 0 failures in 139; live: 400 with `{"error":{"code":400,"message":"[json.exception.out_of_range.403] key 'prompt' not found","type":"invalid_request_error"}}` |

## Not asserted

Token magnitudes; timing values; the `id` beyond its prefix and length; the text itself beyond non-empty for the fixed request; streaming. Invalid UTF-8 is not graded: the body is decoded with `errors='replace'`, and RV01 `nonutf8` (a replacement character inside `text`) is `REQUEST_OK`.

## Open grader defects at tip 03a6a1d8

- `completion_fingerprint` accepts a trailing newline (row above).
- `completion_usage` turns a truthy non-object `usage` into `SETUP_ERROR`, not `FAIL`.
- Invalid UTF-8 in the body passes (`nonutf8`).
