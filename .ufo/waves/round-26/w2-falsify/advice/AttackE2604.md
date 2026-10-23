ATTACK E26-04: partial

The counted row holds: the signature is the fault's own text, the trigger reproduces twice on the
pinned binary, the source pin and line numbers are exact, and S117 is sound. One cell breaks:
the "next action" tells the reader that re-launching with `--props` is how to change global
properties, but on b11755 `post_props` is a stub — with `--props` it answers `{"success":true}`
and changes nothing. The row's remedy produces a false confirmation.

Lane: /home/vgpnk/Projects/shokunin/kama-shokunin, HEAD f4066979096e3452ae731c0e09e50155c6d8258a
(`git rev-parse HEAD`), row at SKILL.md:1087, registry entry at
registry/error-signatures-r26.json (`id: E26-04`), SOURCES row at corpus/SOURCES.md:129,
lesson Gate row at corpus/lessons/round-26.md:30. Ports used: 47712-47715 only.

## (1) Re-run of the registered trigger — HOLDS

Two runs, each a fresh child, exactly the registered fields plus the counter's base argv
(registry `channel: http`, `args: ["-t","2"]`, `model: fixture`, request `POST /props`,
`Content-Type: application/json`, body `{"chat_template":"x"}`):

	llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 47712 -t 2
	curl -X POST http://127.0.0.1:47712/props -H 'Content-Type: application/json' -d '{"chat_template":"x"}'

Run 1 and run 2, identical:

	HTTP/1.1 501 Not Implemented
	Content-Type: application/json; charset=utf-8
	Content-Length: 144
	{"error":{"code":501,"message":"This server does not support changing global properties. Start it with `--props`","type":"not_supported_error"}}
	CURL_STATUS=501   post_curl_exit=0
	GET /props -> GET_STATUS=200

Reproducibility against the counter: my captured body, newline stripped, is 144 bytes and
sha256 `cb686d2d2940d1d40af99cdcf32bfef3f0d01edd0307a61e88145ffb67e8caa8` — byte-identical to
`channel_sha256` for E26-04 in .ufo/waves/round-26/final/c1-tip-receipt.json (`status: 501`,
`e_signature_seen: true`). The counter's own run and mine are the same bytes.
Health gate `GET /health -> 200` before each request; each child killed, `wait`ed, and the port
re-checked closed (`port_closed_check: closed`), then `pgrep -af llama-server` showed none of mine.

## (2) Own error text, not a warning and not an echo — HOLDS (F1/F2/F3 all clear)

- F1: the string occurs once in the pinned tree, at server-context.cpp:5453
  (`grep -rn "changing global properties" .ufo/waves/round-26/sources/llama.cpp-704366d` →
  only `./server-context.cpp:5453` plus `./arg.cpp:3641`, whose text is different and does not
  contain the signature). Both startup logs contain zero occurrences
  (`grep -c` on server_run1.log, server_run2.log -> 0). Clause (f): exact-signature and
  whitespace-stripped search of `llama-server --help` (exit 0) and `--version` (exit 0) is
  False/False in both; help line 626 is the different `--props enable changing global
  properties via POST /props (default: disabled)` text.
- F2/F3: the refusal is independent of every request field. Same server, no `--props`:
  `POST /props` with no body and no Content-Type -> 501, same message;
  `POST /props?chat_template=INJECT-QUERY` with `Content-Type: text/plain` body
  `INJECT-BODY {not json` -> 501, same message, no `INJECT-` text anywhere in the response;
  a request header carrying the signature itself -> 501, same message. Structurally confirmed:
  the handler signature is `[this](const server_http_req &)` with an unnamed parameter
  (server-context.cpp:5450), so the request object is not even reachable; the guard is the
  first statement (5452). The counter's `e_not_echoed` inspects only the request string, so the
  counter would pass an echo if one existed — for this row it cannot exist.

## (3) Pinned source, guard, line numbers, status — HOLDS

Fresh fetch (access date 2026-10-23) of
https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp
-> http 200, 264205 bytes, sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`,
equal to the lane snapshot (.ufo/waves/round-26/sources/llama.cpp-704366d/server-context.cpp) and
to the S117 anchor cell. Lines, identical in fetch and snapshot:

	5450  this->post_props = [this](const server_http_req &) {
	5451      auto res = create_response();
	5452      if (!params.endpoint_props) {
	5453          res->error(format_error_response("This server does not support changing global properties. Start it with `--props`", ERROR_TYPE_NOT_SUPPORTED));
	5454          return res;
	5455      }
	5456      // update any props here
	5458      res->ok({{ "success", true }});

The row's "meaning (code)" claims: guard `params.endpoint_props` false, range 5452-5454
(guard + error + early return — exact), and "`GET /props` still answers". Both supported:
`ERROR_TYPE_NOT_SUPPORTED` maps to 501 in server-common.cpp:115-117; `endpoint_props` defaults
false in common/common.h:687 with the upstream comment "only control POST requests, not GET";
`GET /props` and `POST /props` routes are registered unconditionally (server.cpp:281-282), and
the live `GET /props` returned 200 with `endpoint_props` in the body. The "→ 501" trigger cell is
exact.

## (4) "Next action" cell — BREAKS

Cell: "Changing global properties is off; reading them is not. Re-launch with `--props` only if a
consumer must change them."

The first sentence holds. The second is not supported by the code it cites and is contradicted
by observation. With `--props` on port 47713:

	POST /props {"chat_template":"CHANGED-TEMPLATE-PROBE"} -> 200 {"success":true}
	GET /props before and after -> sha256 17fb6a47876567c958c1d84666a6f311ee1a42cfc8f2e209fa450218f8833d94
	  (byte-identical, `dict_equal_before_after: true`), probe absent from the served props

and a malformed body (`not json at all`) also returns 200, because the handler never reads the
request. The code says the same thing: lines 5456-5458 are the comment `// update any props here`,
a blank line, and `res->ok({{ "success", true }});` — no write path. So on this build `--props`
converts the 501 into a success acknowledgement that changes nothing; an operator following the
cell will believe a global property was changed when it was not. This is the false-confirmation
failure mode, not a cosmetic wording issue, and the C1 counter cannot see it (it only exercises
the refusal path, with `--props` absent).

Smallest correction (one cell, no new claim, keeps the row counted):

	| ... | Changing global properties is off; reading them is not. On b11755 `--props` only silences the 501: `post_props` applies nothing (`server-context.cpp:5456-5458`) and answers `{"success":true}` with the served props unchanged; set the template at launch (`--chat-template-file`). | S117 |

The launch-time alternative is verified, not assumed: a server started with
`--chat-template-file <file>` on port 47715 served that file verbatim from `GET /props`
(`file_template_served: True`, status 200), while the same field did not move under `POST /props`.
Optional, if the L1 prefers the meaning cell to carry it: append
"; when enabled, `post_props` applies nothing (`server-context.cpp:5456-5458`)" there instead.
Do not touch the signature, trigger, source or id cells — those are correct.

Impacted axis: depth (quality of the remedy in a counted row). Claim impact: none — the row still
counts, so `registered 17 counted 17` is unchanged; this is a defect inside a counted row, not a
counting defect.

## (5) S117 cells and the lesson Gate quote — HOLDS (one cosmetic note)

corpus/SOURCES.md:129: URL anchor `#L5453` points at the error line (correct); anchor sha256
`dd1de0f2...c2329` matches the fresh fetch (correct); "teaches" — "the E26-04 error emitted at
server-context.cpp line 5453 and its guard, at commit 704366d76 only; not other builds" —
matches what the code and the live run show; source kind "code" is right (this is an HTTP body,
not a log). Clause (c) holds: `git show 1560e4d8:corpus/SOURCES.md | grep -c S117` -> 0, and the
section heading is absent at base (`grep -c` -> 0), so the row and section are new.

Lesson Gate quote, corpus/lessons/round-26.md:30, is verbatim against line 5453 of both the
snapshot and the fresh fetch.

Cosmetic (systemic, not specific to this row): that Gate cell is a single-backtick code span whose
content itself contains backticks around `--props`, so the span closes early and the remainder
renders as prose. The same pattern is in the S114-S120 rows. Smallest fix: use a double-backtick
fence for those cells (or move the quotes to a fenced block). No content change.

## Countered non-defects (checked, so they need not be re-litigated)

- Receipt tree vs landed tip: the receipt is at tree `7e5ff9b5...`, HEAD is `f4066979...`;
  `git diff --stat 7e5ff9b5 f4066979 -- SKILL.md registry/error-signatures-r26.json
  corpus/SOURCES.md corpus/lessons/round-26.md` is empty, and the E26-04 row at f4066979 is the
  row at SKILL.md:1087 — the receipt covers the landed row.
- Clause (b): `git grep -F -c "<signature>" 1560e4d8 -- SKILL.md corpus` -> exit 1 (no match).
- Clause (g): the signature occurs once in SKILL.md at tip (`grep -c` -> 1), and it is not a
  substring of any other counted signature's body (the "This server does not support " family
  shares a prefix, not a containment relation).
- The sibling `llama-server` on port 47719 observed during cleanup is not mine (outside my block);
  it was left alone.

## Files written

- .ufo/waves/round-26/w2-falsify/advice/AttackE2604.md (this report)
- /fast/scratch/hyaku/kama-r26w2/AttackE2604/{run.sh, props_on.sh, props_on2.sh, f2f3.sh, tmpl.sh},
  server_run1.log, server_run2.log, post_props_run1.out, post_props_run2.out, body1.json,
  body2.json, get_props_run1.json, get_props_run2.json, props_on.log, props_before2.json,
  props_after2.json, post_on.out, f2f3.log, help.out, version.out, props_on2.log, sc.cpp,
  common.h, tmpl.jinja, tmpl.log, tmpl_props.json

No tools installed or updated. No lane production file, fleet path, sibling lane, config or cache
was written; no jj or state-mutating git command was run.
