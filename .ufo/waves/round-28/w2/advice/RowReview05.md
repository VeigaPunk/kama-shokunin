# W2 RowReview05 — C1 rows F28-09 (top_p, S148) and F28-10 (min_p, S149) — FALSIFY

Seat: KamaR28.RowReview05, 2026-10-23. Attack surface: live re-measure on own port 48305
(pinned `~/.local/opt/llama-b11755/llama-server`, `stories260K.gguf`, default argv, exact
counter request `POST /completion {"prompt":"Once upon a time","n_predict":1}` + row `set`),
pinned snapshot `.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp`, SKILL.md
`## Round-28 request-field outcomes` (SKILL.md:1135-1169), SOURCES S148/S149
(corpus/SOURCES.md:160-161), Gate table (corpus/lessons/round-28.md), frozen A1 receipt
(`.ufo/waves/round-28/final/c1-e49b4cf7-receipt.json`). Raw probes + fetched snapshot:
`/fast/scratch/hyaku/kama-r28/w2/RowReview05/`. Server process group killed before return
(`ss -ltnp`: 48305 free). No installs performed (nothing needed).

## Verdict per row: HOLDS (no defect found)

### F28-09 — top_p, set 2.5, outcome `200, top_p = 1.0` (SKILL.md:1168, S148)

1. Live re-measure (my port 48305): HTTP 200, `generation_settings.top_p = 1.0`
   (field-omitted base: 0.949999988079071); other sampling keys unchanged (min_p stayed
   0.05000000074505806). Response sha256 `97ef004752576ded6bcab041e539450f6a3c82844d0045a8818a026cd32b8a98`
   (base `56cbdd5f0979841bb0d585a163b1b2540e52abc9db3e10927f6095864c095e91`).
   Matches registry `live_by_seat` (200 / effective 1.0 / base 0.949999988079071) and the
   receipt `live` block. Response body sha256 is per-run nondeterministic (timings/tokens);
   the counter checks values, not hashes, so the recorded seat sha256 is an artifact, not a
   defect.
2. Source: snapshot L93 `add((new field_num("top_p", params.sampling.top_p))`, L94
   `->set_limits(0.0f, 1.0f)` — soft limits. L538-539: `!is_hard_limit` ⇒
   `val = std::max(min, std::min(max, data.at(n).template get<T>()))` — silent clamp, no
   throw; hard limits (L541-544) would throw `Value must be between …`. 2.5f clamps to
   1.0f exactly. Source fully explains the observation.
3. Meaning cell: no false statement found. "clamped silently to its soft maximum" matches
   set_limits/L539 semantics; "(sampling disabled)" matches the field's own L95 desc
   "(1.0 = disabled)"; "rather than rejected" matches observed 200; the guard
   "One request per field: a row is one observed point" (SKILL.md:1155-1157) contains the
   over-generalization risk, and the section preamble (SKILL.md:1143-1146) already scopes
   "served with" to the value stored in the response's `generation_settings`, "not proof
   that sampling used it". No correction required.
4. SOURCES/Gate: raw URL fetched twice (per-attack leg), sha256 both times
   `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` = pin = SOURCES S148
   raw sha256. Gate quote = L93+L94 whitespace-joined, verbatim in the fetched file, ≤25
   words. "limits/handler line 94" is accurate (L94 sets the limits the generic clamp
   handler at L539 applies). Gate row (DataG03, 08:32:44Z) consistent.
5. Receipt: F28-09 in `counted_ids` (26 counted), `why: []`. Correct: not identity (1.0 ≠
   2.5), not a generic conversion (A1 `conversions(2.5) = [True, 2.5, 2, 2, 2, 2, 2]`,
   recomputed with the counter's own algorithm — no 1.0), not default (1.0 ≠ 0.95 base).

### F28-10 — min_p, set -1.5, outcome `200, min_p = 0.0` (SKILL.md:1169, S149)

1. Live re-measure (port 48305): HTTP 200, `generation_settings.min_p = 0.0` (base
   0.05000000074505806; top_p unchanged at 0.949999988079071). Response sha256
   `e34a7da117a581aaec05b488dd464950464a68a40552db6042ce34ee994c9b59`. Matches registry
   `live_by_seat` and receipt `live` (base_effective 0.05000000074505806).
2. Source: L97 `add((new field_num("min_p", params.sampling.min_p))`, L98
   `->set_limits(0.0f, 1.0f)`; clamp at L539 gives max(0.0f, min(1.0f, -1.5f)) = 0.0f.
   Source fully explains it.
3. Meaning cell: no false statement found. The distinctive clause "a value no truncation
   of the request yields" is true: truncation of -1.5 is -1, and A1
   `conversions(-1.5) = [True, -1.5, -1, 4294967295, -1, 18446744073709551615, -1]` — no
   0.0; this clause is exactly what distinguishes the row from `e:generic-conversion`.
   "(disabled)" matches L99 desc "(0 = disabled)". No correction required.
4. SOURCES/Gate: same fetched sha256 equals pin and S149's raw sha256; Gate quote L97+L98
   verbatim; "limits/handler line 98" accurate.
5. Receipt: F28-10 in `counted_ids`, `why: []`. Correct: not identity, not generic
   conversion, not default (0.0 ≠ 0.05).

## Residual risks / gaps

- "served with X" in both meaning cells is defensible only because the section preamble
  scopes it to `generation_settings`; read alone, "served" could suggest sampling used the
  value. The preamble disclaimer covers it; no edit proposed.
- `same()` tolerance is 1e-6 relative; effective values here are exact, so no tolerance
  sensitivity was exercised for these two rows.
- The one-point-per-field disclaimer (SKILL.md:1155-1157) is what keeps "clients must
  check 0.0..1.0" from being a full response-function claim; it holds only as advice, and
  extreme magnitudes (e.g. 1e39 → float inf) were not probed by this seat.

Bottom line: both rows' live outcomes reproduce, the pinned source explains both via the
soft-limit clamp at server-schema.cpp:539, the prose cells contain no unsupported
statement, the SOURCES quotes and sha256 pins verify verbatim, and both rows are rightly
counted in `c1-e49b4cf7-receipt.json`. Attack failed; C1 rows F28-09/F28-10 hold.
