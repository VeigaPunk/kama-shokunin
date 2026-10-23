source: llama.cpp server b11755, commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad; pinned snapshot `SNAPSHOT.json` (server-common.cpp, server-schema.cpp, server-task.cpp)
verified-at: 2026-10-23 — static reading of the frozen source snapshot; no live C1 run by this scribe
recheck: on server-build change, re-open the pinned sources and use the frozen round-31 C1 counter for the live `/v1/chat/completions` and `/slots` check; treat slot params as stored settings, not proof of sampler use

# Chat-completions parameter outcomes

At the adapter boundary, request fields have three useful dispositions: reject with an error; apply/map the value to an internal generation or response behavior; or accept it without a measured effect. C1 records the evidence channels more finely as `reject`, `slot`, `response`, and `ignored`: `slot` checks stored task parameters, `response` checks only its named response-contract fact, and `ignored` requires no observed slot-parameter or normalized-response delta. A response-contract effect is not an ignored parameter. The parser is `oaicompat_chat_params_parse` for `/chat/completions` (`server-common.cpp:1326-1333`); examples of parameter mapping and rejection are below.

## Mapping and the silent-ignore boundary

The adapter copies request properties not already handled into `llama_params`, except that `n_predict` can replace an earlier value; it then removes the session-owned `grammar_lazy`, `grammar_triggers`, and `preserved_tokens` fields (`server-common.cpp:1524-1543`). The schema pass evaluates its declared fields (`server-schema.cpp:494-499`), and each field checks its registered name list (`server-schema.cpp:531-550`). For example, schema-declared aliases map `max_completion_tokens` and `max_tokens` to `n_predict`, `n` to `n_cmpl`, and `logprobs` to `n_probs` (`server-schema.cpp:44-48,62-65,179-181`).

Consequently, an unrecognized key can be copied by the adapter and then go unused because no schema field consumes it. “Unknown keys are silently ignored” is bounded: C1 permits an ignored row only for a documented OpenAI parameter absent from the pinned schema, and its live check requires the newest `/slots` `params` to equal the base and the normalized response to be unchanged (`count-c1.py:24-39,46-48`; preregistration C1 limits). This does not establish that every unknown key is accepted, nor does it cover effects invisible to those checks.

## Rejections and error envelope

Adapter-authored parser messages differ from schema validation messages. For example, a non-null `top_logprobs` without truthy `logprobs` throws `top_logprobs requires logprobs to be set to true` in the chat adapter (`server-common.cpp:1513-1521`). Separately, hard numeric schema limits can produce `Value must be between ...` (`server-schema.cpp:518-547`); fields using soft limits are clamped instead of taking that hard-limit branch (`server-schema.cpp:89-95`). Do not cite a schema-bound message as an adapter-authored rejection.

The pinned error formatter emits `code`, `message`, and `type`; its `ERROR_TYPE_SERVER` branch is code 500 / `server_error` (`server-common.cpp:91-132`). C1 grades each rejection live by HTTP status and requires the `error` object to have exactly those three keys and exact values (`count-c1.py:24-29`). This is per observed row, not a rule that every parser exception is HTTP 500. For example, the available live `top_logprobs` row is HTTP 400 / `invalid_request_error`, not the 500 branch (`w1/out/DataA05/row.json:8-18,116`). The frozen source subset shows the formatter branch but not the complete exception-to-HTTP dispatch; a claim that a particular adapter exception uses `server_error` needs its own C1 live row.

## Observability and limits

`/slots` is the counter's observability boundary for whether the request's task settings were stored: it does not show that the sampler used them (`count-c1.py:30-31`; preregistration C1 known limit). For no-effect rows, the counter also compares the normalized response, whose defined fields and allowed response checks are finite (`count-c1.py:32-39,99`). A passing setting check is one request on the pinned build/model/default argv, not a parameter's full response function, general behavior of other builds, or a sampler-quality claim (preregistration C1 known limits).
