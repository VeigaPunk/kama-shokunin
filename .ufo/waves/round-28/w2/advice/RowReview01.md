# RowReview01 — F28-01 (`sse_ping_interval`), F28-02 (`n_predict`) — C1 attack

**Verdict: both rows HOLD.** No wrong/overstated/harmful statement found in either row, its SKILL.md meaning cell, its SOURCES row, or the receipt verdict.

## Live re-measure (port 48301, counter's exact request, `~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48301`)

| probe | body (POST /completion) | status | message | body sha256 |
|---|---|---|---|---|
| base (field-omitted) | `{"prompt":"Once upon a time","n_predict":1}` | 200 | — (generation_settings present) | `b51715586f7baacf696b188d80d625d0088253d3f74e3b0cc2be928d43dd78c0` |
| F28-01 | base + `{"sse_ping_interval":-2}` | **400** | `Field 'sse_ping_interval': Value must be between -1 <= value <= 2147483647, but got -2` | `c7d2e2768ee89048cd8ac2cacfb97a56915fe0e6a3e0d482eecbc1791b8a6197` |
| F28-02 | base with `"n_predict":-2` (merge replaces base 1) | **400** | `Field 'n_predict': Value must be between -1 <= value <= 2147483647, but got -2` | `0a238b5697acbad86983ab80e170aabd82e102d1ca65d9aba9505f7f7c686a33` |

Both error-body sha256 are **byte-identical** to the receipt (`c1-e49b4cf7-receipt.json` rows F28-01/F28-02 `live.body_sha256`) and to the registry `live_by_seat.response_sha256`. Re-measurement reproduces the seat data exactly.

## Source verdict (pinned snapshot `sources/llama.cpp-704366d/server-schema.cpp`)

- F28-01: lines 40–41 declare `add((new field_num("sse_ping_interval", params.sse_ping_interval)) ->set_hard_limits(-1, INT32_MAX)` (desc line 42: "‑1 disables pings").
- F28-02: lines 44–45 declare `add((new field_num("n_predict", params.n_predict)) ->set_hard_limits(-1, INT32_MAX)`.

Raw GitHub fetch of `tools/server/server-schema.cpp` at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` hashes `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` = pinned snapshot sha; lines 40/41 and 44/45 byte-match the snapshot. The hard limits `-1..INT32_MAX` fully explain the observed reject-with-400 (message carries the same bounds). Source verdict: **explains**.

## Prose verdict (SKILL.md meaning cells)

- F28-01 (line 1160): "A negative value below -1 is refused outright with HTTP 400 instead of being clamped, so clients must send -1 to disable SSE pings or a non-negative interval." — **true**: measured 400 for -2; backend descriptor and pinned README (line 606, `‑1 disables pings`) support the -1 disable semantics.
- F28-02 (line 1161): "n_predict below -1 is rejected with HTTP 400 and not clamped, so clients asking for unbounded generation must send exactly -1 and never a smaller integer." — **true**: measured 400 for -2; pinned README line 532 ("Default: `-1`, where `-1` is infinity") supports "unbounded generation = -1". Not fixture-specific over-generalization: both sentences are scoped to this build's request-field table and match both measurement and source.

No corrected meaning sentence needed.

## SOURCES / Gate verdict

- SOURCES rows S140/S141 (corpus/SOURCES.md lines 152–153): URL is the correct blob link (`...#L40`/`...#L44`) at the pinned commit; quote `add((new field_num(...)) ->set_hard_limits(-1, INT32_MAX)` is verbatim (lines L and L+1, whitespace-joined) against the fetched file; sha matches. **Holds.**
- Gate table (lessons/round-28.md S140/S141): field/line/quote match the file; per-row "accessed (UTC)" timestamp is historical and not re-verifiable, but the sha256 binding is the load-bearing evidence. **Holds.**

## Receipt verdict

F28-01 and F28-02 are both in `counted_ids` of `final/c1-e49b4cf7-receipt.json` (registered 34, counted 26, met True). That verdict is **right**: the counter's reject check (status 400; `REJECT_RE` field name == registry field; bounds parse to -1/2147483647 within `same()` float32 tolerance) passes for both, matching my independent reproduction byte-for-byte.

## Residual risk / gaps

- None material. Only non-re-verifiable item is the historical "accessed" timestamp in the Gate table; it does not affect the claim.
- Teardown: my server killed (SIGTERM then SIGKILL to its process group), `ss -ltnp` confirms port 48301 free; other llama-server processes on 48306/48307/48312/48313/48314/48315/48316 belong to sibling peers and were not touched. No tools installed.
