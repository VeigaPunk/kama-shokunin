#!/usr/bin/env python3
"""Offline KQ37-only boundary probe; never imports/runs a counter main or server."""
import ast
import hashlib
import json
from pathlib import Path
import re

LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
OUT = LANE / '.ufo/waves/round-27/w1a3/out/CriticKQ37Wording'
COUNTER = LANE / '.ufo/waves/round-27/count-c1.py'
SHORTCUT = LANE / '.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows'
EXPECTED_SHA = '49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765'

source = COUNTER.read_bytes()
assert hashlib.sha256(source).hexdigest() == EXPECTED_SHA
module = ast.parse(source, filename=str(COUNTER))
names = {'squash', 'occurs', 'json_strings', 'request_surfaces'}
functions = [node for node in module.body
             if isinstance(node, ast.FunctionDef) and node.name in names]
assert {node.name for node in functions} == names
namespace = {'json': json, 're': re}
exec(compile(ast.Module(body=functions, type_ignores=[]), str(COUNTER), 'exec'), namespace)

entries = json.loads((SHORTCUT / 'shortcut.registry.json').read_text())['signatures']
observations = json.loads((SHORTCUT / 'shortcut.receipt.json').read_text())['rows']
assert len(entries) == len(observations) == 12
rows = []
frames_cut = set()
frames_a3 = set()
raising_prefixes = set()
for offset, (entry, observed) in enumerate(zip(entries, observations), start=2):
    assert entry['id'] == observed['id']
    old_sig = entry['signature']
    message = json.loads(observed['observed']['channel_excerpt'])['error']['message']
    assert message.endswith(old_sig)
    prefix = message[:-len(old_sig)]
    raising_prefixes.add(prefix)
    request = dict(entry['request'])
    request.pop('headers')
    request['body'] = json.loads(request['body'])
    # Shift only the submitted signature boundary, not any captured request/message.
    signature = prefix[-offset:] + old_sig
    assert signature in message and len(signature.encode()) >= 20
    surfaces = namespace['request_surfaces'](request)
    echoed_a3 = any(namespace['occurs'](signature, surface) for surface in surfaces)
    fold = lambda text: re.sub(r'\s+', '', text).casefold()
    echoed_casefold = any(signature.casefold() in surface.casefold()
                         or fold(signature) in fold(surface) for surface in surfaces)
    frame_cut = message.replace(signature, '').casefold()
    frame_a3 = message.replace(signature, '\0').lower()
    cut_duplicate = frame_cut in frames_cut
    a3_duplicate = frame_a3 in frames_a3
    frames_cut.add(frame_cut)
    frames_a3.add(frame_a3)
    rows.append({
        'id': entry['id'],
        'fixed_prefix_characters_in_signature': offset,
        'signature': signature,
        'captured_message': message,
        'decoded_request': request,
        'echoed_a3': echoed_a3,
        'echoed_casefold': echoed_casefold,
        'frame_literal_cut': frame_cut,
        'frame_a3_nul': frame_a3,
        'duplicate_frame_literal_cut': cut_duplicate,
        'duplicate_frame_a3_nul': a3_duplicate,
        'kq37_mechanical_accept': not echoed_casefold and bool(frame_cut.strip()) and not cut_duplicate,
    })

result = {
    'scope': 'KQ37 echo/frame predicates only; not the full A3 predicate, not a claim verdict',
    'counter_sha256': EXPECTED_SHA,
    'source': 'S137 server-common.cpp:1375 @704366d76',
    'captured_messages_reused': len(rows),
    'different_actual_fixed_prefixes': len(raising_prefixes),
    'decoded_echo_hits_a3': sum(row['echoed_a3'] for row in rows),
    'decoded_echo_hits_casefold': sum(row['echoed_casefold'] for row in rows),
    'different_literal_cut_frames': len(frames_cut),
    'different_a3_nul_frames': len(frames_a3),
    'kq37_mechanical_accepts': sum(row['kq37_mechanical_accept'] for row in rows),
    'rows': rows,
}
output = OUT / 'frame_boundary_probe.json'
output.write_text(json.dumps(result, indent=2, ensure_ascii=True) + '\n')
print(json.dumps({key: value for key, value in result.items() if key != 'rows'}, indent=2))
print('first_signature=' + repr(rows[0]['signature']))
print('first_frame=' + repr(rows[0]['frame_literal_cut']))
print('last_signature=' + repr(rows[-1]['signature']))
print('last_frame=' + repr(rows[-1]['frame_literal_cut']))
print('output=' + str(output))
