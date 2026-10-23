#!/usr/bin/env python3
"""Compare hand-derived reject cells; never import the counter's render function."""
import json
from pathlib import Path

CLONE = Path('/tmp/kama-r31w2/RevRowC/lane')
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowC')
# Literal manual substitutions into RENDER's reject rule at count-c1.py L50-L51:
HAND = {
    'K31-07': "reject 400 invalid_request_error: All non-assistant messages must contain 'content'",
    'K31-08': "reject 400 invalid_request_error: Assistant message must contain either 'content' or 'tool_calls'!",
    'K31-09': "reject 400 invalid_request_error: Expected 'content' to be a string or an array",
}
registry = json.loads((CLONE / 'registry/chat-param-outcomes-r31.json').read_text())
receipt = json.loads((OUT / 'c1.json').read_text())
registry_rows = {r['id']: r for r in registry['rows'] if r['id'] in HAND}
live_rows = {r['id']: r['live'] for r in receipt['rows'] if r['id'] in HAND}
comparisons = []
for number, line in enumerate((CLONE / 'SKILL.md').read_bytes().splitlines(), 1):
    if not line.startswith(b'| K31-0'):
        continue
    cells = [part.strip() for part in line.strip(b'|').split(b'|')]
    rid = cells[0].decode('ascii')
    if rid not in HAND:
        continue
    expected = HAND[rid].encode('utf-8')
    same = cells[3] == expected
    print(f'{rid} | committed-cell==rendered {"yes" if same else "no"} | live-status {live_rows[rid]["status"]}')
    print(f'  committed={cells[3].decode("utf-8")}')
    print(f'  hand-render={HAND[rid]}')
    print(f'  live={json.dumps(live_rows[rid], sort_keys=True)}')
    comparisons.append({
        'id': rid, 'skill_line': number, 'registry': registry_rows[rid],
        'committed_cell': cells[3].decode('utf-8'), 'manual_render': HAND[rid],
        'committed_utf8_hex': cells[3].hex(), 'manual_utf8_hex': expected.hex(),
        'equal_utf8_bytes': same, 'meaning': cells[4].decode('utf-8'),
        'live': live_rows[rid],
    })
(OUT / 'hand-render-comparison.json').write_text(json.dumps(comparisons, indent=2) + '\n')
(OUT / 'scoped-live.json').write_text(json.dumps(live_rows, indent=2) + '\n')
raise SystemExit(0 if len(comparisons) == 3 and all(row['equal_utf8_bytes'] for row in comparisons) else 1)
