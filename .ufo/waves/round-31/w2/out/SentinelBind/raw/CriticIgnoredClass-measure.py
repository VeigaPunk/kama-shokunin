#!/usr/bin/env python3
"""CriticIgnoredClass: exact-fixture observations, not a counter or admission gate.

Run once from /tmp/r31w1-CriticIgnoredClass. Creates fresh evidence files next to
this script. Uses only the mandated server argv and stops/reaps its own server.
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
from pathlib import Path
import random
import runpy
import signal
import socket
import statistics
import subprocess
import time
import traceback
import urllib.error
import urllib.request

OUT = Path(__file__).resolve().parent
REPO = Path('/tmp/r31w1-CriticIgnoredClass')
FROZEN = '0e6f8ed6891c09d5208ac1fdcb294ed9a842832e'
SERVER = Path.home() / '.local/opt/llama-b11755/llama-server'
LIBRARY = SERVER.parent / 'libllama-server-impl.so'
MODEL = Path.home() / '.cache/kama-shokunin/models/stories260K.gguf'
BASE = {'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 1}
VALUES = {
    'user': 'probe-user',
    'parallel_tool_calls': False,
    'tools': [{'type': 'function', 'function': {'name': 'f', 'parameters': {'type': 'object'}}}],
}
EXPECTED = {
    SERVER: 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804',
    LIBRARY: 'e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed',
    MODEL: '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d',
}


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def emit_new(name, obj):
    with (OUT / name).open('x') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write('\n')


def free(port):
    with socket.socket() as s:
        return s.connect_ex(('127.0.0.1', port)) != 0


def http(port, method, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f'http://127.0.0.1:{port}{path}', data=data, method=method,
                                 headers={'Content-Type': 'application/json'})
    began = time.monotonic_ns()
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            status, raw, headers = r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        status, raw, headers = e.code, e.read(), dict(e.headers)
    result = {'method': method, 'path': path, 'status': status,
              'elapsed_ms': (time.monotonic_ns() - began) / 1e6,
              'headers': headers, 'body_raw': raw.decode(errors='replace')}
    try:
        result['body'] = json.loads(raw)
    except json.JSONDecodeError:
        result['body'] = None
    return result, raw


def changed(before, after, eq):
    return {k: {'before': before.get(k), 'after': after.get(k)}
            for k in sorted(before.keys() | after.keys())
            if k not in before or k not in after or not eq(before[k], after[k])}


def main():
    receipt = {'axes': ['depth', 'calibration', 'operability'], 'frozen_checkout': FROZEN,
               'base_body': BASE, 'treatments': VALUES, 'requests': [], 'error': None,
               'installs': [], 'protocol': '20 default cycles; then 20 matched-seed cycles (seeds 0..19)'}
    proc = None
    port = None
    exit_code = 0
    counter_path = REPO / '.ufo/waves/round-31/count-c1.py'
    try:
        receipt['checkout_observed'] = subprocess.check_output(
            ['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
        assert receipt['checkout_observed'] == FROZEN
        assert digest(counter_path) == 'd86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216'
        # Import only the frozen normalization/comparison functions; do not run its main.
        counter = runpy.run_path(str(counter_path), run_name='critic_read_only_counter')
        normalize, eq = counter['normalize_response'], counter['f32_eq']
        receipt['artifact_pins'] = {str(p): digest(p) for p in EXPECTED}
        assert all(receipt['artifact_pins'][str(p)] == want for p, want in EXPECTED.items())
        source_root = REPO / '.ufo/waves/round-31/sources'
        source_pins = json.loads((source_root / 'SNAPSHOT.json').read_text())
        receipt['source_commit'] = source_pins['commit']
        receipt['source_pins'] = {}
        for name, pin in source_pins['files'].items():
            actual = digest(source_root / 'llama.cpp-704366d' / name)
            receipt['source_pins'][name] = actual
            assert actual == pin['sha256']
        ports = list(range(47900, 48000))
        random.SystemRandom().shuffle(ports)
        port = next(p for p in ports if free(p))
        receipt['port'] = port
        receipt['port_free_before'] = free(port)
        argv = [str(SERVER), '-m', str(MODEL), '--host', '127.0.0.1', '--port', str(port)]
        env = {k: v for k, v in os.environ.items()
               if k not in ('PYTHONPATH', 'PYTHONSTARTUP', 'PYTHONHOME', 'LD_PRELOAD', 'LD_LIBRARY_PATH')}
        env['LD_LIBRARY_PATH'] = str(SERVER.parent)
        receipt['argv'] = argv
        receipt['LD_LIBRARY_PATH'] = env['LD_LIBRARY_PATH']
        logpath = OUT / 'server.log'
        with logpath.open('xb', buffering=0) as logfile:
            proc = subprocess.Popen(argv, cwd=REPO, env=env, stdout=logfile, stderr=subprocess.STDOUT)
            receipt['pid'] = proc.pid
            ready = time.monotonic() + 30
            while time.monotonic() < ready:
                if proc.poll() is not None:
                    raise RuntimeError(f'server exited before readiness: {proc.returncode}')
                try:
                    health, _ = http(port, 'GET', '/health')
                    if health['status'] == 200:
                        receipt['health'] = health
                        break
                except (OSError, TimeoutError):
                    pass
                time.sleep(0.05)
            else:
                raise RuntimeError('health did not become ready')
            receipt['proc_exe'] = str((Path('/proc') / str(proc.pid) / 'exe').resolve())
            receipt['proc_cmdline'] = (Path('/proc') / str(proc.pid) / 'cmdline').read_bytes().decode().split('\0')[:-1]
            receipt['props'], _ = http(port, 'GET', '/props')
            assert Path(receipt['props']['body']['model_path']).resolve() == MODEL.resolve()
            receipt['metrics_before'], _ = http(port, 'GET', '/metrics')
            anchor_params = None
            anchor_norm = None
            for phase in ('default', 'matched_seed'):
                for repeat in range(20):
                    names = list(VALUES)
                    random.Random(31000 + repeat).shuffle(names)
                    cycle_base_params = None
                    cycle_base_norm = None
                    for name in ['base', *names]:
                        body = dict(BASE)
                        if phase == 'matched_seed':
                            body['seed'] = repeat
                        if name != 'base':
                            body[name] = VALUES[name]
                        before = logpath.stat().st_size
                        result, raw = http(port, 'POST', '/v1/chat/completions', body)
                        slots, _ = http(port, 'GET', '/slots')
                        assert slots['status'] == 200
                        newest = max(slots['body'], key=lambda s: s.get('id_task', -1))
                        time.sleep(0.002)
                        after = logpath.stat().st_size
                        with logpath.open('rb') as logread:
                            logread.seek(before)
                            logtext = logread.read(after - before).decode(errors='replace')
                        params = newest.get('params') or {}
                        norm = normalize(raw)
                        if name == 'base':
                            cycle_base_params, cycle_base_norm = params, norm
                            if anchor_params is None:
                                anchor_params, anchor_norm = params, norm
                        doc = result['body'] or {}
                        choices = doc.get('choices') or []
                        record = {'phase': phase, 'repeat': repeat, 'name': name, 'request': body,
                                  'http': result, 'slot': newest, 'normalized': norm,
                                  'params_delta_vs_cycle_base': changed(cycle_base_params, params, eq),
                                  'normalized_equal_cycle_base': norm == cycle_base_norm,
                                  'params_delta_vs_frozen_anchor': changed(anchor_params, params, eq),
                                  'normalized_equal_frozen_anchor': norm == anchor_norm,
                                  'choices': choices, 'usage': doc.get('usage'), 'timings': doc.get('timings'),
                                  'log_byte_range': [before, after], 'server_log': logtext}
                        receipt['requests'].append(record)
            receipt['metrics_after'], _ = http(port, 'GET', '/metrics')
    except BaseException:
        receipt['error'] = traceback.format_exc()
        exit_code = 1
    finally:
        if proc is not None:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=10)
            receipt['server_exit'] = proc.returncode
        if port is not None:
            deadline = time.monotonic() + 10
            while not free(port) and time.monotonic() < deadline:
                time.sleep(0.05)
            receipt['port_free_after'] = free(port)
            if not receipt['port_free_after']:
                exit_code = 1
        emit_new('raw.json', receipt)

    summary = {'error': receipt['error'], 'port': port, 'server_exit': receipt.get('server_exit'),
               'port_free_after': receipt.get('port_free_after'), 'metrics_status':
               [receipt.get('metrics_before', {}).get('status'), receipt.get('metrics_after', {}).get('status')],
               'phases': {}}
    for phase in ('default', 'matched_seed'):
        groups = {}
        for name in ['base', *VALUES]:
            group = [r for r in receipt['requests'] if r['phase'] == phase and r['name'] == name]
            texts = collections.Counter()
            finish_reasons = collections.Counter()
            for r in group:
                for choice in r['choices']:
                    texts[str(choice.get('message', {}).get('content', choice.get('text')))] += 1
                    finish_reasons[str(choice.get('finish_reason'))] += 1
            server_timings = collections.defaultdict(list)
            for r in group:
                for key, val in (r['timings'] or {}).items():
                    if isinstance(val, (int, float)):
                        server_timings[key].append(val)
            groups[name] = {'n': len(group), 'statuses': dict(collections.Counter(r['http']['status'] for r in group)),
                            'prompt_tokens': sorted({r['usage']['prompt_tokens'] for r in group if r['usage']}),
                            'completion_tokens': sorted({r['usage']['completion_tokens'] for r in group if r['usage']}),
                            'cached_tokens': sorted({r['usage'].get('prompt_tokens_details', {}).get('cached_tokens')
                                                     for r in group if r['usage']}),
                            'any_param_delta': sum(bool(r['params_delta_vs_cycle_base']) for r in group),
                            'normalized_equal_cycle_base': sum(r['normalized_equal_cycle_base'] for r in group),
                            'text_distribution': dict(texts), 'finish_reasons': dict(finish_reasons),
                            'elapsed_ms': {'min': min((r['http']['elapsed_ms'] for r in group), default=None),
                                           'median': statistics.median([r['http']['elapsed_ms'] for r in group]) if group else None,
                                           'max': max((r['http']['elapsed_ms'] for r in group), default=None)},
                            'server_timings': {k: {'min': min(v), 'median': statistics.median(v), 'max': max(v)}
                                               for k, v in server_timings.items()}}
        base_by_repeat = {r['repeat']: r for r in receipt['requests'] if r['phase'] == phase and r['name'] == 'base'}
        for name in VALUES:
            group = [r for r in receipt['requests'] if r['phase'] == phase and r['name'] == name]
            groups[name]['matched_choice_content_differences'] = sum(
                [c.get('message', {}).get('content') for c in r['choices']] !=
                [c.get('message', {}).get('content') for c in base_by_repeat[r['repeat']]['choices']]
                for r in group)
            groups[name]['matched_choice_message_differences'] = sum(
                [c.get('message') for c in r['choices']] !=
                [c.get('message') for c in base_by_repeat[r['repeat']]['choices']]
                for r in group)
        summary['phases'][phase] = groups
    emit_new('summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
