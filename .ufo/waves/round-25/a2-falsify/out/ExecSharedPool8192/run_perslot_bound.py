#!/usr/bin/env python3
"""ExecSharedPool8192 — boundary cell: does the per-slot ceiling ever bind?

Pool total 8192 (as in the assigned cell) but the per-slot ceiling lowered
to 512 with --kv-unified-per-slot 512. The L1 request pair sends a 1000-token
prompt, which is above a 512 per-slot ceiling. This is the one direction the
assigned cell cannot show: whether the served limit is the pool total alone
or the smaller of the pool total and the per-slot ceiling.
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
    {'id': 'D8192PS512',
     'args': '-c 8192 -np 4 --kv-unified --kv-unified-per-slot 512',
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
    raw_dir = SCRATCH / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    cfg = {'server_real': server_real, 'model_real': model_real,
           'server_sha256': m._sha256_file(server_real),
           'model_sha256': model_sha,
           'scratch': str(SCRATCH),
           'ready_timeout': 180.0}

    receipt = {
        'schema': 'kama-round-25-a2-falsify/shared-pool-perslot/v1',
        'purpose': 'pool total 8192 kept, per-slot ceiling lowered to 512; '
                   'does the per-slot ceiling bind before the pool total?',
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
                                    'error': 'host-not-idle'})
            break
        port = m.pick_free_port(live, refused, PORT_LOW, PORT_HIGH, used)
        if port is None:
            receipt['runs'].append({'id': cell['id'],
                                    'error': 'no-free-port-in-range'})
            break
        used.append(port)
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
    (OUT_DIR / 'shared-pool-perslot-receipt.json').write_text(
        json.dumps(receipt, ensure_ascii=True, indent=2, sort_keys=True) + '\n',
        encoding='utf-8')
    for r in receipt['runs']:
        rid = r.get('id')
        src = raw_dir / f'{rid}.server.log'
        if rid and src.is_file():
            (OUT_DIR / f'{rid}.server.log').write_bytes(src.read_bytes())
    print(json.dumps(receipt['summary'], sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
