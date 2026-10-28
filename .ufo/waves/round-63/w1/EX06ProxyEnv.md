# EX06ProxyEnv — proxy-free path, before/after of the opener swap (advisory finding, no verdict)

Tip under test 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (scratch `git clone --shared` + `checkout --detach`, HEAD verified).
Base tool = `git show 7ee8cbdf160f8c945954e4737e7a2f797e3b2987:tools/kama-completion-live.py`, copied as
`tools/kama-completion-live-old.py` inside the scratch clone only (so REPO/`kama-llamacpp-live.py` resolve to the tip clone;
`kama-llamacpp-live.py` has an empty diff base..tip, so the dependency is identical in both runs).
No installs/upgrades. Lane tree untouched.

## Method
`out/EX06ProxyEnv/driver.py`: a python socket accept-loop listener on a kernel-chosen free loopback port (in-process thread, logs peer + first
160 bytes of every connection, answers 502). Child env = os.environ minus every `*_proxy`/`NO_PROXY` var, then
`HTTP_PROXY=http_proxy=ALL_PROXY=https_proxy=http://127.0.0.1:<listener port>`; asserted NO_PROXY/no_proxy absent.
Command: `python3 <tool> --work $S/w-<label> --out $S/r-<label>.json` (cwd = scratch). Fresh listener per run.

## Result
| run | tool | proxy port | exit | schema | verdict | connections to proxy |
|---|---|---|---|---|---|---|
| tip | tools/kama-completion-live.py @03a6a1d | 40985 | 0 | kama-completion-live/v2 | **REQUEST_OK** (22/22 checks true, 0 failed) | **0** (log empty) |
| old | tools/kama-completion-live.py @7ee8cbd | 36987 | 1 | kama-completion-live/v1 | **FAIL** | **2** |

Old-tool proxy log (verbatim first bytes):
- 19:46:49 from 127.0.0.1:42610 `POST http://127.0.0.1:43025/v1/completions HTTP/1.1 ... Content-Length: 107 ... User-Agent: Python-urllib/3.14`
- 19:46:49 from 127.0.0.1:42614 `POST http://127.0.0.1:43025/v1/completions HTTP/1.1 ... Content-Length: 75 ... User-Agent: Python-urllib/3.14`

Both connections are the two POSTs (the 107-byte valid completion request and the 75-byte malformed request) sent in absolute-URI form to the
proxy instead of the llama-server child (43025). Failed checks in the old receipt: `completion_envelope`, `bad_request_graded` (the 502 stub
answered both); the GET-based checks (`health_ready`, `props_alias`, `models_alias_id`, listener_owned, digests, teardown) stayed true — they go
through `kama-llamacpp-live.py`'s `_OPENER` (ProxyHandler({})) in both versions, so no GET connection reached the proxy.

## Answer
The OLD tool DID leak the POST to the env proxy (2/2 POSTs, 0 reaching the real server) when NO_PROXY is unset; the receipt failed closed as FAIL (exit 1),
not as a false REQUEST_OK. The tip tool with identical env made 0 proxy connections and returned REQUEST_OK, exit 0. The opener swap
(`urllib.request.urlopen` -> `_live._OPENER.open`) is therefore the measured cause of the before/after difference. Caveat: one run each, single
env shape (4 proxy vars, no NO_PROXY, lowercase+uppercase); the old tool's failure here was an operability defect (spurious FAIL on a proxied host), not a hidden pass.

Evidence: `.ufo/waves/round-63/w1/out/EX06ProxyEnv/{driver.py,res-tip.json,res-old.json,r-tip.json,r-old.json,tool-sha256.txt}`.

counter-line: tip proxy_connections=0 verdict=REQUEST_OK exit=0 | old proxy_connections=2 (POST x2) verdict=FAIL exit=1
