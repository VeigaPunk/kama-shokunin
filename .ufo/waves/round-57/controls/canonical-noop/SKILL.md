---
name: kama-shokunin
description: Domain specialist — local model serving & endpoint health — scopes local LLM endpoints, baseURL drift, model-id reconciliation. Rank: shonen.
---

# kama-shokunin

Local model serving & endpoint health. This lane answers exactly one question:
**is the thing at this baseURL the model this config believes it is, right now.**

Rank: shonen; no independent promotion verification recorded. Verdict vocabulary is shared with
`tools/kama-probe.sh`: `MODEL_OK` | `MODEL_MISMATCH` | `FOREIGN_SERVICE` |
`UNAUTHORIZED_SERVICE` | `DEAD` | `NOT_HTTP`. Exit codes: `0` all declared
consumers reconcile, `2` ≥1 drift, `1` probe error.

## Domain

- Local model-serving processes and the ports they own (`llama-server` here),
  their served-model identity, and their liveness/readiness surfaces.
- `baseURL` values declared by consumer configs that point at a loopback port
  (OpenCode provider blocks, agent frontmatter, shell scripts, systemd units).
- Reconciliation: declared `expected_model_id` vs the id the endpoint actually
  serves, plus which process owns the port the consumer named.
- The endpoint-consumers cross-lane registry (`registry/endpoint-consumers.tsv`)
  and the drift timeline.

**Refuses (boundary, unchanged):** model quality/eval (kengaku), credential
material, auth flows and secret handling (kagi), dispatch/route *mechanism*
(kumitate), remote web surfaces (kake). kama never answers "is the model good"
or "is the request safe". A 401 endpoint is *evidence about identity*; the key
that would open it is kagi's surface — report, do not absorb.

## Current sampled state — 2026-10-15

`bash tools/kama-probe.sh check --json` currently evaluates three registered,
loadable consumers: `omp-llama-cpp-default`, `ufo-fsd-thetick`, and
`ufo-fsd-local-helper`. All three sampled `DEAD` / `connection-refused`,
`model_ok=0`, `drift=3`, exit `2`. Full command, streams, revision and exit:
`.ufo/round-5/before-check.json`. This is a sample, not continuous monitoring.

The two explicit UFO pins resolve `file_match=yes`; their endpoints are dead.
The builtin row resolves `file_match=inherited`, `resolve_kind=raw`: it tests
the registry's declared fallback, **not** an effective environment-selected URL.
No environment value was inspected. `qwen-coder.service` reports
`LoadState=not-found`, `ActiveState=inactive`, `SubState=dead`, `MainPID=0`;
the bounded socket query found no listener on the two registered ports
(`.ufo/round-5/host-shape.json`). No server restoration or permanent retirement
is implied.

Use the current checklist below. The worked example, host-specific decision
examples, error signatures, and anti-pattern incidents preserve September
observations; they do not assert that those processes, files, or ports exist
today. Corpus supersession and admission boundary:
`corpus/lessons/round-5.md`; quality bar: `corpus/QUALITY.md`.

## Historical worked example — 2026-09-28

In this dated sample, `8080` was Jitsi and `34113` served the model. Six consumer
surfaces pinned 8080: the OpenCode provider, janitor agent and CLI, janitor
overlay, cascade-protected distiller, and builtin default. This is the
pre-teardown census, not the current registry.

```text
$ ss -ltnp | grep -E '34113|8080|8888'
LISTEN 0 4096 127.0.0.1:8888  0.0.0.0:*
LISTEN 0 4096 127.0.0.1:8080  0.0.0.0:*
LISTEN 0 512  127.0.0.1:34113 0.0.0.0:*  users:(("llama-server",pid=1299,fd=16))
$ docker ps --format '{{.Names}} {{.Ports}}' | grep 8080
docker-jitsi-meet-jvb-1 127.0.0.1:8080->8080/tcp, 0.0.0.0:10000->10000/udp
$ curl -sSI http://127.0.0.1:8080/
HTTP/1.1 404 Not Found
Content-Type: text/html;charset=iso-8859-1
$ curl -sS http://127.0.0.1:34113/health
{"status":"ok"}
$ curl -sS http://127.0.0.1:34113/v1/models | jq -r '.data[0].id'
/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf
```

Gotcha the output teaches: unprivileged `ss -ltnp` prints **no owner** for the
docker-proxy-backed ports (8080/8888) — the `users:(…)` field is missing because
that proxy runs as root. A missing owner is not "no process"; name it with
`docker ps` (no privileges needed) before concluding anything.

Causal chain: the systemd unit moved the listener to `--port 34113`
(`~/.config/systemd/user/qwen-coder.service:17`, mtime 2026-09-08 20:43:13);
its own predecessor had `--port 8080`
(`~/.config/systemd/user/qwen-coder.service.bak.1788033391:16`). Jitsi took
8080 later (`docker-jitsi-meet-jvb-1` created 2026-09-15T01:31:55Z, per
`docker inspect`). No consumer followed — `~/.config/opencode/opencode.json:158`
still reads `http://localhost:8080/v1` at mtime 2026-09-28 16:46:43, i.e. the
pin is fresh, the *value* is stale. Full timeline:
`corpus/knowledge/drift-timeline.md`.

The consumer set (verify each, do not trust a stale list):

| # | consumer | pin | fallback? |
|---|---|---|---|
| 1 | `~/.config/opencode/opencode.json:154,158,161` | provider `qwen-local` → `http://localhost:8080/v1` | none for `qwen-local` |
| 2 | `~/.config/opencode/agents/janitor.md:5,20-21` | `qwen-local/Qwen3-Coder-30B-…` at `http://127.0.0.1:8080/v1` | none — "there is no fallback" (`:21`); CLI agrees (`~/.local/bin/the-janitor:47`) |
| 3 | `~/.config/opencode/agents/distiller.md:5,7` | same model id, `cascade: … > openai/gpt-5.6-sol-fast > xai/grok-4.5` | **cascade-protected** — survives the drift |
| 4 | `~/.local/bin/the-janitor:16-19` | `MODEL_ENDPOINT="http://127.0.0.1:8080/v1"` | none (`:47`) |
| 5 | `~/.config/the-janitor/opencode.json:5-6,8-9,16` | `enabled_providers: ["qwen-local"]` only, `baseURL …:8080/v1` | none — qwen-local is the sole enabled provider |
| 6 | `~/.local/bin/omp` builtin `llama-cpp` provider | default `http://127.0.0.1:8080`, env `LLAMA_CPP_BASE_URL` unset here | hidden until selected |

Fossil copies that must never be restored: `opencode.json.pre-qwen-model-20260829-031834.bak:50`,
`.pre-sentinel-disable-20260829-033405.bak:50`, `.pre-fast-oauth-20260829.bak:155`,
`.bak-20260921-devin-slots:144` — all still `http://localhost:8080/v1`.

**The drift is not one-sided** — correct pins coexist with stale ones, which is
why a single consumer's success proves nothing:

- `~/Projects/ufo-fsd-alpha/config/the-tick.machine.json` and
  `~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs` retain explicit 34113 pins. They were historical
  `MODEL_OK` counterexamples; the current probe resolves the pins but reports
  `DEAD`. A correct pin does not guarantee endpoint readiness, and their failure
  does not by itself indict the probe.
- `~/.local/bin/omp` carries a builtin llama-cpp fallback of 8080, overridable
  by `LLAMA_CPP_BASE_URL`. The registry row attests that fallback shape only.
  It does not establish whether the running consumer uses that URL; no current
  environment-selection claim is made.
- Systemd archives beyond the live unit, all `--port 8080`:
  `qwen-coder.service.pre-template-20260829-033610.bak:16`,
  `.pre-omp-context-20260829-0322.bak:16`, `.pre-safety-20260829-031834.bak:16`.

## Decision table — rules with dated September host examples

| Symptom | First check | Verdict | Action |
|---|---|---|---|
| Model call returns an HTML page (`text/html`, 404 body) | Reconcile that registered endpoint with `bash tools/kama-probe.sh check` | `FOREIGN_SERVICE` | Identify the responder; report the consumer pin for operator correction. September example: Jitsi at 8080. Never alter the foreign service. |
| Worked yesterday at the same baseURL, now refused | Run `check`, then inspect only the named producer's service state and the registered socket | `DEAD` | Report a missing/moved producer. A deleted unit is not an installed runtime; do not enable or recreate it. |
| Consumer's port answers as a different kind of service | Compare `check` with `consumers` | `FOREIGN_SERVICE` or `NOT_HTTP` | Separate pin correctness from responder identity; hand off external-config remediation to the operator. |
| 2xx model-list JSON, but no id matches the expectation | Read the served ids from the registered endpoint's `/v1/models`; apply the normalization below | `MODEL_MISMATCH` | A full GGUF path vs a bare id is not necessarily a mismatch. |
| Registered endpoint returns HTTP 401/403 | Read the probe's verdict and status evidence; do not supply a credential | `UNAUTHORIZED_SERVICE` | Identity remains unverified behind authentication. Historical 8790/8791 examples were brokers; the status code alone does not identify a broker or exclude a model server. Escalate auth handling to kagi. |
| Expected model port has no listener | Bounded `ss -ltn` query for the declared port, plus `check` | `DEAD` | Do not infer a default port or search arbitrary services. Retain the expected pin until the operator authorizes a change. |
| Listening socket does not answer HTTP | Probe only the registered endpoint | `NOT_HTTP` | Listening ≠ HTTP ≠ model. September examples included 8888 resets and an empty sccache reply. |
| `/` returns JSON 404 | Use `/health` and `/v1/models`, not `/` as the health endpoint | Not sufficient for a fault verdict | The September llama.cpp runtime returned a normal root 404; re-establish identity before applying runtime-specific expectations. |
| Archived/latent unit would reuse a port | Read the already identified unit's nonsecret port declaration, if it still exists | Reported risk | Do not enable it. The September disabled 8080 variant is historical, not a current installed-unit claim. |
| A config was changed but drift persists | Re-run `consumers` and `check` across all registered rows | Per-row verdict | One corrected consumer does not certify the registry. External file changes stay operator-owned. |
| Suspected route resolves to a loopback endpoint | Obtain only the nonsecret endpoint/alias metadata needed for that claim | Unverified until observed | Route mechanisms belong to kumitate; credentials belong to kagi. Do not copy a global config or environment into the corpus. |
| One consumer works, another allegedly uses the same model | Compare each row's pin resolution, endpoint verdict and fallback claim | Mixed verdicts are possible | September janitor/no-fallback and distiller/cascade cases illustrate severity, not current installed consumers. |

### Served-id normalization (load-bearing)

llama.cpp reports path-shaped ids; consumers declare bare ids. Exact string
equality produces false `MODEL_MISMATCH` on a healthy endpoint. Rule:

1. Extract, in precedence: `data[].id` → `models[].id` → `models[].name` →
   `models[].model` → top-level `id`.
2. Take `basename`, strip a trailing `.gguf`, compare **case-sensitively**.
3. Empty after normalization ⇒ `MODEL_MISMATCH` (`unresolvable-id`) — never `MODEL_OK`.

Live proof for step 1: `curl -sS http://127.0.0.1:34113/v1/models |
jq -r '.data[0].id, (.models[0].id // "NO models[].id"), .models[0].name'` →
`/scratch/models/…-UD-IQ2_XXS.gguf`, `NO models[].id`,
`/scratch/models/…-UD-IQ2_XXS.gguf` — i.e. `models[].id` is absent on this
runtime, so precedence step 3 (`models[].name`) carries the path-shaped id.

### Request-time id does not validate the model

`POST /v1/chat/completions` returns **200 for a bogus model id** and silently
serves the loaded model: `-d '{"model":"definitely-not-the-loaded-model",…}'`
→ HTTP 200 and the response `"model"` echoes
`/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf`.
Identity evidence is `GET /v1/models` **plus** `Server: llama.cpp` — never
"the request worked".

## Historical error signatures — September runtime sample

| Verbatim string seen | Where | Meaning | Next action |
|---|---|---|---|
| `Server: llama.cpp` (response header) | `curl -sSI http://127.0.0.1:34113/v1/models` | llama.cpp runtime answered | Continue to id check — header alone is not identity |
| `{"models":[{"name":"/scratch/models/…gguf","model":"/scratch/models/…gguf",…}],"object":"list","data":[{"id":"/scratch/models/…gguf",…}]}` | `GET :34113/v1/models` | Served identity, path-shaped | Normalize, then compare to `expected_model_id` |
| `{"status":"ok"}` | `GET :34113/health` | Process alive; says **nothing** about which model | Follow with `/v1/models` |
| `"default_generation_settings":{"params":{…}}` | `GET :34113/props` | Serving config loaded (chat_format `Content-only`, `reasoning_format` `none`) | Use for template/format questions, not identity |
| `<h2>HTTP ERROR 404 Not Found</h2>` + `<th>URI:</th><td>http://127.0.0.1:8080/v1/models</td>` with `Content-Type: text/html;charset=iso-8859-1` | any path on `:8080`, incl. `POST /v1/chat/completions` | Jetty-family servlet; foreign service on a model path | `FOREIGN_SERVICE` — stop the consumer, name the owner, repoint |
| `{"error":"unauthorized"}` with `HTTP/1.1 401 Unauthorized`, `Content-Type: application/json` | Historical `:8790`, `:8791` broker probes | `UNAUTHORIZED_SERVICE`; authentication prevents identity verification, not proof of a specific service | Escalate to kagi; never inject credentials to complete a health census |
| `{"error":{"message":"File Not Found","type":"not_found_error","code":404}}` (`application/json`) | `GET :34113/` | llama.cpp's normal root 404 | Probe `/health` / `/v1/models` instead; do not classify a fault |
| `curl: (7) Failed to connect to 127.0.0.1:11434 after 0 ms` | any unserved port | Nothing bound | `DEAD` — resolve the real port from the unit file |
| `curl: (56) Recv failure: Connection reset by peer` | `:8888` (jicofo) | TCP listener, not an HTTP service | `NOT_HTTP` |
| `Not Found` with `Content-Type: text/plain;charset=utf-8` | `:34955`, `:41453` (`omp`, pids 3467459 / 1053353) | Non-model HTTP service | `FOREIGN_SERVICE` for model purposes |
| `Unauthorized` / `Invalid API Key` / `--api-key KEY` (historical binary strings) | September llama-server inspection and the then-present unit | The runtime could enforce keys; the historical unit did not pass `--api-key`. Neither fact establishes current authentication or bind state | Report an observed unexpected non-loopback bind to the operator/kagi; do not infer one from old strings |
| `opencode-distiller … file_match=inherited … resolver_kind=raw … FOREIGN_SERVICE` in `kama-probe.sh consumers` | a registry row whose target file pins a bare model, not a URL | The consumer inherits its provider's baseURL; the registry's declared value stands and the probe still verifies the endpoint | Normal — but it means the registry's `declared` column is a claim: confirm the provider block (`distiller.md` inherits `qwen-local`) before trusting the row. |

Elision convention: `…` marks a cut inside a single long line of the body, never
a paraphrase — every quoted fragment is byte-for-byte from the live response.

Also-normal, not faults: `# HELP llamacpp:prompt_tokens_total …` from `/metrics`,
and `[{"id":0,"n_ctx":16384,…},{"id":1,…}]` from `/slots` (consistent with
`--parallel 2`, `--ctx-size 16384` and `--kv-unified`; under b11755 semantics
both slots share one 16384-cell pool, not logged for that build; see
`corpus/knowledge/context-capacity.md`).

## Checklist — current registered-endpoint workflow

Run from this repository. `curl`, `ss`, `flock`, coreutils and `python3` are
used by the probe/harness; a missing dependency is a probe error, not `DEAD`.

1. **Reconcile** —
   `bash tools/kama-probe.sh check; echo "CHECK_EXIT=$?"`.
   The measured sample ends
   `registry_rows_evaluated=3 model_ok=0 drift=3 exit=2`, `CHECK_EXIT=2`.
   Read the complete final line on every invocation; do not pin future counts.
   Exit `0` means all declared rows reconcile, `2` means drift, `1` means
   probe/tool error. Never describe exit `2` as model readiness.
2. **Inspect pin provenance** — `bash tools/kama-probe.sh consumers`.
   The current sample ends `consumer_rows_evaluated=3 exit=0`; this command
   lists observations, not an all-healthy verdict. Read `file_match` and
   `resolve_kind`: the explicit UFO rows are `yes`/`url`, the builtin fallback
   is `inherited`/`raw`. An inherited declaration is not an effective URL.
3. **Use machine output** — `bash tools/kama-probe.sh check --json`.
   Schema `kama-probe/v1`, keys `subcommand`, `verdict_vocabulary`,
   `exit_codes`, `registry`, `rows[]` and
   `summary` = `{"registry_rows_evaluated":3,"model_ok":0,"drift":3,"exit":2}`.
   This summary is the 2026-10-15 sample, not an invariant. Preserve the
   command's exit independently of any pipe/parser exit.
4. **Inspect only the named producer and ports** —
   `systemctl --user show qwen-coder.service -p LoadState -p ActiveState -p SubState -p MainPID`;
   `ss -ltn 'sport = :8080 or sport = :34113'`.
   The current service result is not-found/inactive/dead/0; `ss` prints its
   header and no listener rows. This does not prove global absence or permanent
   retirement. Do not recreate, start, or enable a unit.
5. **If an authorized registered endpoint answers**, distinguish liveness
   (`/health`) from served identity (`/v1/models` plus the id expectation).
   Re-establish responder identity; do not require a September pid, model path,
   header or port owner to recur. Do not send credentials or completion
   requests as an identity test.
6. **Capture invocation history when requested** —
   `bash tools/kama-probe.sh snapshot; echo "SNAPSHOT_EXIT=$?"`.
   Default writes: dated local `kama-probe/v2` JSON and
   `registry/history/{latest.tsv,DELTA.md}`. Use `--history DIR` to isolate a
   smoke run. A successful snapshot may still exit `2` for captured drift.
   The tracked baseline records the October teardown, not the September
   eleven-row success sample. No timer is installed by this command.
7. **Discover beyond the registry only under explicit census scope** —
   `bash tools/kama-probe.sh listeners` classifies listening ports and exits
   `0` as a census, not a readiness gate. Do not use historical listener
   counts as a present inventory or contact unrelated local services just
   to complete a documentation update.
8. **Close the actual task** — after an authorized endpoint/config repair,
   capture the transition and require `check` exit `0` to claim reconciliation.
   For an evidence/runbook task, record the observed drift and hand off
   operator-owned service work; never weaken the gate or require restoration
   to report a truthful negative result.


## Anti-patterns — lessons from dated incidents

1. **"Status says it's configured, so it's verified."** Observed symptom: a
   consumer pinned at 8080 for a month (backups from 2026-08-29 through
   `.bak-20260921-devin-slots:144`) while `opencode.json:158` stayed 8080 even
   after an edit at mtime 2026-09-28 16:46:43. Cause: `status`-style surfaces
   print configured values, not verified capability (independently recorded in
   `../.ufo/reports/round-3/kagi.md:23-25`). Fix: run item 1.
2. **Reading `/health` as identity.** A healthy answer does not establish which
   model is served. Use `/v1/models` and the expected-id comparison; the
   historical header is corroboration, not a current identity guarantee.
3. **Comparing ids as raw strings.** Observed symptom: `models[0].name` and
   `data[0].id` are `/scratch/models/…-UD-IQ2_XXS.gguf` while consumers declare
   `Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` — a naive equality test calls a
   healthy endpoint broken. Fix: the normalization rule above.
4. **Validating identity with a completion request.** Observed symptom: a POST
   with `"model":"definitely-not-the-loaded-model"` returns **200** and serves
   the loaded model. Fix: never use request success as identity evidence.
5. **Copying a backup back into place.** Observed symptom: 4 fossil configs
   still pin `http://localhost:8080/v1`; restoring any one reintroduces
   `FOREIGN_SERVICE`. Fix: treat `*.bak*` as evidence only.
6. **Assuming the default port.** Observed symptom: `11434`/`1234`/`5000`/`8000`/
   `3000`/`7860`/`9090` refused in the September sample. Do not assume those
   ports remain absent or that the old unit remains installed; use declared pins.
7. **Enabling the latent variant unit.** Observed symptom:
   `qwen-coder.ctx32k-q4.service:16` (`--port 8080`) is `disabled`; enabling it
   fights the JVB mapping for 8080. Fix: report the trap, do not enable.
8. **Treating a listening socket as a model.** Observed symptom: `631` is CUPS
   (`Server: CUPS/2.4 IPP/2.1`, `200 text/html`), `9222` is Chrome, `40993` is
   `python3` `SimpleHTTP/0.6` on a wildcard bind, `4226` is sccache (empty
   reply), `8888` resets. Fix: fingerprint before classifying (`listeners`), and
   prefer `loopback` rows over `wildcard` ones — never bind assumptions to a
   port number.
9. **Generalizing from one working consumer.** Observed symptom: `the-tick.machine.json:16`
   and `local-helper.mjs:8` hit 34113 with `MODEL_OK` in the same fleet whose
   `opencode.json:158` cannot. Fix: reconcile the *registry*, not a sample —
   `bash tools/kama-probe.sh consumers`.
10. **Mistaking a green `check` for coverage.** The current registry has three
    loadable consumers; the larger census is historical. `check` certifies only
    declared rows, never every possible consumer or a runtime-selected URL.
    Admit new authorized, loadable pins to the registry; keep fossils in the
    dated census. Reconcile pin provenance and endpoint health separately.
11. **Trusting a "raw"/`inherited` row without reading the file.** Observed
    symptom: `opencode-distiller` reports `file_match=inherited`,
    `resolver_kind=raw` — the registry's `declared` value is echoed, and only the
    endpoint is verified. Fix: read the `file_match` column; `inherited` rows
    need the provider block checked by hand. (A round-1 resolver bug that read
    the `30` of `30B` as port `30` was fixed mid-round, but the class of error —
    a claim standing in for a re-derivation — remains the failure mode to watch.)

## Local gate/probe registry

Owner for every row: kama. External services and consumer files are read-only.
Pinned model expectations live in `registry/endpoint-consumers.tsv`; isolated
fixture expectations live in `tools/test-snapshot.sh`. These checks are
lane-local evidence, never native judgment or mission-completion authority.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Registered reconciliation | gate: `bash tools/kama-probe.sh check` (`--json` optional) | 0 clean; 2 failed/drift; 1 could-not-evaluate/probe error | `bash tools/test-snapshot.sh` exercises clean fixture, dead endpoint and their expected verdicts/exits; registry TSV model/pin expectations | Removed temporary work directory only |
| Consumer provenance | probe: `bash tools/kama-probe.sh consumers` | 0 listing, not a health pass; 1 probe error | Existing harness covers registry resolution through `check`/`snapshot`; no standalone consumer-list self-test claimed | Removed temporary work directory only |
| Listener census | probe: `bash tools/kama-probe.sh listeners` | 0 census, not a health pass; 1 probe error | No isolated listener-census self-test claimed | Removed temporary work directory only |
| Invocation history | gate + persistence: `bash tools/kama-probe.sh snapshot --history DIR` | 0 clean; 2 failed/drift captured; 1 could-not-evaluate/probe or persistence error | `bash tools/test-snapshot.sh`; committed fixture expectations include normalized fields, transition ids, stable rerun, malformed baseline and symlink refusal | Explicit history DIR; default `registry/history/` |

## Cited sources

- Current bounded command evidence: `.ufo/round-5/before-check.json`,
  `.ufo/round-5/host-shape.json`; acceptance evidence and measured revision are
  recorded in the round-5 report. These are samples, not a live-service promise.
- Current runnable artifacts: `tools/kama-probe.sh` (`check`, `consumers`,
  `listeners`, `snapshot`; JSON mode on all four), `tools/test-snapshot.sh`,
  and `registry/endpoint-consumers.tsv` (header defines the six-column contract).
  Registry rows: `omp-llama-cpp-default`, `ufo-fsd-thetick`,
  `ufo-fsd-local-helper`. Model expectations and URLs are unchanged by this
  documentation cutover.
- Source-root resolution: explicit `--ufo-src` > `$UFO_SRC` > first existing
  `~/Projects/ufo-fsd-alpha`, then `~/Projects/origin-work/ufo-fsd-alpha`;
  otherwise `$UFO_SRC` rows are `file=missing`. See probe `--help` and
  `PROVINCE.md` for the two surviving source-pin surfaces. This is not
  permission to edit that checkout.
- Historical host authority for the September examples: commands and outputs
  retained in `corpus/lessons/round-1.md`,
  `corpus/lessons/round-1-citations.md`,
  `corpus/knowledge/listener-census.md`, and
  `corpus/knowledge/consumer-registry.md`. Deleted janitor/OpenCode provider,
  systemd unit and backup paths are historical citations only; do not run
  obsolete commands as if those files were current.
- Identity and normalization: `corpus/knowledge/served-model-identity.md`,
  `corpus/knowledge/endpoint-identity.md`,
  `corpus/lessons/probe-mutation-matrix.md`. Their real-runtime evidence is
  llama.cpp-specific and dated; vLLM/Ollama-shaped parser fixtures do not
  establish integration with those runtimes.
- Invocation history and teardown: `corpus/knowledge/snapshot-history.md`,
  `registry/history/DELTA.md`, `corpus/lessons/round-2.md`,
  `corpus/lessons/round-4-recensus.md`, and `corpus/lessons/round-5.md`.
- Historical cross-lane mint evidence: `MINT.md`,
  `corpus/knowledge/cross-lane-scope.md`, fleet
  `../.ufo/reports/round-3/kagi.md` and
  `../.ufo/reports/round-4/kengaku.md`. Fleet sources are read-only; route
  availability is not inferred from this lane's dated alias census.
- Where to learn more: `corpus/SOURCES.md` — tiered, revision-anchored engine docs
  (llama.cpp, vLLM, SGLang, Ollama, GGUF, Prometheus/OTel) with study paths; documentation, never a local-runtime sample.

## Round-11 calibration and identity limits (2026-10-20)

The current lane assignment is the kama row in fleet `shokunin.conf`, as
directed by MISSION's Fleet shape section: operability + calibration. The
historical roster example and earlier freshness plans are historical authority,
not a present assignment (`corpus/lessons/round-11.md`).

Legacy corpus supplements add `source:`, `verified-at:` and `recheck:` without
rewriting dated observations. A metadata review improves the explicit limits of
the record; it does not refresh endpoint observations. New knowledge still
opens with the trio. Admission remains `corpus/QUALITY.md` KQ11–KQ13.

| Question | Evidence to distinguish | Limit |
|---|---|---|
| Does a listed model name prove loaded weights or readiness? | Engine-specific inventory, loading and residency fields | No: llama.cpp may list an id during loading; Ollama tags may be remote, and `/api/ps` expires. |
| Can alias equality prove artifact equality? | Documented aliases versus any native digest fields | No cross-engine identity equivalence; a tags/ps digest join remains inference, not a documented mapping. |
| Is an old `MODEL_OK` sample current authority? | Sample time and original runtime, separately from metadata-review date | No current inference-readiness or local-residency claim follows. |

Sources: `corpus/knowledge/served-identity-crosswalk.md` (S001, S010–S012,
S016, S031); `corpus/lessons/round-11.md` §Gate. This changes interpretation
guidance, not probe behavior, runtime authorization or endpoint expectations.

### Round-11 local evidence registry (owner: kama)

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Legacy provenance integrity | gate: `python3 .ufo/waves/round-11/measure.py provenance` | 0 clean; 1 failed; 2 could-not-evaluate | `python3 .ufo/waves/round-11/measure.py --selftest`; `.ufo/waves/round-11/legacy-baseline.json`, digest pinned in the script; frozen input `.ufo/waves/round-11/frozen/before/`, expected verdict/digests in `frozen/expected.json` | Read-only; self-test creates and removes isolated temporary fixtures |
| Crosswalk metadata count | probe: `python3 .ufo/waves/round-11/measure.py crosswalk` | 0 metadata present; 1 absent/incomplete metadata; 2 could-not-evaluate; none is semantic admission | Same `--selftest`; required source IDs in script, semantic authority in the opened S-rows | Read-only; self-test temporary fixtures only |

## Round-12 correction — admission criteria pointer (D3, 2026-10-20)

The sentence "Admission remains `corpus/QUALITY.md` KQ11–KQ13" in the round-11
section above is a dated pointer to the criteria that round added; it is not a
reduced admission rule. Admission of any new entry or explicit correction is
judged against the complete applicable `corpus/QUALITY.md` criteria set —
KQ1–KQ14 plus every subsequently appended criterion (round 12 appends KQ15) —
all applicable, never a subset, with each row's recorded supersession preserved
(KQ14 governs KQ7's sufficiency). KQ11–KQ13 alone admit nothing. The dated
sentence is preserved as history and is not rewritten. This correction adds no
serving capability, probe behavior or endpoint expectation.

## Round-12 local evidence registry (owner: kama)

Additive to the earlier registry rows above; none of those rows change. This is
lane-local historical-evidence repair, not a serving capability or readiness
claim.

| Name | Kind / entry command | Verdict map (code → class) | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Exact-source snapshot fidelity (D1 corrective snapshot) | gate: `python3 .ufo/waves/round-12/fidelity.py --snapshot PATH [--manifest PATH] [--repo PATH]`; default snapshot `.ufo/waves/round-12/frozen/corpus/SOURCES.md`, default manifest `auto` → `.ufo/waves/round-12/frozen/expected.json`; immutable source constants commit `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`, path `corpus/SOURCES.md` | 0 clean; 1 failed (`source_mismatch`); 2 could-not-evaluate (`snapshot_tampered`, `snapshot_unavailable`, `manifest_invalid`, `source_unavailable`, `unpinned`, `internal_error`); any undeclared nonzero code reads could-not-evaluate | `python3 .ufo/waves/round-12/fidelity.py --selftest` (spelling `--selftest`): real child CLI over temporary snapshot/manifest fixtures and a temporary empty git repo, reading the pinned immutable blob from the live lane repo read-only (`--repo`), asserting exit code and stable finding ID for clean, coherent snapshot+manifest mutation, snapshot tamper, unavailable source, unpinned match and mismatch, manifest anchor redirect, absent manifest, missing snapshot and symlink refusal | `.ufo/waves/round-12/frozen/expected.json` pins snapshot SHA-256 and path, source revision, path, blob OID and content SHA-256, and expected clean verdict; default snapshot `.ufo/waves/round-12/frozen/corpus/SOURCES.md` captured byte-exactly via `git show`, never tool-rendered text | Read-only over the lane repo and git history; no endpoint or live-service access; ordinary runs write nothing; `--selftest` writes and removes isolated temporary trees only | kama |

Notes: the default invocation checks the default snapshot against the committed
manifest. An overridden snapshot supplied without `--manifest` is unpinned: a
byte mismatch is still `source_mismatch` (exit 1), but a matching unpinned
snapshot is `unpinned` (exit 2, could-not-evaluate), never clean; the committed
default manifest is the pinned form. The gate verifies the pinned digest before
comparing a verdict, so an edited snapshot is could-not-evaluate
(`snapshot_tampered`), not a compared source verdict. Source correspondence is
reported separately from digest integrity: snapshot bytes are compared with the
immutable git blob at the code-constant revision and path, and a manifest
cannot redirect that anchor, so a coherent snapshot+manifest edit still reports
`source_mismatch`. The frozen expected file pins a fixed immutable source
revision and does not track mutable `HEAD`.

## Round-13 criterion precision and local evidence registry (owner: kama)

KQ16 in `corpus/QUALITY.md` corrects two inaccurate KQ15 formulations,
without reducing any other applicable criterion. Distinct stable finding IDs
do not require distinct numeric exits. The round-12 mapping 1/2/2 applies to
the selected primary finding; a higher-ranked integrity failure can coexist
with source mismatch. Capture via `git show` is author-recorded provenance;
the comparator's implemented operation is `git cat-file blob`. Separate
command paths still share the same repository object store.

The historical `fidelity.py:55–56` comment overstates precedence: `unpinned`
is below `source_mismatch` in the actual `PRIORITY`. Treat the comment as
inaccurate, not as an instruction to alter valid code or reinterpret receipts.
The existing registry's primary-finding exit map remains valid. Round-12
quality attribution belongs to its D4 crosswalk interpretation, not to
fidelity-gate machinery alone (`corpus/lessons/round-13.md`).

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Two-proposition criterion textual conformance | gate: `python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md`; frozen input uses explicit `--quality PATH --manifest PATH` | 0 clean textual assertions (`clean`); 1 failed (`documentation_mismatch`); 2 could-not-evaluate (`snapshot_tampered`, the round-13 QUALITY snapshot pin); 3 could-not-evaluate (`probe_error`, unavailable/invalid input); undeclared nonzero codes could-not-evaluate; none is semantic admission or endpoint readiness | `python3 .ufo/waves/round-13/measure.py --selftest` invokes the actual CLI over isolated fixtures and checks literal exits/finding IDs | `.ufo/waves/round-13/frozen/expected.json` pins frozen input SHA-256 values and expected verdicts; immutable before revision recorded in script and claims.json | Normal invocation read-only; self-test creates and removes isolated temporary fixtures only | kama |

This gate checks two explicit formulations in the effective KQ16 row, not
arbitrary natural-language correctness. Static source/code and committed
receipt review establish the substantive correction separately; a matching
pin or green self-test cannot replace that review. No new serving capability,
runtime integration, endpoint sample or domain expansion is asserted.

## Round-14 offline Ollama evidence replay (owner: kama)

Use `python3 tools/kama-ollama-evidence.py --tags PATH --ps PATH --expect EXACT_NAME`
only for caller-authorized exported JSON metadata. This tool acquires no evidence
and contacts no endpoint. Workflow and source/inference boundaries:
`corpus/knowledge/ollama-evidence-replay.md` (S012/S031); full precedence:
`.ufo/waves/round-14/rulings.json`.

| Finding | Exit | Meaning limited to supplied captures |
|---|---:|---|
| `loaded_same_digest` | 0 | One exact selected name is listed in each capture with equal nonempty digest; not runtime readiness |
| `available_not_loaded` | 1 | Selected local tag is absent under that exact name from the supplied ps capture; another alias may list the same digest |
| `remote_inventory` | 1 | A selected entry carries a nonempty remote marker; ps-side recognition is conservative inference |
| `identity_conflict` | 1 | Selected name/model conflict or selected digests differ; timing and source are unknown |
| `unknown` | 2 | Insufficient selected identity/digest evidence; never a successful correspondence |
| `invalid_input` | 2 | Missing/unreadable or malformed input, bad field types, duplicate JSON keys or selected entries |

`readiness` is always `unknown`; `scope` is always
`offline-captures-not-runtime`. Names and digests compare exactly, without GGUF,
basename, case, whitespace, implicit tag or prefix normalization. The strict
join is the lane's inference policy, not a vendor contract. Nothing proves that
the inputs came from one host, one daemon, simultaneous captures, or Ollama at
all. No current liveness, local-weight residency, installed runtime, generation
success or permission to route follows. Timestamps are not assessed.

Do not transfer exit meanings across tools: existing `kama-probe.sh check`
uses 0 reconciled / 1 tool error / 2 drift; replay uses 0 metadata match /
1 nonmatching-or-remote evidence / 2 could-not-evaluate. Inspect JSON finding
and scope, never use exit 0 alone as a routing or readiness gate.

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Offline Ollama capture reconciliation | gate: `python3 tools/kama-ollama-evidence.py --tags PATH --ps PATH --expect EXACT_NAME` | 0 clean captured metadata correspondence; 1 failed captured policy; 2 could-not-evaluate; finding IDs above distinguish results; plaintext `--help` exit 0 is help, not classification | `python3 tools/kama-ollama-evidence.py --selftest`; actual isolated child CLI cases assert literal exits and stable IDs plus readiness/scope; outer 0 `clean`, 1 `selftest_failed` | `tests/ollama-evidence/cases.json` literal expected exits/findings; fixed offline inputs, no mutable fleet artifact | Classification writes stdout only; selftest writes removed temporary fixtures only | kama |

The measurement runner `.ufo/waves/round-14/measure.py` reports fixed-corpus
behavior, not serving state or arbitrary-input correctness. Selftest green is
capability evidence; a separately recorded run against a named committed
revision is the round measurement. No live gate is executed by non-author
closure; that reviewer inspects committed evidence.

## Round-15 measurement corpus admission — corrected executable guard

The round-14 measurement runner's duplicate-name rejection promise was false
for corpora with at least sixteen distinct stripped names plus a duplicate.
Outside `corpus/lessons/round-14-verifier-spotcheck.md` R1 found that defect;
`corpus/lessons/round-15.md` preserves the named historical correction and
red-before obligation. The original unique corpus and historical receipt
remain unchanged. This repair does not change the domain classifier.

Corpus identity is the existing runner's `name.strip()` convention, not
Ollama model-name normalization. Case distinctions remain distinct; this
guard does not add Unicode normalization or a new schema-admission policy.
The preflight rejects duplicate declared names before the tool is invoked.
Minimum cardinality and uniqueness are separate obligations.

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Ollama measurement corpus duplicate guard | gate: `python3 tests/ollama-corpus-guard/check.py` exercises `.ufo/waves/round-14/measure.py` | 0 clean test contract, 1 failed test contract (`test_failed`); neither means serving readiness | `python3 tests/ollama-corpus-guard/check.py --selftest`; same literal matrix through actual runner child CLI and actual classifier with temporary invocation marker | `tests/ollama-corpus-guard/*.json` literal duplicate/positive expectations; original classifier cases remain at `tests/ollama-evidence/cases.json` | stdout plus removed isolated temporary fixture/wrapper/marker files; no network or live surface write | kama |

This registered command is a regression gate for the historical measurement
artifact, not a replacement for the domain classifier or a promoted serving
command. It earns no operability, coverage or repertoire-growth credit.

Use `--runner .ufo/waves/round-15/frozen/measure-before.py` with the same
contract to expose the old duplicate-admission defect. A green guard check
certifies only this finite measurement contract, not arbitrary-input
correctness, source authenticity or runtime health. S012's loaded-memory
documentation remains a limit, never readiness evidence.

## Round-16 verdict vocabulary and live llama.cpp lifecycle (owner: kama)

The six-verdict list at lines 11-14 is superseded, not edited: the vocabulary now
has a seventh verdict, `MODEL_LOADING`. `tools/kama-probe.sh` `VOCAB` is the
authority; its `--help` text and the `diff_baseline` whitelist repeat the same
seven words by hand. Decision-table addition (applies before rows 129/131):

| Situation | Verdict | Action |
|---|---|---|
| `GET /v1/models` → 503 whose JSON `error` has `message` exactly `Loading model`, `type` exactly `unavailable_error`, integer `code` 503 | `MODEL_LOADING` / `llamacpp-loading`, drift, exit 2 | Not ready. Re-probe later; do not repoint consumers and do not call it foreign. It does not prove the runtime or the model. |
| Any other 503 (`no slot available`, `Stream owner model is loading, retry later`, text, HTML, empty, `code` as string/float/bool) | unchanged (`FOREIGN_SERVICE`) | Read the body; this verdict makes no loading claim. |

Error signature (llama.cpp b11755 single-model, every non-frontend path while
loading, before the API-key check): `503`
`{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`.
The README prints the keys as `code, message, type`; match parsed fields, never
bytes. The probe needs python3 for this verdict; without it the old
`FOREIGN_SERVICE` reading returns. `check` and `snapshot` exit 2 on it;
`listeners` and `consumers` report it without gating. The router's own
`/v1/models` never answers with the body; a sleeping server answers
`/v1/models` 200 from cache. Details and sources:
`corpus/knowledge/llamacpp-loading-lifecycle.md`; criterion: `corpus/QUALITY.md`
KQ19.

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Probe verdict stub matrix | gate: `python3 tests/probe-verdicts/check.py [--probe PATH] [--json]` | 0 all rows pass, 1 a row failed, 2 harness/schema error; grades verdict, reason, exit and drift | `--selftest`: full matrix plus 4 malformed tests rejected | `tests/probe-verdicts/*.json` literal expectations (72 rows, 9 families, 17 `MODEL_LOADING`) | stdout only; loopback stub servers on ephemeral ports, closed after each row | kama |
| C1 counting command | measurement: `python3 .ufo/waves/round-16/measure.py` | 0 the frozen arm fails exactly the `MODEL_LOADING` rows, the current probe passes all, matrix set digest and counts (72 rows, 17 loading) match the pins and the gate exits are 1/0; 1 not; 3 frozen manifest unreadable or malformed; 4 frozen snapshot does not match its manifest or the git blob | none (runs the gate twice) | frozen probe sha256 `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` = blob of `20e392e:tools/kama-probe.sh`; matrix set sha256 pinned in the script | `.ufo/waves/round-16/run-*.json` | kama |
| Live llama.cpp lifecycle | capability: `python3 tools/kama-llamacpp-live.py --server ~/.local/opt/llama-b11755/llama-server --model ~/.cache/kama-shokunin/models/stories260K.gguf --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --alias kama-stories260k --out PATH` | 0 all 10 checks pass, 1 a check failed, 2 setup error (port refused or not owned, child exited, unreadable registry), 3 model digest mismatch before launch | receipt gate below | asset sha256 `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226` (S038); model sha256 as in the command (S039); refused ports 8080, 34113, every registry port and every listening port | the receipt path; a temporary server log, deleted; one child process on 127.0.0.1, torn down | kama |
| Live receipt gate | gate: `python3 tests/llamacpp-live/check-receipt.py RECEIPT --expect-model-sha256 H --expect-server-sha256 H --expect-probe-sha256 H [--expect-tool-sha256 H]` — pass the pins; without `--expect-server-sha256` a receipt from another build can validate | 0 valid, 1 invalid (every problem listed), 2 unreadable | `--selftest`: single-field mutations rejected (count printed) | 10 check ids; checks re-derived from stored captures and probe output | stdout only | kama |

The live run is a lane-owned fixture on an unregistered loopback port. It is
not service restoration, says nothing about the registered consumers (still
`DEAD`), and grades no model quality. It starts no unit and writes nothing under
`~/.config`, `~/.omp` or systemd. Use the binary's absolute path: a later
`/usr/bin/llama-server` must not be confused with the pinned build.
`~/.local/bin/llama-server` now precedes `/usr/bin` on this host's PATH for every
user; always pass `--server` with the absolute path. The fixture model is a
1.2 MB, 292,800-parameter F32 CI file and the expected id is the harness's own
`--alias`, so a passing receipt says nothing about weights, quality or timing
of any real deployment.

Line 361's "llama.cpp may list an id during loading" does not hold for a direct
single-model llama-server at b11755 (or at the round-10 pin c0fd7862): while
loading it answers `/v1/models` with the 503 envelope, and the round-16 live
receipt captured exactly that body. The row's answer ("No") still stands for
router catalogs, sleeping servers and Ollama.

Round-17 correction (routed by `corpus/lessons/round-16-verifier-spotcheck.md` defect 4). Correction to line 519 (2026-10-20, source accessed 2026-10-20). "Every non-frontend path ... before the API-key check" excludes `OPTIONS` requests, which the pre-routing handler answers at `server-http.cpp:347-352` before the state gate (`:354`). Exempt set is the frontend set only (`:309-311`); `/health` is gated. Type and code are at `:319-320` alongside the message at `:318`. The match rule in this section is unchanged.

## Round-17 gate grading and fail-capable live checks (owner: kama)

Supersedes, without editing, three statements of §Round-16: the stub-matrix row's
"grades verdict, reason, exit and drift" now has a failing detector behind each
field and also grades `served_model` and the `GET /v1/models` route; its "2
harness/schema error" now also covers no traceback on malformed probe output (a
malformed or non-UTF-8 probe stdout is a recorded row failure, exit 1); the live
row's "0 all 10 checks pass" and the gate row's "10 check ids" describe receipt
v1, while the tool now emits `kama-llamacpp-live/v2` with 11 checks. The round-13
row at line 430 gains exit 4. Criteria: `corpus/QUALITY.md` KQ20–KQ22.

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Probe verdict stub matrix (graded fields) | gate: `python3 tests/probe-verdicts/check.py [--probe PATH] [--json]` | 0 all rows pass, 1 a row failed (including malformed or non-UTF-8 probe output, recorded per row), 2 harness/schema error; a row passes only when verdict, reason, exit, drift, `served_model` (derived from the row's own `/v1/models` body exactly as the probe's `served_ids()` precedence, `-` for every non-model verdict) and route (`GET /v1/models` among the stub's requests; closed-port rows exempt) all hold | `--selftest`: full matrix plus 5 rejected schema cases (4 malformed + duplicate name, in a temporary directory) | matrix files unchanged: 9 files, set sha256 `bf9068d8…1f32`, 72 rows | stdout only; loopback stubs | kama |
| C1 fault controls | gate on a gate: `python3 tests/probe-verdicts/fault-controls.py [--check PATH] [--json]` | F0 identity control must pass (else exit 2); F1 reason, F2 exit, F3 drift, F4 verdict case, F5 served_model, F6 route skip (per-row cached output, no `/v1/models` contact), F7 hang, F8 malformed and non-UTF-8 stdout: detected only when check.py exits 1 with parseable JSON and every faulted row fails on the targeted field; 0 none accepted, 1 any accepted, 2 own fault | `--list`; asserts matrix digest and 72 tests in its scratch copy | the nine matrix files, copied, never written | `/tmp` scratch only | kama |
| C1 mutant grid | measurement: `python3 .ufo/waves/round-17/c1/mutants.py --grid --out PATH` | 0 completed (counts in JSON), 2 own fault/refusal; mutants M0 ignore-verdict, M1 ignore-reason, M2 ignore-exit, M3 ignore-drift, M4 casefold-verdict, M5 timeout-pass, M6 ignore-served_model, M7 ignore-route, M8 malformed-passes, M9 reject-all; `site_missing` is not applicable | `--selftest`, `--dry-run` | content-anchored sites; matrix digest `bf9068d8…` and 72 tests refused otherwise | `/tmp` scratch; `--out` refused inside `tests/probe-verdicts/` | kama |
| Live llama.cpp lifecycle v2 | capability: `python3 tools/kama-llamacpp-live.py --model ~/.cache/kama-shokunin/models/stories260K.gguf --model-sha256 270cba1b…d256d --out PATH` | 0 all 11 checks pass, 1 a check failed, 2 setup error or internal fault (receipt still written, `internal:<ExcType>`), 3 model digest mismatch; checks `health_ready` (200 and body exactly `{"status":"ok"}`), `teardown_graceful` (fresh poll shows the child alive, harness SIGTERM delivered, no SIGKILL, returncode 0, child ownership), `teardown_port_closed` (child ownership proven and port refused), `loading_envelope_graded` (503s observed and every stored body exact; none observed fails), `model_unchanged` (input integrity only), plus the six v1 subject checks | none; controls below | sources bound in-receipt (`source_binding`: llama.cpp 704366d76 spans, S036, S042, S043) | receipt path; temp log removed | kama |
| Live receipt gate v1+v2 | gate: `python3 tests/llamacpp-live/check-receipt.py RECEIPT --expect-model-sha256 H --expect-server-sha256 H --expect-probe-sha256 H --expect-tool-sha256 H` | 0 valid, 1 invalid, 2 unreadable; v1 receipts validate exactly as in round 16; v2 re-derives every check from stored evidence, including every stored loading body | `--selftest`: 26 v1 + 13 v2 mutations rejected, 2 valid receipts accepted | — | stdout | kama |
| C2 live controls | measurement: `python3 tests/llamacpp-live/controls.py --tool ABS_PATH --gate ABS_PATH [--json]` (absolute paths) | K0 good fake must be accepted; K1 degraded health, K2 bad loading body, K3 self-exit, K4 ignores SIGTERM, K5 rc 1 on SIGTERM, K6 teardown fault, K7 hang, K8 default SIGTERM (-15) must be rejected with the targeted check failing; gate-flip arm re-submits each bad receipt with its failing checks flipped to passed; 0 accepted_bad 0 and good_ok, 1 otherwise, 2 own fault | — | stages tool + registry copies per control, so frozen copies run unchanged | `/tmp`; fake process groups killed by pidfile | kama |
| SOURCES append-only guard | gate: `python3 tools/sources-append-only.py --from A --to B [--json]` | 0 no violation, 1 removed row or a changed cell outside `status`/`recheck`/`used-by`, 2 unreadable/parse; run over every consecutive commit pair of the round (KQ22) | `--selftest` 14 cases | must flag S041 on `--from b8e485c --to ccc4bb3` | read-only `git show` | kama |
| Round-13 live gate exit 4 | gate: `python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md` | adds 4 could-not-evaluate (`worktree_not_at_measured_revision`) when every check is clean but the worktree QUALITY.md differs from the measured revision; content failures stay 1 | `--selftest` 13 cases (3 new, sandbox git repo) | frozen `expected.json` unchanged | stdout | kama |

Order of operations under jj: commit through the lane helper first, then run the
round-13 live gate. Wave artifacts `.ufo/waves/round-17/count-verdicts.py` (strict
first-line `VERDICT:` counter) and `.ufo/waves/round-17/dispatch-provenance.py`
(policy identity, one `taskCall` canonicalization, spawned count from async task
results) are process tools, not axis evidence.

Round-17 falsify corrections to the table above (appended; `corpus/lessons/round-17.md`
§Falsify wave): C1 fault controls — the self-test is `--selftest` (checks the source
matrix: 9 files, 72 rows, digest), not `--list`, which only prints the fault table;
the full run stages and verifies the scratch copy. Live lifecycle v2 — pass
`--server /home/vgpnk/.local/opt/llama-b11755/llama-server` explicitly (without it
`shutil.which` picks whatever `llama-server` is first on PATH); the in-receipt
`source_binding` names S036 for the loading span only, the `/health` and teardown
spans carry `row: null` (their rows are S042 and S043/S047); exit 1 can also come from
a model rehash `OSError`, and a `BaseException` (e.g. KeyboardInterrupt) can escape
without a receipt. C2 controls — exit 0 requires `accepted_bad`, `gate_flip_bad` and
`inconclusive` all 0 and `good_ok`; K7 (hang) has no targeted check, its rejection
is a setup error; the gate-flip arm does not isolate re-derivation for K3, K6 and K7,
whose receipts carry `setup_error`. Round-13 row at line 430: exit 4
(`worktree_not_at_measured_revision`, could-not-evaluate) is now a declared code, so
that row's "undeclared nonzero codes" clause no longer covers it.

## Round-18 v3 receipt and detector-bound claims (owner: kama)

The round-17 v2 rows remain historical. Current lifecycle output is
`kama-llamacpp-live/v3`. Zero loading observations no longer fail a healthy run;
they remain non-accepted as NOT-EVALUATED. This does not certify consumer health.

| Surface | Command / exit contract | Boundary |
|---|---|---|
| Live v3 tool | `python3 tools/kama-llamacpp-live.py --server /home/vgpnk/.local/opt/llama-b11755/llama-server --model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --out /tmp/kama-live.json`; 0 outcome pass, 1 evaluated failure, 2 not-evaluated or setup-error (including digest refusal/internal fault) | Only loading-envelope grading may be null, with `evaluated:false` and reason `no-loading-503-observed`. Failure dominates null. Use `outcome`, not exit!=0 alone. Help/usage and an unwritable output cannot promise a receipt file. |
| Receipt gate | `python3 tests/llamacpp-live/check-receipt.py /tmp/kama-live.json --require-schema v3 --expect-model-sha256 HEX --expect-server-sha256 HEX --expect-probe-sha256 HEX --expect-tool-sha256 HEX`; 0 VALID, 1 INVALID, 2 unreadable, 3 NOT-EVALUATED | Require v3 for a current run; explicit schema floor prevents self-declared v1 escaping v3 checks. Intentional historical v1/v2 checking omits/lowers the floor. Pins identify bytes; the receipt is still self-reported, not authenticated execution. |
| Ownership parser | `python3 tools/kama-llamacpp-live.py --selftest` | S048/S050-backed tcp6 decoding recognises exact ::1 and mapped 127/8, never wildcard addresses; checks literal procfs rows and real loopback sockets. Linux mechanism only. |
| Input registry guard | `python3 tools/sources-append-only.py --selftest`; `--from REV --to REV` | 42 selftest cases including immutable opened/kind/tier/scope and post-blank rows; exits 0 clean, 1 violation, 2 unreadable/parse/internal fault. KQ22 still requires every consecutive source-changing commit pair, not base-to-tip only. |
| Probe-verdict checker | `python3 tests/probe-verdicts/check.py --selftest --probe /absolute/path/to/tools/kama-probe.sh` | Nested/huge-number JSON errors become row failures; timeout kills the probe's session process group. Deliberately detached children are outside that process-group boundary. Matrix bytes remain the round-16 nine-file/72-row set. |
| Wave provenance | `python3 .ufo/waves/round-18/dispatch-provenance.py --selftest` | 30 self-checks include textual job-limit refusals. On the round-17 input: frozen refused 0 → corrected 82, spawned 0; exact message format is a limitation, not arbitrary refusal detection. |

S054 grounds exact launch argv equality: duplicate flag warnings are not refusals.
The model's raw `arg` and resolved `path` are distinct; relative model arguments
are legitimate when consistently recorded. A models ready capture must be HTTP
200 as well as carry the expected alias/owner. S051 grounds containing internal
BaseException faults (not suppressing a failed check). Python returncode citations
now target `/3.14/`; the `/3/` page is not the host-version authority.

KQ23 checks state resets and trigger-to-outcome reasoning; KQ24 keeps absent
observations separate. Neither source opening nor a killed finite mutant set
establishes universal detector adequacy. `corpus/lessons/round-18.md` binds the
named survivor universe and residual limitations to measured evidence.

Round-18 explicit row supersessions: line 576's append-only “14 cases” is replaced
by the round-18 **42/42** selftest, and line 574's gate tally is replaced by
**5 VALID + 1 NOT-EVALUATED positive receipts; 61 mutations plus unreadable
rejected** (`runs/gate-selftest.stdout`). These are dated measured tallies, not
forever-fixed expectations. The round-17 mutants dry-run requires
`--check /absolute/path/to/check.py --dry-run`, not bare `--dry-run`.

S056 qualifies S054: port/host replace, api-key/spec-type append, spec-type does
not emit the duplicate warning. This does not weaken exact argv equality.
Four-pin VALID externally pins the launcher only; implementation-library/tree
digests are recorded/self-consistent, not an independent expected implementation
pin (`falsify/advice/ConnectTsukuroi.md`). Exact argv is not secret scanning or
effective-config attestation. Host-repair and credential mechanisms stay outside.

## Round-20 instrument registry and evidence boundaries (owner: kama)

This section registers round-19 instruments that previously lacked rows at
their required home. It supersedes older commands/tallies only where stated;
historical table rows stay intact. The sixth receipt pin binds the observed
regular-file install tree, not soname-symlink destinations or authenticated
execution. S057 explains loader resolution; TreeCap remains a named limit.

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Citation provenance | gate: `python3 tools/citation-provenance.py [--json]` (official run omits `--docs`) | 0 clean (all required tokens, bytes and ancestry); 1 failed (missing/mismatch/off-ref); 2 could-not-evaluate (unusable registry/docs/git) | `--selftest`, isolated temporary Git repository; count printed, observed-digest branch and CLI error cases included in round20 | `registry/required-citations.json` fixes document, revision, path and SHA256 per required token | stdout; selftest temporary repo removed | kama |
| Install-tree consistent-swap grid | gate on a gate: `python3 tests/llamacpp-live/install-tree-grid.py --gate tests/llamacpp-live/check-receipt.py --receipt PATH --model-sha H --server-sha H --impl-sha H --probe-sha H --tool-sha H [--tree-sha H] [--json]` | 0 clean (valid baseline and every selected member rejected with emitted INVALID); 1 failed (accepted or absent member); 2 could-not-evaluate (invalid baseline or child error) | `--selftest`, synthetic receipts and fake gates, including actual-verdict and crash/abort controls | default member names in script; receipt's independently supplied five pins and optional tree digest | stdout; temporary mutant receipt tree removed | kama |
| Live receipt gate with six pins | gate: `python3 tests/llamacpp-live/check-receipt.py RECEIPT --require-schema v3 --expect-model-sha256 H --expect-server-sha256 H --expect-server-impl-sha256 H --expect-install-tree-sha256 H --expect-probe-sha256 H --expect-tool-sha256 H` | 0 VALID/clean; 1 INVALID/failed; 2 unreadable/could-not-evaluate; 3 NOT-EVALUATED/could-not-evaluate | `--selftest`; 77 rejected mutations at round-start `37bd4c5` (not 76 at that revision); measured tallies are dated, not perpetual | supplied model, launcher, implementation, tree, probe and tool digests; stored capture/check consistency | stdout only | kama |
| Named error-versus-kill regression measure | gate on instruments: `python3 tools/error-verdict-census.py --json` | 0 clean (all pinned cells and controls match current expectations); 1 failed (misclassification); 2 could-not-evaluate (unrun/tampered/missing input) | `--selftest`; real-verdict positives prohibit always-error green | `registry/error-injection-cells.json`, base instrument revision and fixture digests; finite named regression set, not all lane errors | stdout and removed temporary fixtures | kama |
| Survivor-counter completion boundary | gate on named detectors: `python3 .ufo/waves/round-18/c2/survivors.py --json` | 0 no named after-survivor debt and no inconclusive result; 1 named survivor debt remains; 2 could-not-evaluate (own fault, incomplete selftest, witness mismatch) | `--selftest`; round20 arm fixtures also isolate early abort versus complete target failure; full counter is expensive and not run in round20 | round18 frozen/SHA256SUMS; SELFTEST_TARGETS and completion counts in script; measured old outputs remain revision-qualified | removed temporary clones/fixture processes; stdout or exclusive `--out` | kama |
| GGUF declared-header identity | probe: `python3 tools/gguf-identity.py FILE --json` | 0 decoded metadata (not loader validation); 1 not GGUF/bad magic; 2 could-not-evaluate (malformed/unsupported/budget); 3 could-not-evaluate (unreadable/nonregular file) | `--selftest`, parser plus captured-receipt fixtures, counts printed | format constants/limits in script; independent `tests/gguf-identity/expected.json` and fixture SHA256SUMS | stdout/stderr only; reads explicitly named regular model file, never loads tensors | kama |
| Captured GGUF declaration agreement | gate: `python3 tools/gguf-identity.py FILE --receipt RECEIPT --json` | 0 clean (byte-bound declaration agreement with captured metadata); 1 failed (identity/engine mismatch or bad magic); 2 could-not-evaluate (missing/malformed/incomplete evidence); 3 could-not-evaluate (unreadable model) | same `--selftest`, genuine agreement and digest/context mismatch controls | receipt post-model SHA; complete models body SHA; declared context versus meta.n_ctx_train, not props.n_ctx equality | stdout/stderr only; existing receipt/file read, no live server | kama |
| GGUF capability measurement | gate: `python3 .ufo/waves/round-20/c2/measure.py --json` | 0 clean (23 fixtures, independent real-file oracle and receipt agreement); 1 failed (behavior mismatch); 2 could-not-evaluate (unavailable or snapshot_tampered) | `--selftest`: pinned-input deletion/tamper controls and ordinary behavior mismatch; expected stable finding IDs in script | adjacent measure-reference.json pinned by runner SHA; every fixture, expected manifest, oracle and retained receipt-output digest verified before comparison | stdout; optional explicit `--transcript`; isolated selftest copies removed | kama |

### Offline GGUF declared identity

Read a local regular model file without loading weights or contacting a server.
Compare its byte hash and declared context metadata with an already captured
receipt; the latter remains historical self-report. `/props` per-slot `n_ctx`
is not training context and must not be computed as `ctx / total_slots`
unconditionally (S060); the round-25 entry `corpus/knowledge/context-capacity.md`
holds the rule and its observed cells. Never interpret a CI fixture's header as model quality.

The capability command and measured controls are recorded in the round-20
capabilities appendix of SCORECARD; source mechanisms and limits are in
`corpus/knowledge/gguf-declared-identity.md`. Existing consumer routes,
registered endpoints, model downloads and persistent servers remain operator-owned.

### Round-25 decision rows: declared versus served context capacity

Grounded in `corpus/knowledge/context-capacity.md` (S106-S113, S060) and the
receipt `.ufo/waves/round-25/final/context-capacity-receipt.json`. Scope:
build 11755 (704366d76), fixture `stories260K.gguf` sha256 `270cba1b…256d`,
training context 2048, no sliding-window or rope-scaling keys, fit never
lowers a context on this fixture. Other builds and large models: re-observe.

| Symptom | First check | Verdict | Action |
|---|---|---|---|
| A consumer needs the served context; `/props` reports `n_ctx` | `/props` `default_generation_settings.n_ctx` and `total_slots`, `/slots` `n_ctx`, `/v1/models` `meta.n_ctx` (and `meta.n_ctx_train` for the training context, a separate value) | `n_ctx` is the per-slot ceiling, not the KV pool; the three endpoints read one function, so agreement is not independent evidence (S060; cells K1-K8) | Report it as a single-request ceiling. Never derive the pool from it. |
| No `-c` (or `-c 0`), no `--kv-unified-per-slot`, `-np` given, split cache | The verbose startup log (`llama_context: n_ctx = N`, last line) | With `--fit` on (default) fit raises the context to training context × slots and each slot gets the full training context (S106; X1: 8192 pool, 2048 per slot; `-c 0` not run). With `--fit off` (X3) or `--kv-unified-per-slot` (K7) the round-20 per-slot value holds | Do not use the round-20 `nctx-crosscheck.py` value for the fit-on case; it gives 512 there. |
| Several requests must run at once on one server | Is the cache unified (`kv_unified = 'true'` in the startup log) and how large is the pool | On a shared (unified) pool, concurrent requests draw on the same cells; when together they need more cells than the pool holds, every processing request fails with HTTP 500 `Context size has been exceeded.` (S109; L1: two equal 1000 + 600 token requests both failed at 1025 tokens each on a 2048 pool; L2, split 8192, and L3, sequential, both 200; falsify-wave shared pools 2048 and 3072 fail, 4096 and 8192 pass). On a split cache each request is limited to its own per-slot stream [INFERENCE, S113]. Tested only with two equal requests | On a unified cache, size concurrent use from the pool and the request sizes; on a split cache, from the per-slot value. Never use `total_slots` alone. Escalate a consumer that assumes more. |
| A claim needs the KV pool size | The startup log at `-lv 4` or `-v` | None of `/props`, `/slots` and `/v1/models` carries the pool or the layout at these flags (S112; K1 and X2 report the same capacity values with pools 2048 and 8192); `/metrics` was not read | Require the verbose log line as evidence. Launch flags count only together with the `LLAMA_ARG_*` environment and only where fit cannot lower the context. Without them the pool is unknown. |

## Round-21 instrument registry: report landing audit and install links (owner: kama)

Supersedes the round-20 "six pins" row only by adding an optional seventh pin
and a completeness flag; its historical tallies stay dated. Round-21 measured
gate selftest: **11 VALID + 1 NOT-EVALUATED, 91 mutations plus unreadable
rejected** (was 6 + 1 / 77 at round-start `7a6bc911`).

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Report landing audit | gate on fleet reports: `python3 tools/report-landing-audit.py [--rounds 10-] [--report N=DRAFT] [--errata PATH \| --no-errata] [--json]` | 0 clean (no uncorrected defect, no unmatched/invalid ledger row); 1 failed; 2 could-not-evaluate (missing/irregular report, unusable git, malformed ledger, empty round set, output failure) | `--selftest`: temporary lane+fleet repos under an inherited decoy `GIT_DIR`; splice, omissions, rebase/author-time cutoff, hex words, ledger matching/invalid corrections, exit-2 inputs | ledger `registry/report-landing-errata.tsv` read from the committed `--branch` blob; defect kinds and round-commit rule in the script | stdout only; reads lane and fleet git objects | kama |
| Live receipt gate, links pin | gate: `python3 tests/llamacpp-live/check-receipt.py RECEIPT … [--expect-install-links-sha256 H] [--require-install-links]` | as the six-pin row; additionally INVALID when install_links is malformed, its canonical-JSON digest does not recompute, a chain leaves the directory/loops/dangles, a link shadows a member, the pin differs, or the block is absent under `--require-install-links` | `--selftest` adds legacy-absent VALID, retarget VALID-unpinned/INVALID-pinned, independent canonical-digest literal and 13 link mutations | caller-supplied links digest; legacy v3 receipts without the block stay VALID unless required or pinned | stdout only | kama |
| Install-links detection grid | gate on the pin: `python3 tests/llamacpp-live/install-links-grid.py [--tree DIR] [--arm current\|frozen\|both] [--json]` | 0 every non-null cell detected, null quiet, real tree gate-clean; 1 an arm missed (the `frozen` round-start arm always does); 2 could-not-evaluate (missing tree/soname, unpinnable real tree, git/copy/internal error) | `--selftest`: synthetic soname tree reached through a symlinked path; frozen misses link/subdir cells, current catches all; error and dangling-tree cases | `NEEDED_SONAMES` (b11755 DT_NEEDED links) and `FROZEN_REV` in the script; mirrors the tree under a temporary directory | temporary mirror removed; stdout | kama |

**Checklist addition (round 21).** Before committing a round report to the
fleet repo, run `python3 tools/report-landing-audit.py --rounds 10-<N-1>
--report <N>=<draft path>`; it must exit 0, and its summary line goes into the
report under Landed changes. Generate Landed changes from
`git log --reverse --format='%H %s' <round-start>..<branch>`, never from memory.

**Decision row.** Soname symlink retargeted or a `glibc-hwcaps/` copy added →
`install_tree_sha256` unchanged; `install_links_sha256` changes or the producer
refuses (`install-tree-unpinnable`). Pin the links digest when the install must
not drift (S066, S067).

**Round-21 falsify corrections to the rows above.** The audit reads committed
fleet report bytes (`git show HEAD:`), not working-tree files; `--rounds 10-`
lists committed reports only. Citations are any ≥7-hex mention inside Landed;
tokens without both a digit and a letter (and not 40-hex) are not checked as
citations. Grid exit 1 also covers a real tree that is not gate-clean; the
producer now refuses `glibc-hwcaps`, links not resolving to members, special
files and unhashed members, and records other subdirectories in
`install_unpinned`. Gate selftest at the final commit: 12 VALID + 1
NOT-EVALUATED, 99 mutations. Pre-launch refusal check:
`python3 tests/llamacpp-live/unpinnable-e2e.py` (0 all refused, 1 a case
launched or passed, 2 could-not-evaluate).

## Round-22 install helper completeness boundary (owner: kama)

S075/S076 ground the actual operation's OSError signal, not a Python-mandated
directory identity policy. `install_tree(server_real)` now either returns its
unchanged regular-file map/digest or raises
`SetupError('install-tree-unpinnable:<stage>:…')`; it never silently skips an
I/O error. Symlink/nonregular skips remain intentional and belong to
`install_links` policy. `os.access` alone cannot establish later I/O success
(rejected remedy S077). See the bounded scan-time limits and historical
receipt caveat in `corpus/knowledge/llamacpp-loading-lifecycle.md` §Round-22.

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Install helper I/O completeness | gate: `python3 tests/llamacpp-live/install-io-grid.py --arm current --json`; use `--arm frozen` or `both` for the intentionally red before-state | 0 clean; 1 incomplete-install-identity (escaped fault or control mismatch); 2 could-not-evaluate (unavailable source/fault not reached/input error); errors never earn refusal credit | `--selftest`: CLI fixtures include complete helper, always-refuse/empty, individual refusal deletions and broad catches | `FROZEN`/`FROZEN_SHA`, fixed FAULTS/CONTROLS and independent literal-byte hashlib oracle in script; current source SHA emitted; official run pins clean branch commit | stdout and removed temporary synthetic trees only; no server or network | kama |

**Decision/checklist:** if directory enumeration, lstat or member hashing
raises OSError, stop identity comparison and report the refused stage/member;
do not compare an empty/null or survivor-only result with a stored pin.
TypeError/programming errors and interrupts are not directory-refusal evidence.
For an old receipt, retain its historical schema: this helper repair cannot
discover omitted historical members or certify the bytes that executed.

**R21 outside-routing trust restriction (learned R22).** The report-landing
audit is supported only on this trusted lane and fleet repository. Its Git
environment/system/global-config scrubbing is not repository-local config
isolation, history-integrity proof or safe arbitrary-repository execution.
UTF-8/error/top-level handling and the late selftest fallback/GIT_DIR debt
remain unclaimed until separately hardened. Never point it at an untrusted
repository under the current guarantee (KQ32; round-22 lesson D4).

Current source interpretation for the R21 rows uses correction rows
S078–S086 (superseding S066–S074). Historical source rows and prose remain
intact; S084's generated latest reference is not the installed jj version,
and the author-time audit design is own-work, not a guarantee from that page.

The Python error-signal rows S075/S076 are clarified by S087/S088:
`/3.14/` is a series URL, not a micro-release pin. The observed page-title
drift3.14.8→3.14.9 did not alter the quoted open/os error semantics.

## Round22 report/source classification correction (owner: kama)

The report-wide full-hash rule now distinguishes exact committed Registry
source-URL occurrences from lane/fleet commit citations. The first HTTPS
URL in a structurally valid S-row authorizes only its full form and the
source-census-normalized form; this is not a hash-value whitelist. No source
URL exemption applies inside Landed changes, and a bare copy of the same
foreign hash remains unresolved. Missing legacy SOURCES means no exemptions;
Git/read/type errors are could-not-evaluate. The JSON `source_url_hashes`
field names hashes whose occurrences are confined to classified URLs.

This makes verbatim source-validation output usable in a round report
without mistaking its upstream revision URLs for lane commit citations.
It does not validate upstream bytes/claims, broaden the trusted-repository
scope, or alter the Landed omission rules (KQ33).

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Registered-source report witness | gate: `python3 .ufo/waves/round-22/report-source-fix/ReportSourceFix/out/red-green-witness.py` | 0 clean/red-green-match; 1 failed/red-green-mismatch; 2 could-not-evaluate (snapshot_tampered/unavailable) | `--selftest`: CLI positive, manifest/report tamper, missing candidate, old-as-current genuine mismatch and child-error controls | code-pinned SHA of red-green-fixture.json; manifest pins old script/registry/census blobs at cc9f8d3 and exact report fixture digest | stdout; removed temporary synthetic Git repos only; actual lane/fleet read-only | kama |

The main report auditor retains its existing entry/exit contract and
`--selftest`; source URL loading is from committed `--branch` bytes, never
the worktree. D4 local-Git-config/history and UTF-8 hardening remains frontier.

The existing first canonical Landed-section interpretation is unchanged;
competing duplicate sections are not made semantically valid by this fix.

## Round23 repository-state isolation of the report auditor (owner: kama)

Appended; the R21/R22 trusted-repository restriction above still holds
(KQ32, narrowed by KQ34 to graded rows). Every git call of
`tools/report-landing-audit.py` now runs as
`git --no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8
-c log.follow=false -c log.showRoot=true -c log.showSignature=false
-c log.mailmap=false -C <repo> …` and decodes stdout strictly as UTF-8
(surrogateescape only for the lane log records and the fleet report
listing, which are matched on ASCII and never emitted). Lane log records are
NUL-delimited. A plain `--branch` name means `refs/heads/<name>`, pinned once.

Refused with exit 2 (could-not-evaluate, reason on stderr): non-UTF-8 git
output; a git call that runs longer than 20 s (a FIFO config/include/ref
blocks git); shallow repositories, an info/grafts file holding any line git
would apply (blank and `#` lines are ignored, S101), a partial clone
(`extensions.partialclone`, a `remote.*.promisor` that is true, or a
`.promisor` marker paired with its `.pack`), non-sha1 or non-top-level
repositories, for the lane and the fleet; a Landed citation that names a
ref; an unparseable log record; any unanticipated exception. A
`remote.*.partialclonefilter`-only remote is not refused: `--no-lazy-fetch`
keeps its missing objects missing (F27). Requires git ≥ 2.45 (older git
rejects `--no-lazy-fetch` → exit 2 on every run).

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Repository-state fault grid | gate: `python3 tests/report-audit/repo-state-grid.py --arm frozen\|current\|both [--json]` | 0 every graded (fault, contract, control) row met; 1 a row not met (`--arm frozen` and `both` are 1 by design); 2 fixture premise failed or harness error | premise per builder; exit-2 rows pin the refusal reason; 13 controls | frozen auditor `4fe9339f:tools/report-landing-audit.py`; population SHA over case table and reasons; 30 s per-case timeout that kills the auditor's whole session | temporary fixture repos only | kama |
| Isolation mutants | gate: `python3 tests/report-audit/isolation-mutants.py [--json]` | 0 pristine passed and every mutant ran (kills on grid exit 1 and survivors listed); 2 pristine failed, a pattern did not match once, or the grid could not evaluate a mutant | pristine run is the positive control | 31 single-literal mutants of the auditor | temporary copies only | kama |

Open, not claimed (both arms identical unless noted): objects borrowed
through `objects/info/alternates` or a `.git` gitfile redirect resolve as
local, and a `--shared` clone of a partial clone bypasses the promisor
refusal; peel/cross-repo prefix ambiguity can be overwritten by a later
`found`; only the first `## Landed changes` section is read; a CR inside an
errata line splits it; `--errata` naming a FIFO blocks; no memory ceiling on
git output or the SOURCES URL alternation. Declared trades (frozen 0 →
current 2 on complete repositories): a blobless partial clone (T01) and a
paired promisor pack without promisor config (F23). Never point the auditor
at an untrusted repository.

## Round24 correction — local evidence, not promisor declarations (owner: kama)

This supersedes the round23 promisor-refusal and trade sentences above.
Outside closure rounds[428] rejected round23 as harmed: refusing a correct
complete-state workflow is harm even when disclosed. T01 is a checked-out
single-blob clone whose checkout hydrates that blob; F23 is a different,
`--no-checkout` fixture whose cited blob is genuinely unavailable.

The local-object contract (`tools/report-landing-audit.py`) is metadata
neutral. Keep the existing global Git isolation options and 20-second
deadline. A complete or locally sufficient marked repository receives the
same substantive verdict as its unmarked twin; the tool neither fetches
objects nor guesses empty data on a failed required read.

| Evidence state | Outcome |
|---|---|
| All required reads succeed; citation resolves in either audited local repository | Normal clean/failed verdict and ordinary authorized errata handling |
| Locally present blob/tree fails a commit-only peel | Genuine `landed-unresolved`, not an unknown object |
| Citation is absent locally, with no unavailable referenced content hiding its identity | Ordinary unresolved finding; metadata alone does not change it; authorized errata still applies |
| Required history, source registry, report, ledger or tag-target content cannot be read | Content-derived could-not-evaluate (exit2), naming the required object/path |
| An unresolved citation matches an unavailable referenced object, or a missing tree/commit conceals its dependency names | Content-derived could-not-evaluate; never a guessed defect or an errata-rescued unknown |
| Unrelated missing blobs, branches or unused trees; every citation already resolves | No blanket completeness precondition |

Missing-object diagnosis is lazy and token-scoped. It consults present
commit/tree/tag roots, including dangling objects, only for an unresolved
token; it never narrows normal object lookup to branch reachability.
Two isolated `rev-list --missing=print` walks (the second filtering blobs)
distinguish blob holes from opaque tree/commit dependencies. Commit graphs
are disabled for these diagnostics; they are not an integrity theorem.
S102 documents the encountered-missing format, S103 packaging provenance,
and rejected S104 explains why fsck green is not local availability proof.

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Promisor local-evidence grid | gate: `python3 tests/report-audit/promisor-grid.py --arm frozen\|current\|both [--json]` | 0 selected arm observations meet their declared column; 1 mismatch/twin mismatch/object acquisition; 2 harness/premise/unavailable input. Frozen-history reproduction is not improvement: `amended_view_met` supplies the comparable target score. The original withdrawn view is reported separately. | `--selftest`; fixed cases, grade checks, isolated fixtures | adjacent `promisor-grid-expectations.json`; original44 frozen before L1 source inspection plus3 disclosed opaque-dependency cells; frozen auditor `0df800e:tools/report-landing-audit.py`; exact finding/token, raw/uncorrected distinction and twin documents | temporary fixture repositories under `/fast/scratch/hyaku/kama-r24`, removed unless `--keep`; optional explicit `--out` | kama |

Git>=2.45 remains an inherited prerequisite, not restored older-Git support
or operator approval; R23-H2 is carried in the round24 L0 question.
Trusted repositories only (KQ32/KQ34). No remote completeness or remote
abbreviation uniqueness is claimed. Gitfile/alternates identity, prefix
ambiguity overwrite, duplicate Landed sections, errata CR/FIFO handling,
memory ceilings, live serving and sibling-tool isolation remain unclaimed.

### Round24 mutation experiment registry correction

These are bounded sensitivity experiments, not a claim that every mutation
must be killed or that a completed inventory is an admission gate.
This supersedes the round23 mutation row's31-element current reading:
M14/M22/M27/M29 are explicitly retired because their metadata-classifier
component was deleted; M17 follows the current local-store spelling.
Survival alone does not establish defensive-only status.

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Promisor mutation experiment | probe: `python3 tests/report-audit/promisor-mutants.py --json` | 0 inventory evaluated (kills and survivors listed, not universal green); 2 could-not-evaluate. Pristine failure, grid errors, leaks, timeouts, uncompiled/unapplied mutants and unidentifiable failures kill nothing. | `--selftest`, isolated CLI verdict fixtures; `--anchors PATH --json` checks unique applicable/compiling mutations without executing the grid |11 named mutations: ten executable with declared target cells; PM08 is a manual review-only note, unexecuted, uncredited, with no assertion of any kind (wording corrected in round 25); original/amended expectation manifest in the grid | removed temporary auditor copies; grid-owned scratch fixtures | kama |
| Retained isolation mutation experiment | probe: `python3 tests/report-audit/isolation-mutants.py [--only NAME] [--json]` | 0 pristine passed and selected inventory evaluated, survivors reported; 2 fail-fast could-not-evaluate | pristine grid positive control; existing literal inventory and retirement output |28 retained literals since round 25 (M11 and M17 re-anchored; M33 is the second call site of the M17 refusal), 4 retired IDs without reuse; `RETIRED` explains their removed component; unchanged isolation elements remain explicit | temporary source copies and grid fixtures | kama |

### Round24 live cutover — local evidence, promisor metadata neutral (owner: kama)

This section is the live cutover of the round-24 instrument semantics and
describes the canonical files `tools/report-landing-audit.py` and
`tests/report-audit/` as they stand in the commit that carries this
text. The present tense below describes those canonical files.

**The auditor** (`tools/report-landing-audit.py`) keeps the global Git
isolation options and the 20-second deadline, and stays metadata neutral:
promisor metadata (`extensions.partialclone`, a true `remote.<n>.promisor`,
a `remote.<n>.partialclonefilter`, or a `.promisor` marker paired with its
`.pack`) never changes local-object resolution, a clean/failed verdict or
an authorized errata match. Presence is per store and bare: each store
reports the canonical object it holds for a token, and reconciliation is
per canonical object, never across colliding prefixes. A selected-ledger
lookup and invalid-row accounting ignore unselected rounds. Committed-ledger
and open-range listing read failures take required-read identities, while a
fatal timeout or OS cause spends no second diagnostic timeout. Known
unavailable referenced ids are encountered from all present local
commit/tree/tag roots, and the opaque missing-name boundary comes only from
the pinned audit root. There is no whole-store or reachable-tree
completeness precondition: all-resolved inputs stay runnable despite unused
holes, and a locally sufficient marked repository receives the same
substantive verdict as its unmarked twin. An explicitly cited missing blob
behind a dangling present tree stays could-not-evaluate; unrelated
unreachable opaque garbage plus an ordinary fabricated citation stays an
ordinary failed finding.

**The grid** (`tests/report-audit/promisor-grid.py`, with
`tests/report-audit/promisor-grid-expectations.json`) grades 47 cells
against the pinned manifest bytes `d86b7bea…`; the literal manifest byte
pin authenticates oracle identity, not production wiring correctness, and a
missing manifest is snapshot_unavailable2 while changed bytes are
snapshot_tampered2. Each arm reports its own comparable score
(`amended_view_met`, `amended_view_total`, `amended_view_unmet`,
`amended_view_measured_on`) under identical strong
exit/defect/reason/name/no-verdict/acquisition rules in both arms. The
comparable frozen baseline is the strict 14/47; the older loose 16/47 stays
filed under its own weaker-method label
(`met_amended_frozen_loose`; PG16 and PG20 differ) and is not two extra
product wins, and the frozen historical reproduction 47/47 is a separate
measurement. The original view is reported separately: `original_view_unmet`
lists every unmet original expectation, and `withdrawn_original_failures`
is the legacy name for the unmet original expectations that the amendment
superseded — the amendment-changed cells, PG28 and PG34 among them — not
the literal unknown clause alone; an unmet row whose original and amended
views agree is an ordinary live failure and is not withdrawn. The original
unknown clause stays withdrawn and not achieved.

**The grid's metadata handling and controls.** The r23 blanket refusal is
never the reason of a current-arm refusal: the frozen-history reason class
serves the r23 base's own refusals, the manifest's per-cell
`reason_forbidden` pins and `check_exit2_form` keep the metadata phrasing
forbidden for a current-arm refusal, and the dead unused
`METADATA_REFUSAL` constant is gone. The controls are behavioural and
specific: a blobless contract failure raises a typed contract-violation
clause (`initial-empty`, `still-missing`, `missing-object`), and the
stand-in controls drive real stand-in auditors through the real command
line — a legitimate content-derived refusal must meet, an internal
identity carrying the same reason and the same names must not meet, and a
traceback must not meet. These paired controls distinguish the named
identity/premise failure rather than accepting an unrelated setup error.

**Fixture and evidence rules.** Real blobless absence is asserted
immediately after the clone, before any optional hydration; a hydrated
final-empty state alone cannot prove initial partialness. Connected local
file origins stay acquisition tripwires: never remove or repoint an
origin, never make a lazy forensic read. Hydration changes the input
state; it is not a detector repair. `internal_error` is captured from the
full stderr and is distinct from a legitimate content-derived refusal;
tracebacks and internal errors are unmet observations and can never earn a
mutant kill.

**The mutation experiments** (`tests/report-audit/promisor-mutants.py`,
`tests/report-audit/isolation-mutants.py`) are bounded sensitivity probes,
not an admission gate, and a valid finite survival still completes 0. The
grid protocol carries one canonical internal-error signal: the per-row
boolean `internal_error`, true when the auditor's full stderr contains the
catch-all prefix `could-not-evaluate: internal:`; the two speculative
aliases are removed and no compatibility promise for another spelling is
kept, the stderr checks stay diagnostics on the same catch-all message,
and the per-row boolean remains authoritative because a long message can
push the prefix out of the kept tail. Runtime faults — a leak, a timeout, a
traceback, an internal error, an invalid row exit, a malformed verdict
document — and violations outside a mutant's attribution envelope are
could-not-evaluate with zero kill credit; the out-of-envelope rows are
preserved and reported, and the envelope is never widened. A credited
violation is classified from the row's own comparison fields:

| expected → actual | class | credit |
|---|---|---|
| 0 → 0, 1 → 1 | `same-verdict-exit` | the same exit; the detail may differ — no substantive exit change and no availability claim |
| 0 ↔ 1 | `verdict-change` | the verdict's pass/fail changed |
| 0/1 → 2 | `refusal-2` | an over-refusal signal, not an availability credit |
| 2 → 0/1 | `actual-verdict` | the availability credit |
| 2 → 2 | `diagnostic-only` | the refusal stayed a refusal; only the diagnostics can differ |
| missing or outside 0/1/2 | `unclassified` | no class credit is guessed |

The `diagnostic_only` aggregate means exclusively the same 2 → 2; it never
covers same normal exits and never covers unclassified rows, which are
reported under their own aggregate. No availability credit is guessed from
a `same-verdict-exit`, `diagnostic-only` or `unclassified` row. Ten
executable operators plus one manual PM08 review note: PM08 rests on
uncredited manual source inspection (not settled evidence; corrected in round 25) —
it is never constructed, never executed, never credited with a kill, and no
permanent AST, text or wiring assertion exists for it. Static anchors
authenticate mutation applicability only; finite survival is not global
equivalence; an allowed `expect_rows` is an attribution envelope, not a
promise that every row discriminates; a same-exit diagnostic sensitivity is
not an unavailable-evidence acceptance witness; the KQ35 paired obligations
need class-specific substantive evidence, and a completed probe0 is not
admission.

**Superseded registry reading.** The round23 "Isolation mutants" registry
row (kind `gate`, 31 single-literal mutants of the auditor) is superseded
in kind and in count: the current kind is a bounded sensitivity `probe`,
and `tests/report-audit/isolation-mutants.py` held 27 retained literals at round 24 (28 since the round-25 re-anchor added M33)
with 4 retired ids (M14, M22, M27, M29) that are never reused, so the
historical 31 is not the current count. An empty selection is
could-not-evaluate, decided before the source read, the pristine and any
grid call; the short-id selector hazard pre-existed the retirement, which
changed the id set and exposed the stale full ids.

No final candidate measurement, count, score or approval is claimed here.

[Provenance footnote — prototype paths only, the canonical files are the
ones named above: the round-24 proposals filed under
`.ufo/waves/round-24/fixes/` supply these semantics — core
`StoreLocalPresence/report-landing-audit-v9.py` (`b9be4f42…`), grid
`GridAttestationV7/promisor-grid.py` (`3048383…`), mutator
`MutationEvidenceV14/promisor-mutants.py` (`971c3ec…`) and
`MutationEvidenceV8/isolation-mutants.py` (`eace4f5…`), and the integration
contract `docs-contract.txt` with its mutator delivery and final-selection
supplements.]

**Interface and reproducibility cutover.** Mutation sensitivity accepts only
the current arm: frozen/both cannot execute the supplied mutant and are
could-not-evaluate before a pristine run, never an experiment silently
reported as survival. Full exact case/mutant IDs are required. The grid
honors an existing caller TMPDIR rather than a host-specific shared root;
an unusable requested root is could-not-evaluate before fixtures in normal
and selftest modes. Each arm counts unique violating case IDs across its
individual view and twin constraints. Grade explanations retain their named
view (problems, amended_problems, original_problems), and sensitivity receipts
preserve them with actual auditor/grid/population/expectation identities.
Paths alone are not a producer identity. These changes do not alter the
frozen 47, its criteria or twin links, and add no admission claim.

A sensitivity result needs at least one graded oracle cell in the pristine
and mutant runs. An open-only or empty graded sample is could-not-evaluate,
not a valid survivor; PG40 remains ungraded and no primary cell changes.

The pristine must have exit0 AND no violated graded row. A mutant result
with exit0 but a violated row is contradictory protocol, not a kill; the
receiver refuses it just as it refuses exit1 with no identifiable failure.

**Manual note versus experiment.** A manual-only inventory enumeration may
complete with executable0/evaluated0 and killfalse; that is not behavioral
success, a valid survivor, an applicability assertion or an admission gate.
PM08 stays filed/manual/unexecuted/uncredited, with no permanent AST/text/
wiring assertion. Historical static review notes and a legacy M02 result
do not establish present PM08 behavior. The graded-pristine requirement
above applies to executable sensitivity experiments, not note enumeration.

The current-only restriction belongs to the sensitivity runner. The grid
still supports frozen/current/both; do not reject a valid historical
comparison by copying the mutation runner's restriction into its contract.
Final r24 evidence is bounded, distributed and qualified in
`corpus/lessons/round-24.md`; it does not achieve the full original claim,
prove global no-effects/absence of chains, resolve H2 or grant admission.

## Round-26 live error signatures (b11755 fixture, owner: kama)

Each row is an error that llama-server build 11755 (commit 704366d76) emits in
the lane's fixture setup (loopback, one child at a time; model
`stories260K.gguf`, except E26-15 and E26-16, which use a missing path and a
non-GGUF file), with the trigger that produces it, what the code checks, and
what to do. The signature is a verbatim substring of both the observed output
and the pinned source line named by the row's SOURCES entry. Inside `http body`
signatures, `\"` is the escaped quote as it appears in the raw JSON response
body, which happens to match the C++ source bytes; the decoded
`error.message` has a plain quote. The
re-derivation command is `python3 .ufo/waves/round-26/count-c1.py --out
<receipt.json>`; it relaunches every trigger against the sha256-pinned binary
and model and prints `counted N` (frozen predicate:
`.ufo/waves/round-26/preregistration.json`). The count alone is not proof: an
echo shortcut with no error knowledge also meets this counter
(`corpus/lessons/round-26.md` §Mistakes); each row was re-run by a separate
wave-2 attack seat (`.ufo/waves/round-26/w2-falsify/advice/AttackE26*.md`).
Registry:
`registry/error-signatures-r26.json`. Other builds: re-observe before relying
on a row. Status codes and exit statuses were observed on this build only.
The counter pins the `llama-server` launcher (sha256 b6a31a8e…cd804); the
server code itself is in `libllama-server-impl.so` beside it (sha256
e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed, unchanged since earlier rounds), which the counter does not hash.
Five rows (E26-01, 02, 04, 05, 08) are one mechanism: an unset launch flag
makes a handler refuse at entry with 501. E26-12 and E26-13 share one
condition (`allow_audio` false) on two routes with two statuses.

Cited, not absorbed: API-key and authentication errors are kagi's (the lane
already holds `Invalid API Key`, SKILL.md "Historical error signatures");
served-model quality is kengaku's; OS and service-manager errors are
tsukuroi's; how an omp dispatch or alias resolves, and its error mapping, is
kumitate's (`corpus/knowledge/cross-lane-scope.md:28`): the rows below describe
this server's own endpoints and status meanings, not route resolution. Kengaku
records the serving plane as unowned (`kengaku-shokunin/PROVINCE.md:24-25`);
this section is kama's claim there under its own `PROVINCE.md`, and re-pointing
kengaku's note is kengaku's edit (wave-1 connector `.ufo/waves/round-26/w1-build/advice/ConnectorSiblingOverlap.md`).

| id | signature (channel) | trigger | meaning (code) | next action | source |
|---|---|---|---|---|---|
| E26-01 | `` This server does not support slots endpoint. Start it with `--slots` `` (http body) | `--no-slots`; `GET /slots` → 501 | `get_slots` refuses when `params.endpoint_slots` is false (`server-context.cpp:5365-5367`); `--no-slots` or `LLAMA_ARG_ENDPOINT_SLOTS=0` in the environment turns slot monitoring off (on by default) | Slot monitoring is off on this server, not a dead server. Re-launch with `--slots` only if a consumer needs `/slots`; otherwise stop polling it. `GET /props` shows `endpoint_slots`. | S114 |
| E26-02 | `` This server does not support slots action. Start it with `--slot-save-path` `` (http body) | no `--slot-save-path`; `POST /slots/0?action=save` → 501 | `post_slots` refuses every save/restore/erase action before reading it when `params.slot_save_path` is empty (`server-context.cpp:5407-5409`) | Slot persistence is not configured. Set `--slot-save-path` to an existing writable directory (a path that does not exist stops startup with `not a directory`), or stop sending slot actions. | S115 |
| E26-03 | `No available space in KV cache or invalid slot save file` (http body) | `--slot-save-path /tmp`; `POST /slots/0?action=restore` with a file that does not exist → 400 | `llama_state_seq_load_file` returned 0 bytes, so restore throws (`server-context.cpp:3078-3085`) and the handler answers 400 (`:3100-3102`); the same text covers a missing file, a file that is not a slot file and a cache too small for the saved state | The HTTP body is the same for every cause; the server log line just before the error names it (seen in wave-2 runs: `failed to open <path>: No such file or directory`, `unknown (magic, version)`, `not enough cells in kv cache`; those lines come from files not pinned this round). The file is the `--slot-save-path` directory plus `filename`. | S116 |
| E26-04 | `` This server does not support changing global properties. Start it with `--props` `` (http body) | no `--props`; `POST /props` → 501 | `post_props` refuses when `params.endpoint_props` is false (`server-context.cpp:5452-5454`); `GET /props` still answers | Changing global properties is off; reading them is not. On this build `--props` only silences the 501: `post_props` applies nothing and answers `{"success":true}` with the properties unchanged (`server-context.cpp:5456-5458`, observed in wave 2). Set the chat template at launch (`--chat-template-file`). | S117 |
| E26-05 | `` This server does not support embeddings. Start it with `--embeddings` `` (http body) | no `--embeddings`; `POST /v1/embeddings` → 501 | the embeddings handler refuses before parsing when `params.embedding` is false (`server-context.cpp:6131-6133`) | This server is a generation server. Point embedding consumers at a server launched with `--embeddings` and a pooling type (`--pooling mean` on a model that declares none; otherwise the OpenAI route returns E26-06), ideally an embedding model. | S118 |
| E26-06 | `Pooling type 'none' is not OAI compatible. Please use a different pooling type` (http body) | `--embeddings` with the fixture's default pooling; `POST /v1/embeddings` → 400 | the OpenAI-style route needs pooled output; it refuses when the server's pooling type (`--pooling`, default the model's) is `none` (`server-context.cpp:6136-6138`) | Launch with `--pooling mean` (or the model's intended pooling), or use the native `/embedding` route, which returns per-token vectors when pooling is `none`. | S119 |
| E26-07 | `\"input\" or \"content\" must be provided` (http body) | `--embeddings --pooling mean`; `POST /v1/embeddings` with neither `input` nor `content` → 400 | the handler accepts `input` (OpenAI) or `content` (native) and refuses when both are absent (`server-context.cpp:6145-6152`) | Client bug: the request body lacks the text field. Fix the client to send `input`. | S120 |
| E26-08 | `` This server does not support reranking. Start it with `--reranking` `` (http body) | no `--reranking`; `POST /v1/rerank` → 501 | rerank needs embedding mode and rank pooling; it refuses otherwise (`server-context.cpp:5802-5805`) | Reranking is gated by launch mode only: with `--reranking` (or `--embeddings --pooling rank`) even this generation fixture answers 200 with scores (wave 2). Use a trained reranker model for meaningful scores, not to clear the 501. | S121 |
| E26-09 | `Infill is not supported by this model` (http body) | fixture model; `POST /infill` → 501 | the handler checks the vocabulary for the prefix, suffix and middle fill-in-the-middle tokens and refuses when any is missing (`server-context.cpp:5462-5478`); the message lists which tokens are missing | Model capability: the guard reads the model's fill-in-the-middle token ids. Use a code model that has them, or send the task to `/completion` (prefix only; the suffix is ignored). Forcing the ids with `--override-kv` passes the guard but does not give the model the skill (observed in wave 2). | S122 |
| E26-10 | `is too large to process. increase the physical batch ` (http body) | `-c 64 --embedding`; `POST /embedding` with a 4352-token `content` → 500 | embedding inputs that cannot be split across batches (`can_split()`, which depends on the pooling type) are refused when longer than the physical batch `n_ubatch`; `ERROR_TYPE_SERVER` makes the status 500 (`server-context.cpp:3653-3660`) | Chunk the input on the client. Raising `-ub`/`-b`, as the message suggests, did not help on this fixture: the batch is clamped to the per-slot context, which is capped at the 2048-token training context (wave 2). The 500 is not a crashed server: `/health` stays 200. | S123 |
| E26-11 | `Request body must be an array` (http body) | fixture model; `POST /lora-adapters` with a JSON object body → 400 | the LoRA route refuses any JSON body that is not an array (`server-context.cpp:5996-5999`); entries are documented as `{id, scale}` but not validated (`server-common.cpp:280-291`) | Client bug: send an array; read valid ids from `GET /lora-adapters`. A 200 `{"success":true}` does not validate ids (unknown ids are ignored), and every loaded adapter left out of the list is set to scale 0 (`server-context.cpp:1837-1847`). | S124 |
| E26-12 | `The current model does not support audio input.` (http body) | fixture model; `POST /v1/audio/transcriptions` → 501 | the transcription handler refuses before parsing the body when the model has no multimodal projector or audio is not allowed (`server-context.cpp:5651-5657`); same `allow_audio` condition as E26-13, different route and status | Launch capability. Route audio to a server launched with an audio-capable `--mmproj`; `GET /props` shows `modalities.audio`. | S125 |
| E26-13 | `audio input is not supported - hint: if this is unexpected, you may need to provide the mmproj` (http body) | fixture model; `POST /v1/chat/completions` with an `input_audio` content part → 500 | chat message parsing throws `std::runtime_error` when audio is not allowed (`server-common.cpp:1270-1273`); `ex_wrapper` maps it to a server error, status 500 (`server.cpp:70-73`, `server-common.cpp:107-109`); same condition as E26-12 | A client-side capability mismatch reported as a server error. Do not treat this 500 as an outage; remove audio parts or route to an audio-capable model. | S126 |
| E26-14 | `\"prompt\" elements must be a string, a list of tokens, a JSON object containing a prompt string, or a list of mixed strings & tokens.` (http body) | fixture model; `POST /completion` with `prompt` as a JSON object without a prompt string → 400 | each prompt element must be a string, a token list, an object with a `prompt_string` key, or a mixed list; any other element throws (`server-common.cpp:1088-1115`); a list of strings is accepted | Client bug: send `prompt` as a string, a token list, or an object `{"prompt_string": ...}`. | S127 |
| E26-15 | `failed to open GGUF file` (startup log) | startup with a GGUF path that cannot be opened (here `-m` pointing at a missing file) → exit 1 | `gguf_init_from_file` cannot open the file and logs the path and the system error (`gguf.cpp:1017-1022`); model loading fails and `server.cpp:507-511` returns 1 | Fix the file named in quotes: the `-m` model, a `-md` draft or an `--mmproj` projector (all three observed), or a split shard. The system error in parentheses names the cause (`No such file or directory`: path or mount; `Permission denied`: permissions). Not a model-format problem. | S128 |
| E26-16 | `invalid magic characters: '` (startup log) | startup with a file that is not GGUF → exit 1 | the first four bytes are not `GGUF` (`gguf.cpp:476-483`); the line prints the bytes it found | The file's first four bytes are not `GGUF`: an HTML or error page saved as `.gguf`, another format, or a corrupt header. Compare its sha256 with the published one. An empty, short or truncated GGUF prints `failed to read magic` or a later loader error instead (observed in wave 2), not this line. | S129 |
| E26-17 | `GGML_ASSERT(n_outputs >= 1)` (startup log) | startup with `--ctx-size -5` → the process dies from signal 6 (SIGABRT; the counter records -6, a shell shows 134) | on this build a negative context passes argument parsing; graph reservation then asserts `n_outputs >= 1` (`llama-context.cpp:2620-2624`) and aborts with a backtrace | A supervisor sees a crash (signal 6), not a usage error. Check the launch flags for a negative or non-numeric context before suspecting the build. | S130 |

Observed but not registered this round (reasons in `corpus/lessons/round-26.md`
§Gate): four signatures the lane already held in earlier wave evidence
(`This server does not support metrics endpoint...`, `exceeds the available
context size (`, `couldn't bind HTTP server socket`, `error: invalid argument: `);
error-type labels (`authentication_error`, `invalid_request_error`); router-only
model errors that a single-model launch cannot reach; ten per-flag
argument-validation messages from `arg.cpp`; and 26 genuine, live-confirmed
request-validation messages (embeddings, rerank, prompt, control and 17
chat-completions messages) held back only by the counter's limit of 19
runnable rows. Also seen once by a wave-1 seat and not re-run by the lane: a
server launched with `--embeddings` crashed with SIGSEGV while serving a
`POST /completion` (`.ufo/waves/round-26/w1-build/out/ExecEmbeddingsInput/RUNS.txt`).
It is not registered: the crash needs a request to a healthy server, which only
the http channel sends, and that channel needs an HTTP status.

## Round-28 request-field outcomes (b11755 fixture, owner: kama)

What llama-server does with one out-of-range or transformed value of a single
request field, measured on the lane-owned fixture only: llama.cpp b11755
(commit 704366d76, `~/.local/opt/llama-b11755/llama-server`, sha256
`b6a31a8e…d804`), model `stories260K.gguf` (sha256 `270cba1b…256d`), default
argv `-m <model> --host 127.0.0.1 --port <port>` (so `n_parallel` is 4), native
`POST /completion` with body `{"prompt": "Once upon a time", "n_predict": 1}`
plus the one field shown. Fields are declared in `tools/server/server-schema.cpp`
(pinned snapshot `.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp`,
sha256 `1f9d7b73…4050`): `set_hard_limits` rejects with HTTP 400
`Field '<name>': Value must be between A <= value <= B, but got V`;
`set_limits` clamps silently; handlers transform. "200, key = value" means the
value stored in the completion response's `generation_settings` (not `/props`
`default_generation_settings`) (not proof that sampling
used it, not model quality, not endpoint health or served identity).
Launch-dependent bounds are marked: `n_cmpl`'s upper bound is `n_parallel`.
Re-derive: `/usr/bin/python3 .ufo/waves/round-28/count-c1.py --out <receipt.json>`
(registry `registry/request-field-outcomes-r28.json`; the counter re-runs every
row on its own pinned server). Rows whose stored value is only a generic type
conversion (float32 saturation, truncation, 2^32 wrap) are true but not counted
as field knowledge (amendment A1). One request per field: a row is one observed
point, not the field's whole response function.
Numbers are converted to the field's C++ type before the bound check or clamp
(`server-schema.cpp:531-545`): integer-typed fields truncate a fractional JSON
value toward zero first, float-typed fields keep it subject to float32
rounding, so the bounds apply to the converted value, not necessarily to the
JSON number as written.

| id | field | value | outcome | meaning | source |
|---|---|---|---|---|---|
| F28-01 | sse_ping_interval | -2 | reject 400, bounds -1 to 2147483647 | A negative value below -1 is refused outright with HTTP 400 instead of being clamped, so clients must send -1 to disable SSE pings or a non-negative interval. | S140 |
| F28-02 | n_predict | -2 | reject 400, bounds -1 to 2147483647 | n_predict below -1 is rejected with HTTP 400 and not clamped, so clients asking for unbounded generation must send exactly -1 and never a smaller integer. | S141 |
| F28-03 | n_indent | -1 | reject 400, bounds 0 to 2147483647 | n_indent = -1 is a hard HTTP 400 rejection (bounds 0..2147483647) rather than a clamp to zero, so code-completion clients send 0 to disable indentation; the bound is checked after conversion to an integer. | S142 |
| F28-04 | n_keep | -2 | reject 400, bounds -1 to 2147483647 | n_keep accepts -1 (retain the whole prompt) but -2 is rejected with HTTP 400 (bounds -1..2147483647), so clients use -1 and cannot rely on clamping; the bound is checked after conversion to an integer. | S143 |
| F28-05 | n_discard | -1 | reject 400, bounds 0 to 2147483647 | n_discard = -1 is rejected with HTTP 400 (bounds 0..2147483647) instead of clamped, so clients send 0 (half context) or a positive integer discard count; the bound is checked after conversion to an integer. | S144 |
| F28-06 | n_cmpl | 0 | reject 400, bounds 1 to 4 | The server rejects n_cmpl outside one through n_parallel (four here) with HTTP 400, so clients must ask for no more completions than server slots. | S145 |
| F28-07 | t_max_predict_ms | -2 | reject 400, bounds -1 to 9223372036854775807 | t_max_predict_ms = -2 is rejected with HTTP 400 (bounds -1..9223372036854775807, checked after conversion to int64, so -1.5 becomes -1 and passes); a value of -1 or 0 sets no prediction time limit (the limit applies only when > 0). | S146 |
| F28-08 | top_k | -5 | 200, top_k = 0 | top_k is clamped silently to its soft minimum: -5 is stored as top_k = 0 (top-k disabled) rather than rejected; values beyond int32 wrap before the clamp (5000000000 is stored as 705032704), so clients validate 0..2147483647 themselves. | S147 |
| F28-09 | top_p | 2.5 | 200, top_p = 1.0 | top_p is clamped silently to its soft maximum: 2.5 is stored as top_p = 1.0 (the top-p filter is disabled; temperature and the other samplers are unchanged) rather than rejected, so clients check 0.0..1.0 before sending. | S148 |
| F28-10 | min_p | -1.5 | 200, min_p = 0.0 | min_p is clamped silently to its soft minimum: sent -1.5 it is served as min_p = 0.0 (disabled), a value no truncation of the request yields, so clients must validate 0.0..1.0 themselves. | S149 |
| F28-11 | top_n_sigma | 3.5e+38 | 200, top_n_sigma = 3.4028234663852886e+38 | top_n_sigma declares no explicit bounds, so a value above the float32 maximum is accepted and saturated to 3.4028e38 instead of being rejected; clients must keep values within the float32 range or read the stored value back, since a finite value can still saturate. | S150 |
| F28-12 | xtc_probability | 5.0 | 200, xtc_probability = 1.0 | llama-server silently clamps an out-of-range xtc_probability to 1.0 and still returns HTTP 200, so clients must validate the 0..1 range themselves instead of expecting an error. | S151 |
| F28-13 | temperature | -1.0 | 200, temperature = 0.0 | llama-server silently clamps a negative temperature to 0.0 (greedy decoding) with HTTP 200, so clients should reject negative values before sending them. | S152 |
| F28-14 | dynatemp_exponent | 1e+39 | 200, dynatemp_exponent = 3.4028234663852886e+38 | In this request dynatemp_exponent = 1e+39 (above the float32 maximum) was accepted with 200 and stored as 3.4028234663852886e+38 (field-omitted value 1.0); the declaration has no limits, so this is a generic float32 conversion, not a field bound: keep values in a sane range and read the stored value back. | S153 |
| F28-15 | repeat_last_n | -1 | reject 400, bounds 0 to 2147483647 | A negative repeat_last_n is rejected with HTTP 400 naming the inclusive hard bounds 0 to 2147483647, so clients must validate this count before sending instead of expecting a clamp. | S154 |
| F28-16 | repeat_penalty | 1e+39 | 200, repeat_penalty = 3.4028234663852886e+38 | In this request repeat_penalty = 1e+39 (above the float32 maximum) was accepted with 200 and stored as 3.4028234663852886e+38 (field-omitted value 1.0); the declaration has no limits, so this is a generic float32 conversion, not a field bound: keep values in a sane range and read the stored value back. | S155 |
| F28-17 | frequency_penalty | 1e+39 | 200, frequency_penalty = 3.4028234663852886e+38 | In this request frequency_penalty = 1e+39 (above the float32 maximum) was accepted with 200 and stored as 3.4028234663852886e+38 (field-omitted value 0.0); the declaration has no limits, so this is a generic float32 conversion, not a field bound: keep values in a sane range and read the stored value back. | S156 |
| F28-18 | dry_allowed_length | -1 | reject 400, bounds 0 to 2147483647 | llama-server rejects a negative dry_allowed_length with HTTP 400 and the exact integer bounds, so clients must clamp the DRY window length to 0..2147483647 before sending. | S157 |
| F28-19 | dry_penalty_last_n | -1 | reject 400, bounds 0 to 2147483647 | In this b11755 /completion fixture dry_penalty_last_n = -1 returns HTTP 400 with bounds 0..2147483647; the schema declares those as hard limits, so a negative value is refused rather than clamped. | S158 |
| F28-20 | mirostat | 5 | 200, mirostat = 2 | On this fixture mirostat = 5 returns HTTP 200 and generation_settings.mirostat = 2; the schema declares soft limits 0..2, so read the settings back to confirm the stored mode (not proof the sampler ran it). | S159 |
| F28-21 | mirostat_tau | 1e+39 | 200, mirostat_tau = 3.4028234663852886e+38 | In this request mirostat_tau = 1e+39 (above the float32 maximum) was accepted with 200 and stored as 3.4028234663852886e+38 (field-omitted value 5.0); the declaration has no limits, so this is a generic float32 conversion, not a field bound: keep values in a sane range and read the stored value back. | S160 |
| F28-22 | mirostat_eta | 1e+39 | 200, mirostat_eta = 3.4028234663852886e+38 | In this request mirostat_eta = 1e+39 (above the float32 maximum) was accepted with 200 and stored as 3.4028234663852886e+38 (field-omitted value 0.10000000149011612); the declaration has no limits, so this is a generic float32 conversion, not a field bound: keep values in a sane range and read the stored value back. | S161 |
| F28-23 | adaptive_target | 5.0 | 200, adaptive_target = 1.0 | Values above the soft maximum are silently clamped to 1.0, so clients must expect 200 and read generation_settings instead of a validation error. | S162 |
| F28-24 | adaptive_decay | 1.5 | reject 400, bounds 0.0 to 0.99 | Values above 0.99 are rejected with HTTP 400, so clients must keep adaptive_decay within 0.0 through 0.99 before sending. | S163 |
| F28-25 | seed | 4294967296 | 200, seed = 0 | One observed point: 4294967296 is stored as seed 0 (uint32 wrap modulo 2^32); -1 is the declared random-seed sentinel (stored as 4294967295), so clients send -1 or a uint32-range seed and read generation_settings back. | S164 |
| F28-26 | n_probs | 2.5 | 200, n_probs = 2 | A fractional n_probs is truncated to its integer part, so clients must send integers and confirm the stored value in generation_settings. | S165 |
| F28-27 | min_keep | -1 | reject 400, bounds 0 to 2147483647 | min_keep = -1 is refused with HTTP 400 naming the hard bounds 0..2147483647 (checked after conversion to an integer), so clients send an in-range integer and treat this bounds 400 (not every 400) as their own request error. | S166 |
| F28-28 | lora | [{"id": 0, "scale": 1.0}, {"id": 0, "scale": 0.5}] | 200, lora = [{"id": 0, "scale": 0.5}] | Duplicate adapter ids collapse to one id-keyed entry and the last scale wins, so clients must send at most one lora entry per adapter id. | S167 |
| F28-29 | preserved_tokens | ["upon", "upon", "a"] | 200, preserved_tokens = [261, 407] | Only strings that tokenize to exactly one token are kept, as ascending llama_token ids de-duplicated in a set, so send one-token strings and read preserved_tokens back to see what was kept. | S168 |
| F28-30 | reasoning_budget_tokens | -2 | reject 400, bounds -1 to 2147483647 | A reasoning_budget_tokens value below -1 is rejected with HTTP 400 by the hard limit, so clients must send -1 to disable the budget and never rely on a silent clamp. | S169 |
| F28-31 | logit_bias | {"12": 5} | 200, logit_bias = [{"bias": 5.0, "token": 12}] | Sending logit_bias as a JSON object returns 200 but generation_settings.logit_bias is normalized to an array of {"bias", "token"} objects, keeping only tokens in [0, n_vocab), so a client must read back the array form and may not assume an out-of-vocabulary token was applied. | S170 |
| F28-32 | ignore_eos | true | 200, logit_bias = [{"bias": null, "token": 2}] | Setting ignore_eos true returns 200 with generation_settings.ignore_eos true and, because the handler appends the precomputed EOG biases, injects token 2 into generation_settings.logit_bias with a null (minus-infinity) bias that the client never sent. | S171 |
| F28-33 | stop | "\n" | 200, stop = ["\n"] | A bare stop string is stored wrapped as a one-element array; an empty string is kept as [""], and an empty list falls back to the launch's default stop strings (none with this argv), so a client reads back the stored array. | S172 |
| F28-34 | samplers | "kp" | 200, samplers = ["top_k", "top_p"] | Sending samplers as the string "kp" returns 200 with generation_settings.samplers resolved to ["top_k", "top_p"], while unknown sampler names are dropped without an HTTP error (the server log warns) (an all-unknown array becomes []), so a client must read back the array and cannot assume the requested chain applied. | S173 |

Fields measured with no countable row (wave-1 seats, `.ufo/waves/round-28/w1/out/DataG*/rows.json` `no_rows`):
`field_bool` fields (`verbose`, `timings_per_token`, `stream`,
`cache_prompt`, `return_tokens`, `return_progress`, `backend_sampling`,
`post_sampling_probs`, `grammar_lazy`, `reasoning_control`) and the
`field_json` `echo` store the boolean sent or are not reported, and a
non-boolean value is a 400 JSON type error with no bounds; `include_usage` is
read only inside `stream_options` (a top-level `include_usage` or a non-object
`stream_options` is ignored with 200); the `speculative.*` declarations at lines 198-227 sit in
an `#if 0` block and are silently ignored on b11755; `typical_p`,
`dynatemp_range`, `presence_penalty`, `dry_multiplier`, `n_keep`/`n_predict`
in range echo the value sent; `dry_base` below 1.0 falls back to the default
1.75; `json_schema` is compiled into `generation_settings.grammar` (GBNF text
with `|`, not representable in this table); `reasoning_format`,
`continue_final_message`, `grammar_triggers`, `dry_sequence_breakers`,
`response_fields` and the `reasoning_budget_*` strings have no bounds message
and no stored transform. `n_cache_reuse` (400, bounds 0 to 2147483647) and
`xtc_threshold` (2.5 stored as 1.0) were the counter pilot and are excluded.
Release recheck (round 44, b11889): the `dry_sequence_breakers` clause above
holds for b11755 only. From commit 63412d873 (in b11889) `server-schema.cpp`
rejects more than 64 distinct entries (`Error: dry_sequence_breakers must
contain at most %d distinct entries`, limit `LLAMA_DRY_MAX_SEQ_BREAKERS` 64)
and duplicates are dropped (seat U1Notes, `.ufo/waves/round-44/w1/out/U1Notes/changes.md`).

## Round-28 instrument registry (owner: kama)

Same columns as `## Local gate/probe registry`. Rows added by round 28
(routed defect 3 of `corpus/lessons/round-27-verifier-spotcheck.md`).

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-28 C1 request-field outcomes | measurement: `/usr/bin/python3 .ufo/waves/round-28/count-c1.py --out <receipt.json>` (lane root; `--lane DIR`, `--repo GITDIR`) | 0 ran, prints `registered R counted N target 18 met B not-counted [...]` (label `counted`); 2 could not evaluate (pins, process identity, ports 47600-47619, base request); an uncaught error (e.g. malformed registry JSON) exits 1 with a traceback and no receipt | counter sha256 `a38faefeeb48be9fd3590b5077030ed6b7cef08dcaf1ca0540b464bd222749a5` (A1; A0 `e6a706bb…0540c`); snapshot `server-schema.cpp` sha256 `1f9d7b73…4050`; server `b6a31a8e…d804`, `libllama-server-impl.so` `e404b91a…59ed`, model `270cba1b…256d`; pilot `.ufo/waves/round-28/before/pilot-A1-receipt.json` (2 scratch rows counted 2); controls `.ufo/waves/round-28/controls/`, `controls-A1/` | `--out` file and a removed temporary directory; launches and stops its own llama-server |
| Round-27 C1 counter (retired) | `.ufo/waves/round-27/count-c1.py`, sha256 `49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765` — do not use; if replayed, the counter's entry command is `python3 .ufo/waves/round-27/count-c1.py --lane <lane> --repo <gitdir> --out <receipt.json>` | last run exit 0, `registered 0 counted 0 target 15 met False` (`.ufo/waves/round-27/a3/c1-final.out`) | retired with round-27 C1 (miss, never run on data); superseded for method by KQ37 and its round-28 qualification | none (retired) |
| Round-25 C2 context-capacity binding (repaired round 28) | measurement: `python3 .ufo/waves/round-25/count-c2.py` | prints `registered R observed O bound B missing [...]`; cells are recomputed from sha256-bound raw bodies and log, never read from receipt cells | sha256 `5aa64a370196f352435bdf2cee2526019a3eac2737eb194496c5126d5759fa2a`; committed receipt → `registered 14 observed 14 bound True missing []`; forged-cell and forged-raw fixtures in `.ufo/waves/round-28/w1/out/ExecCountC2Fix/`; every supplied hash in a nonempty raw map must match, but the checker does not require every named raw-hash key, so complete coverage depends on the receipt keeping its full raw-hash map; a coordinated forgery of cell, raw body and hash passes (binds receipt to raw bytes, not raw bytes to the server) | read-only |
| Gate registry completeness | gate: `python3 tools/gate-registry-check.py [--rev REV]` | 0 every tracked `.ufo/waves/round-*/count-*.py` path occurs in SKILL.md; 1 some do not (`unregistered <path>`); 2 could not evaluate | at base `4179301f`: exit 1, `unregistered .ufo/waves/round-25/count-c2.py`, `unregistered .ufo/waves/round-27/count-c1.py` (`.ufo/waves/round-28/w1/out/ExecGateRegistryCheck/base-4179301.out`); occurrence check only, it does not inspect row columns | read-only git |
| Echo recheck (round-27 live probe) | probe: `python3 tools/echo-recheck.py --out <fresh path>` (`--port` optional; default 48231-48233) | 0 `echo-recheck same N/N`; 1 `echo-recheck drift <ids>`; 2 cannot evaluate (also when `--out` exists) | replays `.ufo/waves/round-27/w1a3/out/ExecLiveEchoProbe/` requests against `receipt.json`; pins as round-27 counter; runs in `.ufo/waves/round-28/w1/out/ExecEchoRecheck/` | the `--out` file and its `<out>.server.log` sidecar; starts and stops its own server |

## Round-31 chat-completions parameter outcomes (b11755 fixture, owner: kama)

This section records one live observation per OpenAI-compatible parameter sent to `POST /v1/chat/completions`. The C1 claim is met only when the frozen counter counts at least 12 rows. Its base request is sent before each row request; the row body is the base body with `{param: sent}` applied and then `also` merged. Each counted row also needs a new `S###` source row, absent at the base revision, that cites a pinned filename, line, and commit `704366d`, and whose quoted substring is rechecked against that pinned source.

The fixture uses `~/.local/opt/llama-b11755/llama-server` (server SHA-256 `b6a31a8e…d804`) and `~/.cache/kama-shokunin/models/stories260K.gguf` (model SHA-256 `270cba1b…256d`). The default server arguments are `-m <model> --host 127.0.0.1 --port <port>`; the counter verifies server, implementation-library, and model digests against the registry and verifies the served model path through `/props`. Preregistration limits the measurement to `n_slots` 4.

The pinned llama.cpp snapshot is commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (`.ufo/waves/round-31/sources/SNAPSHOT.json`):

- `tools/server/server-common.cpp` — SHA-256 `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442`
- `tools/server/server-schema.cpp` — SHA-256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`
- `tools/server/server-task.cpp` — SHA-256 `4c3f413b9b54d4cc0e7b5998e6979a2389f5ff716e20cb1510ca7745fa233495`
- `tools/server/server-chat.cpp` — SHA-256 `91f48e09afc5a345033866380e82db1c3ad4d18baf1cec38ffa6cddaf6a6263e`

| id | param | sent | outcome | meaning | source |
|---|---|---|---|---|---|
| K31-01 | max_tokens | 3 | 200, max_tokens = 3, n_predict = 3 | Set max_tokens to bound output; do not assume this stored alias proves sampler use. | S190 |
| K31-02 | max_completion_tokens | 3 | 200, max_tokens = 3, n_predict = 3 | With both keys present, max_completion_tokens determines stored max_tokens and n_predict; clients should send a consistent limit and inspect stored settings when precedence matters. | S189 |
| K31-03 | logprobs | true | 200, n_probs = 20 | On b11755, `logprobs:true` sets `n_probs` to 20 when `top_logprobs` is omitted; explicitly send `top_logprobs` when you need a different count. | S187 |
| K31-04 | top_logprobs | 3 | 200, n_probs = 3 | When requesting token logprobs, set `logprobs` true; the server maps `top_logprobs` to stored `n_probs`. | S187 |
| K31-05 | top_logprobs | 3 | reject 400 invalid_request_error: top_logprobs requires logprobs to be set to true | Send `logprobs: true` when requesting `top_logprobs`; neither field is enabled implicitly. | S188 |
| K31-06 | messages | "hi" | reject 400 invalid_request_error: Expected 'messages' to be an array | Clients must send messages as an array; a string is not a valid substitute for the message list. | S182 |
| K31-07 | messages | [{"role":"user"}] | reject 400 invalid_request_error: All non-assistant messages must contain 'content' | Send content for every non-assistant message or expect this exact adapter rejection. | S183 |
| K31-08 | messages | [{"role":"assistant"}] | reject 400 invalid_request_error: Assistant message must contain either 'content' or 'tool_calls'! | An assistant message must include content or tool_calls; neither omission is accepted. | S184 |
| K31-09 | messages | [{"content":42,"role":"user"}] | reject 400 invalid_request_error: Expected 'content' to be a string or an array | A caller must send message content as a string or array; numeric content is rejected with HTTP 400. | S185 |
| K31-10 | response_format | {"type":"xml"} | reject 400 invalid_request_error: response_format type must be one of "text" or "json_object", but got: xml | This xml value was rejected here; clients should use text or json_object and not infer other response_format behavior from this single observation. | S181 |
| K31-11 | json_schema | {"type":"object"} | reject 500 server_error: Cannot use both json_schema and grammar | When sending a JSON schema, do not also send grammar; the adapter rejects the request with HTTP 500. | S180 |
| K31-12 | logprobs | true | reject 400 invalid_request_error: logprobs is not supported with tools + stream | When tools and streaming are both enabled, clients must omit logprobs to avoid HTTP 400. | S186 |
| K31-13 | user | "probe-user" | 200, no slot-parameter or response change | This request produced no stored user field; clients must not assume user is persisted in slot parameters. | S189 |
| K31-14 | parallel_tool_calls | false | 200, no slot-parameter or response change | In this no-tools sample, no slot or normalized-response fields changed; callers must not infer tool-call concurrency from it. | S189 |
| K31-15 | tools | [{"function":{"name":"f","parameters":{"type":"object"}},"type":"function"}] | 200, no slot-parameter or response change | Do not assume advertised tools run; inspect returned messages before relying on function-call behavior. | S189 |
| K31-16 | n | 2 | 200, n_choices = 2 | This b11755 request returned two choices; callers must not assume other builds match. | S191 |
| K31-17 | stream | true | 200, sse = true | Streaming clients must parse data frames until the server's [DONE] marker. | S189 |
| K31-18 | stream_options | {"include_usage":true} | 200, sse_usage = true | A client must enable streaming explicitly before expecting include_usage to add a usage frame. | S189 |


Limits, in the words of the limits seat (appended, not a counter input):

# C1 outcome limits

A `reject` row establishes the measured API error contract for that request, not a model refusal: C1 checks the HTTP status and exact `{code,message,type}` envelope, while the pinned chat-parameter parser is an endpoint adapter that throws for request conditions such as unsupported tool configuration or `response_format`; the formatter maps invalid requests to code 400, but context-size errors also map to 400, so status alone does not identify the cause (`.ufo/waves/round-31/count-c1.py` docstring L24-L29; `sources/llama.cpp-704366d/server-common.cpp` L91-L132, L123-L126, L1326-L1347, L1357-L1375). A `slot` row establishes only that the measured keys and values were present in the newest slot's stored `params`; the parser builds and returns task parameters and documents a sampling-layer pass-through, but this counter does not observe whether sampling used the stored setting or changed generated behavior (`count-c1.py` docstring L30-L31; `server-common.cpp` L1496-L1510, L1524-L1543). An `ignored` row establishes equality only for the base-versus-probe request's full slot parameters and the counter's normalized response fields; it is not a general claim that a parameter has no effect, because those checks cover a bounded request/profile and selected response summary, while the parser copies remaining request properties into `llama_params` and removes session-owned keys (`count-c1.py` docstring L24-L26, L36-L39, L46-L48; `preregistration.json` L21-L26; `server-common.cpp` L1524-L1541). A `response` row establishes only its named response-contract check: `n_choices` is `len(choices)`, not a measure of answer quality, and the counter admits only four such checks; the pinned parser creates the chat session and returns parameters without a quality judgment (`count-c1.py` docstring L32-L39, L56-L57; `server-common.cpp` L1489-L1494, L1524-L1543).

## Client-facing rules

1. For a request matching a `reject` row, present the recorded status and error as an API/request error, not as generated text or a model refusal (`count-c1.py` docstring L24-L29; `server-common.cpp` L91-L132, L1326-L1347, L1357-L1375).
2. Treat a `slot` row as evidence of the server-stored setting only; if the generation effect matters, verify that behavior separately rather than promising it from `/slots` (`count-c1.py` docstring L30-L31; `server-common.cpp` L1496-L1510, L1534-L1543).
3. Do not rely on an `ignored` result beyond its measured request/profile, and treat `n_choices` only as the number of choices to inspect—not a quality score (`count-c1.py` docstring L24-L26, L32-L39, L56-L57; `preregistration.json` L21-L26; `server-common.cpp` L1524-L1541).


### Round-31 attempt-2 meaning-cell corrections (appended 2026-10-23; frozen rows unchanged)

The round-31 attempt-2 falsification wave re-ran every registered outcome live and re-rendered each
`outcome` cell by hand: all eighteen cells matched byte for byte
(`.ufo/waves/round-31/w2/out/RevRow{A,B,C,D,E}/report.md`). The `meaning` cells are prose the frozen
counter does not check (it requires eight words); six of them overclaim the measured behaviour. The
corrections below are appended, not substituted, so the counted rows keep their measured bytes.

| id | committed meaning overclaims | measured counterexample (b11755, stories260K, default argv) | corrected reading |
|---|---|---|---|
| K31-02 | presents the two OpenAI limit aliases without saying a native `n_predict` wins | adding native `n_predict: 5` alongside `max_tokens`/`max_completion_tokens` stores 5, not the OpenAI value (`w2/out/RevRowA/meaning-probe.json`) | the two-key sample is correct; when a native `n_predict` is also present it takes precedence |
| K31-05 | says neither `logprobs` nor `top_logprobs` is enabled implicitly | `logprobs: true` alone stores `n_probs: 20`; the default comes from `server-common.cpp` L1519 (`w2/out/RevRowB/report.md`) | `top_logprobs` alone does not enable logprobs; `logprobs` alone enables a default of 20 top alternatives |
| K31-08 | reads "neither omission is accepted" as forbidding either omission | an assistant message with `content` and no `tool_calls` returns 200 (`w2/out/RevRowC/meaning-probe.json`) | only an assistant message carrying neither `content` nor `tool_calls` is rejected |
| K31-09 | says message content must be a string or an array | `{"role":"user","content":null}` returns 200 (`w2/out/RevRowC/meaning-probe.json`) | non-string/non-array/non-null content is rejected; `null` is accepted |
| K31-11 | reads as a blanket prohibition on `json_schema` with `grammar` | the same schema with `grammar: ""` returns 200 (`w2/out/RevRowD/`) | the rejection needs a non-empty `grammar`; an empty string does not trigger it |
| K31-12 | says the client must omit `logprobs` with tools and streaming | explicit `logprobs: false` with unchanged `tools` + `stream` returns 200 (`w2/out/RevRowD/`) | `logprobs: true` is what is unsupported with tools + stream; an explicit false is accepted |

One further boundary, from `w2/out/RevRowE/`: an `ignored` row is scoped to slot-parameter and
normalized-response equality at the measured request; `tools` demonstrably changes the response of
a grammar request (200 → 400), so `ignored` never means "no effect on any other request".

### Round-31 instrument registry rows

Same columns as `## Local gate/probe registry`. Counters added by round 31
(routed defect from `corpus/lessons/round-30-verifier-spotcheck.md` item 3, applied
here for both new counters; the round-29 and round-30 counters are registered by
`tools/gate-registry-check.py` at this commit).

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-31 C1 chat-completions outcomes | measurement: `/usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane <lane> --repo <scratch clone> --tip <full commit> --out <receipt.json>` | 0 ran, prints `registered R counted N target 12 met B not-counted [...]`; 2 could not evaluate (pins, `/props` model identity, ports 47900-47999, base request); an uncaught error exits 1 with no receipt | counter sha256 `d86c4a94…9216` (frozen at `0e6f8ed6`); snapshot files and digests `.ufo/waves/round-31/sources/SNAPSHOT.json` (server-common.cpp `b4f4aae7…d442`, server-schema.cpp `1f9d7b73…4050`); server `b6a31a8e…d804`, library `e404b91a…59ed`, model `270cba1b…256d`; `--out` directory must exist | starts and stops its own server; writes only the `--out` file |
| Round-31 C2 claim-row evidence | measurement: `/usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo <scratch clone> --tip <full commit> --out <receipt.json>` | 0 ran, prints `rows N base_mismatched M exempt E valid_corrections V false_corrections F unresolved U append_only A met B`; 2 could not evaluate (tip, base blob, correction header) | counter sha256 `2d06f38d…c6fe` (frozen at `0e6f8ed6`); base `07794a4d`; correction section heading and header fixed in the bytes; known defect: corrections are keyed by `(row, class)` and three claim rows share the cell `C1` (rounds 11-13), so those three dispositions cannot be expressed (`.ufo/waves/round-31/controls/RefRepair/`) | read-only git |
| Round-29 C1 self-assessment statements | measurement: `/usr/bin/python3 .ufo/waves/round-29/count-c1.py --repo <scratch clone> --tip <full commit> --out <receipt.json>` (`--list` adds every statement to the receipt) | 0 ran (whatever the count), prints `statements S mismatched_at_base M append_only A valid_corrections V false_corrections F unresolved U met B tip <12>`; 2 could not evaluate (tip unresolved, missing blob) and also refuses to overwrite an existing `--out` file | counter sha256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`; base `2aa46e24`; round-29 receipts `.ufo/waves/round-29/final/c1-513eba3b.json` and `c1-6de225c2.json`; round-31 re-run `.ufo/waves/round-31/c3/r29-at-tip.json` (`statements 69 mismatched_at_base 11 valid_corrections 11 unresolved 0 met True`) | reads committed objects only (`git --no-replace-objects`), never the working tree; writes only the `--out` file |
| Round-30 hold counter (retired for new claims) | `.ufo/waves/round-30/count-c1.py`, sha256 `c3f16ef1…9ce40d` — hold check only; entry command `python3 .ufo/waves/round-30/count-c1.py --repo <gitdir> --tip <rev> --out <receipt.json>` (`--list` adds every statement, `--oracle <path>` appends an oracle file) | 0 ran; 2 could not evaluate | still `met True`, 141 statements, unresolved 0 at the round-31 tip (`.ufo/waves/round-31/c1/hold-r30.out`) | read-only git |

### Round-32 instrument registry rows

Same columns as `## Local gate/probe registry`. The round-28 "Gate registry completeness" row
above is retained as history; its occurrence-only semantics are superseded by the first row here
(routed defect 3 of `corpus/lessons/round-31-verifier-spotcheck.md`). The two counters after it
were prose-registered before this round; the meaning gate exposed them and they are registered
properly here.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Gate registry completeness (round-32 repair) | gate: `python3 tools/gate-registry-check.py [--rev REV]` | 0 U == 0 and D == 0 (`registered R unregistered U defective D`); 1 a tracked counter is unregistered or a registered row is defective (`unregistered <path>`, `defective <path>: <reason>`); 2 could not evaluate | registered := the path occurs in a cell of a five-column registry table row; row defects graded: `thin-row`, `empty-entry`, `empty-exit-map`, `missing-path:PATH` (repo-relative cited paths must exist at the evaluated revision); `--selftest` prints `GATE_SELFTEST pass=6 fail=0`; arms, controls and mutations `.ufo/waves/round-32/c2/SUMMARY.md`, `selftest-final.out` at the landed tip; row semantics row S193 | read-only git |
| Round-17 verdict census (process tool) | measurement: `python3 .ufo/waves/round-17/count-verdicts.py ADVICE_DIR [--expect-names FILE.json] [--json]` | 0 count completed (any verdict mix); 2 could not evaluate (`--expect-names` unreadable / bad JSON) | strict first-line `VERDICT:` classifier; round-16 falsify arm: 34/40/0 + 5 nonconformant (`corpus/lessons/round-17.md` M3); demo `.ufo/waves/round-17/provenance-0to79-demo.txt` | read-only; writes nothing |
| Round-26 C1 echo-signature counter | measurement: `python3 .ufo/waves/round-26/count-c1.py --out <receipt.json>` | 0 ran, prints `counted N` against the frozen predicate; 2 could not evaluate (pins, launch failure) | relaunches every trigger against the sha256-pinned binary and model (`.ufo/waves/round-26/preregistration.json`); echo-shortcut limit recorded in `corpus/lessons/round-26.md` | starts/stops its own fixture server; writes only the `--out` file |
| Round-32 C2r claim-row evidence | measurement: `/usr/bin/python3 .ufo/waves/round-32/count-c2r.py --repo <clone> --tip <full commit> --out <receipt>` | 0 ran, prints `rows N base_mismatched M exempt E valid_corrections V false_corrections F unresolved U append_only A met B`; 2 could not evaluate (tip, base blob, correction header) | counter sha256 `ef298b63…c92e` (frozen at `9afaf0e9`); base `07794a4d`; round-qualified key `(round, row, class)` parsed from `CR<F>:<N>:` with a uniqueness precondition (duplicates are false); before receipts `.ufo/waves/round-32/c1/before-base.json`; kill-rule controls `.ufo/waves/round-32/c1/controls/`; final re-run `.ufo/waves/round-32/c2r/c2r-tip.json` at the landed tip | read-only git |

## Round-33 receipt evidence replays

The round-32 closure correction records three control filenames whose bodies
are not the fixture outputs their names imply. Leave those historical files
byte-intact; the authoritative fixture outputs are
`.ufo/waves/round-32/c2/controls/{thin-v2.out,noexit-v2.out,badpath-v2.out}`.
`corpus/lessons/round-33.md` records the append-only correction and S194's
precise source anchor. The gate definition is the docstring "Contract" at
`tools/gate-registry-check.py:15-16` (S194), not a live endpoint claim.

Replay the round-32 gate from its pinned source revision and emit the clean
lane-tip run plus three deterministic temporary-Git controls:

```sh
python3 tools/round33-gate-receipts.py capture --repo . --source-rev 967d88528c1d83535563f971863f7855f76b4849 --out .ufo/waves/round-33/c2/final
python3 tools/round33-gate-receipts.py audit --repo . --tip <full-commit> --source-rev 967d88528c1d83535563f971863f7855f76b4849 --receipt-dir .ufo/waves/round-33/c2/final
```

`capture` refuses to overwrite an existing output directory and writes only
beneath `.ufo/waves/round-33/c2/`; fixture Git writes remain temporary. Each
receipt records the exact argv, source/evaluated revision, evaluated tree,
gate and runner digests, numeric `EXIT_CODE`, and stdout/stderr. `audit`
replays the pinned gate and requires the exact expected lines and exit for
each named fixture. These receipts grade the registry instrument, not model
readiness or endpoint health.

The round-33 calibration census is narrower than the round-29 all-statement
counter: it reads the round-32 C2 Scorecard row at its authoring revision and
checks only the three append-only replacement mappings:

```sh
python3 tools/round33-claim-audit.py --repo . --statement-rev dc4258bdb08d658f1c5b15abc8378461659bd155 --tip <full-commit>
```

### Round-34 instrument registry rows

Same columns as `## Local gate/probe registry`. The round-33 counters were
documented in prose only, so the lane's own instrument gate could not see them:
its population named only `.ufo/waves/round-*/count-*.py`. Round 34 widens the
population to `tools/round<N>-*.py` and registers both counters as rows.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-33 C1 claim-statement audit | measurement: `python3 tools/round33-claim-audit.py --repo . --statement-rev <full-commit> --tip <full-commit>` | 0 ran, prints `R33_CLAIM_AUDIT false_at_writing=F valid_corrections=V unresolved=U met=B`; 1 the census did not reach its target; 2 could not evaluate (unreadable revision or blob) | counter sha256 `e98d8c0ca5e118bc7a82...`; preregistration `.ufo/waves/round-33/preregistration.json`; receipts `.ufo/waves/round-33/c1/after-evidence-tip.out`; lesson `corpus/lessons/round-33.md` | read-only git; writes nothing |
| Round-33 C2 gate-receipt replay | measurement: `python3 tools/round33-gate-receipts.py capture --repo . --source-rev <full-commit> --out <dir>` then `python3 tools/round33-gate-receipts.py audit --repo . --tip <full-commit> --source-rev <full-commit> --receipt-dir <dir>` | 0 ran, prints `R33_GATE_RECEIPT_AUDIT complete=C/4 missing=M invalid=I met=B`; 1 a fixture did not match its expected output or exit; 2 could not evaluate | counter sha256 `196d9766cadc286fd...`; receipts `.ufo/waves/round-33/c2/final/`; audit receipt `.ufo/waves/round-33/c2/after-evidence-tip.out` | writes only the `--out` directory; fixture Git writes stay in a temporary directory |
| Round-34 C1 capability-repertoire audit | measurement: `python3 tools/capability-repertoire-audit.py --repo . --tip <full-commit> --out <receipt.json>` | 0 met, prints `listed L observed O missing M unsubstantiated U met True`; 1 the canonical repertoire table does not carry every demonstrated capability, or a canonical row has no resolving evidence pointer; 2 could not evaluate (unreadable revision or missing SCORECARD.md) | `--selftest` prints `CAP_SELFTEST pass=2 fail=0`; before receipt `.ufo/waves/round-34/c1-before.out`; lesson `corpus/lessons/round-34.md` | read-only git; writes only the `--out` receipt |


## Round-43 registry completion (counters of rounds 35-43)

Round 43 claim C1 registers the sixteen tracked round counters of rounds 35-42 that the five-column gate (`tools/gate-registry-check.py`) reported unregistered since round 35, and the three round-43 counters. Every row below names only flags its counter declares, states the exit codes its source returns, and pins the counter's SHA-256 prefix at the round-43 freeze commit `895793e0b4c56bdcb939277b8ff0251b26306d4d` (`tools/round43-registry-audit.py` checks both). The rows describe what each counter computes, not that its claim held.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-35 C2 coverage-map entry | measurement: `python3 tools/round35-coverage-audit.py --repo <lane> --tip <full-commit> [--selftest]` | 0 met True, prints `named 1 file_exists 1 cited_row 1 met True`, or a passing `--selftest`; 1 met False, prints the same line with `met False` (no name inside the `## Coverage map — round 35 addition` block, a missing entry file, or no cited S-id that corpus/SOURCES.md registers), or a failing `--selftest`; 2 usage (argparse) or an uncaught exception at the file-read boundary, while a bad `--tip` is not an error: a failed `git show` reads as absent and exits 1 | counter sha256 `ff5318494c01`; base `.ufo/waves/round-35/controls/c2-base.out` prints `named 0 file_exists 0 cited_row 0 met False`; measured `.ufo/waves/round-35/c2-after.out` prints `named 1 file_exists 1 cited_row 1 met True`; `--selftest` prints `SELFTEST base_met=False junk_met=False pass=1` (`.ufo/waves/round-35/controls/c2-selftest.out`) | read-only `git show` plus local file reads; writes nothing |
| Round-35 C1 r34 self-assessment corrections | measurement: `python3 tools/round35-statement-audit.py --repo <lane> [--lesson <path>] [--selftest]` | 0 met True, prints `uncorrected 0 false_corrections 0 report_unchanged 1 met True`, or a passing `--selftest`; 1 met False (a missing or false correction row, or a changed r34 report blob; a `--lesson` file that does not exist reads as empty text and is not an error), or a failing `--selftest`; 2 usage (argparse) or an uncaught exception from `git show`/`rev-parse` in the fact derivation | counter sha256 `ca7e099dd5e9`; base `.ufo/waves/round-35/controls/c1-noop.out` prints `uncorrected 4 false_corrections 0 report_unchanged 1 met False`; measured `.ufo/waves/round-35/c1-after.out` prints `uncorrected 0 false_corrections 0 report_unchanged 1 met True`; `--selftest` prints `SELFTEST missing_met=False bad_met=False pass=1` (`.ufo/waves/round-35/controls/c1-selftest.out`) | read-only `git show` and `rev-parse`, plus one lesson-file read; writes nothing |
| Round-36 C2 coverage-map entry | measurement: `python3 tools/round36-coverage-audit.py --repo <clone> --tip <full commit>` (`--selftest` runs the base, outside-heading and old-S-id arms) | 0 all three legs hold, prints `named 1 file_exists 1 cited_new 1 met True` (`--selftest`: every arm holds, prints `SELFTEST base_met=False outside_met=False old_id_met=False pass=1`); 1 any leg fails, prints `named N file_exists F cited_new C met False` with the failing legs at 0 (`--selftest`: an arm fails); 2 usage error (argparse exits 2) or an uncaught exception, the latter printing `error: <exc>` | counter sha256 `d2f8965b067f` (blob at 895793e0); base `.ufo/waves/round-36/controls/c2-base.out` (`named 0 file_exists 0 cited_new 0 met False`, exit 1), measured `.ufo/waves/round-36/c2/after.out` (`named 1 file_exists 1 cited_new 1 met True`, exit 0), selftest `.ufo/waves/round-36/c2/selftest.out` (`SELFTEST base_met=False outside_met=False old_id_met=False pass=1`, exit 0) | read-only git in `--repo`; writes nothing |
| Round-36 C1 routed-statement corrections | measurement: `python3 tools/round36-statement-audit.py --repo <clone> --tip <full commit>` (`--selftest` runs the empty-lesson and forbidden-token arms) | 0 every frozen id has a true correction row and both blob pins still match, prints `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True` (`--selftest`: `SELFTEST empty_met=False bad_met=False words=20 pass=1`); 1 a correction row is missing or false, or a blob moved off its pin, prints the same fields with `met False` (`--selftest`: an arm fails); 2 usage error (argparse exits 2) or an uncaught exception, the latter printing `error: <exc>` | counter sha256 `886e4598269f` (blob at 895793e0); base `.ufo/waves/round-36/controls/c1-noop.out` (`uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`, exit 1), measured `.ufo/waves/round-36/c1/after.out` (`uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True`, exit 0), selftest `.ufo/waves/round-36/c1/selftest.out` (`SELFTEST empty_met=False bad_met=False words=20 pass=1`, exit 0) | read-only git in `--repo` and in the hard-coded fleet root at HEAD (the round-35 report blob pin); writes nothing |
| Round-37 C2 coverage-map entries | measurement: `python3 tools/round37-coverage-audit.py --repo <clone> --tip <full-commit> [--selftest]` | 0 met True, print `named N files_exist F cited_new C met True`, and with `--selftest` every fixture arm holds (`SELFTEST base_met=0 outside_met=0 old_id_met=0 missing_met=0 pass=1`); 1 met False, print `met False` (a name outside the heading, a missing entry file, or an S-id already at base), including a `--repo` git cannot read, which degrades to empty inputs and still exits 1; 2 usage, argparse missing `--repo` or `--tip` or an unrecognized flag, and any uncaught error, which prints `error: <exc>` to stderr | counter sha256 `f63ea87adef6` (blob at 895793e0); preregistration `.ufo/waves/round-37/preregistration.json`; measured receipt `.ufo/waves/round-37/c2/after.out`: `named 3 files_exist 3 cited_new 3 met True`, exit 0; base control `.ufo/waves/round-37/controls/c2-base.out`: `named 0 files_exist 0 cited_new 0 met False`, exit 1, selftest line `SELFTEST base_met=0 outside_met=0 old_id_met=0 missing_met=0 pass=1`, exit 0; pinned base `6a4afdfe` | read-only git; writes nothing |
| Round-37 C1 routed-statement corrections | measurement: `python3 tools/round37-statement-audit.py --repo <clone> --tip <full-commit> [--selftest]` | 0 met True, print `uncorrected U false_corrections F lesson_unchanged L report_unchanged R met True`, and with `--selftest` every fixture arm holds (`SELFTEST empty_met=False bad_met=False good_met=True pass=1`); 1 met False, print `met False` (a missing correction row counts as uncorrected, a forbidden wrong-id or rc restatement as false_corrections, a changed r36 lesson or fleet report blob as unchanged 0), including a `--repo` git cannot read, which degrades to an empty lesson and still exits 1; 2 usage, argparse missing `--repo` or `--tip` or an unrecognized flag, and any uncaught error, which prints `error: <exc>` to stderr (e.g. unreadable out-of-repo staged append) | counter sha256 `50dea74c3a3e` (blob at 895793e0); preregistration `.ufo/waves/round-37/preregistration.json`; measured receipt `.ufo/waves/round-37/c1/after.out`: `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True`, exit 0; do-nothing control `.ufo/waves/round-37/controls/c1-noop.out`: `uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`, exit 1, selftest line `SELFTEST empty_met=False bad_met=False good_met=True pass=1`, exit 0; pinned base `6a4afdfe`, lesson blob `6fb1ec15`, report blob `8b7408e6` | read-only git; reads the staged append and the fleet round-36 report outside the repository; writes nothing |
| Round-38 C2 coverage-map block | measurement: `python3 tools/round38-coverage-audit.py --repo <clone> --tip <full-commit>` | 0 met True, prints `named N files_exist N cited_new N met True` and, when non-empty, `new ids: [...]`; 1 met False (an entry not named inside the `## Coverage map — round 38 addition` block, an entry file absent at the tip or already present at base 2a4a97dc, an id not on a `source:` line or held by no registry row whose pinned URL intersects that line, an entry citing no new id, or cited_new other than 3); 2 usage only (argparse: `--repo` and `--tip` are both required); an uncaught error also exits 1 with no measurement line | counter sha256 `7abb0eb901bc` (blob at freeze 895793e0, unchanged at the clone tip); do-nothing control `.ufo/waves/round-38/controls/c2-base.out` prints `named 0 files_exist 0 cited_new 0 met False` (exit 1); measured `.ufo/waves/round-38/c2/after.out` prints `named 2 files_exist 2 cited_new 3 met True` (exit 0) with `new ids: S352, S353, S472`; frozen predicate and counting command `.ufo/waves/round-38/preregistration.json` (frozen before scoring at 41e149ce) | read-only git against `--repo` (`rev-parse`, `show`, `cat-file -e`); writes nothing |
| Round-38 C3 counting-instrument reproducibility | measurement: `python3 tools/round38-operability-audit.py --repo <clone> --tip <full-commit>` | 0 met True, prints `found N base_found N help_ok N rerun_ok N report_37 N receipt_ok N met True`; 1 met False (an inherited r37 instrument missing at the tip or present at base 2a4a97dc, an instrument that exits nonzero on `--help`, a rerun at the r37 tip that exits nonzero, the 37th seat report absent at the tip, or the seat-exit receipt not parsing to 37 members); 2 usage only (argparse: `--repo` and `--tip` are both required); an uncaught error also exits 1 with no measurement line | counter sha256 `cef6f21983a2` (blob at freeze 895793e0, unchanged at the clone tip); do-nothing control `.ufo/waves/round-38/controls/c3-base.out` prints `found 0 base_found 0 help_ok 2 rerun_ok 2 report_37 0 receipt_ok 0 met False` (exit 1); measured `.ufo/waves/round-38/c3/after.out` prints `found 2 base_found 0 help_ok 2 rerun_ok 2 report_37 1 receipt_ok 1 met True` (exit 0); reruns the two inherited round-37 counting instruments (statement and coverage) against r37 tip 2a4a97dc, whose inputs are `.ufo/waves/round-37/w1/out/CriticEntries.md` and `.ufo/waves/round-37/w1/out/seat-exit-codes.json` | read-only git in `--repo` and in the rerun counters (`show`, `cat-file -e`); the two reruns run without `--selftest`; writes nothing |
| Round-38 C1 R36-D2C statement correction | measurement: `python3 tools/round38-statement-audit.py --repo <clone> --tip <full-commit>` | 0 met True, prints `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True` then `note: staged rows present`; 1 met False (no correction row naming R36-D2C in `corpus/lessons/round-38.md`, a forbidden wrong id S331 or S334 inside that row, the five staged ids not all named, the five staged rows not re-derivable at lines 9/13/14/15/16, a changed r37 lesson blob or r37 fleet report blob, or the lesson file absent at the tip); 2 usage only (argparse: `--repo` and `--tip` are both required); an uncaught error also exits 1 with no measurement line | counter sha256 `3c4786dfc53b` (blob at freeze 895793e0, unchanged at the clone tip); do-nothing control `.ufo/waves/round-38/controls/c1-noop.out` prints `uncorrected 1 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False` (exit 1); measured `.ufo/waves/round-38/c1/after.out` prints `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True` (exit 0); pins r37 lesson blob 20f7909b and r37 fleet report blob 1c6ea9fa, both re-verified at freeze; reads the read-only staged package SOURCES.append.md, sha256 `3ad0df68e84` | read-only `git show` and `git rev-parse` in `--repo`, one read-only `git rev-parse` in the fleet repo, and a read of the staged package; writes nothing |
| Round-40 C1 digest-citation corrections | measurement: `python3 tools/round40-calibration-audit.py --repo <clone> --tip <full commit> --out <receipt>` | 0 met, prints `s474_row B amend_corrected B r36d2c_fixed B false_corrections N met=True`; 1 not met (the same line with `met=False`, and likewise an absent blob, an unreadable repo or tip, or a failed `--out` write — the counter never returns a could-not-evaluate code); 2 argparse usage error (a missing `--repo` or `--tip`) | counter sha256 `712ee8b6e7a0` at `895793e0`; base `.ufo/waves/round-40/controls/c1-base.out` = `s474_row=0 amend_corrected=0 r36d2c_fixed=0 false_corrections=1 met=False`; measured `.ufo/waves/round-40/c1/after.out` = `s474_row=0 amend_corrected=1 r36d2c_fixed=1 false_corrections=0 met=False`, re-measured 2026-10-25 at `895793e0` = `s474_row=0 amend_corrected=1 r36d2c_fixed=1 false_corrections=0 met=False` exit 1; routed defect D1 in `corpus/lessons/round-40-verifier-spotcheck.md` — the S474 test reads `row[7]` (status) instead of `row[6]` (teaches), so that leg cannot be met by a schema-valid row, and the claim is declared unverified not credited | read-only git (`git show`); writes only the `--out` file, whose directory must already exist |
| Round-40 C2 wave-evidence completeness | measurement: `python3 tools/round40-operability-audit.py --repo <clone> --tip <full commit> --out <receipt>` | 0 met, prints `spec_exists B run_exists B spec_sha_ok B run_sha_ok B counts_ok B met=True`; 1 not met (the same line with `met=False`, and likewise absent blobs or an unreadable repo or tip — the counter never returns a could-not-evaluate code); 2 argparse usage error (a missing `--repo` or `--tip`) | counter sha256 `c227aedb3857` at `895793e0`; base `.ufo/waves/round-40/controls/c2-base.out` = `spec_exists=0 run_exists=0 spec_sha_ok=0 run_sha_ok=0 counts_ok=0 met=False`; measured `.ufo/waves/round-40/c2/after.out` = `spec_exists=1 run_exists=1 spec_sha_ok=1 run_sha_ok=1 counts_ok=1 met=True`, re-measured 2026-10-25 at `895793e0` = the same line, exit 0; pins `spec.json` 397f598009ad9dab0699cc73d165cff583d8f069b445f0dbaa0b79f6a4122cb7 and `run.json` d0666a36f483685bcadfdce997389ea4af7c6a80efe8b75c70e2e4c6d2039642 with counts.total 36 and items 36, all stated in `.ufo/waves/round-40/preregistration.json` | read-only git (`git show`); writes only the `--out` file, whose directory must already exist |
| Round-41 C2 engine version-pin watch (operability, capability acquisition) | measurement: `python3 tools/round41-pinwatch-audit.py --repo . --tip <full-commit> --seed <int> --out <receipt>` | 0 met, prints `tip=<full>` then `tool=T contract=C live=L sourced=S capability=K met=True seed=N`; 1 not met, same line with `met=False` (an uncaught traceback, for example a tar extract failure or a 120 s `git ls-remote` timeout, also exits 1); 2 could not evaluate, `could-not-evaluate: <err>` on stderr, from an EvalError raised by `git rev-parse` or `git archive` on the repo | sha256 `4ca5ddee1b42` of the blob at 895793e0; base receipt `.ufo/waves/round-41/controls/base.c2.out` at tip 8893b894 reads `tool=0 contract=0 live=0 sourced=0 capability=0 met=False seed=41`; measured receipt `.ufo/waves/round-41/c2/after.out` at tip 4fe239a4 reads `tool=1 contract=1 live=1 sourced=1 capability=1 met=True seed=788600741`; same-seed replay `.ufo/waves/round-41/c2/after-seed41.out`; frozen CASES 6, ROUND_DATE 2026-10-25; inputs `registry/engine-pins.tsv` and `corpus/knowledge/engine-pin-watch.md` | read-only on `--repo` (rev-parse, archive); writes only the `--out` file; unpacks a temporary git archive export whose case directories hold the fixtures and removes it at exit and on SIGTERM; the live leg reads `git ls-remote --tags` over the network for every repo the pins file names |
| Round-41 C1 SCORECARD head-axis reconciliation (calibration) | measurement: `python3 tools/round41-scorecard-reconcile.py --repo . --tip <full-commit> --out <receipt>` | 0 met, prints `tip=<full>` then `axes=A facts=F hash_bad=H lines_bad=L run_bad=R dead=D score_bad=S hollow=W mismatches=M met=True`; 1 met False with one `detail:` line per mismatch (an uncaught tar extract failure also exits 1); 2 could not evaluate, `could-not-evaluate: <err>` on stderr, from an EvalError (unresolvable tip, SCORECARD.md absent, no `## Axes` line or no table beneath it) | sha256 `eff934a27b3e` of the blob at 895793e0; expected score vector operability 8 freshness 8 depth 7 coverage 9 calibration 7 adjacency 7; base receipt `.ufo/waves/round-41/controls/base.c1.out` at tip 8893b894 reads `axes=6 facts=13 hash_bad=2 lines_bad=2 run_bad=0 dead=6 score_bad=2 hollow=4 mismatches=16 met=False`; measured receipt `.ufo/waves/round-41/c1/after.out` at tip 4fe239a4 reads `axes=6 facts=24 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True` | read-only on `--repo` (rev-parse, cat-file, archive); writes only the `--out` file; runs each RUN fact with bash inside a temporary git archive export removed at exit and on SIGTERM |
| Round-42 C3 context-capacity assimilation (entry + rows + coverage + gate + census legs) | measurement: python3 tools/round42-capacity-audit.py --repo <clone> --tip <full commit> --base <full commit> --out <receipt.json> (only its declared options; --base defaults to 0b606b03bf0b2a87b791aa537f6c72c941624cf0) | 0 met, prints `tip=<full>` then `entry=E rows=R coverage=C gate=G census=N met=True` and one `detail:` line per failed leg; 1 not met (any leg 0: an evidence copy or `corpus/knowledge/context-capacity-engine-sides.md` absent at --tip, a row S478/S479 missing or mis-celled, the ground already present at --base, no coverage line in `corpus/README.md`, a gate quote not found whitespace-normalised in its committed copy, or `sources-census.sh` absent or exiting nonzero); 2 could not evaluate (git rev-parse, git archive or tar extraction failure); a census-validate timeout is uncaught, so it exits 1 with a traceback and writes no receipt | counter sha256 `964f12e0f99e` at 895793e0; base `.ufo/waves/round-42/controls/base.c3.out` = `entry=0 rows=0 coverage=0 gate=0 census=1 met=False` exit 1, measured `.ufo/waves/round-42/c3/after.out` = `entry=1 rows=1 coverage=1 gate=1 census=1 met=True` exit 0 at 2c018107; fixed names `corpus/lessons/round-42.md`, evidence copies `.ufo/waves/round-42/c3/vllm-v0.32.0-kv_cache_utils.py` and `.ufo/waves/round-42/c3/llamacpp-704366d7-server-models.cpp`, assimilation scratch `.ufo/waves/round-42/assimilation/` (quarantine-slice must be non-empty), source rows S478 S479 | read-only git; writes only the `--out` receipt and creates its parent directory; the temporary tip export is removed |
| Round-42 C2 digest ledger (tool + contract + live + hygiene + capability legs) | measurement: python3 tools/round42-digest-audit.py --repo <clone> --tip <full commit> [--seed N] --out <receipt.json> (--seed defaults to a random 1..2^31-1 value, printed in the summary) | 0 met, prints `tip=<full>` then `tool=T contract=C live=L hygiene=H capability=K met=True seed=N` plus a `live-reference:` line and one `detail:` line per failure; 1 not met (`tools/digest-ledger.py` absent, a fixture case whose summary line or exit differs from this counter's reference, a live scan differing from the reference or lacking ledger_bad=0 wrong_unflagged=0 unknown=0 external_ok>=4, a leaked private-TMPDIR entry after the two round-41 counters, or no `digest-ledger` row naming `tools/digest-ledger.py` in the highest canonical capability list); 2 could not evaluate (git rev-parse, git archive or tar extraction failure); a contract or live subprocess timeout scores that leg 0 instead of exiting 2 | counter sha256 `c064ddb2050e` at 895793e0; base `.ufo/waves/round-42/controls/base.c2.out` = `tool=0 contract=0 live=0 hygiene=0 capability=0 met=False seed=42` exit 1, measured `.ufo/waves/round-42/c2/after.out` = `tool=1 contract=1 live=1 hygiene=1 capability=1 met=True seed=42` and `.ufo/waves/round-42/c2/after-seed7.out` = `tool=1 contract=1 live=1 hygiene=1 capability=1 met=True seed=7`, both exit 0 with `live-reference: tokens=97 blob=88 external_ok=5 external_absent=0 unverifiable=3 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0 exit=0`; ledger `registry/digest-ledger.tsv` | read-only git; writes only the `--out` receipt and creates its parent directory; extracts a temporary export that it runs the fixture cases inside, removes every temporary directory, and runs the two round-41 counters (bare filenames scorecard-reconcile.py and pinwatch-audit.py) with a private TMPDIR |
| Round-42 C1 self-description reconcile (SCORECARD head plus README and PROVINCE) | measurement: python3 tools/round42-selfdesc-reconcile.py --repo <clone> --tip <full commit> --out <receipt.json> | 0 met, prints `tip=<full>` then `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=N met=True` and one `detail:` line per failed item; 1 not met (mismatches > 0, i.e. any failed item in those ten groups, including a cited receipt that does not resolve and a top-level entry README.md does not name); 2 could not evaluate (SCORECARD.md missing at --tip, a git failure, or an AttributeError/ValueError while parsing the imported round-41 counter's helpers) | counter sha256 `9736923ec308` at 895793e0; imports the round-41 scorecard counter (bare filename scorecard-reconcile.py) and inherits its r41 term; base `.ufo/waves/round-42/controls/base.c1.out` = `r41=0 banner=4 planned=3 retired=4 saturation=3 caps=4 receipts=0 readme=11 province=5 rel=6 mismatches=40 maxN=41 met=False` exit 1, measured `.ufo/waves/round-42/c1/after.out` = `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=42 met=True` exit 0 at 2c018107; lesson `corpus/lessons/round-42.md` | read-only git; writes only the `--out` receipt and creates its parent directory; the imported round-41 counter owns its own temporary export |
| Round-43 C1 instrument registry vs tree | measurement: `python3 tools/round43-registry-audit.py --repo <clone> --tip <full commit> --out <receipt.json>` | 0 met, prints `unreg U defect D flags F pins I selftest S dc C spot P hidden H pop N registered R mismatches M met True`; 1 not met (mismatches above zero, pop below 28 or registered below 28) or an uncaught exception with no summary; 2 could not evaluate (git, gate or gate-selftest failure); a SIGTERM handler exits 143 | counter sha256 `683c72c0de4b`; reads `tools/gate-registry-check.py` as committed at the tip; base receipt `.ufo/waves/round-43/controls/base.c1.out` line `unreg=16 defect=0 flags=2 pins=19 selftest=1 dc=1 spot=1 hidden=2 pop=28 registered=12 mismatches=42 met=False`; the measured line is the same counter's summary at the measured commit | read-only git on `--repo`, plus a throwaway clone in a temp directory for the gate self-test run; writes only the `--out` receipt and creates its parent directory; temp dirs removed at exit and on SIGTERM |
| Round-43 C2 hexrun census | measurement: `python3 tools/round43-hexrun-audit.py --repo <clone> --tip <full commit> --seed <int> --out <receipt.json>` | 0 met, prints `tool T contract C live L hygiene H capability K met True seed S`; 1 any leg 0 or an uncaught exception with no summary; 2 could not evaluate (git, tar, fixture or timeout failure); a SIGTERM handler exits 143 | counter sha256 `a455ba5522d5`; contract is twelve fixtures (eleven planted dir cases plus one throwaway git repo) built by the counter, and the drawn seed is printed for replay; base receipt `.ufo/waves/round-43/controls/base.c2.out` line `tool=0 contract=0 live=0 hygiene=0 capability=0 met=False seed=43`; base unexplained runs `.ufo/waves/round-43/c2/base-unresolved.tsv` holds 73 rows (64 of length 40, 7 of length 32, one 39, one 65); the measured line is the same counter's summary at the measured commit | read-only git on `--repo`; extracts the tip into a temporary tar export, builds fixture repos under temp and runs the scan under an empty private temp dir, all removed at exit; writes only the `--out` receipt |
| Round-43 C3 health-surface process map | measurement: `python3 tools/round43-health-audit.py --repo <clone> --tip <full commit> --base <full commit> --out <receipt.json>` | 0 met, prints `entry E rows R coverage C gate G refetch F census N met True`; 1 any leg 0 or an uncaught exception with no summary; 2 could not evaluate (git, tar or census failure); a SIGTERM handler exits 143 | counter sha256 `aa293a2519a0`; six legs over the process entry, two new registry rows, the lesson Gate, live refetch and census validate; `--base` defaults to the round-42 base commit; base receipt `.ufo/waves/round-43/controls/base.c3.out` line `entry=0 rows=0 coverage=0 gate=0 refetch=1 census=1 met=False`; the measured line is the same counter's summary at the measured commit | read-only git on `--repo`; extracts the tip into a temporary tar export and removes it; live `gh api` fetch with a `curl` fallback per API URL; runs the fleet-root census script in validate mode by absolute path; writes only the `--out` receipt |

## Round-44 instrument registry (release re-verification and calibration ledgers)

Rows for the round-44 counters and drafting tool (seat S9Registry drafted the two counter rows from each tool's `--help`, argparse declarations and measured exits; the L1 rewrote the drafter row after repairing its exit codes). Same columns as `## Local gate/probe registry`.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-44 C1 release re-verification audit | measurement: `python3 tools/round44-release-recheck-audit.py --repo <clone> --tip <full-commit> --upstream <llama.cpp clone> [--out <receipt>]` | 0 met, prints `pop=P rows=R valid=V unverified=U unchanged=a holds=h reworded=w drifted=d removed=r flags_missing=F section=S met=True` then one `detail:` line per unverified row or unflagged drifted/removed row; 1 not met, the same line with `met=False` (measured as the pre-ledger base at `098df344`: `pop=91 rows=0 valid=0 unverified=91 ... section=0 met=False`, exit 1); 2 could not evaluate, `could-not-evaluate: <err>` on stderr from an EvalError raised by `git rev-parse` of `--tip`, `git cat-file -e` of the release or a population pin, or an unreadable base `corpus/SOURCES.md` (measured with a non-git `--repo`: `git rev-parse --verify HEAD^{commit}: fatal: not a git repository`, exit 2), and equally 2 for the argparse usage error | counter sha256 `87503e18e47d` (blob at 77d1bbf5); population is the 91 registry rows of `corpus/SOURCES.md` at base 9d9cc93e whose recheck is `on-release` and whose source is a committed llama.cpp file; each row re-derived against release b11889 = d854d98b; preregistration `.ufo/waves/round-44/preregistration.json`; machine draft `.ufo/waves/round-44/c1/draft-ledger.tsv` (91 rows: 81 `holds`, 4 `unchanged-file`, 6 `TODO`); landed ledger `registry/release-recheck-b11889.tsv` | read-only on `--repo` and `--upstream` (a blobless clone fetches blobs lazily); writes only the `--out` receipt |
| Round-44 C2 verdict-ledger audit | measurement: `python3 tools/round44-verdict-ledger-audit.py --repo <clone> --tip <full-commit> --fleet <fleet repo> [--out <receipt>]` | 0 met, prints `rows=R valid=V missing=M bad=B agree=a overclaim=o underclaim=u other=x absent=k table_missing=T table_extra=E summary=S axes=X met=True` then one `detail:` line per missing, invalid, table or summary failure; 1 not met, the same line with `met=False` (measured as the pre-ledger base at `098df344`: `rows=0 valid=0 missing=204 ... summary=0 axes=0 met=False`, exit 1; a missing `SCORECARD.md` exits 1 rather than 2, because it is read through a non-checking `git show`); 2 could not evaluate, `could-not-evaluate: <err>` on stderr from an EvalError raised by `git rev-parse` of `--tip`, `git cat-file -e` of the frozen fleet or lane base commit (measured with a non-git `--repo`: exit 2), and equally 2 for the argparse usage error | counter sha256 `1933e75b2a53` (blob at 77d1bbf5); keys are rounds 10-43 x (expansion, quality, discernment) x (self, outside) = 204, self rows read the fleet reports at b0fd7b7f and outside rows the lane spotchecks at 9d9cc93e; preregistration `.ufo/waves/round-44/preregistration.json`; machine draft `.ufo/waves/round-44/c2/draft-ledger.tsv` (204 rows: 105 improved, 62 unchanged, 17 mixed, 15 absent, 3 harmed, 2 unprovable-but-better); landed ledger `registry/verdict-ledger.tsv` | read-only on `--repo` and `--fleet`; writes only the `--out` receipt |
| Round-44 release-recheck ledger drafter | tool (not a counter): `python3 tools/release-recheck.py draft --sources corpus/SOURCES.md --upstream <git clone holding the release commit> --release-name <tag> --release-commit <40-hex> [--repo-url <owner/repo>] [--ids S001,S043]`; `python3 tools/release-recheck.py selftest` | draft: 0 a ledger row written for every population id, `TODO` rows included (91 rows for the round-44 population: 81 `holds`, 4 `unchanged-file`, 6 `TODO`); 2 `--sources` unreadable, `--upstream` not holding `--release-commit`, or a failing `git` call, each with a `release-recheck:` message on stderr (round-44 repair after seat S9Registry measured exit 0 for an unreadable upstream and exit 1 for an absent `--sources`); 2 also for an argparse usage error. selftest: 0 all cases pass, 1 any fails | selftest `selftest pass=5 fail=0` on a fixture repo under `$TMPDIR` (isolation checked before the first commit); extension `python3 tools/release-recheck-selftest-extra.py tools/release-recheck.py` → `additions pass=15 fail=0` (seat M3Tool: the built-in 5 cases kill 4 of 18 mutants, the 15 added cases kill all 14 survivors); tool sha256 `3be68fbd5703` | read-only on `--sources` and `--upstream`; writes the ledger to stdout and the selftest fixture under `$TMPDIR` (removed) |
| Round-44 pin-trigger consumer (KQ58) | check: `python3 tools/pin-trigger-consumed.py --repo <clone> --tip <commit> --receipt <committed pin-watch receipt>` | 0 every `status=behind` engine in the receipt has `registry/release-recheck-<newest>.tsv` at the tip (`ok <engine> newest=<tag> consumer=<path>`, then `met=True`); 1 at least one does not (`missing <engine> newest=<tag>: …`, `met=False`); 2 unreadable receipt (`could-not-evaluate:`) | round-44 tip with `.ufo/waves/round-44/c1/pin-watch-freeze.out` → `ok llama.cpp newest=b11889 consumer=registry/release-recheck-b11889.tsv`, `met=True`; round-43 tip `9307b15e` with the round-42 receipt → `met=False` (seat S9Mistake `a-trigger-check.out`); sha256 `965265915d3e` | read-only |
| Round-44 SCORECARD pointer check (KQ59) | check: `python3 tools/planned-pointer-check.py <SCORECARD.md>` | 0 the first `## Planned` section holds the contiguous pointer sentence and every `§Round-<N> measured results` reference resolves to a heading that starts with it (`met=True`); 1 otherwise (`met=False` with one line per failure) | round-44 working tree `met=True`; `git show 9307b15e:SCORECARD.md` → `met=False` (split pointer, dangling §Round-43 measured results); sha256 `df7cecfcf07b` | read-only |
| Round-44 release-recheck selftest extension | selftest: `python3 tools/release-recheck-selftest-extra.py [tools/release-recheck.py]` | 0 all 15 cases pass; 1 any fails | `additions pass=15 fail=0` on the round-44 tool; each case kills one surviving mutant listed in `.ufo/waves/round-44/w1/out/M3Tool/mutants.tsv`; sha256 `39a62a9857a9` | fixture repos under `$TMPDIR` |

## Round-45 instrument registry (re-verification witnesses, claim-outcome ledger, seat yield)

Rows for the round-45 counters and two checks routed by the round-44 closure (D1, D4). Same columns as `## Local gate/probe registry`. The L1 wrote these rows from each tool's docstring and measured exits; the kama-r45-w1 wave did not run (dispatch stalled), so no seat reviewed them.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-45 C1 re-verification audit | measurement: `python3 tools/round45-recheck-audit.py --repo <clone> --tip <full-commit> [--fetch] [--out <receipt>]` | 0 met, prints `pop=11 rows=R valid=V unverified=U unchanged=a holds=h reworded=w drifted=d removed=r flags_missing=F section=S newrows=N fetch=0/1 fetch_bad=B met=True` then one `detail:` line per invalid key; 1 not met; 2 could not evaluate (bad revision) | base `6b8ccfb3` `unverified=11 met=False`; measured `21945c61` with `--fetch`: `valid=11 unverified=0 unchanged=3 holds=8 newrows=2 fetch_bad=0 met=True`; sha256 `244b6690145d` | read-only on `--repo`; `--fetch` reads raw.githubusercontent.com, the GitHub release API (`gh api`) and `git ls-remote` |
| Round-45 C2 claim-outcome audit (v1, frozen) | measurement: `python3 tools/round45-claim-outcome-audit.py --repo <clone> --tip <full-commit> --fleet <fleet repo> [--out <receipt>]` | 0 met, prints `rows=R valid=V missing=M bad=B agree=a overclaim=o underclaim=u other=x absent=k consistency_bad=C table_missing=T table_extra=E summary=S axes=X met=True`; 1 not met; 2 could not evaluate | base `missing=126 met=False`; measured `21945c61`: `valid=91 bad=35 consistency_bad=1 met=False` (vocabulary and attribution defects, SCORECARD §Round-45 claim-outcome ledger); sha256 `0fb7ad42a009` | read-only on `--repo` and `--fleet` |
| Round-45 C2 claim-outcome audit (v2 amendment) | measurement: `python3 tools/round45-claim-outcome-audit-v2.py --repo <clone> --tip <full-commit> --fleet <fleet repo> [--out <receipt>]` | as v1 | adds the met phrases `verify` and `improved` only; measured `21945c61`: `valid=103 bad=23 consistency_bad=1 met=False`; sha256 `024ba8ec8cb5` | read-only on `--repo` and `--fleet` |
| Seat yield per wave (KQ62; considerthese 2026-10-25 proposal 4) | check: `python3 tools/seat-yield.py <wave dir> [--expect-reports N] [--expect-seats N]`; `python3 tools/seat-yield.py --selftest` | 0 counts printed and every `--expect` matches (`wave=… seats=S status=… reports=R missing=M`); 1 an `--expect` differs (`expect-mismatch: …`); 2 no results JSON or no `out/` | `SEAT_YIELD_SELFTEST pass=6 fail=0`; round-44 w1 `seats=65 reports=65`, `--expect-reports 64` exits 1 (`.ufo/waves/round-45/frontier/seat-yield-r44-d1.out`) | read-only; selftest fixtures under `$TMPDIR` |
| Trend-ledger MANIFEST cross-check (KQ63; round-44 closure D4) | check: `python3 tools/manifest-crosscheck.py <ledger.tsv> <MANIFEST.json>`; `python3 tools/manifest-crosscheck.py --selftest` | 0 `diff=0 no_manifest=0`; 1 any `DIFF` or a non-absent outside row without a MANIFEST verdict; 2 unreadable or malformed input | `MANIFEST_CROSSCHECK_SELFTEST pass=5 fail=0`; `registry/verdict-ledger.tsv` `agree=90 diff=0` exit 0, one-row mutant `diff=1` exit 1 (`.ufo/waves/round-45/frontier/manifest-crosscheck*.out`) | read-only; selftest fixtures under `$TMPDIR` |

## Round-46 instrument registry (freshness re-verification, append-only calibration)

Rows for the round-46 counters and the append-only capability they grade (claim C2; considerthese 2026-10-26 proposal 1). Same columns as `## Local gate/probe registry`. Drafted by seat S9Skill from each tool's docstring and measured exits at lane commit 4a2a4d55 and integrated by the L1; measured values are under SCORECARD §Round-46 measured results.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-46 C1 release re-verification audit (freshness) | measurement: `python3 tools/round46-release-recheck-audit.py --repo <clone> --tip <full-commit> --upstream <llama.cpp clone holding b11906> [--out <receipt>]` | 0 met, prints `pop=P rows=R valid=V unverified=U unchanged=a holds=h reworded=w drifted=d removed=r flags_missing=F section=S newrow=N met=True` then one `detail:` line per unverified row, unflagged drifted/removed row or missing section/new row, and writes the same text to `--out`; grades `registry/release-recheck-b11906.tsv` against the population of `corpus/SOURCES.md` at base 0163fea2 and release b11906 = 4d71b42fd87db24b8b7c808c151b713aa4459cfd, so a `removed` or `drifted` verdict needs both witnesses and a >= 40-char note; 1 not met, the same line with `met=False` (measured at 4a2a4d55 before the ledger: `pop=91 rows=0 valid=0 unverified=91 unchanged=0 holds=0 reworded=0 drifted=0 removed=0 flags_missing=0 section=0 newrow=0 met=False`, exit 1); 2 could not evaluate, `could-not-evaluate: <err>` on stderr from an EvalError raised by `git rev-parse` of `--tip`, `git cat-file -e` of the release or a population pin (measured: an `--upstream` without b11906 prints `could-not-evaluate: git cat-file -e 4d71b42f…`, exit 2) or an unreadable base SOURCES; argparse missing or unrecognized `--repo`/`--tip`/`--upstream` also exits 2, and an uncaught exception leaves exit 1 with no summary | no `--selftest`; `--help` exits 0; sha256 `502e6f57036f`; pre-ledger control `.ufo/waves/round-46/controls/base.c1.out` at tip 0163fea2 reads `pop=91 rows=0 valid=0 unverified=91 unchanged=0 holds=0 reworded=0 drifted=0 removed=0 flags_missing=0 section=0 newrow=0 met=False`, and the same counter at 4a2a4d55 prints that identical summary line over the same 91 ids | read-only on `--repo` and `--upstream`; `--out` writes only the receipt path it is given |
| Round-46 C2 append-only calibration audit | measurement: `python3 tools/round46-append-audit-check.py --repo <clone> --tip <full-commit> [--out <receipt>] [--scratch <dir>]` | 0 met, prints `tip=<full>` then `selftest=0|1 fixture=0|1 lane=0|1 table=0|1 lane_events=E lane_unrestored=U lane_partial=P met=True`, one `detail:` line per failed leg and one `event:` line per lane event, and writes the same text to `--out`; the legs are the graded tool's `--selftest` (n >= 6, fail 0), a random-content fixture repo whose content it cannot know in advance, an independent recomputation of the lane history, and a SCORECARD table line naming `append-only-audit` whose last cell is 46; 1 not met, the same line with `met=False` (measured at 4a2a4d55: `selftest=1 fixture=1 lane=1 table=0 lane_events=5 lane_unrestored=0 lane_partial=2 met=False`, exit 1, only the table leg failing); 2 could not evaluate, `could-not-evaluate: <err>` on stderr from an EvalError raised by `git rev-parse` of `--tip` (measured: `--tip deadbeefdeadbeef` exits 2); argparse missing or unrecognized `--repo`/`--tip` also exits 2, and an uncaught exception leaves exit 1 with no summary | no `--selftest` of its own, it runs the graded tool's (measured `AOA_SELFTEST pass=10 fail=0`, exit 0); `--help` exits 0; sha256 `4dcfbe1063d6`; pre-tool control `.ufo/waves/round-46/controls/base.c2.out` at tip 0163fea2 reads `selftest=0 fixture=0 lane=0 table=0 lane_events=5 lane_unrestored=0 lane_partial=2 met=False`, listing `dd9f5dc6` SCORECARD 24/31 partial and `0718b6ab` SCORECARD 2416/2417 partial; fixture bytes are random per run, so only the event counts are pinned | read-only on `--repo`; fixture repos under `--scratch` or `$TMPDIR`, removed on exit; `--out` writes only the receipt path it is given |
| Round-46 append-only self-description audit (claim C2 capability) | tool + selftest: `python3 tools/append-only-audit.py --repo <dir> [--to <rev>] [--threshold <n>] [--files <a,b,...>] [--json]`; `python3 tools/append-only-audit.py --selftest [--scratch <dir>]` | 0 no event partial or unrestored, text lines `event <commit12> <file> deleted=N restored_at_tip=K status=S restored_by=<commit12 or ->` then `summary commits=C events=E restored=R partial=P unrestored=U`, and `--json` prints `to`, `threshold`, `files`, `commits`, `events` and `summary` with full commit ids; 1 at least one event partial or unrestored (measured on this lane at 4a2a4d55: 294 commits, 5 events, 3 restored, 2 partial, 0 unrestored, exit 1); 2 could not evaluate, `could-not-evaluate: <err>` on stderr for `--threshold` below 1 or a `--repo` git cannot read, both measured at exit 2 | `AOA_SELFTEST pass=10 fail=0` measured, exit 0, over no-deletion, below-threshold, exact-threshold-unrestored, restored-later, partial, undeclared-file, declared-file-removed, to-earlier-rev, merge-first-parent and threshold-flag; `--help` exits 0; sha256 `793dab9ffe0c`; the event definition is pinned by `.ufo/waves/round-46/preregistration.json`: commits in `git rev-list --topo-order --reverse`, diff against the first parent, `-` lines minus the header, >= 20 deleted lines per (commit, file), the five declared files only; `tools/sources-append-only.py` is the round-18 predecessor and does not compute `restored_by` | read-only on `--repo`; selftest fixtures under `--scratch` or `$TMPDIR`, removed on exit |

## Round-47 instrument registry (append-only v2 calibration, live receipt replay)

Rows for the round-47 counters and the instruments they grade (claims C1 and C2). Same columns as `## Local gate/probe registry`. Drafted by seat S9Skill from each tool's docstring; the selftest values were measured at lane commit 3a09a1d9, the C2 counter values are the L1 pre-wave dry run at that commit (this seat did not run the network legs). The two tool rows were re-pinned by the L1 after the wave's hardening fixes (lesson §Wave).

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-47 C1 append-only v2 calibration audit | measurement: `python3 tools/round47-append-audit-v2-check.py --repo <clone> --tip <full-commit> [--base <commit>] [--scratch <dir>] [--out <receipt>]` | 0 met, prints one line `selftest=0|1 contract=0|1 lane=0|1 fixture=0|1 stable=0|1 files=F lane_events=E lane_mismatch=M fixture_mismatch=X met=True`, a second line `tip=<full> base=<full>`, one `detail:` line per failed leg, and writes the same text to `--out`; the legs are the graded tool's `--selftest` (n >= 10, fail 0), the contract `registry/append-only-contract.tsv` at the tip (exact header, four cells per row, a known rule, a `declared_at` path and line whose text contains `append`, an expansion holding SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md and at least one lesson file), the tool's lane run against this counter's own recomputation (numstat deletions >= 20, byte-exact deleted multiset, window-maximised `held`), a constructed random-content fixture repo under `--scratch`, and a base/tip stability leg (`--base` defaults to the frozen round-47 base); 1 not met, the same lines with `met=False` (measured at 3a09a1d9: `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True`, exit 0); 2 could not evaluate, prints `could-not-evaluate: <reason>` and writes no `--out` (git failure on `--repo`, unreadable `--tip`) | selftest leg: the tool at `--tip` run with `--selftest --scratch <dir>` exits 0 and prints `AOA_SELFTEST pass=n fail=m` with n >= 10 and m = 0 (measured at 3a09a1d9: `AOA_SELFTEST pass=15 fail=0`); the graded tool's source at `--tip` must not contain the string `round47`, so it cannot load the counter's recomputation; no network | read-only on `--repo`; creates `--scratch` (default `$TMPDIR`) and its fixture repos there, removed on exit; writes `--out` only when it could evaluate |
| Round-47 C2 live-replay operability audit | measurement: `python3 tools/round47-live-replay-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `receipts=0|1 replay=0|1 tamper=0|1 newrow=0|1 rerun_checks=N met=True`, then `tip=<full> started=<iso>`, then one `detail:` line per failed leg, and writes the same text to `--out`; the legs are the three committed receipts `.ufo/waves/round-47/c2/live/receipt-1.json`, and `receipt-2.json` and `receipt-3.json` beside it (schema kama-llamacpp-live/v4, outcome pass, >= 10 evaluated checks all passed, provenance equal to the frozen b11909 asset and digest, build_info starting `b11909-`, `teardown.log_path` null or a committed repo-relative path), a fresh-home replay from `git archive <tip>` of receipt-1 whose rerun receipt this counter re-checks itself (started at or after the counter, server and model sha256 equal to receipt-1, inputs re-acquired under `--scratch`, identical values for every check receipt-1 evaluated), the tamper leg (two copies with the first hex digit of a recorded digest flipped must exit nonzero and leave no passing rerun), and the b11909 registry row in `corpus/SOURCES.md`; 1 not met, the same lines with `met=False` (L1 pre-wave dry run at 3a09a1d9: `receipts=1 replay=1 tamper=1 newrow=0 rerun_checks=11 met=False`, exit 1, because the SOURCES row lands at integration); 2 could not evaluate, `could-not-evaluate: <reason>`, no `--out` (git failure, unreadable `--tip`) | replay leg: runs `python3 tools/kama-live-replay.py --receipt R --work DIR --out J` from the extracted tree with HOME, XDG_CACHE_HOME and TMPDIR inside `--scratch`; needs https to github.com and huggingface.co (release archive about 23 MB and model about 1.2 MB per attempt, three attempts) and a host that can exec the release `llama-server`; 20-minute subprocess timeout per replay; 11 rerun check ids pinned on receipt-1 | read-only on `--repo`; extracts `git archive <tip>` and every download under `--scratch`, removed on exit; writes `--out` only when it could evaluate |
| Round-47 live receipt replay | tool + selftest: `python3 tools/kama-live-replay.py --receipt <v4-receipt> --work <dir> --out <json> [--live <tool>] [--timeout <s>]`; `python3 tools/kama-live-replay.py --selftest --scratch <dir>` | 0 the rerun matches: every check the original evaluated is evaluated again with the same `passed` value and the server and model sha256 are equal, prints `replay match=True refused=None mismatches=0 exit=0` and writes `{"schema": "kama-live-replay/v1", "receipt", "work", "rerun_receipt", "match", "refused", "mismatches", "inputs"}`; 1 it ran and differs (`match=False`, `mismatches` names the divergent check ids); 2 refused or could not run, `refused` carries the reason (`not-a-v4-receipt:<schema>`, `provenance-missing:<keys>`, `provenance-bad-digest:<key>`, `provenance-model-digest-differs-from-receipt-model`, `unsafe-member:<member>`, `url-scheme:<url>`, `digest-mismatch:<file>:want=<hex>:got=<hex>`, `member-absent:<member>`, `receipt-not-an-object`, `no-rerun-receipt:exit=<n>:<tail>`) | `--selftest` prints one `pass <case>` or `FAIL <case>: <why>` line per case, then `KLR_SELFTEST pass=13 fail=0`, and exits 0 only when fail = 0 (measured at 3a09a1d9: pass=10 exit 0; after the round-47 wave hardening, a no-evaluated-check original and a nonzero live-tool exit are mismatches, and the archive member is checked against `server.sha256` before it runs: pass=13); the cases pin a matching rerun, a divergent check, a wrong model digest, a wrong asset digest, a provenance/receipt model-digest mismatch, a v3 receipt, a missing url, an unsafe member, an absent archive member and an http url | writes only `--work` and the `--out` JSON; https only (the selftest uses `file://` fixtures), `--live` defaults to the live tool beside it; `--scratch` must already exist, a missing dir raises FileNotFoundError (exit 1) instead of the documented 2 |
| Round-47 append-only audit v2 | tool + selftest: `python3 tools/append-only-audit.py --repo <dir> [--to <rev>] [--contract <tsv> | --files <a,b,...>] [--threshold <n>] [--json]`; `python3 tools/append-only-audit.py --selftest [--scratch <dir>]` | 0 no event partial or unrestored; text lines `event <commit12> <file> deleted=N restored_max=K status=S restored_best=<c12|-> restored_by=<c12|->` then `summary commits=C files=F events=E restored=R partial=P unrestored=U`; `--json` prints `{"schema": "append-only-audit/v2", "to", "threshold", "contract", "files", "commits", "events", "summary"}` with full commit ids, `restored_max` and `restored_best` replacing v1's tip-only `restored_at_tip`, and deleted counts read from the -U0 hunk headers byte-exactly (a deleted line starting `--` counts) and equal to `git diff --numstat`; 1 at least one event partial or unrestored (measured on this lane at 3a09a1d9: 85 files, 5 events, exit 1); 2 could not evaluate, prints `could-not-evaluate: <reason>` on stderr (`--threshold` < 1, a malformed contract header or row, an unknown rule, an empty contract, a hunk count that disagrees with numstat, an unreadable `--contract` file, git failure) | `--selftest` prints one `pass <case>` or `FAIL <case>: <why>` line per case, then `AOA_SELFTEST pass=19 fail=0`, and exits 0 only when fail = 0 (measured at 3a09a1d9: pass=15; after the round-47 wave hardening, pass=19: a CRLF line restored byte-exact, a kept duplicate copy, the final-segment rule, and vanished/non-ASCII/unmatched/binary paths); the cases pin a `--`-prefixed deleted block, CRLF lines and a final line without a newline, multiset counting, the window maximum, a relocated block, a removed declared file, a merge first parent, the contract header and the threshold flag | read-only on `--repo`; the contract defaults to the one at `--to`; selftest fixtures under `--scratch` (must already exist, default `$TMPDIR`), removed on exit |
| Round-47 live lifecycle receipt v4 | capability: `python3 tools/kama-llamacpp-live.py --model <gguf> --model-sha256 <hex> [--server <llama-server>] [--alias <id>] [--ctx <n>] [--threads <n>] [--port <n>] [--probe <sh>] [--ready-timeout <s>] [--server-asset-url <url> --server-asset-sha256 <hex> --server-member <path> --model-url <url>] [--out <json>]`; `python3 tools/kama-llamacpp-live.py --selftest` | 0 outcome pass (every evaluated check passed); 1 outcome fail (at least one evaluated check failed); 2 outcome not-evaluated or setup error (a `--model-sha256` mismatch, no server binary, an internal fault); receipt `{"schema": "kama-llamacpp-live/v4", "outcome", "checks": [{"id", "passed", "evaluated"}], "server": {"sha256", "realpath", ...}, "model": {"sha256", "path", ...}, "captures", "teardown": {"log_path": null, "log_lines", ...}, "provenance": {"server": {"asset_url", "asset_sha256", "member"}, "model": {"url", "sha256"}}}`; v4 adds the `provenance` block the replay tool re-acquires from and `teardown.log_path` always null (the temp log is deleted, its kept lines inlined), and a missing loading-503 observation is not-evaluated, never a server failure | `--selftest` runs the parser, install-identity, atomic-publish and hostile-handler cases and closed tcp6 listeners without a server, prints `selftest: ok; closed tcp6 listeners <addr>, <addr>` and exits 0 (measured at 3a09a1d9); receipt-1 at 3a09a1d9 records 11 checks, all evaluated and all passed, `captures.props.fields.build_info` = `b11909-caa8191df`, and `provenance.server.member` = `llama-b11909/llama-server` | writes only the `--out` receipt (stdout by default) and a temp log it deletes; binds a loopback port picked by the OS that is never a registered consumer port (8080, 34113 and the `registry/endpoint-consumers.tsv` pins); the child environment is an allowlist whose names are recorded and values never are |

### Re-running live evidence

- Start from a v4 receipt and an empty work dir: the replay tool reads only the `provenance` block, so a receipt without one, or with a digest that does not match what it downloads, is refused with exit 2 before anything is extracted or executed.
- `python3 tools/kama-live-replay.py --receipt .ufo/waves/round-47/c2/live/receipt-1.json --work <empty-dir> --out <json>` re-acquires the release archive and the model into `--work`, verifies both sha256, runs the lifecycle with the receipt's alias, ctx and threads, and writes the `kama-live-replay/v1` JSON.
- Exit 0 means the rerun reproduced every check the original evaluated; 1 means it ran and a check differs (`mismatches` names them); 2 means refused or unable to run.
- It needs https to github.com and huggingface.co (about 24 MB) and a host that can exec the release `llama-server`; for an offline check run `python3 tools/kama-live-replay.py --selftest --scratch <existing-dir>` and expect `KLR_SELFTEST pass=13 fail=0`.
- The graded form is `python3 tools/round47-live-replay-audit.py --repo <clone> --tip <full-commit> --scratch <dir> [--out <receipt>]`: it replays from `git archive <tip>` under a scratch HOME and also refuses two receipts whose recorded digests were flipped.
- A receipt whose log file is gone still replays: `teardown.log_path` is null by design and the kept log lines are inlined in the receipt.

## Round-48 instrument registry (append-only v3 regions, live receipts v5)

Rows for the round-48 counters and the instruments they grade (claims C1 and C2). Same columns as `## Local gate/probe registry`. Written by the L1 from each tool's docstring; selftest values measured at lane commit `380bcdff` (the build).

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-48 C1 append-only v3 calibration audit | measurement: `python3 tools/round48-append-audit-v3-check.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `selftest=0\|1 contract=0\|1 lane=0\|1 fixture=0\|1 stable=0\|1 rows=R files=F lane_events=E lane_failures=N ungraded_lines=U fixture_fail=X met=True`, then `tip=<full>`, one `detail:` line per failed leg, and the same text to `--out`; legs: the tool's `--selftest` (n >= 20, fail 0), the v3 contract at the tip (5 cells, the nine required rows and regions, every declaration and region pointer bound), the tool's lane JSON equal to the counter's own recomputation with a clean derived verdict (no partial/unrestored, regressed 0, vanished 0, unbound 0, ungraded > 0), eleven fixtures with expectations written by construction, stability from base `33e00582`; 1 not met; 2 could not evaluate | frozen at `12284ba3` (sha256 `92b0f9f1…2ac7`); controls `.ufo/waves/round-48/controls/*.c1.out` all `met=False` | `--scratch` (fixtures, removed on exit) and `--out` only; read-only on `--repo` |
| Round-48 C2 live receipts v5 operability audit | measurement: `python3 tools/round48-live-replay-v5-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `receipts=0\|1 recordcheck=0\|1 replay=0\|1 compare=0\|1 tamper=0\|1 urlswap=0\|1 newrow=0\|1 replayed=N/3 met=True`, then `tip=<full> started=<iso>`, one `detail:` line per failed leg, and the same text to `--out`; legs: three v5 receipts `.ufo/waves/round-48/c2/live/receipt-1.json` … `-3.json` with the frozen asset, pinned model and a record-time `provenance.verified`; the live tool refusing five bad provenance sets before executing a stub server (plus a positive control); each receipt replayed from `git archive <tip>` under a scratch HOME with the re-acquired files hashed by the counter and an equal stable projection; `--compare` ignoring instance fields and catching five stable changes; two digest tampers and two URL swaps refused; a SOURCES row naming the pinned URL; 1 not met; 2 could not evaluate | frozen at `12284ba3` (sha256 `6bc16e25…0c09`); needs https to github.com and huggingface.co (~75 MB); controls `.ufo/waves/round-48/controls/*.c2.out` all `met=False` | `--scratch` (archive tree, downloads, reruns; removed on exit) and `--out` only |
| Round-48 append-only audit v3 | tool + selftest: `python3 tools/append-only-audit.py --repo <dir> [--to <rev>] [--contract <tsv> \| --files <a,b,...>] [--threshold <n>] [--json]`; `python3 tools/append-only-audit.py --selftest [--scratch <dir>]` | 0 no event partial or unrestored, none regressed, no vanished declared path, every declaration bound; 1 otherwise; 2 could not evaluate (malformed or CRLF contract, a region cell that is not `*`, `exempt=<## T>\|…@<path>:<line>` or `only=<## P>@<path>:<line>`); text lines `event <c12> <file> deleted=N graded=G ungraded=U restored_max=K held_at_to=H status=S restored_best=… restored_by=…`, `declaration … unbound: …`, then `summary …`; `--json` schema `append-only-audit/v3` with `declarations`; lines before the first `## ` heading have no section and are always graded | `AOA_SELFTEST pass=28 fail=0` (case `preamble-graded` added at integration, seat X1SelftestPower); lane: 10 contract rows, 90 files, 5 events all restored, ungraded_lines 89, regressed 0, exit 0 | read-only on `--repo`; selftest fixtures under `--scratch` or `$TMPDIR`, removed on exit |
| Round-48 live lifecycle receipt v5 | capability: `python3 tools/kama-llamacpp-live.py --model <gguf> --model-sha256 <hex> [--server <llama-server>] [--alias <id>] [--ctx <n>] [--threads <n>] [--server-asset-url <https-url> --server-asset-sha256 <hex> --server-member <path> --model-url <https-url> [--server-archive <tar.gz>]] [--out <json>]`; `python3 tools/kama-llamacpp-live.py --selftest` | as v4 (0 pass, 1 fail, 2 not-evaluated or setup error); the four provenance flags must come together with https URLs and a safe member (argparse exit 2); `--server-archive` selects v5: the model URL must be pinned to `/resolve/<40-hex>/`, and before the server starts the archive must hash to the asset sha256 and its member to the server binary (setup-error tokens `provenance-archive-digest-mismatch`, `provenance-member-absent`, `provenance-member-not-a-file`, `provenance-member-digest-mismatch`); v5 adds `provenance.model.commit` and `provenance.verified`; record time never fetches the URLs (seat K2Record) | `selftest: ok` (includes `_provenance_selftest`); receipts `.ufo/waves/round-48/c2/live/receipt-1.json` … `-3.json` all v5 pass 11/11; `tests/llamacpp-live/check-receipt.py --require-schema v5` and `tools/gguf-identity.py --receipt` read them (seat K0Harm F2/F3) | `--out` and a temp log it deletes; starts one loopback llama-server it tears down |
| Round-48 live receipt replay and compare | tool + selftest: `python3 tools/kama-live-replay.py --receipt <v4-or-v5-receipt> --work <dir> --out <json> [--live <tool>] [--timeout <s>]`; `python3 tools/kama-live-replay.py --compare <a.json> <b.json>`; `python3 tools/kama-live-replay.py --selftest --scratch <dir>` | replay: 0 the rerun matches (same schema and outcome, equal server/model sha256, every evaluated check equal, for v5 the same commit and verified digests, equal stable projection: props fields, slots count and body digest, health status and body digest, models ids/owned_by, metrics status, loading envelope, teardown outcome, listener ownership), 1 ran and differs, 2 refused (v5 also: `provenance-bad-commit`, `provenance-url-revision-differs-from-commit`, `provenance-not-verified-at-record`, `provenance-verified-<key>-differs`; any non-https URL; a malformed receipt); `--compare`: validates both receipts' provenance, prints `compare match=<bool> mismatches=N`, exit 0 equal, 1 different, 2 unreadable or refused; `--timeout` bounds the live child only | `KLR_SELFTEST pass=22 fail=0` | `--work` and `--out` (replay); nothing (`--compare`) |
| Round-48 shortcut tally | tool + selftest: `python3 tools/shortcut-tally.py [--repo <dir>] [--rev <rev>] [--rounds <a-b>] [--check <n>] [--json]`; `python3 tools/shortcut-tally.py --selftest [--scratch <dir>]` | 0 every round readable (and, with `--check N`, the latest round's shortcut count <= N); 1 a round unreadable or the count above N; prints one row per round (shortcut controls or seat-built cheats that met a frozen counter, mutants survived/total, whether a falsify wave ran) and `detail:` lines with their sources | `selftest pass=7 fail=0`; considerthese/2026-10-26.md proposal 3, promoted from `.ufo/waves/round-47/w1/out/X9Tally/` by seat X9Tally | read-only on `--repo`; selftest fixtures under `--scratch` |
| Round-48 SOURCES append-only guard repair | gate: `python3 tools/sources-append-only.py --from A --to B [--json]` (row of `## Local gate/probe registry` unchanged) | as before; a table outside `## Registry` is refused only when it carries the registry header or an eleven-cell `S0NN` row (round-47 closure D8: every transition since round 45 exited 2 on the round-45 re-verification table) | `45/45 selftest cases passed`; `--from 33e00582 --to 380bcdff` → `added S492 (allowed)`, `added S493 (allowed)`, exit 0 (seat X9SourcesGuard) | read-only |

### Re-running live evidence (v5, round 48)

- Record: download the release archive and the model from a revision-pinned URL first, then `python3 tools/kama-llamacpp-live.py --server <extracted llama-server> --model <gguf> --model-sha256 <hex> --server-asset-url <asset-url> --server-asset-sha256 <hex> --server-member <path-in-archive> --model-url https://huggingface.co/<org>/<repo>/resolve/<40-hex-commit>/<path> --server-archive <archive> --out <receipt>`; the archive and member are checked before the server starts.
- Replay: `python3 tools/kama-live-replay.py --receipt .ufo/waves/round-48/c2/live/receipt-1.json --work <empty-dir> --out <json>`; a v5 receipt is replayed with `--server-archive` so the rerun is verified at record time too, and the rerun must match the stable projection, not only the checks.
- Compare two receipts offline: `python3 tools/kama-live-replay.py --compare <a> <b>` (ports, pids, times, log text and the models `created` field are ignored).
- Graded form: `python3 tools/round48-live-replay-v5-audit.py --repo <clone> --tip <full-commit> --scratch <dir>`.

## Round-49 instrument registry (replay execution witness, append-only v4 definitions)

Rows for the round-49 counters and the instruments they change (claims C1 operability and C2 calibration). Same columns as `## Local gate/probe registry`. Drafted by seat S9Skill from each tool's docstring and its own measured exits at the build commit `74558c71` on a `git clone --shared` of the lane at that commit (both counters and all three tool selftests were run there; the two counter rows carry the values this seat measured, not the L1 dry run's). The C1 network legs run in about 13 s on this host.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-49 C1 replay-witness audit | measurement: `python3 tools/round49-replay-witness-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full>` then `witness=0\|1 cap=0\|1 newrow=0\|1 witnessed=N/3 met=True`, one `detail:` line per witness, cap and newrow leg, and writes the same text to `--out`; the witness leg replays each of `.ufo/waves/round-48/c2/live/receipt-1.json` … `receipt-3.json` at the tip (tool from `git archive`) with `--witness-dir` under a scratch HOME and, while the replay holds, checks from outside: sha256 of `/proc/<pid>/exe` equals the frozen b11909 `llama-server` digest `35ac50fb…d8d7ff0`, a LISTEN socket on the announced port whose inode is one of `/proc/<pid>/fd`, the `-m` argument of `/proc/<pid>/cmdline` hashing to the frozen model `270cba1b…d3bd256d`, and a fresh nonce `kama witness <16 hex>` round-tripped through POST /tokenize `with_pieces` and POST /detokenize with every returned piece equal to the counter's own GGUF vocab decoding; then it writes `release` and requires replay exit 0 with match true, `witness.released` true, the pid gone and the port refusing; the cap leg needs a 1-byte-member archive whose PAX header declares a 10^15-byte sparse member to exit 2 within 30 s with setup_error starting `provenance-member` and never execute the stub, with the stub's own bytes passing verification and running as the positive control; the newrow leg needs a `corpus/SOURCES.md` row absent at base `438127bc` naming the server README at commit `caa8191d` and `/tokenize`; 1 not met, the same first two-column lines with `met=False`; 2 could not evaluate, `could-not-evaluate: <err>` printed on stdout when `git rev-parse --verify <tip>^{commit}` or `git archive` fails | measured at `74558c71`: exit 0, `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, `counter vocabulary: 512 tokens`, three witnesses `exe+listen+model ok` each with its own nonce round-trip, `cap sparse-1e15: exit 2 setup_error 'provenance-member-sparse' executed=False`, control `executed=True`, `newrow: 2 rows new since base; 1 name the README … ['\| S494 \|']`; pins `.ufo/waves/round-49/preregistration.json` and the frozen digests in the tool header | read-only on `--repo`; everything else under `--scratch` and removed on exit; needs https to github.com (~75 MB per replay) and huggingface.co (~1 MB), Linux `/proc`, and the three loopback `llama-server` children it starts and tears down |
| Round-49 C2 append-audit v4 check | measurement: `python3 tools/round49-append-audit-v4-check.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full>` then `fixture=0\|1 lane=0\|1 scenarios=N/8 met=True`, one `detail:` line per scenario and per lane leg, and writes the same text to `--out`; the eight constructed fixture repos under `--scratch` are launder (dated text moved under the exempt `## Axes`, then dropped there while the head regrows: `deleted=25 graded=25 ungraded=0 status=unrestored`, exit 1), native-head (`ungraded=25 graded=0 status=ungraded`, exit 0), dated-loss (`graded=25 unrestored`, exit 1), substring / negated / wildcard-self (`bad_declarations 1`, exit 1) and word-token / wildcard-named (`bad_declarations 0`, exit 0); the lane leg runs `tools/append-only-audit.py` from `git archive <tip>` on `--repo` with the contract at the tip (exit 0, bad_declarations 0, at least 5 events), binds every contract row with its own v4 binder, and bounds each event's `ungraded` by its own count of deleted lines that are both in an exempt section and born there; 1 not met; 2 could not evaluate, `could-not-evaluate: <err>` on stdout from a failing git call | measured at `74558c71`: exit 0, `fixture=1 lane=1 scenarios=8/8 met=True` in 4.4 s, `lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 82`, events `dd9f5dc6c0e6` 17 <= 23 and `0718b6abbda6` 65 <= 65; pins `registry/append-only-contract.tsv` at the tip | read-only on `--repo`; fixture repos and the extracted tip tree under `--scratch`, removed on exit |
| Round-49 append-only audit v4 | tool + selftest: `python3 tools/append-only-audit.py --repo <dir> [--to <rev>] [--contract <tsv> \| --files <a,b,...>] [--threshold <n>] [--json]`; `python3 tools/append-only-audit.py --selftest [--scratch <dir>]` | as v3 (0 no event partial or unrestored, none regressed, no vanished declared path, every declaration bound; 1 otherwise; 2 could not evaluate); `--json` keeps `"schema": "append-only-audit/v3"` and adds `"definition": "v4"`; three v4 rules: a deleted line is `ungraded` only when its parent section is an eligible exempt title **and** `origin(l)` — the `## ` titles holding its text at the text's first appearance in `git rev-list --topo-order --reverse <to>` order — contains one of the file's exempt titles; the row token binds as a whole word, not preceded or followed by `[a-z0-9_]` (`log` inside `catalog` no longer binds); a negation (not, never, no, nor, neither, non, isn't, aren't, `no longer`) within three words before `append-only`/`append only` unbinds, and a wildcard row is no longer bound by a covered file's own self-declaration, while a non-wildcard path row still is | `AOA_SELFTEST pass=30 fail=0` at `74558c71` (the round-49 cases are `launder-through-head` and `binding-v4`; the round-48 tool at `438127bc` printed `pass=28 fail=0`); on the lane at `74558c71` the v4 tool grades 7 more lines of the `0718b6ab` SCORECARD event (ungraded 72 -> 65) and exits 0, `ungraded_lines` 89 -> 82 overall, both measured here with the same contract at `registry/append-only-contract.tsv`; routed by round-48 seats K1Regions and K1Binding | read-only on `--repo`; text or `--json` to stdout; selftest fixtures under `--scratch` |
| Round-49 live lifecycle receipt v5 (bounded archive, witness hold) | capability: `python3 tools/kama-llamacpp-live.py --model <gguf> --model-sha256 <hex> [--server <llama-server>] [--ctx <n>] [--threads <n>] [--server-asset-url <https-url> --server-asset-sha256 <hex> --server-member <path> --model-url <https-url> --server-archive <tar.gz>] [--witness-dir <existing-dir> --witness-timeout <s>] [--out <json>]`; `python3 tools/kama-llamacpp-live.py --selftest` | as v5 (0 pass, 1 fail, 2 not-evaluated or setup error; receipt schema unchanged `kama-llamacpp-live/v5`); `--server-archive` verification is now bounded — the archive must be a regular file of at most 1 GiB read once, its index walked streaming with at most 4096 entries, and the member a regular non-sparse file whose declared size equals the `--server` file's size, all before a byte of the member is hashed, with new setup-error tokens `provenance-archive-not-regular`, `provenance-archive-too-large`, `provenance-archive-too-many-members`, `provenance-member-sparse`, `provenance-member-size-mismatch`; `--witness-dir` must be an existing directory and `--witness-timeout` must be > 0 (argparse exit 2), and with them the receipt gains `witness` {schema `kama-live-witness/v1`, dir, port, pid, released, waited_ms} | `python3 tools/kama-llamacpp-live.py --selftest` at `74558c71` prints `selftest: ok; closed tcp6 listeners <host:port pairs>` and exits 0; the provenance selftest now also refuses a sparse 10^15 member, a member size mismatch and a non-regular archive path; the witness hold writes `ready.json` atomically and re-runs `verify_live` as `post-witness`, refreshing `port_listener_ownership`; driven 3/3 by the round-49 C1 counter | read-only on the model and server binaries; writes the receipt; selftest fixtures under `$TMPDIR`; with `--witness-dir` writes `ready.json` and reads `release` in that directory; starts and stops one loopback `llama-server` |
| Round-49 witnessed live receipt replay | tool + selftest: `python3 tools/kama-live-replay.py --receipt <v4-or-v5-receipt> --work <dir> --out <json> [--witness-dir <existing-dir>] [--witness-timeout <s>] [--live <tool>] [--timeout <s>]`; `python3 tools/kama-live-replay.py --compare <a.json> <b.json>`; `python3 tools/kama-live-replay.py --selftest --scratch <dir>` | as round 48 (0 the rerun matches, 1 ran and differs, 2 refused or could not run); with `--witness-dir` the live child also gets `--witness-dir`/`--witness-timeout`, the child bound grows by the witness timeout, and the result JSON gains `witness_dir`; a witnessed replay matches exactly as an unwitnessed one — the witness block is not compared; a `--witness-dir` that is not an existing directory is an argparse error (exit 2) | `KLR_SELFTEST pass=22 fail=0` at `74558c71`; the round-49 C1 counter drove it on three v5 receipts (`witnessed=3/3`, replay exit 0 with match true) | read-only on `--receipt` and the lane; downloads and the rerun tree under `--work`; writes `--out`; starts and stops one loopback `llama-server` per replay |

### Re-running live evidence (witnessed replay, round 49)

- A witnessed replay is the only replay form that shows a server ran: `python3 tools/kama-live-replay.py --receipt .ufo/waves/round-48/c2/live/receipt-1.json --work <empty-dir> --out <json> --witness-dir <existing-empty-dir> --witness-timeout 120`. While it holds, `<dir>/ready.json` names the port and the pid of the `llama-server` child; `touch <dir>/release` lets the replay finish its teardown.
- The observer's checks are all outside the replay: `sha256sum /proc/<pid>/exe` against the recorded server digest, the LISTEN socket inode in `/proc/net/tcp` and `/proc/net/tcp6` against `/proc/<pid>/fd`, the `-m` argument in `/proc/<pid>/cmdline` against the model digest, and a nonce of your own through POST /tokenize with `with_pieces` plus POST /detokenize, comparing every piece with your own GGUF vocabulary. The rerun receipt's `witness.released` records only what the tool itself saw.
- The witness changes nothing about matching: exit 0 means the rerun reproduced every check the original evaluated, exactly as for an unwitnessed replay; the `witness` block is excluded from the comparison.
- Graded form: `python3 tools/round49-replay-witness-audit.py --repo <clone> --tip <full-commit> --scratch <dir>` — needs https to github.com and huggingface.co (about 75 MB per replay), Linux `/proc`, and roughly 13 s on this host.
- Record-time bounds: `tools/kama-llamacpp-live.py --server-archive` refuses a non-regular, over-1-GiB, over-4096-entry, sparse or wrongly sized archive member before hashing it, so an untrusted archive can no longer make record time read an unbounded number of bytes; the setup-error token names which bound was hit.

## Round-50 instrument registry (process-bound replay witness, append-only v5 definitions)

Rows for the round-50 counters and the instruments they change (claims C1 operability and C2 calibration). Same columns as `## Local gate/probe registry`. Drafted from each tool's docstring and its own measured exits at the build commit `97c864be` on a `git clone --shared` of the lane at that commit. The C1 network legs run in ~15-46 s on this host.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-50 C1 replay-bind audit | measurement: `python3 tools/round50-replay-bind-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full>` then `bind=0\|1 teardown=0\|1 newrow=0\|1 bound=N/3 met=True`, one `detail:` line per witness, teardown and newrow leg, and writes the same text to `--out`; the counter starts each of `.ufo/waves/round-48/c2/live/receipt-1.json` … `receipt-3.json` at the tip (tools from `git archive`) under `python3 -I -c` invokers with planted canaries (KAMA_R50_CANARY environment and a PYTHONPATH sitecustomize that stamps a marker file) and, while the replay holds, checks from outside: sha256 of `/proc/<pid>/exe` equals the frozen b11909 `llama-server` digest `35ac50fb…d8d7ff0`, a LISTEN socket on the announced port whose inode is one of `/proc/<pid>/fd`, a fresh nonce round-trip through POST /tokenize (with_pieces) and /detokenize against the counter's own GGUF vocabulary, the pid descending from the replay process (ppid walk), neither the server nor its parent's environ carrying the canary with the marker file empty, `/proc/<pid>/maps` holding a file-backed mapping whose pathname stat()s to the same dev and inode and hashes to the frozen model digest `270cba1b…3bd256d`, the rerun receipt's `child_pid` equal to the observed pid with `model_mapping` recording that same dev/inode/sha256, and after release the pid gone and the port refusing; the teardown leg starts one more replay of receipt-1, snapshots every descendant of the invoker, SIGKILLs the invoker and requires all descendants gone and the port refusing within 30 s. | 1 any leg 0 at the measured commit, or met=True on any control | 0 met, prints `bind=1 teardown=1 newrow=1 bound=3/3 met=True`; base `bind=0 teardown=0 newrow=0 bound=0/3 met=False` (controls `.ufo/waves/round-50/controls/base.c1.out`) | read-only on --repo; everything else under --scratch, removed on exit; needs https (github.com, huggingface.co), Linux /proc |
| Round-50 C2 append-audit v5 check | measurement: `python3 tools/round50-append-audit-v5-check.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full>` then `fixture=0\|1 lane=0\|1 scenarios=N/12 met=True`, one `detail:` line per scenario and per lane leg, and writes the same text to `--out`; the twelve constructed fixture repos under `--scratch` are the round-49 eight (launder, native-head, dated-loss, substring, word-token, negated, wildcard-self, wildcard-named) plus order-a/order-b (the same merged trees with parents swapped; the twin line born under `## Axes` on one branch and `## Round 1` on the other must be ungraded in both), fence (a fenced fake `## Axes` must not hide a dated loss: graded, exit 1) and crlf-launder (dated LF text moved under the head as CRLF and dropped there must be graded, exit 1); every fixture also requires graded + ungraded == deleted on every event; the lane leg runs the tool at the tip, requires exit 0, bad_declarations 0, >= 5 events, asserts the counter's own v4 binder binds every contract row, checks per event graded + ungraded == deleted, deleted equals `git diff --numstat`'s deletion count, and ungraded <= the counter's own v5 native count (fence-aware sections, CRLF-normalized keys, birth-DAG origin). | 1 any leg 0 at the measured commit, or met=True on any control | 0 met, prints `fixture=1 lane=1 scenarios=12/12 met=True`; base `fixture=0 lane=1 scenarios=9/12 met=False` (controls `.ufo/waves/round-50/controls/base.c2.out`) | read-only on --repo; fixtures and tip tree under --scratch, removed on exit |
| Round-50 append-only audit v5 | tool + selftest: `python3 tools/append-only-audit.py --repo <dir> [--to <rev>] [--contract <tsv> | --files <a,b,...>] [--threshold <n>] [--json]`; `python3 tools/append-only-audit.py --selftest [--scratch <dir>]` | as v4 (0 no event partial or unrestored, none regressed, no vanished declared path, every declaration bound; 1 otherwise; 2 could not evaluate); `--json` keeps `"schema": "append-only-audit/v3"` and adds `"definition": "v5"`; three v5 definition changes: `origin(l)` is the union of the `## ` titles holding the line's key (with one trailing carriage return removed) at every birth of the key — a commit whose blob of the file holds the key while no parent's blob does — so it is a property of the commit graph, not of `git rev-list` order; `sections()` ignores `## ` lines inside CommonMark fenced code blocks (up to three spaces of indentation, >= 3 backticks or tildes, closing fence of the same character with at least as many, unclosed fences run to EOF); `key(l)` strips one trailing CR so a line moved with a changed line ending keeps its origin. The byte-exact restore measures are unchanged. | as v4 plus the new selftest cases (fence, crlf, origins) — `AOA_SELFTEST pass=36 fail=0` | read-only on --repo |
| Round-50 live lifecycle receipt v5 (mapped-model record) | capability: `python3 tools/kama-llamacpp-live.py ... [--witness-dir <existing-dir> --witness-timeout <s>] [--out <json>]`; `python3 tools/kama-llamacpp-live.py --selftest` | as v5 (0 pass, 1 fail, 2 not-evaluated or setup error; receipt schema unchanged `kama-llamacpp-live/v5`); the receipt gains `model_mapping`: read from `/proc/<pid>/maps` (dev, inode, pathname) for the `--model` file, re-opened by its pathname with O_NOFOLLOW, accepted only when fstat() shows the same dev and inode, and hashed in full; anything else is `{"mapped": false, "reason": ...}` | `selftest: ok`; `holes` — real server on xfs records `mapped` true with dev `103:05`; btrfs subvolumes fail closed on dev mismatch | read-only on --repo |
| Round-50 witnessed live receipt replay (isolated, parent-death) | tool + selftest: `python3 tools/kama-live-replay.py --receipt <v4-or-v5-receipt> --work <dir> --out <json> [--witness-dir <existing-dir>] [--witness-timeout <s>] [--live <tool>] [--timeout <s>]`; `python3 tools/kama-live-replay.py --compare <a.json> <b.json>`; `python3 tools/kama-live-replay.py --selftest --scratch <dir>` | as round 49 (0 the rerun matches, 1 ran and differs, 2 refused or could not run); the live child now runs `python -I` with only PATH, HOME, LANG, LC_ALL and TMPDIR (<work>/tmp) and gets SIGTERM when the replay dies (PR_SET_PDEATHSIG via preexec_fn); the replay sets the same signal on itself (set_own_pdeathsig), so killing whatever started it takes replay, live tool and server down; a rerun must record `model_mapping` with `mapped` true and the receipt's model sha256, else `model-mapping:<reason>` or `model-mapping:sha256:...` is a mismatch | `KLR_SELFTEST pass=23 fail=0` | read-only; writes only under --work and --out |

### Re-running live evidence (isolated witnessed replay, round 50)

- The counter starts the replay itself; for a manual run, `python3 -I tools/kama-live-replay.py --receipt .ufo/waves/round-48/c2/live/receipt-1.json --work <empty-dir> --out <json> --witness-dir <existing-empty-dir> --witness-timeout 120` holds the rerun server until `<dir>/release` exists. The server child's environment is the allow-list above; the replay and its live child die with their parent.
- The observer's checks are all outside the replay: exe digest, listener inode, the server descending from the replay process, the model file that `/proc/<pid>/maps` shows hashing to the frozen digest, and a nonce of your own through /tokenize + /detokenize. The rerun receipt's `witness.released` and `model_mapping` record what the tool itself saw.
- Graded form: `python3 tools/round50-replay-bind-audit.py --repo <clone> --tip <full-commit> --scratch <dir>` — needs https to github.com and huggingface.co (about 75 MB per replay), Linux `/proc`, and ~15-46 s on this host.

## Round-51 instrument registry (replay server identity, append-only v6 with disclosures)

Rows for the round-51 counters and the instruments they change (claims C1 operability and C2 calibration). Same columns as `## Local gate/probe registry`. Drafted from each tool's docstring and its own measured exits at the build commits `b6bed925` (C1, C2) and `73bf2a7a` (ledger regenerated) on a `git clone --shared` of the lane. The C1 network legs run in ~20 s on this host; C2 in ~5 s.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-51 C1 replay-exe audit | measurement: `python3 tools/round51-replay-exe-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full>` then `bind=0\|1 own=0\|1 teardown=0\|1 newrow=0\|1 bound=N/3 owned=N/3 met=True`, one `detail:` line per bind, own, teardown and newrow leg, and writes the same text to `--out` (its parent directories are created first); 1 not met; 2 could not evaluate (git failure) | the round-50 bind and teardown legs unchanged; `own`: the counter opens `/proc/<pid>/exe` itself (S499) and requires the running image's dev and inode to be the replay's extracted `<work>/server/<member>`, the frozen server digest, and the same values in the rerun receipt's `server_exe` and the replay's `own_server`; base `57a2e25b` `bind=1 own=0 teardown=1 newrow=0`, build `b6bed925` `met=True` | everything under `--scratch` (removed on exit) and `--out`; read-only on `--repo` |
| Round-51 C2 append-audit v6 check | measurement: `python3 tools/round51-append-audit-v6-check.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full>` then `fixture=0\|1 lane=0\|1 scenarios=N/9 lost=L disclosed=X met=True`, one `detail:` line per scenario and lane finding; 1 not met; 2 could not evaluate | nine constructed scenarios (default threshold 1, A-row permitted vs immutable vs code-span pipe vs dropped row, disclosed, four bad disclosures, partial disclosure, two files in one commit); lane: the tip's tool exits 0 at threshold 1 and the counter's own lost-line multiset equals the ledger key for key in every whole-file-graded file; base `fixture=0 lane=0`, build-fix `73bf2a7a` `met=True` | fixture repos under `--scratch` (removed on exit) and `--out`; read-only on `--repo` |
| Round-51 append-only audit v6 | tool + selftest: `python3 tools/append-only-audit.py --repo <dir> [--to <rev>] [--contract <tsv> \| --files <a,b,...>] [--disclosures <tsv>] [--threshold <n>] [--json]`; `python3 tools/append-only-audit.py --selftest [--scratch <dir>]` | 0 no event partial or unrestored, none regressed, no vanished declared path, every declaration bound and every disclosure row good; 1 otherwise; 2 could not evaluate (malformed contract or ledger) | default threshold 1 (v5: 20); A-row `permitted` rows; `disclosed` status from `registry/append-only-disclosures.tsv`; `AOA_SELFTEST pass=47 fail=0` | none (read-only on `--repo`; selftest fixtures under `--scratch`) |
| Round-51 append-only disclosure ledger | data: `registry/append-only-disclosures.tsv` (`commit<TAB>file<TAB>line_sha256<TAB>count<TAB>class<TAB>note`), regenerated by `.ufo/waves/round-51/c2/build_ledger.py <aoa-json> <repo> <out>` from the tool's `undisclosed` JSON | read by the tool at `<to>`; a row naming no event, no unheld line with that key, too many of them or the wrong class makes the audit exit 1 | 166 rows / 166 lines at `73bf2a7a`; a later restoration of a disclosed line turns its row into an over-count, so the row must then be removed (the ledger is not append-only) | the L1 only, through the lane helper |
| Round-51 live lifecycle receipt v5 (server_exe record) | capability: `python3 tools/kama-llamacpp-live.py ... [--witness-dir <existing-dir>] [--out <json>]`; `python3 tools/kama-llamacpp-live.py --selftest` | as v5 (receipt schema unchanged `kama-llamacpp-live/v5`); the receipt gains `server_exe` {opened, path, dev, inode, size, sha256} read by opening `/proc/<child>/exe` (never a check id) | `selftest: ok` | `--out` and its own scratch, as round 50 |
| Round-51 witnessed live receipt replay (own-member check) | tool + selftest: `python3 tools/kama-live-replay.py --receipt <v4-or-v5-receipt> --work <dir> --out <json> [--witness-dir <existing-dir>]`; `python3 tools/kama-live-replay.py --selftest --scratch <dir>` | as round 50; a rerun whose `server_exe` is absent, not opened, of another digest, or of another dev:inode than `<work>/server/<member>` is a `server-exe:<reason>` mismatch (exit 1); the result gains `own_server` | `KLR_SELFTEST pass=26 fail=0` (three new server-exe cases) | `--work` and `--out` |
| Round-51 digest ledger scope | tool: `python3 tools/digest-ledger.py scan --repo <clone> --rev <rev>`; `python3 tools/digest-ledger.py selftest` | as round 42 | `registry/append-only-disclosures.tsv` is out of scope (its 64-hex cells are line keys, re-derived by append-only-audit v6); `selftest pass=10 fail=0` | none |

### Reading the server's identity and the disclosure ledger (round 51)

- A replay result's `own_server` names the file the replay extracted; the rerun receipt's `server_exe` is what the live tool opened through `/proc/<pid>/exe`. They match only when the running image is that very file (same dev and inode): a digest alone says which bytes run, not which file. A byte-identical copy at the member path still matches (stated limit).
- `python3 tools/append-only-audit.py --repo . --to <rev>` now grades every deletion. Status `disclosed` means every graded line gone at `<rev>` is named in `registry/append-only-disclosures.tsv`; `--json` lists what a ledger row would have to name under `undisclosed`. New in-place edits of an append-only file make the audit exit 1 until they are restored by append (preferred) or disclosed.

## Round-52 instrument registry (sealed-memfd replay server, A-corr restoration)

Rows for the round-52 counters and the instruments they change (claims C1 operability and C2 calibration). Same columns as `## Local gate/probe registry`. Drafted from each tool's docstring and its own exits on a `git clone --shared` scratch build before landing (those dry-run receipts were not kept: they named a scratch commit that is not a lane object; seat W3Mistakes) and re-measured at the landed build `5dacf2c7` (`.ufo/waves/round-52/measured/*-build.out`). The C1 network legs run in ~16 s on this host; C2 in ~4 s.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-52 C1 replay-memfd audit | measurement: `python3 tools/round52-replay-memfd-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full>` then `bind=0\|1 sealed=0\|1 teardown=0\|1 newrow=0\|1 bound=N/3 sealedruns=N/3 met=True`, one `detail:` line per bind, sealed, teardown and newrow leg, and writes the same text to `--out` (its parent directories are created first); 1 not met; 2 could not evaluate (git failure) | no selftest; pinned: the three round-48 v5 receipts, server sha256 `35ac50fb…7ff0`, model sha256 `270cba1b…256d`, seals 15, base `9ff76b1f`, memfd page `man7.org/linux/man-pages/man2/memfd_create.2.html` | `--scratch` (default TMPDIR; removed on exit) and `--out` |
| Round-52 C2 append-restore check | measurement: `python3 tools/round52-append-restore-check.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full>` then `fixture=0\|1 lane=0\|1 scenarios=N/8 corr_lost=C row_lost=R disclosed=X met=True`, one `detail:` line per scenario and lane finding; 1 not met; 2 could not evaluate | eight constructed scenarios (A-corr in-place edit, fenced verbatim re-append, ledger cutoff after/before introduction, only= outside/inside, exempt= inside/dated), each also recomputed by the counter's own fence-aware section logic; base contract rows pinned from `9ff76b1f` | `--scratch` (default TMPDIR; removed on exit) and `--out` |
| Round-52 live lifecycle receipt v5 (sealed server fd) | capability: `python3 tools/kama-llamacpp-live.py ... [--server-fd <inherited fd>] [--witness-dir <existing-dir>] [--out <json>]`; `python3 tools/kama-llamacpp-live.py --selftest` | as v5 (schema unchanged `kama-llamacpp-live/v5`); with `--server-fd` the descriptor must be a sealed memfd (seals 15) holding exactly the bytes of `--server`, else setup error `server-fd-not-sealed`/`server-fd-size`/`server-fd-digest-differs-from-server` (exit 2); the server is exec'd from `/proc/<tool pid>/fd/<n>` with `LD_LIBRARY_PATH` and cwd set to `--server`'s directory and an absolute model path; `server_exe` gains `nlink` and `seals`, `server` gains `fd` | `selftest: ok` (from integration it also drives `sealed_fd()` through a sealed memfd, an unsealed one, an unsealable file, a partial seal, a size and a digest mismatch; seat X5Selftest) | `--out`, its log under TMPDIR |
| Round-52 witnessed live receipt replay (sealed-memfd check) | tool + selftest: `python3 tools/kama-live-replay.py --receipt <v4-or-v5-receipt> --work <dir> --out <json> [--witness-dir <existing-dir>]`; `python3 tools/kama-live-replay.py --selftest --scratch <dir>` | as round 51, except the server runs from a sealed memfd filled from the archive's member stream (`memfd-digest-mismatch` refusal, exit 2); a rerun whose `server_exe` is not that memfd (dev, inode), lacks the four seals, has a link or a non-`/memfd:` link is `server-exe:not-own-memfd`/`server-exe:not-sealed-memfd` (exit 1); `own_server` names the memfd | `KLR_SELFTEST pass=31 fail=0` at the build (five new memfd cases; the round-51 member-links case retired with the path binding); `pass=36` after integration (seat M2Replay's five survivors killed: close-on-exec, short writes, fd closed on refusal, other-inode and partial-seal records) | `--work` and `--out` |
| Round-52 receipt checker (fd mode) | validator + selftest: `python3 tests/llamacpp-live/check-receipt.py <receipt.json> [--expect-...]`; `python3 tests/llamacpp-live/check-receipt.py --selftest` | as before; `child_env_keys` may also name `LD_LIBRARY_PATH` only when the receipt's `server` block records `fd` (a `--server-fd` run); elsewhere that name is INVALID | `selftest: 17 VALID and 1 NOT-EVALUATED receipts accepted; 108 mutations + unreadable case rejected` (seat V2Review: the build's fd-mode receipts were INVALID under the round-51 checker) | none |
| Round-52 append-only disclosure ledger (A/A-row only) | data: `registry/append-only-disclosures.tsv` | as round 51; after the round-52 restoration it holds only the 10 lines of `corpus/SOURCES.md` (A-row) and `registry/report-landing-errata.tsv` (A) whose verbatim re-append would duplicate a registry id or an errata key | `python3 tools/append-only-audit.py --repo . --to <rev>` → `disclosed_lines=10` | none |

### Reading the sealed server and the restored lines (round 52)

- A replay result's `own_server` is the sealed memfd the replay filled from its archive; the rerun receipt's `server_exe` is what the live tool opened through `/proc/<pid>/exe`. A match needs the same dev and inode, seals 15, `nlink` 0 and a `/memfd:` link: no file on disk - a copy, a hardlink or a rename-over at the member path - can be that image. Limits: the libraries still load from the extracted tree by path, and a memfd filled from a byte-identical host install still matches.
- A `## Restored lines (round 52)` block (`###` in `SCORECARD.md`) at the end of an append-only file holds lines that file lost in place, verbatim, inside a five-backtick fence, one block per deleting commit. They are history kept so the file's append-only declaration holds; the file's later text stands where it replaced them.

## Round-53 instrument registry (server code identity in memory, cited-path resolution)

Rows for the round-53 counters and the instruments they change (claims C1 operability and C2 calibration). Same columns as `## Local gate/probe registry`. Drafted from each tool's docstring and its own exits, measured at the landed build `c22602bd` (`.ufo/waves/round-53/measured/*-build.out`). The C1 network legs run in ~25 s on this host; C2 in ~2 s.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-53 C1 replay-code audit | measurement: `python3 tools/round53-replay-code-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full>` then `bind=0\|1 sealed=0\|1 code=0\|1 teardown=0\|1 newrow=0\|1 bound=N/3 sealedruns=N/3 coderuns=N/3 met=True`, one `detail:` line per bind, code, sealed, teardown and newrow leg, and writes the same text to `--out` (its parent directories are created first); 1 not met; 2 could not evaluate (git failure) | no selftest; pinned: the three round-48 v5 receipts, server sha256 `35ac50fb…7ff0`, archive URL and sha256 `bf94332a…695b`, model sha256 `270cba1b…256d`, required members `libllama-server-impl.so`, `libggml-base.so*`, `libggml.so*`, `libggml-cpu-*.so`, base `4229ea1b`, memory page `man7.org/linux/man-pages/man5/proc_pid_mem.5.html`; needs Yama ptrace_scope 0 or 1 (it reads its descendant server's `/proc/<pid>/mem`) | `--scratch` (default TMPDIR; removed on exit) and `--out` |
| Round-53 C2 cited-path check | measurement: `python3 tools/round53-cited-path-check.py --repo <clone> --tip <full-commit> [--fleet <fleet repo>] [--fleet-rev <rev>] [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full> fleet=<full>` then `fixture=0\|1 lane=0\|1 scenarios=N/8 cited=N unresolved=N disclosed=N undisclosed=N bad=N stale=N dropped=N met=True`, one `detail:` line per scenario and per undisclosed citation, bad or stale ledger row and dropped citation; 1 not met; 2 could not evaluate | eight constructed scenarios in a scratch git repository (unresolved path, fenced path, brace group, forged `deleted`, true `deleted`, forged `never`, anchor past EOF, stale row); base `4229ea1b`; surfaces `SCORECARD.md`, `SHONEN.md`, `SKILL.md`; ledger `registry/cited-path-corrections.tsv`; `upstream` rows are fetched (network: raw.githubusercontent.com) | `--scratch` (default TMPDIR; removed on exit) and `--out` |
| Round-53 live lifecycle receipt v5 (code mappings) | capability: `python3 tools/kama-llamacpp-live.py ...`; `python3 tools/kama-llamacpp-live.py --selftest` | as round 52 (schema unchanged `kama-llamacpp-live/v5`); the receipt gains `code_mappings` (`read`, `mappings`: path, dev, inode, `opened`, uid, size, sha256, or `opened: False` with `reason` such as `mapped-file-deleted`, `path-is-not-the-mapped-file`, `open-failed:<err>`) recorded with `server_exe` while the server runs; never a check id | `selftest: ok` (from round 53 it also drives `code_mappings()` on a user-owned copy of `sleep` and after a rename-over of it) | as round 52 |
| Round-53 witnessed live receipt replay (code check) | tool + selftest: `python3 tools/kama-live-replay.py --receipt <v4-or-v5-receipt> --work <dir> --out <json> [--witness-dir <existing-dir>]`; `python3 tools/kama-live-replay.py --selftest --scratch <dir>` | as round 52, plus mismatches (exit 1) `code-mappings:<reason>`, `code-mapping:malformed:<n>`, `code-mapping:foreign-memfd:<path>:<dev>:<inode>`, `code-mapping:unopened:<path>:<reason>`, `code-mapping:not-a-member:<member>`, `code-mapping:digest:<member>:<archive>-><mapped>`, `code-mapping:foreign:<path>:uid=<n>`, `code-mapping:no-archive-library`, and `code-mapping:required-absent:<pattern>`; result gains `own_code` (`verified`, `members` {member: archive sha256}, `host`) | `KLR_SELFTEST pass=46 fail=0` after wave-review hardening: path-less row, foreign executable memfd and omitted required library each fail when its own check is removed (`.ufo/waves/round-53/integration/verify-code-hardening.out`) | as round 52 |
| Round-53 cited-path correction ledger | data: `registry/cited-path-corrections.tsv` | not an executable gate: read-only data graded by the cited-path counter | rows `surface token class evidence note`; classes `deleted`, `never`, `moved`, `eof`, `untracked`, `upstream`, `fixed`; their checks differ: history, current disk/tree state, HTTP 200, or same-surface replacement; the round-53 counter does not validate the note's full truth or upstream bytes | read-only; append-only (corrections supersede by dated comment, never rewrite a row) |

### Reading the code identity and the cited-path ledger (round 53)

- A replay result's `own_code.members` names each archive library the server maps with the digest the replay hashed from the archive's own stream; the rerun receipt's `code_mappings` is what the live tool hashed at each mapped path while it was the mapped inode. The round-53 counter goes further and reads the executable ranges out of the server's memory. Limits: the 13 host libraries are classed (root-owned, same inode, not writable), not compared; data segments, anonymous executable memory and the model mapping are not byte-compared; a byte-identical host install still matches; a library rewritten after the counter's read is not seen.
- A citation in `SCORECARD.md`, `SHONEN.md` or `SKILL.md` that does not resolve is disclosed in `registry/cited-path-corrections.tsv`; the citing sentence stands as filed. A dead path cited in `LOG.md`, the lessons or the knowledge entries is outside this ledger.

Post-wave falsification (round 53): an omitted library is caught by the frozen C1
counter (seat J4OmitLib), and a swapped executable library still fails when the
replay's own `verify_code()` is made to lie (J2SwapUnchecked/J3ForgedReceipt). Limits
observed: a root-owned, not-writable library outside the archive is accepted as a host
mapping (J5Preload); a second executable memfd must be recorded and rejected by the
replay's integrated `foreign-memfd` check (V3Review); the frozen C1 counter skips
memfd-backed mappings. The frozen C2 counter can be made to pass by hiding SKILL.md
citations (J12Hide), and only SCORECARD citations are guarded against deletion; its
upstream rows check HTTP 200, not pinned bytes (J11BadFixed), while an `untracked`
row's note can misstate historical existence (X8Regen). Its scratch fixture also
inherits `GIT_*` environment (Sen4Fixture); never run this frozen counter in a
process with untrusted `GIT_DIR`, `GIT_INDEX_FILE` or `GIT_CONFIG_COUNT*` variables.
These are instrument limits, not fixes to the frozen predicates.

## Round-54 instrument registry (hardened code-identity and cited-path counters, seat-report immutability)

Rows for the round-54 counters and the round-53 seat instrument this round lands (claims C1 operability and C2 calibration). Same columns as `## Local gate/probe registry`. Drafted from each tool's docstring and its own exits. The C1 network legs run in ~60 s on this host (two observation passes per receipt); C2 in ~10 s (its fixture fetches three real pinned upstream URLs).

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-54 C1 replay-code audit | measurement: `python3 tools/round54-replay-code-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full>` then `bind=0\|1 sealed=0\|1 code=0\|1 teardown=0\|1 newrow=0\|1 bound=N/3 sealedruns=N/3 coderuns=N/3 envnames=N/3 hostlibs=N/3 anon=N twopass=N/3 rehash=N met=True`, one `detail:` line per leg; 1 not met; 2 could not evaluate (git failure) | no selftest; pinned: the three round-48 v5 receipts, server sha256 `35ac50fb…7ff0`, archive URL and sha256 `bf94332a…695b`, model sha256 `270cba1b…256d`, required members as round 53, the 13-name frozen host set, base `0b75a84c`; kills K1Cheat (LD_PRELOAD, anonymous RWX page), Sen1Mem (reference rewrite, descendant gate, row bound), J7Late facet 1 (post-exit rehash) | read-only on `--repo`; scratch only |
| Round-54 C2 cited-path check | measurement: `python3 tools/round54-cited-path-check.py --repo <clone> --tip <full-commit> [--fleet <fleet repo>] [--fleet-rev <rev>] [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full> fleet=<full>` then `fixture=0\|1 lane=0\|1 scenarios=N/14 cited=N unresolved=N disclosed=N undisclosed=N bad=N stale=N dropped=N met=True`, one `detail:` line per scenario and per undisclosed citation, bad or stale ledger row, dropped citation and prose advisory; 1 not met; 2 could not evaluate (git failure or an unfetchable upstream row) | fourteen constructed scenarios (the round-53 eight plus M10 mutable ref, M11 wrong bytes, M11/M12 honest pin, M13 never-on-inventory, M15 wrong line, honest fixed); pinned upstream owner/repo, revision and digests; base `0b75a84c` | read-only on `--repo`/`--fleet`; every git call strips inherited `GIT_*`; scratch only |
| Seat-report immutability | measurement: `python3 tools/seat-report-immutability.py --repo <dir> --rev <commit> --rounds <N-M>` | 0 no rewritten committed seat report; 1 at least one `REWRITTEN` line (a report whose tip blob differs from its first-add blob; a restoration prints `RESTORED`); 2 could-not-evaluate (not a repo, unresolvable `--rev`, empty population, an `UNBASED` report) | `--selftest`: 13 arms (fixture shows exit 0 and exit 1; TMPDIR-honouring; toplevel re-bind); grades 720 round-46..52 reports at `c22602bd` in ~0.15 s, read-only | read-only (git rev-parse/ls-tree/log/cat-file only) |

## Round-55 instrument registry (frozen round-54 counters, measured + battery)

Rows for the two frozen counters and the kill-battery harness round 55 lands (claims C1
operability, C2 calibration). Same columns as `## Local gate/probe registry`. Frozen
predicates and counter sha256s: `.ufo/waves/round-55/preregistration.json`; receipts:
`.ufo/waves/round-55/{controls,measured,c1/battery}/`.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-55 C1 replay-code audit (frozen round-54 counter) | measurement: `python3 tools/round54-replay-code-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | as the round-54 registry row, plus `envnames=N/3 hostlibs=N/3 anon=N twopass=N/3 rehash=N`; base `3a600d2f` (newrow re-pointed at S511), frozen sha256 `c81fe971…79af` | no selftest; kill battery `.ufo/waves/round-55/c1/battery/run-battery.py` (control + 3 live kills + 1 vector analysis) | read-only |
| Round-55 C2 cited-path check (frozen round-54 counter, `superseded` class) | measurement: `python3 tools/round54-cited-path-check.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | as the round-54 registry row with `scenarios=N/15` (superseded honest/forged pair added); counter BASE stays `0b75a84c` (drop horizon); frozen sha256 `d70a1729…6510` | fifteen constructed scenarios incl. the superseded pair; ledger classes add `superseded` | read-only |
