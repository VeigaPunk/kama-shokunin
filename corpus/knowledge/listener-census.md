# Listener census — every TCP listener on this host, by identity and verdict

**Measured:** 2026-09-28 ~22:47–22:52 -0300, host `plazir27`, live on-box probes.
**Method:** `sudo -n ss -ltnp` (passwordless — succeeded, so owner attribution is *measured*, not
inferred from docker/systemd heuristics), then one HTTP probe per loopback-reachable listener, then
`/proc/<pid>/{cmdline,cgroup,environ}` and `docker ps --no-trunc` / `docker inspect` for identity.
**Verdict vocabulary and classification rules** are the frozen L1 binding contract (see
`PROVINCE.md`); no vocabulary was added or renamed here. Where no rule fires verbatim, the row
names the gap in §9 instead of inventing a label.
**Cross-refs:** `corpus/knowledge/served-model-identity.md` (served id), `corpus/knowledge/drift-timeline.md`
(when the pin went stale), `corpus/knowledge/alias-endpoint-normalization.md` (id normalization).

---

## 0. Scope and completeness

* 23 TCP listeners total (`ss -ltn | tail -n +2 | wc -l` → `23`; `24` on the §7.1 re-check — the
  delta is omp session churn, measured not assumed).
* 20 are loopback-reachable; 3 are not (`172.17.0.1:53` docker0, `100.96.18.49:58075` and
  `[fd7a:115c:a1e0::162e:1232]:37803` tailscale0) — listed for completeness, marked
  `OUT-OF-LOOPBACK`.
* 1 listener is a **wildcard bind reachable via 127.0.0.1**: `0.0.0.0:40993` (also reachable on
  `192.168.0.253/24` and tailscale — §8).
* Every listener has a measured owner; `sudo -n ss -ltnp` resolved the 5 that non-privileged `ss`
  showed ownerless (`43999 containerd`, `8080 docker-proxy`, `8888 docker-proxy`,
  `53 systemd-resolve`, `631 cupsd`).
* UDP is out of scope (contract says TCP listeners); note `0.0.0.0:10000/udp` + `[::]:10000/udp`
  belong to `docker-jitsi-meet-jvb-1` (`docker inspect`).

### 0.1 Two sweep traps, both hit and verified in this round

1. **`ss -tnp` cannot see listeners.** `ss -tnp | grep -c LISTEN` → `0`; `ss -ltnp | grep -c LISTEN`
   → `23`. A port sweep built on bare `ss -tnp` silently misses the listener it is looking for
   (listeners need `-l`; connections need `-a` / `state established`).
2. **`/home/vgpnk/projects` ≠ `/home/vgpnk/Projects`** — two distinct directories
   (`stat -c '%n inode=%i'` → inode `101125103` vs `27238`), and the `ufo-fsd-alpha` checkouts live
   only under the **capital** root (`find /home/vgpnk/projects -maxdepth 3 -name ufo-fsd-alpha` →
   nothing). This census's own repo is under the lowercase tree, so a consumer sweep rooted at the
   wrong case concludes "unverifiable" instead of "not searched here". Both traps were reported by
   peer lanes and re-verified here before being applied.

## 1. Census — one row per listener

`SC` = stability class: `stable` (survives reboot/session), `session` (dies with the owning
process), `churn` (ephemeral port re-picked per process start).

| # | Bind addr:port | SC | Owner — measured evidence | `GET /` | `Server` header | `/v1/models` | Verdict (frozen vocab) | Rule that fired | Cmd |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `127.0.0.1:34113` | stable | `llama-server` pid **1299**, cgroup `…/user@1000.service/app.slice/qwen-coder.service` (sudo `ss -ltnp`; `/proc/1299/cmdline`) | `404` `application/json` | **`llama.cpp`** | **`200` JSON `models[]`** | `MODEL_MISMATCH` *(vs consumer-declared id)* / `MODEL_OK` *(vs own `--alias`)* | 2xx JSON + `models[]` + `Server: llama.cpp` → id compare | C1,C2,C7 |
| 2 | `127.0.0.1:8080` | stable | `docker-proxy` pid **2245** → container `172.18.0.4` = `docker-jitsi-meet-jvb-1` `bda15c10…` (sudo `ss -ltnp` + `docker inspect`) | `404` `text/html;charset=iso-8859-1` (Jetty) | *(none)* | `404` text/html | `FOREIGN_SERVICE` — **drift signature** | HTTP responder, not the model API (no `models[]`, no `llama.cpp`) | C1,C3,C8 |
| 3 | `127.0.0.1:8888` | stable | `docker-proxy` pid **2416** → container `172.18.0.5` = `docker-jitsi-meet-jicofo-1` `f92b0236…` | TCP accept → **RST, 0 bytes** (`curl (56)`, raw `/dev/tcp` too) | *(none)* | *(none — reset)* | `NOT_HTTP` | connection accepted, non-HTTP/zero-byte exchange | C1,C4 |
| 4 | `127.0.0.1:8790` | stable | `omp` pid **1297**, `omp auth-broker serve --bind=127.0.0.1:8790`, unit `omp-auth-broker.service` | `401` `application/json` `{"error":"unauthorized"}` | *(none)* | `401` JSON | `UNAUTHORIZED_SERVICE` | HTTP 401 | C1,C5,C9 |
| 5 | `127.0.0.1:8791` | stable | `omp` pid **2997**, `omp auth-gateway serve --bind=127.0.0.1:8791`, unit `omp-auth-gateway.service` | `401` `application/json` `{"error":"unauthorized"}` | *(none)* | `401` JSON | `UNAUTHORIZED_SERVICE` | HTTP 401 | C1,C5,C10 |
| 6 | `127.0.0.1:4226` | session | `sccache` pid **836055** (`RUSTC_WRAPPER=sccache`, `SCCACHE_IDLE_TIMEOUT=0`) | TCP accept → **0 bytes**, server closes (`curl (52)`) | *(none)* | *(none)* | `NOT_HTTP` | non-HTTP protocol (sccache server RPC) | C1,C6 |
| 7 | `127.0.0.1:43999` | stable | `containerd` pid **1228**, `/usr/bin/containerd`, `v2.3.4` (sudo `ss -ltnp`) | `404` `text/plain` `404: Page Not Found` | *(none)* | `404` text/plain | `FOREIGN_SERVICE` | HTTP responder, not the model API | C1,C11 |
| 8 | `127.0.0.1:9222` | session | `chrome` pid **3080080**, `--remote-debugging-address=127.0.0.1 --remote-debugging-port=9222` | `200` `text/html; charset=UTF-8` (**empty body**) | *(none)* | `404` text/html | `FOREIGN_SERVICE` | 2xx `text/html` (**verbatim rule**) | C1,C12 |
| 9 | `127.0.0.1:631` | stable | `cupsd` pid **1207**, `/usr/bin/cupsd -l` | `200` `text/html; charset=utf-8` | `CUPS/2.4 IPP/2.1` | `404` text/html | `FOREIGN_SERVICE` | 2xx `text/html` (**verbatim rule**) | C1 |
| 10 | `[::1]:631` | stable | `cupsd` pid **1207** (dual-stack sibling of #9) | `200` `text/html; charset=utf-8` (same CUPS page via `::1`) | `CUPS/2.4 IPP/2.1` | `404` text/html | `FOREIGN_SERVICE` | 2xx `text/html` (**verbatim rule**) | C1,C16 |
| 11 | `0.0.0.0:40993` | session | `python3` pid **2360094**, `python3 -m http.server --bind 0.0.0.0 40993`, cwd `/tmp` | `200` `text/html; charset=utf-8` — **directory listing of `/tmp`** | `SimpleHTTP/0.6 Python/3.14.7` | `404` text/html | `FOREIGN_SERVICE` | 2xx `text/html` (**verbatim rule**) | C1,C13 |
| 12 | `127.0.0.1:45507` | churn | `omp` pid **801987**, `omp --model @m_qwen … kasegi-round-16.md` | `404` `text/plain;charset=utf-8` `Not Found` | *(none)* | `404` text/plain | `FOREIGN_SERVICE` | HTTP responder, not the model API | C1,C14 |
| 13 | `127.0.0.1:46631` | churn | `omp` pid **1671602**, `omp --model @m_flash … kagi-round-15.md` | `404` `text/plain;charset=utf-8` | *(none)* | `404` text/plain | `FOREIGN_SERVICE` | HTTP responder, not the model API | C1,C14 |
| 14 | `127.0.0.1:43775` | churn | `omp` pid **1668421**, `omp --model @m_flash … kumitate-round-15.md` | `404` `text/plain;charset=utf-8` | *(none)* | `404` text/plain | `FOREIGN_SERVICE` | HTTP responder, not the model API | C1,C14 |
| 15 | `127.0.0.1:44689` | churn | `omp` pid **1859348**, `omp --model @m_flash … kotoba-round-15.md` | `404` `text/plain;charset=utf-8` | *(none)* | `404` text/plain | `FOREIGN_SERVICE` | HTTP responder, not the model API | C1,C14 |
| 16 | `127.0.0.1:41453` | churn | `omp` pid **1053353**, `omp --model @m_qwen … kengaku-round-12.md` | `404` `text/plain;charset=utf-8` | *(none)* | `404` text/plain | `FOREIGN_SERVICE` | HTTP responder, not the model API | C1,C14 |
| 17 | `127.0.0.1:41819` | churn | `omp` pid **3636400**, `omp --session-dir …/ufo-fsd-alpha/… --model @m_flash` (clean-siblings L1) | `404` `text/plain;charset=utf-8` | *(none)* | `404` text/plain | `FOREIGN_SERVICE` | HTTP responder, not the model API | C1,C14 |
| 18 | `127.0.0.1:34955` | churn | `omp` pid **3467459**, `omp --model @m_qwen … protocol-round-13.md` | `404` `text/plain;charset=utf-8` | *(none)* | `404` text/plain | `FOREIGN_SERVICE` | HTTP responder, not the model API | C1,C14 |
| 19 | `127.0.0.53:53` | stable | `systemd-resolve` pid **816** (sudo `ss -ltnp`) | TCP accept, **no HTTP bytes** | *(none)* | *(none)* | `NOT_HTTP` | DNS-over-TCP stub, non-HTTP protocol | C1,C15 |
| 20 | `127.0.0.54:53` | stable | `systemd-resolve` pid **816** (sudo `ss -ltnp`) | TCP accept, **no HTTP bytes** | *(none)* | *(none)* | `NOT_HTTP` | DNS-over-TCP stub, non-HTTP protocol | C1,C15 |
| 21 | `172.17.0.1:53` | stable | `systemd-resolve` pid **816** | *(not loopback — docker0)* | — | — | `NOT_HTTP` · `OUT-OF-LOOPBACK` | non-HTTP protocol | C1 |
| 22 | `100.96.18.49:58075` | session | `tailscaled` pid **1069** | *(not loopback — tailscale0)* | — | — | `NOT_HTTP` · `OUT-OF-LOOPBACK` | non-HTTP protocol | C1 |
| 23 | `[fd7a:115c:a1e0::162e:1232]:37803` | session | `tailscaled` pid **1069** | *(not loopback — tailscale0)* | — | — | `NOT_HTTP` · `OUT-OF-LOOPBACK` | non-HTTP protocol | C1 |

Row 1 detail (the model row, because its verdict is two-valued):

```json
GET http://127.0.0.1:34113/v1/models   → 200, Server: llama.cpp
{"models":[{"name":"/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf",
            "model":"/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf",
            "capabilities":["completion"], …}],
 "object":"list",
 "data":[{"id":"/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf",
          "aliases":["/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf"],
          "object":"model","owned_by":"llamacpp", …}]}
```

* `MODEL_OK` against the listener's *own* declared identity: `--alias` (`qwen-coder.service:19`)
  and served `id` are byte-identical.
* `MODEL_MISMATCH` against the *consumer-declared* expected id `Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS`
  (registry row for `~/.config/opencode/opencode.json`): served `id` is the **full GGUF path**, and
  `--alias` was set to that path, so the bare model key never matches. Repointing `baseURL` alone
  does **not** clear the mismatch — see §4 and `alias-endpoint-normalization.md`.

## 2. Family separation (assignment item 3)

| Family | Listeners | Verdicts | Identity evidence |
|---|---|---|---|
| **Model serving** | `127.0.0.1:34113` | `MODEL_OK`/`MODEL_MISMATCH` (id axis) | pid 1299 `llama-server`, unit `qwen-coder.service`, `Server: llama.cpp`, `models[]` |
| **Auth-protected API** | `127.0.0.1:8790`, `127.0.0.1:8791` | `UNAUTHORIZED_SERVICE` ×2 | pids 1297/2997 = `omp auth-broker` / `omp auth-gateway` units; both answer `401` `{"error":"unauthorized"}` |
| **Docker-proxied services** | `127.0.0.1:8080` (jvb), `127.0.0.1:8888` (jicofo) | `FOREIGN_SERVICE`, `NOT_HTTP` | `docker-proxy` pids 2245/2416 → `172.18.0.4`/`172.18.0.5` = `docker-jitsi-meet-jvb-1`/`-jicofo-1` |
| **omp session/agent ephemeral** | `45507, 46631, 43775, 44689, 41453, 41819, 34955` | `FOREIGN_SERVICE` ×7 | 7 `omp` pids, each a fleet/`ufo-fsd` L1–L2 session (see §1 rows 12–18) |
| **Build/daemon ephemeral** | `127.0.0.1:4226` (sccache), `127.0.0.1:43999` (containerd) | `NOT_HTTP`, `FOREIGN_SERVICE` | pids 836055, 1228 |
| **Platform/system** | `631` (`+ [::1]:631`), `127.0.0.53:53`, `127.0.0.54:53`, `9222` | `FOREIGN_SERVICE` ×4, `NOT_HTTP` ×2 | cupsd pid 1207, systemd-resolve pid 816, chrome pid 3080080 |
| **Non-loopback (excluded)** | `172.17.0.1:53`, `100.96.18.49:58075`, `[fd7a:…]:37803` | `NOT_HTTP` ×3 | systemd-resolve, tailscaled |

## 3. Consumer → listener reconciliation (declared vs actual)

| Consumer pin (verbatim) | Declared target | Declared model id | Listener at that target | Reconciles? |
|---|---|---|---|---|
| `~/.config/opencode/opencode.json:158` `"baseURL": "http://localhost:8080/v1"` | 8080 | `Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` (`:161`) | **Jitsi JVB** → `FOREIGN_SERVICE` | **NO — drift** |
| `~/.config/opencode/agents/janitor.md:21` "`http://127.0.0.1:8080/v1`; there is no fallback" | 8080 | same (`:5`) | Jitsi JVB | **NO — drift, no fallback** |
| `~/.config/opencode/agents/distiller.md:5,7` `qwen-local/…` + cloud cascade | 8080 (via provider) | same | Jitsi JVB | **NO — drift, cascade-protected** |
| `~/.local/bin/the-janitor:19` `MODEL_ENDPOINT="http://127.0.0.1:8080/v1"` | 8080 | same (`:17`) | Jitsi JVB | **NO — drift** |
| `~/.omp/agent/config.yml:166-168` (`auth:` 166, `broker:` 167, `url:` **168**) `auth.broker.url: http://127.0.0.1:8790` | 8790 | n/a (vault) | `omp auth-broker` → `401` JSON | **YES** — 401 is the expected unauthenticated answer |
| omp built-in llama.cpp provider default (binary string, `strings omp`) `baseUrl: Bun.env.LLAMA_CPP_BASE_URL \|\| "http://127.0.0.1:8080"` | 8080 | n/a | Jitsi JVB | **NO — drift (code-level default)** |
| **`~/Projects/ufo-fsd-alpha/config/the-tick.machine.json:16`** `"endpoint": "http://127.0.0.1:34113/v1/chat/completions"` — re-measured 2026-10-14 after relocation (`origin-work/` path historical; HEAD `964f443e`) | 34113 | `:13` `"apiModel": "Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS"` (bare id) while `:12` `"path"` is the full GGUF path — **one file carries both id forms** | `llama-server` `MODEL_OK` — *historical: 34113 connection-refused today* | **YES (endpoint)** — the one correctly-pinned family |
| `~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs:8` `const DEFAULT_URL = "http://127.0.0.1:34113"` — re-measured | 34113 | same (`:9` `DEFAULT_MODEL` = bare id) | `llama-server` `MODEL_OK` — *historical* | **YES (endpoint)** |
| `~/Projects/ufo-fsd-alpha/tests/the-tick.test.js:61,:1457` `endpoint: "http://127.0.0.1:34113/v1/chat/completions"` — re-measured (was `:87,:1858`) | 34113 | fixtures | `llama-server` — *historical* | **YES (fixture)** |
| **`~/Projects/webzites/repos/ufo-fsd-alpha/config/the-tick.machine.json:16`** + `scripts/local-helper.mjs:8` — **checkout deleted 2026-10; historical** | 34113 | as above | `llama-server` `MODEL_OK` — *historical* | **YES (endpoint)** — two independent trees, same correct pin |

Remote detail (measured, `git remote -v` untruncated): the two trees **share `origin`**
`https://origin.cursor.com/jo-o-veiga/ufo-fsd-alpha.git` — same repo-level convention, which is why
both carry the 34113 pin. Only `origin-work` has more: `github` →
`https://github.com/VeigaPunk/ufo-fsd-alpha.git`, plus a **dangling** `nc5-sandbox` →
`/home/vgpnk/Projects/ephemeral/nc5/origin.git` (that path does not exist: `ls` → *No such file or
directory*, and `find …/ephemeral -maxdepth 3 -name origin.git` → nothing). Report-only for the
owning lane.
| *any* consumer of `34113` inside `~/.omp/agent/config.yml`, `~/.config/opencode/`, `~/.local/bin/`, shell rc | — | — | `llama-server` | **NONE — scoped negative, not box-wide** (the ufo-fsd-alpha rows above falsify a box-wide reading) |

Correction provenance: the scoped negative was independently widened and falsified by the
consumer-scout lane (`corpus/knowledge/consumer-registry.md` §"Transport-level corroboration");
the `ufo-fsd-alpha` rows above were re-verified here (`sed -n '14,20p' config/the-tick.machine.json`,
`sed -n '5,12p' scripts/local-helper.mjs`, `grep -n 34113 tests/the-tick.test.js`).

Evidence for the scoped negative and the drift asymmetry (measured, this session):

```sh
grep -rn '34113' ~/.omp/agent/config.yml ~/.config/opencode/ ~/.bashrc ~/.zshrc ~/.profile   # → no match
env | grep -iE 'LLAMA|BASE_URL|OLLAMA|LM_STUDIO'                                             # → empty
ss -tanp state established | grep -c '127.0.0.1:34113'                                       # → 0 (no live consumer)
ss -tanp state established | grep -c '127.0.0.1:8080'                                        # → 0 at 23:0x
ss -ltnp | grep ':34113'                                                                     # → llama-server pid 1299 LISTEN
```

> **Method warning (verified):** `ss -tnp` shows **non-listening** sockets only —
> `ss -tnp | grep -c LISTEN` → `0`, while `ss -ltnp | grep -c LISTEN` → `23`. Any sweep that greps
> bare `ss -tnp` for a port can never see that port's *listener*. Use `-l` for listeners and
> `-a`/`state established` for connections; the two questions need two different invocations.

**Drift, observed twice — once transient, once durable:**

1. *Transient (22:52):* `omp auth-gateway` (pid 2997, the 8791 listener) held **2 ESTABLISHED
   sockets to `127.0.0.1:8080`** (`ss -tnp | grep ':8080' | grep omp` → `pid=2997 fd=22` / `fd=23`,
   with the matching server-side pair; both sides present ⇒ a real connection, not an artifact).
   Three re-samples ~20 min later returned `0` for 8080 **and** `0` for 34113 — so that was a
   transient connect-and-hang-up, *not* a standing consumer. Recorded as observed-then-absent.
2. *Durable (TIME-WAIT churn, 23:0x–23:1x):* the closed-socket tail shows the stale port being
   used far more than the live one:

   | Sample | host → `127.0.0.1:8080` | host → `127.0.0.1:34113` | ratio | `172.18.0.1 → 172.18.0.4:8080` |
   |---|---|---|---|---|
   | T0 | **62** | **12** | 5.2× | 62 |
   | T+20 s | **26** | **6** | 4.3× | *(not re-counted)* |

   `ss -tanp | awk '$1=="TIME-WAIT" && $4 ~ /^127\.0\.0\.1:[0-9]+$/ {print $5}' | sort | uniq -c | sort -rn`
   → `26 127.0.0.1:8080` / `6 127.0.0.1:34113` (plus 2 each for 8790/8791/9222/46631 = ordinary
   local chatter). The `172.18.0.1 → 172.18.0.4:8080` rows are **Jitsi-internal / docker-proxy**
   legs on the bridge and are *not* host consumers — excluded from the ratio.
   `[INFERENCE]` the clients are host processes using the 8080 pin (the omp llama.cpp-provider
   default is the prime candidate); TIME-WAIT entries carry no pid, so the *who* is not citable.

## 4. Drift flags — TCP accepts, but not the service its consumers expect

| Port | Accepts TCP | What consumers expect | What is actually there | Signature |
|---|---|---|---|---|
| **8080** | yes | llama.cpp OpenAI API `GET /v1/models`, `POST /v1/chat/completions` returning JSON | Jetty `HTTP ERROR 404` HTML page, `Content-Type: text/html;charset=iso-8859-1`, body has `URI/STATUS/MESSAGE` table | `POST /v1/chat/completions` → `404` **text/html**, not JSON (L1-F3, re-confirmed: `code=404 ct=text/html;charset=iso-8859-1`) |
| **34113** | yes | llama.cpp OpenAI API (**the `ufo-fsd-alpha` family does declare it**: `config/the-tick.machine.json:16`, `scripts/local-helper.mjs:8`) | the real model, `Server: llama.cpp`, serves `models[]` | *correct*: right service at the right address — **but** the id axis below still bites this family |
| **the id axis** | — | id `Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` (`local-helper.mjs:9`, `the-tick.machine.json:13` `apiModel`, `opencode.json:161`, `the-janitor:17`, `janitor.md:5`) | id `/scratch/models/qwen3-coder-30b/…IQ2_XXS.gguf` (in `data[].id` and `data[].aliases`; `models[]` has **no** `id` key at all) | repointing `baseURL` 8080→34113 still yields `MODEL_MISMATCH` unless `--alias` is normalized (or an `aliases` entry added) |
| **id axis is invisible to round-trips** | — | the correct-pin family sends the bare id | llama.cpp ignores the requested name outright: `POST /v1/chat/completions` with `{"model":"DEFINITELY-NOT-THE-MODEL"}` → **`200`**, and the response echoes `"model":"/scratch/…gguf"` | measured: a functional probe **cannot** detect this; only `GET /v1/models` + a compare against `data[].id` catches it. `GET /v1/models/<bare-id>` → `404 {"error":{"message":"File Not Found","type":"not_found_error"}}` |
| **40961** | **no** | `the-janitor:15` `PORT="${THE_JANITOR_PORT:-40961}"` | no listener (`ss -ltn \| grep -c ':40961'` → `0`) | second-order staleness: the same script's port pin is also dead |
| **8080 (latent)** | — | — | `~/.config/systemd/user/qwen-coder.ctx32k-q4.service:16` (disabled) carries `--port 8080` | `[INFERENCE]` enabling it would fight `docker-proxy` pid 2245 for the bind and fail/win nondeterministically |

## 5. Command ledger (verbatim; each table row cites these)

```sh
# C1 — listener + owner inventory (the census source)
sudo -n ss -ltnp                      # passwordless sudo OK; 23 rows; every listener attributed
ss -ltn                               # unprivileged cross-check (5 owners hidden: 43999,8080,8888,53,631)

# C2 — model listener identity
curl -sS http://127.0.0.1:34113/v1/models          # 200 JSON, models[] + data[].id = full GGUF path
curl -sS http://127.0.0.1:34113/health             # {"status":"ok"}
curl -sS http://127.0.0.1:34113/props              # model_alias == model_path == full GGUF path
curl -sS http://127.0.0.1:34113/slots              # 2 slots, n_ctx 16384

# C3 — the drift port
curl -sS -D - -o /tmp/b http://127.0.0.1:8080/                 # 404 text/html;charset=iso-8859-1 (Jetty)
curl -sS -o /dev/null -w 'code=%{http_code} ct=%{content_type}\n' \
     -X POST -H 'content-type: application/json' -d '{"model":"x","messages":[]}' \
     http://127.0.0.1:8080/v1/chat/completions                 # code=404 ct=text/html;charset=iso-8859-1

# C4 — jicofo port: TCP accept then reset (not HTTP)
curl -sS -m 3 http://127.0.0.1:8888/                          # curl: (56) Recv failure: Connection reset by peer
timeout 3 bash -c 'exec 3<>/dev/tcp/127.0.0.1/8888; printf "GET / HTTP/1.0\r\n\r\n" >&3; head -c 200 <&3'
                                                               # same reset; no bytes ever returned

# C5 — auth-protected API ports
curl -sS -D - http://127.0.0.1:8790/ ; curl -sS -D - http://127.0.0.1:8791/
                                                               # 401 application/json {"error":"unauthorized"} ×2
curl -sS -o /dev/null -w '%{http_code}\n' -H 'Authorization: Bearer x' http://127.0.0.1:8790/   # 401

# C6 — sccache (accepts, closes silently)
curl -sS -m 3 http://127.0.0.1:4226/                          # curl: (52) Empty reply from server

# C7 — owner attribution (privileged)
tr '\0' ' ' < /proc/1299/cmdline ; tr '\n' ' ' < /proc/1299/cgroup
cat -n ~/.config/systemd/user/qwen-coder.service              # lines 13-23: --port 34113, --alias <full path>

# C8 — docker owner attribution
docker ps --no-trunc --format '{{.ID}}\t{{.Names}}\t{{.Ports}}'
docker inspect -f '{{.Id}} ip={{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}} ports={{json .NetworkSettings.Ports}}' docker-jitsi-meet-jvb-1
tr '\0' ' ' < /proc/2245/cmdline                              # docker-proxy … -host-port 8080 -container-ip 172.18.0.4

# C9 — broker unit + config consumer
systemctl --user status omp-auth-broker.service --no-pager    # Main PID 1297
grep -nE 'auth:|broker:|url: http://127\.0\.0\.1:8790|token:' ~/.omp/agent/config.yml | sed -E 's/(token:).*/\1 <redacted>/'
                                                              # → 166 auth: / 167 broker: / 168 url: http://127.0.0.1:8790 / 169 token: <redacted>
                                                              # NOTE: line 169 holds a live credential — its value is deliberately NOT reproduced anywhere in this repo

# C10 — gateway unit + live drift sockets
systemctl --user status omp-auth-gateway.service --no-pager   # Main PID 2997
ss -tnp | grep ':8080'                                        # omp pid=2997 fd=22/23 ESTAB → 127.0.0.1:8080
ss -tnp | grep ':34113'                                       # NONE

# C11 — containerd identity
containerd --version                                          # github.com/containerd/containerd/v2 v2.3.4
ls -la /run/containerd/containerd.sock                        # srw-rw---- root root (production socket is the unix socket)
containerd config default | grep -nE -A3 '^\[debug\]|address = '   # no TCP debug address; address = '/run/containerd/containerd.sock'
curl -sS -m 2 http://127.0.0.1:43999/debug/pprof/             # 404 text/plain '404: Page Not Found'
                                                              # (also /, /metrics, /healthz, /v2/ → same 404)

# C12 — chrome devtools
curl -sS http://127.0.0.1:9222/json/version                   # Browser Chrome/152.0.7977.64; ws://127.0.0.1:9222/devtools/browser/…
tr '\0' '\n' < /proc/3080080/cmdline | grep remote-debugging  # --remote-debugging-port=9222 --remote-allow-origins=…

# C13 — python wildcard server serving /tmp
readlink -f /proc/2360094/cwd                                 # /tmp
tr '\0' ' ' < /proc/2360094/cmdline                           # python3 -m http.server --bind 0.0.0.0 40993
curl -sS http://127.0.0.1:40993/ | grep -oE '<a href="[^"]+">[^<]*</a>' | head
                                                              # directory listing incl. 1Password-1000/, .X0-lock, a.txt, …

# C14 — omp session ports (7 rows)
for p in 801987 1671602 1668421 1859348 1053353 3636400 3467459; do tr '\0' ' ' < /proc/$p/cmdline; echo; done

# C15 — DNS stubs / non-HTTP verify
timeout 3 bash -c "exec 3<>/dev/tcp/127.0.0.53/53; printf 'GET / HTTP/1.0\r\n\r\n' >&3; head -c 120 <&3"   # no bytes (rc from timeout)

# C16 — IPv6 loopback cupsd (row 10)
curl -sS -m 3 -D - -o /dev/null "http://[::1]:631/"                        # 200 text/html; Server: CUPS/2.4 IPP/2.1
curl -sS -m 3 -o /dev/null -w 'code=%{http_code} ct=%{content_type}\n' "http://[::1]:631/v1/models"   # 404 text/html

# C17 — connection-state method + drift asymmetry (§3)
ss -tnp  | grep -c LISTEN                                    # 0  ← -tnp cannot see listeners
ss -ltnp | grep -c LISTEN                                    # 23 ← listeners need -l
ss -tanp state established | grep -c '127.0.0.1:8080'         # 0 (transient pair at 22:52 had been 2)
ss -tanp state established | grep -c '127.0.0.1:34113'        # 0
ss -tanp | awk '$1=="TIME-WAIT" && $4 ~ /^127\.0\.0\.1:[0-9]+$/ {print $5}' | sort | uniq -c | sort -rn
                                                              # 26 127.0.0.1:8080 / 6 127.0.0.1:34113 (T+20s); T0 was 62 / 12

# C18 — correct-pin family (§3)
sed -n '14,20p' ~/Projects/ufo-fsd-alpha/config/the-tick.machine.json   # "endpoint": "http://127.0.0.1:34113/v1/chat/completions" + parallelSlots 2 / contextTokens 16384 (re-measured 2026-10-14; origin-work/ path historical)
sed -n '5,12p'  ~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs       # DEFAULT_URL = "http://127.0.0.1:34113", DEFAULT_MODEL = bare model id
grep -n '34113' ~/Projects/ufo-fsd-alpha/tests/the-tick.test.js         # :61, :125, :1457 (re-measured; was :87, :1858)

# C19 — id-axis invisibility + the two-checkout / path-case facts (§0.1, §3, §4)
curl -sS -o /tmp/b -w 'code=%{http_code}\n' -X POST -H 'content-type: application/json' \
     -d '{"model":"DEFINITELY-NOT-THE-MODEL","messages":[{"role":"user","content":"hi"}],"max_tokens":1}' \
     http://127.0.0.1:34113/v1/chat/completions        # code=200, response "model":"/scratch/…UD-IQ2_XXS.gguf"
curl -sS -o /dev/null -w 'code=%{http_code}\n' \
     http://127.0.0.1:34113/v1/models/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS   # 404 not_found_error
curl -sS http://127.0.0.1:34113/v1/models | python3 -c 'import json,sys;d=json.load(sys.stdin);print(sorted(d["models"][0]),sorted(d["data"][0]))'
                                                       # models[]: no id key; data[]: id + aliases (both full path)
for d in ~/Projects/ufo-fsd-alpha; do git -C $d rev-parse --short HEAD; git -C $d remote -v; done
                                                       # 964f443e; cursor→cursor.com…, origin→github.com… (2026-10-14; the second checkout and the old remote set are historical)
stat -c '%n inode=%i' /home/vgpnk/projects /home/vgpnk/Projects    # 101125103 vs 27238 — different directories
find /home/vgpnk/projects -maxdepth 3 -name 'ufo-fsd-alpha'        # nothing (checkouts are under the capital root)
sed -n '11,17p' ~/Projects/ufo-fsd-alpha/config/the-tick.machine.json   # :12 path (gguf), :13 apiModel (bare id), :16 endpoint 34113
```

## 6. Measured vs inferred

**Measured (command output / file bytes):** the 23 listener rows, every port number and bind address,
every pid and cgroup, all `docker ps`/`docker inspect` container ids and IP maps, every HTTP status,
`Content-Type` and `Server` header above, the served `models[]`/`data[].id`, `containerd --version`,
`/proc/<pid>/cmdline` contents, `the-janitor` `PORT=40961` with no listener, the transient ESTAB
socket pair (pid 2997 → 8080 at 22:52; absent on 3 re-samples), the TIME-WAIT counts (62/12 at T0,
26/6 at T+20 s), the `[::1]:631` CUPS response (C16), the `ss -tnp` vs `ss -ltnp` listener blind
spot (0 vs 23 LISTEN lines), the four `ufo-fsd-alpha` `34113` pins **in both checkouts**, the
bogus-model-name round-trip (`{"model":"DEFINITELY-NOT-THE-MODEL"}` → `200`), `GET /v1/models/<bare-id>`
→ `404`, `models[]` carrying no `id` key while `data[]` carries `id`+`aliases`, the `projects` vs
`Projects` inode split, and the absence of any `34113` reference inside `~/.omp/agent/config.yml`,
`~/.config/opencode/`, `~/.local/bin/` and the shell rc files.

**`[INFERENCE]`:** (a) the *purpose* of `127.0.0.1:43999` (owner is measured = containerd pid 1228;
the port is absent from `containerd config default`, so it is set by a flag/env outside
`/etc/containerd/` — the config directory does not exist on this host); (b) *who* opened the
connections that left TIME-WAIT on 8080 (TIME-WAIT carries no pid; the omp binary's
`LLAMA_CPP_BASE_URL || "http://127.0.0.1:8080"` default is the candidate, and the transient pid 2997
pair is corroborating but not conclusive); (c) the enable-`ctx32k-q4.service` bind conflict;
(d) that `python3 -m http.server`'s owner session is a fleet session (the pid/cgroup are measured,
the operator's intent is not).

## 7. Freshness contract for this census

* `stable` rows (34113, 8080, 8888, 8790, 8791, 4226, 43999, 631, 9222, 53×2) are re-derivable
  verbatim with `sudo -n ss -ltnp` + C2–C12.
* `churn` rows (7 omp session ports) **will not survive** — the port numbers are re-picked per
  process. Re-running the census must compare *owners* (`omp` pid ↔ session prompt), never port
  numbers. An automated check should filter `users:(("omp",pid=N` and match `N` against live
  `/proc/N/cmdline`.
* Re-verify in one command:
  `sudo -n ss -ltnp | awk '$4 ~ /127\.0\.0\.1|0\.0\.0\.0/ {print $4, $NF}'`.

### 7.1 Observed variance on re-check (same session, ~9 minutes later)

The churn class is not theoretical — the re-check that validates this census produced a delta:

```sh
sudo -n ss -ltn | tail -n +2 | wc -l     # 23 → 24 across the session
sudo -n ss -ltnp | grep ':41819'         # → 0 matches; pid 3636400 had EXITED
sudo -n ss -ltnp | grep ':33525'         # → omp pid=2991185 fd=32  (new)
tr '\0' ' ' < /proc/2991185/cmdline      # omp --model @m_flash --config /tmp/fleet-override.yml …/prompts/kama-round-1.md
```

| Delta | Row | Direction |
|---|---|---|
| `127.0.0.1:41819` | #17 (omp pid 3636400, clean-siblings L1) | **disappeared** — owning process exited |
| `127.0.0.1:33525` | *(not in §1)* | **appeared** — omp pid 2991185, this lane's own `kama-round-1.md` dispatch session |
| ESTAB sockets to `127.0.0.1:8080` | §3 item 1 | **2 at 22:52 → 0 at 23:0x** — transient, and the reason §3 stands on the TIME-WAIT churn instead |
| TIME-WAIT `127.0.0.1 → 8080` : `→ 34113` | §3 item 2 | **62:12 → 26:6** within 20 s — both ports churn; the stale port keeps a ~5× lead |
| `127.0.0.1:44035` | *(not in §1)* | **appeared** ~23:20 — omp pid 2328945, `aggregator-round-10.md` dispatch session (a second independent appearance; the churn set really is a set of owners) |

All other §1 rows were byte-stable across the re-check. Two method lessons, both verified here:
`ss -tnp` cannot see listeners at all (0 LISTEN lines vs 23 with `-l`), and a single ESTAB snapshot
is not evidence of a standing consumer (it can vanish between two reads).

Consequence for any automated census: the `stable` set is the reconciliation surface; the `churn`
set is a *set of owners*, not of ports — and the observer itself is one of them.

## 8. Out-of-province findings (report-only; not absorbed)

1. `0.0.0.0:40993` — `python3 -m http.server` exposing a **browsable directory listing of `/tmp`**
   on the LAN (`192.168.0.253/24`) and tailscale (`100.96.18.49`), process-owned by a tmux session.
   Includes `1Password-1000/` and `*lock` entries in the listing. Owner lane: kagi (credential
   hygiene) / kasegi (host security) — kama only records the listener.
2. `127.0.0.1:9222` — Chrome DevTools protocol, 21 live targets including `https://chatgpt.com/`,
   `gemini.google.com` (`the-musketeer` profile). Any local process can drive a logged-in browser.
   Report-only.
3. `127.0.0.1:8888` accepts TCP then resets: not a health-checkable HTTP endpoint, so a naive
   "TCP connect = alive" check would mark a dead service healthy. Relevant to probe design (this lane).

## 9. Rule gaps found while applying the frozen vocabulary (L1 decision requested)

The contract's rule table only assigns a verdict for **2xx** responses (and for 401/403, refused,
non-HTTP). Two real shapes in this census have no verbatim rule:

| Shape | Row(s) | Verdict emitted here | Gap |
|---|---|---|---|
| HTTP **4xx** with non-model content (e.g. `404 text/plain`, `404 text/html`) | 2, 7, 12–18 | `FOREIGN_SERVICE` | rule text says `2xx text/html → FOREIGN_SERVICE`; a 404 page is the same *kind* of thing. Needs an explicit "HTTP responder that is not the model API" clause, status-agnostic. |
| TCP accept then **RST / zero bytes** (no HTTP response at all) | 3, 6 | `NOT_HTTP` | `DEAD` is defined as refused/timeout; a reset-after-accept is neither. Needs a "connects but never speaks HTTP" clause. |

No vocabulary was changed; these two rows are the only places where the label chosen is an
extension of intent rather than a verbatim rule match. A `listeners` subcommand of
`tools/kama-probe.sh` should emit the same 23 rows and the same two gaps will be visible as
non-zero exit cases.

## 10. One-line summary

Truthful one-line state of this box: **the model server is at `127.0.0.1:34113` (`Server: llama.cpp`,
2 slots, `health ok`); the only configs that pin it are the `ufo-fsd-alpha` family
(`the-tick.machine.json:16`, `local-helper.mjs:8`), while four other pins plus a code-level default
still point at `127.0.0.1:8080`, where Jitsi JVB answers HTML 404 — and host connections to that
stale port outnumber connections to the real model ~5:1 in TIME-WAIT churn (62:12, then 26:6).**

## Provenance supplement — round 11 (2026-10-19)
source: retained historical evidence — this file's own measurement header (live on-box probes, 2026-09-28 ~22:47–22:52 -0300, host `plazir27`) and its §5 command ledger C1–C19 plus the §7.1 same-session re-check, retained as committed bytes at `c6199a2542440db77d69918599e5a378ee116337` (2026-09-28, round-1) and `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21` (2026-10-14, round-3 re-census); corroborating retained records: `LOG.md:72` (`KamaScoutListeners` 23-listener census, landed by that peer before it died) and `LOG.md:164-167` (a later refresh observed 20 listeners — ephemeral socket churn); no host path, config, or endpoint was re-opened for this supplement, so the source is the retained record, not current host state
verified-at: original census 2026-09-28 approximately 22:47–22:52 -0300, with in-file 2026-10-14 remeasurements; metadata review 2026-10-20 only. Retained in-repo bytes reviewed; the original 34489-byte prefix is pinned by `.ufo/waves/round-11/legacy-baseline.json`. No listener, endpoint, host config or environment re-opened, and no live revalidation claimed.
recheck: on authorization — a future declared census scope permits `bash tools/kama-probe.sh listeners` (unprivileged, loopback census, not a drift gate). It does not by itself authorize privilege escalation or process-command-line reads: ownerless socket attribution needs explicit operator authorization for that inspection, otherwise record UNDECIDABLE with the blocked command/error under KQ8. Compare dated observations by bind address and owner only after establishing that authorization; no census ran in round 11.
