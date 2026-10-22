#!/usr/bin/env python3
"""ReviewerCapacityTool harness (round 25, attempt 2, wave 2 falsify).

Target: tools/kama-context-capacity.py at fa3b62ae6475d111eb466d79af616aeebb08bbb9,
loaded from the scratch clone checked out at that commit.

No llama-server child is started and no listening socket is opened. Every cell's
child is a FakeChild that writes committed log bytes; HTTP goes to stubs; os.killpg
is recorded, never sent. The only socket activity is the tool's own teardown
connect probe to unused loopback ports (PORT_BASE..PORT_BASE+27).

Writes results.json beside this file. Scratch work lives under harness-work/.
"""
import contextlib
import http.client
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

CLONE = Path('/fast/scratch/hyaku/kama-r25a2w2/ReviewerCapacityTool/clone')
TOOL = CLONE / 'tools' / 'kama-context-capacity.py'
COUNTER = CLONE / '.ufo' / 'waves' / 'round-25' / 'count-c2.py'
FINAL = CLONE / '.ufo' / 'waves' / 'round-25' / 'final'
RAWC = FINAL / 'raw'
WORK = Path('/fast/scratch/hyaku/kama-r25a2w2/ReviewerCapacityTool/harness-work')
OUT = Path(__file__).resolve().parent
PORT_BASE = 47420
OK_BODY = (b'{"content": "x", "tokens_predicted": 600, "truncated": false, '
           b'"tokens_evaluated": 1000}')
ERR_BODY = (b'{"error": {"code": 500, "message": "Context size has been exceeded.", '
            b'"type": "server_error"}}')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kct = load('kct_clone', TOOL)
c2 = load('c2_clone', COUNTER)
REAL = {k: getattr(kct, k) for k in ('subprocess', 'os', 'http_post', '_completion', '_OPENER')}
REC = json.loads((FINAL / 'context-capacity-receipt.json').read_text(encoding='utf-8'))
RCELL = {c['id']: c for c in REC['cells']}
CELLDEF = {c['id']: c for c in kct.CELLS}
KILLPG = []
CHILDREN = []


class OsProxy:
    def __getattr__(self, name):
        return getattr(os, name)

    def killpg(self, pgid, sig):
        KILLPG.append((pgid, int(sig)))


class FakeChild:
    LOG = b''
    RC = 0

    def __init__(self, argv, stdin=None, stdout=None, stderr=None,
                 start_new_session=None, env=None):
        self.argv = list(argv)
        self.pid = 3900000 + len(CHILDREN)
        self.returncode = None
        CHILDREN.append(self)
        if stdout is not None:
            stdout.write(FakeChild.LOG)

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        if self.returncode is None:
            self.returncode = FakeChild.RC
        return self.returncode


class SubprocessProxy:
    def __init__(self, popen_impl=None):
        self._popen = popen_impl or FakeChild

    def __getattr__(self, name):
        return getattr(subprocess, name)

    def Popen(self, *args, **kwargs):
        return self._popen(*args, **kwargs)


class FakeLive:
    def __init__(self, routes):
        self.routes = routes

    def http_get(self, port, path, timeout=None):
        status, body = self.routes.get(path, (404, b'not found'))
        return {'status': status, 'error': None, 'headers': {}, 'body': body,
                'body_truncated': False}

    def verify_live(self, proc, port, label):
        return None, 'child'


class FakeResp:
    def __init__(self, data=b'', raise_on_read=None):
        self._data = data
        self._raise = raise_on_read
        self.status = 200
        self.headers = {}

    def read(self, n=-1):
        if self._raise is not None:
            raise self._raise
        if n is None or n < 0:
            out, self._data = self._data, b''
        else:
            out, self._data = self._data[:n], self._data[n:]
        return out

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeOpener:
    def __init__(self, make):
        self._make = make

    def open(self, req, timeout=None):
        return self._make()


def routes_for(cid):
    def rd(name):
        return (RAWC / f'{cid}.{name}.body').read_bytes()
    return {'/health': (200, rd('health')), '/props': (200, rd('props')),
            '/slots': (200, rd('slots')), '/v1/models': (200, rd('models'))}


def fake_post(status, body, sleep_s=0.05):
    def post(port, path, payload, timeout=60.0):
        if path == '/tokenize':
            return {'status': 200, 'error': None, 'headers': {},
                    'body': json.dumps({'tokens': list(range(1, 1201))}).encode(),
                    'body_truncated': False}
        if path == '/completion':
            time.sleep(sleep_s)
            return {'status': status, 'error': None, 'headers': {}, 'body': body,
                    'body_truncated': False}
        raise AssertionError(f'unexpected path {path}')
    return post


def default_post(cid):
    if cid == 'L1':
        return fake_post(500, ERR_BODY)
    return fake_post(200, OK_BODY)


def restore():
    for key, value in REAL.items():
        setattr(kct, key, value)


def run_cell(cid, *, routes=None, log=None, post=None, completion=None, popen=None):
    restore()
    rc = RCELL[cid]
    FakeChild.LOG = log if log is not None else (RAWC / f'{cid}.server.log').read_bytes()
    CHILDREN.clear()
    KILLPG.clear()
    kct.subprocess = SubprocessProxy(popen)
    kct.os = OsProxy()
    kct.http_post = post if post is not None else default_post(cid)
    if completion is not None:
        kct._completion = completion
    scratch = WORK / 'scratch'
    raw_dir = WORK / 'raw'
    scratch.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    cfg = {'server_real': rc['argv'][0], 'model_real': rc['argv'][2],
           'server_sha256': REC['server']['sha256'],
           'model_sha256': REC['model_sha256'],
           'scratch': str(scratch), 'ready_timeout': 5.0}
    live = FakeLive(routes if routes is not None else routes_for(cid))
    try:
        rec = kct.run_cell(CELLDEF[cid], cfg, live, set(), PORT_BASE, raw_dir)
        killed = list(KILLPG)
    finally:
        restore()
    return rec, killed


def normalized_argv(argv):
    out = list(argv)
    if '--port' in out:
        out[out.index('--port') + 1] = 'PORT'
    return out


def verdict(rec):
    args, kind = c2.CELLS[rec['id']]
    return {'tool_observed': rec['observed'],
            'counter_accepts': bool(rec['args'] == args and c2.cell_ok(rec, kind))}


COMPARE = ['args', 'props_n_ctx', 'total_slots', 'slots_n_ctx', 'models_n_ctx_train',
           'kv_pool_n_ctx', 'kv_pool_candidates', 'log_lines', 'raw']


def replay_one(cid):
    rec, killed = run_cell(cid)
    ref = RCELL[cid]
    diffs = [k for k in COMPARE if rec[k] != ref[k]]
    if normalized_argv(rec['argv']) != normalized_argv(ref['argv']):
        diffs.append('argv')
    if [q.get('status') for q in rec['requests']] != [q.get('status') for q in ref['requests']]:
        diffs.append('request_statuses')
    out = {'id': cid, 'diffs': diffs, 'receipt_observed': ref['observed']}
    out.update(verdict(rec))
    out.update({'error': rec['error'], 'port_closed': rec['teardown'].get('port_closed'),
                'child_returncode': rec['teardown'].get('child_returncode'),
                'killpg_calls': killed})
    return out


_SEQ = []
_SEQ_LOCK = threading.Lock()


def nonoverlap_completion(port, body):
    with _SEQ_LOCK:
        t0, t1 = _SEQ.pop(0)
    return {'status': 200, 'error': None, 'error_type': None,
            'prompt_tokens': 1000, 'n_predict': 600, 'tokens_predicted': 600,
            'truncated': False, 'elapsed_s': 1.0, 't_start': t0, 't_end': t1}


def k1_routes_with(overrides):
    routes = routes_for('K1')
    for path, body in overrides.items():
        routes[path] = (200, body)
    return routes


def trailing_last_pool(text):
    lines = text.split('\n')
    hits = [i for i, ln in enumerate(lines)
            if re.search(r'llama_context: n_ctx\s*=\s*\d+\s*$', ln)]
    lines[hits[-1]] += ' (serving)'
    return '\n'.join(lines)


def drop_slot_line(text):
    return '\n'.join(ln for ln in text.split('\n') if 'n_slots = ' not in ln)


def summarize(name, rec):
    v = verdict(rec)
    return {'variant': name, 'id': rec['id'], 'tool_observed': v['tool_observed'],
            'counter_accepts': v['counter_accepts'], 'error': rec['error'],
            'total_slots': rec['total_slots'], 'slots_n_ctx': rec['slots_n_ctx'],
            'kv_pool_n_ctx': rec['kv_pool_n_ctx'],
            'requests': [{k: q.get(k) for k in ('status', 'error', 'prompt_tokens',
                                                'n_predict', 'tokens_predicted',
                                                'truncated')}
                         for q in rec['requests']]}


def variants():
    out = []
    slots3 = json.dumps([{'id': i, 'n_ctx': 2048} for i in range(3)]).encode()
    rec, _ = run_cell('K1', routes=k1_routes_with({'/slots': slots3}))
    out.append(summarize('V1 /slots has 3 entries, /props total_slots 4', rec))
    slots_missing = json.dumps([{'id': 0, 'n_ctx': 2048}, {'id': 1, 'n_ctx': 2048},
                                {'id': 2, 'n_ctx': 2048}, {'id': 3}]).encode()
    rec, _ = run_cell('K1', routes=k1_routes_with({'/slots': slots_missing}))
    out.append(summarize('V2 one /slots entry lacks n_ctx (4 entries, 3 kept)', rec))
    k1_log = (RAWC / 'K1.server.log').read_bytes().decode('utf-8', errors='replace')
    rec, _ = run_cell('K1', log=drop_slot_line(k1_log).encode())
    out.append(summarize('V3 server log without n_slots layout line', rec))
    rec, _ = run_cell('K1', log=trailing_last_pool(k1_log).encode())
    out.append(summarize('V4 last pool line carries trailing text', rec))
    with _SEQ_LOCK:
        _SEQ[:] = [(100.0, 101.0), (102.0, 103.0)]
    rec, _ = run_cell('L2', completion=nonoverlap_completion)
    out.append(summarize('V5 concurrent L2, request times do not overlap', rec))
    rec, _ = run_cell('L2', post=fake_post(
        200, b'{"tokens_predicted": 3, "truncated": true, "tokens_evaluated": 17}'))
    out.append(summarize('V6 L2 response: tokens_predicted 3, truncated true, '
                         'tokens_evaluated 17', rec))
    return out


def exc_text(fn):
    try:
        fn()
    except Exception as exc:  # recording the exception type is the purpose here
        return f'{type(exc).__name__}: {exc}'
    return 'no exception'


def direct():
    res = {}
    big = b'{"tokens_predicted": 600, "truncated": false, "content": "' + b'x' * 70000 + b'"}'
    restore()
    kct._OPENER = FakeOpener(lambda: FakeResp(big))
    got = kct.http_post(PORT_BASE, '/completion', {'prompt': [1]}, timeout=5.0)
    res['body_cap_len'] = len(got['body'])
    res['body_cap_flag'] = got['body_truncated']
    done = kct._completion(PORT_BASE, {'prompt': [1]})
    res['body_cap_completion'] = {k: done.get(k) for k in
                                  ('status', 'error', 'tokens_predicted', 'truncated')}
    restore()
    kct._OPENER = FakeOpener(lambda: FakeResp(b'', raise_on_read=http.client.IncompleteRead(b'part')))
    res['incomplete_read_escapes'] = exc_text(
        lambda: kct.http_post(PORT_BASE, '/completion', {}, timeout=5.0))
    restore()

    def bad_line():
        raise http.client.BadStatusLine('garbage')
    kct._OPENER = FakeOpener(bad_line)
    res['bad_status_line_escapes'] = exc_text(
        lambda: kct.http_post(PORT_BASE, '/completion', {}, timeout=5.0))
    restore()
    ver = 'version: 0.7.0-dev (build 117550, commit 704366d76)'
    res['tool_version_substring_accepts_117550'] = kct.SERVER_VERSION_MARK in ver
    res['counter_exact_regex_accepts_117550'] = bool(c2.BUILD.search(ver))
    restore()
    kct.os = OsProxy()
    KILLPG.clear()
    child = FakeChild(['llama-server'])
    child.returncode = 0
    td = kct._teardown(child, PORT_BASE + 27)
    res['teardown_reaped_child_killpg'] = list(KILLPG)
    res['teardown_reaped_child_fields'] = {k: td.get(k) for k in
                                           ('sigterm_sent', 'child_returncode',
                                            'port_closed', 'error')}
    restore()

    def refuse(*args, **kwargs):
        raise OSError(8, 'simulated exec failure')
    rec, _ = run_cell('K1', popen=refuse)
    res['launch_fail_record'] = {'error': rec['error'], 'teardown': rec['teardown'],
                                 'observed': rec['observed']}
    res['launch_fail_summary_expr'] = exc_text(
        lambda: all(c.get('teardown', {}).get('port_closed') for c in [rec]))
    restore()
    return res


def counter_case(name, mutate):
    doc = json.loads(json.dumps(REC))
    mutate(doc)
    path = WORK / 'counter' / f'{name}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc), encoding='utf-8')
    buf = io.StringIO()
    old = sys.argv
    sys.argv = ['count-c2.py', str(path)]
    try:
        with contextlib.redirect_stdout(buf):
            code = c2.main()
    finally:
        sys.argv = old
    return {'case': name, 'exit': code, 'counter_line': buf.getvalue().strip()}


def cell_of(doc, cid):
    return next(c for c in doc['cells'] if c['id'] == cid)


def m_none(doc):
    pass


def m_server_sha(doc):
    doc['server']['sha256'] = 'deadbeef'


def m_tool_sha(doc):
    doc['tool']['sha256'] = 'deadbeef'


def m_port_module(doc):
    doc['port_safety_module'] = '/nonexistent/kama-llamacpp-live.py'


def m_l2_tokens(doc):
    for q in cell_of(doc, 'L2')['requests']:
        q['tokens_predicted'] = 3
        q['truncated'] = True


def m_l2_500(doc):
    for q in cell_of(doc, 'L2')['requests']:
        q['status'] = 500


def m_k1_props(doc):
    cell_of(doc, 'K1')['props_n_ctx'] = 999


def m_l1_prompt(doc):
    for q in cell_of(doc, 'L1')['requests']:
        q['prompt_tokens'] = 999


def m_l1_noverlap(doc):
    reqs = sorted(cell_of(doc, 'L1')['requests'], key=lambda q: q['t_start'])
    reqs[1]['t_start'] = reqs[0]['t_end'] + 1.0
    reqs[1]['t_end'] = reqs[1]['t_start'] + 0.1


def m_ver_minor(doc):
    doc['server_version'] = doc['server_version'].replace('704366d76', '704366d7X')


def counters():
    cases = [('control', m_none), ('server_sha_forged', m_server_sha),
             ('tool_sha_forged', m_tool_sha), ('port_module_path_forged', m_port_module),
             ('L2_tokens_predicted_3_truncated', m_l2_tokens), ('L2_status_500', m_l2_500),
             ('K1_props_n_ctx_999', m_k1_props), ('L1_prompt_tokens_999', m_l1_prompt),
             ('L1_no_overlap', m_l1_noverlap), ('server_version_minor_changed', m_ver_minor)]
    return [counter_case(name, fn) for name, fn in cases]


WRAPPER = '''import importlib.util, subprocess, sys
spec = importlib.util.spec_from_file_location("kct_main", "__CLONE__/tools/kama-context-capacity.py")
kct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kct)

class _NoChild:
    def __init__(self, *a, **k):
        raise OSError(8, "simulated: harness starts no child")

class _SP:
    def __getattr__(self, name):
        return getattr(subprocess, name)
    def Popen(self, *a, **k):
        return _NoChild(*a, **k)
    def run(self, args, *a, **k):
        if args and str(args[-1]) == "--version":
            return subprocess.CompletedProcess(args, 0, stdout="version: 0.7.0-dev (build 11755, commit 704366d76)\\n", stderr="")
        return subprocess.run(args, *a, **k)

kct.subprocess = _SP()
sys.exit(kct.main(["--out", "__WORK__/crash/receipt.json", "--scratch", "__WORK__/crash/scratch", "--only", "K1", "--ready-timeout", "5", "--host-idle-timeout", "5"]))
'''


def wrapper_case():
    crash_dir = WORK / 'crash'
    crash_dir.mkdir(parents=True, exist_ok=True)
    receipt = crash_dir / 'receipt.json'
    if receipt.exists():
        receipt.unlink()
    path = WORK / 'crash_main.py'
    path.write_text(WRAPPER.replace('__CLONE__', str(CLONE)).replace('__WORK__', str(WORK)),
                    encoding='utf-8')
    proc = subprocess.run([sys.executable, str(path)], capture_output=True, text=True,
                          timeout=300)
    return {'exit': proc.returncode, 'stderr_tail': proc.stderr.strip().splitlines()[-4:],
            'stdout': proc.stdout.strip(), 'receipt_written': receipt.exists()}


def main():
    results = {}
    results['replay'] = [replay_one(cid) for cid in CELLDEF]
    results['variants'] = variants()
    results['direct'] = direct()
    results['counter_cases'] = counters()
    results['wrapper_main_launch_failure'] = wrapper_case()
    restore()
    (OUT / 'results.json').write_text(json.dumps(results, indent=2, sort_keys=True),
                                      encoding='utf-8')
    for row in results['replay']:
        print('REPLAY', row['id'], 'diffs=', row['diffs'], 'receipt_obs=',
              row['receipt_observed'], 'tool_obs=', row['tool_observed'],
              'counter=', row['counter_accepts'], 'killpg=', row['killpg_calls'],
              'port_closed=', row['port_closed'], 'rc=', row['child_returncode'])
    for row in results['variants']:
        print('VARIANT', row['variant'], '| tool_observed=', row['tool_observed'],
              'counter_accepts=', row['counter_accepts'], 'error=', row['error'],
              'requests=', row['requests'])
    print('DIRECT', json.dumps(results['direct'], sort_keys=True))
    for row in results['counter_cases']:
        print('COUNTER', row['case'], 'exit=', row['exit'], row['counter_line'])
    print('WRAPPER', json.dumps(results['wrapper_main_launch_failure'], sort_keys=True))


if __name__ == '__main__':
    main()
