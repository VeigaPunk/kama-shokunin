#!/usr/bin/env python3
"""Manual witness of the root-forwarder tool run: is the child stopped, who
holds the run-port listener in the counter's own procfs scan, and do
requests on the run port get answered (by whom: child stopped => forwarder)."""
import importlib.util
import json
import os
import subprocess
import sys
import time
import urllib.request

CLONE = '/fast/scratch/hyaku/kama-r64/b/MT07RefAgree/clone'
W = '/fast/scratch/hyaku/kama-r64/b/MT07RefAgree/work/verify'
os.makedirs(W, exist_ok=True)
for f in os.listdir(W):
    p = os.path.join(W, f)
    if os.path.isdir(p):
        import shutil
        shutil.rmtree(p)
hold = os.path.join(W, 'live', 'hold')
os.makedirs(hold, mode=0o700, exist_ok=True)
server = os.path.realpath(os.path.expanduser('~/.local/opt/llama-b11755/llama-server'))
model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
MODEL_SHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
SERVER_SHA = 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804'
spec = importlib.util.spec_from_file_location('c1', os.path.join(CLONE, 'tools', 'round64-c1-counter.py'))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

tool = os.path.join(CLONE, 'tools', 'kama-completion-live.py')
p = subprocess.Popen([sys.executable, tool, '--nonce', 'verify-nonce', '--work', os.path.join(W, 'tool-work'),
                      '--server', server, '--model', model, '--model-sha256', MODEL_SHA,
                      '--server-sha256', SERVER_SHA, '--alias', C.ALIAS, '--hold-dir', hold,
                      '--hold-timeout', '60', '--out', os.path.join(W, 'receipt.json')],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
hp = os.path.join(hold, 'hold.json')
t0 = time.time()
while not os.path.exists(hp) and time.time() - t0 < 120:
    time.sleep(0.1)
doc = json.load(open(hp))
child, port = doc['pid'], doc['port']
st = open(f'/proc/{child}/stat').read()
state = st[st.rindex(')') + 2]
print(json.dumps({'hold_pid': child, 'port': port, 'child_state': state}))
ls = C.listeners(port)
pids, unread = C.holder_pids([i for i, _ in ls])
print(json.dumps({'counter_scan_holders': sorted(pids), 'unreadable_own': sorted(unread),
                  'listener_inodes': [i for i, _ in ls]}))
ans = []
for i in range(2):
    req = urllib.request.Request(f'http://127.0.0.1:{port}/v1/completions',
                                 data=json.dumps({'prompt': f'verify probe {i}', 'n_predict': 4,
                                                  'temperature': 0.0, 'seed': 1}).encode(),
                                 headers={'Content-Type': 'application/json'})
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    r = json.loads(op.open(req, timeout=60).read())
    ans.append({'text': r['choices'][0]['text'], 'fingerprint': r.get('system_fingerprint'),
                'usage': r.get('usage')})
print(json.dumps({'answers': ans}))
ps = subprocess.run(['ps', '-eo', 'pid,ppid,user,stat,args'], capture_output=True, text=True).stdout
print('\n'.join(l[:200] for l in ps.splitlines() if 'llama-server' in l or 'rootforge' in l))
open(os.path.join(hold, 'release'), 'w').write('go\n')
p.wait(timeout=120)
print('tool rc', p.returncode)
r = json.load(open(os.path.join(W, 'receipt.json')))
print(json.dumps({'verdict': r.get('verdict'), 'listener_holders': r.get('listener_holders'),
                  'checks_failed': [k for k, v in (r.get('checks') or {}).items() if v.get('evaluated') and not v.get('passed')]}))
