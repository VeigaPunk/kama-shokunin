#!/usr/bin/env python3
"""Battery v2: fresh self-produced receipt, two detectors.

D0 = committed tip blob (verbatim exec).
D1 = D0 + exactly two minimal repairs (scratch copy only), applied
     programmatically with occurrence assertions:
     R1 grade(): 'hold' in checks  -> 'hold_released' in checks
        (tool stores the hold check under 'hold_released'; committed guard
         never matches, so every genuine hold-mode receipt grades
         'unexpected-checks' and met=False)
     R2 grade(): u = cj.get('usage') or {}
              -> u = (cj.get('usage') or {}) if isinstance(cj, dict) else {}
        (capture body tampered => sha mismatch => cap() None => cj None =>
         committed line raises AttributeError; counter dies mid-battery)

Verdicts use D1 (working detector): ACCEPTED = forged receipt still scores
met=True. D0 behavior per mutant recorded alongside (score delta or CRASH).
"""
import copy
import hashlib
import json
import os
import re
import subprocess
import sys

SCRATCH = '/fast/scratch/hyaku/kama-r62/w/M04C1AttackThe'
REPO = '/home/vgpnk/Projects/shokunin/kama-shokunin'
TIP = '65d7cad0fce90e34de37527cde22e97b63b118bf'
FRESH = os.path.join(SCRATCH, 'counter-run', 'receipt.json')
MUTDIR = os.path.join(SCRATCH, 'mut')

blob = open(os.path.join(SCRATCH, 'bin', 'round62-c1-counter.py')).read()

OLD1 = "    if 'hold' in (receipt.get('checks') or {}):"
NEW1 = "    if 'hold_released' in (receipt.get('checks') or {}):"
OLD2 = "    u = cj.get('usage') or {}"
NEW2 = ("    u = (cj.get('usage') or {}) if isinstance(cj, dict) else {}\n"
        "    t = (cj.get('timings') or {}) if isinstance(cj, dict) else {}")
OLD3 = "    t = cj.get('timings') or {}\n"
assert blob.count(OLD1) == 1 and blob.count(OLD2) == 1 and blob.count(OLD3) == 1
patched = (blob.replace(OLD1, NEW1).replace(OLD2, NEW2)
           .replace(OLD3, ''))
open(os.path.join(SCRATCH, 'bin', 'counter-repaired.py'), 'w').write(patched)

D0: dict = {}
exec(compile(blob, 'tip:round62-c1-counter.py', 'exec'), D0)
D1: dict = {}
exec(compile(patched, 'scratch:counter-repaired.py', 'exec'), D1)

receipt = json.load(open(FRESH))
NONCE = receipt['nonce']
D0['NONCE'] = NONCE
D1['NONCE'] = NONCE

cj = json.loads(receipt['captures']['completion']['body'])
nprompt = f'{NONCE} under the'
WITNESS = {
    'status': 200,
    'port': receipt['port'],
    'pid': receipt['child_pid'],
    'alias': receipt['alias'],
    'model': cj.get('model'),
    'fingerprint': cj.get('system_fingerprint'),
    'text': (cj.get('choices') or [{}])[0].get('text'),
    'sent_prompt': nprompt,
    'nonce_prompt': nprompt,
    'listener_owned': True,
    'server_sha256': receipt['server']['sha256'],
    'model_sha256': receipt['model']['sha256'],
}

log = open(os.path.join(SCRATCH, 'attack_log2.jsonl'), 'w')


def emit(obj):
    line = json.dumps(obj, sort_keys=True)
    log.write(line + '\n')
    print(line)


def sha_f(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def d0_score(rcpt):
    try:
        return D0['score'](rcpt, WITNESS)
    except Exception as e:
        return {'CRASH': f'{type(e).__name__}: {e}'}


s0 = D1['score'](receipt, WITNESS)
s0d0 = d0_score(copy.deepcopy(receipt))
emit({'phase': 'baseline', 'receipt': FRESH,
      'receipt_sha256': sha_f(FRESH), 'nonce': NONCE,
      'D1_repaired_score': s0, 'D0_committed_score': s0d0,
      'witness': WITNESS})

# ---- committed-control replay under the repaired detector ---------------- #
def mutate(rcpt, fn):
    m = json.loads(json.dumps(rcpt))
    fn(m)
    return m


def set_field(r, *path, val):
    d = r
    for p in path[:-1]:
        d = d.setdefault(p, {})
    d[path[-1]] = val


controls = {}
controls['stale'] = [mutate(receipt, lambda m: m.update(
    {'nonce': 'r60-deadbeef'}))]
controls['log'] = [mutate(receipt, lambda m: (
    m['captures']['health'].update({'body': '{"status":"OK"}'})))]
controls['tamper'] = [
    mutate(receipt, lambda m: set_field(
        m, 'captures', 'completion', 'body',
        val=m['captures']['completion']['body'].replace(
            'text_completion', 'chat.completion'))),
    mutate(receipt, lambda m: set_field(m, 'hold', 'released', val=False)),
    mutate(receipt, lambda m: set_field(
        m, 'teardown', 'child_pre_dead', val=True)),
    mutate(receipt, lambda m: set_field(
        m, 'teardown', 'returncode', val=137)),
    mutate(receipt, lambda m: set_field(
        m, 'teardown', 'port_closed', val=False)),
    mutate(receipt, lambda m: set_field(m, 'verdict', val='FAIL')),
    mutate(receipt, lambda m: set_field(
        m, 'captures', 'completion2', 'body',
        val=m['captures']['completion2']['body'].replace(
            '"text"', '"content"', 1))),
    mutate(receipt, lambda m: (
        set_field(m, 'model', 'sha256', val='0' * 64),
        set_field(m, 'server', 'sha256', val='0' * 64))),
]
controls['predead'] = [mutate(receipt, lambda m: set_field(
    m, 'teardown', 'child_pre_dead', val=True))]
controls['sigterm'] = [mutate(receipt, lambda m: set_field(
    m, 'teardown', 'returncode', val=-9))]
controls['hold'] = [mutate(receipt, lambda m: set_field(
    m, 'hold', 'released', val=False))]
controls['outside'] = [mutate(receipt, lambda m: set_field(
    m, 'captures', 'completion', 'body',
    val=re.sub(r'"model"\s*:\s*"[^"]*"', '"model": "other-alias"',
               m['captures']['completion']['body'])))]

families = {}
for fam, items in controls.items():
    det = []
    for ctl in items:
        r = D1['score'](ctl, WITNESS)
        det.append(bool(r['met']))
    families[fam] = f"{sum(1 for m_ in det if not m_)}/{len(items)}"
fake_ok = 0
for variant in ('envelope', 'fingerprint'):
    if variant == 'envelope':
        body = {'object': 'chat.completion', 'choices': [{'text': ''}],
                'model': D1['ALIAS']}
    else:
        body = {'object': 'text_completion',
                'choices': [{'text': 'x', 'index': 0,
                             'finish_reason': 'length'}],
                'model': D1['ALIAS'], 'system_fingerprint': 'b1-x',
                'usage': {'prompt_tokens': 1, 'completion_tokens': 1,
                          'total_tokens': 2},
                'timings': {'predicted_n': 1, 'predicted_ms': 1.0}}
    srv, port = D1['make_fake'](SCRATCH, body)
    try:
        st_, resp = D1['post'](port, {'prompt': 'p', 'n_predict': 1})
        w = {'status': st_, 'model': body.get('model'),
             'fingerprint': body.get('system_fingerprint'),
             'text': None, 'sent_prompt': 'p', 'nonce_prompt': 'DIFFERENT'}
        if not D1['score'](receipt, w)['met']:
            fake_ok += 1
    finally:
        srv.shutdown()
families['fake'] = f'{fake_ok}/2'
total = sum(int(v.split('/')[1]) for v in families.values())
rejected = sum(int(v.split('/')[0]) for v in families.values())
emit({'phase': 'control_replay_D1', 'families': families,
      'total': total, 'rejected': rejected})


def rehash(r, name):
    b = r['captures'][name]['body']
    r['captures'][name]['body_sha256'] = hashlib.sha256(b.encode()).hexdigest()


FORGERIES = [
    ('R1', 'log-family-control', "captures.health.body -> '{\"status\":\"OK\"}', sha NOT recomputed (counter's own log control)",
     lambda r: r['captures']['health'].update({'body': '{"status":"OK"}'})),
    ('M1', 'unchecked-capture-field', 'captures.completion.error set (capture claims the POST errored)',
     lambda r: r['captures']['completion'].update(
         {'error': 'URLError(<socket gear disconnected>)'})),
    ('M2', 'unchecked-capture-field', 'captures.completion.body_truncated = True (graded bytes not the full server answer)',
     lambda r: r['captures']['completion'].update({'body_truncated': True})),
    ('M3', 'unchecked-capture-field', 'captures.bad_request.status 400 -> 500 (both inside the graded set)',
     lambda r: r['captures']['bad_request'].update({'status': 500})),
    ('M4', 'unchecked-capture-entry', "adds captures.server_log_tail with a forged llama-server build line (self-consistent sha)",
     lambda r: r['captures'].update({'server_log_tail': {
         'body': 'llama-server build b11755 FORGED-LINE listening on 0.0.0.0',
         'body_sha256': hashlib.sha256(
             b'llama-server build b11755 FORGED-LINE listening on 0.0.0.0'
         ).hexdigest(), 'status': None, 'error': None,
         'body_truncated': False}})),
    ('M5', 'graded-capture-field', 'captures.health.status 200 -> 503 (graded field, sanity)',
     lambda r: r['captures']['health'].update({'status': 503})),
    ('M6', 'teardown-unchecked', 'teardown.waited_ms 3 -> 999999',
     lambda r: r['teardown'].update({'waited_ms': 999999})),
    ('M7', 'teardown-unchecked', 'teardown.sigterm_sent True -> False (child never signalled)',
     lambda r: r['teardown'].update({'sigterm_sent': False})),
    ('M8', 'server_log-path-unchecked', "server_log -> /nonexistent/forged/server.log",
     lambda r: r.update({'server_log': '/nonexistent/forged/server.log'})),
    ('M9', 'argv-unchecked', 'argv -> ["/bin/true","--forged"] (pinned-server launch line forged)',
     lambda r: r.update({'argv': ['/bin/true', '--forged']})),
    ('M10', 'request-unchecked', "request.prompt -> 'FORGED PROMPT 2+2=' (captured body is the answer to a different prompt)",
     lambda r: r['request'].update({'prompt': 'FORGED PROMPT 2+2='})),
    ('M11', 'timestamp-unchecked', "at -> '2019-01-01T00:00:00.000Z'",
     lambda r: r.update({'at': '2019-01-01T00:00:00.000Z'})),
    ('M12', 'stored-check-trust', "checks.listener_owned.passed True -> False (grade derives this check FROM the stored value)",
     lambda r: r['checks']['listener_owned'].update({'passed': False})),
    ('M13', 'self-consistent-rehash', 'completion+completion2 text -> " FORGED-TEXT", body_sha256 recomputed (matched hash, wrong bytes)',
     lambda r: [(b := json.loads(r['captures'][n]['body']),
                 b['choices'][0].__setitem__('text', ' FORGED-TEXT'),
                 r['captures'][n].update({'body': json.dumps(b)}),
                 rehash(r, n))
                for n in ('completion', 'completion2')]),
    ('M14', 'self-consistent-rehash', "health body -> '{\"status\":\"FAIL\"}' + re-hash",
     lambda r: (r['captures']['health'].update(
         {'body': '{"status":"FAIL"}'}), rehash(r, 'health'))),
    ('M15', 'self-consistent-rehash', "models body data[].id -> ['other'] + re-hash",
     lambda r: (b := json.loads(r['captures']['models']['body']),
                b['data'][0].__setitem__('id', 'other'),
                r['captures']['models'].update({'body': json.dumps(b)}),
                rehash(r, 'models'))),
    ('M16', 'witness-bound', 'child_pid -> 999999 (live leg binds pid)',
     lambda r: r.update({'child_pid': 999999})),
    ('M17', 'witness-bound', "nonce -> 'r60-deadbeef' (stale)",
     lambda r: r.update({'nonce': 'r60-deadbeef'})),
    ('M18', 'pinned-digest', "model.sha256 -> '0'*64",
     lambda r: r['model'].update({'sha256': '0' * 64})),
    ('M19', 'pinned-digest', "server.sha256 -> '0'*64",
     lambda r: r['server'].update({'sha256': '0' * 64})),
    ('M20', 'verdict', "verdict -> 'FAIL'",
     lambda r: r.update({'verdict': 'FAIL'})),
]

accepted, rejected_m, d0_crashes = [], [], 0
for mid, family, desc, fn in FORGERIES:
    m = copy.deepcopy(receipt)
    fn(m)
    path = os.path.join(MUTDIR, f'{mid}.json')
    with open(path, 'w') as f:
        json.dump(m, f, indent=1, sort_keys=True)
    s1 = D1['score'](m, WITNESS)
    r0 = d0_score(copy.deepcopy(m))
    if 'CRASH' in r0:
        d0_crashes += 1
    verdict = 'ACCEPTED' if s1['met'] else 'REJECTED'
    (accepted if s1['met'] else rejected_m).append(mid)
    emit({'phase': 'forgery', 'id': mid, 'family': family,
          'mutation': desc, 'verdict': verdict,
          'D1_score': s1, 'D0_score': r0,
          'D1_delta_vs_pristine': {
              k: [s0[k], s1[k]] for k in s1 if s0[k] != s1[k]},
          'mutant_sha256': sha_f(path)})

emit({'phase': 'summary', 'baseline_D1_met': s0['met'],
      'controls_total_D1': total, 'controls_rejected_D1': rejected,
      'mutants': len(FORGERIES), 'accepted_D1': accepted,
      'rejected_D1': rejected_m, 'D0_crashes': d0_crashes})
log.close()
