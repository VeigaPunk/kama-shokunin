# Report-out draft: kagi (endpoint health rule and a loading server)

For the round-25 report only. Not for the kagi repo; kama writes nothing there.
Outside the C2 claim; recorded here as an adjacency report-out.

**What kama found.** A single-model llama-server starts its HTTP listener
before the model loads. Until loading finishes it answers `/health`,
`/v1/models` and every other API path with HTTP 503 and
`{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`.
It answers this before the API-key check, so a loading server with `--api-key`
returns 503, not 401. `/health` returns `{"status":"ok"}` only once ready.
Kama's probe grades that exact body `MODEL_LOADING`, not `FOREIGN_SERVICE`.

**Evidence path (kama lane, commit fa3b62ae).**
- `corpus/knowledge/llamacpp-loading-lifecycle.md:9` (claim), `:27-35` (loading gate and order before the API key), `:36` (ready state).
- Sources S036 (`tools/server/server-http.cpp` lines 307-328 and 347-359) and S037 (`tools/server/server.cpp` lines 440-515), pinned at commit 704366d76.
- Live lane-owned receipt `.ufo/waves/round-16/live/receipt.json` (round 16).

**Where it meets kagi.** Kagi's drift check runs
`curl -fsS --max-time 2 ".../health"` and reads the result as
"llama.cpp `/health` → `{"status":"ok"}`; a foreign listener 404s or closes."
(`corpus/knowledge/op-cli-surface.md:87-91`). Its skill row
"Verify model endpoint is real" uses the same `curl -fsS .../health` probe
(`SKILL.md:43`). The rule names two outcomes and has no row for HTTP 503.
With `curl -f`, a 503 exits 22 with no response body, the same exit code as a
404 (`man curl`, curl 8.23.0: "Fail with error code 22 and with no response
body output at all ... at 400 or greater"). A pass/fail reading therefore
treats a still-loading llama-server like a squatted port. A kagi grep for
`503`, `Loading model`, `MODEL_LOADING` and `unavailable_error` found no
loading-state record.

**What kagi would need to check.**
1. Whether any kagi diagnosis treated a failed `/health` probe as proof of a
   foreign listener when the model server could have been loading (for
   example, right after a restart).
2. Whether the drift check should read the status code (for example
   `curl -sS -o /dev/null -w '%{http_code}'`) and add a row: 503 with the
   `Loading model` body means a llama-server that is not ready yet, not a
   foreign service; retry later instead of rerouting.
3. Whether that row belongs in `op-cli-surface.md:91` and `SKILL.md:43`
   together, so the two copies stay identical.

**Limits.** Kama's lifecycle is from build 11755 in single-model mode; router
mode marks itself ready earlier (`llamacpp-loading-lifecycle.md:40`). Whether
kagi's handler ever met a loading server is unknown; the misreading is a
possible case, [INFERENCE], not an observed kagi incident. The body match
proves llama.cpp-shaped loading, not which model is loading.
