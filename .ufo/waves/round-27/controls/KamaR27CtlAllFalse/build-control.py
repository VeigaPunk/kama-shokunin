#!/usr/bin/env python3
"""Construct one all-false control; never edit the frozen counter or source snapshot."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path('/fast/scratch/hyaku/kama-r27/KamaR27CtlAllFalse')
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/controls/KamaR27CtlAllFalse')
COUNTER = ROOT / '.ufo/waves/round-27/count-c1.py'
PIN = '382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6'
assert hashlib.sha256(COUNTER.read_bytes()).hexdigest() == PIN
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('frozen_c1', COUNTER)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

def post(path, body):
    return {'method': 'POST', 'path': path, 'body': body}

def chat(**extra):
    return {'messages': [{'role': 'user', 'content': 'Hi'}], 'max_tokens': 1, **extra}

def completion(**extra):
    return {'prompt': 'Hi', 'n_predict': 1, **extra}

CHAT = '/v1/chat/completions'
COMP = '/completion'
rows = []
intents = []
skill = ['## Round-27 request-validation signatures', '',
         'Adversarial all-false scratch control only: each claimed trigger misses its cited branch.', '',
         '| id | signature | intentionally wrong trigger | cited-branch meaning | next action | source |',
         '|---|---|---|---|---|---|']
sources = ['## All-false control sources (scratch only)', '',
           '| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |',
           '|---|---|---|---|---|---|---|---|---|---|---|']

def add(file, line, signature, request, meaning, action, mode='healthy-or-wrong-error', profile='default', control=None):
    index = len(rows)
    rid, sid = f'E27-{index:02d}', f'S{900 + index}'
    source_line = (ROOT / c1.SOURCE_DIR / file).read_text().splitlines()[line - 1]
    literals = c1.literal_texts(source_line)
    assert any(signature in literal for literal in literals), (rid, source_line, signature)
    assert 'throw' in source_line or 'format_error_response' in source_line, (rid, source_line)
    assert len(signature.encode()) >= 20 and '|' not in signature and '\n' not in signature
    assert len(action.split()) >= 6
    if control is None:
        if request['path'] == CHAT:
            control = post(CHAT, chat())
        elif request['path'] == '/v1/completions':
            control = post('/v1/completions', {'prompt': 'Hi', 'max_tokens': 1})
        elif request['path'] == '/tokenize':
            control = post('/tokenize', {'content': 'Hi'})
        else:
            control = post(COMP, completion())
    row = {'id': rid, 'profile': profile, 'signature': signature,
           'request': request, 'control': control,
           'source': {'row': sid, 'file': file, 'line': line}}
    rows.append(row)
    is_full = signature in literals
    intents.append({'id': rid, 'mode': mode, 'source_file': file, 'source_line': line,
                    'source_text': source_line.strip(), 'full_literal': is_full,
                    'cited_branch_claim': meaning, 'request': request,
                    'expected_detector': 'reject all false claims; any counted row is a coverage finding'})
    body = json.dumps(request.get('body'), ensure_ascii=False, separators=(',', ':'))
    trigger = f"{request['method']} {request['path']} body `{body}`"
    skill.append(f'| {rid} | `{signature}` | {trigger} | {meaning} | {action} | {sid} |')
    path = f'{c1.SOURCE_DIR}/{file}'
    source = f'llama.cpp pinned snapshot — `{path}`'
    anchor = f'{file}#L{line} @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad'
    teaches = meaning.replace('|', '/')
    sources.append(f'| {sid} | {source} | code | A | Cited literal and branch only; no trigger validity claim | {anchor} | {teaches} | mined | 2026-10-23 | on-release | SKILL.md |')

# Eight deliberate literal-overlap attacks, placed before ordinary negatives.
add('chat.cpp', 857, 'Unknown reasoning format',
    post(CHAT, chat(reasoning_format='all-false-unknown')),
    'The enum-to-name formatter received an invalid internal reasoning enum; request instead rejects a string at chat.cpp L874.',
    'Repair the internal reasoning enum before formatting its display name.', 'different-error-shared-words')
add('sampling.cpp', 279, 'failed to parse grammar',
    post(COMP, completion(grammar='%llguidance\nstart: "a"')),
    'Ordinary GBNF initialization returned no grammar; request instead selects unavailable llguidance at sampling.cpp L221.',
    'Repair the ordinary GBNF grammar before retrying sampler initialization.', 'different-error-shared-words')
add('json-schema-to-grammar.cpp', 492, 'unbalanced parentheses',
    post(COMP, completion(json_schema={'type': 'string', 'pattern': '^($'})),
    'A closing parenthesis underflowed parser depth; request instead leaves an opening parenthesis unmatched at L627.',
    'Remove the excess closing parenthesis that underflowed parser depth.', 'different-error-shared-words')
add('chat.cpp', 347, "Expected 'messages' to be an array",
    post(CHAT, {'messages': {}, 'max_tokens': 1}),
    'The lower-level message parser rejected its input; request instead stops at the earlier server-common.cpp L1390 guard.',
    'Repair the lower level parser caller before constructing chat messages.', 'different-error-shared-words')
add('server-common.cpp', 1343, 'param requires --jinja flag',
    post(CHAT, chat(tool_choice='required')),
    'A nonempty tools array requires Jinja; request has no tools and instead fails tool_choice at L1346.',
    'Remove the nonempty tools array before retrying legacy rendering.', 'different-error-shared-words', profile='no-jinja')
add('arg.cpp', 2101, 'must be finite and greater than 0',
    post(COMP, completion(repeat_penalty=0)),
    'The CLI repeat-penalty argument is invalid; request changes no argv and instead fails sampling.cpp L197.',
    'Correct the command line repeat penalty before restarting this process.', 'different-error-shared-words')
add('chat.cpp', 607, 'd continue_final_message',
    post(CHAT, chat(continue_final_message=True, add_generation_prompt=True)),
    'The continuation value has invalid type or spelling; request sends a valid boolean and instead violates mutual exclusion at server-common.cpp L1440.',
    'Replace the malformed continuation value with a supported boolean value.', 'different-error-shared-words')
add('chat.cpp', 1037, 'Failed to parse tool',
    post(CHAT, chat(tools={'not': 'an-array'})),
    'Returned tool-call arguments are invalid JSON; request instead rejects the tools container at L562 and wraps it at L585.',
    'Repair generated tool call argument JSON before deserializing model output.', 'different-error-shared-words')

# Full genuine literals, paired only with healthy or mismatched triggers.
add('server-common.cpp', 1100, 'Multimodal data provided, but model does not support multimodal requests.',
    post(COMP, completion()), 'The model cannot process supplied multimodal data; request supplies plain text only.',
    'Use a multimodal capable model before sending multimodal prompt data.')
add('server-common.cpp', 1129, '"prompt" must not be empty',
    post(COMP, completion()), 'The prompt batch is empty; request supplies a nonempty string prompt.',
    'Populate the prompt batch with at least one valid prompt.')
add('server-common.cpp', 1155, 'Only no echo is supported',
    post('/v1/completions', {'prompt': 'Hi', 'max_tokens': 1, 'echo': False}),
    'OAI completions refuses echo mode; request explicitly disables echo.',
    'Disable echo mode when using this OAI compatible completion route.')
add('server-common.cpp', 1210, 'file:// URLs are not allowed unless --media-path is specified',
    post(CHAT, chat()), 'Media file URLs require a configured media path; request contains no media URL.',
    'Configure the permitted media directory before using local file URLs.')
add('server-common.cpp', 1230, 'Invalid uri-encoded base64 value',
    post(CHAT, chat(messages=[{'role': 'user', 'content': [{'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,'}}]}])),
    'A data URI lacks its separator; request has a separator and instead hits the earlier image capability guard.',
    'Include exactly one separator between data URI metadata and payload.')
add('server-common.cpp', 1236, 'uri must be base64 encoded',
    post('/tokenize', {'content': 'Hi'}), 'A media data URI is not base64 encoded; request uses the text tokenization endpoint.',
    'Encode the media payload as base64 and mark the URI accordingly.')
add('server-common.cpp', 1259, 'image input is not supported - hint: if this is unexpected, you may need to provide the mmproj',
    post(CHAT, chat(messages=[{'role': 'user', 'content': [{'type': 'input_video', 'input_video': {'data': ''}}]}])),
    'Image input capability is unavailable; request supplies video rather than image input.',
    'Attach an image capable projector before submitting image content parts.')
add('server-common.cpp', 1287, 'video input is not supported - hint: if this is unexpected, you may need to provide the mmproj',
    post(CHAT, chat(messages=[{'role': 'user', 'content': [{'type': 'image_url', 'image_url': {'url': ''}}]}])),
    'Video input capability is unavailable; request supplies an image rather than video input.',
    'Attach a video capable projector before submitting video content parts.')
add('server-common.cpp', 1302, 'unsupported content[].type',
    post(CHAT, chat(messages=[{'role': 'user', 'content': [{'type': 'text', 'text': 'Hi'}]}])),
    'A content part has an unsupported type; request supplies the supported text type.',
    'Select a documented content part type before retrying this message.')
add('server-common.cpp', 1309, '"content" must be an array',
    post(CHAT, chat(messages=[{'role': 'user', 'content': {}}])),
    'Embedding OAI content must be an array; request instead fails the earlier chat content shape guard at L1411.',
    'Wrap embedding content parts inside an array before submitting input.')
add('server-common.cpp', 1343, 'tools param requires --jinja flag',
    post(CHAT, chat(tools=[])), 'Legacy rendering refuses a nonempty tools array; request has an empty tools list and default Jinja.',
    'Enable the Jinja renderer before sending nonempty tool declarations.')
add('server-common.cpp', 1346, 'tool_choice param requires --jinja flag',
    post(CHAT, chat(tool_choice='none')), 'Legacy rendering refuses custom tool choice; request uses the default Jinja profile.',
    'Enable Jinja before selecting a nonautomatic legacy tool choice mode.')
add('server-common.cpp', 1360, 'Cannot use both json_schema and grammar',
    post(COMP, completion()), 'Chat requests cannot set schema and grammar together; request sets neither and uses native completion.',
    'Choose either JSON schema constraints or explicit grammar constraints.')
add('server-common.cpp', 1375, 'response_format type must be one of "text" or "json_object", but got: ',
    post(CHAT, chat(response_format={'type': 'text'})), 'The response format type is unsupported; request selects the supported text format.',
    'Choose a supported response format type before resubmitting the request.')
add('server-common.cpp', 1386, "'messages' is required",
    post(COMP, completion()), 'Chat requires messages; request uses the native prompt completion endpoint instead.',
    'Supply a messages array when using the chat completion endpoint.')
add('server-common.cpp', 1390, "Expected 'messages' to be an array",
    post(CHAT, chat()), 'Chat messages is not an array; request supplies a valid messages array.',
    'Replace the messages value with an array of message objects.')
add('server-common.cpp', 1395, "All non-assistant messages must contain 'content'",
    post(CHAT, chat(messages=[{'role': 'assistant'}])),
    'A nonassistant message has no content; request instead contains an assistant message and hits L1399.',
    'Add a content field to each nonassistant message before sending.')
add('server-common.cpp', 1399, "Assistant message must contain either 'content' or 'tool_calls'!",
    post(CHAT, chat(messages=[{'role': 'user'}])),
    'An assistant message lacks content and tools; request instead lacks user content and hits L1395.',
    'Give each assistant message content or a structured tool call.')
add('server-common.cpp', 1411, "Expected 'content' to be a string or an array",
    post(CHAT, chat()), 'Chat content has an unsupported scalar shape; request contains ordinary string content.',
    'Encode message content as a string or structured content array.')
add('server-common.cpp', 1434, 'Cannot have 2 or more assistant messages at the end of the list.',
    post(CHAT, chat()), 'Multiple trailing assistant messages cannot be prefilled; request contains only a user message.',
    'Combine the trailing assistant messages before requesting assistant prefill.')
add('server-common.cpp', 1440, 'Cannot set both add_generation_prompt and continue_final_message to true.',
    post(CHAT, chat(continue_final_message=False, add_generation_prompt=True)),
    'Continuation conflicts with a generation prompt; request explicitly disables continuation.',
    'Disable generation prompt insertion when continuing an existing assistant message.')
add('server-common.cpp', 1446, 'Cannot continue an assistant message that contains tool calls.',
    post(CHAT, chat(continue_final_message=True, add_generation_prompt=True)),
    'An assistant tool call cannot be continued; request contains no assistant tool calls and fails mutual exclusion first.',
    'Finish the assistant tool call before requesting continuation of content.')
add('server-common.cpp', 1455, 'Cannot use custom grammar constraints with tools.',
    post(CHAT, chat()), 'Tool requests cannot also use custom grammar constraints; request contains neither tools nor grammar.',
    'Remove custom grammar constraints from requests that enable tool calls.')
add('server-common.cpp', 1473, 'invalid type for "enable_thinking" (expected boolean, got string)',
    post(CHAT, chat(chat_template_kwargs={'enable_thinking': False})),
    'The thinking template argument is a string; request supplies a valid boolean.',
    'Send enable thinking as a JSON boolean rather than quoted text.')
add('server-common.cpp', 1517, 'logprobs is not supported with tools + stream',
    post(CHAT, chat(logprobs=True, stream=False)),
    'Tools plus streaming cannot return logprobs; request disables streaming and declares no tools.',
    'Disable streaming or tool declarations before asking for token logprobs.')
add('server-common.cpp', 1521, 'top_logprobs requires logprobs to be set to true',
    post(CHAT, chat(logprobs=True, top_logprobs=2)),
    'Top logprobs requires enabled logprobs; request already enables that field.',
    'Enable logprobs before specifying the requested count of top alternatives.')
add('json-schema-to-grammar.cpp', 515, 'unterminated character class',
    post(COMP, completion(json_schema={'type': 'string', 'pattern': '^($'})),
    'A regex character class is unclosed; request contains no character class and instead leaves a parenthesis unmatched.',
    'Close the regex character class before converting its JSON schema.')
add('server-context.cpp', 6161, 'The format to return the embeddings in. Can be either float or base64',
    post('/tokenize', {'content': 'Hi'}),
    'Embedding output encoding is unsupported; request instead tokenizes plain text on a different endpoint.',
    'Choose float or base64 for the embedding output encoding format.')
add('server-context.cpp', 5484, '"prompt" must be a string',
    post(COMP, completion(prompt=[])),
    'Infill validates prompt string type; request instead uses native completion and hits empty prompt validation.',
    'Send a string prompt when using the infill request handler.')
add('server-context.cpp', 5497, '"input_extra" must be an array of {"filename": string, "text": string}',
    post(COMP, completion(input_extra={})),
    'Infill extra input must be an array; request uses native completion where this field is irrelevant.',
    'Represent extra infill input as an array of filename text objects.')
add('server-context.cpp', 5510, 'extra_context chunk\'s "filename" field must be a string',
    post(COMP, completion()),
    'An infill extra chunk filename has invalid type; request has no infill extra chunks.',
    'Use a string filename for each extra infill context chunk.')
add('server-common.cpp', 393, 'Server tokens state is too large',
    post(COMP, completion()),
    'Serialized server token state exceeds uint32 bounds; request is a tiny plain text completion.',
    'Reduce the saved token state before serializing this server prompt.')

assert len(rows) >= 20
assert sum(i['full_literal'] for i in intents) >= 20
registry = json.dumps({'signatures': rows}, indent=1) + '\n'
# Registry is a new control artifact, not a rewrite of existing source.
registry_path = ROOT / c1.REGISTRY
assert not registry_path.exists()
registry_path.write_text(registry)
(OUT / 'control-registry.json').write_text(registry)
(OUT / 'row-intent.json').write_text(json.dumps(intents, indent=1) + '\n')
(OUT / 'skill-fragment.md').write_text('\n'.join(skill) + '\n')
(OUT / 'sources-fragment.md').write_text('\n'.join(sources) + '\n')
print(f'Constructed {len(rows)} rows, {sum(i["full_literal"] for i in intents)} full literals; counter untouched.')
