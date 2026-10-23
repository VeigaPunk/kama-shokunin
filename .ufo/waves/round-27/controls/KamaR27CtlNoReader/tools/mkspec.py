#!/usr/bin/env python3
"""Build the two control row specs for the round-27 no-reader seat.

spec_real.json     : 15 rows citing REAL 704366d literals of server-common.cpp
                     with fabricated trigger links (no observation was made).
spec_invented.json : 15 rows citing INVENTED literals that exist only in a
                     fabricated snapshot file (lines 2150..2164).
"""
import json
from pathlib import Path

REAL = [
    (1129, '"prompt" must not be empty', "/completion", "prompt",
     "the completion handler rejects an empty prompt array before tokenising"),
    (1210, "file:// URLs are not allowed unless --media-path is specified",
     "/v1/chat/completions", "image_url",
     "the chat handler refuses a file url media part unless media paths are allowed"),
    (1230, "Invalid uri-encoded base64 value", "/v1/chat/completions",
     "image data",
     "the media parser rejects a data url whose payload is not valid base64"),
    (1236, "uri must be base64 encoded", "/v1/chat/completions", "audio url",
     "the media parser rejects an audio part that is not base64 encoded"),
    (1302, "unsupported content[].type", "/v1/chat/completions", "content type",
     "the chat handler only knows a fixed set of content part types"),
    (1309, '"content" must be an array', "/v1/chat/completions", "content",
     "a chat message content field must be a string or an array of parts"),
    (1375, 'response_format type must be one of "text" or "json_object", but got:',
     "/v1/chat/completions", "response_format",
     "the chat handler accepts only the text and json_object response formats"),
    (1386, "'messages' is required", "/v1/chat/completions", "messages",
     "the chat handler refuses a body that has no messages member at all"),
    (1390, "Expected 'messages' to be an array", "/v1/chat/completions",
     "messages array",
     "the chat handler refuses a messages member that is not an array"),
    (1395, "All non-assistant messages must contain 'content'", "/v1/chat/completions",
     "message content",
     "every non assistant chat message must carry a content member"),
    (1399, "Assistant message must contain either 'content' or 'tool_calls'!",
     "/v1/chat/completions", "assistant message",
     "an assistant message must carry content or a tool call list"),
    (1411, "Expected 'content' to be a string or an array", "/v1/chat/completions",
     "content shape",
     "the chat handler refuses a content member of an unsupported shape"),
    (1434, "Cannot have 2 or more assistant messages at the end of the list.",
     "/v1/chat/completions", "trailing assistant messages",
     "the chat handler refuses more than one trailing assistant message"),
    (1440, "Cannot set both add_generation_prompt and continue_final_message to true.",
     "/v1/chat/completions", "generation prompt flags",
     "the chat handler refuses both prompt continuation flags at once"),
    (1473, 'invalid type for "enable_thinking" (expected boolean, got string)',
     "/v1/chat/completions", "enable thinking",
     "the chat handler wants enable thinking to be a json boolean"),
]

INVENTED = [
    "the 'top_p' field must be a number between zero and one",
    "the request body is missing the required 'stop' field",
    "chat completions require a non-empty 'messages' array value",
    "the 'seed' parameter must be a signed 32-bit integer value",
    "the 'n_probs' parameter must be a positive integer count",
    "streaming responses require the 'stream_options' object field",
    "the 'logit_bias' map must contain integer token id keys",
    "the 'grammar' field must be a non-empty string expression",
    "the 'cache_prompt' field must be a boolean true or false",
    "the 'frequency_penalty' field must be a number in range",
    "the 'presence_penalty' field must be a number in range",
    "the 'mirostat_tau' field must be a number greater than zero",
    "the 'ignore_eos' field must be a boolean true or false",
    "the 'max_probs' value must not exceed the server limit",
    "the 'samplers' field must be a list of sampler names",
]


def rows_from(items, first_line, file_name):
    rows = []
    for i, it in enumerate(items):
        line, sig, path, field, meaning = it
        n = i + 1
        rows.append({
            "id": "E27-{:02d}".format(n),
            "sig": sig,
            "file": file_name,
            "line": line,
            "path": path,
            "marker": "r{:02d}".format(n),
            "srow": "S{:03d}".format(900 + n),
            "trigger": "POST {} with a malformed {} field returns this error".format(path, field),
            "meaning": meaning,
            "next": "Check the {} field in the request body against the documented key and "
                    "resend the request with the value the handler expects".format(field),
        })
    return rows


def first_line_of(_):
    return None


real_rows = rows_from(REAL, None, "server-common.cpp")
inv_rows = []
for i, sig in enumerate(INVENTED):
    field = sig.split("'")[1] if "'" in sig else "field"
    inv_rows.append({
        "id": "E27-{:02d}".format(i + 1),
        "sig": sig,
        "file": "server-common.cpp",
        "line": 2151 + i,
        "path": "/v1/chat/completions",
        "marker": "r{:02d}".format(i + 1),
        "srow": "S{:03d}".format(900 + i + 1),
        "trigger": "POST /v1/chat/completions with a malformed {} field returns this error".format(field),
        "meaning": "the handler rejects the request when the named field does not match the "
                   "expected shape and the error names the offending field",
        "next": "Check the {} field in the request body against the documented key and "
                "resend the request with the value the handler expects".format(field),
    })

Path("/tmp/kama-r27-noreader/spec_real.json").write_text(
    json.dumps({"rows": real_rows}, indent=1) + "\n", encoding="utf-8")
Path("/tmp/kama-r27-noreader/spec_invented.json").write_text(
    json.dumps({"rows": inv_rows}, indent=1) + "\n", encoding="utf-8")
print("real rows:", len(real_rows), "invented rows:", len(inv_rows))
for r in real_rows[:3] + inv_rows[:2]:
    print(r["id"], r["line"], r["sig"][:60])
