# Request-path error literal inventory

Scope: fresh upstream files at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`, restricted to the four requested files and the requested `throw std::runtime_error` / `throw std::invalid_argument` / `format_error_response` / `send_error` surfaces. A source literal assembled with a variable is called out as dynamic. The guards below are source-code predicates, not live observations.

## Single-model request paths reachable by a text-only fixture

| File:line | Error literal or emitted text | Guard and path |
|---|---|---|
| `server-common.cpp:1100` | `Multimodal data provided, but model does not support multimodal requests.` | `prompt` object has `prompt_string` and `multimodal_data`; `mctx == nullptr`. A text-only fixture meets the source guard before media decoding. |
| `server-common.cpp:1114` | `"prompt" elements must be a string, a list of tokens, a JSON object containing a prompt string, or a list of mixed strings & tokens.` | Prompt is not a string, supported token/string array, or object containing `prompt_string`; `tokenize_input_subprompt` throws. |
| `server-common.cpp:1129` | `"prompt" must not be empty` | `tokenize_input_prompts` produced an empty result, e.g. an empty prompt array. |
| `server-common.cpp:1143` | `"prompt" is required` | OAI completions body omits `prompt`; function comment at 1138 says it serves the `/completions` endpoint. |
| `server-common.cpp:1155` | `Only no echo is supported` | OAI completions body has truthy `echo`. |
| `server-common.cpp:1259` | `image input is not supported - hint: if this is unexpected, you may need to provide the mmproj` | OAI chat message content contains `type: image_url` while `opt.allow_image` is false; the rejection precedes URL decoding. |
| `server-common.cpp:1272` | `audio input is not supported - hint: if this is unexpected, you may need to provide the mmproj` | OAI chat content contains `type: input_audio` while `opt.allow_audio` is false. |
| `server-common.cpp:1287` | `video input is not supported - hint: if this is unexpected, you may need to provide the mmproj` | OAI chat content contains `type: input_video` or `video_url` while `opt.allow_video` is false. |
| `server-common.cpp:1302` | `unsupported content[].type` | A chat content-array part has a type other than `text`, image, audio, or video. |
| `server-common.cpp:1343` | `tools param requires --jinja flag` | Chat body has a non-empty `tools` array while `opt.use_jinja` is false. |
| `server-common.cpp:1346` | `tool_choice param requires --jinja flag` | Chat body sets `tool_choice` other than `auto` while `opt.use_jinja` is false. |
| `server-common.cpp:1360` | `Cannot use both json_schema and grammar` | Chat body provides both a non-null `json_schema` and non-empty `grammar`. |
| `server-common.cpp:1375` | Literal prefix `response_format type must be one of "text" or "json_object", but got: ` plus the request value | Chat body has a non-empty response-format type other than `text`, `json_object`, or `json_schema`. The complete emitted message is dynamic. |
| `server-common.cpp:1386` | `'messages' is required` | Chat body omits `messages`. |
| `server-common.cpp:1390` | `Expected 'messages' to be an array` | Chat body has `messages` with a non-array value. |
| `server-common.cpp:1395` | `All non-assistant messages must contain 'content'` | A message has a role other than `assistant` and omits `content`. |
| `server-common.cpp:1399` | `Assistant message must contain either 'content' or 'tool_calls'!` | An assistant message omits both `content` and `tool_calls`. |
| `server-common.cpp:1411` | `Expected 'content' to be a string or an array` | A message's `content` is neither a string/null nor an array. |
| `server-common.cpp:1434` | `Cannot have 2 or more assistant messages at the end of the list.` | `prefill_assistant` is enabled, continuation is otherwise unset, and the final two messages are assistant messages. |
| `server-common.cpp:1440` | `Cannot set both add_generation_prompt and continue_final_message to true.` | Parsed continuation is non-none while `add_generation_prompt` is true. |
| `server-common.cpp:1446` | `Cannot continue an assistant message that contains tool calls.` | Continuation is enabled and the final assistant message has tool calls. |
| `server-common.cpp:1455` | `Cannot use custom grammar constraints with tools.` | Tools are active, tool choice is not none, and the body contains `grammar`. |
| `server-common.cpp:1473` | `invalid type for "enable_thinking" (expected boolean, got string)` | `chat_template_kwargs.enable_thinking` is a non-empty JSON string other than the accepted `true`/`false` values. |
| `server-common.cpp:1517` | `logprobs is not supported with tools + stream` | Chat body sets `logprobs`, has tools, and enables streaming. |
| `server-common.cpp:1521` | `top_logprobs requires logprobs to be set to true` | `top_logprobs` is non-null while `logprobs` is false/absent. |
| `server-http.cpp:295` | `authentication_error` (the adjacent message `Invalid API Key` is only 15 bytes) | `api_keys` is non-empty; request is not a public endpoint and no matching value is found in `Authorization` or `X-Api-Key`; response status is 401. |

The `server-common.cpp:1162` expression is `"Unsupported param: " + param`; the fixed source literal is 19 bytes, so it is below the counter's 20-byte floor even though the emitted message includes a parameter name.

## Conditional media and saved-state paths

| File:line | Error literal or emitted text | Guard and reachability limit |
|---|---|---|
| `server-common.cpp:1045` | `Failed to load image or audio file` | `mtmd_helper_bitmap_init_from_buf` returns no bitmap; requires multimodal processing. |
| `server-common.cpp:1069` | `Failed to tokenize prompt` | `mtmd_tokenize` returns nonzero; requires the multimodal prompt path. |
| `server-common.cpp:1205` | `Failed to download image` | Remote media fetch is non-2xx after a media-capable request enters `handle_media`. |
| `server-common.cpp:1210` | `file:// URLs are not allowed unless --media-path is specified` | Media handler sees `file://` with empty `media_path`; on a text-only chat image path, the `allow_image` guard at 1259 fires first. |
| `server-common.cpp:1216` | Literal prefix `file path is not allowed: ` plus a path | Media handler rejects a local path. |
| `server-common.cpp:1221` | Literal prefix `file does not exist or cannot be opened: ` plus a path | Media handler cannot open the local path. |
| `server-common.cpp:1230` | `Invalid uri-encoded base64 value` | Media data URI does not split into two comma-separated parts. |
| `server-common.cpp:1234` | Literal prefix `Invalid uri format: ` plus the URI header | Media data URI scheme is not image/video/audio. |
| `server-common.cpp:1236` | `uri must be base64 encoded` | Media data URI header does not end in `base64`. |
| `server-common.cpp:1247` | `Invalid base64 value` | Raw media/base64 input decodes to empty; requires media decoding. |
| `server-common.cpp:393, 421, 425, 447, 461, 590, 603, 706, 714, 723, 728, 734` | Token-state messages, including `Unexpected end of server tokens state`, `Unsupported server tokens state version`, and `Trailing data in server tokens state` | Serialization/deserialization invariants. Deserialization errors require a corrupt server-side slot-state file; the request does not carry the packed token bytes. Not proposed as simple text-fixture triggers. |
| `server-common.cpp:1309` | `"content" must be an array` | Helper-level guard in `tokenize_oai_content_array`; the OAI chat parser at 1410–1411 rejects its non-array content before this helper in the inspected path. No direct trigger is proposed. |

## HTTP compatibility errors

| File:line | Error literal or emitted text | Guard and reachability limit |
|---|---|---|
| `server-http.cpp:799` | `empty response from internal handler` | GCP predict response parser gets a null handler response. Conditional on GCP route and internal handler outcome. |
| `server-http.cpp:802` | `predict route does not support streaming responses` | GCP predict response parser gets a streaming response. Conditional on GCP route and handler outcome. |
| `server-http.cpp:851` | JSON parser `e.what()` | Invalid JSON in a GCP predict request; dynamic library text, not a fixed source literal. |
| `server-http.cpp:857` | `request body must be a JSON object` | GCP predict route receives valid JSON that is not an object. |
| `server-http.cpp:863` | `request body must include an array field named instances` | GCP predict object omits `instances` or gives it a non-array value. |
| `server-http.cpp:872` | Literal prefix `instances array exceeds maximum size of ` plus the configured limit | GCP predict object has more than 128 instances. |
| `server-http.cpp:882` | `each instance must be a JSON object` | GCP `instances` contains a non-object. |
| `server-http.cpp:885` | `each instance must include a string @requestFormat` | A GCP instance omits `@requestFormat` or gives it a non-string. |
| `server-http.cpp:906` | Literal prefix `no handler registered for @requestFormat: ` plus the requested format | GCP format does not map to an installed handler. |

These GCP errors are behind `gcp.enabled` at `server-http.cpp:814–820`; the frozen registry schema has no environment-setting field, so they are not proposed as fixture rows. `Loading model` at line 318 and `Invalid API Key` at line 294 are shorter than 20 bytes; `unavailable_error` is not an error-message literal in this scope.

## Router-only model-name errors

`server-models.cpp` contains these request-facing error literals when its router routes exist:

| File:line | Error literal or emitted text | Guard |
|---|---|---|
| `server-models.cpp:2165` | `model name is missing from the request` | Router proxy request has an empty model name. |
| `server-models.cpp:2170` | Format string `model '%s' not found` | Router proxy request names no model; emitted text substitutes the requested name. |
| `server-models.cpp:2176` | `model is not loaded` (19 bytes, below floor) | Router autoload is disabled and the model is not running. |
| `server-models.cpp:2302` | `request cancelled by a stop while the model was loading` | Router POST's conversation ticket is no longer alive after a stop. |
| `server-models.cpp:2317, 2461` | `model is not found` (18 bytes, below floor) | Router load/unload API names no model. |
| `server-models.cpp:2321` | `model is already running` | Router load API names a running model. |
| `server-models.cpp:2465` | `model is not running` | Router unload API names an unloaded model. |
| `server-models.cpp:2497, 2541` | `model must be a non-empty string` | Router model download/delete has an empty name. |
| `server-models.cpp:2516` | Dynamic `model '<name>' resolves no file to download` | Router model download plan resolves no model file. |
| `server-models.cpp:2572, 2679` | `Missing conversation id in path` | Router stream GET/DELETE omits `conv_id`. |
| `server-models.cpp:2585` | `Stream owner model is loading, retry later` | Router stream owner is transiently loading/downloading. |
| `server-models.cpp:2587` | `Stream not found or expired` | Router stream ID has no current owner. |
| `server-models.cpp:1396` | `model limit reached, try again later` | A normal router model load hits configured `models_max`. |
| `server-models.cpp:1409` | `failed to get a port number` | Router model child cannot acquire a port. |
| `server-models.cpp:1454` | `failed to spawn server instance` | Router cannot create its child process. |
| `server-models.cpp:1783, 1813` | Literal prefix `request cancelled while waiting for model name=` plus a name | A waiting router request is cancelled. |
| `server-models.cpp:1802` | Dynamic `model name=<name> failed to load` | Router child model load failed. |
| `server-models.cpp:2900` | `failed to parse multipart form fields JSON` | Router proxy cannot parse multipart form fields. |

Other `server-models.cpp` request errors interpolate a model/sidecar value; the fixed source fragments alone are shorter than 20 bytes or are not reproduced verbatim as a complete message. Startup-only alias/model collision errors at 590–631 and startup model-cap errors at 1073–1075 are not request-triggerable.

The model-name rows above are not candidate triggers for the frozen C1 runner. `count-c1.py:225–226` always supplies `-m <model>`; the fresh pinned `server.cpp:151–154` defines router mode only when all model locators are empty, and its `/models` routes are inside `if (is_router_server)` at 231–276. Thus the ordinary fixture invocation is single-model mode, not this router API.

## `server-task.cpp`

There is no request-error literal in the requested throw/response forms in this file. `server-task.cpp:1504–1510` formats a caller-provided `err_msg` via `format_error_response`; the message text is supplied elsewhere. No `send_error` occurrence was found in any of the four requested files.
