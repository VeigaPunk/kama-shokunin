source: S581 (llama.cpp `tools/server/README.md` @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad = release b11755, "## Using multiple models" lines 1847-1993, "### GET `/models`" status object lines 2059-2121, "### POST `/models/load`" 2137, "### POST `/models/unload`" 2159); S041-class own-work live receipts `.ufo/waves/round-88/controls/c1-base.out` and the round-88 measured receipt (pinned b11755 router child, `stories260K.gguf` sha256 270cba1b…)
verified-at: 2026-11-06 — README fetched at the pinned commit (sha256 714c067b…); live router child run by L1 through `tools/round88-router-cells.py`; operator router 127.0.0.1:1234 read with GET only
recheck: on-release — re-open the README `status` object list and re-run `python3 tools/round88-router-cells.py --repo . --rev master --work <scratch>` when the pinned llama.cpp build changes

# llama.cpp router mode: listed is not loaded

## Claim

A `llama-server` started without a model (`--models-dir`, `--models-preset`, or the HF cache) runs as a
**router**. Its `GET /v1/models` lists every model it *can* serve, each entry with a `status` object, and
`GET /health` answers `200 {"status":"ok"}` while no model is resident. A listed id is therefore not
evidence of readiness. Before round 88, `tools/kama-probe.sh` graded any listed matching id `MODEL_OK`.

## What the source states (S581, b11755)

- Router mode "exposes an API for dynamically loading and unloading models" (line 1849).
- Autoload is the default; `--no-models-autoload` disables it, and `?autoload=true|false` overrides per
  request (line 1993).
- `status.value` is one of `unloaded`, `loading`, `loaded`, `sleeping`, `downloading`, `incomplete`; a
  failed load reads `value: "unloaded"` with `failed: true` and `exit_code` (lines 2059-2121).
- `POST /models/load` and `POST /models/unload` take `{"model": "<id>"}` (lines 2137, 2159).

## What the lane observed (2026-11-06, Linux/x86_64)

| Cell | Router state | Real `POST /v1/chat/completions` | Probe before r88 | Probe after r88 |
|---|---|---|---|---|
| pinned b11755 router, `--no-models-autoload`, fresh | `unloaded` | `400 {"error":{"code":400,"message":"model is not loaded","type":"invalid_request_error"}}` | `MODEL_OK matched` | `MODEL_UNLOADED router-unloaded` |
| after `POST /models/load` | `loaded` | `200` | `MODEL_OK matched` | `MODEL_OK matched` |
| after `POST /models/unload` | `unloaded` | `400 … model is not loaded` | `MODEL_OK matched` | `MODEL_UNLOADED router-unloaded` |
| operator router 127.0.0.1:1234 (GET only; autoload on, `--sleep-idle-seconds 600`) | `unloaded` ×4 | not sent (would load a model on the operator's GPU) | `MODEL_OK matched` | `MODEL_UNLOADED router-unloaded` |

With autoload on, an unloaded model is *loadable*, not ready: the first request pays the full load. With
autoload off it is a hard 400. Either way `MODEL_OK` overstated the endpoint.

## Decision rule (kama-probe, round 88)

| Matching entry `status` | Verdict / reason | Action |
|---|---|---|
| no `status` object (single-model server) | unchanged (`MODEL_OK matched`) | as before |
| `loaded` | `MODEL_OK` / `matched` | ready |
| `loading`, `downloading` | `MODEL_LOADING` / `router-<value>` | drift; re-probe later |
| `unloaded`, `sleeping`, `incomplete`, unknown | `MODEL_UNLOADED` / `router-<value>` (`-failed` when `failed: true`) | drift; load it (`POST /models/load`) or accept a cold-start on first request if autoload is on |

Any matching `loaded` or status-less entry wins; for a wildcard expectation the rule runs over every entry.

## Limits

- `sleeping` is graded not-ready by choice: the README places it beside `unloaded`, and a request wakes it
  at load cost. A consumer that tolerates cold starts may read it as loadable; the verdict does not.
- The verdict reads the router's own report. It does not send a completion (that would load a model);
  the counter's live cells use a completion only as the independent oracle on a lane-owned child.
- Without python3 the probe keeps the pre-round-88 verdict.
