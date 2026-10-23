#!/usr/bin/python3
"""Compare hand-rendered literals with cell bytes; never call/import the renderer."""
import json
from pathlib import Path

CLONE = Path('/tmp/kama-r31w2/RevRowE/clone')
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowE')
# RENDER at frozen counter lines 50-54: ignored is one constant; response
# substitutes the check and JSON value. JSON 2 -> 2; JSON true -> true.
manual = {
    'K31-13': '200, no slot-parameter or response change',
    'K31-14': '200, no slot-parameter or response change',
    'K31-15': '200, no slot-parameter or response change',
    'K31-16': '200, n_choices = 2',
    'K31-17': '200, sse = true',
    'K31-18': '200, sse_usage = true',
}
registry = json.loads((CLONE / 'registry/chat-param-outcomes-r31.json').read_text())
registry = {r['id']: r for r in registry['rows'] if r['id'] in manual}
receipt = json.loads((OUT / 'full-live.json').read_text())
live = {r['id']: r['live'] for r in receipt['rows'] if r['id'] in manual}
records = []
for line_number, line in enumerate((CLONE / 'SKILL.md').read_text().splitlines(), 1):
    if not line.startswith('| K31-'):
        continue
    cells = [c.strip() for c in line.strip('|').split('|')]
    rid = cells[0]
    if rid not in manual:
        continue
    committed, rendered = cells[3], manual[rid]
    same = committed.encode('utf-8') == rendered.encode('utf-8')
    records.append({'id': rid, 'line': line_number, 'registry': registry[rid],
                    'committed_outcome': committed, 'manual_rendered_outcome': rendered,
                    'utf8_bytes_equal': same, 'meaning': cells[4], 'live': live[rid]})
    print(f"{rid} | committed-cell==rendered {'yes' if same else 'no'} | {live[rid]['status']} | overclaim none")
(OUT / 'row-review.json').write_text(json.dumps(records, indent=2) + '\n')
(OUT / 'scoped-live.json').write_text(json.dumps(live, indent=2) + '\n')
