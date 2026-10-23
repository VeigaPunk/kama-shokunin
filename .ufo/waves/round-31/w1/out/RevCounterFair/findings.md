# RevCounterFair — is the C1 counter honest about its own class?

Reviewer audit of the frozen round-31 C1 counter (`.ufo/waves/round-31/count-c1.py`,
sha256 `d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216` — byte-verified against
preregistration.json `C1.counter_sha256`). All fixtures were built and run in my scratch clone
`/tmp/r31w1-RevCounterFair` (cloned from the lane, checked out at `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e`,
one branch per fixture: `f1` = 3acaa3b552c56bbe63a3e744e7c3703ea0358f66, `f2` = ffa175809b3698b5d598147741b1a3fa700306ce,
`f3` = 735c00d4dd12c4f4ccb58ba15afdcf7ac153e98a). Every fixture registry/SKILL/SOURCES row is an
adversarial audit artifact that exists only in the scratch clone; none of it is lane data.

## Fixture 1 — `ignored` claim true only because the normalized-response check omits the changed field

Row F1R: `param=response_format`, `sent={"type":"json_object","schema":{…story:string…}}`,
`outcome.kind=ignored`. Grounds: at 704366d `response_format` is in the counter's own `OAI_STANDARD`
list, is declared nowhere in `server-schema.cpp` (`schema_declares("response_format") = False`; no
`field_*`/`add_alias` match), and **is honored by the chat adapter** — server-common.cpp L1363-1377
reads it and turns it into a chat-session JSON grammar. The grammar bypasses `task_params` entirely:
`oaicompat_chat_params_parse` erases `grammar`/`json_schema` from `llama_params` when the session owns
a grammar (L1534-1538), and it is applied later via `server_task::apply_chat_session`, so `/slots`
`params` never shows it (`grammar` key stayed `null`).

Ground-truth probe (pinned server, port 47980, temperature 0, max_tokens 24, prompt "The dog said"):
base request → content `"Here,\" replakes.\nSuddenly, `; request + response_format → HTTP 200, content
` \n \n                    ` — generation provably changed, while the `/slots` params diff was empty
(p1_vs_p2_diff = []).

Counter output (`--tip f1`, exit 0):
`registered 1 counted 1 target 12 met False not-counted []`
receipt row F1R: `counted: true, reasons: []`, live status 200, normalized response equal to base
(top_keys/n_choices/choice_keys/has_logprobs/usage_keys/prompt_tokens identical; prompt_tokens 45).

**Verdict: `counter-defect`.** The counter certifies a false `ignored` outcome for a parameter the
adapter actively honors, because its ignored test observes only (a) the fixed `/slots` params key set
and (b) a six-field response normalization that never compares generated content or `message`
sub-keys. Limitation to record (counter is frozen — no fix to apply): any parameter whose effect
lives entirely in the chat session and changes neither slot-serialized params nor the six normalized
fields is unseeable; `response_format` is the concrete instance on this build. A C1 `counted` value
that includes such a row overstates held knowledge; the docstring's "measured as zero slot delta plus
an unchanged normalized response" is the honest boundary, and `logit_bias` (named in known_limits) is
now *guarded* (declared in schema), while `response_format` is not.

## Fixture 2 — `slot` value matches only because the base request already had it

Row F2R: `param=user`, `sent="rev-counter-fair-audit"`, `outcome={"kind":"slot","set":{"temperature":0.8}}`;
`base_body` explicitly carries `"temperature": 0.8`. `user` is inert at 704366d: the chat adapter's
merge loop (server-common.cpp L1524-1531) copies unknown body keys into `llama_params` where the field
parser silently drops them. Probe: base → `/slots` temperature 0.800000011920929; base+`user` → HTTP
200, same value, zero param diff.

Counter output (`--tip f2`, exit 0):
`registered 1 counted 1 target 12 met False not-counted []`
receipt row F2R: `counted: true, reasons: []`, live status 200, slot_task 26.

**Verdict: `counter-defect`.** The slot check only requires each `set` key to be present in the newest
slot with the claimed value; it never compares against the base request's slot params, so a value the
base request already had certifies a "mapping" for any accepted-but-inert parameter. Discrimination
(e) requires only that a `set` key differ from `param` — which an identity row satisfies trivially
(`temperature` ≠ `user`). Limitation (frozen): slot rows prove presence, not causation; a seat could
pad `counted` with identity rows whose mapping value was set by `base_body` or by server defaults.
Fix the L1 would apply if the counter were not frozen: require every `outcome.set` key to differ
(float32 tolerance) from the base request's slot params (a base-delta requirement), mirroring what the
ignored branch already does in reverse.

## Fixture 3 — `reject` message copied from the schema bounds text

Row F3R: `param=top_p`, `sent=42`,
`message="Value must be between 0 <= value <= 1, but got 42"` — the runtime instantiation of the
bounds text constructed at server-schema.cpp L543 (`"Value must be between " + min + " <= value <= "
+ max + ", but got " + tmp`). That full string occurs nowhere in the `server-common.cpp` snapshot
(grepped; `"Value must be between"` has zero matches in common).

Counter output (`--tip f3`, exit 0):
`registered 1 counted 0 target 12 met False not-counted ['F3R']`
receipt row F3R: `counted: false, reasons: ["reject-message-not-adapter"]`, `live: {}` — refused
before any live call.

**Verdict: `counter-holds`.** The schema-layer bounds text is correctly refused as not-adapter; the
live byte-for-byte error-message comparison is an additional backstop against recycling real adapter
messages onto parameters that do not reject.

## Commands and exits

- `git clone -q --no-hardlinks <lane> /tmp/r31w1-RevCounterFair && git checkout -q 0e6f8ed6…` → ok;
  counter sha256 verified `d86c4a94…24216` (matches frozen claim).
- 3 × `/usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane /tmp/r31w1-RevCounterFair --repo
  /tmp/r31w1-RevCounterFair --tip <f1|f2|f3> --out <receipt>` → exit 0 each; summaries above.
- 1 × manual probe server on 47980 (exact pinned argv, LD_LIBRARY_PATH=~/.local/opt/llama-b11755),
  SIGTERM after probes, `port_free: True` verified.
- Receipts: `f1-receipt.json`, `f2-receipt.json`, `f3-receipt.json` (same directory as this file).

## What the L1 must not trust

- Do not trust `counted >= 12` as "12 true parameter outcomes": fixtures 1 and 2 show two independent
  row classes that count while proving nothing (false `ignored`; identity `slot`). Neither KQ38-style
  discrimination rule (e) closes them.
- Do not trust the frozen counter to catch generation-level effects invisible to `/slots` params and
  the six normalized fields; `response_format` (json_object/json_schema) is the demonstrated case.
- My fixture rows S901-S903 and F1R/F2R/F3R are scratch-only audit constructs; they are not sources,
  not data rows, and must never be merged or cited as lane knowledge.
- No tool was installed or updated for this item (none needed); no lane tracked file was touched; the
  frozen counters were never edited.
