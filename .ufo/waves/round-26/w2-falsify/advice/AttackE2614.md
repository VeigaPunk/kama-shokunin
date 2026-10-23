ATTACK E26-14: partial

The registered claim (live 400 + signature in body + S127 pin) survives every factual
check; two prose cells of the row are wrong or unusable: the meaning cell's line span
and its "throws for anything else" claim, and the next-action cell omits the
`prompt_string` key the fix depends on. Details per check below. Nothing under the
lane was edited; port block 47752-47755 only; no server of mine is left running.

Target under attack
- SKILL.md:1062 section `## Round-26 live error signatures`, row at SKILL.md:1097.
- registry/error-signatures-r26.json entry `E26-14` (signature 134 bytes:
  `\"prompt\" elements must be a string, a list of tokens, a JSON object containing a
  prompt string, or a list of mixed strings & tokens.`).
- corpus/SOURCES.md:139 row `S127`; corpus/lessons/round-26.md:40 Gate row `S127`.

(1) Re-run of the registered trigger, twice — HOLDS
Registry fields used verbatim: channel `http`; args `["-t","2"]`; model `fixture`
(`~/.cache/kama-shokunin/models/stories260K.gguf`, sha256
`270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`); request
`POST /completion` body `{"prompt": {"not_prompt": true}}`; `occupy_port` false.
Fixture sha256 of `~/.local/bin/llama-server` =
`b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` (equal to the
counter pin); `llama-server --version` prints
`version: 0.7.0-dev (build 11755, commit 704366d76)`.

argv per run: `llama-server -m <fixture> --host 127.0.0.1 --port <P> -t 2`, one child
at a time, `ss -ltn` showed 47752-47755 free before the runs.
- Run 1, port 47752: ready in 0.25 s; request 1 -> `400`, request 2 -> `400`,
  Content-Type `application/json; charset=utf-8`. Body (both):
  `{"error":{"code":400,"message":"\"prompt\" elements must be a string, a list of tokens, a JSON object containing a prompt string, or a list of mixed strings & tokens.","type":"invalid_request_error"}}`
  Signature present verbatim in the body both times.
- Run 2, port 47753: identical, `400` both requests, same body bytes.
- Body sha256 of all four responses: `0c47e832faed0a6ab7b38f4f777ad85434b0486358977f37853bae6a40f827ff`,
  byte-identical to `observed.channel_sha256` for E26-14 in
  `.ufo/waves/round-26/final/c1-tip-receipt.json`. The landed observation reproduces
  exactly from a fresh process, independent of the counter's own run.
- Teardown: SIGTERM to the process group, `exit=0`, port closed (polled `ss`/connect),
  `pgrep -af llama-server` shows none of my pids (1443193, 1444003, 1507125). A
  foreign `llama-server ... --port 47719 --embeddings` (pid 1665632, sibling seat)
  remained; not mine, not killed.

(2) Fault's own error text, not a warning, not an echo (F1/F2/F3) — HOLDS
- The message literal occurs exactly once across all 13 pinned sources:
  `grep -rn "elements must be a string" .ufo/waves/round-26/sources/llama.cpp-704366d/`
  -> 1 hit, `server-common.cpp:1114`, a `throw std::invalid_argument(<string literal>)`
  with no format arguments. It cannot be assembled from request data.
- Path: `tokenize_input_subprompt` (server-common.cpp:1084-1116) throws at 1114; the
  `/completion` handler `server_routes::handle_completions_impl` (server-context.cpp:4886)
  catches it at `server-context.cpp:4968-4970` and returns
  `format_error_response(e.what(), ERROR_TYPE_INVALID_REQUEST)`; server-common.cpp:91-96
  maps that type to `code = 400`, `"invalid_request_error"`. Observed status matches.
- F1 (warning on an unrelated startup failure): not applicable and not happening — the
  row's channel is `http`, and the signature does not appear anywhere in the server log
  of either run (`log_sig_present=False`, logs 990 B each) nor in the log of the probe
  run (5527 B).
- F2 (request echo through JSON escapes): the signature is not in the request. I rebuilt
  the counter's own `req_bytes` for this row (count-c1.py:378-383) —
  `{"args": ["-t", "2"], "channel": "http", "model": "fixture", "occupy_port": false,
  "request": {"body": {"prompt": {"not_prompt": true}}, "headers": {}, "method": "POST",
  "path": "/completion"}}` plus args/path/headers/body — and the signature is not a
  substring of it. The backslashes in the signature are the server's own JSON escaping
  of `"prompt"`, i.e. output, not a decode of the request; SKILL.md:1066-1068 states this
  convention explicitly.
- F3 (echo through argument file contents): args are `-t 2`, no path/file argument; the
  counter forbids file-shaped args anyway (count-c1.py:96-97).
- Clause (f) independently: `llama-server --help` (60469 B, exit 0) and `--version`
  (90 B, exit 0) contain neither the signature nor its whitespace-squashed form; a
  healthy baseline server answered all 7 baseline requests (health, /v1/models, /props,
  /slots, /completion, /v1/chat/completions, /tokenize) with 200 and the signature in
  none of the bodies.
- Clause (b) independently: `git -C . grep -F -q -e '\"prompt\" elements must be a string'
  1560e4d83f42b04f40336357de6f9637eafa0f4b -- SKILL.md corpus` -> exit 1 (absent at base).
- Clause (g) independently over the landed receipt: no substring/superstring relation
  between this signature and any of the other 16 registered signatures, no duplicate
  trigger, and the signature does not occur in any other row's recorded
  `channel_excerpt`. The receipt records 17 of 17 counted.

(3) Meaning (code) cell — PARTIAL (two defects; the status claim is right)
SKILL.md:1097 meaning cell: "prompt parsing accepts a string, token list, object with a
prompt string, or mixed list, and throws for anything else (`server-common.cpp:1108-1115`)".

3a. Line span is wrong for the claim. In the fresh fetch and the lane snapshot, the
acceptance conditions are at 1088 (`is_string() || json_is_array_of_mixed_numbers_strings`),
1092 (`json_is_array_of_numbers`), 1096 (`contains("prompt_string")`); the cited
1108-1115 starts inside the accepted object branch (1108 is the `} else {` of the
not-multimodal case), so the range shows one accepted shape and the throw but not the
conditions that define the enumeration. Smallest correction: `server-common.cpp:1088-1115`
in SKILL.md:1097 and in the S127 teaches cell (the same span is repeated there).

3b. "throws for anything else" is false for the `prompt` value as a whole. Arrays are
fanned out one task per element by `tokenize_input_prompts` (server-context.cpp:1118-1123),
so a shape the cell does not list is accepted end-to-end. Observed on port 47754, same
launch: `POST /completion {"prompt": ["a","b"], "n_predict": 2}` -> `200` with two
results; `{"prompt": {"prompt_string": "hi"}, "n_predict": 2}` -> `200`. The enumeration
is exhaustive only per element. Smallest correction: "each prompt element must be one of
those four shapes; a JSON array is fanned out one task per element
(`server-context.cpp:1118-1123`), so `{"prompt":["a","b"]}` is accepted (200)".

Status/exit claim: the trigger cell's `400` is confirmed twice; no exit-status claim is
made (http channel), correct.

Not a defect, recorded because it bears on clause (g): the trigger is not the only body
that yields this text — `{"prompt": 5}` also returns the identical 400, i.e. the message
is the catch-all for any non-conforming prompt element. That is consistent with the
row's wording and with the counter's one-fault-one-row rule (distinct triggers only).

(4) Next-action cell — HOLDS as supported, but unusable as written (one defect)
"Client bug: send `prompt` in one of the four accepted shapes." is supported: the
request is malformed and the server answers `400 invalid_request_error`; the cause is
client-side. But the accepted object shape needs the key `prompt_string`
(server-common.cpp:1085, checked at 1096), not a field named `prompt`. Observed on port
47754: `{"prompt": {"prompt": "hi"}}` -> `400` with this exact message, while
`{"prompt": {"prompt_string": "hi"}}` -> `200`. A client that follows the message's own
phrase "a JSON object containing a prompt string" literally keeps failing.
Smallest correction: "Client bug: send `prompt` as a string, a token array, a mixed
array, or `{"prompt_string": ...}` (the object key is `prompt_string`; `{"prompt":
{"prompt": "hi"}}` still returns this 400)."

(5) SOURCES S127 cells and the Gate quote — HOLDS (teaches cell inherits 3a/3b)
- Column count 11, matching the header at corpus/SOURCES.md:11; kind `code`, tier `A`,
  status `mined`, opened `2026-10-23`, recheck `on-release`, used-by
  `SKILL.md, registry/error-signatures-r26.json` are all consistent with sibling rows
  S114-S126.
- URL cell: `.../blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1114`;
  `curl -L` on that blob URL -> HTTP 200 (exit 0). Fresh fetch of the raw file at
  704366d76f8748cf9ad3df62a464bfcc8d1ae6ad -> sha256
  `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442`, 2147 lines,
  equal to the anchor cell, equal to the lane snapshot
  `.ufo/waves/round-26/sources/llama.cpp-704366d/server-common.cpp`, and equal to the
  counter pin; `diff` of lines 1088-1116 between fetch and snapshot -> identical; line
  1114 is the throw, byte for byte, including `\"prompt\"` and `strings & tokens.");`.
- scope cell ("line 1114 and its guard, 704366d76 only; not other builds") is accurate.
- teaches cell repeats the SKILL meaning cell verbatim, so it carries defects 3a and 3b;
  fix both together.
- corpus/lessons/round-26.md:40 Gate row: quote is a 25-word exact prefix of line 1114
  (checked by prefix comparison), access date 2026-10-23, URL matches the S127 cell.
  Holds.

Net
- Predicate (a)-(g) and the live claim: sound, independently reproduced.
- Defects are confined to the row's prose: SKILL.md:1097 meaning cell (3a span, 3b
  exhaustiveness) and next-action cell (4, `prompt_string`); corpus/SOURCES.md:139
  teaches cell inherits 3a/3b. None of them changes the counted status; all three are
  single-cell text edits that leave the signature, the S127 token and the file/commit
  citations intact.

Commands and exit codes (abridged, all run from the lane root unless stated)
- `sha256sum ~/.local/bin/llama-server ~/.cache/kama-shokunin/models/stories260K.gguf` -> exit 0, hashes as above.
- `~/.local/bin/llama-server --version` -> exit 0; `--help` -> exit 0, 60469 B.
- `curl -sSfL -o fresh-server-common.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp` -> exit 0; `sha256sum` -> b4f4aae7...d442.
- `git -C . grep -F -q -e '\"prompt\" elements must be a string' 1560e4d8... -- SKILL.md corpus` -> exit 1 (absent at base). Read-only.
- Live runs: python launcher in /fast/scratch/hyaku/kama-r26w2/AttackE2614, ports 47752/47753/47754, each child SIGTERM'd in its own session, `exit=0`, port closed; `ss -ltn | grep -E ':(47752|47753|47754)\b'` -> no output (exit 1).
- Tools installed or updated: none.

Files written
- .ufo/waves/round-26/w2-falsify/advice/AttackE2614.md (this report)
- .ufo/waves/round-26/w2-falsify/out/AttackE2614/e26-14-live.json (two-run statuses, bodies, body sha256, teardown)
- .ufo/waves/round-26/w2-falsify/out/AttackE2614/probe-47754.json (baseline sweep and accepted-shape probes)
- scratch: /fast/scratch/hyaku/kama-r26w2/AttackE2614/ (logs, help/version text, fresh fetch, same JSONs)

Confidence: high on (1), (2), (5) and on the two live counterexamples in (3b) and (4);
high on (3a) line numbers (fresh-fetch diff, exact).
Remaining unknowns: none blocking. The only unverified corner is full channel texts of
the other 16 rows for clause (g) (the receipt stores 400-byte excerpts only); that does
not touch E26-14's own evidence.
