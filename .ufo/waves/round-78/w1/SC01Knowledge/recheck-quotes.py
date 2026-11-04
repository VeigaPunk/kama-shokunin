#!/usr/bin/env python3
"""Re-open the two new rows' located quotes; no runtime certification."""
from pathlib import Path
import json

lane = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
seat = lane / '.ufo/waves/round-78/w1/SC01Knowledge'
checks = [
    ('S551', lane / 'tools/round77-append-registers.py', 2, 2,
     'Account for append-only history with independent register introductions.'),
    ('S552', seat / 'kubernetes-service.html', 893, 894,
     'The Service API, part of Kubernetes, is an abstraction to help you expose groups of Pods over a network.'),
]
for source_id, path, first, last, quote in checks:
    lines = path.read_text().splitlines()
    selected = ' '.join(' '.join(lines[first - 1:last]).split())
    assert quote in selected, (source_id, str(path), first, last)
    assert len(quote.split()) <= 25, source_id
    print(json.dumps({'id': source_id, 'path': str(path), 'lines': [first, last],
                      'quote': quote, 'words': len(quote.split()), 'located': True}))
print('QUOTES located=2/2')
