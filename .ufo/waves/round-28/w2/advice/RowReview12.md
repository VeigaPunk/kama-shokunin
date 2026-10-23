# RowReview12 — F28-23 (adaptive_target, S162) & F28-24 (adaptive_decay, S163)

Seat: KamaR28.RowReview12, port 48312, pinned llama-server b11755 + stories260K.gguf.
Verdict per row: **holds** on every attack axis. No actionable finding.

## F28-23 — adaptive_target (set 5.0, S162, line 167)

1. Live re-measurement (POST /completion, counter-exact body):
   - var: `{"prompt":"Once upon a time","n_predict":1,"adaptive_target":5.0}` -> status 200,
     `generation_settings.adaptive_target = 1.0`, response sha256 `85b5bc96…f4fae`.
   - base (field omitted): status 200, `adaptive_target = -1.0` (server default).
   - Matches registry `live_by_seat` (200, effective 1.0, base -1.0). The 200-body sha256
     differs between runs (sampled text varies); the counter only uses `effective`, not the hash.
2. Source verdict: pinned snapshot lines 167-169 declare the field and
   `->set_limits(-std::numeric_limits<float>::max(), 1.0f)` (soft limits: clamp, not reject —
   same mechanism as counted F28-08 top_k). Source fully explains the observed 200/1.0.
3. Prose verdict: SKILL.md meaning cell "Values above the soft maximum are silently clamped to
   1.0, so clients must expect 200 and read generation_settings instead of a validation error" is
   supported by measurement and source; not false, not over-general. No correction needed.
4. SOURCES/Gate: SOURCES S162 (blob URL #L167, "line 167 declaration, limits/handler line 168")
   correct. Gate S162 quote = snapshot lines 167-168 whitespace-joined verbatim
   (`add((new field_num("adaptive_target", params.sampling.adaptive_target)) ->set_limits(-std::numeric_limits<float>::max(), 1.0f)`).
   Raw URL fetched -> sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`
   == pinned snapshot. Holds verbatim.
5. Counted: yes, in `c1-e49b4cf7-receipt.json` (`counted_ids`), why [] — verdict right.
   1.0 is not a generic conversion of 5.0 (A1), not identity, not default.

## F28-24 — adaptive_decay (set 1.5, S163, line 171)

1. Live re-measurement:
   - var: `{"prompt":"Once upon a time","n_predict":1,"adaptive_decay":1.5}` -> status 400,
     error "Field 'adaptive_decay': Value must be between 0.000000 <= value <= 0.990000, but got
     1.500000", response sha256 `dda12a91522c46772957adba72eda2549150fc4bada90636e131802924975b19`
     — byte-identical to registry `live_by_seat` and the final receipt (deterministic 400 body).
2. Source verdict: snapshot lines 171-173 declare the field and
   `->set_hard_limits(0.0f, 0.99f)` (hard limits: reject with 400 naming bounds). Explains outcome exactly.
3. Prose verdict: SKILL.md meaning cell "Values above 0.99 are rejected with HTTP 400, so clients
   must keep adaptive_decay within 0.0 through 0.99 before sending" is supported; note the lower
   bound 0.0 is equally enforced (cell omits it but says nothing false). No correction needed.
4. SOURCES/Gate: SOURCES S163 correct ("line 171 declaration, limits/handler line 172"). Gate S163
   quote = lines 171-172 whitespace-joined verbatim
   (`add((new field_num("adaptive_decay", params.sampling.adaptive_decay)) ->set_hard_limits(0.0f, 0.99f)`).
   Raw URL sha256 matches pinned (above). Holds verbatim.
5. Counted: yes, in receipt (why []), verdict right — reject with source-derived bounds.

## Residual risk / verification gaps
- None material. 200-row response sha256 nondeterminism is expected and not part of the counter's
  checks (effective value is).
- F28-24 lower-bound rejection (e.g. -0.1) not re-measured; implied by `set_hard_limits(0.0f,…)`
  and message format; not needed for the row's claim.
