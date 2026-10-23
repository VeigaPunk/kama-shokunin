#!/usr/bin/env python3
"""Bounded offline KQ37 wording probe; never imports or runs count-c1.main()."""
import ast
import hashlib
import json
from pathlib import Path
import re

LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
OUT = LANE / '.ufo/waves/round-27/residual/out/CriticKQ37Qualification'
COUNTER = LANE / '.ufo/waves/round-27/count-c1.py'
SOURCE = LANE / '.ufo/waves/round-27/sources/llama.cpp-704366d/server-common.cpp'
REGISTRY = LANE / '.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json'
RECEIPT = LANE / '.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json'
TAILS = LANE / '.ufo/waves/round-27/w1a3/out/CriticKQ37Wording/frame_boundary_probe.json'
QUALITY = LANE / 'corpus/QUALITY.md'

inputs = {}
for path in (COUNTER, SOURCE, REGISTRY, RECEIPT, TAILS, QUALITY):
    content = path.read_bytes()
    inputs[str(path)] = {'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}
assert inputs[str(COUNTER)]['sha256'] == '49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765'
assert inputs[str(SOURCE)]['sha256'] == 'b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442'

wanted = {'decode_c', 'literal_texts', 'squash', 'occurs', 'json_strings', 'request_surfaces'}
tree = ast.parse(COUNTER.read_text())
nodes = []
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in wanted:
        nodes.append(node)
    elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'LITERAL_RE' for t in node.targets):
        nodes.append(node)
assert len(nodes) == len(wanted) + 1
namespace = {'json': json, 're': re}
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(COUNTER) + ':selected-definitions', 'exec'), namespace)

source_line = SOURCE.read_text().splitlines()[1374]
literals = namespace['literal_texts'](source_line)
assert len(literals) == 1
prefix = literals[0]
assert prefix.endswith('but got: ')


def fold_occurs(signature, text):
    def squash(value):
        return re.sub(r'\s+', '', value).casefold()
    return signature.casefold() in text.casefold() or squash(signature) in squash(text)


def echo(signature, request):
    return any(fold_occurs(signature, text) for text in namespace['request_surfaces'](request))


def occurrences(text, needle):
    if not needle:
        return []  # Empty-string span policy is deliberately not inferred here.
    return [(i, i + len(needle)) for i in range(len(text) - len(needle) + 1) if text.startswith(needle, i)]


def overlap(left, right):
    return max(left[0], right[0]) < min(left[1], right[1])


registry = json.loads(REGISTRY.read_text())['signatures']
receipts = {row['id']: row for row in json.loads(RECEIPT.read_text())['rows']}
tails = json.loads(TAILS.read_text())['rows']
assert len(registry) == len(receipts) == len(tails) == 12
original = []
fixed_owned = []
frames_seen = set()
for index, row in enumerate(registry):
    request = dict(row['request'])
    request['body'] = json.loads(request['body'])
    message = json.loads(receipts[row['id']]['observed']['channel_excerpt'])['error']['message']
    supplied = request['body']['response_format']['type']
    assert supplied == row['signature'] and message == prefix + supplied
    original.append({
        'id': row['id'],
        'raw_request_contains_signature': row['signature'] in row['request']['body'],
        'decoded_echo': echo(row['signature'], request),
        'message': message,
    })
    start = prefix.index('must') + index
    signature = prefix[start:start + 20]
    interval = (start, start + len(signature))
    supplied_interval = (len(prefix), len(message))
    frame = message.replace(signature, '').casefold()
    literal_overlaps = [
        {'request_string': value, 'message_interval': span}
        for value in namespace['json_strings'](request['body'])
        for span in occurrences(message, value)
        if overlap(interval, span)
    ]
    checks = {
        'source_literal_contains_signature': signature in prefix,
        'signature_is_20_ascii_characters': len(signature) == 20 and signature.isascii(),
        'decoded_echo': echo(signature, request),
        'overlaps_provenance_derived_request_interval': overlap(interval, supplied_interval),
        'overlaps_any_equal_request_string': bool(literal_overlaps),
        'nonblank_deleted_frame': bool(frame.strip()),
        'duplicate_deleted_frame': frame in frames_seen,
    }
    eligible = (
        checks['source_literal_contains_signature'] and checks['signature_is_20_ascii_characters']
        and not checks['decoded_echo'] and not checks['overlaps_provenance_derived_request_interval']
        and not checks['overlaps_any_equal_request_string'] and checks['nonblank_deleted_frame']
        and not checks['duplicate_deleted_frame']
    )
    fixed_owned.append({
        'id': row['id'], 'signature': signature, 'signature_interval': interval,
        'source_line': 1375, 'source_literal': prefix,
        'request_derived_interval': supplied_interval, 'checks': checks,
        'deleted_casefold_frame': frame, 'wording_component_predicates_pass': eligible,
    })
    if eligible:
        frames_seen.add(frame)

first = registry[0]
first_request = dict(first['request'])
first_request['body'] = json.loads(first_request['body'])
first_message = original[0]['message']
full_prefix_interval = (0, len(prefix))
prefix_text_matches = [
    {'request_string': value, 'message_interval': span}
    for value in namespace['json_strings'](first_request['body'])
    for span in occurrences(first_message, value)
    if overlap(full_prefix_interval, span)
]
prefix_case = {
    'signature': prefix,
    'signature_interval': full_prefix_interval,
    'request_derived_interval': (len(prefix), len(first_message)),
    'decoded_echo': echo(prefix, first_request),
    'source_literal_contains_signature': prefix in literals,
    'overlap_using_source_provenance': overlap(full_prefix_interval, (len(prefix), len(first_message))),
    'overlap_using_all_equal_request_strings': bool(prefix_text_matches),
    'equal_request_string_spans': prefix_text_matches,
}

tail_results = []
for row in tails:
    message = row['captured_message']
    request = row['decoded_request']
    signature = row['signature']
    supplied = request['body']['response_format']['type']
    assert message == prefix + supplied
    start = message.index(signature)
    tail_results.append({
        'id': row['id'], 'signature': signature,
        'decoded_echo': echo(signature, request),
        'source_literal_contains_signature': signature in prefix,
        'overlaps_provenance_derived_request_interval': overlap((start, start + len(signature)), (len(prefix), len(message))),
    })

unicode_request = {
    'method': 'POST', 'path': '/v1/chat/completions',
    'body': {'messages': [{'role': 'user', 'content': prefix.replace('s', '\u017f')}],
             'response_format': {'type': 'bad-format-marker'}},
}
unicode_results = {
    'ascii_signature': prefix,
    'signature_is_ascii': prefix.isascii(),
    'decoded_content': unicode_request['body']['messages'][0]['content'],
    'a3_lower_flags_echo': any(namespace['occurs'](prefix, surface) for surface in namespace['request_surfaces'](unicode_request)),
    'unicode_casefold_flags_echo': echo(prefix, unicode_request),
    'smaller_ascii_signature': 'invalid-strasse-marker',
    'smaller_decoded_value': 'invalid-stra\u00dfe-marker',
    'smaller_a3_lower_flags_echo': namespace['occurs']('invalid-strasse-marker', 'invalid-stra\u00dfe-marker'),
    'smaller_unicode_casefold_flags_echo': fold_occurs('invalid-strasse-marker', 'invalid-stra\u00dfe-marker'),
    'ascii_signatures_nonascii_remainders': {
        'signatures': ['alpha-marker-123', 'beta-marker-456'],
        'a3_lower_frames': ['Stra\u00dfe: \0'.lower(), 'STRASSE: \0'.lower()],
        'unicode_casefold_frames': ['Stra\u00dfe: \0'.casefold(), 'STRASSE: \0'.casefold()],
    },
}

summary = {
    'original_rows': len(original),
    'original_raw_echo_hits': sum(row['raw_request_contains_signature'] for row in original),
    'original_decoded_echo_hits': sum(row['decoded_echo'] for row in original),
    'tail_rows': len(tail_results),
    'tail_source_literal_failures_at_s137': sum(not row['source_literal_contains_signature'] for row in tail_results),
    'tail_provenance_overlap_failures': sum(row['overlaps_provenance_derived_request_interval'] for row in tail_results),
    'fixed_owned_component_passes': sum(row['wording_component_predicates_pass'] for row in fixed_owned),
    'fixed_owned_distinct_signatures': len({row['signature'] for row in fixed_owned}),
    'fixed_owned_distinct_deleted_frames': len(frames_seen),
    'actual_fixed_prefixes': 1,
    'prefix_false_overlap_by_text_matching': prefix_case['overlap_using_all_equal_request_strings'],
    'prefix_provenance_overlap': prefix_case['overlap_using_source_provenance'],
    'ascii_prefix_lower_echo_hit': unicode_results['a3_lower_flags_echo'],
    'ascii_prefix_casefold_echo_hit': unicode_results['unicode_casefold_flags_echo'],
}
assert summary['original_decoded_echo_hits'] == 12
assert summary['tail_source_literal_failures_at_s137'] == summary['tail_provenance_overlap_failures'] == 12
assert summary['fixed_owned_component_passes'] == summary['fixed_owned_distinct_signatures'] == summary['fixed_owned_distinct_deleted_frames'] == 12
assert summary['prefix_false_overlap_by_text_matching'] and not summary['prefix_provenance_overlap']
assert not summary['ascii_prefix_lower_echo_hit'] and summary['ascii_prefix_casefold_echo_hit']

result = {
    'scope': 'Offline wording/component probe only; no counter main, no server, no source/novelty/admission verdict and no pre-data receipt fabricated.',
    'provenance_intervals': 'S137 emits literal F followed by response_type; intervals are half-open decoded-message character offsets.',
    'hypothetical_receipt_premise': 'Administrative conformance requires bona fide non-author pre-data receipts; none is manufactured or claimed by this probe.',
    'inputs': inputs, 'prefix_length': len(prefix), 'summary': summary,
    'full_prefix_boundary_case': prefix_case, 'original_rows': original,
    'frame_tail_rows': tail_results, 'fixed_owned_rows': fixed_owned,
    'unicode_ascii_signature_counterexamples': unicode_results,
}
output_path = OUT / 'probe.json'
output_path.write_text(json.dumps(result, ensure_ascii=True, indent=2) + '\n')
print(json.dumps(summary, sort_keys=True))
print('PREFIX_BOUNDARY=' + json.dumps(prefix_case, ensure_ascii=True, sort_keys=True))
print('FIXED_OWNED_FIRST=' + json.dumps(fixed_owned[0], ensure_ascii=True, sort_keys=True))
print('FIXED_OWNED_LAST=' + json.dumps(fixed_owned[-1], ensure_ascii=True, sort_keys=True))
print('UNICODE=' + json.dumps(unicode_results, ensure_ascii=True, sort_keys=True))
print('OUT=' + str(output_path))
