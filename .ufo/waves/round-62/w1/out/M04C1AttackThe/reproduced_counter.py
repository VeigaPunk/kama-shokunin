"""Reproduction of tools/round62-c1-counter.py grading core (tip
65d7cad0fce90e34de37527cde22e97b63b118bf), transcribed verbatim for the
M04C1AttackThe falsification probe. Only main()/witness_run/argparse glue is
dropped; post/make_fake are kept so the counter's own 16-control battery can
be replayed against the measured receipt."""
import hashlib
import json
import re

MODEL_SHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
SERVER_SHA = 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804'
ALIAS = 'kama-completion-probe'
FP_RE = re.compile(r'^b\d+-[0-9a-f]{9,40}$')
SCHEMA = 'kama-completion-live/v1'
PROMPT = 'The cat sat on the'
MUT = '__kama_mut__'


def sha256_b(b):
    return hashlib.sha256(b).hexdigest()


def jbody(cap):
    try:
        return json.loads(cap.get('body', ''))
    except (ValueError, TypeError):
        return None


def post(port, payload, timeout=10.0):
    import urllib.error
    import urllib.request
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
    u = cj.get('usage') or {}
    out['completion_usage'] = (
        out['completion_envelope']
        and isinstance(u.get('completion_tokens'), int)
        and isinstance(u.get('prompt_tokens'), int)
        and isinstance(u.get('total_tokens'), int)
        and u['completion_tokens'] >= 1 and u['prompt_tokens'] >= 1
        and u['total_tokens']
        == u['completion_tokens'] + u['prompt_tokens'])
    t = cj.get('timings') or {}
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
    if 'hold' in (receipt.get('checks') or {}):
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
