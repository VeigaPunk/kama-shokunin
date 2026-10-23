# Review: SKILL.md "## Round-28 request-field outcomes" prose (intro + no_rows paragraph)

Seat: KamaR28.ReviewSkillSectionIntro (FALSIFY, wave 2). Read: preregistration.json,
corpus/lessons/round-28.md, SKILL.md:1135-1209, pinned snapshot server-schema.cpp
(sha256 1f9d7b73…0050), count-c1.py, and all 17 w1 seat rows.json.

## Verdict: partly — prose is overwhelmingly accurate; 3 small factual defects in the
"Fields measured with no countable row" paragraph, none in the intro paragraph.

## Findings (by severity)

### 1 (minor, factual misdeclaration): `echo` is not a `field_bool` field
No_rows paragraph: "`field_bool` fields (`verbose`, …, `echo`, `reasoning_control`)…".
In the pinned snapshot `echo` is declared `field_json` — server-schema.cpp:306:
`add((new field_json("echo"))` with a handler that coerces `data.at("echo").get<bool>()`
(:308-310). The behavioral description (discarded, no generation_settings key; non-boolean →
type_error 400) is correct (DataG13 no_rows), but the declaration type is wrong.
Corrected sentence: "`field_bool` fields (`verbose`, `timings_per_token`, `stream`,
`include_usage`, `cache_prompt`, `return_tokens`, `return_progress`, `backend_sampling`,
`post_sampling_probs`, `grammar_lazy`, `reasoning_control`) and `field_json` `echo`
store the boolean sent or are not reported, and a non-boolean value is a 400 JSON type
error with no bounds".

### 2 (minor, overstatement): the "non-boolean → 400" clause does not hold for `include_usage`
The same sentence claims every listed name rejects a non-boolean value with a 400 JSON
type error. `include_usage` is a nested subfield of `stream_options` (snapshot:26-28);
a *top-level* `{"include_usage": true}` is silently ignored → 200 (DataG16 no_rows:
cu_toplevel.out), a non-object `{"stream_options": 5}` / `"x"` is silently dropped → 200
(DataG16, DataG17 additional probes). The type-error 400 occurs only when nested:
`{"stream_options": {"include_usage": 1}}` → "Field 'include_usage': … type must be
boolean, but is number" (DataG16 usage_num.json; DataG17 400 probe). So at top level
`include_usage` has no 400 at all.
Corrected sentence: add "…except `include_usage`, which as a nested subfield is only
validated inside a `stream_options` object; a top-level or non-object value is silently
ignored (200)".

### 3 (minor, omission): `stream_options` itself is not named
The paragraph enumerates the no-row fields but never names `stream_options`, the nested
container declared at snapshot line 26, which DataG17 measured as a no-row field
(non-object silently dropped; no generation_settings key). Corrected sentence: mention
`stream_options` (nested container) alongside `include_usage`.

## Statements checked and found supported (with evidence)
- Intro: fixture pins (server b6a31a8e…d804, model 270cba1b…256d), snapshot sha256, and
  native POST /completion body {"prompt": "Once upon a time", "n_predict": 1} — match
  wave-1 base requests (e.g. DataG03 base_request) and counter BASE_BODY (count-c1.py:103).
- "n_parallel is 4 under default argv" — empirically true: live probe n_cmpl=0 →
  "Field 'n_cmpl': Value must be between 1 <= value <= 4, but got 0" (DataG02 rows).
- "set_hard_limits rejects with HTTP 400 `Field '<name>': Value must be between A <= value
  <= B, but got V`" — exact live strings across DataG01/02/05/07/08/09/14; code path in
  snapshot :522 + :541-546.
- "set_limits clamps silently; handlers transform" — snapshot :539 (soft clamp), :553-590
  (field_str/field_json require handlers); row evidence pass.
- "the counter re-runs every row on its own pinned server" — count-c1.py:575-627 starts the
  pinned Server and POSTs base body + set per row, verifying reject/effective live.
- "Rows whose stored value is only a generic type conversion are true but not counted (A1)"
  — counter conversions() + e:generic-conversion (:283-303, :623-624); the 8 saturated/
  truncated/wrapped table rows (F28-11/14/16/17/21/22/25/26) match counted 26/34.
- "`speculative.*` declarations at lines 198-227 sit in an `#if 0` block and are silently
  ignored" — snapshot :198/#if 0 … :227/#endif; DataG09/G10/G11 no_rows (200, generation_settings
  unchanged; unknown-field control same response sha256).
- Bool fields "store the boolean sent or are not reported; non-boolean → 400 type error"
  (except findings 2/3) — DataG09 (backend_sampling, post_sampling_probs), DataG12
  (grammar_lazy), DataG13 (reasoning_control), DataG16 (verbose, timings_per_token, stream,
  include_usage), DataG17 (cache_prompt, return_tokens, return_progress).
- typical_p / dynatemp_range / presence_penalty / dry_multiplier echo the value sent —
  DataG04 (2.0→2.0, -2.5→-2.5), DataG06 (1e9→1e9, -7.5→-7.5).
- dry_base below 1.0 falls back to default 1.75 — DataG06 (0.5→1.75 == base_effective);
  snapshot handler :144-147.
- json_schema compiled into generation_settings.grammar as GBNF with "|" — DataG12 effective
  grammar ("root ::= (\"true\" | \"false\")…space ::= | \" \" | …").
- reasoning_format / continue_final_message / grammar_triggers / dry_sequence_breakers /
  response_fields / reasoning_budget_* strings: no bounds message and no observable stored
  transform — DataG12/13/14/11/02 no_rows (non-bounds 400s: "Unknown reasoning format",
  "Invalid continue_final_message", "must be a non-empty array of strings", type_error 302).
- n_cache_reuse (400, bounds 0..2147483647) and xtc_threshold (2.5 stored as 1.0) were the
  counter pilot and are excluded — preregistration excluded_fields/pilot_A1; snapshot :68,
  :109; no w1 seat measured them (grep over DataG* rows.json: zero hits).

## Residual risk / verification gaps
- No seat probed in-range n_keep/n_predict live; the "echo the value sent" claim rests on
  the hard-limit code path (snapshot :541-546) — low risk.
- The 8 generic-conversion rows are in the table but uncounted; whether that makes the table
  misleading is a claim-design question, not prose — out of scope here.

## Environment
No tool installs (none needed).
