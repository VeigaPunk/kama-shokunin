# RowReview07 — C1 falsify: F28-13 (temperature), F28-14 (dynatemp_exponent)

Port 48307, pinned server `~/.local/opt/llama-b11755/llama-server` + `stories260K.gguf`, argv exactly as bound. Counter's exact request (POST /completion, `{"prompt": "Once upon a time", "n_predict": 1}`) + the row's `set`, and the field-omitted base. No installs needed (tooling directive: none performed).

## 1. Live re-measure (I ran it)

| Row | request | status | effective (generation_settings) | base (field-omitted) | response sha256 |
|---|---|---|---|---|---|
| F28-13 | + `"temperature": -1.0` | 200 | `temperature = 0.0` | `0.800000011920929` | `e61c031fb18595609f77d8b7d9d6f20be812b1050a098fa9817142cba7e682eb` |
| F28-14 | + `"dynatemp_exponent": 1e+39` | 200 | `dynatemp_exponent = 3.4028234663852886e+38` | `1.0` | `404b387d807700d646cf22c4cf4aa592bbed833842e4ab882f141e318beea62e` |

Both match the registry `live_by_seat` and the receipt's `live` on status and effective/base values exactly. (Body sha256 differs run-to-run — seat/receipt/mine — because the completion body embeds stochastic sample content; the semantic parts match. Not a defect.)

## 2. Source verdict (pinned snapshot .ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp, sha256 1f9d7b73…4050)

- **F28-13** line 116-117: `new field_num("temperature", params.sampling.temp)) ->set_limits(0.0f, std::numeric_limits<float>::infinity())`. `set_limits` = soft limits → silent clamp; -1.0 clamps to the lower bound 0.0, 200. **Source explains the observed outcome exactly.**
- **F28-14** line 123-124: `new field_num("dynatemp_exponent", params.sampling.dynatemp_exponent)) ->set_desc("Dynamic temperature exponent, controls how entropy maps to temperature"))`. No limits declared → nothing to reject; stored value is the plain float32 conversion of 1e39 → FLT_MAX (3.4028234663852886e38). **Source explains the observed outcome exactly.**

## 3. SKILL.md prose verdict (rows at SKILL.md:1172-1173)

- **F28-13**: "llama-server silently clamps a negative temperature to 0.0 (greedy decoding) with HTTP 200, so clients should reject negative values before sending them." — supported by measurement and by `set_limits` + "0 = greedy" desc; no over-generalization (section intro scopes to b11755 fixture). **Holds; no correction needed.**
- **F28-14**: "A dynatemp_exponent beyond the float range is silently saturated to 3.4028234663852886e+38 in generation_settings instead of being rejected, so clients must read the echoed value rather than assume the sent number took effect." — 1e39 > FLT_MAX, no limits, 200, echo value confirms; claim scoped to generation_settings (not sampling effect), per the section intro. **Holds; no correction needed.**

## 4. SOURCES/Gate verdict

- SOURCES.md rows S152 (line 164) and S153 (line 165) cite `server-schema.cpp` lines 116/123 @ 704366d76 with raw sha256 `1f9d7b73…4050`; quotes match the Gate table (round-28.md:90-91, lines L/L+1 whitespace-joined, cut to 25 words) and the pinned snapshot verbatim.
- **URL fetch**: raw `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp` fetched → sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` == pinned snapshot hash == hash quoted in Gate/SOURCESURES. Declaring lines confirmed at 116-118 and 123-125 in the fetched file. **Holds verbatim.**

## 5. Counting verdicts (final/c1-e49b4cf7-receipt.json)

- **F28-13**: counted (counted_ids), `why: []`. Right: effective 0.0 is not any generic conversion of -1.0 (conversions(-1.0) = {True, -1.0, 4294967295}; 0.0 is the declared soft minimum clamp → field knowledge).
- **F28-14**: not counted, `why: ["e:generic-conversion"]`. Right under amendment A1 (preregistration `pre_data_amendment_A1` explicitly names dynatemp_exponent float32 saturation 1e39 → 3.4028e38): 3.4028234663852886e38 == `conversions(1e39)` FLT_MAX entry, so it is true but not counted as field knowledge. The SKILL.md row remains present and truthful; the section intro covers this ("Rows whose stored value is only a generic type conversion … are true but not counted"). Claim still met (26 ≥ 18).

## Findings (severity: none)

No actionable finding: both rows are real, correctly sourced, correctly measured, correctly counted/not-counted, and their meaning cells are supported. Verification gaps: none beyond the inherent single-port single-run nature (reproduced the receipt's semantics exactly).
