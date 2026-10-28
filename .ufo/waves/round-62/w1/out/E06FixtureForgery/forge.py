#!/usr/bin/env python3
"""E06FixtureForgery: hand-built receipt forgeries fed to round62 c1 score().

One authentic hold-mode lifecycle of the byte-pinned
tools/kama-completion-live.py (from the lane tip) yields the base receipt and
a real witness observation exactly as the counter's witness_run() produces
them.  Three forgeries are then hand-built by editing that committed receipt
JSON (sha256 recomputed where a body changes) and each is fed to the
counter's own score() with the same real witness.
"""
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import importlib.util

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
TIP = '65d7cad0fce90e34de37527cde22e97b63b118bf'
W = '/fast/scratch/hyaku/kama-r62/w/E06FixtureForgery'
ALIAS = 'kama-completion-probe'
MODEL_SHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
SERVER_SHA = 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804'


def sha_b(s):
    return hashlib.sha256(s.encode()).hexdigest()


def load_counter():
    path = os.path.join(LANE, 'tools', 'round62-c1-counter.py')
    spec = importlib.util.spec_from_file_location('r62c1', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stage_tip(mod):
    tiproot = os.path.join(W, 'tip')
    os.makedirs(os.path.join(tiproot, 'tools'), exist_ok=True)
    os.makedirs(os.path.join(tiproot, 'registry'), exist_ok=True)
    for rel in ('tools/kama-completion-live.py',
                'tools/kama-llamacpp-live.py',
                'registry/endpoint-consumers.tsv'):
        b = mod.blob(LANE, TIP, rel)
        assert b is not None, rel
        with open(os.path.join(tiproot, rel), 'wb') as f:
            f.write(b)
    return os.path.join(tiproot, 'tools', 'kama-completion-live.py')


def lifecycle(mod, tool_path, extra_prompt='A dog ran to the'):
    """witness_run() replicated, plus one extra real completion body."""
    hold = os.path.join(W, 'hold')
    os.makedirs(hold, exist_ok=True)
    nonce = 'r62-' + hashlib.sha256(os.urandom(16)).hexdigest()[:10]
    out_path = os.path.join(W, 'receipt.json')
    proc = subprocess.Popen(
        [sys.executable, tool_path, '--nonce', nonce,
         '--work', os.path.join(W, 'tool-work'),
         '--model-sha256', MODEL_SHA, '--server-sha256', SERVER_SHA,
         '--alias', ALIAS, '--hold-dir', hold, '--hold-timeout', '90',
         '--out', out_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    witness = extra = None
    t0 = time.monotonic()
    while time.monotonic() - t0 < 120:
        hp = os.path.join(hold, 'hold.json')
        if os.path.exists(hp):
            try:
                h = json.load(open(hp))
            except (ValueError, OSError):
                time.sleep(0.2)
                continue
            port, pid = h.get('port'), h.get('pid')
            nprompt = f'{nonce} under the'
            st, body = mod.post(port, {'prompt': nprompt, 'n_predict': 4,
                                       'temperature': 0.0, 'seed': 3})
            try:
                wj = json.loads(body)
            except ValueError:
                wj = {}
            ch0 = (wj.get('choices') or [{}])[0]
            spec = importlib.util.spec_from_file_location(
                'kama_llamacpp_live_w',
                os.path.join(os.path.dirname(tool_path),
                             'kama-llamacpp-live.py'))
            lm = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lm)
            witness = {
                'status': st, 'port': port, 'pid': pid,
                'alias': h.get('alias'),
                'model': wj.get('model'),
                'fingerprint': wj.get('system_fingerprint'),
                'text': ch0.get('text'),
                'sent_prompt': nprompt, 'nonce_prompt': nprompt,
                'listener_owned': lm.port_owned_by(pid, port),
                'server_sha256': h.get('server_sha256'),
                'model_sha256': h.get('model_sha256'),
            }
            # a second real request, different prompt -> a real captured body
            # whose text differs from the receipt's own completion text
            st2, body2 = mod.post(port, {'prompt': extra_prompt,
                                         'n_predict': 4,
                                         'temperature': 0.0, 'seed': 3})
            extra = {'status': st2, 'body': body2}
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
    return receipt, witness, extra, nonce


def fix_sha(cap):
    cap['body_sha256'] = sha_b(cap['body'])


def forge_a(receipt, extra_body):
    """Real captured body (a second live completion whose text differs) in
    completion2, the check recorded truthfully as failed, verdict fabricated
    to REQUEST_OK."""
    r = copy.deepcopy(receipt)
    c2 = r['captures']['completion2']
    c2['status'] = 200
    c2['error'] = None
    c2['body'] = extra_body
    c2['body_truncated'] = False
    fix_sha(c2)
    r['checks']['completion_deterministic']['passed'] = False
    r['verdict'] = 'REQUEST_OK'
    return r


def forge_a2(receipt, extra_body):
    """Same body substitution, but the failing check is also forged to
    passed=True (a fully fabricated record) with verdict REQUEST_OK."""
    r = forge_a(receipt, extra_body)
    r['checks']['completion_deterministic']['passed'] = True
    return r


def forge_b(receipt):
    """Capture bodies re-ordered across keys (health <-> models), each body's
    sha256 recomputed so the log gate passes, every stored check forged to
    true, verdict REQUEST_OK."""
    r = copy.deepcopy(receipt)
    h, m = r['captures']['health'], r['captures']['models']
    h['body'], m['body'] = m['body'], h['body']
    fix_sha(h)
    fix_sha(m)
    for v in r['checks'].values():
        v['passed'] = True
    r['verdict'] = 'REQUEST_OK'
    return r


def forge_c(receipt, other='kama-completion-other'):
    """Nonce matches the verifier's, but the served alias differs on every
    alias surface; stored checks forged true, verdict REQUEST_OK."""
    r = copy.deepcopy(receipt)
    for key in ('completion', 'completion2'):
        cap = r['captures'][key]
        cap['body'] = re.sub(r'"model"\s*:\s*"[^"]*"',
                             f'"model": "{other}"', cap['body'])
        fix_sha(cap)
    m = r['captures']['models']
    m['body'] = json.dumps({'object': 'list',
                            'data': [{'id': other, 'object': 'model',
                                      'owned_by': 'llamacpp'}]},
                           separators=(',', ':'))
    fix_sha(m)
    p = r['captures']['props']
    p['body'] = json.dumps({'model_alias': other},
                           separators=(',', ':'))
    fix_sha(p)
    for v in r['checks'].values():
        v['passed'] = True
    r['verdict'] = 'REQUEST_OK'
    return r


def detail(mod, receipt, witness):
    s = mod.score(receipt, witness)
    recomputed, inconsistent = mod.grade(receipt)
    failed = sorted(k for k, v in recomputed.items() if v is not True)
    return {'score': s, 'recomputed_false': failed,
            'inconsistent': inconsistent,
            'verdict_field': receipt.get('verdict'),
            'nonce_matches_verifier': receipt.get('nonce') == mod.NONCE}


def main():
    mod = load_counter()
    tool_path = stage_tip(mod)
    receipt, witness, extra, nonce = lifecycle(mod, tool_path)
    mod.NONCE = nonce
    assert receipt is not None and witness is not None and extra is not None
    json.dump({'witness': witness, 'extra_status': extra['status'],
               'nonce': nonce},
              open(os.path.join(W, 'witness.json'), 'w'), indent=1)
    out = {}

    # sanity: the authentic receipt through the same score()
    out['base_authentic'] = detail(mod, receipt, witness)
    # supplementary: receipt alone, no live witness
    out['base_receipt_only_no_witness'] = detail(mod, receipt, None)

    cap_text = json.loads(receipt['captures']['completion']['body'])[
        'choices'][0]['text']
    extra_text = json.loads(extra['body'])['choices'][0]['text']
    assert extra_text != cap_text, ('extra body text equals baseline text',
                                    extra_text)

    fixtures = {
        'a_verdict_fabricated_real_failing_body': forge_a(
            receipt, extra['body']),
        'a2_verdict_and_check_fabricated': forge_a2(
            receipt, extra['body']),
        'b_capture_bodies_reordered_across_keys': forge_b(receipt),
        'c_nonce_matches_alias_differs': forge_c(receipt),
    }
    for name, fx in fixtures.items():
        json.dump(fx, open(os.path.join(W, name + '.json'), 'w'),
                  indent=1, sort_keys=True)
        out[name] = detail(mod, fx, witness)
        out[name]['accepted'] = out[name]['score']['met']
    out['_extra_text_differs'] = extra_text != cap_text
    out['_completion_text'] = cap_text
    out['_extra_text'] = extra_text
    json.dump(out, open(os.path.join(W, 'forgery-results.json'), 'w'),
              indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
