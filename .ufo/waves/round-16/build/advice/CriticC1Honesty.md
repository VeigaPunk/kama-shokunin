# CriticC1Honesty — round 16 C1 (calibration) attack

Seat: critic, read-only. This is advice, not a verdict. I ran no lane gate, harness or probe. The live
`tools/kama-probe.sh` was being edited while I read it; the snapshot was tag `#6F71`. Frozen cites point
at `.ufo/waves/round-16/frozen/kama-probe-before.sh` (sha `93ee4302…cd64`).

Axes I attacked: calibration (the claim's axis), operability (the C2 axis, which C1 could collapse into),
and freshness/adjacency only where they are harmed.

## Verdict in one line
C1 counts as calibration **only if** its before→after measures the skill's own false assertion, not just
the classifier's new branch. As currently worded, the code change adds an edge class, which is
operability/coverage. The repaired evidence text also replaces one absolute overclaim with its opposite.
Score **7→7 is honest. 8 is not earned.**

## Findings

### F1 — Classification risk: C1 can be read as operability, which collapses the round (AXES rule)
- `AXES.md:15` defines calibration as "Self-assessment quality: gaps named honestly, confidence graded,
  overreach caught | SHONEN.md/SCORECARD entries match observed repo state".
- `AXES.md:13` defines operability as "Runnable artifacts … scripts that run … produces the stated outcome".
  A new classifier branch is that.
- `AXES.md:31-33`: "two claims on one axis in one round count as one claim. At least one claim works the
  lane's lowest-scoring non-retired axis". If C1 is judged operability, then C1 + C2 = one operability
  claim. Calibration (7, the lowest) would go unworked, and the round would not be admissible.
- **What saves the framing:** the lane's own docs contradict each other, and the lane already had the
  evidence.
  - `corpus/knowledge/endpoint-identity.md:17` (rule 5) says: "Any non-`2xx` HTTP status other than
    `401`/`403` … `FOREIGN_SERVICE` … A live HTTP error response from a non-model service is foreign".
  - `corpus/knowledge/runtime-health-surface-matrix.md:14` already records: "503 `unavailable_error`
    "Loading model" while loading".
  - The frozen probe prints that overclaim to operators at `frozen/kama-probe-before.sh:522`:
    "(non-2xx HTTP from a non-model service)".
  - This is a self-assessment overreach that sat next to its own refuting evidence: a real calibration
    gap that was never caught.
- **Smallest correction:** make C1's counted before→after include the doc/tool contradiction count. Rule 5
  and the `:522` evidence string against the matrix row go 1 → 0. Update the vocabulary assertions that
  become false once a seventh verdict exists:
  - `SKILL.md:12-14` ("Verdict vocabulary is shared with … `NOT_HTTP`" — six names)
  - `corpus/knowledge/endpoint-identity.md:3` ("The verdict vocabulary is fixed")
  - `corpus/knowledge/consumer-registry.md:84-85` ("binding vocabulary")

  If the docs are left as they are, C1 **harms** calibration by its own definition, because SKILL entries
  would no longer match repo state.

### F2 — Counterexample: the repair swaps one absolute for its opposite
- The live evidence string at `tools/kama-probe.sh:504` reads: "(llama.cpp loading envelope: not ready, not
  a foreign service)".
- The header at `tools/kama-probe.sh:34` reads: "Drift, never a foreign service."
- The counterexample is the measurement itself. The C1 positive control is a stub server that is not
  llama.cpp, and by construction it is graded MODEL_LOADING. Any HTTP service can emit these bytes. The
  predicate (`tools/kama-probe.sh:426-445`) checks only the body and does not check `Server` or
  Content-Type.
- The lane's own rule already forbids this kind of inference. `SKILL.md:133` says "the status code alone does
  not identify a broker or exclude a model server". `endpoint-identity.md:18` says "Neither status `2xx`
  nor `Server: llama.cpp` alone proves identity."
- Upstream does set `Server: llama.cpp` on every response: b11755 `tools/server/server-http.cpp:180`
  `srv->set_default_headers({{"Server", "llama.cpp"}});`. The evidence line already includes `$base`, which
  carries `(Server: …)`. So graded confidence is cheap to express.
- **Smallest correction (text only, verdict/reason/exit unchanged):**
  - evidence → "exact llama.cpp loading envelope (body match; runtime identity unverified)"
  - header → "graded from the envelope bytes; not proof of runtime".
  - The reason name `llamacpp-loading` is acceptable only if documented as "envelope shape", not "runtime is
    llama.cpp".
- Impacted axis: calibration. Leaving the "not a foreign service" wording repeats the overreach C1 claims
  to catch, with the sign flipped.

### F3 — Larger uncaught overreach in the same domain: router-mode false pass (exit 0)
- In llama.cpp router mode, GET `/v1/models` returns 200 with `data[]`, and every entry carries a status.
  b11755 `tools/server/server-models.cpp:2345-2346`: `json status { {"value",
  server_model_status_to_string(meta.status)},`. `:2358-2359` adds `status["exit_code"]` and
  `status["failed"] = true` for failed models. `:2448-2449` is `res_ok(res, { {"data", models_json},`.
- The README (b11755 `tools/server/README.md`, router `/models` section) shows `"status": { "value": "loaded" …`
  and `"value": "unloaded"`.
- The probe's MODEL_OK branch (`frozen:479`, live `:520`) requires only 2xx plus a model array plus an ID
  match. A router whose expected model is `loading`, `unloaded` or `failed` would therefore be graded
  **MODEL_OK, exit 0**. [INFERENCE] I derived this from the code paths and did not run it.
- That is a false pass, which is worse than C1's false-foreign label (C1's case already exited 2).
- **This does not falsify C1.** It caps the claim. C1 must state its scope as "single-model llama-server
  `is_ready` gate" and name router-mode status as an open gap. Otherwise "loading llama.cpp is graded
  honestly" overreaches. This is also the strongest argument against any move to 8 (F6).

### F4 — The "no slot available" scope-limit control is synthetic, not a real overreach
- The claim offers "no slot available" `unavailable_error` as a scope limit.
- Upstream emits it only on the `/slots`/health path, when the caller sets `fail_on_no_slot`. b11755
  `tools/server/server-context.cpp:5394-5396` reads: `if (!req.get_param("fail_on_no_slot").empty()) { … "no
  slot available"`.
- It is never emitted on GET `/v1/models`. So `tests/probe-verdicts/Overbroad503.json`
  `Overbroad503.no-slot-available` is a fine negative control, but it is **not** evidence of a known
  residual overreach. Do not describe it as one.
- The real residual instances are F3 (router status) and F5 (the python-less host).

### F5 — Host-dependent grading: without python3 the old overclaim returns
- `tools/kama-probe.sh:424-427`: "without python3 the body keeps its old FOREIGN_SERVICE verdict (fail
  closed, never false-pass)" / `[ "$HAVE_PY" -eq 1 ] || return 1`.
- "Never false-pass" holds for exit, which is 2 in both cases. But the same server gets two different
  verdicts depending on the host. On the python-less host it is still labelled "non-model service".
- The fix is an honest scope statement, not a defect. The matrix and SKILL should say MODEL_LOADING
  requires python3, and the python-less evidence string should not claim "non-model".
- [INFERENCE] The matrix cannot detect this unless one test runs with python3 masked from PATH.

### F6 — Score: 7→7 is honest; 8 is not earned
- The lane has a long pattern of "improved, delta 0" calibration verdicts (`LOG.md:601`, `:690`, `:782`,
  `:909`). C1 does not break that pattern legitimately. Its reach is:
  - one envelope;
  - body-only evidence (F2);
  - the larger false-pass sibling still open (F3);
  - no non-author sample. `AXES.md:47-48` requires "a named non-author reviewer on record … a dispatched
    subagent does not count" for subjective moves.
- An 8 would put calibration on the saturation line. With operability at 8, every owned axis would be ≥ 8
  (`SCORECARD.md:132`, "Saturation line **8/10 on every owned axis**"). That would flip the stagnation
  nudge, a governance consequence that rests on one regex-free predicate. That would be premature
  saturation.
- **The downside is real:** if the F1 doc updates or the F2 wording fix are skipped, the honest verdict is
  "calibration harmed", and the round fails `AXES.md:35`: "no axis is harmed".

### F7 — C2 must not depend on C1 (causal separability)
- `AXES.md:31` says "Claims must be **causally separable** — each verifiable without the others having landed".
- C2 "runs kama-probe against it". If C2's acceptance requires a MODEL_LOADING verdict during load, C2
  cannot be verified without C1.
- **Correction:** C2's acceptance should rest on the captured raw lifecycle surfaces (503 envelope, `/health`
  200, `/v1/models` 200 with alias) plus a ready-state MODEL_OK. Any loading-phase probe verdict should be
  recorded as observation only, or run with the frozen probe.

### F8 — Mixed-version history hazard (rollback / adjacency)
- The new probe now accepts MODEL_LOADING baseline rows (`tools/kama-probe.sh:937`). The frozen/older probe
  rejects them: `frozen:895-897` reads "dropping malformed baseline row … malformed-row-dropped".
- A history dir written by the new probe, then read by a reverted or older copy, will drop those rows and
  log malformed notes in DELTA.md.
- [INFERENCE] I did not check whether any other lane or copy reads kama history dirs. I was bounded from
  sibling repos.
- This is not a defect in C1. Record the one-way schema step in LOG as a limitation. The snapshot schema
  string stays `kama-probe/v2` (`frozen:1019`), so nothing signals the vocabulary change.

## Positive evidence (C1 survives these checks)
- **Upstream envelope verified.** b11755 `tools/server/server-http.cpp:308-325` reads: `if (!is_ready.load())
  { if (frontend_paths.count(req.path)) … res.status = 503; … {"message", "Loading model"}, {"type",
  "unavailable_error"}, {"code", 503}`.
  - The claim cites `:307-325`. Line 307 is the lambda opener, so the range is acceptable.
- **README agrees.** b11755 `tools/server/README.md:486-487` reads: `{"error": {"code": 503, "message": "Loading
  model", "type": "unavailable_error"}}` … "the model is still being loaded."
  - Note that the README key order is code, message, type. L1's live wire order was message, type, code.
  - A positive control in **each** order shows the matcher is JSON-structural, not byte-based. The python
    predicate at `:430-442` is structural.
- **Loading wins over the API key upstream, so the 401/403 ordering is safe.** `server-http.cpp:354-357`
  runs `middleware_server_state` before `middleware_validate_api_key`. A keyed llama-server that is still
  loading answers 503, not 401. AuthAndDead's "401 + loading envelope" rows are synthetic but correct
  controls.
- **The envelope is stable across many releases**, which is more than the claim states. `"Loading model",
  ERROR_TYPE_UNAVAILABLE` appears at b4000 `examples/server/server.cpp:2414` and b6000
  `tools/server/server.cpp:3823`. (The b3000 and b5000 fetches failed, so they are not checked.)
- **No false pass.** `eval_rows` sets drift for every non-MODEL_OK verdict (`frozen:820`:
  `if [ "$verdict" != "MODEL_OK" ]; then drift=true; fi`), so MODEL_LOADING exits 2 automatically.

## What would falsify C1 (for L1 to run)
1. The frozen probe on the exact live-wire stub (503, `application/json; charset=utf-8`, `Server: llama.cpp`,
   body order message, type, code) does **not** print `FOREIGN_SERVICE non-2xx-non-model-http` exit 2.
   That kills "red".
2. The repaired probe grades the live-wire stub, or the README-order stub, as anything other than
   `MODEL_LOADING llamacpp-loading` exit 2. That kills "green" or exposes a byte matcher.
3. Any row in `Overbroad503.json` / `NonLoadingStatuses.json` / `AuthAndDead.json` grades MODEL_LOADING.
   That means overbroad. Any MODEL_LOADING row shows `drift:false` or exit 0. That means a false pass.
4. C2's live b11755 capture during load shows a `/v1/models` body other than the envelope. That kills the
   premise; L1's 10:17 smoke observation currently supports it.
5. After landing, `SKILL.md:12-14`, `endpoint-identity.md:3/:17` or `consumer-registry.md:84-85` still
   assert the six-verdict fixed vocabulary or the rule-5 "non-model service" claim. Calibration is then
   harmed, not improved.
6. Evidence or header text still asserts "not a foreign service" / "never a foreign service" (F2). That is
   ungraded confidence. The C1 calibration verdict should be at most "unchanged" until the text is fixed.

## Limitations
- I ran no probe or matrix. The router-mode false pass (F3) and the python-less path (F5) are code-derived
  [INFERENCE].
- The live probe was under concurrent edit, so live line numbers may shift. The frozen-file cites are stable.
- I opened upstream sources at tag b11755 via raw.githubusercontent.com, plus b4000 and b6000 for the
  envelope's history.
- Installs: none.
