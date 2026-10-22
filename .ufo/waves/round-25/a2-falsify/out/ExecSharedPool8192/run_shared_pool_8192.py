#!/usr/bin/env python3
"""ExecSharedPool8192 — round-25 wave-2 falsification of the C2 statement
"the limit is the pool total, not the layout".

Unregistered supporting cell (not part of the 14-cell claim count):

    -c 8192 -np 4 --kv-unified

with the L1 request pair: two concurrent POST /completion requests, each a
1000-token prompt given as a flat list of token ids, n_predict 600,
ignore_eos true, cache_prompt false, stream false.

The request code is reused by import from the committed tool
`tools/kama-context-capacity.py` (run_cell / _run_load_requests), so the
request shape is byte-identical to the registered L cells.

Three fresh servers, one child at a time, ports 47420-47439 on 127.0.0.1.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
TOOL = LANE / 'tools' / 'kama-context-capacity.py'
OUT_DIR = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/'
                'waves/round-25/a2-falsify/out/ExecSharedPool8192')
SCRATCH = Path('/fast/scratch/hyaku/kama-r25a2w2/ExecSharedPool8192')
PORT_LOW, PORT_HIGH = 47420, 47439
RUNS = 3
CELL_ARGS = '-c 8192 -np 4 --kv-unified'
HOST = '127.0.0.1'


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    m = load_module(TOOL, 'kama_context_capacity')
    live_path = m.locate_live_module()
    live = m.load_live_module(live_path)

    server_arg = Path.home() / '.local/bin/llama-server'
    model_arg = Path.home() / '.cache/kama-shokunin/models/stories260K.gguf'
    server_real = os.path.realpath(server_arg)
    model_real = os.path.realpath(model_arg)
    ver = subprocess.run([server_real, '--version'], capture_output=True,
                         text=True, timeout=60)
    server_version = ver.stdout.strip() or ver.stderr.strip()
    model_sha = m._sha256_file(model_real)
    assert m.SERVER_VERSION_MARK in server_version, server_version
    assert model_sha == m.MODEL_SHA, model_sha

    refused = live.refused_ports()
    for hard in (8080, 34113):
        assert hard in refused, f'hard pin {hard} missing'

    SCRATCH.mkdir(parents=True, exist_ok=True)
    raw_dir = SCRATCH / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)

    cfg = {'server_real': server_real, 'model_real': model_real,
           'server_sha256': m._sha256_file(server_real),
           'model_sha256': model_sha,
           'scratch': str(SCRATCH),
           'ready_timeout': 180.0}

    receipt = {
        'schema': 'kama-round-25-a2-falsify/shared-pool-8192/v1',
        'cell': {'id': 'S1', 'args': CELL_ARGS, 'kind': 'load-concurrent',
                 'registered': False,
                 'note': 'unregistered supporting cell; not part of the '
                         '14-cell claim count'},
        'request_pair': {
            'source': 'L1 request pair (same shape as the registered L cells)',
            'endpoint': 'POST /completion',
            'concurrency': 'two requests started behind a barrier',
            'prompt': 'flat list of 1000 token ids',
            'n_predict': 600, 'ignore_eos': True, 'cache_prompt': False,
            'stream': False,
        },
        'tool': {'path': str(TOOL), 'sha256': m._sha256_file(TOOL)},
        'live_module': str(live_path),
        'server': {'realpath': server_real,
                   'sha256': cfg['server_sha256'],
                   'version': server_version},
        'model': {'realpath': model_real, 'sha256': model_sha},
        'host': HOST,
        'port_range': [PORT_LOW, PORT_HIGH],
        'runs': [],
        'started_utc': m._utc_now(),
    }

    used_ports = []
    for n in range(1, RUNS + 1):
        cell = {'id': f'S{n}', 'args': CELL_ARGS, 'kind': 'load-concurrent'}
        idle_ok, waited, seen = m.wait_for_host_idle(300.0)
        if not idle_ok:
            receipt['runs'].append({'id': cell['id'], 'error':
                                    'host-not-idle', 'other_pids_seen': seen})
            break
        port = m.pick_free_port(live, refused, PORT_LOW, PORT_HIGH, used_ports)
        if port is None:
            receipt['runs'].append({'id': cell['id'], 'error':
                                    'no-free-port-in-range'})
            break
        used_ports.append(port)
        hits, err = m.ss_listen_lines(port)
        if hits is None:
            receipt['runs'].append({'id': cell['id'], 'error':
                                    f'ss-check-failed:{err}'})
            break
        if hits:
            receipt['runs'].append({'id': cell['id'], 'error':
                                    f'port-not-free:{port}'})
            break
        record = m.run_cell(cell, cfg, live, refused, port, raw_dir)
        receipt['runs'].append(record)

    receipt['ended_utc'] = m._utc_now()
    receipt['summary'] = {
        'runs': len(receipt['runs']),
        'observed': sum(1 for r in receipt['runs'] if r.get('observed')),
        'ports_used': [r.get('port') for r in receipt['runs']],
        'all_ports_closed': all(
            r.get('teardown', {}).get('port_closed')
            for r in receipt['runs'] if 'teardown' in r),
    }
    out = OUT_DIR / 'shared-pool-8192-receipt.json'
    out.write_text(json.dumps(receipt, ensure_ascii=True, indent=2,
                               sort_keys=True) + '\n', encoding='utf-8')
    # keep the raw server logs next to the receipt (they are the pool-line
    # evidence); they are ~200 kB each.
    for r in receipt['runs']:
        rid = r.get('id')
        if not rid:
            continue
        src = raw_dir / f'{rid}.server.log'
        if src.is_file():
            (OUT_DIR / f'{rid}.server.log').write_bytes(src.read_bytes())
    print(json.dumps(receipt['summary'], sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
