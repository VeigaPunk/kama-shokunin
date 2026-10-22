#!/usr/bin/env python3
"""exec-boundary-pool.py — wave-2 falsification seat ExecBoundaryPool.

Attacks the round-25 C2 arithmetic claim:

    "two requests overflow the 2048 pool at 1025 tokens each"
    (corpus/knowledge/context-capacity.md, L1 cell; final/raw/L1.server.log)

Unregistered supporting boundary pair on the L1 config (`-c 0`): two concurrent
1000-token prompts with n_predict 24 and with n_predict 30, ignore_eos true,
cache_prompt false, no streaming.

One llama-server child at a time, 127.0.0.1 only, ports 47440-47459.
Every child is killed and its port proven closed before the run returns.

Usage:
    exec-boundary-pool.py --n-predict 24 --label np24-r1 --out <results.json>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SERVER = Path.home() / '.local/bin/llama-server'
MODEL = Path.home() / '.cache/kama-shokunin/models/stories260K.gguf'
HOST = '127.0.0.1'
PORT_LOW, PORT_HIGH = 47440, 47459
PROMPT_TOKENS = 1000
CHILD_ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')
READY_TIMEOUT = 90.0
HTTP_TIMEOUT = 300.0
TERM_GRACE = 10.0

POOL_RE = re.compile(r'llama_context: n_ctx\s*=\s*(\d+)')
RELEASE_RE = re.compile(r'release: id\s+(\d+)\s*\|\s*task\s+(\d+)\s*\|'
                        r'\s*stop processing: n_tokens = (\d+), truncated = (\d+)')
OVERSIZE_RE = re.compile(r'Context size has been exceeded')
SLOT_INIT_RE = re.compile(r'load_model: initializing, n_slots = (\d+), '
                          r'n_ctx_slot = (\d+), kv_unified = (\S+)')

_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace(
        '+00:00', 'Z')


def http_get(port, path, timeout=10.0):
    req = urllib.request.Request(f'http://{HOST}:{port}{path}', method='GET')
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            return {'status': resp.status, 'body': resp.read(65536),
                    'error': None}
    except urllib.error.HTTPError as exc:
        return {'status': exc.code, 'body': exc.read(65536), 'error': None}
    except Exception as exc:  # noqa: BLE001 - network shapes are recorded
        return {'status': None, 'body': b'', 'error': f'{type(exc).__name__}: {exc}'}


def http_post(port, path, payload, timeout=HTTP_TIMEOUT):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f'http://{HOST}:{port}{path}', data=data,
                                 method='POST',
                                 headers={'Content-Type': 'application/json'})
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            return {'status': resp.status, 'body': resp.read(65536),
                    'error': None}
    except urllib.error.HTTPError as exc:
        return {'status': exc.code, 'body': exc.read(65536), 'error': None}
    except Exception as exc:  # noqa: BLE001
        return {'status': None, 'body': b'', 'error': f'{type(exc).__name__}: {exc}'}


def ss_listen_ports():
    out = subprocess.run(['ss', '-ltnH'], capture_output=True, text=True,
                         timeout=30)
    ports = set()
    for line in out.stdout.splitlines():
        m = re.search(r':(\d+)\s', line)
        if m:
            ports.add(int(m.group(1)))
    return ports


def port_free(port):
    if port in ss_listen_ports():
        return False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((HOST, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def pick_port():
    busy = ss_listen_ports()
    for port in range(PORT_LOW, PORT_HIGH + 1):
        if port in busy:
            continue
        if port_free(port):
            return port
    return None


def port_refuses(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)
    try:
        s.connect((HOST, port))
        return False
    except ConnectionRefusedError:
        return True
    except OSError:
        return False
    finally:
        s.close()


def child_env():
    env = {k: os.environ[k] for k in CHILD_ENV_KEYS if k in os.environ}
    env.setdefault('PATH', '/usr/local/bin:/usr/bin:/bin')
    env.setdefault('HOME', str(Path.home()))
    env.setdefault('LANG', 'C.UTF-8')
    return env


def start_server(port, log_path, extra_args):
    argv = [str(SERVER), '-m', str(MODEL), '--host', HOST, '--port', str(port),
            '--no-webui', '--offline', '-v'] + list(extra_args)
    handle = open(log_path, 'wb')
    proc = subprocess.Popen(argv, stdout=handle, stderr=subprocess.STDOUT,
                            env=child_env(), cwd=str(Path.home()),
                            start_new_session=True)
    return proc, handle, argv


def wait_ready(proc, port, timeout=READY_TIMEOUT):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            return False, 'child-exited'
        res = http_get(port, '/health', timeout=5.0)
        if res['status'] == 200:
            return True, None
        time.sleep(0.3)
    return False, 'ready-timeout'


def teardown(proc, handle, port):
    out = {'sigterm_sent': False, 'sigkill_sent': False,
           'child_returncode': None, 'port_refuses_after': None,
           'ss_listen_ports_after': None}
    if proc is not None and proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            out['sigterm_sent'] = True
        except OSError:
            pass
        try:
            out['child_returncode'] = proc.wait(timeout=TERM_GRACE)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
                out['sigkill_sent'] = True
            except OSError:
                pass
            try:
                out['child_returncode'] = proc.wait(timeout=TERM_GRACE)
            except subprocess.TimeoutExpired:
                out['child_returncode'] = 'wait-timeout'
    elif proc is not None:
        out['child_returncode'] = proc.poll()
    time.sleep(0.5)
    out['port_refuses_after'] = port_refuses(port)
    out['ss_listen_ports_after'] = sorted(
        p for p in ss_listen_ports() if PORT_LOW <= p <= PORT_HIGH)
    if handle is not None:
        handle.close()
    return out


def tokenize_prompt(port):
    text = 'The quick brown fox jumps over the lazy dog. '
    deadline = time.monotonic() + 60.0
    while time.monotonic() < deadline:
        res = http_post(port, '/tokenize', {'content': text}, timeout=30.0)
        if res['status'] == 200:
            try:
                doc = json.loads(res['body'].decode('utf-8', 'replace'))
            except ValueError:
                return None
            tokens = doc.get('tokens') if isinstance(doc, dict) else None
            if isinstance(tokens, list) and len(tokens) >= PROMPT_TOKENS:
                return {'tokens': tokens[:PROMPT_TOKENS],
                        'tokenized_total': len(tokens)}
        text = text * 2
        if len(text) > 200000:
            return None
        time.sleep(0.2)
    return None


def completion(port, body):
    t0 = time.monotonic()
    res = http_post(port, '/completion', body, timeout=HTTP_TIMEOUT)
    t1 = time.monotonic()
    rec = {'status': res['status'], 'error': None, 'error_type': None,
           'tokens_predicted': None, 'truncated': None,
           'stopped_limit': None, 'stopped_type': None,
           'content_len': None,
           'elapsed_s': round(t1 - t0, 3), 't_start': t0, 't_end': t1}
    if res['error'] is not None:
        rec['error'] = f'network:{res["error"]}'
        return rec
    body_text = res['body'].decode('utf-8', 'replace')
    try:
        doc = json.loads(body_text)
    except ValueError:
        doc = None
    if res['status'] == 200 and isinstance(doc, dict):
        rec['tokens_predicted'] = doc.get('tokens_predicted')
        rec['truncated'] = doc.get('truncated')
        rec['stopped_limit'] = doc.get('stopped_limit')
        rec['stopped_type'] = doc.get('stopped_type')
        content = doc.get('content')
        rec['content_len'] = len(content) if isinstance(content, str) else None
    else:
        err = doc.get('error') if isinstance(doc, dict) else None
        if isinstance(err, dict):
            rec['error'] = (err.get('message') or err.get('type')
                            or json.dumps(err))[:500]
            rec['error_type'] = err.get('type')
        else:
            rec['error'] = body_text[:500]
    return rec


def parse_log(log_path):
    text = log_path.read_text(errors='replace')
    pools = POOL_RE.findall(text)
    releases = [{'slot': int(a), 'task': int(b), 'n_tokens': int(c),
                 'truncated': int(d)}
                for a, b, c, d in RELEASE_RE.findall(text)]
    init = SLOT_INIT_RE.search(text)
    return {
        'pool_values': [int(p) for p in pools],
        'kv_pool_n_ctx': int(pools[-1]) if pools else None,
        'release_lines': releases,
        'oversize_mentions': len(OVERSIZE_RE.findall(text)),
        'slot_init': ({'n_slots': int(init.group(1)),
                       'n_ctx_slot': int(init.group(2)),
                       'kv_unified': init.group(3)} if init else None),
        'log_bytes': len(text.encode('utf-8')),
        'log_lines': text.count('\n'),
    }


def run_once(label, n_predict, extra_args, raw_dir):
    port = pick_port()
    if port is None:
        return {'label': label, 'n_predict': n_predict, 'ok': False,
                'error': 'no-free-port'}
    log_path = Path(raw_dir) / f'{label}.server.log'
    proc = handle = None
    result = {
        'label': label,
        'n_predict': n_predict,
        'args': list(extra_args),
        'port': port,
        'started_utc': utc_now(),
        'ok': False,
        'error': None,
    }
    try:
        proc, handle, argv = start_server(port, log_path, extra_args)
        result['argv'] = argv
        ready, reason = wait_ready(proc, port)
        result['ready'] = ready
        result['ready_reason'] = reason
        if not ready:
            result['error'] = f'not-ready:{reason}'
            return result
        body = tokenize_prompt(port)
        if body is None:
            result['error'] = 'tokenize-failed'
            return result
        result['prompt_tokens'] = len(body['tokens'])
        result['tokenized_total'] = body['tokenized_total']
        completion_body = {
            'prompt': body['tokens'],
            'n_predict': n_predict,
            'ignore_eos': True,
            'cache_prompt': False,
            'stream': False,
        }
        barrier = threading.Barrier(2)
        out = [None, None]

        def worker(i):
            barrier.wait()
            out[i] = completion(port, completion_body)

        threads = [threading.Thread(target=worker, args=(i,), daemon=True)
                   for i in (0, 1)]
        t0 = time.monotonic()
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=HTTP_TIMEOUT + 60)
        result['wall_s'] = round(time.monotonic() - t0, 3)
        result['requests_alive'] = [t.is_alive() for t in threads]
        reqs = [r for r in out if r is not None]
        reqs.sort(key=lambda r: r['t_start'])
        result['requests'] = reqs
        result['start_gap_ms'] = (round(abs(reqs[0]['t_start'] - reqs[1]['t_start']) * 1000, 3)
                                  if len(reqs) == 2 else None)
        result['overlap'] = (bool(len(reqs) == 2
                                  and reqs[0]['t_start'] < reqs[1]['t_end']
                                  and reqs[1]['t_start'] < reqs[0]['t_end']))
        result['statuses'] = [r['status'] for r in reqs]
        result['ok'] = True
        return result
    finally:
        result['teardown'] = teardown(proc, handle, port)
        result['finished_utc'] = utc_now()
        try:
            result['log'] = parse_log(log_path)
        except OSError as exc:
            result['log'] = {'error': str(exc)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-predict', type=int, required=True)
    ap.add_argument('--label', required=True)
    ap.add_argument('--raw-dir', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--server-arg', action='append', default=[])
    args = ap.parse_args(argv)
    Path(args.raw_dir).mkdir(parents=True, exist_ok=True)
    result = run_once(args.label, args.n_predict, args.server_arg, args.raw_dir)
    out_path = Path(args.out)
    out_path.write_text(json.dumps(result, ensure_ascii=True, indent=2,
                                   sort_keys=True) + '\n')
    print(json.dumps({k: result.get(k) for k in
                      ('label', 'n_predict', 'port', 'statuses', 'start_gap_ms',
                       'overlap', 'error', 'ok')},
                     ensure_ascii=True, sort_keys=True))
    rel = result.get('log', {}).get('release_lines')
    if rel is not None:
        print('release_lines', json.dumps(rel, ensure_ascii=True))
    print('pool', result.get('log', {}).get('kv_pool_n_ctx'),
          'slot_init', result.get('log', {}).get('slot_init'),
          'oversize_mentions', result.get('log', {}).get('oversize_mentions'))
    print('teardown', json.dumps(result.get('teardown', {}), ensure_ascii=True,
                                 sort_keys=True))
    return 0 if result.get('ok') else 2


if __name__ == '__main__':
    sys.exit(main())
