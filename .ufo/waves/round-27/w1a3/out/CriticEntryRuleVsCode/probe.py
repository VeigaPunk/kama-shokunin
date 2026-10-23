"""Read-only component replay; never imports the counter or calls its main()."""
import ast
import hashlib
import json
from pathlib import Path
import re

COUNTER = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/count-c1.py')
EXPECTED = '49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765'
raw = COUNTER.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
assert sha == EXPECTED, sha
print('counter_sha256=' + sha)
tree = ast.parse(raw, filename=str(COUNTER))
helpers = [node for node in tree.body if isinstance(node, ast.FunctionDef)
           and node.name in {'squash', 'occurs', 'json_strings', 'request_surfaces'}]
assert len(helpers) == 4
scope = {'json': json, 're': re}
exec(compile(ast.Module(body=helpers, type_ignores=[]), str(COUNTER), 'exec'), scope)
occurs = scope['occurs']
surfaces = scope['request_surfaces']
json_strings = scope['json_strings']
main_node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
try_node = next(node for node in main_node.body if isinstance(node, ast.Try))
frame_nodes = [node for node in try_node.body if node.lineno in (691, 692)]
assert len(frame_nodes) == 2
assert isinstance(frame_nodes[0], ast.Assign) and isinstance(frame_nodes[1], ast.For)
frame_code = compile(ast.Module(body=frame_nodes, type_ignores=[]), str(COUNTER), 'exec')

def emit(label, value):
    print(label + '=' + json.dumps(value, ensure_ascii=True, sort_keys=True))

def echo_probe(label, sig, req):
    ss = surfaces(req)
    emit(label, {'signature': sig, 'surfaces': ss,
                 'counter_occurs': any(occurs(sig, text) for text in ss),
                 'unicode_casefold_occurs': any(sig.casefold() in text.casefold() for text in ss)})


def frame_probe(label, specs):
    rows = []
    for i, (sig, message, prior_why) in enumerate(specs):
        rows.append({'id': chr(65 + i), 'why': list(prior_why),
                     'entry': {'signature': sig,
                               'source': {'file': 'source-' + str(i), 'line': i + 1,
                                          'row': 'S' + str(1000 + i)},
                               'request': {'method': 'POST', 'path': '/probe', 'body': {'row': i}},
                               '_next': 'distinct next action ' + str(i)},
                     'live': {'message': message}})
    state = {'json': json, 'rows': rows}
    exec(frame_code, state)
    emit(label, {'counted': state['counted'],
                 'why': {row['id']: row['why'] for row in rows},
                 'literal_cut_casefold_remainders': [msg.replace(sig, '').casefold() for sig, msg, _ in specs],
                 'counter_nul_lower_frames': [msg.replace(sig, '\0').lower() for sig, msg, _ in specs]})


echo_probe('unicode_echo', 'invalid-strasse-marker',
           {'path': '/completion', 'body': {'response_format': {'type': 'invalid-stra\u00dfe-marker'}}})
echo_probe('request_path', 'PATH-MARKER-ABC', {'path': '/path-marker-abc', 'body': None})
echo_probe('whitespace_removed', 'decodedwhitespacemarker',
           {'path': '/completion', 'body': {'value': 'decoded \t white\nspace\u2003marker'}})
echo_probe('nested_key', 'nested-key-marker',
           {'path': '/completion', 'body': [[{'nested-key-marker': 'nested-value-marker'}]]})
echo_probe('nested_value', 'nested-value-marker',
           {'path': '/completion', 'body': [[{'nested-key-marker': 'nested-value-marker'}]]})
scalar_body = [123456789012345, 1.25e40, True, None]
scalar_surfaces = surfaces({'path': '/completion', 'body': scalar_body})
emit('nonstring_scalars', {'json_strings': json_strings(scalar_body),
                          'serialized': scalar_surfaces[1:],
                          'canonical_spellings_detected': {sig: any(occurs(sig, s) for s in scalar_surfaces)
                                                          for sig in ('123456789012345', '1.25e+40', 'true', 'null')},
                          'python_None_spelling_detected': any(occurs('None', s) for s in scalar_surfaces)})
wire_body = {'value': '\u03b1\u03b2'}
wire_surfaces = surfaces({'path': '/completion', 'body': wire_body})
emit('both_serialisations', {'surfaces': wire_surfaces,
                             'ascii_present': json.dumps(wire_body) in wire_surfaces,
                             'utf8_present': json.dumps(wire_body, ensure_ascii=False) in wire_surfaces})
a, b = 'alpha-marker-123', 'beta-marker-456'
frame_probe('unicode_frame', [(a, 'Stra\u00dfe: ' + a, []), (b, 'STRASSE: ' + b, [])])
frame_probe('literal_cut_frame', [(a, 'pre' + a + 'lude', []), (b, 'p' + b + 'relude', [])])
frame_probe('tab_only_remainder', [(a, a + '\t', []), (b, b + '\t', [])])
frame_probe('ordinary_shared_frame', [(a, 'fixed: ' + a, []), (b, 'fixed: ' + b, [])])
frame_probe('already_credited_only', [(a, 'fixed: ' + a, ['a:no-skill-row']),
                                      (b, 'fixed: ' + b, [])])
print('scope=only extracted helpers and lines 691-722; main, static/live eligibility, HTTP and servers not run')
