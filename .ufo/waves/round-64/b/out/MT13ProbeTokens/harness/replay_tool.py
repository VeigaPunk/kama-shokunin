#!/usr/bin/env python3
"""MT13 forged tool R: a GENUINE pinned llama-server is the holder (child of
this tool, exe/argv/env/maps all pinned, listener = its own port). The tool
never sends the lifecycle requests; it replays a genuine receipt copy
(CANNED_TEMPLATE) with the nonce, child pid, port and holder rewritten."""
import argparse, json, os, socket, subprocess, sys, time, hashlib
import urllib.request
ap = argparse.ArgumentParser()
ap.add_argument('--nonce', required=True)
ap.add_argument('--work', required=True)
ap.add_argument('--server', required=True)
ap.add_argument('--model', required=True)
ap.add_argument('--model-sha256', required=True)
ap.add_argument('--server-sha256', required=True)
ap.add_argument('--alias', required=True)
ap.add_argument('--hold-dir', required=True)
ap.add_argument('--hold-timeout', type=float, default=90)
ap.add_argument('--out', required=True)
A, _ = ap.parse_known_args()
s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
child = subprocess.Popen(
    [A.server, '--model', A.model, '--alias', A.alias, '--port', str(port),
     '--host', '127.0.0.1', '-c', '512', '-t', '1'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    stdin=subprocess.DEVNULL,
    env={k: v for k, v in os.environ.items()
         if k in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')})
t0 = time.time()
while time.time() - t0 < 60:
    try:
        if urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=2).status == 200:
            break
    except Exception:
        time.sleep(0.2)
hold_json = os.path.join(A.hold_dir, 'hold.json')
json.dump({'schema': 'kama-completion-hold/v1', 'port': port, 'pid': child.pid,
           'alias': A.alias, 'model_sha256': A.model_sha256,
           'server_sha256': A.server_sha256, 'prompt': 'The cat sat on the',
           'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())},
          open(hold_json, 'w'))
t0 = time.time()
while time.time() - t0 < A.hold_timeout:
    if os.path.exists(os.path.join(A.hold_dir, 'release')):
        break
    time.sleep(0.1)
try:
    os.unlink(hold_json)
except OSError:
    pass
child.terminate(); child.wait()
rcpt = json.load(open(os.environ['CANNED_TEMPLATE']))
rcpt['nonce'] = A.nonce
rcpt['child_pid'] = child.pid
rcpt['port'] = port
rcpt['listener_holders'] = [{'pid': child.pid, 'exe': A.server,
                             'exe_sha256': A.server_sha256}]
rcpt['hold'] = {'dir': A.hold_dir, 'released': True}
json.dump(rcpt, open(A.out, 'w'))
