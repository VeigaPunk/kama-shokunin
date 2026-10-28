# EX05CompletionEdges — kama-completion-live.py edge paths (tip 03a6a1d8)

Advisory findings only. No lane source edited; no verdict on the claims.
Tool under test: `tools/kama-completion-live.py` at tip 03a6a1d850902a66a13dfad33f89cf3a8b759a09, exported with `git archive` into `$S/exp`; sha256 e24bc944…c8f6, identical to the git blob at the tip.
Fixture: llama-server b11755 (sha matches default pin), stories260K.gguf (sha matches pin).
Every case ran with `--work $S/c_<case>/w --out $S/c_<case>/r.json`, with the environment reduced to PATH/HOME/LANG/LC_ALL, on a kernel-chosen loopback port.
No registered port was contacted: the refused-port cases fail before any connection, and the only explicit-port contact was my own `http.server`.
Installs: none. Evidence: `.ufo/waves/round-63/w1/out/EX05CompletionEdges/` (per-case `r.json`, `stderr.txt`, `summary*.json`, `drive*.py`). The `c_g_portbusy` and `c_x*` dirs have no `r.json` because those runs wrote no receipt.

## Requested cases (a)–(i)

| # | case | exit | verdict | failed checks | receipt written | traceback |
|---|------|------|---------|---------------|-----------------|-----------|
| a | `--model-sha256 000…0` | **2** | SETUP_ERROR | `model_digest` | yes | no |
| b | `--server-sha256 000…0` | **2** | SETUP_ERROR | `server_digest` | yes | no |
| c | `--temperature 0.5` | 0 | REQUEST_OK | none; `completion_deterministic` not evaluated (skipped: temperature != 0) | yes | no |
| d | `--n-predict 1` | 0 | REQUEST_OK | none (`predicted_ms`=0.001, `predicted_per_second`=0.0 pass) | yes | no |
| e | `--prompt` "Die Katze saß auf der Mütze — 猫は座った 🐈 naïve" | 0 | REQUEST_OK | none (`prompt_tokens`=52 equals `/tokenize`; request bytes are ASCII-escaped `\u…` and hash-bound) | yes | no |
| f | `--hold-dir D --hold-timeout 2`, no release | **1** | FAIL | `hold_released` ("no release within 2.0s"); wall 2.2 s, teardown clean | yes | no |
| g | `--port P` with `python -m http.server` listening on P | **1** | none (no receipt) | n/a | **NO** | **YES** |
| h | `--ctx 8` | 0 | REQUEST_OK | none (see finding 3) | yes | no |
| i | `--prompt ""` | 0 | REQUEST_OK | none (`prompt_tokens`=1, the BOS; `/tokenize` agrees) | yes | no |

Baseline (no flags): exit 0, REQUEST_OK, 0.2 s.

### Setup-error confirmation: "every setup-error path writes a receipt and exits 2, never a traceback" does NOT hold at this tip

Defects found, with the raw stderr tail:

- **Defect A — (g) port already listening:**
  - `kama_llamacpp_live.SetupError: port-in-use:42051` escapes `run()` at line 250 (`_live.pick_port(refused, args.port)` is outside the `try`).
  - Result: Python traceback, **exit 1**, no receipt, `--out` never created.
  - Exit 1 is the "an evaluated check failed" code, so a setup error reads as a check failure.
  - Same escape for `--port 8080` (`port-refused-registered:8080`), `--port 0` and `--port 70000` (`explicit-port-out-of-range`): traceback, exit 1, no receipt (cases x1–x3).
  - Cause: only `run()`'s hold-dir `prepare_witness_dir` call wraps `_live.SetupError`; `pick_port` does not. `_live.SetupError` is never caught around `pick_port`.
- **Defect B — `--server /nonexistent/llama-server`:** `sha256_file(server)` at line 235 raises `FileNotFoundError`: traceback, exit 1, no receipt (`--server` is checked for existence nowhere; `--model` is, at line 230).
- **Defect C — `--hold-dir` that is an existing regular file:** `os.makedirs(hold, exist_ok=True)` at line 265 raises `FileExistsError` before the `SetupError` wrapper: traceback, exit 1, no receipt. An unwritable hold dir (case x7) is handled correctly: SETUP_ERROR, exit 2, `setup_error: hold dir not usable: witness-dir-unwritable:Permission denied`.
- **Defect D — `--out` into a missing directory:** the whole run (server start, request, teardown) completes, then `open(args.out,'w')` raises `FileNotFoundError` in `main()`: traceback, exit 1, receipt lost. This is a measured instance of the same class (the harness is not wrapped).

Paths that did write a receipt and exit 2 with no traceback:

| case | exit | verdict | `setup_error` |
|------|------|---------|---------------|
| a, b, `--server-sha256 ''`, `--model-sha256 zz` | 2 | SETUP_ERROR | key absent; only the failed `model_digest` / `server_digest` check explains it |
| `--model` missing | 2 | SETUP_ERROR | `model not found: …` |
| hold dir unwritable | 2 | SETUP_ERROR | `hold dir not usable: witness-dir-unwritable:Permission denied` |
| `--ready-timeout 0.01` | 2 | SETUP_ERROR | `server not ready within 0.01s (last=None/ConnectionRefusedError)` |
| `--work` is a file | 2 | SETUP_ERROR | `FileExistsError: …` (internal-fault catch, not a named setup error) |
| `--ctx 100000000` | 2 | SETUP_ERROR | `server not ready within 60.0s (last=None/child-exited)` |

Severity A–D: the contract in the module docstring says "2 setup error / not-evaluated (including internal faults)". The pre-`try` paths violate it. In (g) a non-bound caller cannot tell a busy port from a failed check by exit code.

## Other findings

1. **Digest-mismatch setup errors have no `setup_error` field.** (a)/(b) set only `verdict: SETUP_ERROR` plus the failed `model_digest` / `server_digest` check. Every other SETUP_ERROR path sets `setup_error`, so a consumer keying on that field sees `null`.
2. **`--ctx 100000000` message is misleading.** The child exited after about 17 s and the receipt says "not ready within 60.0s (last=…/child-exited)". Elapsed time is not recorded; the `child-exited` marker is buried in the parenthetical.
3. **(h) `--ctx 8` is recorded but not what ran.**
   - `argv` records `-c 8`, but `server.log` shows `n_slots = 4, n_ctx_slot = 256` (llama.cpp floors per-slot ctx at 256).
   - The receipt never captures the effective n_ctx (`/props` is captured and could carry it).
   - The 8-token prompt plus 8 predicted tokens (16 > 8) would overflow a real ctx 8, but the request succeeds, so REQUEST_OK is not evidence about the ctx the caller asked for.
   - Likewise `--ctx 0` gave `n_ctx_slot = 2048` (model default) and REQUEST_OK, and `--threads 0` gave REQUEST_OK.
4. **`--n-predict 0` and `-1` are accepted.** 0 returned 1 completion token and REQUEST_OK; -1 returned 504 tokens (ctx exhausted) and REQUEST_OK. The receipt's `request.n_predict` records the argument, not what the server did; the `completion_tokens >= 1` check hides that 0 is not honoured.
5. **`--temperature nan`:** `json.dumps` emits a bare `NaN` token and the server answers 400, so `completion_envelope` fails, exit 1, FAIL (acceptable). The receipt itself then contains non-strict JSON `NaN` in `request.temperature`.
6. **Invalid UTF-8 prompt bytes (`ab\xffcd`):** surrogateescape'd arg; the server rejects it, `completion_envelope` fails, exit 1, FAIL, no traceback.
7. **`--alias ''`:** exit 1, FAIL (`completion_model_id`, `models_alias_id`, `props_alias`), no traceback.
8. **Teardown and leaks:** every run that started a child tore it down; I found no stray llama-server from my runs. One `llama-server … -c 512 --port 34451` process (pid 2853755, 1 min old) was running when I looked; it is not in any of my receipts, so it is another seat's.

## Method note
Runs were driven in parallel (up to 10 at once) by `drive.py` / `drive2.py` (in the out dir), each with its own work dir. Requested (a)–(i) plus baseline ran in 2.3 s of wall time; the extras took 21 s.

## Tally
`EX05 cases_run=30 requested=9(+baseline) tracebacks=7/30 (g,x1,x2,x3,x5,x6,x8) exit2_with_receipt=9 (a,b,x4,x7,x9,y6,y7,y8,yA) case_g: exit=1 no_receipt (expected 2)`
