# RowReview03 — F28-05 (n_discard) / F28-06 (n_cmpl) falsify report

Seat: KamaR28.RowReview03 (port 48303). Claim C1, wave 2, lane tip e49b4cf7
(read-only). No tools installed (none needed); no counter run (not in scope).
Verdict: **both rows hold — no finding**.

## Live re-measurement (own server, port 48303, exact pinned argv under timeout)

Server: `~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48303`
(sha256 b6a31a8e…d804, matches PINS; model 270cba1b…256d). Process group killed
after measurement; `ss -ltnp` confirmed port free.

### F28-05 `n_discard: -1`
- Base (field omitted) `{"prompt":"Once upon a time","n_predict":1}`: HTTP 200, response sha256 `75159e65…61e`.
- Request `{"prompt":"Once upon a time","n_predict":1,"n_discard":-1}`: **HTTP 400**,
  message `Field 'n_discard': Value must be between 0 <= value <= 2147483647, but got -1`,
  response sha256 **`a90197b7ee2783dc4bb474bd098125b7a79de697a5fc36b43c724bac5635c584`** —
  identical to the seat's `live_by_seat.response_sha256` and to the L1 receipt's `rows[F28-05].live.body_sha256`.

### F28-06 `n_cmpl: 0`
- Base (above): HTTP 200.
- Request `{...,"n_cmpl":0}`: **HTTP 400**, message `Field 'n_cmpl': Value must be between 1 <= value <= 4, but got 0`,
  response sha256 **`b72883f3b95c177b4bdecc886cecf947125d393c6f5afad0791e46ba121a5038`** —
  identical to seat and receipt values.
- Bonus `n_cmpl: 5` (above the "4" bound): HTTP 400, `... between 1 <= value <= 4, but got 5` —
  confirms the upper bound is 4 at this fixture's default argv (n_parallel=4), as the SKILL.md preamble states.

## Source verdict (pinned snapshot `.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp`, sha256 1f9d7b73…0050)
- Line 58 declares `n_discard` via `new field_num` with `set_hard_limits(0, INT32_MAX)` (line 59) →
  source explains the 400 reject with those exact bounds.
- Line 62 declares `n_cmpl` via `new field_num` with `set_hard_limits(1, params_base.n_parallel)` (line 63) →
  source explains the 400 reject with lower bound 1 and launch-dependent upper bound (=4 here).

## Prose verdict (SKILL.md meaning cells)
- F28-05: "The server rejects any n_discard below zero with HTTP 400 instead of clamping, so clients must send 0 or a positive discard count." — supported by measurement + hard limits; no false/unsupported/over-general statement. No correction.
- F28-06: "The server rejects n_cmpl outside one through n_parallel (four here) with HTTP 400, so clients must ask for no more completions than server slots." — supported (0 and 5 both rejected, bounds 1..4); "four here" matches fixture-default n_parallel=4 (verified live). No correction.
- Both cells ≥6 words (counter's prose floor, fine).

## SOURCES/Gate verdict
- Raw URL fetch (S144/S145) `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L58/#L62`: fetched myself, sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` — equals the pinned snapshot and is byte-identical (`cmp`).
- Gate quotes (lessons/round-28.md) hold verbatim vs whitespace-normalised snapshot lines 58-59 / 62-63 (verified by join+compare).
- SOURCES.md rows S144/S145 name the field, declaring line (58/62), limits line (59/63), commit 704366d76, raw sha256, and live outcome (reject 400, bounds 0..2147483647 value -1; 1..4 value 0) — all consistent with my measurements.

## Counted verdict
Both F28-05 and F28-06 are in the receipt's `counted_ids` with `why: []`; the receipt registers 34, counts 26, target 18 met True. All predicate clauses hold for these rows (set one-key, SKILL row six cells verbatim, meaning ≥6 words, S### token, SOURCES row new vs base, declaration line check), and my live bodies reproduce the receipt's exact `body_sha256`. Verdict **right**.

## Residual risk / gaps
- "Rejects any value below zero / outside one through n_parallel" is verified at one point each side (and 5 above max for n_cmpl); universal rejection follows from the code's hard-limit enforcement, not exhaustive probing — consistent with the claim's "one request per field" framing.
- I did not run `count-c1.py` (not authorized for this seat); the counted verdict is checked by inspection + identical live hashes.

Evidence: `/fast/scratch/hyaku/kama-r28/w2/KamaR28.RowReview03/measure.sh`, `base.bin`, `discard.bin`, `cmpl0.bin`, `cmpl5.bin`, `raw-schema.cpp` (sha256 1f9d7b73…0050).
