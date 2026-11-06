source: S581 (llama.cpp `tools/server/README.md` @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad = release b11755, "## Using multiple models" lines 1847-1993, "### GET `/models`" status object lines 2059-2121, "### POST `/models/load`" 2137, "### POST `/models/unload`" 2159, "## Sleeping on Idle" 2333); prior art held before round 88: S001 via `corpus/knowledge/served-identity-crosswalk.md:28` (router `status.value` vocabulary) and S553 via `corpus/knowledge/unregistered-listener-census.md` §"Why a model list is not a readiness claim"; own-work live receipts `.ufo/waves/round-88/measured/router-lifecycle.out`, `.ufo/waves/round-88/repair/oracle-cells-{B,M,repair}.out`, `.ufo/waves/round-88/controls/pilot-live-1234.out`, `.ufo/waves/round-88/repair/pilot-live-1234-after.out`
verified-at: 2026-11-06 — README fetched at the pinned commit (sha256 714c067b…); lane-owned pinned b11755 router children run by L1; operator router 127.0.0.1:1234 read with GET only (`/props`, `/v1/models`)
recheck: on-release — re-open the README status list and re-run `python3 .ufo/waves/round-88/repair/oracle-cells.py --repo . --rev master --work <scratch>` and `python3 tools/round88-router-cells.py --repo . --rev master --work <scratch>` when the pinned llama.cpp build changes

# llama.cpp router mode: what the probe's verdict means

## What was already held (not new in round 88)

The corpus already stated that a router's model list is not a readiness claim and carried the
`status.value` vocabulary (`served-identity-crosswalk.md:28`, S001; `unregistered-listener-census.md`,
S553). What round 88 adds is the probe's **verdict rule** for that vocabulary, checked against the runtime's
own answer to a real request on lane-owned children, and the observed error signature.

## What the source states (S581, b11755)

- Router mode "exposes an API for dynamically loading and unloading models" (line 1849).
- Autoload is the default; `--no-models-autoload` disables it; `?autoload=true|false` overrides per request
  (line 1993). The router's bare `GET /props` reports `"role":"router"` and `"models_autoload"`.
- `status.value` is one of `unloaded`, `loading`, `loaded`, `sleeping`, `downloading`, `incomplete`; a failed
  load reads `value: "unloaded"` with `failed: true` and `exit_code` (lines 2059-2121).
- "Any new incoming task will automatically trigger the model to reload" for a sleeping model; `GET /health`, `/props`, `/models`, `/metrics` do not (§Sleeping on Idle, lines 2333-2346).

## What the lane observed (2026-11-06, pinned b11755 children, `stories260K.gguf`)

Receipt `.ufo/waves/round-88/measured/router-lifecycle.out` (`--no-models-autoload --sleep-idle-seconds 3`) and
`.ufo/waves/round-88/repair/oracle-cells-*.out`:

| Router state | `GET /health` | Real `POST /v1/chat/completions` | Probe at base | Probe at round-88 tip |
|---|---|---|---|---|
| `unloaded`, `--no-models-autoload` | `200 {"status":"ok"}` | `400 {"error":{"code":400,"message":"model is not loaded","type":"invalid_request_error"}}` | `MODEL_OK matched` | `MODEL_UNLOADED router-unloaded` |
| `loaded` | — | `200` | `MODEL_OK matched` | `MODEL_OK matched` |
| `sleeping` (idle past `--sleep-idle-seconds`) | — | `200`, entry returns to `loaded` | `MODEL_OK matched` | `MODEL_OK router-sleeping` |
| `unloaded`, default autoload | — | `200` (cold load) | `MODEL_OK matched` | `MODEL_OK router-unloaded-autoload` |

Operator router 127.0.0.1:1234 (GET only): `/props` `{"role":"router","models_autoload":true,…}`, four
entries `unloaded`; probe at base `MODEL_OK matched`, at the tip `MODEL_OK router-unloaded-autoload`
(`controls/pilot-live-1234.out`, `repair/pilot-live-1234-after.out`). `GET /health` 200 with nothing
resident is observed on the lane child only.

## Decision rule (kama-probe, round 88 tip)

| Matching entry `status` | Verdict / reason | Meaning |
|---|---|---|
| no `status` object (single-model server) | unchanged (`MODEL_OK matched`) | as before |
| `loaded` | `MODEL_OK` / `matched` | resident |
| `sleeping` | `MODEL_OK` / `router-sleeping` | a request wakes it (cold start) |
| `unloaded`, not failed, router `/props` `models_autoload: true` | `MODEL_OK` / `router-unloaded-autoload` | a request loads it (cold start) |
| `loading`, `downloading` | `MODEL_LOADING` / `router-<value>` | drift; re-probe later |
| `unloaded` without autoload, `unloaded` + `failed: true`, `incomplete`, unknown | `MODEL_UNLOADED` / `router-<value>[-failed]` | drift; a request fails until loaded |

## Limits

- The frozen round-88 claim rule graded `sleeping` and autoload-`unloaded` as `MODEL_UNLOADED`. The round's
  own completion oracle falsified that (wave-1 CR01; `repair/oracle-cells-M.out` mismatches=2); the tip
  follows the oracle. The frozen counter's C05/C12 expectations therefore read red at the tip.
- `/props?model=<id>` routes to a model instance (S581 line 2339); the probe reads bare `/props` only, which never triggers a reload.
- A per-request `?autoload=false` consumer is not modelled: the probe grades the router default.
- Without python3 the probe keeps the pre-round-88 verdict.
