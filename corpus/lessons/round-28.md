# kama — round 28 lesson (2026-10-23, attempt 1)

Author: kama L1 round 28 (KamaR28). Base `4179301f`. One measured claim,
routed repairs from `corpus/lessons/round-27-verifier-spotcheck.md`, and the
frontier step. Every seat report is under `.ufo/waves/round-28/` (controls/,
controls-A1/, w1/advice/, w1/out/).

## Claims

**C1 (measured, depth).** Surface: SKILL.md gains `## Round-28 request-field
outcomes`, a table of what llama-server b11755 does with one out-of-range or
transformed value of a request field declared in `tools/server/server-schema.cpp`
@704366d76 (reject with HTTP 400 and the field's hard bounds, or store a
different value in `generation_settings`), with `registry/request-field-outcomes-r28.json`
and one new SOURCES row per declaring line (S140-S173). The lane held no part of
server-schema.cpp at base (ScoutProvince: zero lane-document hits for
`server-schema`, `set_hard_limits`, `Value must be between` at 5ebe7b1b).
Frozen predicate, counter and target: `.ufo/waves/round-28/preregistration.json`
(A0 at `d8bf1804`, counter sha256 `e6a706bb…0540c`; amendment A1 at `75b78bb4`,
counter sha256 `a38faefe…49a5`); target `counted >= 18`; kill rule: a miss is
reported, never amended or re-scaled.

Why this surface: a feasibility scan before the freeze found the request-error
signature ground at b11755 nearly exhausted (55 literals new to the lane, 2-3
reachable over HTTP; scratch only), the reason rounds 26-27 could not produce
counted data. The schema surface was new and producible.

Order of events (all commits by `jj-lane.sh`):
1. `d8bf1804` freeze A0: counter, preregistration, base receipt
   (`before/c1-base.out`: registered 0 counted 0), pilot receipt (2 scratch
   rows counted 2; fields n_cache_reuse and xtc_threshold then excluded).
2. Pre-freeze control call (10 seats, 08:14Z): `5ebe7b1b`
   (`controls/HOLDS.md`). Evidential: do-nothing 0, junk 0/30, label-keyed
   12/41, source-blind 14/38, duplicate-field 0/26. Holds: CtlNoReader,
   CtlObjectStore, CtlAllFalse (provider cyber refusals), CtlEcho and
   CtlSourceMisuse (automatic model switch after a safety filter). No control
   met 18; the counter was not changed.
3. Wave 1 (32 seats, 08:31-08:34Z): 17 data seats measured every declared
   field live on their own ports and returned uncommitted row drafts.
4. Amendment A1 (`75b78bb4`, before any data row was committed or scored):
   data seats DataG03/05/07/08 returned rows whose stored value is only a
   generic type conversion (float32 saturation 1e39 -> 3.4028e38, uint32 wrap,
   truncation). Under A0 those count, so a type-only policy needs no field
   knowledge. A1 refuses an effective value equal to any generic conversion of
   the value sent (`e:generic-conversion`); nothing else changed.
5. A1 control call (3 seats): `fb10d9da`. CtlA1Conversion: the type-only
   policy counted **20/52 under A0 (meets)** and **0/52 under A1**.
   CtlA1Rescore: the five evidential pre-freeze fixtures under A1 give at most
   9 (source-blind 14 -> 9, label-keyed 12 -> 7). CtlA1BlindPlus (a fixed
   single-shot README-and-names policy): 11/38.
6. Data landed (34 registered rows, F28-01..F28-34), then the frozen A1 counter
   was run from a fresh clone of the lane remote (§Measurement).

## Repairs (round-27 spot-check routed defects, `round-27-verifier-spotcheck.md:258-287`)

| # | Defect | Disposition | Evidence |
|---|---|---|---|
| 1 | `count-c2.py` trusts receipt cells | repaired: every per-cell value is recomputed from the sha256-bound raw bodies/log; a receipt cell that disagrees makes the cell unobserved | `.ufo/waves/round-25/count-c2.py` (sha256 5aa64a37…); ExecCountC2Fix: committed receipt `registered 14 observed 14 bound True missing []` before and after; forged cells with raw untouched: before `observed 14 bound True`, after `observed 11 bound False missing ['K2','K4','L1']`; forged raw with re-bound hash: before `bound True`, after `bound False` (`w1/out/ExecCountC2Fix/`) |
| 2 | F3 file-content echo leg; per-class receipts | closed as a criterion, not code: the round-27 counter is retired without data; KQ37 now requires an F3 leg of any future signature counter (QUALITY.md round-28 qualification 4). This round's counter is not a signature counter; its per-class receipts are non-vacuous (`controls/`, `controls-A1/`); five classes are holds | QUALITY.md; `controls/HOLDS.md` |
| 3 | round-27 counter not registered | repaired: SKILL.md registry rows retire `.ufo/waves/round-27/count-c1.py` and register this round's counter, `tools/gate-registry-check.py` and `tools/echo-recheck.py`; the check itself is the mined-mistake fix below | SKILL.md `## Local gate/probe registry — round-28 rows` |
| 4 | KQ37 S136 wording; clause (d) overstated | repaired: QUALITY.md `## Round 28 qualification -- KQ37` items 1-2 | ScribeKQ37Qualification line checks |
| 5 | boundary probe scope; E26-14 | repaired: QUALITY item 3 and the entry's boundary-cost text now state exact, case-sensitive decoded strings of length >= 4 (`boundary-leg.receipt.json:10-14`); E26-14 is named as the open boundary-design question | `corpus/knowledge/echo-discriminating-counters.md` |
| 6 | entry `recheck:` not runnable | repaired: `tools/echo-recheck.py --out <fresh path>` (refuses an existing path); ExecEchoRecheck runs: `echo-recheck same 6/6` exit 0 twice, existing path exit 2, mutated baseline `drift req1-plain` exit 1 | `w1/out/ExecEchoRecheck/` |
| 7 | round-27 report imprecisions | corrected here and in the round-28 report: the residual call spawned at 07:23:39Z (`.ufo/waves/round-27/residual/spawn-result.txt`), and `8057282c` also added `census-final.out` and `sources-append-only-final.out` | `git show --stat 8057282c` |

## Gate

New SOURCES rows S140-S173, one per declaring line of server-schema.cpp @
704366d76. Each row was opened this round by the data seat named (its own curl
of the raw URL hashed `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`,
equal to the pinned snapshot) and re-read by the L1. Four seat-supplied quotes
were not verbatim (lora, xtc_probability, temperature, logit_bias), so every
quote below is the pinned file's lines L and L+1, whitespace-joined, cut to 25
words (L1 check: each occurs in the whitespace-normalised snapshot).

| S### | field (line) | URL | accessed (UTC) | located quote (lines L and L+1 of the pinned file, whitespace-joined, first <= 25 words) | opened by | fetched sha256 |
|---|---|---|---|---|---|---|
| S140 | `sse_ping_interval` (L40) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L40 | 2026-10-23T08:33:24Z | `add((new field_num("sse_ping_interval", params.sse_ping_interval)) ->set_hard_limits(-1, INT32_MAX)` (5 words) | DataG01 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S141 | `n_predict` (L44) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L44 | 2026-10-23T08:33:24Z | `add((new field_num("n_predict", params.n_predict)) ->set_hard_limits(-1, INT32_MAX)` (5 words) | DataG01 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S142 | `n_indent` (L50) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L50 | 2026-10-23T08:33:24Z | `add((new field_num("n_indent", params.n_indent)) ->set_hard_limits(0, INT32_MAX)` (5 words) | DataG01 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S143 | `n_keep` (L54) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L54 | 2026-10-23T08:33:24Z | `add((new field_num("n_keep", params.n_keep)) ->set_hard_limits(-1, INT32_MAX)` (5 words) | DataG01 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S144 | `n_discard` (L58) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L58 | 2026-10-23T08:33:00Z | `add((new field_num("n_discard", params.n_discard)) ->set_hard_limits(0, INT32_MAX)` (5 words) | DataG02 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S145 | `n_cmpl` (L62) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L62 | 2026-10-23T08:33:00Z | `add((new field_num("n_cmpl", params.n_cmpl)) ->set_hard_limits(1, params_base.n_parallel)` (5 words) | DataG02 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S146 | `t_max_predict_ms` (L74) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L74 | 2026-10-23T08:33:00Z | `add((new field_num("t_max_predict_ms", params.t_max_predict_ms)) ->set_hard_limits(-1, std::numeric_limits<int64_t>::max())` (5 words) | DataG02 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S147 | `top_k` (L89) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L89 | 2026-10-23T08:32:44Z | `add((new field_num("top_k", params.sampling.top_k)) ->set_limits(0, INT32_MAX)` (5 words) | DataG03 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S148 | `top_p` (L93) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L93 | 2026-10-23T08:32:44Z | `add((new field_num("top_p", params.sampling.top_p)) ->set_limits(0.0f, 1.0f)` (5 words) | DataG03 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S149 | `min_p` (L97) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L97 | 2026-10-23T08:32:44Z | `add((new field_num("min_p", params.sampling.min_p)) ->set_limits(0.0f, 1.0f)` (5 words) | DataG03 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S150 | `top_n_sigma` (L101) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L101 | 2026-10-23T08:32:44Z | `add((new field_num("top_n_sigma", params.sampling.top_n_sigma)) ->set_desc("Keep tokens within n standard deviations of the top token logit (< 0 = disabled)"));` (18 words) | DataG03 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S151 | `xtc_probability` (L104) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L104 | 2026-10-23T08:33:00Z | `add((new field_num("xtc_probability", params.sampling.xtc_probability)) ->set_limits(0.0f, 1.0f)` (5 words) | DataG04 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S152 | `temperature` (L116) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L116 | 2026-10-23T08:33:00Z | `add((new field_num("temperature", params.sampling.temp)) ->set_limits(0.0f, std::numeric_limits<float>::infinity())` (5 words) | DataG04 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S153 | `dynatemp_exponent` (L123) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L123 | 2026-10-23T08:33:18Z | `add((new field_num("dynatemp_exponent", params.sampling.dynatemp_exponent)) ->set_desc("Dynamic temperature exponent, controls how entropy maps to temperature"));` (12 words) | DataG05 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S154 | `repeat_last_n` (L126) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L126 | 2026-10-23T08:33:18Z | `add((new field_num("repeat_last_n", params.sampling.penalty_last_n)) ->set_hard_limits(0, INT32_MAX)` (5 words) | DataG05 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S155 | `repeat_penalty` (L130) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L130 | 2026-10-23T08:33:18Z | `add((new field_num("repeat_penalty", params.sampling.penalty_repeat)) ->set_desc("Control the repetition of token sequences in the generated text (1.0 = disabled)"));` (16 words) | DataG05 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S156 | `frequency_penalty` (L133) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L133 | 2026-10-23T08:33:18Z | `add((new field_num("frequency_penalty", params.sampling.penalty_freq)) ->set_desc("Repeat alpha frequency penalty (0 = disabled)"));` (10 words) | DataG05 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S157 | `dry_allowed_length` (L149) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L149 | 2026-10-23T08:33:00Z | `add((new field_num("dry_allowed_length", params.sampling.dry_allowed_length)) ->set_hard_limits(0, INT32_MAX)` (5 words) | DataG06 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S158 | `dry_penalty_last_n` (L153) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L153 | 2026-10-23T08:34:04Z | `add((new field_num("dry_penalty_last_n", params.sampling.dry_penalty_last_n)) ->set_hard_limits(0, INT32_MAX)` (5 words) | DataG07 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S159 | `mirostat` (L157) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L157 | 2026-10-23T08:34:04Z | `add((new field_num("mirostat", params.sampling.mirostat)) ->set_limits(0, 2)` (5 words) | DataG07 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S160 | `mirostat_tau` (L161) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L161 | 2026-10-23T08:34:04Z | `add((new field_num("mirostat_tau", params.sampling.mirostat_tau)) ->set_desc("Set the Mirostat target entropy, parameter tau"));` (10 words) | DataG07 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S161 | `mirostat_eta` (L164) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L164 | 2026-10-23T08:34:04Z | `add((new field_num("mirostat_eta", params.sampling.mirostat_eta)) ->set_desc("Set the Mirostat learning rate, parameter eta"));` (10 words) | DataG07 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S162 | `adaptive_target` (L167) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L167 | 2026-10-23T08:33:29Z | `add((new field_num("adaptive_target", params.sampling.adaptive_target)) ->set_limits(-std::numeric_limits<float>::max(), 1.0f)` (5 words) | DataG08 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S163 | `adaptive_decay` (L171) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L171 | 2026-10-23T08:33:29Z | `add((new field_num("adaptive_decay", params.sampling.adaptive_decay)) ->set_hard_limits(0.0f, 0.99f)` (5 words) | DataG08 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S164 | `seed` (L176) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L176 | 2026-10-23T08:33:29Z | `add((new field_num("seed", params.sampling.seed)) ->set_desc("Set the random number generator (RNG) seed (-1 = random)"));` (13 words) | DataG08 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S165 | `n_probs` (L179) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L179 | 2026-10-23T08:33:29Z | `add((new field_num("n_probs", params.sampling.n_probs)) ->add_alias("logprobs") // use "logprobs" if "n_probs" wasn't provided` (11 words) | DataG08 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S166 | `min_keep` (L183) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L183 | 2026-10-23T08:33:23Z | `add((new field_num("min_keep", params.sampling.min_keep)) ->set_hard_limits(0, INT32_MAX)` (5 words) | DataG09 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S167 | `lora` (L229) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L229 | 2026-10-23T08:32:44Z | `add((new field_json("lora")) ->set_desc("A list of LoRA adapters to apply to this request. Each entry must have `id` and `scale` fields. Adapters not listed default to` (25 words) | DataG11 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S168 | `preserved_tokens` (L316) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L316 | 2026-10-23T08:34:35Z | `add((new field_json("preserved_tokens")) ->set_desc("List of token strings that must not be split during tokenization")` (13 words) | DataG13 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S169 | `reasoning_budget_tokens` (L335) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L335 | 2026-10-23T08:33:42Z | `add((new field_num("reasoning_budget_tokens", params.sampling.reasoning_budget_tokens)) ->set_hard_limits(-1, INT32_MAX)` (5 words) | DataG14 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S170 | `logit_bias` (L382) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L382 | 2026-10-23T08:34:29Z | `add((new field_json("logit_bias")) ->set_desc("Modify the likelihood of specific tokens. Accepts an array of [token, bias] pairs or an object mapping token to bias. Use false as` (25 words) | DataG15 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S171 | `ignore_eos` (L423) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L423 | 2026-10-23T08:34:29Z | `add((new field_bool("ignore_eos", params.sampling.ignore_eos)) ->set_desc("Ignore the end-of-sequence token and continue generating")` (10 words) | DataG15 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S172 | `stop` (L435) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L435 | 2026-10-23T08:34:29Z | `add((new field_json("stop")) ->set_desc("Specify stopping strings. Generation stops when one is produced, and the string is not included in the output")` (20 words) | DataG15 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
| S173 | `samplers` (L453) | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L453 | 2026-10-23T08:34:29Z | `add((new field_json("samplers")) ->set_desc("The order in which samplers are applied. An array of sampler type names, or a single string of sampler chars")` (22 words) | DataG15 (sha256 of own fetch 1f9d7b73b436…) | 1f9d7b73b436… |
