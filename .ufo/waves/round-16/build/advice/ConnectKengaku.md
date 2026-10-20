# ConnectKengaku — overlap scan: kengaku (LLM eval) ↔ kama C1/C2

Seat: read-only connector. Files opened: `kengaku-shokunin/{SKILL.md,PROVINCE.md,corpus/QUALITY.md}`,
`kama-shokunin/{SKILL.md,PROVINCE.md,corpus/QUALITY.md}`, round-16 `build/spec.json`,
`tests/probe-verdicts/*.json`, `tools/kama-probe.sh`, and llama.cpp b11755 source at
`704366d76` (HTTPS, read-only). No lane gate, harness or test was run. No install or
upgrade was made. This report is the only file written.

## Answer to the assigned question

**C2 as specified does not record completions.** Its capture allowlist is metadata only:
`/health`, `/v1/models`, `/props` (four fields), `/slots` (status + count), `/metrics`
(status) — `spec.json:57-59` (item `LiveHarness`): "Ready captures: /health, /v1/models
(full body + headers), /props (only model_alias, total_slots, is_sleeping, build_info and
default_generation_settings.n_ctx)". `kama-probe.sh` has no generation path either: the
only model-route request in `classify()` is `fetch "$port" "/v1/models" "m$port"`
(`tools/kama-probe.sh:452`).

**The risk is latent at one seam, and kama's own bar already names it.** KQ1 rejects
"`/health` answer, completion success, or September MODEL_OK ... as present served-model
identity" (`corpus/QUALITY.md:9`), and the runbook says "Do not send credentials or
completion requests as an identity test" (`SKILL.md:222-223`; anti-pattern at `:259-261`).
So a completion in C2 would be inadmissible for identity on kama's existing bar. If a
generation is ever added for *functional* liveness, it must stay a boolean
(`accepted`/`rejected` + HTTP status), never retained content, never timed, never graded;
a retained completion becomes a citable "model output" with no provenance bar and would
be read as eval ground by construction. For stories260K it has no evidential value in
either lane: kengaku's own numbers are scoped as "every number from these probes is a
**sub-3-bit (UD-IQ2_XXS) + llama.cpp serving-stack** observation" (`kengaku/SKILL.md:468`),
and kengaku refuses model quality/eval only in the sense of owning it — kama
"Refuses: model quality/eval (kengaku)" (`kama/PROVINCE.md:40`). A 1.2 MB F32 toy model
is not a kengaku subject and must not be turned into one.

## Evidence

| # | Finding | Citation | Quote (≤25 words) |
|---|---|---|---|
| E1 | Ownership agrees: kama owns endpoint identity/health; kengaku keeps interpretation | `kengaku/PROVINCE.md:132` | "kama is rostered and owns serving-plane health/detection and endpoint identity; kengaku keeps *interpretation* evidence and never remediates flags" |
| E2 | C2 capture allowlist has no completion route | `kama/.ufo/waves/round-16/build/spec.json:57-59` | "Ready captures: /health, /v1/models (full body + headers), /props ... /slots status + element count, /metrics status" |
| E3 | Probe sends no generation request | `kama/tools/kama-probe.sh:452` | "fetch \"$port\" \"/v1/models\" \"m$port\"" |
| E4 | kama's bar already rejects completion-as-identity | `kama/corpus/QUALITY.md:9`; `kama/SKILL.md:222-223` | "completion success ... is offered as present served-model identity"; "Do not send credentials or completion requests as an identity test" |
| E5 | kama refuses quality/eval | `kama/PROVINCE.md:40` | "Refuses: model quality/eval (kengaku)" |
| E6 | kengaku scopes its numbers to a serving stack, not capability | `kengaku/SKILL.md:468` | "every number from these probes is a sub-3-bit (UD-IQ2_XXS) + llama.cpp serving-stack observation" |
| E7 | Serving-plane flag authority is unowned; only integrator may remediate | `kengaku/PROVINCE.md:24,45,72` | "Not owned: the model-serving plane (llama-server flags, slot/batch config) — no lane owns it"; "flag-change authority remains unowned" |
| E8 | Loading envelope is emitted for every non-frontend path while `is_ready` false | b11755 `tools/server/server-http.cpp:312-325` | "no endpoints are allowed to be accessed when the server is not ready" |
| E9 | HTTP server starts before model load on purpose; one `is_ready` flag flips after load | b11755 `tools/server/server.cpp:493,507,515` | "start the HTTP server before loading the model to be able to serve /health requests" |
| E10 | **State middleware precedes API-key middleware** — loading 503 is auth-blind | b11755 `server-http.cpp:354-359` | "if (!middleware_server_state(req, res))" before "if (!middleware_validate_api_key(req, res))" |
| E11 | Matrix called the `/health`-green + models-503 pair an "Observed race"; on b11755 it is unreachable. **Resolved in-wave** — `MatrixLoadingRace` reworded all 7 affected `why` lines as synthetic and re-validated 9 tests | `kama/tests/probe-verdicts/LoadingRace.json:5` (was); `server.cpp:493-515` | was: "Observed race: /health is already green while /v1/models still returns the loading envelope"; now: "Synthetic race (not reachable on b11755, where one atomic is_ready gates both paths)" |
| E12 | A metrics reader that cannot distinguish "disabled" from "zero" is a known kengaku failure | `kengaku/corpus/knowledge/consumer-registry.md:110` | "a corrected reader pointed at 8080 logs zeros instead of failing" |

E10 is a fact of the pinned source, not an inference: `middleware_server_state` returns
`Handled` before `middleware_validate_api_key` is reached, so a key-protected server in
its loading window answers 503 "Loading model", not 401. Consequence [INFERENCE]: the
new verdict can never be authorization evidence, and a consumer that treats
non-`MODEL_OK` as "repoint" will repoint a healthy keyed server that was merely loading.

E11 was a real overclaim in the fixture text, now corrected by its owner. `server.cpp:493-515`
shows one atomic `is_ready` gates both `/health` and `/v1/models`, and `/health` is not a
frontend path (the API-key bypass set is separate); a green `/health` while `/v1/models`
returns the loading envelope cannot arise from that mechanism. It can arise behind a
proxy or across a restart, but no receipt in this wave shows it. `MatrixLoadingRace`
reworded all 7 affected `why` lines as "Synthetic race (not reachable on b11755 …)";
I verified 9 tests still parse and `grep -c 'Observed race'` returns 0. The fixtures
remain legitimate probe-robustness controls; [INFERENCE] if C1/KQ19 prose cites any of
them as observed lifecycle evidence, it still overclaims.

## Contested scope

| Seam | kama's position | kengaku's position | Resolution |
|---|---|---|---|
| Served-model identity & readiness | owns `GET /v1/models` reconciliation, `/health`, `/props`, `/slots` (`kama/PROVINCE.md:3-11`) | routes endpoint identity to kama (`kengaku/PROVINCE.md:132`) | No contest. C1/C2 are kama's. |
| Readiness vs identity | KQ13 keeps "available inventory, loaded residency, advertised identity and inference readiness" separate (`kama/corpus/QUALITY.md:40`) | "Listening-but-wrong beats closed-port" (`kengaku/SKILL.md:343`) | `MODEL_LOADING` is the missing third readiness state; it must not be read as identity, and "not foreign" must not be read as "ready". |
| llama-server flags | C2 chooses `-c 256 -t 1 --no-webui --alias` for a disposable fixture (`spec.json:59`) | serving flags are "not owned ... no lane owns it"; "flag-change authority remains unowned" (`kengaku/PROVINCE.md:24,45,72`) | Kama may set fixture flags; the receipt/argv must be labelled *fixture launch parameters, not a serving recommendation*. No fleet flag change is proposed. |
| Model output / quality | refuses quality/eval (`kama/PROVINCE.md:40`) | owns eval craft; scope-limits every number to its stack (`kengaku/SKILL.md:468`) | Nothing in C2 may retain or grade output. A stories260K completion is nobody's evidence. |

## What kama must hand off rather than absorb

1. **Any completion content, coherence, determinism or "generation works" quality claim** →
   kengaku (and for stories260K, refuse: not a capability subject; `kengaku/SKILL.md:468`).
2. **Any tokens/s, latency, context-length or quantization-band number** from the toy
   instance → nobody in this round; kengaku's numbers are stack-scoped observations, not
   portable performance figures.
3. **Any flag recommendation inferred from the C2 argv** → integrator / unowned serving
   plane (`kengaku/PROVINCE.md:24,72`).
4. **Any "a real deployment is ready because the fixture was ready"** → no lane; the
   `CriticC2ToyModel` attack owns this, and the receipt must say surfaces/protocol only.
5. **Any auth/credential inference from the loading 503** → kagi, plus the E10 scope
   limit: loading is evaluated before authentication.
6. **Counter-handoff kengaku → kama:** endpoint identity/health, exactly as routed at
   `kengaku/PROVINCE.md:132`.

## Reusable conventions from kengaku the round may adopt

- **Pair the contrast inside one process** (`kengaku/SKILL.md:433-437`: "Report paired
  contrasts, never raw levels, across batches"). C2 already launches once and records
  transitions; the receipt should state that loading→ready is one paired record from one
  pid/port/model, so no reader compares two launches.
- **Write the negative space** (`kengaku/corpus/QUALITY.md:36`, Q4): `loading_observed:
  false` must read "not observed", never "no loading phase" — the 1.2 MB model can load
  between polls.
- **Carry the experimental unit in-band** (`kengaku/SKILL.md` r11 `descriptors` record;
  the q4_0-KV premise was unstated for two rounds). C2's argv + server sha256 + model
  sha256 + `build_info` is the same shape; keep it mandatory, not optional.
- **A control arm must be the control** (`kengaku/SKILL.md:114`, anti-pattern 12): the
  loading fixture must be the real b11755 bytes, or C1 calibrates against an idealized
  body; see E11 for the reachability version of the same defect.
- **A grader's `ok` is not the conjunction the claim needs** (`kengaku/SKILL.md:120`):
  the matrix asserts `verdict`+`reason`+`exit` separately (correct); do not let exit 2
  alone stand for "loading" anywhere in prose.

## Proposed move (one, bounded)

**Name: give `MODEL_LOADING` a two-sided evidence bound — live-byte corroboration plus a
stated auth-blind scope limit.**

**Change 1 — `tools/kama-llamacpp-live.py` (C2, one file, zero new requests).** The
harness already keeps the first loading-503 body verbatim. Add a sibling receipt object
(not a `checks[]` pass):

```json
"loading_envelope": {
  "observed": true,
  "status": 503,
  "message": "Loading model",
  "type": "unavailable_error",
  "code": 503,
  "body_sha256": "...",
  "matches_probe_predicate": true,
  "source": "tools/server/server-http.cpp:307-325 @ 704366d76"
}
```

When no loading capture exists, emit `{"observed": false, "reason":
"not-observed-before-ready", "matches_probe_predicate": null}` and add no
`loading_envelope_predicate` check at all. Cross-field rule for the receipt gate
(`LiveReceiptGate`, separate owner): `loading_observed == true` ⇒ the object is observed
and a `loading_envelope_predicate` check exists and passed; `false` ⇒ the object is
explicitly unobserved and no such check exists. A live body that fails the three-field
predicate is a **finding**, not a pass: the run exits 1, because it falsifies C1's
fixture against the real binary.

**Change 2 — one sentence in C1/KQ19 prose.** `middleware_server_state` runs before
`middleware_validate_api_key` (`server-http.cpp:354-359`), so `MODEL_LOADING` is selected
before authentication and is not auth evidence; a key-protected server in its loading
window is indistinguishable from an unauthenticated one. Consumer action is *retry, do
not repoint*, with `UNAUTHORIZED_SERVICE`/`MODEL_OK` expected when the window closes.

**Coordination item (resolved in-wave):** `MatrixLoadingRace` rewrote the 7 affected
`why` lines; `LoadingRace.HealthAlreadyOk` now reads "Synthetic race (not reachable on
b11755, where one atomic is_ready gates both paths)". Verified after the fix: 9 tests
parse, every `expected` verdict unchanged, `grep -c 'Observed race'` = 0. No further
action on this item; the C1/KQ19 prose restriction above still applies.

**Affected axes.** Calibration (primary): C1's only fixture becomes checkable against the
pinned binary's own bytes at zero request cost, the non-observation is explicit, and the
verdict cannot be cited as auth evidence. Operability (secondary, neutral-positive): no
new HTTP request, no new timing dependence; the harness gains a self-describing block.
No harm to identity/foreign detection: a predicate mismatch fails loud instead of
silently changing a verdict.

**Why non-obvious.** Both items currently stand alone: the stub matrix is the only C1
discriminator, and `loading_observed` is a bare boolean that a reader can cite as live
confirmation. The move joins them by the *same predicate* over already-captured bytes —
a synthesis across the round's proposals, not a new measurement.

## Risks

- **The loading window may be missed** with a 1.2 MB F32 model on CPU (server starts
  before load and flips one flag: `server.cpp:493-515`). `observed:false` must be a
  legal, explicit outcome; never encode it as `passed:true`.
- **Receipt-schema coupling:** `tests/llamacpp-live/check-receipt.py` (LiveReceiptGate)
  validates `kama-llamacpp-live/v1`; if its key set is closed, land both edits together
  or defer the block to the next wave.
- **Body shape drift:** compare the three fields semantically; record `body_sha256`
  separately. A key-order or extra-field difference is an observation, not a failed
  predicate; a field-value difference is the finding.
- **Fixture ownership:** `LoadingRace.json` belongs to `MatrixLoadingRace`; cite it by
  path and frozen sha, and run the comparison after freeze.
- **Spoof surface:** the contract's predicate omits `Server: llama.cpp`. The real server
  always sets it (`server-http.cpp:180`), so requiring it would be a zero-cost
  tightening, but that is `ReviewMatcherExactness`'s call, not this move's.
- **Operability trap to state:** C2's `metrics_not_enabled (non-200)` means a
  kama-launched instance has no prompt/eval counters; a future eval that scrapes
  `/metrics` must distinguish 501 from zero (E12). The receipt's explicit non-200 is the
  guard; do not let a consumer read absence as zero activity.

## Verification (for L1)

1. Live run against `~/.local/bin/llama-server` (build 11755, commit `704366d76`) +
   stories260K: receipt contains `loading_envelope`; if `observed:true`, the three field
   values are exactly `Loading model` / `unavailable_error` / `503`; if `false`, no
   `loading_envelope_predicate` check exists and the reason is present.
2. Negative control on the pure predicate: `{"message":"no slot available",
   "type":"unavailable_error","code":503}` → `matches_probe_predicate:false` (same case
   as `Overbroad503.no-slot-available`).
3. Cross-check `body_sha256` against the stub fixture body in `LoadingRace.json`; equal
   digest is corroboration, unequal-but-predicate-true is a recorded observation.
4. `grep -n 'authentication\|pre-auth'` in the C1/KQ19 prose must hit; the matrix text
   check is now `grep -c 'Observed race' tests/probe-verdicts/LoadingRace.json` → `0`
   with all 9 tests parsing (`python3 -c "import json;print(len(json.load(open(...))))"`).

## Limitations

- Source lines are from the pinned commit fetched over HTTPS; I did not build or run the
  binary. The installed `~/.local/opt/llama-b11755/llama-server` reports "version: 0.7.0-dev
  (build 11755, commit 704366d76)" and sha256 `b6a31a8e…cd804`; the C1 asset pin
  (`753bfa73…e226`) is the release archive, a different object — do not conflate them.
- I did not observe a live loading window; E10/E11 are source facts, their consumer
  consequences are marked [INFERENCE].
- No quality/eval judgment of stories260K was made or implied, and none should be.
