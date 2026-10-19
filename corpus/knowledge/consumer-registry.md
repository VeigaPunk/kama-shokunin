# Consumer registry — every config surface on this box that pins a LOCAL model endpoint

Round 1, lane **kama-shokunin** (local model serving & endpoint health). Axis worked: **operability
(runnable artifacts), measured via freshness** — every row is a live re-read/re-probe, not a
carried-forward claim.

Scope of the census: any `localhost:N` / `127.0.0.1:N` `baseURL`, or a local provider (npm
`openai-compatible`, `ollama`, `lm-studio`, `llama-cpp`, `litellm`, `vllm`) pointing at a loopback
port. Non-model loopback pins (CDP, browser daemons, auth brokers, web previews) are recorded in a
separate section because they share the same "drifted loopback peer" failure class but are *not*
kama's serving surface.

Frozen L1 evidence is cited as `L1-F<n>`; every L1 fact cited here was independently re-verified in
round 1 (live command in `§Live verdicts`).

## The one-line finding

There are **two distinct consumer generations** on this box, and they disagree:

- **Stale (8080)**: the opencode overlay family and `the-janitor` CLI still pin
  `http://…:8080/v1`. Port 8080 is served by **Jitsi `jvb`** (Docker), which answers every
  `/v1/*` path with the same Jetty HTML 404 (L1-F3).
- **Correct (34113)**: the `ufo-fsd-alpha` runtime (`the-tick.machine.json`, `local-helper.mjs`)
  already pins the live `llama-server` port. **The expectation "no config pins 34113" is FALSE** —
  two shipped configs do, plus one lane doc.

So the box contains both the bug and its known-good fix, on different surfaces, with no owner for
the reconciliation. That is precisely kama's domain (MINT.md §Reasoning).

## Errata — 2026-10-14 re-census (append-only; rows below keep their round-1 text)

The box changed under this registry. Everything in this section was re-measured on
2026-10-14; claims it supersedes stay quoted in the table as *historical*.

- **The `ufo-fsd-alpha` tree moved.** `~/Projects/origin-work/ufo-fsd-alpha` no
  longer exists; the same repository now lives at `~/Projects/ufo-fsd-alpha`,
  HEAD `964f443e` ("routing: regenerate omp-seat-routing mirror"). Every
  `origin-work/` citation below names that relocated tree. Re-measured anchors
  in the new location: `config/the-tick.machine.json:16` still carries
  `"endpoint": "http://127.0.0.1:34113/v1/chat/completions"` (`apiModel` at
  `:13`, `parallelSlots`/`contextTokens` at `:17-18` — the model block is
  `:7-13`, not `:7-14`); `scripts/local-helper.mjs:8` still pins
  `http://127.0.0.1:34113`, `UFO_LOCAL_HELPER_URL` override is at `:312`
  (doc) / `:325` (call site), the credential-free-loopback `endpoint_invalid`
  gate is at `:155-161`; `tests/the-tick.test.js:61, :125, :1457` and
  `docs/THE-TICK.md:29` still pin 34113;
  `tests/local-helper.test.js:263-266` still holds the four 8080 rejection
  fixtures; `evidence/nightcall-integration/nc2-verify-global-r01-route-authority.json:135,:144`
  unchanged. The moved tree's remotes re-measured: `cursor` →
  `origin.cursor.com/jo-o-veiga/ufo-fsd-alpha.git`, `origin` →
  `github.com/VeigaPunk/ufo-fsd-alpha.git` (the names swapped roles vs the
  round-1 record; `nc5-sandbox` is gone).
- **The second checkout is gone.** `~/Projects/webzites/` (incl. `repos/ufo-fsd-alpha`
  and `repos/llm-wiki`) does not exist; row #38 and the llm-wiki non-model rows
  are historical.
- **Most consumer files are gone.** Deleted since round 2:
  `~/.config/opencode/agents/`, `~/.config/opencode/opencode.json.*.bak*`,
  `~/.config/the-janitor/`, `~/.local/bin/the-janitor`,
  `~/.local/bin/codex-titanium-kimi`, `~/.local/bin/omp.stock-18.2.2.bak`,
  `~/.config/systemd/user/qwen-coder*.service*`, `~/archive/bench-arena/loop.sh`,
  `/tmp/fleet-override.yml`, `~/.omp/agent/skills/kimi-webbridge`,
  `~/.config/systemd/user/omp-auth-*.service`. `~/.config/opencode/opencode.json`
  still exists but is now 5 lines — the `qwen-local` provider and its
  `localhost:8080/v1` pin are gone. Rows #1-#11, #14-#16, #21, #31-#34 are
  therefore historical: the *drift they recorded was real*, but no live file
  still carries it. `~/.local/bin/omp` (#12) still contains
  `LLAMA_CPP_BASE_URL || "http://127.0.0.1:8080"`. `~/.omp/agent/config.yml`
  still exists; its `:168` auth-broker URL is gone — no `127.0.0.1`/`localhost`
  strings remain, so row #13 is historical too. `opencode.log` (#35) still exists.
- **Neither port answers.** `127.0.0.1:34113` (llama-server) and `127.0.0.1:8080`
  (Jitsi) both refuse connections now; `qwen-coder.service` is inactive and its
  unit file deleted. Every `MODEL_OK`/`FOREIGN_SERVICE` verdict in the table is
  historical; today's `check` reads
  `registry_rows_evaluated=3 model_ok=0 drift=3 exit=2` (three DEAD rows:
  `omp-llama-cpp-default`, `ufo-fsd-thetick`, `ufo-fsd-local-helper`). DELTA.md
  records the row-removal transitions.
- **Registry rows now cite the tree as `$UFO_SRC/...`.** `tools/kama-probe.sh`
  resolves `--ufo-src` > `$UFO_SRC` env > first existing of
  `~/Projects/ufo-fsd-alpha`, `~/Projects/origin-work/ufo-fsd-alpha`; the
  endpoint registry no longer hardcodes a checkout location.

## Consumer table (config pins)

The **live verdict** column uses the binding vocabulary: `MODEL_OK` | `MODEL_MISMATCH` |
`FOREIGN_SERVICE` | `UNAUTHORIZED_SERVICE` | `DEAD` | `NOT_HTTP`. Labels not produced by a probe are
marked `—(no probe: non-model / archival)`.

| # | consumer path:line | declared baseURL | port | provider / model id | live verdict at that port | owning lane |
|---|---|---|---|---|---|---|
| 1 | `~/.config/opencode/opencode.json:158` | `http://localhost:8080/v1` | 8080 | `qwen-local` (:154) / `Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` (:161) | **FOREIGN_SERVICE** (HTTP 404, `text/html;charset=iso-8859-1`, Jetty) | **unowned** — endpoint identity is the "no province owns it" row; MINT.md claims it for kama |
| 2 | `~/.config/opencode/agents/janitor.md:5` (`model:`), `:20-21` (`…at http://127.0.0.1:8080/v1; there is no fallback`) | `http://127.0.0.1:8080/v1` | 8080 | `qwen-local` / `Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` | **FOREIGN_SERVICE** (same Jetty 404) | `kotoba` [INFERENCE] (agent-instruction surface); **kagi** consumes it, and it is the only consumer with *no* fallback |
| 3 | `~/.config/opencode/agents/distiller.md:5` (`model:`), `:7` (`cascade: "qwen-local/… > openai/gpt-5.6-sol-fast > xai/grok-4.5"`) | inherited from provider #1 | 8080 | `qwen-local` / same id | **FOREIGN_SERVICE** — **cascade-protected**: the cloud tail survives the 8080 break; janitor (#2) does not | `kotoba` [INFERENCE] |
| 4 | `~/.local/bin/the-janitor:16-19` (`MODEL_PROVIDER="qwen-local"`, `MODEL_ID="Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS"`, `MODEL_ENDPOINT="http://127.0.0.1:8080/v1"`) | `http://127.0.0.1:8080/v1` | 8080 | `qwen-local` / `Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` | **FOREIGN_SERVICE** — Bash script, **outside the opencode config tree** (L1 broadcast hit, independently re-verified) | **kagi** (the-janitor is the vault handler) |
| 5 | `~/.local/bin/the-janitor:148` (`echo "endpoint $MODEL_ENDPOINT"`) | inherits #4 | 8080 | same | **FOREIGN_SERVICE** (status printout path) | kagi |
| 6 | `~/.config/the-janitor/opencode.json:16` (`"baseURL": "http://127.0.0.1:8080/v1"`), provider `qwen-local` (:12), `model`/`small_model` (:8-9) | `http://127.0.0.1:8080/v1` | 8080 | `qwen-local` / `Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` | **FOREIGN_SERVICE** | **kagi** (own overlay; `enabled_providers: ["qwen-local"]` → fails closed, no cloud tail) |
| 7 | `~/.config/the-janitor/config.json:3-5` (provider `qwen-local` → model limits `context:32768`) | *none declared* (inherits #6) | 8080 | `qwen-local` / same id | — (no own baseURL; resolves through #6) | kagi |
| 8 | `~/.config/the-janitor/client.py:13-14` (`HOST="127.0.0.1"`, `PORT=…THE_JANITOR_PORT…, "40961"`), `:16-17` model ids | `http://127.0.0.1:40961` (control plane) | 40961 | `qwen-local` / `Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` | **DEAD** (`40961` not listening at probe time; `ss` shows no 40961) | kagi |
| 9 | `~/.config/systemd/user/qwen-coder.service:17` (`--host 127.0.0.1 … --port 34113`), `:16` (`--cors-origins http://127.0.0.1:8080`) | **server**, not consumer: `127.0.0.1:34113` | 34113 | llama-server, alias = `/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf` | **MODEL_OK** (L1-F4/F5 re-verified) | **kama** (server side) |
| 10 | `~/.config/systemd/user/qwen-coder.ctx32k-q4.service:16` (`--host 127.0.0.1 --port 8080`), disabled, "UNTESTED variant" | server: `127.0.0.1:8080` | 8080 | llama-server, same gguf | — (unit disabled → not running) **latent FOREIGN_SERVICE**: if enabled it collides with Jitsi jvb on 8080 | kama |
| 11 | `~/.config/systemd/user/qwen-coder.service.bak.1788033391:16` (`--host 127.0.0.1 --port 8080`) | server: `127.0.0.1:8080` | 8080 | llama-server, same gguf | — archival (epoch 1788033391 = 2026-08-29 19:56 UTC) — the **fossil origin** of the stale pin (L1-F9) | kama (retired) |
| 12 | `~/.local/bin/omp:1544771` — builtin provider default: `baseUrl: Bun.env.LLAMA_CPP_BASE_URL \|\| "http://127.0.0.1:8080"` | `http://127.0.0.1:8080` (unless `LLAMA_CPP_BASE_URL` set) | 8080 | builtin `llama-cpp` provider (unset env ⇒ this default) | **FOREIGN_SERVICE** if the builtin is ever selected without the env override | `kumitate` (omp binary / dispatch tooling) |
| 13 | `~/.omp/agent/config.yml:168` (`auth: broker: url: http://127.0.0.1:8790`) | `http://127.0.0.1:8790` | 8790 | omp auth-broker (credential vault), **not a model endpoint** | **UNAUTHORIZED_SERVICE** (HTTP 401, `application/json`) | `kumitate`/`kagi` (omp auth infra) |
| 14 | `~/.config/systemd/user/omp-auth-broker.service:7` (`--bind=127.0.0.1:8790`), `:2` desc | `127.0.0.1:8790` | 8790 | omp auth-broker | **UNAUTHORIZED_SERVICE** (401) | kumitate/kagi |
| 15 | `~/.config/systemd/user/omp-auth-gateway.service:8` (`--bind=127.0.0.1:8791`), `:2`; `~/.config/systemd/user/kimi-auth-proxy.service:2` (`127.0.0.1:8791`) | `127.0.0.1:8791` | 8791 | omp auth-gateway / kimi OAuth proxy | **UNAUTHORIZED_SERVICE** (401, JSON) | kumitate/kagi |
| 16 | `~/.local/bin/codex-titanium-kimi:3` (comment: gateway at `127.0.0.1:8791`) | `127.0.0.1:8791` | 8791 | kimi-code OAuth proxy consumer | **UNAUTHORIZED_SERVICE** (401) | kumitate/kagi |
| 17 | `~/Projects/ufo-fsd-alpha/config/the-tick.machine.json:16` (`"endpoint": "http://127.0.0.1:34113/v1/chat/completions"`; re-measured 2026-10-14 after the tree relocated — the `origin-work/` path is historical), model block `:7-13` (`apiModel` = `Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` at `:13`), `:17-18` (2 slots / 16384 ctx) | `http://127.0.0.1:34113/v1/chat/completions` | 34113 | Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS | **MODEL_OK** ✅ — *historical: 34113 is connection-refused today (§Errata)* | **kumitate** (ufo-fsd-alpha runtime; its corpus `ops-watchers.md:393` names `config.backend.endpoint`) |
| 18 | `~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs:8` (`const DEFAULT_URL = "http://127.0.0.1:34113"`), `:312` doc + `:325` call site (`UFO_LOCAL_HELPER_URL` override), `:155-161` (refuses anything not credential-free loopback HTTP, incl. `localhost`/`[::1]`/`127.0.0.1`) — re-measured 2026-10-14 | `http://127.0.0.1:34113` (default) | 34113 | dedupe/digest/classify helper (`ufo-local-helper-v1`) | **MODEL_OK** ✅ — *historical (§Errata)* | kumitate |
| 19 | `~/Projects/ufo-fsd-alpha/docs/THE-TICK.md:29` (re-measured 2026-10-14; was `:40` in round 1) | `http://127.0.0.1:34113/v1/chat/completions` | 34113 | doc of #17 | **MODEL_OK** ✅ — *historical* | kumitate |
| 20 | `~/Projects/ufo-fsd-alpha/evidence/nightcall-integration/nc2-verify-global-r01-route-authority.json:135` (`"endpoint": "http://127.0.0.1:34113/v1/chat/completions"`), `:144` (verbatim: "No Qwen3-Coder/34113/Tick model identifier matched the global OMP config or project mission/OMP overlays") — re-measured, unchanged | `http://127.0.0.1:34113/v1/chat/completions` | 34113 | recorded evidence artifact | **MODEL_OK** ✅ — *historical* | kumitate |
| 21 | `~/archive/bench-arena/loop.sh:5` (`METRICS_URL=${LLAMA_METRICS_URL:-http://127.0.0.1:8080/metrics}`), `:10` (scrape fn; moved from `~/bench-arena/`) | `http://127.0.0.1:8080/metrics` | 8080 | llama.cpp `/metrics` scraper (default target) | **FOREIGN_SERVICE** — the port answers **HTTP 200 `application/openmetrics-text`, 27461 B**, but it is **Jitsi jvb's** openmetrics stream, not llama.cpp's (`grep -icE 'prompt\|eval'` = 0 → a corrected reader pointed at 8080 logs zeros instead of failing) | **kengaku** (bench-arena owner) |
| 22 | `~/projects/shokunin/kengaku-shokunin/SKILL.md:322-323` | `localhost:8080` / `127.0.0.1:34113` | both | — (documents the drift) | records FOREIGN_SERVICE on 8080 / MODEL_OK on 34113 | kengaku |
| 23 | `~/projects/shokunin/kengaku-shokunin/PROVINCE.md:14` | `http://127.0.0.1:34113` | 34113 | Qwen3-Coder-30B-A3B-Instruct UD-IQ2_XXS, `owned_by=llamacpp`, `n_ctx=16384` | **MODEL_OK** ✅ | kengaku |
| 24 | `~/projects/shokunin/kagi-shokunin/corpus/knowledge/janitor-env-contract.md:55` (`MODEL_ENDPOINT="http://127.0.0.1:8080/v1"` at L19 of the script) | `http://127.0.0.1:8080/v1` | 8080 | — (doc of #4) | FOREIGN_SERVICE | kagi |
| 25 | `~/projects/shokunin/kagi-shokunin/corpus/knowledge/handler-trust-boundary.md:131, :246` | `http://127.0.0.1:8080/v1` (and the `34113` repair snippet) | 8080 | — (doc) | FOREIGN_SERVICE | kagi |
| 26 | `~/projects/shokunin/kagi-shokunin/corpus/knowledge/credential-isolation.md:35, :75` | `http://127.0.0.1:8080/v1` | 8080 | — (doc; `the-janitor status` prints it) | FOREIGN_SERVICE | kagi |
| 27 | `~/projects/shokunin/kagi-shokunin/corpus/knowledge/drift-gate.md:185` (`sed 's\|127.0.0.1:8080/v1\|127.0.0.1:34113/v1\|'`) | both | both | — (the one-command *repair* for #1/#6) | 8080 FOREIGN_SERVICE → 34113 MODEL_OK | kagi |
| 28 | `~/projects/shokunin/kumitate-shokunin/corpus/knowledge/ops-watchers.md:393` | `http://127.0.0.1:34113/v1/chat/completions` | 34113 | — (doc of #17) | MODEL_OK ✅ | kumitate |
| 29 | `~/projects/shokunin/kumitate-shokunin/corpus/knowledge/remaining-scripts-census.md:524` | `http://127.0.0.1:34113` (default) | 34113 | — (doc of #18) | MODEL_OK ✅ | kumitate |
| 30 | `~/projects/shokunin/.ufo/waves/round-9/seats/standing-tables.md:131, :243-244` | `~/.config/the-janitor/opencode.json:16` + `~/.config/opencode/opencode.json:158` | 8080 | — (fleet standing table: "D-85 drift persists") | FOREIGN_SERVICE | aggregator (fleet meta) |
| 31 | `~/.config/opencode/opencode.json.pre-qwen-model-20260829-031834.bak:50` | `http://localhost:8080/v1` | 8080 | `qwen-local` | — archival (superseded by #1) | unowned (archival) |
| 32 | `~/.config/opencode/opencode.json.pre-sentinel-disable-20260829-033405.bak:50` | `http://localhost:8080/v1` | 8080 | `qwen-local` | — archival | unowned (archival) |
| 33 | `~/.config/opencode/opencode.json.pre-fast-oauth-20260829.bak:155` | `http://localhost:8080/v1` | 8080 | `qwen-local` | — archival | unowned (archival) |
| 34 | `~/.config/opencode/opencode.json.bak-20260921-devin-slots:144` | `http://localhost:8080/v1` | 8080 | `qwen-local` | — archival | unowned (archival) |
| 35 | `~/.local/share/opencode/log/opencode.log:3898, 5281, 6194, 6308, …` | `http://localhost:8080/health`, `…/v1/models`, `…/v1/chat/completions` | 8080 | historical consumer **behavior** (permission-evaluated `curl` probes, all 2026-08-29T06:xxZ) | — historical: those probes *succeeded* then; the same paths now return the Jetty 404 (L1-F3) — the log is the pre-drift snapshot | kengaku/kagi (historical) |
| 36 | `~/Projects/ufo-fsd-alpha/tests/the-tick.test.js:61, :1457` (`endpoint: "http://127.0.0.1:34113/v1/chat/completions"`), `:125` (`http://192.168.1.1:34113/…`, non-loopback rejection fixture) — re-measured 2026-10-14 | `http://127.0.0.1:34113/v1/chat/completions` | 34113 | the-tick unit fixtures | **MODEL_OK** ✅ — *historical* | kumitate |
| 37 | `~/Projects/ufo-fsd-alpha/tests/local-helper.test.js:263-266` (`http://user:pass@127.0.0.1:8080`, `https://127.0.0.1:8080`, `…/?debug=1`, `…/#frag`) — re-measured 2026-10-14 | `127.0.0.1:8080` **as a rejection example** | 8080 | negative fixtures for `local-helper`'s `endpoint_invalid` gate (`:155-161`) | — not a pin: these four 8080 URLs are exactly the *shapes the helper must refuse*; incidental use of 8080 as a sample host | kumitate |
| 38 | `~/Projects/webzites/repos/ufo-fsd-alpha/config/the-tick.machine.json:16` and `…/scripts/local-helper.mjs:8` — **checkout deleted 2026-10 (§Errata); row kept as historical evidence** | `http://127.0.0.1:34113/v1/chat/completions` / `http://127.0.0.1:34113` | 34113 | **second, independent checkout** of the same repo (inode 20320717 vs 2916710; HEAD `0522e67a` vs `5725fa7d3`; both shared remote `origin` = `origin.cursor.com/jo-o-veiga/ufo-fsd-alpha.git`, while the `origin-work` tree additionally had `github` = `github.com/VeigaPunk/ufo-fsd-alpha.git` and a **dangling** `nc5-sandbox` = `/home/vgpnk/Projects/ephemeral/nc5/origin.git` — path absent, `git ls-remote nc5-sandbox` → `does not appear to be a git repository`) | **MODEL_OK** ✅ — *historical* | kumitate |

### Row that must not be forgotten: the reconciliation gap

**No consumer on this box declares the model id the server actually serves** — and this is *not*
limited to the stale 8080 family. Three independent executable sites declare the **bare** id
`Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS`:

- `~/.config/opencode/opencode.json:161` + `~/.config/opencode/agents/{janitor,distiller}.md:5`
- `~/.local/bin/the-janitor:17` (`MODEL_ID`) and `~/.config/the-janitor/opencode.json:8-9`
- the **correct-pin** family too: `~/Projects/ufo-fsd-alpha/config/the-tick.machine.json:13` (re-measured 2026-10-14; `origin-work/` path historical)
  (`"apiModel": "Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS"`) and
  `…/scripts/local-helper.mjs:9` (`DEFAULT_MODEL = "Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS"`)

`the-tick.machine.json` is the single best artifact for this lesson, because **one file carries both
id forms two lines apart** — `:12` `"path": "/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf"`
(the full path, exactly what the server reports) and `:13` `"apiModel": "Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS"`
(the bare id, what the request carries). The config already knows both; the reconciler is the only
component that has to decide which one to compare.

The live server exposes **only the full gguf path**, in every id-bearing key — measured, not
inferred:

```
curl -s http://127.0.0.1:34113/v1/models
→ {"models":[{"name":"/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf",
              "model":"/scratch/…gguf","capabilities":["completion"],…}],   ← note the key is name/model, NOT id
   "object":"list",
   "data":[{"id":"/scratch/…gguf","aliases":["/scratch/…gguf"],"owned_by":"llamacpp",
            "meta":{"n_ctx":16384,…}}]}                                  ← id + aliases, both full path
curl -s -o /dev/null -w '%{http_code}' \
  http://127.0.0.1:34113/v1/models/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS   # → 404
```

Two traps follow, both live-measured:

1. **A chat round-trip cannot see the mismatch.** llama.cpp *ignores* the requested model name:
   `POST /v1/chat/completions` with `{"model":"DEFINITELY-NOT-THE-MODEL", …}` → **HTTP 200**, and the
   response echoes `"model":"/scratch/…UD-IQ2_XXS.gguf"`. So every consumer above "works" while
   naming a model the server does not serve. Only a strict id comparison catches it.
2. **That strict comparison, per the binding contract, returns `MODEL_MISMATCH` on a healthy
   server** — because `models[].name`, `data[].id` and `data[].aliases` all carry the full path, and
   no key carries the bare id (`/v1/models/<bare-id>` → 404). So the normalisation
   (`basename` − `.gguf`, both sides; `(basename .gguf)` of `data[].id` == the declared id) is
   **mandatory**, not cosmetic: without it `check` cries wolf on the fixed port *and* the
   correct-pin family fails alongside the broken one. **This is the first thing kama's `check`
   subcommand has to get right.** [certain] — all three commands above were run this round.

This is the one rule this registry *cannot* leave implicit for the probe: the normalisation belongs
in the reconciler's comparison step (see `served-model-identity.md` for the exact `/props` readiness
fields it can read instead — `model_path` there returns the same full gguf path, so both sides of
the comparison should be normalised, not just the config side). `alias-endpoint-normalization.md:54`
already established that `~/.local/bin/the-janitor` is a *consumer* pin, not a dispatch alias; this
row is that file's other half — a consumer pin with a *correct* port and a *mismatched* model-id
form.

## Correct-pin exemplars (the fix already exists on this box)

| consumer path:line | pins | verdict |
|---|---|---|
| `~/Projects/ufo-fsd-alpha/config/the-tick.machine.json:16` (re-measured 2026-10-14 at HEAD `964f443e`) | 34113 | MODEL_OK — *historical: port dead today* |
| `~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs:8` (re-measured 2026-10-14) | 34113 | MODEL_OK — *historical: port dead today* |
| `~/Projects/webzites/repos/ufo-fsd-alpha/config/the-tick.machine.json:16` (2nd checkout — **tree deleted**, §Errata) | 34113 | MODEL_OK — *historical* |
| `~/Projects/webzites/repos/ufo-fsd-alpha/scripts/local-helper.mjs:8` (2nd checkout — **tree deleted**) | 34113 | MODEL_OK — *historical* |
| `~/projects/shokunin/kengaku-shokunin/PROVINCE.md:14` | 34113 | MODEL_OK — *historical: port dead today* |

**Two distinct checkouts, not one.** `~/Projects/origin-work/ufo-fsd-alpha` (inode 2916710, HEAD
`5725fa7d3`) and `~/Projects/webzites/repos/ufo-fsd-alpha` (inode 20320717, HEAD `0522e67a`) are
separate working trees with separate histories. Exact remotes (full `git remote -v`, *not* truncated):

```bash
git -C ~/Projects/origin-work/ufo-fsd-alpha remote -v
# github        https://github.com/VeigaPunk/ufo-fsd-alpha.git
# nc5-sandbox   /home/vgpnk/Projects/ephemeral/nc5/origin.git        ← local bare repo (fleet sync)
# origin        https://origin.cursor.com/jo-o-veiga/ufo-fsd-alpha.git
git -C ~/Projects/webzites/repos/ufo-fsd-alpha remote -v
# origin        https://origin.cursor.com/jo-o-veiga/ufo-fsd-alpha.git
```

Both trees **share** the cursor `origin`; only the `origin-work` tree additionally carries `github`
and the local `nc5-sandbox` bare repo. That shared origin is *why* both trees hold the same pin: the
34113 value is a repo-level convention that propagated through the fleet's sync, not a stray edit in
one clone. (Methodological note: a `git remote -v | head -2` reads as "these trees have different
remotes" — it shows only the alphabetically-first remote. Always read the full list.)

Discovering the second tree matters methodologically: `find /home/vgpnk/projects -maxdepth 6 -name
local-helper.mjs` returns **nothing**, because `/home/vgpnk/projects` (inode 101125103) and
`/home/vgpnk/Projects` (inode 27238) are **different directories** on this case-sensitive
filesystem. Any census rooted at the lowercase path silently misses this entire repo family.

*2026-10-14 errata:* the paragraph above is historical. One checkout survives —
`~/Projects/ufo-fsd-alpha` (inode 41021, HEAD `964f443e`) — whose remotes
re-measure as `cursor` → `origin.cursor.com/jo-o-veiga/ufo-fsd-alpha.git` and
`origin` → `github.com/VeigaPunk/ufo-fsd-alpha.git` (names swapped vs round 1;
`nc5-sandbox` gone). Both pin-bearing files still carry the 34113 value.

**Answer to the brief's "expected: none"**: expectation **falsified** — five shipped artifacts across
two checkouts (four executable configs + one lane doc) pin the live port. The stale 8080 pins and the
correct 34113 pins therefore coexist; nothing forces the 8080 family onto the 34113 family. Naming
this asymmetry is kama's core deliverable this round.

## Non-model loopback pins (same failure class, different surface)

Recorded for completeness; **not** kama's serving surface, and deliberately not given a model
verdict.

| consumer path:line | pins | what it is | live probe |
|---|---|---|---|
| `~/.config/opencode/agents/musketeer.md:26` | `http://localhost:9222` | Chrome CDP endpoint (grok/kimi browser automation) | `9222/v1/models` → HTTP 404 `text/html`; `ss` → `chrome` pid 3080080 listening → **NOT_HTTP / FOREIGN_SERVICE** for model purposes |
| `~/.omp/agent/skills/kimi-webbridge/SKILL.md:11, :42, :53, :64, :75, :91, :94, :164` and `references/operations.md:33` | `127.0.0.1:10086` | kimi-webbridge browser daemon | **DEAD** at probe time (connection refused; `ss` shows no 10086) |
| `~/.local/bin/omp:903216, :898347` and `~/.local/bin/omp.stock-18.2.2.bak:1241757` | `127.0.0.1:4000`, `127.0.0.1:8080`, `127.0.0.1:11434`, `127.0.0.1:1234` | omp bundled provider defaults (litellm/vllm/ollama/lm-studio/llama-cpp) | `4000` **DEAD**, `11434` **DEAD**, `1234` **DEAD** (no listener); `8080` FOREIGN_SERVICE |
| `~/.local/bin/omp:967010, :967012, :967018, :969792, :971785, :1095647, :1095675, :1095715` | `127.0.0.1:11434`, `localhost:4000/v1`, `127.0.0.1:8000/v1`, `127.0.0.1:1234/v1` | same bundled table (string constants in the binary) | all DEAD except 8080 |
| `~/Projects/webzites/repos/llm-wiki/README-SITE.md:15` | `http://127.0.0.1:8766/` | static-site preview server | **DEAD** (no listener) |
| `~/Projects/webzites/repos/llm-wiki/wiki/karpathy/projects-and-tools/local-first-ai-tools.md:63, :191` | `http://localhost:11434/v1` | **documentation prose** (Ollama tutorial), not a pin | 11434 **DEAD** — doc only, no consumer |
| `~/Projects/webzites/repos/llm-wiki/raw/gamedev/aseprite/docs-reference.md:989` | `ws://localhost:8080` | Aseprite extension WebSocket (unrelated to models) | n/a |
| `~/Projects/webzites/repos/llm-wiki/raw/gamedev/…:24, :13` (`8891`, `8890`, `8888`) | local static file servers | dev notes | n/a |

## Live verdicts — exact commands run (round 1)

```bash
# --- 8080 (the stale port) ---
curl -sSI --max-time 5 http://127.0.0.1:8080/
# → HTTP/1.1 404 Not Found ; Content-Type: text/html;charset=iso-8859-1 ; Content-Length: 342
curl -sS  --max-time 5 -X POST -H 'Content-Type: application/json' \
     -d '{"model":"x","messages":[]}' http://127.0.0.1:8080/v1/chat/completions
# → <html>… <h2>HTTP ERROR 404 Not Found</h2> <tr><th>URI:</th><td>http://127.0.0.1:8080/v1/chat/completions</td>…
curl -sS  --max-time 5 http://127.0.0.1:8080/v1/models      # → same Jetty HTML 404 (351 B), NOT JSON
curl -sS  --max-time 3 -o /dev/null -w 'code=%{http_code} ct=%{content_type} bytes=%{size_download}\n' \
     http://127.0.0.1:8080/metrics
# → code=200 ct=application/openmetrics-text;charset=utf-8;version=1.0.0 bytes=27461   (Jitsi jvb, not llama.cpp)
#   ⇒ 8080 verdict = FOREIGN_SERVICE (2xx text/html on /v1/* → FOREIGN_SERVICE per contract)

# --- 34113 (the live port) ---
curl -sS  --max-time 5 http://127.0.0.1:34113/v1/models
# → {"models":[{"name":"/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf",…,
#     "capabilities":["completion"],…}],"object":"list",…}   (872 B)
curl -sSI --max-time 5 http://127.0.0.1:34113/health
# → HTTP/1.1 200 OK ; Server: llama.cpp ; Content-Type: application/json; charset=utf-8
#   (note: Access-Control-Allow-Origin: http://127.0.0.1:8080 — the server's CORS origin still names the stale port)
curl -sS  --max-time 5 http://127.0.0.1:34113/health   # → {"status":"ok"}

# --- classification sweep of every loopback port a config names ---
for p in 8080 34113 11434 1234 10086 8790 8791 8766 40961 8888 9222 4000; do
  curl -sS -m 3 -o /dev/null -w "port $p /v1/models -> code=%{http_code} ct=%{content_type}\n" \
       "http://127.0.0.1:$p/v1/models"; done
# → 8080 code=404 ct=text/html…            FOREIGN_SERVICE
# → 34113 code=200 ct=application/json…   MODEL_OK
# → 11434,1234,10086,8766,40961,4000 code=000 (conn refused)  DEAD
# → 8790,8791 code=401 ct=application/json                    UNAUTHORIZED_SERVICE
# → 8888  curl: (56) Recv failure: Connection reset by peer    (jicofo; not HTTP on /v1)
# → 9222  code=404 ct=text/html                               (CDP; FOREIGN_SERVICE for model purposes)

# --- listener truth (also confirms L1-F1/F2) ---
ss -ltnp | grep -E '8080|34113|8790|8791|9222|8888'
# → 127.0.0.1:8791  omp pid 2997      127.0.0.1:8790  omp pid 1297
# → 127.0.0.1:8888  (no name)          127.0.0.1:9222  chrome pid 3080080
# → 127.0.0.1:8080  (no process name) 127.0.0.1:34113 llama-server pid 1299
```

### Transport-level corroboration: the stale port is contacted ~7× more than the live one

`ss -ltnp` shows listeners; `ss -tanp` adds the closed-socket tail, and the asymmetry there is
independent evidence that a real consumer is *still* talking to 8080:

```bash
ss -tanp > /tmp/ssa.txt; grep -nE '8080|34113' /tmp/ssa.txt    # 310 lines total
# 14:LISTEN     0 4096  127.0.0.1:8080   0.0.0.0:*                          ← jvb (docker-proxy), no proc name
# 21:LISTEN     0  512  127.0.0.1:34113  0.0.0.0:*  llama-server pid 1299
# 142-177: ~40× TIME-WAIT  127.0.0.1:586xx → 127.0.0.1:8080               ← host-level consumer churn
# 181:      TIME-WAIT  127.0.0.1:8080    → 127.0.0.1:59214
# 86-122:   ~35× TIME-WAIT  172.18.0.1:40xxx → 172.18.0.4:8080            ← Jitsi-internal (docker bridge), not a host consumer
# 242-247:   6× TIME-WAIT  127.0.0.1:594xx → 127.0.0.1:34113              ← the correct consumer, 6 connections
ss -tnp state established 2>/dev/null | grep -cE '8080|34113'   # → 0
```

Two readings, both actionable:

1. **~40 loopback TIME-WAITs against 8080 vs 6 against 34113** in the same snapshot ⇒ roughly 7×
   more host connections were made to the *stale* port in the preceding ~60 s than to the live one.
   The 8080 consumer family is not idle — it is being exercised, and failing, continuously.
   (The `172.18.0.1 → 172.18.0.4:8080` rows are Jitsi's own jvb↔jicofo traffic inside the Docker
   bridge and must **not** be counted as host consumers.)
2. **`ss -tnp` on this box prints 0 LISTEN rows** (`ss -ltnp` prints 23; `-tnp` prints 0), so a
   `ss -tnp`-based "no consumer of 34113" sweep is scanning the wrong table: it cannot see the
   listener at all, and it reports `TIME-WAIT` churn as absent. Any liveness sweep must use
   `-l` (listeners) or `-a` (all states), never bare `-t`. `[certain]` — command + counts above.

A prior peer observation ("omp auth-gateway pid 2997 has ESTAB to 127.0.0.1:8080") was **not
reproducible** on re-probe: ESTAB count to both ports is 0, and pid 2997 is
`omp auth-gateway serve --bind=127.0.0.1:8791`. The transient was real when observed but is not a
standing consumer; it is recorded here as a transient, not as a registry row.

## Search roots that produced ZERO local-endpoint pins

Absence is evidence: these are the surfaces a naive reader would expect to hold a local pin.

| root | exact command | result |
|---|---|---|
| `~/.config/opencode/skills/`, `tools/`, `plugin/`, `agent/`, `command/`, `tui.json` | `grep -rn -E 'localhost:[0-9]+\|127\.0\.0\.1:[0-9]+' ~/.config/opencode/skills ~/.config/opencode/tools ~/.config/opencode/plugin ~/.config/opencode/agent ~/.config/opencode/command ~/.config/opencode/tui.json` | **no matches** (exit 1). Only `opencode.json`, `agents/janitor.md`, `agents/musketeer.md` hold pins in that tree; `tools/janitor_auth.ts` and `plugin/fnm-nudge.js` hold none. |
| `~/.agents/` (skills + godspeed-core + AGENTS.md) | `grep -rn -E 'localhost:[0-9]+\|127\.0\.0\.1:[0-9]+' ~/.agents` | **no matches** (exit 1) |
| `/tmp/fleet-override.yml` | `grep -nE 'localhost:[0-9]+\|127\.0\.0\.1:[0-9]+\|base.?url' /tmp/fleet-override.yml` | **no matches** (exit 1). All 14 `agentModelOverrides` values are `@m_*` aliases (`@m_lunamax`, `@m_flash`, `@m_zfl`) that resolve to REMOTE providers through `~/.omp/agent/config.yml` — confirming L1-F11: the dispatch layer never resolves to a loopback baseURL. |
| `~/.omp/agent/config.yml` modelRoles / fallbackChains | `grep -n -E '127\.0\.0\.1\|localhost\|baseUrl\|baseURL' ~/.omp/agent/config.yml` | only hit is `:168` (`auth.broker.url`, an auth vault, not a model). **No model role carries a local baseURL.** |
| `~/Projects/ufo-fsd-alpha/.omp/` (config.yml, ufo-l1.yml, agents/, skills/, hooks/, ssot/) — re-measured 2026-10-14 at the relocated path | `grep -rn -E 'localhost:[0-9]+\|127\.0\.0\.1:[0-9]+' ~/Projects/ufo-fsd-alpha/.omp` | **no matches** (re-confirmed); the only "endpoint" strings remain prose — `skills/ufo/references/run-logic.md:495` and `skills/wwkd/SKILL.md:129` (re-measured; was `:556`/`:131`). Model routing there is remote. |
| `~/Projects/webzites/repos/llm-wiki` state/config surfaces (`state/librarian-config.yaml`, `scripts/`, `CLAUDE.md`, `README.md`) — **tree deleted 2026-10 (§Errata); historical** | `grep -rn -E '(localhost\|127\.0\.0\.1):(11434\|1234\|34113\|5000\|8000)' ~/Projects/webzites/repos/llm-wiki --exclude-dir=.git` | **no model-endpoint pins** (historical). `state/librarian-config.yaml` had no endpoint key; `scripts/vendor/scihub-paper-downloader.py` computed `base_url` from a *remote* URL. The only `11434` mentions were tutorial prose in `wiki/karpathy/…/local-first-ai-tools.md:63,:191`. |
| `~/.config/systemd/user/` as a *consumer* of a local model | `grep -rn -E 'localhost:[0-9]+\|127\.0\.0\.1:[0-9]+' ~/.config/systemd/user` | **zero local-*model* pins.** `qwen-coder.service` is the *server* (#9); `qwen-coder.ctx32k-q4.service`/`.bak` are disabled/archival server variants (#10/#11); `omp-auth-broker`, `omp-auth-gateway`, `kimi-auth-proxy` are auth proxies (#13-15), not model endpoints. |
| `~/projects/shokunin/kumitate-shokunin`, `kotoba-shokunin`, `kake-shokunin`, `kasegi-shokunin`, `.ufo/` (as *config*) | lane-wide sweep below | **no config pins**; every hit is prose/evidence in `corpus/**.md` (14 kotoba/kake hits are the `127.0.0.1:9222` CDP lease, 41 kagi hits are `8090/8080/40961` prose, 48 `.ufo` hits are round reports). Kumitate's 2 hits are *docs of #17/#18*, both 34113. |

Lane-level pin counts across `~/projects/shokunin` (docs + configs, excluding `node_modules`/`.git`):

```bash
grep -rn -E 'localhost:[0-9]+|127\.0\.0\.1:[0-9]+' ~/projects/shokunin \
  --include='*.md' --include='*.json' --include='*.yml' --include='*.yaml' \
  --include='*.tsv' --include='*.sh' --include='*.py' --include='*.js' \
  --exclude-dir=node_modules --exclude-dir=.git | sed -E 's|^.*/shokunin/([^/]+)/.*|\1|' | sort | uniq -c
#  144 kengaku-shokunin   48 .ufo   41 kagi-shokunin
#    3 kotoba-shokunin     2 kumitate-shokunin   2 kake-shokunin   1 kama-shokunin
```

`kama-shokunin`'s single hit is this census's own `PROVINCE.md`/docs, i.e. self-reference — before
this file, **no config on this box was owned by the serving lane.**

## Cross-lane demand evidence (why this registry exists)

- kagi round 3 (`.ufo/reports/round-3/kagi.md:23`): "`opencode.json` pins `127.0.0.1:8080/v1`" —
  endpoint drift found as a side-effect of vault work.
- kengaku round 4 (`.ufo/reports/round-4/kengaku.md:21-23`): same drift, found from the bench lane.
- `.ufo/waves/round-9/seats/standing-tables.md:131`: "config baseURLs … **identical** … **unchanged**
  — D-85 drift persists" (rows #1 and #6 were already byte-compared by the fleet and left unfixed).
- `.ufo/waves/round-9/seats/standing-tables.md:243-244`: "Live drift persists (D-85/D-39) …
  `localhost:8080/v1/models` → `404`; both configs still pin 8080."

Two independent lanes, five rounds apart, same unresolved row, no owning province. Rows #1 and #6
are still live exactly as recorded — re-verified this round.

## Open gaps (hand these to the next round)

1. **No writer exists for #1/#6.** The repair is a one-liner (`kagi-shokunin/corpus/knowledge/drift-gate.md:185`),
   but kama is chartered to *detect*, not to mutate other lanes' `~/.config`. Who applies it?
2. **Model-id normalisation** (see §reconciliation gap) — `check` must not flag the healthy port.
3. **`--cors-origins http://127.0.0.1:8080`** in `qwen-coder.service:16` means the *server itself*
   still advertises the stale origin; a browser consumer at 34113 would be CORS-rejected. Cross-check
   with kagi (request hygiene).
4. **`~/.local/bin/omp` builtin `llama-cpp` default is 8080** (#12): any omp session that selects that
   bundled provider without `LLAMA_CPP_BASE_URL` silently targets Jitsi. No `LLAMA_CPP_BASE_URL` is
   set in the environments checked (`~/.config/systemd/user/*`, `/tmp/fleet-override.yml`).
5. Whether `llama-server` on **34113** stays up across reboot — `qwen-coder.service` is enabled and
   running since 2026-09-28 02:55 (L1-F8), but `Restart=on-failure` with `StartLimitBurst=3` means a
   crash-loop ends in a silently dead endpoint that no consumer registry watches.

## Corrections — round 10 (2026-10-19)

*[correction 2026-10-19 (round 10, A19): `are still live exactly as recorded` at line 359 is stale (wc -l ~/.config/opencode/opencode.json; for p in ~/.config/the-janitor/opencode.json; do test -e "$p" && echo "present $p" || echo "absent $p"; done => 5 ~/.config/opencode/opencode.json ; absent ~/.config/the-janitor/opencode.json — shape-only, no body read); current anchor: `corpus/knowledge/consumer-registry.md:62-75; SKILL.md:35-47`]*

*[correction 2026-10-19 (round 10, A20): `No writer exists for #1/#6` at line 363 is stale (wc -l ~/.config/opencode/opencode.json; for p in ~/.config/the-janitor/opencode.json; do test -e "$p" && echo "present $p" || echo "absent $p"; done => 5 ~/.config/opencode/opencode.json ; absent ~/.config/the-janitor/opencode.json — shape-only, no body read); the former repair gap has no live #1/#6 target; current anchor: `corpus/knowledge/consumer-registry.md:62-66`]*

*[correction 2026-10-19 (round 10, A21): `qwen-coder.service:16` at line 366 is stale (for p in ~/.config/systemd/user/qwen-coder.service; do test -e "$p" && echo "present $p" || echo "absent $p"; done => absent ~/.config/systemd/user/qwen-coder.service — shape-only, no body read); no current unit evidence supports a CORS-origin or browser-rejection claim; current anchor: `corpus/knowledge/consumer-registry.md:56-75; SKILL.md:44-47`]*

*[correction 2026-10-19 (round 10, A22): `qwen-coder.service` at line 372 is stale (for p in ~/.config/systemd/user/qwen-coder.service; do test -e "$p" && echo "present $p" || echo "absent $p"; done => absent ~/.config/systemd/user/qwen-coder.service — shape-only, no body read); current anchor: `SKILL.md:44-47`]*

*[correction 2026-10-19 (round 10, A23): `Restart=on-failure` at line 373 is stale (for p in ~/.config/systemd/user/qwen-coder.service; do test -e "$p" && echo "present $p" || echo "absent $p"; done => absent ~/.config/systemd/user/qwen-coder.service — shape-only, no body read); current anchor: `SKILL.md:44-47`]*

*[correction 2026-10-19 (round 10, A24): `crash-loop ends in a silently dead endpoint` at line 374 is stale (for p in ~/.config/systemd/user/qwen-coder.service; do test -e "$p" && echo "present $p" || echo "absent $p"; done => absent ~/.config/systemd/user/qwen-coder.service — shape-only, no body read); current anchor: `SKILL.md:44-47`]*

*[correction 2026-10-19 (round 10, A51): `~/.local/bin/omp:1544771` at line 101 is stale (sed -n '53,54p' corpus/lessons/round-4-recensus.md => (the ':516' fix covered only one site); 'consumer-registry.md:101' locates the omp ; default at line 1544771 where the string is at newline-line 1149391;); current anchor: `UNDECIDABLE — exact offset not re-derived: the host binary body is not read in this round (KQ8, KQ5)`]*
