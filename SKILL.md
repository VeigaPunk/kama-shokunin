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
  `scripts/local-helper.mjs` retain explicit 34113 pins. They were historical
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
and `[{"id":0,"n_ctx":16384,…},{"id":1,…}]` from `/slots` (matches `--parallel 2`,
`--ctx-size 16384`).

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
unconditionally (S060). Never interpret a CI fixture's header as model quality.

The capability command and measured controls are recorded in the round-20
capabilities appendix of SCORECARD; source mechanisms and limits are in
`corpus/knowledge/gguf-declared-identity.md`. Existing consumer routes,
registered endpoints, model downloads and persistent servers remain operator-owned.

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
