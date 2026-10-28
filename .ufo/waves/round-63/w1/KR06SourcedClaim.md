# KR06SourcedClaim — sourced-claim attack on the C1 completion checks

Seat: KR06SourcedClaim (kama round 63, leaf, no dispatch). Item: attack the sourced-claim requirement
behind the C1 response checks. Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09. Judged on
operability. Advisory findings only: no verdict on C1 or C2, no commit, no lane edit.

## Findings

1. **One graded check rests on a bound the source does not support, and it rejects a valid build.**
   `completion_fingerprint` (tools/kama-completion-live.py:75; tools/round63-c1-counter.py:46) requires
   `^b\d+-[0-9a-f]{9,40}$`. The source builds `system_fingerprint` as `"b" + build number + "-" + LLAMA_COMMIT`
   with `LLAMA_COMMIT` from `git rev-parse --short HEAD` (build-info.cpp.in:28; cmake/build-info.cmake:21).
   The abbreviation length is git's choice, not the source's. A 7-character abbreviation is valid and the
   floor of 9 rejects it. Reproduced in scratch (§Defect). No observed field contradicts the source; this is
   a false-fail defect, not a false pass, and the pinned b11755 receipt (9 characters) is unaffected.
2. **Three graded checks are only partly source-backed**: `completion_choice_shape` (non-empty text and the
   `index` value are not source-bounded), `completion_usage` (the `>= 1` token bounds and the
   `cached_tokens <= prompt_tokens` bound are not stated by the source), and `completion_fingerprint` (item 1).
3. **Two graded checks are observation-only**: `completion_untruncated` (client read plus transport framing,
   not llama.cpp source) and `completion_deterministic` (sampler behaviour, not read). The KB already says
   the text and determinism are observed; `completion_untruncated` is not labelled as transport.
4. **No observed field differs from the pinned source.** The fresh live run and round-63 v2 receipts agree
   with every line-cited shape (§Observed).
5. **Source-backed identities that are not graded** (candidates for L1; not required by C1 as written):
   `timings.cache_n == usage.prompt_tokens_details.cached_tokens` (both from `slot.stats.n_prompt_cached`),
   and `timings.prompt_n + timings.cache_n == usage.prompt_tokens`. One observed cache-hit sample agrees
   (7 = 7; 1 + 7 = 8).

## Method

- Fetched raw files myself from `raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/…`:
  `tools/server/server-task.cpp`, `server-common.cpp`, `server-context.cpp`, `server-http.cpp`, `server-http.h`,
  `server-common.h`, `server-task.h`, `server-schema.cpp`, `README.md`, `common/common.h`, `CMakeLists.txt`,
  `cmake/build-info.cmake`, `common/build-info.cpp.in`.
- Digests (out/KR06SourcedClaim/source-sha256.txt): `server-task.cpp` 4c3f413b…, `server-common.cpp` b4f4aae7…
  equal the retained `.ufo/waves/round-63/source/` copies; `README.md` 714c067b… equals the S526 digest;
  `server-context.cpp` dd1de0f2… and `server-http.cpp` 24ede172… equal the round-17 pins.
- Read every line the SOURCES rows S527/S528 cite (357-363, 366-393, 374-377, 380-386; 139-160) and checked each
  range against the fetched file. All cited ranges are correct.
- Fresh live run, lane tool, unregistered loopback port, scratch work dir, no hold:
  `python3 tools/kama-completion-live.py --work <scratch>/live --nonce kr06-src-<ts> --out <scratch>/live-receipt.json`
  → `REQUEST_OK`, 22/22 evaluated checks true, rc 0, port 43633. Receipt copied to out/KR06SourcedClaim/live-receipt-fresh.json.
- Git probe in a scratch fixture (git 2.56.0): §Defect. Output in out/KR06SourcedClaim/abbrev-probe.txt.
- Compared against round-63 v2 receipts `MT06ToolPromptTokens/A/receipt.json` and `MT01ToolHeaders/realhdr-receipt.json`
  (out/KR06SourcedClaim/observed-compare.txt). Exact cited lines: out/KR06SourcedClaim/cited-lines.txt.

## Per-check ledger (14 graded completion-response checks)

Status: **SRC** = line-cited in the pinned source and observed agrees; **PART** = partly supported (the
unsupported part is named); **OBS** = observation only; **OWN** = the tool's own construction.

| # | Check (tool line) | Graded assertion | Source at 704366d76 (≤25-word quotes, line) | Status |
|---|---|---|---|---|
| 1 | `completion_envelope` (364-367) | `object == "text_completion"`; `choices[0].text` is a string | `{"object", "text_completion"},` (server-task.cpp:390); `{"text", content.text},` (381) | SRC |
| 2 | `completion_headers` (370-372) | Content-Type is `application/json` after dropping params | default `std::string content_type = "application/json; charset=utf-8";` (server-http.h:22); the success path sets only status and data (server-context.cpp:4868-4871 `ok()`); `res.set_content(response->data, response->content_type);` (server-http.cpp:670) | SRC (the KB ground "HTTP layer not opened" is now superseded) |
| 3 | `completion_untruncated` (373-380) | body read whole; equals Content-Length | not in the pinned llama.cpp server files; this is the client reader and transport framing. Receipts: 623 = 623, 622 = 622 | OBS |
| 4 | `completion_choice_shape` (381-389) | one choice; `index == 0` (int, not bool); `logprobs is None`; text non-empty | `choices` is a one-element array (server-task.cpp:379-386); `logprobs` is null unless `!stream && probs_output.size() > 0` (368-373); `n_probs` defaults to 0 (common.h:231; alias `logprobs` at server-schema.cpp:179-180); `index` is the task index (`res->index = slot.task->index;` server-context.cpp:2191) and defaults to 0 (server-task.h:324). Non-empty text has no source bound. | PART (text non-empty observed; index value from default, not the request path) |
| 5 | `completion_finish_reason` (390-392) | in `{length, stop}` | `json finish_reason = "length";` then `"stop"` only `if (stop == STOP_TYPE_WORD || stop == STOP_TYPE_EOS)` (server-task.cpp:374-377); enum at server-task.h:45-48 | SRC (the output set is exhaustive) |
| 6 | `completion_model_id` (393-395) | `model == --alias` | `model_name = *params_base.model_alias.begin();` (server-context.cpp:1523); `task.params.oaicompat_model = meta->model_name;` (4954); `{"model", oaicompat_model}` (server-task.cpp:388) | SRC |
| 7 | `completion_fingerprint` (396-400) | `^b\d+-[0-9a-f]{9,40}$` | `{"system_fingerprint", std::string(llama_build_info())}` (server-task.cpp:389); `"b" + std::to_string(LLAMA_BUILD_NUMBER) + "-" + LLAMA_COMMIT` (build-info.cpp.in:28); `COMMAND ${GIT_EXECUTABLE} rev-parse --short HEAD` (cmake/build-info.cmake:21), `BUILD_COMMIT "unknown"` when git is absent (build-info.cmake:2). The hex length is git's choice; the floor 9 is observed only. | PART — **defect** (§Defect) |
| 8 | `completion_id_created` (401-406) | `id` non-empty string; `created` int > 1e9 | `return "chatcmpl-" + random_string();` (server-common.cpp:181-182); 32 chars from a 62-char alphabet (166-178); `{"id", oaicompat_cmpl_id}` (server-task.cpp:392); `std::time_t t = std::time(0);` (367) and `{"created", t}` (387). The 1e9 floor is the tool's own bound. | SRC (the `chatcmpl-` prefix is source-fixed on the completions route too, from `gen_chatcmplid()` at server-context.cpp:4896; the check does not grade it) |
| 9 | `completion_usage` (407-418) | integer counts; total = completion + prompt; `cached_tokens` int in `[0, prompt_tokens]`; `completion_tokens >= 1`; `prompt_tokens >= 1` | `{"total_tokens", n_decoded + n_prompt_tokens}` and the other keys (server-task.cpp:357-363); counters are `uint64_t` (server-common.h:400-401), so non-negative. `cached <= prompt`: follows from prefix reuse capped at `get_common_prefix` (server-context.cpp:3700) and decremented when equal to the task length (3911-3913), but no line states the bound. `n_gen += 1` per sampled token (4481): `>= 1` holds for `n_predict 8`, and no line rules out 0 in general. | PART (the `>= 1` bounds and the `<= prompt` bound are not source-stated) |
| 10 | `completion_timings` (419-424) | `predicted_n == completion_tokens`; `cache_n`, `prompt_n` non-negative ints; `predicted_ms` finite, non-negative | keys: `{"cache_n", n_prompt_cached}` (server-common.cpp:141), `{"prompt_n", n_prompt_processed}` (143), `{"predicted_n", n_gen}` (148), `{"predicted_ms", t_gen_ms()}` (149); `timings` included when `stats.is_set()` (server-task.cpp:399; `t_start > 0` at server-common.h:478-480); final response carries `res->stats = slot.stats;` (server-context.cpp:2251); `completion_tokens` is `n_decoded = slot.stats.n_gen` (2256) and `predicted_n` is `n_gen` (server-common.cpp:148) — same counter; `predicted_ms` clamped to `>= 1` µs (server-common.h:448) | SRC |
| 11 | `completion_prompt_tokens` (425-435) | `usage.prompt_tokens == len(/tokenize tokens)` with `add_special` true | completions tokenize with `add_special=true, parse_special=true` (server-context.cpp:4929); `/tokenize` reads `add_special` default false and `parse_special` default true (5742-5743); the tool sends `add_special: True` (kama-completion-live.py:427); `n_prompt_tokens = slot.task->n_tokens()` (server-context.cpp:2257). The BOS insertion itself is a tokenizer property (observed 8 = 8). | SRC for the equality rule (supersedes the KB's "no pinned line opened for the special-token rule") |
| 12 | `completion_request_bound` (436-444) | recorded request bytes hash to `request_sha256` and carry the prompt | own construction | OWN |
| 13 | `completion_deterministic` (445-463) | temp 0 + fixed seed → same text | sampler determinism not read; one observed pair (text equal) | OBS |
| 14 | `bad_request_graded` (465-475) | status 400/500 and `error` object | missing `prompt`: `data.at("prompt")` (server-context.cpp:4907) throws; caught at 4968-4969 and passed to `res->error(format_error_response(e.what(), ERROR_TYPE_INVALID_REQUEST))`; `error()` wraps `{"error": error_data}` (4872-4874); `ERROR_TYPE_INVALID_REQUEST` maps to `invalid_request_error` and `code = 400` (server-common.cpp:95-97). Observed 400 and `invalid_request_error`. | SRC |

Tally: 8 SRC (1, 2, 5, 6, 8, 10, 11, 14), 3 PART (4, 7, 9), 2 OBS (3, 13), 1 OWN (12).

## Defect: `completion_fingerprint` floor (check 7)

- Source: the fingerprint's hex part is `git rev-parse --short HEAD` (cmake/build-info.cmake:21), i.e. git's
  default abbreviation, which git sizes to the repository. The source fixes the shape `b<n>-<hash>`, not a hash length.
- Reproduced (scratch fixture, git 2.56.0; out/KR06SourcedClaim/abbrev-probe.txt): a one-commit repo gives
  `e8e2b79` (7 characters). `b11755-e8e2b79` fails `^b\d+-[0-9a-f]{9,40}$` (False). `b11755-704366d76` passes
  (9 characters, the pinned build's observed value). An 8-character `b11755-704366d7` also fails.
- Correct to reject: `b0-unknown` (the no-git fallback, build-info.cmake:2): it is not a commit identity.
- Impact: the live tool (line 75) and the counter (`FP_RE`, line 46; `live_fp_shape` at counter lines 300-301; the
  witness-fingerprint match at 303) all use the same floor. A valid build of this source whose abbreviation is 7 or 8
  characters is rejected by both. The counter does not independently check the floor, so the defect is shared, not caught.
- Smallest correction for L1 (not applied by me): lower the floor to `{7,40}` (7 is the default minimum observed here;
  git's documentation was not fetched) and keep `^b\d+-`. A stronger alternative is to grade the hash as a prefix of the
  build's own `git rev-parse --short` at the source tree, which is out of scope for a shape check.

## Observed versus source

- Fresh live run (out/KR06SourcedClaim/live-receipt-fresh.json): `object` text_completion; `id` `chatcmpl-` + 32
  alphanumerics; `created` 1793227572; `model` kama-completion-probe; `system_fingerprint` b11755-704366d76;
  `Content-Type` `application/json; charset=utf-8`; `content-length` 622 = body bytes; `logprobs` null;
  `finish_reason` length; usage 8/8/16 with `cached_tokens` 0; timings keys exactly `cache_n`, `prompt_n`,
  `prompt_ms`, `prompt_per_token_ms`, `prompt_per_second`, `predicted_n`, `predicted_ms`, `predicted_per_token_ms`,
  `predicted_per_second` (server-common.cpp:141-151; no `draft_n`, consistent with 154-157).
- Second (determinism) request in the same run was a cache hit: `cache_n` 7, `prompt_n` 1, `cached_tokens` 7,
  `prompt_tokens` 8. This agrees with the identities in finding 5.
- Round-63 v2 receipt `MT06ToolPromptTokens/A` (pre-existing) matches the same field set; `content-length` 623 = body bytes.
- **No observed field differs from the source.** The `chatcmpl-` id prefix on the `/v1/completions` route is a fact the KB
  does not record; a future grader that expected `cmpl-` would fail a conforming server.

## Knowledge-entry corrections (completion-request-plane.md; reported, not edited)

- `completion_headers`: ground should be source (server-http.h:22; server-http.cpp:670), not "HTTP layer not opened".
- `completion_model_id`: ground should cite server-context.cpp:1523 and 4954.
- `completion_prompt_tokens`: the equality rule is source-backed (server-context.cpp:4929, 5742-5743); BOS presence stays observed.
- `completion_fingerprint`: no ground row; add server-task.cpp:389 and cmake/build-info.cmake:21, and mark the 9-character floor observed.
- The `id` row: the source fixes `chatcmpl-` + 32 characters (server-common.cpp:181-182), on both routes.

## Tools and installs

None. Used curl, python3 stdlib, and the lane's own live tool; git 2.56.0 was already present. No package or binary installed.

## Cleanup

Scratch dir `/fast/scratch/hyaku/kama-r63/w/KR06SourcedClaim` removed after receipts and excerpts were copied to
`.ufo/waves/round-63/w1/out/KR06SourcedClaim/`. No git mutation anywhere; the only writes are this report and that out dir.

KR06 tally: 14 graded completion-response checks: 8 source-cited (SRC), 3 partly supported (PART: 1 defect, `completion_fingerprint` floor 9 vs source-valid 7), 2 observation-only (OBS), 1 own (OWN); 0 observed contradictions; fresh live run REQUEST_OK 22/22, rc 0.
