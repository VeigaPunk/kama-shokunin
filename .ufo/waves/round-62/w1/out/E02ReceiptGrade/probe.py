#!/usr/bin/env python3
"""E02 sensitivity probe: mutate the receipt, confirm the independent
re-grader flips exactly the expected checks (calibration evidence).

Each semantic mutation re-hashes the mutated capture body so the integrity
gate is satisfied and only the check predicate is exercised; one mutation
tampers the body WITHOUT updating body_sha256 to prove the integrity gate.
"""
import copy
import hashlib
import json
import os
import subprocess
import sys

SRC = sys.argv[1]
TOOL = sys.argv[2]
HOLD = sys.argv[3]
GRADE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'regrade.py')
base = json.load(open(SRC))


def rehash(cap):
    cap['body_sha256'] = hashlib.sha256(
        cap['body'].encode('utf-8')).hexdigest()


def grade(doc, tag):
    p = os.path.join(os.path.dirname(GRADE), f'mut-{tag}.json')
    json.dump(doc, open(p, 'w'), indent=1, sort_keys=True)
    r = subprocess.run([sys.executable, GRADE, p, '--tool-source', TOOL,
                        '--hold-dir', HOLD], capture_output=True, text=True)
    out = json.loads(r.stdout)
    return r.returncode, out


def mutate(name, fn, expect):
    doc = copy.deepcopy(base)
    fn(doc)
    rc, out = grade(doc, name)
    bad = sorted(row['check'] for row in out['checks']
                 if row['status'] == 'MISMATCH')
    integrity_bad = sorted(k for k, v in out['capture_integrity'].items()
                           if not v['match'])
    ok = (bad == sorted(expect)) and rc == 1
    return {'mutation': name, 'expect': sorted(expect),
            'observed_mismatch': bad, 'integrity_bad': integrity_bad,
            'rc': rc, 'sensitive': ok,
            'tally': out['tally']}


def m_text(doc):
    body = json.loads(doc['captures']['completion']['body'])
    body['choices'][0]['text'] = ' ground. She lied'
    doc['captures']['completion']['body'] = json.dumps(body)
    rehash(doc['captures']['completion'])


def m_models(doc):
    body = json.loads(doc['captures']['models']['body'])
    body['data'][0]['id'] = 'other-alias'
    doc['captures']['models']['body'] = json.dumps(body)
    rehash(doc['captures']['models'])


def m_usage(doc):
    body = json.loads(doc['captures']['completion']['body'])
    body['usage']['total_tokens'] = 17
    doc['captures']['completion']['body'] = json.dumps(body)
    rehash(doc['captures']['completion'])


def m_fp(doc):
    body = json.loads(doc['captures']['completion']['body'])
    body['system_fingerprint'] = 'not-a-fingerprint'
    doc['captures']['completion']['body'] = json.dumps(body)
    rehash(doc['captures']['completion'])


def m_bad_status(doc):
    doc['captures']['bad_request']['status'] = 200
    rehash(doc['captures']['bad_request'])


def m_hold(doc):
    doc['hold']['released'] = False


def m_teardown(doc):
    doc['teardown']['returncode'] = 1


def m_prompt_drop(doc):
    # completion2 becomes unparseable -> determinism must fail
    doc['captures']['completion2']['body'] = '{"choices":[]}'
    rehash(doc['captures']['completion2'])


def m_tamper(doc):
    # body changed, sha256 NOT updated -> integrity gate must fail
    doc['captures']['health']['body'] = '{"status":"oops"}'


def m_verdict(doc):
    doc['verdict'] = 'FAIL'


rows = [
    mutate('completion_text', m_text, ['completion_deterministic']),
    mutate('models_id', m_models, ['models_alias_id']),
    mutate('usage_total', m_usage, ['completion_usage']),
    mutate('fingerprint', m_fp, ['completion_fingerprint']),
    mutate('bad_request_status', m_bad_status, ['bad_request_graded']),
    mutate('hold_released', m_hold, ['hold_released']),
    mutate('teardown_rc', m_teardown, ['teardown_clean']),
    mutate('completion2_text', m_prompt_drop, ['completion_deterministic']),
    mutate('health_unhashed', m_tamper, ['health_ready']),
    mutate('verdict_flip', m_verdict, []),
]
print(json.dumps(rows, indent=1, sort_keys=True))
print('SENSITIVE %d/%d' % (sum(1 for r in rows if r['sensitive']), len(rows)))
