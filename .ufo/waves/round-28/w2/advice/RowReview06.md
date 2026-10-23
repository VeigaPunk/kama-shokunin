# RowReview06 — FALSIFY C1 rows F28-11 / F28-12

Seat: KamaR28.RowReview06, round 28 wave 2. Port 48306, pinned server
`~/.local/opt/llama-b11755/llama-server` (argv exactly as bound: `-m
~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port
48306`), process group killed before return, `ss -ltnp` confirms no listener.
No tool installs performed (none needed). All reads above are from the lane at
e49b4cf7 (read-only).

## F28-11 — `top_n_sigma` = 3.5e+38 (line 101, S150)

### Live re-measure (port 48306)
Base: `POST /completion` body `{"prompt": "Once upon a time", "n_predict": 1}`
→ 200, `generation_settings.top_n_sigma` = -1.0 (field omitted).
Row request: same body + `"top_n_sigma": 3.5e38` → **status 200**,
`generation_settings.top_n_sigma` = **3.4028234663852886e+38** (FLT_MAX).
Response sha256 `2897cccbc3c42e8d9c756e322acfaed3b436586062ab00026b6209783c2705d8`.
Matches registry row outcome `200, top_n_sigma = 3.4028234663852886e+38` and
live_by_seat effective value.

### Source verdict — HOLDS (explains outcome)
Pinned `server-schema.cpp` L101-102:
```
add((new field_num("top_n_sigma", params.sampling.top_n_sigma))
    ->set_desc("Keep tokens within n standard deviations of the top token logit (< 0 = disabled)"));
```
No `set_limits`, no `set_hard_limits`, no handler; the value is stored straight
into the float `params.sampling.top_n_sigma`. The JSON double 3.5e38 exceeds
float32 max, so storage saturates to FLT_MAX 3.4028234663852886e38. There is no
rejection path because no bounds are declared. Source explains the observed
outcome; this is exactly the A1 `e:generic-conversion` case.

### Prose verdict — ONE PRESCRIPTIVE CLAUSE WRONG
Descriptive half measured true: "declares no explicit bounds … accepted and
saturated to 3.4028e38 instead of being rejected." But the advice sentence
**"clients must keep it finite" is false/overstated**: 3.5e+38 is finite and
still saturates; finiteness does not avoid saturation, only staying at/below
the float32 maximum (~3.4028235e38) or within the semantic range does.
Corrected meaning sentence:
> `top_n_sigma` declares no explicit bounds, so a finite value above the float32
> maximum (~3.4028235e38) is accepted and saturated to 3.4028e38 instead of
> being rejected; clients must keep values within the float32 range or read the
> echoed value, since finiteness alone does not prevent saturation.

### SOURCES / Gate verdict — HOLDS
SOURCES S150 row exists (line 101 declaration; no limits/handler line).
Raw GitHub fetch at 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad sha256 =
`1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` — equals the
pinned snapshot hash and the Gate table's "fetched sha256". Gate quote
(L101+L102 whitespace-joined, 18 words) is verbatim from the fetch.

### Receipt verdict — right
`c1-e49b4cf7-receipt.json` lists F28-11 under `not_counted` with
`why: ["e:generic-conversion"]`. Frozen A1 counter `conversions()` emits
`copysign(FLT_MAX, 3.5e38)` = 3.4028234663852886e38; effective equals it →
`e:generic-conversion` → not counted. This is the correct verdict under A1: the
row is true but carries no field knowledge. Note: response sha256 differs across
runs (registry 27b80f7f…, receipt e04b0cb6…, mine 2897cccbc…) because the body
contains non-deterministic fields (content token, timings, index); the counter
never compares body hashes, so this is not a defect.

## F28-12 — `xtc_probability` = 5.0 (line 104, S151)

### Live re-measure (port 48306)
Row request: base body + `"xtc_probability": 5.0` → **status 200**,
`generation_settings.xtc_probability` = **1.0**; base (omitted) = 0.0.
Response sha256 `5083481c552e060da0a4150b505ff89a6c72e103e01c95209d946814c25f3f16`.
Also probed lower direction `-1.0` → 0.0 (200): the clamp is symmetric, as
`set_limits` implies. Outcome `200, xtc_probability = 1.0` confirmed.

### Source verdict — HOLDS
Pinned L104-105:
```
add((new field_num("xtc_probability", params.sampling.xtc_probability))
    ->set_limits(0.0f, 1.0f))
```
`set_limits` clamps silently (no 400). Source explains the outcome.

### Prose verdict — HOLDS
Cell: "llama-server silently clamps an out-of-range xtc_probability to 1.0 and
still returns HTTP 200, so clients must validate the 0..1 range themselves
instead of expecting an error." Measured (both directions), sourced, no false
or over-general statement. No correction needed.

### SOURCES / Gate verdict — HOLDS
SOURCES S151 row exists (line 104 declaration, limits/handler line 105).
Fetched file sha256 matches pins (above). Gate quote (L104+L105
whitespace-joined, 5 words) verbatim.

### Receipt verdict — right
F28-12 is in `counted_ids` with `why: []`: effective 1.0 ≠ sent 5.0, ≠ any
`conversions(5.0)` (5.0, True, 5, wraps), ≠ base 0.0 → counted. Correct.

## Summary
- F28-11: measured behavior, source, SOURCES/Gate and receipt verdict all hold;
  the SKILL.md meaning cell's prescriptive half ("clients must keep it finite")
  is wrong/overstated — corrected sentence above.
- F28-12: holds fully.
No other actionable defect found in these two rows. Verification gaps: response
sha256 is run-to-run non-deterministic (bodies differ), so byte-level
reproducibility of live responses cannot be asserted; all asserted semantics
(status, effective value, base value) reproduce exactly.
