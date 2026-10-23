```RESULTS
command: /usr/bin/git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/RevRowC/lane
cwd: /tmp/kama-r31w2/RevRowC
exit: 0
verbatim tail:
Cloning into '/tmp/kama-r31w2/RevRowC/lane'...
done.

command: /usr/bin/sha256sum .ufo/waves/round-31/count-c1.py
cwd: /home/vgpnk/Projects/shokunin/kama-shokunin
exit: 0
verbatim tail:
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  .ufo/waves/round-31/count-c1.py

command: /usr/bin/git -C /tmp/kama-r31w2/RevRowC/lane checkout -q 382d11b2107d335705875da1a4d889b074bd6fa6
cwd: /tmp/kama-r31w2/RevRowC
exit: 0
verbatim tail:

command: /usr/bin/sha256sum .ufo/waves/round-31/count-c1.py
cwd: /tmp/kama-r31w2/RevRowC/lane
exit: 0
verbatim tail:
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  .ufo/waves/round-31/count-c1.py

command: /usr/bin/git -C /tmp/kama-r31w2/RevRowC/lane rev-parse HEAD
cwd: /tmp/kama-r31w2/RevRowC
exit: 0
verbatim tail:
382d11b2107d335705875da1a4d889b074bd6fa6

command: /usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane /tmp/kama-r31w2/RevRowC/lane --repo /tmp/kama-r31w2/RevRowC/lane --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowC/c1.json
cwd: /tmp/kama-r31w2/RevRowC/lane
environment override: TMPDIR=/tmp/kama-r31w2/RevRowC
exit: 0
verbatim tail:
registered 18 counted 17 target 12 met True not-counted ['K31-10']

command: /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowC/compare-hand-render.py
cwd: /tmp/kama-r31w2/RevRowC/lane
exit: 0
verbatim tail:
K31-07 | committed-cell==rendered yes | live-status 400
  committed=reject 400 invalid_request_error: All non-assistant messages must contain 'content'
  hand-render=reject 400 invalid_request_error: All non-assistant messages must contain 'content'
  live={"code": 400, "error_keys": ["code", "message", "type"], "message": "All non-assistant messages must contain 'content'", "status": 400, "type": "invalid_request_error"}
K31-08 | committed-cell==rendered yes | live-status 400
  committed=reject 400 invalid_request_error: Assistant message must contain either 'content' or 'tool_calls'!
  hand-render=reject 400 invalid_request_error: Assistant message must contain either 'content' or 'tool_calls'!
  live={"code": 400, "error_keys": ["code", "message", "type"], "message": "Assistant message must contain either 'content' or 'tool_calls'!", "status": 400, "type": "invalid_request_error"}
K31-09 | committed-cell==rendered yes | live-status 400
  committed=reject 400 invalid_request_error: Expected 'content' to be a string or an array
  hand-render=reject 400 invalid_request_error: Expected 'content' to be a string or an array
  live={"code": 400, "error_keys": ["code", "message", "type"], "message": "Expected 'content' to be a string or an array", "status": 400, "type": "invalid_request_error"}

command: /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowC/probe-meaning.py
cwd: /tmp/kama-r31w2/RevRowC/lane
environment override: TMPDIR=/tmp/kama-r31w2/RevRowC
exit: 0
verbatim tail:
owned-server-port 47945
base-user-string status=200 error=null
user-null status=200 error=null
user-number status=400 error={"code": 400, "message": "Expected 'content' to be a string or an array", "type": "invalid_request_error"}
assistant-content-only status=200 error=null
assistant-neither status=400 error={"code": 400, "message": "Assistant message must contain either 'content' or 'tool_calls'!", "type": "invalid_request_error"}
assistant-tool-calls-only status=400 error={"code": 400, "message": "Cannot continue an assistant message that contains tool calls.", "type": "invalid_request_error"}
```

FINDING: All three rejection outcomes reproduce and match hand-rendered cells byte for byte. K31-09's meaning excludes an accepted null value; K31-08's final clause has an overbroad literal reading despite its correct opening disjunction.

LIMITS: One pinned build/model/default-argv fixture, not a survey of message roles, content arrays, templates, models, or other builds. The exact rejection observations do not prove the meaning prose. The frozen counter's count is not an admission or a judgment of improvement. The tool-calls-only probe failed for a separate continuation rule, so it does not establish successful tool calling. No sampler-use, response-quality, or C2/C3 claim was tested. No tracked lane file or frozen counter was edited; no tools were installed or updated. This is advisory evidence only.

## Axes and row results

Axes: **depth** (the observed API contract), **calibration** (scope and correctness of meaning), **operability** (the resulting client advice). The defects below are fixable prose defects, not a reason to change the frozen predicate or the recorded error text.

```text
K31-07 | committed-cell==rendered yes | live-status 400 | overclaim none
K31-08 | committed-cell==rendered yes | live-status 400 | overclaim literal "neither omission is accepted" wrongly forbids individual omissions; content-only assistant was accepted without tool_calls
K31-09 | committed-cell==rendered yes | live-status 400 | overclaim "must send message content as a string or array" excludes null, which returned HTTP 200
```

## Independent derivation and evidence

The frozen tip's actual **RENDER** block is `count-c1.py` L50–54, not the assignment's L40–46. All three rows use the reject rule at L51: concatenate `reject `, status `400`, a space, type `invalid_request_error`, `: `, and the registry message verbatim. No counter render function was used for the independent comparison. The three manually substituted literals are recorded above and in `compare-hand-render.py`; `hand-render-comparison.json` preserves both UTF-8 byte strings as hex. Equality is for the outcome cell after trimming Markdown table padding, not the surrounding row delimiters.

The registry entries and the committed SKILL cells at L1253–1255 were read from the fresh clone pinned to `382d11b2107d335705875da1a4d889b074bd6fa6`. `c1.json` and `scoped-live.json` retain each live block: status/code 400, type `invalid_request_error`, exactly the error keys `code,message,type`, and the exact respective message. These are rejection-contract observations, not slot-setting or sampler claims.

- **K31-07 / S183:** `server-common.cpp` L1393–1395 checks a non-assistant role and absence of the content key, then throws the measured message. The measured user-message omission supports the recorded point, and the pinned conditional supports the scoped advice. This says nothing about which content values are valid or which earlier request errors take precedence.
- **K31-08 / S184:** L1397–1403 rejects only when **both** content and tool_calls keys are absent. The opening “content or tool_calls” clause is consistent with this. However, “neither omission is accepted” can be read as rejecting either individual omission. Our `assistant-content-only` request omitted tool_calls and returned 200; the bare assistant control returned the recorded 400. This is a wording ambiguity/overbroad literal clause, not evidence that the opening disjunction is wrong. The tool-calls-only request passed this particular presence guard but encountered the distinct continuation rejection at L1442–1446; do not relabel that as the measured missing-fields error or as a successful tool call.
- **K31-09 / S185 — strongest counterexample:** the request `{"messages":[{"role":"user","content":null}],"max_tokens":1}` returned **200**, a `chat.completion` body, and fingerprint `b11755-704366d76`. With content changed to 42, the directional control returned the same 400/type/message as K31-09. The pinned source explicitly accepts strings **or null** past the content-type guard at L1405–1407 before the array test at L1410–1411. Thus numeric rejection is measured correctly, but the meaning's asserted string-or-array-only rule is false on this very fixture. S185's prose description in `corpus/SOURCES.md` L197 repeats that same overgeneralization even though its quoted throw line is genuine.

## Smallest safe correction

Do not change the outcomes, error messages, registry observations, or frozen counter.

1. K31-08 meaning: **“An assistant message omitting both content and tool_calls is rejected with this error.”** This removes the ambiguous clause without promising that either field alone makes an entire request valid.
2. K31-09 meaning: **“This numeric content value is rejected with HTTP 400; the adapter also permits null through this content-type guard.”** Apply the same scope correction to S185's descriptive prose if that prose is retained. Keep the exact observed rejection message unchanged.
3. K31-07: no row correction identified within this scope.

These corrections improve calibration and client operability without erasing depth evidence. Whether the round otherwise qualifies remains exclusively with the canonical judge; no runtime judgment was invoked here.

## Retained artifacts and scope

- `commands.json`; `01-clone.log` through `08-meaning-counterexamples.log`: every subprocess command, cwd, exit, and raw merged stdout/stderr. The first, second and fourth/fifth prerequisites were batched when independent; the manual comparison and live meaning probe also ran concurrently. The empty checkout tail above is genuinely empty.
- `c1.json`: untouched full frozen-counter receipt; no retry was necessary.
- `scoped-live.json`, `hand-render-comparison.json`, `compare-hand-render.py`: row live blocks and independent literal/UTF-8 comparisons.
- `meaning-probe.json`, `probe-meaning.py`, `probe-*-request.json`, `probe-*-response.body`: actual counterexample/control requests, headers, and raw response bytes.
- `meaning-probe-server-before-shutdown.log`: server log copied before shutdown; it is not advertised as a shutdown log. The probe verified server/library/model digests and used the frozen counter's local server helper; only its own process was stopped.

All seat writes are inside this directory or `/tmp/kama-r31w2/RevRowC/`. The requested sibling trailer file `w2/out/RevRowC.md` was not created because the governing seat bound permits writes only inside `w2/out/RevRowC/`; this report is the scoped deliverable at the explicitly requested `RevRowC/report.md` path.
