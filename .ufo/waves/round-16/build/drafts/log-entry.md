## round 16 — loading-envelope verdict and live llama.cpp lifecycle (2026-10-20)

- Trigger: the frozen probe `.ufo/waves/round-16/frozen/kama-probe-before.sh`
  (sha256 `93ee4302…cd64`, source commit `20e392e`, per `frozen/manifest.json`)
  grades a loading llama.cpp server as `FOREIGN_SERVICE` / `non-2xx-non-model-http`.
  That is an overreach: upstream answers every non-frontend path with HTTP 503 while
  the model is loading. Source read at llama.cpp b11755 (accessed 2026-10-20):
  `tools/server/server-http.cpp:319` — "no endpoints are allowed to be accessed when
  the server is not ready"; `:321` `res.status = 503;`; `:325` `{"message", "Loading model"},`;
  `:326` `{"type", "unavailable_error"},`; `:327` `{"code", 503}`. The middleware is
  the pre-routing handler registered at `:338`. Its frontend exemption is `:316-317`.
  Upstream README `tools/server/README.md:490-492` (accessed 2026-10-20) documents the
  same envelope: "Explanation: the model is still being loaded."
- Frozen-path reasoning: `classify()` (`kama-probe-before.sh:415-525`) sends a 503
  without `data[]`/`models[]` (`:392-393`) past the 401/403 arm (`:458-461`) and the
  model-array arm (`:479`) into the non-2xx branch, reason at `:521`. This is a code
  reading. The frozen run result is `[L1-SLOT:red-frozen-stub]`.
- Smoke observation (L1, 10:17 -03; carried in the round context, not re-measured
  here): during load `GET /v1/models` returned 503 with the `Loading model` body. When
  ready, `/health` returned 200 `{"status":"ok"}`, `/v1/models` returned 200 with
  `data[0].id` equal to the alias and `owned_by` `llamacpp`, plus an Ollama-shaped
  `models[]`. `/slots` returned 200. `/metrics` returned 501 without `--metrics`.
- Planned claim C1 (calibration, lowest assigned axis, 7): `tools/kama-probe.sh` gains
  verdict `MODEL_LOADING`, reason `llamacpp-loading`, drift true. It is chosen only when
  `GET /v1/models` returns 503 AND the body is a JSON object whose `error` object has
  `message` == "Loading model", `type` == "unavailable_error" and integer `code` == 503.
  Every other case keeps its current verdict. The scope limit is explicit: an
  `unavailable_error` with "no slot available" stays `FOREIGN_SERVICE`.
  Measured by a literal stub-server matrix in `tests/probe-verdicts/<Family>.json`
  (schema per the round-16 contract). It is red against the frozen snapshot and green
  against the repaired probe. Positive controls must defeat reject-all and loading-all
  implementations.
- Planned claim C2 (operability): `tools/kama-llamacpp-live.py` launches an ephemeral,
  lane-owned llama-server (official b11755 release, commit `704366d76`, pinned tiny GGUF
  `stories260K.gguf`, sha256 `270cba1b…d256`) on a free loopback port that is never a
  registered consumer port. It captures the documented lifecycle surfaces, runs
  `kama-probe` against it, tears it down and proves teardown. It writes nothing under
  `~/.config`, `~/.omp`, systemd or any service path. No registered port is served.
- Named L1 slots (not yet measured; this draft asserts none of them):
  - `[L1-SLOT:red-frozen-stub]`: frozen probe on the loading-envelope stub. Expected
    reason `non-2xx-non-model-http`, exit 2. Record the observed verdict and exit.
  - `[L1-SLOT:green-repaired-matrix]`: repaired probe against the full
    `tests/probe-verdicts/` matrix. Record the pass count, total, and exit.
  - `[L1-SLOT:positive-controls]`: the controls that defeat reject-all and loading-all.
    Record the names and results.
  - `[L1-SLOT:live-lifecycle]`: `kama-llamacpp-live.py` run. Record the surfaces
    captured, the probe verdict on the live server, and the teardown proof.
  - `[L1-SLOT:port-registry-untouched]`: proof that no registered consumer port was served.
  - `[L1-SLOT:asset-digests]`: on-disk sha256 of the llama-server binary and of
    `stories260K.gguf`, compared with the pinned values.
  - `[L1-SLOT:tool-installs]`: any install or update performed this round, with tool,
    version, channel and reason. This scribe installed nothing.
  - `[L1-SLOT:calibration-score]`: the scorecard result for calibration and operability.
- Unknown at drafting time: whether the repaired probe has landed. `tools/kama-probe.sh:415-525`
  currently has no `MODEL_LOADING` branch, so the repair is not in the tree yet.
  Whether the 503 window is long enough for a live observation is also unknown. The
  live binary's install state is unverified here. Whether the upstream `Server`
  header applies to the 503 response is inferred from `server-http.cpp:187`
  (`set_default_headers`), not observed on the wire.
