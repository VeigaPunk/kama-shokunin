# Endpoint identity and health decisions

This guide decides whether a configured local base URL serves the model that its consumer expects. It follows the binding contract implemented by `tools/kama-probe.sh` and `registry/endpoint-consumers.tsv`: `listeners`, `consumers`, and `check` accept `--json`; `check` reconciles each registry row against the live endpoint and its `expected_model_id`. The verdict vocabulary is fixed: `MODEL_OK`, `MODEL_MISMATCH`, `FOREIGN_SERVICE`, `UNAUTHORIZED_SERVICE`, `DEAD`, and `NOT_HTTP`.

All command examples below are run from the repository root. The raw `curl` probes and `kama-probe` listener overrides use loopback only and send no credentials. On-box observations cite frozen L1 evidence (`F1`–`F12`) or the local reproduced census/output with `path:line`; probe timeout defaults are 2 seconds to connect and 5 seconds total (`tools/kama-probe.sh:47-48,83-85`).

## Classification decision table

**First-match precedence:** `tools/kama-probe.sh check --json` sends metadata `GET /v1/models` to each registered consumer's host/port (`tools/kama-probe.sh:386`) and applies this ordered table. Each row has an exact runnable command; `--port` probes that loopback port directly and `--expect` supplies the ID for comparison (`tools/kama-probe.sh:80-85,723-733`). For registry mode, exit `0` means every consumer reconciles, `2` means at least one drift, and `1` means probe error; the JSON row carries the verdict. Targeted `--port` examples exit `0` only for `MODEL_OK` and `2` for other verdicts.

| Order | TCP / HTTP observation | Content-Type, `Server`, and JSON shape | Verdict | Operational meaning | Exact command |
|---:|---|---|---|---|---|
| 1 | No TCP connection: refused, timeout, or DNS/connect failure | No HTTP response | `DEAD` | Endpoint did not answer within the probe budget; unavailable now, not proof its process is stopped. Port `40961` was observed with no listener (`corpus/knowledge/listener-census.md:171`). | `tools/kama-probe.sh check --json --port 40961 --expect '*' --id dead-port` |
| 2 | TCP accepted, but no usable HTTP response (HTTP/0.9, empty reply, or reset with zero response bytes) | No usable HTTP status/headers/body | `NOT_HTTP` | The listener is alive at TCP level but speaks no usable HTTP response. | `tools/kama-probe.sh check --json --port 8888 --expect '*' --id jicofo` |
| 3 | HTTP status `401` or `403` | Any content type/body, including HTML; `Server` does not override | `UNAUTHORIZED_SERVICE` | An HTTP service answered but access was denied. Identity is not established; `8790` is a live auth-broker example (`corpus/knowledge/listener-census.md:52`). | `tools/kama-probe.sh check --json --port 8790 --expect '*' --id auth-broker` |
| 4 | Any HTTP status other than `401`/`403` | `Content-Type: text/html*` **or** body begins `<html` / `<!DOCTYPE`; any `Server` | `FOREIGN_SERVICE` | HTML is not the model-list API, even on `2xx`; HTML `404` is foreign too. | `tools/kama-probe.sh check --json --port 8080 --expect '*' --id jitsi-jvb` |
| 5 | Any non-`2xx` HTTP status other than `401`/`403` | Non-HTML body; any `Server` or JSON shape | `FOREIGN_SERVICE` | A live HTTP error response from a non-model service is foreign, not dead. | `tools/kama-probe.sh check --json --port 43999 --expect '*' --id containerd` |
| 6 | `2xx` with a recognizable top-level `data[]` or `models[]` model array | Any non-HTML content type; any `Server` (including absent or `llama.cpp`); compare normalized served ID(s) to normalized expected ID | `MODEL_OK` if any IDs match; otherwise `MODEL_MISMATCH` | **A model array and matching ID are required.** Neither status `2xx` nor `Server: llama.cpp` alone proves identity. | `tools/kama-probe.sh check --json --port 34113 --expect Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS --id model-match` (match); `tools/kama-probe.sh check --json --port 34113 --expect deliberate-no-match --id model-mismatch` (mismatch). |
| 7 | Non-HTML `2xx` JSON without a recognizable `data[]` or `models[]` model array (or other non-model `2xx` response) | No model array; `Server` cannot supply it | `FOREIGN_SERVICE` (`schema-unrecognized` for JSON; `non-model-2xx` otherwise; `tools/kama-probe.sh:516`) | The HTTP service answered successfully but did not expose a recognizable model list. | `tools/kama-probe.sh check --json` |

**ID normalization:** normalize both the expected ID and each served ID by taking the basename after the final `/`, then stripping **one** trailing lowercase `.gguf`; compare the result case-sensitively (`tools/kama-probe.sh:32-34,338-350`). For example, the served ID `/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf` (F4) and configured key `Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` (F6) normalize to the same ID. `MODEL_OK` still requires a recognized model array and a normalized ID match.

Fresh loopback smoke output excerpt:

```text
$ tools/kama-probe.sh check --json --port 34113 --expect Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS --id model-match
"verdict": "MODEL_OK",
"reason": "matched",
"served_model": "/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf"

$ tools/kama-probe.sh check --json --port 34113 --expect deliberate-no-match --id model-mismatch
"verdict": "MODEL_MISMATCH",
"reason": "served-id-mismatch"

$ tools/kama-probe.sh check --json --port 8080 --expect '*' --id jitsi-jvb
"verdict": "FOREIGN_SERVICE",
"evidence": "GET /v1/models -> 404 text/html;charset=iso-8859-1; 404|text/html;charset=iso-8859-1 @ /; GET /metrics -> 200|application/openmetrics-text;charset=utf-8;version=1.0.0 (status-only liveness would false-pass)"
```

The counterexamples below are live listener-census evidence, not hypothetical cases:

- **Rule 2:** `127.0.0.1:8888` (Jicofo) accepts TCP then resets with zero bytes; `127.0.0.1:4226` (sccache) accepts TCP then closes with zero bytes. Both are `NOT_HTTP`, not `DEAD` (`corpus/knowledge/listener-census.md:51,54`).
- **Rule 4:** `127.0.0.1:8080` returns Jetty `404` HTML (F3; `corpus/knowledge/listener-census.md:50`), while `0.0.0.0:40993` returns `200` HTML with a `/tmp` directory listing (`corpus/knowledge/listener-census.md:59`). The `200 text/html` cases at `9222` and CUPS `631` provide further counterexamples to treating a successful status as model identity (`corpus/knowledge/listener-census.md:56-58`).
- **Rule 5:** `127.0.0.1:43999` (containerd) returns `404 text/plain`; OMP session port `127.0.0.1:45507` also returns `404 text/plain`. Both are `FOREIGN_SERVICE`, not `DEAD` (`corpus/knowledge/listener-census.md:55,60`).

## Commands to run

The three canonical probe commands are:

```sh
tools/kama-probe.sh listeners --json
tools/kama-probe.sh consumers --json
tools/kama-probe.sh check --json
```

Use `listeners` to inventory loopback listeners, `consumers` to inspect declared pins, and `check` to make the identity decision. To inspect the response fields directly for the known model-server listener without sending an API key:

```sh
curl --silent --show-error --connect-timeout 2 --max-time 5 --include \
  http://127.0.0.1:34113/v1/models
```

The frozen response for this path was `Server: llama.cpp` plus both `models[]` and `data[]` arrays (F4). Compare the extracted served ID(s) to the registry's `expected_model_id` after the documented normalization; neither a familiar nickname nor the server header is sufficient.

The observed port-confusion signature can be inspected with safe, read-only requests:

```sh
curl --silent --show-error --connect-timeout 2 --max-time 5 --head \
  http://127.0.0.1:8080/
curl --silent --show-error --connect-timeout 2 --max-time 5 --include \
  http://127.0.0.1:34113/v1/models
```

The first request is the recorded root-path check: it returned `404` and `text/html;charset=iso-8859-1` (F3). The second is the model identity endpoint whose recorded response is `Server: llama.cpp` plus `models[]` (F4). The recorded chat-completions POST to `8080` also returned Jetty HTML 404 (F3); it is not repeated here because a POST to a changing endpoint could generate work if the listener changes.

## Why identity is load-bearing

A TCP-open check answers only “did something accept a socket?” It does not identify the process, API, or served model. On this machine `127.0.0.1:8080` was owned by `docker-proxy` and mapped to the Jitsi JVB container (F1, F2); HTTP probes produced a Jetty-style HTML 404 rather than model JSON (F3). Thus the naive check `nc -z 127.0.0.1 8080` can succeed while the port is not a model endpoint. Its error class is **Open-Port Identity False Positive (OIFP)**. Signature: **TCP connect succeeds; the HTTP route returns `404` / `text/html;charset=iso-8859-1` and a Jetty `HTTP ERROR 404 Not Found` page, while the expected model-list JSON is absent** (F2, F3).

For this box, the positive identity observation is `GET /v1/models` at `127.0.0.1:34113`: it returns `Server: llama.cpp` and recognizable model arrays (F4). Its full-path served ID and the consumer's basename-style key (F6) match only after the documented basename/`.gguf` normalization. That combination proves identity for the expected ID; `/health`, a TCP accept, the HTTP status, or the `Server` header alone does not. The contract also permits `MODEL_OK` from another runtime if the recognized model-array ID matches after normalization.

## Liveness, readiness, latency, and capacity

These checks answer different questions; do not substitute one for another.

| Check | Probe command / method | What it answers | Appropriate use / limit |
|---|---|---|---|
| Liveness: `GET /health` | `curl --silent --show-error --connect-timeout 2 --max-time 5 --include http://127.0.0.1:34113/health` | Does the health route answer? | Lightweight process/service liveness. The recorded body was `{"status":"ok"}` (F5); that status does **not** establish the served model ID or that a consumer is routed to this port. |
| Identity readiness: `GET /v1/models` | `curl --silent --show-error --connect-timeout 2 --max-time 5 --include http://127.0.0.1:34113/v1/models` or, for registered consumers, `tools/kama-probe.sh check --json` | Does the expected model appear in the live model list? | Gate traffic on a matching expected ID. `/props` returning generation settings is runtime metadata, not an identity substitute (F5). |
| First-content-token latency | No command in this metadata-only probe; use a separately authorized, minimal inference canary through the same consumer path | Time from request start to first content token | A functional warm-path/performance signal after identity passes. It generates work, is not a liveness check, and must stay separate from the read-only metadata probe. |
| Slot/capacity state: `GET /slots` | `curl --silent --show-error --connect-timeout 2 --max-time 5 --include http://127.0.0.1:34113/slots` | What does the llama-server slot endpoint report about current serving capacity? | Use when diagnosing saturation/queueing, not to prove identity or liveness. The recorded response had two slots (`id` 0 and 1, both `is_processing:false`; `n_ctx:16384`) (`corpus/knowledge/served-model-identity.md:20-21`). A low/busy slot count is not a universal readiness verdict. |

First-token latency requires an active inference request. The endpoint-identity probe is metadata-only, so this guide does not issue that request or present it as a `kama-probe` command. If an operator authorizes a canary, measure request-start to first content delta through the actual consumer path and compare it with that service's own SLO. A successful `/health` or a low `/slots` count cannot replace the `models[]` identity comparison.

## Timeout, retries, and flakes

`tools/kama-probe.sh` defaults to a **2-second connect timeout** and a **5-second total request timeout** (`tools/kama-probe.sh:47-48,83-85`); the direct `curl` examples set the same limits. The identity fetch is one request per sample with no automatic retry loop (`tools/kama-probe.sh:253-256`).

- A refusal or timeout is `DEAD` for that sample under the binding contract. It means unavailable within the probe budget, not proof the process has stopped.
- Take **3 identity samples**, **1 second apart**. The exact repeat command pins the timeout values explicitly:

  ```sh
  for attempt in 1 2 3; do
    printf 'attempt=%s\n' "$attempt"
    if tools/kama-probe.sh check --json --connect-timeout 2 --timeout 5; then rc=0; else rc=$?; fi
    printf 'check_exit=%s\n' "$rc"
    [ "$attempt" -eq 3 ] || sleep 1
  done
  ```

- A stable identity-ready result requires **3/3 `MODEL_OK`** for the consumer and the same expected ID each time. A **flake** is any mixed outcome across those three samples (for example, a timeout or a mismatch between `MODEL_OK` samples); mark it *not ready*, retain per-attempt results, and investigate rather than hiding it with a majority vote. Three identical non-`MODEL_OK` verdicts are a stable failure/drift, not a flake.
- Exit `1` is a probe error, not an endpoint verdict. If any sample exits `1`, the endpoint is not ready and its identity remains unknown; fix the probe error and repeat the sample set rather than recording a service failure.
- No TTFT pass/fail threshold is specified here; measure it only under a separately authorized canary and establish its latency SLO independently.

A verdict is a timestamped observation, not a promise about the next request. Re-run `check` immediately before routing after a port/config change and on the operational cadence chosen by the service owner.

## Anti-patterns observed on this machine

| Anti-pattern | Concrete symptom here | Corrective rule |
|---|---|---|
| Equating an open TCP port with the model API | `8080` had a live `docker-proxy` listener mapped to Jitsi, and the HTTP response was Jetty HTML 404 (F1, F2, F3). | Treat socket-open as liveness only; classify HTTP/API identity and compare normalized model IDs. |
| Leaving a consumer pointed at a once-valid port | `opencode.json:158` declares `http://localhost:8080/v1` (F6), while the live llama-server listener/API are on `127.0.0.1:34113` (F1, F4, F8); the janitor agent text also pins 8080 (F7). | Reconcile every consumer row against the live endpoint; do not repair operator-owned configs from the probe. |
| Treating `/health` as model readiness | The model listener's `/health` answered `{"status":"ok"}` (F5), but the separate consumer pin still targeted Jitsi at 8080 (F2, F6, F7). | Liveness may pass while identity is wrong; require a matching model-array ID for the declared base URL. |
| Treating idle slots as model identity | `/slots` reported two slots, both `is_processing:false` (`corpus/knowledge/served-model-identity.md:20-21`), while the consumer pin still targeted Jitsi at `8080` (F2, F6, F7). | Slot state is capacity information only; require the model-array identity check. |
| Treating any `2xx` as model-ready | Chrome DevTools at `9222` answered `200 text/html` with an empty body; the `0.0.0.0:40993` Python server answered `200 text/html` with a `/tmp` directory listing (`corpus/knowledge/listener-census.md:56,59`). | Require a recognized model array and normalized model ID, not only an HTTP success. |
| Treating every HTTP error as dead | `43999` containerd and OMP session port `45507` both answered `404 text/plain` and were classified `FOREIGN_SERVICE` (`corpus/knowledge/listener-census.md:55,60`). | A live non-`2xx` non-HTML response is a foreign service; distinguish it from transport failure. |
| Trusting the runtime header or comparing raw IDs byte-for-byte | The response has `Server: llama.cpp` but serves a full GGUF path (F4), while the provider key is the basename without `.gguf` (F6); **[INFERENCE]** bytewise comparison would falsely mismatch. | Require a recognized model array, normalize both IDs to basename and strip one trailing `.gguf`, then compare case-sensitively (`tools/kama-probe.sh:32-34,338-350`). |
| Promoting a backup/disabled unit as if it were the active listener | The dated backup and disabled “UNTESTED variant” both use `--port 8080` (F9, F10), although the enabled active service uses `34113` (F8). | Distinguish active listener evidence from fossils and disabled variants; `listeners` reports what owns the port now. |
| Assuming OMP model-role aliases imply a local URL | The fleet's `m_qwen` and other model roles resolve to remote providers; no `@m_*` alias carries a local base URL (F11). | Only declare local consumers from an actual baseURL/endpoint pin; a model role name is not endpoint identity. |

## Corrections — round 10 (2026-10-19)

*[correction 2026-10-19 (round 10, A01): `tools/kama-probe.sh:47-48,83-85` at line 5 is stale (nl -ba tools/kama-probe.sh | sed -n '47,48p;61,62p;83,85p' => 47-48 describe persisted rows, 83-85 are cleanup; timeout defaults are at 61-62); current anchor: `tools/kama-probe.sh:61-62,107-108`]*

*[correction 2026-10-19 (round 10, A02): `tools/kama-probe.sh:386` at line 9 is stale (nl -ba tools/kama-probe.sh | sed -n '80,85p;98,100p;120,125p;150,159p;386p;418p;723,733p;795,803p' => 386 is model matching, 80-85 cleanup/helpers, 723-733 row resolution, GET is at 418 and direct --port evaluation at 795-803); the accompanying `tools/kama-probe.sh:80-85,723-733` is stale too; current anchor: `tools/kama-probe.sh:418,98-100,120-125,150-159,795-803`]*

*[correction 2026-10-19 (round 10, A03): `corpus/knowledge/listener-census.md:171` at line 13 is stale (nl -ba corpus/knowledge/listener-census.md | sed -n '171p;179p' => 171 is the section heading; port 40961 is the row at 179); current anchor: `corpus/knowledge/listener-census.md:179`]*

*[correction 2026-10-19 (round 10, A04): `tools/kama-probe.sh:32-34,338-350` at line 21 is stale (nl -ba tools/kama-probe.sh | sed -n '32,39p;338,385p' => normalization rules are at 34-39 and the current implementation at 370-385); current anchor: `tools/kama-probe.sh:34-39,370-385`]*

*[correction 2026-10-19 (round 10, A05): `tools/kama-probe.sh:47-48,83-85` at line 97 is stale (nl -ba tools/kama-probe.sh | sed -n '47,48p;61,62p;83,85p;107,108p;253,256p;279,302p' => timeout defaults are 61-62, 253-256 is listener bookkeeping, and fetch makes one curl request at 279-302); the accompanying `tools/kama-probe.sh:253-256` is stale too; current anchor: `tools/kama-probe.sh:61-62,107-108,279-302`]*

*[correction 2026-10-19 (round 10, A06): `opencode.json:158` at line 122 is stale (wc -l ~/.config/opencode/opencode.json => 5 ~/.config/opencode/opencode.json — shape-only, no body read); the claimed live llama-server at 34113 and Janitor 8080 pin are historical as well; current anchor: `corpus/knowledge/consumer-registry.md:56-75; SKILL.md:35-47`]*

*[correction 2026-10-19 (round 10, A07): `tools/kama-probe.sh:32-34,338-350` at line 127 is stale (nl -ba tools/kama-probe.sh | sed -n '32,39p;338,385p' => normalization rules are at 34-39 and the current implementation at 370-385); current anchor: `tools/kama-probe.sh:34-39,370-385`]*

*[correction 2026-10-19 (round 10, A08): `enabled active service uses` at line 128 is stale (nl -ba SKILL.md | sed -n '44,47p' => the unit is not-found and neither registered port has a listener); F8 is a historical observation, not the active service state; current anchor: `SKILL.md:44-47`]*

## Provenance supplement — round 11 (2026-10-19)

source: frozen L1 evidence F1–F12, observed in the round-1 live census (2026-09-28) and retained/re-derived in `corpus/lessons/round-1-citations.md` rows F1–F12; retained local census/output artifacts `corpus/knowledge/listener-census.md` (measured 2026-09-28 ~22:47–22:52 -0300), `corpus/knowledge/served-model-identity.md` (round-1 readiness probes), `corpus/knowledge/consumer-registry.md` (round-1 census; 2026-10-14 errata; round-10 corrections) and `SKILL.md` (round-10 corrected pointers); contract artifacts `tools/kama-probe.sh` and `registry/endpoint-consumers.tsv`, both present at review; plus this file's own appended `## Corrections — round 10 (2026-10-19)` block.
verified-at: original on-box observations 2026-09-28 (round-1 live census); the file was revised 2026-10-14 (round 4) and 2026-10-19 (round 10, appended corrections). Round-11 provenance review performed 2026-10-20T02:14Z as metadata only — this file and the cited retained pointers were re-opened read-only and checked for existence and shape; no endpoint, socket or service was contacted and no on-box observation was revalidated live, so confidence here is provenance-of-record only, not endpoint health.
recheck: a future authorized endpoint census may run `bash tools/kama-probe.sh check --json` for registered loopback metadata only; listener discovery needs its own declared scope. Reopen `corpus/lessons/round-1-citations.md` as historical evidence, not execution authority. Do not replay F6/F7/F11/F12 configuration-body reads or other obsolete recorded commands; host inspection needs a separately approved, shape-only plan. Round 11 ran none of these.

### Readiness terminology correction — round 11 (2026-10-20 UTC)

The line-89 label “Identity readiness” and “Gate traffic on a matching expected
ID” overstate this metadata probe. A matching advertised identifier establishes
only the model-list reconciliation predicate used by `MODEL_OK`; it is not a
guarantee of loaded weights, inference success, capacity, or traffic readiness.
S001's pinned llama.cpp README permits `meta: null` while loading; S011/S012
separate Ollama available inventory from loaded inventory. The model-list probe
implementation and verdict vocabulary are unchanged. Any functional inference
canary remains separately authorized work, not an identity query.

The preceding supplement's metadata-review date applies to retained host
observations only. This separate terminology correction is documentation-reviewed
2026-10-20 against S001's pinned README and S011/S012/S031; its source authority
and detailed limits are `served-identity-crosswalk.md`, not a new endpoint run.

### Historical attribution limits — round 11

The frozen F1–F12 citation table is narrower than some original wording above:
F1 is partial for host-side socket ownership, while F2 identifies the container
mapping, not direct `docker-proxy` process ownership. Treat the latter as
inference, not a directly observed host owner. F3 records HEAD/GET responses,
not by itself a chat-completions POST; F4 records `models[0].name`, not by itself
every header and alternate response field. Original “fresh” examples are dated
2026-09-28 samples, never present service authority. These limits supersede
broader readings of those F-citations without rewriting historical observations.

## Correction — round 16 (2026-10-20): the llama.cpp loading envelope is not "foreign"

source: `S036` (llama.cpp `tools/server/server-http.cpp` @ 704366d76 = release b11755, lines 307-328 and 354-358), `S035` (README @ 704366d76 §GET `/health`, lines 479-490), `S037` (server.cpp @ 704366d76, lines 493-515); lane gate `python3 tests/probe-verdicts/check.py` and `corpus/lessons/round-16.md`
verified-at: 2026-10-20 — upstream files opened at the pinned commit; frozen-versus-repaired stub matrix run by L1 (receipts under `.ufo/waves/round-16/`)
recheck: on-release — re-open the pinned middleware when the installed llama.cpp build changes

Line 3 ("The verdict vocabulary is fixed") and the closing note at line 163
("verdict vocabulary are unchanged") are superseded: the vocabulary now has
seven verdicts. Rule 5 at line 17 ("A live HTTP error response from a
non-model service is foreign, not dead") and its restatement as an
anti-pattern remedy at line 126 overreached for one exact case and are
narrowed, not deleted. When `GET /v1/models` answers HTTP 503 and the body
parses as a JSON object whose `error` object has `message` exactly
`Loading model`, `type` exactly `unavailable_error` and an integer `code`
of 503, the probe now emits `MODEL_LOADING` / `llamacpp-loading` (drift,
exit 2). The check runs after rule 3 (401/403) and before rule 4 (HTML).
Every other non-2xx non-model response keeps rule 5.

Why: at b11755 a single-model llama-server starts its listener before
`load_model` and sets `is_ready` only afterwards (S037), and its pre-routing
middleware answers every non-frontend path with that 503 body while not ready,
before the API-key check (S036). The old table therefore graded a loading
model server as a "non-model service". Limits: the match is on body shape and
does not prove the runtime is llama.cpp or which model is loading. Router mode
never emits the envelope. The no-slot (`no slot available`) and router-stream
(`Stream owner model is loading, retry later`) `unavailable_error` bodies stay
on rule 5. Without python3 the body keeps its old `FOREIGN_SERVICE` verdict.

Line 161 cites S001's README sentence that `meta` may be `null` "while the
model is still loading". At b11755 single-model mode that window is answered
by the 503 middleware, not by a `/v1/models` 200 (S036, S037). The README
sentence is still documented (README @ 704366d76:1258) but the code does not
serve it in that mode. A mid-load `MODEL_OK` from a direct llama-server at this
build is therefore not expected [INFERENCE from the code path, consistent with
the round-16 live receipt in `corpus/knowledge/llamacpp-loading-lifecycle.md`].
