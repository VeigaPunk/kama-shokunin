VERDICT: confirm — `check` in registry mode resolves a /tmp registry row through a real consumer file to a loading stub and returns MODEL_LOADING / llamacpp-loading with drift=true and process exit 2; every summary field is arithmetically consistent with the row set.

## What I ran (exact commands, exits)

Scratch: `/tmp/kama-r16-ExecConsumersCheck/` (to be removed after this report; outputs quoted verbatim below).

Stub: `python3 - <<'PY' … PY` — a `http.server` on 127.0.0.1:**45789** (port picked by ephemeral bind, never 8080/34113; no llama-server started by me) answering EVERY path with `503`, `Content-Type: application/json`, `Server: BaseHTTP/0.6 Python/3.14.8`, body `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`. `curl /v1/models` → `503`.

Consumer pin file `consumer.conf`: `BASE_URL=http://127.0.0.1:45789/v1`.

1. `bash tools/kama-probe.sh check --registry /tmp/kama-r16-ExecConsumersCheck/reg2.tsv --json` → **exit 2**
   Row (verbatim fields): `verdict: "MODEL_LOADING"`, `reason: "llamacpp-loading"`, `served_model: "-"`, `drift: true`, `file_match: "yes"`, `resolve_kind: "url"`, `resolved_from_file: "http://127.0.0.1:45789/v1"`, `endpoint: "http://127.0.0.1:45789/v1"`, `port: 45789`.
   Summary: `{"registry_rows_evaluated": 1, "model_ok": 0, "drift": 1, "exit": 2}` — `summary.exit` equals the real process exit.
   Evidence string includes the loading-envelope note and a live `GET /health -> 503|application/json` follow-up, both served by the stub.

2. Same registry, text mode (`check` without `--json`) → **exit 2**; footer `registry_rows_evaluated=1 model_ok=0 drift=1 exit=2` — non-JSON path agrees with JSON path.

3. Two-row registry (reg3.tsv = loading stub row + a second row pinned to a freshly-released closed port) → **exit 2**; rows `falsify-loading MODEL_LOADING drift=true file_match=yes`, `falsify-dead DEAD drift=true file_match=yes`; summary `{"registry_rows_evaluated": 2, "model_ok": 0, "drift": 2, "exit": 2}` — MODEL_LOADING lands in the drift bucket, not a phantom third bucket.

4. Python cross-check over all three captured JSONs: `rows_evaluated == len(rows)`, `model_ok == count(verdict==MODEL_OK ∧ file_match∈{yes,inherited})`, `drift == count(drift==true)`, `model_ok+drift == rows_evaluated` — all True in all three runs.

5. (Side observation, not part of the claim) First run used `grep:BASE_URL=http://127.0.0.1:45789` — resolver captured only the host:port form, so `file_match: "no"` yet verdict still `MODEL_LOADING`/`drift=true`/exit 2. A `file_match=no` row stays drift even when the live verdict would pass; consistent with `eval_rows` (`kama-probe.sh:865`). [INFERENCE: intended belt-and-suspenders gating, not a bug.]

## Source-level ground truth

- `kama-probe.sh:503-508` — `classify` emits MODEL_LOADING only on `F_CODE=503` + non-empty body + `body_is_llamacpp_loading` pass, before the FOREIGN_SERVICE fallthrough.
- `kama-probe.sh:864-866` — `drift = verdict != MODEL_OK OR file_match∉{yes,inherited}`; drives `EV_DRIFT` and the exit-2 gate at `:881`.
- `kama-probe.sh:889-891` — summary emits `registry_rows_evaluated/model_ok/drift/exit` straight from `EV_N/EV_OK/EV_DRIFT/exit_code`; the arithmetic I checked is structural, not coincidental.
- `kama-probe.sh:755-775` — `resolve_row`: `kind=url` + resolved==declared ⇒ `file_match=yes` (observed); resolved≠declared ⇒ `no`.

## Findings / nuances

- Verdict carries no runtime claim: stub's `Server` header was Python's default, still MODEL_LOADING — the loading gate is body-shape only, as documented (`kama-probe.sh:32-36`).
- `served_model: "-"` and `model_ok: 0` — the loading row cannot leak into the OK bucket.
- No verdict breakdown in check's summary (only model_ok/drift), so per-verdict counts like MODEL_LOADING aren't separately surfaced — by design (`:889`); noted, not attacked.

## Limitations

- Only the `url`-kind resolver path exercised live; `port:` synthesis and `raw`/`inherited` kinds were not registry-fed to a loading stub in this seat.
- Loading stub answers every path 503, so `/health` and `/metrics` side probes also returned the envelope; a partial-loading server (200 health + 503 models) was not tested here.
- Not run against the frozen probe — the separability control is `check`-side only in this item; the frozen diff was demonstrated by sibling ExecListenersSummary for `listeners`.
- Scratch removed post-report; the full JSON bodies' field values are quoted above.

## Teardown / hygiene

- Stub PID 3064471 killed; `curl http://127.0.0.1:45789/v1/models` → `000` (refused).
- `pgrep -x llama-server` → empty at teardown (PID 39645, a sibling's, was briefly alive mid-run and exited on its own; I never started or killed it).
- `pgrep -af ExecConsumersCheck` → empty. No lane/fleet/MANIFEST/.ufo-state files touched; only this Report plus /tmp scratch. No installs (nothing needed).

Report: .ufo/waves/round-16/falsify/advice/ExecConsumersCheck.md
