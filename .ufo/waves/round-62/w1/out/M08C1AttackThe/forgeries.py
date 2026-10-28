#!/usr/bin/env python3
"""M08C1AttackThe — falsification probes against the frozen C1 counter.

Usage: forgeries.py COUNTER_PY RECEIPT_JSON LABEL [SPLICE_RECEIPT_JSON]

The replica is an extracted counter blob imported unmodified (zero drift);
module NONCE is set explicitly the way main() would set it. Every probe feeds
score() a (receipt, witness) pair and prints ACCEPTED (met=True) or REJECTED
(met=False) with the verbatim score() dict.

Witness forgery classes: nonce-less sent_prompt (F1), foreign pid/port (F2),
fully synthetic witness with zero live contact (F3), nonce-substring-only
prompt (F5), colluding receipt+witness pid/port swap to a live foreign
process (F9a/F9b). Receipt-side outside family: completion model disagrees
with live contact (F4a-c). Splice (F6), unset NONCE (F7), negative gates (F8).
"""
import importlib.util
import json
import os
import re
import socket
import subprocess
import sys
import threading
import http.server

COUNTER, RECEIPT, LABEL = sys.argv[1], sys.argv[2], sys.argv[3]
SPLICE = sys.argv[4] if len(sys.argv) > 4 else None
SCRATCH = os.path.dirname(os.path.abspath(__file__))

spec = importlib.util.spec_from_file_location('c1probe', COUNTER)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

receipt = json.load(open(RECEIPT))
NONCE = receipt['nonce']
c1.NONCE = NONCE
comp = json.loads(receipt['captures']['completion']['body'])


def synth_witness(**over):
    """Every field satisfying score(), derived purely from receipt bytes."""
    w = {
        'status': 200,
        'port': receipt['port'],
        'pid': receipt['child_pid'],
        'alias': receipt.get('alias'),
        'model': comp.get('model'),
        'fingerprint': comp.get('system_fingerprint'),
        'text': comp['choices'][0]['text'],
        'sent_prompt': f'{NONCE} under the',
        'nonce_prompt': f'{NONCE} under the',
        'listener_owned': True,
        'server_sha256': receipt['server']['sha256'],
        'model_sha256': receipt['model']['sha256'],
    }
    w.update(over)
    return w


def probe(name, rcpt, w):
    s = c1.score(rcpt, w)
    v = 'ACCEPTED' if s['met'] else 'REJECTED'
    print(f'[{LABEL}:{name}] {v}  score={json.dumps(s, sort_keys=True)}')
    return s


def mut(rcpt, fn):
    m = json.loads(json.dumps(rcpt))
    fn(m)
    return m


print(f'== {LABEL} ==')
print('counter blob', COUNTER)
print('counter sha256', c1.sha256_b(open(COUNTER, 'rb').read()))
print('receipt', RECEIPT, 'nonce', receipt['nonce'], 'port', receipt['port'],
      'child_pid', receipt['child_pid'], 'verdict', receipt.get('verdict'))
print('checks keys', sorted((receipt.get('checks') or {}).keys()))

print(f'[{LABEL}:V0-baseline] pristine receipt + receipt-derived witness')
probe('V0-baseline', receipt, synth_witness())

pid, port = receipt['child_pid'], receipt['port']
alive = os.path.exists(f'/proc/{pid}')
print(f'[{LABEL}:liveness] pid {pid} /proc exists: {alive}')
if alive:
    try:
        cmd = open(f'/proc/{pid}/cmdline', 'rb').read().replace(
            b'\0', b' ').decode('utf-8', 'replace')
    except OSError:
        cmd = '<unreadable>'
    print(f'[{LABEL}:liveness] pid {pid} cmdline: {cmd!r}')
sck = socket.socket()
sck.settimeout(2.0)
try:
    sck.connect(('127.0.0.1', port))
    print(f'[{LABEL}:liveness] port {port}: CONNECTED (someone listening)')
except OSError as e:
    print(f'[{LABEL}:liveness] port {port}: closed ({e})')
finally:
    sck.close()

print(f'[{LABEL}:F1] witness sent_prompt lacks the nonce')
probe('F1-nonceless-prompt', receipt,
      synth_witness(sent_prompt='The cat sat on the mat',
                    nonce_prompt='The cat sat on the mat'))

print(f'[{LABEL}:F2] witness pid/port belong to another process')
foreign = subprocess.Popen(['sleep', '120'])
print(f'[{LABEL}:F2] foreign pid {foreign.pid} (spawned sleep, owns no port)')
probe('F2a-both-foreign', receipt,
      synth_witness(pid=foreign.pid, port=port + 1))
probe('F2b-foreign-port-only', receipt, synth_witness(pid=pid, port=port + 1))
probe('F2c-foreign-pid-only', receipt, synth_witness(pid=foreign.pid, port=port))

print(f'[{LABEL}:F3] synthetic witness, receipt pid/port, zero live contact')
probe('F3-synthetic-witness', receipt, synth_witness())


def outside(rcpt, rehash):
    m = mut(rcpt, lambda x: x['captures']['completion'].update(
        body=re.sub(r'"model"\s*:\s*"[^"]*"', '"model": "other-alias"',
                    x['captures']['completion']['body'])))
    if rehash:
        m['captures']['completion']['body_sha256'] = c1.sha256_b(
            m['captures']['completion']['body'].encode())
    return m


print(f'[{LABEL}:F4] outside family: completion model -> other-alias')
probe('F4a-no-rehash(=committed-control)', outside(receipt, False),
      synth_witness())
probe('F4b-rehashed-capture', outside(receipt, True), synth_witness())
probe('F4c-rehashed+colluding-witness', outside(receipt, True),
      synth_witness(model='other-alias'))

print(f'[{LABEL}:F5] nonce-containment-only prompt (no request)')
probe('F5-nonce-substring', receipt,
      synth_witness(sent_prompt=f'junk {NONCE} tail',
                    nonce_prompt=f'junk {NONCE} tail'))

if SPLICE:
    print(f'[{LABEL}:F6] cross-run splice with {SPLICE}')
    other = json.load(open(SPLICE))
    c1.NONCE = other['nonce']
    probe('F6-cross-run', other, synth_witness(pid=pid, port=port))
    c1.NONCE = NONCE

print(f'[{LABEL}:F7] NONCE global unset')
c1.NONCE = ''
probe('F7-nonce-unset', receipt, synth_witness())
c1.NONCE = NONCE

print(f'[{LABEL}:F8] negative gates (should reject)')
probe('F8a-listener-owned-false', receipt, synth_witness(listener_owned=False))
probe('F8b-fingerprint-bad', receipt, synth_witness(fingerprint='b1-x'))
probe('F8c-model-sha-wrong', receipt,
      synth_witness(model_sha256='0' * 64))
probe('F8d-server-sha-wrong', receipt,
      synth_witness(server_sha256='0' * 64))

print(f'[{LABEL}:F9] colluding swap: receipt pid -> live foreign process')
probe('F9a-foreign-live-pid', mut(receipt, lambda m: m.update(
    child_pid=foreign.pid)), synth_witness(pid=foreign.pid))

srv = http.server.HTTPServer(('127.0.0.1', 0), http.server.BaseHTTPRequestHandler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
fport = srv.server_address[1]
print(f'[{LABEL}:F9] foreign live listener pid={os.getpid()} port={fport}')
probe('F9b-foreign-live-pid+port', mut(receipt, lambda m: m.update(
    child_pid=os.getpid(), port=fport)),
    synth_witness(pid=os.getpid(), port=fport))
srv.shutdown()
foreign.kill()
foreign.wait()
