# RowReview13 — F28-25 (seed, S164) and F28-26 (n_probs, S165), C1 falsify

Seat: KamaR28.RowReview13, wave 2. Port 48313. Server: pinned `~/.local/opt/llama-b11755/llama-server` with `stories260K.gguf` (argv exactly as bound), started under `timeout`, process group killed before return, `ss -ltnp` confirms 48313 free. No tool installs (curl/sha256sum already present). Scratch: `/fast/scratch/hyaku/kama-r28/w2/RowReview13/`.

## F28-25 — seed (line 176, S164)

### Live re-measure (counter-exact request: POST /completion, body BASE_BODY + {"seed": 4294967296})
- status 200, `generation_settings.seed` = 0, response sha256 `7ea268edc48a02e16620cdd5fe3b0987d780474b5d1a8066fb3926bd64ff44b3`.
- Field-omitted base: status 200, `seed` = 4294967295 (default -1 stored as uint32).
- Matches receipt `c1-e49b4cf7-receipt.json`: status 200, effective 0, base_effective 4294967295, body_sha256 `134b3272...` (body hash differs only by request/response timings; effective values identical).

### Source verdict
Declaring lines 175-177: `// seed is uint32_t; field_num uses int32_t so use a handler` + `add((new field_num("seed", params.sampling.seed)) ->set_desc(...))`. No `set_limits`/`set_hard_limits`/`set_handler`. `field_num<T>::eval` (snapshot 531-551) for a limit-less field does `val = data.at(n).get<T>()` with T=uint32_t (min 0, max 4294967295), so 4294967296 is cast to uint32 → 0, accepted 200. The source explains the observed outcome (via the comment at 175 + template eval at 538-539; the declaration line alone does not).

### Prose verdict — FALSE as stated (over-general)
Meaning cell: "Seeds above 4294967295 wrap to 0 through uint32 truncation, so clients must send only uint32-range values and verify generation_settings."
- Only the row's own value wraps to 0. Live probes: seed 4294967297 → `generation_settings.seed` = 1; seed -2 → 4294967294; seed 4294967295 → 4294967295. Values above 4294967295 wrap modulo 2^32, not to 0.
- Corrected meaning sentence: "A seed above 4294967295 is stored modulo 2^32 in uint32 storage (e.g. 4294967296 → 0, 4294967297 → 1), so clients must send only uint32-range values and verify generation_settings."

### SOURCES/Gate verdict
- URL `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp` fetched: sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` = pinned snapshot sha256, equal to Gate table value. ✓
- Gate quote (lines 176+177, whitespace-joined, 13 words) occurs verbatim in the fetched raw. ✓ SOURCES.md S164 row matches the Gate row. ✓

### Counted verdict
Correct: F28-25 is in `not_counted` with `e:generic-conversion`. Effective 0 == `conversions(4294967296)` (`t % 2^32`); the A1 amendment exists precisely to refuse this class. Receipt verdict right.

## F28-26 — n_probs (line 179, S165)

### Live re-measure (counter-exact request: BASE_BODY + {"n_probs": 2.5})
- status 200, `generation_settings.n_probs` = 2, response sha256 `6c439b4d537ecfb9d6b24722ff1aff2a407ab36584318e3d26acc30eb7610477`.
- Field-omitted base: status 200, `n_probs` = 0.
- Matches receipt: status 200, effective 2, base_effective 0, body_sha256 `fbb27187...` (same caveat).

### Source verdict
Declaring lines 179-181: `add((new field_num("n_probs", params.sampling.n_probs)) ->add_alias("logprobs") ...)` with T=int32_t default, no limits; `field_num<T>::eval` → `get<int32_t>(2.5)` → static_cast truncates toward zero → 2, accepted 200. Source explains the observed outcome.

### Prose verdict — Holds
"An fractional n_probs is truncated to its integer part, so clients must send integers and confirm the stored value in generation_settings." Live probes confirm truncation: 2.9 → 2; 0.5 → 0; -0.5 → 0 (truncation toward zero, so negative fractions truncate up — the sentence does not claim otherwise and the row's value is positive). No correction needed.

### SOURCES/Gate verdict
- Same URL fetch as S164 hashes `1f9d7b73...` = pinned sha256. ✓
- Gate quote (lines 179+180, whitespace-joined, 11 words) verbatim in fetched raw. ✓ SOURCES.md S165 row matches. ✓

### Counted verdict
Correct: F28-26 is in `not_counted` with `e:generic-conversion`. Effective 2 == `conversions(2.5)` (`int(2.5)`); A1 refuses it by design. Receipt verdict right.

## Summary
- Both rows: live re-measure reproduces receipt effective values/status exactly; sources explain outcomes; Gate/SOURCES quotes and raw sha256 verbatim; both correctly not counted under A1 (e:generic-conversion).
- One finding: F28-25 meaning cell's "wrap to 0" is a false universal (probe 4294967297 → 1); corrected sentence proposed. F28-26 meaning holds as written.
- No impact on the claim: counted 26 ≥ target 18 regardless of these two rows; not-counted classification is the intended A1 behavior.
