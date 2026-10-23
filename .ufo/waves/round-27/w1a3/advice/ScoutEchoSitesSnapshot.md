VERDICT: holds — S137 (`server-common.cpp:1375`) is one of several request-echo sites in the pinned 704366d snapshot: 11 other lines also splice a client-chosen string into an error that the HTTP layer returns, and 14 more dump the offending request JSON into a message that is rethrown as that HTTP body.

No lsp device is in this seat's inventory. Sites below are from the snapshot text, not a semantic index. No tools installed. No server started. `json_value`'s template body is not in the vendored `.cpp` files (header); call sites show the result type.

## How a throw becomes the live error

`server.cpp:56-84` `ex_wrapper` catches `std::invalid_argument`, `common_json_error`, and `std::exception`, and puts `e.what()` into `format_error_response`. Chat routes call `oaicompat_chat_params_parse` with no local catch (`server-context.cpp:5564-5574`, also 5632, 5668, 5690, 5715, 6273) and are registered under `ex_wrapper` (`server.cpp:288-289`). Router routes are the same (`server.cpp:241-275`).

`server-common.cpp:1162` is not one of these. `param` is the loop variable of the static vector `{"best_of", "suffix"}` (`server-common.cpp:1159-1162`). The appended text is one of those two literals.

## Request-derived, surfaced, client-chosen string (26 lines)

"Free" means the branch does not require the string to already be a loaded model id. Dump lines are re-encoded by `json::dump` (quotes and non-ASCII escaped); the scalar lines concatenate the decoded `std::string`.

| path:line | frame | varying part | how it reaches HTTP |
|---|---|---|---|
| `server-common.cpp:1375` | `response_format type must be one of "text" or "json_object", but got: ` | `response_type` = `json_value(response_format, "type", std::string())` (`:1365-1366`); `response_format` from body | throw to `ex_wrapper`. This is S137 |
| `server-common.cpp:1216` | `file path is not allowed: ` | `file_path` = `url.substr(7)` after `file://` (`:1213`). `url` is `image_url.url`, `input_audio.data`/`url`, or `input_video`/`video_url` data/url (`:1256-1293`) | throw from `handle_media`, called by `oaicompat_content_load_media`, called by `oaicompat_chat_params_parse` |
| `server-common.cpp:1221` | `file does not exist or cannot be opened: ` | same `file_path` | same |
| `server-common.cpp:1234` | `Invalid uri format: ` | `parts[0]` of a `data:` URI split on `,` (`:1228-1234`), same media URL | same |
| `chat.cpp:324` | `Invalid tool_choice: ` | `tool_choice` argument. Caller passes `json_value(body, "tool_choice", std::string("auto"))` (`server-common.cpp:1339`, call `:1422`) | throw, not inside the messages try |
| `chat.cpp:874` | `Unknown reasoning format: ` | `format` argument. Caller passes `body.at("reasoning_format").get<std::string>()` (`server-common.cpp:1450`) | throw |
| `chat.cpp:347` | `Expected 'messages' to be an array, got ` | `messages.dump()` | caught at `:434-437` and rethrown |
| `chat.cpp:352` | `Expected 'message' to be an object, got ` | `message.dump()` | same |
| `chat.cpp:357` | `Missing 'role' in message: ` | `message.dump()` | same |
| `chat.cpp:370` | `Missing content part type: ` | `part.dump()` | same |
| `chat.cpp:374` | `Unsupported content part type: ` | `type.dump()` (`part.at("type")`) | same |
| `chat.cpp:382` | `Invalid 'content' type: expected string or array, got ` plus `content.dump()` plus the issue-8367 ref | `content.dump()` | same |
| `chat.cpp:391` | `Missing tool call type: ` | `tool_call.dump()` | same |
| `chat.cpp:395` | `Unsupported tool call type: ` | `tool_call.dump()` | same |
| `chat.cpp:398` | `Missing tool call function: ` | `tool_call.dump()` | same |
| `chat.cpp:402` | `Missing tool call name: ` | `tool_call.dump()` | same |
| `chat.cpp:437` | `Failed to parse messages: ` | `e.what()` of the row above (frame plus dump) | this is the HTTP what() for those rows. Called at `server-common.cpp:1420` |
| `chat.cpp:562` | `Expected 'tools' to be an array, got ` | `tools.dump()` | caught at `:584-585` |
| `chat.cpp:566` | `Missing tool type: ` | `tool.dump()` | same |
| `chat.cpp:570` | `Unsupported tool type: ` | `tool.dump()` | same |
| `chat.cpp:573` | `Missing tool function: ` | `tool.dump()` | same |
| `chat.cpp:585` | `Failed to parse tools: ` plus `e.what()` plus `; tools = ` | `e.what()` and `tools.dump(2)` | this is the HTTP what(). Called at `server-common.cpp:1421` |
| `server-models.cpp:2170` | `model '%s' not found` | `name` before alias rewrite. `proxy_get` uses `req.get_param("model")` (`:2268`); `proxy_post` uses `json_value(body, "model")` (`:2283`). Fires only when `get_meta` misses | `res_err` to `format_error_response` |
| `server-models.cpp:854` | `model name=` plus name plus ` is not found` | DELETE `model` query (`:2539`) when `has_model` is false and the name is not an unfinished download (`:2554-2555`) | throw to `ex_wrapper` |
| `server-models.cpp:657` | `unknown sidecar '` plus kind plus `', expected one of ` plus catalog | `kind` from body `sidecars` (`parse_sidecars` `:662-671`, POST `/models` `:2499`) or DELETE `sidecar` query (`:2545-2547`). Catalog side is `common_download_sidecars()` names, not the request | throw to `ex_wrapper` |
| `server-models.cpp:2516` | `model '` plus name plus `' resolves no file to download` | POST body `model` (`:2495`) after `common_download_get_hf_plan` returns a plan with empty paths (`:2514-2516`). A throw from the plan fetch is rethrown at `:2508-2511` instead, and that what() is not in this snapshot | throw to `ex_wrapper` |

Distinct HTTP frames in this table, counting a rethrow as one body: **12** (`1375`, `1216`, `1221`, `1234`, `324`, `874`, `437`, `585`, `2170`, `854`, `657`, `2516`). S137 is one of the 12. The 14 dump lines are still request-derived sites; their text is inside `437` or `585`.

## Request-derived, but the string must already be a known model id (15)

The varying part is the request's model name. `router_validate_model` (`server-models.cpp:2173-2174`) rewrites it to `meta->name` before `ensure_model_ready` / `proxy_request`, so an alias is replaced by the registry id. These do not plant an arbitrary signature the way `:1375` does.

| path:line | frame | caller observed |
|---|---|---|
| `server-models.cpp:850` | `model '` plus name plus `' is downloading` | `unfinished_downloads_remove` from DELETE `:2555` (only if `mapping` still has the name) |
| `server-models.cpp:864` | `model '` plus name plus `' is in use, unload it first` | `remove_sidecar` from DELETE `:2548` |
| `server-models.cpp:1330` | `model name=` plus name plus ` is not found` | `load` from POST `/models/load` `:2324` (`meta->name` after lookup). The inner `load` inside `ensure_model_ready` is caught and only logged (`:1824-1827`) |
| `server-models.cpp:1349` | `model '` plus name plus `' is already downloading` | `load` download mode from POST `/models` `:2529` |
| `server-models.cpp:1352` | `model '` plus name plus `' is running, unload it first` | same |
| `server-models.cpp:1355` | `model '` plus name plus `' already exists` | same, when source is not cache |
| `server-models.cpp:1371` | `model '` plus name plus `' shares files with the download of '` plus `d.model` | same. `d.model` is another in-progress download's name (registry), `name` is the request |
| `server-models.cpp:1672` | `model name=` plus name plus ` is not found` | `remove` from DELETE `:2560` |
| `server-models.cpp:1675` | `model name=` plus name plus ` is not removable (not from cache)` | same |
| `server-models.cpp:1731` | `model name=` plus name plus ` is not found` | `ensure_model_ready` from `proxy_get` `:2275` / `proxy_post` `:2297`, after validate |
| `server-models.cpp:1783` | `request cancelled while waiting for model name=` plus name | same function, `should_stop` |
| `server-models.cpp:1802` | `model name=` plus name plus ` failed to load` | same |
| `server-models.cpp:1813` | `request cancelled while waiting for model name=` plus name | same |
| `server-models.cpp:1850` | `model name=` plus name plus ` is not found` | `proxy_request` from both proxy routes |
| `server-models.cpp:1853` | `model name=` plus name plus ` is not running` | same |

## Schema text (3 lines) — fill of the field is not in this snapshot

| path:line | frame | varying part |
|---|---|---|
| `json-schema-to-grammar.cpp:401` | `Invalid pattern ` plus pattern plus `: ` plus `err.what()` | pushed to `_errors` from `_visit_pattern(str.pattern)` (`:935-936`) |
| `json-schema-to-grammar.cpp:689` | `Unresolved $ref ` plus `schema.ref` | pushed to `_errors` |
| `json-schema-to-grammar.cpp:977` | `JSON schema conversion failed:\n` plus joined `_errors` | the throw `check_errors` uses. `json_schema_to_grammar` is called with the request schema at `chat.cpp:1502` (`inputs.json_schema`, set from the body at `server-common.cpp:1357-1373` and `:1423`) and from CLI at `arg.cpp:2289` and `:2306` |

`common_chat_schema_from_json`, which would show the copy from JSON keys into `pattern` / `ref`, is not in the snapshot. [INFERENCE] those fields are the schema's `pattern` and `$ref`. Not counted in the 26.

`json-schema-to-grammar.cpp:804` (`Rule ` plus `dep` plus ` not known`) is a builtin rule name (`PRIMITIVE_RULES` / `STRING_FORMAT_RULES`), not the request. Class: fixed.

`json-schema-to-grammar.cpp:1004` wraps `e.what()` from `common_chat_schema_from_json`. That function is not in the snapshot, so the varying part is unresolved. Not counted.

## Built, then not returned (not live signatures)

`llama_grammar_parser::parse` (`llama-grammar.cpp:694-722`) catches every parse throw and fprintf's `err.what()` plus the whole grammar. It returns false. `llama_grammar_init_impl` (`:1228-1230`) logs `failed to parse grammar` and returns null. `common_sampler_init` then throws the fixed string `failed to parse grammar` (`sampling.cpp:278-279`), which `server-context.cpp:1928-1929` forwards as `Failed to initialize samplers: ` plus that fixed string.

The swallowed throws do concatenate a `const char *` into the grammar buffer (`:120`, `:146`, `:157`, `:178`, `:189`, `:199`, `:204`, `:208`, `:215`, `:223`, `:231`, `:470`, `:608`, `:629`, `:650`, `:654`, `:678`, `:689`, `:712`). When the sampler is given the request `grammar` string, that tail is request text, but only on stderr. `:1472` and `:1527` concatenate `piece`, which is the accepted token piece, not the HTTP request.

`sampling.cpp:1074` concatenates `word` from a grammar trigger. Nothing in this snapshot assigns `grammar_triggers` except moving `applied.grammar_triggers` (`chat.cpp:1725-1750`). Origin of `word` is unresolved. Not counted. `server-common.cpp:1535-1536` erases a client `grammar_triggers` field before the task, so that JSON key is not copied through.

## Other classes (not request echoes)

Detector: 198 interpolating `throw` / `send_error` / `format_error_response` / `res_err` / `res->error` statements under `.ufo/waves/round-27/sources/llama.cpp-704366d/` (extract at `/fast/scratch/hyaku/kama-r27c/ScoutEchoSitesSnapshot/hits.txt`). Two are a plus sign inside a string literal only: `server-common.cpp:1517`, `server-context.cpp:4275`.

- **file/model-derived:** `llama-model-loader.cpp` (paths, GGUF keys, tensor names), `llama-vocab.cpp` (tokenizer model / pre-tokenizer / GGUF key names; `:2401`, `:2686`), `llama-context.cpp` Hadamard tensor names and `model.arch_name()` (`:245`), `llama.cpp:350` and `:358` (wrappers of those load errors), `common.cpp:938` and `:1032` (filesystem paths), `server-models.cpp:590`, `:596`, `:626`, `:631` (preset/alias names at `add_model`, startup, not an HTTP body). `chat.cpp:1409` `tmpl.analysis_error` and `:1439` are template-analysis text; the template object is the server's, not the request body.
- **cli/env:** `arg.cpp` throws that format `arg`, `value`, `fname`, `device`, or `opt.env` (28 statements in the extract). Process start, not a per-request HTTP body. `server-context.cpp:2466` is `tokenize_cli_input` (`:2454-2466`), CLI prompt, not the HTTP body.
- **fixed:** integers and sizes (`server-context.cpp:3656`, `:3668`, `:3678`, `:3690`, `:4403`; `server-http.cpp:872` `MAX_INSTANCES`; `fit.cpp:496`; `gguf.cpp:1615`, `:1623`), static sentences (`server-context.cpp:5476` joins "prefix/suffix/middle token is missing"), `server-common.cpp:1162` as above, `chat.cpp:1669` (`common_chat_format_name` of an enum). `server-context.cpp:3102`, `:3199`, `:3211` are `e.what()` wrappers; the throws inside the slot-restore try (`:3091`, `:3095`) are fixed strings.

## Count

- Request-derived lines whose text is, or is embedded in, a returned HTTP error, client-chosen string: **26** (12 HTTP frames). S137 is one of them.
- Additional request-derived lines that only echo a model id the server already knows (or the canonical id after alias rewrite): **15**.
- Schema-text lines with the JSON-field copy outside the snapshot: **3**. Not in the 26.
- S137 is not the only site of this shape.
