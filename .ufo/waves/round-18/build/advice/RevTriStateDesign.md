VERDICT: partial — the gate confines null structurally, but a later `/v1/models` 503 can still be reported NOT-EVALUATED.

Axes: operability and calibration.

## Findings

### P2 — A later observed `/v1/models` 503 can evade both the null grade and model-status checks

- The staged tool records the ready `/v1/models` capture, but `models_alias_id` checks only its parsed IDs: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/KamaR18.C1LiveTool-2/kama-llamacpp-live.py:1319-1349` — “`bool(ids) and all(value == args.alias for value in ids)`”. The capture retains its HTTP status at `:669-699`.
- The gate likewise re-derives IDs without checking `captures.models.status`: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C1Gate-2/check-receipt.py:887-911` — “served ids ... are not all the alias”. Its null derivation is limited to readiness transition rows at `:1280-1290` — “`not model_503_rows`”.

[INFERENCE] A server can return 200 during readiness, then return HTTP 503 for the separate ready-capture GET with a JSON body containing the expected `data` IDs/owners, and return 200 for later probe requests. The producer and gate do not grade that capture's status, so the other checks can pass while `loading_envelope_graded` remains null and the gate returns NOT-EVALUATED/3. This is not a gate VALID/0, but it hides an observed 503 behind a no-observation classification and becomes unsafe if a caller treats 3 as acceptable.

Require `captures.models.status == 200` for the model identity checks in both producer and gate. Define null against every recorded `/v1/models` observation (readiness transitions, ready capture, and any probe response status present in the receipt), not only readiness transitions. If the intended scope is explicitly readiness-only, a later non-200 capture must still fail an evaluated check rather than leave the run not-evaluated.

## Null predicate

The staged gate correctly restricts `passed: null` to `loading_envelope_graded`, `evaluated: false`, and the exact reason `no-loading-503-observed` (`check-receipt.py:789-813`); it also rejects false checks before returning exit 3. Preserve those guards, and make the evidence condition explicit:

`null` is legitimate iff the schema is v3; exactly the `loading_envelope_graded` check has `passed: null` and `evaluated: false`; its reason is exactly `no-loading-503-observed`; all other required checks are evaluated and true; `loading_observed` re-derives false from the complete recorded `/v1/models` observations; there is no `/v1/models` 503 row/capture/probe observation; `loading_503` and `loading_envelope_exact` are null; `loading_503_bodies` is empty; and `loading_bodies_dropped == 0`. Any recorded 503 makes the check evaluated and requires grading every retained body; any failed check means fail/INVALID, never NOT-EVALUATED.

## Exit-3 consumers, residual risk, and verification gaps

The staged gate labels exit 3 `NOT-EVALUATED` and prints that label (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C1Gate-2/check-receipt.py:31-32,2089-2095`). The known frozen control does not treat it as a pass: K0 requires both exits exactly zero, while the bad-control branch treats nonzero as rejection (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_controls.py:551-559` — “`tool_exit == 0 and gate_exit == 0`”). However, `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:574` documents only the v1/v2 gate map “0 valid, 1 invalid, 2 unreadable”; its v3 consumer guidance and the round-18 controls/measure handling of exit 3 are not yet present in the delivered outputs. The v3 measure/control mapping is therefore unverified; require an explicit expected `(tool_exit, gate_exit)` pair for the zero-observation control and count exit 3 only as not-evaluated, never as a pass.

LSP was unavailable: `read xd://lsp` returned “No such tool”. Caller/definition/diagnostics checks were not possible; literal grep was used only as fallback. No runtime, tests, or measurements were run. Installs: none.