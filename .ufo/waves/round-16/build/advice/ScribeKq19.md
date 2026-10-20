# ScribeKq19 — report (advice only; not a verdict)

Seat: scribe, KQ19 QUALITY.md append draft. Access date for every source: 2026-10-20.
Owned output: `.ufo/waves/round-16/build/drafts/kq19.md` (only file written besides this report).
Installs/updates: none. Commands run were read-only fetches (`curl` to raw.githubusercontent.com and api.github.com, `grep`, `sha256sum`, `ls`, `date`). No gate, harness, probe or test was run against the lane; no subagent was dispatched.

## Behavior drafted

KQ19 admits only the not-ready verdict `MODEL_LOADING` / `llamacpp-loading` (drift true): `GET /v1/models` returns HTTP 503 with a JSON `error` object whose `message` == `Loading model`, `type` == `unavailable_error`, integer `code` == 503 (all exact). It adds no served-model identity. Rejects: other 503 bodies (e.g. `no slot available`), loading bodies on `/health` or `/` as verdict or readiness, loading bodies offered as `MODEL_OK`, stub matrices as real-runtime integration, and green runs without the red control. Preamble states no earlier criterion is superseded and names KQ13, KQ14, KQ16, KQ17, KQ18 as in force.

## Sources (URL or path:line, access 2026-10-20)

1. `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/server-http.cpp:310` — quote: `return true; // frontend asset, allow it to load and show "loading"` (frontend paths pass the gate).
2. Same file `:312-313` — quote: "no endpoints are allowed to be accessed when the server is not ready".
3. Same file `:318-319` — quote: `{"message", "Loading model"},` / `{"type", "unavailable_error"},` and `:314` `res.status = 503;`.
4. Same file `:331` `srv->set_pre_routing_handler(...)` and `:354` — quote: `if (!middleware_server_state(req, res)) {` (gate runs before the API-key check; OPTIONS returns earlier).
5. `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md:485-487` — quote: "Explanation: the model is still being loaded." (`/health` documents `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}`, `:479-486`).
6. `https://api.github.com/repos/ggml-org/llama.cpp/git/refs/tags/b11755` — quote: `"sha": "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"` (tag b11755 resolves to the brief's commit).
7. Lane `tools/kama-probe.sh:521-522` — quote: `C_REASON=non-2xx-non-model-http` / `(non-2xx HTTP from a non-model service)`; this is the overreach. The grep for `Loading model|unavailable_error|is_ready` in this file returned no matches (2026-10-20), so the probe has no loading branch.
8. Lane `.ufo/waves/round-16/frozen/kama-probe-before.sh:521-522` — identical grade; `sha256sum` = `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` (matches brief).
9. Lane `corpus/QUALITY.md:76` — quote: "No earlier criterion is superseded. KQ13's separation of available inventory," (round-15 preamble pattern reused). `:45` — "No earlier criterion is superseded. KQ14's semantic-human boundary remains in force." Table columns at `:7-8`.
10. Lane filesystem (bash, 2026-10-20): `ls: cannot access 'lessons': No such file or directory` at lane root; `corpus/lessons/` contains `round-15.md` and `round-15-verifier-spotcheck.md`. Therefore the pointer `lessons/round-16.md` is not present; under QUALITY.md's bare-path convention it resolves to `corpus/lessons/round-16.md`, which is absent.

## Findings

- The overreach is real at source: every non-frontend path returns the `Loading model` 503 while not ready (`server-http.cpp:307-320`, gate at `:354`), and `tools/kama-probe.sh:521` grades that body `non-2xx-non-model-http`. Admitting MODEL_LOADING narrowly (exact triple, `/v1/models` only) addresses it without the reject-all or loading-all failure modes the brief names.
- Scope limit to state in L1's round notes: the classifier decides from `/v1/models` alone, so `/health` documentation (README `:479-487`) is supporting evidence, not a verdict input.
- `/` returns through the gate during loading (`server-http.cpp:310`); evidence fetched at `/` by classify (`kama-probe.sh:463,509,519,522`) can be HTML during loading and must not be read as readiness.

## Gaps and blockers

- `lessons/round-16.md` does not exist (`corpus/lessons/` has only round-15 files). L1 must author it or change the pointer in the KQ19 row. I did not create it (out of owned files).
- Unknown: whether the repaired probe sets `drift` as specified; whether other llama.cpp tags emit the same body (only b11755 opened); whether any other round-16 seat has claimed `KQ19`. Grep of `corpus/`, `tools/kama-probe.sh` and the frozen probe found no `KQ19`.
- Live smoke observation (L1, 10:17 -03) was not re-observed by me; cited as L1-reported.

## Checks for L1 to run (not run by this scribe)

- Append `.ufo/waves/round-16/build/drafts/kq19.md` table row and preamble to `corpus/QUALITY.md` after line 98; strip the integration-notes block.
- Confirm `corpus/lessons/round-16.md` exists before the row ships.
- Confirm the `tools/kama-probe.sh` 521-522 anchors and the frozen sha after the repair lands.
