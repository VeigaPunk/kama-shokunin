# P04ProbeVersusOllama — the lane's own probe against live Ollama v0.40.11

Seat: P04ProbeVersusOllama (advisory leaf, round 60 w1, axes operability + calibration).
Lane: kama-shokunin — base `ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b`, freeze commit `e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1`.
No lane source, registry row, probe or SKILL text was modified; all writes are under this seat's out dir and removed scratch.

## 1. What ran

Server: `~/.local/opt/ollama-v0.40.11/bin/ollama serve` (sha256 `b0a4becfaf872e3ad5d2e9051244e0dfe55409f03d6e2cd9bd9c34400e201b4c`), started by this seat on a
free loopback port it chose (`python3` bind-to-0), with `env -i` HOME/OLLAMA_MODELS under scratch, `OLLAMA_NO_CLOUD=1`, and CUDA/HIP/Vulkan devices disabled.
Model: `~/.cache/kama-shokunin/models/stories260K.gguf` (sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`) imported as
`ollama create <nonce> -f Modelfile` (`FROM <gguf>`). Run 1: port 55369, model `r60p048170ff`, `create` exit 0.
Run 2 (loaded state): port 44345, model `r60p04b75559d`, `create` exit 0.
Both children were killed by their own PID in the same shell invocation that started them; after the kill `curl` to the port exits 7 and `ss -ltn` shows 0 listeners.

Probe invocation form actually used (single-endpoint mode exists — no read-only substitute was needed):

```
bash <lane>/tools/kama-probe.sh listeners --port $P --expect <ID>          # verdict table
bash <lane>/tools/kama-probe.sh listeners --port $P --expect <ID> --json   # same, JSON
bash <lane>/tools/kama-probe.sh check     --port $P --expect <ID>          # exit gate 0/2
bash <lane>/tools/kama-probe.sh consumers --port $P --expect <ID>          # single-row consumers
```

TMPDIR was set to the scratch dir so the probe's `mktemp` stayed out of `/tmp`; the registry was never read in `--port` mode and was never edited.

## 2. Raw captures

`captures.jsonl` holds the same data with full bodies and body sha256 (25 records). Bodies below are verbatim with `…` marking a cut, per the lane's elision convention.

| run | phase | route | status | content-type | body | reading |
|---|---|---|---|---|---|---|
| 1 | pre | GET `/` | 200 | text/plain; charset=utf-8 | `Ollama is running` | Liveness route on Ollama is `/` (200 text/plain "Ollama is running"), not `/health`. |
| 1 | pre | GET `/health` | 404 | text/plain | `404 page not found` | Ollama v0.40.11 has no /health: 404 text/plain "404 page not found" (the probe appends /health to evidence only when it answers 200 with JSON, so this route never enters its evidence). |
| 1 | pre | GET `/v1/models` | 200 | application/json | `{"object":"list","data":null}\n` | Empty store serves {"object":"list","data":null} — `data` is null, not an array. |
| 1 | pre | GET `/api/version` | 200 | application/json; charset=utf-8 | `{"version":"0.40.11"}` | /api/version reports 0.40.11, equal to registry/ollama-live-pin.tsv version. |
| 1 | pre | GET `/api/tags` | 200 | application/json; charset=utf-8 | `{"models":[]}` | Fresh model store: empty models array. |
| 1 | pre | GET `/api/ps` | 200 | application/json; charset=utf-8 | `{"models":[]}` | Nothing resident before generation. |
| 1 | pre | GET `/v1/models/r60p048170ff:latest` | 404 | application/json | `{"error":{"message":"model 'r60p048170ff:latest' not found","type":"not_found_error","param":null,"code":null}…` | Single-model fetch for a model that does not exist: 404 JSON not_found_error. |
| 1 | post | GET `/` | 200 | text/plain; charset=utf-8 | `Ollama is running` | Same liveness body after import. |
| 1 | post | GET `/health` | 404 | text/plain | `404 page not found` | Still 404 text/plain after import; /health is not an Ollama route. |
| 1 | post | GET `/v1/models` | 200 | application/json | `{"object":"list","data":[{"id":"r60p048170ff:latest","object":"model","created":1793136979,"owned_by":"library…` | Served id from the list route is tag-qualified: <nonce>:latest. This is the id the probe compares. |
| 1 | post | GET `/api/tags` | 200 | application/json; charset=utf-8 | `{"models":[{"name":"r60p048170ff:latest","model":"r60p048170ff:latest","modified_at":"2026-10-27T18:36:19.4646…` | tags name/model = <nonce>:latest, digest 8cf91c71…, details.runner=llamacpp, capabilities=["completion"]. |
| 1 | post | GET `/api/ps` | 200 | application/json; charset=utf-8 | `{"models":[]}` | After create, before any generation: inventory lists the model but /api/ps is empty — listed != resident, and the probe (which reads only /v1/models) reports MODEL_OK here. |
| 1 | post | GET `/api/version` | 200 | application/json; charset=utf-8 | `{"version":"0.40.11"}` | Unchanged version string. |
| 1 | post | GET `/v1/models/r60p048170ff` | 200 | application/json | `{"id":"r60p048170ff","object":"model","created":1793136979,"owned_by":"library"}\n` | Fetch route echoes the requested name form: GET /v1/models/<nonce> returns id "<nonce>" (bare), while the list route returns "<nonce>:latest". |
| 1 | post | POST `/v1/chat/completions` | 404 | application/json | `{"error":{"message":"model 'definitely-not-loaded' not found","type":"not_found_error","param":null,"code":nul…` | Before any load: bogus model id -> 404 not_found_error (no silent serve). |
| 2 | loaded | POST `/api/generate` | 200 | application/json; charset=utf-8 | `{"model":"r60p04b75559d:latest","created_at":"2026-10-27T21:37:09.803210049Z","response":" a time, there","don…` | Native generate with the tagged name loads the model (load_duration 2.5e8 ns) and echoes "<nonce>:latest". |
| 2 | loaded | GET `/api/ps` | 200 | application/json; charset=utf-8 | `{"models":[{"name":"r60p04b75559d:latest","model":"r60p04b75559d:latest","size":6312427,"digest":"8cf91c7109e7…` | Resident entry: expires_at present (5 min TTL), size_vram 0, runner llamacpp, digest 8cf91c71…. |
| 2 | loaded | POST `/v1/chat/completions` | 200 | application/json | `{"id":"chatcmpl-544","object":"chat.completion","created":1793137029,"model":"r60p04b75559d:latest","system_fi…` | Chat with the tagged id: 200, response model echoes "<nonce>:latest". |
| 2 | loaded | POST `/v1/chat/completions` | 200 | application/json | `{"id":"chatcmpl-582","object":"chat.completion","created":1793137029,"model":"r60p04b75559d","system_fingerpri…` | Chat with the BARE name: 200 and the response echoes the bare name "<nonce>" — the request path accepts the untagged name the probe calls MODEL_MISMATCH. |
| 2 | loaded | POST `/v1/chat/completions` | 404 | application/json | `{"error":{"message":"model 'definitely-not-loaded' not found","type":"not_found_error","param":null,"code":nul…` | A model IS resident, yet a bogus id still returns 404 not_found_error — the lane SKILL.md claim of "200 and silently serves the loaded model" does not hold for Ollama v0.40.11. |
| 2 | loaded | POST `/api/generate` | 200 | application/json; charset=utf-8 | `{"model":"r60p04b75559d","created_at":"2026-10-27T21:37:09.829032083Z","response":" upon a","done":true,"done_…` | Native generate with the bare name: 200, echoes the bare name. |
| 2 | loaded | GET `/v1/models` | 200 | application/json | `{"object":"list","data":[{"id":"r60p04b75559d:latest","object":"model","created":1793137029,"owned_by":"librar…` | List route unchanged by residency: id still "<nonce>:latest". |
| 2 | loaded | GET `/v1/models/r60p04b75559d` | 200 | application/json | `{"id":"r60p04b75559d","object":"model","created":1793137029,"owned_by":"library"}\n` | Fetch with bare name -> 200 id "<nonce>". |
| 2 | loaded | GET `/v1/models/r60p04b75559d:latest` | 200 | application/json | `{"id":"r60p04b75559d:latest","object":"model","created":1793137029,"owned_by":"library"}\n` | Fetch with tagged name -> 200 id "<nonce>:latest". |
| 2 | loaded | GET `/api/ps` | 200 | application/json; charset=utf-8 | `{"models":[{"name":"r60p04b75559d:latest","model":"r60p04b75559d:latest","size":6312427,"digest":"8cf91c7109e7…` | Residency unchanged after the chat/generate calls (TTL refreshed). |

## 3. Probe verdicts vs the documented verdict table

`--expect` values are shown symbolically (`<nonce>`); the wire values were `r60p048170ff` (run 1) and `r60p04b75559d` (run 2).
`listeners` does not gate (exit 0 always, documented); `check` is the gate (0 clean / 2 drift).

| state | command | verdict | reason | served | exit | matches documented prediction |
|---|---|---|---|---|---|---|
| empty-store | `listeners --port P --expect *` | FOREIGN_SERVICE | schema-unrecognized | - | 0 | no — vocabulary meaning contradicted |
| empty-store | `check --port P --expect <nonce>:latest` | FOREIGN_SERVICE | schema-unrecognized | - | 2 | no |
| imported-not-loaded | `listeners --port P --expect <nonce>:latest` | MODEL_OK | matched | r60p048170ff:latest | 0 | yes |
| imported-not-loaded | `check --port P --expect <nonce>:latest` | MODEL_OK | matched | r60p048170ff:latest | 0 | yes |
| imported-not-loaded | `consumers --port P --expect <nonce>:latest` | MODEL_OK | — | r60p048170ff:latest | 0 | yes |
| imported-not-loaded | `listeners --port P --expect <nonce>` | MODEL_MISMATCH | served-id-mismatch | r60p048170ff:latest | 0 | yes-by-rule; harmful in practice (see F2) |
| imported-not-loaded | `check --port P --expect <nonce>` | MODEL_MISMATCH | served-id-mismatch | r60p048170ff:latest | 2 | yes-by-rule |
| imported-not-loaded | `consumers --port P --expect <nonce>` | MODEL_MISMATCH | — | r60p048170ff:latest | 0 | yes-by-rule |
| imported-not-loaded | `listeners --port P --expect definitely-not-loaded` | MODEL_MISMATCH | served-id-mismatch | r60p048170ff:latest | 0 | yes |
| imported-not-loaded | `check --port P --expect definitely-not-loaded` | MODEL_MISMATCH | served-id-mismatch | r60p048170ff:latest | 2 | yes |
| imported-not-loaded | `consumers --port P --expect definitely-not-loaded` | MODEL_MISMATCH | — | r60p048170ff:latest | 0 | yes |
| loaded | `listeners --port P --expect <nonce>:latest` | MODEL_OK | matched | r60p04b75559d:latest | 0 | yes |
| loaded | `listeners --port P --expect <nonce>` | MODEL_MISMATCH | served-id-mismatch | r60p04b75559d:latest | 0 | yes-by-rule |
| loaded | `check --port P --expect <nonce>` | MODEL_MISMATCH | served-id-mismatch | r60p04b75559d:latest | 2 | yes-by-rule |

Full transcripts with evidence strings: `evidence/`.

## 4. Findings

### F1 — Empty-store Ollama is reported `FOREIGN_SERVICE`, and the documented meaning of that verdict is false here
Attacked clause: the SKILL.md decision-table rows defining `FOREIGN_SERVICE` as "the consumer's port answers as a different kind of service" / "identify the responder; report the consumer pin for operator correction".
Exact command and output (empty store, after `ollama create` had NOT yet been run):

```
$ bash tools/kama-probe.sh check --port 55369 --expect r60p048170ff:latest
... FOREIGN_SERVICE | schema-unrecognized ... ; GET /v1/models -> 200 application/json (2xx service with no recognisable model array)
registry_rows_evaluated=1 model_ok=0 drift=1 exit=2
```

Exit code 2. The responder is the pinned Ollama v0.40.11 (`/api/version` = `{"version":"0.40.11"}`, 200), and its `/v1/models` answers `200 application/json` with
`{"object":"list","data":null}`. The probe requires `data`/`models` to be a JSON *list*; Ollama's empty inventory is `null`, so a live, healthy, correctly versioned server is filed as
a foreign service. This is not an exotic input: the round's own committed receipt already carries `v1-models-empty` = `{"object":"list","data":null}`.
Operational consequence: the documented remediation ("report the consumer pin for operator correction") is wrong for this state; nothing needs repointing.
The lane's gate therefore cannot express "Ollama up, no models imported".

### F2 — The bare name is `MODEL_MISMATCH` while the same bare name is accepted on the request path
Attacked clause: served-id normalization step 1–2 (basename, strip one trailing `.gguf`, case-sensitive) read together with the decision-table row "2xx model-list JSON, but no id matches the expectation".
Exact commands and outputs:

```
$ bash tools/kama-probe.sh check --port 55369 --expect r60p048170ff
... MODEL_MISMATCH | served-id-mismatch | r60p048170ff:latest ... exit=2
$ bash tools/kama-probe.sh check --port 44345 --expect r60p04b75559d      # model resident
... MODEL_MISMATCH | served-id-mismatch | r60p04b75559d:latest ... exit=2
$ curl -sS -X POST localhost:44345/v1/chat/completions -d '{"model":"r60p04b75559d",...}'
200 {"id":"chatcmpl-582",...,"model":"r60p04b75559d",...}
$ curl -sS -X POST localhost:44345/api/generate -d '{"model":"r60p04b75559d",...}'
200 {"model":"r60p04b75559d",...}
```

Exit codes 2, 2, 200, 200. The rule is applied exactly as documented, but the verdict is operationally wrong: a consumer that pins the untagged name — the form Ollama accepts and echoes — gets a permanent drift row and exit 2 on a working endpoint.
The documented normalization was written for llama.cpp path-shaped ids; nothing in the table or in the normalization section covers an implicit `:latest` tag, which is the *normal* Ollama id shape.
(The same normalization would also not accept `:latest` for a consumer that declares the tagged form against a bare served id, but that direction was not exercised.)

### F3 — `/health` is not an Ollama route; the documented health-endpoint advice inverts on this runtime
Attacked clause: decision-table row "`/` returns JSON 404 → use `/health` and `/v1/models`, not `/` as the health endpoint".
Exact captures (`captures.jsonl`, run 1, pre and post):

```
GET /        -> 200 text/plain  "Ollama is running"
GET /health  -> 404 text/plain  "404 page not found"
```

The probe's evidence line appends `GET /health` only when it answers 200 with JSON, so for Ollama the evidence silently omits the route; that is fail-safe, but the documented first-check ("use /health") sends an operator to a 404 on this runtime while the real liveness route (`/`) is dismissed by the same row.
The probe itself is fine here — it never treats `/` as authoritative — but the table is written as general guidance and is llama.cpp-only.

### F4 — `MODEL_OK` on Ollama carries none of the documented identity evidence
Attacked clause: "Identity evidence is `GET /v1/models` **plus** `Server: llama.cpp` — never 'the request worked'."
Observed: no Ollama response in 25 captures carries a `Server:` header (`grep -i '^server:' *.hdr` → no match); the probe's own evidence string says `(runtime=other; ...)` while still returning `MODEL_OK | matched`.
So under the lane's documented criterion, the `MODEL_OK` this seat obtained is not attributable to Ollama — it is only "some OpenAI-shaped `/v1/models` responder whose id normalises to the expectation". The probe's `listeners` table *does* print `owner=ollama(pid=…)` from `ss -ltnpH`, so the process identity is available to the instrument but is not part of the verdict or its evidence.

### F5 — "A bogus model id is served with 200" is false on Ollama
Attacked clause: SKILL.md "Request-time id does not validate the model": `POST /v1/chat/completions` returns 200 for a bogus model id and silently serves the loaded model.
Exact commands and outputs (run 2, model `r60p04b75559d` resident — `/api/ps` shows it with `expires_at` before and after):

```
$ POST /v1/chat/completions {"model":"definitely-not-loaded",...}   -> 404 {"error":{"message":"model 'definitely-not-loaded' not found","type":"not_found_error","param":null,"code":null}}
$ POST /v1/chat/completions {"model":"r60p04b75559d:latest",...}    -> 200 ... "model":"r60p04b75559d:latest"
```

Exit codes via curl 0, HTTP 404/200. The claim holds only for the llama.cpp sample it came from; on Ollama v0.40.11 a request-time id must resolve to a known model, and residency does not make an unknown id succeed. Anyone using that sentence as a cross-runtime fact would misread an Ollama 404 as a broken endpoint.

### F6 — `MODEL_OK` does not imply loaded weights (observed, and consistent with the lane's stated limit)
After `create` and before any generation, `/v1/models` listed `<nonce>:latest` while `/api/ps` was `{"models":[]}`; the probe reported `MODEL_OK | matched` in exactly that state.
After one `/api/generate`, `/api/ps` shows the entry with `expires_at` (`2026-10-27T18:42:09…-03:00`, ≈5 min TTL), `size_vram: 0`, `runner: "llamacpp"`.
This is the one documented limit that survived contact: the lane already says a listed name does not prove loaded weights. Worth noting for w2 that the probe's `MODEL_OK` is inventory-only and that the lane's Ollama C2 rows lean on `/api/ps` + `expires_at`, which the probe never reads.

### F7 — Route-dependent id shape is not covered by the normalization contract
`GET /v1/models` returns `data[0].id = "<nonce>:latest"`, but `GET /v1/models/<nonce>` returns `{"id":"<nonce>"}` and `GET /v1/models/<nonce>:latest` returns `{"id":"<nonce>:latest"}` — the single-model route echoes the requested form, the list route always returns the canonical tag.
The probe reads only the list route, so this does not corrupt its verdicts; it does mean any future widening to the fetch route would need the same `:latest` decision as F2. Recorded as an observation, not a defect of the current gate.

### Also observed
`MODEL_LOADING` was never produced: it is a llama.cpp-only envelope (`503` + exact `Loading model` body). Ollama never emitted it in these states — during load it answers 200; before import it answers 200 with `data:null`. The vocabulary string in the JSON output still lists `MODEL_LOADING` for an Ollama endpoint, which is harmless but unearned.

## 5. Limits and what is not claimed

- One Ollama version (v0.40.11, digest pinned), one fixture GGUF, one host, CPU only, one random loopback port per run, `OLLAMA_NO_CLOUD=1`, nonce-named models created and thrown away with the scratch model store.
- Not exercised: registry mode (`check`/`consumers` without `--port`), `snapshot`, `UNAUTHORIZED_SERVICE`, `NOT_HTTP`, `DEAD`, concurrent loading, the fetch route as an identity source.
- No verdict on the C1 or C2 claims; this seat reports observations and a prediction-agreement table only.
- No lane file, registry row, probe byte or SKILL.md line was changed. No port other than the seat's own was contacted (no fleet-wide `listeners` run).
- Tooling: nothing installed or upgraded in this wave (host `ollama` release already present, verified by sha256); no pacman transaction was attempted.

## 6. Files

- `captures.jsonl` — 25 raw HTTP captures (run, phase, route, method, path, status, content-type, server header (absent), body, body sha256, reading).
- `probe-runs.jsonl` — 14 probe invocations (state, subcommand, expect, verdict, reason, served, exit, transcript path).
- `evidence/` — verbatim probe/gate/consumers transcripts with their `.rc` files, `run.meta`, teardown receipts.
- `P04ProbeVersusOllama.md` — the scoped report (this file's short form).

Scratch `/fast/scratch/hyaku/kama-r60/P04ProbeVersusOllama` was removed after these receipts were copied here.
