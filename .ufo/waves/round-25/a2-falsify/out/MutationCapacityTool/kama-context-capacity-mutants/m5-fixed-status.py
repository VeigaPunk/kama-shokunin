#!/usr/bin/env python3
"""kama-context-capacity.py — round-25 C2 capability tool (attempt 2).

Runs every registered context-capacity cell of preregistration amendment 2
(K1-K8, X1-X3, L1-L3) against the lane-owned llama-server fixture (b11755,
stories260K.gguf) and writes a receipt that .ufo/waves/round-25/count-c2.py
accepts.

Per cell:
  - one llama-server child at a time on 127.0.0.1 inside the assigned port
    range, launched with the amendment-2 rule (the `-v` flag is added and is
    not part of the registered args string), killed with the port proven
    closed before the next cell starts;
  - the raw bytes of /health, /props, /slots and /v1/models plus the full
    server log are written to files; each file's sha256 is recorded in the
    receipt;
  - the receipt records props_n_ctx, total_slots, slots_n_ctx,
    models_n_ctx_train, kv_pool_n_ctx (from the `llama_context: n_ctx = N`
    log line) and log_lines (every line matching n_ctx, kv_unified, n_seq,
    capping, rounding, KV pool sizing or llama_kv_cache: size);
  - load cells (L1-L3) additionally tokenize a 1000-token prompt via
    /tokenize and send the token ids to /completion (n_predict 600,
    ignore_eos true, cache_prompt false), recording request_mode, per-request
    status, prompt_tokens, n_predict, tokens_predicted and error text.
    Concurrent mode starts both requests within 50 ms using a barrier.

Port safety and readiness reuse tools/kama-llamacpp-live.py (refused-port
set, picker, listener ownership).

Exit codes:
    0  every selected cell produced an observed record
    1  at least one cell was not observed (server/setup failure)
    2  setup error (bad arguments, missing fixture, cells drift)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shlex
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = 'kama-context-capacity/v1'
SCRIPT = Path(__file__).resolve()
HOST = '127.0.0.1'
DEFAULT_SERVER = Path.home() / '.local/bin/llama-server'
DEFAULT_MODEL = Path.home() / '.cache/kama-shokunin/models/stories260K.gguf'
DEFAULT_PORT_RANGE = (47400, 47419)
DEFAULT_SCRATCH = Path('/fast/scratch/hyaku/kama-context-capacity')
MODEL_SHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
SERVER_VERSION_MARK = 'build 11755'
CHILD_ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')
TERM_GRACE = 10.0
READY_POLL = 0.5
HTTP_BODY_CAP = 65536
LOAD_PROMPT_TOKENS = 1000
LOAD_N_PREDICT = 600
CONCURRENT_WINDOW_S = 0.050

# Registered cells, byte-for-byte the CELLS map of count-c2.py (amendment 2).
CELLS = (
    {'id': 'K1', 'args': '-c 0', 'kind': 'config'},
    {'id': 'K2', 'args': '-c 2048 -np 2 --no-kv-unified', 'kind': 'config'},
    {'id': 'K3', 'args': '-c 2048 -np 2 --kv-unified', 'kind': 'config'},
    {'id': 'K4', 'args': '-c 1024 -np 1', 'kind': 'config'},
    {'id': 'K5', 'args': '-c 4096 -np 1', 'kind': 'config'},
    {'id': 'K6', 'args': '-c 1000 -np 3 --no-kv-unified', 'kind': 'config'},
    {'id': 'K7', 'args': '-np 2 --kv-unified-per-slot 512', 'kind': 'config'},
    {'id': 'K8', 'args': '-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512',
     'kind': 'config'},
    {'id': 'X1', 'args': '-np 4 --no-kv-unified', 'kind': 'config'},
    {'id': 'X2', 'args': '-c 8192 -np 4 --no-kv-unified', 'kind': 'config'},
    {'id': 'X3', 'args': '-np 4 --no-kv-unified --fit off', 'kind': 'config'},
    {'id': 'L1', 'args': '-c 0', 'kind': 'load-concurrent'},
    {'id': 'L2', 'args': '-c 8192 -np 4 --no-kv-unified',
     'kind': 'load-concurrent'},
    {'id': 'L3', 'args': '-c 0', 'kind': 'load-sequential'},
)

# The claim-named log-line set: n_ctx | kv_unified | n_seq | capping |
# rounding | KV pool sizing | llama_kv_cache: size.
LOG_KEEP = re.compile(
    r'n_ctx|kv_unified|n_seq|capping|rounding|KV pool|llama_kv_cache: size',
    re.IGNORECASE)
KV_POOL_RE = re.compile(r'llama_context: n_ctx\s*=\s*(\d+)')

_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace(
        '+00:00', 'Z')


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def _get_json(live, port, path):
    result = live.http_get(port, path, timeout=10.0)
    if result.get('status') != 200:
        return None
    try:
        return json.loads(result.get('body') or '')
    except (ValueError, TypeError):
        return None


def http_post(port, path, body, timeout=60.0):
    """One loopback POST. Same result shape as the live harness http_get."""
    url = f'http://{HOST}:{port}{path}'
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'),
                                 method='POST',
                                 headers={'Content-Type': 'application/json'})
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            return {'status': resp.status, 'error': None,
                    'headers': dict(resp.headers.items()),
                    'body': resp.read(HTTP_BODY_CAP + 1),
                    'body_truncated': False}
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read(HTTP_BODY_CAP + 1)
        except OSError:
            raw = b''
        return {'status': exc.code, 'error': None,
                'headers': dict(exc.headers.items()) if exc.headers else {},
                'body': raw, 'body_truncated': False}
    except urllib.error.URLError as exc:
        reason = getattr(exc, 'reason', exc)
        return {'status': None, 'error': type(reason).__name__,
                'headers': {}, 'body': b'', 'body_truncated': False}
    except (OSError, socket.timeout, TimeoutError) as exc:
        return {'status': None, 'error': type(exc).__name__,
                'headers': {}, 'body': b'', 'body_truncated': False}


def extract_log_lines(text):
    """All lines matching the claim-named log-line set, verbatim."""
    return [ln for ln in text.splitlines() if LOG_KEEP.search(ln)]


def extract_kv_pool(text):
    """All `llama_context: n_ctx = N` values in order; the last one is the
    final serving pool (fit may build earlier measurement contexts with the
    unset defaults)."""
    return [int(m.group(1)) for m in KV_POOL_RE.finditer(text)]


# ---------------------------------------------------------------------------
# Port safety (reused from tools/kama-llamacpp-live.py).
# ---------------------------------------------------------------------------

def find_repo_root():
    for parent in SCRIPT.parents:
        if (parent / 'registry' / 'endpoint-consumers.tsv').is_file():
            return parent
    return SCRIPT.parent


def locate_live_module():
    repo_root = find_repo_root()
    path = repo_root / 'tools' / 'kama-llamacpp-live.py'
    return path if path.is_file() else None


def load_live_module(path):
    spec = importlib.util.spec_from_file_location('kama_llamacpp_live', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pick_free_port(live, refused, low, high, used):
    for port in range(low, high + 1):
        if port in used:
            continue
        try:
            chosen = live.pick_port(refused, port)
        except Exception:
            continue
        if chosen == port:
            return port
    return None


def ss_listen_lines(port):
    try:
        proc = subprocess.run(['ss', '-ltn'], capture_output=True, text=True,
                              timeout=20)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f'ss-failed:{type(exc).__name__}'
    needle = f':{port} '
    hits = [ln for ln in proc.stdout.splitlines() if needle in ln]
    return hits, None


def live_llama_server_pids():
    try:
        proc = subprocess.run(['pgrep', '-x', 'llama-server'],
                              capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    pids = []
    for token in proc.stdout.split():
        try:
            pid = int(token)
        except ValueError:
            continue
        try:
            stat = Path(f'/proc/{pid}/stat').read_text()
            fields = stat.rsplit(')', 1)[1].split()
            if fields[0] == 'Z':
                continue
        except (OSError, IndexError):
            continue
        pids.append(pid)
    return pids


def wait_for_host_idle(timeout):
    """Best effort: wait up to `timeout` for no other llama-server child.
    Returns (ok, waited_seconds, observed_pids); ok is True when idle or
    unknown, False only when another child survived the whole wait."""
    t0 = time.monotonic()
    seen = []
    deadline = t0 + timeout
    while True:
        pids = live_llama_server_pids()
        if pids is None:
            return True, round(time.monotonic() - t0, 3), seen
        if not pids:
            return True, round(time.monotonic() - t0, 3), seen
        for pid in pids:
            if pid not in seen:
                seen.append(pid)
        if time.monotonic() >= deadline:
            return False, round(time.monotonic() - t0, 3), seen
        time.sleep(2.0)


# ---------------------------------------------------------------------------
# One cell.
# ---------------------------------------------------------------------------

def run_cell(cell, cfg, live, refused, port, raw_dir):
    record = {
        'id': cell['id'],
        'port': port,
        'args': cell['args'],
        'argv': None,
        'props_n_ctx': None,
        'total_slots': None,
        'slots_n_ctx': [],
        'models_n_ctx_train': None,
        'kv_pool_n_ctx': None,
        'kv_pool_candidates': [],
        'log_lines': [],
        'raw': {},
        'request_mode': None,
        'requests': [],
        'concurrency_delta_s': None,
        'server_sha256': cfg['server_sha256'],
        'model_sha256': cfg['model_sha256'],
        'started_utc': None,
        'stopped_utc': None,
        'observed': False,
        'teardown': None,
        'error': None,
    }

    argv = [
        cfg['server_real'], '-m', cfg['model_real'],
        '--host', HOST, '--port', str(port),
        '--no-webui', '--offline', '-v',
    ] + shlex.split(cell['args'])
    record['argv'] = argv

    log_path = Path(cfg['scratch']) / f"server-{cell['id']}-port{port}.log"
    child_env = {key: os.environ[key] for key in CHILD_ENV_KEYS
                 if key in os.environ}

    proc = None
    log_file = None
    try:
        log_file = open(log_path, 'wb')
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL,
                                stdout=log_file,
                                stderr=subprocess.STDOUT,
                                start_new_session=True,
                                env=child_env)
    except OSError as exc:
        record['error'] = f'launch-failed:{type(exc).__name__}'
        if log_file is not None:
            log_file.close()
        return record
    finally:
        if log_file is not None:
            try:
                log_file.close()
            except OSError:
                pass

    record['started_utc'] = _utc_now()
    try:
        # Readiness: /props 200, then prove our child owns the listener.
        ready = False
        deadline = time.monotonic() + cfg['ready_timeout']
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                record['error'] = f'server-exited-early-rc{proc.returncode}'
                break
            result = live.http_get(port, '/props', timeout=5.0)
            if result.get('status') == 200:
                ready = True
                break
            time.sleep(READY_POLL)
        if not ready and record['error'] is None:
            record['error'] = 'ready-timeout'
        if ready:
            err, owned = live.verify_live(proc, port, 'ready')
            if err is not None:
                record['error'] = err
                ready = False
        if ready:
            _capture_raw(live, record, raw_dir, cell['id'], port)
            props = _get_json(live, port, '/props')
            slots = _get_json(live, port, '/slots')
            models = _get_json(live, port, '/v1/models')
            if isinstance(props, dict):
                dgs = props.get('default_generation_settings')
                if isinstance(dgs, dict):
                    record['props_n_ctx'] = dgs.get('n_ctx')
                record['total_slots'] = props.get('total_slots')
            if isinstance(slots, list):
                record['slots_n_ctx'] = [
                    e.get('n_ctx') for e in slots
                    if isinstance(e, dict) and isinstance(e.get('n_ctx'), int)]
            if isinstance(models, dict):
                data = models.get('data')
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    meta = data[0].get('meta')
                    if isinstance(meta, dict):
                        record['models_n_ctx_train'] = meta.get('n_ctx_train')
            if cell['kind'].startswith('load'):
                record['request_mode'] = (
                    'concurrent' if cell['kind'] == 'load-concurrent'
                    else 'sequential')
                ok, reqs, delta = _run_load_requests(port, cell['kind'],
                                                      cfg)
                record['requests'] = reqs
                record['concurrency_delta_s'] = delta
                if not ok:
                    record['error'] = record['error'] or 'load-request-failed'
    finally:
        record['stopped_utc'] = _utc_now()
        record['teardown'] = _teardown(proc, port)

    try:
        text = log_path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        text = ''
    record['log_lines'] = extract_log_lines(text)
    pool_candidates = extract_kv_pool(text)
    record['kv_pool_candidates'] = pool_candidates
    record['kv_pool_n_ctx'] = pool_candidates[-1] if pool_candidates else None
    try:
        raw_log = log_path.read_bytes()
    except OSError:
        raw_log = b''
    if raw_log:
        raw_log_path = raw_dir / f"{cell['id']}.server.log"
        raw_log_path.write_bytes(raw_log)
        record['raw']['server_log'] = _sha256_bytes(raw_log)

    record['observed'] = bool(
        record['error'] is None
        # a cell whose child was not reaped or whose port did not close is
        # never an observation (round-25 sentinel finding)
        and record['teardown'].get('child_returncode') is not None
        and record['teardown'].get('port_closed') is True
        and isinstance(record['props_n_ctx'], int)
        and isinstance(record['total_slots'], int)
        and record['slots_n_ctx']
        and isinstance(record['models_n_ctx_train'], int)
        and isinstance(record['kv_pool_n_ctx'], int)
        and record['log_lines'])
    if cell['kind'].startswith('load'):
        record['observed'] = bool(
            record['observed']
            and record['request_mode'] is not None
            and len(record['requests']) >= 2
            and all(isinstance(q.get('status'), int)
                    and q.get('prompt_tokens') == LOAD_PROMPT_TOKENS
                    and q.get('n_predict') == LOAD_N_PREDICT
                    for q in record['requests']))
    return record


def _capture_raw(live, record, raw_dir, cell_id, port):
    for name, path in (('health', '/health'), ('props', '/props'),
                       ('slots', '/slots'), ('models', '/v1/models')):
        result = live.http_get(port, path, timeout=10.0)
        body = result.get('body') or b''
        raw_path = raw_dir / f'{cell_id}.{name}.body'
        raw_path.write_bytes(body)
        record['raw'][f'raw_{name}'] = _sha256_bytes(body)


def _run_load_requests(port, kind, cfg):
    """Tokenize a 1000-token prompt and run two /completion requests.

    Returns (ok, requests, delta_s). `requests` is ordered by start time.
    Concurrent mode starts both requests behind a barrier; delta_s is the
    absolute start-time gap (must be <= 50 ms, else ok is False)."""
    body = _tokenize_prompt(port, cfg)
    if body is None:
        return False, [{'status': None, 'error': 'tokenize-failed',
                         'prompt_tokens': LOAD_PROMPT_TOKENS,
                         'n_predict': LOAD_N_PREDICT,
                         'tokens_predicted': None}], None
    completion_body = {
        'prompt': body['tokens'],
        'n_predict': LOAD_N_PREDICT,
        'ignore_eos': True,
        'cache_prompt': False,
        'stream': False,
    }

    def one_request():
        ts = time.monotonic()
        return ts, _completion(port, completion_body)

    if kind == 'load-sequential':
        reqs = [one_request(), one_request()]
        reqs.sort(key=lambda q: q[0])
        return True, [r for _, r in reqs], None

    # concurrent: both start within 50 ms
    barrier = threading.Barrier(2)
    out = [None, None]

    def worker(i):
        barrier.wait()
        out[i] = one_request()

    threads = [threading.Thread(target=worker, args=(i,), daemon=True)
               for i in (0, 1)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=360)
    alive = [t.is_alive() for t in threads]
    if any(alive):
        # teardown (kill) will end any hung request; rejoin briefly later
        return False, [{'status': None, 'error': 'request-timeout',
                         'prompt_tokens': LOAD_PROMPT_TOKENS,
                         'n_predict': LOAD_N_PREDICT,
                         'tokens_predicted': None}], None
    reqs = [out[0], out[1]]
    reqs.sort(key=lambda q: q[0])
    delta = abs(out[0][0] - out[1][0])
    if delta > CONCURRENT_WINDOW_S:
        return False, [r for _, r in reqs], round(delta, 4)
    return True, [r for _, r in reqs], round(delta, 4)


def _tokenize_prompt(port, cfg):
    """POST /tokenize until the text yields >= 1000 tokens; return the first
    1000 token ids. Applies no special tokens (default add_special false)."""
    text = 'The quick brown fox jumps over the lazy dog. '
    deadline = time.monotonic() + cfg['ready_timeout']
    while time.monotonic() < deadline:
        res = http_post(port, '/tokenize', {'content': text}, timeout=30.0)
        if res.get('status') != 200:
            text = text * 2
            if len(text) > 200000:
                return None
            continue
        try:
            doc = json.loads(res.get('body') or '')
        except (ValueError, TypeError):
            return None
        tokens = doc.get('tokens') if isinstance(doc, dict) else None
        if isinstance(tokens, list) and len(tokens) >= LOAD_PROMPT_TOKENS:
            return {'tokens': tokens[:LOAD_PROMPT_TOKENS],
                    'tokenized_total': len(tokens)}
        text = text * 2
        if len(text) > 200000:
            return None
    return None


def _completion(port, body):
    """One POST /completion. Returns the request record.

    t_start/t_end are time.monotonic() seconds of this process, so the two
    requests of one load cell can be checked for overlap."""
    t0 = time.monotonic()
    res = http_post(port, '/completion', body, timeout=360.0)
    t1 = time.monotonic()
    record = {
        'status': 200,
        'error': None,
        'error_type': None,
        'prompt_tokens': LOAD_PROMPT_TOKENS,
        'n_predict': LOAD_N_PREDICT,
        'tokens_predicted': None,
        'truncated': None,
        'elapsed_s': round(t1 - t0, 3),
        't_start': t0,
        't_end': t1,
    }
    if res.get('error') is not None:
        record['error'] = f'network:{res["error"]}'
        return record
    try:
        doc = json.loads(res.get('body') or '')
    except (ValueError, TypeError):
        doc = None
    if res.get('status') == 200 and isinstance(doc, dict):
        record['tokens_predicted'] = doc.get('tokens_predicted')
        record['truncated'] = doc.get('truncated')
    else:
        err = doc.get('error') if isinstance(doc, dict) else None
        if isinstance(err, dict):
            record['error'] = (err.get('message') or err.get('type')
                               or json.dumps(err))
            record['error_type'] = err.get('type')
        else:
            record['error'] = (res.get('body') or b'').decode(
                'utf-8', errors='replace')[:500]
    return record


def _teardown(proc, port):
    """Kill the child process group and prove the port is closed."""
    out = {'sigterm_sent': False, 'sigkill_sent': False,
           'child_returncode': None, 'port_closed': False,
           'ss_listen_lines_after': None, 'error': None}
    if proc is None:
        out['error'] = 'no-child'
        return out
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        out['sigterm_sent'] = True
    except (ProcessLookupError, PermissionError, OSError) as exc:
        out['error'] = f'sigterm:{type(exc).__name__}'
    try:
        out['child_returncode'] = proc.wait(timeout=TERM_GRACE)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
            out['sigkill_sent'] = True
        except (ProcessLookupError, PermissionError, OSError) as exc:
            out['error'] = (out['error'] or '') + f'sigkill:{type(exc).__name__}'
        try:
            out['child_returncode'] = proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            out['error'] = (out['error'] or '') + 'wait-timeout'
    deadline = time.monotonic() + 10.0
    closed = False
    while time.monotonic() < deadline:
        try:
            socket.create_connection((HOST, port), timeout=1.0).close()
        except ConnectionRefusedError:
            closed = True
            break
        except OSError:
            pass
        time.sleep(0.5)
    out['port_closed'] = closed
    hits, err = ss_listen_lines(port)
    out['ss_listen_lines_after'] = hits if hits is not None else err
    return out


# ---------------------------------------------------------------------------
# Drift check against the registered counter (count-c2.py).
# ---------------------------------------------------------------------------

def load_counter_cells(repo_root):
    """CELLS from count-c2.py, imported read-only, or (None, reason)."""
    path = repo_root / '.ufo' / 'waves' / 'round-25' / 'count-c2.py'
    if not path.is_file():
        return None, f'counter-not-found:{path}'
    try:
        spec = importlib.util.spec_from_file_location('kama_count_c2', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        return None, f'counter-import-failed:{type(exc).__name__}:{exc}'
    cells = getattr(module, 'CELLS', None)
    if not isinstance(cells, dict):
        return None, 'counter-CELLS-not-dict'
    return cells, None


def check_cells_drift(embedded, counter):
    problems = []
    if counter is None:
        return ['counter cells unavailable']
    for cell in embedded:
        other = counter.get(cell['id'])
        if other is None:
            problems.append(f"{cell['id']}: absent from count-c2.py CELLS")
            continue
        if other[0] != cell['args']:
            problems.append(f"{cell['id']}: args differ from count-c2.py")
        if other[1] != cell['kind']:
            problems.append(f"{cell['id']}: kind differs from count-c2.py")
    for cid in counter:
        if cid not in {c['id'] for c in embedded}:
            problems.append(f'{cid}: registered in count-c2.py, not implemented')
    return problems


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------

def _port_range_arg(text):
    if not re.fullmatch(r'\s*\d{1,5}\s*-\s*\d{1,5}\s*', text or ''):
        raise argparse.ArgumentTypeError(f'bad port range: {text!r}')
    return text


def build_parser():
    parser = argparse.ArgumentParser(
        prog='kama-context-capacity.py',
        description='Run the registered round-25 C2 context-capacity cells '
                    '(K1-K8, X1-X3, L1-L3) against the lane-owned llama-server '
                    'fixture and write a receipt count-c2.py accepts.')
    parser.add_argument('--server', default=str(DEFAULT_SERVER),
                        help='llama-server binary (default: %(default)s)')
    parser.add_argument('--model', default=str(DEFAULT_MODEL),
                        help='GGUF model (default: %(default)s)')
    parser.add_argument('--out', default=None,
                        help='receipt JSON path (default: stdout only)')
    parser.add_argument('--port-range', default='47400-47419',
                        type=_port_range_arg,
                        help='inclusive loopback port range to serve on '
                             '(default: %(default)s)')
    parser.add_argument('--scratch', default=str(DEFAULT_SCRATCH),
                        help='directory for per-cell temp server logs '
                             '(default: %(default)s)')
    parser.add_argument('--ready-timeout', type=float, default=180.0,
                        help='seconds to wait for the server to serve '
                             '/props (default: %(default)s)')
    parser.add_argument('--host-idle-timeout', type=float, default=120.0,
                        help='seconds to wait for no other llama-server child '
                             'before a cell (default: %(default)s)')
    parser.add_argument('--only', default=None,
                        help='comma-separated cell ids to run (default: all)')
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        m = re.fullmatch(r'\s*(\d{1,5})\s*-\s*(\d{1,5})\s*', args.port_range)
        low, high = int(m.group(1)), int(m.group(2))
        if not (1 <= low <= high <= 65535):
            raise ValueError
    except (AttributeError, ValueError):
        parser.error(f'bad port range: {args.port_range!r}')
        return 2

    receipt = {
        'schema': SCHEMA,
        'started_utc': None,
        'ended_utc': None,
        'tool': {'path': str(SCRIPT), 'sha256': None},
        'host': HOST,
        'port_range': [low, high],
        'server_version': None,
        'server': {'arg': None, 'realpath': None, 'sha256': None},
        'model_sha256': None,
        'model': {'arg': None, 'realpath': None, 'size_bytes': None},
        'cells_drift': None,
        'port_refusal_set': [],
        'cells': [],
        'summary': {},
        'exit_code': 2,
        'error': None,
    }

    class SetupError(Exception):
        pass

    try:
        receipt['started_utc'] = _utc_now()
        receipt['tool']['sha256'] = _sha256_file(SCRIPT)

        repo_root = find_repo_root()
        counter_cells, counter_reason = load_counter_cells(repo_root)
        if counter_cells is None:
            raise SetupError(f'counter-unavailable:{counter_reason}')
        problems = check_cells_drift(CELLS, counter_cells)
        receipt['cells_drift'] = problems
        if problems:
            raise SetupError('cells-drift:' + ';'.join(problems))

        live_path = locate_live_module()
        if live_path is None:
            raise SetupError('kama-llamacpp-live.py-not-found')
        live = load_live_module(live_path)
        receipt['port_safety_module'] = str(live_path)

        server_arg = Path(args.server)
        if not server_arg.is_file():
            raise SetupError(f'server-not-found:{args.server}')
        server_real = os.path.realpath(server_arg)
        model_arg = Path(args.model)
        if not model_arg.is_file():
            raise SetupError(f'model-not-found:{args.model}')
        model_real = os.path.realpath(model_arg)
        receipt['server'].update({'arg': str(server_arg),
                                  'realpath': server_real,
                                  'sha256': _sha256_file(server_real)})
        receipt['model'].update({'arg': str(model_arg),
                                 'realpath': model_real,
                                 'size_bytes': Path(model_real).stat().st_size})
        try:
            ver = subprocess.run([server_real, '--version'],
                                 capture_output=True, text=True, timeout=60)
            receipt['server_version'] = ver.stdout.strip() or \
                ver.stderr.strip()
        except (OSError, subprocess.SubprocessError) as exc:
            raise SetupError(f'server-version-failed:{type(exc).__name__}')
        if SERVER_VERSION_MARK not in (receipt['server_version'] or ''):
            raise SetupError('server-version-mismatch:'
                             + str(receipt['server_version']))
        receipt['model_sha256'] = _sha256_file(model_real)
        if receipt['model_sha256'] != MODEL_SHA:
            raise SetupError('model-sha256-mismatch:'
                             + receipt['model_sha256'])

        refused = live.refused_ports()
        receipt['port_refusal_set'] = sorted(refused)
        for hard in (8080, 34113):
            if hard not in refused:
                raise SetupError(f'hard-pin-missing:{hard}')

        scratch = Path(args.scratch)
        scratch.mkdir(parents=True, exist_ok=True)
        raw_dir = None
        if args.out:
            raw_dir = Path(args.out).parent / 'raw'
        else:
            raw_dir = scratch / 'raw'
        raw_dir.mkdir(parents=True, exist_ok=True)

        cfg = {'server_real': server_real, 'model_real': model_real,
               'server_sha256': receipt['server']['sha256'],
               'model_sha256': receipt['model_sha256'],
               'scratch': str(scratch),
               'ready_timeout': args.ready_timeout}

        selected = list(CELLS)
        if args.only:
            wanted = {x.strip() for x in args.only.split(',') if x.strip()}
            selected = [c for c in CELLS if c['id'] in wanted]
            if not selected:
                raise SetupError('no-cells-selected')

        used_ports = []
        for cell in selected:
            idle_ok, waited, seen = wait_for_host_idle(args.host_idle_timeout)
            receipt['host_idle'] = {'ok': idle_ok, 'waited_s': waited,
                                    'other_pids_seen': seen,
                                    'cell': cell['id']}
            if not idle_ok:
                raise SetupError(f'host-not-idle-before-{cell["id"]}')
            port = pick_free_port(live, refused, low, high, used_ports)
            if port is None:
                raise SetupError(f'no-free-port-in-range-for-{cell["id"]}')
            used_ports.append(port)
            hits, err = ss_listen_lines(port)
            if hits is None:
                raise SetupError(f'ss-check-failed:{err}')
            if hits:
                raise SetupError(f'port-not-free:{port}')
            record = run_cell(cell, cfg, live, refused, port, raw_dir)
            receipt['cells'].append(record)

        observed = [c for c in receipt['cells'] if c.get('observed')]
        receipt['summary'] = {
            'cells': len(receipt['cells']),
            'observed': len(observed),
            'ports_used': used_ports,
            'all_ports_closed': all(
                c.get('teardown', {}).get('port_closed')
                for c in receipt['cells']),
        }
        receipt['exit_code'] = 0 if (
            len(observed) == len(receipt['cells'])
            and all(c.get('teardown', {}).get('port_closed')
                    for c in receipt['cells'])) else 1
    except SetupError as exc:
        receipt['error'] = str(exc)
        receipt['exit_code'] = 2
    except BaseException as exc:
        receipt['error'] = f'internal:{type(exc).__name__}:{exc}'
        receipt['exit_code'] = 2
    finally:
        observed_cells = [c for c in receipt['cells'] if c.get('observed')]
        receipt['summary'] = {
            'cells': len(receipt['cells']),
            'observed': len(observed_cells),
            'ports_used': [c.get('port') for c in receipt['cells']],
            'all_ports_closed': all(
                c.get('teardown', {}).get('port_closed')
                for c in receipt['cells']),
        }
        receipt['ended_utc'] = _utc_now()

    text = json.dumps(receipt, ensure_ascii=True, indent=2, sort_keys=True)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + '\n', encoding='utf-8')
    sys.stdout.write(json.dumps(receipt['summary'], sort_keys=True) + '\n')
    if receipt.get('error'):
        sys.stderr.write(f'kama-context-capacity: {receipt["error"]}\n')
    return receipt['exit_code']


if __name__ == '__main__':
    sys.exit(main())
