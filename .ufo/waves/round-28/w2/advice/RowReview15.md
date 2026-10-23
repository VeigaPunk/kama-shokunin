# RowReview15 — FALSIFY C1 rows F28-29 / F28-30 (verdict: both hold)

Seat: KamaR28.RowReview15, port 48315, pinned llama-server b11755 (argv exactly as
specified), model stories260K.gguf (sha256 270cba1…), pinned snapshot
server-schema.cpp sha256 1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050
(verified == GitHub raw fetch at 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad). No tool
installed (none needed). No lane edits; scratch evidence under
/fast/scratch/hyaku/kama-r28/w2/RowReview15/.

## F28-29 (preserved_tokens, SKILL.md line 1188, S168)

1. **Live re-measure (port 48315, counter body {prompt, n_predict:1}):**
   - field-omitted base: HTTP 200, `generation_settings.preserved_tokens = []`
     (response sha256 715ec2383c6a02ffc52ef83fe883996e4f747a4a8caffdde14aa7d1accef4b09).
   - + `"preserved_tokens": ["upon","upon","a"]`: HTTP 200, effective `[261, 407]`
     (response sha256 935c0956e49d077b4ab08f6bc4379e33c9b3fb4a384d525bee8b30ab5bd4fb00).
   - Variants: `["a","upon","a"]` and `["upon","a"]` both → `[261, 407]`
     (order-insensitive, duplicates collapse → set semantics, ascending ids).
   - Matches registry `live_by_seat` (200, [261,407]) and L1 receipt `live`
     (200, effective [261,407], body_sha256 972939ea…; body hash differs only
     because the 200 body includes per-run timings — verified, not a defect).
2. **Source verdict:** pinned schema line 316-320 declares
   `field_json("preserved_tokens")` with `set_desc("List of token strings that must
   not be split during tokenization")`; the handler (line 319) forwards to
   `common_sampling_add_preserved_tokens`, which is outside the pinned snapshot
   (only server-schema.cpp/h, server-task.cpp pinned). Bounds/limits: none — the
   field has no limits, so value storage behavior is impl-level. Source explains
   the outcome: a JSON-array echo field holding the kept token ids; the drop
   semantics are not visible in the pinned declaring lines (verified live instead).
3. **Meaning cell attack** ("Only strings that tokenize to exactly one token are
   kept, as ascending llama_token ids de-duplicated in a set, so send one-token
   strings and read preserved_tokens back to see what was kept."):
   - `/tokenize` probes: "a"→[261] (1 token), "upon"→[407] (1 token), so 261/407
     are exactly the two sent strings.
   - Multi-token candidates "unlikelyword" (10 tokens), "xyzzyqqq" (9),
     "Tokenization" (9), "未来" (7), "a b" ([261,268]) all → `preserved_tokens=[]`
     (dropped, HTTP 200). Claim "only single-token strings are kept" **holds**.
   - Dedup + ascending order claim **holds** (order-insensitive, duplicates
     collapse, emitted sorted by llama_token id).
   - No false, unsupported, or over-general statement found. No correction needed.
4. **SOURCES/Gate verdict:** SOURCES.md S168 (line 180) URL
   `…/tools/server/server-schema.cpp#L316`; raw fetch sha256 == 1f9d7b73… == pinned
   snapshot. Gate quote (round-28.md line 106) = pinned lines 316–317
   whitespace-joined, `add((new field_json("preserved_tokens")) ->set_desc("List of
   token strings that must not be split during tokenization")` — holds verbatim.
5. **Counted?**

: F28-29 is in `counted_ids` (receipt line 26, why=[]). Verdict right:
   static clauses (a)-(c) hold (SKILL row cells match canon JSON; S168 row new,
   line 316 declares field via `new field_json`; unique line/field), and the live
   clause (d) reproduces (200, effective == outcome value, != sent/omitted
   default/conversion).

## F28-30 (reasoning_budget_tokens, SKILL.md line 1189, S169)

1. **Live re-measure:** field-omitted base HTTP 200 (no `reasoning_budget_tokens`
   key echoed in generation_settings); + `"reasoning_budget_tokens": -2` → HTTP
   400, message `Field 'reasoning_budget_tokens': Value must be between -1 <= value
   <= 2147483647, but got -2` (response sha256 9c6ad502b6f1f4a7cfc44112ac21a4757497d4504520cfd409062ed22571f6b5 — **identical** to registry and L1
   receipt; error bodies are deterministic, so the exact byte match independently
   confirms the same server build and behavior).
   - Context probes: -1 → 200 (accepted, disabled per schema desc), 0 → 200,
     2147483648 → 400 with same bounds message (shows the upper bound is hard too).
2. **Source verdict:** pinned schema line 335-336 declares
   `field_num("reasoning_budget_tokens", params.sampling.reasoning_budget_tokens))
   ->set_hard_limits(-1, INT32_MAX)`; the observed 400 message text and bounds
   (-1, 2147483647 = INT32_MAX) come straight from this hard-limit declaration.
   Source fully explains the outcome.
3. **Meaning cell attack** ("A reasoning_budget_tokens value below -1 is rejected
   with HTTP 400 by the hard limit, so clients must send -1 to disable the budget
   and never rely on a silent clamp."): verified live (-2 → 400, -1 → 200;
   `set_desc("… -1 = disabled)")` in the schema). No false/unsupported/over-general
   statement. No correction needed.
4. **SOURCES/Gate verdict:** SOURCES.md S169 (line 181) URL `#L335`; raw sha256
   == pinned. Gate quote (round-28.md line 107) = pinned lines 335–336 joined,
   `add((new field_num("reasoning_budget_tokens", params.sampling.reasoning_budget_tokens)) ->set_hard_limits(-1, INT32_MAX)` — holds verbatim.
5. **Counted?** F28-30 is in `counted_ids` (receipt line 27, why=[]). Verdict
   right: clauses (a)-(c) hold (S169 row new, line 335 declares field; reject
   outcome text `reject 400, bounds -1 to 2147483647` matches canon), live clause
   (d) holds (400 + REJECT_RE bounds match).

## Findings (by severity)

- **No defect found.** Both rows are true, reproducible, source-consistent, and
  correctly counted. The SKILL.md meaning cells — the only prose the counter does
  not judge — survive attack: F28-29's "only single-token strings are kept"
  claim was stress-tested with five multi-token/OOV sets (all dropped, 200); the
  ascending/member-dup claim holds under reordered and duplicate inputs. F28-30's
  "never rely on a silent clamp" claim holds (hard 400 at both bounds).

## Residual risk / verification gaps

- The drop/keep semantics of `preserved_tokens` live in
  `common_sampling_add_preserved_tokens` (common/sampling.cpp), not in the pinned
  snapshot; behavior verified black-box only. A deep-code claim (e.g. "must not
  be split during tokenization" actually altering tokenization) is not testable
  from the pinned files with this model.
- `reasoning_budget_tokens` is never echoed in `generation_settings`, so the
  "send -1 to disable" advice is grounded in the schema description, not an
  observable stored value — consistent with the row being a reject row.
- Response sha256 of 200 bodies (F28-29) differs run-to-run because of embedded
  timings; only reject-body hashes are byte-stable. Not a consistency failure.
