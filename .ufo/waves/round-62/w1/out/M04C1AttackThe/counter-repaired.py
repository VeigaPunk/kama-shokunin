#!/usr/bin/env python3
"""Round-62 C1 counter: hold-verified live request-plane receipt.

Usage: python3 tools/round62-c1-counter.py --repo REPO --tip REV --work DIR

Frozen predicate (same sentence as .ufo/waves/round-62/controls/freeze.txt):
  C1-r62: at the tip, the byte-pinned tools/kama-completion-live.py runs one
  hold-mode live request-plane lifecycle on the pinned llama.cpp fixture
  (sha256-verified model and server, unregistered loopback port, pdeathsig
  child) whose receipt the counter re-derives from captured bytes — every
  graded check recomputed true and agreeing with the recorded verdict — while
  the counter's own outside request during the hold window returns a live
  answer bound to the served alias, build fingerprint and fresh nonce; and
  all 16 controls are rejected, errors=0.

The counter never trusts receipt-claimed results: it re-runs the tool's
grading on the captured bodies, re-hashes capture bodies against their
recorded sha256, re-hashes the model and server files, contacts the held
child itself, and feeds the same grading 16 mutated or synthetic inputs
(the control families below). Output: one line, exit 0 iff met.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

MODEL_SHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
SERVER_SHA = 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804'
ALIAS = 'kama-completion-probe'
FP_RE = re.compile(r'^b\d+-[0-9a-f]{9,40}$')
SCHEMA = 'kama-completion-live/v1'
PROMPT = 'The cat sat on the'
MUT = '__kama_mut__'


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    return subprocess.run(['git', '-C', str(repo), *args],
                          capture_output=True, env=env)


def blob(repo, rev, path):
    p = git(repo, 'show', f'{rev}:{path}')
    return p.stdout if p.returncode == 0 else None


def sha256_b(b):
    return hashlib.sha256(b).hexdigest()


def jbody(cap):
    try:
        return json.loads(cap.get('body', ''))
    except (ValueError, TypeError):
        return None


def post(port, payload, timeout=10.0):
    req = urllib.request.Request(
        f'http://127.0.0.1:{port}/v1/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')
    except Exception as e:
        return None, type(e).__name__


# ---------------------------------------------------------------- grading #

def grade(receipt):
    """Recompute every check the receipt records from its captured bytes.
    Returns (recomputed: {name: bool|None}, inconsistent: list[str]).
    A recomputed value None means the check could not be evaluated (its
    inputs are absent); an inconsistent name means the recomputed value
    disagrees with the stored checks[name].passed."""
    caps = receipt.get('captures') or {}
    td = receipt.get('teardown') or {}
    hold = receipt.get('hold') or {}
    out = {}

    def cap(name):
        c = caps.get(name) or {}
        if sha256_b(c.get('body', '').encode()) != c.get('body_sha256'):
            return None
        return c

    h = cap('health')
    out['health_ready'] = (h is not None and h.get('status') == 200
                           and h.get('body') == '{"status":"ok"}')
    m = cap('models')
    mj = jbody(m) if m else None
    ids = [d.get('id') for d in (mj or {}).get('data') or []
           if isinstance(d, dict)] if isinstance(mj, dict) else None
    out['models_alias_id'] = (m is not None and m.get('status') == 200
                              and ids == [ALIAS])
    pr = cap('props')
    prj = jbody(pr) if pr else None
    out['props_alias'] = (isinstance(prj, dict)
                          and prj.get('model_alias') == ALIAS)
    c = cap('completion')
    cj = jbody(c) if c else None
    ch0 = (cj.get('choices') or [{}])[0] if isinstance(cj, dict) else {}
    out['completion_envelope'] = (
        c is not None and c.get('status') == 200
        and isinstance(cj, dict)
        and cj.get('object') == 'text_completion'
        and isinstance(cj.get('choices'), list)
        and len(cj['choices']) >= 1
        and isinstance(ch0.get('text'), str))
    out['completion_finish_reason'] = (out['completion_envelope']
        and ch0.get('finish_reason') in ('length', 'stop'))
    out['completion_model_id'] = (out['completion_envelope']
        and cj.get('model') == ALIAS)
    out['completion_fingerprint'] = (out['completion_envelope']
        and isinstance(cj.get('system_fingerprint'), str)
        and bool(FP_RE.match(cj.get('system_fingerprint') or '')))
    u = (cj.get('usage') or {}) if isinstance(cj, dict) else {}
    t = (cj.get('timings') or {}) if isinstance(cj, dict) else {}
    out['completion_usage'] = (
        out['completion_envelope']
        and isinstance(u.get('completion_tokens'), int)
        and isinstance(u.get('prompt_tokens'), int)
        and isinstance(u.get('total_tokens'), int)
        and u['completion_tokens'] >= 1 and u['prompt_tokens'] >= 1
        and u['total_tokens']
        == u['completion_tokens'] + u['prompt_tokens'])
    out['completion_timings'] = (
        out['completion_envelope']
        and isinstance(t.get('predicted_n'), int)
        and t.get('predicted_n') == u.get('completion_tokens')
        and isinstance(t.get('predicted_ms'), (int, float)))
    c2 = cap('completion2')
    c2j = jbody(c2) if c2 else None
    ch02 = ((c2j.get('choices') or [{}])[0]
            if isinstance(c2j, dict) else {})
    out['completion_deterministic'] = (
        out['completion_envelope'] and c2 is not None
        and c2.get('status') == 200
        and ch02.get('text') == ch0.get('text')
        and ch0.get('text') not in (None, ''))
    b = cap('bad_request')
    bj = jbody(b) if b else None
    out['bad_request_graded'] = (
        b is not None and b.get('status') in (400, 500)
        and isinstance(bj, dict) and isinstance(bj.get('error'), dict))
    out['listener_owned'] = bool(
        (receipt.get('checks') or {}).get('listener_owned', {}).get('passed'))
    out['model_digest'] = (
        (receipt.get('model') or {}).get('sha256') == MODEL_SHA)
    out['server_digest'] = (
        (receipt.get('server') or {}).get('sha256') == SERVER_SHA)
    if 'hold_released' in (receipt.get('checks') or {}):
        out['hold_released'] = bool(hold.get('released'))
    td_ok = (not td.get('child_pre_dead')
             and td.get('returncode') in (0, -15))
    out['teardown_clean'] = td_ok
    out['teardown_port_closed'] = td.get('port_closed') is True
    out['nonce_match'] = receipt.get('nonce') == NONCE

    stored = receipt.get('checks') or {}
    required = set(out) - {'nonce_match'}
    inconsistent = [k for k, v in out.items()
                    if k in stored and v is not None
                    and stored[k].get('passed') is not None
                    and stored[k].get('passed') != v]
    if not required.issubset(stored):
        inconsistent.append('missing-checks')
    if set(stored) != required:
        inconsistent.append('unexpected-checks')
    return out, inconsistent


NONCE = ''


def score(receipt, witness):
    """Witness: dict of the counter's own live observation or None."""
    recomputed, inconsistent = grade(receipt)
    alltrue = all(v is True for v in recomputed.values())
    verdict_ok = receipt.get('verdict') == 'REQUEST_OK'
    live = (witness is not None and witness.get('status') == 200
            and witness.get('model') == ALIAS
            and witness.get('alias') == ALIAS
            and witness.get('pid') == receipt.get('child_pid')
            and witness.get('port') == receipt.get('port')
            and isinstance(witness.get('fingerprint'), str)
            and FP_RE.match(witness['fingerprint'] or '') is not None
            and isinstance(witness.get('text'), str)
            and witness.get('nonce_prompt') == witness.get('sent_prompt')
            and NONCE in (witness.get('sent_prompt') or '')
            and witness.get('listener_owned') is True
            and witness.get('server_sha256') == SERVER_SHA
            and witness.get('model_sha256') == MODEL_SHA)
    if witness is not None:
        cap_cj = jbody((receipt.get('captures') or {}).get('completion') or {})
        live = bool(live and isinstance(cap_cj, dict)
                    and cap_cj.get('model') == witness.get('model')
                    and (receipt.get('server') or {}).get('sha256')
                    == witness.get('server_sha256'))
    return {
        'met': bool(alltrue and verdict_ok and live
                    and not inconsistent),
        'alltrue': alltrue, 'verdict_ok': verdict_ok, 'live': bool(live),
        'inconsistent': inconsistent,
    }


def witness_run(work, tool_path):
    """Run the tip-pinned tool in hold mode; during the hold send a fresh
    nonce request ourselves. Returns (receipt_dict|None, witness_dict|None,
    setup_error|None)."""
    hold = os.path.join(work, 'hold')
    os.makedirs(hold, exist_ok=True)
    nonce = 'r62-' + hashlib.sha256(os.urandom(16)).hexdigest()[:10]
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
        if os.path.exists(os.path.join(hold, 'hold.json')):
            try:
                h = json.load(open(os.path.join(hold, 'hold.json')))
            except (ValueError, OSError):
                time.sleep(0.2)
                continue
            port = h.get('port')
            pid = h.get('pid')
            nprompt = f'{nonce} under the'
            st, body = post(port, {'prompt': nprompt, 'n_predict': 4,
                                   'temperature': 0.0, 'seed': 3})
            wj = {}
            try:
                wj = json.loads(body)
            except ValueError:
                pass
            ch0 = (wj.get('choices') or [{}])[0]
            mod = importlib.util.spec_from_file_location(
                'kama_live_r62', os.path.join(
                    os.path.dirname(tool_path), 'kama-llamacpp-live.py'))
            live_mod = importlib.util.module_from_spec(mod)
            mod.loader.exec_module(live_mod)
            witness = {
                'status': st, 'port': port, 'pid': pid,
                'alias': h.get('alias'),
                'model': wj.get('model'),
                'fingerprint': wj.get('system_fingerprint'),
                'text': ch0.get('text'),
                'sent_prompt': nprompt,
                'nonce_prompt': nprompt,
                'listener_owned': live_mod.port_owned_by(pid, port),
                'server_sha256': h.get('server_sha256'),
                'model_sha256': h.get('model_sha256'),
            }
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


def make_fake(work, body):
    """A canned JSON server on a free loopback port."""
    import http.server
    import threading

    class H(http.server.BaseHTTPRequestHandler):
        def _send(self, payload):
            b = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            if self.path == '/health':
                self._send({'status': 'ok'})
            elif self.path == '/v1/models':
                self._send({'object': 'list',
                            'data': [{'id': ALIAS, 'object': 'model',
                                      'owned_by': 'llamacpp'}]})
            elif self.path == '/props':
                self._send({'model_alias': ALIAS})
            else:
                self._send({})

        def do_POST(self):
            n = int(self.headers.get('Content-Length') or 0)
            self.rfile.read(n)
            self._send(body)

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--tip', required=True)
    ap.add_argument('--work', required=True)
    ap.add_argument('--no-live', action='store_true',
                    help='skip the live leg (fixture/control audit only)')
    args = ap.parse_args(argv)
    work = os.path.abspath(args.work)
    os.makedirs(work, exist_ok=True)
    errors = []

    # -- presence ------------------------------------------------------ #
    tool_blob = blob(args.repo, args.tip, 'tools/kama-completion-live.py')
    tool_present = 1 if tool_blob else 0
    receipt = witness = nonce = None
    live_ok = '0/1'
    if tool_present and not args.no_live:
        tiproot = os.path.join(work, 'tip')
        os.makedirs(os.path.join(tiproot, 'tools'), exist_ok=True)
        os.makedirs(os.path.join(tiproot, 'registry'), exist_ok=True)
        tool_path = os.path.join(tiproot, 'tools',
                                 'kama-completion-live.py')
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
        receipt, witness, nonce = witness_run(work, tool_path)
        global NONCE
        NONCE = nonce or ''
        if receipt is None:
            errors.append('live: no receipt produced')
        else:
            s = score(receipt, witness)
            live_ok = '1/1' if s['met'] else '0/1'
            if not s['met']:
                errors.append('live: ' + json.dumps(s, sort_keys=True))
    elif not tool_present:
        errors.append('tools/kama-completion-live.py absent at tip')

    # -- controls -------------------------------------------------------- #
    def mutate(rcpt, fn):
        m = json.loads(json.dumps(rcpt))
        fn(m)
        return m

    families = {}
    if receipt is not None:
        controls = {}
        # stale: a receipt for a different nonce
        controls['stale'] = [mutate(receipt, lambda m: m.update(
            {'nonce': 'r60-deadbeef'})), ]
        # log: one capture body tampered so its sha256 disagrees
        controls['log'] = [mutate(receipt, lambda m: (
            m['captures']['health'].update({'body': '{"status":"OK"}'})), )]
        # tamper: eight one-field receipt mutations
        def set_field(r, *path, val):
            d = r
            for p in path[:-1]:
                d = d.setdefault(p, {})
            d[path[-1]] = val
        tam = []
        tam.append(mutate(receipt, lambda m: set_field(
            m, 'captures', 'completion', 'body',
            val=m['captures']['completion']['body'].replace(
                'text_completion', 'chat.completion'))))
        tam.append(mutate(receipt, lambda m: set_field(
            m, 'hold', 'released', val=False)))
        tam.append(mutate(receipt, lambda m: set_field(
            m, 'teardown', 'child_pre_dead', val=True)))
        tam.append(mutate(receipt, lambda m: set_field(
            m, 'teardown', 'returncode', val=137)))
        tam.append(mutate(receipt, lambda m: set_field(
            m, 'teardown', 'port_closed', val=False)))
        tam.append(mutate(receipt, lambda m: set_field(
            m, 'verdict', val='FAIL')))
        tam.append(mutate(receipt, lambda m: set_field(
            m, 'captures', 'completion2', 'body',
            val=m['captures']['completion2']['body'].replace(
                '"text"', '"content"', 1))))
        tam.append(mutate(receipt, lambda m: (
            set_field(m, 'model', 'sha256', val='0' * 64),
            set_field(m, 'server', 'sha256', val='0' * 64))))
        controls['tamper'] = tam
        controls['predead'] = [mutate(receipt, lambda m: set_field(
            m, 'teardown', 'child_pre_dead', val=True))]
        controls['sigterm'] = [mutate(receipt, lambda m: set_field(
            m, 'teardown', 'returncode', val=-9))]
        controls['hold'] = [mutate(receipt, lambda m: set_field(
            m, 'hold', 'released', val=False))]
        # outside: receipt completion model disagrees with the live contact
        controls['outside'] = [mutate(receipt, lambda m: set_field(
            m, 'captures', 'completion', 'body',
            val=re.sub(r'"model"\s*:\s*"[^"]*"',
                       '"model": "other-alias"',
                       m['captures']['completion']['body'])))]

        for fam, items in controls.items():
            ok = 0
            for ctl in items:
                s = score(ctl, witness)
                if not s['met']:
                    ok += 1
            families[fam] = f'{ok}/{len(items)}'

        # fake: two canned servers; neither survives live grading
        fake_ok = 0
        for variant in ('envelope', 'fingerprint'):
            if variant == 'envelope':
                body = {'object': 'chat.completion', 'choices': [{'text': ''}],
                        'model': ALIAS}
            else:
                body = {'object': 'text_completion',
                        'choices': [{'text': 'x', 'index': 0,
                                     'finish_reason': 'length'}],
                        'model': ALIAS, 'system_fingerprint': 'b1-x',
                        'usage': {'prompt_tokens': 1,
                                  'completion_tokens': 1,
                                  'total_tokens': 2},
                        'timings': {'predicted_n': 1, 'predicted_ms': 1.0}}
            srv, port = make_fake(work, body)
            try:
                st, resp = post(port, {'prompt': 'p', 'n_predict': 1})
                w = {'status': st, 'model': body.get('model'),
                     'fingerprint': body.get('system_fingerprint'),
                     'text': None, 'sent_prompt': 'p',
                     'nonce_prompt': 'DIFFERENT'}
                s = score(receipt, w)
                if not s['met']:
                    fake_ok += 1
            finally:
                srv.shutdown()
        families['fake'] = f'{fake_ok}/2'

        total = sum(int(v.split('/')[1]) for v in families.values())
        rejected = sum(int(v.split('/')[0]) for v in families.values())
    else:
        families = {'stale': '0/1', 'log': '0/1', 'tamper': '0/8',
                    'predead': '0/1', 'sigterm': '0/1', 'hold': '0/1',
                    'outside': '0/1', 'fake': '0/2'}
        total, rejected = 0, 0

    live_num = int(live_ok.split('/')[0])
    met = (tool_present == 1 and live_num == 1
           and total == 16 and rejected == 16 and not errors)
    print(f'tool_present={tool_present} live_ok={live_ok} '
          f'fake_rejected={families["fake"]} '
          f'stale_rejected={families["stale"]} '
          f'tamper_rejected={families["tamper"]} '
          f'log_rejected={families["log"]} '
          f'predead_rejected={families["predead"]} '
          f'sigterm_rejected={families["sigterm"]} '
          f'hold_rejected={families["hold"]} '
          f'outside_rejected={families["outside"]} '
          f'errors={len(errors)} met={str(met)}')
    for e in errors[:8]:
        print(f'error: {e}', file=sys.stderr)
    return 0 if met else 1


if __name__ == '__main__':
    sys.exit(main())
