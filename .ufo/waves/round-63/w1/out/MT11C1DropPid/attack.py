#!/usr/bin/env python3
"""Attacker-written hold.json driver (MT11C1DropPid seat).

Runs the tip-pinned kama-completion-live.py in hold mode, waits for its
ready.json (which names the REAL llama-server child pid and its port), then
plays the attacker: writes its own hold.json naming the real child pid and a
canned loopback server's port, serves consistent /v1/completions + /tokenize
answers from that canned server, and releases the hold. The genuine receipt is
then re-scored by the genuine counter and by the mutants with the attacker's
witness, and the variants are printed.

Variant A: pid = real child, port = canned server (listener not owned by child).
Variant B: pid = attacker's own pid, port = canned server (canned server runs
           in this process, so it owns its own listener).
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

S = os.path.abspath(sys.argv[1])          # scratch root
CLONE = os.path.join(S, 'clone')
MODS = {
    'genuine': os.path.join(CLONE, 'tools', 'round63-c1-counter.py'),
    'm1-drop-pid+port': os.path.join(S, 'm1', 'tools', 'round63-c1-counter.py'),
    'm2-drop-pid': os.path.join(S, 'm2', 'tools', 'round63-c1-counter.py'),
    'm3-drop-port': os.path.join(S, 'm3', 'tools', 'round63-c1-counter.py'),
}
TOOL = os.path.join(CLONE, 'tools', 'kama-completion-live.py')
MODEL_SHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
SERVER_SHA = 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804'
ALIAS = 'kama-completion-probe'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


G = load('c1_genuine', MODS['genuine'])
LIVE = load('kama_live_attack', os.path.join(CLONE, 'tools', 'kama-llamacpp-live.py'))

nonce = 'r63-' + hashlib.sha256(os.urandom(16)).hexdigest()[:10]
hold = os.path.join(S, 'attack', 'hold')
os.makedirs(hold, exist_ok=True)
out = os.path.join(S, 'attack', 'receipt.json')
proc = subprocess.Popen(
    [sys.executable, TOOL, '--nonce', nonce, '--work', os.path.join(S, 'attack', 'tool-work'),
     '--model-sha256', MODEL_SHA, '--server-sha256', SERVER_SHA, '--alias', ALIAS,
     '--hold-dir', hold, '--hold-timeout', '90', '--out', out],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

ready = None
t0 = time.monotonic()
while time.monotonic() - t0 < 120:
    rp = os.path.join(hold, 'ready.json')
    if os.path.exists(rp):
        try:
            ready = json.load(open(rp))
            break
        except (ValueError, OSError):
            pass
    if proc.poll() is not None:
        break
    time.sleep(0.05)
assert ready, 'no ready.json from the real tool'
child_pid, real_port = ready['pid'], ready['port']
print(f'real child pid={child_pid} real port={real_port}', file=sys.stderr)

# the attacker learns the public fingerprint from the real server (public data)
st, _, body, _ = G.http(real_port, '/v1/completions',
                        {'prompt': 'probe', 'n_predict': 1, 'temperature': 0.0, 'seed': 3})
real_fp = json.loads(body)['system_fingerprint']

# canned, self-consistent loopback server: usage.prompt_tokens == tokenize count
canned, cport = G.make_fake(5, 5, real_fp)
results = {}
try:
    for variant, pid in (('A-real-child-pid', child_pid), ('B-attacker-pid', os.getpid())):
        hd = {'schema': 'kama-completion-hold/v1', 'port': cport, 'pid': pid,
              'alias': ALIAS, 'model_sha256': MODEL_SHA, 'server_sha256': SERVER_SHA,
              'at': 'attacker'}
        with open(os.path.join(hold, 'hold.json'), 'w') as f:
            json.dump(hd, f)
        # attacker's witness, observed with the counter's own observe()
        wit = G.observe(cport, pid, hd, LIVE, nonce)
        results[variant] = wit
finally:
    pass

# release the hold so the genuine tool finishes; keep the canned server up for scoring
open(os.path.join(hold, 'release'), 'w').write('go\n')
proc.wait(timeout=120)
receipt = json.load(open(out))

print(f'receipt verdict={receipt.get("verdict")} child_pid={receipt.get("child_pid")} '
      f'port={receipt.get("port")} nonce_ok={receipt.get("nonce") == nonce}')
for variant, wit in results.items():
    print(f'-- variant {variant}: witness pid={wit["pid"]} port={wit["port"]} '
          f'listener_owned={wit["listener_owned"]} usage={wit["usage_prompt_tokens"]} '
          f'tok={wit["tokenize_count"]} fp_match={wit["fingerprint"] == real_fp}')
    for name, path in MODS.items():
        M = G if name == 'genuine' else load('c1_' + name.replace('-', '_'), path)
        M.NONCE = nonce
        s = M.score(receipt, wit)
        print(f'   {name:18s} live_gate_met={s["met"]} fails={sorted(s["fails"])}')
canned.shutdown()
