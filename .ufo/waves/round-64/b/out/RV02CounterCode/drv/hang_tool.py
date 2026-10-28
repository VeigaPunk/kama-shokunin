import argparse, json, os, subprocess, sys, time
ap = argparse.ArgumentParser()
for a in ('--nonce','--work','--server','--model','--model-sha256','--server-sha256','--alias','--hold-dir','--hold-timeout','--out'):
    ap.add_argument(a)
A, _ = ap.parse_known_args()
MODE = os.environ['LEAK_MODE']
port = 39000 + (os.getpid() % 900)
p = subprocess.Popen([A.server, '--model', A.model, '--alias', A.alias, '--port', str(port),
    '--host', '127.0.0.1', '-c', '512', '-t', '1'], stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
open(os.path.join(os.path.dirname(A.out), 'child.pid'), 'w').write(str(p.pid))
if MODE == 'noexit':
    for _ in range(300):
        time.sleep(0.2)
        import urllib.request
        try:
            if urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=2).status == 200: break
        except Exception: pass
    doc = {'schema': 'kama-completion-hold/v1', 'port': port, 'pid': p.pid, 'alias': A.alias,
           'model_sha256': A.model_sha256, 'server_sha256': A.server_sha256, 'prompt': 'x', 'at': '2026-10-28T00:00:00Z'}
    json.dump(doc, open(os.path.join(A.hold_dir, 'hold.json'), 'w'))
# 'hang': never write hold.json; 'noexit': ignore the release file. Both sleep.
time.sleep(100000)
