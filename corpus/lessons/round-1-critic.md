# Round 1 critic: falsification of the local-endpoint claim

## Scope and verdict convention

The claim under attack is: the endpoint pinned by `opencode.json:158` and
`janitor.md:21` is dead (serves Jitsi), while the real model is at `34113`.
All probes below were read-only and targeted loopback. The pinned base URL is
`http://localhost:8080/v1` (`~/.config/opencode/opencode.json:158`); the Janitor
pin is `qwen-local/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` at
`~/.config/opencode/agents/janitor.md:21`.

## Route 1: localhost versus 127.0.0.1, including IPv6

Command:

```text
getent ahosts localhost
curl -sS -i --max-time 3 http://localhost:8080/v1/models
curl -sS -i --max-time 3 http://127.0.0.1:8080/v1/models
curl -g -sS -i --max-time 3 http://[::1]:8080/v1/models
curl -g -sS -o /dev/null -w 'localhost remote=%{remote_ip} code=%{http_code}\\n' --max-time 3 http://localhost:8080/v1/models
```

Raw output:

```text
::1             STREAM localhost
::1             DGRAM
::1             RAW
127.0.0.1       STREAM
127.0.0.1       DGRAM
127.0.0.1       RAW
--- localhost GET ---
HTTP/1.1 404 Not Found
Date: Tue, 29 Sep 2026 01:47:09 GMT
Cache-Control: must-revalidate,no-cache,no-store
Content-Type: text/html;charset=iso-8859-1
Content-Length: 351

<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1"/>
<title>Error 404 Not Found</title>
</head>
<body>
<h2>HTTP ERROR 404 Not Found</h2>
<table>
<tr><th>URI:</th><td>http://localhost:8080/v1/models</td></tr>
<tr><th>STATUS:</th><td>404</td></tr>
<tr><th>MESSAGE:</th><td>Not Found</td></tr>
</table>

</body>
</html>
--- 127 GET ---
HTTP/1.1 404 Not Found
Date: Tue, 29 Sep 2026 01:47:09 GMT
Cache-Control: must-revalidate,no-cache,no-store
Content-Type: text/html;charset=iso-8859-1
Content-Length: 351

<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1"/>
<title>Error 404 Not Found</title>
</head>
<body>
<h2>HTTP ERROR 404 Not Found</h2>
<table>
<tr><th>URI:</th><td>http://127.0.0.1:8080/v1/models</td></tr>
<tr><th>STATUS:</th><td>404</td></tr>
<tr><th>MESSAGE:</th><td>Not Found</td></tr>
</table>

</body>
</html>
--- ::1 GET ---
curl: (7) Failed to connect to ::1:8080 after 0 ms: Could not connect to server
localhost remote=127.0.0.1 code=404
```

**Verdict: CLAIM HOLDS** for the configured `localhost` route. Resolver data
contains both `::1` and `127.0.0.1`, but curl's successful localhost request
used `127.0.0.1`; explicit `::1` is dead and does not hide an alternate model
endpoint. Both successful IPv4 spellings return the same Jetty-style HTML 404.

## Route 2: forwarding or translation from 8080 to 34113

Command:

```text
ss -ltnp
iptables -t nat -S
cat ~/.ssh/config
ps -eo pid,args | grep -E '[s]ocat|[n]ginx|[c]addy|[s]sh.*-[LRD]'
```

Raw output (relevant lines):

```text
LISTEN 0 4096 127.0.0.1:8080 0.0.0.0:*
LISTEN 0 512  127.0.0.1:34113 0.0.0.0:* users:(("llama-server",pid=1299,fd=16))
iptables v1.8.13 (nf_tables): Could not fetch rule set generation id: Permission denied (you must be root)
# ~/.ssh/config contains Host the-janitor, Host github.com, Host amdporrada;
# no LocalForward, RemoteForward, DynamicForward, or ProxyJump lines.
4923 socat -U - UNIX-CONNECT:/run/user/1000/hypr/efb50993780079460b0cbed1363e2166a2de1d9f_1790574934_209458179/.socket2.sock
```

The `socat` process is a Unix-socket Hyprland process, not a TCP listener or
8080-to-34113 forward. No nginx, caddy, or SSH forwarding process was found.
The NAT rules are **undecidable without root**: the command failed with the
verbatim permission error above. The socket table nevertheless shows distinct
listeners: `8080` has no owning process shown by `ss`, while `34113` is owned by
`llama-server` (also recorded as L1-F1).

**Verdict: UNDECIDABLE** specifically for invisible kernel NAT translation,
because root was unavailable. **Claim holds on all observable user-space
forwarding evidence.** The round report must not say “no NAT exists”; it must
say “iptables NAT could not be inspected without root.”

## Route 3: actual OpenAI-compatible request at the configured endpoint

Command:

```text
body='{"model":"Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS","messages":[{"role":"user","content":"ping"}],"max_tokens":1}'
curl -sS -i --max-time 10 -H 'Content-Type: application/json' -d "$body" http://localhost:8080/v1/chat/completions
curl -sS -i --max-time 10 -H 'Content-Type: application/json' -d "$body" http://127.0.0.1:8080/v1/chat/completions
```

Raw output (localhost and 127.0.0.1 respectively):

```text
HTTP/1.1 404 Not Found
Content-Type: text/html;charset=iso-8859-1
Content-Length: 361

<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1"/>
<title>Error 404 Not Found</title>
</head>
<body>
<h2>HTTP ERROR 404 Not Found</h2>
<table>
<tr><th>URI:</th><td>http://localhost:8080/v1/chat/completions</td></tr>
<tr><th>STATUS:</th><td>404</td></tr>
<tr><th>MESSAGE:</th><td>Not Found</td></tr>
</table>

</body>
</html>

HTTP/1.1 404 Not Found
Content-Type: text/html;charset=iso-8859-1
Content-Length: 361

<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1"/>
<title>Error 404 Not Found</title>
</head>
<body>
<h2>HTTP ERROR 404 Not Found</h2>
<table>
<tr><th>URI:</th><td>http://127.0.0.1:8080/v1/chat/completions</td></tr>
<tr><th>STATUS:</th><td>404</td></tr>
<tr><th>MESSAGE:</th><td>Not Found</td></tr>
</table>

</body>
</html>
```

**Verdict: CLAIM HOLDS** for the operational meaning of “the pinned route
cannot serve the configured model.” It is not connection-dead: it is an alive
foreign HTTP service returning HTML 404, never an OpenAI JSON completion.

## Route 4: can opencode rewrite the base URL at runtime?

Command:

```text
find ~/.config/opencode/plugin -maxdepth 3 -type f -print -exec cat {} \;
find ~/.config/opencode/tools -maxdepth 3 -type f -print -exec cat {} \;
```

Raw output:

```text
/home/vgpnk/.config/opencode/plugin/fnm-nudge.js
// fnm-nudge ... checks node/fnm and appends a nudge after the first bash result
// It contains no baseURL, endpoint, provider, or model rewrite.
/home/vgpnk/.config/opencode/tools/janitor_auth.ts
// janitor_auth ... runs `op vault list --format=json` and returns AUTH_OK or AUTH_REQUIRED
// It contains no baseURL, endpoint, provider, or model rewrite.
```

**Verdict: CLAIM HOLDS** against the requested plugin/tool rewrite hypothesis.
The inspected plugin and tool have no endpoint mutation logic. This is a scope
claim about those two configured directories, not proof about arbitrary future
runtime code outside them.

## Route 5: is 34113 serving the configured model id?

Command:

```text
curl -sS -i --max-time 10 http://127.0.0.1:34113/v1/models
```

Raw output (identity-bearing fields):

```text
HTTP/1.1 200 OK
Server: llama.cpp
Content-Type: application/json; charset=utf-8
{"models":[{"name":"/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf","model":"/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf","capabilities":["completion"]...}],"object":"list","data":[{"id":"/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf","aliases":["/scratch/models/qwen3-coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf"]...}]}
```

The configured model key is the basename
`Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS`; the live server reports the same
model with its full `.gguf` path (L1-F4). This is identity-compatible by
basename, but not a byte-for-byte string match to the config key.

**Verdict: CLAIM HOLDS with a qualification.** 34113 is genuinely
`llama.cpp` and serves the configured Qwen3-Coder model, not merely an
unrelated compatible-looking server. The exact API model identifier returned
by `/v1/models` is the full path, so clients that require exact ID equality
must use that returned ID or rely on aliasing; the evidence does not prove
that the short OpenCode key is accepted as an exact request ID.

## Route 6: shell-level Janitor consumer

The stale route is not confined to the OpenCode config tree.

Command:

```text
nl -ba ~/.local/bin/the-janitor | while IFS= read -r l; do
  case "$l" in 1[6-9]\ *|1[6-9]\t*) printf '%s\n' "$l";; esac
done
```

Raw output:

```text
16 MODEL_PROVIDER="qwen-local"
17 MODEL_ID="Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS"
18 MODEL_SELECTOR="$MODEL_PROVIDER/$MODEL_ID"
19 MODEL_ENDPOINT="http://127.0.0.1:8080/v1"
```

**Verdict: CLAIM HOLDS.** The independent executable
`~/.local/bin/the-janitor:16-19` pins the same model to the same stale
8080 route. This strengthens the claim's consumer census, but does not alter
the route behavior above. The corrected wording must include this fourth
consumer: `the-janitor` also pins `127.0.0.1:8080/v1`; it is not enough to
name only `opencode.json` and `janitor.md`.

The same executable scan found no additional local executable with this exact
Qwen endpoint pin. Other `MODEL_*` matches included unrelated dispatch tools
and binaries; they were not treated as local Qwen consumers.

## Final verdict and corrected wording

**FINAL VERDICT: CLAIM HOLDS**, with two precision corrections. First, “dead”
means *dead as the configured model/API route*, not TCP-dead: 8080 is alive
but returns Jitsi/Jetty-style HTML 404 (L1-F2/L1-F3). Second, the 8080→34113
NAT question is **UNDECIDABLE** without root, so the strongest defensible
wording is:

> The configured `localhost:8080/v1` route does not serve the Qwen model: both
> IPv4 spellings return a Jetty HTML 404, explicit `::1` is refused, and the
> minimal chat request fails. The live llama.cpp model is independently
> exposed at `127.0.0.1:34113`, reporting the configured Qwen3-Coder model by
> full `.gguf` path. No user-space forward was found; kernel NAT could not be
> ruled out because `iptables -t nat -S` required root.
