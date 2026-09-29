---
name: kama-shokunin
description: Domain specialist — local model serving & endpoint health — scopes local LLM endpoints, baseURL drift, model-id reconciliation. Rank: shonen.
---

# kama-shokunin

Local model serving & endpoint health. This lane answers exactly one question:
**is the thing at this baseURL the model this config believes it is, right now.**

Rank: shonen (round 2). Verdict vocabulary is frozen and shared with
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

## Worked example — the live drift (2026-09-28, re-verified)

`8080` = Jitsi. `34113` = the model. Six consumer surfaces still pin 8080: the
OpenCode `qwen-local` provider, two fail-closed janitor surfaces (agent + CLI),
the janitor's own single-provider overlay, a cascade-protected distiller, and a
builtin default nobody selected yet.

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

- `~/Projects/origin-work/ufo-fsd-alpha/config/the-tick.machine.json:16` →
  `http://127.0.0.1:34113/v1/chat/completions` (`MODEL_OK`);
  same repo, `scripts/local-helper.mjs:8` → `DEFAULT_URL = "http://127.0.0.1:34113"`.
  Census rows and ownership: `corpus/knowledge/consumer-registry.md:54-55`. Both
  are registry rows (`ufo-fsd-thetick`, `ufo-fsd-local-helper`) and act as the
  probe's positive controls — if they ever stop reading `MODEL_OK`, the probe
  itself is suspect, not the endpoint.
- `~/.local/bin/omp` carries a builtin llama-cpp default of 8080, overridable by
  env: `strings -a ~/.local/bin/omp | grep 'LLAMA_CPP_BASE_URL'` → a line reading
  `LLAMA_CPP_BASE_URL || "http://127.0.0.1:8080",`. `LLAMA_CPP_BASE_URL` is set
  nowhere on this host, so the builtin provider resolves to the squatted port
  (`corpus/knowledge/consumer-registry.md:49`).
- Systemd archives beyond the live unit, all `--port 8080`:
  `qwen-coder.service.pre-template-20260829-033610.bak:16`,
  `.pre-omp-context-20260829-0322.bak:16`, `.pre-safety-20260829-031834.bak:16`.

## Decision table

| Symptom | First check (verbatim) | Verdict | Action |
|---|---|---|---|
| Model call returns an HTML page (`text/html`, 404 body with URI/STATUS/MESSAGE table) | `curl -sSI <the port the consumer's baseURL names>` (live: `http://127.0.0.1:8080/`) | `FOREIGN_SERVICE` | Port is squatted. Identify the owner (`ss -ltnp`, `docker ps`), then repoint the **consumer**, never the foreign service. Live: `docker-jitsi-meet-jvb-1`. |
| Worked yesterday at the same baseURL, now refused | `bash tools/kama-probe.sh listeners` | `DEAD` | Read the producer, not the consumer: `grep -n -- '--port' ~/.config/systemd/user/qwen-coder*.service*`; `systemctl --user status qwen-coder.service`. The port may have moved under you. |
| Consumer's port answers, but as a different *kind* of service | `bash tools/kama-probe.sh check` | `FOREIGN_SERVICE` or `NOT_HTTP` | Reconcile registry vs listeners; the truth for the port is the unit's `ExecStart`. Update the consumer's `baseURL` + registry row in the same change. |
| 2xx JSON with `models[]`, but the id ≠ expected | `curl -sS http://127.0.0.1:34113/v1/models \| jq -r '.data[0].id'` | `MODEL_MISMATCH` | Compare **after normalization** (see below). A full GGUF path vs a bare id is *not* a mismatch. |
| Endpoint returns HTTP 401/403, body `{"error":"unauthorized"}` | `curl -sS http://127.0.0.1:8790/health` | `UNAUTHORIZED_SERVICE` | It is not a model server: `8790` = `omp auth-broker serve` (pid 1297), `8791` = `omp auth-gateway serve` (pid 2997) — the fleet's credential brokers. Never add a key to a model config; escalate to kagi. |
| A "model port" is expected but nothing answers | `ss -ltnp \| grep :PORT` | `DEAD` | Do not guess defaults. On this box `11434`, `1234`, `5000`, `8000`, `3000`, `7860`, `9090` all `curl: (7) Failed to connect`; the model port lives only in the unit file (34113). |
| Port that *listens* but is not HTTP | `curl -sSI http://127.0.0.1:8888/` | `NOT_HTTP` | `curl: (56) Recv failure: Connection reset by peer` (jicofo). Also `4226` = sccache → empty reply. Listening ≠ HTTP ≠ model. |
| `/` on the real model port returns JSON 404 | `curl -sS http://127.0.0.1:34113/health` | (not a fault) | `{"error":{"message":"File Not Found","type":"not_found_error","code":404}}` is llama.cpp's normal root. Probe `/health` or `/v1/models`, not `/`. |
| A latent/probable unit would re-take the port | `grep -n -- '--port' ~/.config/systemd/user/qwen-coder.ctx32k-q4.service` | (risk) | `:16` still declares `--port 8080`; the unit is `disabled` — enabling it collides with the JVB mapping. Report as a trap; do not enable. |
| A config was "fixed" but drift persists | `grep -rn 'baseURL\|MODEL_ENDPOINT' <consumer set>` | `FOREIGN_SERVICE` | Editing one consumer does not reconcile the surface: the live pins above are separate files, and 4 config archives + 3 systemd archives still carry 8080. Re-run `check` after every edit. |
| Suspected dispatch-level drift onto loopback | `grep -nE "(baseURL\|baseUrl\|endpoint):[[:space:]]*https?://(127\.0\.0\.1\|localhost)(:\|/)" ~/.omp/agent/config.yml` | (empty = ok) | Empty output today: `modelRoles` aliases are all remote (`~/.omp/agent/config.yml:13-44`), e.g. `:24 m_flash: charm-hyper/deepseek-v4.1-flash:max`. Any match is a new kama-relevant pin. |
| A consumer works, another "with the same model" fails | `bash tools/kama-probe.sh consumers` | mixed `FOREIGN_SERVICE` / `MODEL_OK` | Classify the consumer before debugging the model: `janitor.md:21`, `the-janitor:47` and `the-janitor/opencode.json:5-6` have **no fallback** (drift = outage), while `distiller.md:7` has a cloud cascade (drift = silent degradation). Same symptom, opposite severity. |

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

## Error signatures

| Verbatim string seen | Where | Meaning | Next action |
|---|---|---|---|
| `Server: llama.cpp` (response header) | `curl -sSI http://127.0.0.1:34113/v1/models` | llama.cpp runtime answered | Continue to id check — header alone is not identity |
| `{"models":[{"name":"/scratch/models/…gguf","model":"/scratch/models/…gguf",…}],"object":"list","data":[{"id":"/scratch/models/…gguf",…}]}` | `GET :34113/v1/models` | Served identity, path-shaped | Normalize, then compare to `expected_model_id` |
| `{"status":"ok"}` | `GET :34113/health` | Process alive; says **nothing** about which model | Follow with `/v1/models` |
| `"default_generation_settings":{"params":{…}}` | `GET :34113/props` | Serving config loaded (chat_format `Content-only`, `reasoning_format` `none`) | Use for template/format questions, not identity |
| `<h2>HTTP ERROR 404 Not Found</h2>` + `<th>URI:</th><td>http://127.0.0.1:8080/v1/models</td>` with `Content-Type: text/html;charset=iso-8859-1` | any path on `:8080`, incl. `POST /v1/chat/completions` | Jetty-family servlet; foreign service on a model path | `FOREIGN_SERVICE` — stop the consumer, name the owner, repoint |
| `{"error":"unauthorized"}` with `HTTP/1.1 401 Unauthorized`, `Content-Type: application/json` | `:8790`, `:8791` — on `/`, `/health`, `/v1/models`; unchanged by a bogus `Authorization: Bearer` | Auth broker, not a model (`omp auth-broker` / `auth-gateway`) | `UNAUTHORIZED_SERVICE` — escalate; never inject credentials |
| `{"error":{"message":"File Not Found","type":"not_found_error","code":404}}` (`application/json`) | `GET :34113/` | llama.cpp's normal root 404 | Probe `/health` / `/v1/models` instead; do not classify a fault |
| `curl: (7) Failed to connect to 127.0.0.1:11434 after 0 ms` | any unserved port | Nothing bound | `DEAD` — resolve the real port from the unit file |
| `curl: (56) Recv failure: Connection reset by peer` | `:8888` (jicofo) | TCP listener, not an HTTP service | `NOT_HTTP` |
| `Not Found` with `Content-Type: text/plain;charset=utf-8` | `:34955`, `:41453` (`omp`, pids 3467459 / 1053353) | Non-model HTTP service | `FOREIGN_SERVICE` for model purposes |
| `Unauthorized` / `Invalid API Key` / `--api-key KEY` (strings in the binary) | `strings -a ~/.local/bin/llama-server \| grep -i 'unauthorized\|api.key'` | The runtime *can* enforce keys, but the live unit passes no `--api-key` (`qwen-coder.service:13-23`) ⇒ 34113 is unauthenticated loopback-only | `[INFERENCE]` treat any 0.0.0.0 bind of this endpoint as a security event; report to kagi |
| `opencode-distiller … file_match=inherited … resolver_kind=raw … FOREIGN_SERVICE` in `kama-probe.sh consumers` | a registry row whose target file pins a bare model, not a URL | The consumer inherits its provider's baseURL; the registry's declared value stands and the probe still verifies the endpoint | Normal — but it means the registry's `declared` column is a claim: confirm the provider block (`distiller.md` inherits `qwen-local`) before trusting the row. |

Elision convention: `…` marks a cut inside a single long line of the body, never
a paraphrase — every quoted fragment is byte-for-byte from the live response.

Also-normal, not faults: `# HELP llamacpp:prompt_tokens_total …` from `/metrics`,
and `[{"id":0,"n_ctx":16384,…},{"id":1,…}]` from `/slots` (matches `--parallel 2`,
`--ctx-size 16384`).

## Checklist (run from the repo root; all deps present on this box)

1. **Reconcile** — the entry point, runnable as written from the repo root:
   `bash tools/kama-probe.sh check; echo $?`
   Today it prints one row per registry entry and ends
   `registry_rows_evaluated=11 model_ok=3 drift=8 exit=2` → `EXIT=2` — exactly the
   drift this lane exists to name: eight rows `FOREIGN_SERVICE` at 8080 (five live
   pins, the `omp` builtin default, two systemd traps) against three `MODEL_OK`
   rows at 34113 (`systemd-qwen-coder` plus the two cross-repo positive controls
   `ufo-fsd-thetick` / `ufo-fsd-local-helper`). The tally grows as registry rows
   are added, so read the last line rather than this document's number. Expect
   `0` only after every consumer is repointed.
2. **Capture comparable state** —
   `bash tools/kama-probe.sh snapshot; echo $?`. The final tracked baseline ended
   `snapshot=20260929T043044Z prev=- rows=11 model_ok=3 drift=8 transitions=0 exit=2`;
   an unchanged run ended `snapshot=20260929T043052Z prev=20260929T043044Z ...`
   and left both tracked artifacts byte-stable. Exit `2` mirrors the drift gate;
   it is not a write failure. The command writes a local dated JSON plus tracked
   `latest.tsv` and `DELTA.md`; `--history DIR` isolates the state. This is
   invocation history, not a scheduler (`corpus/knowledge/snapshot-history.md`).
3. `bash tools/kama-probe.sh listeners` — live census over every listening TCP
   port, exit `0`. Counts move with ephemeral `omp` listeners (one run tallied
   `probed=18 model_endpoints=1 foreign_service=12 unauthorized_service=2 dead=1 not_http=2`),
   so pin the *classifications*, not the tally: `34113` `MODEL_OK` (with
   `served_model` = the full GGUF path), `8080` `FOREIGN_SERVICE`, `8790`/`8791`
   `UNAUTHORIZED_SERVICE`, `8888` `NOT_HTTP`, `631` `FOREIGN_SERVICE`
   (`Server: CUPS/2.4 IPP/2.1`).
4. `bash tools/kama-probe.sh consumers` — registry reconciled against the files;
   columns `declared | resolved_from_file | file_match | resolver_kind | endpoint |
   port | verdict | served_model`; exit `0` today (it is a listing, not a gate —
   `check` is the gate), tally `consumer_rows_evaluated=11 exit=0`. Read
   `file_match` before trusting a row: `opencode-distiller` is
   `file_match=inherited`, `resolver_kind=raw` (its file pins a bare model, so
   the registry's declared 8080 stands) and still reconciles to
   `FOREIGN_SERVICE`; `systemd-*` rows are `resolver_kind=port:<n>`.
5. `bash tools/kama-probe.sh check --json` — machine form, same exit codes as
   item 1 (`EXIT=2` today): stdout JSON with keys `schema` (`kama-probe/v1`),
   `subcommand`, `verdict_vocabulary`, `exit_codes`, `registry`, `rows[]`
   (`id | consumer_path | declared | resolved_from_file | file_match |
   resolve_kind | endpoint | port | expected_model_id | verdict`), and
   `summary` = `{"registry_rows_evaluated":11,"model_ok":3,"drift":8,"exit":2}`.
   `listeners --json` and `consumers --json` behave the same way, exit `0`;
   `snapshot --json` emits its persisted `kama-probe/v2` document on stdout.
6. `curl -sS --max-time 5 http://127.0.0.1:34113/health` → `{"status":"ok"}`.
7. `curl -sS --max-time 5 -D- -o/dev/null http://127.0.0.1:34113/v1/models | grep -i '^Server:'` → `Server: llama.cpp`.
8. `curl -sS --max-time 5 http://127.0.0.1:34113/v1/models | jq -r '.data[0].id'` → `/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf`.
9. `ss -ltnp | grep -E ':(34113|8080|8888)'` — model on 34113 (`llama-server`), Jitsi mappings on 8080/8888.
10. `docker ps --format '{{.Names}} {{.Ports}}' | grep -E '8080|8888'` — names the squatter.
11. `grep -n -- '--port' ~/.config/systemd/user/qwen-coder*.service*` — the producer's truth (`qwen-coder.service:17 --port 34113`; every archived unit at `:16` still `8080`).
12. `grep -rn 'baseURL\|MODEL_ENDPOINT' ~/.config/opencode/opencode.json ~/.config/opencode/agents/janitor.md ~/.config/opencode/agents/distiller.md ~/.config/the-janitor/opencode.json ~/.local/bin/the-janitor` — every live pin in one shot.
13. `systemctl --user show qwen-coder.service -p ActiveState -p SubState -p MainPID` → `active` / `running` / `1299`.
14. After any fix: run item 2 to preserve the transition, then require item 1 to
    exit `0` before reporting done.

## Anti-patterns

1. **"Status says it's configured, so it's verified."** Observed symptom: a
   consumer pinned at 8080 for a month (backups from 2026-08-29 through
   `.bak-20260921-devin-slots:144`) while `opencode.json:158` stayed 8080 even
   after an edit at mtime 2026-09-28 16:46:43. Cause: `status`-style surfaces
   print configured values, not verified capability (independently recorded in
   `.ufo/reports/round-3/kagi.md:23-25`). Fix: run item 1.
2. **Reading `/health` as identity.** Observed symptom: `{"status":"ok"}` from
   34113 looks like success, but the same class of "ok" answer is exactly what
   hid the drift; only `/v1/models` + `Server:` distinguishes. Fix: items 5-6.
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
   `3000`/`7860`/`9090` all refuse on this host; 34113 exists only because the
   unit says so. Fix: item 9 before probing anything.
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
10. **Mistaking a green `check` for coverage.** Observed symptom: `check` now
    evaluates **11** registry rows, while the lane's own census holds **37**
    (`corpus/knowledge/consumer-registry.md`); the uncovered remainder is fossils
    and other lanes' correct-34113 pins — so `exit=0` would certify *declared*
    consumers only, while a brand-new config that copied a 8080 backup (four
    exist) enters the fleet unseen. Fix: every new local-endpoint pin earns a
    `registry/endpoint-consumers.tsv` row; reconcile the census against the
    registry each round.
11. **Trusting a "raw"/`inherited` row without reading the file.** Observed
    symptom: `opencode-distiller` reports `file_match=inherited`,
    `resolver_kind=raw` — the registry's `declared` value is echoed, and only the
    endpoint is verified. Fix: read the `file_match` column; `inherited` rows
    need the provider block checked by hand. (A round-1 resolver bug that read
    the `30` of `30B` as port `30` was fixed mid-round, but the class of error —
    a claim standing in for a re-derivation — remains the failure mode to watch.)

## Cited sources

- Live host state (re-verified this round: 2026-09-28 local / HTTP `Date`
  header 2026-09-29T01:47Z, read-only): `ss -ltnp`,
  `docker ps --format '{{.Names}} {{.Ports}}'`, `docker inspect
  docker-jitsi-meet-jvb-1`, `systemctl --user show qwen-coder.service`,
  `curl` against `:34113` (`/health`, `/v1/models`, `/props`, `/slots`,
  `/metrics`), `:8080`, `:8790`, `:8791`, `:8888`, `:631`, `:4226`, `:9222`,
  `:34955`, `:41453`.
- Consumers: `~/.config/opencode/opencode.json:154,158,161`;
  `~/.config/opencode/agents/janitor.md:5,20-21`;
  `~/.config/opencode/agents/distiller.md:5,7`;
  `~/.local/bin/the-janitor:16-19,47`; `~/.config/the-janitor/opencode.json:5-6,8-9,16`.
- Correct-pin counterexamples: `~/Projects/origin-work/ufo-fsd-alpha/config/the-tick.machine.json:16`,
  `~/Projects/origin-work/ufo-fsd-alpha/scripts/local-helper.mjs:8`; builtin default
  in `~/.local/bin/omp` (`strings -a ~/.local/bin/omp | grep LLAMA_CPP_BASE_URL`
  → `LLAMA_CPP_BASE_URL || "http://127.0.0.1:8080",`).
- This lane's runnable artifacts: `tools/kama-probe.sh` (`check`, `listeners`,
  `consumers`, and `snapshot`; JSON stdout for all four),
  `tools/test-snapshot.sh` (24 behavioral checks), and
  `registry/endpoint-consumers.tsv` (11 rows, md5
  `87eb156b7cc36e98f3cbfb37c00f5351`; 6 columns — `id`, `consumer_path`,
  `json_pointer_or_grep`, `declared_baseurl`, `expected_model_id`, `notes`) —
  round-2 hashes and measured outputs are pinned in `LOG.md`. Row ids:
  `opencode-qwen-local`, `janitor-agent`, `opencode-distiller`, `janitor-cli`,
  `janitor-opencode`, `omp-llama-cpp-default`, `systemd-qwen-coder`,
  `systemd-qwen-coder-fossil`, `systemd-qwen-coder-ctx32k-latent`,
  `ufo-fsd-thetick`, `ufo-fsd-local-helper`.
- Producer: `~/.config/systemd/user/qwen-coder.service:13-23` (mtime 2026-09-08
  20:43:13), `~/.config/systemd/user/qwen-coder.service.bak.1788033391:16`,
  `~/.config/systemd/user/qwen-coder.ctx32k-q4.service:16` (disabled),
  `~/.local/bin/llama-server` (`version: 0.3.0-dev (build 1, commit d7bd3bf)`).
- Dispatch layer: `~/.omp/agent/config.yml:13-44` (no loopback `baseURL` on any
  `m_*` alias; `:24 m_flash: charm-hyper/deepseek-v4.1-flash:max`).
- Fossils: `~/.config/opencode/opencode.json.pre-qwen-model-20260829-031834.bak:50`,
  `.pre-sentinel-disable-20260829-033405.bak:50`,
  `.pre-fast-oauth-20260829.bak:155`, `.bak-20260921-devin-slots:144`;
  systemd archives `qwen-coder.service.pre-template-20260829-033610.bak:16`,
  `.pre-omp-context-20260829-0322.bak:16`, `.pre-safety-20260829-031834.bak:16`.
- Lane memory: `corpus/knowledge/drift-timeline.md`,
  `corpus/knowledge/served-model-identity.md`,
  `corpus/knowledge/alias-endpoint-normalization.md`,
  `corpus/knowledge/consumer-registry.md` (37-row census),
  `corpus/lessons/probe-mutation-matrix.md` (M7 = the normalization spec hole).
- Prior art (same defect, independent lanes):
  `.ufo/reports/round-3/kagi.md:23-25,69-70`;
  `.ufo/reports/round-4/kengaku.md:20-23,79`.