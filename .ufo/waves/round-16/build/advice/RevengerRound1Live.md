# RevengerRound1Live — what the pre-deletion llama.cpp record supports, and what C2 can re-measure on b11755

**Seat:** revenger, leaf (read-only). **Axes:** calibration (7, lowest) + operability.
**Scope:** reconstruction bounded to `LOG.md` rounds 1–3 and `corpus/knowledge/endpoint-identity.md`,
`served-model-identity.md`, `runtime-health-surface-matrix.md`; C2 surfaces taken from the
LiveHarness item (`.ufo/waves/round-16/build/spec.json:59`); b11755 behavior read from the tag
source and from the installed pin (read-only commands only).
**Axes named:** (1) *calibration* — does the round-1 record license what C2 will assert, and where
must the receipt say "not observed"? (2) *operability* — can C2 actually reproduce those surfaces
on the installed b11755 pin (flags, digests, timing)?

## Headline

The pre-deletion runtime was one ready-state llama.cpp server on `127.0.0.1:34113`; kama recorded
its identity route (`/v1/models`, `Server: llama.cpp`, `models[]`+`data[]`, full-GGUF-path id), its
health body, `/props`/`/slots`/`/metrics` samples, and one decisive alias fact: chat completions
accepts **any** requested model name. It never recorded a loading state. C2 on b11755 can re-verify
the ready-state identity and health surfaces, but **cannot** re-verify the path-id normalization
branch (it always passes `--alias`), the chat-completions name-ignoring behavior (it sends no
generation), the `/metrics` counter body (it runs without `--metrics`), or the 2-slot/16384-context
shape (it launches `-c 256`, default slots). The loading 503 is a *new* observation on b11755; it is
code-grounded, not round-1-grounded, and C2 sees it only opportunistically.

## 1. Reconstruction — what kama observed before deletion

### 1.1 Endpoint and process

- The model endpoint was loopback `127.0.0.1:34113`, served by `llama-server` pid 1299 under
  `qwen-coder.service` with `--port 34113`.
  Evidence: `LOG.md:50-52` — “The model is `llama-server` pid 1299 on `127.0.0.1:34113`”.
- `8080` was not the model: it was the Jitsi JVB container, HTML 404 on `/v1/*`, while its
  `/metrics` returned 200 — the status-only-liveness false-pass this lane exists to catch.
  Evidence: `LOG.md:48-50` — “which is now `docker-jitsi-meet-jvb-1` (Jetty HTML 404 on `/v1/*`”.
- The runtime was later deleted, not repointed: the unit is gone and both ports refuse.
  Evidence: `LOG.md:245-246` — “`qwen-coder.service` is inactive and its unit deleted; ports 34113
  and 8080 both refuse”.
- Observation date is the round-1 live census, 2026-09-28.
  Evidence: `endpoint-identity.md:151` — “observed in the round-1 live census (2026-09-28)”; the
  readiness fragment says “Samples targeted the then-live 127.0.0.1:34113 llama.cpp server”
  (`served-model-identity.md:41`).

### 1.2 Identity route and ids

- The probe's decision input was metadata `GET /v1/models` only.
  Evidence: `endpoint-identity.md:9` — “sends metadata `GET /v1/models`”; implementation
  `tools/kama-probe.sh:452` (`fetch "$port" "/v1/models"`).
- The frozen response was `Server: llama.cpp` **plus both** `models[]` and `data[]`.
  Evidence: `endpoint-identity.md:63` — “`Server: llama.cpp` plus both `models[]` and `data[]`
  arrays (F4)”.
- The served id was a full GGUF path, not a bare name; consumers declared the bare basename, so
  basename-plus-one-`.gguf` normalization was mandatory, not cosmetic.
  Evidence: `endpoint-identity.md:21` — “the served ID
  `/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf`”; and
  “compare the result case-sensitively”.
- The probe's positive/negative controls on that live server were `MODEL_OK`/`matched` and
  `MODEL_MISMATCH`/`served-id-mismatch`.
  Evidence: `endpoint-identity.md:26-33` — “`"verdict": "MODEL_OK"` … `"reason": "matched"`” and
  “`"verdict": "MODEL_MISMATCH"` … `"reason": "served-id-mismatch"`”.
- Identity required a model array **and** an id match; status or `Server` alone was insufficient.
  Evidence: `endpoint-identity.md:18` — “A model array and matching ID are required.”

### 1.3 Alias behaviour

- **Requested model name is not enforced.** `POST /v1/chat/completions` returned 200 for any
  requested model name and served the loaded model, so a successful chat round-trip was *not*
  identity evidence.
  Evidence: `LOG.md:59-61` — “answers `POST /v1/chat/completions` with **200** for any requested
  model name”.
- The advertised id is configuration-driven: `data[].id` is the `-m` path **or** `--alias`.
  Evidence: `runtime-health-surface-matrix.md:14` — “`data[].id` = `-m` path, or `--alias`”.
- The round-1 id was the `-m` full path, so **no alias was in effect** (or the alias equaled the
  path). [INFERENCE] — the four-source record never names the launch flags beyond `--port`, and
  `LOG.md:50-52` records only the port. Do not assert “the service had no `--alias` flag”; assert
  “the served id was the path”.

### 1.4 Health, readiness, capacity, metrics (ready state only)

- `/health` answered 200 with `{"status":"ok"}` when ready.
  Evidence: `served-model-identity.md:16-17` — “`=== /health ===` / `{"status":"ok"}`”; restated at
  `endpoint-identity.md:88` — “The recorded body was `{"status":"ok"}` (F5)”.
- `/props` was read with a jq projection that kept only `default_generation_settings.params`;
  recorded values were `chat_format:"Content-only"`, `reasoning_format:"none"`.
  Evidence: `served-model-identity.md:18-19` — “`"chat_format":"Content-only",
  "reasoning_format":"none"`”.
  Caveat: the projection means the round-1 record **cannot** establish the full `/props` key set.
- `/slots` was printed as the whole array (the jq filter returns `.` for arrays) and showed two
  slots, id 0/1, `n_ctx:16384`, `is_processing:false`.
  Evidence: `served-model-identity.md:20-21` — “`[{"id":0,"n_ctx":16384,"is_processing":false},
  {"id":1,...}]`”; repeated at `endpoint-identity.md:91` — “The recorded response had two slots”.
- `/metrics` served `llamacpp:` counters; therefore `--metrics` was enabled on that launch.
  [INFERENCE from presence of the surface; the four sources do not record the status code]
  Evidence: `served-model-identity.md:33-36` — “`llamacpp:prompt_tokens_total 360853`”.
- Liveness/identity separation was explicit: `/health` was a liveness signal, `/props` runtime
  metadata, `/slots` capacity, never identity substitutes.
  Evidence: `endpoint-identity.md:88-91` — “that status does **not** establish the served model ID”.

### 1.5 What the round-1 record never observed

- **No loading state at all.** Rounds 1–3 contain no 503 sample, no “Loading model” body, and no
  transition observation; every recorded sample is ready-state. [INFERENCE] the loading path was
  never exercised before deletion — this is an absence across all four bounded sources, not a
  positive statement that the old build lacked the gate.
  Supporting ready-only samples: `served-model-identity.md:16-21`, `endpoint-identity.md:26-33`.
- No `/v1/models` payload beyond arrays and the id; no response headers beyond `Server`. So
  payload-key drift cannot be reconstructed from the record.

## 2. C2 re-verification matrix (b11755)

C2 checks are the LiveHarness receipt ids (`.ufo/waves/round-16/build/spec.json:59`:
`health_ready`, `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`,
`props_alias`, `probe_model_ok`, `probe_mismatch`, `teardown_exited`, `teardown_port_closed`).

| Surface | Round-1 record | C2 check | Verdict |
|---|---|---|---|
| `GET /health` 200 `{"status":"ok"}` | yes (`served-model-identity.md:16-17`) | `health_ready` | **Re-verified.** b11755 README:488-490: “`{"status": "ok" }` … successfully loaded”. |
| `/v1/models` 2xx with model array | yes (`endpoint-identity.md:18,63`) | `models_alias_id`, `probe_model_ok` | **Partly re-verified**: `MODEL_OK` proves *a* model array exists (`body_has_model_array`) and gates the id; simultaneous `models[]`+`data[]` presence is visible only in the captured body, not gated. The probe reads `data[].id` first (`tools/kama-probe.sh:353-358`). |
| `MODEL_OK`/`matched` and `MODEL_MISMATCH`/`served-id-mismatch` | yes (`endpoint-identity.md:26-33`) | `probe_model_ok`, `probe_mismatch` | **Re-verified in semantics**, with the alias id: `--expect ALIAS` normalizes to itself; a deliberate wrong id yields `served-id-mismatch`, exit 2. |
| `data[].id` = full `-m` path | yes (`endpoint-identity.md:21`) | none | **Not re-verified.** C2 always launches with `--alias`; at b11755 the alias wins: “use first alias as model name” (`server-context.cpp:1521-1523`). |
| `owned_by` | **not in the four-source record** | `models_owned_by_llamacpp` | **New evidence**, not a re-verification. b11755 emits `"owned_by", "llamacpp"` (`server-context.cpp:5182`). |
| `Server: llama.cpp` | yes (`endpoint-identity.md:63`) | captured headers only | Captured, **no check id gates it**; b11755 sets a default header (`server-http.cpp:180` — “`srv->set_default_headers({{"Server", "llama.cpp"}})`”). |
| `/metrics` `llamacpp:*` counters | yes (`served-model-identity.md:33-36`) | `metrics_not_enabled` | **Different assertion.** C2 runs without `--metrics`, so it proves absence (501), not the round-1 body. |
| `/props` `default_generation_settings.params.chat_format` | yes (`served-model-identity.md:18-19`) | `props_alias` (subset) | **Not re-verified.** C2 captures only alias/slots/sleep/build/n_ctx; b11755 still serializes `chat_format`/`reasoning_format` (`server-task.cpp:76-77`). |
| `/slots` 2 slots, `n_ctx:16384` | yes (`served-model-identity.md:20-21`) | status+count only | **Not re-verified.** b11755 default `n_parallel = 1` (`common.h:462`); C2’s `-c 256` replaces 16384. Config delta, not version. |
| `POST /v1/chat/completions` 200 for any model name | yes (`LOG.md:59-61`) | none | **Not re-verified.** C2 sends no generation request; excluded “by the no-generation-request rule” (`runtime-health-surface-matrix.md:26`). |
| Port 34113 loopback binding | yes (`LOG.md:50-52`) | `teardown_port_closed` | **Not re-verified**; C2 uses an ephemeral loopback port and must never serve a registered port. |
| Loading 503 envelope | **never observed** | `loading_observed` (optional) | **Opportunistic only**; the receipt records observed/not-observed and must not require it. |
| Teardown exit + port close | no teardown record (operator-owned service) | `teardown_exited`, `teardown_port_closed` | **New evidence**, not a re-verification. |

### 2.1 Landed-harness cross-check (read-only, after the harness appeared)

The harness landed while this seat was reviewing it; the implementation matches the matrix above and
adds two calibration boundaries worth naming:

- `models_alias_id` requires **every** `data[].id` to equal the alias (`tools/kama-llamacpp-live.py:617-620`
  — “all(i == args.alias for i in ids)”). That is correct for b11755 single-model mode (“always has
  one single element”, `README.md:1258`) but would fail on a router/multi-model payload. It also
  means the check can never pass on round-1’s path id.
- `metrics_not_enabled` is a `status != 200` predicate (`tools/kama-llamacpp-live.py:626-630`), so it
  proves absence, not the 501 body; the exact 501 is available in the capture for a stricter
  future check.
- Port policy is enforced in code: `HARD_REFUSED_PORTS = {8080, 34113}`
  (`tools/kama-llamacpp-live.py:57`) plus ports read from `registry/endpoint-consumers.tsv`
  (`tools/kama-llamacpp-live.py:52`).

## 3. Version deltas that matter for calibration

### D1 — The loading gate is new to this record, and is code-grounded, not README-grounded

At b11755, while `is_ready` is false, **every** non-frontend path returns 503 with the exact
envelope. Evidence: `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/server-http.cpp:307-328`
— “no endpoints are allowed to be accessed when the server is not ready”; body fields at
`server-http.cpp:317-321` — “`{"message", "Loading model"}` … `{"type", "unavailable_error"}` …
`{"code", 503}`”.
The b11755 README documents that body in `GET /health` (`README.md:485-487` — “the model
is still being loaded.”), while the `/v1/models` section documents only a 200-path nullable `meta`
(`README.md:1258` — “`meta` field can be `null`”). So C1’s `/v1/models`-503 predicate is exactly
grounded in `server-http.cpp`, not in the `/v1/models` documentation; an advice text that cited
the README for that 503 would overstate the source. Round 1 contributes nothing here: it never
sampled loading.

### D2 — `/v1/models` keeps both arrays at b11755; payload keys grew

b11755 still returns the Ollama-shaped `models[]` and the OpenAI-shaped `data[]` in one body
(`server-context.cpp:5200` — “`{"models", json::array({`”; `server-context.cpp:5223` —
“`{"data", json::array({`”). The data element now carries `id`, `aliases`, `tags`, `object`,
`architecture`, `created`, `owned_by`, `meta` (`server-context.cpp:5172-5192`).
`architecture` is versioned: “Older servers can omit `architecture`” (`README.md:1282`).
Round 1 recorded only arrays+id, so it cannot establish whether the extra keys existed then.

### D3 — Id source at b11755: alias > HF/docker name > basename; the path branch is unchanged

`model_name` selection: first alias, else `model.get_name()`, else filename (`server-context.cpp:1521-1530`
— “use first alias as model name”). `get_name()` returns `hf_repo`, then `docker_repo`, then the
path (`common/common.h:312-320` — “return path;”). The README states the same contract: “By
default, model `id` field is the path to model file” (`README.md:1284`). Therefore a local
`-m /path/model.gguf` with no alias advertises the **same full path** round 1 saw, while
`--alias X` advertises exactly `X`.
The no-alias behaviour is version-stable; C2 simply never exercises it.
Note: `model_alias` is a `std::set`, so “first alias” is lexicographic, not command-line order.

### D4 — `/props` at b11755: same params, more surrounding keys

b11755 returns `default_generation_settings` (`params` + `n_ctx`), `total_slots`, `model_alias`,
`model_ftype`/`model_path`, `build_info`, `is_sleeping` and more (`server-context.cpp:5229-5266` —
“`{ "model_alias", meta.model_name }` … `{ "is_sleeping", is_sleeping }`”). Parameters still carry
`chat_format`/`reasoning_format` (`server-task.cpp:76-77`). Round-1’s jq projection cannot resolve
whether this key set changed; do not claim either direction.

### D5 — `/slots` shape and count are launch-configuration, not version

`/slots` is enabled by default and can be disabled (`README.md:985` — “enabled by default and can be
disabled with `--no-slots`”). b11755 defaults to one parallel slot (`common.h:462` —
“`n_parallel = 1`”); round 1 had two slots at 16384 context. [INFERENCE] round-1’s unit passed an
explicit parallel/context configuration; the four bounded sources record the *result*, not the
flag. C2 will see 1 slot at `-c 256`; encoding 2 in any check would be a false failure.

### D6 — `/metrics`: round 1 served counters, so `--metrics` was on; disabled is 501 at b11755

Disabled path: `ERROR_TYPE_NOT_SUPPORTED` maps to `not_supported_error`/501
(`server-common.cpp:115-117` — “case ERROR_TYPE_NOT_SUPPORTED: … code = 501;”) with body
“This server does not support metrics endpoint.” (`server-context.cpp:5303-5306`). Enabled metric
names are unchanged (`README.md:1131-1155` — “`llamacpp:prompt_tokens_total`”). So the round-1
metric body would still be reproducible *if* the server were launched with `--metrics`; C2’s
absence check is the opposite assertion and should not be read as a version change.

### D7 — Sleep and router modes exist at b11755 and change readiness semantics

`/health`, `/props`, `/models`, `/metrics` are “exempt from being considered as incoming tasks”
(`README.md:2341-2345`), and sleeping state is reported only via `/props`. The mature correction in
the corpus warns not to generalize the llama.cpp row to “router or sleeping-model state”
(`runtime-health-surface-matrix.md:53-57` — “must not be generalized to router or sleeping-model
state”). C2’s single-model launch with no `--sleep-idle-seconds` stays outside both; keep it there.

### D8 — Port is intentionally different

Round 1 bound 34113; C2 must bind an ephemeral loopback port and never a registered consumer port
(LiveHarness, `spec.json:59`). This is a safety delta, not a runtime-behaviour delta; C2 cannot and
should not reproduce 34113.

## 4. Advice to L1 (calibration + operability)

1. **Do not let `loading_observed=false` count against C1.** Only the stub matrix is deterministic
   for the envelope. The harness contract itself records observed-or-not and never requires it
   (`spec.json:59`). The pinned model is 1,185,376 bytes (`~/.cache/kama-shokunin/models/stories260K.gguf`),
   so the load window is short [INFERENCE]; a connection-refused-then-200 transition is a valid outcome.
2. **If C2 does capture the envelope, assert all three exact fields** (message `Loading model`,
   type `unavailable_error`, integer code 503), not just `503`. The repaired probe already does this
   (`tools/kama-probe.sh:440-442,501-505`); a status-only live assertion would reintroduce the
   over-breadth C1 fixed.
3. **Keep C1’s red/green independent of C2.** `probe_model_ok` runs only at ready, so C2 can never
   exercise `MODEL_LOADING`; the stub matrix remains the only oracle for that verdict.
4. **Do not advertise C2 as a normalization re-check.** `--alias` short-circuits the `-m` path
   branch. The path-id trap stays covered by the `ReadyControls` stubs and the round-1 record.
   A future optional arm could launch once without `--alias` to reproduce the path id on b11755
   (same code path: `server-context.cpp:1524-1525` + `common.h:319`).
5. **Server digest expectation:** `--expect-server-sha256` must be the **installed binary** digest,
   `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` (17,864-byte launcher;
   self-reports “build 11755, commit 704366d76”). The assigned `753bfa73…e226` is the **release
   tarball** digest (`~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz`, 22,240,468 bytes), not the
   binary. Passing the asset digest to the receipt checker will fail a correct pin.
6. **Pin scope is partial:** the loading envelope strings and the models/props serializers live in
   `libllama-server-impl.so` (`sha256 e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed`),
   not in the launcher. A receipt that hashes only the launcher identifies the wrapper, not the
   implementation. Either record the impl digest as an extra field or state the limitation.
7. **Keep one alias token.** `std::set` ordering makes multi-alias launches lexicographic; a
   comma list would make `models_alias_id` depend on spelling order.
8. **Do not encode round-1’s slot count/context.** Expect one slot at `-c 256`; do not assert two
   or 16384 anywhere.
9. **Treat `metrics_not_enabled` as exact 501 if precision is wanted.** b11755 returns
   501/`not_supported_error`; the harness’s non-200 check is safe but weaker.
10. **Do not extend a passing `/health` to “loaded weights”** under sleep or router semantics. C2
    does not enable either; keep the claim to the single-model, non-sleeping process it launched.

## 5. Limitations and provenance

- Read-only seat: no server launched, no lane gate/harness/test run, no registry row probed, no
  local endpoint or registered port contacted. Nothing written outside this report.
- Reconstruction is bounded to the four named sources; where a claim would require
  `consumer-registry.md` or other corpus files, it is omitted or marked [INFERENCE].
- b11755 claims come from the tag tree on `raw.githubusercontent.com/ggml-org/llama.cpp/b11755/…`
  (file:line quoted), not from executing the server. Installed-pin facts are read-only observations:
  `llama-server --version`, `--help`, `sha256sum` of `~/.local/opt/llama-b11755/{llama-server,
  libllama-server-impl.so}`, `~/.cache/kama-shokunin/models/stories260K.gguf`, and the release
  tarball.
- The model digest matches the assigned pin exactly:
  `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.
- The round-1 `/props` sample is field-projected and the `/v1/models` sample retains ids/arrays but
  not the full payload or all headers; conclusions that need the full payload are marked
  [INFERENCE] or left open.
- Installs/upgrades this run: **none**.
