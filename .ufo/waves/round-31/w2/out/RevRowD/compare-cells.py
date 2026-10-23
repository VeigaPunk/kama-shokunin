#!/usr/bin/python3
"""Compare hand-derived RENDER literals to committed cells, without importing render()."""
import argparse
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--clone', required=True)
ap.add_argument('--out', required=True)
a = ap.parse_args()
# Hand-applied reject rule: 'reject <status> <type>: <message>'.
# The rule is at frozen docstring L50-L54 (not L40-L46 in these frozen bytes).
expected = {
    'K31-11': 'reject 500 server_error: Cannot use both json_schema and grammar',
    'K31-12': 'reject 400 invalid_request_error: logprobs is not supported with tools + stream',
}
rows = {}
for line_number, line in enumerate((Path(a.clone) / 'SKILL.md').read_text().splitlines(), 1):
    if not line.startswith('|'):
        continue
    cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
    if cells and cells[0] in expected:
        rid = cells[0]
        same = cells[3].encode('utf-8') == expected[rid].encode('utf-8')
        rows[rid] = {'line': line_number, 'table_row': line, 'committed': cells[3],
                     'hand_rendered': expected[rid], 'equal_bytes': same,
                     'committed_utf8_hex': cells[3].encode('utf-8').hex(),
                     'hand_rendered_utf8_hex': expected[rid].encode('utf-8').hex(),
                     'meaning': cells[4]}
        print(f'{rid} committed-cell==rendered={"yes" if same else "no"} utf8_bytes={len(cells[3].encode("utf-8"))}')
if set(rows) != set(expected):
    raise RuntimeError('An assigned table row was not found')
Path(a.out).write_text(json.dumps(rows, indent=2) + '\n')
