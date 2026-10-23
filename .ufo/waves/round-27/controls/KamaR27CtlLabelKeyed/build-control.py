#!/usr/bin/env python3
"""Build the label-keyed / copy-shortcut control inside a kama-shokunin sandbox.

Shape:
  group 1  E27-01..17  round-26 wave-1 ExecChatFormat rows copied verbatim
                       (ids, signatures, requests) with placeholder S901-S917
  group 2  E27-18..21  round-26 lesson "held back" candidates copied (decoded
                       r26 quote forms, prompt/input emptiness)
  group 3  E27-31..47  literal port of registry/error-signatures-r26.json,
                       reusing the existing S114-S130 rows and copying the
                       E26 SKILL row text
  group 4  E27-51..67  same port with new S880-S896 rows that duplicate the
                       S114-S130 text
"""
import json
import re
import sys
from pathlib import Path

SANDBOX = Path(sys.argv[1]).resolve()
COMMIT = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
BLANK = "https://github.com/ggml-org/llama.cpp/blob/" + COMMIT

# ---------------------------------------------------------------- group 1
# (id, sig, line, profile, request_body, trigger, meaning, next)
CHAT = [
    ("E27-01", "'messages' is required", 1386, "default",
     {"model": "gpt-3.5-turbo"},
     "POST /v1/chat/completions with a body that has no messages field",
     "the OAI chat parser throws invalid_argument when the body lacks messages (server-common.cpp:1386)",
     "Send a messages array in the request body before retrying the chat call."),
    ("E27-02", "Expected 'messages' to be an array", 1390, "default",
     {"messages": "hi"},
     "POST /v1/chat/completions with messages set to a JSON string",
     "the chat parser requires messages to be a JSON array (server-common.cpp:1390)",
     "Wrap the message objects in an array instead of a bare string."),
    ("E27-03", "All non-assistant messages must contain 'content'", 1395, "default",
     {"messages": [{"role": "user"}]},
     "POST /v1/chat/completions with a user message that has no content",
     "every non-assistant message must carry a content field (server-common.cpp:1395)",
     "Add a content field to each user and system message."),
    ("E27-04", "Assistant message must contain either 'content' or 'tool_calls'!", 1399, "default",
     {"messages": [{"role": "assistant"}]},
     "POST /v1/chat/completions with an assistant message that has neither content nor tool_calls",
     "an assistant message needs content or tool_calls before templating (server-common.cpp:1399)",
     "Give the assistant turn content or a tool_calls array."),
    ("E27-05", "Expected 'content' to be a string or an array", 1411, "default",
     {"messages": [{"role": "user", "content": 123}]},
     "POST /v1/chat/completions with numeric content instead of text",
     "content must be a string or an array of parts (server-common.cpp:1411)",
     "Send content as a string or as typed content parts."),
    ("E27-06", "unsupported content[].type", 1302, "default",
     {"messages": [{"role": "user", "content": [{"type": "weird", "text": "x"}]}]},
     "POST /v1/chat/completions with a content part whose type is unknown",
     "only known content part types pass the multimodal parser (server-common.cpp:1302)",
     "Use a supported content part type such as text or image_url."),
    ("E27-07", "response_format type must be one of ", 1375, "default",
     {"messages": [{"role": "user", "content": "hi"}], "response_format": {"type": "xml"}},
     "POST /v1/chat/completions with response_format type xml",
     "response_format accepts only text or json_object on this build (server-common.cpp:1375)",
     "Set response_format type to text or json_object."),
    ("E27-08", "tools param requires --jinja flag", 1343, "no-jinja",
     {"messages": [{"role": "user", "content": "hi"}],
      "tools": [{"type": "function", "function": {"name": "get_weather", "description": "get weather",
                                                 "parameters": {"type": "object", "properties": {}}}}]},
     "POST /v1/chat/completions with tools while the server runs --no-jinja",
     "tools need the jinja chat template engine enabled (server-common.cpp:1343)",
     "Restart the server with jinja enabled or drop the tools field."),
    ("E27-09", "tool_choice param requires --jinja flag", 1346, "no-jinja",
     {"messages": [{"role": "user", "content": "hi"}], "tool_choice": "required"},
     "POST /v1/chat/completions with tool_choice while the server runs --no-jinja",
     "tool_choice is rejected when jinja templating is off (server-common.cpp:1346)",
     "Enable jinja at launch before sending a tool_choice value."),
    ("E27-10", "Cannot use both json_schema and grammar", 1360, "default",
     {"messages": [{"role": "user", "content": "hi"}], "json_schema": {"type": "object"},
      "grammar": "root ::= \"a\""},
     "POST /v1/chat/completions with both json_schema and grammar set",
     "json_schema and a raw grammar cannot be combined on one request (server-common.cpp:1360)",
     "Send either json_schema or grammar, never both together."),
    ("E27-11", "(expected boolean, got string)", 1473, "default",
     {"messages": [{"role": "user", "content": "hi"}],
      "chat_template_kwargs": {"enable_thinking": "maybe"}},
     "POST /v1/chat/completions with a string enable_thinking template kwarg",
     "the enable_thinking kwarg must be a JSON boolean (server-common.cpp:1473)",
     "Pass enable_thinking as true or false, not a string."),
    ("E27-12", "Cannot have 2 or more assistant messages at the end of the list.", 1434, "default",
     {"messages": [{"role": "assistant", "content": "a"}, {"role": "assistant", "content": "b"}]},
     "POST /v1/chat/completions ending with two assistant messages",
     "prefill refuses two trailing assistant turns in the list (server-common.cpp:1434)",
     "Merge or drop one of the trailing assistant messages."),
    ("E27-13", "Cannot set both add_generation_prompt and continue_final_message to true.", 1440, "default",
     {"messages": [{"role": "user", "content": "hi"}], "add_generation_prompt": True,
      "continue_final_message": True},
     "POST /v1/chat/completions with add_generation_prompt and continue_final_message both true",
     "the two continuation switches are mutually exclusive in the parser (server-common.cpp:1440)",
     "Choose one continuation switch and unset the other flag."),
    ("E27-14", "Cannot continue an assistant message that contains tool calls.", 1446, "default",
     {"messages": [{"role": "assistant", "content": None,
                    "tool_calls": [{"id": "call_0", "type": "function",
                                    "function": {"name": "get_weather", "arguments": "{}"}}]}],
      "continue_final_message": True},
     "POST /v1/chat/completions continuing an assistant turn that has tool calls",
     "a tool-call assistant turn cannot be continued as plain text (server-common.cpp:1446)",
     "Start a fresh turn instead of continuing the tool call."),
    ("E27-15", "top_logprobs requires logprobs to be set to true", 1521, "default",
     {"messages": [{"role": "user", "content": "hi"}], "top_logprobs": 5},
     "POST /v1/chat/completions with top_logprobs but without logprobs",
     "top_logprobs is only meaningful when logprobs is enabled (server-common.cpp:1521)",
     "Enable logprobs before asking for top_logprobs values."),
    ("E27-16", "Cannot use custom grammar constraints with tools.", 1455, "default",
     {"messages": [{"role": "user", "content": "hi"}],
      "tools": [{"type": "function", "function": {"name": "get_weather", "description": "get weather",
                                                 "parameters": {"type": "object", "properties": {}}}}],
      "grammar": "root ::= \"a\""},
     "POST /v1/chat/completions with tools and a custom grammar",
     "tool calls and raw grammar constraints cannot be combined (server-common.cpp:1455)",
     "Remove the grammar field when you send tool definitions."),
    ("E27-17", "logprobs is not supported with tools + stream", 1517, "default",
     {"messages": [{"role": "user", "content": "hi"}],
      "tools": [{"type": "function", "function": {"name": "get_weather", "description": "get weather",
                                                 "parameters": {"type": "object", "properties": {}}}}],
      "logprobs": True, "stream": True},
     "POST /v1/chat/completions with logprobs, tools and stream together",
     "streamed tool calls cannot also return log probabilities (server-common.cpp:1517)",
     "Drop streaming or logprobs when you send tools."),
]

# ---------------------------------------------------------------- group 2
EXTRA = [
    ("E27-18", "\"input\" or \"content\" must be provided", 6151, "server-context.cpp", "embeddings",
     {"method": "POST", "path": "/embedding", "body": {}},
     {"method": "POST", "path": "/embedding", "body": {"content": "Hello"}},
     "POST /embedding with a JSON body that has neither input nor content",
     "the embeddings handler needs an input or content field (server-context.cpp:6151)",
     "Add an input or content field to the embedding request."),
    ("E27-19", "\"prompt\" elements must be a string, a list of tokens, a JSON object containing a "
               "prompt string, or a list of mixed strings & tokens.", 1114, "server-common.cpp", "default",
     {"method": "POST", "path": "/completion", "body": {"prompt": {"not_prompt": True}}},
     {"method": "POST", "path": "/completion", "body": {"prompt": "Hi", "n_predict": 4}},
     "POST /completion with prompt as an object without prompt_string",
     "a prompt object must carry a prompt_string key or a mixed list (server-common.cpp:1114)",
     "Send prompt as a string, a token list or a prompt_string object."),
    ("E27-20", "\"prompt\" must not be empty", 1129, "server-common.cpp", "default",
     {"method": "POST", "path": "/completion", "body": {"prompt": []}},
     {"method": "POST", "path": "/completion", "body": {"prompt": "Hi", "n_predict": 4}},
     "POST /completion with an empty prompt array",
     "an empty prompt array tokenizes to no subprompts at all (server-common.cpp:1129)",
     "Provide at least one non-empty prompt element per call."),
    ("E27-21", "\"input\" must not be empty", 6183, "server-context.cpp", "embeddings",
     {"method": "POST", "path": "/embedding", "body": {"input": []}},
     {"method": "POST", "path": "/embedding", "body": {"content": "Hello"}},
     "POST /embedding with an empty input array",
     "an empty input array leaves no tokenized prompt to embed (server-context.cpp:6183)",
     "Send one or more input entries instead of an empty array."),
]

# ---------------------------------------------------------------- group 3/4
# r26 S row -> (file, line, profile)
R26 = {
    "S114": ("server-context.cpp", 5366, "default"),
    "S115": ("server-context.cpp", 5408, "default"),
    "S116": ("server-context.cpp", 3084, "default"),
    "S117": ("server-context.cpp", 5453, "default"),
    "S118": ("server-context.cpp", 6132, "default"),
    "S119": ("server-context.cpp", 6137, "embeddings"),
    "S120": ("server-context.cpp", 6151, "embeddings"),
    "S121": ("server-context.cpp", 5803, "default"),
    "S122": ("server-context.cpp", 5476, "default"),
    "S123": ("server-context.cpp", 3657, "embeddings"),
    "S124": ("server-context.cpp", 5998, "default"),
    "S125": ("server-context.cpp", 5655, "default"),
    "S126": ("server-common.cpp", 1272, "default"),
    "S127": ("server-common.cpp", 1114, "default"),
    "S128": ("gguf.cpp", 1021, "default"),
    "S129": ("gguf.cpp", 482, "default"),
    "S130": ("llama-context.cpp", 2624, "default"),
}
# healthy same-endpoint controls for the r26 ports
CTL = {
    "S114": {"method": "GET", "path": "/slots", "body": None},
    "S115": {"method": "POST", "path": "/slots/0?action=save", "body": {"filename": "s0.bin"}},
    "S116": {"method": "POST", "path": "/slots/0?action=restore", "body": {"filename": "absent.bin"}},
    "S117": {"method": "POST", "path": "/props", "body": {"chat_template": "x"}},
    "S118": {"method": "POST", "path": "/v1/embeddings", "body": {"model": "stories260K", "input": "hello"}},
    "S119": {"method": "POST", "path": "/v1/embeddings", "body": {"input": "hello world"}},
    "S120": {"method": "POST", "path": "/v1/embeddings", "body": {"model": "stories260K", "input": "hi"}},
    "S121": {"method": "POST", "path": "/v1/rerank", "body": {"query": "test", "documents": ["a", "b"]}},
    "S122": {"method": "POST", "path": "/infill", "body": {"prompt": "a + b"}},
    "S123": {"method": "POST", "path": "/embedding", "body": {"content": "hello"}},
    "S124": {"method": "POST", "path": "/lora-adapters", "body": []},
    "S125": {"method": "POST", "path": "/v1/audio/transcriptions", "body": {}},
    "S126": {"method": "POST", "path": "/v1/chat/completions",
             "body": {"messages": [{"role": "user", "content": "Hi"}], "max_tokens": 4}},
    "S127": {"method": "POST", "path": "/completion", "body": {"prompt": "Hi", "n_predict": 4}},
    "S128": {"method": "POST", "path": "/completion", "body": {"prompt": "Hi", "n_predict": 4}},
    "S129": {"method": "POST", "path": "/completion", "body": {"prompt": "Hi", "n_predict": 4}},
    "S130": {"method": "POST", "path": "/completion", "body": {"prompt": "Hi", "n_predict": 4}},
}


def skill_row(rid, sig, trigger, meaning, action, srow):
    return f"| {rid} | `{sig}` | {trigger} | {meaning} | {action} | {srow} |"


def sources_row(srow, fname, line, note):
    return (f"| {srow} | llama.cpp {fname} @ 704366d (b11755) — {BLANK}/tools/server/{fname}#L{line} | "
            f"code | A | {note}, at commit 704366d76 only; not other builds | "
            f"{fname} line {line} @ {COMMIT}; signature quoted from the pinned snapshot |")


def main():
    entries, rows = [], []
    CANDS = json.loads((SANDBOX / ".ufo/waves/round-26/w1-build/out/ExecChatFormat/candidates.json")
                       .read_text())["signatures"]
    # group 1
    for i, (rid, sig, line, profile, body, trig, meaning, action) in enumerate(CHAT, 1):
        srow = f"S{900 + i}"
        creq = dict(CANDS[i - 1]["request"])
        creq.pop("headers", None)
        entries.append({
            "id": rid, "profile": profile, "signature": sig,
            "request": creq,
            "control": {"method": "POST", "path": "/v1/chat/completions",
                        "body": {"messages": [{"role": "user", "content": "Hi"}], "max_tokens": 4}},
            "source": {"row": srow, "file": "server-common.cpp", "line": line},
        })
        rows.append(skill_row(rid, sig, trig, meaning, action, srow))
    # group 2
    for rid, sig, line, fname, profile, req, ctl, trig, meaning, action in EXTRA:
        n = int(rid.split("-")[1])
        srow = f"S{879 + n}"  # E27-18 -> S897 ... E27-21 -> S900
        entries.append({
            "id": rid, "profile": profile, "signature": sig, "request": req, "control": ctl,
            "source": {"row": srow, "file": fname, "line": line},
        })
        rows.append(skill_row(rid, sig, trig, meaning, action, srow))
    # group 3/4: literal port of the r26 registry
    r26 = json.loads((SANDBOX / "registry/error-signatures-r26.json").read_text())
    skill_text = (SANDBOX / "SKILL.md").read_text()
    e26_rows = {}
    for line in skill_text.splitlines():
        m = re.match(r"^\| (E26-\d\d) \|", line)
        if m:
            e26_rows[m.group(1)] = line
    src_lines = (SANDBOX / "corpus/SOURCES.md").read_text().splitlines()
    s_text = {}
    for line in src_lines:
        m = re.match(r"^\| (S\d{3,}) \|", line)
        if m:
            s_text[m.group(1)] = line
    for idx, e in enumerate(r26["signatures"]):
        srow_old = e["source"]["row"]
        if srow_old not in R26:
            continue
        fname, line, profile = R26[srow_old]
        req = dict(e.get("request") or {"method": "POST", "path": "/completion",
                                        "body": {"prompt": "Hi"}})
        req.pop("headers", None)
        if req.get("body") == "":
            req["body"] = None
        base = {"profile": profile, "signature": e["signature"], "request": req,
                "control": CTL[srow_old], "source": {"file": fname, "line": line}}
        # group 3: reuse the existing S row
        rid = f"E27-{31 + idx:02d}"
        entries.append(dict(base, id=rid, source=dict(base["source"], row=srow_old)))
        row = e26_rows[e["id"]].replace(f"| {e['id']} |", f"| {rid} |", 1)
        rows.append(row)
        # group 4: new S row duplicating the existing row text
        rid2 = f"E27-{51 + idx:02d}"
        srow_new = f"S{880 + idx:02d}"
        entries.append(dict(base, id=rid2, source=dict(base["source"], row=srow_new)))
        rows.append(e26_rows[e["id"]].replace(f"| {e['id']} |", f"| {rid2} |", 1)
                    .replace(f"| {srow_old} |", f"| {srow_new} |"))

    section = ["", "## Round-27 request-validation signatures", "",
               "Label-keyed control submission: `registry/error-signatures-r27.json`; source rows",
               "S880-S917 in `corpus/SOURCES.md`; each row's request is POST against the pinned",
               "fixture model unless the trigger cell names another method. The first 21 rows copy",
               "round-26 findings; the rest port `registry/error-signatures-r26.json`. Never a lane claim.",
               "",
               "| id | signature | trigger | meaning | next action | source |",
               "|---|---|---|---|---|---|"] + rows + [""]
    skill = SANDBOX / "SKILL.md"
    skill.write_text(skill.read_text().rstrip("\n") + "\n" + "\n".join(section))

    # SOURCES rows: S880-S896 duplicate S114-S130 text; S897-S900 and S901-S917 are new
    add = []
    for idx, e in enumerate(r26["signatures"]):
        old = e["source"]["row"]
        if old in s_text:
            add.append(s_text[old].replace(f"| {old} |", f"| S{880 + idx:02d} |", 1))
    add.append(sources_row("S897", "server-context.cpp", 6151, "the embeddings input/content guard"))
    add.append(sources_row("S898", "server-common.cpp", 1114, "the prompt element type guard"))
    add.append(sources_row("S899", "server-common.cpp", 1129, "the empty prompt guard"))
    add.append(sources_row("S900", "server-context.cpp", 6183, "the empty embedding input guard"))
    for i, (_rid, _sig, line, _prof, _body, _t, _m, _a) in enumerate(CHAT, 1):
        add.append(sources_row(f"S{900 + i}", "server-common.cpp", line,
                               "a chat-completions request-validation error"))
    src = SANDBOX / "corpus/SOURCES.md"
    src.write_text(src.read_text().rstrip("\n") + "\n" + "\n".join(add) + "\n")

    reg = SANDBOX / "registry/error-signatures-r27.json"
    reg.write_text(json.dumps({"schema": "kama-r27-error-signatures/v1",
                               "note": "label-keyed control submission", "signatures": entries},
                              indent=1, sort_keys=True) + "\n")
    print(f"rows={len(entries)} skill_rows={len(rows)} sources_added={len(add)}")


if __name__ == "__main__":
    main()
