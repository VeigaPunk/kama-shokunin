# P04ProbeVersusOllama — round 60 w1 scoped report

Seat: P04ProbeVersusOllama (advisory leaf). Axes: operability + calibration. Lane: kama-shokunin, base
`ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b`, freeze `e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1`. No lane file,
registry row, probe byte or SKILL.md line was edited; writes are only this out dir plus removed scratch.

## What ran

The probe DOES have a single-endpoint mode (`--port N --expect ID`), so no read-only substitute was needed.
Seat-owned live servers: `ollama serve` v0.40.11 (bin sha256 `b0a4becf…1b4c`), free loopback ports 55369 (run 1,
model `r60p048170ff`) and 44345 (run 2, model `r60p04b75559d`, loaded), fixture `stories260K.gguf`
(`270cba1b…2565d` → `ollama create`), `env -i`, `OLLAMA_NO_CLOUD=1`, CUDA/HIP/Vulkan disabled. Both children killed
by their own PID in the starting shell; post-kill curl rc 7 and `ss -ltn` 0 listeners on both ports.

```
bash tools/kama-probe.sh listeners|check|consumers --port $P --expect <ID>
```

## Verdicts, exit codes, and whether the documented table predicted them

| state | expect | verdict | reason | exit | documented prediction |
|---|---|---|---|---|---|
| empty store (`data:null`) | `*` / `<nonce>:latest` | FOREIGN_SERVICE | schema-unrecognized | 0 / 2 | no row exists; F1 |
| imported | `<nonce>:latest` | MODEL_OK | matched | 0 | yes |
| imported | `<nonce>` (bare) | MODEL_MISMATCH | served-id-mismatch | 2 (check) | yes-by-rule, wrong in practice (F2) |
| imported | `definitely-not-loaded` | MODEL_MISMATCH | served-id-mismatch | 2 (check) | yes |
| loaded | `<nonce>:latest` / `<nonce>` | MODEL_OK / MODEL_MISMATCH | matched / served-id-mismatch | 0 / 2 | yes / yes-by-rule |

`listeners` exit 0 always (documented); `check` is the gate and returned 0 only for the tagged name.

## Calibration defects (each names the clause and the observation)

- **F1** A live, version-correct Ollama with no models imported (`/v1/models` = `{"object":"list","data":null}`,
  `/api/version` = `{"version":"0.40.11"}`) is reported `FOREIGN_SERVICE | schema-unrecognized`, gate exit 2. The
  table's meaning/remediation for that verdict ("different kind of service", "report the consumer pin") is false
  here; the lane's gate cannot express "Ollama up, empty store". The same body is already in the round's receipt.
- **F2** `MODEL_MISMATCH` on the bare name while the bare name works: `POST /v1/chat/completions {"model":"<nonce>"}`
  → 200 echoing `"model":"<nonce>"`, and `/api/generate` likewise; `check` still exits 2. Documented normalisation
  (basename, strip one `.gguf`, case-sensitive) was written for llama.cpp path ids and never covers Ollama's
  implicit `:latest`, so a healthy consumer pinned to the untagged name shows permanent drift.
- **F3** `/health` is 404 `text/plain` on Ollama and `/` is 200 `"Ollama is running"` — the table row "use `/health`
  and `/v1/models`, not `/`" is inverted for this runtime.
- **F4** No Ollama response carries `Server:` (25 captures, none). The probe says `runtime=other` yet returns
  `MODEL_OK`, so by the lane's own identity rule ("`/v1/models` plus `Server: llama.cpp`") the MODEL_OK is not
  attributable to Ollama; `listeners` does print `owner=ollama(pid=…)` from `ss`, outside the verdict.
- **F5** SKILL.md's "`POST /v1/chat/completions` returns 200 for a bogus model id and silently serves the loaded
  model" is false on v0.40.11: with a model resident, bogus id → 404 `not_found_error`.
- **F6 (consistent, not a defect)** `MODEL_OK` is inventory-only: after create, `/v1/models` listed the model while
  `/api/ps` was `{"models":[]}`; after one generate, `expires_at` ≈5 min, `size_vram` 0, `runner` llamacpp.
- **F7 (observation)** id shape depends on route: list → `<nonce>:latest`; `GET /v1/models/<nonce>` → `<nonce>`;
  `GET /v1/models/<nonce>:latest` → `<nonce>:latest`. The probe reads only the list route.

## Evidence

- `.ufo/waves/round-60/w1/out/P04ProbeVersusOllama/captures.jsonl` — 25 raw HTTP captures (status, content-type,
  server header absent, body, body sha256, reading).
- `…/probe-runs.jsonl` — 14 invocations with verdict/reason/served/exit.
- `…/findings.md` — full tables, exact commands, per-finding reasoning; `…/evidence/` — verbatim transcripts + `.rc`.

## Limits

One version, one fixture, one host, CPU only, one random port per run; no registry-mode run, no fleet-wide
`listeners` sweep, no port other than the seat's own contacted. Nothing installed (release binary verified by
sha256); no pacman transaction. No verdict on C1/C2 — observations only. Scratch removed after receipts were copied.
