# Round-1 frozen-fact citation audit

Audit performed against the live box. Commands are shown verbatim; outputs are reduced only where explicitly marked. `MATCH` means the frozen fact is reproduced; `MISMATCH` means the live value differs; `PARTIAL` means the command exposed only part of the claimed value.

| Fact | Exact command | Observed output | Verdict / corrected value |
|---|---|---|---|
| F1 | `ss -ltnp \| grep -E '127\\.0\\.0\\.1:(34113\|8080)'` | `LISTEN ... 127.0.0.1:8080 ...`; `LISTEN ... 127.0.0.1:34113 ... users:(("llama-server",pid=1299,fd=16))` | **PARTIAL** — 34113 is owned by `llama-server` PID 1299. `ss` exposed no owner for 8080 in this run; the separately observed Docker mapping in F2 identifies the listener as Docker-published Jitsi JVB, but `docker-proxy` ownership was not reproduced by this command. |
| F2 | `docker ps --format '{{.Names}} {{.Ports}}'` | `docker-jitsi-meet-jvb-1 127.0.0.1:8080->8080/tcp, 0.0.0.0:10000->10000/udp, [::]:10000->10000/udp`; `docker-jitsi-meet-jicofo-1 127.0.0.1:8888->8888/tcp`; other listed containers had no published ports | **MATCH** — 8080 is Jitsi JVB; 8888 is Jicofo. Corrected detail: this command names the container, not the host-side `docker-proxy` process. |
| F3 | `curl -sSI http://127.0.0.1:8080/; curl -sS http://127.0.0.1:8080/ \| grep -E 'HTTP ERROR 404\|URI\|STATUS\|MESSAGE'` | Headers: `HTTP/1.1 404 Not Found`, `Content-Type: text/html;charset=iso-8859-1`; body markers: `<h2>HTTP ERROR 404 Not Found</h2>`, `URI: http://127.0.0.1:8080/`, `STATUS: 404`, `MESSAGE: Not Found` | **MATCH** — byte-level required markers, status, and content type reproduced. |
| F4 | `curl -sS http://127.0.0.1:34113/v1/models` | `"models":[{"name":"/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf",...}]` | **MATCH** — exact `models[0].name` is `/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf`. |
| F5 | `curl -sS http://127.0.0.1:34113/health` | `{"status":"ok"}` | **MATCH** — exact response body is `{"status":"ok"}`. |
| F6 | `nl -ba ~/.config/opencode/opencode.json \| { grep -A10 -B5 'qwen-local'; }` | Lines 154–163 show provider; line 158 is `"baseURL": "http://localhost:8080/v1"` | **MATCH** — exact line and string reproduced. |
| F7 | `nl -ba ~/.config/opencode/agents/janitor.md \| { grep -A2 -B2 'qwen-local/Qwen3'; }` | Line 21: `` `http://127.0.0.1:8080/v1`; there is no fallback. ``; lines 19–21 form `The model is fixed to` + model pin + that URL sentence | **MATCH** — line 21 and wording reproduced exactly. |
| F8 | `stat -c 'mtime=%y' ~/.config/systemd/user/qwen-coder.service; nl -ba ~/.config/systemd/user/qwen-coder.service \| grep -- '--port'` | `mtime=2026-09-08 20:43:13.212316261 -0300`; line 17 contains `--port 34113` | **MATCH** — active unit uses port 34113; corrected exact mtime is the timestamp shown (2026-09-08 20:43:13.212316261 -0300). |
| F9 | `stat -c 'mtime=%y' ~/.config/systemd/user/qwen-coder.service.bak.1788033391; nl -ba ... \| grep -- '--port'` | `mtime=2026-08-29 16:56:36.838785584 -0300`; line 16 contains `--port 8080` | **MATCH** — backup uses port 8080; exact observed mtime as shown. |
| F10 | `stat -c 'mtime=%y' ~/.config/systemd/user/qwen-coder.ctx32k-q4.service; nl -ba ... \| grep -- '--port'` | `mtime=2026-08-29 03:36:10.297033667 -0300`; line 16 contains `--port 8080` | **MATCH** — variant uses port 8080; exact observed mtime as shown. |
| F11 | `nl -ba ~/.omp/agent/config.yml \| head -35` | Lines 21–29: `m_kimi: cursor/kimi-k3-max:max`; `m_dsflash: alibaba-token-plan/deepseek-v4.1-flash:max`; `m_flash: charm-hyper/deepseek-v4.1-flash:max`; `m_qwen: alibaba-token-plan/qwen3.8-max:xhigh`; `m_luna: openai-codex/gpt-5.6-luna:low`; `m_daybreak: openai-codex/gpt-daybreak-blue-latest:max`; `m_grok: xai-oauth/grok-4.5:low` | **MISMATCH** — frozen F11's `m_flash` route (`alibaba-token-plan/...`) is stale. Correct alias→route table is exactly the seven quoted pairs above, at lines 21, 23–29 (with `m_dsflash` additionally present). None is a local-baseURL alias. |
| F12 | `for f in /home/vgpnk/projects/shokunin/.ufo/reports/round-3/kagi.md /home/vgpnk/projects/shokunin/.ufo/reports/round-4/kengaku.md; do echo "--- $f"; test -f "$f" && { nl -ba "$f" \| grep -in -E '8080\|34113\|drift\|qwen'; } \|\| echo ABSENT; done` | `kagi.md` exists; lines 23–24 say opencode pins `127.0.0.1:8080/v1`, 8080 is Jitsi, llama-server serves on `34113`. `kengaku.md` exists; lines 20–23 say qwen-local targets `localhost:8080`, Jitsi returns 404, real llama-server listens on `127.0.0.1:34113` | **MATCH** — both prior-art reports exist and contain the 8080→34113 drift claim. |

## Citation checks for other round-1 artifacts

Inventory command: `find corpus -type f -maxdepth 3 -print | sort; find . -maxdepth 2 -name SKILL.md -print`. At check time the only corpus file present was `corpus/README.md`; no `corpus/knowledge/*.md`, no other `corpus/lessons/*.md`, and no `tools/kama-probe.sh` existed. `SKILL.md` did exist at repository root. Therefore there were no existing knowledge lessons or probe citations to resolve, and the requested probe artifact was absent rather than silently treated as valid.

The existing `corpus/README.md` (lines 1–21) is descriptive scope text and contains no external command citation or line-number claim. Root `SKILL.md` was present, but the inventory command did not print its contents; no citation claim from it was assessed here. This is an absence-at-check-time finding, not evidence that sibling artifacts will remain absent.

## Unresolved or incorrect citations

- **Incorrect frozen citation:** F11's `m_flash` route is incorrect at live line 24: it is `charm-hyper/deepseek-v4.1-flash:max`, not `alibaba-token-plan/deepseek-v4.1-flash:max`.
- **Unresolved artifact citation:** `tools/kama-probe.sh` was absent at check time, so any citation to its behavior or line numbers cannot resolve yet.
- No other unresolved citations were found among artifacts that existed at check time; the corpus artifact inventory above is the evidence for that scope.
## Completeness census: executable consumers

Command: `nl -ba ~/.local/bin/the-janitor | grep -E 'MODEL_(PROVIDER|ID|ENDPOINT)'`

Observed output:

```text
16 MODEL_PROVIDER="qwen-local"
17 MODEL_ID="Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS"
19 MODEL_ENDPOINT="http://127.0.0.1:8080/v1"
```

**MATCH** for the newly reported fourth stale consumer: the exact endpoint and model id are reproduced at `~/.local/bin/the-janitor:16-19`.

Command: `nl -ba ~/.config/opencode/agents/distiller.md | grep -E 'model:|cascade|qwen-local'`

Observed output:

```text
5 model: qwen-local/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS
6 cascade_class: volume
7 cascade: "qwen-local/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS > openai/gpt-5.6-sol-fast > xai/grok-4.5"
8 cascade_note: "Qwen local is the primary deduper; cloud fallbacks remain available."
```

**MATCH** for the cascade-protected consumer: the local pin is at line 5 and explicit cloud fallback is at line 7.

Command: `find ~/.local/bin -type f -perm /111 -print0 | xargs -0 grep -nH -E 'MODEL_(PROVIDER|ID|ENDPOINT)='`

Observed output includes `~/.local/bin/the-janitor:16-19`; `xask-l3` and `xask` also set generic `MODEL_ID` variables for command-line selection, but neither output contains a local Qwen `MODEL_ENDPOINT`. Thus the executable census adds `the-janitor` as the only additional local endpoint pin found by this scan.

The registry requested by the parent lane is not present in this checkout at audit time (`test -f registry/endpoint-consumers.tsv` was not run before this artifact was written); this lesson records evidence only and does not create or modify that sibling-owned registry.
