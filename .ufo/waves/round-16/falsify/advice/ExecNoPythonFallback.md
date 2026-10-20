# ExecNoPythonFallback — no-python3 fallback to FOREIGN_SERVICE

VERDICT: confirm — without python3, the probe keeps the old FOREIGN_SERVICE path on the exact llama.cpp loading envelope; --json still emits valid JSON, unvalidated and unindented.

## Attack

Claim attacked (probe header, `tools/kama-probe.sh:36`): "requires python3 (without it the body keeps FOREIGN_SERVICE)".

Setup:
- `/tmp/kama-r16-ExecNoPythonFallback/stub.py`: `http.server` stub answering **every** path on `127.0.0.1:41297` with `503`, `Content-Type: application/json; charset=utf-8`, body `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` (the byte-exact envelope; extra whitespace from `json.dumps`, key names/values identical).
- `/tmp/kama-r16-ExecNoPythonFallback/bin`: symlinks to `/usr/bin/{env,bash,curl,ss,env,mktemp,head,tr,grep,sed,sort,dirname,basename,rm,rmdir,cat,ls,date,sleep,wc}` — bash, curl, ss, coreutils plus grep/sed (script fallbacks need them; strictest test keeps them present so only python3 is absent). **No python3** (verified `command -v python3` → "no python3" under that PATH).
- Started stub with `/usr/bin/python3` (absolute path, outside the restricted PATH — allowed: the restriction applies to the probe's PATH, not the stub's launcher). Port 41297; never touched 8080/34113. Stub verified live: `curl -w` → `http_code=503`, body echoed back exactly.

Runs:

1. Restricted PATH, no python3:
   `env -i PATH=/tmp/kama-r16-ExecNoPythonFallback/bin bash tools/kama-probe.sh check --port 41297 --expect '*' --json`
   - exit **2**
   - stderr: `[kama-probe] python3 not found — using grep fallbacks for JSON-pointer and model-id parsing`
   - verdict `"FOREIGN_SERVICE"`, reason `"non-2xx-non-model-http"`, `drift: true`. Evidence line: `GET /v1/models -> 503 application/json; charset=utf-8 (Server: BaseHTTP/0.6 Python/3.14.8) (non-2xx HTTP from a non-model service); 503|application/json; charset=utf-8 @ /` — i.e. the body fell straight through `body_is_llamacpp_loading` (returns 1 at `tools/kama-probe.sh:429` when `HAVE_PY=0`) into the generic non-2xx tail (`:556-565`).

2. Control, normal PATH (python3 present), same stub:
   `bash tools/kama-probe.sh check --port 41297 --expect '*' --json`
   - exit **2**, verdict `"MODEL_LOADING"`, reason `"llamacpp-loading"` — the only difference is python3, isolating it as the sole cause.

## --json without python3

`emit_json` (`tools/kama-probe.sh:180-188`) prints the raw `printf`-assembled string when `HAVE_PY=0` — **no JSON validation, no indentation**. Observed: restricted run produced compact single-line-per-row output (11 lines) vs the control's `indent=2` pretty-print (33 lines). External check: `/usr/bin/python3 -c 'json.load'` on the restricted output parsed cleanly → valid JSON, just unnormalized. So `--json` still works without python3; it only loses the structural-validation safety net (a probe bug in `jstr` escaping would ship silently).

## Limitations

- Only the 503-loading-envelope family tested; by symmetry the exact-match gate cannot run at all without python3 ([INFERENCE] same holds for `served_ids`/JSON-pointer paths, which already document grep fallbacks).
- Stub served the envelope on `/` too; real llama.cpp loading differs on frontend paths — irrelevant here since the verdict path only reads `/v1/models`, `/`, `/metrics`.
- Restricted PATH kept grep/sed/sort: the probe runs correctly without python3 as documented. A PATH missing grep would likely still yield the same verdict chain ([INFERENCE], not tested — outside the named matrix).

## Cleanup / state

- Stub killed; `ss -ltn` shows 41297 free; `pgrep -x llama-server` empty (no llama-server was ever started).
- Scratch under `/tmp/kama-r16-ExecNoPythonFallback/` left in place only as this seat's own scratch: stub.py, body.json, out-nopy.json, err-nopy.txt, out-withpy.json, err-withpy.txt, bin/. No lane files touched.

## Installs

None.
