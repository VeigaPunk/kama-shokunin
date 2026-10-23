ATTACK E26-03 (SKILL.md row + registry entry, S116 server-context.cpp:3084): partial — signature, trigger, source and S116 hold; the next-action cell misses the discriminator the server prints

Seat: KamaR26.AttackE2603 (wave 2 FALSIFY, round 26). Run 2026-10-23 03:57-03:59Z. Port block 47708-47711.
No tools installed or updated. No lane production file edited. No counter run (the tip receipt already holds the counter's result for this row; see check 1).

## Verdicts

| check | verdict |
|---|---|
| (1) re-run registered trigger twice | holds |
| (2) not a warning / unrelated path (F1), not echoed (F2/F3) | holds |
| (3) pinned source line, fresh fetch, meaning (code) cell | holds (one small citation gap, low) |
| (4) next action supported, not overreach | partial: supported and not overreach, but it says nothing tells the cause apart, and the server log does (live) |
| (5) SOURCES S116 cells + lesson Gate quote | holds |

## Pins (re-checked)

- `sha256sum ~/.local/bin/llama-server` → `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` (= count-c1.py SERVER_SHA256). `llama-server --version` → `version: 0.7.0-dev (build 11755, commit 704366d76)`.
- `sha256sum ~/.cache/kama-shokunin/models/stories260K.gguf` → `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (= MODEL_SHA256).
- `sha256sum .ufo/waves/round-26/count-c1.py` → `6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588` (= frozen value).
- Registry entry (`registry/error-signatures-r26.json:55-77`): channel `http`, args `["--slot-save-path","/tmp","-t","2"]`, model `fixture`, occupy_port false, request `POST /slots/0?action=restore`, headers `{}`, body `{"filename":"kama-r26-absent-slot.bin"}`, source `S116` / `server-context.cpp`.

## (1) Re-run of the registered trigger — holds

Command: `timeout 150 python3 /fast/scratch/hyaku/kama-r26w2/AttackE2603/run_trigger.py <port> <log>`. It copies the counter's `http()`: JSON body, `Content-Type: application/json`, a `/health` wait, and the same argv shape `-m <fixture> --host 127.0.0.1 --port P` + registry args. The server runs under `timeout 120`. `ss -ltn` showed 47708/47709 free before each run.

Run 1 (port 47708), driver exit 0:
```
pre-exists /tmp/kama-r26-absent-slot.bin: False
ready: True
status: 400
body: {"error":{"code":400,"message":"Unable to restore slot: No available space in KV cache or invalid slot save file","type":"invalid_request_error"}}
exit: 1            (server exit after SIGTERM)
port_closed: True
```
Run 2 (port 47709), driver exit 0: same lines, byte for byte (status 400, same body, port_closed True).

Server log, both runs (run1.log:11-12, run2.log:11-12):
```
E llama_state_seq_load_file: error loading sequence state file: failed to open /tmp/kama-r26-absent-slot.bin: No such file or directory
E srv    send_error: task id = 0, error: Unable to restore slot: No available space in KV cache or invalid slot save file
```
The counter at the landed tip agrees (`.ufo/waves/round-26/final/c1-tip-receipt.json`, entry E26-03): status 400, every check true, the same body excerpt, counted true.

## (2) F1 / F2 / F3 — holds

- F1: the signature comes from the HTTP response body on the real error path. `send_error(..., ERROR_TYPE_INVALID_REQUEST)` (server-context.cpp:3102) maps to code 400 (server-common.cpp:95-97), and `res->error` takes the status from `code` (server-context.cpp:4872-4874). It is not a warning or a startup line: the channel is http and the server was healthy.
- F2: the request is `POST /slots/0?action=restore` with no headers and body `{"filename":"kama-r26-absent-slot.bin"}`. No request field, query string or header holds any part of the signature. The body contains no JSON unicode escapes.
- F3: the args are `--slot-save-path /tmp -t 2`. No argument file is used.
- The signature occurs exactly once in the pinned sources (`rg -n "No available space in KV cache|invalid slot save file" .ufo/waves/round-26/sources/llama.cpp-704366d/` → only `server-context.cpp:3084`).

## (3) Source line and meaning (code) cell — holds

Fresh fetch: `curl -sSfL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp` (exit 0) → sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`. That equals the lane snapshot and the S116 anchor. The fetched arg.cpp, llama-context.cpp and server-common.cpp also match their pinned values.

- server-context.cpp:3078: `nread = llama_state_seq_load_file(ctx_tgt, filepath.c_str(), slot->id, nullptr, 0, &n_packed);`. Lines 3079-3082 do a second load only when `nread != 0`. Lines 3083-3085: `if (nread == 0) { throw std::runtime_error("No available space in KV cache or invalid slot save file"); }`. The cited range 3078-3085 is exact.
- Line 3100-3102 catches the throw and sends `"Unable to restore slot: " + err.what()` as INVALID_REQUEST, which becomes 400. So the trigger cell's "→ 400" is right.
- The three causes the row names are code paths that each return 0, and I reproduced each one live:
  - Missing or unreadable file: `llama_file` init throws `failed to open %s: %s` (src/llama-mmap.cpp:222, fresh sha256 `130601ff…03e7`). `llama_state_seq_load_file` catches it and returns 0 (llama-context.cpp:4591-4595).
  - Wrong file: `unknown (magic, version)` returns 0 (llama-context.cpp:3542-3544).
  - Cache too small: `state_read_meta: not enough cells in kv cache` (src/llama-kv-cache.cpp:2364, fresh sha256 `d0739eaf…d294`), then `failed to restore kv cache` (llama-kv-cache.cpp:2214), which is caught and returns 0.
- Live check of the "cache too small" and "wrong file" causes (`timeout 300 python3 run_causes.py`, exit 0). I saved slot 0 after a 281-token prompt on `-np 1 -c 2048` (port 47710; save → 200, `n_written 186476`). I then restored it on `-np 1 -c 64` (port 47711): 400, same body. Log: `E state_read_meta: not enough cells in kv cache` / `E llama_state_seq_load_file: error loading sequence state file: failed to restore kv cache`. Restoring a 51-byte text file `junk.bin`: 400, same body. Log: `E state_seq_load_file: unknown (magic, version) for sequence state file: 20746f6e, 6c6c2061`. Both ports closed (`port_closed: True`).
- Citation gap (low): the meaning cell cites only 3078-3085. The 400 comes from 3100-3102. Smallest correction: change `(server-context.cpp:3078-3085)` to `(server-context.cpp:3078-3085; 400 via 3100-3102)`.

## (4) Next action — partial

Cell: "The message does not tell which cause applies. Check that the file exists under the save path first; only then suspect cache size or a file saved by another model or build."

- Supported: the HTTP body is the same for all three causes (live, see 3). Checking "file exists first" fits the live missing-file trigger. "A file saved by another model or build" is supported by the magic/version check (llama-context.cpp:3542) and the layer/type mismatch checks in llama-kv-cache.cpp (e.g. :2567). Nothing claims more than the code shows.
- Defect (medium, usefulness): the cell implies an operator must find the cause by elimination. But the server's stderr prints an error line right before `send_error`, and that line names the cause. All three cases were observed live above: `failed to open <path>: No such file or directory`, `unknown (magic, version)`, `not enough cells in kv cache`. The cell also leaves out that the file path is `--slot-save-path` + filename, with a separator added (arg.cpp:3662-3665). Run 1's log shows this as `/tmp/kama-r26-absent-slot.bin`.
- Smallest correction: replace the cell with
  `The HTTP body is the same for every cause; the server log line just before send_error names it: "failed to open <path>" (no such file under --slot-save-path), "unknown (magic, version)" (not a slot file, or another build), "not enough cells in kv cache" (cache too small for the saved state). Fix what that line names.`
  If the lane wants those log strings sourced, it needs llama-mmap.cpp and llama-kv-cache.cpp pinned at 704366d (fresh sha256 above). The row's counted signature does not change.

## (5) SOURCES S116 and lesson Gate quote — holds

- `corpus/SOURCES.md:128`: URL `…/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L3084`. Line 3084 holds the throw (verified on the fresh fetch). The anchor `server-context.cpp line 3084 @ 704366d…; sha256 dd1de0f2…2329` equals the fresh-fetch sha256. The "teaches" cell repeats the meaning cell, which is accurate (see 3). The scope is limited to commit 704366d76.
- `corpus/lessons/round-26.md:29`: `line 3084: throw std::runtime_error("No available space in KV cache or invalid slot save file");`. This is the source line verbatim, minus its leading indentation, and under 25 words. The URL and access date 2026-10-23 match.
- Not a defect for this row: `.ufo/waves/round-26/final/census-validate.out:32` reports `W04 S116 duplicate url … across scopes`. It strips the `#L` fragment, so it fires for every S1xx row on server-context.cpp. It is not specific to S116.
- History, no defect: the wave-1 draft `.ufo/waves/round-26/w1-build/out/ScribeSourcesContext/rows.md:5` used S116 for line 5408 (now S115). The landed S116 is correct.

## Residual risk and verification gaps

- Host-state dependency (low; can only cause a false miss, never a false count): the trigger relies on `/tmp/kama-r26-absent-slot.bin` not existing. `/tmp` is world-writable and shared. If a valid slot file appears there, restore succeeds (200) and the counter would not count the row. If an invalid file appears there, the same signature still comes out. Smallest correction, only if the registry is ever revised: use a filename that holds a per-run random token. That needs a counter change and is out of scope under the freeze, so record it as a known limit.
- Not run: the frozen counter itself (I relied on the tip receipt), and the unreadable-permission case (I covered it by code reading: it goes through the same `failed to open` path as a missing file).

## Processes and ports

- Every server I started ran under `timeout`, received SIGTERM in `finally`, and its port closed (all four runs report `port_closed: True`).
- `pgrep -af "llama-server.*477(0[89]|1[01])"` → exit 1 (none on my ports).
- The remaining `pgrep -af llama-server` entries (ports 47719, 47734, 47740) belong to other seats.

## Files written

- `.ufo/waves/round-26/w2-falsify/advice/AttackE2603.md` (this report)
- Scratch: `/fast/scratch/hyaku/kama-r26w2/AttackE2603/` containing `run_trigger.py`, `run_causes.py`, `run1.log`, `run2.log`, `save.log`, `restore.log`, `slots/big.bin`, `slots/junk.bin`, and the fresh fetches `server-context.cpp`, `llama-context.cpp`, `arg.cpp`, `server-common.cpp`, `llama-mmap.cpp`, `llama-kv-cache.cpp`
