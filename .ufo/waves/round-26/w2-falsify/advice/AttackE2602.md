ATTACK E26-02 (SKILL.md row + registry entry; S115 = server-context.cpp:5408): holds — all five checks pass; one low-severity wording gap in the next-action cell (the directory must exist), no counter-limit breach

Seat: KamaR26.AttackE2602 (wave 2 FALSIFY, round 26). Run 2026-10-23 00:58-01:02Z. Port block 47704-47707; one child at a time; no tools installed or updated; no lane production file edited; no counter run (the landed receipt already carries the counter's run of this row, and I re-ran the trigger myself instead).

## Verdicts

| check | verdict |
|---|---|
| (1) re-run registered trigger twice | holds — 501 both runs, body byte-identical to the counter's recorded channel text |
| (2) fault's own text, not F1 warning, not F2/F3 echo | holds |
| (3) pinned source line, fresh fetch, meaning (code) cell | holds — guard, line numbers and 501 mapping all exact |
| (4) next action supported, not overreach | holds; one low-severity gap: `--slot-save-path` needs an **existing** directory |
| (5) SOURCES S115 cells + lesson Gate quote | holds |

## Pins (re-checked)

- `sha256sum ~/.local/bin/llama-server` → `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` (= `count-c1.py` `SERVER_SHA256`). `llama-server --version` → `version: 0.7.0-dev (build 11755, commit 704366d76)`.
- `sha256sum ~/.cache/kama-shokunin/models/stories260K.gguf` → `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (= `MODEL_SHA256`).
- `sha256sum .ufo/waves/round-26/count-c1.py` → `6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588` (= frozen value; also `final/tip-counter-sha.txt`).
- Fresh fetch, commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad (`curl -sL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp`, exit 0): `sha256sum fresh-server-context.cpp` → `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`; lane snapshot `.ufo/waves/round-26/sources/llama.cpp-704366d/server-context.cpp` → same digest (= S115 anchor cell and `SOURCE_SHA256["server-context.cpp"]`).
- Registry entry (`registry/error-signatures-r26.json`, id E26-02): channel `http`, args `["-t","2"]`, model `fixture`, `occupy_port` false, request `POST /slots/0?action=save`, headers `{}`, body `{"filename":"s0.bin"}`, source S115 / `server-context.cpp`.

## (1) Re-run of the registered trigger — holds

Command (`/fast/scratch/hyaku/kama-r26w2/KamaR26.AttackE2602/run1.sh <port>`): `timeout 120 llama-server -m <fixture> --host 127.0.0.1 --port <P> -t 2` (start_new_session, log to file), `/health` poll to 200, then `curl -s -i -X POST -H 'Content-Type: application/json' -d '{"filename":"s0.bin"}' http://127.0.0.1:<P>/slots/0?action=save`, then SIGTERM + `ss -ltn`. `ss -ltn` showed the block free before the first run.

Run 1 (port 47704), driver exit 0:
```
HTTP/1.1 501 Not Implemented
{"error":{"code":501,"message":"This server does not support slots action. Start it with `--slot-save-path`","type":"not_supported_error"}}
server exit=0   (after SIGTERM)
port 47704 closed: yes (ss -ltn shows no listener)
```
Run 2 (port 47705), driver exit 0: same status, same body; `server exit=1` after SIGTERM (signal-timing only, the body and status are identical); port 47705 closed: yes.

Independent match against the landed tip receipt: `sha256sum` of both response bodies → `93b83e653dfde42dc8221925d50c368e7d31465cc2fb7a2298f970658338ad93`, equal to `final/c1-tip-receipt.json` → `rows[E26-02].observed.channel_sha256` (139-byte body, no trailing newline). The counter's own observed status for this row is `501`; the row's "→ 501" and the registry's channel/request/args reproduce it exactly.

## (2) Own error text, not a warning / unrelated path / echo — holds

- Source uniqueness: `grep -rn "does not support slots action" .ufo/waves/round-26/sources/llama.cpp-704366d/` → exactly one hit, `server-context.cpp:5408` (inside `server_context::post_slots`). No other code path can print this text.
- Not a startup warning: run-1 log (`srv-run1-47704.log`) shows the model loading and `llama_server: model loaded`, `listening on http://127.0.0.1:47704`, `/health` 200 before the request; `grep -cF "does not support" srv-47704.log` → 0; `grep -cF "does not support slots action"` → 0. The only warnings are bad-special-token and no-API-key lines, unrelated. So F1 does not apply.
- Not an echo (F2/F3): the guard precedes every use of the request (see check 3), so nothing is decoded before the error is formatted. Live probe (`probe-echo.sh`, port 47704, exit 0): sending `{"filename":"MARKER_ZZ_9f3c","note":"MARKER_ZZ_9f3c"}` with `&marker=MARKER_ZZ_9f3c`, and separately sending the signature text itself unicode-escaped as `filename`, both returned the byte-identical 501 body with no marker echoed. Registry request bytes (`\n`.join of the trigger key, `-t 2`, path, `{}` headers, `{"filename": "s0.bin"}`) contain no part of the signature, and no registry arg is a file path (F3 has no carrier here: the only file argument is the counter's own `-m`).
- Clause (f) side-check: the signature occurs in neither `llama-server --help` nor `--version`, verbatim (`grep -cF` → 0 in each) or whitespace-squashed (python check → `False`).

## (3) Pinned source line and meaning (code) cell — holds

`server-context.cpp` at 704366d (fresh fetch, digest in Pins), exact lines:
```
5405:     this->post_slots = [this](const server_http_req & req) {
5406:         auto res = create_response();
5407:         if (params.slot_save_path.empty()) {
5408:             res->error(format_error_response("This server does not support slots action. Start it with `--slot-save-path`", ERROR_TYPE_NOT_SUPPORTED));
5409:             return res;
5410:         }
5412:         std::string id_slot_str = req.get_param("id_slot");
5422:         std::string action = req.get_param("action");
```
- Guard condition is exactly `params.slot_save_path.empty()` (5407) and the refusal is before the first `req.get_param`/`req.body` use (5412, 5422) — "refuses every save/restore/erase action before reading it" is literal, and it does not overreach: save/restore/erase dispatch happens only at 5424-5434.
- Line range `5407-5409` in the row and in S115's teaches cell is exact (guard, error, return).
- Status mapping: `ERROR_TYPE_NOT_SUPPORTED` → `code = 501` (`server-common.cpp:115-117`), and `server_http_res::error` sets `status = json_value(error_data, "code", 500)` (`server-context.cpp:4872-4874`), so 501 is the code the wire carries — observed.
- The route is registered unconditionally (`server.cpp:319: ctx_http.post("/slots/:id_slot", …)`), so the trigger needs no `--slots`; the live runs used only `-t 2` as the row and registry say.

## (4) Next action — holds, one low-severity wording gap

Live support (`probe-fix.sh`, port 47706, driver exit 0): identical argv plus `--slot-save-path /fast/scratch/hyaku/kama-r26w2/KamaR26.AttackE2602/saves` (pre-created) →
```
HTTP/1.1 200 OK
{"id_slot":0,"filename":"s0.bin","n_saved":0,"n_written":36,"timings":{"save_ms":0.077}}
```
and `saves/s0.bin` exists at 36 bytes. `POST /slots/0?action=bogus` on the same server → 400 `Invalid action`, i.e. the guard really was the only blocker. "or stop sending slot actions" is self-evidently supported. So the remedy is real, not a dead end.

Gap: `--slot-save-path` is validated at launch and a non-existent path aborts startup — `arg.cpp:3659-3661`: `if (!fs_is_directory(params.slot_save_path)) { throw std::invalid_argument("not a directory: " + value); }`. "a writable directory" does not tell a reader the directory must already exist.

Smallest correction (optional, low): change the next-action cell to "Set `--slot-save-path` to an **existing** writable directory, or stop sending slot actions." No status, signature, source or trigger cell changes; the counter is unaffected.

Supporting observation, not a defect of this row: on this build `GET /slots` answers 200 with no flag (`probe-defaults.sh`, port 47707, exit 0: `GET /slots -> 200`, `GET /props -> 200`), i.e. `endpoint_slots` is enabled by default here — which is why the counter's baseline (it requires 200 on `GET /slots`) can pass, and why E26-01's trigger correctly says `--no-slots` while E26-02's correctly does not.

## (5) SOURCES S115 and the lesson Gate quote — holds

`corpus/SOURCES.md:127`, 11 cells under the `| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |` header:
- URL: `https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5408` — 40-char commit; the page resolves (`curl -sL -o /dev/null -w '%{http_code}'` → 200) and line 5408 is the error line shown above. Correct anchor line.
- anchor cell: `server-context.cpp line 5408 @ 704366d76…; sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` — equals the fresh fetch and the lane snapshot (Pins). Correct.
- teaches cell: "`post_slots` refuses every save/restore/erase action before reading it when `params.slot_save_path` is empty (`server-context.cpp:5407-5409`). Live trigger and next action: SKILL.md row E26-02." — matches the code (check 3) and points at the right row. `scope` ("at commit 704366d76 only; not other builds") is appropriately narrow; `status` `mined`, `opened` `2026-10-23`, `recheck` `on-release`, `used-by` `SKILL.md, registry/error-signatures-r26.json` — the only two files that carry the signature today (`grep -rF -l` over `SKILL.md corpus/ registry/` → `SKILL.md`, `corpus/lessons/round-26.md`).
- Clause (c) side-check: `git show 1560e4d83f42b04f40336357de6f9637eafa0f4b:corpus/SOURCES.md | grep -c '^| S115 '` → `0` (row new this round); `git grep -F` for the signature at the same base over `SKILL.md corpus` → exit 1 (absent).
- Lesson Gate (`corpus/lessons/round-26.md:28`), S115 row: `| S115 | https://…/server-context.cpp#L5408 | 2026-10-23 | line 5408: `res->error(format_error_response("This server does not support slots action. Start it with `--slot-save-path`", ERROR_TYPE_NOT_SUPPORTED));` |`. Programmatic check: quote starts `line 5408: `, the code span stripped of its wrapping backticks is an exact substring of source line 5408 (`l.strip() == core` → True), 14 words (limit 25), access date and URL agree with the SOURCES row. Correct.
- Section placement: heading `## Round-26 live error signatures (b11755 fixture, owner: kama)` at `SKILL.md:1062`; no heading intervenes before the row at `SKILL.md:1085`, so the counter's `skill_rows` attributes E26-02 to this section. Registry signature (75 bytes) is present verbatim in the row and `\bS115\b` matches.

## Defects

1. Low — next-action cell requires a directory that already exists (see check 4). Correction: "Set `--slot-save-path` to an existing writable directory, or stop sending slot actions."

No other defect found. Nothing in F1-F3 touches this row: the signature has one source occurrence in the error path, no request field is decoded before it is formatted, and no argument file is involved.

## Files written

- `.ufo/waves/round-26/w2-falsify/advice/AttackE2602.md` (this report)
- `.ufo/waves/round-26/w2-falsify/out/KamaR26.AttackE2602/` — `body-run1-47704.json`, `body-run2-47705.json` (both sha256 `93b83e65…ad93`), `srv-run1-47704.log`, `srv-run2-47705.log`, `srv-fix-47706.log`, `srv-echo-47704.log`
- Scratch (not in the lane): `/fast/scratch/hyaku/kama-r26w2/KamaR26.AttackE2602/` — `run1.sh`, `probe-fix.sh`, `probe-echo.sh`, `probe-defaults.sh`, `fresh-server-context.cpp`, `help.txt`, `version.txt`, server logs, `saves/s0.bin`

Ports 47704-47707 were free before use and show no listener now; every server I started was killed and reaped (the `llama-server` on port 47719 visible during the run is not mine — outside my block).
