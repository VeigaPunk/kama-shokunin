#!/usr/bin/env python3
"""Round-63 C1 counter: strict, outside-bound live request-plane receipt.

Usage: python3 tools/round63-c1-counter.py --repo REPO --tip REV --work DIR

Frozen predicate (same sentence as .ufo/waves/round-63/controls/freeze.txt):
  C1-r63: at the tip, the byte-pinned tools/kama-completion-live.py (schema
  kama-completion-live/v2) runs one hold-mode live request-plane lifecycle on
  the pinned llama.cpp fixture whose receipt the counter re-derives from
  captured bytes - every graded check recomputed true and agreeing with the
  recorded verdict, the model and server files re-hashed by the counter
  itself, response headers, body completeness, choice shape, id/created,
  strict timings, the request bytes and the server's own /tokenize prompt
  count all bound - while the counter's own outside request during the hold
  window returns an answer whose usage.prompt_tokens equals the held child's
  /tokenize count for that nonce prompt, whose fingerprint equals the
  receipt's captured one, and whose listener is the receipt's child; and all
  44 targeted controls are rejected by the check each one names, errors=0.

The counter never trusts receipt-claimed results. A control counts as
rejected only when the failure set of its re-score contains the named check:
a mutation rejected by an unrelated failure is not credit. Output: one line,
exit 0 iff met. Every scratch path is under --work.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

MODEL_SHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
SERVER_SHA = 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804'
ALIAS = 'kama-completion-probe'
FP_RE = re.compile(r'^b\d+-[0-9a-f]{9,40}$')
SCHEMA = 'kama-completion-live/v2'
PROMPT = 'The cat sat on the'
EXPECT_CONTROLS = 44
STORED = {
    'health_ready', 'models_alias_id', 'props_alias', 'completion_envelope',
    'completion_headers', 'completion_untruncated', 'completion_choice_shape',
    'completion_finish_reason', 'completion_model_id',
    'completion_fingerprint', 'completion_id_created', 'completion_usage',
    'completion_timings', 'completion_prompt_tokens',
    'completion_request_bound', 'completion_deterministic',
    'bad_request_graded', 'listener_owned', 'model_digest', 'server_digest',
    'hold_released', 'teardown_clean', 'teardown_port_closed'}
NONCE = ''
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
_HASH_CACHE = {}


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    return subprocess.run(['git', '-C', str(repo), *args],
                          capture_output=True, env=env)


def blob(repo, rev, path):
    p = git(repo, 'show', f'{rev}:{path}')
    return p.stdout if p.returncode == 0 else None


def sha256_b(b):
    return hashlib.sha256(b).hexdigest()


def sha256_path(path):
    if path in _HASH_CACHE:
        return _HASH_CACHE[path]
    try:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(1 << 20), b''):
                h.update(chunk)
        _HASH_CACHE[path] = h.hexdigest()
    except (OSError, TypeError):
        _HASH_CACHE[path] = None
    return _HASH_CACHE[path]


def jbody(cap):
    try:
        return json.loads((cap or {}).get('body', ''))
    except (ValueError, TypeError):
        return None


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def is_num(v):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v))


def ctype_json(headers):
    ct = (headers or {}).get('content-type') or ''
    return ct.split(';')[0].strip().lower() == 'application/json'


def http(port, path, payload=None, timeout=10.0):
    """One loopback request on the proxy-free opener. Returns
    (status|None, headers, body_text, request_bytes|None)."""
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f'http://127.0.0.1:{port}{path}', data=data,
        headers={'Content-Type': 'application/json'} if data else {},
        method='POST' if data is not None else 'GET')
    try:
        with _OPENER.open(req, timeout=timeout) as r:
            return (r.status, {k.lower(): v for k, v in r.headers.items()},
                    r.read().decode('utf-8', 'replace'), data)
    except urllib.error.HTTPError as e:
        return (e.code, {k.lower(): v for k, v in (e.headers or {}).items()},
                e.read().decode('utf-8', 'replace'), data)
    except Exception as e:
        return None, {}, type(e).__name__, data


# ---------------------------------------------------------------- grading #

def grade(receipt):
    """Recompute every check from captured bytes and re-hashed files.
    Returns (recomputed {name: bool}, inconsistent [str])."""
    caps = receipt.get('captures') or {}
    td = receipt.get('teardown') or {}
    hold = receipt.get('hold') or {}
    stored = receipt.get('checks') or {}
    out = {}

    def cap(name):
        c = caps.get(name)
        if not isinstance(c, dict):
            return None
        body = c.get('body')
        if not isinstance(body, str):
            return None
        if sha256_b(body.encode()) != c.get('body_sha256'):
            return None
        return c

    out['schema'] = receipt.get('schema') == SCHEMA
    h = cap('health')
    out['health_ready'] = (h is not None and h.get('status') == 200
                           and h.get('body') == '{"status":"ok"}')
    m = cap('models')
    mj = jbody(m) if m else None
    ids = ([d.get('id') for d in mj.get('data') or [] if isinstance(d, dict)]
           if isinstance(mj, dict) else None)
    out['models_alias_id'] = (m is not None and m.get('status') == 200
                              and ids == [ALIAS])
    pr = cap('props')
    prj = jbody(pr) if pr else None
    out['props_alias'] = (isinstance(prj, dict)
                          and prj.get('model_alias') == ALIAS)
    c = cap('completion')
    cj = jbody(c) if c else None
    chs = cj.get('choices') if isinstance(cj, dict) else None
    ch0 = chs[0] if isinstance(chs, list) and chs and isinstance(
        chs[0], dict) else {}
    env = (c is not None and c.get('status') == 200
           and isinstance(cj, dict) and cj.get('object') == 'text_completion'
           and isinstance(chs, list) and len(chs) >= 1
           and isinstance(ch0.get('text'), str))
    out['completion_envelope'] = bool(env)
    out['completion_headers'] = bool(
        env and ctype_json(c.get('headers')))
    cl = (c.get('headers') or {}).get('content-length') if c else None
    out['completion_untruncated'] = bool(
        env and c.get('body_truncated') is False
        and is_int(c.get('body_bytes'))
        and c['body_bytes'] == len(c['body'].encode())
        and (cl is None or (str(cl).isdigit() and int(cl) == c['body_bytes'])))
    out['completion_choice_shape'] = bool(
        env and len(chs) == 1 and ch0.get('index') == 0
        and not isinstance(ch0.get('index'), bool)
        and ch0.get('text') != '' and ch0.get('logprobs') is None)
    out['completion_finish_reason'] = bool(
        env and ch0.get('finish_reason') in ('length', 'stop'))
    out['completion_model_id'] = bool(env and cj.get('model') == ALIAS)
    fp = cj.get('system_fingerprint') if isinstance(cj, dict) else None
    out['completion_fingerprint'] = bool(
        env and isinstance(fp, str) and FP_RE.match(fp))
    out['completion_id_created'] = bool(
        env and isinstance(cj.get('id'), str) and cj['id'] != ''
        and is_int(cj.get('created')) and cj['created'] > 1_000_000_000)
    u = (cj.get('usage') if isinstance(cj, dict) else None) or {}
    pd = u.get('prompt_tokens_details')
    out['completion_usage'] = bool(
        env and is_int(u.get('completion_tokens'))
        and is_int(u.get('prompt_tokens')) and is_int(u.get('total_tokens'))
        and u['completion_tokens'] >= 1 and u['prompt_tokens'] >= 1
        and u['total_tokens'] == u['completion_tokens'] + u['prompt_tokens']
        and isinstance(pd, dict) and is_int(pd.get('cached_tokens'))
        and 0 <= pd['cached_tokens'] <= u['prompt_tokens'])
    t = (cj.get('timings') if isinstance(cj, dict) else None) or {}
    out['completion_timings'] = bool(
        env and isinstance(t, dict) and is_int(t.get('predicted_n'))
        and t['predicted_n'] == u.get('completion_tokens')
        and is_int(t.get('cache_n')) and t['cache_n'] >= 0
        and is_int(t.get('prompt_n')) and t['prompt_n'] >= 0
        and is_num(t.get('predicted_ms')) and t['predicted_ms'] >= 0)
    tk = cap('tokenize')
    tkj = jbody(tk) if tk else None
    toks = tkj.get('tokens') if isinstance(tkj, dict) else None
    out['completion_prompt_tokens'] = bool(
        env and tk is not None and tk.get('status') == 200
        and isinstance(toks, list) and len(toks) >= 1
        and u.get('prompt_tokens') == len(toks))
    rb = c.get('request_body') if c else None
    try:
        rj = json.loads(rb) if isinstance(rb, str) else None
    except ValueError:
        rj = None
    out['completion_request_bound'] = bool(
        env and isinstance(rj, dict) and isinstance(rb, str)
        and sha256_b(rb.encode()) == c.get('request_sha256')
        and rj.get('prompt') == PROMPT)
    c2 = cap('completion2')
    c2j = jbody(c2) if c2 else None
    c2c = c2j.get('choices') if isinstance(c2j, dict) else None
    ch02 = c2c[0] if isinstance(c2c, list) and c2c and isinstance(
        c2c[0], dict) else {}
    out['completion_deterministic'] = bool(
        env and c2 is not None and c2.get('status') == 200
        and ch02.get('text') == ch0.get('text')
        and ch0.get('text') not in (None, '')
        and c2.get('request_sha256') == c.get('request_sha256'))
    b = cap('bad_request')
    bj = jbody(b) if b else None
    out['bad_request_graded'] = bool(
        b is not None and b.get('status') in (400, 500)
        and isinstance(bj, dict) and isinstance(bj.get('error'), dict))
    mdl = receipt.get('model') or {}
    srv = receipt.get('server') or {}
    out['model_digest'] = bool(
        mdl.get('sha256') == MODEL_SHA
        and sha256_path(mdl.get('path')) == MODEL_SHA)
    out['server_digest'] = bool(
        srv.get('sha256') == SERVER_SHA
        and sha256_path(srv.get('path')) == SERVER_SHA)
    if 'hold_released' in stored:
        out['hold_released'] = bool(hold.get('released'))
    out['teardown_clean'] = bool(not td.get('child_pre_dead')
                                 and td.get('returncode') in (0, -15))
    out['teardown_port_closed'] = td.get('port_closed') is True
    out['nonce_match'] = bool(NONCE) and receipt.get('nonce') == NONCE

    inconsistent = [k for k, v in out.items()
                    if k in stored and stored[k].get('passed') is not None
                    and stored[k].get('passed') != v]
    # the receipt's own listener_owned bit cannot be re-derived offline:
    # it is graded against the outside witness in score(), never from itself
    if not STORED.issubset(stored):
        inconsistent.append('missing-checks')
    if set(stored) - STORED:
        inconsistent.append('unexpected-checks')
    return out, inconsistent


def score(receipt, witness):
    """Re-score a receipt against the counter's outside witness. Returns
    {'met': bool, 'fails': set of failing check names}."""
    recomputed, inconsistent = grade(receipt)
    fails = {k for k, v in recomputed.items() if v is not True}
    fails |= {'inconsistent:' + i for i in inconsistent}
    if receipt.get('verdict') != 'REQUEST_OK':
        fails.add('verdict')
    stored = receipt.get('checks') or {}
    if (stored.get('listener_owned') or {}).get('passed') is not True:
        fails.add('listener_owned')
    w = witness or {}
    caps = receipt.get('captures') or {}
    ccj = jbody(caps.get('completion') or {})
    cfp = ccj.get('system_fingerprint') if isinstance(ccj, dict) else None
    live = {
        'live_status': w.get('status') == 200,
        'live_ctype': ctype_json(w.get('headers')),
        'live_object': w.get('object') == 'text_completion',
        'live_model': w.get('model') == ALIAS and w.get('alias') == ALIAS,
        'live_text': isinstance(w.get('text'), str) and w['text'] != '',
        'live_created': is_int(w.get('created')) and w['created'] > 1e9
        and isinstance(w.get('id'), str) and w['id'] != '',
        'live_fp_shape': isinstance(w.get('fingerprint'), str)
        and FP_RE.match(w['fingerprint']) is not None,
        'live_fp_capture': isinstance(cfp, str)
        and w.get('fingerprint') == cfp,
        'live_pid': w.get('pid') is not None
        and w.get('pid') == receipt.get('child_pid'),
        'live_port': w.get('port') is not None
        and w.get('port') == receipt.get('port'),
        'live_owned': w.get('listener_owned') is True,
        'live_nonce': bool(NONCE) and NONCE in (w.get('sent_prompt') or ''),
        'live_ptok': is_int(w.get('usage_prompt_tokens'))
        and is_int(w.get('tokenize_count'))
        and w['usage_prompt_tokens'] == w['tokenize_count'] >= 1,
        'live_server_sha': w.get('server_sha256') == SERVER_SHA
        and (receipt.get('server') or {}).get('sha256')
        == w.get('server_sha256'),
        'live_model_sha': w.get('model_sha256') == MODEL_SHA,
    }
    fails |= {k for k, v in live.items() if not v}
    return {'met': not fails, 'fails': fails}


def observe(port, pid, hold_doc, live_mod, nonce):
    """The counter's own outside contact with a listener: one nonce prompt,
    the exact request bytes kept, and the listener's own /tokenize count
    for the prompt sent. Same code path for the live child and the fakes."""
    nprompt = f'{nonce} under the'
    st, hdr, body, req = http(port, '/v1/completions', {
        'prompt': nprompt, 'n_predict': 4, 'temperature': 0.0, 'seed': 3})
    try:
        wj = json.loads(body)
    except ValueError:
        wj = {}
    if not isinstance(wj, dict):
        wj = {}
    sent = json.loads(req.decode())['prompt']
    chs = wj.get('choices')
    ch0 = chs[0] if isinstance(chs, list) and chs and isinstance(
        chs[0], dict) else {}
    tst, _, tbody, _ = http(port, '/tokenize',
                            {'content': sent, 'add_special': True})
    try:
        tj = json.loads(tbody)
    except ValueError:
        tj = {}
    toks = tj.get('tokens') if isinstance(tj, dict) else None
    usage = wj.get('usage') if isinstance(wj.get('usage'), dict) else {}
    return {
        'status': st, 'headers': hdr, 'port': port, 'pid': pid,
        'alias': (hold_doc or {}).get('alias'),
        'object': wj.get('object'), 'model': wj.get('model'),
        'fingerprint': wj.get('system_fingerprint'),
        'text': ch0.get('text'), 'created': wj.get('created'),
        'id': wj.get('id'),
        'sent_prompt': sent,
        'usage_prompt_tokens': usage.get('prompt_tokens'),
        'tokenize_count': (len(toks) if tst == 200
                           and isinstance(toks, list) else None),
        'listener_owned': (live_mod.port_owned_by(pid, port)
                           if pid is not None else None),
        'server_sha256': (hold_doc or {}).get('server_sha256'),
        'model_sha256': (hold_doc or {}).get('model_sha256'),
    }


def load_live_mod(tool_path):
    mod = importlib.util.spec_from_file_location(
        'kama_live_r63', os.path.join(os.path.dirname(tool_path),
                                      'kama-llamacpp-live.py'))
    live_mod = importlib.util.module_from_spec(mod)
    mod.loader.exec_module(live_mod)
    return live_mod


def witness_run(work, tool_path):
    """Run the tip-pinned tool in hold mode; during the hold contact the
    child ourselves. Returns (receipt|None, witness|None, nonce)."""
    hold = os.path.join(work, 'hold')
    os.makedirs(hold, exist_ok=True)
    nonce = 'r63-' + hashlib.sha256(os.urandom(16)).hexdigest()[:10]
    out_path = os.path.join(work, 'receipt.json')
    proc = subprocess.Popen(
        [sys.executable, tool_path, '--nonce', nonce,
         '--work', os.path.join(work, 'tool-work'),
         '--model-sha256', MODEL_SHA, '--server-sha256', SERVER_SHA,
         '--alias', ALIAS, '--hold-dir', hold, '--hold-timeout', '90',
         '--out', out_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    witness = None
    t0 = time.monotonic()
    while time.monotonic() - t0 < 120:
        hp = os.path.join(hold, 'hold.json')
        if os.path.exists(hp):
            try:
                h = json.load(open(hp))
            except (ValueError, OSError):
                time.sleep(0.2)
                continue
            witness = observe(h.get('port'), h.get('pid'), h,
                              load_live_mod(tool_path), nonce)
            break
        if proc.poll() is not None:
            break
        time.sleep(0.25)
    open(os.path.join(hold, 'release'), 'w').write('go\n')
    try:
        proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)
    receipt = None
    try:
        receipt = json.load(open(out_path))
    except (ValueError, OSError):
        pass
    return receipt, witness, nonce


def make_fake(usage_prompt, tok_count, fp):
    """A canned loopback server: /v1/completions claims usage_prompt prompt
    tokens, /tokenize answers tok_count tokens."""
    import http.server

    class H(http.server.BaseHTTPRequestHandler):
        def _send(self, payload):
            b = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_POST(self):
            n = int(self.headers.get('Content-Length') or 0)
            self.rfile.read(n)
            if self.path == '/tokenize':
                self._send({'tokens': [1] * tok_count})
            else:
                self._send({
                    'object': 'text_completion', 'model': ALIAS,
                    'id': 'cmpl-x', 'created': 1_800_000_000,
                    'system_fingerprint': fp,
                    'choices': [{'text': ' x', 'index': 0,
                                 'logprobs': None,
                                 'finish_reason': 'length'}],
                    'usage': {'prompt_tokens': usage_prompt,
                              'completion_tokens': 1,
                              'total_tokens': usage_prompt + 1,
                              'prompt_tokens_details': {'cached_tokens': 0}}})

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


# --------------------------------------------------------------- controls #

def clone(o):
    return json.loads(json.dumps(o))


def reseal(c):
    c['body_sha256'] = sha256_b(c['body'].encode())
    c['body_bytes'] = len(c['body'].encode())


def edit_body(rcpt, name, fn):
    """Mutate the JSON body of one capture and re-seal its hash, so the
    mutation is rejected by the grader and not by the hash comparison."""
    m = clone(rcpt)
    c = m['captures'][name]
    obj = json.loads(c['body'])
    fn(obj)
    c['body'] = json.dumps(obj, separators=(',', ':'))
    reseal(c)
    if 'content-length' in c.get('headers', {}):
        c['headers']['content-length'] = str(c['body_bytes'])
    return m


def edit(rcpt, fn):
    m = clone(rcpt)
    fn(m)
    return m


def build_controls(receipt, work):
    """(family, mutated receipt, witness-mutator|None, expected fail name).
    Witness mutators receive and return a witness copy."""
    decoy = os.path.join(work, 'decoy-model.bin')
    with open(decoy, 'wb') as f:
        f.write(b'not-the-pinned-model')
    ctl = []

    def add(fam, m, expect, wm=None):
        ctl.append((fam, m, wm, expect))

    add('stale', edit(receipt, lambda m: m.update({'nonce': 'r60-dead'})),
        'nonce_match')
    add('log', edit(receipt, lambda m: m['captures']['health'].update(
        {'body': '{"status":"OK"}'})), 'health_ready')
    add('tamper', edit_body(receipt, 'completion', lambda o: o.update(
        {'object': 'chat.completion'})), 'completion_envelope')
    add('tamper', edit(receipt, lambda m: m['hold'].update(
        {'released': False})), 'hold_released')
    add('tamper', edit(receipt, lambda m: m['teardown'].update(
        {'child_pre_dead': True})), 'teardown_clean')
    add('tamper', edit(receipt, lambda m: m['teardown'].update(
        {'returncode': 137})), 'teardown_clean')
    add('tamper', edit(receipt, lambda m: m['teardown'].update(
        {'port_closed': False})), 'teardown_port_closed')
    add('tamper', edit(receipt, lambda m: m.update({'verdict': 'FAIL'})),
        'verdict')

    def swap_text(o):
        o['choices'][0]['text'] = o['choices'][0]['text'] + '!'
    add('tamper', edit_body(receipt, 'completion2', swap_text),
        'completion_deterministic')
    add('tamper', edit(receipt, lambda m: (
        m['model'].update({'sha256': '0' * 64}),
        m['server'].update({'sha256': '0' * 64}))), 'model_digest')
    add('predead', edit(receipt, lambda m: m['teardown'].update(
        {'child_pre_dead': True})), 'teardown_clean')
    add('sigterm', edit(receipt, lambda m: m['teardown'].update(
        {'returncode': -9})), 'teardown_clean')
    add('hold', edit(receipt, lambda m: m['hold'].update(
        {'released': False})), 'hold_released')
    add('outside', edit_body(receipt, 'completion', lambda o: o.update(
        {'model': 'other-alias'})), 'completion_model_id')
    # ---- round-63 families ----------------------------------------- #
    add('hdr', edit(receipt, lambda m: m['captures']['completion'][
        'headers'].update({'content-type': 'text/plain'})),
        'completion_headers')
    add('hdr', edit(receipt, lambda m: m['captures']['completion'][
        'headers'].pop('content-type')), 'completion_headers')
    add('trunc', edit(receipt, lambda m: m['captures']['completion'].update(
        {'body_truncated': True})), 'completion_untruncated')
    add('trunc', edit(receipt, lambda m: m['captures']['completion'][
        'headers'].update({'content-length': str(
            m['captures']['completion']['body_bytes'] + 1)})),
        'completion_untruncated')

    def timing(**kw):
        return lambda o: o['timings'].update(kw)
    add('timing', edit_body(receipt, 'completion', timing(predicted_ms=-1.0)),
        'completion_timings')
    add('timing', edit_body(receipt, 'completion', timing(predicted_ms=True)),
        'completion_timings')
    add('timing', edit_body(receipt, 'completion',
                            timing(predicted_ms=float('inf'))),
        'completion_timings')
    add('timing', edit_body(receipt, 'completion',
                            lambda o: o['timings'].pop('cache_n')),
        'completion_timings')
    add('shape', edit_body(receipt, 'completion', lambda o: o[
        'choices'].append(dict(o['choices'][0]))), 'completion_choice_shape')
    add('shape', edit_body(receipt, 'completion', lambda o: o['choices'][
        0].update({'index': 1})), 'completion_choice_shape')
    add('shape', edit_body(receipt, 'completion', lambda o: o['choices'][
        0].update({'text': ''})), 'completion_choice_shape')
    add('shape', edit_body(receipt, 'completion', lambda o: o['choices'][
        0].update({'logprobs': {}})), 'completion_choice_shape')
    add('idcr', edit_body(receipt, 'completion', lambda o: o.update(
        {'id': ''})), 'completion_id_created')
    add('idcr', edit_body(receipt, 'completion', lambda o: o.update(
        {'created': True})), 'completion_id_created')
    add('idcr', edit_body(receipt, 'completion', lambda o: o.update(
        {'created': 5})), 'completion_id_created')

    def ptok(o):
        o['usage']['prompt_tokens'] += 1
        o['usage']['total_tokens'] += 1
    add('ptok', edit_body(receipt, 'completion', ptok),
        'completion_prompt_tokens')
    add('ptok', edit_body(receipt, 'tokenize', lambda o: o['tokens'].append(
        7)), 'completion_prompt_tokens')

    def req_prompt(m):
        c = m['captures']['completion']
        c['request_body'] = c['request_body'].replace(PROMPT, 'Other text')
        c['request_sha256'] = sha256_b(c['request_body'].encode())
    add('reqbind', edit(receipt, req_prompt), 'completion_request_bound')
    add('reqbind', edit(receipt, lambda m: m['captures']['completion'].update(
        {'request_sha256': '0' * 64})), 'completion_request_bound')
    add('listener', edit(receipt, lambda m: m['checks'][
        'listener_owned'].update({'passed': False})), 'listener_owned')
    add('digest', edit(receipt, lambda m: m['model'].update(
        {'path': decoy})), 'model_digest')
    add('schema', edit(receipt, lambda m: m.update(
        {'schema': 'kama-completion-live/v1'})), 'schema')
    # ---- witness mutations (the receipt itself is the genuine one) ---- #
    def wm(**kw):
        return lambda w: {**w, **kw}
    add('witness', receipt, 'live_fp_capture',
        wm(fingerprint='b1-aaaaaaaaa'))
    add('witness', receipt, 'live_ptok',
        lambda w: {**w, 'usage_prompt_tokens': w['usage_prompt_tokens'] + 1})
    add('witness', receipt, 'live_object', wm(object='chat.completion'))
    add('witness', receipt, 'live_text', wm(text=''))
    add('witness', receipt, 'live_pid', wm(pid=1))
    add('witness', receipt, 'live_owned', wm(listener_owned=False))
    return ctl


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--tip', required=True)
    ap.add_argument('--work', required=True)
    args = ap.parse_args(argv)
    work = os.path.abspath(args.work)
    os.makedirs(work, exist_ok=True)
    errors = []

    tool_blob = blob(args.repo, args.tip, 'tools/kama-completion-live.py')
    tool_present = 1 if tool_blob else 0
    receipt = witness = None
    live_ok = 0
    live_mod = None
    tool_path = None
    global NONCE
    if tool_present:
        tiproot = os.path.join(work, 'tip')
        os.makedirs(os.path.join(tiproot, 'tools'), exist_ok=True)
        os.makedirs(os.path.join(tiproot, 'registry'), exist_ok=True)
        tool_path = os.path.join(tiproot, 'tools', 'kama-completion-live.py')
        with open(tool_path, 'wb') as f:
            f.write(tool_blob)
        dep = blob(args.repo, args.tip, 'tools/kama-llamacpp-live.py')
        if not dep:
            errors.append('tip lacks tools/kama-llamacpp-live.py')
        else:
            with open(os.path.join(tiproot, 'tools',
                                   'kama-llamacpp-live.py'), 'wb') as f:
                f.write(dep)
        reg = blob(args.repo, args.tip, 'registry/endpoint-consumers.tsv')
        if reg:
            with open(os.path.join(tiproot, 'registry',
                                   'endpoint-consumers.tsv'), 'wb') as f:
                f.write(reg)
        if not errors:
            live_mod = load_live_mod(tool_path)
            receipt, witness, nonce = witness_run(work, tool_path)
            NONCE = nonce or ''
            if receipt is None:
                errors.append('live: no receipt produced')
            else:
                s = score(receipt, witness)
                live_ok = 1 if s['met'] else 0
                if not s['met']:
                    errors.append('live: ' + json.dumps(
                        sorted(s['fails'])))
    else:
        errors.append('tools/kama-completion-live.py absent at tip')

    fam_tot, fam_ok = {}, {}
    detail = []
    if live_ok == 1 and receipt is not None and witness is not None:
        for fam, m, wm, expect in build_controls(receipt, work):
            w = wm(witness) if wm else witness
            s = score(m, w)
            hit = (not s['met']) and expect in s['fails']
            fam_tot[fam] = fam_tot.get(fam, 0) + 1
            fam_ok[fam] = fam_ok.get(fam, 0) + int(hit)
            if not hit:
                detail.append(f'escape {fam} expect={expect} '
                              f'fails={sorted(s["fails"])[:4]}')
        # fakes: the same observe() code on canned servers
        fp = ((jbody(receipt['captures']['completion']) or {})
              .get('system_fingerprint') or 'b1-aaaaaaaaa')
        for name, up, tc, pid, expect in (
                ('fake-inconsistent', 5, 3, receipt.get('child_pid'),
                 'live_ptok'),
                ('fake-foreign', 5, 5, os.getpid(), 'live_pid')):
            srv, port = make_fake(up, tc, fp)
            try:
                hd = {'alias': ALIAS, 'server_sha256': SERVER_SHA,
                      'model_sha256': MODEL_SHA}
                w = observe(port, pid, hd, live_mod, NONCE)
                s = score(receipt, w)
                hit = (not s['met']) and expect in s['fails']
                fam_tot['fake'] = fam_tot.get('fake', 0) + 1
                fam_ok['fake'] = fam_ok.get('fake', 0) + int(hit)
                if not hit:
                    detail.append(f'escape {name} expect={expect} '
                                  f'fails={sorted(s["fails"])[:4]}')
            finally:
                srv.shutdown()
    total = sum(fam_tot.values())
    rejected = sum(fam_ok.values())
    met = (tool_present == 1 and live_ok == 1 and total == EXPECT_CONTROLS
           and rejected == EXPECT_CONTROLS and not errors)
    fams = ' '.join(f'{k}={fam_ok.get(k, 0)}/{v}'
                    for k, v in sorted(fam_tot.items()))
    print(f'tool_present={tool_present} live_ok={live_ok}/1 '
          f'controls_targeted={rejected}/{total} '
          f'errors={len(errors)} met={met} families[{fams}]')
    for e in errors[:8] + detail[:8]:
        print(f'error: {e}', file=sys.stderr)
    return 0 if met else 1


if __name__ == '__main__':
    sys.exit(main())
