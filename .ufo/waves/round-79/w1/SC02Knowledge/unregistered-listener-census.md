source: S553 — llama.cpp router `GET /models` at commit 39febd2adb947b70da35e95f9351b3bf58ad170a (round-79 SOURCES row, SC01 draft `.ufo/waves/round-79/w1/SC01Sources/sources-append.md`; pre-freeze receipt `.ufo/waves/round-79/measured/before/source-router-models.out`); the class is frozen by the round-79 C3 predicate (`plans/round-79-claims.md:96-119`); own-work instruments `tools/kama-probe.sh` (`listeners`) and `tools/round79-unregistered-census.py`.
verified-at: 2026-11-04 — plan read in full; base receipt `.ufo/waves/round-79/measured/before/c3-listeners-base.out` (rev `ee53f1a2`, exit 0) read; round-78 observation `.ufo/waves/round-78/measured/observation/unregistered-1234.out` (sealed `7a3cd982`) read; the README at commit `39febd2a` re-hashed (sha256 `8fd5abde…`) and its router `GET /models` section read; the class read in the worktree `tools/kama-probe.sh` (sha256 `0943fb46…`) and exercised read-only against the live host — `listeners --json` printed `probed=33 model_endpoints=7 foreign_service=24 dead=2 governed=0 unregistered=7 registry=ok`, exit 0 (`.ufo/waves/round-79/w1/SC02Knowledge/listeners-class.json.out`); registry `registry/endpoint-consumers.tsv` read (3 rows, ports 8080 and 34113). No `round79-unregistered-census.py` run is claimed: that counter is EX04's instrument.
recheck: on-release, and 90d — `bash tools/kama-probe.sh listeners --json` must carry the `registered` column (`yes`/`no`/`-`) and the `governed`/`unregistered`/`registry` summary keys; `python3 tools/round79-unregistered-census.py --repo .` must print `UNREGISTERED_CENSUS port=<p> unregistered=1 governed=1 class_missing=0` and exit 0. A probe without the class reads `class_missing=1` with exit 1: a missing instrument, not a clean host.

# An unregistered serving listener is a census class, not a verdict

## The class

A *serving listener* here is a loopback TCP port whose `GET /v1/models` route reached a model
API: `MODEL_OK`/`MODEL_MISMATCH` (2xx with a model array), `MODEL_LOADING` (llama.cpp's loading
503 envelope), or `UNAUTHORIZED_SERVICE` (401/403 on that route). It is *unregistered* when the
registry consulted for the same run declares no row for its port — one sampled listener against
one registry state at one moment.

The probe appends a last table column, `registered`, with three values: `yes` — a model-API
listener whose port a registry row's declared baseURL names, counted in `governed` (a
declaration relation, never a health check); `no` — a model-API listener and no row declares its
port, counted in `unregistered`; `-` — not asked: the listener is not a model surface (`DEAD`,
`NOT_HTTP`, `FOREIGN_SERVICE`), or the registry was unreadable for that run. A missing or
unreadable `--registry` keeps every class `-` with a warning: never a probe error, never `no`.

The summary line carries `governed=<g> unregistered=<u> registry=<ok|missing>` after
`model_loading`; the JSON carries `"registered"` per row and the same keys. The frozen C3 target
has the same fixture read `no` (`unregistered=1`) under a registry that omits its port and `yes`
(`governed=1`) under one that declares it. The verdict vocabulary and exit codes are unchanged:
a row carries a verdict and a registration value side by side, and neither replaces the other.

## Why a model list is inventory, not readiness

S553: the router's `GET /models` section (README line 2197) is an inventory surface — body line
2199 "Listing all models in cache" — where a model that is not running is still listed: on
refresh it "will be added or updated according to the source" (line 2227). Each entry carries a
`status.value` with six documented values (`unloaded`, `loading`, `loaded`, `sleeping`,
`downloading`, `incomplete`; a failed unload adds `failed` and `exit_code`), and the router
computes both arrays offline, "does not load the model, download files, or run inference" (line
2230). A 200 model list proves a model API answered; it does not prove a model is loaded, that
the served model matches a consumer's expectation, or that a request would succeed.

The round-78 observation is the lane's own instance: `llama-server` pid 1505 on `127.0.0.1:1234`
answered `/v1/models` with four LFM3 ids, graded `MODEL_OK`, and no lane registry row declared
that port — a manual observation only. The base probe counted the same population as
`model_endpoints=7` with no registry relation: no `registered` column, no summary keys.

## What it does not claim

- **No loaded model.** Served ids are the listener's self-report; the probe reads them, not
  verifies them, and `MODEL_LOADING` is already its own verdict when llama.cpp reports not ready.
- **No consumer readiness.** The class reads no consumer config. `registered=yes` is a
  declaration by the registry's bytes, not evidence that the consumer's path works;
  consumer-file reconciliation is the separate `consumers` subcommand.
- **No registry row.** The census admits nothing and writes no registry. Consumer pins stay
  operator-owned; `unregistered` does not demand a row, since classifying a port is not a
  disposition to add one.
- **Not ownership or authorization.** `UNAUTHORIZED_SERVICE` remains the HTTP 401/403 verdict:
  unregistered is not unauthorized, and the class says nothing about which process owns the
  port (process binding is a separate, heavier observation).
- **Not a gate.** `listeners` reports; `check` and `snapshot` gate. The live-host leg of the
  census is informational by the C3 scope ruling.

## Live-host reading rule

- A run is a dated sample: the listener set churns between runs and a port number can be reused
  by another process. Two consecutive runs of the class saw `probed=34` with a `DEAD`
  `llama-server` on port 51085, then `probed=33` without it. Quote a reading with the lane tip
  (`git rev-parse master`) and the probe's sha256; re-read before repeating it.
- `registered=no` means "a readable registry consulted at this run declares no row for this
  port" — not "unknown", not "foreign". `-` means the question was not asked; never read `-`
  as registered, and never read `no` off an unreadable registry.
- The registry is the lane's consumer registry — LIVE or LOADABLE consumers, not a host-wide
  port inventory. `unregistered` therefore does not mean unowned or unused; it means no
  consumer row pins the port.
- At the readings above the registry named only ports 8080 and 34113, while seven model
  endpoints answered on 1234, 8788, 8789, 8790, 8791, 8793 and 8795; all seven read `no`, so
  `governed=0 unregistered=7 registry=ok`. That is informational, never a gate: the census
  target is the lane-owned fixture, torn down in the run, not the live host.

## Coverage map row (for `corpus/README.md`, appended not inserted)

```
## Coverage map — round 79 addition

| Entry | Covers | Round |
|---|---|---|
| `corpus/knowledge/unregistered-listener-census.md` | The unregistered-serving-listener census class: a model-API listener whose port no registry row declares, the `registered` column (`yes`/`no`/`-`) and `governed`/`unregistered`/`registry` summary keys, why a router model list is inventory and not readiness, the class's explicit non-claims, and the live-host reading rule | 79 |

Frontier: the class is a census relation, not a disposition — it admits no registry row and
certifies no loaded model and no consumer; the verdict vocabulary and `check`/`snapshot` gates
are unchanged, and the live-host leg stays informational.
```
