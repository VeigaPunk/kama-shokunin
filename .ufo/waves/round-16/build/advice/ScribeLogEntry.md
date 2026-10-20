# ScribeLogEntry — round 16 LOG draft report

Scope: drafted only `.ufo/waves/round-16/build/drafts/log-entry.md`. No other file was written.
Measurements: none run. No lane gate, probe, harness or test was executed. No installs.
Access date for every source below: 2026-10-20.

## Sources (URL or path:line, located quote <= 25 words)

- llama.cpp b11755 `tools/server/server-http.cpp:319`
  (https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/server-http.cpp):
  "no endpoints are allowed to be accessed when the server is not ready".
- Same file `:321`: `res.status = 503;`; `:325`: `{"message", "Loading model"},`;
  `:326`: `{"type", "unavailable_error"},`; `:327`: `{"code", 503}`.
- Same file `:316-317`: `if (frontend_paths.count(req.path)) {` / "frontend asset, allow it to load and show "loading"".
- Same file `:338`: `srv->set_pre_routing_handler(...)`, the registration of the middleware.
- Same file `:187`: `srv->set_default_headers({{"Server", "llama.cpp"}});`.
- llama.cpp b11755 `tools/server/README.md:490-492`
  (https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md):
  "Explanation: the model is still being loaded."
- `tools/server/README.md:484-486`: "This endpoint is public (no API key check)."
- Lane frozen probe `.ufo/waves/round-16/frozen/kama-probe-before.sh:392-393`:
  "body_has_model_array() { # $1 body -> 0 when data[] or models[] is present".
- Same file `:521`: `C_REASON=non-2xx-non-model-http`; `:458-461` 401/403 arm; `:479` model-array arm.
- Lane `tools/kama-probe.sh:415-525`: text identical to the frozen `classify()`. No `MODEL_LOADING` branch yet.
- Lane `LOG.md` round-15 heading, `:854`: "## round 15 — executable duplicate-corpus admission repair (2026-10-20)".
- Lane `.ufo/waves/round-16/frozen/manifest.json:3`: "sha256": "93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64".

## Findings

1. The frozen probe's classification follows from its code: a 503 with no model array
   falls through to `non-2xx-non-model-http`. This is a code reading. I did not run the
   probe, so the observed frozen result is slot `[L1-SLOT:red-frozen-stub]`.
2. Upstream b11755 returns the loading envelope from a pre-routing middleware for every
   non-frontend path while `is_ready` is false. The README documents the same body. The
   classification is therefore an overreach rather than a model-less foreign service.
3. The draft keeps the scope exactly as specified: `MODEL_LOADING` / `llamacpp-loading`
   only on the exact three-field envelope. "no slot available" stays `FOREIGN_SERVICE`.
4. The L1 smoke observation (10:17 -03) is carried as L1-provided context. I did not re-observe it.

## Named slots for L1

`[L1-SLOT:red-frozen-stub]`, `[L1-SLOT:green-repaired-matrix]`, `[L1-SLOT:positive-controls]`,
`[L1-SLOT:live-lifecycle]`, `[L1-SLOT:port-registry-untouched]`, `[L1-SLOT:asset-digests]`,
`[L1-SLOT:tool-installs]`, `[L1-SLOT:calibration-score]`. The draft asserts no value for any of them.

## Unknown

- Whether the repaired probe has landed. The current tree has no `MODEL_LOADING` branch.
- The live binary's install state and on-disk digests (not checked; slot `asset-digests`).
- Whether the 503 window is long enough for a live observation.
- The wire-level `Server` header on the 503 response. Inferred from `:187`, not observed.
- The stub-matrix test files named in the draft do not exist yet under `tests/probe-verdicts/`.

## Installs

None. This scribe installed or updated nothing; the pacman pause remained in force and was not relevant.
