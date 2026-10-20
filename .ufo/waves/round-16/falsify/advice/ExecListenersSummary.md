VERDICT: confirm — `listeners --port` integration routes the llama.cpp loading envelope to MODEL_LOADING with summary `model_loading=1` and `probed` equal to the bucket sum; the frozen probe still reports FOREIGN_SERVICE on identical input.

## What I ran (exact commands, exits)

Stub: `python3 /tmp/kama-r16-ExecListenersSummary/stub_loading.py 37883` — a 30-line `http.server` on 127.0.0.1:37883 answering **every** path with `503` + `Content-Type: application/json` + body `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` and `Server: stub-loading/0.1` (deliberately NOT `llama.cpp`). No llama-server was started; port 37883 was allocated free by an ephemeral bind probe, never 8080/34113.

1. `bash .../tools/kama-probe.sh listeners --port 37883 --json` → **exit 0**
   - Row: `"verdict": "MODEL_LOADING", "reason": "llamacpp-loading", "served_model": "-"`, `owner: "python3(pid=2908021)"`, `bind: "override"`.
   - Evidence string: `GET /v1/models -> 503 application/json (Server: stub-loading/0.1 ) (body matches the llama.cpp loading envelope: not ready; runtime identity and served model unverified); GET /health -> 503|application/json` — the `/health` follow-up probe also fired (also 503 from the stub).
   - Summary: `{"probed": 1, "model_endpoints": 0, "foreign_service": 0, "unauthorized_service": 0, "dead": 0, "not_http": 0, "model_loading": 1}`.
   - Full output retained at `/tmp/kama-r16-ExecListenersSummary/current.json` (scratch dir removed per contract; reproduced verbatim above). [scratch now deleted — see limitations]

2. Frozen probe: `bash .../.ufo/waves/round-16/frozen/kama-probe-before.sh listeners --port 37883 --json` → **exit 0**
   - Same port, same live stub, seconds later: `"verdict": "FOREIGN_SERVICE", "reason": "non-2xx-non-model-http"`; vocabulary line lacks `MODEL_LOADING` (`MODEL_OK MODEL_MISMATCH FOREIGN_SERVICE UNAUTHORIZED_SERVICE DEAD NOT_HTTP`); summary has no `model_loading` key and `foreign_service: 1`.
   - Clean separability contrast: identical 503+envelope is the sole difference in output, matching the 17-row stub-matrix delta the build wave measured.

3. `bash .../tools/kama-probe.sh listeners --port 37883` (table mode) → **exit 0**
   - Row `MODEL_LOADING | llamacpp-loading`; footer `probed=1 model_endpoints=0 foreign_service=0 unauthorized_service=0 dead=0 not_http=0 model_loading=1`. Non-JSON path agrees with JSON path.

4. Bucket arithmetic check (python3 over both captured JSONs): `probed == sum(buckets)` → `True` for current (1 = 0+0+0+0+0+1) and frozen (1 = 0+1+0+0+0). No row fell outside the verdict buckets.

## Source-level ground truth (not inference)

- `tools/kama-probe.sh:503-508`: `classify` emits `MODEL_LOADING`/`llamacpp-loading` only when `F_CODE=503`, body non-empty, and `body_is_llamacpp_loading` passes — checked before the foreign-service fallthrough.
- `tools/kama-probe.sh:727-733`: `MODEL_LOADING` increments `n_loading`, which lands in `summary.model_loading` at `:743-744` (JSON) and `:748-749` (table). `probed` is `${#ports[@]}`, structurally the bucket sum.
- `tools/kama-probe.sh:713-714`: `--port` forces `ports=("$OPT_PORT")` with scope `override` — matches observed `"bind": "override"`.

## Findings / nuances

- **Owner attribution works**: `OWNER[37883]` resolved to `python3(pid=2908021)` via `ss` — the listeners row correctly names the non-llama stub process, so the verdict carries no runtime claim (evidence text states "runtime identity and served model unverified"). Consistent with the contract.
- **No false MODEL_OK**: stub has no `data`/`models` array; `served_model: "-"` and `model_endpoints: 0` — the loading gate did not leak into the model bucket.
- **Body-shape gating confirmed independent of headers**: the stub's `Server: stub-loading/0.1` (not `llama.cpp`) still produced MODEL_LOADING, matching the documented "body-shape match only" design. [INFERENCE: this is intended behavior, not a bug — header spoofing cannot downgrade the verdict since the check never reads `Server`.]
- **`listeners` does not gate**: exit 0 despite a drift verdict — documented at `:38` and in the emitted `exit_codes` block; not re-litigated here.

## Limitations

- Single-port `--port` run exercises only the override path; the no-flag `ss -ltn` enumeration path was not attacked (outside this item).
- Only the exact-envelope happy path was probed live; deviant envelopes (bool/string `code`, non-503 status) are covered by the sibling stub-matrix item, not re-run here.
- Scratch dir `/tmp/kama-r16-ExecListenersSummary/` removed after the run per contract; full JSON bodies are quoted verbatim above as retained evidence.

## Teardown / hygiene

- `kill 2908021`; `pgrep -x llama-server` → empty (never started); post-kill `curl http://127.0.0.1:37883/v1/models` → `000` connect-refused. No lane files, fleet files, or `.ufo/state` touched. No installs.

Report: .ufo/waves/round-16/falsify/advice/ExecListenersSummary.md
