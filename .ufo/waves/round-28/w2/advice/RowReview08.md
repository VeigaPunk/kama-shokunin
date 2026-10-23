# RowReview08 — C1 falsify: F28-15 (repeat_last_n), F28-16 (repeat_penalty)

Seat: KamaR28.RowReview08 (leaf). Port 48308, pinned build/model (model sha256
270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d OK; server
~/.local/opt/llama-b11755/llama-server). Counter exact request: POST /completion
{"prompt": "Once upon a time", "n_predict": 1} + row `set`; field-omitted base
for the base value. Server killed afterward (ss -ltnp: 48308 closed).

## Verdict: both rows HOLD. No false, unsupported or over-general statement found
in either SKILL.md meaning cell; no corrected sentence proposed.

## F28-15 repeat_last_n = -1 (S154, L126) — HOLDS
- Live re-measure: status **400**, body sha256
  `8a1934153f6ecbdc2284a1e8acd485af9d07009c9723796e608fbf633d6d57c0` (exact match
  to seat `live_by_seat.response_sha256` AND receipt `body_sha256`), message
  `Field 'repeat_last_n': Value must be between 0 <= value <= 2147483647, but got -1`.
  Base omit: 200, `generation_settings.repeat_last_n` = 64.
- Source explains outcome: snapshot L126 declares `field_num("repeat_last_n",
  params.sampling.penalty_last_n)`, L127 `->set_hard_limits(0, INT32_MAX)`.
  `field_num<T>::eval` (L531-551): hard-limit branch throws `Value must be
  between <min> <= value <= <max>, but got <tmp>` when `tmp < min || tmp > max`
  (bounds inclusive), wrapped by `handle_with_catch` as `Field '<name>': …`
  → HTTP 400. Exactly the observed message/bounds.
- Meaning cell: "A negative repeat_last_n is rejected with HTTP 400 naming the
  inclusive hard bounds 0 to 2147483647, so clients must validate this count
  before sending instead of expecting a clamp." — accurate, field-scoped; no
  correction. (Inclusivity is source-confirmed; boundary values 0/2147483647
  not live-exercised — low risk.)

## F28-16 repeat_penalty = 1e39 (S155, L130) — HOLDS
- Live re-measure: status **200**, `generation_settings.repeat_penalty` =
  **3.4028234663852886e38**; base omit = 1.0. Body sha256 of this run
  `602a74ff…`; seat recorded `0f0dae56…`, receipt `cd2a5258…` — all differ
  because /completion bodies embed wall-clock `timings` (prompt_ms,
  predicted_per_second, verified present); the counter verdicts on status +
  effective value, not raw hash, so this is benign and not a defect.
- Source explains outcome: L130 declares `field_num("repeat_penalty",
  params.sampling.penalty_repeat)`, L131 only `->set_desc(...)` — no limits, no
  handler, so `field_num<T>::eval` takes the soft-clamp branch
  `val = max(min, min(max, get<T>()))` with T=float numeric_limits (max =
  FLT_MAX 3.4028234663852886e38); 1e39 → float32 saturation to FLT_MAX. No
  field-specific code does this; it is the generic float32 conversion.
- Meaning cell: "A repeat_penalty above the float range is silently saturated to
  3.4028234663852886e+38 in generation_settings, so operators should verify the
  echoed value and keep penalties near the 1.0 default." — accurate; no
  correction. It does not overgeneralize beyond the field's own behavior.
- Receipt: F28-16 is **not counted**, `why: ["e:generic-conversion"]` — right
  under amendment A1 (effective == generic float32 conversion of the sent value;
  would count only under superseded A0). F28-15 counted, `why: []` — right.

## SOURCES / Gate verification (step 4)
- Raw fetch https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp
  sha256 = `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`
  = pinned snapshot = preregistration sourced hash. Verbatim.
- S154 quote = snapshot lines 126-127 whitespace-joined (present verbatim in the
  whitespace-normalised snapshot; spans two lines so absent as a raw single line).
- S155 quote = lines 130-131 whitespace-joined (same check OK).

## Verification gaps / residual risk
- Boundary inclusivity (0 and 2147483647 accepted) rests on the `tmp < min ||
  tmp > max` source check, not a live send of the exact boundary values.
- repeat_penalty's stored value's exact mechanism (get<float> overflow vs clamp
  to FLT_MAX) is not separated at runtime; the observable value is FLT_MAX and
  the source clamp branch explains it.
- No tooling installed (system curl/python3 only); RULES.md read; no lane
  writes beyond this advice file.
