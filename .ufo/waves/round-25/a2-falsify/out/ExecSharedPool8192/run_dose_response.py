#!/usr/bin/env python3
"""ExecSharedPool8192 — supplementary dose-response for the C2 statement
"the limit is the pool total, not the layout".

Layout is held fixed (unified / --kv-unified, 4 slots, per-slot ceiling 2048)
while the KV pool total varies: 2048 (L1's pool), 3072, 4096. The L1 request
pair needs 2 x (1000 prompt + 600 predicted) = 3200 cells at once. If the pool
total is the binding constraint, the outcome must flip between a pool of 3072
(fail) and a pool of 4096 (pass), while the per-slot ceiling stays 2048 in
every cell.

Same request code as the registered L cells (imported from the committed
tool). Fresh server per cell, one child at a time, ports 47420-47439.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
TOOL = LANE / 'tools' / 'kama-context-capacity.py'
OUT_DIR = LANE / '.ufo/waves/round-25/a2-falsify/out/ExecSharedPool8192'
SCRATCH = Path('/fast/scratch/hyaku/kama-r25a2w2/ExecSharedPool8192')
PORT_LOW, PORT_HIGH = 47420, 47439
HOST = '127.0.0.1'

CELLS = [
    {'id': 'D2048', 'args': '-c 2048 -np 4 --kv-unified',
     'kind': 'load-concurrent'},
    {'id': 'D3072', 'args': '-c 3072 -np 4 --kv-unified',
     'kind': 'load-concurrent'},
    {'id': 'D4096', 'args': '-c 4096 -np 4 --kv-unified',
     'kind': 'load-concurrent'},
]


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    m = load_module(TOOL, 'kama_context_capacity')
    live = m.load_live_module(m.locate_live_module())

    server_real = os.path.realpath(Path.home() / '.local/bin/llama-server')
    model_real = os.path.realpath(
        Path.home() / '.cache/kama-shokunin/models/stories260K.gguf')
    ver = subprocess.run([server_real, '--version'], capture_output=True,
                         text=True, timeout=60)
    server_version = ver.stdout.strip() or ver.stderr.strip()
    model_sha = m._sha256_file(model_real)
    assert m.SERVER_VERSION_MARK in server_version, server_version
    assert model_sha == m.MODEL_SHA, model_sha

    refused = live.refused_ports()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    raw_dir = SCRATCH / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)

    cfg = {'server_real': server_real, 'model_real': model_real,
           'server_sha256': m._sha256_file(server_real),
           'model_sha256': model_sha,
           'scratch': str(SCRATCH),
           'ready_timeout': 180.0}

    receipt = {
        'schema': 'kama-round-25-a2-falsify/shared-pool-dose/v1',
        'purpose': 'layout held fixed (unified, 4 slots, per-slot 2048); '
                   'KV pool total varied 2048 / 3072 / 4096; the L1 request '
                   'pair needs 3200 cells at once',
        'registered': False,
        'server_version': server_version,
        'model_sha256': model_sha,
        'host': HOST,
        'port_range': [PORT_LOW, PORT_HIGH],
        'runs': [],
        'started_utc': m._utc_now(),
    }

    used = []
    for cell in CELLS:
        idle_ok, waited, seen = m.wait_for_host_idle(300.0)
        if not idle_ok:
            receipt['runs'].append({'id': cell['id'],
                                    'error': 'host-not-idle',
                                    'other_pids_seen': seen})
            break
        port = m.pick_free_port(live, refused, PORT_LOW, PORT_HIGH, used)
        if port is None:
            receipt['runs'].append({'id': cell['id'],
                                    'error': 'no-free-port-in-range'})
            break
        used.append(port)
        hits, err = m.ss_listen_lines(port)
        if hits is None or hits:
            receipt['runs'].append({'id': cell['id'],
                                    'error': f'port-not-free:{port}:{err}'})
            break
        receipt['runs'].append(
            m.run_cell(cell, cfg, live, refused, port, raw_dir))

    receipt['ended_utc'] = m._utc_now()
    receipt['summary'] = {
        'runs': len(receipt['runs']),
        'observed': sum(1 for r in receipt['runs'] if r.get('observed')),
        'ports_used': [r.get('port') for r in receipt['runs']],
        'all_ports_closed': all(
            r.get('teardown', {}).get('port_closed')
            for r in receipt['runs'] if 'teardown' in r),
    }
    (OUT_DIR / 'shared-pool-dose-receipt.json').write_text(
        json.dumps(receipt, ensure_ascii=True, indent=2, sort_keys=True) + '\n',
        encoding='utf-8')
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
