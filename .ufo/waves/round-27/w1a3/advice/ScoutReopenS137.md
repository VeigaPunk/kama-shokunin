VERDICT: holds — S137's anchor (server-common.cpp:1363-1377, throw at 1375, raw sha256 b4f4aae7…d442) and its teaches (one fixed frame plus the JSON-decoded response_format.type string) match commit 704366d76.

No packages installed.

## Hash

Command (exit 0):

```
ulimit -f 1048576
timeout 120 curl -fsSL -o /fast/scratch/hyaku/kama-r27c/ScoutReopenS137/server-common.cpp \
  https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp
sha256sum <that file> <lane snapshot>
wc -l <that file>
```

- raw fetch sha256 `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442`, 2147 lines. Equals the expected hash and `corpus/SOURCES.md` S137 anchor cell.
- same digest on `.ufo/waves/round-27/sources/llama.cpp-704366d/server-common.cpp`, so the committed snapshot bytes are the raw file.

## Anchor (lines 1363-1377)

Function: `oaicompat_chat_params_parse` at `server-common.cpp:1327` (comment line 1326: "used by /chat/completions endpoint"). Body parameter is `json & body` ("openai api json semantics", line 1329).

```
1363    // Handle "response_format" field
1364    if (body.contains("response_format")) {
1365        json response_format      = json_value(body, "response_format", json::object());
1366        std::string response_type = json_value(response_format, "type", std::string());
1367        if (response_type == "json_object") {
1368            if (response_format.contains("schema") || json_schema.empty()) {
1369                json_schema = json_value(response_format, "schema", json::object());
1370            }
1371        } else if (response_type == "json_schema") {
1372            auto schema_wrapper = json_value(response_format, "json_schema", json::object());
1373            json_schema = json_value(schema_wrapper, "schema", json::object());
1374        } else if (!response_type.empty() && response_type != "text") {
1375            throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);
1376        }
1377    }
```

Lesson quote (`corpus/lessons/round-27.md` S137 row) matches line 1375 aside from indent. Spot-check pointer in the teaches cell (`lessons/round-26-verifier-spotcheck.md:106-110`) names this same sentence and `server-common.cpp:1375`.

The throw runs only when the decoded `type` string is non-empty and is not `text`, `json_object`, or `json_schema`. The thrown sentence still names only `"text"` or `"json_object"`; `json_schema` is accepted one branch above and does not throw. The variable part is `response_type` with no extra quotes: one fixed literal frame plus that string.

## json_value

Grep of the lane snapshot `.ufo/waves/round-27/sources/llama.cpp-704366d/` (cpp files only; no `server-common.h`) finds call sites, not a definition. `server-common.cpp:10` includes `"server-common.h"`. Fetched that header at the same commit (sha256 `ee401cf81ed0fb515f9870b018c762074903e72712dcb81a652e49761fe1577b`).

Definition: `tools/server/server-common.h:43-56`.

```
template <typename T>
static T json_value(const json & body, const std::string & key, const T & default_value) {
    if (body.contains(key) && !body.at(key).is_null()) {
        try {
            return body.at(key).get<T>();
        } catch (const common_json_error & err) {
            LOG_WRN(...);
            return default_value;
        }
    } else {
        return default_value;
    }
}
```

`using json = common_json` is `server-common.h:25`. So line 1366 reads `response_format.type` from the parsed object via `.get<std::string>()`, or the empty default if the key is missing, null, or not a string. A non-string `type` does not reach line 1375 and is not echoed here.

Decode path, same commit:

- `common/json.h:18-19`: `common_json` wraps nlohmann. `common/json.h:223`: `template <typename T> T get() const`.
- `common/json.cpp:201-205`: `common_json::parse` assigns `ordered_json::parse(text)`. sha256 of fetched `json.cpp`: `d8c556445cef8e7c93b0857f6ca7ae7ebd8295f169403ac66641b72f6b0598f2`.
- `common/json.cpp:416`: `COMMON_JSON_GET(std::string)` returns `as_json(this).get<std::string>()`.
- vendored `vendor/nlohmann/json.hpp` sha256 `08f19bbcc66ff3082f5caf58867b1232987dba98d82e2b29d870722fce42776b`. `scan_string` case `'u'` at lines 7351-7440 turns `\uXXXX` (and a surrogate pair) into UTF-8 bytes via `add(...)`, not into the six-character escape spelling.

The teaches cell is therefore right for a JSON string `type`: a `\u`-escaped request spelling is decoded before concatenation, and the error contains the decoded text inside one fixed frame. It does not claim this for a non-string `type`, and the code does not do that.

## HTTP status for std::invalid_argument

S137 scope already excludes the status mapping. Observed mapping, not a row claim:

Chat and the other in-process callers of `oaicompat_chat_params_parse` do not catch `std::invalid_argument` locally. `post_chat_completions` (`server-context.cpp:5564-5581`) parses then calls the function at 5569. Same uncaught call at `server-context.cpp:5632` (`post_responses_oai`), `:5668` (`post_transcriptions_oai`), `:5690` (`post_anthropic_messages`), `:5715` (`post_apply_template`), `:6273` (`handle_count_tokens`). Those routes are registered through `ex_wrapper` (`server.cpp:288-289`, `:291-295`, `:307`, `:309-313`).

The mapper is `server.cpp:62-83`, not a catch in `server-http.cpp` or `server-context.cpp`:

- `server.cpp:62-65`: `catch (const std::invalid_argument & e)` sets `ERROR_TYPE_INVALID_REQUEST`; comment says invalid request (400). `e.what()` is the thrown string, so the frame is the HTTP error message.
- `server-common.cpp:91-97`: `format_error_response` sets `code = 400` and `type_str = "invalid_request_error"` for that enum.
- `server.cpp:80-83`: response starts at 500, then `res->status = json_value(error_data, "code", 500)`, which copies the 400.

`server-http.cpp` does not map this chat throw:

- `:182-195` fail-safe httplib handler: any exception that still escapes `ex_wrapper` becomes HTTP 500 `text/plain`. Comment says `ex_wrapper` should already have handled it.
- `:921-922` (GCP `/predict` only): `catch (const std::invalid_argument & e)` calls `build_error` (`:841-842`), which nests `format_error_response` so the prediction object's `error.code` is 400. The handler (`:936-938`) sets `data` only. Default `server_http_res::status` is 200 (`tools/server/server-http.h:21-23`, fetched sha256 `fafbdb8db708656d702f3cef1adb0d341a67d68d49636a5559b9769518b5e50a`).

`server-context.cpp:4968-4969` catches `std::exception` inside `handle_completions_impl` and passes `ERROR_TYPE_INVALID_REQUEST` to `error()`, which copies `code` onto `status` (`:4872-4873`). The line-1375 throw happens before `handle_completions_impl` is called, so that catch is not the chat-route mapper for S137.

Router mode rebinds several of these routes to `proxy_post` before the same `ex_wrapper` registration (`server.cpp:247-260`). `proxy_post` was not traced. [INFERENCE] the in-process handler path above is the one that returns HTTP 400 for this throw.

## Row check

| cell | result |
|---|---|
| anchor lines 1363-1377, throw 1375, commit 704366d76, sha256 b4f4aae7…d442 | holds |
| teaches: one fixed frame + `response_format.type` via `json_value` on the parsed body, so a `\u` spelling shows up decoded | holds, for a JSON string `type` only |
| scope exclusion of other builds, other echo sites, and the HTTP status | matches the file; status is 400 on the in-process chat path via `server.cpp`, which the row does not claim |

Confidence: high on hash, lines, `json_value` definition, and the in-process 400 mapping. Unresolved: `proxy_post` in router mode.
