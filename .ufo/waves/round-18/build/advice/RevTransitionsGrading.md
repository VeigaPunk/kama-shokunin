VERDICT: confirm — the routed v3 requirement is correct: the frozen gate provably lets non-exact /v1/models 503s hide in transitions rows and in the dropped (>256-distinct) tail.

Reviewed: frozen copies at `.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py` (tool) and `.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py` (gate), rev `e75cf680b53484a6`. Demo runs below are advice, not verdicts; scratch was under `/tmp/kama-r18-RevTransitionsGrading/` and was removed.

## How the frozen surfaces record a 503

- Tool `_transition_row` (tool:436-449): every poll becomes a row `t_ms, path, status, error, body_sha256, body, body_read_truncated, body_over_cap, headers, repeats`. `body_sha256` is over the raw read (≤ `HTTP_BODY_CAP` 65536, tool:78, tool:443); `body` text comes from `_decode_body` (tool:429-432): "None when body exceeds cap" — cap `TRANSITION_BODY_CAP = 4096` (tool:74), flagged `body_over_cap`.
- Consecutive-dedup in `_observe` (tool:535-545) merges only runs with equal `_sig = (status, error, body_sha256)` and same path; A,B,A yield three rows, so every distinct response keeps its row and body.
- The 503 branch (tool:554-576) fires for any 503 after ownership proof, regardless of path, and (a) dedups into `loading_bodies` by sha ("deduped by sha256 and capped at LOADING_BODY_MAX", tool:142-143; append tool:560-565), (b) silently TRUNCATES to a 4096-byte prefix for the log and `loading_503` (`result['body'][:TRANSITION_BODY_CAP]`, tool:555-556, stored tool:564/tool:575) with **no over-cap flag on those two surfaces**, and (c) is the only writer of `loading_503` (first 503, tool:568-576).
- Past `LOADING_BODY_MAX = 256` distinct bodies (tool:75): `loading_bodies.dropped += 1` (tool:567); the body survives only as its transitions row. Count lands in the receipt (tool:1151-1152).
- Producer's own check predicate (tool:1352-1354): `loading_observed is True and loading_envelopes_all(bodies) is True` — "every distinct captured 503 body is the exact envelope" (tool:231-233) — **dropped bodies are absent from the predicate**; `bodies_dropped` is only narrated in `observed` (tool:1356).
- Gate loading block (gate:423-464): `loading_503.status == 503`, path in `/v1/models|/health`, `loading_observed` ⟺ `loading_503` present ⟺ "transitions … status-503 row" (`has_503_transition = any(`, gate:441-450); `want_lef` re-derived from the `loading_503` body only (gate:455-457).
- Gate v2 `loading_envelope_graded` (gate:908-940): `want_lef is not True` → bad; `all_exact` over `loading_503_bodies` — "a stored loading_503_bodies entry is not the exact envelope" (gate:933-934); `observed.exact` cross-checked (gate:936-940). **No other 503 grading exists**: `validate()` touches transitions rows only for the status peek (gate:437-450); `loading_bodies_dropped` has zero occurrences in the gate (grep).

## Findings (by severity)

**F1 — HIGH, hiding spot (demonstrated): transitions-row 503 bodies are never graded.** The gate reads transitions rows only for `status == 503` existence (gate:441-443). Executed proof, built on the gate's own valid v2 selftest receipt, frozen gate run unchanged:
- A1 (`transitions[1].body` → `{"error":{"message":"Warming up",…,"code":429}}`, sha left stale): exit 0 VALID — the gate never parses or re-derives a row body, not even against its own sha.
- A2 (row replaced by a genuinely distinct non-exact 503, true sha, absent from `loading_503_bodies`): exit 0 VALID — there is no coverage join row↔log.
The selftest has no mutant altering only a row body; `v2-loading-503-nonexact-transitions` also edits `loading_503` and is caught via `want_lef` (gate:1297-1303). Honest producers cannot produce A1/A2 (every distinct proven sha is appended to the log, tool:560-565), so the gap is forgery-tolerance today — and becomes a real hole in combination with F2.

**F2 — HIGH, hiding spot (demonstrated): the 257th distinct body.** Dropped bodies are counted, never graded: the producer predicate omits `dropped` (tool:1352-1354) and the gate never reads `loading_bodies_dropped` (grep: 0 hits). Demo B (`loading_bodies_dropped=1`, non-exact 503 present only as a transitions row): exit 0 VALID. Demo B2 additionally announces `observed.bodies_dropped = 0` against receipt field 1: exit 0 VALID (gate checks only `observed.exact`, gate:936-940). So any non-exact 503 arriving after 256 distinct bodies passes every grade on every surface. [INFERENCE on reachability: a real b11755 run "shows dozens" of distinct bodies (tool:142), so 256 is headroom — but the v3 contract must close the path regardless.]

**F3 — MEDIUM: `loading_bodies_dropped` counts responses, not distinct bodies.** A dropped sha is never inserted into `_seen_503`, so every later occurrence re-increments `dropped` (branch order tool:558-567). v3 must pin the semantics ("unrecorded 503 responses; ≥1 distinct") or record dropped shas, else a `dropped: 400` receipt overstates distinct non-exact candidates and a `dropped: 1` understates nothing.

**F4 — MEDIUM: asymmetric over-cap encoding makes one of the two surfaces un-gradable.** Transitions row: `body=None, body_over_cap=True` (tool:429-432, tool:446). Log/`loading_503`: silent 4096-byte prefix, no flag (tool:555-556, tool:564, tool:575). The sha is over the full read (tool:443), so the row text cannot be re-derived from the sha, and the gate can only ever grade a prefix. Bounded impact: the documented envelope is a ~80-byte fixed JSON (gate:973-981), so any real >4096-byte "loading" body is by construction non-envelope and the prefix parse fails → correctly non-exact; false-exact survives only as envelope + trailing whitespace beyond 4096 (json.loads accepts trailing whitespace), which is semantically still the documented document.

**F5 — LOW: `observed.bodies_dropped/distinct_bodies/total_503_responses` unverified** (gate:936-940 checks only `exact`) — demonstrated by B2.

**F6 — LOW, residual: read-cap collision.** sha over first 65536 bytes only (tool:78, tool:409-411, tool:494-497); two 503 bodies differing only after byte 65536 collapse into one distinct entry, and `body_read_truncated` is never graded. Contrived; note as a documented limit.

**F7 — INFO: `/health` 503s share the same log.** The 503 branch does not filter by path (tool:554) and the gate accepts `loading_503.path == "/health"` (gate:433-435). A non-exact 503 served on `/health` hides through the identical F1/F2 holes; the v3 per-row rule should cover every 503 row, not only `/v1/models`.

**F8 — INFO: transitions rows have no schema validation.** A forged `[{"status": 503}]`-style row satisfies the only transitions rule (gate:438-450). Per-row grading in v3 needs row well-formedness (types of `body`, `body_sha256`, `body_over_cap`) defined first.

D1 interaction (no defect): ownership-failure receipts have rows with `body=null, body_sha256=null` (`_discard_bodies`, tool:613-624) — but those receipts are already INVALID because `port_listener_ownership` ≠ child ("requires the ready listener proven to be our child", gate:470-472), so the v3 row rule may condition on sha presence without opening a hole.

## Required v3 gate grading spec (deliverable)

Grade `loading_envelope_graded` as the conjunction of (1)-(7). Any conjunct false → re-derivation false; since v2/v3 are pass-only ("check {cid!r}: passed is false" → bad, gate:647-650, `claim` mismatch → bad, gate:662-669), a false conjunct makes the receipt INVALID (gate exit 1).

1. **want_lef** — unchanged from frozen (gate:455-457, gate:913-919): `loading_503` body re-derives exact.
2. **all_exact** — unchanged (gate:922-934): every `loading_503_bodies` entry exact.
3. **dropped == 0** — require `receipt.loading_bodies_dropped == 0` whenever the check is graded. Dropped>0 means ungraded 503 responses existed; the check cannot re-derive true. Tool-side companion (advice to the C1 seats): add `receipt.get('loading_bodies_dropped', 0) == 0` to the predicate at tool:1352-1354 so such a run honestly emits `passed=false` → tool exit 1, instead of passing with a hidden tail.
4. **Per-row grading** — every transitions row `t` with `t.status == 503` (both paths; F7):
   a. well-formed: `t.body` str|null, `t.body_sha256` hex64|null, `t.body_over_cap` bool (F8);
   b. `t.body` str → `loading_envelope_ok(parse_body(t.body))` must be True — the row's own verbatim text is authoritative (closes A1/A2);
   c. `t.body` null with `body_over_cap` true → join by `t.body_sha256` into `loading_503_bodies`; joined entry must exist and grade exact. This is prefix-grading of a >4096-byte body (F4); correct because the documented envelope is ~80 bytes, and the only accepted false-exact is trailing whitespace past the cap — record that as a stated limit in the receipt doc;
   d. `t.body_sha256` null rows are D1-discarded and only exist in already-INVALID receipts (gate:470-472); no grading needed.
5. **Coverage join (anti-forgery)** — with dropped==0: the set of `body_sha256` over all 503 rows == the set of shas in `loading_503_bodies` == `{loading_503.body_sha256}` ∪ …; every log entry traces to ≥1 row and vice versa (closes A2/B structurally, even before grading).
6. **Cross-surface text equality** — for in-cap bodies the row text and its log entry text must be identical: both are the same verbatim body (`_decode_body` tool:429-434 vs `[:TRANSITION_BODY_CAP]` tool:555-556 coincide for ≤cap). A mismatch proves one surface was altered → INVALID.
7. **Observed cross-check** — keep `observed.exact == want_lef` (gate:936-940) and add `observed.bodies_dropped == receipt.loading_bodies_dropped`, `observed.distinct_bodies == len(loading_503_bodies)`, `observed.total_503_responses == Σ(1 + repeats)` (closes F5/B2).

Exit mapping, grounded in the frozen rules: exit 0 — all evaluated checks re-derive true; exit 3 — every evaluated check re-derives true and the only shortfall is the legitimately-null `loading_envelope_graded` (`loading_observed` false, `passed: null`, `observed.not_evaluated_reason: "no-loading-503-observed"`, per the v3 contract); exit 1 — any structural violation, re-derivation mismatch, or false conjunct above; exit 2 — unreadable. Truncated-body and 257th-body outcomes under this spec: over-cap body → graded via sha-join (4c), never silently passed; 257th+ distinct body → blocked by (3), so an honest producer must either raise `LOADING_BODY_MAX` or emit `passed=false` (tool exit 1) — never a passing receipt with a hidden tail.

## Residual risk and verification gaps

- Trailing-whitespace-past-cap false-exact (F4c) is intrinsic to 4096-byte prefix storage; semantically harmless, should be a documented limit, not fixable by the gate alone.
- 65536-byte read-cap sha collision (F6) stands; closing it needs a full-read sha or graded `body_read_truncated`, out of the routed scope.
- I did not run llama-server b11755 to measure real distinct-body counts; "dozens" is taken from the tool's own DOC anchor (tool:142-143). Reachability of dropped>0 on real runs is [INFERENCE].
- Duplicate-JSON-key bodies grade by json.loads last-key semantics identically on tool and gate (both json.loads) — no surface divergence; not a hiding spot.
- Demo receipts were derived from the gate's internal `_selftest_receipt_v2()` and run against the frozen gate with host Python 3.14.8; outputs quoted verbatim above. Advice only; L1 owns official measurement.

Installs: none. Scratch `/tmp/kama-r18-RevTransitionsGrading/` removed after the demo.
