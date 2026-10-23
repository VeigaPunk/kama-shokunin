ATTACK E26-12: holds

Targets attacked: SKILL.md:1095 (row E26-12), registry/error-signatures-r26.json entry
E26-12, corpus/SOURCES.md:137 (S125), corpus/lessons/round-26.md:38 (Gate quote for S125),
and the landed-tip receipt .ufo/waves/round-26/final/c1-tip-receipt.json (E26-12 block).

Port block used: 127.0.0.1:47744-47747, one child at a time, each wrapped in `timeout` and
killed; every port confirmed closed with `ss -ltn` after each run. Nothing was installed or
updated. All raw captures are in .ufo/waves/round-26/w2-falsify/out/AttackE2612/
(trigger-47744.out, server-47744.log, e2612-run1..4.log, source-check.out, scripts/).

Observation outside my block, left untouched: `pgrep -af llama-server` at the end showed one
process I did not start and did not kill —
`/home/vgpnk/.local/bin/llama-server ... --port 47719 -t 2 --embeddings --pooling mean`
(another seat's port, not in 47744-47747). My ports were free: `ss -ltn | grep -cE ':(4774[4-7])\b'` -> 0.

================================================================================
(1) Registered trigger re-run twice — PASS
--------------------------------------------------------------------------------
Launch (registry args are exactly `-t 2`; counter base argv is
`[SERVER, -m, model, --host, HOST, --port, P] + args`, .ufo/waves/round-26/count-c1.py:225-227):

  timeout 300 ~/.local/bin/llama-server -m /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf \
      --host 127.0.0.1 --port 47744 -t 2
  curl -sS -i -X POST http://127.0.0.1:47744/v1/audio/transcriptions \
      -H 'Content-Type: application/json' -d '{}'

Run 1 (47744) and run 2 (47745) produced byte-identical results:

  HTTP/1.1 501 Not Implemented
  Server: llama.cpp
  Content-Type: application/json; charset=utf-8
  Content-Length: 111

  {"error":{"code":501,"message":"The current model does not support audio input.","type":"not_supported_error"}}
  curl_exit=0

sha256 of that body = 7e1665fa588d3383ea04823856aefed0314b0fa6544b89f4a1c6219064443f66, which
equals `channel_sha256` in final/c1-tip-receipt.json for E26-12: my independent run reproduces
the tip receipt byte for byte. Ports closed after each run (`port 47744 closed`, `port 47745 closed`).
Each server log is 11 lines and contains the signature 0 times (`grep -c` -> 0, exit 1).

Extra variants (run 1 and run 4, evidence in trigger-47744.out):
  - body `not-json` (not valid JSON) -> same 501 body;
  - bodyless POST, no Content-Type -> same 501 body;
  - multipart `-F file=@/etc/hostname` -> same 501 body;
  - GET /v1/audio/transcriptions -> 404 `{"error":{"message":"File Not Found",...}}` (route is POST-only);
  - POST /audio/transcriptions (no /v1) -> same 501 body (server.cpp:294 registers the same handler).

Verdict: the row's trigger and its "-> 501" claim are exactly reproducible on this host.

================================================================================
(2) Own error text, not a warning (F1) and not an echo (F2/F3) — PASS
--------------------------------------------------------------------------------
F1 — not a warning line from an unrelated startup failure:
  The string exists in exactly one place in the pinned source, server-context.cpp:5655, inside
  the HTTP handler `post_transcriptions_oai` (server-context.cpp:5651). It is returned with
  `res->error(...)`, never logged. `grep -c "does not support audio input" server-47744.log` -> 0
  (exit 1). The row is an http-body row, and the text was observed in the response body.

F2 — not a decode of request content:
  The guard at server-context.cpp:5654 sits before `json::parse(req.body)` at 5661, and the live
  run proves the order: an invalid-JSON body still returns the same 501 message instead of a parse
  error. The registered body is `{}` — no request bytes can decode to the message. The counter's
  `e_not_echoed` is also true in the receipt.

F3 — not contents of an argument file: the registered args are `-t 2`; no file-naming argument.

================================================================================
(3) Pinned source line and the 'meaning (code)' cell — PASS
--------------------------------------------------------------------------------
Fresh fetch at commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad (access date 2026-10-23), URL
https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp,
sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329 (6320 lines) — identical
to the lane snapshot .ufo/waves/round-26/sources/llama.cpp-704366d/server-context.cpp and to the
S125 anchor sha256 (source-check.out).

  5651  this->post_transcriptions_oai = [this](const server_http_req & req) {
  5654      if (!meta->has_mtmd || !meta->chat_params.allow_audio) {
  5655          res->error(format_error_response("The current model does not support audio input.", ERROR_TYPE_NOT_SUPPORTED));
  5656          return res;
  5657      }

The cell's guard condition, its 5651-5657 range, and "-> 501" all check out:
  - has_mtmd = `impl->mctx != nullptr` (server-context.cpp:4825), i.e. an mmproj is loaded;
  - allow_audio = `mctx ? mtmd_support_audio(mctx) : false` (server-context.cpp:1632, the only
    assignment of chat_params, line 1625 — `grep -n "chat_params = " server-context.cpp` -> 1625);
  - ERROR_TYPE_NOT_SUPPORTED -> `code = 501` (server-common.cpp:115-117); observed 501.
  - the route is registered unconditionally for POST (server.cpp:293), so the handler is reachable
    on a text-only launch, which is what the fixture is.

================================================================================
(4) 'Next action' cell — PASS with one wording note
--------------------------------------------------------------------------------
"Model capability. Route audio to a model launched with an audio-capable `--mmproj`."
Supported: `allow_audio` is set only from `mtmd_support_audio(mctx)`; `grep -rn allow_audio`
over the snapshot yields exactly four sites (1632 init, 4826 props, 5654 this guard,
server-common.cpp:1271 the chat guard). No CLI flag toggles it, and `--audio` in arg.cpp:2633 is an
input-file option, not a capability toggle. So an audio-capable mmproj is the exact lever — the
advice is not overreach. Live corroboration of the observable: `GET /props` on the fixture returns
`modalities: {"audio": false, "video": false, "vision": false}` with build_info `b11755-704366d76`.

Note (not a defect, optional): "Model capability" slightly misplaces the cause. The guard tests the
*launch* (no mmproj loaded, or an mmproj without audio); the model file may be irrelevant. Smallest
correction if the cell is ever touched for another reason: "Launch capability: server started
without an audio-capable mmproj (`/props` shows `modalities.audio=false`)."

================================================================================
(5) SOURCES S125 cells and the lesson Gate quote — PASS
--------------------------------------------------------------------------------
corpus/SOURCES.md:137 S125:
  - URL `.../tools/server/server-context.cpp#L5655` resolves to the error line (fresh fetch 5655);
  - anchor sha256 dd1de0f2...c2329 equals the fresh whole-file hash and the lane snapshot;
  - teaches cell ("error emitted at line 5655 and its guard, at commit 704366d76 only") matches the
    code and the guard at 5654.
  - S125 is new this round: `git grep "^| S125 " 1560e4d8 -- corpus/SOURCES.md` -> exit 1 (absent);
    current SOURCES.md has exactly one S125; base's highest row is S113.

corpus/lessons/round-26.md:38 Gate row quotes line 5655 verbatim (modulo leading indentation) from
the fresh fetch; the URL and access date (2026-10-23) are right.

Row integrity, for completeness:
  - SKILL.md:1095 sits inside the section that starts at SKILL.md:1062 and parses to 6 cells
    against the 6-column header at 1082-1083;
  - the signature occurs once in SKILL.md and not at base:
    `git grep -F -e "The current model does not support audio input." 1560e4d8 -- SKILL.md corpus` -> exit 1;
  - the gate files are unchanged between the receipt's commit 7e5ff9b5 (a commit) and the landed
    tip f4066979 (`git diff --stat` over SKILL.md, corpus/SOURCES.md,
    registry/error-signatures-r26.json, .ufo/waves/round-26/sources/, count-c1.py -> empty, exit 0),
    so the counted row is the landed row.

================================================================================
Findings (none changes the counted status)
--------------------------------------------------------------------------------
D1 — ADVISORY, adjacency: E26-12 and E26-13 are one root condition, two counted rows.
  E26-12's guard `!has_mtmd || !allow_audio` (server-context.cpp:5654) collapses to
  `allow_audio == false`, because `has_mtmd == false` implies `allow_audio == false`
  (1632: `mctx ? mtmd_support_audio(mctx) : false`). E26-13's guard is literally
  `if (!opt.allow_audio) throw ...` (server-common.cpp:1270-1272). Same state, two entry points
  (dedicated transcription route -> 501; chat with input_audio -> 500).
  The frozen clause (g) tests signature substring/superset relations, channel-text overlap and
  trigger distinctness — not condition equivalence — so 17/17 stands and this is not a predicate
  violation. It is a depth-accounting note: the pair yields one fault, two rows.
  Smallest correction: no artifact change (the row is true and counted). If a future round writes
  the depth note, record that E26-12/E26-13 share `allow_audio == false`; and if strict
  "one fault, one counted row" is wanted, E26-12 is the row to keep (dedicated route, 501,
  launch-level fix) and E26-13 is its alternate symptom.

D2 — MINOR wording: "Model capability." vs launch capability (see check 4). Optional rephrase.

D3 — Saturation note for the judge, not a defect of this row: 7 of the 17 rows (E26-01, E26-02,
E26-04, E26-05, E26-08, E26-09, E26-12) claim 501 and all but E26-09 belong to the
"this server/model does not support X" family; E26-13 is the same family surfaced as 500. The
section's breadth is therefore concentrated in one message shape; each row is nevertheless a
distinct endpoint, message and fix, so the count is not inflated by split messages.

Impacted axes: depth (C1) — unchanged for E26-12; calibration — D1/D3 are notes about how the 17
signatures are distributed; adjacency — E26-12/E26-13 equivalence.

Files written:
  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/advice/AttackE2612.md (this report)
  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/AttackE2612/trigger-47744.out
  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/AttackE2612/server-47744.log
  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/AttackE2612/e2612-run1.log
  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/AttackE2612/e2612-run2.log
  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/AttackE2612/e2612-run3.log
  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/AttackE2612/e2612-run4.log
  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/AttackE2612/source-check.out
  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/AttackE2612/scripts/{evidence.sh,run1.sh,run3.sh,run4.sh}

Tools installed or updated: none.
